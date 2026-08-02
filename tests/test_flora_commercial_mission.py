import json
from cios.applications.flora.commercial_mission import resolve_commercial_mission


def test_mission_is_resolved_by_authenticated_user_and_not_inferred(monkeypatch, tmp_path):
    path = tmp_path / "missions.json"
    path.write_text(json.dumps({"sam": {"executive_role": "Director", "employer": "Example",
        "commercial_objective": "Investigate evidenced needs", "offer_portfolio": []}}))
    monkeypatch.setenv("FLORA_COMMERCIAL_MISSIONS_FILE", str(path))
    monkeypatch.setenv("FLORA_TRUST_PROXY_HEADERS", "1")
    mission = resolve_commercial_mission({"X-Flora-User": "sam"})
    assert mission and mission.executive_role == "Director"
    assert mission.authority_status == "human-supplied operational context"
    assert mission.offer_portfolio == ()
    assert resolve_commercial_mission({"X-Flora-User": "unknown"}) is None

from cios.applications.flora.commercial_mission import save_commercial_mission


def test_mission_edit_persists_against_authenticated_profile(monkeypatch, tmp_path):
    path = tmp_path / "missions.json"
    monkeypatch.setenv("FLORA_COMMERCIAL_MISSIONS_FILE", str(path))
    monkeypatch.setenv("FLORA_TRUST_PROXY_HEADERS", "1")
    headers = {"X-Flora-User": "alice"}
    saved = save_commercial_mission(headers, {
        "executive_role": "Sales Director", "employer": "Sopra Steria",
        "commercial_objective": "Identify evidenced client problems",
        "interests": ["industry change"], "offer_portfolio": []})
    assert saved.employer == "Sopra Steria"  # accepted as a legacy input, but not persisted with mission authority
    resolved = resolve_commercial_mission(headers)
    assert resolved and resolved.executive_role == saved.executive_role
    assert resolved.employer == ""
    stored = json.loads(path.read_text())
    assert stored["alice"]["authority_status"] == "human-supplied operational context"
    assert "employer" not in stored["alice"]
    assert "offer_portfolio" not in stored["alice"]

from dataclasses import asdict
from cios.applications.flora.commercial_mission import (
    resolve_employer_context, save_employer_context,
)


def test_employer_context_persists_in_an_independent_profile_store(monkeypatch, tmp_path):
    mission_path = tmp_path / "missions.json"
    employer_path = tmp_path / "employers.json"
    monkeypatch.setenv("FLORA_COMMERCIAL_MISSIONS_FILE", str(mission_path))
    monkeypatch.setenv("FLORA_EMPLOYER_CONTEXTS_FILE", str(employer_path))
    monkeypatch.setenv("FLORA_TRUST_PROXY_HEADERS", "1")
    headers = {"X-Flora-User": "alice"}
    save_commercial_mission(headers, {"mission_name": "UK growth", "executive_role": "Director",
                                     "commercial_objective": "Find evidenced demand"})
    employer = save_employer_context(headers, {"organisation": "Example Supplier", "offer_portfolio": ["Cloud"],
                                                "capabilities": ["Migration"], "propositions": ["Modernisation"]})
    assert resolve_employer_context(headers) == employer
    assert mission_path != employer_path
    assert "organisation" not in json.loads(mission_path.read_text())["alice"]
    assert "mission_name" not in json.loads(employer_path.read_text())["alice"]
    assert employer.field_statuses["offer_portfolio"] == "human-supplied"
    assert employer.field_statuses["competitors"] == "unresolved"


def test_saving_mission_does_not_change_employer_context(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_COMMERCIAL_MISSIONS_FILE", str(tmp_path / "missions.json"))
    monkeypatch.setenv("FLORA_EMPLOYER_CONTEXTS_FILE", str(tmp_path / "employers.json"))
    monkeypatch.setenv("FLORA_TRUST_PROXY_HEADERS", "1")
    headers = {"X-Flora-User": "alice"}
    before = save_employer_context(headers, {"organisation": "Supplier", "offer_portfolio": ["Data"]})
    save_commercial_mission(headers, {"executive_role": "Lead", "commercial_objective": "Grow accounts"})
    assert resolve_employer_context(headers) == before
