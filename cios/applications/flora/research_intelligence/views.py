"""Drill-down research lenses inside the existing Explorer visual language."""
from html import escape as e
import json

from ..banking_explorer import _page, _map
from ..sales_views import capture_controls
from .model import (ROOT, load_assessment, freshness, ranked_candidates, candidate,
                    claim_segment, candidate_claim, evidence_item, primary_claim_supported, _index)

STYLE="""
.research-nav{display:flex;flex-wrap:wrap;gap:8px;margin:22px 0}.research-nav a{padding:9px 14px;border:1px solid #bfcebf;border-radius:22px;text-decoration:none}.research-nav a[aria-current]{background:#164d48;color:white}.research-warning{border-left:4px solid #ba7942;background:#fff1df;padding:18px 22px;border-radius:10px;margin:22px 0}.research-badge{display:inline-block;border-radius:5px;padding:4px 8px;font-size:.76rem;background:#fff0df;color:#774322}.research-badge.interpretation{background:#e3ebdf;color:#365d4b}.research-badge.unknown{background:#eeece6;color:#575c55}.research-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.research-grid>*{min-width:0}.research-grid h3{overflow-wrap:anywhere}.research-chain{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}.research-chain a{padding:20px;background:#e5eee3;border:1px solid #c3d5c6;border-radius:14px;text-decoration:none}.research-chain span{display:block;font-size:.8rem;margin-bottom:9px;color:#5d7064}.research-chain strong{display:block;font-size:1.15rem}.research-chain em{font-size:.85rem;font-style:normal;font-weight:400}.research-quote{padding:18px;border-left:3px solid #b57a4c;background:#fff8ed;white-space:pre-wrap;overflow-wrap:anywhere}.research-dl{display:grid;grid-template-columns:150px minmax(0,1fr);gap:12px}.research-dl dt{font-weight:700;font-size:.85rem}.research-dl dd{margin:0}.research-rank{font-size:2rem;font-weight:800;color:#164d48}.research-links a{display:inline-block;margin:5px 12px 5px 0}.research-edges{display:grid;gap:10px}.research-edge{border:1px solid #d5dfd2;padding:13px;border-radius:10px;background:#fffdf8}.research-table{overflow-x:auto}.research-table table{width:100%;border-collapse:collapse}.research-table th,.research-table td{padding:14px;text-align:left;border-bottom:1px solid #d7e0d3;vertical-align:top}.research-metric{font-size:1.7rem;font-weight:800}.research-source{font-size:.86rem;color:#5f7166}.research details{margin:16px 0}.research summary{cursor:pointer;font-weight:700}.research pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#efeee7;padding:16px}.research a{overflow-wrap:anywhere}@media(max-width:900px){.research-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.research-chain{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:540px){.research-grid,.research-chain,.research-dl{grid-template-columns:1fr}.research-dl dd{margin-bottom:10px}}
"""


def href(data, identifier):
    if any(r['id']==identifier for r in data['claims']):return ROOT+'/evidence/'+identifier
    if any(r['id']==identifier for r in data['candidates']):return ROOT+'/candidates/'+identifier
    if any(r['id']==identifier for r in data['sources']):return ROOT+'/sources#'+identifier
    if any(r['id']==identifier for r in data['gaps']):return ROOT+'/gaps#'+identifier
    if identifier==data['enterprise_twin_id']:return ROOT+'/lloyds'
    if identifier==data['industry_twin_id']:return ROOT
    return ROOT+'/nodes/'+identifier


def label(data, identifier):
    for key in ('frameworks','capabilities','suppliers','programmes','candidates','gaps','sources'):
        for item in data[key]:
            if item['id']==identifier:return item.get('title',identifier)
    return {'BK-ENT-001':data['enterprise_name'],'BK-IND-002':data['industry_name']}.get(identifier,identifier)


def links(data, ids):
    return "<div class='research-links'>"+''.join(f"<a href='{href(data,i)}'>{e(label(data,i))} →</a>" for i in dict.fromkeys(ids))+'</div>'


