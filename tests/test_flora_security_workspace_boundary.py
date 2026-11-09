"""Bounded workspace-blocker regression tests; real synthetic authority."""
from dataclasses import replace
from hashlib import sha256
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import threading
from types import SimpleNamespace
from urllib.parse import urlencode

import pytest
from tests.test_flora_security_repair_01b import authority, signed
from cios.applications.flora import document_review, security
from cios.applications.flora.security_store import canonical, digest, COOKIE
from cios.applications.flora.enterprise_canvas.access import EnterpriseCanvasAccessRecord, EnterpriseCanvasAccessRepository

pytestmark = pytest.mark.real_security_boundary


def hashes(root):
    return {str(p.relative_to(root)):sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}


def resource(store, **overrides):
    run={'run_id':'fi-synthetic','enterprise_id':'synthetic-enterprise','workspace_id':'synthetic-workspace','claims':[],'status':'ready_for_review'}
    run.update(overrides)
    document_review._write_json(document_review._run_path('fi-synthetic'),run)
    record=EnterpriseCanvasAccessRecord('1.0','synthetic-canvas','synthetic-enterprise','synthetic-workspace','synthetic-human',
        acl=({'principal_id':'synthetic-human','role':'owner','grant_source':'synthetic-existing-acl'},))
    EnterpriseCanvasAccessRepository().save(record)
    return run,record


def assert_unchanged(store, before, tmp_path):
    after=hashes(store.path.parent.parent)
    (tmp_path/'hash-comparison.json').write_text(json.dumps({'before':before,'after':after,'unchanged':before==after},indent=2))
    assert after==before


CASES=['wrong-workspace','different-enterprise','missing-membership','revoked-membership',
       'missing-workspace','empty-workspace','invalid-workspace','ambiguous-workspace','ambiguous-enterprise',
       'claim-workspace','browser-override','wildcard-wrong-workspace','missing-acl','acl-workspace',
       'acl-principal','no-capability','forged-identity']

@pytest.mark.parametrize('operation',['review','apply'])
@pytest.mark.parametrize('case',CASES)
def test_financial_mutations_intersect_persisted_workspace_and_acl(authority,tmp_path,case,operation):
    store,token,csrf,headers,_=signed(authority,tmp_path)
    run,record=resource(store)
    form={}
    if case in {'wrong-workspace','browser-override','wildcard-wrong-workspace'}:run['workspace_id']='other-workspace'
    if case=='different-enterprise':run['enterprise_id']='other-enterprise'
    if case=='missing-workspace':del run['workspace_id']
    if case=='empty-workspace':run['workspace_id']=''
    if case=='invalid-workspace':run['workspace_id']=['synthetic-workspace']
    if case=='ambiguous-workspace':run['document']={'workspace_id':'other-workspace'}
    if case=='ambiguous-enterprise':run['document']={'enterprise_id':'other-enterprise'}
    if case=='claim-workspace':run['claims']=[{'workspace_id':'other-workspace'}]
    if case=='browser-override':form={'workspace_id':['synthetic-workspace']}
    with store.transaction() as db:
        if case=='missing-membership':db.execute('DELETE FROM memberships')
        if case=='revoked-membership':db.execute('UPDATE memberships SET active=0,version=version+1')
        if case=='wildcard-wrong-workspace':db.execute('UPDATE memberships SET enterprises=?',(canonical(['*']),))
        if case=='no-capability':db.execute('UPDATE memberships SET roles=?',(canonical(['package.inspect']),))
    repo=EnterpriseCanvasAccessRepository()
    if case=='missing-acl':repo.path.unlink()
    if case=='acl-workspace':repo.save(replace(record,workspace_id='other-workspace'))
    if case=='acl-principal':repo.save(replace(record,owner_account='other-human',acl=({'principal_id':'other-human'},)))
    if case=='forged-identity':headers={'X-Flora-User':'synthetic-human','X-Flora-Roles':'cios_owner','X-Flora-Active-Workspace':'synthetic-workspace'}
    document_review._write_json(document_review._run_path('fi-synthetic'),run)
    before=hashes(store.path.parent.parent)
    with pytest.raises(PermissionError):
        if operation=='review':document_review.update_reviews('fi-synthetic',form,headers=headers)
        else:document_review.apply_accepted('fi-synthetic',headers=headers)
    assert_unchanged(store,before,tmp_path)


