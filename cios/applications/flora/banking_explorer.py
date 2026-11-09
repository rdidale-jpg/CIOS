"""Read-only visual journey over the existing repository Banking pilot.

No private model/store resolution: Canvas and evidence retain their own routes.
"""
from html import escape as e

from .banking_portfolio import BANKS, GENERATED_DATE

ROOT = '/flora/banking/explorer'

STYLE = """
.explorer{--sea:#164d48;--mint:#d7ede4;--coral:#f6b397;--quiet:#566b65;--edge:#d7e0d9}
.explorer h1{font-size:clamp(2.5rem,6vw,5.2rem);letter-spacing:-.055em;max-width:850px}
.explorer h2{font-size:clamp(1.5rem,3vw,2.2rem);letter-spacing:-.03em;line-height:1.15}
.explorer h3{line-height:1.25}
.explorer p{max-width:75ch}
.explorer a{overflow-wrap:anywhere}
.ex-breadcrumb{display:flex;flex-wrap:wrap;gap:9px;font-size:.85rem;margin-bottom:24px}
.ex-hero{background:var(--sea);color:#fffdf6;border-radius:26px;padding:clamp(24px,5vw,56px);position:relative;overflow:hidden}
.ex-hero:after{content:'';position:absolute;width:260px;height:260px;border:45px solid #ffffff0a;border-radius:50%;right:-100px;top:-85px;pointer-events:none}
.ex-hero .eyebrow{color:#bde3ce}
.ex-hero p{color:#d8e9e2;max-width:650px}
.ex-hero a{color:#fff}
.ex-hero .ex-button{color:#173c36;background:#d7ede4}
.ex-meta{display:flex;gap:26px;flex-wrap:wrap;border-top:1px solid #ffffff30;padding-top:22px;margin-top:28px}
.ex-meta strong{display:block;font-size:1.8rem}
.ex-meta span{font-size:.82rem;color:#c2dbd2}
.ex-button{display:inline-block;background:var(--sea);color:white;padding:12px 20px;border-radius:8px;text-decoration:none;margin:8px 8px 8px 0}
.ex-section{margin:46px 0;scroll-margin-top:24px}
.ex-heading{display:flex;align-items:baseline;justify-content:space-between;gap:18px;flex-wrap:wrap}
.ex-kicker{color:var(--quiet);font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;font-weight:800}
.ex-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.ex-card{background:#fffdf8;border:1px solid var(--edge);border-radius:16px;padding:24px;min-width:0}
.ex-card h3{margin:12px 0}
.ex-bank{display:flex;flex-direction:column;text-decoration:none;color:#173c36;transition:transform .15s,border-color .15s}
.ex-bank:hover{transform:translateY(-4px);border-color:var(--sea)}
.ex-monogram{width:48px;height:48px;display:grid;place-items:center;background:var(--mint);border-radius:12px;font-size:1.2rem;font-weight:800}
.ex-bank p{color:var(--quiet);font-weight:400;font-size:.92rem}
.ex-bank .ex-arrow{margin-top:auto;padding-top:22px}
.ex-tag{display:inline-block;font-size:.75rem;background:#ecf0e9;border-radius:5px;padding:3px 8px;color:#36564c}
.ex-tag.hypothesis{background:#ffe7d8;color:#754324}
.ex-subnav{display:flex;flex-wrap:wrap;gap:6px;margin:20px 0}
.ex-subnav a{padding:9px 15px;border:1px solid var(--edge);border-radius:30px;text-decoration:none;font-size:.9rem}
.ex-subnav a[aria-current=page]{background:var(--sea);color:white}
.ex-map{padding:28px;background:#e8eee7;border:1px solid var(--edge);border-radius:20px}
.ex-map svg{display:block;width:100%;height:auto}
.ex-map svg a:hover rect,.ex-map svg a:focus rect{stroke:#cb673e;stroke-width:3}
.ex-map svg text{font-family:Arial,sans-serif;fill:#164d48}
.ex-map svg .small{font-size:12px;fill:#536d64}
.ex-map svg .center{fill:white}
.ex-map svg rect{fill:#fffdf8;stroke:#bbcfc1}
.ex-map svg .core{fill:#164d48;stroke:#164d48}
.ex-map svg path{fill:none;stroke:#9cb9aa;stroke-width:2}
.ex-map-key{font-size:.82rem;color:var(--quiet)}
.ex-split{display:grid;grid-template-columns:1.35fr 1fr;gap:20px}
.ex-list{padding-left:20px}
.ex-list li{padding-bottom:10px}
.ex-insight{border-left:4px solid var(--coral)}
.ex-insight dl{display:grid;grid-template-columns:110px minmax(0,1fr);gap:12px 20px}
.ex-insight dt{font-size:.8rem;font-weight:800;color:#456458}
.ex-insight dd{margin:0}
.ex-evidence{font-size:.88rem;border-top:1px solid var(--edge);padding-top:16px;margin-top:20px}
.ex-notice{font-size:.85rem;color:var(--quiet);border-left:3px solid #b4c9b7;padding:10px 18px;margin:22px 0}
.ex-metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.ex-metric strong{display:block;font-size:1.15rem}
.ex-metric span{font-size:.8rem;color:var(--quiet)}
.explorer details{border-bottom:1px solid var(--edge);padding:16px 0}
.explorer summary{cursor:pointer;font-weight:700}
.ex-empty{background:#f3eee5;border:1px dashed #b4b7a9;border-radius:12px;padding:18px}
.ex-footer{border-top:1px solid var(--edge);padding:24px 0;color:var(--quiet);font-size:.85rem}
.explorer :focus-visible{outline:3px solid #b35432;outline-offset:5px}
.ex-skip{position:absolute;left:-10000px}
.ex-skip:focus{position:static}
.ex-map-mobile{display:none}
@media(max-width:760px){.ex-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
.ex-split{grid-template-columns:1fr}
.ex-metrics{grid-template-columns:repeat(2,minmax(0,1fr))}
.ex-insight dl{grid-template-columns:1fr;gap:5px}
.ex-insight dd{margin-bottom:16px}
.ex-map{padding:16px}
.ex-map svg{display:none}
.ex-map-mobile{display:grid;gap:12px}
.ex-map-mobile a{padding:14px;background:#fffdf8;border-radius:10px}
.ex-meta{gap:20px}
.ex-section{margin:32px 0}
}
@media(max-width:440px){.ex-grid{grid-template-columns:1fr}
.ex-hero{border-radius:18px}
.ex-card{padding:20px}
.ex-metrics{grid-template-columns:1fr 1fr}
}
@media(prefers-reduced-motion:reduce){.ex-bank{transition:none}
}

"""