def shell(title, body, headers=None, data=None):
    data=data or load_assessment();state=freshness(data)
    nav=[(ROOT,'Industry lenses'),(ROOT+'/lloyds','Lloyds deep research'),(ROOT+'/opportunities','Research priorities'),(ROOT+'/sources','Source register'),(ROOT+'/gaps','Research gaps')]
    controls="<nav class='research-nav' aria-label='Research navigation'>"+''.join(f"<a href='{path}'>{text}</a>" for path,text in nav)+'</nav>'
    warning=f"<aside class='research-warning'><strong>Primary-source re-verification {'pending' if state['primary_verified']==0 else 'partially complete'}.</strong> {state['primary_verified']}/{state['primary_total']} source documents retrieved and verified against content snapshots. This view reuses existing repository research effective {data['upstream_research_effective_date']}; as-of assessment {data['assessed_at']}. Source publication dates remain Unknown unless evidenced. These are research candidates, not accepted canonical Evidence or customer-confirmed requirements.</aside>"
    crumb=f"<nav class='ex-breadcrumb' aria-label='Breadcrumb'><a href='/flora/banking/explorer'>Banking Explorer</a> / <a href='{ROOT}'>Industry Twin research</a> / <span>{e(title)}</span></nav>"
    return _page(title,f"<style>{STYLE}</style><div class='research'>{crumb}{controls}{warning}{body}</div>",headers)


def claims_html(data, ids):
    if not ids:return "<p class='ex-empty'>No direct supporting claim is recorded here. Inspect linked research and explicit gaps; absence is not evidence of no need.</p>"
    claims=_index(data['claims']);cards=[]
    for identifier in dict.fromkeys(ids):
        item=claims[identifier]
        badge='Research gap' if item['kind']=='unknown' else 'Interpretation' if item['kind']=='interpretation' else 'Repository-reported · primary unverified' if item['verification']=='repository_reported' else 'Primary-source supported · not customer demand'
        cards.append(f"<article class='ex-card'><span class='research-badge'>{e(badge)}</span><h3>{e(item['statement'])}</h3><p>{e(item['reporting_period'])}</p><p class='research-source'>Claim {identifier} · {e(item['asset_id'])}</p><a href='{ROOT}/evidence/{identifier}'>Inspect quotation, dates & provenance →</a></article>")
    return "<div class='research-grid'>"+''.join(cards)+'</div>'


def edges_html(data, identifier):
    edges=[r for r in data['relationships'] if identifier in {r['subject'],r['object']}]
    return "<div class='research-edges'>"+''.join(f"<div class='research-edge'><span class='research-badge {r['assertion_kind']}'>{'Primary-supported relationship' if r['verified'] else e(r['assertion_kind'].replace('_',' '))}</span> <a href='{href(data,r['subject'])}'>{e(label(data,r['subject']))}</a> → {e(r['predicate'].replace('_',' '))} → <a href='{href(data,r['object'])}'>{e(label(data,r['object']))}</a>{links(data,r['claim_ids'])}</div>" for r in edges)+'</div>'


