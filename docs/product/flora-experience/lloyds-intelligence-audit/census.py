"""Read-only, finite Lloyds audit. No import, owner or publication decisions."""
import argparse, ast, hashlib, json, re, subprocess, sys
from collections import Counter
from dataclasses import asdict
from decimal import Decimal
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
BASE='3a4c7e0f6ad81af7ef32ed477a1a584ac2efae87'
sys.path.insert(0,str(ROOT))
from cios.applications.flora import visual_streams as v, lloyds_gold as g, intelligence_presentation as p, leadership_agenda as agenda

def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def read(path,ref=BASE):return git('show',ref+':'+path)
def norm(s):return re.sub(r'\s+',' ',unescape(s)).strip()
class Main(HTMLParser):
 def __init__(self,html):
  super().__init__();self.depth=0;self.text=[];self.claims=[];self.regions=0;self.tables=0;self.articles=0;self.sources=[];self.feed(html)
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=='main':self.depth+=1
  if self.depth:
   if d.get('data-claim-id'):self.claims.append(d['data-claim-id'])
   if d.get('data-canvas-region'):self.regions+=1
   self.tables+=t=='table';self.articles+=t=='article'
   if t=='a'and d.get('href','').startswith('https:'):self.sources.append(d['href'])
 def handle_endtag(self,t):
  if t=='main':self.depth-=1
 def handle_data(self,s):
  if self.depth:self.text.append(s)

PACKS=[(618,'c57ed9728473563b5535db36d5bfbe5e96a8c572','docs/flora-runtime/rie1-617','Facts.json'),
 (620,'71d34bb50cff4a7e99cf49f53a0ee5c8724c3df5','docs/flora-runtime/rie2-619','Claims.json'),
 (622,'9db8253b23deefac00022716c53311472203aec7','docs/flora-runtime/ric1','Claim-Ledger.json'),
 (666,'412c086391194ec4e9d2f1b76841b0bb1df8917d','docs/flora-runtime/bnk-ent-1','Claims.json')]

