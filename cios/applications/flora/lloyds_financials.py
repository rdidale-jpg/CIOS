"""Lloyds chart selection over the existing public Financial statement owner."""
from collections import defaultdict
from html import escape

from . import intelligence_presentation as presentation
from .financial_intelligence import chart, public_statements
from .research_intelligence import source_import

SUBJECT = ('research-subject:lloyds-banking-group-plc', 'Lloyds Banking Group plc')
GROUP = 'Consolidated Group'
DIVISIONS = {'retail': 'Retail', 'commercial': 'Commercial Banking',
             'retirement': 'Insurance Pensions and Investments', 'central': 'Other'}
FINANCIAL_SUBJECTS = tuple(DIVISIONS.values()) + (GROUP,)
COMPONENTS = (
    ('u_nii', 'Net interest'), ('u_other', 'Other income'), ('u_lease', 'Lease depreciation'),
    ('u_cost', 'Operating costs'), ('u_remediation', 'Remediation'), ('u_impairment', 'Credit impairment'),
    ('restructuring', 'Restructuring'), ('volatility', 'Volatility & other'),
)
# FY guidance is independently phrased from the exact EDGAR revision; source changes suppress it.
OBJECTIVES = '73e6c418e0edc12a265beacfb5c0b49387925c83025d15ed1f415081c6090e0f'


def current():
    active = defaultdict(list)
    # Retain the existing document-wide withdrawal boundary for the matching
    # issuer reporting packs, even when numbers also exist in an EDGAR filing.
    available = {
        'LBG-EDGAR-2026-Q3': 'lloyds-q3',
        'LBG-EDGAR-2026-Q3-RESULTS': 'lloyds-q3',
        'LBG-EDGAR-2026-H1': 'lloyds-h1',
    }
    allowed = set()
    for selection in set(available.values()):
        try:
            source_import.public_statement_record(selection)
        except (OSError, ValueError, KeyError, TypeError, PermissionError):
            continue
        allowed.add(selection)
    for row, fact in public_statements.statements(public_statements.statement_series(SUBJECT)):
        selection = available.get(row.source.source_id)
        if row.perimeter in FINANCIAL_SUBJECTS and (selection is None or selection in allowed):
            period = row.period
            key = (row.perimeter, row.metric, str(period.as_at or period.end),
                   str(period.start) if period.start else None)
            active[key].append((row, fact))
    results = {key: rows[0] for key, rows in active.items() if len(rows) == 1}
    admitted = public_statements.economic_projection('lloyds-q3').get('lines', ())
    for line in admitted:
        if line.measurement_id not in {'profit_before_tax-2025', 'profit_before_tax-2026'}:
            continue
        key = (GROUP, 'pbt', str(line.period.end), str(line.period.start))
        reported = results.get(key)
        if reported and reported[0].value.amount != line.value.amount:
            # A revised admitted total may remain visible on its own. A different
            # filing revision cannot still support a bridge to the replaced total.
            del results[key]
    return results


def select(data, keys, end, *, scope=GROUP, start=None):
    if start is None and end.endswith(('-06-30', '-09-30', '-12-31')):
        start = end[:4] + '-01-01'
    return tuple(data.get((scope, key, end, start or None)) for key in keys)


def values(rows, *, monetary_bridge=False, basis=None):
    if not all(rows):
        return ()
    if basis is not None and tuple(row.accounting_basis for row, _ in rows) != basis:
        return ()
    if monetary_bridge and any(
        row.value.unit != 'currency' or row.value.currency != 'GBP' or row.value.scale != 'millions'
        for row, _ in rows
    ):
        return ()
    for _, fact in rows:
        presentation.note_editorial_sources(fact.sources)
    return tuple(row.value.amount for row, _ in rows)


BRIDGE_BASIS = ('Underlying performance',) * 6 + ('Underlying-to-statutory adjustment',) * 2 + (
    'Underlying performance', 'Underlying performance', 'Statutory',
)


