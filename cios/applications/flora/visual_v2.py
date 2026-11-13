"""Two read-only, image-native design studies; no canonical Home replacement.

The economy basis is a frozen public presentation extract, not canonical
intelligence. PESTLE adapts the existing validated macro owner. No private
commercial store, runtime network, matching engine or mutation is used.
"""
from html import escape as e
import json
from pathlib import Path
from urllib.parse import urlencode

from .security import verified_context
from .research_intelligence import macro_intelligence as macro

BASE = '/visual-v2'
ASSETS = Path(__file__).with_name('visual_v2_assets')
FILES = {'styles': ('visual.css', 'text/css; charset=utf-8'),
         'interactions': ('visual.js', 'text/javascript; charset=utf-8'),
         'uk-artwork': ('uk-economy.webp', 'image/webp'),
         'pestle-artwork': ('pestle.webp', 'image/webp'),
         'pestle-mobile-artwork': ('pestle-mobile.webp', 'image/webp')}

# IDs are independent of the artwork. The broader sections never inherit the
# coverage or numeric meaning of their researched sub-sector destinations.
RESEARCH = {
    'J': ('Technology', '/industries/technology/experience'),
    'K': ('Banking', '/industries/banking'),
    'H': ('Aviation', '/industries/aviation'),
}
# Three researched host sections and two large contextual benchmarks. The
# complete comparable series stays in the one optional methodology disclosure.
VISIBLE_SHARES = frozenset({'H', 'J', 'K', 'L', 'G'})
FACTORS = {
    'political': ('Political', 24, 18, 23, 15, 'social-value'),
    'economic': ('Economic', 76, 18, 77, 15, None),
    'social': ('Social', 22, 50, 23, 36, 'social-value'),
    'technological': ('Technological', 78, 50, 77, 36, 'cyber'),
    'legal': ('Legal', 24, 82, 23, 89, 'cyber-bill'),
    'environmental': ('Environmental', 76, 82, 77, 89, 'uk-srs'),
}
COPY = {
    'political': ('Public buying is changing.',
        'From January 2027, the reviewed social-value policy covers specified UK central-government tenders. Contract scope and transition rules matter.',
        'Aviation procurement · test the actual tender criteria before shaping a bid.'),
    'social': ('Social value needs delivery.',
        'Covered UK public tenders connect social-value promises to delivery commitments. Start with the outcomes the specific contract requests.',
        'Commercial question · how will the proposed outcomes be measured?'),
    'technological': ('Resilience follows connections.',
        'UK cyber evidence is aggregate. Trace critical services through technology and supplier dependencies before proposing change.',
        'Banking & Aviation · an exposure to test, not evidence of a company incident.'),
    'legal': ('A proposal is not a duty.',
        'UK cyber reform was still proposed legislation at the November review. Recheck parliamentary status and the final entity and activity scope.',
        'Banking & Aviation · monitor the proposal; do not infer non-compliance.'),
    'environmental': ('Reporting meets operations.',
        'Reviewed FCA rules cover specified listed issuers from accounting periods starting January 2027. First reporting is in 2028; reliefs matter.',
        'Banking & Aviation · test reporting-data and control needs with the exact issuer.'),
}


def basis():
    return json.loads((ASSETS / 'economy.json').read_text())


def asset(name):
    if name not in FILES:
        raise ValueError('Visual study asset unavailable')
    filename, mime = FILES[name]
    return (ASSETS / filename).read_bytes(), mime


def url(pestle=False, **query):
    return BASE + ('/pestle' if pestle else '') + '?' + urlencode({'market': 'GB', **query})


def selection(path, query):
    if path not in {BASE, BASE + '/pestle'}:
        raise ValueError('Visual study route unavailable')
    keys = {'market', 'factor'} if path.endswith('/pestle') else {'market'}
    if set(query) - keys or any(len(v) != 1 for v in query.values()):
        raise ValueError('Unsupported visual study selector')
    if query.get('market', ['GB'])[0] != 'GB':
        raise ValueError('This visual study covers the United Kingdom only')
    factor = query.get('factor', [''])[0]
    if factor and factor not in FACTORS:
        raise ValueError('PESTLE factor unavailable')
    if 'factor' in query and not factor:
        raise ValueError('PESTLE factor unavailable')
    return factor