def _page(title, body, headers=None, *, active=None, notice=None):
    # Reuse the product shell and its verified account presentation.
    from .web.app import _flora_v2_page, _account_context_html
    from .access import blueprint_upload_authorisation
    notice = notice or (f"Curated public-source pilot · snapshot {GENERATED_DATE}. Source dates vary. "
              "Not accepted canonical intelligence. Figures are historical fixture values; "
              "interpretations and opportunities require validation, not confirmed buying intent.")
    return _flora_v2_page(title, active or 'industries', f"<style>{STYLE}</style><div class='explorer'>"
        "<a class='ex-skip' href='#explorer-content'>Skip to explorer content</a>" + body +
        f"<footer class='ex-footer'>{e(notice)}</footer></div>",
        _account_context_html(blueprint_upload_authorisation(headers or {})))


def _crumb(bank=None, insight=False):
    parts = ["<a href='/'>FLORA</a>", "<a href='/intelligence?tab=industries'>Industries</a>",
             f"<a href='{ROOT}'>Banking</a>"]
    if bank:
        parts.append(f"<a href='{ROOT}/{bank.slug}'>{e(bank.name)}</a>")
    if insight:
        parts.append("<span aria-current='page'>Strategic insights</span>")
    return "<nav class='ex-breadcrumb' aria-label='Breadcrumb'>" + "<span aria-hidden='true'>/</span>".join(parts) + '</nav>'


