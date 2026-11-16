"""ISP-1 semantics, authority orthogonality, information-flow and real HTTP tests."""
from dataclasses import replace
from decimal import Decimal
from copy import deepcopy
from pathlib import Path
import hashlib,json
from html.parser import HTMLParser
import pytest
from cios.applications.flora import intelligence_presentation as p,visual_streams as v
from cios.applications.flora.public_routes import public_request_target,owner_inspection_request_target
from tests.test_flora_sales_pipeline import actor,web
from tests.test_flora_security_repair_01b import authority,signed

# Isolated policy examples only. No company/Observation/Evidence import.
SOURCE=p.Source('Example method, not company research','https://example.com/method','Example publisher','2026-01-01')
def reported(**changes):
 return replace(p.Statement('Example reported movement was 130.','reported','Example unit','H1 2026',(SOURCE,),
                'reported_source','candidate',measurement_state='actual',basis='same example definition',value=Decimal(130),unit='GBP million'),**changes)

@pytest.mark.parametrize('quality',['reported_source','reviewed_excerpt','verified_original'])
@pytest.mark.parametrize('canonical',['candidate','accepted','not_assessed'])
def test_type_verification_and_acceptance_are_independent(quality,canonical):
 item=reported(verification=quality,canonical_status=canonical)
 assert p.eligible(item)and item.semantic_type=='reported'
 html=p.render(item);assert 'Reported: 'in html and canonical not in html
 assert 'data-semantic-type="reported"'in html

@pytest.mark.parametrize('kind',['estimated','assumed'])
def test_calculation_retains_uncertain_input_chain_and_never_becomes_reported(kind):
 left=reported(semantic_type=kind,method='Example measured range',caveats=('Illustrative input range, not company data.',),assumption_owner='Example model owner',assumption_version='example-v1')
 right=reported(text='Example second movement was 129.',value=Decimal(129))
 result=p.difference(left,right,text='Difference between the two example movements is 1.')
 assert result.value==Decimal(1)and result.semantic_type=='calculated'and kind in result.dependency_types
 assert p.eligible(result)and 'Depends on'in p.render(result)
 assert not p.eligible(replace(result,semantic_type='reported'))
 # Transitive assumptions survive another calculation.
 chained=p.difference(result,right,text='Second illustrative difference.')
 assert kind in chained.dependency_types and 'Depends on'in p.render(chained)

@pytest.mark.parametrize('field,value',[('scope','Another legal entity'),('period','FY 2025'),('unit','GBP billion'),('basis','statutory'),('measurement_state','target'),('value',None)])
def test_incompatible_entity_period_unit_basis_or_target_inputs_rejected(field,value):
 left=reported();right=replace(left,**{field:value})
 with pytest.raises(ValueError):p.difference(left,right,text='Unsupported result.')

def test_owner_worked_example_is_test_only_not_leasing_profit():
 other=reported(text='Other income increased £130m.',scope='Lloyds Banking Group Retail reporting division')
 lease=replace(other,text='Lease depreciation increased £129m.',value=Decimal(129))
 calc=p.difference(other,lease,text='£1m difference between the reported movements. Not a leasing profit margin.')
 insight=replace(calc,semantic_type='insight',value=None,text='Higher lease depreciation offset most of the reported other-income improvement.',reasoning='Difference of the stated movements; no product-level profit computation.',counter_evidence=('Retail profit improved and existing mitigation was disclosed.',))
 hypo=replace(insight,semantic_type='hypothesis',text='Further asset-return improvements may be possible beyond disclosed mitigation.',falsifier='Product-level returns are satisfactory or existing mitigation exhausts the proposed improvement.')
 for item in (other,lease,calc,insight,hypo):assert p.eligible(item)
 assert p.render(insight).find('Retail profit improved')>=0
 assert p.render(hypo).find('Falsifier')>=0
 assert not p.eligible(replace(hypo,falsifier=''))
 assert not p.eligible(replace(insight,counter_evidence=()))
 # No RIE or RIC candidate is loaded by the production adapter.
 assert '130m'not in v.render('/enterprises/lloyds',{'detail':['economics']})

@pytest.mark.parametrize('text',['Unknown','Missing income','Research coverage is 90%.','Next action: engage.','Which buyer owns this?','Evidence needs validation.','Recommended action.'])
def test_backlogs_questions_recommendations_are_omitted_even_from_hidden_markup(text):
 item=reported(text=text)
 assert not p.eligible(item)and p.render(item)==''

@pytest.mark.parametrize('mutation',[{'owner_only':True},{'core_contradiction':True},{'freshness':'stale'},{'freshness':'superseded'},{'sources':()},{'value':Decimal('NaN')},{'semantic_type':'certain_fact'}])
def test_unsupported_withdrawn_or_internal_records_are_omitted(mutation):
 assert p.render(reported(**mutation))==''

def test_source_url_date_and_no_original_authority_fabrication():
 for s in [replace(SOURCE,url='javascript:alert(1)'),replace(SOURCE,url='https://secret:password@example.com/doc'),replace(SOURCE,published='2099-01-01')]:
  assert not p.eligible(reported(sources=(s,)))
 item=reported(canonical_status='PRIVATE_ACCEPTANCE_SENTINEL')
 assert 'PRIVATE_ACCEPTANCE_SENTINEL'not in p.render(item)

