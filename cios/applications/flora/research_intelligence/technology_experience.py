"""Owner-approved Technology journey; read-only public research, tab-local sales demo.

No canonical enterprise binding, importer, model client or live Pipeline access.
The supplementary presentation facts cite their public sources; they do not
create an Evidence store or change the reviewed foundation's acceptance state.
"""
from html import escape
from pathlib import Path
from urllib.parse import urlencode

from . import technology as research
from .technology_views import DESCRIPTIONS
from .unified_views import page

BASE = '/industries/technology/experience'
PATHS = frozenset(BASE + suffix for suffix in (
    '', '/district', '/enterprise', '/operating-model', '/pipeline', '/opportunity',
))
ASSET_BASE = BASE + '/assets/'
ASSETS = Path(__file__).with_name('technology_experience_assets')
ASSET_FILES = {'artwork': 'uk-technology.webp', 'styles': 'experience.css', 'interactions': 'experience.js'}
ASSET_TYPES = {'artwork': 'image/webp', 'styles': 'text/css; charset=utf-8',
               'interactions': 'text/javascript; charset=utf-8'}
STAGES = ('Discovery', 'Qualified', 'Proposal', 'Negotiation', 'Won', 'Lost')
DISTRICTS = {
    'applications': ('Applications & software', (3, 21, 30, 39)),
    'cloud': ('Cloud & data centres', (69, 23, 30, 27)),
    'ai': ('AI & data', (25, 57, 23, 19)),
    'cyber': ('Cybersecurity', (32, 23, 24, 17)),
    'services': ('Services & integration', (45, 39, 28, 22)),
    'channels': ('Channels & distribution', (0, 66, 26, 25)),
    'infrastructure': ('Connectivity & infrastructure', (59, 17, 9, 24)),
    'frontier': ('Frontier technology', (57, 58, 42, 34)),
}
REPORT_URL = 'https://investor.equinix.com/sec-filings/all-sec-filings/content/0001101239-26-000032/eqix-20251231.htm'
CMA_URL = 'https://assets.publishing.service.gov.uk/media/688b20e6ff8c05468cb7b120/summary_of_final_decision.pdf'
GRID_URL = 'https://commonslibrary.parliament.uk/research-briefings/cbp-10315/'
SOURCE_NOTE = 'Public presentation research checked 12 Nov 2026; not a canonical import.'
# These fields match the approved mockups. No named customer demand is inferred.
DEMO_ROWS = (
    {'id': 'cooling', 'title': 'Cooling optimisation', 'enterprise': 'Northbridge DC (demo)',
     'district': 'cloud', 'stage': 'Discovery', 'start': '2026-12-01', 'close': '2027-03-31',
     'tcv': '240000', 'unit': 'Facilities', 'stakeholder': '', 'owner': '',
     'need': 'Assess whether cooling upgrades could support planned capacity and operating efficiency.',
     'next': 'Confirm need, sponsor and funding'},
    {'id': 'migration', 'title': 'Cloud migration', 'enterprise': 'Example Services (demo)',
     'district': 'cloud', 'stage': 'Qualified', 'start': '2026-11-15', 'close': '2027-06-30',
     'tcv': '680000', 'unit': 'Technology', 'stakeholder': '', 'owner': '',
     'need': 'Explore a migration scope and the business outcomes it would support.',
     'next': 'Confirm scope and delivery requirements'},
    {'id': 'resilience', 'title': 'Resilience assessment', 'enterprise': 'Example Platforms (demo)',
     'district': 'cyber', 'stage': 'Proposal', 'start': '2026-11-01', 'close': '2027-02-28',
     'tcv': '95000', 'unit': 'Operations', 'stakeholder': '', 'owner': '',
     'need': 'Review service recovery objectives and dependencies.',
     'next': 'Review the illustrative proposal'},
    {'id': 'connectivity', 'title': 'Connectivity upgrade', 'enterprise': 'Example Infrastructure (demo)',
     'district': 'infrastructure', 'stage': 'Discovery', 'start': '', 'close': '', 'tcv': '',
     'unit': 'Network services', 'stakeholder': '', 'owner': '',
     'need': 'Explore connectivity requirements and delivery options.',
     'next': 'Arrange an initial discovery conversation'},
)


