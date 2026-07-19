from cios.applications.flora.banking_portfolio import BANKS, PESTLE_FORCES, bank_page, compare_page, pipeline, portfolio_page, totals


def test_financial_behaviour_narrative_has_required_causal_sections():
    for bank in BANKS.values():
        html, status = bank_page(bank.slug)
        assert status == 200
        assert "What the financial results imply about behaviour" in html
        for heading in ("Financial position", "Management pressure", "Likely behaviour", "Buying posture", "What would change the view"):
            assert heading in html
        assert bank.management_pressure
        assert bank.likely_behaviour
        assert bank.buying_posture_detail


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
    html = compare_page()
    for category, force in PESTLE_FORCES.items():
        assert category in html
        assert force["force"] in html
        assert force["banks"]
        assert force["themes"]
        for bank in force["banks"]:
            assert bank in html
    assert "does not affect all banks equally" in html
    assert "generic" not in html.lower()


def test_supplier_names_render_and_unnamed_labels_are_suppressed_when_names_exist():
    html = compare_page()
    assert "Google Cloud" in html
    assert "Microsoft" in html
    assert "Supplier: Google Cloud" in html or "Google Cloud —" in html
    google_cell_start = html.index("Google Cloud")
    assert "No reliable view" not in html[max(0, google_cell_start-80):google_cell_start+180]


def test_supplier_relationships_are_source_backed_or_human_labelled():
    for opportunity in pipeline():
        for entry in opportunity.supplier_entries:
            assert entry.supplier_name
            assert entry.source_date
            assert entry.supporting_rationale
            assert entry.insight_basis in {"confirmed", "inferred", "human-supplied"}


def test_heatmap_cells_show_pressure_barrier_supplier_and_whitespace():
    html = compare_page()
    for term in ("Pressure:", "Supplier:", "Barrier:", "Whitespace:", "Financial behaviour link", "Next commercial action"):
        assert term in html


def test_industry_opportunity_totals_reconcile_to_account_opportunities():
    html = compare_page()
    _, _, portfolio_mid = totals()
    force_total = sum(opportunity.value.midpoint for opportunity in pipeline())
    assert force_total == portfolio_mid
    assert f"Flora working estimate £{portfolio_mid}m" in html or f"Flora working estimate: £{portfolio_mid}m" in html


def test_existing_opportunity_values_remain_unchanged_and_internal_codes_excluded_from_executive_views():
    assert totals() == (630, 1280, 910)
    executive = portfolio_page() + compare_page().split("Detailed inspection", 1)[0]
    assert "BK-ENT-" not in executive
    assert "COH-" not in executive


def test_rendered_acceptance_artefacts_exist():
    lloyds, _ = bank_page("lloyds")
    industry = compare_page()
    for artefact in ("UK Banking PESTLE view", "Industry reinvention map", "What is happening in UK Banking", "Commercial heatmap", "Supplier landscape", "Whitespace analysis", "Industry opportunity roll-up"):
        assert artefact in industry
    for artefact in ("What the financial results imply about behaviour", "Reinvention pressure", "Reinvention barriers", "Reinvention opportunities"):
        assert artefact in lloyds
