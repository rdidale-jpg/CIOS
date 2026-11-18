"""Root and framework compositions over the existing FLORA read projections."""
from html import escape

from . import intelligence_presentation as p
from . import leadership_agenda as agenda
from . import reading_views as reading
from . import visual_streams as v

UK_DIMENSIONS = {
    "political": "Political", "economic": "Economic", "social": "Social",
    "technological": "Technological", "legal": "Legal", "environmental": "Environmental",
}
BANKING_FORCES = {
    "rivalry": ("Rivalry", "funding-economics", "Funding & lending",
                "Competition for deposits can increase funding costs. Banks with different deposit mixes and wholesale funding needs can face different costs.",
                "Comparable pricing, deposit mix and balance movements are needed to distinguish a pricing response from changes in customer balances."),
    "buyer-power": ("Buyer power", "funding-economics", "Customers & businesses",
                    "Customer choice can discipline pricing. A household moving one product and a business moving linked payments and borrowing face different switching effort.",
                    "Comparable switching, multi-banking and migration costs by cohort remain unverified."),
    "supplier-power": ("Supplier power", "provider-oversight", "Technology & infrastructure",
                       "Shared technology providers may have more bargaining power when switching requires data migration, redesign and continuity testing.",
                       "Designation establishes neither supplier bargaining power nor a contract or workload at an individual bank."),
    "new-entrants": ("Threat of new entrants", "reporting-change", "Customers & businesses",
                     "Controls and operating resilience can create fixed costs. An entrant serving one product may face different economics from a multi-product bank.",
                     "Entry costs, authorisation scope and service coverage need comparable evidence."),
    "substitutes": ("Threat of substitutes", "", "Payments & settlement",
                    "A payment specialist can substitute for part of an account journey while relying on other institutions for settlement or funding.",
                    "Usage data and exact scheme and operator roles are needed to establish actual substitution."),
}
_BANKING_CONTEXT = {
    "rivalry": "Economic · funding costs and the rate environment.",
    "buyer-power": "Economic · the price and effort of moving accounts or related services.",
    "supplier-power": "Technological · portability and recovery affect the ability to switch providers.",
    "new-entrants": "Legal · the scope of reporting and resilience obligations can affect entry costs.",
    "substitutes": "Technological · channels and infrastructure affect which parts of a payment journey can move.",
}
_STAGE = {
    "Funding & lending": "funding", "Customers & businesses": "customers",
    "Technology & infrastructure": "providers", "Payments & settlement": "payments",
}
STYLE = """<style>
.experience-path{margin:16px 0 24px;padding-inline-start:22px;border-inline-start:2px solid #937644}
.experience-path li{margin:10px 0;padding-inline-start:4px}
.experience-nav{display:flex;flex-wrap:wrap;gap:4px 14px;margin-block:12px}
.experience-nav a{display:inline-flex;align-items:center;min-height:44px}
.experience-nav a[aria-current]{font-weight:bold;text-decoration-thickness:2px}
.experience-abilities{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,14rem),1fr));gap:10px}
.experience-abilities>div{padding:10px 14px;background:#eee8d7;border-inline-start:2px solid #937644}
.experience-abilities dd{margin:4px 0}.experience-abilities dt{font-weight:bold}
</style>"""


def _facts(items):
    return "".join(p.render(item) for item in items)


def _interpret(title, items, text, gap, ctx):
    if ctx.reading == "facts":
        return _facts(items) or f'<p>{escape(gap)}</p>'
    if items:
        return reading.interpretation(title, items, text, gap, heading="h2")
    return f'<p>No eligible premise for this interpretation. {escape(gap)}</p>'


def _navigation(ctx, items, label, active):
    return f'<nav aria-label="{escape(label)}" class="experience-nav">' + "".join(
        f'<a href="{escape(v.url(ctx, detail=key) + "#visual-content", quote=True)}"'
        + (' aria-current="page"' if key == active else '') + f'>{escape(name)}</a>'
        for key, name in items
    ) + '</nav>'