MACRO_CONTEXT = {
    'technology': ('AI & Technology', 'AI and hybrid workloads connect capacity demand to integration and platform choices.',
                   'Explore workload readiness and the capacity needed to deliver useful services.'),
    'economy': ('Economy & Geopolitics', 'Capital-intensive infrastructure has different economics from software and labour-intensive services.',
                'Explore capacity utilisation, investment priorities and the business case for change.'),
    'sustainability': ('Sustainability & Social Value', 'Energy, water and infrastructure location affect growth decisions.',
                      'Explore efficiency, measurement and delivery constraints at a specific facility.'),
    'cyber': ('Cyber & Resilience', 'Connected digital services depend on resilient infrastructure and recoverable operations.',
              'Explore critical-service dependencies and recovery requirements; no enterprise weakness is inferred.'),
}


def url(suffix='', **query):
    return BASE + suffix + ('?' + urlencode({k: v for k, v in query.items() if v}) if any(query.values()) else '')


def link(href, text, **attrs):
    attributes = ''.join(f' {escape(k.replace("_", "-"))}="{escape(str(v), quote=True)}"' for k, v in attrs.items())
    return f'<a href="{escape(href, quote=True)}"{attributes}>{escape(text)}</a>'


def asset(name):
    if name not in ASSET_TYPES:
        raise ValueError('Unknown experience asset')
    file = ASSETS / ASSET_FILES[name]
    if file.is_symlink() or not file.is_file() or not file.resolve().is_relative_to(ASSETS.resolve()):
        raise ValueError('Experience asset unavailable')
    return file.read_bytes(), ASSET_TYPES[name]


def validate(query):
    if set(query) - {'selected', 'district', 'scope', 'record', 'detail', 'area', 'macro'}:
        raise ValueError('Unknown experience selector')
    for key in ('selected', 'district'):
        if query.get(key, '') not in ('', *DISTRICTS):
            raise ValueError('Unknown district')
    if query.get('scope', '') not in ('', 'industry', 'equinix', *DISTRICTS):
        raise ValueError('Unknown Pipeline scope')
    if query.get('area', '') not in ('', 'facilities', 'interconnection'):
        raise ValueError('Unknown conceptual area')
    if query.get('macro', '') not in ('', *MACRO_CONTEXT):
        raise ValueError('Unknown macro category')
    record = query.get('record', '')
    # Tab-local new records are validated again by JS. No ID resolves a server store.
    import re
    if record and not re.fullmatch(r'(cooling|migration|resilience|connectivity|demo-[a-f0-9-]{1,40})', record):
        raise ValueError('Unknown demo opportunity')
    if query.get('detail', '') not in ('', 'financials', 'strategy'):
        raise ValueError('Unknown enterprise detail')


def crumbs(parts):
    items = [link('/industries', 'Industries'), link(BASE, 'UK Technology')]
    items += [link(href, label) if href else f'<span aria-current="page">{escape(label)}</span>' for label, href in parts]
    return '<nav class="exp-crumb" aria-label="Breadcrumb">' + '<span aria-hidden="true"> / </span>'.join(items) + '</nav>'


def pipeline_link(scope='industry'):
    return link(url('/pipeline', scope=scope), 'Pipeline →', class_='exp-pipeline-link')


def support():
    return ('<details class="exp-support"><summary>Research & supporting views</summary><nav>'
            + link(research.BASE + '?lens=how', 'Original functional prototype')
            + link(research.BASE + '/providers', 'All 80 provider views')
            + link(research.BASE + '?lens=uses', '34 programmes & relationships')
            + link(research.BASE + '?lens=work', 'Six commercial themes')
            + link(research.BASE + '/evidence', 'Research sources & limitations')
            + link('/macro', 'Macro intelligence') + link('/flora/sales/pipeline', 'Live Pipeline (sign-in required)')
            + '</nav><p>Research remains partial. Canonical identities and source-operation rights remain unresolved. '
            'No canonical promotion or live Pipeline writes.</p></details>')


