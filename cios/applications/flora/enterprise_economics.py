"""A1 Landscape composition, not an Economics model or financial owner.

Only existing public, currently eligible projections enter this renderer. No
Financial-run discovery, persistence, source admission or qualification occurs.
The unweighted diagrams explain mechanisms; they allocate no company money.
"""
from dataclasses import replace
from html import escape
from pathlib import Path

from . import intelligence_presentation as p
from . import visual_streams as v

STYLE = '<style>' + Path(__file__).with_name('visual_stream_assets').joinpath('economics.css').read_text() + '</style>'
AIRLINE_STAGES = frozenset({'airline-revenue', 'airline-delivery', 'airline-return'})

BANK = (
    ('funding', 'Funding', 'Customer deposits', 'A foundation for lending',
     'Deposits help fund lending and other earning assets. Some accounts earn interest for customers.',
     'The balance alone does not show funding cost. Customer mix and the rates paid determine how much deposits cost the bank.'),
    ('lending-income', 'Lending & income', 'Interest + fees', 'Turning funding into income',
     'Loans and other earning assets generate interest. Fees and services contribute other income.',
     'Lending and deposits reprice at different times. That timing can widen or narrow the difference between interest earned and paid.'),
    ('profit-costs', 'Profit & costs', 'Earnings after costs', 'What remains after costs',
     'Funding costs, operating costs and credit losses reduce earnings. Capital absorbs risk; it is not an expense in this flow.',
     'More income need not mean more profit. Higher costs or credit losses can absorb the gain; additional lending can also require capital.'),
)
AIRLINE = (
    ('airline-revenue', 'Revenue', 'Seats + services', 'Turning a network into sales',
     'Passengers buy seats and related services. A route network connects origin and destination markets.',
     'A broad network creates reach, not guaranteed earnings. Fare mix, frequency and how many seats sell determine the revenue from scheduled capacity.'),
    ('airline-delivery', 'Delivery & costs', 'Aircraft + operations', 'Delivering the flying programme',
     'Aircraft, crew, fuel, maintenance and airports enable flying. Aircraft availability bounds the schedule that can be delivered.',
     'Using aircraft more intensively can spread fixed costs over more flying. Reserve capacity can improve recovery while reducing utilisation.'),
    ('airline-return', 'Profit & reinvestment', 'Earnings after costs', 'Capturing value from flying',
     'Revenue must cover operating and financing costs. Profit, cash generation and aircraft investment describe different parts of the economics.',
     'Higher passenger revenue need not produce higher profit or cash. Pricing, delivery costs and investment timing can move in different directions.'),
)


def _basis(facts):
    """Optional inspection of the same eligible public facts; no raw records.

    Lloyds PDF locators stay with the existing internal Source owner (§5).
    Replacing a presentation URL neither edits that owner nor grants rights.
    """
    facts = tuple(dict.fromkeys(f for f in facts if f is not None and p.eligible(f)))
    if not facts:
        return ''
    items = []
    for fact in facts:
        p.note_editorial_sources(fact.sources)
        sources = tuple(replace(s, url='https://www.lloydsbankinggroup.com/', locator='', quote='')
                        if 'lloydsbankinggroup.com' in s.url else replace(s, quote='') for s in fact.sources)
        with p.editorial_view(False):
            # Retain the owning semantic formatter and every caveat, but use
            # one inspection action rather than a disclosure for each fact.
            rendered = p.render(replace(fact, sources=sources), compact=True)
            rendered = rendered.replace('<details class="intelligence-source"><summary>Sources &amp; reasoning</summary>',
                                        '<div class="econ-source">').replace('</details>', '</div>')
            items.append(rendered)
    return ('<details class="econ-basis"><summary>Source &amp; basis</summary>'
            + ''.join(items) + '</details>')


