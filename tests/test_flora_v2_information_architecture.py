from cios.applications.flora.web.app import (
    FloraWebHandler,
    _flora_governance_page,
    _flora_home_page,
    _flora_intelligence_page,
    _flora_opportunities_page,
    _flora_research_page,
)
from http.server import ThreadingHTTPServer
import http.client
import threading


def test_home_is_enterprise_intelligence_workspace_and_flora_map():
    page = _flora_home_page({})

    assert "Enterprise Intelligence Workspace" in page
    assert "Enterprise Intelligence Map" in page
    assert "Commercial Context" in page
    assert "Commercial opportunities" in page
    assert "Intelligence Requiring Attention" in page
    assert "Industry Portfolio" in page
    assert "UK Banking" in page
    assert "Governed" in page
    assert "active candidates" not in page
    assert "Upcoming monitoring triggers</strong><span>Not currently available" in page
    assert "current contradictions require monitoring" not in page


def test_primary_navigation_uses_five_executive_destinations():
    page = _flora_home_page({"X-Flora-User": "owner", "X-Flora-Roles": "owner", "X-Flora-Active-Workspace": "CIOS", "X-Flora-Enterprises": "CIOS"})

    for label in ("Home", "Intelligence", "Opportunities", "Research", "Governance"):
        assert f">{label}</a>" in page
    assert ">Explore</a>" not in page
    assert ">Focus</a>" not in page
    assert ">Shape</a>" not in page
    assert "aria-label='Profile and settings'" in page


def test_new_workspaces_compose_existing_capability_routes():
    intelligence = _flora_intelligence_page({}, {})
    opportunities = _flora_opportunities_page({}, {})
    research = _flora_research_page({})
    governance = _flora_governance_page({})

    assert "/digital-twins" in intelligence
    assert "Horizon 1" in opportunities
    assert "/focus?opportunity=" in _flora_opportunities_page({}, {"tab": ["horizon_2"]})
    assert "/blueprint-import" in research and "/live/evidence" in research
    assert "/blueprint-import/history" in governance and "/deployment" in governance


def test_primary_workspace_routes_are_served_without_replacing_deep_links():
    server = ThreadingHTTPServer(("127.0.0.1", 0), FloraWebHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        for path, expected in (("/", "Enterprise Intelligence Workspace"), ("/intelligence", "Explore the enterprise intelligence estate"), ("/opportunities", "Commercial Pipeline Workspace"), ("/research", "Research Workspace"), ("/governance", "Governed Intelligence Workspace"), ("/digital-twins", "Digital Twins"), ("/explore", "What is changing in Banking"), ("/focus", "Banking Opportunity Pipeline"), ("/shape", "Strategic Sales Brief")):
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port)
            connection.request("GET", path)
            response = connection.getresponse()
            body = response.read().decode("utf-8")
            connection.close()
            assert response.status == 200
            assert expected in body
    finally:
        server.shutdown()
        server.server_close()


def test_home_resolves_canonical_commercial_context_and_only_claims_mission_ordering_on_match(monkeypatch):
    from cios.applications.flora.commercial_mission import CommercialMission, EmployerContext, ResolvedCommercialContext
    import cios.applications.flora.commercial_mission as context_module

    mission = CommercialMission(
        user_id="owner", executive_role="Client Partner", employer="Acme",
        commercial_objective="Grow trusted transformation", industries=("UK Banking",),
        geography=("United Kingdom",), commercial_horizon="2026–2028",
        named_accounts=("Nationwide",),
    )
    monkeypatch.setattr(context_module, "resolve_commercial_context", lambda headers: ResolvedCommercialContext(
        mission, EmployerContext(organisation="Acme")))

    page = _flora_home_page({"X-Flora-User": "owner"})

    assert "Commercial context configured" in page
    assert "Client Partner · Acme · United Kingdom · 2026–2028" in page
    assert "Priorities for my mission" in page
    assert "Named priority customer in your Commercial Context" in page
    assert page.index("Nationwide / Virgin Money") < page.index("Customer unresolved")


def test_home_neutral_and_unresolved_customer_contract(monkeypatch):
    from cios.applications.flora.commercial_mission import ResolvedCommercialContext
    import cios.applications.flora.commercial_mission as context_module
    monkeypatch.setattr(context_module, "resolve_commercial_context", lambda headers: ResolvedCommercialContext(None, None))

    page = _flora_home_page({})

    assert "Commercial context not configured" in page
    assert "Commercial opportunities" in page
    assert "Priorities for my mission" not in page
    assert "Strategic opportunity hypothesis" in page
    assert "Customer unresolved" in page
    assert "Reason shown" not in page
    for forbidden in ("runtime opportunities", "runtime intelligence", "evidence assets", "Not signed in", "active candidates"):
        assert forbidden not in page