def scene(selected=''):
    hotspots = []
    for key, (label, (x, y, w, h)) in DISTRICTS.items():
        current = ' aria-current="true"' if selected == key else ''
        hotspots.append(f'<a class="exp-hotspot" data-district="{key}" href="{url(selected=key)}#scene" '
                        f'aria-label="{escape(label)}" style="left:{x}%;top:{y}%;width:{w}%;height:{h}%"{current}>'
                        f'<span>{escape(label)}</span></a>')
    detail = ''
    if selected:
        label = DISTRICTS[selected][0]
        desc = ('Compute, storage and the facilities that support digital services.' if selected == 'cloud'
                else DESCRIPTIONS[selected])
        detail = (f'<aside class="exp-scene-detail" aria-label="Selected district"><a class="exp-close" href="{BASE}#scene" '
                  f'aria-label="Close district detail">×</a><h2>{escape(label)}</h2><p>{escape(desc)}</p>'
                  + link(url('/district', district=selected), 'Explore this area →') + '</aside>')
    return (crumbs([]) + '<div class="exp-heading exp-scene-heading"><h1>UK Technology</h1>' + pipeline_link() + '</div>'
            f'<section class="exp-scene" id="scene" aria-label="UK Technology industry scene"><div class="exp-artwork">'
            f'<img src="{ASSET_BASE}artwork" width="1536" height="1024" alt="Conceptual UK technology landscape with software offices, '
            'data centres, research laboratories, a connectivity mast and distribution facilities against a London skyline.">'
            + ''.join(hotspots) + ('' if selected else '<span class="exp-scene-hint">Explore an area</span>')
            + '</div>' + detail + '</section><details class="exp-textnav"><summary>Explore by name</summary><nav>'
            + ''.join(link(url('/district', district=k), label) for k, (label, _) in DISTRICTS.items())
            + '</nav></details>')


def image_crop(css='exp-crop', caption='Conceptual illustration, not an Equinix facility'):
    return f'<figure class="{css}"><img src="{ASSET_BASE}artwork" alt="{escape(caption)}" width="1536" height="1024"></figure>'


def macro_links(suffix='/district', selected='', **context):
    # Same category IDs as the Macro owner, interpreted against Technology's
    # existing PESTLE research. Never inherit its default Banking applicability.
    nav = '<nav class="exp-macro" aria-label="Macro themes"><span>Macro themes</span>' + ' · '.join(
        link(url(suffix, macro=key, **context) + '#macro-context', value[0],
             aria_current='page' if selected == key else 'false') for key, value in MACRO_CONTEXT.items()) + '</nav>'
    if not selected:
        return nav
    label, insight, next_step = MACRO_CONTEXT[selected]
    data, _ = research.load()
    return (nav + '<section class="exp-editorial" id="macro-context"><h2>' + escape(label) + '</h2>'
            '<p class="exp-lead">' + escape(insight) + '</p><p>' + escape(next_step) + '</p>'
            '<details class="exp-support"><summary>Background</summary><p>Flora interpretation of industry context; '
            'not confirmed enterprise demand or a legal applicability finding.</p>'
            + link(research.BASE + '/evidence#block-' + data['pestle_block'], 'Technology industry context')
            + '</details></section>')


