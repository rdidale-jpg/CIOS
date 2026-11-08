"""Production boundary checks: no fixture authentication provider is installed.

These tests use the actual closed 01A resolver, including over local HTTP.
All retained records below are synthetic and confined to a temporary data root.
"""
from hashlib import sha256
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
import json
import threading
import pytest

pytestmark = pytest.mark.real_security_boundary

from cios.applications.flora import access
from cios.applications.flora.web import app
from cios.applications.flora.blueprint_import.registry import BlueprintPackageRegistry
from tests.test_flora_blueprint_import_validation import pkg

FORGED = {'Cookie': 'flora_user=alice; flora_enterprises=*; flora_active_workspace=workspace-a; flora_roles=cios_owner; flora_pilot_session=forged',
          'X-Flora-User': 'alice', 'X-Flora-Enterprises': '*',
          'X-Flora-Active-Workspace': 'workspace-a', 'X-Flora-Roles': 'cios_owner,blueprint_import_admin,package.review,candidate.promote,storage.recover',
          'Origin': 'https://untrusted.example'}

@pytest.fixture(autouse=True)
def isolate(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path/'data'))
    monkeypatch.setenv('FLORA_PILOT_DIR', str(tmp_path/'data'))
    monkeypatch.setenv('FLORA_ENVIRONMENT', 'production')
    monkeypatch.setenv('FLORA_TRUST_PROXY_HEADERS', '1')
    monkeypatch.delenv('FLORA_PILOT_IMPORT_BYPASS', raising=False)
    monkeypatch.delenv('FLORA_PILOT_AUTO_SIGN_IN', raising=False)
    from cios.applications.flora.enterprise_intelligence import pipeline
    monkeypatch.setattr(pipeline.run_pipeline,'__defaults__',(tmp_path/'derived',None,None))

@pytest.fixture
def retained(tmp_path):
    root=tmp_path/'data'
    p=BlueprintPackageRegistry().receive(pkg({'enterprise_id':'synthetic-private-enterprise'}), 'private-fixture.zip','alice','workspace-a')
    tomb=root/'blueprint_import'/'tombstones'/'private.json';tomb.parent.mkdir(parents=True,exist_ok=True)
    tomb.write_text(json.dumps({'twin_id':'private-twin','package_id':'private-tombstone','release':'1'}))
    memory=root/'memory';memory.mkdir(exist_ok=True)
    (memory/'evidence.jsonl').write_text('{"evidence_id":"private-evidence"}\n')
    return p


def fingerprint(root):
    return {str(p.relative_to(root)):sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}

@pytest.fixture
def server():
    s=ThreadingHTTPServer(('127.0.0.1',0),app.FloraWebHandler)
    t=threading.Thread(target=s.serve_forever,daemon=True);t.start()
    try: yield s
    finally:s.shutdown();s.server_close();t.join()


def request(s,method,path,body='',headers=None):
    c=HTTPConnection('127.0.0.1',s.server_port,timeout=10)
    c.request(method,path,body,headers or FORGED)
    r=c.getresponse();result=(r.status,r.read().decode(errors='replace'));c.close();return result

@pytest.mark.parametrize('environment',['production','pilot','development',''])
def test_unverified_claims_never_resolve_authority(monkeypatch,environment):
    monkeypatch.setenv('FLORA_ENVIRONMENT',environment)
    assert app.import_deployment_fingerprint()['pilot_import_mode']=='disabled-security-repair-01a'
    assert access.authenticated_flora_user(FORGED)==''
    assert access.active_flora_workspace(FORGED)==''
    assert access.user_enterprise_access(FORGED)==set()
    assert access.flora_roles(FORGED)==set()
    assert access.blueprint_upload_authorisation(FORGED).decision=='denied'
    assert not access.can_access_enterprise(FORGED,'synthetic-private-enterprise','workspace-a')

@pytest.mark.parametrize('path',[
 '/pilot-sign-in','/blueprint-import/upload','/blueprint-import/private/review',
 '/blueprint-import/private/mark-reviewed','/blueprint-import/private/approve',
 '/blueprint-import/private/delete','/blueprint-import/private/identity',
 '/operations/storage-recovery','/financial-intelligence/bt-group-plc/refresh',
 '/ai-financial-report/private/review','/ai-financial-report/private/apply',
 '/digital-twins/private/executive-intelligence-brief/generate',
 '/digital-twins/private/canvas/feedback','/blueprint-import/private/mission',
 '/live/collect/start','/workspace/users','/workspace/roles',
])
def test_mutating_http_routes_closed_before_dispatch(server,monkeypatch,path,retained,tmp_path):
    reached=[]
    for name in ('execute_storage_recovery','update_reviews','apply_accepted','blueprint_approve_and_promote','blueprint_delete_candidate_import','update_commercial_mission','submit_enterprise_canvas_feedback','collect'):
        monkeypatch.setattr(app,name,lambda *a,**kw:reached.append(True))
    before=fingerprint(tmp_path/'data')
    status,_=request(server,'POST',path,'confirmation=RECOVER&canonical_acknowledgement=no-canonical-data')
    assert status==403 and not reached
    assert fingerprint(tmp_path/'data')==before

