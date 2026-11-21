"""Corruption negatives for candidate identity, source extent and acceptance boundaries."""
import copy,json,os,subprocess,sys
from pathlib import Path
import pytest
from tools.research.ric1_validation import read,validate,check_sources,check_claims,check_excerpts,check_proposals,check_matrix,check_agendas,check_financial_controls
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'docs/flora-runtime/ric1'

def test_consolidated_pack_has_no_owner_acceptance_or_canonical_mutations():
 assert validate()['canonical_mutations']==0

@pytest.mark.parametrize('mutation',['rights','bytes','inspection','url','corroboration'])
def test_source_rights_original_extent_identity_and_no_false_corroboration(mutation):
 x=copy.deepcopy(read('Source-Ledger.json'))
 if mutation=='rights':x[0]['rights_acceptance']='owner approved'
 if mutation=='bytes':x[0]['original_bytes_sha256']='a'*64
 if mutation=='inspection':x[0]['inspections'][0]['record']['publication_date']='2026-11-16'
 if mutation=='url':x[0]['original_url']='https://example.com/?X-Amz-Signature=private'
 if mutation=='corroboration':x[0]['document_reference_count']=2
 with pytest.raises(AssertionError):check_sources(x)

@pytest.mark.parametrize('mutation',['period','value','entity','accepted'])
def test_original_findings_cannot_be_silently_rewritten(mutation):
 x=copy.deepcopy(read('Claim-Ledger.json'));r=x[0]
 if mutation=='period':r['record']['reporting_period']='2026'
 if mutation=='value':r['record']['value']+=1
 if mutation=='entity':r['record']['subject_scope']='Lloyds private tenant'
 if mutation=='accepted':r['canonical_acceptance']=True
 with pytest.raises(AssertionError):check_claims(x)

@pytest.mark.parametrize('field,value',[('text','Invented primary quote'),('primary_content_sha256','a'*64),('rights',''),('content_kind','verified_download')])
def test_excerpt_hash_is_not_original_byte_proof(field,value):
 x=copy.deepcopy(read('Reviewed-Excerpts.json'));x[0][field]=value
 with pytest.raises(AssertionError):check_excerpts(x)

@pytest.mark.parametrize('mutation',['entity','basis','period','value','signed_expense','approval','private_join','compound'])
def test_atomic_proposals_preserve_financial_identity_and_owner_gate(mutation):
 x=copy.deepcopy(read('Observation-Proposals.json'));r=next(a for a in x if a['metric']=='operating_costs')
 if mutation=='entity':r['scope']='Lloyds Bank PLC'
 if mutation=='basis':r['accounting_basis']='statutory'
 if mutation=='period':r['period_start']='2026-04-01'
 if mutation=='value':r['value']=2873
 if mutation=='signed_expense':r['value']=abs(r['value'])
 if mutation=='approval':r['owner_evidence_acceptance']=True
 if mutation=='private_join':r['canonical_entity_id']='private-lloyds'
 if mutation=='compound':r['statement']='Income rose; costs fell.'
 with pytest.raises(AssertionError):check_proposals(x)

@pytest.mark.parametrize('identifier,classification',[('RIE1:LAND-L26-F1','A'),('NEG-IPSOS-LABEL','A'),('USE-COMPOUND-PROMOTION','A'),('LBG-A1','A')])
def test_unverified_interpretive_and_forbidden_records_cannot_enter_acceptance_slice(identifier,classification):
 x=copy.deepcopy(read('Evidence-Acceptance-Matrix.json'));next(r for r in x if r['id']==identifier)['class']=classification
 with pytest.raises(AssertionError):check_matrix(x)

def test_issue_version_history_does_not_inflate_current_agenda():
 x=copy.deepcopy(read('Strategic-Agendas.json'));x.append(copy.deepcopy(x[-1]))
 with pytest.raises(AssertionError):check_agendas(x)
 x=copy.deepcopy(read('Strategic-Agendas.json'));next(r for r in x if r['id']=='LBG-A1')['versions'][-1]['record']['buyer_need']='confirmed'
 with pytest.raises(AssertionError):check_agendas(x)

def test_existing_financial_definition_and_customer_cohort_negative_checks():
 ns=check_financial_controls()
 from tools.research.ric1_validation import original
 finance=original('RIE2','Financial-Reconciliation.json');finance['statutory_bridges']['H12026']['statutory_to_underlying']['impairment']=[0,0,0]
 with pytest.raises(AssertionError):ns['check_finance'](finance)
 outcomes=original('RIE2','Customer-Outcomes.json');outcomes['fos']['period_start']='2026-01-01'
 with pytest.raises(AssertionError):ns['check_outcomes'](outcomes)
 outcomes=original('RIE2','Customer-Outcomes.json');outcomes['survey']['scores_admitted']=[{'bank':'Lloyds','score':63}]
 with pytest.raises(AssertionError):ns['check_outcomes'](outcomes)

def test_actual_proposed_payload_rehearses_current_contracts_without_approval_or_cross_tenant_access():
 result=subprocess.run([sys.executable,str(D/'research-tools/import_dry_run.py')],cwd=ROOT,text=True,capture_output=True)
 assert result.returncode==0,result.stderr
 x=json.loads(result.stdout);assert x==read('Import-Dry-Run.json')
 assert x['canonical_mutations']==x['approvals_created']==x['reviews_created']==0
 assert x['cross_workspace_inspection_denied']and x['cross_workspace_planning_denied']

def test_standalone_report_does_not_require_pythonpath():
 env=dict(os.environ);env.pop('PYTHONPATH',None)
 result=subprocess.run([sys.executable,str(ROOT/'tools/research/ric1_validation.py')],cwd=ROOT,env=env,text=True,capture_output=True)
 assert result.returncode==0,result.stderr
 assert json.loads(result.stdout)['production_acceptance']=='UNVERIFIED'

def test_consolidation_reproduces_bytes_without_touching_runtime():
 files=[p for p in D.glob('*.json')if p.name not in ['Import-Dry-Run.json']]+[D/'Proposed-Records.ndjson']
 before={p:p.read_bytes()for p in files}
 result=subprocess.run([sys.executable,str(D/'research-tools/consolidate.py')],cwd=ROOT,text=True,capture_output=True)
 assert result.returncode==0,result.stderr
 assert all(p.read_bytes()==b for p,b in before.items())

def test_existing_visual_publisher_policy_is_preserved_and_blockers_are_explicit():
 from cios.applications.flora.research_intelligence.source_import import official_url
 aliases=read('Source-Aliases.json');sources={s['id']:s for s in read('Source-Ledger.json')}
 for identifier in ['R2-LBG-H126','ONS-GDP-SEP26']:
  with pytest.raises(ValueError):official_url(sources[aliases[identifier]]['original_url'])
 assert official_url(sources[aliases['R2-FCA-H126']]['original_url']).startswith('https://www.fca.org.uk/')
 matrix={m['id']:m for m in read('Evidence-Acceptance-Matrix.json')}
 assert matrix['USE-UNAPPROVED-VISUAL-PUBLISHER']['class']=='E'
