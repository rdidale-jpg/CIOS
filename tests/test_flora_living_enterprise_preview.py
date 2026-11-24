"""Optional public preview: live Source guards, real IAM and unchanged default."""
from copy import deepcopy
from hashlib import sha256
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import re

import pytest
from cios.applications.flora import living_enterprise_preview as preview
from cios.applications.flora import visual_streams as v, security
from cios.applications.flora.public_routes import public_request_target
from cios.applications.flora.security_store import digest
from tests.test_flora_security_repair_01b import authority, signed
from tests.test_flora_research_intelligence import web

pytestmark = pytest.mark.real_security_boundary


@pytest.fixture
def http(tmp_path, monkeypatch):
    from cios.applications.flora.web.app import FloraWebHandler
    monkeypatch.setenv('FLORA_DATA_DIR',str(tmp_path/'isolated-runtime'))
    monkeypatch.setenv('FLORA_ENVIRONMENT','development')
    monkeypatch.setenv('FLORA_AUTH_PROVIDER','local')
    monkeypatch.setenv('FLORA_TRUST_PROXY_HEADERS','0')
    server=ThreadingHTTPServer(('127.0.0.1',0),FloraWebHandler)
    worker=Thread(target=server.serve_forever,daemon=True);worker.start()
    def request(target, method='GET',headers=None):
        connection=HTTPConnection('127.0.0.1',server.server_port,timeout=20)
        try:
            connection.request(method,target,headers=headers or {})
            response=connection.getresponse()
            return response.status,dict(response.getheaders()),response.read().decode()
        finally:connection.close()
    yield request
    server.shutdown();server.server_close();worker.join(2)


@pytest.mark.parametrize('stream',preview.REGIONS)
def test_three_layers_twelve_live_selections_and_same_original_art(stream):
    for focus,label,*_ in preview.REGIONS[stream]:
        html=preview.render({'stream':[stream],'focus':[focus]})
        assert '<h1>'+label.replace('&','&amp;')+'</h1>' in html
        assert html.count('data-region-key=')==4 and html.count('aria-current="true"')==1
        assert html.count('data-region="')==3
        assert 'Experimental design' in html and 'Return to current experience' in html
        assert preview.ART in html and 'Preview New Experience' not in html
        assert '<details' not in html.split('<main ',1)[1] and '.pdf' not in html and 'Reading mode' not in html
        if stream=='landscape':
            assert '£502.8bn' in html and '£6.6bn' in html and 'SWOT quadrants' not in html
        elif stream=='inside':
            assert '£502.8bn' not in html and '£6.6bn' not in html and 'SWOT quadrants' not in html
        else:assert html.count('id="llf-swot-')==8


def test_preview_is_optional_and_preserves_existing_arrival_and_flagship():
    for query in ({},{'stream':['inside']},{'stream':['forces']},{'stream':['landscape'],'detail':['flagship']}):
        html=v.render('/enterprises/lloyds',query)
        assert html.count('Preview New Experience')==1
        assert 'data-preview="experimental-design"' not in html
        assert 'aria-label="Insight streams"' in html
    assert 'From funding to earnings' in v.render('/enterprises/lloyds',{})
    flagship=v.render('/enterprises/lloyds',{'stream':['landscape'],'detail':['flagship']})
    assert all(text in flagship for text in ('Overview','Explore','Investigate','SWOT quadrants'))
    for path in ('/industries/banking',v.EASYJET_ROUTE):
        assert 'Preview New Experience' not in v.render(path,{})


@pytest.mark.parametrize('query',[
    {'stream':['foreign']},{'focus':['private-run']},{'subject':['BK-ENT-003']},
    {'stream':['inside'],'focus':['funding']},{'stream':['landscape','inside']},
    {'focus':[]},{'focus':'retail'},{'subject':['']},{'workspace':['foreign']},
    {'analysis':['fi-private']},{'lens':['inspection']},{'selected':['natwest']},
])
def test_strict_view_state_cannot_be_used_as_identity_or_private_selector(query):
    with pytest.raises(ValueError):preview.render(query)


@pytest.mark.parametrize('suffix',[
    '?workspace=private','?analysis=fi-private','?lens=inspection','?selected=natwest',
    '?stream=inside&stream=forces','/../lloyds','%2fprivate','//private',
    '/snapshot','/export','/assets/preview.html','/assets/styles?workspace=private',
])
def test_finite_public_route_cannot_expand_to_snapshots_or_private_records(http,suffix):
    status,_,_=http(preview.PATH+suffix)
    assert not public_request_target(preview.PATH+suffix) and status==403


