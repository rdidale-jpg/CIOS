"""Read-only Home design preview over existing owners, never a new truth store.

Active market is explicit URL presentation context. Seller territory, employer,
permissions and macro jurisdiction remain separate. No country/profile writes.
The current canonical Home is deliberately unchanged pending owner acceptance.
"""
from datetime import date
from html import escape as e
from pathlib import Path
from urllib.parse import urlencode

from .security import verified_service_read, verified_context
from .access import require_capability
from . import offers
from .commercial_mission import resolve_commercial_mission
from .research_intelligence import macro_intelligence as macro
from .research_intelligence.model import load_assessment, claim_segment

BASE = '/home'
ASSETS = Path(__file__).with_name('home_assets')
MARKETS = {
    'GB': {'name': 'United Kingdom', 'art': 'uk-artwork', 'coverage': 'industry_preview', 'lang': 'en-GB'},
    'FR': {'name': 'France', 'art': 'fr-artwork', 'coverage': 'layout_preview_only', 'lang': 'en-GB'},
}
REGIONS = (
    ('technology', 'Technology', '/industries/technology/experience', 23, 56),
    ('banking', 'Banking', '/industries/banking', 53, 42),
    ('aviation', 'Aviation', '/industries/aviation', 82, 69),
)
MARKETS['GB'].update(width=1774, height=887, regions=REGIONS,
    alt='Conceptual UK commercial landscape with a technology campus, financial district and airport.')
MARKETS['FR'].update(width=1983, height=793, regions=(),
    alt='Conceptual Paris-inspired landscape, used only to demonstrate the country layout.')
LENSES = {
    'political': ('Political', 'Policy priorities and public choices.'),
    'economic': ('Economic', 'Capital, costs and the economics of change.'),
    'social': ('Social', 'Changing behaviours, expectations and work.'),
    'technological': ('Technological', 'New capabilities and connected dependencies.'),
    'legal': ('Legal', 'Law, scope and implementation timelines.'),
    'environmental': ('Environmental', 'Resources, resilience and reporting.'),
}
FILES = {'styles': ('home.css', 'text/css; charset=utf-8'),
         'uk-artwork': ('uk-world.webp', 'image/webp'), 'fr-artwork': ('fr-world.webp', 'image/webp')}


def url(market='GB', path='', **query):
    return BASE + path + '?' + urlencode({'market': market, **query})


def asset(name):
    if name not in FILES:
        raise ValueError('Home preview asset unavailable')
    filename, mime = FILES[name]
    return (ASSETS / filename).read_bytes(), mime


def selected(query, macro_view=False):
    allowed = {'market', 'lens'} if macro_view else {'market'}
    if set(query) - allowed or any(len(value) != 1 for value in query.values()):
        raise ValueError('Unsupported Home selector')
    market = query.get('market', ['GB'])[0]
    lens = query.get('lens', ['overview'])[0]
    if market not in MARKETS or lens not in {'overview', *LENSES}:
        raise ValueError('Home preview selection unavailable')
    return market, lens


def _source_detail(sources, statement='', limits=''):
    body = '<details class="home-sources"><summary>Source & context</summary>'
    if statement:
        body += '<p>' + e(statement) + '</p>'
    for source in sources:
        body += '<p><a href="' + e(source['url'], quote=True) + '" rel="noreferrer">' + e(source['title']) + ' →</a></p>'
        if source.get('publication_date'):
            body += '<p>Published ' + e(source['publication_date']) + '</p>'
        if source.get('limitation'):
            body += '<p>' + e(source['limitation']) + '</p>'
    if limits:
        body += '<p>' + e(limits) + '</p>'
    return body + '</details>'


