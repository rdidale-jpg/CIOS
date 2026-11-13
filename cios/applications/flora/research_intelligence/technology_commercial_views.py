"""Commercial presentation for Issue #573; diagnostics remain secondary."""
from html import escape as e
from . import technology as research
from . import technology_commercial as c
from . import technology_experience as x


def source_details(ids, data, boundary='', label='Sources & context'):
    sources = [data['sources'][key] for key in dict.fromkeys(ids)]
    body = ''.join('<p>' + x.link(s['url'], s['title'] + ' ↗') + '<br><small>'
                   + e(s['reporting_period']) + ' · reviewed ' + e(s['reviewed_at']) + '<br>'
                   + e(s['locator']) + '</small></p>' for s in sources)
    if boundary:
        body += '<p>' + e(boundary) + '</p>'
    return '<details class="commercial-source"><summary>' + e(label) + '</summary>' + body + '</details>'


def format_metric(metric):
    if metric is None:
        return ''
    value, unit = metric['value'], metric['unit']
    if unit in ('GBP', 'USD'):
        prefix = '£' if unit == 'GBP' else '$'
        if value >= 1e9:
            # Preserve meaningful source precision, without implying extra accuracy.
            return prefix + f'{value / 1e9:,.3f}'.rstrip('0').rstrip('.') + 'bn'
        if value >= 1e6:
            return prefix + f'{value / 1e6:,.1f}'.rstrip('0').rstrip('.') + 'm'
        return prefix + f'{value:,.0f}'
    if unit == 'percent':
        return f'{value:g}%'
    return ('c. ' if metric.get('approximate') else '') + f'{value:,.0f}'


def metric_cell(metric, data):
    if metric is None:
        return ''
    c.validate_metric(metric, data['sources'], uk=True)
    estimate = '<span class="commercial-est">EST</span>' if metric['kind'] == 'estimate' else ''
    detail = '<p>' + e(f'{metric["value"]:,}') + ' ' + e(metric['unit']) + '</p><p>' + e(metric['scope']) + ' · ' + e(metric['period']) + '</p>'
    if metric.get('basis'):
        detail += '<p>' + e(metric['basis']) + '</p>'
    if metric['kind'] == 'estimate':
        detail += '<p>Range: ' + e(str(metric['range'][0])) + '–' + e(str(metric['range'][1])) + ' ' + e(metric['unit']) + '</p>'
    detail += ''.join('<p>' + x.link(data['sources'][key]['url'], data['sources'][key]['title'] + ' ↗') + '</p>' for key in metric['source_ids'])
    return ('<details class="commercial-metric"><summary>' + e(format_metric(metric)) + estimate
            + '<small>' + e(metric['period']) + '</small></summary><div>' + detail + '</div></details>')


