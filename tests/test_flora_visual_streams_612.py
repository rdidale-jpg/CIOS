"""VEX-1 integration: native scope navigation, public-source boundaries and assets."""
from copy import deepcopy
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import json
from http.client import HTTPConnection

import pytest
from tests.test_flora_security_repair_01b import authority, signed
from tests.test_flora_sales_pipeline import actor, web
from tests.test_flora_offers_v1 import pilot, draft
from cios.applications.flora import visual_streams as v, offers, sales_pipeline
from cios.applications.flora.public_routes import public_request_target, public_route_catalog
from cios.applications.flora.storage import data_path

class DOM(HTMLParser):
 def __init__(self,html):super().__init__();self.nodes=[];self.feed(html)
 def handle_starttag(self,t,a):self.nodes.append((t,dict(a)))

CASES=[(s,stream)for s,b in v.SCOPES.items()for stream in b['streams']]

@pytest.mark.parametrize('scope,stream',CASES)
def test_scope_identity_exact_native_streams_and_single_title(scope,stream):
 path=v.SCOPES[scope]['route'];query={'stream':[stream]}
 if scope!='uk':query.update(layer=['regulators'],selected=['lloyds'])
 ctx=v.resolve(path,query);html=v.render(path,query)
 assert html.count('<h1>')==1
 assert 'href="#visual-content"'in html and 'id="visual-content" tabindex="-1"'in html
 assert f'data-scope="{scope}"'in html and f'data-stream="{stream}"'in html
 nav=html.split('<nav class="stream-switcher"',1)[1].split('</nav>',1)[0]
 assert nav.count('aria-current="page"')==1
 for dest in v.SCOPES[scope]['streams']:
  expected=v.url(ctx,stream=dest,detail='').replace('&','&amp;')
  assert f'href="{expected}"'in nav
 assert 'Sources & method</summary>'not in html
 assert 'Primary product navigation'in html and 'Sources & detail</summary>'in html
 assert 'name="flora-header"'in html
 assert all(x not in nav for x in ('News','Topic Cards','Tools','<select','<button'))
 assert 'data-identity="'+('GB'if scope=='uk'else 'BK-IND-002'if scope=='banking'else 'BK-ENT-001')+'"'in html


def test_exact_accepted_seven_sources_and_only_responsive_current_scene_loaded():
 expected=json.loads((Path(__file__).parents[1]/'docs/flora-runtime/vex1-612/Accepted-Artwork.json').read_text())
 manifest=v.artwork();assert len(manifest['scenes'])==7
 for name,row in manifest['scenes'].items():
  assert row['original_sha256']==expected[name]
  for variant in row['variants']:
   raw,mime=v.asset(variant['file'].removesuffix('.webp'));assert mime=='image/webp'
   assert hashlib.sha256(raw).hexdigest()==variant['sha256']
   assert len(raw)==variant['bytes'] and variant['bytes']<row['original_bytes']
 for scope,stream in CASES:
  html=v.render(v.SCOPES[scope]['route'],{'stream':[stream]})
  images=[a for t,a in DOM(html).nodes if t=='img'];assert len(images)==2
  current=v.artwork()['scenes'][scope+'-'+stream]
  assert all(current['variants'][-1]['file'].removesuffix('.webp')in a['src']for a in images)
  assert all('768w'in a['srcset'] and '1152w'in a['srcset'] and '1536w'in a['srcset']for a in images)
  assert images[0]['fetchpriority']=='high' and images[1]['loading']=='lazy'
  assert 'width'in images[0]and'height'in images[0]
  assert not any('preload'in a.get('rel','')for t,a in DOM(html).nodes)


def test_twenty_original_labels_available_industries_and_two_selection_journey():
 html=v.render('/',{});dom=DOM(html)
 labels=[a for t,a in dom.nodes if 'data-sic'in a]
 assert len(labels)==20 and {a['data-sic']for a in labels}==set('ABCDEFGHIJKLMNOPQRST')
 links=[a for t,a in dom.nodes if 'data-research'in a]
 assert {a['data-research']for a in links}=={'banking','aviation','technology'}
 assert all(t=='span'for t,a in dom.nodes if 'data-sic'in a and 'data-research'not in a)
 assert all('available'in a['class']and'broader section'in a['aria-label']for a in links)
 bank=v.render('/industries/banking',{})
 for slug in v.BANKS:assert 'href="/enterprises/'+slug+'"'in bank
 assert v.resolve('/enterprises/lloyds',{}).stream=='inside'
 assert '/groups'not in bank and 'banking-groups'not in bank


