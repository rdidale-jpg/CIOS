"""Industry stage presentation backed by existing Banking public projections."""
from dataclasses import replace
from html import escape

from . import intelligence_presentation as p
from . import leadership_agenda as agenda
from . import reading_views as reading
from . import visual_streams as v

STAGES = {
    "customers": "Customers & businesses",
    "funding": "Funding & lending",
    "providers": "Technology & infrastructure",
}
POSITIONS = {
    "boe": (30, 19),
    "providers": (65, 27),
    "lloyds": (53, 42),
    "funding": (68, 55),
    "payments": (77, 65),
    "customers": (39, 82),
}
STYLE = """<style>
.vp-page .banking-stages{margin:12px 16px 20px}
figure[aria-label="banking landscape"] [data-label-id="providers"]{width:min(50%,10rem);text-align:center;white-space:normal}
.banking-stages a{display:inline-flex;align-items:center;min-height:44px;margin-inline-end:16px}
.banking-stages a[aria-current]{font-weight:700}
.banking-values{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,13rem),1fr));gap:12px 24px;margin:20px 0}
.banking-values div{border-top:2px solid #aa8445;padding-block:10px}
.banking-values dd{margin:5px 0}.banking-values dt{font-weight:700}
.banking-values strong{display:block;font:1.7rem Georgia,serif;margin:4px 0}
.banking-ledger,.banking-market,.banking-dependencies{margin:20px 0}
.banking-ledger{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,14rem),1fr));gap:2px;background:#a68a54;border-block:2px solid #a68a54}
.banking-ledger section{margin:0;padding:14px;background:#eee9d8}
.banking-ledger h3,.banking-market h3{margin:0 0 6px;font-size:1.05em}
.banking-ledger p,.banking-market dd{margin:4px 0}
.banking-bridge{border-inline-start:3px solid #a68a54;padding-inline-start:12px;margin:12px 0}
.banking-bridge strong{display:block;color:#244435;font:clamp(1rem,2.4vw,1.45rem)/1.45 Georgia,serif}
.banking-market{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,15rem),1fr));gap:12px}
.banking-market section{margin:0;padding:12px;border:1px solid #ad9b76;background:#f5f0e1}
.banking-market dl{margin:0}
.banking-market dt{font-weight:bold;margin-top:8px;border-top:1px solid #ad9b76;padding-top:4px}
.banking-dependencies{padding:0;list-style:none;border-inline-start:2px solid #9a8044}
.banking-dependencies li{position:relative;padding:7px 12px}
.banking-dependencies li::before{content:"";position:absolute;inset-inline-start:0;top:1.2em;width:8px;border-top:2px solid #9a8044}
.banking-dependencies strong{display:block;color:#244435}
.banking-ancillary{border-top:1px solid var(--line);padding-top:12px;margin-top:18px}
.banking-ancillary summary{cursor:pointer;min-height:44px;align-content:center}
</style>"""


def extra_entries(ctx):
    return [
        {"id": key, "label": label, "href": v.url(ctx, detail=key, selected="", agenda="") + "#visual-content",
         "selected": ctx.detail == key, "research": "", "sic": ""}
        for key, label in STAGES.items()
    ]


def stage_links(ctx, *, include_payments):
    entries = extra_entries(ctx)
    if include_payments:
        entries.insert(2, {"href": v.url(ctx, detail="payments", selected="", agenda="") + "#visual-content",
                           "label": "Payments & settlement", "selected": ctx.detail == "payments"})
    return '<nav class="banking-stages" aria-label="Industry stages">' + "".join(
        f'<a href="{escape(row["href"], quote=True)}"'
        + (' aria-current="page"' if row['selected'] else '') + f'>{escape(row["label"])}</a>'
        for row in entries
    ) + '</nav>'


def _definitions(rows):
    return '<dl class="banking-values">' + "".join(
        f'<div><dt>{escape(label)}</dt><dd>{escape(value)}</dd></div>' for label, value in rows
    ) + '</dl>'


def _named_links():
    return (
        '<nav class="banking-stages" aria-label="Enterprise examples">'
        '<a href="/industries/banking?stream=landscape&amp;selected=nationwide">Nationwide Group earnings</a>'
        '<a href="/enterprises/lloyds?stream=inside&amp;detail=technology">Lloyds technology &amp; data</a></nav>'
    )


