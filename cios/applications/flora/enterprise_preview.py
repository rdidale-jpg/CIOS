"""ET-VIS-2 finite, read-only easyJet presentation experiment.

Not a Twin, taxonomy, source owner, matcher or intelligence store. Research
identity/lifecycle stays with research_intelligence; semantics with ISP-1.
URLs select only fixed presentation views. No private owner is queried.
"""
from dataclasses import dataclass, replace
from datetime import date
from hashlib import sha256
from html import escape as e
import json
from pathlib import Path
from urllib.parse import urlencode

from . import design_system as ds, intelligence_presentation as p
from .research_intelligence import model
from .research_intelligence.source_import import working_restricted

ROUTE = '/enterprises/easyjet/preview'
ASSET_BASE = ROUTE + '/assets/'
ASSETS = Path(__file__).with_name('enterprise_preview_assets')
STREAMS = {'landscape': 'Landscape', 'forces': 'Forces', 'changing': "What's changing?"}
# Transient presentation bindings onto existing activity/capability references.
CAPABILITIES = {
    'fleet-operations': ('Fleet Operations', 'VI-EJ-FLEET', ('AV-CAP-OPS', 'AV-CAP-MRO')),
    'network-planning': ('Network Planning', 'VI-EJ-PLAN', ('AV-CAP-NETWORK',)),
    'customer-service': ('Customer Service', 'VI-EJ-RECOVER', ('AV-CAP-SERVICE',)),
}
FILES = {'styles': ('preview.css', 'text/css; charset=utf-8'),
         'interactions': ('preview.js', 'text/javascript; charset=utf-8'),
         'artwork': ('airline.svg', 'image/svg+xml')}


@dataclass(frozen=True)
class Context:
    stream: str = 'landscape'
    capability: str = 'fleet-operations'


def resolve(query):
    if set(query) - {'stream', 'capability'}:
        raise ValueError('Unsupported preview selector')
    for key, values in query.items():
        if not isinstance(values, list) or len(values) != 1 or not isinstance(values[0], str):
            raise ValueError('Ambiguous preview selector')
    ctx = Context(query.get('stream', ['landscape'])[0], query.get('capability', ['fleet-operations'])[0])
    if ctx.stream not in STREAMS or ctx.capability not in CAPABILITIES:
        raise ValueError('Unavailable preview view')
    return ctx


def url(ctx, **changes):
    ctx = replace(ctx, **changes)
    return ROUTE + '?' + urlencode({'stream': ctx.stream, 'capability': ctx.capability})


def asset(name):
    if name not in FILES:
        raise ValueError('Unavailable preview asset')
    filename, mime = FILES[name]
    path = ASSETS / filename
    if path.is_symlink() or not path.resolve().is_relative_to(ASSETS.resolve()):
        raise ValueError('Unavailable preview asset')
    return path.read_bytes(), mime


def _profile():
    from .research_intelligence.registry import assessment_path
    profile = json.loads(assessment_path('aviation').with_name('Visual-Profile.json').read_text())
    if not isinstance(profile, dict):
        return None
    activities = profile.get('activities')
    if (not isinstance(activities, list) or any(not isinstance(a, dict) or 'id' not in a for a in activities)
            or len({a['id'] for a in activities}) != len(activities)):
        return None
    if profile.get('profile_id') != 'VI-AVIATION-1' or profile.get('domain') != 'aviation' or working_restricted(profile):
        return None
    return profile


def _read_assessment():
    # The existing registered Source owner supplies the fixed repository path.
    # Validate each selected disclosure with model.primary_claim_supported;
    # whole-graph validation would erase unrelated facts on one bad snapshot.
    from .research_intelligence.registry import assessment_path
    return json.loads(assessment_path('aviation').read_text())


