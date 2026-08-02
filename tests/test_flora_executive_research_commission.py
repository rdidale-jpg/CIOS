from cios.applications.flora.blueprint_import.executive_workspace import (
    _research_gaps,
    research_gap_brief,
    twin_readiness,
)
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
    assert "3 market participants require enrichment" in html
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
        "Major Programmes", "Opportunities", "Reinvention Timing", "Evidence, Unknowns and Contradictions",
        "Required Structured Deliverables", "Researcher Acceptance Criteria", "Remaining Known Limitations"), 1)]
    assert [brief.index(heading) for heading in headings] == sorted(brief.index(heading) for heading in headings)
    assert "Mission: Optional name not supplied" in brief and "- Status: Configured" in brief
    assert "- Employer: Example Supplier" in brief and "- Capabilities: AI" in brief
    assert "Mission settings remove nothing" in brief and "### BBC" in brief
    assert "Executive dependency impact: High" in brief
    assert "canonical owner" not in brief.split("## Appendix A", 1)[0].casefold()
