from pathlib import Path
from html import escape as e
import re,json,hashlib
R=Path(__file__).resolve().parents[5];D=Path(__file__).resolve().parent.parent;old=D.parent/'lj2';rich=D.parent/'rich'
tr=json.loads((old/'Force-Trace.json').read_text());bindings=[]
selected={'uk':['economic','technological','legal','environmental'],'banking':['UK-RATE-NOV26','UK-PRA-REPORT27','LBG-ENVOY-CONTROLS','UK-VALUE'],'lloyds':['LBG-A2030-PLATFORMS','LBG-A2030-CIR','LBG-ENVOY-CONTROLS','LBG-BRAND26-TIMING']}
inside=[('businesses','Businesses & brands',25,27,'Halifax branches: 2027 plan'),('economics','Financial performance',74,26,'2030 cost:income target <45%'),('operations','Service operations',24,68,None),('technology','Technology & data',76,69,'Envoy · controls described'),('governance','Governance & change',50,48,None)]
external=[('customers','Customer groups',21,76,None),('businesses','Peers & market context',22,28,None),('economics','Payments & oversight',50,52,None),('operations','Business customers',80,26,None),('technology','Suppliers & partners',83,78,'Google Cloud → Envoy')]
def spot(id,title,x,y,sub=None):
 mx=(x-50)*2 if x>=50 else x*2;fy=(y+(100 if x>=50 else 0))/2
 return f'<a class="spot active" data-label-id="{id}" href="#{id}" style="--x:{x}%;--y:{y}%;--mx:{mx}%;--fy:{fy}%">{e(title)} <span aria-hidden="true">›</span>'+('<small>'+e(sub)+'</small>'if sub else '')+'</a>'
def panel(id,title,body,file):return f'<section class="focus" id="{id}" tabindex="-1"><a class="close" href="{file}" aria-label="Close {e(title,quote=True)}">×</a><h2>{e(title)}</h2>{body}</section>'
def replacefig(html,asset,nodes):
 fig=re.search(r'<figure class="world".*?</figure>',html,re.S).group(0)
 fig=re.sub(r'<a\b[^>]*class="spot.*?</a>|<span\b[^>]*class="spot.*?</span>','',fig,flags=re.S)
 fig=re.sub(r'src="assets/[^"]*"',f'src="assets/{asset}"',fig)
 fig=fig.replace('</figure>',''.join(spot(*n) for n in nodes)+'</figure>')
 return re.sub(r'<figure class="world".*?</figure>',lambda m:fig,html,count=1,flags=re.S)
