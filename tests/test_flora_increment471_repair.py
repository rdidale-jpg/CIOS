import pytest

from cios.applications.flora.banking_portfolio import (
    BANKS,
    CAUSAL_LANES,
    TIMELINE_TRACKS,
    ai_native_capability_model_page,
    ai_native_page,
    banking_landing_page,
    banks_page,
    compare_page,
    industry_outlook_page,
    industry_signal_explorer_page,
    pipeline_page,
    timeline_page,
    validate_reinvention_timeline,
)


def test_landing_contains_direct_links_to_all_five_banks_and_lloyds_one_click():
    html = banking_landing_page()
    assert "Explore the banks" in html
    for slug, bank in BANKS.items():
        assert f"href='/flora/banking/{slug}'" in html
        assert bank.name in html
    assert "Lloyds Banking Group" in html
    assert "Open bank" in html


def test_banks_route_shows_all_five_enterprises():
    html = banks_page()
    assert "data-bank-count='5'" in html
    for slug, bank in BANKS.items():
        assert f"/flora/banking/{slug}" in html
        assert bank.name in html


def test_every_bank_name_in_signal_explorer_links_to_enterprise_page():
    html = industry_signal_explorer_page()
    for slug, bank in BANKS.items():
        if bank.name in html:
            assert f"href='/flora/banking/{slug}'" in html


def test_every_bank_heading_in_comparison_links_to_enterprise_page():
    html = compare_page()
    for slug, bank in BANKS.items():
        assert f"href='/flora/banking/{slug}'>{bank.name}</a>" in html


def test_causal_chains_render_as_separate_selectable_lanes():
    html = industry_outlook_page()
    assert html.count("class='causal-lane'") == 3
    assert html.count("data-causal-node=") >= 15
    for lane in CAUSAL_LANES:
        assert lane[0] in html
        assert lane[4] in html
    assert "Plain English" in html
    assert "/flora/banking/lloyds" in html


def test_ai_native_page_has_before_after_and_customer_scenario():
    html = ai_native_page()
    assert "Today’s bank" in html
    assert "AI-native bank" in html
    assert "A day in the life" in html
    for phrase in ("proactive", "virtual financial advice", "consents", "human specialist", "Vulnerable-customer safeguard"):
        assert phrase.lower() in html.lower()


def test_ai_native_capability_model_is_explorable_and_has_12_cards():
    html = ai_native_capability_model_page()
    assert html.count("data-drilldown='true'") == 12
    for phrase in ("Current traditional state", "Digitally enabled state", "AI-assisted state", "AI-native state", "Customer consequence", "Employee consequence", "Cost consequence", "Main barrier", "Likely opportunity"):
        assert phrase in html


def test_reinvention_timeline_tracks_contain_distinct_progression():
    html = timeline_page()
    all_descriptions = [description for stages in TIMELINE_TRACKS.values() for description in stages]
    assert len(all_descriptions) == len(set(all_descriptions))
    for track, stages in TIMELINE_TRACKS.items():
        assert track in html
        for stage in stages:
            assert stage in html
    assert "What Flora expects to happen" in html
    assert "What this means commercially" in html


def test_duplicate_timeline_descriptions_fail_validation():
    invalid = dict(TIMELINE_TRACKS)
    invalid["Operations and workforce"] = TIMELINE_TRACKS["Customer and channel model"]
    with pytest.raises(ValueError):
        validate_reinvention_timeline(invalid)


def test_account_opportunity_timing_not_on_industry_reinvention_timeline():
    html = timeline_page()
    assert "opportunity_horizon" not in html
    assert "Buying window" not in html
    assert "account opportunity timing chart" in html


def test_enterprise_routes_and_intelligence_preserved():
    assert set(BANKS) == {"lloyds", "barclays", "natwest", "hsbc-uk", "santander-uk"}
    assert all(b.opportunities for b in BANKS.values())
    assert "Lloyds Banking Group" in banking_landing_page()
    assert "Lloyds Banking Group" in pipeline_page()
