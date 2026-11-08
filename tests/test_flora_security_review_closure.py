"""PR 539 review closure; real production authority remains absent.

Synthetic stores and local HTTP only. The baseline is PR head 4c029a2, not main.
"""
import json
from hashlib import sha256
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
import threading
from urllib.parse import urlencode
import pytest
from cios.applications.flora import access, security
from cios.applications.flora.web import app

pytestmark=pytest.mark.real_security_boundary

@pytest.fixture(autouse=True)
def isolate(tmp_path,monkeypatch):
    root=tmp_path/'data';root.mkdir()
    monkeypatch.setenv('FLORA_DATA_DIR',str(root))
    from cios.applications.flora.enterprise_intelligence import pipeline,reasoning
    monkeypatch.setattr(pipeline.run_pipeline,'__defaults__',(tmp_path/'derived',None,None))
    monkeypatch.setattr(pipeline,'configured_reasoning_adapter',lambda:reasoning.DeterministicDevelopmentAdapter())
    for sub in ('memory','blueprint_import/packages','enterprise_canvas'):(root/sub).mkdir(parents=True,exist_ok=True)
    (root/'memory/evidence.jsonl').write_text(json.dumps({'evidence_id':'BK-OBS-014','quote':'SYNTHETIC_PRIVATE_MARKER'})+'\n')
    (root/'memory/private-model.json').write_text('{"enterprise_id":"private-model","name":"SYNTHETIC_PRIVATE_MARKER"}')
    (root/'blueprint_import/packages/private.json').write_text('{"name":"SYNTHETIC_PRIVATE_MARKER"}')
    return root

@pytest.fixture(scope='module')
def server():
    s=ThreadingHTTPServer(('127.0.0.1',0),app.FloraWebHandler)
    t=threading.Thread(target=s.serve_forever,daemon=True);t.start()
    try:yield s
    finally:s.shutdown();s.server_close();t.join()

def get(server,path,method='GET'):
    c=HTTPConnection('127.0.0.1',server.server_port,timeout=30)
    c.request(method,path,headers={'X-Flora-User':'untrusted','X-Flora-Roles':'cios_owner','X-Flora-Active-Workspace':'private-workspace'})
    r=c.getresponse();result=r.status,r.read().decode(errors='replace');c.close();return result

def hashes(root):
    return {str(p.relative_to(root)):sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file() and 'non_canonical_runtime_audit' not in p.parts}

BAD_PATHS=[
 '/evidence/private-canonical-id','/evidence/BK-OBS-014/extra','/evidence/../blueprint-import/history',
 '/evidence/%2e%2e/blueprint-import/history','/evidence/BK-OBS-014;ignored','/evidence/BK-OBS-014%2fextra',
 '/evidence//BK-OBS-014','/evidence/BK-OBS-014/','/flora/banking/private-model',
 '/flora/banking/lloyds/extra/briefing','/flora/banking/lloyds/../briefing',
 '/flora/banking/%6cloyds','/flora/banking/lloyds;ignored','/flora/banking/lloyds//briefing',
 '/flora/banking/lloyds/opportunity/private-canonical-id',
 '/flora/object/BK-ENT-001/lineage/unknown','/flora/object/BK-ENT-001/lineage/extra/CHG-LBG-001',
 '/flora/object/BK-ENT-001/lineage/CHG-LBG-001;ignored','//flora/banking',
 'http://untrusted.example/flora/banking','/flora/banking/lloyds%5c..',
]

@pytest.mark.parametrize('path',BAD_PATHS)
def test_unregistered_or_ambiguous_public_paths_deny_before_dispatch(server,path,isolate):
    before=hashes(isolate)
    status,body=get(server,path)
    assert status==403 and 'SYNTHETIC_PRIVATE_MARKER' not in body
    assert hashes(isolate)==before

@pytest.mark.parametrize('path',[
 '/intelligence?workspace_id=private-workspace','/digital-twins?run_id=private-run',
 '/flora/banking?enterprise_id=private-model','/intelligence?tab=industries&tab=enterprises',
 '/intelligence?tab=%ff','/intelligence?tab=%','/flora/banking?unknown',
 '/flora/object/BK-ENT-001/explain?question_id=private-question',
])
def test_ambiguous_or_resource_selecting_query_denied(server,path,isolate):
    before=hashes(isolate)
    status,body=get(server,path)
    assert status==403 and 'SYNTHETIC_PRIVATE_MARKER' not in body
    assert hashes(isolate)==before