def _list(items):
    return "<ul class='ex-list'>" + ''.join(f'<li>{e(v)}</li>' for v in items) + '</ul>'


def _map(title, center, nodes):
    """Accessible linked SVG, with equivalent compact navigation on small screens.

    Edges mean conceptual capability/context relationships, never supplier incumbency.
    """
    boxes, paths = [], []
    positions = [
        (16,24),
        (16,124),
        (16,224),
        (560,24),
        (560,124),
        (560,224)
    ]
    for (label, subtitle, href), (x,y) in zip(nodes, positions):
        endpoint = x+224 if x<300 else x
        paths.append(f"<path d='M {endpoint} {y+34} L 400 158'/>")
        boxes.append(f"""<a href='{e(href, quote=True)}' aria-label='{e(label, quote=True)}'>
<rect x='{x}' y='{y}' width='224' height='68' rx='12'/>
<text x='{x+16}' y='{y+29}' font-size='15' font-weight='700'>{e(label)}</text>
<text class='small' x='{x+16}' y='{y+49}'>{e(subtitle)}</text>
</a>""")
    mobile = ''.join(f"<a href='{e(h, quote=True)}'>{e(t)} <span class='ex-kicker'>→ {e(s)}</span></a>" for t,s,h in nodes)
    return f"<div class='ex-map'><svg viewBox='0 0 800 318' role='group' aria-label='{e(title, quote=True)}'>" + ''.join(paths) + f"""<rect class='core' x='280' y='116' width='240' height='84' rx='16'/>
<text class='center' x='400' y='151' text-anchor='middle' font-size='18' font-weight='700'>{e(center)}</text>
<text class='center' x='400' y='176' text-anchor='middle' font-size='12'>Explore the connections</text>""" + ''.join(boxes) + f"</svg><div class='ex-map-mobile' aria-label='{e(title, quote=True)}'>{mobile}</div><p class='ex-map-key'>Select a node to explore. Lines show conceptual relationships, not verified contracts or ownership.</p></div>"


