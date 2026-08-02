from cios.applications.flora.blueprint_import.executive_workspace import research_gap_brief, twin_readiness
from cios.applications.flora.blueprint_import.intelligence_projection import executive_assessments
from cios.applications.flora.blueprint_import.research_requirements import research_requirements
from cios.applications.flora.blueprint_import.semantic_twin import assemble_semantic_twin, business_collections
from cios.applications.flora.commercial_mission import CommercialMission, EmployerContext


def row(identifier, kind, **payload):
    return {"candidate_record_id": identifier, "original_source_id": identifier,
            "candidate_object_class": kind, "payload": payload}


def twin():
    rows = [row("bbc", "enterprise_twin", name="BBC", enterprise_id="bbc", domain="Media")]
    rows += [row(f"p{i}", "market_participant_twin", name=f"Participant {i}", domain="Media") for i in range(10)]
    rows += [row(f"o{i}", "opportunity_hypothesis", statement=f"Opportunity {i}", affected_enterprises=["BBC"]) for i in range(9)]
    rows += [row(f"ranked-{i}", "ranked_opportunity", statement=f"Ranked {i}") for i in range(9)]
    rows += [row(f"m{i}", "transformation_programme", statement=f"Programme {i}", subject="BBC") for i in range(9)]
    return assemble_semantic_twin(rows)


def test_canonical_identity_counts_do_not_count_ranked_representations_twice():
    value = twin()
    collections = {c.key: c for c in business_collections(value, include_empty=True)}
    assert len(collections["opportunities"].objects) == 9
    readiness = {a.key: a for a in twin_readiness(value)}
    assert readiness["opportunities"].present[1].startswith("9 canonical opportunity")
    assert readiness["market-participants"].present[1].startswith("10 canonical participant")
    assert readiness["major-programmes"].present[1].startswith("9 canonical programme")


def test_translation_is_subject_specific_and_does_not_request_present_fields():
    reqs = research_requirements(twin(), executive_assessments(twin()))
    bbc = next(r for r in reqs if r.aspect == "enterprises" and r.subject == "BBC")
    assert "annual reports" in bbc.source_categories
    assert "organisation description" in bbc.missing_fields
    assert "no pass is inferred" in bbc.acceptance_test


def test_brief_has_business_structure_mission_context_and_traceability_appendix():
    mission = CommercialMission.from_dict("sales-director", {"mission_name": "UK growth", "executive_role": "Sales Director",
        "commercial_objective": "Find pre-procurement demand", "industries": ["Media"], "priority_accounts": ["BBC"],
        "geography": ["United Kingdom"], "interests": ["AI-led reinvention"], "commercial_horizon": "Next 12 months"})
    employer = EmployerContext.from_dict({"organisation": "Example Supplier", "capabilities": ["AI"],
        "offer_portfolio": ["Transformation"], "propositions": ["AI reinvention"], "competitors": ["Competitor"], "partners": ["Partner"]})
    brief = research_gap_brief(twin(), "Telecoms and Media", mission, employer_context=employer)
    for heading in ("Purpose and intended executive decisions", "Active Commercial Mission", "Employer Context",
                    "Current Twin coverage", "Priority for this Commercial Mission", "Broader Industry Twin gaps",
                    "Required structured deliverables", "Remaining known uncertainty", "Appendix — governed traceability"):
        assert heading in brief
    assert "Opportunities: 9 canonical opportunity hypotheses" in brief
    assert "Market Participants: 10 canonical participants" in brief
    assert "Research BBC" in brief
    assert "owner-produced assessment result" not in brief
    assert "legacy_unassessed" not in brief.split("## Appendix", 1)[0]
