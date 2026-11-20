"""Editorial compositions for the public Lloyds Group root perspectives."""
from html import escape
from pathlib import Path

from . import visual_streams as v
from . import intelligence_presentation as p

STYLE = '<style>' + Path(__file__).with_name("visual_stream_assets").joinpath("lloyds.css").read_text() + '</style>'
GROUP = "Lloyds Banking Group plc, consolidated Group unless stated"
MEASURES = {
    "LBG-Q326-DEPOSITS": ("GBP billion; balance at 30 September 2026",
                          "Nine months ended / balance sheet at 30 September 2026"),
    "LBG-AR25-DEPOSITS": ("GBP billion; year-end balance", "31 December 2025"),
    "LBG-Q326-PROFIT": ("GBP billion; nine-month statutory pretax profit",
                        "Nine months ended / balance sheet at 30 September 2026"),
}

CAPABILITIES = (
    ("risk-assessment", "Risk assessment",
     ("Assess affordability", "Triage financial difficulty"),
     "Affordability and vulnerability information shapes the next decision. Lloyds’ thresholds and accountable roles are unverified.",
     "Earlier checks can limit losses and rework. Overly restrictive thresholds can also exclude sound applicants."),
    ("servicing", "Servicing",
     ("Book and service credit", "Correct an account"),
     "Account history and transaction records support servicing decisions. The actual hand-offs are unverified.",
     "A shared account history can reduce repeat work. Corrections still need permission checks to protect balances."),
    ("customer-operations", "Customer operations",
     ("Explain the offer", "Resolve a service request"),
     "Terms, case history and customer communications are relevant inputs. Channel responsibilities are unverified.",
     "Giving the first handler more discretion can shorten a case. Escalation still matters for exceptions or redress."),
    ("technology-controls", "Technology and controls",
     ("Record the credit decision", "Protect access to case data"),
     "Access and audit controls are relevant to both journeys. Systems and accountable teams are unverified.",
     "A shared audit trail can support both decisions and dispute review. Shared infrastructure also creates a common point of failure."),
)
INSIDE_DETAILS = frozenset(row[0] for row in CAPABILITIES)


def _claims(data, ids):
    return {
        claim["id"]: statement for claim in v.claim_rows(data, ids)
        if (statement := p.claim_view(data, claim)) is not None and p.eligible(statement)
    }


def _measure(statement, unit, period):
    if (statement and statement.scope == GROUP and statement.unit == unit
            and statement.period == period and statement.semantic_type == "reported"
            and statement.value is not None and statement.measurement_state in {"actual", "not_applicable"}):
        return statement
    return None


def _amount(statement, label, date):
    if statement is None:
        return '<p class="lv-missing">No eligible reported measure.</p>'
    p.note_editorial_sources(statement.sources)
    return f'<p class="lv-amount"><strong>£{escape(str(statement.value))}bn</strong> {label}<small>{date}</small></p>'


LANDSCAPE_COMPONENTS = {
    "funding": (
        "Funding", "Deposits and other funding", "Where does the money come from?",
        "Customer deposits are one source of funding. The bank pays interest on some accounts.",
        "If customers move into accounts paying more, the bank can pay more for funding even when total deposits stay flat. If the mix stays stable, a change in the rates paid may matter more.",
        "What share of deposits earns interest, and how quickly are the rates paid on those accounts changing?",
    ),
    "lending-income": (
        "Lending & income", "Loans earn interest. Fees add income.", "What brings income in?",
        "Loans earn interest. Other assets and services can contribute income too. The Group figures below give no lending yield or split between interest and fees.",
        "Fixed-rate loans can keep earning the same interest while funding costs rise. New or variable-rate loans can change sooner. The mix can widen or narrow the difference between interest earned and paid.",
        "What share of lending changes rate in the next year, and how does interest on that lending compare with the cost of funding it?",
    ),
    "profit-costs": (
        "Profit & costs", "Income less costs and credit losses", "What is left after costs?",
        "Funding and operating costs and expected losses on loans reduce earnings. Capital helps absorb losses and limits how much risk the bank can take.",
        "Even if interest income rises faster than funding costs, higher loan losses or operating costs can absorb the gain. Lending more can also require more capital.",
        "How much of the change in Group profit came from interest income, running costs or provisions for expected loan losses?",
    ),
}


def landscape(ctx, data, issues, *, headers=None):
    from .enterprise_economics import banking
    return banking(ctx, data, issues, headers=headers)


