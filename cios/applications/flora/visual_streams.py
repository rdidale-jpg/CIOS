"""Scope-aware visual presentation over existing public research owners.

No Twin/Evidence/pressure store, model call, private record resolution or write
service. Public reference identities never authorize a private Canvas lookup.
"""
from dataclasses import dataclass, replace
from functools import lru_cache
from html import escape as e
import hashlib
import json
import re
from pathlib import Path
from types import MappingProxyType
from urllib.parse import urlencode

from . import design_system as ds, visual_v2
from .research_intelligence import model, registry
from .research_intelligence.visual_specs import claim_state

ASSETS=Path(__file__).with_name('visual_stream_assets')
ASSET_BASE='/visual-streams/assets/'
DESIGN='c6bf2280594922db6951c5c36205984c85ca4aea'
# Finite public reference bindings, not a second Twin registry or an ACL.
SCOPES=MappingProxyType({
 'uk':{'route':'/','kind':'country','streams':('landscape','forces'),'title':'United Kingdom','identity':'GB'},
 'banking':{'route':'/industries/banking','kind':'industry','streams':('landscape','forces'),'domain':'banking','identity_key':'industry_twin_id','sic':'K'},
 'lloyds':{'route':'/enterprises/lloyds','kind':'enterprise','streams':('inside','landscape','forces'),'domain':'banking','identity_key':'enterprise_twin_id','slug':'lloyds',
           'headline_metrics':(('LBG-Q326-DEPOSITS','Group deposits'),('LBG-Q326-PROFIT','Group statutory pretax profit'))},
})
ROUTES={r['route']:key for key,r in SCOPES.items()} | {'/flora':'uk','/flora/':'uk'}
LAYERS={'enterprises':'Enterprises','suppliers':'Customers & Suppliers','regulators':'Regulators'}
BANKS=('barclays','hsbc-uk','lloyds','natwest','santander-uk')
CAPTION_SOURCES=frozenset({'enterprise-knowledge/banking/research-model/Assessment-Overlay.json',
 'enterprise-knowledge/macro/research-model/Macro-Context-v1.json','cios/applications/flora/visual_v2_assets/economy.json'})
# These are nine presentation questions, not new research records or claims.
GAPS=(('FIN-01','Current income and operating-cost reconciliation'),('FIN-02','Comparable growth and profitability'),
 ('ORG-01','Current businesses, brands and legal subsidiaries'),('OPS-01','Operations and important technology systems'),
 ('REL-01','Current suppliers, partners and customers'),('REG-01','Legal-entity regulatory applicability'),
 ('ORG-02','Current leadership and accountability'),('INF-01','Infrastructure operating relationships'),
 ('COM-01','Remaining influence and external need'))

@dataclass(frozen=True)
class Context:
 scope:str
 stream:str
 layer:str='enterprises'
 selected:str=''
 detail:str=''


def artwork():
 data=json.loads((ASSETS/'artwork.json').read_text())
 if data['design_commit']!=DESIGN or set(data['scenes'])!={s+'-'+v for s,r in SCOPES.items()for v in r['streams']}:
  raise ValueError('Approved visual assets unavailable')
 if set(data['caption_source_pins'])!=CAPTION_SOURCES:raise ValueError('Visual caption source boundary mismatch')
 return data


def geometry():
 data=json.loads((ASSETS/'scenes.json').read_text())
 if data['design_commit']!=DESIGN:raise ValueError('Approved visual geometry unavailable')
 return data['scenes']


@lru_cache(maxsize=1)
def asset_files():
 files={'styles':('streams.css','text/css; charset=utf-8'),'interactions':('streams.js','text/javascript; charset=utf-8')}
 for row in artwork()['scenes'].values():
  for v in row['variants']:
   filename=v['file']
   if Path(filename).name!=filename or not filename.endswith('-'+v['sha256'][:12]+'.webp'):
    raise ValueError('Unsafe image manifest')
   # Existing public route grammar stays extensionless and finite. The file
   # extension is an on-disk concern, not a reason to widen that grammar.
   files[filename.removesuffix('.webp')]=(filename,'image/webp')
 return MappingProxyType(files)


