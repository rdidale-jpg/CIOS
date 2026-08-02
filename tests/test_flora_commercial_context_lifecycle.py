"""End-to-end persistence invariants for the commercial-context handoff."""
from dataclasses import asdict

from cios.applications.flora.blueprint_import.executive_workspace import (
    _mission_editor,
    _mission_prioritised,
    research_gap_brief,
    twin_readiness,
)
from cios.applications.flora.blueprint_import.intelligence_projection import executive_assessments
from cios.applications.flora.blueprint_import.research_requirements import research_requirements
from cios.applications.flora.blueprint_import.semantic_twin import assemble_semantic_twin
from cios.applications.flora.commercial_mission import (
    resolve_commercial_mission,
    resolve_employer_context,
    save_commercial_context,
)


def _headers():
    return {"X-Flora-User": "pilot-operator"}


def _values():
    return ({
        "mission_name": "UK growth", "executive_role": "Sales Director",
        "commercial_objective": "Find evidenced demand", "geography": ["United Kingdom"],
        "industries": ["Media"], "objectives": ["Active procurements"],
        "commercial_horizon": "Next 12 months", "interests": ["AI"],
        "priority_accounts": ["BBC"],
    }, {
        "organisation": "Example Supplier", "capabilities": ["AI"],
        "offer_portfolio": ["Transformation"], "competitors": ["Rival"],
        "partners": ["Partner"], "propositions": ["Modernisation"],
    })


def _twin():
    return assemble_semantic_twin([
        {"candidate_record_id": "bbc", "candidate_object_class": "enterprise_twin",
         "payload": {"name": "BBC", "enterprise_id": "bbc", "domain": "Media"}},
        {"candidate_record_id": "opp", "candidate_object_class": "opportunity_hypothesis",
         "payload": {"statement": "AI opportunity", "affected_enterprises": ["BBC"]}},
    ])


def test_blank_then_save_reload_and_module_restart_use_persistent_data_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_TRUST_PROXY_HEADERS", "1")
    monkeypatch.delenv("FLORA_COMMERCIAL_MISSIONS_FILE", raising=False)
    monkeypatch.delenv("FLORA_EMPLOYER_CONTEXTS_FILE", raising=False)
    assert resolve_commercial_mission(_headers()) is None
    assert resolve_employer_context(_headers()) is None
    assert "value=''" in _mission_editor(None, None, "run")

    mission, employer = save_commercial_context(_headers(), *_values())
    assert mission.version == employer.version == 1
    assert (tmp_path / "commercial_context" / "commercial_missions.json").is_file()
    assert (tmp_path / "commercial_context" / "employer_contexts.json").is_file()

    # Resolvers read the durable files on every call (there is no process
    # cache), which is the application-restart persistence boundary.
    restored_mission = resolve_commercial_mission(_headers())
    restored_employer = resolve_employer_context(_headers())
    assert asdict(restored_mission) == asdict(mission)
    assert asdict(restored_employer) == asdict(employer)
    html = _mission_editor(restored_mission, restored_employer, "another-import")
    assert all(value in html for value in ("UK growth", "United Kingdom", "BBC", "Example Supplier", "Rival", "Partner"))


def test_shared_context_drives_export_but_never_completeness(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_TRUST_PROXY_HEADERS", "1")
    mission, employer = save_commercial_context(_headers(), *_values())
    twin = _twin()
    neutral = twin_readiness(twin)
    focused = twin_readiness(twin, mission)
    assert [(a.state, a.missing) for a in focused] == [(a.state, a.missing) for a in neutral]

    requirements = research_requirements(twin, executive_assessments(twin))
    assert set(_mission_prioritised(requirements, mission, employer)) < set(requirements)
    brief = research_gap_brief(twin, "Media", mission, employer_context=employer)
    assert "## Appendix A — Architectural Traceability" in brief
    assert "Mission settings remove nothing from this commission" in brief
    assert "Unknowns" in brief and "Contradictions" in brief
    assert "### BBC" in brief


def test_optional_examples_are_guidance_not_configuration_or_export(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_TRUST_PROXY_HEADERS", "1")
    html = _mission_editor(None, None, "run")

    # Optional controls are blank and their examples are separate explanatory text.
    assert "name='priority_accounts' value=''" in html
    assert "name='industries' value=''" in html
    assert "name='employer_capabilities' value=''" in html
    assert "Example: BT Group, BBC, ITV" in html
    assert "placeholder='BT Group, BBC, ITV'" not in html
    assert "Optional · <span class='field-status' data-status-for='priority_accounts'>Not configured" in html

    mission, employer = save_commercial_context(_headers(), {
        "executive_role": "Sales Director", "commercial_objective": "Active procurements",
        "geography": ["United Kingdom"], "commercial_horizon": "12–24 months",
    }, {"organisation": "Sopra Steria"})
    restored = resolve_commercial_mission(_headers())
    assert restored == mission
    assert restored.industries == restored.priority_accounts == ()
    assert employer.capabilities == ()

    brief = research_gap_brief(_twin(), "Media", restored, employer_context=employer)
    assert "- Industries: Not supplied" in brief
    assert "- Priority customers: Not supplied" in brief
    assert "- Capabilities: Not supplied" in brief
    assert "- target industries" in brief and "- priority customers" in brief and "- capabilities" in brief
    assert "BT Group, BBC, ITV" not in brief
    assert "Digital transformation, cloud, data, AI, managed services" not in brief


def test_saved_optional_values_reload_as_configured_and_export_verbatim(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("FLORA_TRUST_PROXY_HEADERS", "1")
    mission, employer = save_commercial_context(_headers(), *_values())
    html = _mission_editor(resolve_commercial_mission(_headers()), resolve_employer_context(_headers()), "run")
    assert "name='priority_accounts' value='BBC'" in html
    assert "data-status-for='priority_accounts'>Configured" in html
    brief = research_gap_brief(_twin(), "Media", mission, employer_context=employer)
    assert "- Industries: Media" in brief
    assert "- Priority customers: BBC" in brief
    assert "- Capabilities: AI" in brief