def industry_page(headers=None):
    banks = sorted(BANKS.values(), key=lambda b:b.priority_rank)
    cards = ''.join(f"""<a class='ex-card ex-bank' href='{ROOT}/{b.slug}'>
<span class='ex-monogram' aria-hidden='true'>{e(b.name[0])}</span>
<h3>{e(b.name)}</h3>
<p>{e(b.description)}</p>
<span class='ex-arrow'>Explore enterprise <span aria-hidden='true'>→</span>
</span>
</a>""" for b in banks)
    nodes = [
        ('Customers & channels','Digital + assisted access',ROOT+'#forces'),
        ('Banks & challengers','Explore five enterprises',ROOT+'#enterprises'),
        ('Payments & platforms','Operating ecosystem',ROOT+'#structure'),
        ('Regulators & trust','Resilience + conduct',ROOT+'#forces'),
        ('Technology partners','Supplier context','/flora/banking/competitors'),
        ('Capital & economics','Financial signals','/flora/banking/signals')
    ]
    forces = [
        ('01','Economics & customer value','Margin normalisation and deposit competition sharpen the focus on relationships and measurable returns.','/flora/banking/signals'),
        ('02','Resilience & trust','Operational resilience and conduct obligations constrain how quickly change can move.','/flora/banking/outlook'),
        ('03','Technology & reinvention','Cloud, data and governed AI create options; legacy complexity and benefit proof determine feasibility.','/flora/banking/ai-native')
    ]
    themes = ''.join(f"<article class='ex-card'><span class='ex-kicker'>{n} / Derived interpretation</span><h3>{e(t)}</h3><p>{e(d)}</p><a href='{h}'>Explore the signals →</a></article>" for n,t,d,h in forces)
    body = _crumb() + f"""<section class='ex-hero' id='explorer-content'>
<p class='eyebrow'>Industry explorer / United Kingdom</p>
<h1>Banking.<br>See the bigger picture.</h1>
<p>Follow the forces reshaping banking. Explore the enterprises, connect their operating landscapes and discover where evidence points to opportunity.</p>
<a class='ex-button' href='#enterprises'>Choose an enterprise ↓</a>
<a href='#ecosystem'>Explore the ecosystem</a><p><a href='/flora/banking/research'>Industry Twin research: PESTLE, Five Forces & value chain →</a></p>
<div class='ex-meta'>
<div>
<strong>{len(banks):02}</strong>
<span>Enterprise profiles</span>
</div>
<div>
<strong>03</strong>
<span>Transformation lenses</span>
</div>
<div>
<strong>Public</strong>
<span>Curated source context</span>
</div>
</div>
</section>
<p class='ex-notice'>Reference experience · historical public-source fixtures, not live market intelligence. Financial values retain their reporting period. Interpretations are labelled; opportunities are hypotheses.</p>
<section class='ex-section' id='enterprises'>
<div class='ex-heading'>
<div>
<p class='ex-kicker'>01 / Enterprise explorer</p>
<h2>A sector. Different starting points.</h2>
</div>
<a href='/flora/banking/compare'>Compare bank dossiers →</a>
</div>
<div class='ex-grid'>{cards}</div>
</section>
<section class='ex-section' id='ecosystem'>
<p class='ex-kicker'>02 / Visual landscape</p>
<h2>Banking is an interconnected system.</h2>{_map('Banking industry ecosystem','UK Banking',nodes)}</section>
<section class='ex-section' id='forces'>
<p class='ex-kicker'>03 / Strategic context</p>
<h2>Three lenses on what changes next.</h2>
<div class='ex-grid'>{themes}</div>
</section>
<section class='ex-section ex-split' id='structure'>
<div class='ex-card'>
<p class='ex-kicker'>Industry structure</p>
<h2>Value moves through relationships.</h2>
<p>Retail and commercial banking connect deposits, lending, payments and service. Technology providers and shared infrastructure support those activities within capital, conduct and resilience constraints.</p>
<p class='ex-tag'>Conceptual industry model · not an exhaustive registry</p>
</div>
<div class='ex-card'>
<h3>Go deeper with existing FLORA views</h3>
<p>
<a href='/flora/banking/outlook'>Industry outlook</a>
</p>
<p>
<a href='/flora/banking/pipeline'>Strategic opportunity scenarios</a>
</p>
<p>
<a href='/flora/banking/inspect'>Industry source inspection</a>
</p>
<p>
<a href='/flora/banking'>Detailed Banking research</a>
</p>
</div>
</section>"""
    from .navigation import compatibility_body
    return _page('Banking Industry Explorer | FLORA', compatibility_body(body,'/industries/banking','Banking Explorer context'), headers)


