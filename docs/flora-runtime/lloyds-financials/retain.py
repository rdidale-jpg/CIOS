"""Rebuild the bounded record set from locally retrieved, original EDGAR HTML."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from lxml import html

SUBJECT = ['research-subject:lloyds-banking-group-plc', 'Lloyds Banking Group plc']
ORIGIN = 'https://www.sec.gov'
PREFIX = '/Archives/edgar/data/1160106/'
FILES = {
    'FY25': ('000116010626000010', 'lyg-20251231.htm', '2026-02-13'),
    'H1': ('000116010626000022', 'lyg-20260630.htm', '2026-07-30'),
    'Q3': ('000116010626000026', 'lbg6-kimsxq32026.htm', '2026-10-29'),
    'Q3-RESULTS': ('000165495426009203', 'a8900a.htm', '2026-10-29'),
}


def cells(table):
    return [
        [' '.join(cell.text_content().split()) for cell in row.xpath('./td|./th')
         if cell.text_content().strip()]
        for row in table.xpath('./tr|./tbody/tr')
    ]


def rows(table):
    result = {}
    for row in cells(table):
        if len(row) > 1:
            result.setdefault(row[0], row[1:])
    return result


def amount(raw):
    return {'–': '0', '—': '0'}.get(raw, raw.replace('£', '').replace('bn', '')
                                  .replace('%', '').replace(',', '').replace('(', '-').replace(')', ''))


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def retain(code, raw, inspected):
    accession, filename, publication = FILES[code]
    url = ORIGIN + PREFIX + accession + '/' + filename
    version = 'sha256:' + hashlib.sha256(raw).hexdigest()
    form = '20-F, annual accounts' if code == 'FY25' else '6-K'
    title = f'Lloyds Banking Group Form {form} · ' + ('FY2025' if code == 'FY25' else f'{code} 2026')
    identity = dict(url=url, publisher=SUBJECT[1], title=title, published=publication, version=version)
    original = html.fromstring(raw).xpath('//table')
    bindings = []

    def bind(metric, label, raw_value, year, locator, *, perimeter='Consolidated Group',
             basis='Statutory', stock=False, unit='currency', scale='millions', period_end=None, start=None):
        end = period_end or f'{year}-' + {'H1': '06-30', 'Q3': '09-30', 'Q3-RESULTS': '09-30'}[code]
        period = {'kind': 'instant', 'as_at': end} if stock else {
            'kind': 'duration', 'start': start or f'{year}-01-01', 'end': end, 'fiscal_year_end': '12-31'}
        value = amount(raw_value)
        sign = 'Signed expense or adjustment as reported.'
        if metric in {'remove_restructuring', 'remove_volatility'}:
            sign = 'Filing sign is statutory to underlying. Reverse for underlying to statutory.'
        bindings.append({
            'key': f'lbg-{code.lower()}-{metric}-{end}-{perimeter.lower().replace(" ", "-")}',
            'kind': 'financial_measurement', 'locator': locator,
            'facts': dict(subject_id=SUBJECT[0], subject_name=SUBJECT[1], perimeter=perimeter,
                          metric=metric, definition=label, accounting_basis=basis,
                          accounting_standard='IFRS' if basis == 'Statutory' else '',
                          period=period, value=dict(amount=value, unit=unit,
                          currency='GBP' if unit == 'currency' else None, scale=scale),
                          original_display=raw_value, precision_dp=len(value.split('.')[-1]) if '.' in value else 0,
                          rounding='reported_rounded', state='actual', semantic_type='reported',
                          statement='balance' if stock else 'segment' if basis == 'Underlying segment reporting' else 'income',
                          fiscal_year=year, reported_label=label, sign_convention=sign, caveats=[]),
        })

    years = (2026, 2025)
    end_dates = {'FY25': '31 December', 'H1': '30 June', 'Q3': '30 September', 'Q3-RESULTS': '30 September'}
    if code == 'FY25':
        annual = rows(original[676])
        for index, year in enumerate((2025, 2024)):
            for key, label, note in [('nii', 'Net interest income', True), ('fees', 'Net fee and commission income', True),
                                     ('other', 'Other income', False), ('total', 'Total income', False),
                                     ('expenses', 'Operating expenses', True), ('impairment', 'Impairment', True),
                                     ('pbt', 'Profit before tax', False)]:
                bind(key, label, annual[label][index+int(note)], year,
                     f'Audited consolidated income statement · {year} column as presented · {label}',
                     period_end=f'{year}-12-31')
    elif code != 'Q3-RESULTS':
        statutory = rows(original[9 if code == 'H1' else 4])
        metrics = {'pbt': 'Profit before tax'}
        if code == 'Q3':
            metrics.update(nii='Net interest income', other='Other income', total='Total income',
                           expenses='Operating expenses', impairment='Impairment')
        else:
            metrics['fees'] = 'Net fee and commission income'
        for index, year in enumerate(years):
            for key, label in metrics.items():
                bind(key, label, statutory[label][index], year,
                     f'Consolidated income statement · to {end_dates[code]} {year} · {label}')

    if code == 'Q3-RESULTS':
        performance = rows(original[0])
        bridge = {
            'u_nii': 'Underlying net interest income', 'u_other': 'Underlying other income',
            'u_lease': 'Operating lease depreciation', 'u_net': 'Net income',
            'u_cost': 'Operating costs', 'u_remediation': 'Remediation',
            'u_impairment': 'Underlying impairment charge', 'u_profit': 'Underlying profit',
            'restructuring': 'Restructuring', 'volatility': 'Volatility and other items',
        }
        for index, year in enumerate(years):
            for key, label in bridge.items():
                basis = 'Underlying performance' if key.startswith('u_') else 'Underlying-to-statutory adjustment'
                bind(key, label, performance[label][index], year,
                     f'Summary results · nine months to September {year} · {label}', basis=basis)
            for key, fragment in [('cir', 'Cost:income ratio'), ('rote', 'Return on tangible equity'),
                                  ('nim', 'Banking net interest margin')]:
                label = next(name for name in performance if name.startswith(fragment))
                bind(key, fragment, performance[label][index], year,
                     f'Summary results · nine months to September {year} · {fragment}',
                     basis='Issuer performance measure', unit='percentage', scale='units')
        quarterly = rows(original[2])['Statutory profit before tax']
        for index, year, month, first_month, day in [(0, 2026, 9, 7, 30), (1, 2026, 6, 4, 30),
                 (3, 2026, 3, 1, 31), (4, 2025, 12, 10, 31), (5, 2025, 9, 7, 30),
                 (6, 2025, 6, 4, 30), (7, 2025, 3, 1, 31)]:
            end = f'{year}-{month:02}-{day}'
            bind('pbt', 'Profit before tax', quarterly[index], year,
                 f'Quarterly information · quarter ended {end} · statutory profit before tax',
                 period_end=end, start=f'{year}-{first_month:02}-01')
        balance = rows(original[1])
        for key, label, unit, scale in [
            ('wholesale', 'Wholesale funding', 'currency', 'billions'),
            ('lcr', 'Liquidity coverage ratio', 'percentage', 'units'),
            ('nsfr', 'Net stable funding ratio', 'percentage', 'units'),
            ('net_loans', 'Underlying loans and advances', 'currency', 'billions'),
        ]:
            found = next(name for name in balance if name.startswith(label))
            bind(key, label, balance[found][0], 2026, f'Summary balance sheet · September 2026 · {label}',
                 basis='Issuer reported measure', stock=True, unit=unit, scale=scale)
        text = ' '.join(html.fromstring(raw).text_content().split())
        assert '£5.2 billion of total income from structural hedge balances' in text
        assert 'September 2025: £4.0 billion' in text
        assert 'Cost:income ratio of less than 50%' in text
        assert 'Return on tangible equity of greater than 16%' in text
        for index, year in enumerate(years):
            bind('hedge', 'Structural hedge income', ('5.2', '4.0')[index], year,
                 f'Net interest income commentary · structural hedge · nine months ended September {year}',
                 basis='Issuer reported structural hedge income', scale='billions')

    if code == 'Q3':
        balance = rows(original[6])
        capital = rows(original[7])
        for index, end in enumerate(('2026-09-30', '2025-12-31')):
            for key, label in [('deposits', 'Customer deposits'), ('assets', 'Total assets'),
                               ('debt', 'Debt securities in issue at amortised cost'), ('equity', 'Total equity')]:
                bind(key, label, balance[label][index], int(end[:4]), f'Balance sheet · {end} · {label}',
                     stock=True, period_end=end)
            for key, label, unit, scale in [('rwa', 'Risk-weighted assets', 'currency', 'billions'),
                                            ('cet1', 'Common equity tier 1 ratio', 'percentage', 'units')]:
                bind(key, label, capital[label][index], int(end[:4]), f'Capital · {end} · {label}',
                     stock=True, period_end=end, unit=unit, scale=scale, basis='Prudential reported')
        portfolio = rows(original[12])
        for key, label in [('mortgages', 'UK mortgages'), ('cards', 'Credit cards'),
                           ('unsecured', 'UK unsecured loans and overdrafts'), ('motor', 'UK Motor Finance'),
                           ('retail_gross', 'Retail'), ('bcb_gross', 'Business and Commercial Banking'),
                           ('cib_gross', 'Corporate and Institutional Banking'), ('gross', 'Total gross lending')]:
            bind(key, label, portfolio[label][4], 2026, f'Credit risk · gross lending by stage · Total · {label}',
                 stock=True, basis='Gross customer lending before allowance')
    if code == 'H1':
        perimeters = ('Retail', 'Commercial Banking', 'Insurance Pensions and Investments', 'Other', 'Consolidated Group')
        for index, year in enumerate(years):
            segment = rows(original[119 if index == 0 else 122])
            for column, perimeter in enumerate(perimeters):
                for key, label in [('net', 'Underlying income, net of underlying operating lease depreciation'),
                                   ('cost', 'Underlying operating costs'), ('segment_pbt', 'Underlying profit before tax')]:
                    bind(key, label, segment[label][column], year, f'Note 4 Segmental analysis · {year} · {perimeter} · {label}',
                         perimeter=perimeter, basis='Underlying segment reporting')
                if perimeter == 'Consolidated Group':
                    for key, label in [('lease', 'Underlying operating lease depreciation1'), ('remediation', 'Remediation')]:
                        bind(key, label.rstrip('1'), segment[label][column], year, f'Note 4 Segmental analysis · {year} · Total · {label}',
                             basis='Underlying segment reporting')
                if year == 2026 and perimeter in perimeters[:3]:
                    name = 'Underlying impairment charge'
                    bind('segment_impairment', name, segment[name][column], year,
                         f'Note 4 Segmental analysis · {year} · {perimeter} · {name}',
                         perimeter=perimeter, basis='Underlying segment reporting')
                if year == 2026 and perimeter in {'Retail', 'Commercial Banking', 'Other'}:
                    bind('segment_deposits', 'Customer deposits', segment['Customer deposits'][column], year,
                         f'Note 4 Segmental analysis · 30 June 2026 · {perimeter} · Customer deposits',
                         perimeter=perimeter, basis='Reported segment balances', stock=True)
            bridge = [row for row in cells(original[126]) if row and row[0] == 'Profit before tax'][index]
            for key, label, raw_value in zip(('remove_restructuring', 'remove_volatility'),
                                            ('Removal of restructuring', 'Removal of volatility and other items'), bridge[2:4]):
                bind(key, label, raw_value, year, f'Note 4 · reconciliation · {year} · Profit before tax · {label}',
                     basis='Statutory-to-underlying adjustment')
    assert len(bindings) <= 48
    payload = dict(document_identity=identity, fact_bindings=bindings)
    canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
    record_id = f'LBG-EDGAR-2026-{code}'
    record = dict(id=record_id, authority='analytical_working_research', canonical_mutation=False,
                  title=title, publisher=SUBJECT[1], url=url, retrieval_url=url, publication_date=publication,
                  publication_date_evidence=f'Official SEC submissions index · accession {accession}',
                  retrieved_at=inspected, retrieval_method='approved_web_research_tool',
                  retrieval_reference=f'Original public SEC Form {form}; CIK 1160106; accession {accession}',
                  verification='primary_retrieved', content_kind='minimal_verified_numerical_facts',
                  primary_content_sha256=None, reporting_period=f'To {end_dates[code]} 2026 and disclosed comparatives',
                  reviewed_by='CIOS financial sprint repository verification',
                  review_notes='Filing tables checked in original EDGAR HTML. Retain numerical facts and locators only.',
                  source_category='issuer_results', third_party_material=False,
                  retained_form='minimal_facts_and_provenance', purpose='attributed_analytical_working_views',
                  audience='flora_research_views', retention='minimal_facts_and_provenance',
                  rights=dict(basis='ordinary_public_factual_analysis',
                              policy_reference='https://github.com/rdidale-jpg/CIOS/pull/698/commits/9a7181fbcc43c23188c3f4ce7b7b1dea9d41977e',
                              expression_reuse=False, contract_restriction_found=False,
                              method_review='Independently retrieved regulator-filed EDGAR record. Existing EDGAR access practice and ordinary independent factual analysis; no investor-host material or copied tables.',
                              operations=['read_public', 'independent_facts', 'minimal_numerical_retention', 'public_read_only'],
                              material_exceptions=[], attribution_url=ORIGIN+'/', homepage_conditions_met=True),
                  facts_sha256=hashlib.sha256(canonical).hexdigest(), **payload)
    entry = dict(id=record_id, file=record_id+'.json', publisher=SUBJECT[1], url=url, version=version,
                 subject=SUBJECT, accession=accession, presentation='banking:lloyds',
                 origin=dict(origin=ORIGIN, document_prefix=PREFIX, cik='1160106',
                             identity_evidence='https://data.sec.gov/submissions/CIK0001160106.json'))
    return entry, record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('originals', type=Path)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--inspected', default=datetime.now(timezone.utc).isoformat(timespec='seconds'))
    args = parser.parse_args()
    catalogue = args.destination/'catalogue.json'
    records = json.loads(catalogue.read_text())
    records['reports'] = [row for row in records['reports'] if not row['id'].startswith('LBG-EDGAR-')]
    for code, (_, filename, _) in FILES.items():
        entry, record = retain(code, (args.originals/filename).read_bytes(), args.inspected)
        dump(args.destination/entry['file'], record)
        records['reports'].append(entry)
    dump(catalogue, records)


if __name__ == '__main__':
    main()
