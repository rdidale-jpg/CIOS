"""LJ-1R isolated four-composition design projection. Never changes application owners."""
from pathlib import Path
from html import escape as e
import os,json,hashlib
R=Path(__file__).resolve().parents[5];D=Path(__file__).resolve().parent.parent
os.environ['FLORA_DATA_DIR']='/tmp/flora-lj1r-public-design'
from cios.applications.flora import visual_v2
from cios.applications.flora.banking_portfolio import BANKS
basis=visual_v2.basis();audit=json.loads((D/'Research-Audit.json').read_text())
slugnames=[('barclays','Barclays'),('hsbc-uk','HSBC UK'),('lloyds','Lloyds Banking Group'),('natwest','NatWest Group'),('santander-uk','Santander UK')]
layernames={'enterprises':'Enterprises','suppliers':'Customers & Suppliers','regulators':'Regulators'}
def filename(state,layer='enterprises'):return f'{state:02d}-'+{1:'uk',2:'banking',3:'groups',4:'lloyds'}[state]+('' if layer=='enterprises' else '-'+layer)+'.html'
def link(txt,href,attrs=''):return f'<a href="{href}" {attrs}>{e(txt)}</a>'
def focus(id,title,body,back):return f'<section class="focus" id="{id}" tabindex="-1" aria-labelledby="{id}-title"><a class="close" href="{back}" aria-label="Close {e(title,quote=True)}">×</a><h2 id="{id}-title">{e(title)}</h2>{body}</section>'
# Every coordinate refers to its own original illustration, never to a preceding screen's crop.
nodes={2:[('boe','Bank of England',20,34,'regulators',None),('pra','PRA',38,23,'regulators',None),('groups','Banking groups',77,36,'enterprises',None),('customers','Households & businesses',18,80,'suppliers',None),('payments','Payments',62,72,'enterprises',None),('fca','FCA',88,66,'regulators',None)],3:[('barclays','Barclays',18,39,'enterprises',None),('hsbc-uk','HSBC UK',50,39,'enterprises',30),('lloyds','Lloyds Banking Group',83,39,'enterprises',44),('natwest','NatWest Group',24,75,'enterprises',None),('santander-uk','Santander UK',82,75,'enterprises',None)],4:[('customers','Household customers',21,76,'suppliers',None),('businesses','Business areas & brands',22,28,'enterprises',None),('economics','Income & capital',50,52,'enterprises',None),('operations','Business customers',80,26,'enterprises',None),('technology','Data, cloud & AI',83,66,'suppliers',76)]}
imgnames={2:'banking-ecosystem.png',3:'banking-groups.png',4:'lloyds-world.png'}
def world(state,layer):
 if state==1:
  body='<figure class="world" aria-labelledby="world-desc"><figcaption class="sr-only" id="world-desc">Original UK economic panorama. Twenty unchanged industry labels. Underlined green-outlined labels open the three available public industry experiences. Availability does not imply complete research. Technology and Aviation open the existing FLORA site; Banking follows this local design journey.</figcaption>'
  rows=[]
  for d in basis['districts']:
   available=visual_v2.RESEARCH.get(d['sic']);href=None
   if available:href=filename(2) if d['sic']=='K' else 'https://flora-current.onrender.com'+available[1]
   rows.append((d['id'],d['label'],*d['position'],'enterprises',None,href,available))
  asset='assets/uk-economy.webp'
 else:
  body='<figure class="world" aria-label="'+e({2:'UK Banking ecosystem',3:'Five equal-entry banking enterprises',4:'Illustrated Lloyds commercial world'}[state],quote=True)+'">'
  rows=[(id,txt,x,y,kind,my,filename(3,layer) if state==2 and id=='groups' else '#'+id,None) for id,txt,x,y,kind,my in nodes[state]]
  asset='assets/'+imgnames[state]
 for side in ['left','right']:
  body+=f'<div class="half {side}"><img src="{asset}" width="1536" height="1024" alt="">'
  body+='</div>'
 for id,txt,x,y,kind,my,href,available in rows:
  right=x>=50;lx=(x-50)*2 if right else x*2;my=my or y;fy=(my+(100 if right else 0))/2
  cls='spot '+('available' if state==1 and available else 'inert' if state==1 else 'active')+(' layer-focus' if layer==kind and layer!='enterprises' else '')
  attrs=f'class="{cls}" style="--x:{x}%;--y:{y}%;--mx:{lx}%;--fy:{fy}%" data-label-id="{id}" data-kind="{kind}"'
  if href:
   aria=(available[0]+': open available industry experience; '+txt+' is its broader section') if available else ('Explore '+txt)
   sub={'businesses':'Halifax branches: 2027 plan','economics':'2030 cost:income target <45%','technology':'Envoy · Google Cloud','operations':'Credit, payments & service','customers':'Deposits, lending & payments'}.get(id) if state==4 else None
   body+=f'<a href="{href}" {attrs} aria-label="{e(aria,quote=True)}">{e(txt)} <span class="cue" aria-hidden="true">'+('↗' if available and id not in ['uk-sic07-k'] else '›')+'</span>'+('<small>'+e(sub)+'</small>' if sub else '')+'</a>'
  else:body+=f'<span {attrs}>{e(txt)}</span>'
 return body+'</figure>'