def insight(factor):
    if factor == 'economic':
        data = basis()
        return {'title': 'Services lead the expansion.',
            'text': 'Services led UK real GDP growth of 0.7% in the three months to September 2026 versus the previous three months. Volume change, separate from 2024 current-price GVA.',
            'effect': 'Commercial question · which customers face a change in demand or capacity?',
            'lineage': {'source_ids': ['ONS-GDP-2026-09'], 'locator': data['growth']['locator'],
                        'authority': 'public presentation extract; not a canonical accepted observation'},
            'sources': [s for s in data['sources'] if s['id'] == 'ONS-GDP-2026-09'],
            'details': 'UK aggregate only; not industry growth, global growth, a forecast or an enterprise buying signal. Publication: 12 November 2026. Preliminary and subject to revision.'}
    if factor not in COPY:
        raise ValueError('PESTLE factor unavailable')
    data = macro.load_context()  # Validates existing sources and country contracts.
    force = next(f for f in data['forces'] if f['id'] == FACTORS[factor][5])
    if 'GB' not in force['country_ids']:
        raise ValueError('Force outside selected market')
    source_ids = force['country_source_ids']['GB']
    sources = [s for s in data['sources'] if s['id'] in source_ids]
    title, text, effect = COPY[factor]
    return {'title': title, 'text': text, 'effect': effect,
        'lineage': {'force_id': force['id'], 'source_ids': source_ids,
                    'authority': data['authority'], 'as_of': data['as_of'],
                    'kind': force['kind']},
        'sources': sources,
        'details': force['what'] + ' ' + force['counter'] + ' Existing review cutoff: ' + data['as_of']
            + '. This is UK relevance of a wider theme, not global prevalence or verified company impact.'}


def _sources(factor):
    data = basis()
    body = '<details class="sources-menu" name="visual-header-tools"><summary>Sources & method</summary><section class="menu-sheet source-sheet" aria-label="Sources and methodology"><h2>Scale, scope & sources</h2>'
    body += '<p>United Kingdom · 2024 · GVA at current basic prices. £2.62tn is a rounded display of the ONS £2,623bn total. GVA is output less intermediate consumption; it is neither company revenue nor GDP at market prices.</p>'
    body += '<p>District shares are the published 2024 weights divided by ten, not estimates of sales. Rounded sections total 100.2%; no normalisation is applied. Real estate includes imputed owner-occupier rents. Area and building size are illustrative, not a quantitative map.</p>'
    body += '<p>SIC 2007 matches these national-accounts data; the newer SIC 2026 is not silently mixed in. All domestic sections A–T appear. U is extraterritorial activity and is outside the published domestic denominator.</p>'
    body += '<p>Technology, Banking and Aviation are researched subsets or cross-sector views. Their links do not claim coverage of their whole host section. Shares belong to Information & communication, Finance & insurance and Transport & storage respectively. No unsupported sub-sector share, employment or growth is shown.</p>'
    body += '<p>Solid green labels open existing research. Other district labels are inert. The illustration is conceptual geography, with no claimed corporate relationships. No personalised company information is read by these screens.</p>'
    body += '<details class="statistical-table"><summary>All comparable sector shares</summary><table><caption>UK GVA shares · 2024 · ONS published weights ÷ 10</caption><thead><tr><th>Section</th><th>Industry</th><th>Share</th></tr></thead><tbody>'
    for district in sorted(data['districts'], key=lambda d:d['sic']):
        body += '<tr><td>' + district['sic'] + '</td><th scope="row">' + e(district['label']) + '</th><td>' + f"{district['weight_per_thousand']/10:.1f}%" + '</td></tr>'
    body += '</tbody></table></details>'
    if factor:
        row = insight(factor)
        body += '<h3>' + e(FACTORS[factor][0]) + '</h3><p>' + e(row['details']) + '</p><p class="source-lineage">' + e(json.dumps(row['lineage'], sort_keys=True)) + '</p>'
        data['sources'] += row['sources']
    seen = set()
    for source in data['sources']:
        if source['id'] in seen:
            continue
        seen.add(source['id'])
        body += '<p><a href="' + e(source['url'], quote=True) + '" rel="noreferrer">' + e(source['title']) + '</a><br><small>' + e(source.get('publication_date') or source.get('reviewed_at') or '') + ' · ' + e(source.get('locator') or source.get('limitation') or '') + '</small></p>'
    return body + '<p>ONS data: Crown copyright, Open Government Licence. Public source excerpts and existing macro review retain their original limitations; no canonical research status is changed. Defensible estimates, when introduced, require EST, range and method. None are used in this study.</p></section></details>'


def _header(pestle, factor, headers):
    context = verified_context(headers)
    account = ('<p class="workspace-name">' + e(context.workspace) + '</p><a href="/auth/workspace">Switch workspace</a><form method="post" action="/auth/sign-out"><button type="submit">Sign out</button></form>'
               if context else '<a href="/auth/sign-in">Sign in</a>')
    return ('<header class="product-header"><span class="wordmark">FLORA</span><nav aria-label="FLORA navigation">'
        '<a href="' + url() + '"' + ('' if pestle else ' aria-current="page"') + '>UK economy</a>'
        '<a href="' + url(True) + '"' + (' aria-current="page"' if pestle else '') + '>PESTLE</a>'
        '<details class="product-menu" name="visual-header-tools"><summary>Menu</summary><div class="menu-sheet"><p class="market-label">Selected market · United Kingdom</p>'
        '<a href="/industries">Industries</a><a href="/enterprises">Enterprises</a><a href="/flora/offers">Offers</a><a href="/opportunities">Opportunities</a><a href="/pipeline">Pipeline</a>'
        + account + '</div></details>' + _sources(factor) + '</nav></header>')