def changes(market, mission=None):
    """Presentation selections over validated existing dated source records.

    Dates below come only from the original source's publication_date. Retrieval
    or model updates can never create a fresh news date. No new claims stored.
    """
    if market != 'GB':
        return []
    rows = []
    configs = (
        ('aviation', 'AV-WIFI', 'Aviation', 'easyJet plans its next connected cabin',
         'The announced rollout creates a question about passenger experience and service integration; fleet-wide deployment is still ahead.',
         '/enterprises/easyjet?lens=timeline'),
        ('banking', 'LBG-ENVOY-CONTROLS', 'Banking', 'Lloyds describes AI controls inside Envoy',
         'Lloyds describes built-in Envoy controls and monitoring. A useful conversation starts with residual needs, rather than a greenfield-control pitch.',
         '/enterprises/lloyds?lens=ecosystem'),
    )
    for domain, claim_id, industry, title, why, href in configs:
        data = load_assessment(domain)
        claim = next(c for c in data['claims'] if c['id'] == claim_id)
        segment = claim_segment(data, claim)  # Existing SourceSegment validation/owner.
        sources = [s for s in data['sources'] if s['id'] in claim['source_ids']]
        dates = [s['publication_date'] for s in sources if s.get('publication_date')]
        if not dates:
            continue
        published = max(dates)
        if date.fromisoformat(published) > date.today():
            continue
        rows.append({'title': title, 'why': why, 'industry': industry, 'date': published,
            'href': href, 'sources': sources, 'statement': claim['statement'],
            'lineage': {'claim_id': claim_id, 'segment_id': segment.segment_id,
                        'content_sha256': segment.content_hash, 'authority': data['authority']}})
    context = macro.load_context()
    for force_id, title, industry in (
        ('uk-srs', 'A new reporting horizon for UK listed issuers', 'Across industries'),
        ('social-value', 'Social value is reshaping covered public tenders', 'Public procurement'),
    ):
        force = next(f for f in context['forces'] if f['id'] == force_id)
        sources = [s for s in context['sources'] if s['id'] in force['source_ids']]
        dates = [s['publication_date'] for s in sources if s.get('publication_date')]
        if not dates or date.fromisoformat(max(dates)) > date.today():
            continue
        rows.append({'title': title, 'why': ('For covered issuers, the next reporting cycle puts data, controls and assurance on the agenda.' if force_id == 'uk-srs' else 'For covered central-government tenders, social-value criteria become part of the commercial conversation.'), 'industry': industry, 'date': max(dates),
            'href': '/macro?' + urlencode({'market': market, 'category': force['category_ids'][0], 'force': force_id}),
            'sources': sources, 'statement': force['what'], 'limits': force['counter'],
            'lineage': {'force_id': force_id, 'source_ids': force['source_ids'], 'authority': context['authority']}})
    priorities = tuple(v.casefold() for v in mission.industries) if mission else ()
    return sorted(rows, key=lambda row: (not any(row['industry'].casefold() in p or p in row['industry'].casefold() for p in priorities),
                                          -date.fromisoformat(row['date']).toordinal()))[:4]


@verified_service_read('commercial_context.view')
def _personal(headers, market):
    state = offers.snapshot(headers=headers)
    mission = resolve_commercial_mission(headers)
    # Only current accessible employer-approved definitions enter Home's plays.
    approved = {o['id']: o for o in state['offers'] if o['current'] and o['eligible'] and o['state'] == 'employer_approved' and o['content'].get('evidence')}
    plays = []
    if market == 'GB' and state['selected'] and approved:
        assessments = offers.discover(evidence_cutoff='2026-11-13', headers=headers)
        for assessment in assessments:
            if assessment['offer_id'] not in approved or assessment['recommended_posture'] not in {'validate', 'partner'}:
                continue
            if not assessment['evidence_lineage'] or not any(r.get('segment_id') for r in assessment['evidence_lineage']):
                continue  # Presentation-only citations cannot become Home recommendations.
            plays.append({'assessment': assessment, 'offer': approved[assessment['offer_id']]})
        # Different account/offer pairs retain the existing assessment identity.
        unique = {}
        for play in plays:
            unique.setdefault(play['assessment']['assessment_id'], play)
        ordered = list(unique.values())
        first_by_account = {}
        for play in ordered:
            first_by_account.setdefault(play['assessment']['enterprise_id'], play)
        diverse = list(first_by_account.values())
        plays = (diverse + [p for p in ordered if p not in diverse])[:3]
    return state, mission, plays


def personal(headers, market):
    try:
        require_capability(headers, 'commercial_context.view')
    except PermissionError:
        return None, None, [], False
    try:
        state, mission, plays = _personal(headers, market)
        return state, mission, plays, False
    except PermissionError:
        # A revocation between the first check and scoped resolution returns no data.
        return None, None, [], False
    except (OSError, ValueError):
        return None, None, [], True