def test_guest_http_entry_assets_headers_head_and_no_write_route(http):
    status,headers,body=http('/enterprises/lloyds')
    assert status==200 and 'Preview New Experience' in body
    assert public_request_target(preview.PATH)
    status,headers,body=http(preview.PATH)
    assert status==200 and headers['Cache-Control']=='no-store'
    assert 'Experimental design' in body and 'Guest' in body
    assert http(preview.PATH,'HEAD')[0]==200
    assert http(preview.PATH,'HEAD')[1]['Cache-Control']=='no-store'
    assert http(preview.PATH+'?focus=private','HEAD')[0]==404
    assert http(preview.PATH+'?stream=foreign')[0]==404
    assert http(preview.PATH,'POST')[0]==403
    for name,(_,mime) in preview.FILES.items():
        path=preview.PATH+'/assets/'+name
        status,headers,body=http(path)
        assert status==200 and headers['Content-Type']==mime and headers['Cache-Control']=='no-store'
    for bad in ('../private','preview.html','styles?run=private'):
        with pytest.raises(ValueError):preview.asset(bad)


@pytest.mark.parametrize('flag',['withdrawn','revoked','owner_only','contradictory','stale','superseded'])
def test_source_restriction_removes_financials_marker_and_dependent_swot(monkeypatch,flag):
    data=deepcopy(v.current_data(v.Context('lloyds','landscape')))
    next(s for s in data['sources'] if s['id']=='PR-LBG-Q326')[flag]=True
    monkeypatch.setattr(v,'current_data',lambda ctx:data)
    landscape=preview.render({})
    assert '£502.8bn' not in landscape and '£6.6bn' not in landscape
    assert 'class="change-marker"' not in landscape
    assert 'Curve: acquisition reported complete' not in landscape
    forces=preview.render({'stream':['forces'],'focus':['renewal']})
    assert 'Curve · reported complete' not in forces and 'id="llf-swot-2"' not in forces
    assert 'id="llf-swot-0"' in forces


@pytest.mark.parametrize('field,value',[
    ('entity_scope','TSB Bank plc'),('reporting_period','Year ended 31 December 2025'),
    ('metric_unit','USD billion'),('kind','management_target'),
])
def test_group_figures_fail_closed_on_incompatible_scope_period_unit_or_kind(monkeypatch,field,value):
    data=deepcopy(v.current_data(v.Context('lloyds','landscape')))
    for claim in data['claims']:
        if claim['id'] in {'LBG-Q326-DEPOSITS','LBG-Q326-PROFIT'}:claim[field]=value
    monkeypatch.setattr(v,'current_data',lambda ctx:data)
    html=preview.render({})
    assert '£502.8bn' not in html and '£6.6bn' not in html


def test_withdrawal_rechecks_full_http_and_dependent_diagrams(monkeypatch,http):
    state={'withdrawn':False}
    original=v.current_data
    def source_data(ctx):
        data=deepcopy(original(ctx))
        if state['withdrawn']:
            for source in data['sources']:source['withdrawn']=True
        return data
    monkeypatch.setattr(v,'current_data',source_data)
    first=http(preview.PATH+'?stream=forces&focus=renewal')[2]
    assert 'Core renewal links the efficiency ambition' in first and 'Curve · reported complete' in first
    state['withdrawn']=True
    status,headers,second=http(preview.PATH+'?stream=forces&focus=renewal')
    assert status==200 and headers['Cache-Control']=='no-store'
    for text in ('Core renewal links the efficiency ambition','Efficiency ambition','Curve · reported complete','id="llf-swot-'):
        assert text not in second
    resilience=http(preview.PATH+'?stream=forces&focus=resilience')[2]
    assert 'Published March 2027 timetable' not in resilience
    assert 'event.persisted' in preview.asset('interactions')[0].decode()