def enterprise_page(slug, headers=None, insights=False):
    bank = BANKS.get(slug)
    if bank is None:
        return _page('Enterprise not available | FLORA', _crumb()+f"<section class='ex-card' id='explorer-content'><h1>Enterprise not available</h1><p>This reference experience contains five curated bank profiles.</p><a href='{ROOT}'>Choose a supported enterprise</a></section>", headers),404
    base = f'{ROOT}/{bank.slug}'
    nav = f"""<nav class='ex-subnav' aria-label='Enterprise exploration'>
<a href='{base}' {'aria-current=page' if not insights else ''}>Overview & landscape</a>
<a href='{base}/insights' {'aria-current=page' if insights else ''}>Strategic insights</a>
<a href='{base}/opportunities'>Opportunity landscape</a>{"<a href='/flora/banking/research/lloyds'>Enterprise research</a>" if slug=='lloyds' else ''}<a href='/flora/sales/pipeline'>Workspace pipeline</a><a href='/flora/banking/{bank.slug}/evidence'>Sources & evidence</a>
<a href='/digital-twins'>Governed Canvas (requires access)</a>
</nav>"""
    hero = f"""<section class='ex-hero' id='explorer-content'>
<p class='eyebrow'>Enterprise explorer / Banking</p>
<h1>{e(bank.name)}</h1>
<p>{e(bank.description)}</p>
<p>{e(bank.footprint)}</p>
<a class='ex-button' href='{base}{'/insights#insight-list' if insights else '#landscape'}'>{'Explore insight cards' if insights else 'Explore operating landscape'} ↓</a>
</section>"""
    if insights:
        content = _insights(bank)
    else:
        metrics = ''.join(f"<div class='ex-card ex-metric'><span>{e(k)}</span><strong>{e(v)}</strong></div>" for k,v in list(bank.metrics.items())[:6])
        nodes = [
            ('Customer & service','Capabilities → insights',base+'/insights'),
            ('Business divisions','Operating structure',base+'#business-model'),
            ('Technology & data','Dependencies + unknowns',base+'#technology'),
            ('Risk & resilience','Transformation hypotheses',base+'/insights'),
            ('Supplier ecosystem','Relationship evidence gaps',base+'#suppliers'),
            ('Strategy & change','Priorities → opportunities',base+'/insights')
        ]
        content = f"""<section class='ex-section'>
<p class='ex-kicker'>Enterprise overview</p>
<div class='ex-split'>
<div>
<h2>The enterprise in context.</h2>
<p>{e(bank.outlook)}</p>
<p class='ex-tag'>FLORA interpretation · validation required</p>
</div>
<div class='ex-card'>
<h3>Strategic priorities</h3>{_list(bank.priorities)}</div>
</div>
</section>
<section class='ex-section'>
<div class='ex-heading'>
<h2>Financial reference points</h2>
<a href='/flora/banking/{bank.slug}/financial-performance'>Full financial view →</a>
</div>
<p class='ex-notice'>Sourced-fixture values, not independently verified here. Scope: {e(bank.name)}. Historical reporting periods shown per metric; do not compare group and UK-only figures as like-for-like.</p>
<div class='ex-metrics'>{metrics}</div>
<p class='ex-evidence'>Source labels: {e('; '.join(bank.analyst_sources))}. <a href='/flora/banking/{bank.slug}/evidence'>Inspect source context and limitations</a>.</p>
</section>
<section class='ex-section' id='landscape'>
<p class='ex-kicker'>Visual intelligence / Conceptual operating landscape</p>
<h2>Connect the business to its dependencies.</h2>{_map(bank.name+' operating landscape','Operating landscape',nodes)}</section>
<section class='ex-section ex-split'>
<div class='ex-card' id='business-model'>
<h2>Business & operating structure</h2>{_list(bank.divisions)}<p>
<strong>Brands:</strong> {e(', '.join(bank.brands))}</p>
<p class='ex-notice'>Public profile structure. Detailed capability ownership and operating relationships are not established by these fixtures.</p>
</div>
<div class='ex-card' id='technology'>
<h2>Technology landscape</h2>
<p>{e(bank.tech_profile)}</p>
<p class='ex-tag'>Profile interpretation · incomplete</p>
<details>
<summary>What remains unknown?</summary>
<p>Verified application inventory, platform ownership, data flows, supplier contracts and current programme status require accepted enterprise evidence.</p>
</details>
</div>
</section>
<section class='ex-section ex-split' id='suppliers'>
<div class='ex-card'>
<h2>Suppliers & partnerships</h2>
<div class='ex-empty'>Verified bank-specific supplier contracts, partner relationships and renewal dates are not established here.</div>
<p>
<a href='/flora/banking/competitors'>Explore industry supplier scenarios →</a>
</p>
<p class='ex-notice'>Market presence does not establish incumbency. Scenario positioning is not a verified enterprise dependency.</p>
</div>
<div class='ex-card'>
<h2>Competitive context</h2>
<p>Explore other banks in the same curated industry set. Their group boundaries and financial reporting scopes differ.</p>{_list_links(bank)}<a href='/flora/banking/compare'>Open existing comparison</a>
</div>
</section>
<section class='ex-section ex-card'>
<p class='ex-kicker'>From landscape to action</p>
<h2>What might this mean for change?</h2>
<p>{e(bank.management_pressure)}</p>
<p class='ex-tag'>Derived interpretation</p>
<p>
<a class='ex-button' href='{base}/insights'>Explore {len(bank.opportunities)} strategic hypotheses →</a>
</p>
<p>Named programme ownership, funding and delivery dates remain unconfirmed. Use the insight cards to identify what evidence is needed next.</p>
</section>"""
    from .navigation import compatibility_body
    body=_crumb(bank,insights)+hero+nav+content
    if not insights:
        body=compatibility_body(body,'/enterprises/'+slug,'Enterprise Explorer context')
    return _page(f'{bank.name} | '+('Strategic Insights' if insights else 'Enterprise Explorer'), body, headers),200