def _market_bar(market, macro_view=False, lens='overview'):
    path = BASE + ('/global-forces' if macro_view else '')
    options = ''.join('<option value="' + key + '"' + (' selected' if key == market else '') + '>'
                      + e(row['name'] + (' · layout preview' if key == 'FR' else '')) + '</option>' for key, row in MARKETS.items())
    globe = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18"/></svg>'
    return ('<div class="world-context"><form method="get" action="' + path + '"><label for="home-market">Selected market</label>'
            + ('<input type="hidden" name="lens" value="' + e(lens, quote=True) + '">' if macro_view and lens != 'overview' else '')
            + '<select id="home-market" name="market">' + options + '</select><button type="submit">View</button></form>'
            '<a class="global-window" href="' + url(market, '/global-forces') + '">' + globe + 'Global forces <span aria-hidden="true">→</span></a></div>')


def _focus(state, mission, unavailable, signed_in=False):
    body = '<section class="commercial-focus" aria-labelledby="focus-title"><div><p class="world-eyebrow">Your perspective</p><h2 id="focus-title">My Commercial Focus</h2></div>'
    if unavailable:
        return body + '<div><p>Your focus is temporarily unavailable.</p><a href="/flora/offers">Open My offers →</a></div></section>'
    if state is None and signed_in:
        return body + '<div><p>Commercial focus is not available in this workspace.</p><a href="/auth/workspace">Choose workspace →</a></div></section>'
    if state is None:
        return body + '<div><p>A clearer view starts with what you sell and who you want to reach.</p><a href="/auth/sign-in">Sign in to personalise your focus →</a></div></section>'
    selected_employer = state['selected']
    parts = []
    if selected_employer:
        parts.append('<div><small>Representing</small><strong>' + e(selected_employer['organisation']) + '</strong></div>')
    eligible = [o for o in state['offers'] if o['current'] and o['eligible']]
    if eligible:
        parts.append('<div><small>Offers available</small><strong>' + str(len(eligible)) + '</strong><a href="/flora/offers">My offers →</a></div>')
    if mission:
        if mission.geography:
            parts.append('<div><small>Seller territory</small><strong>' + e(' · '.join(mission.geography)) + '</strong></div>')
        if mission.priority_accounts:
            parts.append('<div><small>Your priority accounts</small><strong>' + e(' · '.join(mission.priority_accounts[:3])) + '</strong></div>')
        if mission.commercial_horizon:
            parts.append('<div><small>Horizon</small><strong>' + e(mission.commercial_horizon) + '</strong></div>')
    body += '<div class="focus-fields">' + ''.join(parts) + '</div>' if parts else '<p>Select your company and offers to shape your perspective.</p>'
    body += '<a class="focus-edit" href="/flora/offers/company">' + ('Refine focus' if parts else 'Choose company') + ' →</a>'
    return body + '</section>'


def _plays(plays, market):
    body = '<aside class="sales-plays" aria-labelledby="plays-title"><p class="world-eyebrow">Where to begin</p><h2 id="plays-title">Recommended Sales Plays</h2>'
    if not plays:
        if market == 'FR':
            return body + '<p>Local plays will appear when supported account and offer assessments are available.</p><a href="' + url(market, '/global-forces') + '">Explore global forces →</a></aside>'
        return body + '<p>Start with what you offer. Find the right account, then a useful first conversation.</p><a href="/flora/offers">Explore My offers →</a></aside>'
    for item in plays:
        a, offer = item['assessment'], item['offer']
        href = '/flora/offers/discover?' + urlencode({'mode': 'account', 'selected': a['enterprise_slug'], 'cutoff': a['source_cut_off']})
        body += ('<article class="home-play" data-assessment-id="' + e(a['assessment_id']) + '"><p class="world-eyebrow">'
            + e(a['enterprise_name']) + ' · ' + e(a['recommended_posture']) + '</p><h3>' + e(offer['content']['name'])
            + '</h3><p>' + e(a['entry_play']) + '</p><a href="' + e(href, quote=True) + '#' + e(a['assessment_id'])
            + '">Explore this play →</a><details class="home-sources"><summary>Why this play</summary><p>' + e(a['why_account'])
            + '</p><p>' + e(a['next_validation_action']) + '</p><p>Need, buyer access and delivery fit require validation. No buying intent or funding established.</p></details></article>')
    return body + '</aside>'


