from cios.applications.flora.financial_intelligence.normalisation import canonicalise_financial_claim, normalise_reporting_period, resolve_metric, normalise_amount, rounding_compatible


def _claim(**kw):
    base = dict(claim_type='financial_metric_reported', canonical_enterprise_id='bt-group-plc', predicate='Revenue', reported_amount='19654', currency='GBP', reported_scale='millions', period='Year ended 31 March 2026', state='actual', source_excerpt='Income statement £m Year ended 31 March 2026 Revenue 19,654', accounting_basis='statutory', confidence=90, evidence_id='ev1', source_identity='doc', source_locator='p1')
    base.update(kw)
    return base


def test_metric_aliases_resolve_and_unknown_metrics_do_not_slugify():
    assert resolve_metric('Reported revenue')[0].canonical_metric_id == 'revenue'
    assert resolve_metric('Adjusted EBITDA')[0].canonical_metric_id == 'adjusted_ebitda'
    assert resolve_metric('Customer joy score') == (None, 'unsupported_metric')
    claim, reasons = canonicalise_financial_claim(_claim(predicate='Customer joy score'))
    assert 'unsupported_metric' in reasons
    assert claim['affected_attribute'] is None


def test_period_texts_resolve_to_one_identity_and_original_text_is_retained():
    assert normalise_reporting_period('FY26').canonical_period_id == 'FY26'
    assert normalise_reporting_period('FY 2026').canonical_period_id == 'FY26'
    p = normalise_reporting_period('Year ended 31 March 2026')
    assert p.canonical_period_id == 'FY26'
    assert p.original_period_text == 'Year ended 31 March 2026'
    claim, reasons = canonicalise_financial_claim(_claim())
    assert not reasons
    assert claim['period'] == 'FY26'
    assert claim['original_period_text'] == 'Year ended 31 March 2026'
    assert claim['affected_attribute'] == 'financial_performance.metrics.revenue.FY26.actual'


def test_decimal_arithmetic_exact_values_and_no_float_artifacts():
    assert normalise_amount('8.2', 'billions') == 8200000000
    claim, reasons = canonicalise_financial_claim(_claim(reported_amount='8.2', reported_scale='billions', predicate='Adjusted EBITDA', accounting_basis='adjusted', source_excerpt='Adjusted EBITDA £8.2bn FY26'))
    assert not reasons
    assert claim['normalised_amount'] == 8200000000
    assert '8199999999' not in str(claim)


def test_rounding_compatibility_examples_and_incompatible_values():
    assert rounding_compatible('19.7', 'billions', '19654000000')
    assert rounding_compatible('8.2', 'billions', '8230000000')
    assert rounding_compatible('5.1', 'billions', '5127000000')
    assert not rounding_compatible('19.1', 'billions', '19654000000')


def test_accounting_basis_not_invented_and_narrative_guidance_excluded():
    _, reasons = canonicalise_financial_claim(_claim(accounting_basis=None, source_excerpt='Revenue £19,654m FY26'))
    assert 'accounting_basis_ambiguous' in reasons
    narrative, reasons = canonicalise_financial_claim(_claim(predicate='cash flow inflection', reported_amount=None, source_excerpt='cash flow inflection to around £2bn in FY27, rising to around £3bn by the end of the decade'))
    assert 'non_numeric_narrative' in reasons or 'unsupported_metric' in reasons
    assert narrative.get('normalised_amount') is None