def _funding(ctx):
    from .financial_intelligence.candidate_analytics import public_nationwide_projection

    projection = public_nationwide_projection()
    if ctx.reading == "facts":
        body = (
            '<h2>What a balance sheet connects</h2>'
            '<p class="reading-context">Conceptual · bank and building society balance sheets</p>'
            '<div class="banking-ledger">'
            '<section><h3>Funding and equity</h3><p>Deposits and wholesale borrowing are liabilities. '
            'Equity supports loss absorption.</p></section>'
            '<section><h3>Assets and liquidity</h3><p>Loans and mortgages earn interest and carry credit risk. '
            'Cash and liquid assets help meet outflows.</p></section></div>'
        )
    else:
        body = (
            '<section class="reading-economy"><h2>Interest and risk</h2>'
            '<p class="reading-context">Conceptual · bank and building society economics</p>'
            '<p>Deposit and wholesale costs can reprice faster than loan yields. The spread can narrow '
            'even as lending grows. Impairment and operating costs reduce profit after interest income.</p>'
            '<p>Capital absorbs losses. Liquidity meets withdrawals and other near-term obligations. '
            'A mutual can distribute value to members through rewards or pricing, alongside retaining capital.</p></section>'
        )
    underlying = reading.nationwide_bridge(projection, "underlying") if projection else ""
    statutory = reading.nationwide_bridge(projection, "statutory") if projection else ""
    if not underlying or not statutory:
        return body + ('<p>No supported FLORA Insight for this selection’s Group results.</p>'
                       if ctx.reading == "insight" else "")
    p.note_editorial_sources(p.Source(s["title"], s["url"], "Nationwide Building Society") for s in projection["sources"])
    body += '<h2>Nationwide Group profit bridge</h2><p class="reading-context">Consolidated Group · FY ended 31 March 2026 · GBP millions</p>'
    if ctx.reading == "facts":
        body += (
            '<div class="banking-bridge" data-semantic-type="calculated">Underlying pretax profit'
            f'<strong>{underlying}</strong>'
            '<p>Total income − underlying operating costs − impairment charges.</p></div>'
            '<div class="banking-bridge" data-semantic-type="calculated">Statutory pretax profit'
            f'<strong>{statutory}</strong>'
            '<p>Underlying profit + net income adjustments − acquisition-related expense adjustments − member rewards.</p></div>'
        )
        if any(item["type"] == "reported" and "£127m integration expenditure" in item["text"]
               for item in projection["insights"]):
            body += '<p>Integration costs of £127m are included in underlying operating costs.</p>'
    else:
        body += (
            '<p>Operating costs and impairment explain the step from total income to underlying profit. '
            'Member rewards account for most of the net reduction from underlying to statutory profit.</p>'
            '<p>Virgin Money contributes a full year compared with six months in the prior period. '
            'The bridge describes this Group and period. The scope change limits like-for-like comparisons.</p>'
        )
    return body


def _customers(ctx, issues):
    row = next((issue for issue in issues if issue.key == "service-landscape"), None)
    if ctx.reading == "insight":
        if row:
            p.note_editorial_sources(source for fact in row.facts for source in fact.sources)
        return (
            '<h2>Where customers have a choice</h2><p class="reading-context">Conceptual · distribution economics</p>'
            + _definitions((
                ("Acquisition", "Distribution and account servicing both use resources. Digital self-service can lower the cost of routine interactions. Advice and exception handling can still require people."),
                ("Retention", "Switching options can strengthen buyer choice. Moving linked payments, credit or cash-management arrangements can increase the effort of changing provider."),
            ))
            + ('<p>FCA counts describe service-handling volumes within the published legal-entity cohorts. '
               'Customer bases and product mixes are needed to interpret differences.</p>' if row else "")
        )
    body = (
        '<h2>What customers use Banking for</h2>'
        '<p class="reading-context">Conceptual · examples of needs, products and channels</p>'
        '<div class="banking-market">'
        '<section><h3>Households</h3><dl><dt>Needs</dt><dd>Pay bills, build savings and finance purchases.</dd>'
        '<dt>Products</dt><dd>Current accounts, savings and mortgages.</dd>'
        '<dt>Channels</dt><dd>Mobile, branches and mortgage intermediaries.</dd></dl></section>'
        '<section><h3>Businesses</h3><dl><dt>Needs</dt><dd>Collect receipts, pay staff and fund working capital.</dd>'
        '<dt>Products</dt><dd>Business accounts, payments and credit facilities.</dd>'
        '<dt>Channels</dt><dd>Online banking, relationship teams and intermediaries.</dd></dl></section></div>'
        '<p>Customers place funds, request credit or instruct payments. Banks and building societies provide '
        'account access, financing or payment execution.</p>'
    )
    if row:
        body += ('<details class="banking-ancillary"><summary>FCA complaint activity by legal entity</summary>'
                 + reading.agenda_facts(row)
                 + '<p>These counts do not measure market size or cover the whole sector.</p></details>')
    return body