def _explore(market):
    # The existing libraries are UK-oriented; switching country never relabels them.
    label = 'Industries' if market == 'GB' else 'UK industry library'
    return ('<nav class="world-explore" aria-label="Explore"><span>Explore</span><a href="/industries">' + label
            + '</a><a href="/enterprises">' + ('Enterprises' if market == 'GB' else 'UK enterprise library') + '</a><a href="/flora/offers">Offers</a><a href="/opportunities">' + ('Opportunities' if market == 'GB' else 'UK opportunity library') + '</a>'
            '<a href="/flora/sales/pipeline">Pipeline</a></nav>')


def home(market, headers):
    state, mission, plays, unavailable = personal(headers, market)
    info = MARKETS[market]
    body = _market_bar(market)
    body += '<header class="world-heading"><p class="world-eyebrow">Your commercial world</p><h1>Find your next opening.</h1><p>See the landscape. Connect industries, enterprises and the forces changing them.</p></header>'
    body += '<div class="world-scene world-scene-' + market.lower() + '" id="industry-world">'
    body += '<img src="' + BASE + '/assets/' + info['art'] + '" width="' + str(info['width']) + '" height="' + str(info['height']) + '" alt="' + e(info['alt'], quote=True) + '" fetchpriority="high">'
    if info['regions']:
        body += '<nav class="world-regions" aria-label="Illustrated ' + e(info['name'], quote=True) + ' industry regions">'
        for key, title, href, left, top in info['regions']:
            body += '<a href="' + href + '" class="world-region" data-industry="' + key + '" style="--x:' + str(left) + '%;--y:' + str(top) + '%"><span aria-hidden="true">◦</span>' + e(title) + '<span aria-hidden="true">→</span></a>'
        body += '</nav>'
    else:
        body += '<div class="country-preview"><p class="world-eyebrow">Country layout preview</p><h2>France. A new perspective.</h2><p>Explore global forces while local industry views take shape.</p></div>'
    body += '</div>' + _focus(state, mission, unavailable, bool(verified_context(headers)))
    body += '<div class="world-editorial"><section class="world-changes" aria-labelledby="changes-title"><div class="section-heading"><div><p class="world-eyebrow">Signals that matter</p><h2 id="changes-title">What’s Changing</h2></div><a href="' + url(market, '/global-forces') + '">The wider picture →</a></div>'
    rows = changes(market, mission)
    if not rows:
        body += '<div class="country-brief"><h3>A wider lens on your next market</h3><p>This layout preview contains no local industry briefing or account recommendations.</p><a href="' + url(market, '/global-forces') + '">Look through the global lens →</a></div>'
    for row in rows:
        body += ('<article class="world-change"><div><time datetime="' + row['date'] + '">' + date.fromisoformat(row['date']).strftime('%d %b %Y').lstrip('0')
                 + '</time><small>' + e(row['industry']) + '</small></div><div><h3>' + e(row['title']) + '</h3><p>' + e(row['why'])
                 + '</p><a href="' + e(row['href'], quote=True) + '">Read the insight →</a>'
                 + _source_detail(row['sources'], row['statement'], row.get('limits', 'Existing source, scope and identity limits retained; no customer demand inferred.')) + '</div></article>')
    body += '</section>' + _plays(plays, market) + '</div>' + _explore(market)
    return body


