from cios.applications.flora.banking_portfolio import (
    BANKS, BACKLOG_46, INDUSTRY_SIGNALS, PESTLE_FORCES,
    ai_native_page, banking_landing_page, compare_page, competitor_capability_html,
    global_industry_portfolio_page, heatmap_page, industry_outlook_page,
    industry_signal_explorer_page, pipeline, pipeline_page, timeline_page,
    capability_gap_map, opportunity_horizon_chart,
)


def test_global_landing_renders_multi_industry_cards_with_only_banking_active():
    html = global_industry_portfolio_page()
    for name in ["UK Banking", "Insurance", "Retail", "Telecommunications", "Public Sector"]:
        assert name in html
    assert html.count("Active governed industry") == 1
    assert "No governed view yet" in html


def test_banking_landing_links_outlook_and_separates_featured_from_all_signals():
    html = banking_landing_page()
    assert "Understand what is changing in UK Banking" in html
    assert "/flora/banking/outlook" in html
    assert "Three issues Flora believes matter most right now" in html
    assert "Featured:</strong> 3" in html
    assert f"All current signals:</strong> {len(INDUSTRY_SIGNALS)}" in html
    assert len(INDUSTRY_SIGNALS) > 3
    assert "Explore all industry forces and signals" in html


def test_outlook_has_visual_narrative_pestle_and_actionable_conclusions():
    html = industry_outlook_page()
    assert "Flora’s view of UK Banking" in html
    for phrase in ["Industry force", "management pressure", "likely bank behaviour", "required reinvention", "commercial implications"]:
        assert phrase.lower() in html.lower()
    for force in PESTLE_FORCES:
        assert force in html
    for rank in ["Critical now", "Material", "Emerging"]:
        assert rank in html
    assert "The five most important conclusions" in html


def test_signal_inventory_covers_material_forces_and_lineage():
    html = industry_signal_explorer_page()
    assert len(INDUSTRY_SIGNALS) >= 12
    for phrase in ["Force or cause", "Affected banks", "Likely behaviour", "Horizon", "Reinvention pressure", "Commercial implication", "Related opportunities", "Provenance", "Source lineage", "Generated date"]:
        assert phrase in html
    for force in PESTLE_FORCES:
        assert force in html


def test_ai_native_vision_branch_tension_and_distinct_pages():
    ai = ai_native_page(); timeline = timeline_page(); comparison = compare_page()
    assert "The AI-native bank of the future" in ai
    assert "A day in the life of an AI-native bank customer" in ai
    assert "Branch and Human Service Strategy" in ai
    assert "branches do not necessarily disappear" in ai.lower()
    assert "What is the future-state destination?" in ai
    assert "How will the industry move toward" in timeline
    assert "Where does each bank sit today?" in comparison


def test_major_visuals_have_before_and_after_explanation():
    visuals = [capability_gap_map("lloyds"), opportunity_horizon_chart("lloyds"), timeline_page(), compare_page(), pipeline_page(), competitor_capability_html()]
    for html in visuals:
        assert "What this visual shows" in html
        assert "What Flora sees" in html
        assert "How to read this visual" in html


def test_comparison_narrative_and_opportunity_value_mode():
    theme = compare_page(); value = heatmap_page("opportunity-value")
    assert "Compare UK banks" in theme
    assert "What this tells you: Customer experience" in theme
    assert "What this tells you: Lloyds has the largest current working pipeline" in value
    assert "£ working estimates" in value


def test_competitor_research_gaps_grouped_and_hideable():
    html = competitor_capability_html()
    assert "Capability areas Flora understands" in html
    assert "Capability areas Flora needs to research" in html
    assert "Hide insufficient-view columns" in html
    assert "missing suppliers" in html


def test_complete_opportunities_and_value_semantics_are_reachable():
    html = pipeline_page()
    assert "Featured opportunities" in html
    assert "All opportunity hypotheses" in html
    assert len(pipeline()) > 3
    for bank in BANKS.values():
        for o in bank.opportunities:
            assert o.title in html
    for phrase in ["Buying-window pipeline", "Expected contract signature value", "Total contract value", "Annual contract value", "Estimated delivery revenue", "Qualified pipeline", "Confirmed CRM pipeline"]:
        assert phrase in html
    assert "Delivery value is spread across delivery years" in html


def test_backlog_and_shared_component_readiness_terms_present():
    assert "FLR-095 Multi-industry landing experience" in BACKLOG_46
    html = global_industry_portfolio_page() + industry_outlook_page() + compare_page() + pipeline_page() + competitor_capability_html()
    for term in ["industry-card", "Industry Outlook", "Compare UK banks", "Pipeline", "Competitor capability"]:
        assert term.lower() in html.lower()
