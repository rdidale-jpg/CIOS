"""Offline integrity/contract QA for RIE2 proposals. No inference, scoring, qualification or persistence engine."""
from pathlib import Path
from datetime import date
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'docs/flora-runtime/rie2-619'
RIE1='c57ed9728473563b5535db36d5bfbe5e96a8c572';MAIN='fe66516c15726dc45de147ede2674c9172f8cac6'
def read(name):return json.loads((D/name).read_text())
def blob(path):return subprocess.check_output(['git','show',RIE1+':'+path],cwd=ROOT)
def baseline(name):return json.loads(blob('docs/flora-runtime/rie1-617/'+name))
def check_sources(sources):
 assert len(sources)==len({s['id']for s in sources})==19
 for s in sources:
  assert s['url'].startswith('https://')
  assert not any(t in s['url'].lower()for t in ['x-amz-','access_token','password=','authorization='])
  assert s['rights'] and s['confidence_reason'] and s['reviewed_locator'] and s['read_extent'] and s['scope']
  assert s['canonical_acceptance']is False and s['original_response_sha256']is None
  if s['publication_date']:assert date.fromisoformat(s['publication_date'])<=date(2026,11,14)
  assert s['production_import_status'].startswith('unverified')
def check_finance(f):
 p={p['id']:p for p in f['periods']};assert set(p)=={'FY2024','FY2025','H12025','H22025','H12026'}
 # Independently transcribed reported Group totals: order NII/other/lease/net/op/remediation/total/PBI/imp/profit.
 golden={'FY2024':[12845,5597,-1325,17117,-9442,-899,-10341,6776,-433,6343],'FY2025':[13635,6120,-1454,18301,-9761,-968,-10729,7572,-795,6777],'H12025':[6655,2969,-710,8914,-4874,-37,-4911,4003,-442,3561],'H22025':[6980,3151,-744,9387,-4887,-931,-5818,3569,-353,3216],'H12026':[7278,3310,-841,9747,-4876,-39,-4915,4832,-617,4215]}
 names=['net_interest_income','other_income','lease_depreciation','net_income','operating_costs','remediation','total_costs','profit_before_impairment','impairment','underlying_profit']
 for key,row in p.items():
  v=row['values'];assert row['unit']=='GBP million'and row['accounting_basis']=='alternative_performance_measure'
  assert row['duration_months']==(12 if key.startswith('FY')else 6)
  assert row['period_start']==key[-4:]+('-07-01'if key.startswith('H2')else'-01-01')
  assert row['period_end']==key[-4:]+('-06-30'if key.startswith('H1')else'-12-31')
  for name,want in zip(names,golden[key]):assert v[name][4]==want,(key,name)
  for vals in v.values():assert len(vals)==5 and sum(vals[:4])==vals[4]
  for i in range(5):
   assert v['net_interest_income'][i]+v['other_income'][i]+v['lease_depreciation'][i]==v['net_income'][i]
   assert v['operating_costs'][i]+v['remediation'][i]==v['total_costs'][i]
   assert v['net_income'][i]+v['total_costs'][i]==v['profit_before_impairment'][i]
   assert v['profit_before_impairment'][i]+v['impairment'][i]==v['underlying_profit'][i]
 for metric in names:
  assert all(a+b==c for a,b,c in zip(p['H12025']['values'][metric],p['H22025']['values'][metric],p['FY2025']['values'][metric]))
 for period,b in f['statutory_bridges'].items():
  s=b['statutory'];u=b['underlying'];a=b['statutory_to_underlying']
  assert s['net_interest_income']+s['other_income']==s['total_income']
  assert s['total_income']+s['operating_expenses']+s['impairment']==s['pbt']
  for k in ['net_interest_income','other_income','impairment','pbt']:assert s[k]+sum(a[k])==u[k]
  assert s['total_income']+sum(a['total_income'])==u['net_income']
  assert s['operating_expenses']+sum(a['operating_expenses'])==u['total_costs']
  assert u['net_income']+u['total_costs']+u['impairment']==u['pbt']==p[period]['values']['underlying_profit'][4]
 assert f['statutory_bridges']['H12026']['statutory_to_underlying']['impairment']==[0,0,-1]
 for b in f['annual_bridges'].values():
  assert b['underlying_profit']+b['restructuring']+b['volatility_other']==b['statutory_pbt']
  assert b['statutory_pbt']+b['tax']==b['pat']
 q=f['q3_nine_months_pinned_input'];assert q['commit']==RIE1 and q['values']==baseline('Lloyds-Financial-Reconciliation.json')
 assert p['H12026']['values']['underlying_profit'][4]+2367==q['values']['underlying']['underlying_profit'][0]
 assert f['guidance_2026']['measurement_state']=='guidance'and f['targets_2030']['measurement_state']=='target'
 assert f['current_capital_liquidity']['lcr_pct_12_month_average']==143
 assert f['current_capital_liquidity']['nsfr_pct_4_quarter_average']==123

