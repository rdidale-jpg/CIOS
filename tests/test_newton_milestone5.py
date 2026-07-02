import os

from cios.applications.flora.observatory.engine import build_observatory
from cios.applications.flora.observatory.views import observatory_page, organisation_observatory_page
from cios.applications.flora.workspace.views import landing_page
from cios.applications.flora.url_utils import link_or_label, report_href


def test_observatory_assesses_all_monitored_enterprises():
    obs = build_observatory()
    names = {o.organisation for o in obs.organisations}
    assert len(names) > 3
    assert {"BT", "DWP", "National Grid", "Vodafone", "Thames Water", "United Utilities", "HMRC", "NHS England"} & names


def test_org_report_thesis_immediately_after_header_and_no_fy_cutoff():
    html = organisation_observatory_page("BT")
    assert html.index("report-header") < html.index("Executive Transformation Thesis") < html.index("So What? / Next Best Conversation")
    cutoff_block = html.split("Evidence cut-off timestamp", 1)[1].split("</tr>", 1)[0]
    assert "FY2025" not in cutoff_block


def test_executive_brief_visible_label_replaces_morning_edition():
    html = landing_page()
    assert "Executive Brief" in html
    nav = html.split("<nav", 1)[1].split("</nav>", 1)[0]
    assert "Morning Edition" not in nav


def test_navigation_simplified_business_labels():
    nav = landing_page().split("<nav", 1)[1].split("</nav>", 1)[0]
    for label in ["Executive Brief", "Observatory", "Portfolio", "Evidence", "Research", "Settings"]:
        assert label in nav
    for old in ["Commercial DNA", "Portfolio Radar", "Live Evidence", "Scoring Model"]:
        assert old not in nav


def test_base_url_absolute_links_and_invalid_url_suppression(monkeypatch):
    monkeypatch.setenv("BASE_URL", "https://flora.example")
    assert report_href("/observatory/BT") == "https://flora.example/observatory/BT"
    assert "<a " not in link_or_label("not a url")
    assert "not linked" in link_or_label("")


def test_observatory_index_top_theses_and_insufficient_labels():
    html = observatory_page()
    assert "Top Transformation Theses" in html
    assert "seeded fallback / insufficient live evidence" in html


def test_so_what_sections_present():
    assert "So What? / Next Best Conversation" in landing_page()
    assert "So What? / Next Best Conversation" in organisation_observatory_page("DWP")
