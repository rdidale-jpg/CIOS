"""Banking participant perspectives over existing public owner projections."""
from html import escape

from . import intelligence_presentation as p
from . import leadership_agenda as agenda
from . import reading_views as reading
from . import visual_streams as v

SUBJECTS = {
    "natwest": ("National Westminster Bank PLC", "Legal-bank service profile",
                "Retail and business banking", "Deposits, lending and current-account services"),
    "hsbc-uk": ("HSBC UK Bank Plc", "Legal-bank service profile",
                "UK retail and commercial banking", "Customer accounts and credit within a wider group context"),
    "nationwide": ("Nationwide", "Mutual banking",
                   "Member value and retained capital", "Savings, mortgages and member rewards"),
    "starling": ("Starling Bank Limited", "Challenge and distribution",
                 "Digital account servicing", "Digital distribution changes the channels used to serve account holders"),
    "boe": ("Bank of England", "Central-bank institution",
            "Monetary policy and settlement context", "Settlement services move obligations between participants"),
}
STREAMS = ("landscape", "inside", "forces")

_OPERATIONS = {
    "boe": ("Settle a payment obligation",
            ("Receive obligations", "Settle between institutions", "Confirm completion"),
            "Payment operations and settlement assurance", "Exact work allocation is unverified."),
    "nationwide": ("Resolve a member service issue",
                   ("Receive the issue", "Review the member’s case", "Respond and record the decision"),
                   "Member servicing and complaint resolution", "The Society cohort measures complaints across products."),
    "starling": ("Resolve an account-service issue",
                 ("Receive the issue", "Route it for investigation", "Notify the customer and report the outcome"),
                 "Digital service intake and case management", "Specific channels and platform roles for these cases are unverified."),
}
_BANK_OPERATIONS = ("Resolve a customer complaint",
                    ("Receive a complaint", "Investigate and respond", "Record the outcome"),
                    "Case handling and reporting", "Exact accountable teams and process ownership are unverified.")
STYLE = """<style>
.cohort-nav{display:flex;flex-wrap:wrap;gap:4px 16px;margin:18px 0}
.cohort-nav a{display:inline-flex;min-height:44px;align-items:center}
.cohort-mechanism{padding:14px 18px;border-inline-start:3px solid #a08349;background:#efe8d6;margin:16px 0}
.cohort-outcomes{margin:16px 0;padding-inline-start:20px;list-style-type:square}
</style>"""


def navigation(ctx, data, issues):
    service_review = any(row.key == "service-landscape" for row in issues)
    rows = [("lloyds", "Lloyds Banking Group")]
    rows.extend((key, value[0]) for key, value in SUBJECTS.items()
                if key not in {"natwest", "hsbc-uk"} or (service_review and agenda.bank_service_issue(key, data)))

    return '<nav class="cohort-nav" aria-label="Banking cohort">' + "".join(
        f'<a href="{escape("/enterprises/lloyds" if key == "lloyds" else v.url(ctx, stream="landscape", selected=key, detail="", agenda=""), quote=True)}">'
        f'{escape(label)}</a>' for key, label in rows
    ) + '</nav><p><a href="/industries/banking?detail=payments">Payment roles</a> · <a href="/industries/banking?detail=providers">Technology ecosystem</a></p>'


def landscape(ctx, body, data, issues):
    _, label, heading, mechanism = SUBJECTS[ctx.selected]
    return body + (
        f'<section class="cohort-mechanism"><p class="reading-context">Conceptual · {escape(label)}</p>'
        f'<h2>{escape(heading)}</h2><p>{escape(mechanism)}.</p>'
        '<p>Business-line economics and verified dependencies require separate, scoped evidence.</p></section>'
    ) + navigation(ctx, data, issues)


def render(ctx, data, issues):
    name, label, heading, _ = SUBJECTS[ctx.selected]
    if ctx.selected == "boe":
        facts = next((row.facts[:1] for row in issues if row.key == "funding-economics"), ())
        caveat = "The rate decision does not identify settlement volumes, participants or bank-specific effects."
        interpretation = "The policy rate can affect funding and borrowing conditions. Settlement is a separate institutional function."
    else:
        in_review = any(row.key == "service-landscape" for row in issues)
        row = (agenda.bank_service_issue(ctx.selected, data)
               if ctx.selected not in {"natwest", "hsbc-uk"} or in_review else None)
        facts = row.facts if row else ()
        caveat = "These measures do not establish service quality, costs, accountable teams or the systems used. Received and closed complaints are different cohorts. Firm-upheld is not independent adjudication."
        interpretation = "Intake and resolution volumes describe different activities. The firm-upheld share provides limited decision context without a common customer denominator."
    body = f'<p class="eyebrow">{escape(label)}</p><h1>{escape(name)}</h1>'
    if ctx.stream == "inside":
        outcome, steps, capabilities, limit = _OPERATIONS.get(ctx.selected, _BANK_OPERATIONS)
        body += (
            f'<h2>{escape(outcome)}</h2><p class="reading-context">Conceptual · activity sequence</p>'
            '<ol class="cohort-outcomes">' + "".join(f'<li>{escape(step)}</li>' for step in steps) + '</ol>'
            f'<h2>Durable capabilities</h2><p>{escape(capabilities)}. {escape(limit)}</p>'
        )
    elif ctx.stream == "forces":
        body += (
            '<h2>Observed conditions and response</h2>'
            + ('<p>Monetary policy is an institutional decision with effects that depend on the recipient’s exposure.</p>'
               if ctx.selected == "boe" else '<p>Service activity gives a measure of operating demand. A specific response programme is unverified.</p>')
        )
    else:
        body += f'<h2>{escape(heading)}</h2>'
    if ctx.selected == "boe" and ctx.stream == "inside":
        if ctx.reading == "insight":
            body += ('<h2>Conceptual operating mechanism</h2><p>Settlement can reduce outstanding obligations '
                     'while raising the importance of available liquidity and resilient operations.</p>')
        return body + '<p>CHAPS and RTGS work allocation, throughput and bilateral dependencies are unverified in this view.</p>' + navigation(ctx, data, issues)
    body += ('<h2>Monetary policy context</h2>' if ctx.selected == "boe" else '<h2>Reported complaint activity · legal entity</h2>')
    if facts:
        if ctx.reading == "facts":
            body += "".join(p.render(fact) for fact in facts)
        else:
            body += reading.interpretation("What the measurements support", facts, interpretation, caveat, heading="h2")
    else:
        body += '<p>Scoped evidence for this selection is unavailable.</p>'
    body += f'<p>{escape(caveat)}</p>'
    return landscape(ctx, body, data, issues) if ctx.stream == "landscape" else body + navigation(ctx, data, issues)
