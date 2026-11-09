"""HTTP owner workflow through the real producer on synthetic records only."""
import json
from http.client import HTTPConnection
from http.cookies import SimpleCookie
from http.server import ThreadingHTTPServer
import re
import threading
from urllib.parse import urlencode

import pytest
from tests.test_flora_security_repair_01b import authority, PASSWORD
from tests.test_flora_security_workspace_boundary import hashes
from cios.applications.flora.security_store import COOKIE

pytestmark=pytest.mark.real_security_boundary

class Browser:
    def __init__(self,server):self.server=server;self.cookies={}
    def request(self,method,path,fields=None,raw=None,content_type=None,origin='https://flora.test'):
        headers={'Cookie':'; '.join(k+'='+v for k,v in self.cookies.items())}
        if method=='POST':
            headers['Origin']=origin
            headers['Content-Type']=content_type or 'application/x-www-form-urlencoded'
            if raw is None:raw=urlencode(fields or {})
        connection=HTTPConnection('127.0.0.1',self.server.server_port,timeout=30)
        connection.request(method,path,body=raw,headers=headers)
        response=connection.getresponse();body=response.read().decode()
        self.last_response_cookies=[]
        for name,value in response.getheaders():
            if name.lower()=='set-cookie':
                self.last_response_cookies.append(value)
                cookie=SimpleCookie();cookie.load(value)
                for key,item in cookie.items():
                    assert item['secure'] and item['httponly'] and item['samesite']=='Strict'
                    assert item['path']=='/' and not item['domain']
                    if item.value:self.cookies[key]=item.value
                    else:self.cookies.pop(key,None)
        result=response.status,dict(response.getheaders()),body
        connection.close();return result


def hidden(html,name='csrf'):
    found=re.findall(r'name=[\'\"]'+name+r'[\'\"]\s+value=[\'\"]([^\'\"]+)',html)
    assert len(found)==1,(name,found)
    return found[0]

@pytest.fixture
def browser():
    from cios.applications.flora.web.app import FloraWebHandler
    server=ThreadingHTTPServer(('127.0.0.1',0),FloraWebHandler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    yield Browser(server)
    server.shutdown();server.server_close();thread.join()


def authenticate(authority,tmp_path,browser):
    store=authority[0]
    delivery=tmp_path/'private-enrollment-delivery'
    store.enroll_offline('synthetic-human',delivery)
    status,_,body=browser.request('GET','/auth/enroll');assert status==200
    status,_,_=browser.request('POST','/auth/enroll',{'csrf':hidden(body),'enrollment_token':delivery.read_text().strip(),'password':PASSWORD})
    assert status==303
    status,_,body=browser.request('GET','/auth/sign-in');assert status==200
    status,_,_=browser.request('POST','/auth/sign-in',{'csrf':hidden(body),'user_id':'synthetic-human','password':PASSWORD})
    assert status==303
    before=browser.cookies[COOKIE]
    status,_,body=browser.request('GET','/auth/workspace');assert status==200
    # Workspace page includes its own sign-out form: both share this proof.
    csrf=re.findall(r'name="csrf" value="([^"]+)"',body)[0]
    status,_,_=browser.request('POST','/auth/workspace',{'csrf':csrf,'workspace_id':'synthetic-workspace'})
    assert status==303
    assert browser.cookies[COOKIE]!=before
    return browser.cookies['__Host-flora_csrf']


def multipart(fields,filename,content):
    boundary='flora-synthetic-boundary'
    chunks=[]
    for key,value in fields.items():
        chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode())
    chunks += [f'--{boundary}\r\nContent-Disposition: form-data; name="blueprint_zip"; filename="{filename}"\r\nContent-Type: application/zip\r\n\r\n'.encode(),content,b'\r\n',f'--{boundary}--\r\n'.encode()]
    return b''.join(chunks),'multipart/form-data; boundary='+boundary


