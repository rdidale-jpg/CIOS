"""Offline RIC-1 provenance, consolidation and acceptance-boundary QA; no importer."""
from pathlib import Path
from datetime import date
from collections import Counter
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'docs/flora-runtime/ric1'
if __name__=='__main__':sys.path.insert(0,str(ROOT))
PINS={'RIE1':'c57ed9728473563b5535db36d5bfbe5e96a8c572','RIE2':'71d34bb50cff4a7e99cf49f53a0ee5c8724c3df5','SI1':'85317167b4001dc027216c1c4e2faf058f0631a3'}
PREFIX={'RIE1':'docs/flora-runtime/rie1-617/','RIE2':'docs/flora-runtime/rie2-619/','SI1':'docs/flora-runtime/si1-615/'}
MAIN='fe66516c15726dc45de147ede2674c9172f8cac6'
def read(name):return json.loads((D/name).read_text())
def blob(pack,path):return subprocess.check_output(['git','show',PINS[pack]+':'+path],cwd=ROOT)
def original(pack,name):return json.loads(blob(pack,PREFIX[pack]+name))
def sha(value):return hashlib.sha256(value).hexdigest()
def check_sources(sources):
 original_by_alias={s['id']:(p,s)for p in ['RIE1','RIE2']for s in original(p,'Source-Ledger.json')}
 assert len(sources)==65 and len({s['original_url']for s in sources})==65
 seen=[]
 for s in sources:
  assert s['original_url'].startswith('https://')and s['original_bytes_sha256']is None
  assert s['canonical_acceptance']is False and s['rights_acceptance'].startswith('not granted')
  assert not any(t in s['original_url'].lower()for t in ['x-amz-','access_token','password=','authorization='])
  assert s['document_reference_count']==1
  for i in s['inspections']:
   pack,row=original_by_alias[i['source_id']];assert i['package']==pack and i['record']==row
   assert row['url']==s['original_url']and row['rights']
   if row['publication_date']:assert date.fromisoformat(row['publication_date'])<=date(2026,11,15)
   seen.append(i['source_id'])
 assert len(seen)==71 and len(set(seen))==71 and set(seen)==set(original_by_alias)
 aliases=read('Source-Aliases.json')
 assert aliases=={i['source_id']:s['id']for s in sources for i in s['inspections']}

def check_claims(claims):
 wanted={p+':'+c['id']:c for p,name in [('RIE1','Facts.json'),('RIE2','Claims.json')]for c in original(p,name)}
 assert len(claims)==len({c['id']for c in claims})==len(wanted)==362
 aliases=read('Source-Aliases.json')
 for c in claims:
  assert c['record']==wanted[c['id']]
  assert c['canonical_acceptance']is False and c['owner_mapping']is None
  assert c['document_refs']==sorted({aliases[s]for s in c['record']['source_refs']})
 # Supplemental reconciliation preserves every original table field; no new unsupported totals.
 context=read('Reconciliation-Context.json')
 for r in context:
  p,name=r['input'].split(':',1);assert r['record']==original(p,name)[r['pointer'][1:]]
  assert r['canonical_acceptance']is False and r['acceptance_class']=='B'

def check_excerpts(excerpts):
 assert {e['id']for e in excerpts}=={'EX-H126','EX-FCA','EX-ONS'}
 aliases=read('Source-Aliases.json')
 for e in excerpts:
  assert e['excerpt_content_sha256']==sha(e['text'].encode())
  assert e['content_kind']=='reviewed_web_excerpt'and e['primary_content_sha256']is None
  assert e['retrieval_method']=='approved_web_research_tool'and e['retrieval_reference']and e['locator']
  assert e['retrieved_at']=='2026-11-15'and e['document_id']==aliases[e['source_id']]
  assert e['rights']and e['limitations']and e['canonical_acceptance']is False
  assert len(e['text'].split())<=200

