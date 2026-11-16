"""INT-1 source admission, agenda semantics, route isolation and owner continuity."""
from copy import deepcopy
from dataclasses import replace
from datetime import date
import hashlib,json,subprocess
from pathlib import Path
from urllib.parse import parse_qs,urlsplit
import pytest
from cios.applications.flora import leadership_agenda as a,intelligence_presentation as p,visual_streams as v
from cios.applications.flora.research_intelligence import model
from cios.applications.flora.research_intelligence.source_import import official_url,PUBLISHERS
from cios.applications.flora.public_routes import public_request_target
from tests.test_flora_sales_pipeline import actor,web
from tests.test_flora_security_repair_01b import authority,signed

ROOT=Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('scope',a.KEYS)
def test_same_agenda_across_lenses_preserves_issue_subject_selection_and_native_urls(scope):
 rows=a.agenda(scope);assert len(rows)==(4 if scope=='banking'else 3)  # BIE-2 adds one bounded Banking view.
 for stream in v.SCOPES[scope]['streams']:
  q={'stream':[stream],'agenda':[rows[0].key]}
  if scope!='uk':q.update(selected=['lloyds'],layer=['regulators'])
  ctx=v.resolve(v.SCOPES[scope]['route'],q)
  html=v.render(v.SCOPES[scope]['route'],q)
  assert 'id="agenda-insight" tabindex="-1"'in html
  assert html.count('aria-label="Leadership Agenda"')==1
  assert all(r.title in html for r in rows)
  for dest in v.SCOPES[scope]['streams']:
   target=v.url(ctx,stream=dest,detail='');parsed=urlsplit(target)
   assert public_request_target(target)
   selected=v.resolve(parsed.path,parse_qs(parsed.query))
   assert (selected.scope,selected.selected,selected.layer,selected.agenda)==(ctx.scope,ctx.selected,ctx.layer,ctx.agenda)

@pytest.mark.parametrize('path,key',[('/','service-recovery'),('/industries/banking','ai-benefits'),('/enterprises/lloyds','growth-mix'),('/enterprises/lloyds','private'),('/','<script>'),('/','')])
def test_cross_scope_empty_or_arbitrary_issue_never_resolves(path,key):
 with pytest.raises(ValueError):v.render(path,{'agenda':[key]})

@pytest.mark.parametrize('mutation',[
 ('claim','entity_scope','Lloyds Group'),('claim','asset_id','FOREIGN-PRIVATE'),
 ('claim','metric_value',999999),('claim','canonical_acceptance','accepted'),
 ('claim','verification','repository_reported'),('claim','freshness','stale'),
 ('claim','retracted',True),('source','url','https://www.sec.gov/fact'),
 ('source','publisher','Other issuer'),('source','publication_date','2099-01-01'),
 ('source','retrieval_url','https://www.ons.gov.uk/proxy'),
 ('source','rights',{'status':'revoked'}),('source','rights',{'status':'unknown'}),
 ('source','primary_content_sha256','f'*64),('source','withdrawn',True),
])
def test_source_claim_rights_status_dates_identity_or_release_change_removes_dependent_issue(mutation,tmp_path,monkeypatch):
 data=model.load_assessment();proposal=json.loads(a.CANDIDATE.read_text());kind,key,value=mutation
 row=proposal[kind]
 row[key]=value
 changed=tmp_path/'candidate.json';changed.write_text(json.dumps(proposal))
 monkeypatch.setattr(a,'CANDIDATE',changed)
 assert 'service-recovery'not in [r.key for r in a.agenda('lloyds',data)]
 assert 'ai-benefits'in [r.key for r in a.agenda('lloyds',data)]

@pytest.mark.parametrize('host',['www.sec.gov','www.ons.gov.uk','fca.org.uk.evil.example','www.fca.org.uk@evil.example'])
def test_restricted_publishers_have_no_new_import_exception(host):
 with pytest.raises(ValueError):official_url('https://'+host+'/source')
 assert 'www.sec.gov'not in PUBLISHERS and 'www.ons.gov.uk'not in PUBLISHERS

