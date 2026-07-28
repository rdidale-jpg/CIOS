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
    assert saved.employer == "Sopra Steria"
    assert resolve_commercial_mission(headers) == saved
    stored = json.loads(path.read_text())
    assert stored["alice"]["authority_status"] == "human-supplied operational context"
    assert stored["alice"]["offer_portfolio"] == []
