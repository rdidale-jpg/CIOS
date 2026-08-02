"""Focused acceptance contract for the researcher-ready commissioning handoff."""
import re

from cios.applications.flora.blueprint_import.executive_workspace import (
    _mission_indicator, _mission_prioritised, _research_gaps, research_gap_brief, twin_readiness,
)
from cios.applications.flora.blueprint_import.intelligence_projection import executive_assessments
from cios.applications.flora.blueprint_import.research_requirements import research_requirements
from cios.applications.flora.blueprint_import.semantic_twin import assemble_semantic_twin
from cios.applications.flora.commercial_mission import (
    EmployerContext, resolve_commercial_context, save_commercial_context,
)

HEADERS = {"X-Flora-User": "handoff-user"}


def twin():
    rows = []
    for name, domain in (("BT Group", "Telecommunications"), ("BBC", "Media"), ("ITV", "Media"), ("Other Co", "Sport")):
        rows.append({"candidate_record_id": name.lower(), "candidate_object_class": "enterprise_twin",
                     "payload": {"name": name, "enterprise_id": name.lower(), "domain": domain}})
    rows.append({"candidate_record_id": "bt-programme", "candidate_object_class": "transformation_programme",
                 "payload": {"name": "Network renewal", "subject": "BT Group", "domain": "Telecommunications",
                             "expected_horizon": "12–24 months"}})
    rows.append({"candidate_record_id": "cloud", "candidate_object_class": "market_participant_twin",
                 "payload": {"name": "Google Cloud", "domain": "Technology"}})
    return assemble_semantic_twin(rows)


def values():
    return ({"executive_role": "Sales Director", "commercial_objective": "Pre-procurement opportunities",
             "geography": "United Kingdom", "industries": "Media, telecommunications, MEDIA",
             "commercial_horizon": "12–24 months", "interests": ["Consulting", "AI", "Cloud"],
             "priority_accounts": "BT Group, BBC, ITV", "target_customers": "BT Group",
             "relevant_business_units": "Openreach", "objectives": ["Partner opportunities"]},
            {"organisation": "Sopra Steria",
             "capabilities": "Digital transformation, cloud, data, AI, managed services, CLOUD",
             "competitors": "Accenture, Cap Gemini, IBM", "partners": "", "offer_portfolio": ""})


def test_every_key_field_persists_resolves_and_exports(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path)); monkeypatch.setenv("FLORA_TRUST_PROXY_HEADERS", "1")
    mission, employer = save_commercial_context(HEADERS, *values())
    context = resolve_commercial_context(HEADERS)
    assert context.commercial_mission == mission and context.employer_context == employer
    assert mission.industries == ("Media", "telecommunications")
    assert employer.capabilities == ("Digital transformation", "cloud", "data", "AI", "managed services")
    assert mission.operational_status == "Configured" and not mission.mission_name
    brief = research_gap_brief(twin(), "ignored imported label", mission, employer_context=employer)
    for text in ("Industries: Media; telecommunications", "Priority customers: BT Group; BBC; ITV",
                 "Capabilities: Digital transformation; cloud; data; AI; managed services",
                 "Competitors: Accenture; Cap Gemini; IBM", "Partners: Not supplied"):
        assert text in brief


def test_complete_scope_and_deterministic_emphasis_are_separate():
    from cios.applications.flora.commercial_mission import CommercialMission
    mission_values, employer_values = values()
    mission = CommercialMission.from_dict("u", mission_values)
    employer = EmployerContext.from_dict(employer_values)
    model = twin(); requirements = research_requirements(model, executive_assessments(model))
    assert len(_mission_prioritised(requirements, mission, employer)) < len(requirements)
    brief = research_gap_brief(model, "ignored", mission, employer_context=employer)
    assert "## 4. Complete Research Commission" in brief and "Mission settings remove nothing" in brief
    assert "### BT Group" in brief and "named priority customer: BT Group" in brief
    other_emphasis = brief.split("## 5. Mission Emphasis", 1)[1].split("## 6.", 1)[0]
    assert "named priority customer: Other Co" not in other_emphasis
    assert "Google Cloud\nPriority because" not in other_emphasis
    assert "supported timing within configured horizon: 12–24 months" in brief
    industry_reasons = other_emphasis.split("### the represented industry", 1)[1].split("### ", 1)[0]
    assert "named priority customer" not in industry_reasons and "supported timing" not in industry_reasons


def test_collection_language_counts_banner_and_markdown_contract():
    from cios.applications.flora.commercial_mission import CommercialMission
    mission_values, employer_values = values(); mission = CommercialMission.from_dict("u", mission_values)
    employer = EmployerContext.from_dict(employer_values); model = twin()
    gaps = _research_gaps(model, "run", mission)
    collection_prose = gaps.split("Architectural traceability", 1)[0]
    assert all(value not in collection_prose for value in ("BBC", "Ericsson", "Full-fibre rollout"))
    assert "1 Industry Twin; 11 required overview dimensions incomplete" in gaps
    assert "enterprise profiles require enrichment" in gaps and "Executive dependency impact" in gaps
    banner = _mission_indicator(mission, employer, "run")
    assert banner.count("configured") == 1 and "Commercial context saved" not in banner
    brief = research_gap_brief(model, "ignored", mission, employer_context=employer)
    assert brief.startswith("# Telecommunications, Media and Sport Industry Twin — Executive Research Commission\n")
    assert len(re.findall(r"^# ", brief, re.MULTILINE)) == 1
    headings = re.findall(r"^## (.+)$", brief, re.MULTILINE)
    assert len(headings) == len(set(headings))
    assert headings[:16] == [f"{i}. {name}" for i, name in enumerate(("Executive Purpose", "Commercial Context", "Twin Summary", "Complete Research Commission", "Mission Emphasis", "Industry Overview", "Enterprises", "Market Participants", "Major Programmes", "Opportunities", "Reinvention Timing", "Evidence Requirements", "Unknowns and Contradictions", "Required Structured Deliverables", "Researcher Acceptance Criteria", "Remaining Known Limitations"), 1)]
    primary, appendix = brief.split("## Appendix A", 1)
    assert "canonical owner" not in primary.casefold() and "promotion effect" not in primary.casefold()
    assert "canonical owner" in appendix.casefold() and "## Appendix B" in brief and "## Appendix C" in brief
