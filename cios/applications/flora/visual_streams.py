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

from . import design_system as ds, visual_v2, leadership_agenda
from .research_intelligence import model, registry
from . import intelligence_presentation as presentation
from .intelligence_presentation import Source, Statement

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
 agenda:str=''


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
 from .visual_panels import asset_manifest
 files['panel-styles']=('panels.css','text/css; charset=utf-8')
 for name,row in asset_manifest()['files'].items():
  if name in files:raise ValueError('Visual asset identity collision')
  files[name]=(row['file'],row['mime'])
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
  from .visual_panels import asset_manifest
  originals=[v['sha256']for row in artwork()['scenes'].values()for v in row['variants']if v['file']==filename]
  expected=originals[0]if originals else asset_manifest()['files'][name]['sha256']
  if hashlib.sha256(body).hexdigest()!=expected:raise ValueError('Visual asset checksum mismatch')
 if mime=='image/svg+xml':
  from .visual_panels import asset_manifest
  if hashlib.sha256(body).hexdigest()!=asset_manifest()['files'][name]['sha256']:raise ValueError('Visual asset checksum mismatch')
 return body,mime


def resolve(path,query):
 if path not in ROUTES or set(query)-{'stream','market','layer','selected','detail','agenda'} or any(not isinstance(v,list) or len(v)!=1 for v in query.values()):
  raise ValueError('Visual journey unavailable')
 scope=ROUTES[path];binding=SCOPES[scope]
 if query.get('market',['GB'])!=['GB']:raise ValueError('Country unavailable')
 stream=query.get('stream',[binding['streams'][0]])[0]
 layer=query.get('layer',['enterprises'])[0];selected=query.get('selected',[''])[0];detail=query.get('detail',[''])[0]
 if stream not in binding['streams'] or layer not in LAYERS:raise ValueError('Insight view unavailable')
 if binding['kind']=='country':
  if layer!='enterprises' or selected not in ('','banking','technology','aviation'):raise ValueError('Country context unavailable')
 else:
  if scope=='banking':
   from .banking_value_system import STAGES
   if selected not in ('',*BANKS,'tsb','nationwide','starling',*STAGES):raise ValueError('Banking selection unavailable')
  elif selected not in ('',binding['slug']):raise ValueError('Enterprise selection unavailable')
 agenda=query.get('agenda',[''])[0]
 if agenda and agenda not in leadership_agenda.KEYS[scope]:raise ValueError('Leadership view unavailable')
 for key in ('selected','detail','agenda'):
  if key in query and not query[key][0]:raise ValueError('Empty visual selector')
 spots=geometry()[scope+'-'+stream]['spots']
 if detail and detail not in {s['id']for s in spots}:raise ValueError('Selected detail unavailable')
 if detail and binding['kind']=='country' and stream=='landscape':raise ValueError('District detail unavailable')
 if binding['kind']=='industry' and detail in BANKS and selected not in ('',detail):raise ValueError('Selected bank mismatch')
 return Context(scope,stream,layer,selected,detail,agenda)


def url(ctx,**changes):
 ctx=replace(ctx,**changes)
 q={'stream':ctx.stream}
 if ctx.layer!='enterprises':q['layer']=ctx.layer
 if ctx.selected:q['selected']=ctx.selected
 if ctx.detail:q['detail']=ctx.detail
 if ctx.agenda:q['agenda']=ctx.agenda
 return SCOPES[ctx.scope]['route']+'?'+urlencode(q)


def stream_url(ctx,stream):
 """Compatible subject across the existing finite scene selectors, no new router."""
 if stream not in SCOPES[ctx.scope]['streams']:raise ValueError('Insight view unavailable')
 detail=ctx.detail
 target={s['id']for s in geometry()[ctx.scope+'-'+stream]['spots']}
 if detail and stream!=ctx.stream:
  if ctx.scope=='lloyds':
   topics={('inside','technology'):'technology',('landscape','technology'):'technology',
       ('forces','LBG-ENVOY-CONTROLS'):'technology',('forces','LBG-A2030-PLATFORMS'):'technology',
       ('inside','economics'):'finance',('forces','LBG-A2030-CIR'):'finance',
       ('inside','businesses'):'brands',('forces','LBG-BRAND26-TIMING'):'brands'}
   subject=topics.get((ctx.stream,detail))
   detail=next((key for(s,key),topic in topics.items()if s==stream and subject and topic==subject),'')
  elif detail not in target:detail=''
 return url(ctx,stream=stream,detail=detail)