def asset(name):
 if name not in asset_files():raise ValueError('Visual asset unavailable')
 filename,mime=asset_files()[name];p=ASSETS/filename
 if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(ASSETS.resolve()):raise ValueError('Visual asset unavailable')
 try:body=p.read_bytes()
 except OSError:raise ValueError('Visual asset unavailable') from None
 if mime=='image/webp' and not filename.endswith('-'+hashlib.sha256(body).hexdigest()[:12]+'.webp'):
  raise ValueError('Visual asset checksum mismatch')
 if mime=='image/webp':
  expected=next(v['sha256']for row in artwork()['scenes'].values()for v in row['variants']if v['file']==filename)
  if hashlib.sha256(body).hexdigest()!=expected:raise ValueError('Visual asset checksum mismatch')
 return body,mime


def resolve(path,query):
 if path not in ROUTES or set(query)-{'stream','market','layer','selected','detail'} or any(not isinstance(v,list) or len(v)!=1 for v in query.values()):
  raise ValueError('Visual journey unavailable')
 scope=ROUTES[path];binding=SCOPES[scope]
 if query.get('market',['GB'])!=['GB']:raise ValueError('Country unavailable')
 stream=query.get('stream',[binding['streams'][0]])[0]
 layer=query.get('layer',['enterprises'])[0];selected=query.get('selected',[''])[0];detail=query.get('detail',[''])[0]
 if stream not in binding['streams'] or layer not in LAYERS:raise ValueError('Insight view unavailable')
 if binding['kind']=='country':
  if layer!='enterprises' or selected not in ('','banking','technology','aviation'):raise ValueError('Country context unavailable')
 else:
  if selected not in ('',*BANKS):raise ValueError('Enterprise selection unavailable')
  if binding['kind']=='enterprise' and selected not in ('',binding['slug']):raise ValueError('Enterprise context mismatch')
 for key in ('selected','detail'):
  if key in query and not query[key][0]:raise ValueError('Empty visual selector')
 spots=geometry()[scope+'-'+stream]['spots']
 if detail and detail not in {s['id']for s in spots}:raise ValueError('Selected detail unavailable')
 if detail and binding['kind']=='country' and stream=='landscape':raise ValueError('District detail unavailable')
 if binding['kind']=='industry' and detail in BANKS and selected not in ('',detail):raise ValueError('Selected bank mismatch')
 return Context(scope,stream,layer,selected,detail)


def url(ctx,**changes):
 ctx=replace(ctx,**changes)
 q={'stream':ctx.stream}
 if ctx.layer!='enterprises':q['layer']=ctx.layer
 if ctx.selected:q['selected']=ctx.selected
 if ctx.detail:q['detail']=ctx.detail
 return SCOPES[ctx.scope]['route']+'?'+urlencode(q)


def current_data(ctx):
 binding=SCOPES[ctx.scope]
 if binding['kind']=='country':return None
 data=model.load_assessment(binding['domain'])
 ref=registry.enterprise_reference(binding.get('slug',registry.DOMAINS[binding['domain']][1]))
 if (not ref or data['enterprise_twin_id']!=ref.id or
     (binding['kind']=='enterprise' and data.get('enterprise_slug','lloyds')!=binding['slug'])):
  raise ValueError('Unbound public reference')
 # The canonical research owner resolves identity and validates all sources.
 if not data.get(binding['identity_key']):raise ValueError('Twin reference unavailable')
 return data


