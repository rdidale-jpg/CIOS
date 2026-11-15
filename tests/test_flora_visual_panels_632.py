"""VP-2 integration: accepted assets, all routes, current sources and real IAM."""
from copy import deepcopy
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.parse import parse_qs, urlsplit

import pytest
from cios.applications.flora import visual_streams as v, visual_panels as panels
from cios.applications.flora import intelligence_presentation as p, leadership_agenda as agenda
from cios.applications.flora.public_routes import public_request_target
from tests.test_flora_sales_pipeline import actor, web
from tests.test_flora_offers_v1 import pilot, draft
from tests.test_flora_security_repair_01b import authority, signed

ROOT=Path(__file__).resolve().parents[1]
BASE='8a53777d1dec359f56b66e533d512c0a86881939'
DESIGN='f4059a34a55277adbd2a2337239827cab96d962e'
MATRIX=json.loads((ROOT/'docs/flora-runtime/vp2-632/Retained-Destinations.json').read_text())
CASES=[(s,t)for s,b in v.SCOPES.items()for t in b['streams']]

class DOM(HTMLParser):
 def __init__(self,text):super().__init__();self.nodes=[];self.feed(text)
 def handle_starttag(self,t,a):self.nodes.append((t,dict(a)))


@pytest.mark.parametrize('scope,stream',CASES)
def test_three_named_regions_current_role_and_single_header_h1(scope,stream):
 html=v.render(v.SCOPES[scope]['route'],{'stream':[stream]})
 dom=DOM(html);regions=[(t,a['data-region'])for t,a in dom.nodes if 'data-region'in a]
 assert regions==[('header','top'),('aside','left'),('main','main')]
 assert sum(t=='header'for t,a in dom.nodes)==1
 assert sum(t=='h1'for t,a in dom.nodes)==1
 assert '>Guest</span>'in html and 'Current account role'in html
 assert 'prototype/'not in html and 'SnapshotDate'not in html
 nav=html.split('aria-label="Insight streams"',1)[1].split('</nav>',1)[0]
 assert all(x not in nav for x in ['News','Topic Cards','Tools'])
 assert nav.count('aria-current="page"')==1
 assert '/flora/offers'in html and '/flora/sales/pipeline'in html
 assert 'Source supported'not in nav


@pytest.mark.parametrize('item',MATRIX['entries'],ids=lambda r:r['scene']+'-'+r['id'])
def test_every_original_label_active_destination_and_inert_boundary(item):
 ctx=v.Context(item['scope'],item['stream']);data=v.current_data(ctx)
 row=next(r for r in v.destinations(ctx,data)if r['id']==item['id'])
 assert (row['label'],row['href'])==(item['label'],item['href'])
 html=v.render(v.SCOPES[item['scope']]['route'],{'stream':[item['stream']]})
 assert item['label'].replace('&','&amp;')in html
 matches=[(tag,a)for tag,a in DOM(html).nodes if a.get('data-label-id')==item['id']]
 assert matches
 assert all(tag==('a'if item['active']else'span')for tag,a in matches)
 assert all(a.get('href','')==item['href'].replace('&amp;','&')for tag,a in matches)


def test_matrix_counts_full_fifty_one_labels_thirty_two_destinations():
 assert MATRIX['labels']==51 and MATRIX['active_destinations']==32
 assert len(MATRIX['entries'])==51 and sum(r['active']for r in MATRIX['entries'])==32
 assert {r['id']for r in MATRIX['entries']if r['scene']=='uk-landscape'}=={'uk-sic07-'+c.lower()for c in 'ABCDEFGHIJKLMNOPQRST'}


def test_exact_accepted_derivatives_selective_import_and_originals_retained():
 data=panels.asset_manifest();assert data['design_commit']==DESIGN and len(data['files'])==23
 assert len(data['portraits'])==7 and len(data['watermarks'])==7
 for key,row in data['files'].items():
  raw,mime=v.asset(key)
  assert mime==row['mime']and hashlib.sha256(raw).hexdigest()==row['sha256']
  original=subprocess.check_output(['git','show',DESIGN+':'+row['design_path']],cwd=ROOT)
  assert raw==original
 for path in ['artwork.json','scenes.json']:
  file='cios/applications/flora/visual_stream_assets/'+path
  assert (ROOT/file).read_bytes()==subprocess.check_output(['git','show',BASE+':'+file],cwd=ROOT)
 for scene,row in v.artwork()['scenes'].items():
  raw=subprocess.check_output(['git','show',v.DESIGN+':'+row['original_path']],cwd=ROOT)
  assert hashlib.sha256(raw).hexdigest()==row['original_sha256']
  for r in row['variants']:assert hashlib.sha256(v.asset(r['file'].removesuffix('.webp'))[0]).hexdigest()==r['sha256']


