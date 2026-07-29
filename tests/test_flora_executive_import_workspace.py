"""Acceptance coverage for the executive-first post-import experience."""
from cios.applications.flora.blueprint_import.executive_workspace import executive_workspace_page
from cios.applications.flora.blueprint_import.semantic_twin import assemble_semantic_twin, business_collections
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
    assert "Imported Twin · Candidate" in html
    assert "Twin composition" in html
    assert html.index("Executive understanding") < html.index("Candidate governance")


def test_provisional_composition_resolves_human_supplied_mission_and_scope(monkeypatch, tmp_path):
    run_id, _ = _import(monkeypatch, tmp_path, [{
        "external_id": "FACT-COST", "record_class": "fact", "truth_class": "evidence_backed",
        "payload": {"statement": "Financial cost pressure is material"},
    }])
    html, status = executive_workspace_page(run_id, HEADERS)
    assert status == 200
    assert "This understanding is provisional because the Twin identity and governed scope have not yet been confirmed." in html
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
    assert "Imported Twin · Candidate" in html


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
    assert "Explore Example Telecom" in html
    explorer, status = executive_workspace_page(run_id, HEADERS, view="explore", collection="enterprises")
    assert status == 200 and "Advanced aspect coverage" in explorer and "Example Telecom" in explorer
    dossier, status = executive_workspace_page(run_id, HEADERS, view="enterprise", enterprise_id="example-telecom")
    assert status == 200
    assert "Enterprise dossier" in dossier
    assert "EV-1" in dossier and "2026-06-30" in dossier
    assert "Programme ownership remains unknown" in dossier
    assert "Review candidate governance" in dossier


def test_business_projection_is_deterministic_immutable_and_reconciled():
    candidates = [
        {"candidate_record_id": "1", "original_source_id": "ENT-1", "candidate_object_class": "enterprise_twin", "payload": {"name": "Alpha", "enterprise_id": "alpha"}},
        {"candidate_record_id": "2", "original_source_id": "OPP-1", "candidate_object_class": "opportunity_hypothesis", "payload": {"statement": "Modernise channels"}},
        {"candidate_record_id": "3", "original_source_id": "X-1", "candidate_object_class": "control_body", "payload": {"title": "Regulator"}},
    ]
    before = repr(candidates)
    twin = assemble_semantic_twin(candidates)
    collections = business_collections(twin)
    assert [(c.key, len(c.objects)) for c in collections] == [("enterprises", 1), ("opportunities", 1), ("other", 1)]
    assert sum(len(c.objects) for c in collections) == len(twin.objects)
    assert {o.record_id for c in collections for o in c.objects} == {"1", "2", "3"}
    assert repr(candidates) == before


def test_tile_navigation_and_progressive_explanation(monkeypatch, tmp_path):
    run_id, _ = _import(monkeypatch, tmp_path, [{
        "external_id": "OPP-1", "record_class": "opportunity_hypothesis", "truth_class": "candidate",
        "payload": {"statement": "Improve customer retention", "evidence_refs": ["EV-1"], "confidence": "medium"},
    }])
    overview, _ = executive_workspace_page(run_id, HEADERS)
    assert f"/blueprint-import/{run_id}/explore?collection=opportunities" in overview
    assert "Evidence:</strong>" not in overview.split("<section class='card' id='composition'>", 1)[1].split("</section>", 1)[0]
    collection, _ = executive_workspace_page(run_id, HEADERS, view="explore", collection="opportunities")
    assert "Improve customer retention" in collection
    assert "Explain this insight" in collection and "Confidence:" in collection and "Lineage:" in collection
