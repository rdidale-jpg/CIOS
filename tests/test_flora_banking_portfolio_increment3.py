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
    # Current executive overview replaces the numbered, thirteen-section brief.
    from tests.flora_html_contract import Document
    from cios.applications.flora.banking_portfolio import GENERATED_DATE, evidence_page
    for slug, bank in BANKS.items():
        html, status = bank_page(slug, briefing=True)
        doc = Document(html)
        assert status == 200
        for section in ["What the financial results imply", "Working reinvention-pressure interpretation",
                        "Top opportunities", "Supplier and competitor position", "What should be investigated next"]:
            assert section in doc.headings
        assert GENERATED_DATE in doc.text
        for opportunity in bank.opportunities[:3]:
            assert f"/flora/banking/{slug}/opportunity/{opportunity.id}" in doc.hrefs
            assert opportunity.title in doc.text
        assert f"/flora/banking/{slug}/evidence" in doc.hrefs
        inspection, status = evidence_page(slug)
        assert status == 200 and bank.name in Document(inspection).text
        assert 'canonical Evidence IDs / accepted Observation mappings / source locators: Not supplied' in Document(inspection).text
        assert 'Illustrative, unverified commercial scenario' in doc.text
    html, status = bank_page("unknown-bank")
    assert status == 404 and 'No governed bank route is available' in html


def test_financial_metrics_render_and_missing_metrics_not_fabricated():
    lloyds, _ = bank_page("lloyds")
    assert "£17.9bn FY2024" in lloyds
    hsbc, _ = bank_page("hsbc-uk")
    assert "not publicly disclosed" in hsbc
    assert "£0.0bn" not in hsbc


def test_analyst_views_preserve_attribution_without_fake_consensus():
    from tests.flora_html_contract import Document
    from cios.applications.flora.banking_portfolio import analyst_history_page
    for slug, bank in BANKS.items():
        overview = Document(bank_page(slug)[0])
        assert f'/flora/banking/{slug}/analyst-history' in overview.hrefs
        analysis = Document(analyst_history_page(slug))
        assert 'Analyst interpretation' in analysis.headings
        for statement in bank.analyst_like + bank.analyst_question:
            assert statement in analysis.text
        from cios.applications.flora.banking_portfolio import evidence_page
        sources = Document(evidence_page(slug)[0])
        for source in bank.analyst_sources or bank.sources:
            assert source in sources.text
        assert 'Generic source labels above are not accepted claim citations' in sources.text
        assert 'not calibrated Evidence confidence' in analysis.text
        assert 'analyst consensus' not in analysis.text.lower()


def test_theme_relevance_ranking_and_pipeline_are_deterministic():
    from tests.flora_html_contract import Document
    from cios.applications.flora.banking_portfolio import COMPARE_MODES, heatmap_page
    first = compare_page()
    assert first == compare_page()
    comparison = Document(first)
    for mode in COMPARE_MODES:
        assert mode in comparison.headings
    # Theme-by-bank cells live in the dedicated heatmap, not the six-mode summary.
    heatmap = Document(heatmap_page('theme-relevance'))
    for theme in THEMES:
        assert theme in heatmap.text
    for bank in BANKS.values():
        assert f'/flora/banking/{bank.slug}' in comparison.hrefs
    assert 'every other mode is non-monetary' in comparison.text
    assert 'not customer-confirmed budget or qualified commercial pipeline' in comparison.text
    assert 'safe-unavailable' not in first


