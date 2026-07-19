from cios.applications.flora.banking_portfolio import (
    BANKS, BACKLOG_47, CAPABILITY_DOMAINS, INDUSTRY_SIGNALS,
    ai_native_capability_model_page, ai_native_page, analyst_history_page,
    bank_page, enterprise_event_timeline_page, financial_history_page,
    global_industry_portfolio_page, industry_outlook_page,
    industry_signal_explorer_page, market_reaction_page, pestle_view_html,
    research_backlog_page, timeline_page, validate_pestle_distinctiveness,
    validate_signal_semantics,
)


def test_industry_tiles_show_pressure_and_inactive_no_fabrication():
    html = global_industry_portfolio_page()
    assert "pressure-battery" in html
    assert "UK Banking" in html and "High" in html
    assert html.count("No current view") >= 2
    assert html.count("Active governed industry") == 1


def test_pestle_forces_are_distinct_and_not_generic():
    html = pestle_view_html()
    assert validate_pestle_distinctiveness()
    assert "Prioritised industry-force board" in html
    assert "It affects profit, trust, control, cost or change capacity" not in html
    assert "Capability gaps become structural disadvantages" not in html


def test_all_12_banking_signals_semantic_and_prioritised():
    html = industry_signal_explorer_page()
    assert len(INDUSTRY_SIGNALS) == 12
    assert validate_signal_semantics()
    for i in range(1, 13):
        assert f"#{i} " in html
    assert "data-default-field-count='6'" in html
    assert "Views: Ranked list · Timeline · By PESTLE force · By bank · By opportunity theme" in html


def test_ai_native_vision_and_capability_drilldown():
    ai = ai_native_page()
    model = ai_native_capability_model_page()
    assert "This page answers: What is the future-state destination?" not in ai
    for phrase in ["In one sentence", "What customers experience", "What employees experience", "What disappears or shrinks", "What becomes more important"]:
        assert phrase in ai
    assert "Explore all 12 capabilities" in ai + model
    assert len(CAPABILITY_DOMAINS) == 12
    assert model.count("data-drilldown='true'") == 12


def test_timeline_separates_industry_timing_from_pipeline_visual():
    html = timeline_page()
    assert "How UK Banking is likely to move from today’s operating model toward AI-native banking" in html
    assert "What this means for sales" in html
    assert "Pipeline value chart" not in html
    assert "opportunity_horizon" not in html.lower()


def test_visual_guidance_and_bank_links():
    html = industry_outlook_page() + industry_signal_explorer_page()
    assert "Causal industry-force graphic" in html
    assert "External force → Management pressure → Likely bank behaviour → Required reinvention → Commercial opportunity" in html
    assert "stronger labels, wider bands" not in html
    for b in BANKS.values():
        assert f"/flora/banking/{b.slug}" in html


def test_enterprise_tab_structure_for_each_bank():
    for slug in BANKS:
        html, status = bank_page(slug)
        assert status == 200
        for tab in ["Overview", "Financial performance", "Market and analyst view", "Strategy and behaviour", "Reinvention journey", "Opportunities", "Suppliers and competitors", "Detailed inspection"]:
            assert tab in html
        assert "pressure-battery" in html


def test_financial_history_does_not_fabricate_missing_values():
    html = financial_history_page("lloyds")
    assert "historical financial performance" in html
    assert "Missing values are not fabricated" in html
    assert "2022" in html and "2024" in html


def test_market_and_analyst_views_separate_fact_from_interpretation():
    market = market_reaction_page("lloyds")
    analyst = analyst_history_page("lloyds")
    assert "Observed market move" in market
    assert "Published analyst explanation" in market
    assert "Flora interpretation" in market
    assert "not causal proof" in market
    assert "Consensus" in analyst
    assert "Individual opinion remains labelled" in analyst
    assert "not treated as consensus" in analyst


def test_enterprise_events_retain_lineage_and_opportunity_links():
    html = enterprise_event_timeline_page("lloyds")
    assert "Source/date lineage retained" in html
    assert "COH history link" in html
    assert "financial results" in html


def test_research_gaps_preserved_prioritised_and_backlog_added():
    html = research_backlog_page("lloyds")
    for gap in ["missing financial periods", "missing technology spend", "missing opportunity validation"]:
        assert gap in html
    assert "High commercial usefulness" in html
    for item in ["FLR-108 Industry reinvention-pressure indicator", "FLR-122 Enterprise snapshot upgrade"]:
        assert item in BACKLOG_47
