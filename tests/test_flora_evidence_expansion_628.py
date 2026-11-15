"""EAI-1 permitted-source views and owner-side evidence decision preparation."""
from copy import deepcopy
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
import hashlib,inspect,json,subprocess,types
import pytest
from cios.applications.flora import leadership_agenda as a,visual_streams as v,intelligence_presentation as p
from cios.applications.flora.research_intelligence import model,registry
from cios.applications.flora.research_intelligence.source_import import official_url
from tests.test_flora_sales_pipeline import actor,web
from tests.test_flora_security_repair_01b import authority,signed

ROOT=Path(__file__).resolve().parents[1];DOC=ROOT/'docs/flora-runtime/eai1-628'
BASE='8a53777d1dec359f56b66e533d512c0a86881939'


def package(key):
 domain,name,*_=a.EAI_RELEASES[key]
 return json.loads((registry.snapshot_boundary(domain)/name).read_text())


def topic(scope,key):return next(r for r in a.agenda(scope)if r.key==key)


def test_eight_forms_are_lossless_individual_unexecuted_owner_choices_not_imports():
 original=json.loads(subprocess.check_output(['git','show','9db8253:docs/flora-runtime/ric1/Observation-Proposals.json'],cwd=ROOT))
 forms=json.loads((DOC/'Eight-Evidence-Review-Proposals.json').read_text())
 assert len(forms)==8 and len({f['form_id']for f in forms})==8
 assert [f['original_proposal']for f in forms]==original
 for f in forms:
  choice=f['owner_decision_form'];receipt=f['existing_state_reconciliation'];review=f['primary_review']
  assert choice['selected']is None and choice['choices']==['Accept','Defer','Reject']
  assert not any(choice[k]for k in ['decision_recorded','import_executed','canonical_mutation'])
  assert receipt['canonical_target_id']is None and receipt['owner_workspace_id']is None
  assert receipt['production_receipt_status'].startswith('UNVERIFIED')
  assert review['source_rechecked']and review['original_content_sha256']is None
  assert f['original_proposal']['owner_evidence_acceptance']is False
  assert f['original_proposal']['canonical_acceptance']is False
  assert f['canonical_execution_recommendation'].startswith('Defer')


def test_eight_measurements_keep_sign_period_and_group_legal_segment_boundaries():
 forms=json.loads((DOC/'Eight-Evidence-Review-Proposals.json').read_text());fca=next(f for f in forms if f['original_proposal']['metric']=='complaints_received')
 identity=fca['primary_review']['issuer_or_entity_verified']
 assert identity['FRN']=='119278'and identity['companies_house_number']=='00002065'
 for f in forms:
  r=f['primary_review'];o=f['original_proposal']
  assert (r['value'],r['unit'],r['accounting_basis'])==(o['value'],o['unit'],o['accounting_basis'])
  if o['metric']in {'operating_costs','lease_depreciation'}:assert r['value']<0
  if o['accounting_basis']=='alternative_performance_measure':
   assert (r['period_start'],r['period_end'])==('2026-01-01','2026-06-30')
   assert r['issuer_or_entity_verified']['SEC_CIK']=='1160106'
   assert r['issuer_or_entity_verified']['companies_house_number']=='SC095000'
   assert not f['rights_and_admission']['visual_publisher_admitted']
 lease=next(f for f in forms if f['original_proposal']['metric']=='lease_depreciation')
 assert '£32m'in lease['primary_review']['measurement_definition']and 'gross'in lease['primary_review']['measurement_definition']


def test_owner_financial_reconciliation_exact_and_never_live_leasing_margin():
 d=json.loads((DOC/'Financial-Reconciliation.json').read_text())
 assert not d['runtime_admission']and not d['canonical_import']and d['original_byte_hash']is None
 for key in ['Retail_H126','Retail_H125']:
  r=d[key];assert r['net_interest_income']+r['other_income']+r['lease_depreciation']==r['net_income']
  assert r['net_income']+r['operating_costs']+r['remediation']+r['impairment']==r['underlying_profit_before_tax']
 g=d['Group_H126'];assert g['net_income']+g['operating_costs']+g['remediation']+g['impairment']==4215
 new,old=d['Retail_H126'],d['Retail_H125']
 assert new['other_income']-old['other_income']==130
 assert abs(new['lease_depreciation'])-abs(old['lease_depreciation'])==129
 assert 130-129==1 and new['underlying_profit_before_tax']-old['underlying_profit_before_tax']==282
 html=v.render('/enterprises/lloyds',{'agenda':['funding-base']})
 assert not any(t in html for t in ('£130m','£129m','£1m','leasing profit margin'))