def current_data(ctx):
 binding=SCOPES[ctx.scope]
 if binding['kind']=='country':return None
 data=model.load_assessment(binding['domain'])
 if data.get('owner_only')is True:raise ValueError('Public reference unavailable')
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
 'economic':('Growth changes the national output context; enterprise effects depend on actual exposure.','UK GDP is not an industry or enterprise growth rate.',None),
 'technological':('Operational resilience includes technology and supplier dependencies.','Aggregate cyber evidence proves no company incident or unmet need.',None),
 'legal':('The reviewed cyber reform is a legislative proposal.','A proposal is not an effective duty or evidence of non-compliance.',None),
 'environmental':('Specified issuer rules connect sustainability reporting with operational data.','First reporting is in 2028; reliefs matter. Existing capabilities may cover the work.',None),
 'UK-RATE-NOV26':('Funding conditions affect the context for deposit pricing and lending.','Rate direction alone proves neither lost margin nor customer demand.',None),
 'UK-PRA-REPORT27':('Incident reporting policy concerns operational resilience and third-party reporting.','Sector policy does not establish a specific bank’s preparedness or unmet need.',None),
 'UK-VALUE':('Banking combines deposits, lending, payments and customer protection.','An industry value-system interpretation is not a measure of customer trust or financial loss.',None),
 'LBG-A2030-PLATFORMS':('Core renewal is a stated part of Lloyds’ 2027–2030 strategy.','A priority establishes neither open procurement nor external supplier scope.','technology'),
 'LBG-A2030-CIR':('The efficiency ambition is a future management target.','The target is not achieved performance or a supplier budget.','economics'),
 'LBG-ENVOY-CONTROLS':('Envoy is an existing company-described AI platform with controls.','Existing capabilities weaken a generic missing-platform proposition. Designed controls do not measure effectiveness.','technology'),
 'LBG-BRAND26-TIMING':('The announcement sets a timetable for branch-brand changes.','A plan is distinct from delivery outcomes and establishes no open procurement.','businesses'),
}
TOPICS={
 'inside':{
  'businesses':('Businesses & brands',['LBG-BRAND26-TIMING']),
  'economics':('Financial performance',['LBG-Q326-DEPOSITS','LBG-Q326-PROFIT','LBG-A2030-CIR']),
  'operations':('Service operations',['LBG-AR25-MIGRATION']),
  'technology':('Technology & data',['LBG-ENVOY-GOOGLE','LBG-ENVOY-CONTROLS','LBG-A2030-PLATFORMS']),
  'governance':('Governance & change',['LBG-A2030-DATA'])},
 'landscape':{
  'customers':('Customer groups',[]),
  'businesses':('Peers & market context',[]),
  'economics':('Payments & oversight',['UK-PRA-REPORT27','UK-FCA-REPORT27']),
  'operations':('Business customers',[]),
  'technology':('Suppliers & partners',['LBG-ENVOY-GOOGLE'])},
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
 return ''.join(presentation.render(item)for claim in claims if (item:=presentation.claim_view(data,claim)))


def force_view(ctx,key,data):
 if SCOPES[ctx.scope]['kind']!='country':
  return presentation.editorial_force(presentation.claim_view(data,claim_rows(data,[key])[0]),key)
 row=visual_v2.insight(key)
 if any(presentation.restricted_metadata(s)for s in row['sources']):return None
 sources=tuple(Source(s['title'],s['url'],s.get('publisher',''),s.get('publication_date')or'',s.get('reporting_period',''),
              (s.get('excerpts')or[{}])[0].get('quote',''),s.get('locator',''))for s in row['sources'])
 text=re.split(r'(?<=[.!])\s+',row['text'],maxsplit=1)[0]
 # Review timestamps are not the period of the underlying evidence.
 period=(visual_v2.basis()['growth']['period']if key=='economic'else
     '; '.join(dict.fromkeys(s.get('reporting_period','')for s in row['sources']if s.get('reporting_period'))))
 if not period:period='; '.join('Published '+s['publication_date']for s in row['sources']if s.get('publication_date'))
 if not period:return None
 return presentation.editorial_force(Statement(text,'reported','United Kingdom; national or specified issuer scope',period,sources,
                  'reviewed_excerpt','candidate_intelligence',
                  measurement_state='proposal'if key=='legal'else'not_applicable',
                  caveats=(row['details'],)),key)


def detail_claims(ctx,spot,data):
 if SCOPES[ctx.scope]['kind']!='enterprise':return []
 refs=TOPICS[ctx.stream][spot['id']][1]
 if ctx.stream=='landscape'and spot['id']=='technology':
  refs=[key for key in refs if any(r.get('verified')and key in r.get('claim_ids',())and r['subject']==data['enterprise_twin_id']for r in data['relationships'])]
 return claim_rows(data,refs)


def has_detail(ctx,spot,data):
 if ctx.stream=='forces':return bool(force_view(ctx,spot['id'],data)and presentation.eligible(force_view(ctx,spot['id'],data)))
 if SCOPES[ctx.scope]['kind']=='enterprise':
  if ctx.stream=='landscape'and spot['id']=='businesses':return True
  return any(presentation.claim_view(data,c)for c in detail_claims(ctx,spot,data))
 return True


def destinations(ctx,data):
 """Existing scene addressability, independent of portrait placement."""
 rows=[]
 for spot in geometry()[ctx.scope+'-'+ctx.stream]['spots']:
  sid=spot['id'];href='';research='';sic=''
  if ctx.scope=='uk'and ctx.stream=='landscape':
   district=next(d for d in visual_v2.basis()['districts']if d['id']==sid);sic=district['sic']
   from .public_routes import public_read_path
   if sic in visual_v2.RESEARCH and public_read_path(visual_v2.RESEARCH[sic][1]):research,href=visual_v2.RESEARCH[sic]
  elif ctx.scope=='banking'and ctx.stream=='landscape'and sid in BANKS:href='/enterprises/'+sid
  elif has_detail(ctx,spot,data):href=url(ctx,detail=sid,selected=sid if ctx.scope=='banking'and sid in BANKS else ctx.selected)+'#insight'
  rows.append({'id':sid,'label':spot['label'],'href':href,'sic':sic,'research':research,
      'selected':sid==ctx.detail or sid==ctx.selected or bool(research and ctx.selected==research.lower())})
 return rows


def _metric(ctx,data):
 kind=SCOPES[ctx.scope]['kind']
 if kind=='country':
  basis=visual_v2.basis();g=basis['growth']
  return '<p class="metric"><span class="sr-only">Reported: </span><strong>£'+f"{basis['published_total_billion']/1000:.2f}"+'tn</strong> GVA · '+str(basis['year'])+' · current basic prices <span><strong>+'+str(g['value_pct'])+'%</strong> real GDP · '+e(g['period'])+' vs previous three months</span></p>'
 if kind=='industry':
  basis=visual_v2.basis();district=next(d for d in basis['districts']if d['sic']==SCOPES[ctx.scope]['sic'])
  return '<p class="metric"><span class="intelligence-label">Calculated</span> '+e(district['label'])+': <strong>'+str(district['weight_per_thousand']/10)+'%</strong> of UK GVA · '+str(basis['year'])+' · current basic prices</p>'
 fields=SCOPES[ctx.scope]['headline_metrics']
 rows=claim_rows(data,[key for key,label in fields])
 # No invented income/cost/growth decomposition or investment allocation.
 parts=[]
 for claim,(_,label) in zip(rows,fields):
  if not presentation.claim_view(data,claim):continue
  if not claim.get('metric_unit','').startswith('GBP billion'):
   raise ValueError('Unsupported financial display unit')
  date=re.search(r'\d{1,2} [A-Za-z]+ \d{4}',claim['reporting_period'])
  period=claim['reporting_period']
  if date:
   period=('nine months to ' if 'nine-month' in claim['metric_unit'] else '')+date.group(0)
  parts.append('<strong>£'+e(str(claim['metric_value']))+'bn</strong> '+e(label)+' · '+e(period))
 return ('<p class="metric"><span class="sr-only">Reported: </span>'+' · '.join(parts)+'</p>')if parts else''


def _detail(ctx,spot,data):
 if not ctx.detail or not has_detail(ctx,spot,data):return ''
 close=url(ctx,detail='')+'#visual-content'
 body='<section class="focus" id="insight" tabindex="-1" aria-labelledby="insight-title"><a class="close close-insight" href="'+e(close,quote=True)+'" aria-label="Close '+e(spot['label'],quote=True)+'">×</a><h2 id="insight-title">'+e(spot['label'])+'</h2>'
 if ctx.stream=='forces':
  item=force_view(ctx,spot['id'],data)
  body+=presentation.render(item)
  text,counter,inside=FORCE_POLICY[spot['id']]
  if SCOPES[ctx.scope]['kind']=='industry'and item and spot['id'].startswith('LBG-'):
   counter+=' This is a Lloyds example; it does not establish effects across all banks.'
  inference=Statement(text,'insight',item.scope,item.period,item.sources,'derived_from_inputs','derived_view_not_canonical',
             reasoning='Scoped interpretation of the displayed disclosure; no causal or buying-intent claim.',
             dependencies=(item.text,),counter_evidence=(counter,))
  body+=presentation.render(inference)
  if inside and SCOPES[ctx.scope]['kind']=='enterprise':body+='<a class="action" href="'+e(url(ctx,stream='inside',detail=inside)+'#insight',quote=True)+'">Inside '+e(TOPICS['inside'][inside][0])+' →</a>'
 elif SCOPES[ctx.scope]['kind']=='industry':
  if spot['id']in BANKS:
   bank=registry.enterprise_reference(spot['id']);body+='<a class="action" href="/enterprises/'+e(bank.slug)+'">Explore '+e(bank.name)+' →</a>'
  else:
   title,text,refs=ROLE_CONTEXT[spot['id']]
   # Actor labels express navigation context, not a bank-specific relationship.
   body+='<p>'+e({'boe':'UK central bank and monetary-policy context.','pra':'Prudential supervision context; PRA is part of the Bank of England.','fca':'Conduct-supervision context, distinct from prudential supervision.','payments':'Conceptual industry payments infrastructure; the illustration does not assert a named bank participation or contract.'}[spot['id']])+'</p>'+claim_html(data,claim_rows(data,refs))
 elif SCOPES[ctx.scope]['kind']=='enterprise':
  body+=claim_html(data,detail_claims(ctx,spot,data))
  if ctx.stream=='landscape'and spot['id']=='businesses':
   body+='<p>Peer-bank navigation; no bilateral customer or supplier relationship is asserted.</p><ul>'+''.join('<li><a href="/enterprises/'+slug+'">'+e(registry.enterprise_reference(slug).name)+'</a></li>'for slug in BANKS if slug!='lloyds')+'</ul>'
 return body+'</section>'


def _proof(ctx,data):
 body='<details class="proof"><summary>Sources & detail</summary>'
 if (SCOPES[ctx.scope]['kind']in {'country','industry'}
     and leadership_agenda.fingerprint(visual_v2.basis())==leadership_agenda._pins().get('existing_economy')):
  basis=visual_v2.basis()
  body+='<p>UK GVA uses 2024 current basic prices. The displayed total is rounded from £2,623bn. GVA is not company revenue or GDP at market prices.</p><p>Industry shares are the published SIC2007 section weights divided by ten; rounded sections total 100.2%. Finance & insurance includes more than Banking. No sales-market value is inferred.</p>'
  if SCOPES[ctx.scope]['kind']=='industry':
   district=next(d for d in basis['districts']if d['sic']==SCOPES[ctx.scope]['sic'])
   body+='<p>Calculation: SIC '+e(district['sic'])+' published weight '+str(district['weight_per_thousand'])+' per thousand ÷ 10 = '+str(district['weight_per_thousand']/10)+'% of UK GVA.</p>'
  for source in basis['sources']:
   body+='<p><a href="'+e(source['url'],quote=True)+'" rel="noreferrer">'+e(source['title'])+'</a>'+(' · '+e(source['publication_date'])if source.get('publication_date')else'')+'</p>'
  body+='<p>ONS data: Crown copyright / Open Government Licence. Real GDP growth is a separate volume measure; the preliminary estimate is subject to revision.</p>'
 body+='<p>Conceptual owner-commissioned FLORA illustration; not actual premises, a legal hierarchy, a system topology or a quantitative pressure map.</p></details>'
 return body


@ds.view_scope
def render(path,query,headers=None):
 from .visual_panels import render as panels
 if 'analysis'in query:
  from .financial_intelligence.analyst import selection
  ctx,run_id=selection(path,query)
  return panels(ctx,headers,financial_run_id=run_id)
 return panels(resolve(path,query),headers)