@pytest.mark.parametrize('path,query',[
 ('/private',{}),('/',{'market':['FR']}),('/',{'market':['GB','FR']}),('/',{'stream':['inside']}),
 ('/',{'workspace':['foreign']}),('/',{'enterprise':['private']}),('/',{'selected':['lloyds']}),
 ('/',{'stream':['']}),('/',{'stream':['landscape','forces']}),('/',{'layer':['regulators']}),
 ('/industries/banking',{'selected':['private']}),('/industries/banking',{'stream':['inside']}),
 ('/industries/banking',{'detail':['<script>']}),('/industries/banking',{'layer':['foreign']}),
 ('/enterprises/lloyds',{'selected':['barclays']}),('/enterprises/lloyds',{'detail':['does-not-exist']}),
 ('/enterprises/lloyds',{'stream':['forces'],'detail':['technology']}),('/enterprises/lloyds',{'detail':['']}),
 ('/enterprises/lloyds',{'user':['owner']}),('/enterprises/private',{'stream':['inside']}),
])
def test_route_country_entity_duplicate_and_stream_abuse_fails_closed(path,query):
 with pytest.raises(ValueError):v.render(path,query,{'X-User':'owner','X-Workspace':'other','X-Roles':'cios_owner'})


@pytest.mark.parametrize('scope,stream',CASES)
def test_every_interactive_detail_is_server_addressable_without_js(scope,stream):
 path=v.SCOPES[scope]['route']
 for spot in v.geometry()[scope+'-'+stream]['spots']:
  if stream=='landscape'and scope=='uk':continue
  if stream=='landscape'and scope=='banking'and spot['id']in v.BANKS:continue
  html=v.render(path,{'stream':[stream],'detail':[spot['id']]})
  assert 'id="insight" tabindex="-1" aria-labelledby="insight-title"'in html
  assert 'id="insight-title"'in html and 'aria-label="Close 'in html
  if stream=='forces':assert 'not a qualified Material Pressure'in html


def test_current_source_facts_targets_periods_and_truthful_unknowns():
 data=v.model.load_assessment();refs=['LBG-Q326-DEPOSITS','LBG-Q326-PROFIT','LBG-A2030-CIR']
 html=v.render('/enterprises/lloyds',{'detail':['economics']})
 for r in v.claim_rows(data,refs):
  assert r['id']in html and r['statement'].replace('<','&lt;')in html
  assert r['reporting_period']in html
 assert 'balance-sheet stock'in html and 'nine-month flow'in html and 'target'in html
 assert 'Finance &amp; insurance'in v.render('/industries/banking',{})
 assert 'Banking 8.1%'not in v.render('/industries/banking',{})
 for key,label in v.GAPS:assert key in html
 assert 'not actual premises'in html and 'Unknown current income/cost/growth'in html
 assert not any(x in html for x in ('verified buying intent','qualified opportunity','£2bn supplier budget'))


def test_only_source_supported_announced_supplier_link_is_visible():
 html=v.render('/enterprises/lloyds',{'stream':['landscape'],'detail':['technology']})
 data=v.model.load_assessment()
 assert any(r['verified']and r['object']=='SUP-GOOGLE'for r in data['relationships'])
 assert 'LBG-ENVOY-GOOGLE'in html and 'workshare'in html.lower()
 assert 'data-claim="LBG-VERTEX"'not in html  # Historical technology is not silently upgraded.
 assert 'not a supplier or customer relationship'in v.render('/industries/banking',{'detail':['barclays']})


def test_projection_uses_current_owner_not_frozen_design_facts(monkeypatch):
 original=v.model.load_assessment;data=original()
 claim=next(c for c in data['claims']if c['id']=='LBG-A2030-PLATFORMS')
 claim['statement']='Changed owner statement <script>must remain text</script>'
 monkeypatch.setattr(v.model,'load_assessment',lambda *a,**k:deepcopy(data))
 html=v.render('/enterprises/lloyds',{'stream':['forces'],'detail':['LBG-A2030-PLATFORMS']})
 assert 'Changed owner statement &lt;script&gt;'in html and '<script>must remain text</script>'not in html
 assert original()['claims']!=data['claims']


def test_no_private_owner_reads_no_matching_models_or_writes(monkeypatch,pilot):
 record=draft(pilot,name='PRIVATE VEX sentinel',evidence='PRIVATE VEX proof')
 before=offers._path().read_bytes()
 def no(*a,**k):raise AssertionError('Forbidden private owner or write')
 for name in ('snapshot','discover','save_offer','select_employer'):monkeypatch.setattr(offers,name,no)
 monkeypatch.setattr(sales_pipeline,'create_opportunity',no)
 from cios.applications.flora.enterprise_canvas.service import EnterpriseCanvasService
 monkeypatch.setattr(EnterpriseCanvasService,'get_canvas',no)
 from cios.applications.flora.blueprint_import import material_pressure
 import urllib.request
 monkeypatch.setattr(urllib.request,'urlopen',no)
 for headers in (None,pilot['seller'],pilot['outsider'],pilot['foreign'],{'X-User':'owner','X-Workspace':'other','X-Roles':'cios_owner'}):
  for scope,stream in CASES:
   html=v.render(v.SCOPES[scope]['route'],{'stream':[stream]},headers)
   assert 'PRIVATE VEX sentinel'not in html and record['id']not in html
 assert offers._path().read_bytes()==before
 assert not data_path('sales_pipeline','opportunities.json').exists()