@pytest.mark.parametrize('key',['service','provider','cyber'])
def test_new_releases_use_existing_publisher_owner_contracts_and_no_original_archive(key):
 d=package(key);s=d['source']
 assert d['authority']=='candidate_intelligence'and d['canonical_mutation']is False
 assert official_url(s['url'])==s['retrieval_url']
 assert s['primary_content_sha256']is None and s['content_kind']=='reviewed_web_excerpt'
 assert hashlib.sha256((ROOT/s['text_path']).read_bytes()).hexdigest()==s['text_sha256']
 assert model.primary_text(s)and a._eai_release(key)
 if key=='cyber':
  assert all(o['accepted_observation']is False for o in d['observations'])
  assert len(d['observations'])==9 and sum(len(e['quote'].split())for e in s['excerpts'])<=200


def test_survey_is_estimated_with_inspectable_method_and_no_enterprise_incident():
 row=topic('uk','cyber-resilience');f=row.facts[0]
 assert f.semantic_type=='estimated'and f.canonical_status=='candidate_intelligence'
 assert '43%'in f.text and '69%'in f.text and 'eligible'in f.text
 assert '250'in f.method and 'Weighted'in f.method
 retained=model.primary_text(package('cyber')['source'])
 for t in ['August to December 2025','weighted','Sole traders','250 or more employees','preceding 12 months','willing to report']:
  assert t in retained
 html=p.render(row.conclusion)+p.render(f)
 assert 'Estimated'in html and 'Depends on estimated'in html
 assert 'in line with the prior year'in html and 'named bank'in html
 assert 'sole traders'in html and not p.NON_CORE.search(row.conclusion.text)


def test_provider_legal_entities_publication_effective_date_and_no_contract_edges():
 row=topic('banking','provider-oversight');f=row.facts[0]
 assert '13 July 2026'in f.text and f.sources[0].published=='2026-07-10'
 for entity in ['Microsoft Ireland Operations Limited','Google Cloud EMEA Limited','Amazon Web Services EMEA SARL','Oracle Corporation UK Limited']:assert entity in f.text
 assert 'contract'in p.render(row.conclusion)and '10 July'in p.render(row.conclusion)
 assert 'bank customer'in p.render(row.conclusion)


def test_service_measures_omit_unresolved_speed_and_keep_cohorts_and_firm_outcomes_separate():
 row=topic('lloyds','service-recovery');text=p.render(row.conclusion)+''.join(p.render(f)for f in row.facts)
 assert len(row.facts)==3
 for number in ['118,762','118,861','66.12%']:assert number in text
 for forbidden in ['55.25','calendar days','business days','backlog cleared']:assert forbidden not in text
 assert 'Different cohorts'in text and 'No deterioration'in text and 'not independent adjudication'in text
 assert 'FOS April–September'in text
 assert len(package('service')['claims'])==2


def test_stock_change_is_calculated_not_a_same_portfolio_flow_or_lease_bridge():
 row=topic('lloyds','funding-base');calc=row.facts[-1]
 assert calc.semantic_type=='calculated'and calc.value==Decimal('6.3')
 assert calc.canonical_status=='derived_view_not_canonical'
 assert calc.method.startswith('502.8 − 496.5')
 assert '2025'in calc.period and '2026'in calc.period and 'two balance-sheet dates'in calc.period
 text=p.render(calc)+p.render(row.conclusion)
 assert 'not adjusted'in text.lower()and 'organic'in text and 'supplier budget'in text
 assert all(f.semantic_type=='reported'for f in row.facts[:2])