def test_numerical_source_original_entity_period_rights_and_unaccepted_authority():
 data=a._public_data(model.load_assessment());c=next(c for c in data['claims']if c['id']=='LBG-FCA-H126-RECEIVED');s=next(s for s in data['sources']if s['id']==c['source_ids'][0])
 assert model.primary_claim_supported(data,c)
 assert c['metric_value']==118762 and c['canonical_acceptance']=='not_accepted'
 assert c['entity_scope'].startswith('Lloyds Bank PLC only')and c['reporting_period']=='1 January–30 June 2026'
 assert s['primary_content_sha256']is None and s['content_kind']=='reviewed_web_excerpt'
 assert s['url']==s['retrieval_url']=='https://www.fca.org.uk/data/firm-level-complaints-data-sortable-table'
 assert s['rights']['terms_clause'].startswith('2.2')and s['rights']['permission_is_not_acceptance']
 assert s['rights']['extent'].startswith('One numerical row only')
 row=next(r for r in a.agenda('lloyds')if r.key=='service-recovery')
 assert row.facts[0].canonical_status=='candidate_intelligence'
 assert 'No deterioration' in p.render(row.conclusion) and 'FOS'in p.render(row.conclusion)
 assert '118,762'in row.conclusion.text and '66.12%'in row.conclusion.text
 assert '55.25%'not in p.render(row.conclusion)
 html=v.render('/enterprises/lloyds',{'agenda':['service-recovery']})
 assert 'Contains Financial Conduct Authority information licensed under the'in html
 assert 'href="https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"'in html

def test_no_h1_financial_proxy_or_unaccepted_eight_record_import():
 data=model.load_assessment();delta=json.loads((ROOT/'docs/flora-runtime/int1-625/Research-Owner-Delta.json').read_text())
 assert delta['new_claim']=='LBG-FCA-H126-RECEIVED'and delta['canonical_imports']==0
 for scope in a.KEYS:
  for row in a.agenda(scope):
   text=p.render(row.conclusion)+''.join(p.render(f)for f in row.facts)
   assert not any(x in text for x in ('130m','129m','£1m','Retail margin','SEC'))
   assert row.conclusion.semantic_type=='insight'
 assert all('sec.gov'not in s['url']and 'ons.gov.uk'not in s['url']for s in data['sources'])

def test_reported_expected_and_existing_capability_countercase_not_greenfield_or_budget():
 row=next(r for r in a.agenda('lloyds')if r.key=='ai-benefits')
 assert row.facts[0].value==50 and row.facts[1].value==100
 assert row.facts[1].measurement_state=='expectation'
 html=p.render(row.conclusion)+''.join(p.render(f)for f in row.facts)
 assert 'Management expectation'in html and 'not achieved net benefit'in html
 assert 'incumbents'in html and 'Google Cloud'in html
 assert all(not s.quote for f in row.facts for s in f.sources)  # No new issuer-prose republication.

def test_stale_editorial_review_and_changed_macro_or_economy_are_omitted(monkeypatch):
 class Later(date):
  @classmethod
  def today(cls):return cls(2026,12,16)
 monkeypatch.setattr(a,'date',Later)
 assert a.agenda('lloyds')==()and a.agenda('uk')==()
 monkeypatch.undo()
 original=a.visual_v2.basis
 changed=deepcopy(original());changed['growth']['value_pct']=99
 monkeypatch.setattr(a.visual_v2,'basis',lambda:changed)
 assert 'growth-mix'not in [r.key for r in a.agenda('uk')]

@pytest.mark.parametrize('contents',[None,'{broken JSON'])
def test_missing_or_unreadable_candidate_omits_service_without_hiding_existing_ai(tmp_path,monkeypatch,contents):
 path=tmp_path/'unavailable.json'
 if contents is not None:path.write_text(contents)
 monkeypatch.setattr(a,'CANDIDATE',path)
 assert [r.key for r in a.agenda('lloyds')]==['ai-benefits','funding-base']


def test_read_only_native_app_views_exclude_owner_metadata_hidden_sources_and_actions(monkeypatch):
 data=deepcopy(model.load_assessment());data['owner_only']={'question':'PRIVATE_RESEARCH_QUESTION?','coverage':'PRIVATE_COMPLETENESS','canonical_receipt':'PRIVATE_ACCEPTANCE'}
 data['gaps'].append({'id':'OWNER_SENTINEL','title':'OWNER_SENTINEL?'})
 monkeypatch.setattr(model,'load_assessment',lambda *args,**kwargs:deepcopy(data))
 for scope in a.KEYS:
  for row in a.agenda(scope,data):
   assert not p.NON_CORE.search(row.title)and not p.NON_CORE.search(row.conclusion.text)
   for stream in v.SCOPES[scope]['streams']:
    html=v.render(v.SCOPES[scope]['route'],{'stream':[stream],'agenda':[row.key]})
    assert not any(t in html for t in ('OWNER_SENTINEL','PRIVATE_RESEARCH','PRIVATE_COMPLETENESS','PRIVATE_ACCEPTANCE','Research gaps','Recommended action','Next question','data-claim='))
    assert row.conclusion.counter_evidence and 'Sources &amp; reasoning'in html

