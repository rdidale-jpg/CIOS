"""Canonical executive presentation over existing Banking research and Pipeline."""
from html import escape as e
from ..banking_portfolio import BANKS
from .model import load_assessment, commercial_candidates
from .visual_specs import build_visual_specs, claim_state
from .visual_templates import STYLE as VISUAL_STYLE, render_visual

ROUTES={'industry':'/industries/banking','enterprise':'/enterprises/lloyds',
        'nodes':'/flora/banking/research/nodes','evidence':'/flora/banking/research/evidence',
        'candidates':'/flora/banking/research/candidates'}
STYLE="""
.ux{--ux-ink:#174d3f;--ux-gold:#9c733c}.ux-breadcrumb{font-size:.85rem;display:flex;flex-wrap:wrap;gap:9px;margin:16px 0 24px}.ux-hero{padding:36px 40px;border-radius:24px;background:linear-gradient(130deg,#174d3f,#235d51);color:#fff;position:relative;overflow:hidden}.ux-hero .eyebrow{color:#c7ddcb}.ux-hero h1{font-size:clamp(2.2rem,4.6vw,4rem);max-width:850px;line-height:1.08}.ux-hero p{max-width:740px;color:#dfebe1}.ux-hero a{color:#174d3f;background:#e6eedf;border-radius:25px;padding:11px 17px;text-decoration:none;display:inline-block;margin:8px 10px 0 0}.ux-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:22px 0}.ux-card{border:1px solid #d2ddcf;background:#fffefa;padding:22px;border-radius:18px;min-width:0}.ux-card h2,.ux-card h3{font-size:1.15rem;margin:10px 0}.ux-card p{font-size:.95rem;color:#53685a}.ux-card .ux-status{font-size:.7rem}.ux-status{display:inline-block;background:#e7eee1;color:#355b44;padding:5px 9px;border-radius:6px;font-size:.76rem;letter-spacing:.03em}.ux-status.uncertain{background:#f4e9d7;color:#775429}.ux-tabs{display:flex;flex-wrap:wrap;gap:7px;padding:18px 0}.ux-tabs a{padding:8px 13px;border:1px solid #c7d4c8;border-radius:20px;text-decoration:none}.ux-tabs a[aria-current]{color:#fff;background:#174d3f}.ux details,.context-tools{border:1px solid #d4ddce;border-radius:15px;margin:18px 0;background:#fffdf8;padding:17px 22px}.ux summary,.context-tools summary{cursor:pointer;font-weight:750;min-height:30px}.ux .ux-fold summary{font-size:1.1rem}.ux-disclosure{font-size:.85rem;color:#647267;margin:14px 0}.ux-actions{display:flex;gap:12px;flex-wrap:wrap}.ux-claim{margin:12px 0;border-top:1px solid #dce3d6;padding-top:14px}.ux-claim p{margin:8px 0}.ux-claim small{color:#647267}.ux-findings h3{line-height:1.45;font-size:1rem}.ux-kicker{color:#6a755f;font-size:.72rem;letter-spacing:.09em;text-transform:uppercase}.ux-section-head{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;gap:10px;margin:32px 0 12px}.ux-section-head h2{margin:0}.ux-rating{display:block;color:#566b5d;font-size:.8rem}.ux-support{border-left:3px solid #b49059;padding-left:16px}.context-tools{font-size:.9rem}.context-tools nav{display:flex;gap:12px;flex-wrap:wrap;margin-top:14px}@media(max-width:1100px){.topbar{flex-wrap:wrap}.primary-nav{order:3;width:100%}.profile-control{margin-left:auto}}@media(max-width:780px){.ux-grid{grid-template-columns:1fr 1fr}.ux-hero{padding:26px}.ux-hero h1{font-size:2.5rem}.ux-tabs a{font-size:.9rem}}@media(max-width:540px){.ux-grid{grid-template-columns:1fr}.ux-hero h1{font-size:2.15rem}.ux details{padding:15px}.ux .ux-section-head h2{font-size:1.4rem}}
"""


def specs(data=None):return build_visual_specs(data or load_assessment(),ROUTES)


