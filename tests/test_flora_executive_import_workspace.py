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
    assert "PILOT" in html and "synthetic-blueprint" in html
    assert "Twin Composition" in html
    assert "Executive understanding" not in html and "Candidate governance" not in html


def test_provisional_composition_resolves_human_supplied_mission_and_scope(monkeypatch, tmp_path):
    run_id, _ = _import(monkeypatch, tmp_path, [{
        "external_id": "FACT-COST", "record_class": "fact", "truth_class": "evidence_backed",
        "payload": {"statement": "Financial cost pressure is material"},
    }])
    html, status = executive_workspace_page(run_id, HEADERS)
    assert status == 200
    assert "pilot-mode" not in html.casefold()
    assert "Sales Director · Sopra Steria" not in html
    health, _ = executive_workspace_page(run_id, HEADERS, view="health")
    assert "Researcher Feedback Report" in health
    assert "business consequence" in health and "evidence reference" in health


def test_governance_remains_accessible_without_promoting_candidates(monkeypatch, tmp_path):
    run_id, _ = _import(monkeypatch, tmp_path, [{
        "external_id": "UNK-1", "record_class": "unknown", "truth_class": "unknown",
        "payload": {"statement": "Regulatory timing remains unknown"},
    }])
    html, _ = executive_workspace_page(run_id, HEADERS)
    assert f"/blueprint-import/{run_id}/health" in html
    assert "Review candidate governance" not in html
    health, _ = executive_workspace_page(run_id, HEADERS, view="health")
    assert f"/blueprint-import/{run_id}/review" in health
    assert "Protected governance actions" in health
    review, status = review_page(run_id, HEADERS)
    assert status == 200 and "Review" in review
    assert "No automatic promotion occurs" in health


def test_semantic_filter_explorer_and_enterprise_dossier(monkeypatch, tmp_path):
    run_id, _ = _import(monkeypatch, tmp_path, [
        {"external_id": "ORG-1", "record_class": "entity", "truth_class": "candidate",
         "payload": {"name": "Example Telecom", "enterprise_id": "example-telecom"}},
        {"external_id": "RAW-1", "record_class": "fact", "truth_class": "candidate",
         "payload": {"value": 30.9, "subject": "Example Telecom"}},
        {"external_id": "OBS-1", "record_class": "observation", "truth_class": "evidence_backed",
         "payload": {"statement": "Network modernisation is increasing operating-model pressure",
                     "subject": "Example Telecom", "evidence_refs": ["EV-1"],
                     "observation_date": "2026-06-30", "confidence": "medium",
                     "domain": "Telecoms", "business_consequence": "Operating-model cost and delivery risk increase."}},
        {"external_id": "UNK-1", "record_class": "unknown", "truth_class": "unknown",
         "payload": {"statement": "Programme ownership remains unknown", "subject": "Example Telecom"}},
    ])
    html, status = executive_workspace_page(run_id, HEADERS)
    assert status == 200
    assert "Network modernisation is increasing operating-model pressure" not in html
    assert "<h4>30.9</h4>" not in html
    assert "Metric meaning, unit, period, subject, source or significance is incomplete" not in html
    assert "No interpreted material change" not in html
    health, _ = executive_workspace_page(run_id, HEADERS, view="health")
    assert "Researcher Feedback Report" in health
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


def test_business_projection_uses_canonical_wrappers_and_supported_domains():
    candidates = [
        {"candidate_record_id": "ent", "candidate_object_class": "enterprise", "payload": {"name": "Alpha", "canonical_id": "alpha"}},
        {"candidate_record_id": "twin", "candidate_object_class": "enterprise_twin", "payload": {"name": "Alpha", "enterprise_id": "alpha", "domain": "Telecoms"}},
        {"candidate_record_id": "opp", "candidate_object_class": "opportunity_hypothesis", "payload": {"statement": "Supported opportunity", "domain": "Media"}},
        {"candidate_record_id": "rank", "candidate_object_class": "ranked_opportunity", "payload": {"statement": "Ranked wrapper", "domain": "Media"}},
        {"candidate_record_id": "co-located", "candidate_object_class": "observation", "truth_class": "evidence_backed", "payload": {
            "statement": "A supported change", "subject": "Alpha", "domain": "Telecoms",
            "business_consequence": "Investment sequencing is affected.", "evidence_refs": ["EV-1"],
            "confidence": "high", "observation_date": "2026-07-01"}},
    ]
    twin = assemble_semantic_twin(candidates)
    all_counts = {c.key: len(c.objects) for c in business_collections(twin)}
    assert all_counts["enterprises"] == 1 and all_counts["opportunities"] == 1
    assert len(next(c for c in business_collections(twin, domain="telecoms") if c.key == "insights").objects) == 1
    assert not any(c.key == "insights" for c in business_collections(twin, domain="cross-domain"))
    assert {o.record_id for o in twin.objects} == {"ent", "twin", "opp", "rank", "co-located"}


def test_material_insight_contract_excludes_labels_sources_and_unsupported_consequence():
    twin = assemble_semantic_twin([
        {"candidate_record_id": "source", "candidate_object_class": "evidence", "payload": {"title": "Annual report"}},
        {"candidate_record_id": "entity", "candidate_object_class": "entity", "payload": {"name": "Alpha"}},
        {"candidate_record_id": "cap", "candidate_object_class": "capability_offer", "payload": {"name": "Cloud migration"}},
        {"candidate_record_id": "raw", "candidate_object_class": "observation", "payload": {"statement": "Demand changed", "subject": "Alpha", "domain": "Media", "evidence_refs": ["EV"]}},
    ])
    insights = next((c.objects for c in business_collections(twin, include_empty=True) if c.key == "insights"), ())
    assert insights == ()
    assert len(twin.objects) == 4


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
    assert "Explain this insight" not in collection
    assert "Improve customer retention" in collection