# Editorial interpretation/question policy from the accepted design. Claims,
# values, dates, kinds and source rights are always resolved from their owners.
FORCE_POLICY={
 'economic':('UK aggregate → possible demand and capacity questions, not bank-specific performance.','Which businesses face a demand or capacity change?','UK GDP is not an industry or enterprise growth rate.',None),
 'technological':('Operational resilience → technology and supplier-dependency questions.','Which critical services depend on suppliers?','Aggregate cyber evidence proves no company incident or unmet need.',None),
 'legal':('Proposed cyber reform → scope and readiness questions.','Which final rules and entities would apply?','A proposal is not an effective duty or evidence of non-compliance.',None),
 'environmental':('Specified issuer rules → finance and reporting-data preparation.','Which reporting-data controls need validation?','Existing teams may cover the work; issuer scope and reliefs matter.',None),
 'UK-RATE-NOV26':('Funding conditions → deposit-pricing and lending questions.','Which funding sensitivities apply to this bank?','Rate direction alone proves neither lost margin nor customer demand.',None),
 'UK-PRA-REPORT27':('Incident reporting → resilience and third-party preparation.','Which regulated entity and existing readiness apply?','A sector deadline does not prove this bank has an unmet need.',None),
 'UK-VALUE':('Deposits and lending → product and customer-service choices.','Which customer friction is material?','Conceptual value-system interpretation, not measured loss of trust.',None),
 'LBG-A2030-PLATFORMS':('Core renewal → technology operations and customer-service continuity.','Which migration decision is still open?','Stated priority reveals no supplier scope, budget or decision dates.','technology'),
 'LBG-A2030-CIR':('Cost discipline → finance, service processes and operating efficiency.','What baseline and customer outcome constrain change?','The efficiency target is not achieved performance or a supplier budget.','economics'),
 'LBG-ENVOY-CONTROLS':('Existing AI platforms and controls → data and frontline-service workflows.','Is a process-only alternative sufficient?','Internal teams, controls and existing partners may already cover the need.','technology'),
 'LBG-BRAND26-TIMING':('Planned branch changes → assisted channels and customer servicing.','Which customer outcomes still need validation?','An announced timetable does not establish an open procurement.','businesses'),
}
TOPICS={
 'inside':{
  'businesses':('Business areas, brands and structure','Current ownership and legal hierarchy remain to be reconciled. Historical brands do not establish current subsidiaries.',['LBG-BRAND26-TIMING'],'ORG-01'),
  'economics':('Current financial picture','Deposits are a balance-sheet stock; profit is a nine-month flow. The 2030 efficiency ambition is a target. Current income, cost and comparable growth remain unknown.',['LBG-Q326-DEPOSITS','LBG-Q326-PROFIT','LBG-A2030-CIR'],'FIN-01 / FIN-02'),
  'operations':('People, processes and service','Customer relationships connect deposits, lending, payments and service. This interior explains a business mechanism, not actual premises or a system topology.',[],'OPS-01'),
  'technology':('Platforms, data and programmes','The announced platform is not a complete system inventory or proof of net customer outcomes.',['LBG-ENVOY-GOOGLE','LBG-ENVOY-CONTROLS','LBG-A2030-PLATFORMS'],'OPS-01'),
  'governance':('Governance, leadership and change','Current named accountability and decision authority are unknown. No executive is inferred to be a buyer.',['LBG-A2030-DATA'],'ORG-02')},
 'landscape':{
  'customers':('Customer groups','Households and business customers are role categories, not named clients or verified customer dependencies.',[],'REL-01'),
  'businesses':('Peers and market context','Peer banks are navigation references. Their presence establishes neither a bilateral relationship nor a quantified competitive effect.',[],'REL-01'),
  'economics':('Payments and oversight','Payments infrastructure and regulators provide industry context. Specific participation and legal-entity obligations need validation.',[],'INF-01 / REG-01'),
  'operations':('Business customers','Business banking is a customer-role category, not a list of disclosed current clients.',[],'REL-01'),
  'technology':('Suppliers and partners','Only the existing source-supported announced collaboration is displayed. Workshare, value, exclusivity and renewal remain unknown.',['LBG-ENVOY-GOOGLE'],'REL-01')},
}
ROLE_CONTEXT={
 'boe':('Bank of England','UK central bank and monetary-policy context. The reviewed rate decision supports the policy context, not a commercial relationship with each bank.',['UK-RATE-NOV26']),
 'pra':('Prudential Regulation Authority','Prudential supervision context; PRA is part of the Bank of England. Entity-specific applicability remains to be verified.',['UK-PRA-REPORT27']),
 'fca':('Financial Conduct Authority','Conduct supervision context, distinct from PRA prudential supervision. The reviewed reporting policy does not establish a particular entity’s readiness.',['UK-FCA-REPORT27']),
 'payments':('Payments infrastructure','Payments is a sector function. No specific bank participation, operator contract or current infrastructure dependency is inferred.',[]),
}


