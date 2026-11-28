"""Regulatory Financial statements, presentation, withdrawal and comparability."""
from copy import deepcopy

from cios.applications.flora import lloyds_financials as f, lloyds_gold as gold
from cios.applications.flora.financial_intelligence import candidate_analytics, chart
from cios.applications.flora.research_intelligence import statement_sources

def test_real_group_and_divisional_reconciliations():
    dataset = f.current()
    assert len(dataset) == 133
    body = f.earnings(dataset, '#evidence')
    for expected in ('14,819', '6,582', '6,625', '1,947', '851', 'Quarterly earnings',
                     '2,332', '2,268', '10,827', '1,002', '19,422', '6,661'):
        assert expected in body
    body = f.segments(dataset, '#evidence')
    for expected in ('2,256', '1,425', '245', '289', '4,215', '4,293', '3,561', '3,504'):
        assert expected in body
    assert '325,832' in f.funding(dataset, '#evidence')
    assert '49.3%' in f.capital(dataset, '#evidence')
    assert 'full-year' in f.capital(dataset, '#evidence')


def test_withdrawal_hides_filing_values_and_dependent_outputs(monkeypatch):
    read = statement_sources._read

    def withdrawn(path):
        record = read(path)
        if path.name == 'LBG-EDGAR-2026-Q3-RESULTS.json':
            record = deepcopy(record)
            record['withdrawn'] = True
        return record

    monkeypatch.setattr(statement_sources, '_read', withdrawn)
    dataset = f.current()
    assert 'Income to statutory profit' not in f.earnings(dataset, '#evidence')
    assert 'Quarterly earnings' not in f.earnings(dataset, '#evidence')
    assert 'Statutory income and expenses' in f.earnings(dataset, '#evidence')
    assert 'FY2026 guidance' not in f.capital(dataset, '#evidence')
    assert '4,293' in f.segments(dataset, '#evidence')
    assert 'Q3-RESULTS' not in f.evidence(dataset)


def test_source_version_mismatch_fails_closed(monkeypatch):
    read = statement_sources._read

    def invalid(path):
        record = read(path)
        if path.name == 'LBG-EDGAR-2026-H1.json':
            record['document_identity']['version'] = 'wrong-revision'
        return record

    monkeypatch.setattr(statement_sources, '_read', invalid)
    assert not f.segments(f.current(), '#evidence')


