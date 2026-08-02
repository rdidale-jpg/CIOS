from cios.applications.flora.blueprint_import.views import upload_and_validate_blueprint
from cios.applications.flora.blueprint_import.executive_workspace import executive_workspace_page
from tests.test_tms_001_governed_import_lifecycle import FIXTURE, HEADERS


def test_tms_canonical_semantics_relationships_and_executive_intelligence(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    _, status, target = upload_and_validate_blueprint(
        {"blueprint_zip": FIXTURE.read_bytes()},
        {"blueprint_zip.filename": FIXTURE.name, "blueprint_zip.content_type": "application/zip", "expected_type": "industry"}, HEADERS)
    assert status == 200
    run_id = target.rsplit("/", 1)[-1]
    html, status = executive_workspace_page(run_id, HEADERS)
    assert status == 200
    assert "PILOT" in html and "Telecommunications, Media and Sport Industry Twin" in html
    assert "Twin Composition" not in html
    assert "<h3>Market Participants</h3>" in html
    assert "<h3>Opportunities</h3>" in html
    assert "Evidence Sources" not in html
    assert all(lens in html for lens in ("All Twin", "Telecoms", "Media", "Sport", "Cross-domain"))
    assert "Explain this insight" not in html
    assert "Deterministic package validation" not in html
    health, status = executive_workspace_page(run_id, HEADERS, view="health")
    assert status == 200 and "Research Gaps" in health
    assert "Deterministic package validation" not in health
    advanced, status = executive_workspace_page(run_id, HEADERS, view="diagnostics")
    assert status == 200 and "Canonical priority enterprises: 14" in advanced
    assert "Deterministic package validation" in advanced and "Researcher Feedback Report" in advanced
