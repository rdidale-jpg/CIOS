"""Industry stage presentation backed by existing Banking public projections."""
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
    if ctx.reading == "insight" and not projection:
        return '<p>No supported FLORA Insight for this selection.</p>'
    if ctx.reading == "facts":
        body = (
            '<p class="reading-context">Conceptual · bank and building society balance sheets</p>'
            + _definitions((("Funding", "Deposits and wholesale borrowing are liabilities."),
                            ("Lending", "Loans and mortgages are assets that carry credit risk.")))
        )
    else:
        body = (
            '<section class="reading-economy"><h2>Interest and risk</h2>'
            '<p>Yield on assets and the price of funding shape interest income after funding costs. '
            'Impairment, operating costs and capital requirements shape how much value can be retained.</p>'
            '<p>Member rewards and acquisition adjustments affect different profit bases. '
            'One mutual’s result does not establish an industry-wide margin.</p></section>'
        )
    if projection:
        p.note_editorial_sources(p.Source(s['title'], s['url'], 'Nationwide Building Society') for s in projection['sources'])
        body += '<p class="reading-context">Nationwide consolidated Group · FY ended 31 March 2026 · GBP millions</p>'
        body += _definitions((("Underlying pretax profit", reading.nationwide_bridge(projection, "underlying")),
                              ("Statutory pretax profit", reading.nationwide_bridge(projection, "statutory"))))
    return body


def _customers(ctx, issues):
    row = next((issue for issue in issues if issue.key == "service-landscape"), None)
    if ctx.reading == "insight":
        rendered = reading.interpretation(
            "Service and retention", row.facts if row else (),
            "Distribution and account servicing shape the effort customers face. Switching options can strengthen buyer choice.",
            "Complaint count alone does not measure service quality, switching, or harm. Product mix, customer bases and periods may differ.",
            heading="h2",
        )
        return rendered
    body = _definitions((("Households", "Save, borrow and make payments."),
                         ("Businesses", "Manage working capital, collections and cash movements.")))
    return body + (reading.agenda_facts(row) if row else '')


def _providers(ctx, data, issues):
    oversight = next((row for row in issues if row.key == "provider-oversight"), None)
    if ctx.reading == "facts":
        return _definitions((("Bank", "Provides accounts, credit and customer service."),
                             ("Infrastructure operator", "Runs processing services and access arrangements."),
                             ("Technology platform", "Supplies software, computing capacity or specialist services."))) + reading.provider_pulse(issues)
    body = reading.interpretation(
        "Shared dependencies", oversight.facts if oversight else (),
        "Shared platforms can concentrate operational exposure when services are difficult to replace. "
        "Provider revenues follow service arrangements, while capacity, engineering and continuity drive costs.",
        "A designation does not establish concentration, fees or a bank-specific workload.",
        heading="h2",
    )
    collaboration = agenda._claims(data, ("LBG-ENVOY-GOOGLE",)) if oversight else ()
    if collaboration:
        p.note_editorial_sources(collaboration[0].sources)
        body += '<p>The designated Google Cloud EMEA Limited and Lloyds Group’s disclosed Google Cloud brand collaboration establish different relationships. The legal contracting company and any Lloyds Bank plc Envoy workload remain unverified.</p>'
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
