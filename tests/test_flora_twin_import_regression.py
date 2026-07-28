"""Regression contract for the established governed Twin importer entry point."""
from cios.applications.flora.blueprint_import.executive_workspace import executive_workspace_page
from cios.applications.flora.blueprint_import.views import (
    import_blueprint_entry_page,
    upload_and_validate_blueprint,
)
from cios.applications.flora.digital_twins import digital_twins_landing_page
from tests.test_flora_blueprint_import_interface import BAD, HEADERS, pkg


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
    assert "Import Twin" not in digital_twins_landing_page(BAD)


def test_import_route_loads_and_supported_upload_can_be_initiated(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    html, status = import_blueprint_entry_page(HEADERS)

    assert status == 200
    assert "<h1>Import Twin</h1>" in html
    assert "action='/blueprint-import/upload'" in html
    assert "type='file'" in html and "accept='.zip,application/zip'" in html
    assert "Commercial Mission or an existing Twin selection is not required" in html


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