def district(key, macro=""):
    data, _ = research.load()
    label = DISTRICTS[key][0]
    title = crumbs([(label, '')]) + '<div class="exp-heading"><h1>' + escape(label) + '</h1>' + pipeline_link(key) + '</div>'
    if key != 'cloud':
        providers = [r for r in data['providers'] if key in r['memberships']]
        return (title + '<p class="exp-lead">' + escape(DESCRIPTIONS[key]) + '</p>' + image_crop()
                + '<h2>Enterprises in Flora</h2><div class="exp-list">'
                + ''.join(link(research.BASE + '/providers?provider=' + r['key'], r['label'] + ' →') for r in providers)
                + '</div><p class="exp-subtle">Provider research views; identities remain unbound. This district’s market baseline is not yet reconciled.</p>')
    return (title + '<div class="exp-market-intro"><div><p class="exp-market-number">£10.5bn</p>'
            '<p>UK public cloud spend · 2024 · IaaS & PaaS</p><p class="exp-subtle">Cloud benchmark, not total district value</p></div>'
            + image_crop() + '</div><section class="exp-editorial"><h2>Demand meets delivery constraints</h2>'
            '<p class="exp-lead">AI and cloud demand face power, grid and planning constraints.</p>'
            '<dl class="exp-facts"><div><dt>Key pain points</dt><dd>Power availability, connection delays and capacity delivery.</dd></div>'
            '<div><dt>Where to investigate</dt><dd>Capacity delivery, energy efficiency and resilient connectivity.</dd></div></dl></section>'
            + macro_links(selected=macro, district=key) + '<section><h2>Enterprises in Flora</h2><div class="exp-list">'
            + link(url('/enterprise'), 'Equinix →')
            + link(research.BASE + '/providers?provider=digital-realty', 'Digital Realty →')
            + link(research.BASE + '/providers?provider=virtus', 'VIRTUS →') + '</div></section>'
            '<details class="exp-support"><summary>Market context & definitions</summary><p>2024 spending benchmark from the CMA’s 2025 final decision; '
            'it excludes SaaS and is not a combined cloud-and-colocation market valuation. No newer comparable market figure is asserted here.</p>'
            + link(CMA_URL, 'CMA market definition & spending') + ' · ' + link(GRID_URL, 'UK capacity constraints')
            + '<p>Macro themes are existing Flora categories. Their relevance here is analysis, not proof of a specific enterprise obligation or buying need.</p></details>')


def enterprise(detail=''):
    body = (crumbs([('Cloud & data centres', url('/district', district='cloud')), ('Equinix', '')])
            + '<div class="exp-heading"><div><h1>Equinix</h1><p class="exp-subtitle">Global group · FY2025 annual report</p></div>'
            + pipeline_link('equinix') + '</div><p class="exp-subtle">Global figures · USD</p><div class="exp-financials">'
            + ''.join(link(url('/enterprise', detail='financials') + '#' + key,
                           value + ' · ' + label) for key, value, label in (
                               ('revenue', '$9.217bn', 'Revenue'), ('colocation', '$6.475bn', 'Colocation'),
                               ('interconnection', '$1.655bn', 'Interconnection')))
            + '</div><p class="exp-lead">A recurring infrastructure business built around colocation and interconnection.</p>'
            + image_crop() + '<div class="exp-list">'
            + link(url('/enterprise', detail='strategy') + '#enterprise-detail', 'Strategy & investment →')
            + link(url('/enterprise', detail='financials') + '#enterprise-detail', 'Business & financials →')
            + link(url('/operating-model'), 'Explore enterprise →') + '</div>')
    if detail:
        content = ('<h2>Business & financials</h2><dl class="exp-facts">'
                   '<div id="revenue"><dt>Revenue</dt><dd>$9.217bn consolidated revenue in FY2025, compared with $8.748bn in FY2024.</dd></div>'
                   '<div id="colocation"><dt>Colocation</dt><dd>$6.475bn FY2025 revenue.</dd></div>'
                   '<div id="interconnection"><dt>Interconnection</dt><dd>$1.655bn FY2025 revenue.</dd></div></dl>'
                   '<p>The two service lines do not sum to group revenue; other revenue classifications remain in the filing. No UK-only financial figure is inferred.</p>'
                   if detail == 'financials' else
                   '<h2>Strategy & investment</h2><p>FY2025 revenue growth included completed data-centre expansion projects and additional customer orders. '
                   'Capacity delivery and connected ecosystems provide areas for further commercial investigation.</p>'
                   '<p>Flora interpretation: explore whether a specific facility has a power, cooling or connectivity requirement. '
                   'This does not establish a UK project, available budget or an external sourcing mandate.</p>')
        body += '<section class="exp-editorial" id="enterprise-detail">' + content + link(REPORT_URL, 'Read the FY2025 filing →') + '</section>'
    return body + ('<details class="exp-support"><summary>Reporting context</summary><p>' + SOURCE_NOTE
                   + ' Latest annual filing checked: FY2025, filed 11 February 2026. These are annual figures, not the latest quarterly trading update. '
                   'Equinix is an existing Flora provider view; group-to-UK operating entity and contracting scope remain unresolved.</p>'
                   + link(REPORT_URL, 'Annual report') + ' · ' + link(research.BASE + '/providers?provider=equinix', 'Retained Flora profile') + '</details>')


