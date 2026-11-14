"""Meaningful data-integrity and negative mutation checks; no research qualification engine."""
import copy
import pytest
from tools.research.rie1_617_validation import read,validate,check_sources,check_financials

def test_proposal_source_scope_ownership_and_financial_integrity():
 assert validate()['foundational_standards_met']==0

@pytest.mark.parametrize('field,value',[('rights',''),('extent',''),('geography',''),('reporting_period',''),('publication_date','2027-01-01'),('canonical_acceptance',True),('response_sha256','invented-original-byte-hash'),('url','https://example.org/?X-Amz-Signature=private')])
def test_source_loss_or_false_authority_is_rejected(field,value):
 sources=copy.deepcopy(read('Source-Ledger.json'));sources[0][field]=value
 with pytest.raises(AssertionError):check_sources(sources)

@pytest.mark.parametrize('change',['income','period','basis','deposit'])
def test_financial_basis_period_and_bridge_corruption_is_rejected(change):
 f=copy.deepcopy(read('Lloyds-Financial-Reconciliation.json'))
 if change=='income':f['underlying']['net_income'][0]+=1
 if change=='period':f['period']='Full year 2026'
 if change=='basis':f['statutory']['impairment']=f['underlying']['impairment'][:]
 if change=='deposit':f['deposit_changes_YTD_GBP_bn']['central_items']=0
 with pytest.raises(AssertionError):check_financials(f)

def test_negative_cases_keep_legal_programme_value_and_privacy_boundaries():
 n={x['id']:x for x in read('Negative-Cases.json')}
 assert {'NEG-TSB','NEG-FR','NEG-AI-VALUE','NEG-PROPERTY','NEG-HOUSEHOLD','NEG-PAYMENT'}<=set(n)
 assert n['NEG-FR']['status']=='blocked enterprise transmission'
 assert n['NEG-TSB']['preserved_history']=='Sprint B tiers and versioned facts unchanged.'
 assert n['NEG-AI-VALUE']['status']=='rejected value/intent inference'
 assert n['NEG-HOUSEHOLD']['status']=='no agenda'
 assert not any('LAND-L26'in a['source_refs']for a in read('Agenda-Candidates.json'))

def test_existing_import_contract_rehearsal(tmp_path):
 import runpy
 from pathlib import Path
 script=Path(__file__).resolve().parents[1]/'docs/flora-runtime/rie1-617/research-tools/import_dry_run.py'
 # Rehearsal publishes only its sanitized deterministic summary; fixture state is temporary.
 runpy.run_path(str(script),run_name='__main__')