def test_verified_account_context_revokes_and_never_caches_html(actor,web):
 store,token,csrf,headers=actor
 status,html,_=web('/enterprises/lloyds?stream=forces')
 assert status==200 and 'synthetic-workspace'in html and 'Switch workspace'in html
 assert web.last_headers['Cache-Control']=='no-store'
 store.logout(token,csrf)
 status,html,_=web('/enterprises/lloyds?stream=forces')
 assert status==200 and 'synthetic-workspace'not in html and 'Sign in'in html
 assert 'X-Workspace'not in html


@pytest.mark.parametrize('target',['/?workspace=private','/enterprises/private?stream=inside','/enterprises/BK-ENT-001?stream=inside','/visual-streams/assets/../security_store.py','/visual-streams/assets/artwork.json','/visual-streams/assets/scenes.json','/?stream=forces&stream=landscape'])
def test_unregistered_public_selectors_never_grant_access(target):
 assert not public_request_target(target)


def test_real_http_all_seven_states_and_permission_negatives(web):
 for scope,stream in CASES:
  target=v.url(v.Context(scope,stream))
  status,html,_=web(target,authenticated=False)
  assert status==200 and f'data-stream="{stream}"'in html
  assert web.last_headers['Cache-Control']=='no-store'
 for target in ('/?stream=unknown','/industries/banking?stream=inside','/enterprises/lloyds?selected=private','/enterprises/lloyds?lens=ecosystem&stream=inside'):
  assert web(target,authenticated=False)[0]in (403,404)
 assert web('/industries/banking?lens=pestle',authenticated=False)[0]==200
 assert web('/enterprises/lloyds?lens=ecosystem',authenticated=False)[0]==200
 assert web('/flora/offers',authenticated=False)[0]in (302,303,403)
 assert web('/flora/sales/pipeline',authenticated=False)[0]in (302,303,403)
 assert web('/digital-twins/BK-ENT-001/canvas',authenticated=False)[0]in (302,303,403)


def test_immutable_public_art_cache_is_separate_from_private_html(actor):
 from http.server import ThreadingHTTPServer
 from cios.applications.flora.web.app import FloraWebHandler
 import threading
 server=ThreadingHTTPServer(('127.0.0.1',0),FloraWebHandler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
 name=v.artwork()['scenes']['lloyds-inside']['variants'][0]['file'].removesuffix('.webp');path=v.ASSET_BASE+name
 def get(headers):
  c=HTTPConnection('127.0.0.1',server.server_port)
  try:c.request('GET',path,headers=headers);r=c.getresponse();return r.status,dict(r.getheaders()),r.read()
  finally:c.close()
 try:
  status,h,body=get({});assert status==200 and body==v.asset(name)[0]
  assert h['Cache-Control']=='public, max-age=31536000, immutable' and 'Set-Cookie'not in h
  assert get({'If-None-Match':h['ETag']})[0]==304
  auth=get(actor[3]);assert auth[2]==body and 'Set-Cookie'not in auth[1]
 finally:server.shutdown();server.server_close();thread.join(2)


def test_asset_traversal_and_symlinks_fail_closed(tmp_path,monkeypatch):
 for name in ('../web/app.py','artwork.json','scenes.json','private','uk-landscape.png'):
  with pytest.raises(ValueError):v.asset(name)
 (tmp_path/'streams.css').symlink_to(Path(__file__).resolve())
 monkeypatch.setattr(v,'ASSETS',tmp_path)
 with pytest.raises(ValueError):v.asset('styles')


def test_withdrawn_relationship_is_not_reinstated_from_retained_claim(monkeypatch):
 data=v.model.load_assessment()
 for edge in data['relationships']:edge['verified']=False
 monkeypatch.setattr(v.model,'load_assessment',lambda *a,**k:deepcopy(data))
 html=v.render('/enterprises/lloyds',{'stream':['landscape'],'detail':['technology']})
 assert 'Current supplier relationships require revalidation'in html
 assert 'data-claim="LBG-ENVOY-GOOGLE"'not in html


def test_frozen_captions_disappear_if_public_source_pins_change(monkeypatch):
 manifest=v.artwork();manifest['caption_source_pins']={p:'0'*64 for p in manifest['caption_source_pins']}
 monkeypatch.setattr(v,'artwork',lambda:deepcopy(manifest))
 html=v.render('/enterprises/lloyds',{'detail':['economics']})
 assert 'Halifax branches: 2027 plan'not in html
 assert 'data-claim="LBG-Q326-DEPOSITS"'in html  # Current owner facts still render.