def _icon(index, airline):
    # Original small line drawings, not replacement enterprise artwork.
    paths = (
        ('M8 22h48M12 22v30m11-30v30m18-30v30m11-30v30M8 54h48M9 17L32 5l23 12Z',
         'M7 32h48M41 18l14 14-14 14M7 19h15M7 45h15',
         'M9 53h46M16 47V34h9v13m6 0V24h9v23m6 0V11h9v36'),
        ('M6 35l50-8-18-8-8-12h-6l7 17-16 4-7-7H3l8 13-4 13h6l8-11',
         'M10 48h44M15 45V28h34v17M21 28V17h22v11M23 36h4m10 0h4',
         'M7 49h48M13 42l12-13 12 6 15-22M42 13h10v10'),
    )
    return '<svg viewBox="0 0 64 64" aria-hidden="true" focusable="false"><path d="' + paths[airline][index] + '"/></svg>'


def _composition(ctx, stages, selected, figures, facts, extra='', related=''):
    airline = ctx.scope == 'easyjet'
    title = 'From seats to earnings' if airline else 'From funding to earnings'
    company = 'easyJet Group' if airline else 'Lloyds Banking Group plc · consolidated Group'
    links = []
    for i, (key, name, mechanism, *_rest) in enumerate(stages):
        figure = figures.get(key)
        amount = ('<span class="econ-number" data-semantic-type="reported"><span class="econ-type">Reported</span>'
                  + escape(figure[0]) + '<small>' + escape(figure[1]) + '</small></span>') if figure else (
                  '<span class="econ-mechanism">' + escape(mechanism) + '</span>')
        links.append('<li><a data-stage="' + key + '" href="' + escape(v.url(ctx, detail=key, reading=ctx.reading), quote=True)
                     + '#visual-content"' + (' aria-current="page"' if key == selected else '') + '>'
                     + _icon(i, airline) + '<span class="econ-stage-name">' + escape(name) + '</span>' + amount + '</a></li>')
    active = next(row for row in stages if row[0] == selected)
    analysis = ctx.reading == 'insight'
    heading_id = 'insight-title' if ctx.detail else 'economics-title'
    focus = ' id="insight" tabindex="-1"' if ctx.detail else ''
    close = ('<a class="close close-insight" aria-label="Close economic detail" href="'
             + escape(v.url(ctx, detail='', reading=ctx.reading), quote=True) + '#visual-content">×</a>') if ctx.detail else ''
    return (STYLE + '<section class="economics ' + ('econ-airline' if airline else 'econ-bank') + '"' + focus + ' aria-labelledby="' + heading_id + '">'
            + close + '<p class="eyebrow">' + company + '</p><h1 id="' + heading_id + '">' + title + '</h1>'
            '<figure class="econ-story"><figcaption>Illustrative ' + ('airline' if airline else 'banking') + ' model · not to scale</figcaption>'
            '<nav aria-label="Economic stages"><ol class="econ-stages">' + ''.join(links) + '</ol></nav></figure>'
            '<section class="econ-focus" aria-labelledby="economic-detail"><h2 id="economic-detail">' + escape(active[3]) + '</h2>'
            '<p class="econ-explanation" data-semantic-type="' + ('insight' if analysis else 'assumed') + '">'
            + escape(active[5] if analysis else active[4]) + '</p>' + extra + '</section>'
            + related + _basis(facts) + '</section>')


def _qualified_pressure_link(headers, company):
    """Link only to an explicitly bound, accessible, currently qualified model.

    No role/email inference; no stored QUALIFIED label alone is sufficient.
    No public probe of canonical models, private Financial runs or workspaces.
    """
    from .access import authenticated_flora_user
    if not authenticated_flora_user(headers):
        return ''
    try:
        from .live.source_registry import canonical_enterprise_id, configured_enterprise_aliases
        identity = canonical_enterprise_id(company)
        if identity not in set(configured_enterprise_aliases().values()):
            return ''  # A generated slug is not a canonical identity binding.
        from .enterprise_canvas.service import can_view_enterprise_canvas
        if not can_view_enterprise_canvas(headers, identity):
            return ''
        from .memory.repository import EnterpriseModelRepository
        from .blueprint_import.material_pressure import model_pressure_assessments
        owned = EnterpriseModelRepository().get(identity)
        if not any(row['qualification'] == 'QUALIFIED' for row in model_pressure_assessments(owned)):
            return ''
        return '<a href="/digital-twins/' + escape(identity, quote=True) + '/canvas#material-pressures">Material pressures</a>'
    except (PermissionError, OSError, ValueError, KeyError, TypeError):
        return ''