def operating_model(area='facilities', macro=''):
    label, angle, question = {
        'facilities': ('Facilities', 'Explore power and cooling optimisation as capacity expands.', 'Which facilities have a funded requirement and an external delivery gap?'),
        'interconnection': ('Interconnection', 'Explore resilient connectivity and hybrid-cloud integration needs.', 'Which workloads or connections need improvement, and who owns the decision?'),
    }[area]
    return (crumbs([('Cloud & data centres', url('/district', district='cloud')), ('Equinix', url('/enterprise')), ('Inside Equinix', '')])
            + '<div class="exp-heading"><div><h1>Inside Equinix</h1><p class="exp-subtitle">Flora conceptual operating view</p></div>'
            + pipeline_link('equinix') + '</div>' + image_crop()
            + '<nav class="exp-tabs" aria-label="Conceptual enterprise areas">'
            + ''.join(link(url('/operating-model', area=k, macro=macro), name, aria_current='page' if k == area else 'false')
                      for k, name in (('facilities', 'Facilities'), ('interconnection', 'Interconnection')))
            + '</nav><section id="operating-area" class="exp-editorial"><h2>' + label + '</h2>'
            + '<dl class="exp-facts"><div><dt>Potential sales angle</dt><dd>' + angle + '</dd></div>'
            + '<div><dt>Next conversation</dt><dd>' + question + '</dd></div></dl></section>'
            + macro_links('/operating-model', selected=macro, area=area) + '<p class="exp-subtle">Hypothesis · demand and budget not established. This model is not a disclosed organisation chart.</p>'
            + link(url('/pipeline', scope='equinix'), 'View enterprise Pipeline →', class_='exp-button')
            + '<details class="exp-support"><summary>Investigate this need</summary><p>Confirm the facility, requirement, sponsor, timing and procurement route with the customer. '
            'Existing teams or suppliers may already address it. A public growth theme is not a qualified opportunity.</p>'
            + link(research.BASE + '?lens=work&theme=theme-4', 'Infrastructure & cloud connectivity research') + '</details>')


def demo_json():
    import json
    return json.dumps(DEMO_ROWS, separators=(',', ':')).replace('<', '\\u003c').replace('&', '\\u0026')


def baseline_rows(scope):
    rows = [r for r in DEMO_ROWS if scope == 'industry' or r['district'] == scope]
    if not rows:
        return '<tr><td colspan="8">No illustrative opportunities in this scope. No research hypothesis has been promoted to Pipeline.</td></tr>'
    return ''.join('<tr><td>' + link(url('/opportunity', record=r['id'], scope=scope), r['title'])
        + '</td><td>' + escape(r['enterprise']) + '</td><td>' + r['stage'] + '</td><td>' + (r['start'] or 'Not set')
        + '</td><td>' + (r['close'] or 'Not set') + '</td><td>' + ('£' + format(float(r['tcv']), ',.0f') if r['tcv'] else 'Not set')
        + '</td><td>' + escape(r['unit']) + '</td><td>Unassigned</td></tr>' for r in rows)


