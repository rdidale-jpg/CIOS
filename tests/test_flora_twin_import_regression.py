"""Regression contract for the established governed Twin importer entry point."""
import threading
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

import cios.applications.flora.web.app as web_app
from cios.applications.flora.blueprint_import.executive_workspace import executive_workspace_page
from cios.applications.flora.blueprint_import.views import (
    import_blueprint_entry_page,
    upload_and_validate_blueprint,
)
from cios.applications.flora.digital_twins import digital_twins_landing_page
from tests.test_flora_blueprint_import_interface import BAD, HEADERS, pkg


def _get(path, headers=None):
    """Exercise the production HTTP handler rather than a test-only view seam."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), web_app.FloraWebHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    connection = HTTPConnection("127.0.0.1", server.server_port)
    try:
        connection.request("GET", path, headers=headers or {})
        response = connection.getresponse()
        return response.status, response.read().decode("utf-8")
    finally:
        connection.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def _upload(monkeypatch, tmp_path, records=None):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    return upload_and_validate_blueprint(
        {"blueprint_zip": pkg(records=records)},
        {
            "blueprint_zip.filename": "tms-package.zip",
            "blueprint_zip.content_type": "application/zip",
            "expected_type": "industry",
        },
        HEADERS,
    )


def test_authorised_digital_twins_navigation_exposes_import_twin(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    html = digital_twins_landing_page(HEADERS)

    assert "Import Twin" in html
    assert "class='button primary' href='/blueprint-import'" in html
    assert "No governed Digital Twins" in html  # no existing Twin selection is required
    assert "Import a Twin package to create a candidate for review" in html


def test_production_routes_render_zero_twin_import_action(monkeypatch, tmp_path):
    """Prove the GET boundary repairs an omitted action and its target loads."""
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_TRUST_PROXY_HEADERS", "1")
    rendered = []
    def observed_renderer(headers):
        html = ("<!doctype html><html><body><section class='hero'><h1>Digital Twins</h1>"
                "<p>Governed Commercial Digital Twins available to your signed-in account.</p></section>"
                "<section><h2>Available Twins</h2>"
                "<p>No governed Digital Twins are available to this signed-in account.</p></section></body></html>")
        rendered.append(html)
        return html

    monkeypatch.setattr(web_app, "digital_twins_landing_page", observed_renderer)

    status, html = _get("/digital-twins", HEADERS)

    assert status == 200
    assert len(rendered) == 1
    assert "No governed Digital Twins are available" in html
    assert "<a class='button primary' href='/blueprint-import'>Import Twin</a>" in html
    assert html.count("href='/blueprint-import'") == 1
    action = html[html.index("<a class='button primary'"):html.index("</a>", html.index("href='/blueprint-import'"))]
    assert "hidden" not in action and "disabled" not in action
    assert "<!-- flora-revision:" in html

    import_status, import_html = _get("/blueprint-import", HEADERS)
    assert import_status == 200
    assert "<h1>Import Twin</h1>" in import_html
    assert "action='/blueprint-import/upload'" in import_html


def test_route_boundary_preserves_one_usable_action(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_TRUST_PROXY_HEADERS", "1")

    existing = "<!doctype html><html><body><a class='button primary' href='/blueprint-import'>Import Twin</a></body></html>"
    monkeypatch.setattr(web_app, "digital_twins_landing_page", lambda headers: existing)
    status, html = _get("/digital-twins", HEADERS)
    assert status == 200 and html.count("href='/blueprint-import'") == 1


def test_import_visibility_depends_only_on_authenticated_upload_authority(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_COMMERCIAL_MISSIONS_FILE", str(tmp_path / "missing-missions.json"))

    authorised = digital_twins_landing_page(HEADERS)
    unauthorised = digital_twins_landing_page(BAD)
    anonymous = digital_twins_landing_page({})

    assert "href='/blueprint-import'>Import Twin</a>" in authorised
    assert "No governed Digital Twins" in authorised
    assert "requires the package.upload capability" in unauthorised
    assert "href='/blueprint-import'>Import Twin</a>" not in unauthorised
    assert "package.upload capability" not in anonymous
    assert "href='/blueprint-import'>Import Twin</a>" not in anonymous


def test_import_route_loads_and_supported_upload_can_be_initiated(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    html, status = import_blueprint_entry_page(HEADERS)

    assert status == 200
    assert "<h1>Import Twin</h1>" in html
    assert "action='/blueprint-import/upload'" in html
    assert "type='file'" in html and "accept='.zip,application/zip'" in html
    assert "Commercial Mission or an existing Twin selection is not required" in html


def test_import_get_is_entry_only_even_without_workspace_or_upload_capability(monkeypatch, tmp_path):
    """Navigation must never masquerade as a failed package submission."""
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))

    html, status = import_blueprint_entry_page({})

    assert status == 200
    assert "name='expected_type'" in html
    assert "name='blueprint_zip' type='file'" in html
    assert "<button type='submit'>Upload Twin</button>" in html
    assert "method='post' action='/blueprint-import/upload' enctype='multipart/form-data'" in html
    assert "Workspace and upload access required" in html
    assert "no package upload has been attempted" in html
    assert "Package import needs attention" not in html
    assert "Package import access denied" not in html
    assert not (tmp_path / "blueprint_import").exists()


def test_incomplete_form_submission_returns_entry_validation_not_diagnostics(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))

    no_file, file_status, _ = upload_and_validate_blueprint(
        {}, {"_form_submission": "true", "expected_type": "industry"}, HEADERS,
    )
    no_type, type_status, _ = upload_and_validate_blueprint(
        {"blueprint_zip": pkg()},
        {"_form_submission": "true", "blueprint_zip.filename": "twin.zip", "blueprint_zip.content_type": "application/zip"},
        HEADERS,
    )

    assert file_status == 400 and "Choose a Twin package ZIP file." in no_file
    assert type_status == 400 and "Select a supported Twin type." in no_type
    assert "Package import needs attention" not in no_file + no_type
    assert not (tmp_path / "blueprint_import" / "packages").exists()


def test_valid_incomplete_candidate_redirects_to_executive_workspace_without_mission(monkeypatch, tmp_path):
    missing_missions = tmp_path / "no-commercial-missions.json"
    monkeypatch.setenv("FLORA_COMMERCIAL_MISSIONS_FILE", str(missing_missions))
    html, status, target = _upload(monkeypatch, tmp_path, records=[{
        "external_id": "OBS-INCOMPLETE",
        "record_class": "observation",
        "truth_class": "evidence_backed",
        "payload": {"statement": "A candidate with identity, scope and evidence still unresolved"},
    }])

    assert status == 200 and "Validation result" in html
    run_id = target.rsplit("/", 1)[-1]
    assert target == f"/blueprint-import/{run_id}"
    workspace, workspace_status = executive_workspace_page(run_id, HEADERS)
    assert workspace_status == 200
    assert "Executive Intelligence Workspace" in workspace
    assert "no Commercial Mission is available" in workspace
    assert "Twin identity and governed scope have not yet been confirmed" in workspace
    assert f"/blueprint-import/{run_id}/review" in workspace
    assert "Review candidate governance" in workspace
    assert "Resolve Twin scope" in workspace
    assert "Inspect import decisions" in workspace
    assert "View package validation" in workspace


def test_semantic_or_technical_validation_failure_does_not_hide_import_action(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    failed, status, _ = upload_and_validate_blueprint(
        {"blueprint_zip": b"not-a-readable-package"},
        {"blueprint_zip.filename": "invalid.zip", "blueprint_zip.content_type": "application/zip"},
        HEADERS,
    )

    assert status == 400
    assert "Package receipt failed" in failed
    landing = digital_twins_landing_page(HEADERS)
    assert "Import Twin" in landing and "href='/blueprint-import'" in landing
