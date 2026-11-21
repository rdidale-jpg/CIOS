"""Lloyds-only visual composition for the existing bounded flagship detail."""

from html import escape
from pathlib import Path

from . import visual_streams as visual

ART = 'vp2-lloyds-inside-768-13827db67c30'
STYLE = '<style>' + Path(__file__).with_name('visual_stream_assets').joinpath('lloyds-twin.css').read_text() + '</style>'

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


def _division_cards():
    cards = []
    for title, customer, activity, driver, key in DIVISIONS:
        cards.append(f'<article class="ltv-division ltv-{key}">'
                     f'<p>{escape(customer)}</p><h3>{escape(title)}</h3>'
                     f'<p>{escape(activity)}</p><details><summary>Economic lens</summary><p>{escape(driver)}</p>'
                     '<p>Illustrative driver, without a segment allocation.</p></details></article>')
    return ''.join(cards)


def _operations(ctx, facts, basis):
    cards = []
    for title, label, key, stream, detail in OPERATIONS:
        if key in facts:
            cards.append(f'<article><p class="ltv-kicker">{escape(title)}</p><h3>{escape(label)}</h3>'
                         + _link(ctx, stream, detail, 'Open existing view') + basis((facts[key],))
                         + '</article>')
    return ''.join(cards)


def opening(ctx, facts, stages, basis, overview):
    """Render visual lanes over the flagship's existing eligible evidence."""
    links = ''.join(f'<li>{_link(ctx, stream, detail, label)}</li>'
                    for label, key, stream, detail in stages if key in facts)
    core = tuple(facts[key] for _, key, _, _ in stages if key in facts)
    image = escape(visual.ASSET_BASE + ART, quote=True)
    return (STYLE + '<section class="ltv" aria-label="Lloyds enterprise landscape">'
            '<div class="ltv-hero"><div class="ltv-title"><p class="ltv-kicker">Enterprise Twin · Prototype</p>'
            '<h1>Lloyds Banking Group</h1><p>Renew the bank while it runs</p></div>'
            f'<img src="{image}" alt="" width="768" height="512"></div>'
            '<nav class="ltv-jump" aria-label="Twin sections">'
            '<a href="#ltv-landscape">Landscape</a><a href="#ltv-inside">Inside Lloyds</a>'
            '<a href="#ltv-thread">Core renewal</a><a href="#ltv-perspectives">Perspectives</a></nav>'
            '<section id="ltv-landscape"><p class="ltv-kicker">Landscape</p><h2>Three businesses, different economics</h2>'
            '<div class="ltv-grid">' + _division_cards() + '</div>'
            '<details><summary>Reporting basis and limits</summary>'
            '<p>FY2025 reporting segments. Customer and product labels are orientation examples. Card sizes do not encode revenue, cost or ownership.</p>'
            '<p>Segment names were checked against the issuer-filed annual report. This prototype uses no newly admitted financial values.</p>'
            '<a href="https://www.lloydsbankinggroup.com/" rel="noreferrer">Lloyds Banking Group</a></details>'
            '<div class="ltv-band"><strong>Group funding and earnings</strong>'
            '<span>Deposits, lending income, operating costs and credit losses</span>'
            + _link(ctx, 'landscape', 'economics', 'Inspect Group economics') + '</div></section>'
            '<section id="ltv-inside"><p class="ltv-kicker">Inside the enterprise</p>'
            '<h2>Customer operations and their dependencies</h2>'
            '<div class="ltv-grid ltv-operations">' + _operations(ctx, facts, basis) + '</div>'
            '<p class="ltv-note">Examples across the Group. Internal system hand-offs and accountable teams remain unverified.</p></section>'
            '<section id="ltv-thread"><p class="ltv-kicker">Strategic issue</p>'
            '<h2>Core renewal and the cost of running the bank</h2>'
            '<p>' + escape(overview) + '</p><ol class="ltv-thread" aria-label="Follow the strategic issue">'
            + links + '</ol>' + (basis(core) if core else '')
            + '<p class="ltv-note">The links join related evidence. Their order does not establish causation.</p></section></section>')