def banking(ctx, data, issues, *, headers=None):
    from . import lloyds_recovery as lloyds
    from . import leadership_agenda
    from .research_intelligence import model

    # Reuse the existing public projection, exact entity/period/unit checks and
    # stock-date comparison. Never reuse caller-cached derived results.
    verified = []
    for claim in data.get('claims', ()):
        if claim.get('id') not in lloyds.MEASURES:
            continue
        try:
            if model.primary_claim_supported(data, claim):
                verified.append(claim['id'])
        except (ValueError, OSError, KeyError, TypeError):
            continue
    claims = lloyds._claims(data, verified)
    stock, opening, profit = (lloyds._measure(claims.get(key), *basis)
                              for key, basis in lloyds.MEASURES.items())
    change = (leadership_agenda._deposit_change((opening, stock)) if opening and stock
              and any(issue.key == 'funding-base' for issue in issues) else None)
    selected = ctx.detail if ctx.detail in lloyds.LANDSCAPE_COMPONENTS else 'funding'
    figures = {}
    if stock:
        figures['funding'] = ('£' + str(stock.value) + 'bn', 'Customer deposits · 30 Sep 2026')
    if profit:
        figures['profit-costs'] = ('£' + str(profit.value) + 'bn', 'Statutory pretax profit · 9m to 30 Sep 2026')
    facts = [stock, profit]
    extra = ''
    if selected == 'funding' and change and p.eligible(change):
        facts += [opening, change]
        extra = ('<p class="econ-change" data-intelligence="funding-base" data-semantic-type="calculated">Calculated · <strong>£'
                 + escape(str(change.value)) + 'bn</strong> difference in deposits'
                 '<span>31 December 2025 → 30 September 2026 · two balance-sheet dates</span></p>'
                 '<p class="econ-caveat">A difference between reported balances, not an organic inflow or an income measure.</p>')
    elif selected == 'profit-costs' and profit:
        extra = '<p class="econ-caveat">Group statutory profit is a period flow. It does not allocate earnings or costs to individual capabilities.</p>'
    elif selected == 'lending-income':
        # Preserve the existing Source-owned finite projection and its hold.
        # Shipping §2 is unresolved, so this returns nothing. No permission,
        # identity, legal exception or persistence is changed here.
        from .financial_intelligence.candidate_analytics import public_factual_html
        extra = public_factual_html(insight=ctx.reading == 'insight')
    related = '<nav class="econ-related" aria-label="Related enterprise views">'
    related += '<a href="' + escape(v.url(ctx, stream='inside', detail='economics', reading=ctx.reading), quote=True) + '#visual-content">Financial analysis</a>'
    if change and any(issue.key == 'funding-base' for issue in issues):
        related += '<a href="' + escape(v.url(ctx, detail='', agenda='funding-base', reading=ctx.reading), quote=True) + '#agenda-insight">Funding perspective</a>'
    if any(issue.key == 'service-recovery' for issue in issues):
        related += '<a href="' + escape(v.url(ctx, detail='', agenda='service-recovery', reading=ctx.reading), quote=True) + '#agenda-insight">Customer outcomes · Lloyds Bank plc</a>'
    related += _qualified_pressure_link(headers, 'Lloyds Banking Group plc') + '</nav>'
    return _composition(ctx, BANK, selected, figures, facts, extra, related)


