"""Data-driven cross-industry research presentation in the existing FLORA shell.

Uses the shared evidence spine, graph links, ranking and Pipeline capture. Sector
content belongs in registered overlays, not new applications or permission rules.
"""
from html import escape as e
from .registry import DOMAINS
from .model import (load_assessment, commercial_candidates, commercial_dimensions,
                    claim_segment, candidate_claim, evidence_item, _index)
from .views import STYLE, claims_html, edges_html, links, href
from ..banking_explorer import _page, _map
from ..sales_views import capture_controls

VISUAL_STYLE = """
.twin-metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:24px 0}.twin-metrics a{padding:22px;border:1px solid #c6d6c9;border-radius:16px;background:#edf3e9;text-decoration:none}.twin-metrics strong{display:block;font-size:2rem;color:#164d48}.twin-score{display:flex;flex-wrap:wrap;gap:8px}.twin-score span{padding:7px 10px;background:#eef2e8;border-radius:6px;font-size:.85rem}.twin-flow{background:linear-gradient(135deg,#e9f0e5,#fff8ec);border:1px solid #c8d6c7;border-radius:20px;padding:18px;margin:20px 0}.twin-flow svg{width:100%;height:auto}.twin-flow svg a:hover rect,.twin-flow svg a:focus rect{fill:#d6e7ce;stroke:#164d48;stroke-width:3}.twin-flow svg text{font-family:inherit;fill:#164d48}.twin-flow svg .sub{font-size:12px;fill:#5d7064}.twin-flow svg .heading{font-size:14px;font-weight:700}.twin-flow svg .step{font-size:12px;fill:#957044}.twin-flow-nav{display:flex;flex-wrap:wrap;gap:10px}.twin-flow-nav a{border:1px solid #b8cbb9;border-radius:20px;padding:8px 12px;font-size:.85rem}.twin-sector-cards{display:grid;grid-template-columns:1fr 1fr;gap:24px}.twin-sector-cards a{text-decoration:none}.twin-sector-cards .ex-card{height:100%;box-sizing:border-box}.twin-sector-cards strong{font-size:2rem;color:#164d48}.twin-callout{padding:22px;border-left:4px solid #b47d40;background:#fff1df;border-radius:12px}.twin-legend{font-size:.85rem;color:#5b6a5e}.research summary{min-height:32px}.research h1{overflow-wrap:anywhere}@media(max-width:600px){.twin-metrics,.twin-sector-cards{grid-template-columns:1fr}.twin-flow{padding:8px}.twin-flow svg{display:none}.twin-flow-nav{display:grid;grid-template-columns:1fr 1fr}.twin-score{display:grid;grid-template-columns:1fr 1fr}}
"""


def shell(data, title, body, headers=None):
    root=data['route_root']; slug=data['enterprise_slug']
    nav=[(root,'Industry Twin'),(root+'/'+slug,data['enterprise_name']+' Twin'),
         (root+'/opportunities','Opportunity landscape'),(root+'/sources','Sources'),(root+'/gaps','Research gaps')]
    crumbs=f"<nav class='ex-breadcrumb' aria-label='Breadcrumb'><a href='/'>FLORA</a> / <a href='/flora/industries'>Industries</a> / <a href='{root}'>{e(data['industry_name'])}</a> / <span>{e(title)}</span></nav>"
    controls="<nav class='research-nav' aria-label='Research navigation'>"+''.join(f"<a href='{u}'>{e(t)}</a>" for u,t in nav)+"</nav>"
    notice=f"Public research candidate · assessed {data['assessed_at']}. Reporting periods differ. Short reviewed excerpts, not archived originals. Interpretations are not sourced facts; hypotheses are not customer demand."
    return _page(title,f"<style>{STYLE}{VISUAL_STYLE}</style><div class='research'>{crumbs}{controls}{body}</div>",headers,notice=notice)