def comparison(district='', sort='name', direction='asc', search='', macro=''):
    data = c.load()
    rows = c.participants(district, sort, direction)
    if search:
        term = search.casefold()
        rows = [r for r in rows if term in ' '.join(str(r[k] or '') for k in ('name', 'role', 'specialty')).casefold()]
    title = x.DISTRICTS[district][0] if district else 'Technology participants'
    intro = x.crumbs([(title, '')]) + '<div class="exp-heading"><div><h1>' + e(title) + '</h1>'
    intro += '<p class="commercial-deck">Compare the enterprises, their roles and commercial signals.</p></div>' + x.pipeline_link(district or 'industry') + '</div>'
    if district == 'cloud':
        intro += '<p class="commercial-market"><strong>£10.5bn</strong> UK public cloud spend · 2024 · IaaS & PaaS</p>'
        intro += '<details class="commercial-source"><summary>Market context</summary><p>Cloud benchmark, not total district value. '
        intro += 'AI and cloud demand face power, grid and planning constraints.</p>' + x.link(x.CMA_URL, 'CMA definition & spending') + ' · ' + x.link(x.GRID_URL, 'UK infrastructure context') + '</details>'
    endpoint = '/district' if district else '/participants'
    hidden = ''.join(f'<input type="hidden" name="{key}" value="{e(value,quote=True)}">' for key, value in
                     [('district', district), ('sort', sort), ('direction', direction)] if value)
    body = (intro + '<form class="commercial-search" method="get"><label for="participant-search">Find a participant</label>'
            f'<div><input id="participant-search" name="search" type="search" maxlength="80" value="{e(search,quote=True)}" placeholder="Name, role or specialty">'
            + hidden + '<button>Search</button></div></form>'
            '<div class="commercial-table-wrap" role="region" tabindex="0" aria-label="Participant comparison, scroll for all columns">'
            '<table class="commercial-table"><caption class="visually-hidden">UK Technology participant comparison. Empty cells carry no value; estimates are labelled EST.</caption><thead><tr>')
    for key, label in [('name', 'Participant'), ('uk_revenue', 'UK revenue'), ('uk_workforce', 'UK workforce'),
                       ('role', 'Role'), ('specialty', 'Specialty'), ('signal', 'Commercial signal')]:
        state = ('ascending' if direction == 'asc' else 'descending') if sort == key else 'none'
        target = x.url(endpoint, district=district, sort=key, direction='desc' if sort == key and direction == 'asc' else 'asc', search=search)
        body += '<th scope="col" aria-sort="' + state + '">' + x.link(target, label + ' ↕', data_comparison_sort=key) + '</th>'
    body += '<th scope="col"><span class="visually-hidden">Source context</span></th></tr></thead><tbody>'
    for row in rows:
        context = district or row['memberships'][0]
        sources = [s for key in ('uk_revenue', 'uk_workforce') if row[key] for s in row[key]['source_ids']]
        signal = row['signal']
        if signal:
            sources += signal['source_ids']
        source = source_details(sources, data, label='Details') if sources else ''
        if row['foundation_blocks']:
            source += '<details class="commercial-source"><summary>Research</summary>' + ''.join(
                '<p>' + x.link(research.BASE + '/evidence#block-' + key, 'Retained research passage') + '</p>' for key in row['foundation_blocks']) + '</details>'
        body += ('<tr data-participant="' + e(row['key']) + '"><th scope="row">'
                 + x.link(x.url('/enterprise', enterprise=row['key'], district=context), row['name'] + ' →') + '</th>'
                 '<td data-metric="uk_revenue">' + metric_cell(row['uk_revenue'], data) + '</td>'
                 '<td data-metric="uk_workforce">' + metric_cell(row['uk_workforce'], data) + '</td><td>' + e(row['role']) + '</td>'
                 '<td>' + e(row['specialty']) + '</td><td>' + (e(signal['title']) if signal else '')
                 + (' <span class="commercial-hypothesis">Hypothesis</span>' if signal and signal['kind'] == 'hypothesis' else '')
                 + '</td><td>' + source + '</td></tr>')
    body += '</tbody></table></div><p class="exp-subtle">' + str(len(rows)) + ' participant views</p>'
    if district:
        body += x.macro_links(selected=macro, district=district)
    return body


def financials(profile, data):
    metrics = profile['metrics']
    keys = [('revenue', 'Revenue'), ('net_income', 'Net income · GAAP'), ('gross_margin', 'Gross margin · GAAP')]
    html = '<section id="financials" class="commercial-section"><h2>Financial context</h2><p class="exp-subtle">Global group · FY2026 ended 25 January 2026 · USD</p><div class="commercial-financials">'
    for key, label in keys:
        html += '<a href="#financial-detail-' + key + '"><strong>' + e(format_metric(metrics[key])) + '</strong><span>' + label + '</span></a>'
    html += '</div><p>Data Center revenue <strong>' + e(format_metric(metrics['data_center'])) + '</strong> · Global workforce <strong>' + e(format_metric(metrics['workforce'])) + '</strong> at FY2026 year-end.</p>'
    html += '<p class="commercial-update">Reviewed trading update: <strong>' + e(format_metric(metrics['latest_quarter'])) + '</strong> revenue · Q2 FY2027 ended 26 July 2026 · Global group, USD.</p>'
    html += source_details(['NV-FY26', 'NV-10K', 'NV-Q227'], data, 'Annual and quarterly periods remain separate. UK-specific revenue and workforce are not inferred from group figures.')
    for key, label in keys:
        html += ('<details class="commercial-financial-detail" id="financial-detail-' + key + '"><summary>' + label + ' detail</summary><p>'
                 + e(format_metric(metrics[key])) + ' · ' + e(metrics[key]['scope']) + ' · ' + e(metrics[key]['period']) + '</p>'
                 + x.link(data['sources'][metrics[key]['source_ids'][0]]['url'], 'Issuer financial report ↗') + '</details>')
    return html + '</section>'


def observations(title, rows, data, ident):
    return '<section class="commercial-section" id="' + ident + '"><h2>' + title + '</h2>' + ''.join(
        '<article class="commercial-insight"><h3>' + e(r['title']) + '</h3><p>' + e(r['text']) + '</p>'
        + source_details(r['source_ids'], data, r.get('boundary', '')) + '</article>' for r in rows) + '</section>'