def _home():
    data = basis()
    body = '<div class="scene-heading"><h1>United Kingdom</h1><p><strong>£2.62tn</strong> GVA <span>· 2024 · current basic prices</span></p></div>'
    body += '<figure class="economy-scene" aria-labelledby="world-description"><figcaption class="sr-only" id="world-description">A conceptual UK economic landscape. All 20 domestic SIC sections appear. Each percentage is its share of 2024 UK GVA, based on rounded ONS weights, not the size of the illustrated area. Only Technology, Banking and Aviation open existing researched experiences. On small screens the continuous world folds into its left and right halves.</figcaption>'
    for side in ('left', 'right'):
        body += '<div class="world-half ' + side + '"><img class="world-art" src="' + BASE + '/assets/uk-artwork" width="1536" height="1024" alt="" aria-hidden="true">'
        for district in data['districts']:
            x, y = district['position']
            if (x < 50) != (side == 'left'):
                continue
            x = x * 2 if side == 'left' else (x - 50) * 2
            body += '<div class="district" id="' + district['id'] + '" data-sic="' + district['sic'] + '" style="--x:' + str(x) + '%;--y:' + str(y) + '%"><span class="district-label">' + e(district['label']) + '</span><span class="' + ('district-scale' if district['sic'] in VISIBLE_SHARES else 'sr-only') + '"><span class="sr-only">UK GVA, 2024: </span>' + f"{district['weight_per_thousand'] / 10:.1f}%" + '</span>'
            if district['sic'] in RESEARCH:
                label, href = RESEARCH[district['sic']]
                body += '<a class="researched" href="' + href + '" data-research="' + label.lower() + '" aria-label="' + label + ': open existing researched experience; the percentage above is for the broader ' + e(district['label'], quote=True) + ' section">' + label + '<svg aria-hidden="true" width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 12L12 4M4 4h8v8"/></svg></a>'
            body += '</div>'
        body += '</div>'
    return body + '</figure>'


def _pestle(factor):
    body = '<div class="scene-heading"><h1>The forces around us.</h1><p>Global themes <span>· United Kingdom relevance</span></p></div>'
    body += '<figure class="pestle-scene" aria-labelledby="pestle-description"><figcaption class="sr-only" id="pestle-description">Six PESTLE factors in a conceptual landscape. Select a labelled factor to read one concise UK-relevant insight on the image. Global themes are not a claim of universal impact. Sources and the existing source review dates are available in the header.</figcaption><picture><source media="(max-width:600px)" srcset="' + BASE + '/assets/pestle-mobile-artwork"><img class="pestle-art" src="' + BASE + '/assets/pestle-artwork" width="1536" height="1024" alt="" aria-hidden="true"></picture>'
    for key, (label, x, y, mx, my, _) in FACTORS.items():
        body += '<a class="factor" id="factor-' + key + '" href="' + url(True, factor=key) + '#insight" style="--x:' + str(x) + '%;--y:' + str(y) + '%;--mx:' + str(mx) + '%;--my:' + str(my) + '%"' + (' aria-current="true"' if key == factor else '') + '>' + label + '<span aria-hidden="true"> +</span></a>'
    if factor:
        row = insight(factor)
        body += '<aside class="image-insight" id="insight" tabindex="-1" aria-labelledby="insight-title" data-factor="' + factor + '"><a class="close-insight" href="' + url(True) + '#factor-' + factor + '" aria-label="Close ' + e(FACTORS[factor][0]) + ' insight">×</a><p class="insight-label">' + e(FACTORS[factor][0]) + ' · UK</p><h2 id="insight-title">' + e(row['title']) + '</h2><p>' + e(row['text']) + '</p><p class="insight-effect">' + e(row['effect']) + '</p></aside>'
    return body + '</figure>'


def render(path, query, headers=None):
    factor = selection(path, query)
    pestle = path.endswith('/pestle')
    body = _pestle(factor) if pestle else _home()
    return ('<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>FLORA · ' + ('PESTLE' if pestle else 'United Kingdom') + ' · Visual study v2</title><link rel="stylesheet" href="' + BASE + '/assets/styles"><script defer src="' + BASE + '/assets/interactions"></script></head><body><a class="skip" href="#visual-content">Skip to visual</a>'
        + _header(pestle, factor, headers) + '<main id="visual-content" tabindex="-1" data-market="GB">' + body + '</main></body></html>')