def group_bridge(data, period):
    keys = tuple(key for key, _ in COMPONENTS) + ('u_net', 'u_profit', 'pbt')
    rows = select(data, keys, period)
    read = values(rows, monetary_bridge=True, basis=BRIDGE_BASIS)
    if read and sum(read[:3]) == read[8] and sum(read[:6]) == read[9] and sum(read[:8]) == read[10]:
        return rows, read
    return (), ()


def comparable_group_change(data):
    current, now = group_bridge(data, '2026-09-30')
    previous, prior = group_bridge(data, '2025-09-30')
    if not public_statements.comparable_durations(tuple(row for row, _ in current),
                                                  tuple(row for row, _ in previous)):
        return ()
    deltas = tuple(a - b for a, b in zip(now[:8], prior[:8]))
    return (now[10], now[10] - prior[10], deltas) if sum(deltas) == now[10] - prior[10] else ()


def half_year_bridge(data, period):
    rows = select(data, ('segment_pbt', 'remove_restructuring', 'remove_volatility', 'pbt'), period)
    group = values(rows, monetary_bridge=True,
                   basis=('Underlying segment reporting', 'Statutory-to-underlying adjustment',
                          'Statutory-to-underlying adjustment', 'Statutory'))
    divisions = [values(select(data, ('segment_pbt',), period, scope=division),
                        monetary_bridge=True, basis=('Underlying segment reporting',))
                 for division in DIVISIONS.values()]
    if (group and all(divisions) and sum(item[0] for item in divisions) == group[0]
            and group[0] - group[1] - group[2] == group[3]):
        return sum(item[0] for item in divisions[:-1]), divisions[-1][0], -group[1], -group[2], group[3]
    return ()


def year_to_date_bridge(data):
    half = half_year_bridge(data, '2026-06-30')
    rows = (*select(data, ('pbt',), '2026-06-30'),
            *select(data, ('pbt',), '2026-09-30', start='2026-07-01'),
            *select(data, ('pbt',), '2026-09-30'))
    amounts = values(rows, monetary_bridge=True, basis=('Statutory',) * 3)
    if half and amounts and public_statements.reconciled_subperiods(*(row for row, _ in rows)):
        return (*half, *amounts[1:])
    return ()