def claim_rows(data,ids):
 claims={c['id']:c for c in data['claims']}
 if set(ids)-set(claims):raise ValueError('Visual research reference unavailable')
 return [claims[i]for i in ids]


def claim_html(data,claims):
 sources={s['id']:s for s in data['sources']};body=''
 for claim in claims:
  state=claim_state(data,claim)
  body+='<article class="claim" data-claim="'+e(claim['id'],quote=True)+'"><p>'+e(claim['statement'])+'</p><p class="timing">'+e(claim['reporting_period'])+' · '+e(state)+'</p><details><summary>Sources & scope</summary><p>'+e(claim.get('entity_scope','Research context; enterprise applicability not established'))+'</p>'
  for sid in claim['source_ids']:
   s=sources[sid]
   body+='<p><a href="'+e(s['url'],quote=True)+'" rel="noreferrer">'+e(s['title'])+'</a> · '+e(s.get('publication_date') or 'Publication date unknown')+'</p><p>'+e(s.get('limitation') or 'Historical citation; original primary verification remains outstanding.')+'</p>'
  body+='<p><a href="/flora/banking/research/evidence/'+e(claim['id'],quote=True)+'">Quotation and original research status</a></p></details></article>'
 return body


def force_row(ctx,key,data):
 if SCOPES[ctx.scope]['kind']=='country':
  row=visual_v2.insight(key)
  return {'text':row['text'],'date':row['lineage'].get('as_of','12 November 2026'),'proof':row['details'],
          'source_html':''.join('<p><a href="'+e(s['url'],quote=True)+'">'+e(s['title'])+'</a> · '+e(s.get('publication_date') or 'Date unknown')+'</p>'for s in row['sources'])}
 claim=claim_rows(data,[key])[0]
 return {'text':claim['statement'],'date':claim['reporting_period'],'proof':claim_state(data,claim), 'source_html':claim_html(data,[claim])}


def _metric(ctx,data):
 kind=SCOPES[ctx.scope]['kind']
 if kind=='country':
  basis=visual_v2.basis();g=basis['growth']
  return '<p class="metric"><strong>£'+f"{basis['published_total_billion']/1000:.2f}"+'tn</strong> GVA · '+str(basis['year'])+' · current basic prices <span><strong>+'+str(g['value_pct'])+'%</strong> real GDP · '+e(g['period'])+' vs previous three months</span></p>'
 if kind=='industry':
  basis=visual_v2.basis();district=next(d for d in basis['districts']if d['sic']==SCOPES[ctx.scope]['sic'])
  return '<p class="metric">'+e(district['label'])+': <strong>'+str(district['weight_per_thousand']/10)+'%</strong> of UK GVA · '+str(basis['year'])+' · current basic prices</p>'
 fields=SCOPES[ctx.scope]['headline_metrics']
 rows=claim_rows(data,[key for key,label in fields])
 # No invented income/cost/growth decomposition or investment allocation.
 parts=[]
 for claim,(_,label) in zip(rows,fields):
  if not claim.get('metric_unit','').startswith('GBP billion'):
   raise ValueError('Unsupported financial display unit')
  date=re.search(r'\d{1,2} [A-Za-z]+ \d{4}',claim['reporting_period'])
  period=claim['reporting_period']
  if date:
   period=('nine months to ' if 'nine-month' in claim['metric_unit'] else '')+date.group(0)
  parts.append('<strong>£'+e(str(claim['metric_value']))+'bn</strong> '+e(label)+' · '+e(period))
 return '<p class="metric">'+parts[0]+' <span>'+parts[1]+'</span></p>'