def industry_page(lens='pestle',headers=None):
    data=load_assessment()
    if lens not in {'pestle','porter','value-chain'}:raise ValueError('Choose an implemented research lens')
    rows=[r for r in data['frameworks'] if r['lens']==lens]
    choices=[('pestle','PESTLE'),('porter',"Porter’s Five Forces"),('value-chain','Industry value chain')]
    tabs="<nav class='research-nav' aria-label='Industry research lenses'>"+''.join(f"<a href='{ROOT}?lens={key}' {'aria-current=page' if key==lens else ''}>{e(text)}</a>" for key,text in choices)+'</nav>'
    hero=f"<section class='ex-hero' id='explorer-content'><p class='eyebrow'>Industry Twin / {data['industry_twin_id']}</p><h1>Banking.<br>From forces to evidence.</h1><p>Explore how industry forces constrain enterprise choices. Follow each assessment into capabilities, programme signals and commercial research questions.</p><a class='ex-button' href='{ROOT}/lloyds'>Open Lloyds deep research →</a></section>"
    if lens=='value-chain':
        diagram="<div class='research-chain'>"+''.join(f"<a href='{ROOT}/nodes/{r['id']}'><span>Value activity {i:02}</span><strong>{e(r['title'])}</strong><em>Conceptual activity · inspect supporting research →</em></a>" for i,r in enumerate(rows,1))+'</div>'
    else:
        diagram=_map('Interactive '+lens+' research lens','UK Banking',[(r['title'],'Interpretation / research gap',ROOT+'/nodes/'+r['id']) for r in rows])
    cards=''.join(f"<article class='ex-card'><span class='research-badge interpretation'>Working interpretation</span><h3><a href='{ROOT}/nodes/{r['id']}'>{e(r['title'])}</a></h3><p>{e(r['assessment'])}</p><p>{len(r['claim_ids'])} linked research claims · {len(r['gap_ids'])} explicit gaps</p></article>" for r in rows)
    body=hero+tabs+diagram+f"<section class='ex-section'><div class='research-grid'>{cards}</div></section><section class='ex-card'><h2>One research spine, not another duplicate Twin.</h2><p>These lenses reference existing Banking Foundation, Industry Twin and Lloyds Twin identities. Conceptual arrows show analytical relationships, not verified contracts, customer demand or accepted Enterprise Model ownership.</p>{links(data,['BK-IND-001','BK-IND-002','BK-REF-001','BK-ENT-001'])}</section>"
    return shell('Banking Industry Twin research',body,headers,data)


def enterprise_page(headers=None):
    data=load_assessment();state=freshness(data)
    domains=[('strategy','Strategy & economic mechanism'),('financials','Financial reference points'),('operating_capabilities','Operating capabilities & customer outcomes'),('technology','Technology & platforms'),('supplier_relationships','Supplier relationships & unknowns'),('programmes','Transformation signals'),('investment','Investment versus supplier spend')]
    nodes=[('Strategy & financials','Company economics, not budget',ROOT+'/lloyds#financials'),('Operating capabilities','Customer and service evidence',ROOT+'/lloyds#operating_capabilities'),('Technology & AI','Reported use, unknown scope',ROOT+'/lloyds#technology'),('Supplier relationships','Reported versus unknown',ROOT+'/lloyds#supplier_relationships'),('Transformation signals','Priority, rollout, proposal',ROOT+'/lloyds#programmes'),('Commercial questions','Eight provisional candidates',ROOT+'/opportunities')]
    sections=[]
    for domain,title in domains:
        selected=[c['id'] for c in data['claims'] if c['domain']==domain and c['asset_id']==data['enterprise_twin_id']]
        sections.append(f"<section class='ex-section' id='{domain}'><p class='ex-kicker'>Enterprise knowledge domain</p><h2>{e(title)}</h2>{claims_html(data,selected)}</section>")
    programme_cards=''.join(f"<article class='ex-card'><span class='research-badge'>{e(p['signal_class'])}</span><h3><a href='{ROOT}/nodes/{p['id']}'>{e(p['title'])}</a></h3><p>Owner: {e(p['owner'])} · Funding: {e(p['funding'])} · Procurement: {e(p['procurement'])}</p><p>{e(p['current_phase'])}</p></article>" for p in data['programmes'])
    body=f"<section class='ex-hero' id='explorer-content'><p class='eyebrow'>Enterprise Twin / {data['enterprise_twin_id']}</p><h1>Lloyds.<br>Connect the economic spine.</h1><p>Deposits, earnings, capital, simplification and customer outcomes: test each link before turning it into a commercial claim.</p><a class='ex-button' href='{ROOT}/opportunities'>Reassess the opportunities →</a></section><section class='ex-section'>{_map('Lloyds research landscape','Lloyds research',nodes)}</section>"+''.join(sections)+f"<section class='ex-section'><h2>Programme and investment signals</h2><p>Reported priorities, rollouts and proposed transactions are not interchangeable. No funding, buyer or procurement date is inferred.</p><div class='research-grid'>{programme_cards}</div></section><section class='ex-card'><h2>Continue in existing FLORA views</h2><p><a href='/flora/banking/explorer/lloyds'>Enterprise Explorer</a> · <a href='/flora/banking/explorer/lloyds/opportunities'>Original opportunity landscape</a> · <a href='/digital-twins'>Governed Canvas discovery (requires appropriate access)</a></p><p>Financial values in this research preserve their own reporting periods and source limitations. They do not overwrite the older Explorer fixtures or customer pipeline records.</p></section>"
    return shell('Lloyds Enterprise Twin research',body,headers,data)