def _list_links(bank):
    return '<ul>'+''.join(f"<li><a href='{ROOT}/{b.slug}'>{e(b.name)}</a></li>" for b in BANKS.values() if b.slug!=bank.slug)+'</ul>'


def _insights(bank):
    cards = []
    for opportunity in bank.opportunities:
        fields = [
            ('Observation', '; '.join(opportunity.signals) + ' — signals recorded in the curated scenario fixture; claim-level source validation is incomplete.'), ('Interpretation', opportunity.problem), ('Implication', opportunity.description), ('Opportunity', opportunity.scope + ' scope hypothesis: ' + ', '.join(opportunity.components))
        ]
        rows = ''.join(f'<dt>{label}</dt><dd>{e(value)}</dd>' for label,value in fields)
        cards.append(f"""<article class='ex-card ex-insight' id='{e(opportunity.id)}'>
<span class='ex-tag hypothesis'>Strategic hypothesis · not a qualified opportunity</span>
<h2>{e(opportunity.title)}</h2><p><a href='{ROOT}/{bank.slug}/opportunities/{opportunity.id}'>Develop this commercial hypothesis →</a></p>
<dl>{rows}</dl>
<div class='ex-evidence'>
<strong>Evidence &amp; confidence</strong>
<p>Source context: {e('; '.join(bank.analyst_sources))}. Claim-level accepted Evidence: not supplied. Editorial conviction: {e(opportunity.conviction)}; not calibrated evidence confidence.</p>
<p>
<a href='/flora/banking/{bank.slug}/evidence'>Inspect source context</a> · <a href='/flora/banking/{bank.slug}/opportunity/{opportunity.id}'>Detailed hypothesis, assumptions & risks</a>
</p>
</div>
<details>
<summary>What would validate or change this insight?</summary>
<p>
<strong>Next step:</strong> {e(opportunity.next_action)}</p>
<h3>Assumptions</h3>{_list(opportunity.assumptions)}<h3>Disconfirming signals</h3>{_list(opportunity.disconfirming)}</details>
</article>""")
    empty = "<p class='ex-empty'>No strategic hypotheses are available for this profile. Validate source evidence before deriving opportunities.</p>"
    return """<section class='ex-section' id='insight-list'>
<p class='ex-kicker'>Strategic insights / Evidence → interpretation → opportunity</p>
<h2>Make the reasoning inspectable.</h2>
<p>These are derived working hypotheses, not customer-confirmed programmes. Expand each card to inspect its assumptions and disconfirming evidence.</p>""" + (''.join(cards) or empty) + f"</section><p><a href='{ROOT}/{bank.slug}#landscape'>← Back to operating landscape</a></p>"
