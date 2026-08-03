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
    assert "Mission Priorities" in page
    assert "Intelligence Requiring Attention" in page
    assert "Industry Portfolio" in page
    assert "UK Banking" in page
    assert "Governed" in page


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
