"""Bounded reading views over the existing FLORA presentation and source owners."""
from dataclasses import replace
from decimal import Decimal
from html import escape as e

from . import intelligence_presentation as p
from . import leadership_agenda as agenda
from . import visual_streams as v

STYLE = """<style>
.reading-mode{display:flex;flex-wrap:wrap;gap:4px;margin:0 0 22px;padding:3px;width:fit-content;
  border:1px solid var(--line);border-radius:24px;background:#f4efdf}
.reading-mode a{display:inline-flex;align-items:center;min-height:44px;padding:4px 14px;
  border-radius:21px;text-decoration:none;line-height:1.25}
.reading-mode a[aria-current]{background:#244435;color:white;font-weight:700}
.reading-mode a:focus-visible{outline:2px solid currentColor;outline-offset:2px}
.reading-flow{display:flex;flex-wrap:wrap;gap:12px;list-style:none;padding:0;margin:24px 0}
.reading-flow li{flex:1 1 9rem;border-top:2px solid #ae9158;padding:12px 8px;background:#eee8d6}
.reading-flow strong,.reading-flow span{display:block}.reading-flow span{font-size:.85em}
.vp-page #visual-content:focus-visible,.vp-page .focus:focus-visible{outline:none}
.vp-page #visual-content:focus-visible .reading-mode,.vp-page .focus:focus-visible h1{box-shadow:inset 3px 0 #7055a0;padding-inline-start:8px}
.reading-sequence{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;list-style:none;padding:0;margin:24px 0}
.reading-sequence li{position:relative;border-top:2px solid #9a8044;padding-block:12px}
.reading-sequence li:not(:last-child)::after{content:"";position:absolute;right:-15px;top:-6px;width:8px;height:8px;border:solid #9a8044;border-width:2px 2px 0 0;transform:rotate(45deg)}
.reading-sequence strong,.reading-sequence span{display:block}
.reading-roles,.reading-drivers,.reading-links ul{display:flex;flex-wrap:wrap;gap:12px 24px}
.reading-roles>div,.reading-drivers>div{flex:1 1 12rem}
.reading-roles dt,.reading-drivers dt{font-weight:700}.reading-roles dd,.reading-drivers dd{margin:4px 0 0}
.reading-economy{margin:24px 0;padding:clamp(12px,3vw,24px);background:#ede8d8;border-inline-start:3px solid #ae9158}
.reading-economy h2,.reading-capability h2{font-size:1.25rem;margin:0 0 8px}
.reading-capability{border-top:1px solid var(--line);padding-top:14px;margin-top:20px}
.reading-links ul{padding:0;list-style:none;margin:18px 0 0}
.reading-links a{display:inline-flex;align-items:center;min-height:44px}
@media(max-width:600px){.reading-sequence{grid-template-columns:1fr;gap:10px}.reading-sequence li:not(:last-child)::after{display:none}}
.reading-payment-flows{margin:16px 0}
.reading-payment-flows div{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,12rem),1fr));gap:4px 14px;padding:12px;border-block-start:2px solid #a68a54}
.reading-payment-flows div+div{border-block-start-style:dashed}
.reading-payment-flows dt{font-weight:bold}.reading-payment-flows dd{margin:0}
.reading-context{font-size:.85em;color:var(--muted)}
.reading-pulse{border-inline-start:3px solid #ae9158;padding-inline-start:16px;margin:24px 0}
@media(forced-colors:active){.reading-mode a[aria-current]{background:Highlight;color:HighlightText}}
</style>"""


def selector(ctx):
    return '<nav class="reading-mode" aria-label="Reading mode">' + "".join(
        f'<a href="{e(v.url(ctx, reading=mode) + "#visual-content", quote=True)}"'
        f'{" aria-current=page" if ctx.reading == mode else ""}>{label}</a>'
        for mode, label in (("facts", "Facts"), ("insight", "FLORA Insight"))
    ) + "</nav>"


def flow(stages):
    return '<ol class="reading-flow">' + "".join(
        f'<li><strong>{e(title)}</strong><span>{e(description)}</span></li>'
        for title, description in stages
    ) + '</ol>'


