from cios.applications.flora.blueprint_import.executive_workspace import (
    _enterprise_completeness, _opportunities, _pressure, _reinvention_themes,
)
from cios.applications.flora.blueprint_import.semantic_twin import (
    assemble_semantic_twin, business_collections, executive_insight_eligible,
)


def _twin():
    return assemble_semantic_twin([
        {"candidate_record_id": "ent", "candidate_object_class": "enterprise_twin", "payload": {"name": "BBC", "enterprise_id": "bbc", "description": "The BBC is the UK's public-service broadcaster.", "domain": "Media"}},
        {"candidate_record_id": "change", "original_source_id": "CH-1", "candidate_object_class": "transformation_programme", "payload": {"statement": "BBC distribution migration must complete", "subject": "BBC", "domain": "Media", "business_consequence": "Delay would increase duplicated distribution cost.", "evidence_refs": ["SRC-1"], "confidence": "high", "deadline": "2027-12-31"}},
        {"candidate_record_id": "opp", "candidate_object_class": "opportunity_hypothesis", "payload": {"statement": "Modernise audience distribution", "affected_enterprises": ["BBC"], "client_problem": "Duplicated distribution estates", "domain": "Media", "evidence_refs": ["SRC-1"], "confidence": "medium", "why_now": "Migration deadline is 2027-12-31"}},
        {"candidate_record_id": "src", "original_source_id": "SRC-1", "candidate_object_class": "evidence", "payload": {"title": "BBC annual report", "publisher": "BBC", "publication_date": "2026-07-01"}},
    ])


def test_distinct_enterprise_collection_reconciles_with_domain_count():
    twin = _twin()
    assert len(twin.enterprises) == len(next(c for c in business_collections(twin) if c.key == "enterprises").objects) == 1
    assert len(next(c for c in business_collections(twin, domain="media") if c.key == "enterprises").objects) == 1


def test_first_class_opportunity_does_not_invent_supplier_fit():
    html = _opportunities(_twin(), "run", None)
    assert "Commercial Opportunities" in html and "Duplicated distribution estates" in html
    assert "supplier fit" not in html.casefold() and "offer alignment" not in html.casefold()


def test_supported_theme_and_dated_pressure_are_projected():
    twin = _twin()
    assert "Technology and infrastructure" in _reinvention_themes(twin, "run")
    pressure = _pressure(twin, "run")
    assert "Pressure and Urgency" in pressure and "2027-12-31" in pressure


def test_source_title_and_twin_scope_are_not_insights():
    twin = _twin()
    source = next(o for o in twin.objects if o.kind == "evidence")
    assert not executive_insight_eligible(source)
    assert all(o.subject != "Twin scope" for o in twin.objects if executive_insight_eligible(o))


def test_completeness_has_every_deterministic_aspect_and_no_score():
    aspects = _enterprise_completeness(_twin().enterprises[0], None)
    assert len(aspects) == 14
    assert {a.state for a in aspects} <= {"Complete enough for executive use", "Partial", "Insufficient", "Not applicable"}
    procurement = next(a for a in aspects if a.name == "Known procurements")
    assert procurement.state == "Insufficient" and "No explicit procurement" in procurement.missing[0]