def test_complete_isolated_owner_http_journey(authority,tmp_path,browser):
    store=authority[0]
    csrf=authenticate(authority,tmp_path,browser)
    from cios.applications.flora.blueprint_import.registry import BlueprintPackageRegistry
    from cios.applications.flora.blueprint_import.review import ImportHumanReviewRepository
    from cios.applications.flora.blueprint_import.review_plan import BlueprintReviewPlanCoordinator
    from tests.test_flora_blueprint_import_validation import pkg
    content=pkg(records=[{'external_id':'synthetic-evidence','record_class':'evidence','truth_class':'evidence_backed','payload':{'quote':'Synthetic reviewable evidence','source_url':'https://example.invalid/synthetic'}}])
    raw,kind=multipart({'csrf':csrf,'expected_type':'enterprise'},'synthetic.zip',content)
    status,headers,body=browser.request('POST','/blueprint-import/upload',raw=raw,content_type=kind)
    assert status==303,body
    records=BlueprintPackageRegistry().list();assert len(records)==1
    package=records[0];run=package.import_run_id
    assert package.received_by=='synthetic-human'
    assert package.workspace_id=='synthetic-workspace'
    memory=store.path.parent.parent/'memory'
    before=hashes(memory) if memory.exists() else {}
    status,_,body=browser.request('GET',f'/blueprint-import/{run}/inspect');assert status==200
    status,_,body=browser.request('GET',f'/blueprint-import/{run}/review');assert status==200
    assert 'Review preparation required' in body
    status,_,body=browser.request('POST',f'/blueprint-import/{run}/prepare-review',{'csrf':csrf});assert status==200,body
    status,_,body=browser.request('POST',f'/blueprint-import/{run}/mark-reviewed',{'csrf':csrf});assert status==200,body
    human=ImportHumanReviewRepository().get(run)
    assert human['reviewer_identity']=='synthetic-human'
    assert (hashes(memory) if memory.exists() else {})==before
    job=BlueprintReviewPlanCoordinator().latest_job(run)
    assert job['status']=='Ready',job
    status,_,body=browser.request('GET',f'/blueprint-import/{run}/promote');assert status==200,body
    plan=hidden(body,'plan_id')
    assert plan==job['plan_id']
    status,_,body=browser.request('POST',f'/blueprint-import/{run}/approve',{'csrf':csrf,'plan_id':plan,'confirm_plan':'yes','confirm_mutations':'yes','rationale':'Synthetic explicit owner approval'})
    assert status==200,body
    from cios.applications.flora.blueprint_import.promotion import CanonicalPromotionRepository
    repo=CanonicalPromotionRepository()
    approvals=list(repo._approval_dir(run).glob('*.json'));assert len(approvals)==1
    approval=json.loads(approvals[0].read_text());assert approval['approver_identity']=='synthetic-human'
    result=repo.successful_for(run,plan,approval['approval_id'])
    assert result is not None and result.actor=='synthetic-human'
    assert result.actual_mutation_count==1
    # Existing governance idempotency must suppress replayed canonical effects.
    accepted=hashes(memory)
    status,_,_=browser.request('POST',f'/blueprint-import/{run}/approve',{'csrf':csrf,'plan_id':plan,'confirm_plan':'yes','confirm_mutations':'yes','rationale':'Synthetic explicit owner approval'})
    assert status==200
    assert hashes(memory)==accepted
    old_session=browser.cookies[COOKIE]
    status,_,_=browser.request('POST','/auth/sign-out',{'csrf':csrf});assert status==303
    from cios.applications.flora import security
    assert security.verified_context({'Cookie':f'{COOKIE}={old_session}'}) is None
    assert COOKIE not in browser.cookies
    status,_,_=browser.request('GET','/flora/banking');assert status==200


@pytest.mark.parametrize('case',['bad-origin','missing-csrf','forged-csrf'])
def test_authenticated_cross_origin_and_csrf_deny_without_writes(authority,tmp_path,browser,case):
    store=authority[0];csrf=authenticate(authority,tmp_path,browser)
    before=hashes(store.path.parent.parent)
    fields={'csrf':csrf}
    if case=='missing-csrf':fields={}
    if case=='forged-csrf':fields={'csrf':'forged'}
    origin='https://untrusted.invalid' if case=='bad-origin' else 'https://flora.test'
    status,_,_=browser.request('POST','/blueprint-import/upload',fields,origin=origin)
    assert status==403
    assert hashes(store.path.parent.parent)==before