@pytest.mark.parametrize('target',['/visual-streams/assets/panels-artwork.json','/visual-streams/assets/../security_store.py','/visual-streams/assets/vp2-unknown','/visual-streams/assets/../../private.json','/?panel=private','/enterprises/private?stream=inside'])
def test_no_generic_asset_or_parallel_router(target):
 assert not public_request_target(target)


@pytest.mark.parametrize('change',['byte','symlink','manifest_path'])
def test_asset_tampering_and_symlink_fail_closed(tmp_path,monkeypatch,change):
 manifest=panels.asset_manifest();key=next(iter(manifest['files']));row=manifest['files'][key]
 (tmp_path/'artwork.json').write_bytes((v.ASSETS/'artwork.json').read_bytes())
 if change=='manifest_path':manifest['files'][key]['file']='../'+row['file']
 (tmp_path/'panels-artwork.json').write_text(json.dumps(manifest))
 file=tmp_path/row['file']
 if change=='symlink':
  secret=tmp_path/'private-record';secret.write_text('PRIVATE_ART_SENTINEL');file.symlink_to(secret)
 elif change=='byte':file.write_bytes(b'changed unapproved asset')
 monkeypatch.setattr(v,'ASSETS',tmp_path);v.asset_files.cache_clear()
 try:
  with pytest.raises(ValueError):v.asset(key)
 finally:v.asset_files.cache_clear()


@pytest.mark.parametrize('source,stream,detail,expected',[
 ('inside','forces','technology','LBG-ENVOY-CONTROLS'),('forces','inside','LBG-A2030-PLATFORMS','technology'),
 ('forces','landscape','LBG-ENVOY-CONTROLS','technology'),('landscape','inside','technology','technology'),
 ('inside','forces','economics','LBG-A2030-CIR'),('inside','landscape','economics',''),
 ('inside','landscape','businesses',''),('landscape','inside','businesses',''),
 ('inside','forces','businesses','LBG-BRAND26-TIMING'),('inside','forces','governance',''),
 ('inside','landscape','operations',''),
])
def test_only_semantically_compatible_subject_survives_stream_change(source,stream,detail,expected):
 ctx=v.Context('lloyds',source,'regulators','lloyds',detail,'ai-benefits')
 target=v.stream_url(ctx,stream);u=urlsplit(target);q=parse_qs(u.query)
 if not expected:q.pop('detail',None)  # URL may carry empty before existing normalisation below.
 # Empty selectors never enter a public route.
 if not expected:assert 'detail='not in u.query
 restored=v.resolve(u.path,parse_qs(u.query))
 assert restored.detail==expected
 assert (restored.scope,restored.selected,restored.layer,restored.agenda)==('lloyds','lloyds','regulators','ai-benefits')


FLAGS=[('owner_only',True),('withdrawn',True),('retracted',True),('core_contradiction',True),
 ('freshness','stale'),('freshness','superseded'),('rights',{'status':'denied'}),('rights',{'status':'revoked'}),('rights',{'status':'unknown'}),('rights',None)]

@pytest.mark.parametrize('kind',['claim','source'])
@pytest.mark.parametrize('key,value',FLAGS)
def test_restricted_financial_input_never_enters_chart_or_hidden_html(monkeypatch,kind,key,value):
 data=deepcopy(v.model.load_assessment());claim=next(c for c in data['claims']if c['id']=='LBG-Q326-DEPOSITS')
 source=next(s for s in data['sources']if s['id']==claim['source_ids'][0]);row=claim if kind=='claim'else source
 row[key]=value
 if kind=='claim':claim['statement']='PRIVATE_REVOKED_FINANCIAL_SENTINEL';claim['metric_value']=123456789
 else:source['title']='PRIVATE_REVOKED_SOURCE_SENTINEL'
 monkeypatch.setattr(v.model,'load_assessment',lambda *a,**k:deepcopy(data))
 html=v.render('/enterprises/lloyds',{})
 assert '123456789'not in html and 'PRIVATE_REVOKED'not in html
 assert 'Customer-deposit stocks · Group'not in html
 assert 'deposit-reference'not in html