def source_body(state):
 if state==1:return visual_v2._sources(None)
 body='<p>Existing public-source research, frozen for design review. Dates and original status remain attached. Newly generated architectural scenes are illustrative, not evidence or actual office/tenant/organisational maps.</p>'
 if state in [2,3]:body+='<p>Banking labels refer to selected known enterprises and economic roles, not a complete census or revenue/height rank. The 8.1% figure is the broad SIC K Finance & insurance section, UK 2024 GVA, current basic prices—not Banking-only market share.</p><a href="https://www.bankofengland.co.uk/prudential-regulation/publication/2026/june/pra-annual-report-2025-26">PRA annual report reference, published in existing Banking Foundation</a><a href="https://www.bankofengland.co.uk/payment-and-settlement/payment-and-settlement-statistics">Bank of England payment and settlement reference</a><a href="https://www.fca.org.uk/publications/multi-firm-reviews/strategic-review-retail-banking-business-models">FCA banking-model reference</a><p>These institutional/category references are inherited citations, not new verification of a particular firm relationship. PRA is shown as the Bank’s prudential-regulation function, not a separate commercial institution. Current firm-specific applicability remains unverified.</p>'
 if state==4:
  for cid in ['LBG-Q326-DEPOSITS','LBG-Q326-PROFIT','LBG-A2030-CIR','LBG-ENVOY-GOOGLE','LBG-BRAND26-TIMING']:
   c=audit['claims'][cid];body+=f'<h3>{e(c["statement"])}</h3><p>{e(c["reporting_period"])} · {e(c["verification"])}.</p>'
   for s in c['source_records']:body+=f'<a href="{e(s["url"],quote=True)}">{e(s["title"])}</a><p>Publication: {e(s.get("publication_date") or "not established")}. {e(s.get("limitation") or "Inherited source limitations apply.")}</p>'
  body+='<p>No primary current income/operating-cost/growth reconciliation, complete entity hierarchy, leadership or critical-system inventory is supplied. Historical profile labels and older repository-reported figures are not silently upgraded. See targeted research gaps.</p>'
 return body
