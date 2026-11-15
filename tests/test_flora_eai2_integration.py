"""EAI-2 adapts permitted candidate views to VP-2; no admission/approval."""
from copy import deepcopy
from datetime import date
from pathlib import Path
import hashlib,json,re,subprocess
import pytest
from cios.applications.flora import leadership_agenda as a,visual_panels as panels,visual_streams as v
from cios.applications.flora import intelligence_presentation as p
from cios.applications.flora.research_intelligence import registry,model
from tests.test_flora_sales_pipeline import actor,web
from tests.test_flora_security_repair_01b import authority,signed

ROOT=Path(__file__).resolve().parents[1]
BASE='ce4314c3528d5f4beae6e0e4fa53209ddb56ff5c'
EAI='678412a4320b5d13d88ffe66592e7a225cc4817c'
KEYS={'cyber':('uk','cyber-resilience'),'provider':('banking','provider-oversight'),'service':('lloyds','service-recovery')}

def release(key):
 domain,name,*_=a.EAI_RELEASES[key]
 return json.loads((registry.snapshot_boundary(domain)/name).read_text())

def changed_release(key,mutation,tmp_path,monkeypatch):
 data=release(key);source=data['source']
 if mutation=='rights':source['rights']['status']='revoked'
 elif mutation=='malformed_rights':source['rights']=None
 elif mutation=='private':source['owner_only']=True
 elif mutation=='stale':source['freshness']='stale'
 elif mutation=='withdrawn':source['withdrawn']=True
 elif mutation=='retracted':source['retracted']=True
 elif mutation=='contradiction':source['core_contradiction']=True
 elif mutation=='package_private':data['owner_only']=True
 elif mutation=='wrong_subject':data['subject_ref']='FOREIGN'
 elif mutation=='canonical_mutation':data['canonical_mutation']=True
 elif mutation=='source_host':source['url']='https://www.sec.gov/forged'
 domain,name,*_=a.EAI_RELEASES[key]
 if mutation!='missing':(tmp_path/name).write_text(json.dumps(data))
 pins=deepcopy(a._pins());pins['eai_releases'][key]=a.fingerprint(data)
 monkeypatch.setattr(a,'_pins',lambda:pins)
 original=registry.snapshot_boundary
 monkeypatch.setattr(registry,'snapshot_boundary',lambda d,repo=None:tmp_path if d==domain and repo is None else original(d,repo))

@pytest.mark.parametrize('scope,stream',[(s,t)for s,b in v.SCOPES.items()for t in b['streams']])
def test_three_regions_unchanged_exploration_and_singular_agenda_keys(scope,stream):
 ctx=v.Context(scope,stream);issues=a.agenda(scope);html=v.render(v.SCOPES[scope]['route'],{'stream':[stream]})
 assert len(issues)==len({r.key for r in issues})==(4 if scope=='banking'else 3)
 assert html.count('data-region=')==3 and html.count('<h1')==1
 assert html.count('aria-label="Leadership Agenda"')==1
 assert html.count('class="portrait"')==2
 for row in v.destinations(ctx,v.current_data(ctx)):
  assert row['label'].replace('&','&amp;')in html
  if row['href']:assert row['href'].replace('&','&amp;')in html
 assert all(t not in html for t in ['EAI1-REVIEW','Source-Admission-Review','research coverage','55.25%','£130m','£129m'])

@pytest.mark.parametrize('route,key,tokens',[
 ('/','cyber-resilience',['Estimated','43%','69%','August–December 2025','in line with the prior year']),
 ('/industries/banking','provider-oversight',['four named','13 July 2026','10 July','Microsoft Ireland Operations Limited']),
 ('/enterprises/lloyds','service-recovery',['118,762','118,861','66.12%','Lloyds Bank PLC','not independent adjudication']),
 ('/enterprises/lloyds','funding-base',['Calculated','£6.3bn','31 December 2025','30 September 2026','not an organic inflow']),
])
def test_four_bounded_additions_in_main_and_current_agenda(route,key,tokens):
 html=v.render(route,{})
 assert 'data-intelligence="'+key+'"'in html
 for token in tokens:assert token in html
 detail=v.render(route,{'agenda':[key]})
 assert 'id="agenda-insight"'in detail
 assert all(token in detail for token in tokens)

@pytest.mark.parametrize('key',KEYS)
@pytest.mark.parametrize('mutation',['rights','malformed_rights','private','stale','withdrawn','retracted','contradiction','package_private','wrong_subject','canonical_mutation','source_host','missing'])
def test_denied_release_removes_inline_title_links_and_dependent_numbers(key,mutation,tmp_path,monkeypatch):
 changed_release(key,mutation,tmp_path,monkeypatch)
 scope,agenda_key=KEYS[key];issues=a.agenda(scope);html=v.render(v.SCOPES[scope]['route'],{})
 if key=='service':
  row=next(r for r in issues if r.key==agenda_key)
  assert len(row.facts)==1 and '118,762'in row.conclusion.text
  assert row.title=='Complaint handling is a substantial service activity'
  assert html.count('id="preview-service-recovery"')==1
  assert '66.12%'not in html and '118,861'not in html
 else:
  assert agenda_key not in [r.key for r in issues]
  assert 'data-intelligence="'+agenda_key+'"'not in html
  assert 'agenda='+agenda_key not in html
  assert ('69%'if key=='cyber'else'Microsoft Ireland Operations Limited')not in re.sub(r'<[^>]+>','',html)