def catalogue(headers=None):
    cards=''.join(f"<a href='{root}'><article class='ex-card'><p class='ex-kicker'>Industry → Enterprise → Opportunity</p><strong>{e(name)}</strong><p>{'Lloyds Banking Group' if slug=='lloyds' else 'easyJet'} reference enterprise</p><p>Industry forces, operating model, primary evidence and commercial research priorities.</p><span class='ex-button'>Explore Twin →</span></article></a>" for name,slug,root in DOMAINS.values())
    return _page('Industry Twins',f"<style>{VISUAL_STYLE}</style><section class='ex-hero' id='explorer-content'><p class='eyebrow'>FLORA / Cross-industry intelligence</p><h1>Understand the industry.<br>Find a credible opening.</h1><p>One research method. Distinct sector economics. Evidence before opportunity.</p></section><div class='twin-sector-cards'>{cards}</div>",headers,notice='Public research candidates. Banking and Aviation use the same evidence, graph and qualification contracts. No customer demand is inferred.')


def operating_model(data):
    """Reusable eight-activity SVG with keyboard links and mobile equivalents."""
    rows=[r for r in data['frameworks'] if r['lens']=='value-chain']
    root=data.get('route_root','/flora/banking/research');nodes=[];paths=[]
    for index,row in enumerate(rows):
        x=20+(index%4)*235;y=54+(index//4)*140
        title=row['title'];parts=title.split(' & ')
        if len(parts)==1:parts=[title,'']
        else:parts=[parts[0]+' &',' & '.join(parts[1:])]
        nodes.append(f"<a href='{root}/nodes/{row['id']}' aria-label='{e(title,quote=True)}'><title>{e(title)} — inspect claims, capabilities and opportunities</title><rect x='{x}' y='{y}' width='215' height='102' rx='14' fill='#fffdf6' stroke='#a6bca7'/><text class='step' x='{x+16}' y='{y+23}'>{index+1:02} / VALUE ACTIVITY</text><text class='heading' x='{x+16}' y='{y+49}'>{e(parts[0])}</text><text class='heading' x='{x+16}' y='{y+69}'>{e(parts[1])}</text><text class='sub' x='{x+16}' y='{y+88}'>Evidence & dependencies →</text></a>")
        if index%4<3: paths.append(f"<path d='M{x+216} {y+51} h18' stroke='#a5b9a1' stroke-dasharray='4 4' fill='none'/>")
    mobile="<nav class='twin-flow-nav' aria-label='Operating model activities'>"+''.join(f"<a href='{root}/nodes/{r['id']}'>{i+1:02} · {e(r['title'])}</a>" for i,r in enumerate(rows))+'</nav>'
    return "<div class='twin-flow'><svg viewBox='0 0 960 322' role='group' aria-labelledby='operating-title operating-desc'><title id='operating-title'>Enterprise operating model</title><desc id='operating-desc'>Conceptual value activities. Select an activity to inspect evidence and its linked capabilities. Dashed connectors show analytical flow, not verified contracts.</desc><text x='24' y='27' class='heading'>CUSTOMER & OPERATIONAL VALUE FLOW</text>"+''.join(paths+nodes)+"</svg>"+mobile+"<p class='twin-legend'>Dashed flow = conceptual sequence, not verified ownership or a system integration. Supporting technology, supplier and opportunity links open inside each activity.</p></div>"


def industry(data, lens='pestle', headers=None):
    if lens not in ('pestle','porter','value-chain'):raise ValueError('Unknown lens')
    root=data['route_root'];rows=[r for r in data['frameworks'] if r['lens']==lens]
    tabs="<nav class='research-nav' aria-label='Industry lenses'>"+''.join(f"<a href='{root}?lens={key}' {'aria-current=page' if key==lens else ''}>{text}</a>" for key,text in [('pestle','PESTLE'),('porter','Five Forces'),('value-chain','Value chain')])+"</nav>"
    hero=f"<section class='ex-hero' id='explorer-content'><p class='eyebrow'>Industry Twin / {data['industry_twin_id']}</p><h1>Aviation.<br>Connect the whole journey.</h1><p>Commercial flight depends on a tightly coupled ecosystem. Explore the forces, then follow them into easyJet’s capabilities and commercially testable hypotheses.</p><a class='ex-button' href='{root}/{data['enterprise_slug']}'>Explore {e(data['enterprise_name'])} →</a></section>"
    metrics=f"<div class='twin-metrics'><a href='{root}/evidence/AV-ECON'><strong>$1.165trn</strong>Global airline revenue · IATA June forecast for 2026, not actuals</a><a href='{root}/evidence/AV-MARKET'><strong>302m journeys</strong>UK & Crown Dependency airports · calendar 2025, not unique people</a><a href='{root}/evidence/AV-ECON'><strong>2.0%</strong>Global net margin · IATA June 2026 forecast</a></div>"
    diagram=operating_model(data) if lens=='value-chain' else _map(lens.upper()+' · select a force',data['industry_name'],[(r['title'],'Analyst interpretation',root+'/nodes/'+r['id']) for r in rows])
    cards=''.join(f"<article class='ex-card'><span class='research-badge interpretation'>Analyst interpretation</span><h3><a href='{root}/nodes/{r['id']}'>{e(r['title'])}</a></h3><p>{e(r['assessment'])}</p>{links(data,r['capability_ids']+r['claim_ids'])}</article>" for r in rows)
    ecosystem=_map('Aviation ecosystem · conceptual relationships','Commercial aviation',[
        ('Airlines','easyJet and European peers',root+'/evidence/AV-PEERS'),('Airports & airspace','Capacity & turnaround',root+'/nodes/AV-SUP-AIRPORTS'),('Fleet & maintenance','Engineering dependencies',root+'/nodes/AV-SUP-AIRBUS'),('Fuel & sustainability','Supply, policy & assurance',root+'/nodes/AV-CAP-SUSTAIN'),('Travellers & channels','Digital & passenger rights',root+'/nodes/AV-CAP-DIGITAL'),('Hotels & destinations','Holiday partner network',root+'/nodes/AV-SUP-HOTELS')])
    return shell(data,'Aviation Industry Twin',hero+metrics+tabs+diagram+f"<div class='research-grid'>{cards}</div><section class='ex-section'><h2>One ecosystem. Distinct dependencies.</h2>{ecosystem}<p>Illustrative ecosystem, not an exhaustive market ranking. CAA’s review discusses Heathrow, Gatwick and Luton capacity and growth at Edinburgh, Liverpool and Newcastle. These are ecosystem examples, not verified easyJet supplier contracts. Airline peer membership is not route-level rivalry evidence.</p></section>",headers)


def enterprise(data, headers=None):
    root=data['route_root']
    hero=f"<section class='ex-hero' id='explorer-content'><p class='eyebrow'>Enterprise Twin / {data['enterprise_twin_id']}</p><h1>easyJet.<br>From operating reality<br>to commercial relevance.</h1><p>Airline and holidays. Existing operational AI. New conversational distribution and planned connectivity. Find the unresolved outcome before proposing a solution.</p><a class='ex-button' href='{root}/opportunities'>Explore six opportunity hypotheses →</a></section>"
    metrics=f"<div class='twin-metrics'><a href='{root}/evidence/AV-REVENUE'><strong>£10,106m</strong>Group revenue · FY2025 actual</a><a href='{root}/evidence/AV-PROFIT'><strong>£665m</strong>Headline PBT · FY2025, distinct from £658m reported</a><a href='{root}/evidence/AV-FLEET'><strong>356 aircraft</strong>Fleet at 30 September 2025 · not today’s count</a></div>"
    warning=f"<aside class='twin-callout'><strong>Current-state boundary.</strong> FY2026 Q3 and the latest holidays article are indexed official excerpts, not full retrieved reports. FY2026 final results and current ownership/decision rights require verification. A recommended acquisition is not a completed change of control. {links(data,['AV-Q3','AV-OWNERSHIP','AV-G-LATEST'])}</aside>"
    domains=[('strategy','Strategy & investment direction'),('financials','Financial performance — retain the period'),('operating-model','Airline, holidays & network'),('technology','Technology, digital & AI'),('operations','Fleet & operational resilience'),('suppliers','Suppliers & route to market'),('programmes','Transformation plans'),('sustainability','Sustainability & fuel dependencies')]
    sections=''.join(f"<section class='ex-section' id='{key}'><h2>{title}</h2>{claims_html(data,[c['id'] for c in data['claims'] if c['domain']==key and c['asset_id']==data['enterprise_twin_id']])}</section>" for key,title in domains)
    programmes=''.join(f"<article class='ex-card'><span class='research-badge'>Public signal</span><h3><a href='{root}/nodes/{p['id']}'>{e(p['title'])}</a></h3><p>{e(p['current_phase'])}</p><p>Owner, budget and external work package: Unknown.</p>{links(data,p['claim_ids'])}</article>" for p in data['programmes'])
    supplier_map=_map('Technology & supplier landscape · inspect the date','easyJet dependencies',[(s['title'],{'AV-SUP-AIRBUS':'Reported 2023; scope unknown','AV-SUP-OPENAI':'October 2026 integration','AV-SUP-STARLINK':'Future rollout announced','AV-SUP-ECOVADIS':'FY2025 assessment context','AV-SUP-AIRPORTS':'Ecosystem category','AV-SUP-HOTELS':'Partner category'}[s['id']],root+'/nodes/'+s['id']) for s in data['suppliers']])
    return shell(data,'easyJet Enterprise Twin',hero+metrics+warning+"<section class='ex-section'><h2>The operating landscape</h2>"+operating_model(data)+"</section><section class='ex-section'><h2>Known relationships, bounded claims</h2>"+supplier_map+"<p>Reported 2023 maintenance relationship, 2026 integration and planned future rollout have different temporal meanings. No exclusive incumbent, contract value or available workshare is inferred.</p></section>"+sections+f"<section class='ex-section'><h2>Programmes and investment signals</h2><div class='research-grid'>{programmes}</div></section>",headers)


def score_html(data,row):
    return "<div class='twin-score'>"+''.join(f"<span>{e(d.replace('_',' ').title())} <strong>{row['commercial'][d]['score']}/3</strong></span>" for d in commercial_dimensions(data))+"</div>"


def opportunities(data, headers=None):
    rows=commercial_candidates(data);root=data['route_root']
    labels=['Operational AI','Conversational channel','Holiday orchestration','Connectivity readiness','Fleet/MRO data','Fuel evidence']
    nodes=[(f"{r['commercial_rank']:02} · {label}",'Unqualified hypothesis',root+'/candidates/'+r['id']) for r,label in zip(rows,labels)]
    cards=''.join(f"<article class='ex-card'><p class='ex-kicker'>{r['commercial_rank']:02} / {'Validate first' if r['commercial']['shortlisted'] else 'Research before outreach'}</p><h3><a href='{root}/candidates/{r['id']}'>{e(r['title'])}</a></h3>{score_html(data,r)}<p>{e(r['problem'])}</p><p><strong>Next:</strong> {e(r['commercial']['next_commercial_action'])}</p></article>" for r in rows)
    body=f"<section class='ex-hero' id='explorer-content'><p class='eyebrow'>Commercial intelligence / {e(data['enterprise_name'])}</p><h1>A credible opening.<br>Not an invented deal.</h1><p>Six evidence-led hypotheses. Three priorities for validation. Zero confirmed supplier mandates.</p></section><section class='ex-card'><h2>Four assessments, kept separate</h2><p>{e(data['commercial_assessment']['method'])}</p><p><strong>Seller:</strong> {e(data['seller_profile']['description'])} {e(data['seller_profile']['basis'])}</p><p>Relevance does not establish access. Public evidence does not establish unmet need. No budgets, contract values, procurement dates or named buyers verified. Saving requires authorised user action; no hypothesis is automatically qualified.</p></section>"+_map('Prioritised opportunity landscape','easyJet opportunities',nodes)+f"<div class='research-grid'>{cards}</div>"
    return shell(data,'easyJet opportunity landscape',body,headers)


def detail(data, category, identifier, headers=None):
    root=data['route_root']
    if category=='candidates':
        row=next((r for r in commercial_candidates(data) if r['id']==identifier),None)
        if not row:raise ValueError('Unknown candidate')
        a=row['commercial']
        ratings=''.join(f"<li><strong>{e(d.replace('_',' ').title())}: {a[d]['score']}/3.</strong> {e(a[d]['reason'])}</li>" for d in commercial_dimensions(data))
        brief=''.join(f"<dt>{title}</dt><dd>{e(a[key])}</dd>" for key,title in [('business_problem','Business problem'),('proposed_service','Proposed service'),('buyer_status','Stakeholder status'),('supplier_position','Supplier / competition'),('route_to_market','Route to market'),('timing_context','Timing'),('next_commercial_action','Next commercial action')])
        body=f"<section class='ex-hero' id='explorer-content'><p class='eyebrow'>Research hypothesis / {identifier}</p><h1>{e(row['title'])}</h1><p>{e(row['confidence'])}</p></section><section class='ex-card'><h2>Commercial assessment</h2>{score_html(data,row)}<ul>{ratings}</ul><dl class='research-dl'>{brief}<dt>Potential stakeholders</dt><dd>{e('; '.join(a['buyer_functions']))} (inferred)</dd><dt>Value / buying window</dt><dd>Unknown / Unknown</dd></dl></section><section class='ex-section' id='evidence'><h2>Observation</h2>{claims_html(data,row['claim_ids'])}</section><section class='ex-card'><h2>Interpretation</h2><p>{e(row['problem'])}</p><h2>Implication</h2><p>Existing teams or partners may already address this outcome. Validate the residual gap before proposing external delivery.</p><h2>Opportunity</h2><p>{e(row['intervention'])}</p><h2>Customer evidence needed</h2>{links(data,row['gap_ids'])}<p>Still unqualified. Capture preserves public-source provenance; qualification remains an explicit authorised workflow.</p>{capture_controls(data['enterprise_slug'],identifier,headers)}</section>"
        return shell(data,row['title'],body,headers)
    if category=='evidence':
        c=_index(data['claims']).get(identifier)
        if not c:raise ValueError('Unknown claim')
        # Exercise the same semantic and Evidence contracts as Banking.
        segment=claim_segment(data,c); semantic=candidate_claim(data,c); evidence=evidence_item(data,c)
        s=_index(data['sources'])[c['source_ids'][0]]
        body=f"<section class='ex-hero' id='explorer-content'><p class='eyebrow'>{identifier} / Public source claim</p><h1>{e(c['statement'])}</h1><p>{e(c['reporting_period'])}</p></section><section class='ex-card'><h2>Evidence and provenance</h2><p>Scope: {e(c['entity_scope'])}. Source-supported public statement; not accepted canonical Evidence or sales qualification.</p><blockquote class='research-quote'>{e(segment.content)}</blockquote><p>Locator: {e(c['quote_locator'])}</p><p><a href='{e(s['url'],quote=True)}' rel='noreferrer'>Open official source →</a></p><p>Published: {e(s['publication_date'] or 'Unknown')} · Retrieved: {e(s['retrieved_at'])}</p><p>{e(s['retrieval_extent'])}</p><p>{e(s['review_notes'])}</p><details><summary>Traceable source identity</summary><p>{e(segment.source_location)}</p><p>Excerpt SHA256: {e(s['text_sha256'])}</p><p>Original file SHA256: Unavailable; no original bytes archived.</p><p>{e(semantic.authority)} · {e(evidence.truth_status)}</p></details></section>"
        related=[r['id'] for r in data['frameworks']+data['programmes']+data['candidates'] if identifier in r.get('claim_ids',[])]
        return shell(data,identifier,body+"<section class='ex-card'><h2>What this informs</h2>"+links(data,related)+"</section>",headers)
    if category=='nodes':
        row=next((r for key in ('frameworks','capabilities','suppliers','programmes') for r in data[key] if r['id']==identifier),None)
        if identifier in data['assets']:
            return enterprise(data,headers) if identifier==data['enterprise_twin_id'] else industry(data,headers=headers)
        if not row:raise ValueError('Unknown node')
        body=f"<section class='ex-hero' id='explorer-content'><p class='eyebrow'>Knowledge node / {identifier}</p><h1>{e(row['title'])}</h1><p>{e(row.get('assessment') or row.get('status') or row.get('current_phase') or row.get('scope',''))}</p></section><section class='ex-section'><h2>Supporting observations</h2>{claims_html(data,row.get('claim_ids',[]))}</section><section class='ex-section'><h2>Forces → capabilities → opportunities</h2>{edges_html(data,identifier)}</section>{links(data,row.get('gap_ids',[]))}"
        if row.get('capability_ids'):body+="<section class='ex-card'><h2>Affected capabilities</h2>"+links(data,row['capability_ids'])+"</section>"
        return shell(data,row['title'],body,headers)
    raise ValueError('Unknown view')


def sources(data, headers=None):
    cards=[]
    for s in data['sources']:
        claims=[c['id'] for c in data['claims'] if s['id'] in c['source_ids']]
        cards.append(f"<article class='ex-card' id='{s['id']}'><span class='research-badge'>{'Reviewed excerpt' if s['verification']=='primary_retrieved' else 'Retrieval pending'}</span><h2>{e(s['title'])}</h2><p>{e(s['publisher'])} · Published: {e(s['publication_date'] or 'Unknown')}</p><p>Period: {e(s['reporting_period'])}</p><p>{e(s.get('retrieval_extent',s['limitation']))}</p><p>Retrieved: {e(s.get('retrieved_at') or 'Not retrieved')} · Original checksum: Unavailable</p><p><a href='{e(s['url'],quote=True)}' rel='noreferrer'>Official source →</a></p>{links(data,claims)}</article>")
    return shell(data,'Aviation source register',"<section class='ex-hero' id='explorer-content'><p class='eyebrow'>Provenance before confidence</p><h1>Inspect the evidence.</h1><p>13 short excerpt records, including two search-index-only extracts. One pending retrieval. Full originals are not archived. Source date, reporting period and retrieval date remain distinct.</p></section><div class='research-grid'>"+''.join(cards)+"</div>",headers)


def gaps(data, headers=None):
    cards=''.join(f"<article class='ex-card' id='{g['id']}'><span class='research-badge unknown'>Open / {e(g['priority'])}</span><h2>{e(g['title'])}</h2><p>{e(g['question'])}</p><p>Owner: {e(g['owner_role'])}</p></article>" for g in data['gaps'])
    return shell(data,'Research and qualification gaps',"<section class='ex-hero' id='explorer-content'><h1>Know what is still unknown.</h1><p>Public intelligence narrows the next question. Customer evidence determines whether there is a deal.</p></section><div class='research-grid'>"+cards+"</div>",headers)


def render(domain, suffix='', lens='pestle', headers=None):
    data=load_assessment(domain)
    if suffix=='':return industry(data,lens,headers)
    if suffix=='/'+data['enterprise_slug']:return enterprise(data,headers)
    if suffix=='/opportunities':return opportunities(data,headers)
    if suffix=='/sources':return sources(data,headers)
    if suffix=='/gaps':return gaps(data,headers)
    parts=suffix.strip('/').split('/')
    if len(parts)==2:return detail(data,parts[0],parts[1],headers)
    raise ValueError('Unknown registered research route')
