from cios.applications.flora.blueprint_import.executive_workspace import (
    _assessment_state_label, _research_gaps,
)
from cios.applications.flora.blueprint_import.intelligence_projection import executive_assessments
from cios.applications.flora.blueprint_import.research_requirements import (
    assessment_field_disposition, research_requirements,
)
from cios.applications.flora.blueprint_import.semantic_twin import assemble_semantic_twin, business_collections


def _candidate_twin():
    return assemble_semantic_twin([
        {"candidate_record_id": "opp", "candidate_object_class": "opportunity_hypothesis",
         "governance_status": "candidate", "source_file": "records/opportunities.ndjson", "payload": {"title": "Modernise access operations",
         "client_problem": "Manual fulfilment", "business_unit": "Operations",
         "buyer": "COO", "procurement_status": "Shaping", "procurement_timing": "2027",
         "evidence_refs": ["SRC-1"], "confidence": "medium"}},
        {"candidate_record_id": "ra", "candidate_object_class": "ai_reinvention_assessment",
         "governance_status": "candidate", "source_file": "records/assessments.ndjson", "payload": {"title": "Access operations",
         "summary": "Manual operating model", "ai_disruption_mechanism": "Agentic fulfilment",
         "timing": "2027", "evidence_refs": ["SRC-1"]}},
    ])


def test_candidate_owner_boundary_and_reinvention_output_are_distinct():
    assessments = {row.key: row for row in executive_assessments(_candidate_twin())}
    assert assessments["opportunities"].state == "assessment_pending_governance"
    assert assessments["reinvention-timing"].state == "owner_assessment_supplied_candidate"
    assert _assessment_state_label(assessments["opportunities"].state) == \
        "Intelligence supplied; owner assessment pending governance"
    assert "No owner-produced assessment supplied" not in assessments["opportunities"].evidence_source


def test_present_unassessed_field_is_not_recommissioned_but_absent_field_is():
    twin = _candidate_twin()
    projection = next(row for row in executive_assessments(twin) if row.key == "opportunities")
    opportunity = next(c for c in business_collections(twin) if c.key == "opportunities").objects
    assert assessment_field_disposition("client problem", opportunity, projection) == "source_field_present_unassessed"
    assert assessment_field_disposition("competition", opportunity, projection) == "source_field_absent"
    requirement = next(row for row in research_requirements(twin, executive_assessments(twin))
                       if row.aspect == "opportunities")
    assert "client problem" not in requirement.missing_fields
    assert "competition" in requirement.missing_fields
    html = _research_gaps(twin, "run", None)
    assert "Intelligence supplied; owner assessment pending governance" in html


def test_opportunity_uses_canonical_title_and_reinvention_collection_is_populated():
    twin = _candidate_twin()
    opportunity = next(c for c in business_collections(twin) if c.key == "opportunities").objects[0]
    reinvention = next(c for c in business_collections(twin) if c.key == "reinvention-assessments")
    assert opportunity.subject == "Modernise access operations"
    assert opportunity.subject != "Twin scope"
    assert len(reinvention.objects) == 1