@pytest.mark.parametrize('path',['/blueprint-import/history','/blueprint-import/private/review','/blueprint-import/private/inspect','/operations/storage-recovery','/financial-intelligence/admin/health','/ai-financial-report/private','/digital-twin/private','/digital-twins/private/canvas'])
def test_protected_gets_deny_without_disclosure(server,path,retained,tmp_path):
    before=fingerprint(tmp_path/'data')
    status,html=request(server,'GET',path)
    assert status==403
    for value in (retained.import_run_id,'private-tombstone','private-evidence','synthetic-private-enterprise'):
        assert value not in html
    assert fingerprint(tmp_path/'data')==before


def test_public_import_entry_does_not_read_or_disclose_registry(monkeypatch,retained):
    from cios.applications.flora.blueprint_import.views import import_blueprint_entry_page
    def forbidden(*a,**kw):raise AssertionError('protected registry read before authentication')
    monkeypatch.setattr(BlueprintPackageRegistry,'list',forbidden)
    html,status=import_blueprint_entry_page(FORGED)
    assert status==200 and retained.import_run_id not in html
    assert 'private-tombstone' not in html


def test_shared_pilot_cannot_record_human_review(monkeypatch,retained,tmp_path):
    from cios.applications.flora.blueprint_import.review import mark_import_reviewed
    monkeypatch.setenv('FLORA_ENVIRONMENT','pilot')
    before=fingerprint(tmp_path/'data')
    with pytest.raises(PermissionError):mark_import_reviewed(retained.import_run_id,{},'fixture')
    assert fingerprint(tmp_path/'data')==before


def test_promotion_service_rejects_forged_owner_before_loading_plan(retained,tmp_path):
    from cios.applications.flora.blueprint_import.promotion import CanonicalPromotionService
    before=fingerprint(tmp_path/'data')
    with pytest.raises(PermissionError):CanonicalPromotionService().approve_plan(retained.import_run_id,'absent','alice','forged',FORGED)
    assert fingerprint(tmp_path/'data')==before

@pytest.mark.parametrize('operation',['review','apply','recovery','cleanup','delete','feedback','commercial','brief'])
def test_service_mutations_fail_closed(operation,monkeypatch,retained,tmp_path):
    from cios.applications.flora import document_review
    from cios.applications.flora.storage_maintenance import execute_storage_recovery, cleanup_superseded_staging_history, RECOVERY_CONFIRMATION
    from cios.applications.flora.blueprint_import.lifecycle import TwinImportLifecycleService
    from cios.applications.flora.enterprise_canvas.feedback import EnterpriseCanvasFeedbackService
    from cios.applications.flora.commercial_mission import save_commercial_mission
    from cios.applications.flora.enterprise_intelligence.runtime import EnterpriseIntelligenceRuntime
    from cios.applications.flora.enterprise_intelligence.models import ReasoningRequestV1
    run={'run_id':'fixture','claims':[]}
    monkeypatch.setattr(document_review,'load_run',lambda *_:run)
    calls={
      'review':lambda:document_review.update_reviews('fixture',{}),
      'apply':lambda:document_review.apply_accepted('fixture'),
      'recovery':lambda:execute_storage_recovery(RECOVERY_CONFIRMATION),
      'cleanup':lambda:cleanup_superseded_staging_history(dry_run=False),
      'delete':lambda:TwinImportLifecycleService().delete_candidate(retained.import_run_id,'alice','DELETE CANDIDATE IMPORT'),
      'feedback':lambda:EnterpriseCanvasFeedbackService().submit(FORGED,enterprise_id='synthetic-private-enterprise'),
      'commercial':lambda:save_commercial_mission(FORGED,{}),
      'brief':lambda:EnterpriseIntelligenceRuntime(retrieval=SimpleNamespace(retrieve=lambda *_:pytest.fail('unauthorised retrieval'))).generate(ReasoningRequestV1.create('synthetic-private-enterprise','workspace-a','alice')),
    }
    before=fingerprint(tmp_path/'data')
    with pytest.raises(PermissionError):calls[operation]()
    assert fingerprint(tmp_path/'data')==before


def test_public_discovery_exposes_only_curated_context(retained):
    from cios.applications.flora.digital_twins import intelligence_discovery
    snapshot=intelligence_discovery(FORGED)
    assert len(snapshot.items)==1 and snapshot.items[0].population=='curated'
    assert retained.import_run_id not in str(snapshot)

