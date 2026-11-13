from cios.applications.flora.banking_portfolio import BANKS, PESTLE_FORCES, bank_page, compare_page, pipeline, portfolio_page, totals


def test_financial_behaviour_narrative_has_required_causal_sections():
    from tests.flora_html_contract import Document
    from cios.applications.flora.banking_portfolio import financial_history_page
    for bank in BANKS.values():
        html, status = bank_page(bank.slug)
        overview = Document(html)
        assert status == 200 and 'What the financial results imply' in overview.headings
        assert bank.buying_posture_detail in overview.text
        assert bank.visible_response in overview.text and bank.unresolved_pressure in overview.text
        assert f'/flora/banking/{bank.slug}/financial-performance' in overview.hrefs
        history = Document(financial_history_page(bank.slug))
        if bank.slug == 'lloyds':
            for heading in ('Income', 'Profit', 'Costs', 'Capital'):
                assert heading in history.headings
            for causal_part in ('What changed:', 'Management pressure:', 'Likely behaviour:', 'Commercial implication:'):
                assert causal_part in history.text
        else:
            assert 'unavailable metrics are not fabricated' in history.text
        assert bank.management_pressure and bank.likely_behaviour and bank.buying_posture_detail


def test_every_bank_has_reinvention_pressure_independent_of_priority():
    levels = {bank.reinvention_pressure for bank in BANKS.values()}
    assert levels <= {"Extreme", "High", "Material", "Emerging", "Low", "Insufficient view"}
    assert all(bank.pressure_drivers and bank.pressure_horizon for bank in BANKS.values())
    same_pressure_different_priority = [bank.priority for bank in BANKS.values() if bank.reinvention_pressure == "High"]
    assert len(set(same_pressure_different_priority)) > 1


def test_every_major_opportunity_has_explicit_barrier_and_supplier_effect():
    for opportunity in pipeline():
        assert opportunity.barrier
        assert opportunity.barrier_severity in {"High", "Material"}
        assert opportunity.barrier_effect
        assert opportunity.barrier_supplier_effect
        assert opportunity.barrier_reducer


def test_pestle_forces_map_to_specific_banks_themes_and_non_generic_outputs():
    from tests.flora_html_contract import Document
    from cios.applications.flora.banking_portfolio import industry_outlook_page
    # Forces have their own outlook, rather than being repeated in comparisons.
    comparison = Document(compare_page())
    assert '/flora/banking' in comparison.hrefs
    from cios.applications.flora.banking_portfolio import banking_landing_page
    assert any(h.split('#')[0] == '/flora/banking/outlook' for h in Document(banking_landing_page()).hrefs)
    outlook = Document(industry_outlook_page())
    for category, force in PESTLE_FORCES.items():
        assert category in outlook.text and force['force'] in outlook.text
        assert force['banks'] and force['themes']
        for bank in force['banks']:
            assert bank in outlook.text
    assert 'not an enterprise-specific qualified Material Pressure' in outlook.text


def test_supplier_names_render_and_unnamed_labels_are_suppressed_when_names_exist():
    from tests.flora_html_contract import Document
    from cios.applications.flora.banking_portfolio import opportunity_page
    named = set()
    for bank in BANKS.values():
        for opportunity in bank.opportunities:
            html, status = opportunity_page(bank.slug, opportunity.id)
            assert status == 200
            text = Document(html).text
            for entry in opportunity.supplier_entries:
                named.add(entry.supplier_name)
                assert entry.supplier_name in text
                assert entry.supporting_rationale in text
                assert 'Basis (' + entry.insight_basis + ')' in text
            if not opportunity.supplier_entries:
                assert 'No reliable view' in text
    assert {'Google Cloud', 'Microsoft'} <= named


def test_supplier_relationships_are_source_backed_or_human_labelled():
    for opportunity in pipeline():
        for entry in opportunity.supplier_entries:
            assert entry.supplier_name
            assert entry.source_date
            assert entry.supporting_rationale
            assert entry.insight_basis in {"confirmed", "inferred", "human-supplied"}


def test_heatmap_cells_show_pressure_barrier_supplier_and_whitespace():
    from tests.flora_html_contract import Document
    from cios.applications.flora.banking_portfolio import COMPARE_MODES, opportunity_page
    comparison = Document(compare_page())
    for mode in COMPARE_MODES:
        assert mode in comparison.headings
    # Substantial causal detail is in each opportunity, not repeated in every cell.
    for bank in BANKS.values():
        for opportunity in bank.opportunities:
            detail, status = opportunity_page(bank.slug, opportunity.id)
            doc = Document(detail)
            assert status == 200
            for heading in ('Current barrier', 'Supplier landscape', 'Competitive whitespace', 'Recommended next action'):
                assert heading in doc.headings
            assert opportunity.barrier in doc.text
            assert opportunity.whitespace in doc.text
            assert opportunity.next_action in doc.text


def test_industry_opportunity_totals_reconcile_to_account_opportunities():
    from tests.flora_html_contract import Document
    html = Document(compare_page())
    _, _, portfolio_mid = totals()
    assert sum(opportunity.value.midpoint for opportunity in pipeline()) == portfolio_mid
    account_totals = []
    for bank in BANKS.values():
        total = sum(opportunity.value.midpoint for opportunity in bank.opportunities)
        account_totals.append(total)
        assert f'Illustrative, unverified commercial scenario sum: £{total}m' in html.text
    assert sum(account_totals) == portfolio_mid == 910
    assert 'Scenarios may overlap; their sum does not establish additive funded demand' in html.text
    assert 'not customer-confirmed budget or qualified commercial pipeline' in html.text


def test_existing_opportunity_values_remain_unchanged_and_internal_codes_excluded_from_executive_views():
    assert totals() == (630, 1280, 910)
    executive = portfolio_page() + compare_page().split("Detailed inspection", 1)[0]
    assert "BK-ENT-" not in executive
    assert "COH-" not in executive


def test_rendered_acceptance_artefacts_exist():
    from tests.flora_html_contract import Document
    from cios.applications.flora.banking_portfolio import industry_outlook_page, heatmap_page, competitors_page, opportunity_page
    comparison = Document(compare_page())
    # Current dedicated destinations preserve information without a single long page.
    for route in ('/flora/banking', '/flora/banking/compare', '/flora/banking/competitors'):
        assert route in comparison.hrefs
    assert 'Prioritised industry-force board' in Document(industry_outlook_page()).headings
    assert '<table' in heatmap_page('opportunity-value')
    for bank in BANKS.values():
        assert bank.name in Document(heatmap_page('opportunity-value')).text
    competitors, status = competitors_page()
    assert status == 200 and 'Competitor capability landscape' in Document(competitors).headings
    assert 'Scenario sizing assumptions and limits' in comparison.headings
    lloyds = Document(bank_page('lloyds')[0])
    assert 'Working reinvention-pressure interpretation' in lloyds.headings
    for opportunity in BANKS['lloyds'].opportunities:
        assert f'/flora/banking/lloyds/opportunity/{opportunity.id}' in lloyds.hrefs
        detail, status = opportunity_page('lloyds', opportunity.id)
        assert status == 200
        assert all(h in Document(detail).headings for h in ('Current barrier','Competitive whitespace'))

import pytest

# Domain tests use an explicit fixture identity provider, never HTTP trust.
pytestmark = pytest.mark.usefixtures("verified_flora_test_authority")