def _data():
    try:
        data = _read_assessment()
        if not isinstance(data, dict):
            return None
        if data.get('schema_version') != 1 or data.get('authority') != 'candidate_intelligence':
            return None
        for category in ('sources', 'claims', 'capabilities'):
            rows = data[category]
            if (not isinstance(rows, list) or any(not isinstance(r, dict) or not isinstance(r.get('id'), str) for r in rows)
                    or len({r['id'] for r in rows}) != len(rows)):
                return None
        if (data.get('research_domain') != 'aviation' or data.get('enterprise_twin_id') != 'AV-ENT-001'
                or data.get('industry_twin_id') != 'AV-IND-001' or working_restricted(data)
                or not model.freshness(data)['eligible']):
            return None
        return data
    except (ValueError, OSError, KeyError, TypeError):
        return None


# Narrow editorial projections: no new facts, extended compound statements or
# fabricated original-byte archive. Binding digests fail closed on revision.
# This is render copy, not a Source/claim registry. All provenance is resolved
# from the current existing owner on each request; nothing is persisted here.
DISCLOSURES = {
    'AV-FLEET': ('356 aircraft', 'At 30 September 2025 · easyJet Group', 'Historical fleet snapshot; not today’s count.'),
    'AV-NETWORK': ('1,202 routes', 'Winter / summer 2025 · easyJet network', 'Annualised network definition; not daily flights or route profitability.'),
    'AV-MRO': ('easyJet described the Skywise Core Platform in its S.Fleet Performance + announcement.', '3 November 2023', 'Historical announcement; current supplier workshare and contract terms are not established.'),
    'AV-ICC': ('easyJet announced its generative AI tool Jetstream.', '22 May 2024', 'An announcement does not demonstrate current adoption or realised operating benefits.'),
    'AV-CHAT': ('ChatGPT discovery directs customers to easyJet sites to complete a booking.', '5 October 2026', 'The disclosed channel does not establish additional bookings, revenue or demand.'),
    'AV-WIFI': ('easyJet announced connectivity powered by Starlink from SpaceX.', '29 October 2026', 'Announced service; the retained evidence does not establish fleet-wide live availability.'),
    'AV-RIGHTS': ('CAA passenger-rights guidance addresses refunds, with applicability depending on the flight.', 'UK flight-specific passenger-rights guidance · reviewed 9 November 2026', 'Applicable rights depend on the flight and disruption circumstances.'),
}
# Generated once from the verified baseline's existing claim records. Editing
# or superseding a record cannot inherit the previous editorial projection.
CLAIM_PINS = {'AV-RIGHTS': 'b45b2bb0da10e5dde9d98aa31268adc6a08d04235556920cec481846889a81ca', 'AV-FLEET': 'eaf2e07f0c2d96138d4c967b5eaa466f95577ec0be6c9d8df8307c965d5b0d09', 'AV-NETWORK': '3628d8af41df7654f0fd203b3f32541e5b19cd9ac5315625319c6a50c0348b53', 'AV-ICC': 'c6852692aef0dc22b5d7ad5f802d1ddbea820622d3b39e2ad6e4d79a699e9f26', 'AV-MRO': 'ad471e5993402d553b05bf3c9b2432674e28900154c430760b50ad231888f9d4', 'AV-CHAT': '45651959a6ffeca32ff5d999e8efddde9b3fe10a2f4b2593711b4c1376d14837', 'AV-WIFI': '9fb9e65d98e49a94e27447a1695be8643a7a8af451bd2045b6b9e071bf8ec4d7'}

SOURCE_PINS = {'SRC-AV-AR25': 'e9e0cda88fdcf26749217f8a206a16b9ea7596e212c8cf0f4d2a4ca776a4dea4', 'SRC-AV-RIGHTS': '51ca8da39519cffde724dcea9d6c32ba1fdce43dc4b6e37d6a3141dffc572cf3', 'SRC-AV-ICC': '87b48db6c9115550eb18c6546bb5853c57dddfaa680f495266f5bb8fa10779ba', 'SRC-AV-SFP': '8930077575a41e58d5a25a6f18b96803547d19c164512d6446b97be05364edf5', 'SRC-AV-CHAT26': '369f555f2f4ba80caf70ecb28d866ba52ba0c5dbdd8e7714fa0f5689eb337f9c', 'SRC-AV-WIFI26': '77a417d4dfad9c43864216e88d9d1b1797656b39f8fdde186052b62b5d8493fd'}


