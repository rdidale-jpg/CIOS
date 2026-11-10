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
.ux{--ux-ink:#174d3f;--ux-gold:#9c733c}.ux-breadcrumb{font-size:.85rem;display:flex;flex-wrap:wrap;gap:9px;margin:16px 0 24px}.ux-hero{padding:36px 40px;border-radius:24px;background:linear-gradient(130deg,#174d3f,#235d51);color:#fff;position:relative;overflow:hidden}.ux-hero .eyebrow{color:#c7ddcb}.ux-hero h1{font-size:clamp(2.2rem,4.6vw,4rem);max-width:850px;line-height:1.08}.ux-hero p{max-width:740px;color:#dfebe1}.ux-hero a{color:#174d3f;background:#e6eedf;border-radius:25px;padding:11px 17px;text-decoration:none;display:inline-block;margin:8px 10px 0 0}.ux-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:22px 0}.ux-industry-catalogue{grid-template-columns:repeat(2,minmax(0,1fr))}.ux-card{border:1px solid #d2ddcf;background:#fffefa;padding:22px;border-radius:18px;min-width:0}.ux-card h2,.ux-card h3{font-size:1.15rem;margin:10px 0}.ux-card p{font-size:.95rem;color:#53685a}.ux-card .ux-status{font-size:.7rem}.ux-status{display:inline-block;background:#e7eee1;color:#355b44;padding:5px 9px;border-radius:6px;font-size:.76rem;letter-spacing:.03em}.ux-status.uncertain{background:#f4e9d7;color:#775429}.ux-tabs{display:flex;flex-wrap:wrap;gap:7px;padding:18px 0}.ux-tabs a{padding:8px 13px;border:1px solid #c7d4c8;border-radius:20px;text-decoration:none}.ux-tabs a[aria-current]{color:#fff;background:#174d3f}.ux details,.context-tools{border:1px solid #d4ddce;border-radius:15px;margin:18px 0;background:#fffdf8;padding:17px 22px}.ux summary,.context-tools summary{cursor:pointer;font-weight:750;min-height:30px}.ux .ux-fold summary{font-size:1.1rem}.ux-disclosure{font-size:.85rem;color:#647267;margin:14px 0}.ux-actions{display:flex;gap:12px;flex-wrap:wrap}.ux-claim{margin:12px 0;border-top:1px solid #dce3d6;padding-top:14px}.ux-claim p{margin:8px 0}.ux-claim small{color:#647267}.ux-findings h3{line-height:1.45;font-size:1rem}.ux-kicker{color:#6a755f;font-size:.72rem;letter-spacing:.09em;text-transform:uppercase}.ux-section-head{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;gap:10px;margin:32px 0 12px}.ux-section-head h2{margin:0}.ux-rating{display:block;color:#566b5d;font-size:.8rem}.ux-support{border-left:3px solid #b49059;padding-left:16px}.context-tools{font-size:.9rem}.context-tools nav{display:flex;gap:12px;flex-wrap:wrap;margin-top:14px}@media(max-width:1100px){.topbar{flex-wrap:wrap}.primary-nav{order:3;width:100%}.profile-control{margin-left:auto}}@media(max-width:780px){.ux-grid{grid-template-columns:1fr 1fr}.ux-hero{padding:26px}.ux-hero h1{font-size:2.5rem}.ux-tabs a{font-size:.9rem}}@media(max-width:540px){.ux-grid{grid-template-columns:1fr}.ux-hero h1{font-size:2.15rem}.ux details{padding:15px}.ux .ux-section-head h2{font-size:1.4rem}}
"""


def routes_for(data):
    from .registry import DOMAINS
    domain=data.get('research_domain','banking');root=DOMAINS[domain][2];slug=data.get('enterprise_slug',DOMAINS[domain][1])
    return {'industry':'/industries/'+domain,'enterprise':'/enterprises/'+slug,
            'evidence':root+'/evidence','nodes':root+'/nodes','candidates':root+'/candidates','opportunities':'/opportunities'}


def specs(data=None):
    data=data or load_assessment()
    return build_visual_specs(data,routes_for(data))


def page(title,body,headers=None,active='industries',canonical=''):
    from ..web.app import _flora_v2_page, _account_context_html
    from ..access import blueprint_upload_authorisation
    html=_flora_v2_page(title,active,f"<style>{STYLE}{VISUAL_STYLE}</style><div class='ux'><a class='visually-hidden' href='#content'>Skip to content</a>{body}</div>",_account_context_html(blueprint_upload_authorisation(headers or {})))
    if canonical:html=html.replace('</head>',f"<link rel='canonical' href='{canonical}'></head>",1)
    return html


def breadcrumb(enterprise=False,data=None):
    data=data or load_assessment();r=routes_for(data)
    return f"<nav class='ux-breadcrumb' aria-label='Breadcrumb'><a href='/'>Home</a> / <a href='/industries'>Industries</a> / <a href='{r['industry']}'>{e(data['industry_name'])}</a>"+(f" / <a href='{r['enterprise']}'>{e(data['enterprise_name'])}</a>" if enterprise else '')+"</nav>"


def home_body():
    return f"<style>{STYLE}</style><div class='ux'><section class='ux-hero' id='content'><p class='eyebrow'>FLORA / Commercial intelligence</p><h1>Understand the landscape.<br>Find your next opening.</h1><p>Move from industry forces to enterprise priorities and evidence-led commercial hypotheses.</p><a href='/industries'>Explore industries →</a><a href='/flora/sales/pipeline'>Open your Pipeline →</a></section><div class='ux-grid'><article class='ux-card'><p class='ux-kicker'>01 / Industry</p><h2>What is changing?</h2><p>Explore forces and value chains through the same visual language.</p><p><a href='/industries/banking'>Banking Industry Twin →</a></p><a href='/industries/aviation'>Aviation Industry Twin →</a></article><article class='ux-card'><p class='ux-kicker'>02 / Enterprise</p><h2>Where does it matter?</h2><p>Connect supported disclosures to capabilities, programmes and supplier evidence.</p><p><a href='/enterprises/lloyds'>Lloyds Enterprise Twin →</a></p><a href='/enterprises/easyjet'>easyJet Enterprise Twin →</a></article><article class='ux-card'><p class='ux-kicker'>03 / Opportunity</p><h2>What is worth validating?</h2><p>Inspect commercial priorities, then qualify with customer evidence and user confirmation.</p><a href='/opportunities'>Explore opportunities →</a></article></div></div>"


def catalogue(enterprises=False,headers=None):
    from .registry import DOMAINS
    cards=[]
    for domain,(name,slug,root) in DOMAINS.items():
        d=load_assessment(domain)
        cards.append(f"<article class='ux-card'><span class='ux-status'>Public research / qualification outstanding</span><h2>{e(d['enterprise_name'] if enterprises else name)}</h2><p>{e(name)} · industry forces, capabilities and evidence-led opportunities.</p><a href='{'/enterprises/'+slug if enterprises else '/industries/'+domain}'>Explore {e(d['enterprise_name'] if enterprises else name.replace('UK ','').replace('Commercial ',''))} →</a><details><summary>Supporting research</summary><a href='{root}'>Earlier research entry</a></details></article>")
    if enterprises:
        for slug,b in BANKS.items():
            if slug=='lloyds':continue
            cards.append(f"<article class='ux-card'><span class='ux-status uncertain'>Historical profile; deep research incomplete</span><h2>{e(b.name)}</h2><p>{e(b.description)}</p><a href='/enterprises/{slug}'>Explore enterprise →</a></article>")
    title='Enterprises' if enterprises else 'Industries'
    hero="Start with the enterprise." if enterprises else "See the forces.<br>Follow the implications."
    return page(title,f"<section class='ux-hero' id='content'><p class='eyebrow'>{title} / FLORA</p><h1>{hero}</h1><p>Banking and Aviation. One visual research framework, with source limitations and sector terminology preserved.</p></section><div class='ux-grid {'ux-industry-catalogue' if not enterprises else ''}'>{''.join(cards)}</div>",headers,'enterprises' if enterprises else 'industries','/enterprises' if enterprises else '/industries')


def provenance_notice(data):
    sources=data['sources'];indexed=[s for s in sources if 'search-index' in s.get('retrieval_extent','')]
    pending=sum(s['verification']=='citation_only' for s in sources)
    note=f"<p>Assessment {e(data['assessed_at'])}. Source dates and reporting periods differ. Public disclosures support research, not customer demand.</p>"
    if indexed:note+=f"<p><strong>{len(indexed)} official search-index excerpts only; original documents not directly verified.</strong> "+e('; '.join(s['title'] for s in indexed))+".</p>"
    if pending:note+=f"<p>{pending} source citations still require primary verification. See source register and research gaps.</p>"
    return "<aside class='ux-card ux-support'>"+note+"</aside>"


def claim_cards(data,asset,limit=3):
    r=routes_for(data);sources={s['id']:s for s in data['sources']}
    rows=[c for c in data['claims'] if c['asset_id']==asset and c['verification']=='source_supported' and claim_state(data,c) not in {'historical','superseded','unknown','interpretation'}]
    rows.sort(key=lambda c:max(sources[s].get('publication_date') or '' for s in c['source_ids']),reverse=True)
    return "<div class='ux-grid ux-findings'>"+''.join(f"<article class='ux-card'><span class='ux-status'>{e(claim_state(data,c))}</span><h3>{e(c['statement'])}</h3><p class='ux-disclosure'>{e(c['reporting_period'])}</p><a href='{r['evidence']}/{c['id']}'>Evidence, date & scope →</a></article>" for c in rows[:limit])+"</div>"


def research_fold(data,asset):
    r=routes_for(data);root=r['evidence'].rsplit('/',1)[0];rows=[c for c in data['claims'] if c['asset_id']==asset]
    body=''.join(f"<article class='ux-claim'><span class='ux-status uncertain'>{e(claim_state(data,c))}</span><p>{e(c['statement'])}</p><small>{e(c['reporting_period'])}</small><p><a href='{r['evidence']}/{c['id']}'>Inspect quotation and source provenance →</a></p></article>" for c in rows)
    return f"<details class='ux-fold'><summary>Evidence, historical observations & research gaps ({len(rows)} claims)</summary><p>Observation period and publication date remain distinct. Historical and superseded intelligence is preserved; inferred relationships never become verified facts.</p>{body}<p><a href='{root}/sources'>Source register</a> · <a href='{root}/gaps'>Research gaps & next actions</a></p></details>"


def opportunity_cards(data,limit=3):
    from .model import commercial_dimensions
    r=routes_for(data);rows=commercial_candidates(data)[:limit]
    labels={'strategic_relevance':'Relevance','commercial_accessibility':'Access','evidence_maturity':'Evidence','seller_fit':'Seller fit'}
    cards=[]
    for row in rows:
        c=row['commercial'];ratings=' · '.join(f"{labels[k]} {c[k]['score']}/3" for k in commercial_dimensions(data))
        cards.append(f"<article class='ux-card'><span class='ux-status uncertain'>Research priority {row['commercial_rank']} / Unqualified</span><h3>{e(row['title'])}</h3><p>{e(c['business_problem'])}</p><span class='ux-rating'>{ratings}</span><p><strong>Next:</strong> {e(c['next_commercial_action'])}</p><a href='{r['candidates']}/{row['id']}'>Inspect proposition & evidence →</a></article>")
    return "<div class='ux-grid'>"+''.join(cards)+"</div>"


def enterprise_cards(data):
    from .registry import enterprise_reference
    slugs=list(BANKS) if data.get('research_domain','banking')=='banking' else [data['enterprise_slug']]
    return "<div class='ux-grid'>"+''.join(f"<article class='ux-card'><span class='ux-status'>{'Enriched reference Twin' if s==data.get('enterprise_slug','lloyds') else 'Historical supporting profile'}</span><h3>{e(enterprise_reference(s).name)}</h3><a href='/enterprises/{s}'>Explore enterprise →</a></article>" for s in slugs)+"</div>"


def industry_page(lens='overview',headers=None,domain='banking'):
    choices=[('overview','Overview'),('pestle','PESTLE'),('porter','Five Forces'),('value-chain','Value chain'),('ai-disruption','AI disruption')]
    if lens not in dict(choices):raise ValueError('Unknown industry lens')
    d=load_assessment() if domain=='banking' else load_assessment(domain);r=routes_for(d);root=r['evidence'].rsplit('/',1)[0]
    nav="<nav class='ux-tabs' aria-label='Industry views'>"+''.join(f"<a href='{r['industry']}?lens={k}' {'aria-current=page' if k==lens else ''}>{label}</a>" for k,label in choices)+"</nav>"
    short=d['industry_name'].replace('UK ','').replace('Commercial ','')
    body=breadcrumb(data=d)+f"<section class='ux-hero' id='content'><p class='eyebrow'>{e(d['industry_name'])} / Industry Twin</p><h1>{e(short)}.<br>From forces to commercial relevance.</h1><p>One view of industry structure, supported disclosures and the enterprise questions they create.</p><a href='{r['enterprise']}'>Explore {e(d['enterprise_name'].replace(' Banking Group',''))} →</a><a href='/opportunities#opportunities-{domain}'>Find opportunity hypotheses →</a></section>"+nav
    if lens in ('overview','ai-disruption'):
        from .visual_intelligence import render_intelligence
        from .visual_specs import build_intelligence_specs
        body=breadcrumb(data=d)+f"<header class='vi-page-head' id='content'><p class='ux-kicker'>Industry Twin / {e(d['industry_name'])}</p><h1>{e(short)}. The whole landscape.</h1><p>Understand the participants, explore the structural forces, investigate the evidence.</p></header>"+nav+render_intelligence(build_intelligence_specs(d)['industry-signature'],lens)
    if lens=='overview':body+="<div class='ux-section-head'><h2>Key findings</h2><span>Supported disclosures · retain their reporting periods</span></div>"+claim_cards(d,d['industry_twin_id'])
    body+="<p class='ux-disclosure'>Analyst interpretation · conceptual frameworks, not verified enterprise ownership or buying demand.</p>"
    kind={'overview':'pestle','pestle':'pestle','porter':'five-forces','value-chain':'value-chain','ai-disruption':'pestle'}[lens];body+=("<details><summary>Existing PESTLE diagram</summary>"+render_visual(specs(d)[kind])+"</details>" if lens in ('overview','ai-disruption') else render_visual(specs(d)[kind]))
    rows=[f for f in d['frameworks'] if f['lens']=={'overview':'pestle','pestle':'pestle','porter':'porter','value-chain':'value-chain','ai-disruption':'pestle'}[lens]]
    body+="<details class='ux-fold'><summary>Interpretation, affected capabilities & evidence</summary>"+''.join(f"<article class='ux-claim'><h3>{e(f['title'])}</h3><p>{e(f['assessment'])}</p><a href='{r['nodes']}/{f['id']}'>Follow capabilities, evidence & opportunities →</a></article>" for f in rows)+"</details>"
    body+="<div class='ux-section-head'><h2>Enterprise landscape</h2><a href='/enterprises'>All enterprises →</a></div>"+enterprise_cards(d)+"<h2>Commercial implications</h2>"+opportunity_cards(d)+provenance_notice(d)+research_fold(d,d['industry_twin_id'])
    body+=f"<details><summary>Supporting research & legacy intelligence</summary><p><a href='{root}'>Detailed research entry</a> · <a href='{r['industry']}/visual-specs'>Structured visual specifications (JSON)</a></p>"+("<p><a href='/flora/banking'>Historical Banking portfolio</a> · <a href='/flora/banking/explorer'>Earlier Explorer</a></p>" if domain=='banking' else '')+"</details>"
    return page(d['industry_name']+' Industry Twin',body,headers,canonical=r['industry'])


def enterprise_page(slug='lloyds',lens='operating-model',headers=None):
    from .registry import enterprise_domain,enterprise_reference
    bank=enterprise_reference(slug)
    if bank is None:raise ValueError('Unknown enterprise')
    if lens not in ('operating-model','ecosystem','opportunities','timeline'):raise ValueError('Unknown enterprise lens')
    if slug in BANKS and slug!='lloyds':
        return page(bank.name,breadcrumb()+f"<section class='ux-hero' id='content'><p class='eyebrow'>Historical supporting profile</p><h1>{e(bank.name)}</h1><p>{e(bank.description)}</p><a href='/flora/banking/explorer/{slug}'>Open existing profile & historical sources →</a></section><p>Deep primary-source research, capabilities and current supplier relationships are incomplete. No new facts are inferred.</p>",headers,'enterprises','/enterprises/'+slug)
    domain=enterprise_domain(slug);d=load_assessment() if domain=='banking' else load_assessment(domain);r=routes_for(d);root=r['evidence'].rsplit('/',1)[0]
    tabs="<nav class='ux-tabs' aria-label='Enterprise views'>"+''.join(f"<a href='{r['enterprise']}?lens={k}' {'aria-current=page' if lens==k else ''}>{label}</a>" for k,label in [('operating-model','How it works'),('timeline','Strategic timeline'),('ecosystem','Supplier & technology ecosystem'),('opportunities','Opportunity landscape')])+"</nav>"
    body=breadcrumb(True,d)+f"<section class='ux-hero' id='content'><p class='eyebrow'>{e(d['enterprise_name'])} / Enterprise Twin</p><h1>{e(d['enterprise_name'].replace(' Banking Group',''))}.<br>Connect strategy to a credible opening.</h1><p>Follow supported disclosures through capabilities, transformation priorities and evidence-led commercial hypotheses.</p><a href='/opportunities#opportunities-{domain}'>Inspect commercial priorities →</a></section>"+tabs
    from .visual_intelligence import render_intelligence
    from .visual_specs import build_intelligence_specs
    if lens in ('operating-model','timeline'):
        body=breadcrumb(True,d)+f"<header class='vi-page-head' id='content'><p class='ux-kicker'>Enterprise Twin / {e(d['industry_name'])}</p><h1>{e(d['enterprise_name'])}.</h1><p>How the business works. What is changing. Where the evidence leads.</p></header>"+tabs
        body+=render_intelligence(build_intelligence_specs(d)['enterprise-story' if lens=='operating-model' else 'strategic-timeline'])
        if lens=='operating-model':body+="<details><summary>Existing capability map</summary>"+render_visual(specs(d)['operating-model'])+"</details>"
    else:body+=render_visual(specs(d)[lens])
    body+="<h2>Key findings & important changes</h2>"+claim_cards(d,d['enterprise_twin_id'])+provenance_notice(d)+"<h2>Where to validate next</h2>"+opportunity_cards(d)
    programme=''.join(f"<article class='ux-claim'><h3>{e(p['title'])}</h3><p>{e(p['current_phase'])}</p><p>Owner: {e(p['owner'])} · Funding: {e(p['funding'])} · Procurement: {e(p['procurement'])}</p><a href='{r['nodes']}/{p['id']}'>Programme evidence and commercial questions →</a></article>" for p in d['programmes'])
    body+=f"<p><a href='/enterprises/{slug}/understanding'>Enterprise Understanding — evidence quality and explainable relationships →</a></p>"
    body+=f"<p><a href='/enterprises/{slug}/research-diagnostic'>Research Intelligence Diagnostic — evidence coverage and prioritised gaps →</a></p>"
    body+=f"<details class='ux-fold'><summary>Programmes & investment signals</summary><p>Reported management priorities are not customer-verified buying demand.</p>{programme}</details>"+research_fold(d,d['enterprise_twin_id'])+f"<details><summary>Supporting research & specialist analysis</summary><p><a href='{root}/{slug}'>Full research dossier</a> · <a href='/digital-twins'>Governed Canvas (destination permissions apply)</a></p></details>"
    return page(d['enterprise_name']+' Enterprise Twin',body,headers,'enterprises',r['enterprise'])


def opportunities_body(domain=None):
    from .registry import DOMAINS
    if domain is not None and domain not in DOMAINS:raise ValueError('Unknown industry')
    blocks=[]
    for key in ([domain] if domain else DOMAINS):
        d=load_assessment() if key=='banking' else load_assessment(key);r=routes_for(d)
        blocks.append(f"<section id='opportunities-{key}'><h2>{e(d['industry_name'])} / {e(d['enterprise_name'])}</h2><p>Within-enterprise research rank; no cross-industry aggregate score.</p>{opportunity_cards(d)}<details class='ux-fold'><summary>Full ranked opportunity landscape ({len(d['candidates'])} hypotheses)</summary>{render_visual(specs(d)['opportunities'])}</details><p><a href='{r['enterprise']}'>Return to {e(d['enterprise_name'])} →</a> · <a href='{r['evidence'].rsplit('/',1)[0]}/gaps'>Qualification and research gaps</a></p></section>")
    tabs="<nav class='ux-tabs' aria-label='Opportunity sectors'>"+''.join(f"<a href='#opportunities-{k}'>{e(DOMAINS[k][0])}</a>" for k in ([domain] if domain else DOMAINS))+"</nav>"
    return f"<style>{STYLE}{VISUAL_STYLE}</style><div class='ux'><section class='ux-hero' id='content'><p class='eyebrow'>Commercial opportunity discovery</p><h1>Prioritise the question.<br>Earn the qualification.</h1><p>Public research supports relevance. Customer evidence establishes need, access and a qualified opportunity. No budget or buying intent is inferred.</p><a href='/flora/sales/pipeline'>Open authorised Pipeline →</a></section>{tabs}{''.join(blocks)}</div>"
