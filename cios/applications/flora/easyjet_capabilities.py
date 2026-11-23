"""easyJet view content bound to the existing Aviation research owner."""
from dataclasses import replace
from hashlib import sha256
from html import escape
import json

from . import intelligence_presentation as p
from .research_intelligence import model
from .research_intelligence.source_import import working_restricted


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


DISCLOSURES = {
    'AV-FLEET': ('356 aircraft', 'At 30 September 2025 · easyJet Group', 'Historical fleet snapshot; not today’s count.'),
    'AV-NETWORK': ('1,202 routes', 'Winter / summer 2025 · easyJet network', 'Annualised network definition; not daily flights or route profitability.'),
    'AV-MRO': ('easyJet described the Skywise Core Platform in its S.Fleet Performance + announcement.', '3 November 2023', 'Historical announcement; current supplier workshare and contract terms are not established.'),
    'AV-CHAT': ('ChatGPT discovery directs customers to easyJet sites to complete a booking.', '5 October 2026', 'The disclosed channel does not establish additional bookings, revenue or demand.'),
}
# Generated once from the verified baseline's existing claim records. Editing
# or superseding a record cannot inherit the previous editorial projection.
CLAIM_PINS = {'AV-FLEET': 'eaf2e07f0c2d96138d4c967b5eaa466f95577ec0be6c9d8df8307c965d5b0d09', 'AV-NETWORK': '3628d8af41df7654f0fd203b3f32541e5b19cd9ac5315625319c6a50c0348b53', 'AV-MRO': 'ad471e5993402d553b05bf3c9b2432674e28900154c430760b50ad231888f9d4', 'AV-CHAT': '45651959a6ffeca32ff5d999e8efddde9b3fe10a2f4b2593711b4c1376d14837'}

SOURCE_PINS = {'SRC-AV-AR25': 'e9e0cda88fdcf26749217f8a206a16b9ea7596e212c8cf0f4d2a4ca776a4dea4', 'SRC-AV-SFP': '8930077575a41e58d5a25a6f18b96803547d19c164512d6446b97be05364edf5', 'SRC-AV-CHAT26': '369f555f2f4ba80caf70ecb28d866ba52ba0c5dbdd8e7714fa0f5689eb337f9c'}