def test_public_view_never_reads_financial_runs_and_keeps_old_investor_hold(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Private run used during public rendering')

    assert len(candidate_analytics.public_factual_projection()['facts']) == 3
    for method in ('read_analysis', 'find_existing_run', 'create_run'):
        monkeypatch.setattr(candidate_analytics, method, forbidden)
    text = gold.render({'focus': ['economics'], 'detail': ['income']})
    assert '1,947' in text and '#financial-evidence' in text and '.pdf' not in text


def test_chart_uses_same_typed_contract_for_equinix_without_currency_conversion():
    subject = ('research-subject:equinix-inc-group', 'Equinix, Inc.')
    data = f.public_statements.statement_series(subject)
    rows = [(str(line.fiscal_year), line.value.amount) for line in data if line.metric == 'revenue']
    body = chart.bars('Equinix revenue', 'Group reported · USD million', rows)
    assert '9,217' in body and 'USD million' in body and 'GBP' not in body


def test_changed_underlying_basis_suppresses_bridge_without_hiding_statutory_figures():
    dataset = f.current()
    key = (f.GROUP, 'u_cost', '2026-09-30', '2026-01-01')
    row, fact = dataset[key]
    dataset[key] = row.model_copy(update={'accounting_basis': 'Incompatible'}), fact
    body = f.earnings(dataset, '#evidence')
    assert 'Income to statutory profit' not in body
    assert 'What moved pretax profit?' not in body
    assert 'Statutory income and expenses' in body


def test_public_document_withdrawal_also_removes_report_equivalents(monkeypatch):
    from cios.applications.flora.research_intelligence import source_import

    current_source_records = source_import.current_source_records

    def restricted(domain):
        records = deepcopy(current_source_records(domain))
        next(record for record in records if record.get('id') == 'PR-LBG-Q326')['withdrawn'] = True
        return records

    monkeypatch.setattr(source_import, 'current_source_records', restricted)
    opening = gold.render({}, canonical=True)
    assert 'Lloyds in one minute' in opening
    assert 'Where earnings came from' not in opening
    assert '+1,947m' not in opening
    dataset = f.current()
    assert all('Q3' not in row.source.source_id for row, _ in dataset.values())
    assert '1,947' not in f.earnings(dataset, '#evidence')
    assert '6,661' in f.earnings(dataset, '#evidence')
    assert '4,293' in f.segments(dataset, '#evidence')


def test_opening_reconciles_all_signed_effects_and_compatible_subperiods():
    opening = gold.render({}, canonical=True).split('One Group, different economic engines')[0]
    for amount in ('3,926', '+289', '-34', '+112', '4,293', '2,332', '6,625',
                   '+1,262', '+851', '-70', '-312', '-35', '+251', '+1,947'):
        assert amount in opening
    assert 'does not allocate it to the businesses' in opening

    data = f.current()
    key = (f.GROUP, 'pbt', '2026-09-30', '2026-07-01')
    row, fact = data[key]
    data[key] = row.model_copy(update={'perimeter': 'Different entity'}), fact
    assert not f.year_to_date_bridge(data)
    assert f.comparable_group_change(data)


def test_connected_wealth_evidence_updates_and_withdraws_across_views(monkeypatch):
    from dataclasses import replace
    from decimal import Decimal
    from cios.applications.flora import lloyds_connections

    get = gold.facts_for
    key = 'LBG-CE-INVESTMENTACCOUNTS'
    retained_path = lloyds_connections.BUSINESS['retirement']
    observed = {}

    def with_state(data):
        facts = get(data)
        item = facts[key]
        observed['facts'] = facts.copy()
        if observed['mode'] == 'corrected':
            # An isolated fixture for an already admitted replacement returned by the owner.
            sources = tuple(replace(ref, quote=ref.quote.replace('84,000', '84,001').replace('84000', '84001'))
                            for ref in item.sources)
            facts[key] = replace(item, text='84,001 investment accounts opened',
                                 value=Decimal('84001'), sources=sources)
        elif observed['mode'] == 'withdrawn':
            facts[key] = replace(item, freshness='withdrawn')
        return facts

    monkeypatch.setattr(gold, 'facts_for', with_state)
    observed['mode'] = 'current'
    open_pages = ({'focus': ['retirement']},
                  {'stream': ['inside'], 'focus': ['operations'], 'detail': ['journey-insurance'],
                   'subject': ['retirement']},
                  {'stream': ['forces'], 'focus': ['strategy'], 'detail': ['investigations'],
                   'subject': ['retirement']})
    for query in open_pages:
        assert retained_path.title in gold.render(query, canonical=True)
    assert lloyds_connections.evidence_for(retained_path, observed['facts'])

    observed['mode'] = 'corrected'
    for query in open_pages:
        assert '84,001' in gold.render(query, canonical=True)
    observed['mode'] = 'withdrawn'
    for query in open_pages:
        assert retained_path.title not in gold.render(query, canonical=True)


def test_generic_compatibility_on_equinix_without_lloyds_axes():
    rows = f.public_statements.statement_series(('research-subject:equinix-inc-group', 'Equinix, Inc.'))
    revenue = sorted((row for row in rows if row.metric == 'revenue'), key=lambda row: row.fiscal_year)
    assert len(revenue) >= 2
    first, second = revenue[-2:]
    assert f.public_statements.comparable_durations((second,), (first,))
    foreign = second.model_copy(update={'perimeter': 'Unaffiliated entity'})
    assert not f.public_statements.comparable_durations((foreign,), (first,))


def test_existing_source_withdrawal_omits_all_wealth_path_destinations(monkeypatch):
    from cios.applications.flora import visual_streams
    from cios.applications.flora.research_intelligence import source_import

    original_data = visual_streams.current_data
    original_records = source_import.current_source_records

    def restricted(rows):
        rows = deepcopy(rows)
        for row in rows:
            if row.get('id') == 'LCE-ANNUAL-OPERATIONS':
                row['withdrawn'] = True
        return rows

    def data(ctx):
        current = deepcopy(original_data(ctx))
        current['sources'] = restricted(current['sources'])
        return current

    monkeypatch.setattr(visual_streams, 'current_data', data)
    monkeypatch.setattr(source_import, 'current_source_records', lambda domain: restricted(original_records(domain)))

    for query in ({'focus': ['retirement']},
                  {'stream': ['inside'], 'focus': ['operations'], 'detail': ['journey-insurance'],
                   'subject': ['retirement']},
                  {'stream': ['forces'], 'focus': ['strategy'], 'detail': ['investigations'],
                   'subject': ['retirement']}):
        html = gold.render(query, canonical=True)
        assert 'Investment account openings and business resources' not in html
        assert '84,000' not in html
    assert '£6.625bn' in gold.render({}, canonical=True)
