"""LJ-1 static design projection; no application routes, service or store changes."""
from pathlib import Path
from html import escape as e
import os,re,json,copy,hashlib
R=Path(__file__).resolve().parents[4];D=R/'docs/flora-runtime/living-journey-lj1'
os.environ['FLORA_DATA_DIR']='/tmp/flora-lj1-anonymous-design'
from cios.applications.flora import visual_v2,design_system as ds
from cios.applications.flora.banking_portfolio import BANKS
from cios.applications.flora.research_intelligence.model import load_assessment
from cios.applications.flora.research_intelligence.living_map_specs import build_living_map
from cios.applications.flora.research_intelligence.living_map import _scene,_building,_asset,STYLE as MAP_STYLE
basis=visual_v2.basis();assessment=load_assessment();spec=build_living_map(assessment)
raw=json.loads((R/'enterprise-knowledge/banking/research-model/Assessment-Overlay.json').read_text())
claims={c['id']:c for c in raw['claims']};sources={s['id']:s for s in raw['sources']}
for src,dest in [('cios/applications/flora/visual_v2_assets/uk-economy.webp','uk-economy.webp'),('cios/applications/flora/visual_v2_assets/visual.css','world.css'),('cios/applications/flora/design_assets/design.css','design.css')]:
 (D/'assets'/dest).write_bytes((R/src).read_bytes())
# Freeze the accepted Banking illustration primitives into review-only SVG; actual source stays untouched.
quiet=copy.deepcopy(spec);quiet['flows']=[]
for n in quiet['map_nodes']:
 n['participants']=[];n['conflict_ids']=[]
original_scene=_scene(spec,'overview');(D/'assets/accepted-banking-reference.svg').write_text(original_scene)
quiet_scene=_scene(quiet,'overview')
# Read-only original group, bank labels and source pins; never promote profile data.
actors=[('lloyds','Lloyds Banking Group'),('barclays','Barclays'),('natwest','NatWest Group'),('hsbc-uk','HSBC UK'),('santander-uk','Santander UK')]
positions={'lloyds':(720,300),'barclays':(350,430),'natwest':(1080,430),'hsbc-uk':(480,730),'santander-uk':(960,730)}
layers=['enterprises','suppliers','regulators']
def filename(state,layer='enterprises'):return f'{state:02d}-'+{1:'uk',2:'banking',3:'groups',4:'lloyds',5:'deeper'}[state]+('' if layer=='enterprises' else '-'+layer)+'.html'
def anchor(label,url,extra=''):return f'<a href="{url}" {extra}>{e(label)}</a>'
def scene_base():
 return '<svg class="bank-scene" viewBox="0 0 1440 1080" role="group" aria-label="Banking landscape; conceptual roles, not locations or financial rank"><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 10 5 0 10" fill="none" stroke="#466e60" stroke-width="1.5"/></marker></defs><rect width="1440" height="1080" fill="#f6f3e6"/><path d="M0 385Q240 340 480 410T960 380T1440 420V515Q1160 460 920 485T450 475T0 460Z" fill="#dce9e3"/><path d="M0 423Q240 378 480 448T960 418T1440 458" fill="none" stroke="#adc8bc" stroke-width="2"/><path d="M90 980 1420 605M30 315 1310 40" stroke="#e7e3cf" stroke-width="33"/>'
def label(x,y,txt,size=20):
 # Real SVG text, not raster labels; wrap deliberately for no tiny responsive text.
 return f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}" fill="#173f37" style="paint-order:stroke;stroke:#f6f3e6;stroke-width:7px;stroke-linejoin:round">{e(txt)}</text>'
def building_actor(x,y,name,href,selected=False):
 return f'<a href="{href}" aria-label="Focus {e(name)}"'+(' aria-current="location"' if selected else '')+'>'+f'<ellipse cx="{x}" cy="{y+50}" rx="130" ry="62" fill="'+('#d9e6d3' if selected else '#e9ebd9')+'" stroke="#91ac90"/>'+_building(x,y-70,170,100)+label(x,y+112,name,22)+'</a>'