def opportunities_page(headers=None):
    data=load_assessment();rows=ranked_candidates(data)
    primary_count=sum(primary_claim_supported(data,c) for c in data['claims'])
    cards=''.join(f"<article class='ex-card'><span class='research-rank'>{r['rank']:02}</span> <span class='research-badge'>Tier {r['research_tier']} / Research effort</span><h3><a href='{ROOT}/candidates/{r['id']}'>{e(r['title'])}</a></h3><p>{e(r['problem'])}</p><p><strong>Why this changed:</strong> {e(r['ranking_change'])}</p><p class='research-source'>{e(r['family'])} family · {e(r['confidence'])}</p><a href='{ROOT}/candidates/{r['id']}'>Inspect drivers, evidence & customer questions →</a></article>" for r in rows)
    comparisons=[('COH-LBG-001','Customer experience / outsourcing','Split into brand-migration and assisted-outcome discovery. Generic BPO/outsourcing demand is not established.',['LBG-BRAND','LBG-ACCESS','LBG-BPO-GAP']),('COH-LBG-002','Deposits and customer value','Economic relevance is better connected to the reported deposit/hedge spine; primacy, elasticity and sourcing remain unknown.',['LBG-DEPOSITS','LBG-HEDGE','LBG-PRIMACY-GAP']),('COH-LBG-003','Cloud, Data and AI Control Tower','Split into migration, benefit, model-governance, resilience and colleague-adoption questions. These overlap and cannot be added as separate deal values.',['LBG-MIGRATION','LBG-VERTEX','LBG-AI-VALUE'])]
    comparison=''.join(f"<tr><td><a href='/flora/banking/lloyds/opportunity/{id}'>{e(title)}</a><p>{id}</p></td><td>{e(change)}{links(data,refs)}</td></tr>" for id,title,change,refs in comparisons)
    watch=''.join(f"<article class='ex-card'><span class='research-badge unknown'>Watchlist / not admitted as a current opportunity</span><h3>{e(w['title'])}</h3><p>{e(w['reason'])}</p>{links(data,w['claim_ids']+w['gap_ids'])}</article>" for w in data['watchlist'])
    body=f"<section class='ex-hero' id='explorer-content'><p class='eyebrow'>Evidence-led commercial discovery</p><h1>Better questions.<br>Not invented deals.</h1><p>{len(rows)} provisional Lloyds research candidates. Eight are supported by the existing research context; no extra candidates are manufactured to reach ten.</p></section><section class='ex-card'><h2>How this ranking works</h2><p>Research tier first: reported programme/adoption signals before economics/risk interpretations. Within a tier: primary-supported claims, then enterprise-specific claim coverage, then stable ID. Source counts are not truth probabilities. Current primary-supported claim count: {primary_count}. All ranks remain research priorities, not customer qualification. No deal value, procurement date or customer-verified demand is inferred.</p><p>Related candidates share families and may compete for the same scope; do not sum them as separate budgets.</p></section><section class='ex-section'><div class='research-grid'>{cards}</div></section><section class='ex-section'><h2>What changed from the original three hypotheses?</h2><div class='research-table'><table><thead><tr><th>Original hypothesis</th><th>Research-led reassessment</th></tr></thead><tbody>{comparison}</tbody></table></div></section><section class='ex-section'><h2>Kept off the ranked opportunity list</h2><div class='research-grid'>{watch}</div></section>"
    return shell('Lloyds research opportunity priorities',body,headers,data)


