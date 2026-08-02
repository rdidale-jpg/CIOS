from __future__ import annotations

import io
import json
import threading
import zipfile
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path

from cios.applications.flora.blueprint_import.registry import BlueprintPackageRegistry
from cios.applications.flora.blueprint_import.views import MAX_UPLOAD_BYTES, approve_and_promote, upload_and_validate_blueprint
from cios.applications.flora.pilot_import import PILOT_IMPORT_ACTOR, PILOT_IMPORT_WORKSPACE, pilot_import_bypass_enabled, pilot_import_mode
from cios.applications.flora.access import (
    COMMERCIAL_CONTEXT_EDIT, COMMERCIAL_CONTEXT_VIEW, BLUEPRINT_PROMOTE_PERMISSION,
    commercial_context_authorisation, flora_roles,
)
from tests.test_flora_blueprint_import_validation import pkg

FIELDS = {"expected_type": "industry", "blueprint_zip.filename": "pilot.zip", "blueprint_zip.content_type": "application/zip", "_form_submission": "true"}


def pilot(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_ENVIRONMENT", "pilot")
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("FLORA_PILOT_IMPORT_BYPASS", raising=False)
    monkeypatch.delenv("FLORA_PILOT_AUTO_SIGN_IN", raising=False)


def multipart(package: bytes, expected_type: str = "industry") -> tuple[bytes, str]:
    boundary = "----flora-vertical-boundary"
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"expected_type\"\r\n\r\n{expected_type}\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"blueprint_zip\"; filename=\"pilot.zip\"\r\n"
            "Content-Type: application/zip\r\n\r\n").encode() + package + f"\r\n--{boundary}--\r\n".encode()
    return body, boundary


def request(server, method, path, body=None, headers=None):
    conn = HTTPConnection("127.0.0.1", server.server_port)
    conn.request(method, path, body=body, headers=headers or {})
    response = conn.getresponse(); payload = response.read().decode(errors="replace")
    result = response.status, dict(response.getheaders()), payload
    conn.close()
    return result


def test_one_canonical_mode_and_conflicting_legacy_modes_fail(monkeypatch):
    monkeypatch.setenv("FLORA_ENVIRONMENT", "production")
    assert pilot_import_bypass_enabled() is False
    monkeypatch.setenv("FLORA_ENVIRONMENT", "pilot")
    assert pilot_import_bypass_enabled() is True
    monkeypatch.setenv("FLORA_PILOT_IMPORT_BYPASS", "true")
    assert pilot_import_bypass_enabled() is False
    assert "conflicting deprecated pilot mode" in pilot_import_mode().conflict