def aviation(ctx, data):
    from . import easyjet_capabilities as easyjet
    fleet = easyjet.fact(data, 'AV-FLEET')
    network = easyjet.fact(data, 'AV-NETWORK')
    selected = ctx.detail if ctx.detail in AIRLINE_STAGES else 'airline-revenue'
    figures = {}
    if network:
        figures['airline-revenue'] = (network.text, 'Winter / summer 2025 · network')
    if fleet:
        figures['airline-delivery'] = (fleet.text, 'At 30 September 2025 · Group fleet')
    caveat = ('<p class="econ-caveat">Historical operating scale. Routes are an annual network measure, not daily flights; '
              'fleet size is not utilisation or profitability.</p>') if fleet or network else ''
    related = '<nav class="econ-related" aria-label="Related enterprise views">'
    for detail, label in (('network-planning', 'Network Planning'), ('fleet-operations', 'Fleet Operations')):
        related += '<a href="' + escape(v.url(ctx, stream='inside', detail=detail, reading=ctx.reading), quote=True) + '#visual-content">' + label + '</a>'
    related += '<a href="/enterprises/easyjet/understanding">Research and evidence</a></nav>'
    return _composition(ctx, AIRLINE, selected, figures, (fleet, network), caveat, related)


def statement_summary(lines, *, insight=False, fixture=False, inspection=True):
    """One editorial composition for eligible statement lines from any issuer."""
    from .financial_intelligence.public_statements import statements

    eligible = tuple(statements(lines))
    if not eligible:
        return ''
    disclaimer = '<p><strong>Synthetic review fixture</strong></p>' if fixture else ''
    body = '<section class="reading-capability" aria-labelledby="eei-summary"><h2 id="eei-summary">Financial statements</h2>' + disclaimer
    for kind, label, context in (
        ('income', 'Income statement', 'Income and costs explain earnings during the reporting period.'),
        ('balance', 'Balance sheet', 'Assets and obligations describe the position on the reported date.'),
        ('cash_flow', 'Cash flow statement', 'Cash movements show how operations, investment and funding changed cash during the period.'),
    ):
        body += '<h3>' + label + '</h3>'
        rows = tuple((line, fact) for line, fact in eligible if line.statement == kind)
        if not rows:
            body += '<p>No eligible figures in this view.</p>'
        elif insight:
            body += '<p>' + context + ' Use matching scope and basis when comparing figures.</p>'
        else:
            for line, fact in rows:
                details = f'{fact.scope} · FY{line.fiscal_year} · {fact.period} · {fact.unit}'
                restated = ' · Restated' if line.revision_state == 'restated' else ''
                body += ('<p><strong>' + escape(line.reported_label) + ' · ' + escape(line.original_display)
                         + '</strong><br><small>' + escape(details + restated) + '</small></p>')
    if inspection:
        body += _basis(fact for _, fact in eligible)
    return body + '</section>'


def source_statement_summary(record, *, subject, insight=False, fixture=False):
    """Resolve fresh trusted Source input before rendering; no cached view payload."""
    from .financial_intelligence.public_statements import project

    return statement_summary(project(record, subject=subject), insight=insight, fixture=fixture)


