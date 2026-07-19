from cios.applications.flora.banking_portfolio import (
    BANKS,
    INDUSTRY_SIGNALS,
    commercial_pipeline_table,
    competitor_capability_html,
    heatmap_page,
    industry_signal_explorer_page,
    intelligence_inventory,
    opportunity_horizon_chart,
    pipeline,
    pipeline_page,
    banking_landing_page,
)


def test_working_estimate_is_separate_sortable_column_and_values_reconcile():
    html = commercial_pipeline_table("working-estimate")
    assert "Low estimate" in html
    assert "Working estimate" in html
    assert "High estimate" in html
    for opportunity in pipeline():
        assert f"data-sort-value='{opportunity.value.low}'" in html
        assert f"data-sort-value='{opportunity.value.midpoint}'" in html
        assert f"data-sort-value='{opportunity.value.high}'" in html
        assert opportunity.value.low <= opportunity.value.midpoint <= opportunity.value.high


def test_timeline_keeps_paragraph_detail_outside_svg_and_preserves_full_title_access():
    html = opportunity_horizon_chart("lloyds")
    svg = html.split("<svg", 1)[1].split("</svg>", 1)[0]
    assert "<p" not in svg
    assert "Trigger:" not in svg
    assert "Delay risk" not in svg
    for opportunity in BANKS["lloyds"].opportunities:
        assert f"<title>{opportunity.title}</title>" in html
        assert f"<summary>{opportunity.title}</summary>" in html


def test_executive_visual_does_not_expand_full_table_by_default():
    html = pipeline_page()
    assert "<details class='accessible-fallback visually-collapsed'>" in html
    assert "View as table" in html
    assert "Download data" in html
    assert "Open detailed pipeline" in html


def test_heatmap_first_viewport_active_mode_and_working_values():
    html = heatmap_page("opportunity-value")
    assert "first-viewport" in html
    assert "aria-selected='true'" in html
    assert "Working estimate" in html or "£" in html
    assert any(f"£{sum(o.value.midpoint for o in bank.opportunities if o.theme == theme or o.category == theme)}m" in html for bank in BANKS.values() for theme in {o.theme for o in bank.opportunities})


def test_competitor_assessments_are_separate_and_insufficient_view_has_no_meter():
    html = competitor_capability_html()
    assert "supplier-name" in html
    assert "capability-assessment" in html
    assert "visual-bar" in html
    assert "Insufficient viewInsufficient view" not in html
    unavailable = html.split("Offers where Flora does not yet have a reliable view", 1)[-1]
    assert "Not enough information" in unavailable
    assert "<meter" not in unavailable.split("Competitor-offer matrix", 1)[0]
    assert "Credible/No view" not in html


def test_featured_subset_has_full_exploration_route_and_counts_match_projection():
    html = banking_landing_page()
    assert "Featured intelligence" in html
    assert "Available intelligence" in html
    assert f"Explore all industry signals ({len(INDUSTRY_SIGNALS)})" in html
    assert f"View all opportunities ({len(pipeline())})" in html
    inv = intelligence_inventory()
    assert inv["Industry signals"] == len(INDUSTRY_SIGNALS)
    assert inv["Opportunity hypotheses"] == len(pipeline())


def test_industry_signal_explorer_reaches_every_underlying_signal():
    html = industry_signal_explorer_page()
    for i, signal in enumerate(INDUSTRY_SIGNALS, 1):
        assert f"data-signal-id='SIG-{i:03d}'" in html
        assert signal[0] in html
    for label in ["PESTLE force", "Strategic theme", "Affected bank", "Urgency", "Horizon", "Reinvention pressure", "Commercial opportunity", "Supplier impact"]:
        assert label in html