def candidate_page(identifier,headers=None):
    data=load_assessment();row=candidate(identifier,data)
    if row is None:raise ValueError('Research candidate unavailable')
    basis=''.join(f'<dt>{e(k.replace("_"," "))}</dt><dd>{e(str(v))}</dd>' for k,v in row['rank_basis'].items())
    capture=capture_controls(row['enterprise_slug'],row['id'],headers)
    body=f"<section class='ex-hero' id='explorer-content'><p class='eyebrow'>Research priority {row['rank']} / Lloyds</p><h1>{e(row['title'])}</h1><p>{e(row['problem'])}</p></section><section class='ex-section ex-split'><article class='ex-card'><span class='research-badge interpretation'>Commercial interpretation / not a confirmed requirement</span><h2>Potential intervention</h2><p>{e(row['intervention'])}</p><h3>Programme signal</h3><p>{e(row['programme_signal'])}</p><p><strong>Estimated deal value:</strong> Unknown · <strong>Procurement date:</strong> Unknown</p><p><strong>Confidence:</strong> {e(row['confidence'])}</p><h3>Rank rationale</h3><dl class='research-dl'>{basis}</dl><p>{e(row['ranking_change'])}</p></article><aside class='ex-card'><h2>Develop with customer evidence.</h2><p>Capture a private research-stage copy using the existing pipeline. It starts Discovered with blank qualification, unknown value and unchanged source limitations. This action does not qualify or activate a pursuit.</p>{capture}<p><a href='/flora/sales/pipeline'>Workspace pipeline</a></p></aside></section><section class='ex-section'><h2>Industry drivers and capabilities</h2>{links(data,row['driver_ids']+row['capability_ids']+row['programme_ids'])}</section><section class='ex-section' id='evidence'><h2>Supporting research and provenance</h2>{claims_html(data,row['claim_ids'])}</section><section class='ex-section'><h2>Evidence needed before qualification</h2>{links(data,row['gap_ids'])}</section><section class='ex-section'><h2>Trace the relationships</h2>{edges_html(data,identifier)}</section><p><a href='{ROOT}/opportunities'>← Return to research priorities</a> · <a href='{ROOT}/lloyds'>Lloyds Enterprise Twin</a></p>"
    return shell(row['title'],body,headers,data)


def evidence_page(identifier,headers=None):
    data=load_assessment();item=_index(data['claims']).get(identifier)
    if item is None:raise ValueError('Research claim unavailable')
    segment=claim_segment(data,item);claim=candidate_claim(data,item);package=evidence_item(data,item)
    upstream_url='https://github.com/rdidale-jpg/CIOS/blob/'+data['source_base_commit']+'/'+segment.source_location
    source_cards=''.join(f"<article class='ex-card'><h3>{e(s['title'])}</h3><p>Publisher: {e(s['publisher'])}</p><p>Publication date: {e(s['publication_date'] or 'Unknown')}</p><p>Reporting period: {e(s['reporting_period'])}</p><p>Primary retrieval: {e(s['retrieved_at'] or 'Not retrieved')}</p><p>{e(s['limitation'])}</p><a href='{e(s['url'],quote=True)}'>Open cited primary-source URL ↗</a></article>" for s in data['sources'] if s['id'] in item['source_ids'])
    body=f"<section class='ex-hero' id='explorer-content'><p class='eyebrow'>Claim-level research lineage / {identifier}</p><h1>Inspect the evidence boundary.</h1><p>{e(item['statement'])}</p></section><section class='ex-card'><h2>Verbatim quotation from the preserved repository research</h2><blockquote class='research-quote'>{e(segment.content)}</blockquote><p>This is a quotation of the existing research, not a newly retrieved quotation of the primary publication.</p><dl class='research-dl'><dt>Existing Twin / asset</dt><dd>{e(segment.asset_id)}</dd><dt>Source section</dt><dd>{e(segment.section_heading)}</dd><dt>Local provenance</dt><dd>{e(segment.source_location)}</dd><dt>Research claim</dt><dd>{e(claim.claim_id)}</dd><dt>Truth status</dt><dd>{e(package.truth_status)}</dd><dt>Entity scope</dt><dd>{e(item['entity_scope'])}</dd><dt>Reporting period</dt><dd>{e(item['reporting_period'])}</dd><dt>Freshness</dt><dd>{e(package.freshness)}</dd></dl><p><a href='{e(upstream_url,quote=True)}'>Inspect immutable repository source →</a></p><details><summary>Segment integrity and reusable contract</summary><p>SHA-256 {e(segment.content_hash)} identifies repository quotation integrity; it does not prove primary-source truth.</p><pre>{e(json.dumps(claim.to_dict(),indent=2,ensure_ascii=False))}</pre></details></section><section class='ex-section'><h2>Cited primary documents — verification still needed</h2><div class='research-grid'>{source_cards}</div></section><p><a href='{ROOT}/lloyds'>Return to Lloyds research</a> · <a href='{ROOT}/opportunities'>Opportunity priorities</a></p>"
    return shell('Research claim provenance',body,headers,data)