for state in range(1,5):
 for layer in (['enterprises'] if state==1 else layernames):
  file=filename(state,layer);title={1:'United Kingdom',2:'UK Banking',3:'Banking groups',4:'Lloyds Banking Group'}[state]
  crumb='' if state==1 else '<nav class="breadcrumb" aria-label="Current scope">'+link('UK',filename(1))+(' › '+link('Banking',filename(2,layer)) if state>=3 else '')+(' › '+link('Groups',filename(3,layer)) if state==4 else '')+'</nav>'
  layernav='' if state==1 else '<details class="layers"><summary>Layers</summary><nav aria-label="Context layers">'+''.join(link(name,filename(state,k),'aria-current="page"' if k==layer else '') for k,name in layernames.items())+'</nav></details>'
  metric={1:'<strong>£2.62tn</strong> UK GVA · 2024 · current basic prices',2:'Finance & insurance: 8.1% of UK GVA · 2024 · current basic prices',3:'',4:'<strong>£502.8bn</strong> Group deposits · 30 Sep 2026 &nbsp; <span><strong>£6.6bn</strong> Group statutory pretax profit · nine months to 30 Sep 2026</span>'}[state]
  header='<header><a class="wordmark" href="01-uk.html">FLORA</a><nav aria-label="Product"><a href="01-uk.html">Home</a><details><summary>Explore</summary><div class="menu">'+link('UK Economy',filename(1))+link('UK Banking',filename(2))+link('Banking groups',filename(3))+'</div></details><details class="sources"><summary>Sources</summary><div class="menu source-menu">'+source_body(state)+'</div></details></nav></header>'
  body=crumb+'<div class="page-title"><h1>'+title+'</h1>'+layernav+'</div>'+(f'<p class="metric">{metric}</p>' if metric else '')+world(state,layer)
  if state==2:
   details={'boe':('Bank of England','<p>Central banking, financial stability and sterling payment/settlement context. This illustration does not assign a contractual relationship to every bank.</p>'),'pra':('PRA','<p>The Bank of England’s prudential-regulation function, shown separately for its distinct role. Sector-policy references do not establish the applicable Lloyds legal entity, permissions or current obligation.</p>'),'fca':('FCA','<p>A distinct conduct regulator and banking-model policy actor. Firm/activity applicability is not inferred from sector policy.</p>'),'payments':('Payments & settlement','<p>CHAPS/RTGS, Faster Payments and Bacs are grounded sector infrastructure references. Current operator, participation and bank-specific contracts require the targeted infrastructure audit.</p>'),'customers':('Households & businesses','<p>Deposits, credit, payments and service connect households and business customers. No named corporate customer relationship is asserted.</p>')}
   for id,(t,b) in details.items():body+=focus(id,t,b,file)
  if state==3:
   for slug,name in slugnames:
    desc={'barclays':'Universal-banking portfolio reference; legal entity scope and current figures need primary confirmation.','hsbc-uk':'UK banking enterprise reference, distinct from HSBC Group.','lloyds':'UK-centred banking franchise; a reviewed-source illustrated enterprise pilot is available here.','natwest':'Deposit and business-banking franchise represented in the existing repository Twin.','santander-uk':'UK mortgage and deposit franchise represented in the existing repository Twin.'}[slug]
    detail=link('Explore profile →',filename(4,layer),'class="action"') if slug=='lloyds' else '<details><summary>Explore profile</summary><p>'+e(BANKS[slug].description)+'</p><p>Existing curated public-source profile; current detailed financial/organisational verification is incomplete. A rich enterprise composition is not supplied for this bank in this pilot.</p>'+link('Open existing FLORA profile ↗','https://flora-current.onrender.com/enterprises/'+slug)+'</details>'
    body+=focus(slug,name,'<p>'+desc+'</p>'+detail,file)
  if state==4:
   body+='<section class="commercial-story" aria-label="Commercial interpretation"><p><strong>Deposits & customer relationships → lending and hedge → interest, fees & capital.</strong></p><p>Modernise core systems and scale AI while protecting service and proving benefits.</p><p class="question">What customer outcome remains unresolved beyond existing programmes?</p></section>'
   panels={
    'customers':('Customers & value flows','<p>Household savers/borrowers and business customers create deposit, lending, payment and servicing relationships. These are supported customer roles, not named company contracts.</p><p>The economic mechanism links stable funding and hedge income with lending, capital and investment capacity; the precise internal allocation remains unknown.</p>'),
    'businesses':('Businesses, brands & legal boundaries','<p>Lloyds, Halifax, Bank of Scotland and Scottish Widows are recorded brand references in the historical portfolio. They are not all the same kind of legal or organisational entity.</p><p>The July 2026 announcement plans Halifax branch-brand changes through 2027; delivery is not assumed complete. Current subsidiaries, ownership and segment boundaries require primary report reconciliation. The historic Retail / Commercial Banking / Insurance, Pensions and Investments labels are not presented as a verified current organisation chart.</p>'),
    'economics':('How it makes and spends money','<p>Interest and fees, funding costs, operating expenses, credit impairment and capital constraints are the banking economic mechanism—not an approved financial model.</p><p><strong>2030 cost:income ambition: below 45% (target, not achieved).</strong> Management also projects about £2bn gross savings; aggregation/run-rate scope needs confirmation and this is not supplier budget.</p><p>Current income, operating-cost amounts, profit reconciliation and comparable growth remain unverified in the reviewed excerpt set. No balancing figures or implied growth rates are fabricated.</p>'),
    'operations':('Business customers, operations & pressures','<p>Businesses use credit, payments and service. Illustrated factories/workplaces represent customer activity, not Lloyds-owned sites. Supported priorities include core modernisation, legacy decommissioning, cloud migration, service continuity and measurable AI benefits. Detailed current core/payments systems, ownership, dependency graph and vendor workshare are not established.</p><p>Investment is described as plateauing at the end of the current cycle. The later strategy presentation plans a 2027 increase subject to opportunity and return discipline. These are distinct periods—not an unrestricted new external budget.</p>'),
    'technology':('Technology, suppliers & control','<p><strong>Envoy: Google Cloud collaboration, announced May 2026.</strong> Built-in controls, monitoring and oversight are described. Contract value, exclusivity, renewal, current effectiveness and wider programme scope remain unknown.</p><p>Vertex AI and model migrations are older repository-reported context, not proof of the current technology inventory. Existing internal teams and partners may already cover delivery.</p>')}
   for id,(t,b) in panels.items():body+=focus(id,t,b,file)
   body+='<details class="studio"><summary>Model the Enterprise <span>· future tool</span></summary><p>Proposed separately in Issue #611. Architecture and owner design approval are required. No model, scenario, formula, editable assumption or simulation is implemented here.</p>'+link('Read the proposed scope ↗','https://github.com/rdidale-jpg/CIOS/issues/611')+'</details>'
  if state in [2,3] and layer=='suppliers':body+='<aside class="layer-note">Customer segments and infrastructure roles are grounded. Named supplier/customer links require enterprise-specific evidence; none are inferred across this district.</aside>'
  if state==4 and layer=='suppliers':body+='<aside class="layer-note"><strong>'+('Lloyds reference case: ' if state==2 else '')+'Google Cloud → Lloyds Envoy collaboration.</strong> Named customer contracts, other supplier workshares and new external scope remain unknown.</aside>'
  if state>=2 and layer=='regulators':body+='<aside class="layer-note"><strong>BoE · PRA · FCA: distinct institutional roles.</strong> Sector context only; no unverified regulator-to-bank legal-entity obligation is drawn.</aside>'
  # Native semantic alternative is one optional disclosure, not a second default gateway.
  alt=''
  if state==1:alt='<p>All twenty original sector labels remain visible. Only the three public researched-route entries are linked. A destination retains its own access rules.</p>'
  else:alt=''.join(link(txt,filename(3,layer) if state==2 and id=='groups' else '#'+id) for id,txt,*_ in nodes[state])
  body+='<details class="text-view"><summary>Text view</summary>'+alt+'</details>'
  if state>1:body+='<footer>'+link('← Back',filename(state-1,layer if state>2 else 'enterprises'))+'</footer>'
  html='<!doctype html><html lang="en-GB"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+title+' · FLORA LJ-1R design</title><link rel="stylesheet" href="rich.css"><body><a class="skip" href="#main">Skip to landscape</a>'+header+'<main id="main" tabindex="-1" data-state="'+str(state)+'" data-layer="'+layer+'">'+body+'</main></body></html>'
  (D/file).write_text(html)