@pytest.mark.parametrize('key,value',FLAGS)
def test_restricted_macro_input_omitted_before_title_and_content(monkeypatch,key,value):
 original=v.visual_v2.insight
 def changed(name):
  data=deepcopy(original(name))
  if name=='technological':
   for source in data['sources']:source[key]=value;source['title']='PRIVATE_MACRO_SOURCE'
  return data
 monkeypatch.setattr(v.visual_v2,'insight',changed)
 html=v.render('/',{'stream':['forces']})
 assert 'PRIVATE_MACRO_SOURCE'not in html
 assert '<h2>Cyber resilience</h2>'not in html


@pytest.mark.parametrize('field,value',[
 ('entity_scope','NatWest Group plc'),('metric_unit','GBP million'),('metric_unit','percent'),
 ('reporting_period','Year ended 31 December 2026'),('kind','management_expectation'),
])
def test_financial_chart_rejects_wrong_entity_unit_period_or_target(monkeypatch,field,value):
 data=deepcopy(v.model.load_assessment());c=next(c for c in data['claims']if c['id']=='LBG-Q326-DEPOSITS');c[field]=value
 monkeypatch.setattr(v.model,'load_assessment',lambda *a,**k:deepcopy(data))
 html=v.render('/enterprises/lloyds',{})
 assert 'deposit-reference'not in html and 'Customer-deposit stocks · Group'not in html
 assert 'Reported · Group customer deposits'not in html


def test_wholly_private_release_denied_not_projected(monkeypatch):
 data=deepcopy(v.model.load_assessment());data['owner_only']=True;data['enterprise_name']='PRIVATE_ENTERPRISE_NAME'
 monkeypatch.setattr(v.model,'load_assessment',lambda *a,**k:deepcopy(data))
 with pytest.raises(ValueError,match='Public reference'):v.render('/enterprises/lloyds',{})


def test_changed_economy_source_not_republished_via_proof(monkeypatch):
 data=deepcopy(v.visual_v2.basis());data['sources'][0]['title']='PRIVATE_ECONOMY_SOURCE';data['growth']['value_pct']=98765
 monkeypatch.setattr(v.visual_v2,'basis',lambda:data)
 html=v.render('/',{})
 assert 'PRIVATE_ECONOMY_SOURCE'not in html and '98765'not in html
 assert 'Four comparable sector shares'not in html


def test_real_verified_owner_signout_forms_and_foreign_header_denial(actor,web):
 status,html,_=web('/enterprises/lloyds')
 assert status==200 and '>Owner</span>'in html and 'Switch workspace'in html
 assert 'synthetic-workspace'in html and any(t=='input'and a.get('name')=='csrf'and a.get('value')==actor[2]for t,a in DOM(html).nodes)
 assert web.last_headers['Cache-Control']=='no-store'
 assert web('/industries/banking?lens=pestle',authenticated=False)[0]==403
 assert web('/industries/banking?lens=pestle')[0]==200
 assert web('/enterprises/lloyds?workspace=foreign')[0]in {403,404}
 forged=v.render('/',{}, {'X-User':'owner','X-Workspace':'foreign','X-Roles':'cios_owner'})
 assert '>Guest</span>'in forged and 'synthetic-workspace'not in forged


def test_new_images_public_immutable_but_html_and_source_admin_not_cached(actor):
 from http.server import ThreadingHTTPServer
 from http.client import HTTPConnection
 import threading
 from cios.applications.flora.web.app import FloraWebHandler
 server=ThreadingHTTPServer(('127.0.0.1',0),FloraWebHandler)
 thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
 def read(target,headers=None):
  conn=HTTPConnection('127.0.0.1',server.server_port)
  try:
   conn.request('GET',target,headers=headers or {});r=conn.getresponse();return r.status,r.read(),dict(r.getheaders())
  finally:conn.close()
 try:
  key=next(k for k,r in panels.asset_manifest()['files'].items()if r['mime']=='image/webp')
  status,body,headers=read(v.ASSET_BASE+key)
  assert status==200 and body==v.asset(key)[0]
  assert headers['Cache-Control']=='public, max-age=31536000, immutable'
  assert headers['X-Content-Type-Options']=='nosniff'
  status,_,headers=read('/',actor[3]);assert status==200 and headers['Cache-Control']=='no-store'
  for target in ['/visual-streams/assets/panels-artwork.json','/flora/banking/research/gaps','/industries/banking/visual-specs','/?stream=news']:
   assert read(target)[0]in {403,404}
 finally:server.shutdown();server.server_close();thread.join(2)


