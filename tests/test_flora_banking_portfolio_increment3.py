from cios.applications.flora.banking_portfolio import BANKS, THEMES, bank_page, compare_page, portfolio_page, pipeline, totals, FEEDBACK_ACTIONS


def test_all_five_bank_accounts_have_commercial_snapshots():
    assert [b.name for b in BANKS.values()] == ["Lloyds Banking Group", "Barclays", "NatWest Group", "HSBC UK", "Santander UK"]
    html = portfolio_page()
    for bank in BANKS.values():
        assert bank.name in html
        assert "Open account" in html
        assert "Why Flora ranks it here" in html
    assert "Enterprise Model:" not in html
    assert "Material Unknowns" not in html
    assert "Context Package" not in html
    assert "This is not a Recommendation" not in html


def test_each_bank_page_uses_executive_structure_and_preserves_inspection():
    for slug, bank in BANKS.items():
        html, status = bank_page(slug, briefing=True)
        assert status == 200
        for section in ["1. Account in one minute", "2. Financial snapshot", "5. Analyst view", "8. Recommended opportunities", "9. Estimated pipeline", "12. Why Flora believes this", "13. Detailed inspection"]:
            assert section in html
        assert "Current to 2026-07-19" in html
        assert "Estimated contract value" in html
        assert "Flora working estimate" in html
        assert "Valuation method" in html
        assert bank.id in html  # only Level 3
    html, status = bank_page("unknown-bank")
    assert status == 200
    assert "Flora does not yet have a reliable view" in html


def test_financial_metrics_render_and_missing_metrics_not_fabricated():
    lloyds, _ = bank_page("lloyds")
    assert "£17.9bn FY2024" in lloyds
    hsbc, _ = bank_page("hsbc-uk")
    assert "not publicly disclosed" in hsbc
    assert "£0.0bn" not in hsbc


def test_analyst_views_preserve_attribution_without_fake_consensus():
    for slug in BANKS:
        html, _ = bank_page(slug)
        assert "What analysts broadly like" in html
        assert "No single analyst view is presented as consensus" in html
        assert "Analyst synthesis preserves attribution" in html


def test_theme_relevance_ranking_and_pipeline_are_deterministic():
    first = compare_page()
    second = compare_page()
    assert first == second
    for theme in THEMES:
        assert theme in first
    assert "Most relevant bank" in first
    assert "Highest-value associated opportunity" in first
    assert "probability of winning" in first
    assert "safe-unavailable" not in first


def test_opportunities_have_values_feedback_and_preserve_originals():
    opps = pipeline()
    assert len(opps) >= 15
    for o in opps:
        assert o.id
        assert o.value.low < o.value.midpoint < o.value.high
        assert o.value.low % 5 == 0 and o.value.high % 5 == 0 and o.value.midpoint % 5 == 0
        assert o.value.method
        assert o.assumptions
    html, _ = bank_page("lloyds")
    for action in FEEDBACK_ACTIONS:
        assert action in html
    assert "preserves the original Recommendation and estimate" in html


def test_pipeline_totals_calculate_correctly_and_no_probability_of_winning():
    lo, hi, mid = totals()
    assert lo == sum(o.value.low for o in pipeline())
    assert hi == sum(o.value.high for o in pipeline())
    assert mid == sum(o.value.midpoint for o in pipeline())
    html = portfolio_page() + compare_page()
    assert f"£{lo}m–£{hi}m" in html
    assert "probability of winning" in html
    assert "likelihood of winning" not in html.lower()


def test_increment_41_pipeline_reconciliation_horizons_and_value_meaning():
    for bank in BANKS.values():
        lo, hi, mid = totals(list(bank.opportunities))
        assert lo == sum(o.value.low for o in bank.opportunities)
        assert hi == sum(o.value.high for o in bank.opportunities)
        assert mid == sum(o.value.midpoint for o in bank.opportunities)
        assert bank.financial_interpretation
        assert bank.likely_accelerate and bank.likely_buying_posture
        html, _ = bank_page(bank.slug)
        assert "What the financial results are telling us" in html
        assert "Gross addressable pipeline" in html
        assert "Overlap-adjusted pipeline" in html
        assert "Qualified pipeline" in html
        assert "User-validated pipeline" in html
        assert "Confirmed CRM pipeline" in html
        assert "not probability-weighted" in html
        assert "Near-term total" in html and "Medium-term total" in html and "Longer-term total" in html
        for o in bank.opportunities:
            assert o.horizon_label in ("Immediate: 0–12 months", "Near term: 12–24 months", "Medium term: 24–36 months", "Longer term: 36–60 months", "Monitor", "Unclear")
            assert o.earliest_entry and o.buying_window and o.programme_start and o.contract_duration
            assert o.horizon_rationale and o.accelerate_signal and o.delay_signal
            assert o.supplier_position
            if not o.supplier_entries:
                assert o.supplier_position == "No reliable view"


def test_increment_41_supplier_traction_is_sourced_or_human_labelled_and_unknown_is_bounded():
    allowed = {"Strong incumbent position", "Gaining traction", "Established relationship", "Competitive field", "Early signal", "No reliable view"}
    for o in pipeline():
        assert o.supplier_position in allowed
        for e in o.supplier_entries:
            assert e.supplier_name and e.source_date and e.supporting_rationale
            assert e.insight_basis in ("confirmed", "inferred", "human-supplied")
            assert e.traction_label in allowed
    html, _ = bank_page("santander-uk")
    assert "No reliable view" in html


def test_increment_41_portfolio_cards_and_heatmap_are_scannable_with_expansion():
    html = portfolio_page()
    for text in ("Near-term pipeline", "Medium-term pipeline", "Supplier signal", "Timing trigger", "Next commercial action"):
        assert text in html
    compare = compare_page()
    assert "Commercial heatmap" in compare
    assert "Supplier field:" in compare
    assert "<details><summary>Expand</summary>" in compare
    assert "Commercial driver:" not in compare


def test_increment_41_analyst_rendering_quality_gates():
    html, _ = bank_page("lloyds")
    for text in ("writing-mode:horizontal-tb", "word-break:normal", "overflow-wrap:break-word", "@media print", "page-break-inside:avoid"):
        assert text in html
    assert "analyst-view" in html
    executive = html.split("12. Detailed inspection", 1)[0]
    assert "BK-ENT-" not in executive