def uk_forces(ctx, data):
    key = ctx.detail or "economic"
    label = UK_DIMENSIONS[key]
    fact = v.force_view(ctx, key, data)
    items = (fact,) if fact and p.eligible(fact) else ()
    mechanism, gap, _ = v.FORCE_POLICY[key]
    close = escape(v.url(ctx, detail="") + "#visual-content", quote=True)
    body = (
        '<h1>The UK’s economic context</h1>'
        + _navigation(ctx, UK_DIMENSIONS.items(), "PESTLE dimensions", key)
    )
    if ctx.detail and items:
        body += ('<section class="focus" id="insight" tabindex="-1" aria-labelledby="insight-title">'
                 f'<a class="close" href="{close}" aria-label="Close {label} conditions">×</a>')
    body += (
        f'<h2 id="insight-title">{label} conditions</h2><ol class="experience-path"><li><strong>UK condition</strong>'
        + (_facts(items) or '<p>The national evidence for this dimension is unavailable.</p>')
        + '</li><li><strong>Industry context</strong> · Follow the relevant economic channel in '
          '<a href="/industries/banking?stream=forces">Banking</a> or <a href="/industries/aviation?lens=pestle">Aviation</a>. '
          'These links give sector context.</li><li><strong>Enterprise applicability</strong> · Needs evidence about the exact entity and activity.</li></ol>'
        + (_interpret("Sector mechanism", items, mechanism, gap, ctx) if ctx.reading == "insight" else '')
    )
    if ctx.detail and items:
        body += '</section>'
    return body + '<p><a href="/industries/banking?stream=forces">Explore these forces in Banking</a></p>'


def banking_forces(ctx, data, issues):
    key = ctx.detail or "rivalry"
    title, anchor, stage, mechanism, gap = BANKING_FORCES[key]
    items = next((row.facts[:1] for row in issues if row.key == anchor), ())
    if key == "substitutes":
        fact = v.force_view(ctx, "UK-VALUE", data)
        items = (fact,) if fact and p.eligible(fact) else ()
    href = escape(v.url(ctx, stream="landscape", detail=_STAGE[stage]) + "#visual-content", quote=True)
    body = (
        '<h2>Five Forces</h2>'
        + _navigation(ctx, ((key, row[0]) for key, row in BANKING_FORCES.items()), "Five Forces", key)
        + f'<h3 id="insight" tabindex="-1">{title}</h3><ol class="experience-path"><li><strong>Industry stage</strong> · <a href="{href}">{stage}</a></li>'
        + f'<li><strong>Contextual PESTLE</strong> · {escape(_BANKING_CONTEXT[key])} '
          '<a href="/?stream=forces">See national conditions</a>.</li>'
        + f'<li><strong>Evidence needed</strong> · {escape(gap)}</li></ol>'
        + _interpret("Competitive mechanism", items, mechanism, gap, ctx)
    )
    return body


def _capability_root(ctx, title, outcome, activities, abilities, facts, mechanism, gap):
    targets = {name: f"ability-{index}" for index, (name, _) in enumerate(abilities)}
    sequence = '<ol class="reading-sequence">' + "".join(
        f'<li><strong>{escape(activity)}</strong>Uses '
        + ", ".join(f'<a href="#{targets[name]}">{escape(name)}</a>' for name in names)
        + '</li>' for activity, names in activities
    ) + '</ol>'
    return (
        f'<h1>{escape(title)}</h1><p class="reading-context">Conceptual · stakeholder value stream</p>'
        f'<h2>{escape(outcome)}</h2>'
        + sequence
        + '<h2>Durable capabilities</h2><dl class="experience-abilities">'
        + "".join(f'<div id="{targets[label]}" tabindex="-1"><dt>{escape(label)}</dt><dd>{escape(detail)}</dd></div>'
                  for label, detail in abilities)
        + '</dl><h2>Roles, enablers and measures</h2>'
        + _interpret("Operating mechanism", facts, mechanism, gap, ctx)
        + (f'<p>{escape(gap)}</p>' if facts and ctx.reading == "facts" else '')
    )


