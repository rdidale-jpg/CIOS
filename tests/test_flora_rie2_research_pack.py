"""RIE2 data/lineage/basis corruption negatives and isolated current-contract rehearsal."""
import copy,runpy
from pathlib import Path
import pytest
from tools.research.rie2_619_validation import read,validate,check_sources,check_finance,check_outcomes,check_issues,check_comparability

def test_research_data_source_ownership_and_current_contract_integrity():
 assert validate()['canonical_mutations']==0

@pytest.mark.parametrize('field,value',[('rights',''),('scope',''),('reviewed_locator',''),('read_extent',''),('publication_date','2027-01-01'),('original_response_sha256','invented-byte-hash'),('canonical_acceptance',True),('url','https://example.org/?X-Amz-Signature=private')])
def test_missing_provenance_or_false_authority_is_rejected(field,value):
 s=copy.deepcopy(read('Source-Ledger.json'));s[0][field]=value
 with pytest.raises(AssertionError):check_sources(s)

@pytest.mark.parametrize('mutation',['segment','reported_total','period','basis','insurance','target'])
def test_financial_corruptions_are_rejected(mutation):
 f=copy.deepcopy(read('Financial-Reconciliation.json'))
 if mutation=='segment':f['periods'][0]['values']['net_income'][0]+=1
 if mutation=='reported_total':f['periods'][0]['values']['net_income'][4]+=1
 if mutation=='period':f['periods'][0]['duration_months']=6
 if mutation=='basis':f['periods'][0]['accounting_basis']='statutory'
 if mutation=='insurance':f['statutory_bridges']['H12026']['statutory_to_underlying']['impairment']=[0,0,0]
 if mutation=='target':f['targets_2030']['measurement_state']='actual'
 with pytest.raises(AssertionError):check_finance(f)

@pytest.mark.parametrize('mutation',['fos_period','consumer_credit_total','closure_denominator','entity','guessed_survey','escalation_ratio'])
def test_customer_period_product_entity_and_cohort_misjoins_are_rejected(mutation):
 x=copy.deepcopy(read('Customer-Outcomes.json'))
 if mutation=='fos_period':x['fos']['period_start']='2026-01-01'
 if mutation=='consumer_credit_total':x['complaints_received']=12308
 if mutation=='closure_denominator':x['complaints_upheld_by_firm_pct']=21.50
 if mutation=='entity':x['entity']='Lloyds Banking Group'
 if mutation=='guessed_survey':x['survey']['scores_admitted']=[{'bank':'Lloyds','score':63}]
 if mutation=='escalation_ratio':x['escalation_rate']=3764/118762
 with pytest.raises(AssertionError):check_outcomes(x)

@pytest.mark.parametrize('field,value',[('external_value',100000000),('buyer_need','confirmed'),('external_supplier_scope','open'),('potential_remaining_decision','OPEN')])
def test_public_research_cannot_be_relabelled_as_qualified_commercial_need(field,value):
 x=copy.deepcopy(read('Leadership-Agenda.json'));x[0][field]=value
 with pytest.raises(AssertionError):check_issues(x)

def test_cross_bank_profit_league_and_insurance_basis_are_rejected():
 x=copy.deepcopy(read('Banking-Comparability.json'));x['rows'][0]['financial_level_comparison']='ADMITTED efficiency rank'
 with pytest.raises(AssertionError):check_comparability(x)
 x=copy.deepcopy(read('Banking-Comparability.json'));x['additional_nonbank_example']['continuing_pbt'][0]=918
 with pytest.raises(AssertionError):check_comparability(x)

def test_existing_import_dry_run_stays_noncanonical_and_evidence_is_byte_stable():
 script=Path(__file__).resolve().parents[1]/'docs/flora-runtime/rie2-619/research-tools/import_dry_run.py'
 artifact=script.parents[1]/'Import-Dry-Run.json';before=artifact.read_bytes()
 runpy.run_path(str(script),run_name='__main__')
 assert artifact.read_bytes()==before


def test_standalone_report_works_without_pythonpath():
 import os,subprocess,sys,json
 root=Path(__file__).resolve().parents[1]
 env=dict(os.environ);env.pop('PYTHONPATH',None)
 result=subprocess.run([sys.executable,str(root/'tools/research/rie2_619_validation.py')],cwd=root,env=env,text=True,capture_output=True)
 assert result.returncode==0,result.stderr
 assert json.loads(result.stdout)['canonical_mutations']==0
