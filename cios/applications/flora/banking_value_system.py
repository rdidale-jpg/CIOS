"""Banking value-system presentation over the existing public scene owners."""
from html import escape

from . import intelligence_presentation as presentation
from . import leadership_agenda
from . import visual_streams as streams

STAGES = {
    "customers": (
        "Customers & businesses",
        "Households save, borrow and make payments. Businesses also need working capital and a way to collect and move cash.",
        "Accounts, mobile services and branches bring these needs into the banking system. Onboarding, identification and servicing carry costs.",
    ),
    "funding": (
        "Deposits & lending",
        "Interest on loans and other assets, less the cost of funding, drives the bank’s interest margin.",
        "Credit losses and operating costs reduce earnings. Capital absorbs losses and liquidity helps meet cash outflows. A mutual can also share value with members.",
    ),
    "clearing": (
        "Payments & settlement",
        "A payment instruction passes through processing and clearing before obligations are settled.",
        "Operators provide infrastructure and access. Schemes set rules, networks carry instructions and settlement discharges obligations. Amounts moved measure customer funds, while operator fees pay for services.",
    ),
    "outcomes": (
        "Customer outcomes",
        "Customers need reliable access to money and timely service when something goes wrong.",
        "Complaint numbers describe cases handled by a legal entity. Comparing service quality requires comparable customers, products and periods.",
    ),
    "technology": (
        "Technology & providers",
        "Cloud capacity, core software and specialist operations support banks across the value system.",
        "A cloud platform earns through capacity and services, with infrastructure and support costs. A provider’s commercial brand, reporting segment and legal entities have distinct scopes.",
    ),
}

STYLE = """<style>
.banking-flow{margin:16px 0 22px;padding:0 12px;border-left:2px solid #ad8d4f}
.banking-flow a{display:flex;align-items:center;min-height:44px;color:inherit;
  text-decoration:none;font:1rem/1.3 Georgia,serif;padding:4px 6px;border-bottom:1px solid var(--line)}
.banking-flow a[aria-current]{font-weight:bold;background:#ede5ce}
.banking-flow a:focus-visible,.banking-links a:focus-visible{outline:2px solid currentColor;outline-offset:2px}
.banking-pathway{border-top:1px solid var(--line);margin:24px 0;padding-top:16px}
.banking-pathway p{max-width:59ch}
.banking-links{display:flex;gap:8px 20px;flex-wrap:wrap}
.banking-links a{min-height:44px;display:inline-flex;align-items:center}
.banking-pulse{border-left:3px solid #ad8d4f;padding-left:16px;margin:24px 0}
</style>"""


def navigation(ctx):
    links = "".join(
        f'<a href="{escape(streams.url(ctx, stream="landscape", selected=key, detail="", agenda="") + "#visual-content", quote=True)}"'
        f'{" aria-current=page" if ctx.selected == key else ""}>{escape(stage[0])}</a>'
        for key, stage in STAGES.items()
    )
    return f'<nav class="banking-flow" aria-label="Banking value system">{links}</nav>'


def enterprise_links(ctx):
    nationwide = streams.url(ctx, stream="landscape", selected="nationwide", detail="", agenda="")
    lloyds = streams.url(streams.Context("lloyds", "landscape", detail="technology"))
    return (
        '<nav class="banking-links" aria-label="Enterprise examples">'
        f'<a href="{escape(nationwide, quote=True)}">Nationwide Group earnings</a>'
        f'<a href="{escape(lloyds, quote=True)}">Lloyds technology &amp; data</a></nav>'
    )


def landscape(ctx):
    stage = STAGES.get(ctx.selected)
    if stage is None:
        return (
            '<section class="banking-pathway" aria-labelledby="banking-mechanisms">'
            '<h2 id="banking-mechanisms">Three ways Banking creates value</h2>'
            '<p>Banks fund lending and manage credit risk. Payment operators provide the infrastructure '
            'that connects accounts. Technology providers supply software, capacity and specialised services.</p>'
            '<p>Public authorities oversee distinct parts of that system, including monetary policy, '
            'prudential supervision and customer conduct.</p>' + enterprise_links(ctx) + '</section>'
        )
    title, lead, detail = stage
    return (
        f'<p class="eyebrow">UK Banking · Landscape</p><h1>{escape(title)}</h1>'
        f'<p class="editorial-lead">{escape(lead)}</p>'
        f'<section class="banking-pathway"><p>{escape(detail)}</p>{enterprise_links(ctx)}</section>'
    )


def historical_pulse(ctx, issues):
    provider = next((issue for issue in issues if issue.key == "provider-oversight"), None)
    if provider is None:
        return ""
    presentation.note_editorial_sources(provider.facts[0].sources)
    return (
        '<aside class="banking-pulse" aria-labelledby="banking-change">'
        '<p class="eyebrow">Historical development</p><h2 id="banking-change">Oversight of critical providers</h2>'
        '<p>Effective <time datetime="2026-07-13">13 July 2026</time>, the UK designated four technology-provider '
        'legal entities, including Google Cloud EMEA Limited.</p>'
        '<p>The effect on a bank depends on the services it uses and their importance to its operations.</p>'
        + enterprise_links(ctx) + '</aside>'
    )


def lloyds_scope(data):
    facts = leadership_agenda._claims(data, ("LBG-ENVOY-GOOGLE",))
    if not facts or not all(presentation.eligible(fact) for fact in facts):
        return ""
    presentation.note_editorial_sources(facts[0].sources)
    return (
        '<section class="banking-pathway"><h2>What the relationship establishes</h2>'
        '<p>Lloyds Banking Group describes Google Cloud as an Envoy collaborator. The disclosure names the '
        'brand. It leaves the contracting company, any Lloyds Bank plc workload and operating outcomes unverified.</p>'
        '</section>'
    )


def review_relationship():
    """Pinned research discussion for existing authorised inspection only."""
    return (
        '<section aria-labelledby="banking-relationship-review"><h2 id="banking-relationship-review">'
        'Payment participation · review only</h2>'
        '<p>Pay.UK Limited’s participant list, inspected 18 November 2026, lists Lloyds Bank plc '
        'under Faster Payments. This records scheme participation. Settlement access, contract terms '
        'and service exposure require separate evidence.</p>'
        '<p><a href="https://github.com/rdidale-jpg/CIOS/blob/46f0ed42e10f2c8a2cabbf344498898e94072990/'
        'docs/flora-runtime/bnk-ind-1/Handoff.json">Reviewed handoff · IND-PART-LLOYDS</a></p></section>'
    )