def test_deployed_equivalent_pilot_route_imports_candidate_to_executive_workspace(monkeypatch, tmp_path):
    import cios.applications.flora.web.app as web_app
    import cios.applications.flora.blueprint_import.views as import_views
    pilot(monkeypatch, tmp_path)
    repository = str(Path(__file__).resolve().parents[1])
    assert str(web_app.__file__).startswith(repository)
    assert str(import_views.__file__).startswith(repository)
    server = ThreadingHTTPServer(("127.0.0.1", 0), web_app.FloraWebHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    try:
        status, _, landing = request(server, "GET", "/digital-twins")
        assert status == 200 and "href='/blueprint-import'>Import Twin" in landing
        assert landing.count("href='/blueprint-import'") == 1
        assert "Import a Twin package to create a candidate for review" in landing
        assert "application_module=cios.applications.flora.web.app" in landing
        assert "pilot_import_mode=active" in landing
        assert "import_route_owner=cios.applications.flora.digital_twins.digital_twins_landing_page" in landing
        assert "import_route_implementation=pilot-candidate-import-v1" in landing
        status, _, form = request(server, "GET", "/blueprint-import")
        assert status == 200 and 'name="expected_type"' not in form  # templates use canonical single quotes
        assert "name='expected_type'" in form and "Industry" in form and "name='blueprint_zip'" in form
        assert "method='post' action='/blueprint-import/upload' enctype='multipart/form-data'" in form
        assert "flora-import-deployment:" in form
        body, boundary = multipart(pkg())
        status, headers, _ = request(server, "POST", "/blueprint-import/upload", body, {
            "Content-Type": f"multipart/form-data; boundary={boundary}", "Content-Length": str(len(body))})
        assert status == 303
        target = headers["Location"]
        assert target.startswith("/blueprint-import/bpi-run-")
        status, _, workspace = request(server, "GET", target)
        assert status == 200 and "Executive Intelligence" in workspace
        assert "Candidate governance" in workspace and "/review" in workspace
    finally:
        server.shutdown(); server.server_close(); thread.join()

    record = BlueprintPackageRegistry().list()[0]
    summary = json.loads((tmp_path / "blueprint_import" / "staging" / record.import_run_id / "summary.json").read_text())
    assert record.byte_count == len(pkg()) and record.received_by == PILOT_IMPORT_ACTOR
    assert record.workspace_id == PILOT_IMPORT_WORKSPACE
    assert record.package_inspection["authentication_mode"] == "pilot"
    assert summary["files_inspected"] and summary["candidate_records_staged"] > 0
    assert not (tmp_path / "memory" / "observations.jsonl").exists()
    events = (tmp_path / "blueprint_import" / "audit" / "events.jsonl").read_text()
    assert "package_received" in events and "pilot_import_bypass_result" in events


def test_deployment_endpoint_identifies_canonical_import_runtime(monkeypatch, tmp_path):
    import cios.applications.flora.web.app as web_app
    pilot(monkeypatch, tmp_path)
    monkeypatch.setenv("RENDER_GIT_COMMIT", "abc123deployed")
    web_app.application_revision.cache_clear()
    server = ThreadingHTTPServer(("127.0.0.1", 0), web_app.FloraWebHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    try:
        status, _, body = request(server, "GET", "/deployment")
        payload = json.loads(body)
        assert status == 200
        assert payload["commit_sha"] == "abc123deployed"
        assert payload["application_module"] == "cios.applications.flora.web.app"
        assert payload["pilot_import_mode"] == "active"
        assert payload["import_route_owner"] == "cios.applications.flora.digital_twins.digital_twins_landing_page"
        assert payload["import_route_implementation"] == "pilot-candidate-import-v1"
    finally:
        server.shutdown(); server.server_close(); thread.join()
        web_app.application_revision.cache_clear()


def test_pilot_configure_save_and_recompose_uses_narrow_actor_scope(monkeypatch, tmp_path):
    """Exercise the configured HTTP entry point, not a view-only test double."""
    import cios.applications.flora.web.app as web_app
    pilot(monkeypatch, tmp_path)
    mission_file = tmp_path / "commercial-missions.json"
    employer_file = tmp_path / "employer-contexts.json"
    monkeypatch.setenv("FLORA_COMMERCIAL_MISSIONS_FILE", str(mission_file))
    monkeypatch.setenv("FLORA_EMPLOYER_CONTEXTS_FILE", str(employer_file))
    _, status, target = upload_and_validate_blueprint({"blueprint_zip": pkg()}, FIELDS, {})
    assert status == 200
    run_id = target.rsplit("/", 1)[-1]
    server = ThreadingHTTPServer(("127.0.0.1", 0), web_app.FloraWebHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    try:
        status, _, workspace = request(server, "GET", f"{target}?domain=technology")
        assert status == 200 and "Commercial Mission not configured" in workspace
        assert f"/blueprint-import/{run_id}/mission?domain=technology" in workspace
        status, _, settings = request(server, "GET", f"/blueprint-import/{run_id}/mission?domain=technology")
        assert status == 200 and "Access denied" not in settings
        assert "Commercial Mission" in settings and "Employer Context" in settings
        assert "Back to Twin Map" in settings and "Cancel" in settings
        form = ("mission_name=UK+growth&executive_role=Director&commercial_objective=Find+evidenced+demand"
                "&industries=Telecoms&interests=technology&target_customers=Example+Account"
                "&employer_organisation=Example+Supplier&employer_capabilities=Advisory"
                "&employer_competitors=&employer_partners=&save_scope=both&return_domain=technology")
        status, response_headers, _ = request(server, "POST", f"/blueprint-import/{run_id}/mission", form, {
            "Content-Type": "application/x-www-form-urlencoded", "Content-Length": str(len(form))})
        assert status == 303
        assert response_headers["Location"] == f"/blueprint-import/{run_id}?domain=technology"
        status, _, recomposed = request(server, "GET", response_headers["Location"])
        assert status == 200 and "Commercial Mission: UK growth" in recomposed
        assert "Commercial Mission not configured" not in recomposed
        status, _, brief = request(server, "GET", f"/blueprint-import/{run_id}/research-brief")
        assert status == 200 and "UK growth" in brief and "Example Supplier" in brief
    finally:
        server.shutdown(); server.server_close(); thread.join()

    mission_data = json.loads(mission_file.read_text())
    employer_data = json.loads(employer_file.read_text())
    assert list(mission_data) == [PILOT_IMPORT_ACTOR]
    assert list(employer_data) == [PILOT_IMPORT_ACTOR]
    assert "organisation" not in mission_data[PILOT_IMPORT_ACTOR]
    assert "mission_name" not in employer_data[PILOT_IMPORT_ACTOR]
    twin_files = list((tmp_path / "blueprint_import").rglob("*.json"))
    assert all("UK growth" not in path.read_text() for path in twin_files)

    view = commercial_context_authorisation({}, COMMERCIAL_CONTEXT_VIEW, PILOT_IMPORT_WORKSPACE)
    edit = commercial_context_authorisation({}, COMMERCIAL_CONTEXT_EDIT, PILOT_IMPORT_WORKSPACE)
    isolated = commercial_context_authorisation({}, COMMERCIAL_CONTEXT_EDIT, "another-workspace")
    assert view.decision == edit.decision == "allowed"
    assert isolated.decision == "denied" and isolated.failed_stage == "scope isolation"
    assert BLUEPRINT_PROMOTE_PERMISSION not in flora_roles({})


def test_secure_mode_commercial_context_remains_denied_with_diagnostic(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_ENVIRONMENT", "production")
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    decision = commercial_context_authorisation({}, COMMERCIAL_CONTEXT_VIEW, PILOT_IMPORT_WORKSPACE)
    assert decision.decision == "denied"
    assert decision.failed_stage == "actor resolution"
    assert decision.required_capability == COMMERCIAL_CONTEXT_VIEW


def test_validation_and_archive_safety_precede_identity(monkeypatch, tmp_path):
    pilot(monkeypatch, tmp_path)
    html, status, _ = upload_and_validate_blueprint({"blueprint_zip": b"not a zip"}, FIELDS, {})
    assert status == 400 and "Stage failed: Package received" in html
    assert "not applicable in pilot import mode" in html and "No active workspace" not in html

    unsafe = io.BytesIO()
    with zipfile.ZipFile(unsafe, "w") as archive: archive.writestr("../escape.json", "{}")
    html, status, _ = upload_and_validate_blueprint({"blueprint_zip": unsafe.getvalue()}, FIELDS, {})
    assert status == 400 and "Unsafe package member path" in html

    monkeypatch.setattr("cios.applications.flora.blueprint_import.views.MAX_UPLOAD_BYTES", 3)
    html, status, _ = upload_and_validate_blueprint({"blueprint_zip": b"1234"}, FIELDS, {})
    assert status == 400 and "upload limit" in html


def test_form_validation_secure_mode_and_promotion_boundary(monkeypatch, tmp_path):
    pilot(monkeypatch, tmp_path)
    html, status, _ = upload_and_validate_blueprint({}, {**FIELDS, "expected_type": "industry"}, {})
    assert status == 400 and "Choose a Twin package" in html
    html, status, _ = upload_and_validate_blueprint({"blueprint_zip": pkg()}, {**FIELDS, "expected_type": ""}, {})
    assert status == 400 and "Select a supported Twin type" in html
    _, status, target = upload_and_validate_blueprint({"blueprint_zip": pkg()}, FIELDS, {})
    assert status == 200
    _, promotion_status = approve_and_promote(target.rsplit("/", 1)[-1], {}, {})
    assert promotion_status == 403

    monkeypatch.setenv("FLORA_ENVIRONMENT", "production")
    _, status, _ = upload_and_validate_blueprint({"blueprint_zip": pkg()}, FIELDS, {})
    assert status == 403