manifest={'baseline_commit':'208015805e12772fb425cb014870db697f878f6d','uk_artwork':'cios/applications/flora/visual_v2_assets/uk-economy.webp','uk_sha256':hashlib.sha256((R/'cios/applications/flora/visual_v2_assets/uk-economy.webp').read_bytes()).hexdigest(),'generator':'image_gen, 2026-11-14, explicitly commissioned design artwork','style_reference':'Original accepted UK panorama used for visual language only; not composited, cropped or repeated as deeper artwork','rights_boundary':'New generated conceptual architectural art; no publisher photo, company logo or claim of real premises. Research/excerpt/source rights remain separate and unchanged. Owner visual acceptance pending.','scenes':[]}
for f in imgnames.values():manifest['scenes'].append({'file':'assets/'+f,'sha256':hashlib.sha256((D/'assets'/f).read_bytes()).hexdigest(),'composition':'Independent original 1536×1024 scene; no factual label baked into raster','purpose':f.removesuffix('.png')})
(D/'Artwork-Provenance.json').write_text(json.dumps(manifest,indent=2)+'\n')
(D/'Interaction-Mapping.json').write_text(json.dumps({'UK_labels':[{'id':d['id'],'label':d['label'],'position':d['position'],'route':visual_v2.RESEARCH.get(d['sic'])} for d in basis['districts']],'scene_nodes':nodes,'coordinates':'Percent of own illustration. Mobile preserves both halves; center-edge labels clamp to readable bounds and may use an explicit alternate y.','semantics':'Generated buildings have no financial, ownership, geographic or legal-entity meaning. Interaction and evidence remain separate from pixels.','model_studio':'Optional future entry only; Issue #611, no engine or store'},indent=2)+'\n')
print('Four independent screen compositions, ten native state/layer pages generated')
