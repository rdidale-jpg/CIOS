import pytest
from cios.applications.flora.banking_portfolio import (
    AI_NATIVE_COMPARISON, BANKS, COMPARE_MODES, INDUSTRY_SIGNALS,
    banking_landing_page, industry_signal_explorer_page, industry_outlook_page,
    ai_native_page, validate_ai_native_comparison, TIMELINE_TRACKS,
    validate_reinvention_timeline, bank_page, financial_history_page,
    analyst_history_page, compare_page, opportunity_page, pipeline_page,
    pestle_view_html, competitors_page,
)

BANK_NAMES = [b.name for b in BANKS.values()]


def test_banking_landing_shows_exactly_three_featured_signals_and_explorer_has_remaining():
    html = banking_landing_page()
    assert "Explore all 12 industry signals" in html
    assert html.count("executive-insight") == 3
    assert len(INDUSTRY_SIGNALS) == 12
    explorer = industry_signal_explorer_page()
    assert explorer.count("class='card signal'") == 12
    for title, *_ in INDUSTRY_SIGNALS[3:]:
        assert title not in html
        assert title in explorer


def test_all_five_bank_cards_appear_on_landing():
    html = banking_landing_page()
    assert "data-bank-count='5'" in html
    for name in BANK_NAMES:
        assert name in html
        assert "Open bank" in html


def test_causal_flow_nodes_do_not_split_words_vertically():
    html = industry_outlook_page()
    assert "causal-flow" in html
    assert "writing-mode:vertical" not in html
    assert "word-break:break-all" not in html
    for phrase in ("Industry force", "Management pressure", "Likely behaviour", "Required reinvention", "Commercial opportunity"):
        assert phrase in html


def test_ai_native_dimensions_are_distinct_and_duplicates_fail_validation():
    assert validate_ai_native_comparison()
    today = [d[1] for d in AI_NATIVE_COMPARISON]
    future = [d[2] for d in AI_NATIVE_COMPARISON]
    assert len(today) == len(set(today))
    assert len(future) == len(set(future))
    bad = (("A", "same", "future"), ("B", "same", "future 2"))
    with pytest.raises(ValueError):
        validate_ai_native_comparison(bad)
    html = ai_native_page()
    for name, today_text, future_text in AI_NATIVE_COMPARISON:
        assert name in html and today_text in html and future_text in html


def test_timeline_stages_are_concise_distinct_content():
    assert validate_reinvention_timeline()
    all_stages = [stage for stages in TIMELINE_TRACKS.values() for stage in stages]
    assert len(all_stages) == len(set(all_stages))
    assert all(len(stage.split()) <= 12 for stage in all_stages)


def test_lloyds_overview_contains_working_links_to_enterprise_tabs():
    html, status = bank_page("lloyds")
    assert status == 200
    for path in ("/financial-performance", "/market-reaction", "/analyst-history", "/event-timeline", "/evidence", "/research-backlog"):
        assert f"/flora/banking/lloyds{path}" in html


def test_financial_metrics_render_without_fabrication():
    html = financial_history_page("lloyds")
    for metric in ("Total income", "Profit before tax", "Operating costs", "Cost:income ratio", "Net interest margin", "Deposits", "Lending", "Capital ratio", "Conduct or impairment charges"):
        assert metric in html
    assert "not fabricated" in html
    assert "£999" not in html


def test_analyst_prose_does_not_render_character_by_character():
    html = analyst_history_page("lloyds")
    assert "Prevailing positive view" in html
    assert "P r e v a i l i n g" not in html


def test_compare_exposes_six_modes_value_money_and_executive_interpretation():
    html = compare_page()
    for mode in COMPARE_MODES:
        assert mode in html
    assert len(COMPARE_MODES) == 6
    assert "£" in html
    assert html.count("What Flora sees") == 6
    assert "non-monetary comparison" in html


def test_opportunity_pages_contain_no_implementation_mechanics_narrative():
    opp = BANKS["lloyds"].opportunities[0]
    html, status = opportunity_page("lloyds", opp.id)
    assert status == 200
    banned = ("lane selection opens", "duplicate link rows are avoided", "table fallback remains", "selected value semantics are being shown")
    assert not any(b in html for b in banned)
    assert "What Flora sees" in html


def test_all_five_banks_reachable_from_relevant_journeys():
    journeys = [banking_landing_page(), industry_signal_explorer_page(), compare_page(), pipeline_page(), pestle_view_html(), competitors_page()[0]]
    for b in BANKS.values():
        route = f"/flora/banking/{b.slug}"
        for html in journeys:
            assert route in html
