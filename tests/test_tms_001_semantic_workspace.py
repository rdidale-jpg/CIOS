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
    assert "Canonical priority enterprises: 14" in html
    assert "Composed for: Sales Director · Sopra Steria" in html
    assert "2026 telecom regulation/security/infrastructure data is active." in html
    assert "No supported timing conclusion" not in html
    assert html.count("Imported Twin · Candidate") == 1
    assert "Twin composition" in html and "Enterprises" in html and "Opportunities" in html
    assert "Capabilities/offers: 16" in html
    assert "5G SA network slicing" in html
    assert "AI fan companion and fan data product" in html
    assert "Evidence Sources" in html
    assert "Explain this insight" in html
    assert "Offer alignment is incomplete" in html
