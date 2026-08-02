from cios.applications.flora.blueprint_import.executive_workspace import (
    _research_gaps,
    research_gap_brief,
    twin_readiness,
    validate_research_commission_markdown,
)
from cios.applications.flora.blueprint_import.intelligence_projection import executive_assessments
from cios.applications.flora.blueprint_import.research_requirements import participant_classification, research_requirements
from cios.applications.flora.blueprint_import.semantic_twin import assemble_semantic_twin
from cios.applications.flora.commercial_mission import CommercialMission, EmployerContext


def _row(identifier, kind, **payload):
    return {"candidate_record_id": identifier, "original_source_id": identifier,
            "candidate_object_class": kind, "payload": payload}


def _twin():
    rows = [_row("bbc", "enterprise_twin", name="BBC", enterprise_id="bbc", domain="Media")]
    rows += [_row(f"participant-{i}", "market_participant_twin", name=f"Participant {i}", domain="Media") for i in range(3)]
    rows += [_row(f"programme-{i}", "transformation_programme", statement=f"Programme {i}", subject="BBC") for i in range(2)]
    rows += [_row(f"opportunity-{i}", "opportunity_hypothesis", statement=f"Opportunity {i}", affected_enterprises=["BBC"]) for i in range(4)]
    return assemble_semantic_twin(rows)


def _mission():
    return CommercialMission.from_dict("director", {"executive_role": "Sales Director",
        "commercial_objective": "Pre-procurement opportunities", "geography": ["United Kingdom"],
        "industries": ["Media"], "interests": ["Digital transformation"],
        "commercial_horizon": "12–24 months", "priority_accounts": ["BBC"]})


def test_collection_gaps_use_canonical_collection_counts_and_progressive_traceability():
    twin = _twin()
    html = _research_gaps(twin, "run-1", _mission())
    assert "1 enterprise profiles require enrichment" in html
    assert "3 market participant concepts require enrichment or classification" in html
    assert "2 major-programme hypotheses require enrichment" in html
    assert "4 opportunity hypotheses require enrichment" in html
    assert "Inspect all 1 affected subjects" in html
    assert "Why this matters" in html and "Executive dependency impact" in html
    assert "<details><summary>Architectural traceability</summary>" in html
    assert all(aspect.bars is None for aspect in twin_readiness(twin))

def test_issue_ready_brief_has_fixed_business_structure_complete_scope_and_appendix():
    employer = EmployerContext.from_dict({"organisation": "Example Supplier", "capabilities": ["AI"],
        "offer_portfolio": ["Transformation"], "competitors": ["Rival"], "partners": ["Partner"]})
    brief = research_gap_brief(_twin(), "Media", _mission(), employer_context=employer)
    headings = [f"## {i}. {name}" for i, name in enumerate(("Executive Purpose", "Commercial Context", "Twin Summary",
        "Complete Research Commission", "Mission Emphasis", "Industry Overview", "Enterprises", "Market Participants",
        "Major Programmes", "Opportunities", "Reinvention Timing", "Evidence Requirements", "Unknowns and Contradictions",
        "Required Structured Deliverables", "Researcher Acceptance Criteria", "Remaining Known Limitations"), 1)]
    assert [brief.index(heading) for heading in headings] == sorted(brief.index(heading) for heading in headings)
    assert "Mission: Optional name not supplied" in brief and "- Status: Configured" in brief
    assert "- Employer: Example Supplier" in brief and "- Capabilities: AI" in brief
    assert "Mission settings remove nothing" in brief and "### BBC" in brief
    assert "Executive dependency impact: High" in brief
    assert "canonical owner" not in brief.split("## Appendix A", 1)[0].casefold()


def test_classification_gate_and_subject_type_language_do_not_guess_from_names():
    rows = [
        _row("cloud-category", "market_participant_twin", name="Hyperscale cloud platforms",
             participant_type="participant_category"),
        _row("venue-capability", "market_participant_twin", name="EE / BT venue connectivity capability",
             participant_type="capability"),
        _row("ambiguous", "market_participant_twin", name="Looks Like A Company"),
        _row("regulator", "enterprise_twin", name="Ofcom", enterprise_id="ofcom",
             organisational_form="regulator"),
        _row("company", "enterprise_twin", name="BT Group", enterprise_id="bt",
             organisational_form="company"),
    ]
    twin = assemble_semantic_twin(rows)
    participants = twin.of_kind("market_participant_twin")
    assert [participant_classification(row) for row in participants] == [
        "participant category", "capability", "unresolved identity"]
    requirements = research_requirements(twin, executive_assessments(twin))
    by_subject = {row.subject: row.missing_fields for row in requirements}
    assert "category definition" in by_subject["Hyperscale cloud platforms"]
    assert "capability definition" in by_subject["EE / BT venue connectivity capability"]
    assert "identity resolution" in by_subject["Looks Like A Company"]
    assert "statutory mandate" in by_subject["Ofcom"] and "profitability" not in by_subject["Ofcom"]
    assert "profitability" in by_subject["BT Group"] and "statutory mandate" not in by_subject["BT Group"]


def test_markdown_validation_fails_closed_on_truncation_and_empty_heading():
    brief = research_gap_brief(_twin(), "Media", _mission())
    validate_research_commission_markdown(brief)
    import pytest
    with pytest.raises(ValueError, match="empty heading"):
        validate_research_commission_markdown(brief + "##\n")