def page(title,body,headers=None,active='industries',canonical=''):
    from ..web.app import _flora_v2_page, _account_context_html
    from ..access import blueprint_upload_authorisation
    html=_flora_v2_page(title,active,f"<style>{STYLE}{VISUAL_STYLE}</style><div class='ux'><a class='visually-hidden' href='#content'>Skip to content</a>{body}</div>",_account_context_html(blueprint_upload_authorisation(headers or {})))
    if canonical:html=html.replace('</head>',f"<link rel='canonical' href='{canonical}'></head>",1)
    return html


def breadcrumb(enterprise=False):
    return "<nav class='ux-breadcrumb' aria-label='Breadcrumb'><a href='/'>Home</a> / <a href='/industries'>Industries</a> / <a href='/industries/banking'>Banking</a>"+(" / <span>Lloyds Banking Group</span>" if enterprise else '')+"</nav>"


def home_body():
    return f"<style>{STYLE}</style><div class='ux'><section class='ux-hero' id='content'><p class='eyebrow'>FLORA / Commercial intelligence</p><h1>Understand the landscape.<br>Find your next opening.</h1><p>Move from industry forces to enterprise priorities and evidence-led commercial hypotheses.</p><a href='/industries'>Explore industries →</a><a href='/flora/sales/pipeline'>Open your Pipeline →</a></section><div class='ux-grid'><article class='ux-card'><p class='ux-kicker'>01 / Industry</p><h2>What is changing?</h2><p>Explore external forces, industry structure and the value chain.</p><a href='/industries/banking'>Banking Industry Twin →</a></article><article class='ux-card'><p class='ux-kicker'>02 / Enterprise</p><h2>Where does it matter?</h2><p>Connect supported disclosures to capabilities, programmes and supplier evidence.</p><a href='/enterprises/lloyds'>Lloyds Enterprise Twin →</a></article><article class='ux-card'><p class='ux-kicker'>03 / Opportunity</p><h2>What is worth validating?</h2><p>Inspect commercial priorities, then qualify with customer evidence and user confirmation.</p><a href='/opportunities'>Explore opportunities →</a></article></div></div>"


def catalogue(enterprises=False,headers=None):
    if enterprises:
        cards=''.join(f"<article class='ux-card'><span class='ux-status {'uncertain' if s!='lloyds' else ''}'>{'Primary-source research + historical context' if s=='lloyds' else 'Historical profile; deep research incomplete'}</span><h2>{e(b.name)}</h2><p>{e(b.description)}</p><a href='/enterprises/{s}'>Explore enterprise →</a></article>" for s,b in BANKS.items())
        title='Enterprises';body="<section class='ux-hero' id='content'><p class='eyebrow'>Enterprise intelligence</p><h1>Start with the enterprise.</h1><p>Lloyds is the enriched reference Twin. Other bank profiles retain their historical context and explicit knowledge gaps.</p></section>"
    else:
        title='Industries';cards="<article class='ux-card'><span class='ux-status'>Reference Industry Twin</span><h2>UK Banking</h2><p>Industry forces, value creation, enterprise priorities and commercial research in one coherent view.</p><a href='/industries/banking'>Explore Banking →</a></article>";body="<section class='ux-hero' id='content'><p class='eyebrow'>Industry intelligence</p><h1>See the forces.<br>Follow the implications.</h1><p>Use the same visual research framework across sectors. Banking is the integrated reference experience; additional industries join through the shared specification.</p></section>"
    return page(title,body+f"<div class='ux-grid'>{cards}</div>",headers,active='enterprises' if enterprises else 'industries',canonical='/enterprises' if enterprises else '/industries')


def claim_cards(data,asset,limit=3):
    sources={s['id']:s for s in data['sources']}
    rows=[c for c in data['claims'] if c['asset_id']==asset and c['verification']=='source_supported' and claim_state(data,c) not in {'historical','superseded','unknown','interpretation'}]
    rows.sort(key=lambda c:max(sources[r].get('publication_date') or '' for r in c['source_ids']),reverse=True)
    return "<div class='ux-grid ux-findings'>"+''.join(f"<article class='ux-card'><span class='ux-status'>{e(claim_state(data,c))}</span><h3>{e(c['statement'])}</h3><p class='ux-disclosure'>{e(c['reporting_period'])}</p><a href='{ROUTES['evidence']}/{c['id']}'>Evidence, date & scope →</a></article>" for c in rows[:limit])+"</div>"


