"""Source, Financial and editorial proof without issuer eligibility activation."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from cios.applications.flora import enterprise_economics as economics
from cios.applications.flora.financial_intelligence import candidate_analytics as financial
from cios.applications.flora.financial_intelligence import public_statements as public
from cios.applications.flora.research_intelligence import source_import
from tests.test_flora_public_financial import PATH, seal


def example(host, name, currency):
    record = json.loads(Path(PATH).read_text())
    url = 'https://' + host + '/isolated-eei2a-test'
    record.update(id='fixture-' + host, title='Synthetic statement package', publisher=name, url=url, retrieval_url=url)
    record['document_identity'].update(url=url, title=record['title'], publisher=name, version='fixture-v1')
    record['rights'].update(material_exceptions=[], contract_restriction_found=False,
                            attribution_url='https://' + host + '/')
    bindings = []
    for year in (2024, 2025):
        for kind, metric, label, amount in (
            ('income', 'revenue', 'Revenue', 70),
            ('balance', 'cash', 'Cash and cash equivalents', 15),
            ('cash_flow', 'operating_cash', 'Net cash from operating activities', 31),
        ):
            value = amount + (year - 2024) * 2
            period = ({'kind': 'instant', 'as_at': f'{year}-12-31'} if kind == 'balance' else
                      {'kind': 'duration', 'start': f'{year}-01-01', 'end': f'{year}-12-31', 'fiscal_year_end': '12-31'})
            bindings.append({'key': f'{metric}-{year}', 'kind': 'financial_measurement', 'locator': f'Fixture note {year}/{kind}',
                             'facts': {'subject_id': record['id'], 'subject_name': name, 'perimeter': 'Synthetic consolidated group',
                                       'metric': metric, 'definition': label, 'period': period, 'statement': kind,
                                       'fiscal_year': year, 'accounting_basis': 'Statutory', 'accounting_standard': 'IFRS',
                                       'reported_label': label, 'state': 'actual', 'semantic_type': 'reported',
                                       'precision_dp': 0, 'rounding': 'reported_rounded',
                                       'sign_convention': 'Positive values as reported',
                                       'value': {'amount': str(value), 'unit': 'currency', 'currency': currency, 'scale': 'millions'},
                                       'original_display': f'{currency} {value}m'}})
    record['fact_bindings'] = bindings
    return seal(record), (record['id'], name)


@pytest.mark.parametrize(('host','name','currency'), [
    ('www.nationwide.co.uk', 'Nationwide synthetic', 'GBP'),
    ('corporate.easyjet.com', 'easyJet synthetic', 'GBP'),
])
def test_cross_issuer_statements_and_annual_comparison(host, name, currency, monkeypatch):
    if host == 'www.nationwide.co.uk':
        # Use the existing narrow official-origin route shape, no retrieval.
        record, subject = example(host, name, currency)
        url = 'https://www.nationwide.co.uk/-/assets/nationwidecouk/documents/about/how-we-are-run/results-and-accounts/2026/2026-preliminary-results.pdf'
        record.update(url=url, retrieval_url=url)
        record['document_identity']['url'] = url
        seal(record)
    else:
        record, subject = example(host, name, currency)
    def forbidden(*args, **kwargs):
        raise AssertionError('Private-run service called')
    monkeypatch.setattr(financial, 'find_existing_run', forbidden)
    monkeypatch.setattr(financial, 'create_run', forbidden)
    monkeypatch.setattr(financial, 'read_analysis', forbidden)
    lines = public.project(record, subject=subject)
    assert len(lines) == 6
    assert {row.period.kind for row in lines} == {'instant', 'duration'}
    assert {row.fiscal_year for row in lines} == {2024, 2025}
    revenue = [line for line in lines if line.metric == 'revenue']
    spec = financial.Derivation(derivation_id='fixture-delta', formula='difference', comparison='duration_dates',
                                inputs=tuple(financial.InputReference(measurement_id=line.measurement_id, revision=line.revision)
                                             for line in revenue))
    result = public.compare(lines, spec)
    assert result['value'] == '2'
    assert result['inputs'] == [item.model_dump() for item in spec.inputs]
    facts = economics.source_statement_summary(record, subject=subject, fixture=True)
    assert all(item in facts for item in ('Income statement', 'Balance sheet', 'Cash flow statement', name, 'Synthetic review fixture'))
    assert 'GBP 72m' in facts
    insight = economics.source_statement_summary(record, subject=subject, insight=True, fixture=True)
    assert 'Assets and obligations describe' in insight
    record['withdrawn'] = True
    assert economics.source_statement_summary(record, subject=subject) == ''


def test_restatement_history_does_not_return_old_value():
    record, subject = example('corporate.easyjet.com', 'Synthetic travel', 'GBP')
    prior = record['fact_bindings'][0]
    prior['facts']['revision_state'] = 'superseded'
    current = deepcopy(prior)
    current['key'] += '-restated'
    current['facts'].update(revision_state='restated', supersedes=financial.stable_hash(prior), original_display='GBP 71m')
    current['facts']['value']['amount'] = '71'
    record['fact_bindings'].append(current)
    seal(record)
    lines = public.project(record, subject=subject)
    assert {line.revision_state for line in lines} == {'original', 'restated', 'superseded'}
    rendered = economics.source_statement_summary(record, subject=subject)
    assert 'Restated' in rendered and 'GBP 71m' in rendered and 'GBP 70m' not in rendered
    current['withdrawn'] = True
    assert economics.source_statement_summary(seal(record), subject=subject) == ''


@pytest.mark.parametrize('field,value', [
    ('subject_id', 'other'), ('statement', 'balance'), ('accounting_basis', ''), ('state', 'forecast'),
    ('value', {'amount': '70', 'unit': 'percentage', 'currency': 'GBP', 'scale': 'millions'}),
])
def test_invalid_bound_meaning_fails_closed(field, value):
    record, subject = example('corporate.easyjet.com', 'Synthetic travel', 'GBP')
    record['fact_bindings'][0]['facts'][field] = value
    assert public.project(seal(record), subject=subject) == ()


def test_lifecycle_and_restricted_issuers_remain_inactive():
    record, subject = example('www.lloydsbankinggroup.com', 'Synthetic restricted', 'GBP')
    # Concrete restriction, rather than a publisher-name ban.
    record['rights']['contract_restriction_found'] = True
    assert public.project(record, subject=subject) == ()
    assert len(financial.public_factual_projection()['facts']) == 3
    record, subject = example('investor.equinix.com', 'Synthetic data centres', 'USD')
    # Concrete restriction, rather than a publisher-name ban.
    record['rights']['contract_restriction_found'] = True
    assert public.project(record, subject=subject) == ()
    record, subject = example('www.bt.com', 'Synthetic telecoms', 'GBP')
    # Concrete restriction, rather than a publisher-name ban.
    record['rights']['contract_restriction_found'] = True
    assert public.project(record, subject=subject) == ()
    assert source_import.official_url('https://corporate.easyjet.com/test')
    eligible = public.nationwide_lines(financial.public_nationwide_projection())
    assert len(eligible) == 5 and all(line.statement == 'income' for line in eligible)
    html = economics.statement_summary(eligible)
    assert 'No eligible figures' in html and '£6,378m' in html


def test_reported_percentage_stays_out_of_monetary_arithmetic():
    record, subject = example('corporate.easyjet.com', 'Synthetic travel', 'GBP')
    cash = record['fact_bindings'][1]['facts']
    cash.update(metric='capital_ratio', definition='Synthetic capital ratio', reported_label='Synthetic capital ratio',
                value={'amount': '15', 'unit': 'percentage', 'currency': None, 'scale': 'units'}, original_display='15%')
    lines = public.project(seal(record), subject=subject)
    assert len(lines) == 6 and '15%' in economics.statement_summary(lines)
    spec = financial.Derivation(derivation_id='bad-pair', formula='difference', comparison='stock_dates',
                                inputs=tuple(financial.InputReference(measurement_id=row.measurement_id, revision=row.revision)
                                             for row in (lines[1], lines[4])))
    with pytest.raises(ValueError):
        public.compare(lines, spec)


def test_comparison_rejects_different_basis_or_period_length():
    record, subject = example('corporate.easyjet.com', 'Synthetic travel', 'GBP')
    for change in (
        {'accounting_standard': 'Different standard'},
        {'period': {'kind': 'duration', 'start': '2025-07-01', 'end': '2025-12-31', 'fiscal_year_end': '12-31'}},
        {'perimeter': 'A separate legal entity'},
    ):
        changed = deepcopy(record)
        changed['fact_bindings'][3]['facts'].update(change)
        lines = public.project(seal(changed), subject=subject)
        assert len(lines) == 6
        spec = financial.Derivation(
            derivation_id='invalid-bridge', formula='difference', comparison='duration_dates',
            inputs=tuple(financial.InputReference(measurement_id=row.measurement_id, revision=row.revision)
                         for row in (lines[0], lines[3])),
        )
        with pytest.raises(ValueError):
            public.compare(lines, spec)


def test_nationwide_summary_preserves_customer_view_and_no_private_access(monkeypatch):
    from cios.applications.flora import visual_streams
    from cios.applications.flora import document_review
    def forbidden(*args, **kwargs):
        raise AssertionError('Private-run service called')
    monkeypatch.setattr(document_review, 'load_run', forbidden)
    html = visual_streams.render('/industries/banking', {'selected': ['nationwide']})
    main = html.split('<main ', 1)[1].split('</main>', 1)[0]
    assert 'id="eei-summary"' in main and 'class="legal-notice"' in main
    assert '<details' not in main