def test_real_owner_targets_dates_and_scope_are_retained():
 data=v.model.load_assessment();c=next(c for c in data['claims']if c['id']=='LBG-A2030-CIR')
 item=p.claim_view(data,c)
 assert item.semantic_type=='reported'and item.measurement_state=='target'
 assert item.canonical_status==data['authority']=='candidate_intelligence'
 assert item.scope==c['entity_scope']and item.period==c['reporting_period']
 assert 'Management target'in p.render(item)and 'not achieved'in p.render(item)
 assert p.claim_view(data,next(c for c in data['claims']if c['id']=='LBG-BPO-GAP'))is None

class Text(HTMLParser):
 def __init__(self,html):super().__init__();self.parts=[];self.feed(html)
 def handle_data(self,text):self.parts.append(text)


def test_all_scopes_streams_details_omit_owner_metadata_without_erasing_records(monkeypatch):
 data=v.model.load_assessment();original=deepcopy(data)
 data['gaps'].append({'id':'OWNER_GAP_SENTINEL','title':'OWNER_QUESTION_SENTINEL?'})
 data['owner_inspection']={'questions':['OWNER_ACTION_SENTINEL'],'coverage':'OWNER_PERCENT_SENTINEL'}
 data['sources'][0]['private_admin']='OWNER_RIGHTS_TASK_SENTINEL'
 monkeypatch.setattr(v.model,'load_assessment',lambda *a,**kw:deepcopy(data))
 for scope,b in v.SCOPES.items():
  for stream in b['streams']:
   keys=[None]+[s['id']for s in v.geometry()[scope+'-'+stream]['spots']if stream!='landscape'or scope=='lloyds']
   for key in keys:
    query={'stream':[stream]}
    if key:query['detail']=[key]
    html=v.render(b['route'],query)
    assert 'OWNER_'not in html
    assert not any(t in html for t in ('Research gaps','Still to establish','A useful next question','data-claim='))
    assert not any(k in html for k,label in v.GAPS)
 assert original['gaps']==data['gaps'][:-1]


def test_real_http_core_and_research_export_ownership_revocation_no_store(actor,web):
 # Existing fixture is a real authenticated owner, not an impersonated header.
 paths=['/flora/banking/research/gaps','/flora/banking/research/sources','/industries/banking/visual-specs','/enterprises/lloyds/research-diagnostic','/industries/banking?lens=pestle']
 for path in paths:
  assert not public_request_target(path)and owner_inspection_request_target(path)
  assert web(path,authenticated=False)[0]==403
  assert web(path)[0]==200
  assert web.last_headers['Cache-Control']=='no-store'
 # Downgrade verified membership in isolated storage; an existing session cannot retain owner reads.
 store=actor[0]
 with store.transaction()as db:db.execute('UPDATE memberships SET roles=?',(json.dumps(['seller']),))
 for path in paths:assert web(path)[0]==403
 assert web('/enterprises/lloyds?stream=inside')[0]==200
 assert web.last_headers['Cache-Control']=='no-store'
 for path in ['/industries/banking?lens=pestle&workspace=other','/flora/banking/research/gaps?search=OWNER','/industries/banking/visual-specs?export=all']:
  assert web(path)[0]in {403,404}


def test_no_owner_record_model_matcher_network_or_pipeline_reads_or_writes(monkeypatch):
 from cios.applications.flora import offers,sales_pipeline
 from cios.applications.flora.memory.repository import EvidenceRepository,EnterpriseModelRepository
 def no(*args,**kwargs):raise AssertionError('Forbidden owner/write call')
 for obj,name in [(EvidenceRepository,'get'),(EnterpriseModelRepository,'get'),(offers,'snapshot'),(offers,'assess_fit'),(sales_pipeline,'create_opportunity')]:
  monkeypatch.setattr(obj,name,no)
 for scope,b in v.SCOPES.items():
  for stream in b['streams']:assert v.render(b['route'],{'stream':[stream]})


def test_all_seven_original_artworks_and_responsive_variants_are_byte_identical():
 root=Path(__file__).resolve().parents[1]
 expected=json.loads((root/'docs/flora-runtime/vex1-612/Accepted-Artwork.json').read_text())
 for key,row in v.artwork()['scenes'].items():
  assert row['original_sha256']==expected[key]
  for variant in row['variants']:
   body,_=v.asset(variant['file'].removesuffix('.webp'))
   assert hashlib.sha256(body).hexdigest()==variant['sha256']


def test_pinned_intelligence_security_pipeline_and_baseline_owners_remain_unchanged():
 import subprocess
 root=Path(__file__).resolve().parents[1]
 manifest=json.loads((root/'docs/flora-runtime/isp1-623/Preserved-Owners-and-Artwork.json').read_text())
 assert manifest['base_sha']=='fe66516c15726dc45de147ede2674c9172f8cac6'
 for row in manifest['unchanged']:
  content=subprocess.check_output(['git','show',manifest['base_sha']+':'+row['path']],cwd=root)
  assert hashlib.sha256(content).hexdigest()==row['sha256'],row['path']
  from tests.flora_f2_owner_contract import assert_owner_compatible
  assert_owner_compatible(root,row['path'],content)


def test_six_factor_pestle_uses_same_policy_without_raw_lineage_or_action_copy():
 from cios.applications.flora import visual_v2
 for factor in visual_v2.FACTORS:
  html=visual_v2.render('/visual-v2/pestle',{'factor':[factor]})
  assert 'data-semantic-type="reported"'in html
  assert 'Commercial question'not in html and 'class="source-lineage"'not in html
  assert 'Trace critical services'not in html and 'Recheck parliamentary'not in html