def check_outcomes(x):
 assert x['entity']=='Lloyds Bank PLC'
 assert (x['period_start'],x['period_end'])==('2026-01-01','2026-06-30')
 assert (x['complaints_received'],x['complaints_closed'])==(118762,118861)
 assert (x['closed_within_3_days_pct'],x['closed_after_3_days_within_8_weeks_pct'],x['complaints_upheld_by_firm_pct'])==(55.25,31.49,66.12)
 assert x['consumer_credit_separate_table']=={'received':12308,'closed':12222,'upheld_pct':21.50,'warning':'Different activity/product table; never substitute for or add to all-product total.'}
 f=x['fos'];assert(f['period_start'],f['period_end'])==('2026-04-01','2026-09-30')
 assert f['new_cases']==3764==sum(f[k]for k in ['banking_credit','mortgages_home_finance','general_insurance','investments','pensions'])
 assert 'escalation_rate'not in x and 'escalation_rate'not in f
 assert x['survey']['scores_admitted']==[]
 assert x['canonical_acceptance']is False and x['pipeline_writes']==0

def check_issues(issues):
 assert {x['id']for x in issues}=={'LBG-A1','LBG-A2','LBG-A3','LBG-A4'}
 for x in issues:
  assert x['baseline_commit']==RIE1 and x['buyer_need']=='unknown'and x['external_supplier_scope']=='unknown'
  assert x['external_value']is None and x['canonical_acceptance']is False and x['pipeline_writes']==0
  assert x['what_disproves_it']and x['counter_evidence']and x['alternatives']and x['rie2_delta']and x['specific_next_commercial_investigation']
  assert x['potential_remaining_decision'].startswith('UNKNOWN')

def check_comparability(x):
 assert x['periods']==['H1 2026','H1 2025']
 for row in x['rows']:
  assert row['financial_level_comparison'].startswith('NOT ADMITTED')
  assert all(row['income'][i]+row['expenses'][i]+row['impairment'][i]==row['profit'][i]for i in [0,1])
 lg=x['additional_nonbank_example'];assert sum(lg['core_segment_components_2026'])==lg['core_operating_profit'][0]==918
 assert lg['continuing_pbt'][0]==699!=lg['core_operating_profit'][0]