def banking_links(*, include_payments=True):
    return (
        '<nav class="reading-links" aria-label="Banking subjects"><ul>'
        + ('<li><a href="/industries/banking?stream=landscape&amp;detail=payments#visual-content">Payments &amp; settlement</a></li>' if include_payments else '')
        +
        '<li><a href="/industries/banking?stream=landscape&amp;selected=nationwide#visual-content">Nationwide Group earnings</a></li>'
        '<li><a href="/enterprises/lloyds?stream=inside&amp;detail=technology#visual-content">Lloyds technology &amp; data</a></li>'
        '</ul></nav>'
    )


def payments(ctx, data):
    close = e(v.url(ctx, detail="") + "#visual-content", quote=True)
    body = (
        '<section class="focus" id="insight" tabindex="-1" aria-labelledby="insight-title">'
        f'<a class="close close-insight" href="{close}" aria-label="Close Payments and settlement">×</a>'
        '<p class="eyebrow">Banking · Landscape</p><h1 id="insight-title">Payments &amp; settlement</h1>'
    )
    body += '<p class="reading-context">Conceptual · UK payment roles</p>'
    body += sequence((
        ("Initiate", "A household or business authorises a payment and its provider checks and routes the instruction."),
        ("Clear", "Participants exchange and validate instructions, establishing obligations that may be netted."),
        ("Settle", "Transfer of settlement funds discharges the obligations. The recipient’s provider makes funds available under the applicable arrangement."),
    ))
    body += (
        '<p class="reading-context">Arrows show the order of activities. Actual access and settlement arrangements vary by system.</p>'
        '<dl class="reading-roles"><div><dt>Scheme</dt><dd>Sets the rules for participation and processing.</dd></div>'
        '<div><dt>Operator</dt><dd>Provides and runs the system service.</dd></div>'
        '<div><dt>Network</dt><dd>Carries messages between participants.</dd></div></dl>'
    )
    model = v.force_view(ctx, "UK-VALUE", data)
    if not model or not p.eligible(model):
        return body + banking_links(include_payments=False) + '</section>'
    p.note_editorial_sources(model.sources)
    body += (
        '<section class="reading-economy"><h2>One payment, two economic flows</h2>'
        '<dl class="reading-payment-flows"><div><dt>Customer principal</dt><dd>Money moves to the recipient. '
        'Settlement discharges obligations between participants, which can represent many payments.</dd></div>'
        '<div><dt>Service income</dt><dd>Participants or customers may pay service charges under the applicable arrangements. Operators incur costs to run and maintain the service.</dd></div></dl></section>'
        '<h2>What changes the economics?</h2><dl class="reading-drivers">'
        '<div><dt>Service mix</dt><dd>The same volume can produce different income under different pricing and access arrangements.</dd></div>'
        '<div><dt>Continuity</dt><dd>Capacity, monitoring and recovery can incur costs even when traffic is steady.</dd></div></dl>'
        '<p>Payment volume and principal alone cannot establish operator revenue, actual fees or bank-level dependencies.</p>'
    )
    return body + banking_links(include_payments=False) + '</section>'


def sequence(stages):
    return '<ol class="reading-sequence">' + "".join(
        f'<li><strong>{e(title)}</strong><span>{e(description)}</span></li>' for title, description in stages
    ) + '</ol>'


def lloyds_capability(data, *, insight):
    controls = agenda._claims(data, ("LBG-ENVOY-CONTROLS",))
    if not controls:
        return unavailable("Technology & data") if insight else ""
    collaboration = agenda._claims(data, ("LBG-ENVOY-GOOGLE",))
    if not insight:
        return (
            '<section class="reading-capability"><h2>Group capability</h2>'
            '<p class="reading-context">Conceptual · Group capability operating sequence</p>'
            + sequence((("Develop", "Build platform tools"), ("Operate", "Use platform controls"),
                        ("Monitor", "Review activity"))) + '</section>'
        )
    body = interpretation(
        "Technology & data", controls + collaboration,
        "Platform controls can make monitoring part of the operating process as AI use scales.",
        "Deployment breadth, control effectiveness, net benefits and the legal contracting entity remain unverified.",
    )
    body += (
        '<section class="reading-capability"><h2>Where the platform supports the capability</h2>'
        '<dl class="reading-drivers"><div><dt>Capability</dt><dd>Operate and monitor AI use.</dd></div>'
        '<div><dt>Enabler</dt><dd>Lloyds Banking Group describes Envoy and its controls.</dd></div>'
    )
    if collaboration:
        body += '<div><dt>Disclosed collaboration</dt><dd>Google Cloud at brand scope. Any Google Cloud EMEA Limited contract or Lloyds Bank plc workload remains unverified.</dd></div>'
    return body + '</dl></section>'