def nvidia(district='ai'):
    data = c.load(); p = data['profiles']['nvidia']
    body = (x.crumbs([(x.DISTRICTS[district][0], x.url('/district', district=district)), ('NVIDIA', '')])
            + '<div class="exp-heading"><div><h1>NVIDIA</h1><p class="commercial-deck">' + e(p['subtitle']) + '</p></div>'
            + x.pipeline_link('nvidia') + '</div><p class="commercial-perspective">' + e(p['summary']['text']) + '</p>'
            '<nav class="commercial-jumps" aria-label="Enterprise sections">'
            + ''.join(x.link('#' + key, label) for key, label in [('financials', 'Financials'), ('strategy', 'Strategy'),
                ('pressures', 'Pressures'), ('ecosystem', 'Ecosystem'), ('programmes', 'Programmes'), ('opportunities', 'Opportunities')]) + '</nav>')
    body += financials(p, data)
    body += '<div class="commercial-two-column">' + observations('Strategic priorities', p['strategy'], data, 'strategy') + observations('Commercial pressures', p['pressures'], data, 'pressures') + '</div>'
    body += '<section class="commercial-section" id="ecosystem"><h2>Customers, partners & suppliers</h2>'
    body += '<div class="commercial-ecosystem">'
    for category in ('Customers & deployed use', 'Partners', 'Suppliers'):
        body += '<section><h3>' + e(category) + '</h3><ul class="commercial-relationships">'
        for r in p['relationships']:
            if r['category'] != category:
                continue
            body += '<li><strong>' + e(r['name']) + '</strong><span>' + e(r['role']) + '</span><small>' + e(r['scope']) + '</small><p>' + e(r['text']) + '</p>' + source_details(r['source_ids'], data, r['boundary']) + '</li>'
        body += '</ul></section>'
    body += '</div></section><section class="commercial-section" id="programmes"><h2>UK programmes & activity</h2>'
    for r in p['programmes']:
        body += ('<article class="commercial-programme"><div><h3>' + e(r['title']) + '</h3><p>' + e(r['text']) + '</p>'
                 '<small>' + e(r['period']) + '</small></div><strong>' + e(r['value']) + '</strong>'
                 + source_details(r['source_ids'], data, r['boundary']) + '</article>')
    body += '</section><section class="commercial-section" id="opportunities"><h2>Where sales work may emerge</h2>'
    for r in p['opportunities']:
        body += ('<article class="commercial-opportunity" id="hypothesis-' + r['id'] + '"><span class="commercial-hypothesis">Hypothesis</span><h3>'
                 + e(r['title']) + '</h3><p>' + e(r['text']) + '</p><p><strong>Potential buyer:</strong> ' + e(r['buyer']) + '</p>'
                 '<details><summary>Develop this opportunity</summary><dl class="exp-facts"><div><dt>Observed basis</dt><dd>' + e(r['basis'])
                 + '</dd></div><div><dt>Next conversation</dt><dd>' + e(r['qualification']) + '</dd></div><div><dt>Alternative</dt><dd>'
                 + e(r['countercase']) + '</dd></div></dl>' + source_details(r['source_ids'], data)
                 + '<p>Macro themes: ' + ', '.join(x.link(x.url('/district', district=district, macro=k) + '#macro-context', x.MACRO_CONTEXT[k][0]) for k in r['macro'])
                 + '</p></details></article>')
    body += '</section>'
    return body


def profile(key, district=''):
    foundation, _ = research.load()
    provider = next(r for r in foundation['providers'] if r['key'] == key)
    district = district or provider['memberships'][0]
    if key == 'nvidia':
        return nvidia(district)
    if key == 'equinix':
        # Existing financial drill remains addressable; presentation is refined in x.
        return x.enterprise()
    data = c.load(); row = next(r for r in c.participants() if r['key'] == key)
    body = (x.crumbs([(x.DISTRICTS[district][0], x.url('/district', district=district)), (provider['label'], '')])
            + '<div class="exp-heading"><div><h1>' + e(provider['label']) + '</h1><p class="commercial-deck">'
            + e(row['role']) + '</p></div>' + x.pipeline_link(key) + '</div>')
    if row['specialty']:
        body += '<p class="commercial-perspective">' + e(row['specialty']) + '</p>'
    values = [(label, row[field]) for label, field in [('UK revenue', 'uk_revenue'), ('UK workforce', 'uk_workforce')] if row[field]]
    if values:
        body += '<section class="commercial-section"><h2>UK operating context</h2><div class="commercial-financials">'
        body += ''.join('<div><span>' + label + '</span>' + metric_cell(value, data) + '</div>' for label, value in values) + '</div></section>'
    if row['signal']:
        body += observations('Commercial context', [row['signal']], data, 'commercial-context')
    if row['foundation_blocks']:
        body += '<details class="commercial-source"><summary>Company research</summary>' + ''.join('<p>' + x.link(research.BASE + '/evidence#block-' + key, 'Retained company passage') + '</p>' for key in row['foundation_blocks']) + '</details>'
    return body + '<p>' + x.link(x.url('/district', district=district), 'Compare participants →') + '</p>'