def research_fold(data,asset):
    rows=[c for c in data['claims'] if c['asset_id']==asset]
    body=''.join(f"<article class='ux-claim'><span class='ux-status uncertain'>{e(claim_state(data,c))}</span><p>{e(c['statement'])}</p><small>{e(c['reporting_period'])}</small><p><a href='{ROUTES['evidence']}/{c['id']}'>Inspect quotation and source provenance →</a></p></article>" for c in rows)
    return f"<details class='ux-fold'><summary>Evidence, historical observations & research gaps ({len(rows)} claims)</summary><p>Observation period and publication date remain distinct. Historical and superseded intelligence is preserved; inferred relationships never become verified facts.</p>{body}<p><a href='/flora/banking/research/sources'>Source register</a> · <a href='/flora/banking/research/gaps'>Research gaps & next actions</a></p></details>"


def opportunity_cards(data,limit=3):
    rows=commercial_candidates(data)[:limit]
    return "<div class='ux-grid'>"+''.join(f"<article class='ux-card'><span class='ux-status uncertain'>Research priority {r['commercial_rank']} / Unqualified</span><h3>{e(r['title'])}</h3><p>{e(r['commercial']['business_problem'])}</p><span class='ux-rating'>Relevance {r['commercial']['strategic_relevance']['score']}/3 · Access {r['commercial']['commercial_accessibility']['score']}/3 · Evidence {r['commercial']['evidence_maturity']['score']}/3</span><p><strong>Next:</strong> {e(r['commercial']['next_commercial_action'])}</p><a href='{ROUTES['candidates']}/{r['id']}'>Inspect proposition & evidence →</a></article>" for r in rows)+"</div>"


def industry_page(lens='overview',headers=None):
    choices=[('overview','Overview'),('pestle','PESTLE'),('porter','Five Forces'),('value-chain','Value chain')]
    if lens not in dict(choices):raise ValueError('Unknown industry lens')
    data=load_assessment();visuals=specs(data)
    nav="<nav class='ux-tabs' aria-label='Industry views'>"+''.join(f"<a href='/industries/banking?lens={k}' {'aria-current=page' if k==lens else ''}>{label}</a>" for k,label in choices)+"</nav>"
    body=breadcrumb()+"<section class='ux-hero' id='content'><p class='eyebrow'>UK Banking / Industry Twin</p><h1>From external forces<br>to commercial relevance.</h1><p>One view of industry structure, supported disclosures and the enterprise questions they create.</p><a href='/enterprises/lloyds'>Explore Lloyds →</a><a href='/opportunities'>Find opportunity hypotheses →</a></section>"+nav
    if lens=='overview':body+="<div class='ux-section-head'><h2>Key findings</h2><span>Supported disclosures · retain their reporting periods</span></div>"+claim_cards(data,data['industry_twin_id'])
    kind={'overview':'pestle','pestle':'pestle','porter':'five-forces','value-chain':'value-chain'}[lens]
    body+=render_visual(visuals[kind])
    if lens!='overview':
        selected=[r for r in data['frameworks'] if r['lens']=={'pestle':'pestle','porter':'porter','value-chain':'value-chain'}[lens]]
        body+="<details class='ux-fold'><summary>Interpretation, affected capabilities & evidence</summary>"+''.join(f"<article class='ux-claim'><h3>{e(r['title'])}</h3><p>{e(r['assessment'])}</p><a href='{ROUTES['nodes']}/{r['id']}'>Follow capabilities, evidence & opportunities →</a></article>" for r in selected)+"</details>"
    body+="<div class='ux-section-head'><h2>Enterprise landscape</h2><a href='/enterprises'>All enterprises →</a></div><div class='ux-grid'>"+''.join(f"<article class='ux-card'><span class='ux-status'>{'Enriched reference Twin' if s=='lloyds' else 'Historical supporting profile'}</span><h3>{e(b.name)}</h3><a href='/enterprises/{s}'>Explore enterprise →</a></article>" for s,b in BANKS.items())+"</div><div class='ux-section-head'><h2>Commercial implications</h2><a href='/opportunities'>All hypotheses →</a></div>"+opportunity_cards(data)+research_fold(data,data['industry_twin_id'])+"<details><summary>Supporting research & legacy intelligence</summary><p><a href='/flora/banking'>Historical Banking portfolio</a> · <a href='/flora/banking/explorer'>Earlier Explorer</a> · <a href='/flora/banking/research'>Detailed research lenses</a> · <a href='/industries/banking/visual-specs'>Structured visual specifications (JSON)</a></p><p>These views preserve historical source material and scenarios. They are supporting records, not competing current Banking home pages.</p></details>"
    return page('Banking Industry Twin',body,headers,canonical=ROUTES['industry'])