def unavailable(title):
    return f'<h1>{e(title)}</h1><p>No supported FLORA Insight for this selection.</p>'


def interpretation(title, facts, text, caveat, *, heading="h1"):
    if not facts or not all(p.eligible(fact) for fact in facts):
        return f'<{heading}>{e(title)}</{heading}><p>No supported FLORA Insight for this selection.</p>'
    item = p.Statement(
        text, "insight", facts[0].scope, facts[0].period,
        tuple(dict.fromkeys(source for fact in facts for source in fact.sources)),
        "derived_from_inputs", "derived_view_not_canonical",
        reasoning="Interpretation of the eligible disclosures in this selection.",
        dependencies=tuple(fact.text for fact in facts),
        dependency_types=tuple(fact.semantic_type for fact in facts),
        counter_evidence=(caveat,), material_caveats=(caveat,),
    )
    return f'<{heading}>{e(title)}</{heading}>' + (p.render(item) or '<p>No supported FLORA Insight for this selection.</p>')


def provider_pulse(issues):
    provider = next((row for row in issues if row.key == "provider-oversight"), None)
    if not provider:
        return ""
    p.note_editorial_sources(provider.facts[0].sources)
    return (
        '<aside class="reading-pulse"><p class="eyebrow">Historical development</p>'
        '<h2>Critical-provider oversight</h2><p>Announced 10 July 2026. Effective '
        '<time datetime="2026-07-13">13 July 2026</time>. Four named legal entities '
        'include Google Cloud EMEA Limited.</p></aside>'
    )



def agenda_facts(row):
    facts = row.facts
    caveat = ""
    if row.key == "cyber-resilience":
        caveat = "Overall prevalence remained in line with the prior year. These are weighted, self-reported estimates."
    if row.key == "service-recovery" and len(facts) == 3:
        caveat = "Received and closed cases are different cohorts. The firm’s decisions are not independent adjudication."
    if row.key == "service-landscape":
        caveat = ("Received and closed cases are different cohorts, not a service-quality ranking or backlog measure."
                  if len({fact.scope for fact in facts}) == 1 else
                  "Separate legal-entity counts, not a service-quality ranking.")
    if row.key == "funding-base":
        facts = tuple(replace(fact, text=fact.text.replace("GBP", "£")) for fact in facts)
    return "".join(p.render(fact) for fact in facts) + (f'<p class="material">{e(caveat)}</p>' if caveat else "")

def nationwide_bridge(projection, basis):
    """Display equations from the Financial owner's validated signed recipes."""
    measures = {m["measurement_id"]: m for m in projection["measurements"]}
    result = next((r for r in projection["results"] if r.get("basis") == basis and r["formula"] == "signed_bridge"), None)
    if not result:
        return ""
    amounts = [Decimal(measures[i["measurement_id"]]["value"]["amount"]) for i in result["inputs"]]
    opening, *adjustments, outcome = amounts
    terms = "".join((" − " if val < 0 else " + ") + f"{abs(val):,}" for val in adjustments)
    return f'{opening:,}{terms} = {outcome:,}'


def nationwide_facts_bridge(projection):
    equation = nationwide_bridge(projection, "underlying")
    return (
        '<p class="earnings-equation" data-semantic-type="calculated">Calculated · Underlying pretax profit '
        f'(GBP millions): {equation}.</p>'
    ) if equation else ""