def pipeline(scope):
    options = [('industry', 'All UK Technology'), *[(k, v[0]) for k, v in DISTRICTS.items()], ('equinix', 'Equinix')]
    choices = ''.join(f'<option value="{k}"' + (' selected' if k == scope else '') + '>' + escape(v) + '</option>' for k, v in options)
    body = (crumbs([('Pipeline', '')]) + '<div class="exp-heading"><div><h1>Sales pipeline</h1><p class="exp-subtitle" id="scope-label">'
            + escape(dict(options)[scope]) + '</p></div><form method="get" class="exp-scope-form"><label for="pipeline-scope">Scope</label>'
            f'<select id="pipeline-scope" name="scope">{choices}</select><button>Apply</button></form></div>'
            '<div class="exp-toolbar"><label>Search opportunities<input type="search" id="pipeline-search" placeholder="Search opportunities"></label>'
            '<label>Stage<select id="pipeline-stage"><option value="">All stages</option>'
            + ''.join(f'<option>{x}</option>' for x in STAGES) + '</select></label>'
            '<label>Owner<select id="pipeline-owner"><option value="">All owners</option><option value="__unassigned">Unassigned</option></select></label>'
            '<button type="button" data-new-opportunity class="exp-button">+ Opportunity</button></div>'
            '<p class="exp-demo-notice">Owner-testing preview · illustrative entries · edits stay in this browser tab</p>'
            '<div class="exp-table-wrap" tabindex="0" role="region" aria-label="Sales pipeline, scroll horizontally for all columns">'
            '<table class="exp-table"><caption class="visually-hidden">Illustrative sales opportunities. Select an opportunity to view details.</caption><thead><tr>'
            + ''.join(f'<th scope="col" aria-sort="none"><button type="button" data-sort="{key}">{label} <span aria-hidden="true">↕</span></button></th>' for key, label in (
                ('title', 'Opportunity'), ('enterprise', 'Enterprise'), ('stage', 'Stage'), ('start', 'Start date'), ('close', 'Close date'),
                ('tcv', 'TCV (GBP)'), ('unit', 'Business unit / stakeholder'), ('owner', 'Owner')))
            + '</tr></thead><tbody id="pipeline-rows">' + baseline_rows(scope) + '</tbody></table></div>'
            '<noscript><p>Illustrative records are read-only without JavaScript. Tab-local editing requires JavaScript.</p></noscript>'
            '<p id="pipeline-count" class="exp-subtle" role="status"></p><section id="quick-detail" hidden aria-label="Selected opportunity"></section>'
            '<p class="exp-subtle">Start date = opportunity opened · Close date = expected signature · TCV = estimated full-term value, excluding VAT.</p>'
            '<p><button class="exp-text-button" type="button" id="reset-demo">Reset preview changes</button></p>')
    return body + demo_form()


def demo_form():
    return ('<dialog id="demo-editor" aria-labelledby="editor-title"><form id="opportunity-form"><div class="exp-heading"><h2 id="editor-title">Edit opportunity</h2>'
            '<button type="button" id="close-editor" aria-label="Cancel editing">×</button></div><p class="exp-subtle">Preview only · no live sales records are created or changed.</p>'
            '<div class="exp-form-grid">'
            + ''.join(f'<label>{label}<input name="{key}" type="{kind}" maxlength="{limit}"'
                      + (' required' if key in ('title', 'enterprise') else '')
                      + (' min="0" max="999999999999" step="0.01"' if key == 'tcv' else '') + '></label>'
                      for key, label, kind, limit in (
                          ('title', 'Opportunity', 'text', 120), ('enterprise', 'Enterprise', 'text', 120),
                          ('start', 'Start date (opened)', 'date', 10), ('close', 'Expected close', 'date', 10),
                          ('tcv', 'Estimated TCV (GBP, excluding VAT)', 'number', 15), ('owner', 'Owner', 'text', 100),
                          ('unit', 'Business unit', 'text', 100), ('stakeholder', 'Key stakeholder', 'text', 100),
                          ('decision', 'Decision maker', 'text', 100), ('budgetOwner', 'Budget owner', 'text', 100),
                          ('responsible', 'Next-action owner', 'text', 100), ('due', 'Next-action due date', 'date', 10)))
            + '<label>Stage<select name="stage">' + ''.join(f'<option>{x}</option>' for x in STAGES) + '</select></label>'
            '<label>District<select name="district">' + ''.join(f'<option value="{k}">{v[0]}</option>' for k, v in DISTRICTS.items()) + '</select></label>'
            '<label>Budget<select name="budget"><option>Not confirmed</option><option>Confirmed (demo)</option></select></label>'
            '<label>Procurement route<input name="procurement" maxlength="200"></label>'
            '<label>Competition<input name="competition" maxlength="200"></label>'
            '<label class="exp-form-wide">Buying need<textarea name="need" maxlength="1000" rows="2"></textarea></label>'
            '<label class="exp-form-wide">Next action<input name="next" maxlength="300"></label></div>'
            '<p id="editor-error" role="alert"></p><button type="submit" class="exp-button">Save preview changes</button></form></dialog>')