@pytest.mark.parametrize('operation',['review','apply'])
def test_financial_same_enterprise_correct_workspace_and_acl_permitted(authority,tmp_path,operation):
    store,_,_,headers,_=signed(authority,tmp_path)
    resource(store)
    if operation=='review':result=document_review.update_reviews('fi-synthetic',{},headers=headers)
    else:result=document_review.apply_accepted('fi-synthetic',headers=headers)
    assert result['workspace_id']=='synthetic-workspace'
    assert result['status']==('reviewed' if operation=='review' else 'applied')


def test_canvas_acl_cannot_be_rebound_by_selected_workspace_argument(authority,tmp_path):
    store,_,_,headers,_=signed(authority,tmp_path)
    _,record=resource(store)
    EnterpriseCanvasAccessRepository().save(replace(record,workspace_id='other-workspace'))
    from cios.applications.flora.enterprise_canvas.access import can_access_canvas_record
    before=hashes(store.path.parent.parent)
    assert not can_access_canvas_record(headers,'synthetic-enterprise','synthetic-workspace')
    assert_unchanged(store,before,tmp_path)


def test_canvas_feedback_uses_recorded_scope(authority,tmp_path):
    store,_,_,headers,_=signed(authority,tmp_path)
    _,record=resource(store)
    EnterpriseCanvasAccessRepository().save(replace(record,workspace_id='other-workspace'))
    from cios.applications.flora.enterprise_canvas.feedback import EnterpriseCanvasFeedbackService
    before=hashes(store.path.parent.parent)
    with pytest.raises(PermissionError):
        EnterpriseCanvasFeedbackService().submit(headers,enterprise_id='synthetic-enterprise',workspace_id='synthetic-workspace',action_type='unknown',user_statement='synthetic candidate',rationale='synthetic review')
    assert_unchanged(store,before,tmp_path)


def test_executive_brief_uses_recorded_scope_before_retrieval(authority,tmp_path):
    store,_,_,headers,_=signed(authority,tmp_path)
    _,record=resource(store)
    EnterpriseCanvasAccessRepository().save(replace(record,workspace_id='other-workspace'))
    from cios.applications.flora.enterprise_intelligence.runtime import EnterpriseIntelligenceRuntime
    retrieval=SimpleNamespace(retrieve=lambda _:pytest.fail('protected retrieval reached'))
    request=SimpleNamespace(enterprise_id='synthetic-enterprise',workspace_id='synthetic-workspace',requested_by='synthetic-human')
    before=hashes(store.path.parent.parent)
    with pytest.raises(PermissionError):EnterpriseIntelligenceRuntime(retrieval=retrieval).generate(request,headers=headers)
    assert_unchanged(store,before,tmp_path)


def test_blueprint_promotion_uses_package_workspace(authority,tmp_path):
    store,_,_,headers,_=signed(authority,tmp_path)
    from cios.applications.flora.blueprint_import.promotion import CanonicalPromotionService
    service=CanonicalPromotionService()
    service.registry=SimpleNamespace(get=lambda _:SimpleNamespace(identity=SimpleNamespace(enterprise_id='synthetic-enterprise'),workspace_id='other-workspace'))
    service.staging=SimpleNamespace(list_candidates=lambda _:pytest.fail('candidate processing reached'))
    before=hashes(store.path.parent.parent)
    with pytest.raises(PermissionError):service._assert_target_ownership('synthetic-run',{'package_ref':'synthetic-package','effects':[]},headers)
    assert_unchanged(store,before,tmp_path)


@pytest.fixture
def local_server():
    from cios.applications.flora.web.app import FloraWebHandler
    server=ThreadingHTTPServer(('127.0.0.1',0),FloraWebHandler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    yield server
    server.shutdown();server.server_close();thread.join()


@pytest.mark.parametrize('suffix',['review','apply'])
def test_route_and_direct_service_both_deny_wrong_workspace(authority,tmp_path,local_server,suffix):
    store,_,csrf,headers,_=signed(authority,tmp_path)
    resource(store,workspace_id='other-workspace')
    before=hashes(store.path.parent.parent)
    connection=HTTPConnection('127.0.0.1',local_server.server_port,timeout=10)
    body=urlencode({'csrf':csrf,'workspace_id':'synthetic-workspace'})
    connection.request('POST','/ai-financial-report/fi-synthetic/'+suffix,body=body,
        headers={**headers,'Origin':'https://flora.test','Content-Type':'application/x-www-form-urlencoded'})
    response=connection.getresponse();response.read();connection.close()
    assert response.status==403
    assert_unchanged(store,before,tmp_path)