def test_seller_private_offer_and_other_workspace_never_enter_public_panels(monkeypatch,pilot):
 record=draft(pilot,name='PRIVATE_VP2_OFFER_SENTINEL',evidence='PRIVATE_VP2_PROOF')
 from cios.applications.flora import offers,sales_pipeline
 before=offers._path().read_bytes()
 def forbidden(*a,**k):raise AssertionError('Private owner/writer reached by visual view')
 for name in ['snapshot','discover','save_offer','select_employer']:monkeypatch.setattr(offers,name,forbidden)
 monkeypatch.setattr(sales_pipeline,'create_opportunity',forbidden)
 from cios.applications.flora.memory.repository import EvidenceRepository,EnterpriseModelRepository
 monkeypatch.setattr(EvidenceRepository,'get',forbidden);monkeypatch.setattr(EnterpriseModelRepository,'get',forbidden)
 for headers in [pilot['seller'],pilot['outsider'],pilot['foreign'],None]:
  for scope,stream in CASES:
   html=v.render(v.SCOPES[scope]['route'],{'stream':[stream]},headers)
   assert 'PRIVATE_VP2'not in html and record['id']not in html
 assert offers._path().read_bytes()==before


def test_no_pending_evidence_source_or_frozen_design_data_dependency():
 for file in ['Assessment-Overlay.json','Understanding-Review.json']:
  path='enterprise-knowledge/banking/research-model/'+file
  assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
 for scope,stream in CASES:
  html=v.render(v.SCOPES[scope]['route'],{'stream':[stream]})
  assert all(s not in html for s in ['EAI1-REVIEW','£130m','£129m','£1m','£212bn','SnapshotDate','canonical_acceptance','data-claim='])
  assert 'Future concept'not in html


def test_unimplemented_stream_still_rejected_by_existing_resolver():
 with pytest.raises(ValueError):v.render('/',{'stream':['news']})


def test_external_supplier_visibility_retains_existing_verified_relationship_gate(monkeypatch):
 data=deepcopy(v.model.load_assessment())
 for relation in data['relationships']:
  if relation['object']=='SUP-GOOGLE':relation['verified']=False
 monkeypatch.setattr(v.model,'load_assessment',lambda *a,**k:deepcopy(data))
 html=v.render('/enterprises/lloyds',{'stream':['landscape']})
 assert 'Google Cloud'not in html
 assert not next(r for r in v.destinations(v.Context('lloyds','landscape'),data)if r['id']=='technology')['href']


@pytest.mark.parametrize('scope,stream',[('banking','landscape'),('banking','forces'),('lloyds','inside'),('lloyds','landscape'),('lloyds','forces')])
@pytest.mark.parametrize('layer',['regulators','suppliers'])
def test_context_layers_keep_original_visible_emphasis_and_supplementary_disclosure(scope,stream,layer):
 ctx=v.Context(scope,stream,layer);rows=v.destinations(ctx,v.current_data(ctx))
 expected={r['id']for r in rows if (layer=='regulators'and(r['id']in v.ROLE_CONTEXT or r['id']=='economics'))or(layer=='suppliers'and r['id']in {'technology','customers','operations','payments'})}
 html=v.render(v.SCOPES[scope]['route'],{'stream':[stream],'layer':[layer]})
 actual={a['data-label-id']for t,a in DOM(html).nodes if 'layer-focus'in a.get('class','')}
 assert actual==expected
 assert all('aria-description'in a for t,a in DOM(html).nodes if 'layer-focus'in a.get('class',''))
 css=(v.ASSETS/'panels.css').read_text()
 assert '.subject.layer-focus'in css and '.exploration-link.layer-focus'in css


@pytest.mark.parametrize('key',['technological','legal','environmental'])
def test_uk_force_uses_source_reporting_scope_not_bare_review_date(key):
 fact=v.force_view(v.Context('uk','forces'),key,None);row=v.visual_v2.insight(key)
 assert fact.period!=row['lineage']['as_of']
 assert any(source.get('reporting_period','')in fact.period for source in row['sources']if source.get('reporting_period'))
 if key=='technological':
  assert 'August–December 2025'in fact.period
  assert fact.sources[0].published=='2026-04-30'


def test_unavailable_financial_topic_does_not_get_a_selected_detail_wrapper(monkeypatch):
 data=deepcopy(v.model.load_assessment())
 for c in data['claims']:
  if c['id']in {'LBG-Q326-DEPOSITS','LBG-Q326-PROFIT','LBG-A2030-CIR'}:c['owner_only']=True
 monkeypatch.setattr(v.model,'load_assessment',lambda *a,**k:deepcopy(data))
 html=v.render('/enterprises/lloyds',{'stream':['inside'],'detail':['economics']})
 assert 'id="insight"'not in html