def lloyds_inside(ctx, data):
    controls = agenda._claims(data, ("LBG-ENVOY-CONTROLS",))
    return _capability_root(
        ctx, "How Lloyds operates", "Resolve a customer request",
        (("Receive", ("Service handling",)), ("Resolve", ("Service handling", "Technology governance")),
         ("Review", ("Technology governance",))),
        (("Service handling", "Customer operations · receive and resolve"),
         ("Technology governance", "Technology & data · resolve and review")),
        controls, "Controls embedded in operating tools can make monitoring repeatable. The Group’s existing platform disclosure gives a scoped example.",
        "Accountable teams, capability performance and supplier contracts remain unverified for this example.",
    ) + f'<p><a href="{escape(v.url(ctx, detail="technology") + "#visual-content", quote=True)}">Explore Technology &amp; data</a></p>'


def enterprise_forces(ctx, title, observed, response, mechanism, gap, *, dependencies=None):
    return (
        f'<h1>{escape(title)}</h1><ol class="experience-path">'
        '<li><strong>Observed condition</strong>' + (_facts(observed) or '<p>Scoped observation unavailable.</p>') + '</li>'
        '<li><strong>Disclosed response</strong>' + (_facts(response) or '<p>No linked response is verified for this condition.</p>') + '</li>'
        f'<li><strong>Evidence needed</strong><p>{escape(gap)}</p></li></ol>'
        + (_interpret("Conditional consequence", (*observed, *response) if dependencies is None else dependencies,
                      mechanism, gap, ctx) if ctx.reading == "insight" else '')
    )


def easyjet_root(ctx, data):
    from . import easyjet_capabilities as easyjet

    fleet = tuple(item for key in ("AV-FLEET",) if (item := easyjet.fact(data, key)))
    network = tuple(item for key in ("AV-NETWORK",) if (item := easyjet.fact(data, key)))
    if ctx.stream == "inside":
        return _capability_root(
            ctx, "How easyJet operates", "Deliver scheduled flying",
            (("Allocate aircraft", ("Fleet management",)), ("Dispatch flights", ("Fleet management", "Operations control")),
             ("Recover the schedule", ("Operations control", "Customer service"))),
            (("Fleet management", "Fleet Operations · allocation and dispatch"),
             ("Operations control", "Dispatch and recovery"), ("Customer service", "Customer assistance during recovery")),
            fleet, "Aircraft availability bounds the flying schedule. Reserve aircraft can improve recovery at the cost of lower utilisation.",
            "Fleet scale provides Group context. Accountable roles, suppliers and matched utilisation or recovery performance remain unverified.",
        )
    if ctx.stream == "forces":
        return enterprise_forces(
            ctx, "Conditions affecting easyJet", fleet, (),
            "A loss of aircraft availability can constrain scheduled flying. The consequences depend on reserve capacity, network and timing.",
            "Test reserve capacity, maintenance and recovery measures for the same operations. The fleet count does not establish a disruption or how management responded.",
        )
    return (
        '<h1>easyJet’s business and network</h1>'
        '<p class="reading-context">Conceptual · short-haul airline economics</p>'
        '<p>Routes connect customers to destinations. Fleet capacity determines how much flying can be scheduled.</p>'
        + _facts((*fleet, *network))
        + (_interpret("Capacity and commercial reach", (*fleet, *network) if fleet and network else (),
                      "Fleet and network breadth frame capacity. Frequency, utilisation and demand determine how that capacity translates into earnings.",
                      "Comparable business-line financials, yields and costs remain outside this projection.", ctx)
           if ctx.reading == "insight" else '<p>Comparable business-line financials, yields and costs remain outside this projection.</p>')
    )