@pytest.mark.parametrize('field,value',[('scope','Other Group'),('unit','GBP million'),('basis','IFRS revenue'),('period','H1 2026'),('measurement_state','target'),('semantic_type','estimated'),('value',None),('freshness','stale'),('owner_only',True)])
def test_stock_bridge_rejects_unlike_scope_units_dates_states_or_uncertain_inputs(field,value):
 facts=a._claims(model.load_assessment(),('LBG-AR25-DEPOSITS','LBG-Q326-DEPOSITS'))
 changed=(replace(facts[0],**{field:value}),facts[1])
 assert a._deposit_change(changed)is None


@pytest.mark.parametrize('key',['service','provider','cyber'])
@pytest.mark.parametrize('mutation',['rights','withdrawn','stale','core_contradiction','owner_only','wrong_subject','canonical_mutation','source_url'])
def test_repinned_bad_proposal_still_cannot_pass_lifecycle_rights_identity_or_private_gate(key,mutation,tmp_path,monkeypatch):
 d=package(key);s=d['source']
 if mutation=='rights':s['rights']['status']='revoked'
 elif mutation=='wrong_subject':d['subject_ref']='FOREIGN-PRIVATE'
 elif mutation=='canonical_mutation':d['canonical_mutation']=True
 elif mutation=='source_url':s['url']='https://www.sec.gov/forged'
 else:s[mutation]='stale'if mutation=='stale'else True
 if mutation=='stale':s['freshness']='stale'
 domain,name,*_=a.EAI_RELEASES[key];path=tmp_path/name;path.write_text(json.dumps(d))
 pins=deepcopy(a._pins());pins['eai_releases'][key]=a.fingerprint(d)
 monkeypatch.setattr(a,'_pins',lambda:pins)
 original=registry.snapshot_boundary
 monkeypatch.setattr(registry,'snapshot_boundary',lambda domain,repo=None:tmp_path)
 assert a._eai_release(key)is None


@pytest.mark.parametrize('key',['service','provider','cyber'])
def test_missing_candidate_is_omitted_without_unrelated_empty_panels(key,tmp_path,monkeypatch):
 original=registry.snapshot_boundary;domain,name,scope,subject,ids=a.EAI_RELEASES[key]
 monkeypatch.setattr(registry,'snapshot_boundary',lambda d,repo=None:tmp_path if d==domain else original(d,repo))
 assert a._eai_release(key)is None


def test_source_ledger_and_proposed_decision_do_not_activate_sec_or_ons():
 for url in ['https://www.sec.gov/Archives/edgar/data/1160106/000116010626000022/lyg-20260630.htm','https://www.ons.gov.uk/economy/grossdomesticproductgdp/bulletins/gdpmonthlyestimateuk/september2026/pdf']:
  with pytest.raises(ValueError):official_url(url)
 path='cios/applications/flora/research_intelligence/source_import.py'
 assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
 decision=(ROOT/'architecture/decisions/ADR-027-Document-Scoped-Publisher-Admission-Proposal.md').read_text()
 assert 'Status: Proposed'in decision and 'not accepted or implemented'in decision
 assert 'SEC hosting does not make an issuer-authored filing'in decision


def test_news_handoff_is_not_imported_report_weekly_edition_or_news_implementation():
 d=json.loads((DOC/'Banking-News-Handoff.json').read_text());r=d['external_report']
 assert r['reported_completed_by_owner']and not r['actual_original_report_retrieved']and not r['GitHub_research_PR_identified']
 assert not any(d[k]for k in ['news_ui_implemented','collector_or_schedule_created','canonical_mutations','pipeline_mutations','images_copied'])
 events=d['events'];assert len(events)==6 and len({e['event_key']for e in events})==6
 ctp=next(e for e in events if e['event_key'].startswith('CTP-'))
 assert len(ctp['source_urls'])==2 and ctp['publication_date']=='2026-07-10'and ctp['effective_date']=='2026-07-13'
 cass=next(e for e in events if e['event_key'].startswith('CASS-'))
 assert 'July–September2026'in cass['reporting_period']and 'April–June2026'in cass['reporting_period']
 assert all(e['runtime_news_admission']is False for e in events)
 assert all(actor['canonical_id']is None and actor['this_handoff_import_executed']is False and actor['canonical_record_presence']=='UNVERIFIED' for actor in d['actors'])
 assert all('news'not in b['streams']for b in v.SCOPES.values())