@pytest.mark.parametrize('state',['guest','forged','owner','expired','revoked-membership'])
def test_public_preview_does_not_inherit_private_authority_or_financial_discovery(authority,tmp_path,monkeypatch,state):
    from cios.applications.flora.financial_intelligence import candidate_analytics, analyst
    from cios.applications.flora import document_review as review
    def forbidden(*args,**kwargs):raise AssertionError('Private financial service must not be called')
    monkeypatch.setattr(candidate_analytics,'find_existing_run',forbidden)
    monkeypatch.setattr(review,'load_run',forbidden)
    monkeypatch.setattr(analyst,'_selected_financial',forbidden)
    headers={}
    if state=='forged':headers={'X-Flora-Roles':'cios_owner','X-Flora-Workspace':'foreign'}
    if state in {'owner','expired','revoked-membership'}:
        store,token,_,headers,_=signed(authority,tmp_path)
        if state!='owner':
            with store.transaction() as db:
                if state=='expired':db.execute('UPDATE tokens SET expires=0 WHERE hash=?',(digest(token),))
                else:db.execute('UPDATE memberships SET active=0,version=version+1')
            assert security.verified_context(headers) is None
    before=preview.render({}).split('<main ',1)[1]
    after=preview.render({},headers).split('<main ',1)[1]
    assert before==after
    assert 'fi-private' not in after and 'primary_content_sha256' not in after
    assert candidate_analytics.public_factual_projection()=={}


def test_frame_is_never_monkey_patched_and_context_remains_navigation_only():
    from cios.applications.flora import visual_panels as panels
    left,top=panels._left,panels._top
    html=preview.render({'stream':['inside'],'focus':['credit'],'subject':['commercial']})
    assert panels._left is left and panels._top is top
    assert 'From Commercial Banking' in html and 'no divisional allocation is asserted' in html
    assert 'subject=commercial' in preview.href(preview.State('inside','credit','commercial'),stream='forces')


def test_exact_original_art_and_no_static_snapshot_in_application():
    root=Path(__file__).resolve().parents[1]
    art=root/'cios/applications/flora/visual_stream_assets'/ (preview.ART+'.webp')
    assert sha256(art.read_bytes()).hexdigest()=='13827db67c3077e5a390965499c38ec2a93d3003cde580895d86eac82140d80f'
    assert not (root/'cios/applications/flora/preview.html').exists()


def test_preview_compatibility_cut_is_exact_and_preserves_every_historical_cut():
    import ast
    import subprocess
    from tools.research import eei2b_compatibility as compatibility
    root=Path(__file__).resolve().parents[1]
    for path,(expected,functions) in compatibility.PREVIEW_CUTS.items():
        current=(root/path).read_bytes()
        assert sha256(current).hexdigest()==expected and functions==('_frame',)
        previous=compatibility.checked_cut(root,path,current,compatibility.PREVIEW_BASE,compatibility.PREVIEW_CUTS)
        assert previous==subprocess.check_output(['git','show',compatibility.PREVIEW_BASE+':'+path],cwd=root)
        mutation=current+b'\n# Unreviewed frame mutation\n'
        assert compatibility.checked_cut(root,path,mutation,compatibility.PREVIEW_BASE,compatibility.PREVIEW_CUTS)==mutation
    old=ast.parse(subprocess.check_output(['git','show',compatibility.PREVIEW_BASE+':tools/research/eei2b_compatibility.py'],cwd=root))
    for node in old.body:
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
            name=node.targets[0].id
            if name.endswith(('_BASE','_CUTS')) or name in {'BASE','CUTS'}:
                assert getattr(compatibility,name)==ast.literal_eval(node.value),name


def test_route_evolution_pins_are_exact_and_reject_unreviewed_bytes(monkeypatch):
    import ast
    import subprocess
    from tools.research import ux_unify_compatibility as compatibility
    root=Path(__file__).resolve().parents[1]
    read_bytes=Path.read_bytes
    for path,expected in compatibility.PREVIEW_ROUTE_PINS.items():
        target=root/path;current=target.read_bytes()
        assert sha256(current).hexdigest()==expected
        assert compatibility.predecessor(root,path)!=current
        mutation=current+b'\n# Unreviewed route mutation\n'
        with monkeypatch.context() as patch:
            patch.setattr(Path,'read_bytes',lambda self:mutation if self==target else read_bytes(self))
            assert compatibility.predecessor(root,path)==mutation
    old=ast.parse(subprocess.check_output(['git','show',compatibility.PREVIEW_ROUTE_BASE+':tools/research/ux_unify_compatibility.py'],cwd=root))
    for node in old.body:
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
            name=node.targets[0].id
            if name.isupper():assert getattr(compatibility,name)==ast.literal_eval(node.value),name
