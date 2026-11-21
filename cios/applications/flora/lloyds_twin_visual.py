"""Lloyds-only visual composition for the existing bounded flagship detail."""

from html import escape
from pathlib import Path

from . import visual_streams as visual

ART = 'vp2-lloyds-inside-768-13827db67c30'
ASSETS = Path(__file__).with_name('visual_stream_assets')
STYLE = '<style>' + (ASSETS / 'lloyds-twin.css').read_text() + '</style>'
INTERACTIONS = '<script>' + (ASSETS / 'lloyds-twin.js').read_text() + '</script>'

# Independently checked against the issuer-filed FY2025 Form 20-F, segment
# reporting. Descriptive labels alone form the prototype's navigation. No
# report cells, issuer prose, PDF links or financial Source admissions.
DIVISIONS = (
    ('Retail', 'Households', 'Current accounts, savings and mortgages', 'Interest paid on deposits and earned on loans', 'retail'),
    ('Commercial Banking', 'Businesses and institutions', 'Deposits, lending and payments', 'Lending income and fees for services', 'commercial'),
    ('Insurance, Pensions & Investments', 'Savers and retirement customers', 'Long-term savings and pensions', 'Premiums, investment performance and policyholder obligations', 'retirement'),
)
OPERATIONS = (
    ('Customer service', 'Keep branch access clear', 'LBG-BRAND26-TIMING',
     'inside', 'customer-operations'),
    ('Platform renewal', 'Retire applications in stages', 'LBG-AR25-MIGRATION',
     'inside', 'technology-controls'),
    ('Data & AI', 'Run AI with oversight', 'LBG-ENVOY-CONTROLS',
     'inside', 'technology'),
)


def _link(ctx, stream, detail, label):
    href = visual.url(ctx, stream=stream, detail=detail, reading=ctx.reading)
    return f'<a href="{escape(href, quote=True)}#visual-content">{escape(label)}</a>'


def choices(label, entries, kind):
    """In-page links retain an accessible section fallback without scripting."""
    if not entries:
        return ''
    nav, panels = [], []
    for key, title, content in entries:
        ident = f'llf-{key}'
        nav.append(f'<a href="#{ident}" data-llf-choice>{escape(title)}</a>')
        panels.append(f'<section id="{ident}" data-llf-panel><h3 tabindex="-1">{escape(title)}</h3>{content}</section>')
    return (f'<div class="llf-choices llf-{kind}" data-llf-choices>'
            f'<nav aria-label="{escape(label, quote=True)}">' + ''.join(nav)
            + '</nav>' + ''.join(panels) + '</div>')


def _division_cards(inspect):
    cards = []
    for title, customer, activity, driver, key in DIVISIONS:
        content = (f'<p><strong>{escape(customer)}</strong> · {escape(activity)}</p>'
                   f'<p>{escape(driver)}. <span class="ltv-note">Illustrative economics without a segment allocation.</span></p>'
                   '<p class="ltv-note">Operating examples and strategic priorities are Group-wide. '
                   'Their ownership and segment-level effects remain unverified.</p>'
                   '<div class="ltv-related"><a href="#ltv-inside">Group operating examples</a> '
                   '<a href="#ltv-thread">Core renewal strategy</a></div>')
        cards.append((key, title, content))
    return choices('Reporting segments', cards, 'division') + inspect('FY2025 reporting segments', (),
        content=('<p>Customer and product labels are orientation examples. Card sizes do not encode revenue, cost or ownership. '
                 'Segment names were checked against the issuer-filed annual report.</p>'
                 '<a href="https://www.lloydsbankinggroup.com/" rel="noreferrer">Lloyds Banking Group</a>'))


def _operations(ctx, facts, inspect):
    cards = []
    for title, label, key, stream, detail in OPERATIONS:
        if key in facts:
            cards.append(f'<article><p class="ltv-kicker">{escape(title)}</p><h3>{escape(label)}</h3>'
                         + _link(ctx, stream, detail, 'Open existing view') + inspect(title, (facts[key],))
                         + '</article>')
    return ''.join(cards)


def opening(ctx, facts, stages, inspect, overview):
    """Render the same eligible evidence as a browsable issue map."""
    cards = []
    for label, key, stream, detail in stages:
        if key in facts:
            fact = facts[key]
            content = ('<p>' + escape(fact.text) + ' <small>' + escape(fact.period) + '</small></p><div class="ltv-related">'
                       + _link(ctx, stream, detail, 'Open ' + label.lower())
                       + inspect(label, (fact,)) + '</div>')
            cards.append(('stage-' + label.lower(), label, content))
    image = escape(visual.ASSET_BASE + ART, quote=True)
    return (STYLE + '<section class="ltv" aria-label="Lloyds enterprise landscape">'
            '<div class="ltv-hero"><div class="ltv-title"><p class="ltv-kicker">Enterprise Twin · Prototype</p>'
            '<h1>Lloyds <span>Banking Group</span></h1><p>Renew the bank while it runs</p></div>'
            f'<img src="{image}" alt="" width="768" height="512"></div>'
            '<nav class="ltv-jump" aria-label="Twin sections">'
            '<a href="#ltv-landscape">Landscape</a><a href="#ltv-inside">Inside Lloyds</a>'
            '<a href="#ltv-thread">Core renewal</a><a href="#ltv-perspectives">Perspectives</a></nav>'
            '<section id="ltv-landscape"><h2>Three businesses, different economics</h2>'
            + _division_cards(inspect)
            + '<div class="ltv-band"><strong>Group funding and earnings</strong>'
            '<span>Deposits, lending income, operating costs and credit losses</span>'
            + _link(ctx, 'landscape', 'economics', 'Inspect Group economics') + '</div></section>'
            '<section id="ltv-inside"><h2>Customer operations and their dependencies</h2>'
            '<div class="ltv-grid ltv-operations">' + _operations(ctx, facts, inspect) + '</div>'
            '<p class="ltv-note">Examples across the Group. Internal system hand-offs and accountable teams remain unverified.</p></section>'
            '<section id="ltv-thread"><h2>Core renewal and the cost of running the bank</h2>'
            '<p>' + escape(overview) + '</p>' + choices('Follow the strategic issue', cards, 'thread')
            + '<p class="ltv-note">Each step cites a disclosure. Their connection is analytical and establishes no causal impact.</p>'
            '</section></section>')