def test_existing_received_source_denial_omits_compound_outcomes_even_with_valid_new_release(tmp_path,monkeypatch):
 monkeypatch.setattr(a,'CANDIDATE',tmp_path/'absent.json')
 assert a._eai_release('service')
 assert 'service-recovery'not in [r.key for r in a.agenda('lloyds')]
 html=v.render('/enterprises/lloyds',{})
 assert '118,762'not in html and '66.12%'not in html
 assert '£502.8bn'in html and '£6.3bn'in html

@pytest.mark.parametrize('field,value',[('owner_only',True),('freshness','stale'),('core_contradiction',True)])
def test_private_or_ineligible_macro_composition_cannot_expand_cyber(field,value,monkeypatch):
 context=deepcopy(a.visual_v2.macro.load_context());context[field]=value
 monkeypatch.setattr(a.visual_v2.macro,'load_context',lambda:deepcopy(context))
 assert a._cyber_estimate()is None
 assert 'cyber-resilience'not in [r.key for r in a.agenda('uk')]

@pytest.mark.parametrize('scope',['banking','lloyds'])
@pytest.mark.parametrize('field,value',[('owner_only',True),('freshness','stale'),('withdrawn',True),('retracted',True),('core_contradiction',True)])
def test_whole_assessment_denial_blocks_existing_and_expanded_agenda(scope,field,value):
 data=deepcopy(model.load_assessment());data[field]=value
 assert a.agenda(scope,data)==()

@pytest.mark.parametrize('identifier',['LBG-AR25-DEPOSITS','LBG-Q326-DEPOSITS'])
def test_denied_deposit_input_omits_delta_and_retains_other_eligible_stock(identifier,monkeypatch):
 data=deepcopy(model.load_assessment())
 next(c for c in data['claims']if c['id']==identifier)['owner_only']=True
 monkeypatch.setattr(model,'load_assessment',lambda *args,**kwargs:deepcopy(data))
 html=v.render('/enterprises/lloyds',{})
 assert 'data-intelligence="funding-base"'not in html and '£6.3bn'not in html
 assert '£6.6bn'in html
 if identifier=='LBG-AR25-DEPOSITS':assert '£502.8bn'in html

def test_single_chart_and_single_delta_share_existing_qualifiers():
 html=v.render('/enterprises/lloyds',{'detail':['economics']})
 assert html.count('id="deposit-reference"')==1
 assert html.count('data-intelligence="funding-base"')==1
 assert 'composition' in html and 'two balance-sheet dates'in html
 assert '£130m'not in html and '£129m'not in html and 'leasing margin'not in html

def test_expired_review_omits_all_new_views_without_empty_preview_sections(monkeypatch):
 class Later(date):
  @classmethod
  def today(cls):return cls(2026,12,16)
 monkeypatch.setattr(a,'date',Later)
 for route in ['/','/industries/banking','/enterprises/lloyds']:
  html=v.render(route,{})
  assert 'data-intelligence='not in html
  text=re.sub(r'<[^>]+>','',html)
  assert '£6.3bn'not in text and '66.12%'not in text and '69%'not in text

def test_exact_eai_forms_sources_and_proposed_adr_preserved_without_approval():
 from tools.research.history_integrity import EAI1_CANDIDATE_ADDITIONS
 paths=list(EAI1_CANDIDATE_ADDITIONS)+[
  'docs/flora-runtime/eai1-628/Eight-Evidence-Review-Proposals.json',
  'docs/flora-runtime/eai1-628/Eight-Evidence-Reviews.md',
  'docs/flora-runtime/eai1-628/Source-Ledger.json',
  'architecture/decisions/ADR-027-Document-Scoped-Publisher-Admission-Proposal.md']
 for path in paths:assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show',EAI+':'+path],cwd=ROOT)
 forms=json.loads((ROOT/paths[-4]).read_text());assert len(forms)==8
 assert all(f['owner_decision_form']['selected']is None and not f['owner_decision_form']['import_executed']for f in forms)

def test_current_vp2_shell_assets_and_all_old_dependency_pins_preserved():
 for path in ['cios/applications/flora/visual_stream_assets/panels.css','cios/applications/flora/visual_stream_assets/panels-artwork.json','cios/applications/flora/visual_stream_assets/artwork.json','cios/applications/flora/visual_stream_assets/scenes.json','cios/applications/flora/visual_stream_assets/streams.js','cios/applications/flora/public_routes.py','cios/applications/flora/design_system.py','cios/applications/flora/web/app.py','cios/applications/flora/intelligence_presentation.py']:
  assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
 manifest=panels.asset_manifest()
 for key,row in manifest['files'].items():assert hashlib.sha256(v.asset(key)[0]).hexdigest()==row['sha256']
 pins=json.loads(subprocess.check_output(['git','show',BASE+':cios/applications/flora/visual_stream_assets/agenda-dependencies.json'],cwd=ROOT))
 now=a._pins()
 for group in ['claims','sources']:
  assert all(now[group][key]==value for key,value in pins[group].items())
 for key in ['existing_economy','existing_macro','candidate_proposal']:assert now[key]==pins[key]

@pytest.mark.parametrize('target',['/docs/flora-runtime/eai1-628/Eight-Evidence-Review-Proposals.json','/architecture/decisions/ADR-027-Document-Scoped-Publisher-Admission-Proposal.md','/visual-streams/assets/EAI1-FCA-Service-Candidate','/?workspace=foreign&agenda=cyber-resilience','/enterprises/lloyds?agenda=service-recovery&export=all'])
def test_owner_decision_material_and_private_exports_not_new_public_routes(target,actor,web):
 assert web(target,authenticated=False)[0]in {403,404}