def enterprise_page(slug='lloyds',lens='operating-model',headers=None):
    if slug not in BANKS:raise ValueError('Unknown enterprise')
    if lens not in ('operating-model','ecosystem','opportunities'):raise ValueError('Unknown enterprise lens')
    bank=BANKS[slug]
    if slug!='lloyds':
        return page(bank.name,breadcrumb()+f"<section class='ux-hero' id='content'><p class='eyebrow'>Historical supporting profile</p><h1>{e(bank.name)}</h1><p>{e(bank.description)}</p><a href='/flora/banking/explorer/{slug}'>Open existing profile & historical sources →</a></section><p>Deep primary-source research, capabilities and current supplier relationships are incomplete. No new facts are inferred.</p>",headers,'enterprises','/enterprises/'+slug)
    data=load_assessment();visuals=specs(data)
    tabs="<nav class='ux-tabs' aria-label='Enterprise views'>"+''.join(f"<a href='/enterprises/lloyds?lens={k}' {'aria-current=page' if lens==k else ''}>{label}</a>" for k,label in [('operating-model','Operating landscape'),('ecosystem','Supplier & technology ecosystem'),('opportunities','Opportunity landscape')])+"</nav>"
    body=breadcrumb(True)+"<section class='ux-hero' id='content'><p class='eyebrow'>Lloyds Banking Group / Enterprise Twin</p><h1>Connect strategy<br>to a credible opening.</h1><p>Follow supported disclosures through capabilities, transformation priorities and evidence-led commercial hypotheses.</p><a href='/opportunities'>Inspect commercial priorities →</a></section>"+tabs+render_visual(visuals[lens])+"<div class='ux-section-head'><h2>Key findings & important changes</h2><span>Actuals, expectations and proposals are labelled separately</span></div>"+claim_cards(data,data['enterprise_twin_id'])+"<div class='ux-section-head'><h2>Where to validate next</h2><a href='/opportunities'>All hypotheses →</a></div>"+opportunity_cards(data)
    programme=''.join(f"<article class='ux-claim'><h3>{e(p['title'])}</h3><p>{e(p['current_phase'])}</p><p>Owner: {e(p['owner'])} · Funding: {e(p['funding'])} · Procurement: {e(p['procurement'])}</p><a href='{ROUTES['nodes']}/{p['id']}'>Programme evidence and commercial questions →</a></article>" for p in data['programmes'])
    body+=f"<details class='ux-fold'><summary>Programmes & investment signals</summary><p>Reported management priorities are not customer-verified buying demand.</p>{programme}</details>"+research_fold(data,data['enterprise_twin_id'])+"<details><summary>Historical profiles & specialist analysis</summary><p><a href='/flora/banking/explorer/lloyds'>Historical Explorer</a> · <a href='/flora/banking/research/lloyds'>Full research dossier</a> · <a href='/flora/banking/lloyds/financial-performance'>Historical financial intelligence</a> · <a href='/digital-twins'>Governed Canvas (destination permissions apply)</a></p></details>"
    return page('Lloyds Enterprise Twin',body,headers,'enterprises',ROUTES['enterprise'])


def opportunities_body():
    data=load_assessment()
    return f"<style>{STYLE}{VISUAL_STYLE}</style><div class='ux'>{breadcrumb(True)}<section class='ux-hero' id='content'><p class='eyebrow'>Commercial opportunity discovery</p><h1>Prioritise the question.<br>Earn the qualification.</h1><p>Public research supports relevance. Customer evidence establishes need, access and a qualified opportunity. No budget or buying intent is inferred.</p><a href='/flora/sales/pipeline'>Open authorised Pipeline →</a></section>{opportunity_cards(data)}<details class='ux-fold'><summary>Full ranked opportunity landscape ({len(data['candidates'])} hypotheses)</summary>{render_visual(specs(data)['opportunities'])}</details><p><a href='/flora/banking/research/opportunities'>Detailed reassessment, historical hypotheses and qualification gaps →</a></p></div>"