def test_all_163_prior_sources_and_exact_comparator_remain_and_unknown_additions_fail():
 from tools.research import history_integrity as current
 source=subprocess.check_output(['git','show',BASE+':tools/research/history_integrity.py'],cwd=ROOT).decode()
 old=types.ModuleType('eai_original_history');exec(compile(source,'original_history','exec'),old.__dict__)
 original=old.approved_history(ROOT);now=current.approved_history(ROOT)
 assert len(original)==163 and len(now)==169
 assert {k:now[k]for k in original}==original
 assert set(now)-set(original)==set(current.EAI1_CANDIDATE_ADDITIONS)
 body=source.split('def compare_history(',1)[1].split('\n\ndef verify_history',1)[0]
 assert inspect.getsource(current.compare_history).split('def compare_history(',1)[1].strip()==body.strip()
 for path in current.EAI1_CANDIDATE_ADDITIONS:
  changed=deepcopy(now);changed[path]+=b'unapproved'
  with pytest.raises(AssertionError):current.compare_history(now,changed)
 changed=deepcopy(now);changed['enterprise-knowledge/banking/research-model/source-snapshots/EAI1-UNKNOWN.txt']=b'unknown'
 with pytest.raises(AssertionError):current.compare_history(now,changed)


def test_protected_owners_policy_and_all_existing_dependency_pins_are_unchanged():
 manifest=json.loads((DOC/'Preserved-Owners.json').read_text());assert manifest['base_sha']==BASE
 for r in manifest['unchanged']:
  content=(ROOT/r['path']).read_bytes()
  assert hashlib.sha256(content).hexdigest()==r['sha256']
  assert content==subprocess.check_output(['git','show',BASE+':'+r['path']],cwd=ROOT)
 path='cios/applications/flora/visual_stream_assets/agenda-dependencies.json';old=json.loads(subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT));new=a._pins()
 for key in ['claims','sources']:
  assert all(new[key][k]==value for k,value in old[key].items())


def test_real_http_new_views_deny_owner_export_foreign_scope_and_hidden_research(actor,web):
 for scope,key in [('uk','cyber-resilience'),('banking','provider-oversight'),('lloyds','funding-base')]:
  route=v.SCOPES[scope]['route'];status,html,_=web(route+'?agenda='+key,authenticated=False)
  assert status==200 and web.last_headers['Cache-Control']=='no-store'
  assert all(t not in html for t in ['canonical_acceptance','EAI1-REVIEW','Research gaps','Unknown','Next action','Recommended action','55.25'])
 for path in ['/flora/banking/research/gaps','/flora/banking/research/sources','/industries/banking/visual-specs']:
  assert web(path,authenticated=False)[0]==403 and web(path)[0]==200
 for path in ['/enterprises/lloyds?agenda=funding-base&workspace=other','/?agenda=cyber-resilience&export=all','/industries/banking?agenda=provider-oversight&source=private']:
  assert web(path,authenticated=False)[0]in {403,404}


def test_new_views_cannot_reach_private_owners_approval_or_pipeline(monkeypatch):
 from cios.applications.flora import offers,sales_pipeline
 from cios.applications.flora.memory.repository import EvidenceRepository,EnterpriseModelRepository
 from cios.applications.flora.blueprint_import.review import CandidateReviewService
 from cios.applications.flora.blueprint_import.promotion import CanonicalPromotionService
 def no(*args,**kwargs):raise AssertionError('Forbidden private/approval/write service')
 for obj,name in [(offers,'snapshot'),(offers,'assess_fit'),(sales_pipeline,'create_opportunity'),(EvidenceRepository,'get'),(EnterpriseModelRepository,'get'),(CandidateReviewService,'record_decision'),(CanonicalPromotionService,'approve_plan'),(CanonicalPromotionService,'execute_approved_plan')]:monkeypatch.setattr(obj,name,no)
 for scope in a.KEYS:
  for row in a.agenda(scope):
   assert not p.NON_CORE.search(row.title)and not p.NON_CORE.search(row.conclusion.text)
   for stream in v.SCOPES[scope]['streams']:assert v.render(v.SCOPES[scope]['route'],{'stream':[stream],'agenda':[row.key]})