def _providers(ctx, data, issues):
    oversight = next((row for row in issues if row.key == "provider-oversight"), None)
    collaboration = agenda._claims(data, ("LBG-ENVOY-GOOGLE",))
    if ctx.reading == "facts":
        body = (
            '<h2>Who operates each layer?</h2><p class="reading-context">Conceptual · service roles</p>'
            '<ul class="banking-dependencies">'
            '<li><strong>Bank or building society</strong>Operates customer and core banking services.</li>'
            '<li><strong>Infrastructure operator</strong>Runs shared transactional processing and access.</li>'
            '<li><strong>Technology provider</strong>Supplies computing, software or specialist services.</li></ul>'
            + reading.provider_pulse(issues)
        )
        if oversight:
            body += p.render(oversight.facts[0])
        if collaboration:
            body += '<section class="reading-capability"><h2>Disclosed Group collaboration</h2>'
            disclosure = replace(collaboration[0], text="Lloyds Banking Group identifies Google Cloud as an Envoy platform collaborator.")
            body += p.render(disclosure) + '</section>'
        return body
    body = (
        '<h2>Shared dependencies</h2><p class="reading-context">Conceptual · service continuity</p>'
        '<ul class="banking-dependencies">'
        '<li><strong>Concentration</strong>Disruption can spread when multiple firms depend on the same hard-to-replace service.</li>'
        '<li><strong>Substitutability</strong>Data portability, integration effort and tested recovery determine whether alternate capacity can be used in time.</li>'
        '<li><strong>Continuity costs</strong>Providers operate capacity and recovery processes. Banks incur integration and fallback costs. The division depends on the service arrangements.</li></ul>'
    )
    if oversight:
        body += reading.interpretation(
            "What designation tells us", oversight.facts,
            "Critical-provider oversight addresses potential financial-system dependencies at provider level.",
            "Designation alone reveals neither concentration at a particular bank nor the terms of a service arrangement.",
            heading="h2",
        )
    if collaboration:
        p.note_editorial_sources(collaboration[0].sources)
        if oversight:
            body += '<p>The designated Google Cloud EMEA Limited and Lloyds Group’s disclosed Google Cloud brand collaboration establish different relationships. The legal contracting company and any Lloyds Bank plc Envoy workload remain unverified.</p>'
        else:
            body += '<p>The Group’s disclosed Google Cloud brand collaboration leaves the legal contracting company and any Lloyds Bank plc Envoy workload unverified.</p>'
    return body


def render(ctx, data, issues):
    body = f'<p class="eyebrow">Banking · Landscape</p><h1>{STAGES[ctx.detail]}</h1>'
    body += '<p class="reading-context">UK Banking · Conceptual roles and scoped evidence</p>'
    if ctx.detail == "funding":
        body += _funding(ctx)
    elif ctx.detail == "customers":
        body += _customers(ctx, issues)
    else:
        body += _providers(ctx, data, issues)
    return body + _named_links()


def overview():
    return (
        '<section class="reading-economy"><h2>How value moves through Banking</h2>'
        '<p>Households and businesses use banks and building societies for funding, credit and payments. '
        'Operators and technology providers support different parts of those services.</p>'
        '<p class="reading-context">Conceptual industry roles</p></section>'
    )


def forces(ctx, data, issues):
    if ctx.reading == "facts":
        return ""
    rows = {row.key: row for row in issues}
    body = ""
    if funding := rows.get("funding-economics"):
        body += reading.interpretation(
            "Funding conditions", funding.facts,
            "Deposit competition can alter funding costs. Assets and liabilities can reprice at different speeds.",
            "Policy rates alone do not establish the effect on any bank’s spread.", heading="h2",
        )
    if rows.get("provider-oversight"):
        body += _providers(ctx, data, issues)
    return body
