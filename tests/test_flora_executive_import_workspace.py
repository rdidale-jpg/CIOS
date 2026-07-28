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


def test_provisional_composition_resolves_human_supplied_mission_and_scope(monkeypatch, tmp_path):
    run_id, _ = _import(monkeypatch, tmp_path, [{
        "external_id": "FACT-COST", "record_class": "fact", "truth_class": "evidence_backed",
        "payload": {"statement": "Financial cost pressure is material"},
    }])
    html, status = executive_workspace_page(run_id, HEADERS)
    assert status == 200
    assert "Executive understanding is provisional because the Twin identity and governed scope have not yet been confirmed." in html
    assert "Composed for: Sales Director · Sopra Steria" in html
    assert "human-supplied operational context" in html
    assert "Offer alignment is incomplete" in html
    assert "No explicit Evidence reference" in html


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
    assert "Candidate intelligence" in html


def test_semantic_filter_explorer_and_enterprise_dossier(monkeypatch, tmp_path):
    run_id, _ = _import(monkeypatch, tmp_path, [
        {"external_id": "ORG-1", "record_class": "entity", "truth_class": "candidate",
         "payload": {"name": "Example Telecom", "enterprise_id": "example-telecom"}},
        {"external_id": "RAW-1", "record_class": "fact", "truth_class": "candidate",
         "payload": {"value": 30.9, "subject": "Example Telecom"}},
        {"external_id": "OBS-1", "record_class": "observation", "truth_class": "evidence_backed",
         "payload": {"statement": "Network modernisation is increasing operating-model pressure",
                     "subject": "Example Telecom", "evidence_refs": ["EV-1"],
                     "observation_date": "2026-06-30", "confidence": "medium"}},
        {"external_id": "UNK-1", "record_class": "unknown", "truth_class": "unknown",
         "payload": {"statement": "Programme ownership remains unknown", "subject": "Example Telecom"}},
    ])
    html, status = executive_workspace_page(run_id, HEADERS)
    assert status == 200
    assert "Network modernisation is increasing operating-model pressure" in html
    assert "<h4>30.9</h4>" not in html
    assert "Metric meaning, unit, period, subject, source or significance is incomplete" in html
    assert "Open Enterprise Intelligence dossier" in html
    explorer, status = executive_workspace_page(run_id, HEADERS, view="explore")
    assert status == 200 and "Aspect coverage" in explorer and "Example Telecom" in explorer
    dossier, status = executive_workspace_page(run_id, HEADERS, view="enterprise", enterprise_id="example-telecom")
    assert status == 200
    assert "Enterprise Intelligence dossier" in dossier
    assert "EV-1" in dossier and "2026-06-30" in dossier
    assert "Programme ownership remains unknown" in dossier
    assert "Review candidate governance" in dossier