def node_page(identifier,headers=None):
    data=load_assessment();node=None
    for key in ('frameworks','capabilities','suppliers','programmes'):
        node=next((r for r in data[key] if r['id']==identifier),None)
        if node:break
    if node is None and identifier in data['assets']:
        node={'id':identifier,'title':identifier+' / existing knowledge asset','assessment':'Existing repository-owned research asset; no new canonical owner is created.','claim_ids':[c['id'] for c in data['claims'] if c['asset_id']==identifier]}
    if node is None:raise ValueError('Research node unavailable')
    detail=node.get('assessment') or node.get('scope') or node.get('signal_class') or 'Supplier relationship scope must be checked at enterprise and contract level.'
    body=f"<section class='ex-hero' id='explorer-content'><p class='eyebrow'>Research relationship explorer</p><h1>{e(node['title'])}</h1><p>{e(detail)}</p></section><section class='ex-section'><h2>Supporting research statements</h2>{claims_html(data,node.get('claim_ids',[])) or 'No direct claim; inspect the relationship context.'}</section><section class='ex-section'><h2>Connected capabilities, programmes and questions</h2>{edges_html(data,identifier)}</section><section class='ex-section'><h2>Outstanding research</h2>{links(data,node.get('gap_ids',[]))}</section>"
    return shell(node['title'],body,headers,data)


def sources_page(headers=None):
    data=load_assessment();cards=''.join(f"<article class='ex-card' id='{s['id']}'><span class='research-badge'>{'Primary retrieved; inspect claim-level verification' if s['verification']=='primary_retrieved' else 'Citation only / primary unverified'}</span><h3>{e(s['title'])}</h3><p>{e(s['publisher'])}</p><p><strong>Publication date:</strong> {e(s['publication_date'] or 'Unknown')}</p><p><strong>Reporting period:</strong> {e(s['reporting_period'])}</p><p><strong>Retrieved:</strong> {e(s['retrieved_at'] or 'Not retrieved')}</p><p>{e(s['limitation'])}</p><a href='{e(s['url'],quote=True)}'>Open original publisher URL →</a></article>" for s in data['sources'])
    return shell('Primary-source register',"<section class='ex-hero' id='explorer-content'><p class='eyebrow'>Evidence discipline</p><h1>Publication dates.<br>Not assumptions.</h1><p>Local provenance is verified. The original publications still require retrieval, quotation checks and current-period reconciliation.</p></section><section class='ex-section'><div class='research-grid'>"+cards+'</div></section>',headers,data)


def gaps_page(headers=None):
    data=load_assessment();cards=''.join(f"<article class='ex-card' id='{g['id']}'><span class='research-badge unknown'>{e(g['priority'])} priority / Open</span><h3>{e(g['title'])}</h3><p>{e(g['question'])}</p><p><strong>Required evidence:</strong> {e(g['required_evidence'])}</p><p><strong>Decision constrained:</strong> {e(g['decision_impact'])}</p><p class='research-source'>{e(g['owner_role'])}</p></article>" for g in data['gaps'])
    return shell('Research gaps and next actions',"<section class='ex-hero' id='explorer-content'><p class='eyebrow'>Research process / next commission</p><h1>Make the unknowns<br>commercially useful.</h1><p>Research gaps constrain decisions. They are not negative evidence and must not be converted into sales claims.</p></section><section class='ex-section'><div class='research-grid'>"+cards+'</div></section>',headers,data)
