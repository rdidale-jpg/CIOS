from cios.applications.flora.blueprint_import.executive_workspace import research_gap_brief, _research_gaps, twin_readiness
from cios.applications.flora.blueprint_import.semantic_twin import assemble_semantic_twin
from cios.applications.flora.commercial_mission import CommercialMission


def _twin():
    return assemble_semantic_twin([
        {"candidate_record_id": "ENT-BBC", "candidate_object_class": "enterprise_twin", "payload": {"name": "BBC", "enterprise_id": "bbc", "domain": "Media"}},
        {"candidate_record_id": "PRG-1", "candidate_object_class": "transformation_programme", "payload": {"statement": "Audience platform renewal", "subject": "BBC", "domain": "Media"}},
        {"candidate_record_id": "OPP-1", "candidate_object_class": "opportunity_hypothesis", "payload": {"statement": "Modernise audience operations", "affected_enterprises": ["BBC"], "domain": "Media"}},
    ])


def _mission():
    return CommercialMission(user_id="u", executive_role="Sales Director", employer="Example Supplier", commercial_objective="Find transformation demand", industries=("Media",), geography=("United Kingdom",), interests=("Consulting",))


def test_research_gaps_exposes_markdown_export_action():
    assert "Export Research Brief" in _research_gaps(_twin(), "run-1", _mission())
    assert "/blueprint-import/run-1/research-brief" in _research_gaps(_twin(), "run-1", _mission())


def test_brief_reuses_exact_six_runtime_aspects_and_separates_contexts():
    brief = research_gap_brief(_twin(), "TMS 001", _mission(), "Media")
    names = [a.name for a in twin_readiness(_twin(), _mission())]
    assert brief.index("### Commercial Mission") < brief.index("### Employer Context")
    assert all(name in brief for name in names)
    assert "### Employer Context\n- Status: Not configured" in brief
    assert "Example Supplier capability" not in brief


def test_brief_is_actionable_human_readable_and_keeps_ids_in_appendix():
    brief = research_gap_brief(_twin(), "TMS 001", _mission())
    primary, appendix = brief.split("## Appendix", 1)
    assert "### BBC" in primary and "### Audience platform renewal" in primary
    assert "Research:" in primary and "**Why this matters**" in primary and "Executive dependency impact" in primary
    assert "### PRG-1" not in primary and "### OPP-1" not in primary
    assert "PRG-1" in appendix and "OPP-1" in appendix
    assert "owner-projection-v1" in brief
    assert "Governed owner" in brief and "Acceptance criteria" in brief

from cios.applications.flora.commercial_mission import EmployerContext


def test_brief_separates_external_research_from_user_configuration():
    employer = EmployerContext.from_dict({"organisation": "Example Supplier", "offer_portfolio": ["Cloud"],
                                          "competitors": ["Explicit Rival"], "partners": ["Explicit Partner"],
                                          "propositions": ["Modernisation"]})
    brief = research_gap_brief(_twin(), "TMS 001", _mission(), employer_context=employer)
    assert "## 4. Complete Research Commission" in brief
    assert "- Employer: Example Supplier" in brief
    assert "- Offers: Cloud" in brief
    assert "- Competitors: Explicit Rival" in brief
