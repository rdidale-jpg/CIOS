from cios.applications.flora.banking_portfolio import (
    BANKS,
    BANK_REINVENTION_POSITIONS,
    ai_native_page,
    bank_journey_timeline,
    bank_page,
    capability_gap_map,
    competitor_capability_html,
    opportunity_horizon_chart,
    pipeline,
    pipeline_page,
    pipeline_value_timeline,
    portfolio_page,
    timeline_page,
    totals,
    visual_legend,
)


def test_ai_native_maturity_journey_renders_as_visual_progression():
    html = ai_native_page()
    assert "AI-native maturity rail" in html
    for stage in ["Legacy constrained", "Digitally enabled", "Integrated and data-led", "AI-assisted enterprise", "AI-native bank"]:
        assert stage in html
    assert "maturity-rail" in html
    assert html.count("<details class='maturity-stage'") == 5


def test_all_five_banks_appear_on_shared_time_axis_with_ranges():
    html = bank_journey_timeline()
    for year in ["2026", "2027", "2028", "2029", "2031", "2033", "2036"]:
        assert year in html
    for bank in BANKS.values():
        assert bank.name in html
        assert BANK_REINVENTION_POSITIONS[bank.slug]["next"] in html
        assert BANK_REINVENTION_POSITIONS[bank.slug]["native"] in html
        assert BANK_REINVENTION_POSITIONS[bank.slug]["barriers"] in html
    assert "stroke-dasharray" in html


def test_opportunity_start_duration_values_and_supplier_markers_render():
    html = opportunity_horizon_chart("lloyds")
    for opp in BANKS["lloyds"].opportunities:
        assert opp.title[:42] in html
        assert opp.value.label in html
        assert opp.conviction in html
        assert opp.accelerate_signal in html
        assert opp.delay_signal in html
    assert "Supplier" in html
    assert "human-labelled" in html or "inferred" in html
    assert "Accessible data table fallback" in html


def test_pipeline_values_reconcile_and_value_states_not_conflated():
    html = pipeline_value_timeline()
    assert f"Gross £{totals()[2]}m" not in html  # distributed by year, not one misleading total
    for label in ["Gross addressable", "Overlap-adjusted", "User-validated", "Qualified", "Confirmed CRM"]:
        assert label in html
    assert "not probability weighted" in html
    page = pipeline_page()
    assert "Cross-bank pipeline timeline" in page
    assert "Lloyds Banking Group opportunity timeline" in page
    assert sum(o.value.midpoint for o in pipeline()) == totals()[2]


def test_supplier_and_event_markers_do_not_invent_dates_or_contract_ownership():
    html = opportunity_horizon_chart(cross_bank=True)
    assert "Trigger:" in html
    assert "No reliable view" in html or "Supplier" in html
    assert "partnership is contract ownership" not in html.lower()
    assert "2026-01-01" not in html


def test_visuals_have_accessible_text_keyboard_and_print_fallbacks():
    html = ai_native_page() + timeline_page() + pipeline_page()
    for token in ["role='img'", "aria-labelledby", "tabindex='0'", "Accessible data table fallback", "@media print", "Mobile vertical timeline fallback"]:
        assert token in html


def test_portfolio_capability_and_competitor_visual_artifacts_render():
    assert "Portfolio priority map" in portfolio_page()
    assert "not guaranteed buying" in portfolio_page() or "not purchase certainty" in portfolio_page()
    cap = capability_gap_map("lloyds")
    for domain in ["Customer experience", "Service operations", "Data and AI", "Supplier ecosystem"]:
        assert domain in cap
    comp = competitor_capability_html()
    assert "Competitor-offer matrix" in comp
    assert "<meter" in comp


def test_visual_elements_link_to_drill_down_and_are_deterministic():
    first = ai_native_page() + pipeline_page() + visual_legend()
    second = ai_native_page() + pipeline_page() + visual_legend()
    assert first == second
    assert "/flora/banking/lloyds" in portfolio_page()
    assert "/flora/banking/lloyds/opportunity/" in bank_page("lloyds")[0]
    assert "What Flora sees" in first
    assert "generic banking illustration" not in first.lower()
