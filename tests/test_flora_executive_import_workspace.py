"""Acceptance coverage for the executive-first post-import experience."""
from cios.applications.flora.blueprint_import.executive_workspace import executive_workspace_page
from cios.applications.flora.blueprint_import.views import review_page, upload_and_validate_blueprint
from tests.test_flora_blueprint_import_interface import HEADERS, pkg


def _import(monkeypatch, tmp_path, records):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    _, status, target = upload_and_validate_blueprint(
        {"blueprint_zip": pkg(records=records)},
        {"blueprint_zip.filename": "executive.zip", "blueprint_zip.content_type": "application/zip"},
        HEADERS,
    )
    assert status == 200
    return target.rsplit("/", 1)[-1], target


def test_post_import_target_defaults_to_executive_workspace(monkeypatch, tmp_path):
    run_id, target = _import(monkeypatch, tmp_path, [{
        "external_id": "OBS-MARKET", "record_class": "observation", "truth_class": "evidence_backed",
        "payload": {"statement": "Customer adoption is changing the market", "evidence_refs": ["EV-1"]},
    }])
    html, status = executive_workspace_page(run_id, HEADERS)
    assert status == 200 and target == f"/blueprint-import/{run_id}"
    assert "Executive Intelligence Workspace" in html
    assert html.index("Executive understanding") < html.index("Candidate governance")


def test_provisional_composition_missing_mission_and_scope(monkeypatch, tmp_path):
    run_id, _ = _import(monkeypatch, tmp_path, [{
        "external_id": "FACT-COST", "record_class": "fact", "truth_class": "evidence_backed",
        "payload": {"statement": "Financial cost pressure is material"},
    }])
    html, status = executive_workspace_page(run_id, HEADERS)
    assert status == 200
    assert "Executive understanding is provisional because the Twin identity and governed scope have not yet been confirmed." in html
    assert "Personal commercial prioritisation is not yet applied" in html
    assert "Unsupported candidate conclusion" in html
    assert "0 newly governed records" in html


def test_governance_remains_accessible_without_promoting_candidates(monkeypatch, tmp_path):
    run_id, _ = _import(monkeypatch, tmp_path, [{
        "external_id": "UNK-1", "record_class": "unknown", "truth_class": "unknown",
        "payload": {"statement": "Regulatory timing remains unknown"},
    }])
    html, _ = executive_workspace_page(run_id, HEADERS)
    assert f"/blueprint-import/{run_id}/review" in html
    assert "Review candidate governance" in html and "Resolve Twin scope" in html
    review, status = review_page(run_id, HEADERS)
    assert status == 200 and "Review" in review
    assert "Candidate only; not promoted to governed intelligence" in html