def earnings(data, target):
    title = 'Nine months ended 30 September · Group · GBP million'
    current_period = '2026-09-30'
    _, now = group_bridge(data, current_period)
    body = ''
    if now:
        body += chart.bars('Income to statutory profit', title + ' · 2026 · signed bridge',
                           [(name, value) for (_, name), value in zip(COMPONENTS, now)], target=target, waterfall=True)
        body += f'<p>Underlying net income £{now[8]:,}m · underlying profit £{now[9]:,}m · statutory pretax profit £{now[10]:,}m.</p>'
        change = comparable_group_change(data)
        if change:
            _, _, deltas = change
            body += chart.bars('What moved pretax profit?', title + ' · 2026 versus 2025 · signed changes',
                               [(name, value) for (_, name), value in zip(COMPONENTS, deltas)],
                               target=target, waterfall=True)
            body += (f'<p>Calculated change {sum(deltas):+,}m GBP. Remediation contribution {deltas[4]:+,}m '
                     f'and operating costs plus credit impairment {deltas[3]+deltas[5]:+,}m GBP.</p>'
                     '<p><strong>FLORA Insight.</strong> The remediation comparison is distinct from a recurring efficiency gain. '
                     'Test which costs fall after implementation and parallel running, while maintaining service and controls.</p>')
    basis_lines = values(select(data, ('nii', 'other', 'total', 'expenses', 'impairment', 'pbt'), current_period),
                         monetary_bridge=True, basis=('Statutory',)*6)
    if basis_lines and sum(basis_lines[:2]) == basis_lines[2] and sum(basis_lines[2:5]) == basis_lines[5]:
        body += chart.bars('Statutory income and expenses', title + ' · 2026 · IFRS',
                           list(zip(('Net interest', 'Other income', 'Total income', 'Operating expenses',
                                     'Impairment', 'Pretax profit'), basis_lines)), target=target)
    fees = [(year, found[0]) for year in ('2025', '2026')
            if (found := values(select(data, ('fees',), year+'-06-30')))]
    body += chart.bars('Net fee and commission income', 'Six months to 30 June · Group statutory · GBP million',
                       fees, target=target)
    for key, label in [('total', 'Total income'), ('pbt', 'Pretax profit')]:
        audited = [(year, found[0]) for year in ('2024', '2025')
                   if (found := values(select(data, (key,), year+'-12-31')))]
        body += chart.bars(label + ' · full year', 'Group audited statutory · GBP million',
                           audited, target=target)
    quarterly = []
    for year in (2025, 2026):
        for quarter, (first, end) in enumerate((('01-01', '03-31'), ('04-01', '06-30'), ('07-01', '09-30'), ('10-01', '12-31')), 1):
            found = values(select(data, ('pbt',), f'{year}-{end}', start=f'{year}-{first}'))
            if found:
                quarterly.append((f'{year} Q{quarter}', found[0]))
    body += chart.bars('Quarterly earnings', 'Group statutory pretax profit · GBP million · individual quarters',
                       quarterly, target=target)
    periods = dict(quarterly)
    if all(key in periods for key in ('2025 Q3', '2026 Q2', '2026 Q3')):
        recent = periods['2026 Q3']
        body += (
            f'<p>Q3 2026 profit of £{recent:,}m moved {recent - periods["2026 Q2"]:+,}m GBP from Q2 '
            f'and {recent - periods["2025 Q3"]:+,}m against Q3 2025. These are single-quarter comparisons. '
            'Use the separate nine-month bridge to test the remediation comparator and other drivers. '
            'The quarterly change alone does not establish a sustainable run rate.</p>'
        )
    return body


def segments(data, target, scope=None):
    end = '2026-06-30'
    columns = [('segment_pbt', 'Underlying pretax profit'), ('net', 'Income after lease depreciation'),
               ('cost', 'Operating costs')]
    body = ''
    if scope:
        for metric, label in columns + [('segment_impairment', 'Credit impairment')]:
            series = []
            for year in (2025, 2026):
                found = values(select(data, (metric,), f'{year}-06-30', scope=scope))
                if found:
                    series.append((f'H1 {year}', found[0]))
            body += chart.bars(label, scope + ' · six months to 30 June · underlying · GBP million',
                               series, target=target)
        return body
    for metric, label in columns:
        series = []
        for division in DIVISIONS.values():
            found = values(select(data, (metric,), end, scope=division))
            if found:
                series.append((division, found[0]))
        body += chart.bars(label + ' by business', 'H1 2026 · segment reporting · GBP million',
                           series, target=target)
    for year in (2026, 2025):
        period = f'{year}-06-30'
        bridge = half_year_bridge(data, period)
        if bridge:
            subtotal, other, restructuring, volatility, statutory = bridge
            body += (f'<p>H1 {year} · Group underlying segment sum £{subtotal + other:,}m '
                     f'{restructuring:+,}m restructuring {volatility:+,}m volatility and other '
                     f'= £{statutory:,}m statutory pretax profit.</p>')
    if body:
        body += '<p>Other is the filed segment caption. H1 values are six-month results and are not extrapolated to nine months.</p>'
    return body


