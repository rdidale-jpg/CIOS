"""Offline integrity checks for the RIE-1 research proposal, not an intelligence engine.

No qualification, matching, acceptance, mutation, network collection or scoring.
"""
from pathlib import Path
import hashlib,json
from datetime import date
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'docs/flora-runtime/rie1-617'
AS_OF=date(2026,11,14)
def read(name):return json.loads((D/name).read_text())
def check_sources(sources):
 ids=[s['id']for s in sources];assert len(ids)==len(set(ids))
 for s in sources:
  assert s['url'].startswith('https://')
  assert not any(term in s['url'].lower()for term in ['x-amz-','access_token','authorization=','password='])
  assert s['rights'] and s['extent'] and s['confidence_reason']
  assert s['canonical_acceptance']is False
  assert date.fromisoformat(s['retrieved_at'])<=AS_OF
  if s['publication_date']:assert date.fromisoformat(s['publication_date'])<=AS_OF
  assert s['reporting_period'] and s['geography']
  assert s['response_sha256']is None,'Unavailable source bytes must not have fabricated hashes'
def check_refs(records,source_ids):
 for r in records:
  assert r['source_refs'] and set(r['source_refs'])<=source_ids
  assert r['canonical_acceptance']is False
  assert r['pipeline_handoff']is False

def check_financials(f):
 assert f['period']=='Nine months ended 30 September'
 assert f['columns']==['2026','2025']
 u=f['underlying'];s=f['statutory']
 for i in [0,1]:
  assert u['net_interest_income'][i]+u['other_income'][i]+u['operating_lease_depreciation'][i]==u['net_income'][i]
  assert u['operating_costs'][i]+u['remediation'][i]==u['total_costs'][i]
  assert u['net_income'][i]+u['total_costs'][i]==u['profit_before_impairment'][i]
  assert u['profit_before_impairment'][i]+u['impairment'][i]==u['underlying_profit'][i]
  assert u['underlying_profit'][i]+u['restructuring'][i]+u['volatility_other'][i]==u['statutory_pbt'][i]
  assert u['statutory_pbt'][i]+u['tax'][i]==u['statutory_pat'][i]
  assert s['net_interest_income'][i]+s['other_income'][i]==s['total_income'][i]
  assert s['total_income'][i]+s['operating_expenses'][i]+s['impairment'][i]==s['pbt'][i]
  assert s['pbt'][i]+s['tax'][i]==s['pat'][i]==u['statutory_pat'][i]
  assert round(-100*u['total_costs'][i]/u['net_income'][i],1)==f['ratios_reported']['cost_income_pct'][i]
 d=f['deposit_changes_YTD_GBP_bn'];assert round(d['commercial']+d['retail']+d['central_items'],1)==d['group']
 assert d['central_items']==0.4
 assert s['total_income'][0]!=u['net_income'][0]
 assert s['impairment'][0]!=u['impairment'][0]

def validate():
 sources=read('Source-Ledger.json');check_sources(sources);ids={s['id']for s in sources}
 facts=read('Facts.json');check_refs(facts,ids);assert len({f['id']for f in facts})==len(facts)
 fids={f['id']for f in facts}
 sectors=read('Sector-Research.json');assert [s['sic']for s in sectors]==list('ABCDEFGHIJKLMNOPQRST')
 displayed=json.loads((ROOT/'cios/applications/flora/visual_v2_assets/economy.json').read_text())['districts']
 assert {(s['panorama_id'],s['label'],s['sic'])for s in sectors}=={(s['id'],s['label'],s['sic'])for s in displayed}
 check_refs(sectors,ids)
 for s in sectors:
  assert set(s['pestle'])=={'Political','Economic','Social','Technological','Legal','Environmental'}
  assert len(s['five_forces'])==5
  assert set(s['fact_refs'])<=fids
  assert s['foundational_standard'].startswith('PARTIAL')
  assert s['coverage'] and s['counter_evidence_and_limits'] and s['next_research']
 assert next(s for s in sectors if s['sic']=='T')['strategic_questions']==[]
 assert next(s for s in sectors if s['sic']=='C')['coverage']['customer_supplier_relationships'].startswith('unknown')
 extraction=read('Statistical-Extraction.json');assert len(extraction['columns'])==23
 assert sum(extraction['weights_per_thousand'][extraction['columns'].index(s)]for s in 'ABCDEFGHIJKLMNOPQRST')==1002
 assert extraction['columns'].index('C')==4
 assert extraction['september_yoy_volume_pct'][4]==4.4
 check_financials(read('Lloyds-Financial-Reconciliation.json'))
 agendas=read('Agenda-Candidates.json');check_refs(agendas,ids)
 for a in agendas:
  assert set(a['fact_refs'])<=fids
  assert a['buyer_need'].startswith('unknown') and a['open_decision_status'].startswith('UNKNOWN')
  assert a['counter_evidence']and a['alternatives']and a['next_salesperson_learning_action']
  assert a['opportunity_value']is None and a['external_supplier_scope']=='unknown'
  assert all(next(s for s in sources if s['id']==sid)['acquisition']!='official_index_only'for sid in a['source_refs'])
 check_refs(read('Relationships.json'),ids)
 for edge in read('Relationships.json'):
  assert edge['monetary_flow']is None and edge['scope']
  assert not(edge['subject']=='Lloyds Banking Group'and edge['object']=='CHAPS')
 gaps=read('Gap-Disposition.json');assert [len(gaps[k])for k in ['visual_nine','overlay_thirteen','rco_nine']]==[9,13,9]
 for p,digest in gaps['owner_digests'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest
 dry=read('Import-Dry-Run.json');assert dry['canonical_mutations']==dry['pipeline_writes']==dry['reviews_created']==dry['approvals_created']==0
 assert dry['atomic_observation_proposals']==8 and dry['repeated_plan_idempotent']
 assert all(a['source_payload_retained']and a['statement_retained']for a in dry['adapter_checks'])
 assert dry['effects_by_original_id']['NEG-COMPOUND']=='quarantine'
 assert dry['effects_by_original_id']['PROJECTION-ONLY']=='projection'
 assert dry['cross_workspace_inspection_denied']and dry['cross_workspace_planning_denied']
 return {'source_candidates':len(sources),'original_text_sources':sum(s['acquisition']=='official_original_via_research_tool'for s in sources),'index_only_sources':sum(s['acquisition']=='official_index_only'for s in sources),'research_fact_bundles':len(facts),'sector_dossiers':len(sectors),'foundational_standards_met':0,'agenda_interpretations':len(agendas),'typed_edges':len(read('Relationships.json')),'canonical_mutations':0,'pipeline_writes':0,'status':'integrity checks pass; substantive coverage remains partial; owner evidence acceptance pending'}
if __name__=='__main__':print(json.dumps(validate(),indent=2))