for scope in ['uk','banking','lloyds']:
 streams=['inside','landscape','forces']if scope=='lloyds'else ['landscape','forces']
 for stream in streams:
  for layer in (['enterprises']if scope=='uk'else ['enterprises','suppliers','regulators']):
   suffix=''if layer=='enterprises'else '-'+layer;file=f'{scope}-{stream}{suffix}.html';source=f'{scope}-'+('landscape'if stream=='inside'else stream)+suffix+'.html';html=(old/source).read_text().replace('lj2.css','lj3.css')
   controls='<nav class="lens" aria-label="Insight stream">'+''.join(f'<a data-lens="true" href="{scope}-{s}{suffix}.html"'+(' aria-current="page"'if s==stream else '')+'>'+s.upper()+'</a>'for s in streams)+'</nav>'
   html=re.sub(r'<nav class="lens".*?</nav>',controls,html,count=1,flags=re.S)
   html=html.replace('data-lens="landscape"',f'data-lens="{stream}"') if stream=='inside'else html
   if scope=='banking' and stream=='landscape':html=html.replace('lloyds-landscape','lloyds-inside')
   if stream=='inside':html=html.replace('lloyds-landscape','lloyds-inside')
   if stream=='forces':
    html=re.sub(r'<section class="focus" id="force-.*?</section>','',html,flags=re.S)
    html=re.sub(r'<p class="metric">.*?</p>','',html,flags=re.S) if scope=='lloyds' else html
    html=re.sub(r'<figcaption[^>]*>.*?</figcaption>','',html,flags=re.S)
    html=re.sub(r'<figure class="world"[^>]*>','<figure class="world" aria-label="'+scope+' Forces: metaphorical currents and pressure fields; no severity, forecast or geography is implied">',html)
    forces=[f for f in tr['scopes'][scope]if f['id']in selected[scope]]
    html=replacefig(html,scope+'-forces.png',[(f['id'],f['title'],25 if i%2==0 else 75,28+(i//2)*43,{'economic':'GDP +0.7% · to Sep 2026','technological':'UK aggregate · Nov 2026 review','legal':'Proposal · Nov 2026 review','environmental':'2027 accounting periods','UK-RATE-NOV26':'4% Bank Rate · Nov 2026','UK-PRA-REPORT27':'March 2027 · entity scope to check','LBG-ENVOY-CONTROLS':'Envoy · existing controls','UK-VALUE':'Customer-value mechanism','LBG-A2030-PLATFORMS':'2027–2030 strategy','LBG-A2030-CIR':'2030 target below 45%','LBG-BRAND26-TIMING':'Branches · 2027 plan'}.get(f['id']))for i,f in enumerate(forces)])
    for f in forces:
     affected={'uk':'UK industries may be affected differently; no enterprise-specific consequence is established.','banking':'Funding, customer service, resilience or control activities may be affected. Lloyds examples are not sector-wide proof.','lloyds':'A possible pathway concerns Lloyds technology, service, cost or change decisions; actual legal-entity scope and residual need require validation.'}[scope]
     affected={'economic':'UK aggregate volume change → possible industry demand/capacity questions; not inferred Banking growth.','technological':'UK cyber context → possible digital-service and resilience exposure; no company incident established.','legal':'Proposed cyber reform → possible governance/reporting duties; enactment, entity and activity scope need checking.','environmental':'Rules for specified issuers → finance and reporting-data preparation, not every UK enterprise.','UK-RATE-NOV26':'Deposit funding, lending and hedge economics → margin/treasury choices; bank-specific sensitivity differs.','UK-PRA-REPORT27':'Incident and third-party reporting → risk, supplier management and resilience processes; legal-entity applicability unverified.','LBG-A2030-PLATFORMS':'Core-platform renewal → technology operations and customer-service continuity. Current system dependencies and still-open decisions are unknown.','LBG-A2030-CIR':'Cost discipline → finance, service processes and operating efficiency. Current expense breakdown and achievable net outcomes are unverified.','LBG-ENVOY-CONTROLS':'AI platforms and existing controls → data teams and frontline service workflows. Lloyds is an example, not proof of a sector-wide gap; effectiveness needs validation.','LBG-BRAND26-TIMING':'Planned Halifax branch changes → assisted channels and customer servicing. Delivery progress and remaining decision windows are unknown.','UK-VALUE':'Current accounts, deposits and lending → product/customer-service choices. This is a conceptual mechanism, not measured loss of trust.'}.get(f['id'],affected)
     why={'uk':'National changes can alter industry conditions; their magnitude and transmission need sector evidence.','banking':'Funding economics, trust and regulated service continuity can influence operating decisions; this is an interpretation.','lloyds':'Modernisation, cost discipline and existing controls may constrain choices; the source does not prove an unmet customer need.'}[scope]
     body=''.join('<h3>'+q+'</h3><p>'+e(v)+'</p>'for q,v in [('What is changing?',f['text']),('Why does it matter?',why),('Who or what is affected?',affected),('What remains uncertain?',f['counter']),('What decision might follow?',f['question'])])
     body+=('<p><a href="banking-forces.html">Explore Banking context →</a></p>'if scope=='uk'else '<p><a href="lloyds-forces.html">Inspect the Lloyds context →</a></p>'if scope=='banking'else '')
     if scope=='lloyds':
      target={'LBG-A2030-PLATFORMS':'operations','LBG-A2030-CIR':'economics','LBG-ENVOY-CONTROLS':'technology','LBG-BRAND26-TIMING':'businesses'}[f['id']]
      body+='<p><a href="lloyds-inside.html#'+target+'">Inspect the possible internal pathway →</a></p>'
     body+='<p class="timing">Source period: '+e(f['date'])+'. Announced/planned change is not a verified early shaping window. Demand, funding, procurement and external scope remain unknown.</p><details><summary>Sources and status</summary><p>'+e(f['status'])+' · '+e(f['kind'])+'</p>'+''.join('<p><a href="'+e(s['url'],quote=True)+'">'+e(s['title'])+'</a> · published '+e(s.get('publication_date')or'not established')+'</p>'for s in f['sources'])+'</details>'
     html=html.replace('</main>',panel(f['id'],f['title'],body,file)+'</main>');bindings.append({'scope':scope,'stream':'forces','label':f['title'],'source':f,'impact':'Interpretation/hypothesis, not qualified Material Pressure or buyer demand','pathway':affected,'timing':'No early/late score computed; retain original dates, existing programmes and unknown decision window'})
    alt=''.join('<a href="#'+f['id']+'">'+e(f['title'])+'</a>'for f in forces)
    html=re.sub(r'<details class="text-view">.*?</details>','<details class="text-view"><summary>Text view</summary>'+alt+'</details>',html,flags=re.S)
   if scope=='lloyds'and stream in ['inside','landscape']:
    # Keep the exterior raster unchanged; change semantic focus, not its composition.
    html=re.sub(r'<section class="focus".*?</section>','',html,flags=re.S)
    nodes=inside if stream=='inside'else external
    html=replacefig(html,'lloyds-inside.png'if stream=='inside'else'lloyds-world.png',nodes)
    html=re.sub(r'<section class="commercial-story".*?</section>','',html,flags=re.S)
    if stream=='inside':
     html=re.sub(r'<figure class="world"[^>]*>','<figure class="world" aria-label="Conceptual Inside Lloyds business and operating world, not actual premises, hierarchy or floorplan">',html)
     content={
      'businesses':('Business areas, brands and structure','The July 2026 announcement plans Halifax branch-brand changes through 2027. Historic portfolio references include Lloyds, Halifax, Bank of Scotland and Scottish Widows; these are not a verified current legal hierarchy. Current segment/subsidiary ownership remains ORG-01.'),
      'economics':('Current financial picture','Reviewed Q3 source: £502.8bn Group deposits at 30 September 2026 and £6.6bn statutory pretax profit for the nine months to that date. Current income, costs, margins and comparable growth remain FIN-01/02. Below 45% cost:income in 2030 is a target, not actual performance or a supplier budget.'),
      'operations':('People, processes and service','Customer relationships connect deposits, lending, payments and service. The interior is an explanatory business/operating metaphor, not Lloyds premises or an actual process/system topology. Current dependencies and systems remain OPS-01.'),
      'technology':('Platforms, data and programmes','Envoy controls/monitoring and Google Cloud collaboration are described in the May 2026 announcement. Older Vertex/model-migration references do not establish a current complete inventory or workshare. Current delivery and net outcomes need validation.'),
      'governance':('Governance, leadership and change','The strategy prioritises core modernisation, data enablement and cost discipline. Named current leadership/accountability is not established in this selected primary evidence; ORG-02 remains open. No executive is inferred to be a buyer.')}
     story='<section class="commercial-story"><p><strong>Customer relationships → funding and lending → income, risk and capital.</strong></p><p>Current actuals, strategy targets and conceptual operating links remain distinct. Income/cost decomposition, current organisation and leadership need primary reconciliation.</p></section>'
    else:
     html=re.sub(r'<p class="metric">.*?</p>','',html,flags=re.S)
     content={
      'customers':('Customers and market segments','Household savers and borrowers and business customer groups are supported roles. No named corporate customer contract is established here.'),
      'businesses':('Peers and competitive context','Barclays, HSBC UK, NatWest Group and Santander UK are existing Banking portfolio identities. Shared industry participation is not a measured bilateral competitive impact or business relationship.'),
      'economics':('Payment infrastructure and oversight','CHAPS/RTGS, Faster Payments and Bacs are sector infrastructure references. BoE, PRA and FCA have distinct roles; institution context does not establish a specific Lloyds legal-entity obligation or contract. REG-01 and INF-01 remain open.'),
      'operations':('Business customer ecosystem','Business customers use credit, payments and service. Illustrated firms are generic customer roles, not named Lloyds customers, owned factories or a factual tenant map.'),
      'technology':('Supported collaboration and unknown partners','Google Cloud → Envoy → Lloyds: source-supported announced platform collaboration in May 2026, not proof of exclusivity, renewal, wider workshare or current effectiveness. No other supplier/customer/partner edge is drawn without appropriate evidence.')}
     story='<section class="commercial-story"><p><strong>Customers, providers and institutions around Lloyds.</strong></p><p>One named platform collaboration is supported. Other relationship scope, firm applicability and named customer links remain unverified.</p></section>'
    for id,(t,b)in content.items():html=html.replace('</main>',panel(id,t,'<p>'+e(b)+'</p><details><summary>Evidence and limitations</summary><p>Original claim dates/status and nine research deficiencies remain in the shared source map and Sources disclosure. Conceptual illustration does not upgrade facts or prove buyer need.</p></details>',file)+'</main>')
    html=html.replace('<details class="studio">',story+'<details class="studio">')
    alt=''.join('<a href="#'+id+'">'+e(t)+'</a>'for id,t,*_ in nodes)
    html=re.sub(r'<details class="text-view">.*?</details>','<details class="text-view"><summary>Text view</summary>'+alt+'</details>',html,flags=re.S)
    bindings.append({'scope':'lloyds','stream':stream,'nodes':nodes,'owner':'Existing Enterprise Twin / Assessment-Overlay; LJ-1R Research-Audit','relationships':'External: only announced Google Cloud/Envoy link; internal: conceptual economic/operating mechanism, not actual organisation or system graph','gaps':'Nine original deficiencies preserved'})
   if scope=='banking':
    if stream=='landscape':html=html.replace('data-label-id="lloyds"','id="selected-lloyds" data-label-id="lloyds"')
    else:html=html.replace('</main>','<p class="return-context" id="selected-lloyds">Selected enterprise: <a href="lloyds-forces.html">Lloyds Banking Group</a></p></main>')
   if scope=='lloyds':html=re.sub(r'href="(banking-[^"#]+.html)"',r'href="\1#selected-lloyds"',html)
   html=re.sub(r'(?:<span>›</span>|›)\s*<a[^>]+>Groups</a>','',html)
   html=html.replace('<title>','<title>LJ-3 · ',1)
   (D/file).write_text(html)
(D/'Stream-Mapping.json').write_text(json.dumps({'authority':'Read-only design projections, not independent models, qualification or evidence stores','source_head':'f4a62d8f0b57968f5cce3d2abcac986dac6ac61d','bindings':bindings,'research_gaps':'Research-Gaps.md','future_streams':'News / Topic Cards / Tools are architecture slots only, no UI or runtime implementation','qualification':'ADR-026 gates and canonical Enterprise/source owners remain unchanged; no pressure qualified'},indent=2)+'\n')