def inspect():
 data=v.current_data(v.Context('lloyds','landscape'));facts=g.facts_for(data)
 out={'baseline':BASE,'authority':'Static repository/isolated runtime audit; no admission or canonical verification',
 'collection_counts':{k:len(z)for k,z in data.items()if isinstance(z,list)},'public_projection':[], 'owner_claims':[],
 'relationship_assertion_counts':dict(Counter(str((r.get('verified'),r.get('assertion_kind')))for r in data['relationships'])),
 'verified_relationships':[r for r in data['relationships']if r.get('verified')is True],
 'capabilities':[{'id':r['id'],'title':r['title'],'scope':r.get('scope')}for r in data['capabilities']],
 'programmes':data['programmes'],'screens':[],'research_census':[],'draft_packages':[]}
 for k,s in facts.items():
  out['public_projection'].append({'id':k,'text':s.text,'type':s.semantic_type,'scope':s.scope,'period':s.period,
   'canonical_status':s.canonical_status,'measurement_state':s.measurement_state,'sources':[{'url':x.url,'publisher':x.publisher,'published':x.published,'period':x.period,'locator':x.locator}for x in s.sources]})
 for c in data['claims']:
  s=p.claim_view(data,c)
  out['owner_claims'].append({'id':c['id'],'source_ids':c['source_ids'],'kind':c.get('kind'),'verification':c.get('verification'),
   'scope':c.get('entity_scope'),'period':c.get('reporting_period'),'eligible_via_existing_adapter':bool(s and p.eligible(s)),
   'in_default_projection':c['id']in facts,'supersedes':c.get('supersedes'),'updates':c.get('updates')})
 # Screen denominator is the finite default focus/detail vocabulary; subject
 # permutations and specialist/legacy routes are not silently called covered.
 surface_texts=[]
 for stream,items in [*g.REGIONS.items(),('inside',(('people','Organisation & workforce'),))]:
  for focus,title in items:
   for detail in ('',*g.DETAILS[focus]):
    q={'stream':[stream],'focus':[focus],'detail':[detail]};html=v.render(g.CANONICAL,q);doc=Main(html);text=norm(' '.join(doc.text))
    if detail!='sources':surface_texts.append(text)
    measured={k for k in ('LBG-Q326-DEPOSITS','LBG-Q326-PROFIT','LBG-AR25-DEPOSITS')if k in facts and ('£'+str(facts[k].value)+'bn')in text}
    exact={k for k,s in facts.items()if norm(s.text)in text}
    out['screens'].append({'stream':stream,'focus':focus,'detail':detail,'title':title,
     'url':g.CANONICAL+'?stream='+stream+'&focus='+focus+('&detail='+detail if detail else ''),
     'word_count':len(text.split()),'regions':doc.regions,'tables':doc.tables,'articles':doc.articles,
     'tagged_claim_ids':sorted(set(doc.claims)),'measured_claim_ids':sorted(measured),'exact_statement_ids':sorted(exact),
     'observed_claim_ids':sorted(set(doc.claims)|exact|measured),'main_external_link_count':len(doc.sources),
     'unknown_mentions':len(re.findall(r'\bunknown\b|\bunavailable\b|\bunverified\b',text,re.I))})
 out['agenda']=[{'key':a.key,'conclusion':a.conclusion.text,'conclusion_eligible':p.eligible(a.conclusion),
  'exact_conclusion_observed_in_gold':any(norm(a.conclusion.text)in text for text in surface_texts),
  'limit':'Exact wording test only; similar interpretation and underlying facts may already be present',
  'facts':[{'type':f.semantic_type,'text':f.text,'scope':f.scope,'period':f.period}for f in a.facts]}for a in agenda.agenda('lloyds',data)]
 paths=git('ls-tree','-r','--name-only',BASE).decode().splitlines()
 text_suffix={'.json','.jsonl','.ndjson','.md','.txt','.yaml','.yml','.py','.csv'}
 for path in paths:
  if Path(path).suffix.lower()not in text_suffix:continue
  if not path.startswith(('docs/','enterprise-knowledge/','architecture/','cios/','knowledge-packs/')):continue
  raw=read(path)
  if re.search(rb'lloyds|LBG-',raw,re.I):
   out['research_census'].append({'path':path,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),
    'kind':'runtime'if path.startswith('cios/')else'contract'if path.startswith('architecture/')else'repository_research_or_documentation'})
 for pr,ref,folder,name in PACKS:
  pkgpaths=git('ls-tree','-r','--name-only',ref,folder).decode().splitlines();rows=[]
  for path in pkgpaths:
   raw=read(path,ref);same=None
   if path in paths:same=raw==read(path)
   rows.append({'path':path,'sha256':hashlib.sha256(raw).hexdigest(),'main_has_same_path':same is not None,'byte_equal_on_main':same})
  d=json.loads(read(folder+'/'+name,ref));claims=d if isinstance(d,list)else d.get('claims',d.get('facts',[]))
  out['draft_packages'].append({'pr':pr,'sha':ref,'path':folder,'claim_file':name,'record_count':len(claims),
   'ancestor_of_main':subprocess.run(['git','merge-base','--is-ancestor',ref,BASE],cwd=ROOT,capture_output=True).returncode==0,'files':rows,
   'note':'Counts are package records, overlap across packages; not additive, verified facts, or canonical authority'})
 out['tier1']={f.stem:len(f.read_text().splitlines())for f in (ROOT/'docs/research/lloyds-tier1-sprint1').glob('*.ndjson')}
 replay=json.loads(read('docs/research/initial-factory/commercial-replay.json'))['lloyds-banking-group-plc']
 isolated=next(r for r in json.loads(read('docs/research/initial-factory/verified/isolated-records.json'))if r['enterprise_id']=='lloyds-banking-group-plc')
 body=next(r for r in json.loads(read('docs/research/initial-factory/completion/body-proof.json'))if r['enterprise_id']=='lloyds-banking-group-plc')
 out['initial_factory']={'replay_claims':[{'key':c['key'],'statement':c['statement'],'period':c['period'],'scope':c['scope'],'publisher':r['publisher'],'published':r['published'],'locator':c['locator']}for r in replay for c in r['claims']],
  'verified_isolated_record_count':len(isolated['records']),'verified_isolated_classes':dict(Counter(r['record_class']for r in isolated['records'])),
  'verified_isolated_subject':'events.responsible_ai_ethics','body_discovery_cut':body['as_of'],'body_article_candidates':body['article_count'],
  'body_publication_flags':[r['publication_eligible']for r in body['candidates']],
  'authority_limit':'Retained replay and isolated test-scoped execution through existing owners; NOT proof of production canonical import or public projection authority'}
 canonical=json.loads(read('enterprise-knowledge/banking/canonical/banking-research-canonical-objects.json'))['canonical_objects']
 out['migration_index']={'count':len(canonical),'types':dict(Counter(r['object_type']for r in canonical)),
  'archived_input_references':[{'path':path,'present_in_baseline_tree':path in paths}for path in sorted({r['source_zip_path']for r in canonical if r.get('source_zip_path')})],
  'authority_limit':'Migration index of research artefacts; not production accepted Evidence/Observation/Enterprise Model records'}
 checks=json.loads(read('docs/flora-runtime/lei-1/reconciliations.json'))['checks']
 out['existing_reconciliations']=[{'id':r['id'],'scope':r['subject'],'period':r['period'],'basis':r['basis'],
  'arithmetic_reproduces':sum(Decimal(str(n))for n in r['inputs'])==Decimal(str(r['expected'])),
  'eligibility':'Research only: arithmetic success is neither source authority nor canonical acceptance'}for r in checks]
 ids=set(facts);surface=set().union(*(set(s['observed_claim_ids'])for s in out['screens']if s['detail']!='sources'))
 out['finite_measures']={'default_focus_count':sum(not s['detail']for s in out['screens']),'focus_detail_states':len(out['screens']),
  'public_projection_statement_count':len(facts),'projection_statement_ids_observed_outside_source_inspection':sorted(surface&ids),
  'projection_ids_not_observed_by_finite_text_or_measure_match':sorted(ids-surface),
  'owner_claim_count':len(data['claims']),'eligible_owner_claim_count':sum(c['eligible_via_existing_adapter']for c in out['owner_claims']),
  'empty_focus_fact_lists':[k for k,z in g.FOCUS_FACTS.items()if not z],
  'caution':'Bounded adapter/finite-route coverage only, NOT Lloyds research, extraction, relationship or commercial completeness'}
 return out

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,default=HERE/'Inventory.json');args=a.parse_args()
 d=inspect();args.output.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps({'finite_measures':d['finite_measures'],'census_files':len(d['research_census']),'draft_packages':[(p['pr'],p['record_count'])for p in d['draft_packages']]},indent=2))