def opportunity(record, scope):
    # JS hydrates tab-local changes; the repository demo also has a native read view.
    row = next((r for r in DEMO_ROWS if r['id'] == record and (scope == 'industry' or r['district'] == scope)), None)
    initial = ('<h1>' + escape(row['title']) + '</h1><p>' + escape(row['enterprise']) + ' · Illustrative opportunity</p>'
               + '<h2>Buying need</h2><p>' + escape(row['need']) + '</p><h2>Next action</h2><p>' + escape(row['next']) + '</p>'
               + '<p>Stage: ' + row['stage'] + ' · Owner: Unassigned</p>' if row else
               '<h1>Opportunity preview</h1><p>This tab-local record requires JavaScript to display.</p>')
    return (crumbs([('Pipeline', url('/pipeline', scope=scope)), ('Opportunity', '')])
            + '<div id="opportunity-detail" aria-live="polite">' + initial + '</div>'
            + '<noscript><p>Interactive preview editing requires JavaScript. No live records are accessed.</p>'
            + link(url('/pipeline', scope=scope), 'Return to Pipeline') + '</noscript>' + demo_form())


def render(path, query, headers=None):
    if path not in PATHS:
        raise ValueError('Unknown Technology experience view')
    validate(query)
    suffix = path[len(BASE):]
    context_scope = ('equinix' if suffix in ('/enterprise', '/operating-model') else
                     (query.get('district') or 'cloud') if suffix == '/district' else 'industry')
    scope = query.get('scope') or context_scope
    if suffix == '': body = scene(query.get('selected', ''))
    elif suffix == '/district': body = district(query.get('district') or 'cloud', query.get('macro', ''))
    elif suffix == '/enterprise': body = enterprise(query.get('detail', ''))
    elif suffix == '/operating-model': body = operating_model(query.get('area') or 'facilities', query.get('macro', ''))
    elif suffix == '/pipeline': body = pipeline(scope)
    else: body = opportunity(query.get('record') or 'cooling', scope)
    import json
    config = json.dumps({'base': BASE, 'scope': scope, 'record': query.get('record') or 'cooling',
                         'view': suffix, 'stages': STAGES, 'districts': {k: v[0] for k, v in DISTRICTS.items()}}, separators=(',', ':'))
    body = (f'<link rel="stylesheet" href="{ASSET_BASE}styles"><div class="experience" id="content">'
            + body + '<p id="preview-status" class="exp-subtle" role="status"></p>' + support() + '</div>'
            + f'<script type="application/json" id="experience-config">{config}</script>'
            + f'<script type="application/json" id="experience-demo">{demo_json()}</script>'
            + f'<script src="{ASSET_BASE}interactions" defer></script>')
    html = page('UK Technology — Flora visual experience', body, headers, 'pipeline' if suffix in ('/pipeline', '/opportunity') else 'industries', path)
    # Only this presentation's primary Pipeline entry inherits the current scope.
    html = html.replace("href='/flora/sales/pipeline'", "href='" + url('/pipeline', scope=scope) + "'", 1)
    return html