def global_forces(market, lens):
    data = macro.load_context()
    body = '<a class="back-world" href="' + url(market) + '">← Back to your world</a>' + _market_bar(market, True, lens)
    body += '<header class="world-heading macro-heading"><p class="world-eyebrow">Global forces · PESTLE</p><h1>A wider lens.<br>A clearer perspective.</h1><p>Separate the force from its local effect. Selected market: ' + e(MARKETS[market]['name']) + '.</p></header>'
    body += '<nav class="pestle-nav" aria-label="Global PESTLE lenses"><a href="' + url(market, '/global-forces') + '"' + (' aria-current="page"' if lens == 'overview' else '') + '>Overview</a>'
    for key, (label, _) in LENSES.items():
        body += '<a href="' + url(market, '/global-forces', lens=key) + '"' + (' aria-current="page"' if lens == key else '') + '>' + label + '</a>'
    body += '</nav>'
    if lens == 'overview':
        body += '<div class="pestle-intro">' + ''.join('<a href="' + url(market, '/global-forces', lens=k) + '"><h2>' + e(v[0]) + '</h2><p>' + e(v[1]) + '</p></a>' for k, v in LENSES.items()) + '</div>'
    else:
        body += '<h2 class="lens-title">' + e(LENSES[lens][0]) + '</h2><p>' + e(LENSES[lens][1]) + '</p>'
    forces = [f for f in data['forces'] if market in f['country_ids'] and (lens == 'overview' or LENSES[lens][0] in f['pestle'])]
    if not forces:
        body += '<section class="macro-reading"><h2>Keep this lens open</h2><p>No selected signal is presented in this lens. The wider macro view remains available.</p></section>'
    for force in forces:
        cross = force['id'] == 'cyber'
        ids = force.get('country_source_ids', {}).get(market, [])
        sources = [s for s in data['sources'] if s['id'] in ids]
        href = '/macro?' + urlencode({'market': market, 'category': force['category_ids'][0], 'force': force['id'], 'view': 'industry'})
        body += '<article class="macro-reading"><p class="world-eyebrow">' + ('Across markets → ' if cross else 'Local policy → ') + e(MARKETS[market]['name']) + '</p><h2>' + e(force['label']) + '</h2>'
        if cross:
            body += '<p class="macro-origin">Cross-market theme: connected-service dependencies can transmit disruption. The cited country evidence below is not a global prevalence estimate.</p>'
        body += '<div class="macro-columns"><div><h3>What the sources describe</h3><p>' + e(force['what']) + '</p></div><div><h3>Local exposure to test</h3><p>' + e(force['why']) + '</p></div></div><p><strong>First question</strong> ' + e(force['next']) + '</p><a href="' + e(href, quote=True) + '">Follow the industry and enterprise context →</a>'
        body += _source_detail(sources, limits=force['counter'] + ' No measured national or enterprise impact is inferred. Existing reviewed source cutoff: ' + data['as_of'] + '.') + '</article>'
    body += '<p class="macro-bottom"><a href="/macro?market=global">Open the full Global & Macro view →</a></p>'
    return body


def _render(path, query, headers=None):
    from .web.app import _flora_v2_page
    from .security import verified_context
    macro_view = path == BASE + '/global-forces'
    if path not in {BASE, BASE + '/global-forces'}:
        raise ValueError('Home preview route unavailable')
    market, lens = selected(query, macro_view)
    body = global_forces(market, lens) if macro_view else home(market, headers)
    content = '<link rel="stylesheet" href="' + BASE + '/assets/styles"><a class="home-skip" href="#home-content">Skip to content</a><section class="home-world" id="home-content" tabindex="-1" data-market="' + market + '"><p class="home-preview-label">Home v1 · Design preview</p>' + body + '</section>'
    context = verified_context(headers)
    if context:
        account = ('<details class="home-account-menu"><summary>My workspace</summary><p>' + e(context.workspace)
                   + '</p><a href="/auth/workspace">Switch workspace</a><form method="post" action="/auth/sign-out"><button type="submit">Sign out</button></form></details>')
    else:
        account = '<a class="home-sign-in" href="/auth/sign-in">Sign in</a>'
    html = _flora_v2_page('FLORA — Your commercial world', 'home', content, account)
    return html.replace('</head>', '<meta name="robots" content="noindex,nofollow"></head>', 1).replace('<body>', '<body class="home-preview">', 1)



@verified_service_read('commercial_context.view')
def _render_personal(path, query, headers=None):
    # Preserve the existing authority/revocation lock for the complete private render.
    return _render(path, query, headers)


def render(path, query, headers=None):
    if path == BASE:
        try:
            require_capability(headers, 'commercial_context.view')
        except PermissionError:
            return _render(path, query, headers)
        try:
            return _render_personal(path, query, headers)
        except PermissionError:
            # Revocation cannot leave a partial personalised response behind.
            return _render(path, query, headers)
    return _render(path, query, headers)