def overlay(layer,state):
 if layer=='suppliers':
  return '<path d="M300 260Q500 120 670 230" stroke="#466e60" stroke-width="3" fill="none" marker-end="url(#arrow)"/>'+building_actor(270,230,'Google Cloud','#google')+label(495,170,'Envoy collaboration',18)
 if layer=='regulators':
  return building_actor(260,220,'PRA','#pra')+building_actor(1180,220,'FCA','#fca')+label(720,100,'UK sector policy · firm scope to confirm',18)
 return ''
def portrait(layer):
 out=scene_base()+building_actor(720,200,'Lloyds Banking Group',filename(4,layer),True)
 for x,title,href in [(350,'Retail','#retail'),(720,'Commercial Banking','#commercial'),(1090,'Insurance, Pensions & Investments','#insurance')]:
  out+=f'<path d="M720 320Q{x} 340 {x} 470" fill="none" stroke="#aabd9e" stroke-width="2"/>'
  node={'position':[x,520],'illustration':{'Retail':'home','Commercial Banking':'bank'}.get(title,'shield'),'label':title,'conflict_ids':[]}
  out+='<a href="'+href+'" aria-label="Explore '+e(title)+'">'+_asset('banking',node)+'</a>'
 out+=label(720,750,'Business areas · historical profile; current boundaries to confirm',18)
 out+=label(720,880,'Customer relationships → funding & lending → income, risk & capital',20)
 return out+overlay(layer,4)+'</svg>'
def scene(state,layer):
 if state==2 and layer!='enterprises':
  out=scene_base()
  if layer=='suppliers':
   out+=building_actor(720,300,'Lloyds Envoy','#google')+label(720,780,'Lloyds reference case · wider supplier map unavailable',20)
  else:
   node=next(n for n in quiet['map_nodes'] if n['id']=='VI-LBG-CONTROL')
   out+=_asset('banking',node)
  return out+overlay(layer,2)+'</svg>'
 if state==2:
  out=quiet_scene
  # Accepted original activity positions and labels; selected district action over lending.
  for node in quiet['map_nodes']:
   dest=filename(3,layer) if node['id']=='VI-LBG-LEND' else '#district-'+node['id']
   out=out.replace("href='#lm-banking-"+node['id']+"'","href='"+dest+"'")
  out=out.replace('</svg>', '<a href="'+filename(3,layer)+'" aria-label="Explore Major banking groups"><rect x="835" y="390" width="330" height="60" rx="25" fill="#fffdf6" stroke="#91ac90"/>'+label(1000,429,'Major banking groups →',22)+'</a>'+overlay(layer,2)+'</svg>')
  out=re.sub(r'<text[^>]*>.*?</text>',lambda m:'' if 'Dashed arrows' in m.group(0) else m.group(0),out,flags=re.S)
  return out.replace("viewBox='0 0 1440 1080'",'class="bank-scene" viewBox="0 0 1440 1080"')
 if state==3:
  return scene_base()+''.join(building_actor(*positions[slug],name,filename(4,layer) if slug=='lloyds' else '#'+slug,slug=='lloyds') for slug,name in actors)+overlay(layer,3)+'</svg>'
 return portrait(layer)