def _fingerprint(claim):
    return sha256(json.dumps(claim, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def fact(data, identifier):
    if data is None or working_restricted(data) or identifier not in DISCLOSURES:
        return None
    claim = next((c for c in data['claims'] if c['id'] == identifier), None)
    if (claim is None or working_restricted(claim) or _fingerprint(claim) != CLAIM_PINS.get(identifier)
            or claim.get('asset_id') != ('AV-IND-001' if identifier == 'AV-RIGHTS' else 'AV-ENT-001')
            or (identifier != 'AV-RIGHTS' and claim.get('entity_scope') != 'easyJet Group unless otherwise stated')):
        return None
    try:
        sources = {s['id']: s for s in data['sources']}
        for sid in claim['source_ids']:
            source = sources[sid]
            if (working_restricted(source) or _fingerprint(source) != SOURCE_PINS.get(sid)
                    or source.get('research_domain') != 'aviation'
                    or 'search-index' in source.get('retrieval_extent', '')):
                return None
        if not model.primary_claim_supported(data, claim):
            return None
        statement = p.claim_view(data, claim)
        if statement is None:
            # Original research copy can contain internal Unknowns; project only
            # the separately pinned disclosure, after the same ISP-1 checks.
            clean = dict(claim, statement=DISCLOSURES[identifier][0])
            statement = p.claim_view(data, clean)
        if statement is None:
            return None
        text, timing, caveat = DISCLOSURES[identifier]
        statement = replace(statement, text=text, period=timing, material_caveats=(caveat,))
        return statement if p.eligible(statement) else None
    except (ValueError, OSError, KeyError, TypeError):
        return None


CONTENT = {
 'fleet-operations': {
  'purpose': 'Keep aircraft ready. Deliver the schedule.',
  'intro': 'Fleet Operations connects aircraft readiness, crew coordination and day-of-flight recovery.',
  'economics': 'Aircraft earn through flying, while maintenance, fuel and disruption consume resources. Availability and schedule reliability influence how productive the fleet can be.',
  'steps': ('Prepare aircraft', 'Coordinate crew', 'Deliver & recover'),
  'people': 'Illustrative roles: flight operations, engineering and crew planning. Coordination links aircraft readiness with the flying schedule.',
  'data': 'Illustrative inputs: aircraft condition, maintenance requirements, crew availability and disruption status. ',
  'dependencies': 'Aircraft, airports, air navigation and maintenance are enabling dependencies.',
  'metric': 'AV-FLEET', 'technology': 'AV-MRO',
  'forces': ('Aircraft availability meets the flying schedule', 'Maintenance constraints and disruption can reduce productive flying time. This is an operating mechanism, not a measured easyJet loss or unmet buying need.'),
  'events': ('AV-WIFI', 'AV-ICC'),
  'changing_scope': 'Connectivity is passenger-service context; Jetstream is a historical operations announcement. Neither demonstrates current fleet performance.',
 },
 'network-planning': {
  'purpose': 'Put capacity where it can create value.',
  'intro': 'Network Planning connects destinations, schedule choices and available aircraft capacity.',
  'economics': 'Route choice and flight timing shape the seats available to sell. Demand, fares, seasonality and operating cost influence route contribution; route counts alone do not measure profitability.',
  'steps': ('Assess demand', 'Design the schedule', 'Allocate capacity'),
  'people': 'Illustrative roles: network planners, commercial teams and operations. Planning reconciles demand expectations with aircraft and airport constraints.',
  'data': 'Illustrative inputs: booking patterns, seasonal demand, schedules and capacity.',
  'dependencies': 'Aircraft capacity and airport access constrain feasible schedules.',
  'metric': 'AV-NETWORK', 'technology': None,
  'forces': ('Seasonality changes the value of capacity', 'A route can serve different demand and cost conditions across the year. The retained network count establishes scale, not route-level market share, yield or an available sales opportunity.'),
  'events': ('AV-CHAT',),
  'changing_scope': 'Booking discovery is adjacent commercial-channel context; the announcement does not establish a change in this capability.',
 },
 'customer-service': {
  'purpose': 'Help customers keep moving.',
  'intro': 'Customer Service connects booking support with assistance when a journey changes.',
  'economics': 'Resolution effort, refunds and customer experience interact during disruption. Self-service can change the service mix; this prototype does not quantify savings or retention.',
  'steps': ('Understand the journey', 'Resolve the change', 'Support recovery'),
  'people': 'Illustrative roles: customer service teams, digital service and airport operations. Handoffs matter when a flight or booking changes.',
  'data': 'Illustrative inputs: booking details, flight status and customer contact.',
  'dependencies': 'Digital channels and airport operations support the service journey.',
  'metric': None, 'technology': 'AV-CHAT',
  'forces': ('Disruption has a service consequence', 'Service obligations depend on the flight and circumstances. A sector obligation does not establish a company failing or a new procurement.'),
  'events': ('AV-CHAT',),
  'changing_scope': 'Booking discovery is adjacent commercial-channel context; the announcement does not establish a change in this capability.',
 },
}


def _capability_available(ctx, data=None):
    try:
        data = _data() if data is None else data
        if data is None or working_restricted(data):
            return False
        profile = _profile()
        if profile is None:
            return False
        _, activity_id, refs = CAPABILITIES[ctx.capability]
        activity = next(a for a in profile['activities'] if a['id'] == activity_id)
        capabilities = {c['id']: c for c in data['capabilities']}
        return (not working_restricted(activity) and set(refs).issubset(activity['resource_ids'])
                and all(ref in capabilities and not working_restricted(capabilities[ref]) for ref in refs))
    except (KeyError, StopIteration, ValueError, OSError, TypeError):
        return False


def main_content(ctx, data):
    title = CAPABILITIES[ctx.capability][0]
    row = CONTENT[ctx.capability]
    body = '<p class="eyebrow">easyJet · '+e(STREAMS[ctx.stream])+'</p>'
    body += '<h1 id="main-title" tabindex="-1">'+e(title)+'</h1>'
    if not _capability_available(ctx, data):
        return body + '<p class="lead">This preview subject is unavailable.</p>'
    body += '<p class="lead">'+e(row['purpose'])+'</p>'
    if ctx.stream == 'landscape':
        body += '<p class="summary">'+e(row['intro'])+'</p>'
        metric = fact(data, row['metric']) if row['metric'] else None
        if metric:
            body += '<div class="anchor-fact"><span class="eyebrow">Reported scale</span><strong>'+e(metric.text)+'</strong><span>'+e(metric.period)+'</span><p>'+e(metric.material_caveats[0])+'</p></div>'
        body += '<section class="economics"><span class="kind">Conceptual operating model</span><h2>How it creates value</h2><p>'+e(row['economics'])+'</p></section>'
        body += '<ol class="steps" aria-label="Illustrative operating steps">'+''.join('<li>'+e(step)+'</li>' for step in row['steps'])+'</ol>'
        body += '<div class="operating-detail"><section><h2>People &amp; process</h2><p>'+e(row['people'])+'</p></section><section><h2>Data &amp; technology</h2><p>'+e(row['data'])+'</p></section></div>'
        technology = fact(data, row['technology']) if row['technology'] else None
        if technology:
            body += '<section class="disclosure"><h2>Disclosed technology</h2>'+p.render(technology)+'</section>'
        body += '<section class="dependency"><h2>Partners &amp; dependencies</h2><p>'+e(row['dependencies'])+'</p></section><p class="boundary">The operating structure is conceptual. It does not identify easyJet’s organisation, system connections or supplier contracts.</p>'
    elif ctx.stream == 'forces':
        body += '<section class="force"><span class="kind">Conceptual operating mechanism</span><h2>'+e(row['forces'][0])+'</h2><p>'+e(row['forces'][1])+'</p></section>'
        metric = fact(data, row['metric']) if row['metric'] else None
        if metric:
            body += '<section class="disclosure"><h2>The scale in context</h2>'+p.render(metric)+'</section>'
        if ctx.capability == 'customer-service':
            rights = fact(data, 'AV-RIGHTS')
            if rights: body += p.render(rights)
        body += '<p class="boundary">Operating pressures describe mechanisms; they do not establish customer demand or buying intent.</p>'
    else:
        body += '<p class="summary">Dated company announcements, in context.</p>'
        events = [item for key in row['events'] if (item := fact(data, key))]
        for item in events:
            body += '<section class="change"><span class="change-date">'+e(item.period)+'</span>'+p.render(item, compact=True)+'</section>'
        if not events:
            body += '<p class="boundary">No dated disclosure is available in this bounded preview.</p>'
        body += '<p class="boundary">'+e(row['changing_scope'])+'</p>'
    return body


def render(query, headers=None):
    ctx = resolve(query)
    data = _data()
    from .access import is_cios_owner
    body = '<header id="top" data-region="top"><a class="skip" href="#main-title">Skip to intelligence</a><div class="global">'
    body += ds.header(headers=headers or {}, compact=True, embedded=True, research_tools=is_cios_owner(headers or {}))
    body += '<span class="preview-mark">Enterprise Twin · Preview</span></div><div class="context"><nav aria-label="Enterprise context"><a href="/industries/aviation">Aviation</a><span aria-hidden="true">/</span><strong>easyJet</strong></nav><nav class="stream-switcher" aria-label="Insight streams">'
    for key, label in STREAMS.items():
        body += '<a data-preview-nav="true" href="'+e(url(ctx, stream=key), quote=True)+'"'+(' aria-current="page"' if key == ctx.stream else '')+'>'+e(label)+'</a>'
    body += '</nav></div></header><aside id="left" data-region="left" aria-label="Airline operating system"><details class="scene-control" open><summary>Explore the operating system</summary><div class="operating-system"><p class="left-heading">From possibility to flight</p><div class="airline-scene"><img src="'+ASSET_BASE+'artwork" alt="Illustrative airline landscape: route planning, an airport terminal, aircraft and a maintenance hangar. Not actual easyJet premises or a systems topology." width="720" height="1000"><nav aria-label="Operating capabilities">'
    for key, (label, _, _) in CAPABILITIES.items():
        body += '<a id="cap-'+key+'" data-preview-nav="true" class="capability '+key+'" href="'+e(url(ctx, capability=key), quote=True)+'"'+(' aria-current="true"' if ctx.capability == key else '')+'>'+e(label)+'</a>'
    body += '</nav></div><p class="left-caption">Capabilities support the journey.</p><ol class="value-flow" aria-label="Illustrative value-stream activities"><li>Plan</li><li>Sell</li><li>Fly</li><li>Care</li></ol><p class="concept-note">Conceptual value flow · not an organisation chart</p></div></details></aside>'
    with p.editorial_view():
        main = main_content(ctx, data)
    body += '<main id="visual-content" data-region="main"><div id="preview-main" class="workspace">'+main+'</div><p id="preview-status" class="sr-only" role="status" aria-live="polite"></p></main>'
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+e(CAPABILITIES[ctx.capability][0])+' · easyJet · FLORA Preview</title>'+ds.head()+'<link rel="stylesheet" href="/visual-streams/assets/panel-styles"><link rel="stylesheet" href="'+ASSET_BASE+'styles"><script defer src="'+ASSET_BASE+'interactions"></script></head><body class="vp-page et-preview" data-stream="'+ctx.stream+'" data-capability="'+ctx.capability+'">'+body+'</body></html>'
