"""Banking participant perspectives over existing public owner projections."""
from dataclasses import replace
from html import escape

from . import intelligence_presentation as p
from . import leadership_agenda as agenda
from . import reading_views as reading
from . import visual_streams as v

SUBJECTS = {
    "natwest": ("National Westminster Bank PLC", "Partial service profile",
                "How a retail and business bank earns",
                "A bank can use customer deposits to fund lending and earn the spread between loan yields and funding costs.",
                "Deposit repricing and credit losses can move earnings in different directions. Legal-bank income and funding mix would show which matters here."),
    "hsbc-uk": ("HSBC UK Bank Plc", "Partial service profile",
                "How a UK bank inside a wider group earns",
                "A UK bank can earn from lending and customer services. The legal bank and the wider group have separate reporting perimeters.",
                "Fees, funding costs and shared services can affect UK-bank economics differently from Group results. The UK-bank segment breakdown is needed."),
    "nationwide": ("Nationwide", "Mutual banking",
                   "How a mutual allocates value",
                   "A mutual can return value through member pricing or rewards while retaining earnings to support lending.",
                   "Member benefits and retained capital are different uses of earnings. Group results and Society service activity answer different questions."),
    "starling": ("Starling Bank Limited", "Partial service profile",
                 "How a digital bank earns",
                 "A digital bank can earn through funded lending and account services, with distribution centred on digital channels.",
                 "Digital channels can shift costs from branches to technology and support. Legal-bank economics are needed to measure the effect. Group and Engine platform economics remain separate research."),
    "boe": ("Bank of England", "Central-bank institution",
            "What the central bank provides",
            "Monetary policy sets a rate context. Settlement infrastructure serves a separate institutional purpose.",
            "Rate decisions can change borrowing conditions. Settlement instead depends on liquidity and reliable operation."),
}
STREAMS = ("landscape", "inside", "forces")

_OPERATIONS = {
    "boe": ("Settle a payment obligation",
            (("Receive obligations", "Payment operations"), ("Settle between institutions", "Settlement assurance"),
             ("Confirm completion", "Settlement assurance")),
            "CHAPS and RTGS operating responsibilities and participant links remain unverified here."),
    "nationwide": ("Resolve a member service issue",
                   (("Receive an issue", "Member servicing"), ("Review the member’s case", "Case resolution"),
                    ("Respond and record", "Case resolution")),
                   "Society complaint data cover all products. Team and system assignments remain unverified."),
    "starling": ("Resolve an account-service issue",
                 (("Receive the issue", "Digital service intake"), ("Route for investigation", "Case management"),
                  ("Notify the customer", "Case management")),
                 "The channel, system and platform used for these cases remain unverified."),
}
_BANK_OPERATIONS = ("Resolve a customer complaint",
                    (("Receive a complaint", "Case handling"), ("Investigate and respond", "Case handling"),
                     ("Record the outcome", "Service reporting")),
                    "Accountable teams and systems remain unverified.")

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


def _model(ctx):
    _, _, heading, facts, insight = SUBJECTS[ctx.selected]
    text = facts + " " + insight
    return (
        f'<section class="cohort-mechanism"><p class="reading-context">Conceptual business model</p>'
        f'<h2>{escape(heading)}</h2><p>{escape(text)}</p></section>'
    )


def landscape(ctx, body, data, issues):
    return body + _model(ctx) + navigation(ctx, data, issues)


def _inside(ctx):
    outcome, steps, limit = _OPERATIONS.get(ctx.selected, _BANK_OPERATIONS)
    body = f'<h2>{escape(outcome)}</h2><p class="reading-context">Conceptual · activity and capability map</p>'
    body += '<ol class="cohort-outcomes">' + "".join(
        f'<li><strong>{escape(step)}</strong> · {escape(capability)}</li>' for step, capability in steps
    ) + '</ol>'
    capabilities = dict.fromkeys(capability for _, capability in steps)
    body += '<h2>Durable capabilities</h2><p>' + escape(" · ".join(capabilities)) + '</p>'
    return body + f'<p>{escape(limit)}</p>'


def _service(ctx, facts):
    if not facts:
        return '<p>Scoped evidence for this selection is unavailable.</p>'
    if ctx.stream == "forces":
        condition = facts[:1]
        return p.render(condition[0], compact=True) + reading.interpretation(
            "What complaint intake signals", condition,
            "Intake measures service workload. A change in volume could reflect scale, product mix or customer experience.",
            "Compare rates on a matched customer base and period before judging commercial pressure.",
            heading="h2",
        )

    heading = "Customer service evidence" if ctx.stream == "landscape" else "Reported service activity"
    body = f'<h2>{heading}</h2>'
    interpretation = ''
    if ctx.stream == "inside":
        interpretation = reading.interpretation(
            "What the cohorts show", facts,
            "Intake, case closure and firm decisions measure different parts of service operations.",
            "Received and closed complaints are different cohorts. Firm-upheld is the bank’s own decision.",
            heading="h3",
        )
    lines = (
        f"{facts[0].value:,} complaints received",
        f"{facts[1].value:,} complaints closed",
        f"{facts[2].value}% of closed complaints upheld",
    )
    return (
        body + f'<p class="reading-context">{escape(facts[0].period)} · legal entity · FCA</p>'
        + "".join(p.render(replace(fact, text=line), compact=True) for fact, line in zip(facts, lines))
        + '<p>Received and closed complaints are different cohorts. Firm-upheld is the bank’s own decision.</p>' + interpretation
    )


def _institution(ctx, issues):
    if ctx.stream == "inside":
        body = _inside(ctx)
        body += '<h2>Conceptual operating mechanism</h2><p>Settlement reduces outstanding obligations and depends on liquidity and resilient operations.</p>'
        return body
    facts = next((row.facts[:1] for row in issues if row.key == "funding-economics"), ())
    if ctx.stream == "landscape":
        return _model(ctx) + '<h2>Monetary policy context</h2>' + (
            p.render(facts[0]) if facts else '<p>Scoped policy evidence is unavailable.</p>'
        )
    return ('<h2>Monetary policy decision</h2>' + (p.render(facts[0]) if facts else '')
        + reading.interpretation(
            "How policy affects funding", facts,
            "The policy rate can affect borrowing and funding costs. The effect depends on each institution’s exposure.",
            "The decision does not establish bank-specific effects or settlement outcomes.", heading="h2",
        ))


def render(ctx, data, issues):
    name, label, *_ = SUBJECTS[ctx.selected]
    body = f'<p class="eyebrow">{escape(label)}</p><h1>{escape(name)}</h1>'
    if ctx.selected == "boe":
        return body + _institution(ctx, issues) + navigation(ctx, data, issues)

    in_review = any(row.key == "service-landscape" for row in issues)
    row = (agenda.bank_service_issue(ctx.selected, data)
           if ctx.selected not in {"natwest", "hsbc-uk"} or in_review else None)
    facts = row.facts if row else ()
    if ctx.stream == "inside":
        body += _inside(ctx)
    elif ctx.stream == "forces":
        body += '<h2>Service workload</h2><p>Company response: no scoped programme is evidenced here.</p>'
    else:
        body += _model(ctx)
    return body + _service(ctx, facts) + navigation(ctx, data, issues)