def test_real_http_issue_deep_links_are_public_but_inspection_exports_remain_owner_only(actor,web):
 for path in ['/?agenda=growth-mix','/industries/banking?agenda=funding-economics','/enterprises/lloyds?agenda=service-recovery&selected=lloyds']:
  status,html,_=web(path,authenticated=False)
  assert status==200 and 'agenda-insight'in html and web.last_headers['Cache-Control']=='no-store'
 for path in ['/flora/banking/research/sources','/flora/banking/research/gaps','/industries/banking/visual-specs']:
  assert web(path,authenticated=False)[0]==403 and web(path)[0]==200
 for target in ['/enterprises/lloyds?agenda=service-recovery&workspace=foreign','/enterprises/lloyds?agenda=service-recovery&export=all','/?agenda=growth-mix&agenda=public-value']:
  assert not public_request_target(target)
  assert web(target,authenticated=False)[0]in {403,404}

def test_all_prior_research_and_exact_artwork_manifest_and_caption_pins_unchanged():
 base='fe66516c15726dc45de147ede2674c9172f8cac6';path='cios/applications/flora/visual_stream_assets/artwork.json'
 old=json.loads(subprocess.check_output(['git','show',base+':'+path],cwd=ROOT));new=v.artwork()
 assert old['scenes']==new['scenes']and old['design_commit']==new['design_commit']
 assert old==new
 owner='enterprise-knowledge/banking/research-model/Assessment-Overlay.json'
 assert (ROOT/owner).read_bytes()==subprocess.check_output(['git','show',base+':'+owner],cwd=ROOT)
 assert (ROOT/'cios/applications/flora/visual_stream_assets/scenes.json').read_bytes()==subprocess.check_output(['git','show',base+':cios/applications/flora/visual_stream_assets/scenes.json'],cwd=ROOT)

def test_new_read_projection_cannot_invoke_existing_writers_or_private_owners(monkeypatch):
 from cios.applications.flora import offers,sales_pipeline
 from cios.applications.flora.memory.repository import EvidenceRepository,EnterpriseModelRepository
 def forbidden(*args,**kwargs):raise AssertionError('Writer/private owner reached')
 for obj,name in [(offers,'snapshot'),(offers,'assess_fit'),(offers,'save_offer'),(sales_pipeline,'create_opportunity'),(EvidenceRepository,'get'),(EnterpriseModelRepository,'get')]:monkeypatch.setattr(obj,name,forbidden)
 for scope in a.KEYS:
  for row in a.agenda(scope):assert v.render(v.SCOPES[scope]['route'],{'agenda':[row.key]})


@pytest.mark.parametrize('name',['INT1-FCA-Candidate.json','PR-FCA-COMPLAINTS-H126.txt'])
def test_history_guard_pins_each_new_candidate_byte_without_admitting_future_research(name):
 from tools.research.history_integrity import approved_history,compare_history,INT1_CANDIDATE_ADDITIONS
 assert len(INT1_CANDIDATE_ADDITIONS)==2
 path='enterprise-knowledge/banking/research-model/source-snapshots/'+name
 expected=approved_history(ROOT);actual=deepcopy(expected);actual[path]+=b' unreviewed change'
 with pytest.raises(AssertionError,match='Historical or approved source changed'):compare_history(expected,actual)
 actual=deepcopy(expected);actual['enterprise-knowledge/banking/research-model/source-snapshots/INT1-UNREVIEWED.json']=b'{}'
 with pytest.raises(AssertionError):compare_history(expected,actual)


def test_all_161_prior_history_expectations_and_comparator_are_exactly_preserved():
 import types,inspect
 from tools.research import history_integrity as current
 original=subprocess.check_output(['git','show','fe66516:tools/research/history_integrity.py'],cwd=ROOT).decode()
 historical=types.ModuleType('int1_historical_source_guard');exec(compile(original,'historical_source_guard','exec'),historical.__dict__)
 old=historical.approved_history(ROOT);new=current.approved_history(ROOT)
 assert len(old)==161 and len(new)==178
 assert {k:new[k] for k in old}==old
 assert set(new)-set(old)==set(current.INT1_CANDIDATE_ADDITIONS)|set(current.EAI1_CANDIDATE_ADDITIONS)|set(current.BIE2_CANDIDATE_ADDITIONS)|set(current.BIE3_CANDIDATE_ADDITIONS)|set(current.F1_CANDIDATE_ADDITIONS) | set(current.RUD1_ADDITIONS)
 # The byte comparator itself is untouched, not replaced by an exclusion.
 section=original.split('def compare_history(',1)[1].split('\n\ndef verify_history',1)[0]
 assert inspect.getsource(current.compare_history).split('def compare_history(',1)[1].strip()==section.strip()