def mobile_scene(state,layer):
 out=scene_base().replace('viewBox="0 0 1440 1080"','viewBox="0 0 720 2100"')
 out=out.replace('<rect width="1440" height="1080"','<rect width="1440" height="2100"')
 if state==2:
  for idx,n in enumerate(quiet['map_nodes']):
   n=copy.deepcopy(n);n['position']=[180+(idx%2)*360,180+(idx//2)*390]
   out+='<a href="'+(filename(3,layer) if n['id']=='VI-LBG-LEND' else '#district-'+n['id'])+'" aria-label="Explore '+e(n['label'])+'">'+_asset('banking',n)+'</a>'
 elif state==3:
  for idx,(slug,name) in enumerate(actors):
   x,y=180+(idx%2)*360,220+(idx//2)*580
   out+=building_actor(x,y,name,filename(4,layer) if slug=='lloyds' else '#'+slug,slug=='lloyds')
 else:
  out=out.replace('0 0 720 2100','0 0 720 1450')
  out+=building_actor(360,180,'Lloyds Banking Group',filename(4,layer),True)
  for y,name,href in [(520,'Retail','#retail'),(850,'Commercial Banking','#commercial'),(1180,'Insurance, Pensions & Investments','#insurance')]:
   node={'position':[360,y],'illustration':{'Retail':'home','Commercial Banking':'bank'}.get(name,'shield'),'label':name,'conflict_ids':[]}
   out+='<a href="'+href+'" aria-label="Explore '+e(name)+'">'+_asset('banking',node)+'</a>'
  out+=label(360,1400,'Historical profile · boundaries to confirm',24)
 if layer!='enterprises':
  # Compact counterpart to the desktop contextual layer; detailed scope follows image.
  out+=label(360,2030,'Google Cloud → Envoy' if layer=='suppliers' else 'PRA / FCA · sector context',26)
 out=out.replace('id="arrow"','id="mobile-arrow"').replace('url(#arrow)','url(#mobile-arrow)')
 return '<div class="mobile-scene">'+out+'</svg></div>'
def source_detail():
 ids=['PR-LBG-Q326','PR-LBG-AR25','PR-LBG-ENVOY','PR-PRA-PS726','PR-FCA-RES26']
 return '<details class="support"><summary>Sources and limits</summary><p>Frozen reviewed repository references; no fresh source verification or canonical promotion. Short reviewed excerpts, not full original-file archives. Company reports do not establish buying intent. Read the linked source for its full context.</p>'+''.join(f'<p><a href="{e(sources[k]["url"],quote=True)}">{e(sources[k]["title"])}</a> · published {e(sources[k].get("publication_date") or "unknown")} · {e(sources[k]["reporting_period"])}</p>' for k in ids)+'<p>GVA share is the broad SIC K Finance and insurance section, not Banking-only; 2024 UK at current basic prices. Existing ONS extract: cios/applications/flora/visual_v2_assets/economy.json.</p><p>Historical divisions: existing BANKS[lloyds].divisions in banking_portfolio.py; segment-effective date/claim-level primary citation not established. These labels are historical profile context, not verified current boundaries.</p><p>Firm-level PRA/FCA applicability is not proven by the sector-policy citations. Named customers and supplier contract terms are unavailable. Heights, geography and grouping have no financial meaning. No external scope, budget or buyer is inferred.</p></details>'
def scope_header(state,layer):
 # Original compact shell anatomy; no rejected VA-1 layout is imported.
 source_body=visual_v2._sources(None) if state==1 else source_detail().split('</summary>',1)[1].rsplit('</details>',1)[0]
 return '<header class="product-header"><a class="wordmark" href="01-uk.html">FLORA</a><nav aria-label="Product"><a href="01-uk.html">Home</a><details class="product-menu"><summary>Explore</summary><div class="menu-sheet"><a href="01-uk.html">UK Economy</a><a href="'+filename(2,layer)+'">UK Banking</a><a href="'+filename(3,layer)+'">Major banking groups</a></div></details><details class="sources-menu"><summary>Sources</summary><div class="menu-sheet source-sheet">'+source_body+'</div></details></nav></header>'
def layers_nav(state,layer):
 return '<details class="layer-picker"><summary>Layers</summary><nav aria-label="Context layers">'+''.join(anchor(t,filename(state,k),'aria-current="page"' if k==layer else '') for k,t in [('enterprises','Enterprises'),('suppliers','Customers & Suppliers'),('regulators','Regulators')])+'</nav></details>'
def context_panel(layer):
 if layer=='suppliers':return '<aside class="context" id="google"><h2>Google Cloud → Lloyds Envoy</h2><p>Named platform collaboration, announced May 2026. Contract value, renewal and wider workshare are unknown.</p><details><summary>Customers</summary><p>Retail and business customer roles are supported conceptually. Named enterprise customers and contractual links are not supplied; none are drawn.</p></details></aside>'
 if layer=='regulators':return '<aside class="context"><h2>Sector oversight</h2><p id="pra">PRA: prudential incident and third-party reporting policy.</p><p id="fca">FCA: operational-resilience reporting context. Firm and activity applicability require checking.</p></aside>'
 return ''
for state in range(1,6):
 for layer in (['enterprises'] if state==1 else layers):
  title={1:'United Kingdom',2:'UK Banking',3:'Major banking groups',4:'Lloyds Banking Group',5:'The next customer question'}[state]
  back=filename(max(1,state-1),layer if state>2 else 'enterprises')
  crumb='' if state==1 else '<nav class="breadcrumb" aria-label="Current context">'+anchor('UK',filename(1))+'<span>›</span>'+anchor('Banking',filename(2,layer))+(('<span>›</span>'+anchor('Major banking groups',filename(3,layer))) if state>=3 else '')+('<span>›</span>'+anchor('Lloyds',filename(4,layer)) if state>=4 else '')+'</nav>'
  if state==1:
   body=visual_v2._home().replace('/visual-v2/assets/uk-artwork','assets/uk-economy.webp').replace('/industries/banking','02-banking.html').replace('/industries/technology/experience','#other-industries').replace('/industries/aviation','#other-industries')
   body+='<details class="support" id="other-industries"><summary>Other researched industries</summary><p>Technology and Aviation retain their existing production routes. This bounded design prototype follows Banking only.</p></details>'
  else:
   metric='<p class="metric">8.1% of UK GVA · Finance & insurance · 2024 · current basic prices</p>' if state in [2,3] else '<p class="metric">£502.8bn customer deposits · Group · 30 Sep 2026<br>£6.6bn statutory pretax profit · Group · nine months to 30 Sep 2026</p>'
   head=f'<div class="journey-head"><div>{crumb}<h1>{title}</h1></div>{layers_nav(state,layer)}</div>'+metric
   body=head+'<div class="scene-frame">'+scene(state,layer)+mobile_scene(state,layer)+'</div>'+context_panel(layer)
   if state==2:
    body+='<a class="next mobile-next" href="'+filename(3,layer)+'">Explore Major banking groups →</a>'
    for node in quiet['map_nodes']:
     if node['id']=='VI-LBG-LEND':continue
     body+='<aside class="actor-focus" id="district-'+node['id']+'"><h2>'+e(node['label'])+'</h2><p>'+e(node['purpose'])+'</p><a href="'+filename(2,layer)+'">Back to ecosystem</a></aside>'
   if state==3:
    body+='<a class="next" href="'+filename(4,layer)+'">Focus Lloyds →</a>'
    for slug,name in actors[1:]:body+=f'<aside class="actor-focus" id="{slug}"><h2>{name}</h2><p>Selected enterprise from the existing Banking portfolio. Current comparable scale is not supplied. This pilot deepens Lloyds only.</p><a href="{filename(3,layer)}">Back to group landscape</a></aside>'
   if state==4:
    body+='<p class="pressure">Modernise and scale AI while protecting live services and proving benefits.</p><a class="next" href="'+filename(5,layer)+'">Explore deeper →</a>'
   if state==5:
    body=head+'<div class="deep-scene">'+portrait(layer)+mobile_scene(4,layer)+'<aside class="question"><h2>Which process decisions, if any, are still open beyond the existing AI rollout?</h2><p>Ask whether a customer-owned process needs redesign, rather than more tools. Compare a process-only or non-AI alternative first.</p><details><summary>Why ask this?</summary><p>Existing reviewed research reports AI expansion and built-in Envoy controls. An active platform does not prove an unmet business-process need or an early shaping window. Investment is described as plateauing at the end of the strategic cycle.</p><p>Counter-evidence: internal teams and current partners may already cover the work. Customer intent, access, budget and external scope are unknown.</p><p>Next validation: which measurable service outcome remains unresolved, which decision is still open, and who is authorised to discuss it?</p></details></aside></div>'+context_panel(layer)+'<a class="next" href="'+filename(4,layer)+'">Back to Lloyds portrait →</a>'
   body+='<details class="support"><summary>Explore the picture as text</summary>'+(''.join(anchor(n['label'],filename(3,layer) if n['id']=='VI-LBG-LEND' else '#district-'+n['id']) for n in quiet['map_nodes']) if state==2 else ''.join(anchor(name,filename(4,layer) if slug=='lloyds' else '#'+slug) for slug,name in actors) if state==3 else '<p id="retail">Retail · customer banking, deposits and lending.</p><p id="commercial">Commercial Banking · business relationships and banking services.</p><p id="insurance">Insurance, Pensions and Investments · protection and long-term financial needs.</p><p>Division labels are retained from the historical repository profile; current segment boundaries require confirmation. The operating model is an explanatory synthesis, not an actual organisation, system or supplier topology.</p><p>Deposit direction: £496.5bn at 31 Dec 2025 to £502.8bn at 30 Sep 2026. Balance snapshots, not revenue growth or a constant-currency/organic growth series. Comparable revenue growth is unavailable.</p>')+'</details>'
  html='<!doctype html><html lang="en-GB"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+title+' · FLORA LJ-1 design</title><link rel="stylesheet" href="assets/design.css"><link rel="stylesheet" href="assets/world.css"><link rel="stylesheet" href="journey.css"><body class="ds-page visual-world"><a class="skip" href="#content">Skip to scene</a>'+scope_header(state,layer)+'<main id="content" tabindex="-1" data-state="'+str(state)+'" data-layer="'+layer+'">'+body+'</main>'+(('<footer>'+anchor('← Back',back)+'<span>Concept landscape · scale not implied</span></footer>') if state>1 else '')+'</body></html>'
  (D/filename(state,layer)).write_text(html)
# Review-only evidence map: explicit projection of existing facts, no new durable intelligence owner.
mapping={'base_commit':'0cb07c2e78ccb16240c799b31cd62736e2135529','authority':'Static design mapping only; no source/relationship/Twin owner added','labels':[],'claims':{},'relationships':[],'unavailable':['Named enterprise customers','Other bank-specific supplier contracts','Firm-specific regulatory-register proof','Current primary-source divisional boundaries','Comparable company revenue growth','External scope, procurement, budget and buying intent']}
for d in basis['districts']:mapping['labels'].append({'label':d['label'],'source':'cios/applications/flora/visual_v2_assets/economy.json','id':d['id'],'scope':d['share_scope'],'position':d['position'],'weight_per_thousand':d['weight_per_thousand'],'source_records':[{k:v for k,v in z.items() if k in ['id','url','title','publication_date','reviewed_at','limitation']} for z in basis['sources'] if z['id']==d['source_id']],'status':'frozen public presentation extract','rights':'Existing approved conceptual artwork; ONS statistical references retain OGL/recorded limits'})
for n in quiet['map_nodes']:mapping['labels'].append({'label':n['label'],'source':'enterprise-knowledge/banking/research-model/Living-Map.json','id':n['id'],'status':'conceptual activity/role; not ownership or a contract','scope':'UK Retail/Commercial Banking conceptual system','evidence_refs':n.get('evidence_refs',[]),'inherited_evidence':[ {k:v for k,v in ev.items() if k not in ['passage','label']} for ev in n.get('evidence',[])],'source_limits':n.get('limitations'),'original_conflicts':next(a['conflict_ids'] for a in spec['map_nodes'] if a['id']==n['id']),'period':'Inherited source-specific; no new date','rights':'Existing FLORA SVG illustration primitives; public-source limits unchanged'})
for slug,name in actors:mapping['labels'].append({'label':name,'id':slug,'source':'cios/applications/flora/banking_portfolio.py / BANKS','scope':'Selected Banking enterprise identity; HSBC UK is not HSBC Group','status':'historical curated public-source portfolio; not ranked/size-weighted','period':'Historical profile; no current primary verification','rights':'Existing public-source fixture; no logos/new rights'})
for label in BANKS['lloyds'].divisions:mapping['labels'].append({'label':label,'source':'cios/applications/flora/banking_portfolio.py / BANKS[lloyds].divisions','scope':'Lloyds historical business-area labels','status':'profile-supported; current effective segmentation not independently verified','period':'Not established for division fields','rights':'Paraphrased existing public-source profile, not new primary research'})
for cid in ['LBG-Q326-DEPOSITS','LBG-Q326-PROFIT','LBG-Q326-INVESTMENT','LBG-ENVOY-GOOGLE','LBG-ENVOY-CONTROLS','LBG-DEPOSITS']:
 c=claims[cid];mapping['claims'][cid]={k:v for k,v in c.items() if k not in ['primary_quotes','repository_quote']};mapping['claims'][cid]['source_records']=[{k:v for k,v in sources[sid].items() if k in ['id','title','url','reporting_period','publication_date','retrieved_at','verification','limitation','reviewed_by','text_path']} for sid in c['source_ids']]
mapping['relationships']=[{'drawn_direction':'Google Cloud → Lloyds Envoy','original_relation_id':'REV-ENVOY-GOOGLE','original_direction':'BK-ENT-001 reported_uses SUP-GOOGLE','claim':'LBG-ENVOY-GOOGLE','source':'PR-LBG-ENVOY','scope':'May 2026 platform collaboration; not every Group programme','status':'source_supported_relationship in assessment; not independent implementation proof','unknown':['contract value','renewal','exclusivity','current effectiveness']},{'drawn':'PRA / FCA sector-policy context; no line to Lloyds legal entity','sources':['PR-PRA-PS726','PR-FCA-RES26'],'scope':'UK in-scope regulated activities; applicability not established here','status':'sector context; direct company relationship unverified'},{'drawn':'Customer roles only; no named customer links','scope':'conceptual industry/business model','status':'named relationships unavailable'}]
mapping['metrics']=[{'display':'£2.62tn UK GVA','source':'visual_v2_assets/economy.json / ONS-BB-2026','scope':'UK; GBP; current basic prices','period':'2024','status':'frozen public presentation extract; no fresh verification','rights':'ONS reference; existing OGL/source limitations'},{'display':'8.1%','source':'economy.json / SIC K weight 81 per thousand','scope':'Finance and insurance; broader than Banking','period':'2024 UK GVA, current basic prices','status':'frozen published section weight','rights':'ONS reference; existing OGL/source limitations'},{'display':'£502.8bn customer deposits','claim':'LBG-Q326-DEPOSITS','scope':'Lloyds consolidated Group; balance at 30 Sep 2026','status':'source-supported reviewed company statement','rights':'Existing short reviewed excerpts; original-file bytes not archived'},{'display':'£6.6bn statutory pretax profit','claim':'LBG-Q326-PROFIT','scope':'Lloyds consolidated Group; nine months to 30 Sep 2026','status':'source-supported reviewed company statement','rights':'Existing short reviewed excerpts; original-file bytes not archived'}]
mapping['interpretations']=[{'display':'Customer relationships → funding & lending → income, risk & capital','source':'Lloyds-Enterprise-Twin.md structural hedge and customer-primacy mechanisms; Banking-Industry-Foundation.md','scope':'Explanatory economic mechanism, not a system dataflow or formal organisation chart','period':'Inherited historical research, not independently updated','rights':'Paraphrased existing repository research'},{'display':'Modernise and scale AI while protecting live services and proving benefits','claim_refs':['LBG-ENVOY-CONTROLS','LBG-Q326-INVESTMENT'],'scope':'Commercial interpretation; no verified unmet need or external scope','period':'2026 reviewed source context','rights':'Derived question over existing references'},{'display':'Which process decisions, if any, are still open beyond the existing AI rollout?','source':'Existing Lloyds AI-first validation approach / buying-trigger-591; Envoy controls and investment commentary','scope':'Human validation question; no early-influence classification or live opportunity','period':'Existing source cutoffs; no new intelligence','rights':'Derived interpretation; existing source limits retained'}]
(D/'Evidence-Mapping.json').write_text(json.dumps(mapping,indent=2)+'\n')
files=['cios/applications/flora/visual_v2_assets/uk-economy.webp','cios/applications/flora/visual_v2_assets/economy.json','cios/applications/flora/research_intelligence/living_map.py','enterprise-knowledge/banking/research-model/Living-Map.json','enterprise-knowledge/banking/research-model/Assessment-Overlay.json']
(D/'Reference-Hashes.json').write_text(json.dumps({p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in files},indent=2)+'\n')
print('13 static states/layers created; original architecture/data unchanged')