def annual_statement_view(lines, *, insight=False, comparison_keys=(), context=''):
    """Shared Economics composition for paired reported years and stock movements."""
    from decimal import Decimal
    from .financial_intelligence.public_statements import balance_changes, statements

    rows = tuple(statements(lines))
    if not rows:
        return ''
    years = sorted({line.fiscal_year for line, _ in rows}, reverse=True)
    for kind in ('income', 'balance', 'cash_flow'):
        for year in years:
            periods = {line.period.label for line, _ in rows if line.statement == kind and line.fiscal_year == year}
            if len(periods) > 1:
                return ''
    columns = {year: f'FY{year}' for year in years}
    units = ' · '.join(sorted({fact.unit for _, fact in rows if fact.unit != '%'}))
    if any(fact.unit == '%' for _, fact in rows):
        units = (units + ' · ' if units else '') + 'Ratios shown as %'
    title = ('<style>.eei-annual table{width:min(100%,46rem);margin:8px 0 24px;border-collapse:collapse}'
             '.eei-annual td,.eei-annual thead th:not(:first-child){padding-inline-start:clamp(5px,2vw,24px);'
             'text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}'
             '.eei-annual th[scope=row]{text-align:left;padding-inline-end:8px}'
             '</style><section class="reading-capability eei-annual" aria-labelledby="eei-summary">'
             '<h2 id="eei-summary">Financial statements</h2>')
    source = rows[0][1].sources[0]
    body = (title + '<p class="reading-context">' + escape(rows[0][0].subject_name)
            + ' · annual report · ' + escape(units) + '</p>')
    if context:
        body += '<p>' + escape(context) + '</p>'
    if insight:
        body += '<h3>Changes in the year-end balance sheet</h3><ul>'
        for label, result in balance_changes(lines, comparison_keys):
            change = Decimal(result['value'])
            body += ('<li data-semantic-type="calculated"><strong>' + escape(label)
                     + ':</strong> ' + f'{change:+,f}' + ' ' + escape(result['unit'])
                     + ' · closing minus opening</li>')
        body += '</ul>'
        context_insight = _cash_flow_insight(rows)
        body += ''.join(p.render(fact, compact=True) for fact in context_insight)
        if context_insight:
            body += '<p>Which cash movements recur, and how much depends on changes in assets or funding?</p>'
    else:
        for kind, label in (('income', 'Income statement'), ('balance', 'Balance sheet'), ('cash_flow', 'Cash flow statement')):
            selected = [line for line, _ in rows if line.statement == kind]
            if not selected:
                continue
            groups = {}
            for line in selected:
                key = (line.metric, line.reported_label, line.accounting_basis, line.perimeter if kind == 'balance' else '')
                groups.setdefault(key, {})[line.fiscal_year] = line
            body += ('<h3>' + label + '</h3><table><caption class="sr-only">' + label
                     + ' · reported values</caption><thead><tr><th scope="col">Measure</th>'
                     + ''.join('<th scope="col">' + columns[year] + '</th>' for year in years)
                     + '</tr></thead><tbody>')
            for (_, label, basis, _), periods in groups.items():
                spans = []
                for year in years:
                    line = periods.get(year)
                    if line:
                        tag = ' · Restated' if line.revision_state == 'restated' else ''
                        spans.append('<td><span title="' + escape(line.period.label + ' · ' + line.perimeter + ' · ' + basis + ' · ' + line.source.locator, quote=True)
                                     + '">' + escape(line.original_display + tag) + '</span></td>')
                    else:
                        spans.append('<td>—</td>')
                body += '<tr><th scope="row">' + escape(label) + '</th>' + ''.join(spans) + '</tr>'
            body += '</tbody></table>'
    return body + '<p class="reading-context">Source: ' + escape(source.title) + '.</p></section>'


def _cash_flow_insight(rows):
    """One sign-based reading of current reported cash categories."""
    cash = [(line, fact) for line, fact in rows if line.statement == 'cash_flow']
    if not cash:
        return ()
    current_year = max(line.fiscal_year for line, _ in cash)
    metrics = ('operating_cash', 'investing_cash', 'financing_cash')
    chosen = [(line, fact) for line, fact in cash if line.fiscal_year == current_year and line.metric in metrics]
    if {line.metric for line, _ in chosen} != set(metrics) or len(chosen) != 3:
        return ()
    first = chosen[0][1]
    if any((fact.scope, fact.period, fact.unit, fact.basis, fact.sources[0].url) !=
           (first.scope, first.period, first.unit, first.basis, first.sources[0].url)
           or fact.value <= 0 for _, fact in chosen):
        return ()
    return (p.Statement(
        'Operating, investing and financing activities each contributed cash in the latest annual period shown.',
        'insight', first.scope, first.period, tuple(fact.sources[0] for _, fact in chosen),
        'repository_interpretation', 'analytical_working_research',
        reasoning='The three signed cash-flow subtotals are positive for the same reporting period and scope.',
        dependencies=tuple(fact.text for _, fact in chosen), dependency_types=('reported',) * 3,
        counter_evidence=('Timing, investment maturities and funding activity can change year-to-year cash movement.',),
    ),)