def inside(ctx, data):
    active = ctx.detail or CAPABILITIES[0][0]
    key, name, tasks, basis, mechanism = next(row for row in CAPABILITIES if row[0] == active)
    nav = "".join(
        f'<tr><th scope="row"><a href="{escape(v.url(ctx, detail=slug, reading=ctx.reading), quote=True)}#lv-selection"'
        + (' aria-current="page"' if slug == key else '')
        + f'>{label}</a></th><td>{tasks[0]}</td><td>{tasks[1]}</td></tr>'
        for slug, label, tasks, _, _ in CAPABILITIES
    )
    envoy = _claims(data, ("LBG-ENVOY-CONTROLS",)).get("LBG-ENVOY-CONTROLS")
    separate = ""
    if envoy and envoy.scope == GROUP:
        separate = ('<aside class="lv-separate"><h2>Separate Group technology example</h2>'
                    + p.render(envoy)
                    + f'<a href="{escape(v.url(ctx, detail="technology", reading=ctx.reading), quote=True)}#visual-content">Explore Technology &amp; data</a>'
                    '<p>Workflow use and supplier contract remain unverified.</p></aside>')
    insight = ctx.reading == "insight"
    selection = (
        '<h3>Conceptual operating mechanism</h3>'
        f'<div class="lv-shared"><span>{tasks[0]}</span><strong>{name}</strong><span>{tasks[1]}</span></div>'
        f'<p>{mechanism}</p>'
        if insight else f'<p>{basis}</p>'
    )
    return (
        '<section class="lv lv-inside"><p class="eyebrow">Lloyds Banking Group plc · conceptual map</p>'
        '<h1>Credit and customer service</h1>'
        '<table class="lv-matrix" aria-label="Capabilities across two value streams">'
        '<thead><tr><th scope="col">Durable capabilities</th>'
        '<th scope="col">Credit origination and servicing</th><th scope="col">Customer support and service</th></tr></thead>'
        '<tbody>' + nav + '</tbody></table>'
        f'<section class="lv-selection" id="lv-selection" tabindex="-1"><h2>{name}</h2>'
        + selection
        + '</section>' + separate + '</section>'
    )


def forces(ctx, data):
    claims = _claims(data, ("UK-RATE-NOV26", "LBG-A2030-CIR", "LBG-Q326-PROFIT"))
    rate = claims.get("UK-RATE-NOV26")
    response = claims.get("LBG-A2030-CIR")
    profit = _measure(claims.get("LBG-Q326-PROFIT"), *MEASURES["LBG-Q326-PROFIT"])
    industry = p.render(rate) if rate and rate.scope == "United Kingdom monetary policy; no enterprise-specific outcome inferred" else '<p>Eligible policy observation unavailable.</p>'
    group = p.render(response) if response and response.scope == GROUP else '<p>Eligible Group ambition unavailable.</p>'
    transmission = (
        '<dl class="lv-rate-branches"><div><dt>Funding costs reprice first</dt>'
        '<dd>If funding costs rise faster than asset yields, spread can narrow.</dd></div>'
        '<div><dt>Lending reprices first</dt><dd>If asset yields rise faster, spread can widen.</dd></div></dl>'
        if ctx.reading == "insight" else
        '<p>Conceptual · Changes in rates can reach bank earnings through funding costs and loan yields.</p>'
    )
    consequence = ("A weaker spread can reduce income. The cost-to-income ratio can rise even when operating costs are steady."
                   if ctx.reading == "insight" else "Conditional · Earnings sensitivity depends on the timing and size of repricing.")
    return (
        '<section class="lv lv-forces"><p class="eyebrow">Lloyds Banking Group plc · rates and earnings</p>'
        '<h1>What can put pressure on earnings?</h1><ol class="lv-pressure">'
        '<li><h2>Observed condition</h2><p class="lv-tag">UK monetary policy · industry context</p>' + industry + '</li>'
        f'<li><h2>Transmission</h2>{transmission}</li>'
        '<li><h2>Disclosed response</h2><p>No eligible evidence links a Lloyds response to this rate decision.</p>'
        '<div class="lv-group-context"><h3>Separate Group efficiency ambition</h3>' + group + '</div></li>'
        f'<li><h2>Conditional consequence</h2><p>{consequence}</p>'
        '<p>To assess Lloyds’ exposure, compare deposit and asset repricing, income and costs over matching periods.</p></li>'
        '</ol><div class="lv-separate"><h2>Reported Group performance context</h2>'
        + _amount(profit, "statutory pretax profit", "Nine months to 30 September 2026 · earnings flow")
        + '</div></section>'
    )