def funding(data, target):
    date = '2026-09-30'
    keys = [('mortgages', 'UK mortgages'), ('cards', 'Credit cards'), ('unsecured', 'UK unsecured & overdrafts'),
            ('motor', 'UK Motor Finance'), ('bcb_gross', 'Business & Commercial'), ('cib_gross', 'Corporate & Institutional')]
    loans = [(label, found[0]) for key, label in keys
             if (found := values(select(data, (key,), date, start='')))]
    deposits = [(scope, found[0]) for scope in ('Retail', 'Commercial Banking', 'Other')
                if (found := values(select(data, ('segment_deposits',), '2026-06-30', scope=scope, start='')))]
    hedge = [(year, found[0]) for year in ('2025', '2026')
             if (found := values(select(data, ('hedge',), year+'-09-30')))]
    aggregate = [(label, found[0]) for key, label in (
        ('assets', 'Total assets'), ('deposits', 'Customer deposits'), ('debt', 'Debt securities'),
        ('equity', 'Total equity'),
    ) if (found := values(select(data, (key,), date, start='')))]
    return (chart.bars('Balance sheet at September 2026', 'Selected Group balances · statutory · GBP million',
                       aggregate, target=target)
            + chart.bars('Structural hedge income', 'Nine months to September · GBP billion · reported contribution',
                       hedge, target=target)
            + chart.bars('Major gross lending portfolios', 'Selected portfolios · September 2026 · Group · GBP million',
                       loans, target=target)
            + chart.bars('Funding by reporting business', 'June 2026 · customer deposits · GBP million', deposits, target=target))


def capital(data, target):
    stock = [('cet1', 'CET1', '%'), ('rwa', 'Risk-weighted assets', ' GBP bn'),
             ('wholesale', 'Wholesale funding', ' GBP bn'), ('lcr', 'Liquidity coverage ratio', '%'),
             ('nsfr', 'Net stable funding ratio', '%')]
    measures = [('cir', 'Cost / income'), ('rote', 'Return on tangible equity'), ('nim', 'Banking net interest margin')]
    body = ''
    for key, label, suffix in stock + [(k, label, '%') for k, label in measures]:
        is_stock = any(key == s[0] for s in stock)
        dates = ('2025-12-31', '2026-09-30') if is_stock else ('2025-09-30', '2026-09-30')
        rows = [(date, found[0]) for date in dates
                if (found := values(select(data, (key,), date, start='' if is_stock else None)))]
        basis = 'Group · dated reported values' if is_stock else 'Group reported · nine months to 30 September'
        body += chart.bars(label, basis, rows, target=target, suffix=suffix)
    return body + guidance(data, target)


def guidance(data, target):
    body = ''
    seen = select(data, ('cir', 'rote'), '2026-09-30')
    if all(seen) and all(item[0].source.source_revision == OBJECTIVES for item in seen):
        body += ('<section><h3>FY2026 guidance versus nine-month actuals</h3>'
                 '<p>Management guidance is full-year. The nine-month actuals are a checkpoint only.</p>'
                 + chart.bars('Cost / income', 'Group · % · lower than 50% is the FY threshold',
                              [('9M actual', seen[0][0].value.amount), ('FY threshold', 50)], target=target, suffix='%')
                 + chart.bars('Return on tangible equity', 'Group · % · above 16% is the FY threshold',
                              [('9M actual', seen[1][0].value.amount), ('FY threshold', 16)], target=target, suffix='%')
                 + '</section>')
    return body


def evidence(data):
    body = '<section id="financial-evidence"><h3>Regulatory filing evidence</h3>'
    if not data:
        return body + '<p>No eligible financial filings are available.</p></section>'
    grouped = {}
    for row, fact in data.values():
        grouped.setdefault(row.source.title, []).append((row, fact))
    for title, rows in grouped.items():
        body += '<h4>' + escape(title) + '</h4><ul>'
        for row, fact in rows:
            body += '<li>' + ' · '.join(escape(str(x)) for x in (
                row.perimeter, row.reported_label, row.period.label, row.accounting_basis,
                row.original_display, fact.unit, row.source.locator)) + '</li>'
        body += '</ul>'
    return body + '<p><a href="https://www.sec.gov/">SEC EDGAR</a> · Identifying accessions and original document digests are retained with the Source record.</p></section>'