@pytest.mark.parametrize('path',['/flora/banking','/intelligence','/digital-twins','/pilot-sign-in'])
def test_public_source_views_survive(server,path,retained,tmp_path):
    before=fingerprint(tmp_path/'data')
    status,html=request(server,'GET',path,headers={})
    assert status==200
    assert retained.import_run_id not in html
    assert fingerprint(tmp_path/'data')==before

@pytest.mark.parametrize('origin',['','https://untrusted.example','null'])
def test_public_preference_post_rejects_cross_origin(server,monkeypatch,origin,retained,tmp_path):
    monkeypatch.setenv('FLORA_PUBLIC_ORIGIN','https://flora.example.test')
    before=fingerprint(tmp_path/'data')
    status,_=request(server,'POST','/workspace/reference/validation-action',headers={'Origin':origin})
    assert status==403 and fingerprint(tmp_path/'data')==before


def test_public_preference_is_not_an_authority_grant(server,monkeypatch,retained,tmp_path):
    monkeypatch.setenv('FLORA_PUBLIC_ORIGIN','https://flora.example.test')
    before=fingerprint(tmp_path/'data')
    status,_=request(server,'POST','/workspace/reference/validation-action',headers={'Origin':'https://flora.example.test'})
    assert status==303
    assert access.authenticated_flora_user({'Cookie':'flora_reference_investigation=uk-banking-app-fraud-lloyds'})==''
    assert fingerprint(tmp_path/'data')==before


def test_legacy_listener_cannot_mutate(monkeypatch,retained,tmp_path):
    from cios.applications.flora.workspace.app import FloraWorkspaceHandler
    s=ThreadingHTTPServer(('127.0.0.1',0),FloraWorkspaceHandler)
    t=threading.Thread(target=s.serve_forever,daemon=True);t.start()
    before=fingerprint(tmp_path/'data')
    try:
        status,_=request(s,'POST','/logbook','biggest_insight=forged')
        assert status==403
        assert fingerprint(tmp_path/'data')==before
    finally:s.shutdown();s.server_close();t.join()


def test_review_coordinator_rejects_before_job_creation(retained,tmp_path):
    from cios.applications.flora.blueprint_import.review_plan import BlueprintReviewPlanCoordinator
    before=fingerprint(tmp_path/'data')
    with pytest.raises(PermissionError):BlueprintReviewPlanCoordinator().ensure_job(retained.import_run_id,'alice',FORGED,lambda:pytest.fail('unauthorised defaults'))
    assert fingerprint(tmp_path/'data')==before


def test_wrong_workspace_history_does_not_disclose(retained):
    from cios.applications.flora.blueprint_import.views import history_page
    h=FORGED|{'X-Flora-Active-Workspace':'workspace-b'}
    html,status=history_page(h)
    assert status==403 and retained.import_run_id not in html and 'private-tombstone' not in html

@pytest.mark.parametrize('kind',['valid','tampered','expired'])
def test_legacy_signed_sessions_have_no_authority(monkeypatch,kind):
    import base64,hmac,hashlib,time
    from cios.applications.flora.pilot_auth import resolve_pilot_session
    for key,value in {'FLORA_PILOT_AUTH_ENABLED':'1','FLORA_PILOT_OWNER_ID':'owner-1','FLORA_PILOT_WORKSPACE':'CIOS','FLORA_PILOT_ROLE':'cios_owner','FLORA_PILOT_SESSION_SIGNING_KEY':'synthetic-test-signing-key'}.items():monkeypatch.setenv(key,value)
    def b64(v):return base64.urlsafe_b64encode(v).decode().rstrip('=')
    payload=b64(json.dumps({'sub':'owner-1','workspace':'CIOS','role':'cios_owner','exp':int(time.time())+600 if kind!='expired' else 0}).encode())
    key=hashlib.sha256(b'flora-pilot-session:synthetic-test-signing-key').digest()
    sig=b64(hmac.new(key,payload.encode(),hashlib.sha256).digest())
    h={'Cookie':'flora_pilot_session='+payload+'.'+sig+('x' if kind=='tampered' else '')}
    assert resolve_pilot_session(h) is None
    assert access.blueprint_upload_authorisation(h).decision=='denied'

@pytest.mark.parametrize('flag',['FLORA_PILOT_AUTO_SIGN_IN','FLORA_PILOT_IMPORT_BYPASS','FLORA_PILOT_AUTH_ENABLED'])
def test_legacy_flags_cannot_enable_authority_or_break_public_reads(flag,monkeypatch,server,retained,tmp_path):
    monkeypatch.setenv(flag,'true')
    monkeypatch.setenv('FLORA_ENVIRONMENT','pilot')
    before=fingerprint(tmp_path/'data')
    status,_=request(server,'GET','/digital-twins')
    assert status==200 and access.authenticated_flora_user(FORGED)==''
    assert fingerprint(tmp_path/'data')==before