EXPECTED={
 'OBS-R2-FIN-H12026-0-NET_INCOME':('Lloyds Banking Group reporting segment Retail','H12026','net_income',5710,'EX-H126'),
 'OBS-R2-FIN-H12026-0-OPERATING_COSTS':('Lloyds Banking Group reporting segment Retail','H12026','operating_costs',-2872,'EX-H126'),
 'OBS-R2-FIN-H12026-0-LEASE_DEPRECIATION':('Lloyds Banking Group reporting segment Retail','H12026','lease_depreciation',-835,'EX-H126'),
 'OBS-R2-FIN-H12026-0-UNDERLYING_PROFIT':('Lloyds Banking Group reporting segment Retail','H12026','underlying_profit',2256,'EX-H126'),
 'OBS-R2-FIN-H12026-4-NET_INCOME':('Lloyds Banking Group consolidated total','H12026','net_income',9747,'EX-H126'),
 'OBS-R2-FIN-H12026-4-UNDERLYING_PROFIT':('Lloyds Banking Group consolidated total','H12026','underlying_profit',4215,'EX-H126')}
def check_proposals(atoms):
 from cios.applications.flora.blueprint_import.atomicity import validate_atomic_statement
 assert len(atoms)==len({a['id']for a in atoms})==8
 assert len({a['statement']for a in atoms})==8
 excerpts={e['id']:e for e in read('Reviewed-Excerpts.json')}
 originals={p+':'+c['id']:c for p,name in [('RIE1','Facts.json'),('RIE2','Claims.json')]for c in original(p,name)}
 for a in atoms:
  assert validate_atomic_statement(a['statement']).atomic
  assert a['canonical_acceptance']is False and a['owner_evidence_acceptance']is False and a['canonical_entity_id']is None
  assert a['claim_ref']in originals
  assert a['source_refs']==[excerpts[a['excerpt_ref']]['source_id']]
  if a['id']in EXPECTED:
   assert tuple(a[k]for k in ['scope','reporting_period','metric','value','excerpt_ref'])==EXPECTED[a['id']]
   assert a['period_start']=='2026-01-01'and a['period_end']=='2026-06-30'
   assert a['accounting_basis']=='alternative_performance_measure'and a['financial_measurement_state']=='actual'
   orig=originals[a['claim_ref']]
   assert a['value']==orig['value']
   if '-4-'in a['id']:assert a['original_scope_label']==orig['subject']and a['scope']=='Lloyds Banking Group consolidated total'
   else:assert a['scope']==orig['subject']
  elif a['id']=='OBS-SIC-K-WEIGHT24':
   assert a['value']==81 and a['excerpt_ref']=='EX-ONS'and a['reporting_period']=='2024'
   assert a['metric']=='rounded_GVA_weight'and a['accounting_basis']=='GVA at basic prices'
  else:
   assert a['id']=='OBS-FCA-RECEIVED'and a['scope'].startswith('Lloyds Bank PLC legal entity')
   assert a['value']==118762 and a['excerpt_ref']=='EX-FCA'and a['metric']=='complaints_received'
   assert(a['period_start'],a['period_end'])==('2026-01-01','2026-06-30')

def check_matrix(matrix):
 assert len(matrix)==len({m['id']for m in matrix})
 assert set(m['class']for m in matrix)==set('ABCDE')
 assert all(m['reason']and m['owner_acceptance']is False for m in matrix)
 by={m['id']:m for m in matrix}
 for c in read('Claim-Ledger.json'):assert c['id']in by
 for a in read('Observation-Proposals.json'):assert by[a['id']if a['id']=='OBS-FCA-RECEIVED'else a['claim_ref']]['class']=='A'
 assert sum(m['class']=='A'for m in matrix)==8
 for m in matrix:
  if m['class']=='A':assert m['id']in {'OBS-FCA-RECEIVED'}|{a['claim_ref']for a in read('Observation-Proposals.json')if a['id']!='OBS-FCA-RECEIVED'}
 assert by['RIE1:LAND-L26-F1']['class']=='B'
 assert by['NEG-IPSOS-LABEL']['class']=='D'and by['NEG-AI-VALUE']['class']=='D'
 assert by['USE-COMPOUND-PROMOTION']['class']=='E'
 for i in read('Strategic-Agendas.json'):assert by[i['id']]['class']=='C'
 for r in read('Relationship-Proposals.json'):assert by[r['id']]['class']=='B'