def _fingerprint(claim):
    return sha256(json.dumps(claim, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def fact(data, identifier):
    if data is None or working_restricted(data) or identifier not in DISCLOSURES:
        return None
    claim = next((c for c in data['claims'] if c['id'] == identifier), None)
    if (claim is None or working_restricted(claim) or _fingerprint(claim) != CLAIM_PINS.get(identifier)
            or claim.get('asset_id') != 'AV-ENT-001'
            or claim.get('entity_scope') != 'easyJet Group unless otherwise stated'):
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


CAPABILITIES = {
    "fleet-operations": "Fleet Operations",
    "network-planning": "Network Planning",
    "customer-service": "Customer Service",
}
POSITIONS = {
    "fleet-operations": (43, 75),
    "network-planning": (52, 17),
    "customer-service": (68, 36),
}
FACTS = {
    "fleet-operations": ("AV-FLEET", "AV-MRO"),
    "network-planning": ("AV-NETWORK",),
    "customer-service": ("AV-CHAT",),
}
ACTIVITIES = {
    "fleet-operations": (
        ("Prepare", "Assess aircraft and crew readiness"),
        ("Operate", "Coordinate the flying schedule"),
        ("Recover", "Replan when an aircraft is unavailable"),
    ),
    "network-planning": (
        ("Assess", "Compare demand and seasonality"),
        ("Schedule", "Fit frequencies to capacity and airport access"),
        ("Allocate", "Commit aircraft time across the network"),
    ),
    "customer-service": (
        ("Understand", "Read booking and flight status"),
        ("Respond", "Coordinate digital or airport assistance"),
        ("Resolve", "Support the customer’s next step"),
    ),
}
ENABLERS = {
    "fleet-operations": "Engineering and crew coordination · aircraft condition · maintenance and airport access",
    "network-planning": "Network and commercial planning · demand and schedule information · aircraft and airport capacity",
    "customer-service": "Digital, airport and service teams · booking and flight information · service channels",
}
MECHANISMS = {
    "fleet-operations": (
        "Aircraft availability can protect productive flying time. Recovery buffers can improve resilience while holding back capacity from the schedule.",
        "A fleet snapshot and a technology announcement do not measure utilisation, realised savings or current supplier commitments.",
        (("Availability", "Aircraft and crew ready to fly"), ("Utilisation", "Productive use of aircraft time"),
         ("Resilience", "Capacity to absorb disruption")),
    ),
    "network-planning": (
        "Allocating scarce aircraft time changes the seats available to sell. Timing, demand and delivery costs affect whether more capacity adds value.",
        "A route count provides network scale. It does not measure flight frequency, route contribution or demand at specific times.",
        (("Capacity decision", "Aircraft time and airport access"), ("Revenue exposure", "Seats, timing and demand"),
         ("Cost exposure", "Utilisation and operating expense")),
    ),
    "customer-service": (
        "Booking discovery and disruption support serve different stages of the journey. Clear handoffs can shape the effort needed to resolve a disruption.",
        "The booking announcement establishes the channel handoff. Resolution performance, customer outcomes and cost effects remain unmeasured.",
        (("Channel", "Digital discovery and booking"), ("Handoff", "Use booking and flight information"),
         ("Service effort", "Resolve changes across channels")),
    ),
}

STYLE = """<style>
.et-picture{margin:0;position:relative}
.et-picture img{width:100%;height:auto;display:block;aspect-ratio:2/3;object-fit:cover}
.et-picture .subject{position:absolute;left:var(--x);top:var(--y);transform:translate(-50%,-50%);white-space:normal;text-align:center;min-width:7.5em}
.et-selection{padding:12px 16px}
.et-selection a{display:flex;align-items:center;min-height:44px}
.et-selection a[aria-current]{font-weight:700}
.et-facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,15rem),1fr));gap:12px 24px;margin:14px 0}
.et-facts article{border-top:2px solid #ae9158;padding-top:8px}
.et-enablers{border-inline-start:3px solid #ae9158;padding-inline-start:14px;margin:16px 0}
@media(max-width:999px){.et-picture{max-width:290px;margin-inline:auto}}
</style>"""


def left(ctx):
    from . import visual_streams as v

    def choices(overlay):
        result = []
        for key, title in CAPABILITIES.items():
            x, y = POSITIONS[key]
            classes = f' class="subject" style="--x:{x}%;--y:{y}%"' if overlay else ""
            active = ' aria-current="page"' if key == ctx.detail else ""
            url = escape(v.url(ctx, detail=key) + "#visual-content", quote=True)
            result.append(f'<a href="{url}"{classes}{active}>{title}</a>')
        return "".join(result)

    scene = (
        f'<figure class="et-picture"><img src="{v.ASSET_BASE}{v.EASYJET_ART}" width="768" height="1152" '
        'alt="Conceptual airport with aircraft maintenance, an apron and a passenger terminal">'
        '<nav aria-label="Capabilities in the illustration">' + choices(True) + '</nav></figure>'
        '<nav class="et-selection" aria-label="Select an operating capability">' + choices(False) + '</nav>'
    )
    return (
        '<aside id="left" data-region="left" aria-label="Visual exploration"><div class="wide-scene">' + scene
        + '</div><details class="compact-scene"><summary>Explore the operating system</summary>'
        + scene + '</details></aside>'
    )


PERSPECTIVE = {
    "landscape": {
        "fleet-operations": "Fleet availability bounds the flying schedule an airline can offer; mix and utilisation determine how that equipment translates into capacity.",
        "network-planning": "Network breadth describes where the airline participates. Frequency and the timing of available seats shape its commercial reach.",
        "customer-service": "A discovery channel can broaden where customers find flights, while a separate booking handoff determines where transactions are completed.",
    },
    "forces": {
        "fleet-operations": "Maintenance and disruption can remove aircraft from the schedule. Recovery options depend on how much reserve capacity is available.",
        "network-planning": "Seasonal demand, airport access and aircraft supply can shift the trade-off between higher frequencies and opening another route.",
        "customer-service": "Disruption can concentrate service demand. Channel and airport handoffs affect how much effort is needed to resolve changes.",
    },
}


def main(ctx):
    from . import reading_views as reading

    data = _data()
    from .enterprise_economics import AIRLINE_STAGES, aviation
    if ctx.stream == 'landscape' and ctx.detail in AIRLINE_STAGES:
        return aviation(ctx, data)
    if not ctx.detail:
        from .experience_composition import easyjet_root
        return easyjet_root(ctx, data)
    identifiers = FACTS[ctx.detail]
    if ctx.stream == "landscape":
        identifiers = identifiers[:1]
    elif ctx.stream == "forces":
        identifiers = identifiers[-1:]
    facts = tuple(item for key in identifiers if (item := fact(data, key)))
    name = CAPABILITIES[ctx.detail]
    mechanism, caveat, drivers = MECHANISMS[ctx.detail]
    scope = f'<p class="eyebrow">easyJet · {ctx.stream.title()}</p>'
    body = scope + f'<h1>{name}</h1>'
    if ctx.stream == "inside":
        body += (
            '<p class="reading-context">Conceptual · operating activities</p>'
            + reading.sequence(ACTIVITIES[ctx.detail])
            + '<p class="et-enablers"><strong>Illustrative enablers</strong><br>' + escape(ENABLERS[ctx.detail]) + '</p>'
        )
    elif ctx.stream == "landscape":
        body += '<p class="reading-context">easyJet Group · capability context</p>'
    else:
        body += '<p class="reading-context">Published context · capability exposure and outcomes remain unmeasured</p>'
    if facts:
        body += '<div class="et-facts">' + "".join(p.render(item) for item in facts) + '</div>'
    else:
        body += '<p>No eligible disclosures for this selection.</p>'
    if facts:
        body += reading.interpretation("Operating implications", facts, PERSPECTIVE.get(ctx.stream, {}).get(ctx.detail, mechanism), caveat, heading="h2")
        if facts and ctx.stream == "inside":
            if ctx.detail == "network-planning":
                capacity, *tradeoffs = drivers
                body += ('<section class="reading-economy"><h2>Scheduling trade-off</h2><p><strong>'
                         + escape(capacity[0]) + '</strong> · ' + escape(capacity[1]) + '</p>'
                         '<dl class="reading-drivers">' + ''.join(
                             '<div><dt>' + escape(title) + '</dt><dd>' + escape(detail) + '</dd></div>'
                             for title, detail in tradeoffs
                         ) + '</dl></section>')
            elif ctx.detail == "fleet-operations":
                body += reading.sequence(drivers)
            else:
                body += reading.flow(drivers)
    return body
