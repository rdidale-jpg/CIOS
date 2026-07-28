"""Focused WP2-003 presentation relevance contract checks."""
from types import SimpleNamespace

from cios.applications.flora.blueprint_import.relevance import project_candidate_relevance, relevance_counts
from cios.applications.flora.blueprint_import.twin_governance import TwinIdentityProjection
from cios.applications.flora.blueprint_import.views import _material_conclusions, _promotion_impact


IDENTITY = TwinIdentityProjection("TWIN-1", "industry", "IND-1", "Communications", "industry",
                                  "Communications services", "industry-owner", "1", None, None,
                                  "PKG-1", "recognised")
PACKAGE = SimpleNamespace(package_inspection={"industry": "Communications", "geography": "UK",
                                               "time_horizon": "2026-2028"})


def candidate(**payload):
    return {"candidate_record_id": payload.pop("id", "C-1"), "truth_class": "evidence_backed",
            "validation_status": "accepted", "candidate_object_class": "observation", "payload": payload}


def test_owner_backed_core_and_sub_sector_items_are_primary_eligible():
    common = {"twin_id": "TWIN-1", "supporting_relationship": "governs", "relevance_basis": "Owner classification",
              "evidence_status": "linked", "owner": "analyst"}
    core = project_candidate_relevance(candidate(relevance_status="core", **common), PACKAGE, IDENTITY)
    sub = project_candidate_relevance(candidate(relevance_status="relevant sub-sector", sub_sector="Mobile", **common), PACKAGE, IDENTITY)
    assert core.primary_eligible and sub.primary_eligible
    assert sub.sub_sector_or_domain == "Mobile" and sub.geography == "UK"


def test_adjacent_out_of_scope_and_unresolved_are_never_primary():
    common = {"twin_id": "TWIN-1", "supporting_relationship": "adjacent_to", "relevance_basis": "Package owner annotation",
              "evidence_status": "linked", "owner": "analyst"}
    items = [project_candidate_relevance(candidate(id=status, relevance_status=status, **common), PACKAGE, IDENTITY)
             for status in ("adjacent", "out of scope", "unresolved")]
    assert not any(item.primary_eligible for item in items)
    assert relevance_counts(items)["out of scope"] == 1


def test_labels_and_keywords_do_not_infer_relevance_or_twin_link():
    item = project_candidate_relevance(candidate(statement="Communications mobile market outlook",
                                                 evidence_status="linked"), PACKAGE, IDENTITY)
    assert item.status == "unresolved"
    assert item.proposed_twin_identity is None
    assert "not supplied" in item.unresolved_scope_reason.lower()


def test_explicit_status_without_relationship_remains_ineligible():
    item = project_candidate_relevance(candidate(relevance_status="core", twin_id="TWIN-1",
                                                 relevance_basis="Owner classification", evidence_status="linked"), PACKAGE, IDENTITY)
    assert item.status == "core"
    assert not item.primary_eligible


def test_unknown_status_is_preserved_as_presentation_unresolved():
    item = project_candidate_relevance(candidate(relevance_status="highly_relevant"), PACKAGE, IDENTITY)
    assert item.status == "unresolved"


def test_mixed_industry_render_groups_and_explains_every_statement():
    common = {"twin_id": "TWIN-1", "supporting_relationship": "classified_for", "relevance_basis": "Owner register",
              "evidence_status": "linked", "owner": "analyst", "statement": "Owner statement"}
    pairs = []
    for status, industry in (("core", "Communications"), ("relevant sub-sector", "Communications"),
                             ("adjacent", "Media"), ("out of scope", "Sport"), ("unresolved", "Telecoms")):
        record = candidate(id=status, relevance_status=status, industry=industry, **common)
        pairs.append((record, project_candidate_relevance(record, PACKAGE, IDENTITY)))
    html = _material_conclusions(pairs, "run")
    for heading in ("Core to this Industry Twin", "Relevant sub-sector intelligence",
                    "Adjacent or cross-industry intelligence", "Relevance unresolved", "Out of scope"):
        assert heading in html
    assert html.count("Why is this relevant here?") == 5
    assert html.count("Primary executive conclusion") == 2


def test_quarantined_contradiction_is_not_rendered_as_primary():
    record = candidate(statement="Challenge", relevance_status="core", twin_id="TWIN-1",
                       supporting_relationship="challenges", relevance_basis="Owner register",
                       evidence_status="linked", owner="analyst")
    record.update(validation_status="quarantined", candidate_object_class="contradiction")
    relevance = project_candidate_relevance(record, PACKAGE, IDENTITY)
    html = _material_conclusions([(record, relevance)], "run")
    assert "Provisional — not a primary executive conclusion" in html


def test_promotion_impact_is_broken_down_by_relevance_without_changing_mutations():
    records = [project_candidate_relevance(candidate(id=status, relevance_status=status), PACKAGE, IDENTITY)
               for status in ("core", "adjacent", "unresolved", "out of scope")]
    html = _promotion_impact({"Creates": 2}, {}, 1, 0, records)
    assert "In-scope intelligence proposed for promotion" in html
    assert "Adjacent intelligence retained but not promoted" in html
    assert "Unresolved intelligence requiring review" in html
    assert "Out-of-scope intelligence excluded" in html
    assert "Quarantined intelligence" in html and "New intelligence" in html