def _detail(ctx,spot,data):
 if not ctx.detail:return ''
 close=url(ctx,detail='')+'#label-'+spot['id']
 body='<section class="focus" id="insight" tabindex="-1" aria-labelledby="insight-title"><a class="close close-insight" href="'+e(close,quote=True)+'" aria-label="Close '+e(spot['label'],quote=True)+'">×</a><h2 id="insight-title">'+e(spot['label'])+'</h2>'
 if ctx.stream=='forces':
  row=force_row(ctx,spot['id'],data);pathway,question,counter,inside=FORCE_POLICY[spot['id']]
  if SCOPES[ctx.scope]['kind']=='industry' and claim_rows(data,[spot['id']])[0]['asset_id']!=data['industry_twin_id']:
   counter+=' Enterprise evidence is an example, not evidence for every participant.'
  body+='<p>'+e(row['text'])+'</p><p class="timing">'+e(row['date'])+'</p><h3>Why it matters</h3><p>'+e(pathway)+'</p><h3>What remains uncertain</h3><p>'+e(counter)+'</p><h3>A useful next question</h3><p>'+e(question)+'</p><details><summary>Sources & limitations</summary><p>'+e(row['proof'])+'</p>'+row['source_html']+'<p>Interpretation to validate; not a qualified Material Pressure, verified buyer need, procurement, external supplier scope, budget or early opportunity.</p></details>'
  if inside and SCOPES[ctx.scope]['kind']=='enterprise':body+='<a class="action" href="'+e(url(ctx,stream='inside',detail=inside)+'#insight',quote=True)+'">Explore the possible internal pathway →</a>'
 elif SCOPES[ctx.scope]['kind']=='industry':
  if spot['id']in BANKS:
   bank=registry.enterprise_reference(spot['id'])
   body+='<p>Existing public enterprise reference; current primary-source depth varies by bank. Presence in this district is not a supplier or customer relationship.</p><a class="action" href="/enterprises/'+e(bank.slug)+'">Explore '+e(bank.name)+' →</a>'
  else:
   title,text,refs=ROLE_CONTEXT[spot['id']];body+='<p>'+e(text)+'</p>'+claim_html(data,claim_rows(data,refs))
 elif SCOPES[ctx.scope]['kind']=='enterprise':
  title,text,refs,gap=TOPICS[ctx.stream][spot['id']]
  if ctx.stream=='landscape' and spot['id']=='technology':
   # Consume the existing relationship decision, not a new qualification rule.
   # A retained claim alone must not silently reinstate a withdrawn edge.
   refs=[key for key in refs if any(r.get('verified') and key in r.get('claim_ids',())
         and r['subject']==data['enterprise_twin_id'] for r in data['relationships'])]
   if not refs:text='Current supplier relationships require revalidation. Preserved research is available in the original source register; no current relationship is inferred here.'
  gap_names=dict(GAPS)
  missing='; '.join(gap_names.get(k.strip(),k.strip()) for k in gap.split('/'))
  body+='<p>'+e(text)+'</p>'+claim_html(data,claim_rows(data,refs))+'<p class="timing">Still to establish: '+e(missing)+'.</p>'
  if ctx.stream=='landscape' and spot['id']=='businesses':body+='<ul>'+''.join('<li><a href="/enterprises/'+s+'">'+e(registry.enterprise_reference(s).name)+'</a></li>'for s in BANKS if s!='lloyds')+'</ul>'
 return body+'</section>'