def validate():
 sources=read('Source-Ledger.json');check_sources(sources);ids={s['id']for s in sources}
 check_finance(read('Financial-Reconciliation.json'));check_outcomes(read('Customer-Outcomes.json'));check_issues(read('Leadership-Agenda.json'));check_comparability(read('Banking-Comparability.json'))
 claims=read('Claims.json');assert len(claims)==len({c['id']for c in claims})
 for c in claims:
  assert set(c['source_refs'])<=ids and c['source_locator']and c['rights_status']and c['uncertainty']
  assert c['canonical_acceptance']is False
  if c['claim_class']=='reported_financial_value_candidate':assert c['financial_measurement_state']in ['actual','prior_period_comparator']and c['accounting_basis']=='alternative_performance_measure'
 for i in read('Leadership-Agenda.json'):assert set(i['source_refs'])<=ids
 inputs=read('Pinned-Inputs.json')
 for item in inputs['rie1_inputs']:assert hashlib.sha256(blob(item['path'])).hexdigest()==item['repository_blob_content_sha256']
 original_sectors=baseline('Sector-Research.json');assert [s['sic']for s in original_sectors]==list('ABCDEFGHIJKLMNOPQRST')
 assert all(s['foundational_standard'].startswith('PARTIAL')for s in original_sectors)
 gaps=read('Gap-Dispositions.json');assert[len(gaps[k])for k in ['visual_nine','overlay_thirteen','rco_nine']]==[9,13,9]
 original=json.loads((ROOT/'enterprise-knowledge/banking/research-model/Assessment-Overlay.json').read_text())
 for group,owner in [('overlay_thirteen','gaps'),('rco_nine','candidates')]:
  by={r['id']:r for r in original[owner]}
  for r in gaps[group]:
   o=by[r['id']];assert r['original_record_sha256']==hashlib.sha256(json.dumps(o,sort_keys=True).encode()).hexdigest()
   if group=='overlay_thirteen':assert r['original_status']==o['status']
   else:assert r['original_research_tier']==o['research_tier']and r['original_qualification']==o['qualification']
 for r in gaps['visual_nine']:assert r['rie1_remaining']and r['rie2_remaining']
 m=read('Operating-Model.json')
 for e in m['principal_legal_interests']:
  assert e['as_at']=='2025-12-31'
  if e['interest_type']=='indirect':assert e['intermediate_parent']is None
 for r in m['current_roles']:assert r['buyer_status']=='not established'
 for s in m['supplier_capabilities']:assert all(s[k]is None for k in ['value','term_end','exclusivity','counterparty_legal_entity'])
 for row in read('Ownership-Checks.json')['owners']:
  assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256']
  assert (ROOT/row['path']).read_bytes()==subprocess.check_output(['git','show',MAIN+':'+row['path']],cwd=ROOT)
 dry=read('Import-Dry-Run.json');assert dry['atomic_observation_proposals']==8 and dry['canonical_mutations']==dry['pipeline_writes']==dry['reviews_created']==dry['approvals_created']==0
 assert dry['effects_by_original_id']['NEG-COMPOUND']=='quarantine'and dry['effects_by_original_id']['PROJECTION-ONLY']=='projection'
 assert dry['cross_workspace_inspection_denied']and dry['cross_workspace_planning_denied']and dry['repeated_plan_idempotent']
 # Validate existing SourceRecord shape, disabled and in-memory only. No source registration or collection.
 from cios.applications.flora.live.source_registry import SourceRecord,SOURCES
 before=len(SOURCES)
 for s in [next(x for x in sources if x['id']=='R2-LBG-H126')]:
  candidate=SourceRecord(source_id=s['id'],organisation=s['scope'],source_name=s['title'],source_type='investor_results'if s['evidence_kind']=='company_reported'else'regulator_publications',url=s['url'],sector='Banking/FinancialServices research',evidence_tier='tier_1_company'if s['evidence_kind']=='company_reported'else'tier_1_public_body',expected_signal_types=[],enabled=False,notes='Offline contract probe, not registered/accepted source or collection authority')
  assert candidate.enabled is False and candidate.canonical_enterprise_id is None
 assert len(SOURCES)==before
 delta=read('Source-Delta.json');assert delta['new_document_urls']+delta['reinspected_document_urls']==len(sources)
 return {'status':'integrity/contract PASS, not research completeness or owner acceptance','sources':len(sources),'new_document_urls':delta['new_document_urls'],'reinspections':delta['reinspected_document_urls'],'financial_periods':5,'leadership_candidates':4,'source_registration_writes':0,'canonical_mutations':0,'pipeline_writes':0,'original_bytes':'unavailable; no hashes fabricated'}
if __name__=='__main__':print(json.dumps(validate(),indent=2))