def test_every_public_route_uses_declared_handler_without_private_reads(server,monkeypatch,isolate):
    from cios.applications.flora.memory.repository import EvidenceRepository,EnterpriseModelRepository
    from cios.applications.flora.blueprint_import.registry import BlueprintPackageRegistry
    from cios.applications.flora.enterprise_canvas.access import EnterpriseCanvasAccessRepository
    def forbidden(*a,**kw):pytest.fail('Public view read protected owner data')
    for cls,names in ((EvidenceRepository,('get','list')),(EnterpriseModelRepository,('get',)),(BlueprintPackageRegistry,('get','list')),(EnterpriseCanvasAccessRepository,('get','list'))):
        for name in names:monkeypatch.setattr(cls,name,forbidden)
    catalog=security.public_route_catalog()
    assert len(catalog)>70
    before=hashes(isolate)
    for path,route in catalog.items():
        seen=[]
        handler=getattr(app,route.handler,None)
        if callable(handler):
            def observed(*a,_handler=handler,**kw):seen.append(True);return _handler(*a,**kw)
            with monkeypatch.context() as patch:
                patch.setattr(app,route.handler,observed)
                status,body=get(server,path)
            assert seen,(path,route.handler)
        else:status,body=get(server,path)
        assert status==200,(path,status)
        assert 'SYNTHETIC_PRIVATE_MARKER' not in body,path
        assert route.source_boundary and route.query_keys is not None
    assert hashes(isolate)==before


def test_public_source_queries_cannot_select_canonical_records(server,monkeypatch,isolate):
    from cios.applications.flora.memory.repository import EvidenceRepository,EnterpriseModelRepository
    from cios.applications.flora.blueprint_import.registry import BlueprintPackageRegistry
    def forbidden(*a,**kw):pytest.fail('Public query selected protected data')
    for cls,name in ((EvidenceRepository,'get'),(EvidenceRepository,'list'),(EnterpriseModelRepository,'get'),(BlueprintPackageRegistry,'list')):monkeypatch.setattr(cls,name,forbidden)
    for path in ('/focus?'+urlencode({'enterprise':'private-model'}),'/shape?opportunity=private-model','/ask?'+urlencode({'question':'What is changing in banking for private-model?'}),'/evidence/BK-OBS-014'):
        status,body=get(server,path)
        assert status==200 and 'SYNTHETIC_PRIVATE_MARKER' not in body


def test_public_fingerprint_excludes_environment_configuration(server,monkeypatch,isolate):
    for key in ('RENDER_SERVICE_NAME','RENDER_GIT_REPO_SLUG','RENDER_BUILD_COMMAND','RENDER_START_COMMAND','FLORA_PILOT_OWNER_ID','FLORA_PILOT_WORKSPACE'):
        monkeypatch.setenv(key,'SYNTHETIC_PRIVATE_MARKER')
    monkeypatch.setenv('RENDER_GIT_COMMIT','SYNTHETIC_PRIVATE_MARKER')
    app.application_revision.cache_clear()
    try:
        status,body=get(server,'/deployment')
        assert status==200 and 'SYNTHETIC_PRIVATE_MARKER' not in body
        assert json.loads(body)['pilot_import_mode']=='disabled-security-repair-01a'
        for path in ('/digital-twins','/governance'):
            status,body=get(server,path)
            assert status==200 and 'SYNTHETIC_PRIVATE_MARKER' not in body
    finally:app.application_revision.cache_clear()

@pytest.mark.parametrize('path',['/evidence/private-id','/flora/banking/private-model','/flora/object/BK-ENT-001/lineage/unknown'])
def test_head_classification_matches_get(server,path):
    assert get(server,path,'HEAD')[0]==403


def test_verified_context_protocol_is_explicit_but_not_authority():
    from cios.applications.flora.verified_context_contract import VerifiedContext,VerifiedMembership,VerifiedSession
    for protocol in (VerifiedContext,VerifiedMembership,VerifiedSession):
        with pytest.raises(TypeError):protocol()
    assert 'VerifiedContext' in str(security.verified_context.__annotations__['return'])
    fields={'user_id','workspace','roles','effective_capabilities','enterprise_ids','workspace_ids','membership','session','verified_human','authentication_source'}
    assert fields.issubset(VerifiedContext.__dict__)

@pytest.mark.parametrize('kind',['object','dictionary','headers','cookie','environment'])
def test_arbitrary_objects_and_claims_cannot_supply_context(kind,monkeypatch):
    fake=SimpleNamespace(user_id='fixture-owner',workspace='fixture-workspace',roles=frozenset({'cios_owner'}),effective_capabilities=frozenset({'candidate.promote'}),enterprise_ids=frozenset({'*'}),verified_human=True)
    payload={'object':fake,'dictionary':vars(fake),'headers':{'X-Flora-User':'fixture-owner','X-Flora-Roles':'cios_owner'},'cookie':{'Cookie':'flora_user=fixture-owner; flora_roles=cios_owner'},'environment':{}}[kind]
    if kind=='environment':monkeypatch.setenv('FLORA_TRUST_PROXY_HEADERS','1');monkeypatch.setenv('FLORA_ENVIRONMENT','pilot')
    assert security.verified_context(payload) is None
    assert access.authenticated_flora_user(payload)==''
    with pytest.raises(PermissionError):security.require_verified_human(payload)