def _proof(ctx,data):
 body='<details class="proof"><summary>Sources & detail</summary>'
 if data is None:return body+visual_v2._sources('')+'</details>'
 body+='<p>Research review '+e(data['assessed_at'])+'. Dates and reporting periods differ. Disclosures, interpretation and unknowns remain distinct; no source is promoted by this view.</p>'
 if SCOPES[ctx.scope]['kind']=='industry':
  body+='<p>Finance & insurance is a whole SIC section, not Banking-only market value. Regulatory actors and payments are industry context; no bank-specific permissions or participation is inferred.</p>'
  basis=visual_v2.basis();district=next(d for d in basis['districts']if d['sic']==SCOPES[ctx.scope]['sic'])
  source=next(s for s in basis['sources']if s['id']==district['source_id'])
  body+='<p><a href="'+e(source['url'],quote=True)+'">'+e(source['title'])+'</a> · '+e(source.get('publication_date') or '')+'</p><p>2024 nominal GVA at current basic prices; not Banking revenue, addressable sales or real GDP growth. Rounded ONS weights, Crown copyright / Open Government Licence.</p>'
 body+='<p>Illustration is a conceptual business world, not actual premises, a legal hierarchy, system topology, financial scale or quantified pressure map.</p><p><a href="/flora/banking/research/sources">Original source register and rights</a> · <a href="/flora/banking/research/gaps">Research gaps</a></p>'
 if SCOPES[ctx.scope]['kind']=='enterprise':
  body+='<h2>Still to establish</h2><ul>'+''.join('<li><strong>'+e(k)+'</strong> · '+e(label)+'</li>'for k,label in GAPS)+'</ul><p>Unknown current income/cost/growth, hierarchy, leadership and external need remain unknown. An announced programme is not an opportunity to shape.</p>'
  root=SCOPES[ctx.scope]['route']
  body+='<p><a href="'+root+'/understanding">Account understanding</a> · <a href="'+root+'/research-diagnostic">Research review</a></p>'
  views=(('operating-model','Operating model'),('ecosystem','Supplier research'),('timeline','Strategy timeline'),('opportunities','Commercial hypotheses'))
 else:
  views=(('overview','Industry model'),('pestle','PESTLE'),('porter','Five Forces'),('value-chain','Value chain'),('ai-disruption','AI disruption'),('regulation','Regulation and resilience'),('commercial','Commercial hypotheses'))
 body+='<details><summary>Supporting intelligence</summary><ul>'+''.join('<li><a href="'+SCOPES[ctx.scope]['route']+'?lens='+key+'">'+label+'</a></li>'for key,label in views)+'</ul></details>'
 body+='<p>Images: owner-commissioned FLORA artwork from accepted design '+DESIGN[:7]+'. Interpretation only; no real-world building, logo affiliation or supplier scope is implied.</p></details>'
 return body