def test_opportunities_have_values_feedback_and_preserve_originals():
    from copy import deepcopy
    from tests.flora_html_contract import Document
    from cios.applications.flora.banking_portfolio import opportunity_page, _opportunity_html
    opps = pipeline()
    before = deepcopy(opps)
    assert len(opps) >= 15
    for o in opps:
        assert o.id and o.value.low < o.value.midpoint < o.value.high
        assert o.value.low % 5 == 0 and o.value.high % 5 == 0 and o.value.midpoint % 5 == 0
        assert o.value.method and o.assumptions
    for o in BANKS['lloyds'].opportunities:
        html, status = opportunity_page('lloyds', o.id)
        assert status == 200
        assert o.title in Document(html).text
        assert 'Customer-confirmed budget: Unknown' in Document(html).text
    # Unwired legacy feedback buttons are no longer a capture workflow.
    component_html = _opportunity_html(opps[0])
    component = Document(component_html)
    assert not component.buttons and '<form' not in component_html
    assert opps[0].title in component.text
    assert 'Useful' in FEEDBACK_ACTIONS and 'Validated with customer' in FEEDBACK_ACTIONS
    assert pipeline() == before


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
    from tests.flora_html_contract import Document
    from cios.applications.flora.banking_portfolio import financial_history_page, opportunity_page
    for bank in BANKS.values():
        lo, hi, mid = totals(list(bank.opportunities))
        assert lo == sum(o.value.low for o in bank.opportunities)
        assert hi == sum(o.value.high for o in bank.opportunities)
        assert mid == sum(o.value.midpoint for o in bank.opportunities)
        assert bank.financial_interpretation and bank.likely_accelerate and bank.likely_buying_posture
        overview = Document(bank_page(bank.slug)[0])
        assert 'What the financial results imply' in overview.headings
        assert f'/flora/banking/{bank.slug}/financial-performance' in overview.hrefs
        assert Document(financial_history_page(bank.slug)).headings
        assert f'Illustrative, unverified commercial scenario sum: £{mid}m' in overview.text
        assert 'not customer-confirmed budget or qualified commercial pipeline' in overview.text
        for o in bank.opportunities:
            assert o.horizon_label in ('Immediate: 0–12 months', 'Near term: 12–24 months', 'Medium term: 24–36 months', 'Longer term: 36–60 months', 'Monitor', 'Unclear')
            assert o.earliest_entry and o.buying_window and o.programme_start and o.contract_duration
            assert o.horizon_rationale and o.accelerate_signal and o.delay_signal and o.supplier_position
            if not o.supplier_entries:
                assert o.supplier_position == 'No reliable view'
            detail, status = opportunity_page(bank.slug, o.id)
            assert status == 200
            assert 'Confirmed procurement dates / customer milestones / buying triggers: Unknown' in Document(detail).text


def test_increment_41_supplier_traction_is_sourced_or_human_labelled_and_unknown_is_bounded():
    from tests.flora_html_contract import Document
    from cios.applications.flora.banking_portfolio import opportunity_page
    allowed = {'Strong incumbent position', 'Gaining traction', 'Established relationship', 'Competitive field', 'Early signal', 'No reliable view'}
    for o in pipeline():
        assert o.supplier_position in allowed
        for entry in o.supplier_entries:
            assert entry.supplier_name and entry.source_date and entry.supporting_rationale
            assert entry.insight_basis in ('confirmed', 'inferred', 'human-supplied')
            assert entry.traction_label in allowed
    overview = Document(bank_page('santander-uk')[0])
    assert '/flora/banking/competitors' in overview.hrefs
    assert 'general market presence does not establish incumbency, renewal or displacement' in overview.text
    for opportunity in BANKS['santander-uk'].opportunities:
        if not opportunity.supplier_entries:
            assert opportunity.supplier_position == 'No reliable view'
        detail, status = opportunity_page('santander-uk', opportunity.id)
        assert status == 200
        if not opportunity.supplier_entries:
            assert 'No reliable view' in Document(detail).text
        else:
            for entry in opportunity.supplier_entries:
                assert entry.supplier_name in Document(detail).text and 'Inferred supplier position' in Document(detail).text


def test_increment_41_portfolio_cards_and_heatmap_are_scannable_with_expansion():
    from tests.flora_html_contract import Document
    from cios.applications.flora.banking_portfolio import heatmap_page
    portfolio = Document(portfolio_page())
    for bank in BANKS.values():
        assert bank.name in portfolio.text
        assert f'/flora/banking/{bank.slug}' in portfolio.hrefs
    # A scenario sum is not a confirmed pipeline; the full table is on demand.
    assert 'Scenario sizing assumptions and limits' in portfolio.headings
    for opportunity in pipeline():
        assert opportunity.title in portfolio.text
        assert opportunity.value.label in portfolio.text
    comparison = Document(heatmap_page('opportunity-value'))
    assert 'Compare UK banks' in comparison.headings
    assert '<table' in heatmap_page('opportunity-value')
    for bank in BANKS.values():
        assert bank.name in comparison.text
    assert 'Scenario sizing assumptions and limits' in comparison.headings
    assert 'qualified commercial pipeline' in comparison.text


def test_increment_41_analyst_rendering_quality_gates():
    html, _ = bank_page("lloyds")
    for text in ("writing-mode:horizontal-tb", "word-break:normal", "overflow-wrap:break-word", "@media print", "page-break-inside:avoid"):
        assert text in html
    assert "analyst-view" in html
    executive = html.split("12. Detailed inspection", 1)[0]
    assert "BK-ENT-" not in executive

import pytest

# Domain tests use an explicit fixture identity provider, never HTTP trust.
pytestmark = pytest.mark.usefixtures("verified_flora_test_authority")