def check_agendas(issues):
 old={i['id']:i for i in original('RIE1','Agenda-Candidates.json')};new={i['id']:i for i in original('RIE2','Leadership-Agenda.json')}
 assert len(issues)==len({i['id']for i in issues})==8
 assert sum(len(i['versions'])for i in issues)==12
 for i in issues:
  assert i['versions'][0]['record']==old[i['id']]
  assert i['current_version']==('RIE2'if i['id']in new else'RIE1')
  assert i['acceptance_class']=='C'and i['canonical_acceptance']is False and i['pipeline_writes']==0
  if i['id']in new:
   assert len(i['versions'])==2 and i['versions'][1]['record']==new[i['id']]
   x=i['versions'][1]['record'];assert x['buyer_need']==x['external_supplier_scope']=='unknown'and x['external_value']is None
   assert x['potential_remaining_decision'].startswith('UNKNOWN')and x['counter_evidence']and x['what_disproves_it']


def check_financial_controls():
 # Execute pinned, previously independently reviewed arithmetic/scope checks, not a refreshed implementation comparator.
 code=blob('RIE2','tools/research/rie2_619_validation.py')
 ns={'__file__':str(ROOT/'tools/research/rie2_619_validation.py'),'__name__':'ric1_pinned_rie2_checks'}
 exec(compile(code,'pinned-rie2-validation','exec'),ns)
 ns['check_finance'](original('RIE2','Financial-Reconciliation.json'))
 ns['check_outcomes'](original('RIE2','Customer-Outcomes.json'))
 ns['check_comparability'](original('RIE2','Banking-Comparability.json'))
 return ns

def validate():
 p=read('Pinned-Inputs.json');assert p['packages']==PINS and p['validated_main']==MAIN
 for i in p['inputs']:assert i['commit']==PINS[i['package']]and sha(blob(i['package'],i['path']))==i['repository_content_sha256']
 check_sources(read('Source-Ledger.json'));check_claims(read('Claim-Ledger.json'));check_excerpts(read('Reviewed-Excerpts.json'));check_proposals(read('Observation-Proposals.json'));check_matrix(read('Evidence-Acceptance-Matrix.json'));check_agendas(read('Strategic-Agendas.json'));check_financial_controls()
 gaps=read('Gap-Register.json');assert gaps['original_RIE1']==original('RIE1','Gap-Disposition.json')and gaps['RIE2_enrichment']==original('RIE2','Gap-Dispositions.json')
 assert [len(gaps['RIE2_enrichment'][k])for k in ['visual_nine','overlay_thirteen','rco_nine']]==[9,13,9]
 sectors=gaps['all_twenty_sectors'];assert [s['sic']for s in sectors]==list('ABCDEFGHIJKLMNOPQRST')and all(s['foundational_standard'].startswith('PARTIAL')for s in sectors)
 for r in original('RIE2','Ownership-Checks.json')['owners']:
  assert sha((ROOT/r['path']).read_bytes())==r['sha256']
  assert(ROOT/r['path']).read_bytes()==subprocess.check_output(['git','show',MAIN+':'+r['path']],cwd=ROOT)
 for r in read('Relationship-Proposals.json'):assert r['endpoint_mapping']is None and r['canonical_acceptance']is False
 negatives=read('Contradictions-and-Negatives.json');assert len(negatives)==17 and len(next(n for n in negatives if n['id']=='NEG-AI-VALUE')['versions'])==2
 dry=read('Import-Dry-Run.json');assert dry['canonical_mutations']==dry['pipeline_writes']==dry['approvals_created']==dry['reviews_created']==dry['source_registrations']==0
 assert dry['atomic_observation_proposals']==8 and dry['effect_counts']=={'unresolved':16,'mapped':3,'projection':1,'quarantine':1}
 assert dry['cross_workspace_inspection_denied']and dry['cross_workspace_planning_denied']and dry['repeated_plan_idempotent']
 package=read('Import-Package-Proposal.json');assert package['production_manifest']is None and package['canonical_target_ids']is None
 assert package['records_sha256']==dry['proposed_payload_sha256']==sha((D/package['records_path']).read_bytes())
 summary=read('Consolidation-Summary.json');assert summary['matrix_counts']==dict(Counter(m['class']for m in read('Evidence-Acceptance-Matrix.json')))
 return {'status':'research QA PASS; not owner acceptance or production verification','documents':65,'inspections':71,'original_claim_records':362,'current_issues':8,'proposed_atoms':8,'matrix_counts':summary['matrix_counts'],'production_acceptance':'UNVERIFIED','canonical_mutations':0,'pipeline_writes':0}
if __name__=='__main__':print(json.dumps(validate(),indent=2))