@ds.view_scope
def render(path,query,headers=None):
 ctx=resolve(path,query);binding=SCOPES[ctx.scope];data=current_data(ctx);scene=geometry()[ctx.scope+'-'+ctx.stream];art=artwork()['scenes'][ctx.scope+'-'+ctx.stream]
 title=binding.get('title') or data['industry_name'if binding['kind']=='industry'else 'enterprise_name']
 identity=binding.get('identity') or data[binding['identity_key']]
 # Frozen annotations are supplementary presentation, never an updated source.
 # Hide them if any underlying public research/basis pin changes. Detailed
 # facts below always come from current validated owners, not these captions.
 caption_pins=artwork()['caption_source_pins']
 caption_current=all(hashlib.sha256((model.REPO/p).read_bytes()).hexdigest()==digest for p,digest in caption_pins.items())
 if binding['kind']=='country' and ctx.stream=='forces':visual_v2.macro.load_context()
 body='<div class="page-title"><h1>'+e(title)+'</h1></div>'+_metric(ctx,data)
 body+='<nav class="stream-switcher" aria-label="Insight streams">'+''.join('<a href="'+e(url(ctx,stream=s,detail=''),quote=True)+'"'+(' aria-current="page"'if ctx.stream==s else '')+'>'+s.title()+'</a>'for s in binding['streams'])+'</nav>'
 body+='<figure class="world" aria-labelledby="world-description"><figcaption class="sr-only" id="world-description">'+e(scene['description'])+'. Conceptual illustration; labelled controls and text view provide equivalent navigation.</figcaption>'
 variants=art['variants'];srcset=', '.join(ASSET_BASE+v['file'].removesuffix('.webp')+' '+str(v['width'])+'w'for v in variants)
 sizes='(max-width:600px) 200vw, (min-width:1000px) min(100vw, calc(150vh - 300px)), 100vw'
 for side in ('left','right'):
  body+='<div class="half '+side+'"><img src="'+ASSET_BASE+variants[-1]['file'].removesuffix('.webp')+'" srcset="'+srcset+'" sizes="'+sizes+'" width="'+str(art['width'])+'" height="'+str(art['height'])+'" alt="" decoding="async"'+(' fetchpriority="high"'if side=='left'else ' loading="lazy"')+'></div>'
 text_entries=[]
 for spot in scene['spots']:
  sid=spot['id'];label=spot['label'];href='';attrs='';classes='spot'
  selected=sid==ctx.selected
  if binding['kind']=='country' and ctx.stream=='landscape':
   district=next(d for d in visual_v2.basis()['districts']if d['id']==sid);sic=district['sic'];attrs=' data-sic="'+sic+'"'
   from .public_routes import public_read_path
   if sic in visual_v2.RESEARCH and public_read_path(visual_v2.RESEARCH[sic][1]):
    name,href=visual_v2.RESEARCH[sic];attrs+=' data-research="'+name.lower()+'" aria-label="'+e(name+': open available industry experience; '+label+' is its broader section',quote=True)+'"';classes+=' available'
    selected=ctx.selected==name.lower()
   else:classes+=' inert'
  elif binding['kind']=='industry' and ctx.stream=='landscape' and sid in BANKS:
   href='/enterprises/'+sid
   # Lloyds enters Inside directly. Other banks retain their current public views.
  else:href=url(ctx,detail=sid,selected=sid if binding['kind']=='industry' and sid in BANKS else ctx.selected)+'#insight'
  if href:classes+=' active'
  text_entries.append((href,label))
  if selected:classes+=' selected'
  layer_focus=(ctx.layer=='regulators' and (sid in ROLE_CONTEXT or sid=='economics'))or(ctx.layer=='suppliers'and sid in ('technology','customers','operations','payments'))
  if layer_focus:classes+=' layer-focus'
  attrs+=' data-label-id="'+e(sid,quote=True)+'" id="label-'+e(sid,quote=True)+'" style="'+e(spot['position'],quote=True)+'"'
  tag='a'if href else 'span'
  body+='<'+tag+' class="'+classes+'"'+attrs+(' href="'+e(href,quote=True)+'"'if href else '')+'>'+e(label)+(' <span aria-hidden="true">›</span>'if href else '')
  # Approved annotations are backed by the unchanged, validated research review.
  # Drop frozen mini-captions if the research cutoff changes, rather than infer updates.
  if spot['small'] and caption_current:body+='<small>'+e(spot['small'])+'</small>'
  body+='</'+tag+'>'
 body+='</figure><p class="art-fallback">Artwork could not load. All labelled links and the text view remain available.</p>'
 if ctx.selected and binding['kind']=='industry':body+='<p class="selection-note">Selected: '+e(registry.enterprise_reference(ctx.selected).name)+'</p>'
 if ctx.detail:body+=_detail(ctx,next(s for s in scene['spots']if s['id']==ctx.detail),data)
 body+='<details class="text-view"><summary>Text view</summary><ul>'+''.join('<li>'+('<a href="'+e(h,quote=True)+'">'+e(l)+'</a>'if h else e(l))+'</li>'for h,l in text_entries)+'</ul></details>'
 if binding['kind']!='country':
  body+='<details class="layer-options"><summary>Context layers</summary><nav aria-label="Context layers">'+''.join('<a href="'+e(url(ctx,layer=k),quote=True)+'"'+(' aria-current="page"'if ctx.layer==k else '')+'>'+e(v)+'</a>'for k,v in LAYERS.items())+'</nav></details>'
 body+=_proof(ctx,data)
 if binding['kind']=='enterprise':body+='<footer><a href="'+e(url(Context('banking','landscape',ctx.layer,binding['slug'])),quote=True)+'">← Back to Banking</a></footer>'
 elif binding['kind']=='industry':body+='<footer><a href="'+e(url(Context('uk','landscape',selected=ctx.scope)),quote=True)+'">← Back to United Kingdom</a></footer>'
 return '<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>'+e(title)+' · '+ctx.stream.title()+' · FLORA</title>'+"<link rel='canonical' href='"+binding['route']+"'>"+ds.head()+'<link rel="stylesheet" href="'+ASSET_BASE+'styles"><script defer src="'+ASSET_BASE+'interactions"></script></head><body class="ds-page vex-page"><a class="skip" href="#visual-content">Skip to main content</a>'+ds.header(headers=headers,compact=True)+'<main id="visual-content" tabindex="-1" data-market="GB" data-scope="'+ctx.scope+'" data-identity="'+e(identity,quote=True)+'" data-stream="'+ctx.stream+'" data-layer="'+ctx.layer+'">'+body+'</main></body></html>'