def nationwide_insight(projection, *, narrative_only=False):
    if not projection:
        return unavailable("Nationwide Group earnings")
    underlying = nationwide_bridge(projection, "underlying")
    statutory = nationwide_bridge(projection, "statutory")
    if not underlying or not statutory:
        return unavailable("Nationwide Group earnings")
    p.note_editorial_sources(p.Source(s["title"], s["url"], "Nationwide Building Society") for s in projection["sources"])
    return (
        ('' if narrative_only else '<h1>Nationwide Group earnings</h1><p class="reading-context">Consolidated Group · FY ended 31 March 2026 · GBP millions</p>'
         + flow((("Underlying", underlying), ("Statutory", statutory))))
        + '<p>The underlying result isolates the trading basis. The statutory bridge brings member rewards and acquisition-related '
        'adjustments back into the result. Integration spending of £127m is already included in underlying operating costs.</p>'
        '<p>Virgin Money contributes a full year. The previous period included six months, which limits comparisons of organic performance.</p>'
    )


def insight(ctx, data, issues):
    if ctx.scope == "banking" and ctx.detail == "payments":
        return payments(ctx, data)
    if ctx.stream == "forces" and ctx.detail and not ctx.agenda:
        spot = next(row for row in v.geometry()[ctx.scope + "-forces"]["spots"] if row["id"] == ctx.detail)
        fact = v.force_view(ctx, ctx.detail, data)
        text, caveat, _ = v.FORCE_POLICY[ctx.detail]
        return interpretation(spot["label"], (fact,) if fact else (), text, caveat)
    if ctx.scope == "banking" and ctx.stream == "forces" and ctx.agenda in {"", "provider-oversight"}:
        provider = next((row for row in issues if row.key == "provider-oversight"), None)
        return interpretation(
            "Critical-provider oversight", provider.facts if provider else (),
            "Provider oversight addresses disruption that can affect several firms at once. Bank-specific relevance depends on the services used and their role in continuity.",
            "A designation and a brand collaboration do not establish a Lloyds Bank plc Envoy contract, workload or service exposure.",
        )
    if ctx.scope == "lloyds" and ctx.stream == "inside" and ctx.detail == "technology" and not ctx.agenda:
        return lloyds_capability(data, insight=True)
    if ctx.scope == "banking" and ctx.stream == "landscape" and not (ctx.detail or ctx.agenda or ctx.selected):
        item = v.force_view(ctx, "UK-VALUE", data)
        return interpretation(
            "Where money meets the economy", (item,) if item else (),
            "Deposits and lending connect funding and credit risk. Payments connect customer accounts through services whose revenues follow a different mechanism.",
            "Business-model mechanisms do not establish the earnings mix, dependencies or market position of a specific bank.",
        ) + banking_links()
    if ctx.agenda:
        row = next((row for row in issues if row.key == ctx.agenda), None)
        if row:
            return f'<h1>{e(row.title)}</h1>' + p.render(row.conclusion)
    if ctx.scope == "uk" and ctx.stream == "landscape":
        basis = v.visual_v2.basis()
        if agenda.fingerprint(basis) == agenda._pins().get("existing_economy"):
            p.note_editorial_sources(p.Source(s["title"], s["url"]) for s in basis["sources"])
            return (
                '<h1>The shape of the UK economy</h1><p class="reading-context">2024 · UK GVA at current basic prices</p>'
                '<p>Sector shares show where value is added in the economy. Finance and insurance places Banking in a wider sector that also includes other businesses. '
                'A sector share does not measure an individual bank’s revenue or a sector’s growth rate.</p>'
            )
    if ctx.stream == "forces" and not ctx.detail and not ctx.agenda:
        analyses = []
        for spot in v.geometry()[ctx.scope + "-forces"]["spots"]:
            item = v.force_view(ctx, spot["id"], data)
            if item and p.eligible(item):
                text, caveat, _ = v.FORCE_POLICY[spot["id"]]
                analyses.append(interpretation(spot["label"], (item,), text, caveat).replace("<h1>", "<h2>", 1).replace("</h1>", "</h2>", 1))
        if analyses:
            return '<h1>Forces and their implications</h1>' + ''.join(analyses)
    names = {"uk": "United Kingdom", "banking": "UK Banking", "lloyds": "Lloyds Banking Group"}
    return unavailable(names[ctx.scope])
