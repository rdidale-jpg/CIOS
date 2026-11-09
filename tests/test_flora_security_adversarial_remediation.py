"""01C real-producer, fault and clock tests. Synthetic protected stores only."""
from dataclasses import replace
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import threading
import time

import pytest
from tests.test_flora_security_repair_01b import authority, signed
from tests.test_flora_security_owner_journey import browser, authenticate
from tests.test_flora_security_release_review import Forms
from tests.test_flora_security_workspace_boundary import resource, hashes
from tests.test_flora_security_admin_policy import plan_for
from cios.applications.flora import document_review as review, security, security_store
from cios.applications.flora.security_store import SecurityStore, COOKIE, IDLE, ABSOLUTE, canonical, digest
from cios.applications.flora.enterprise_canvas.access import EnterpriseCanvasAccessRepository
from cios.applications.flora.protected_storage import ProtectedJournal, serialized_runtime_writer

pytestmark = pytest.mark.real_security_boundary


def financial(store):
    run, record = resource(store)
    run['document'] = {'enterprise_id': 'synthetic-enterprise', 'workspace_id': 'synthetic-workspace'}
    run['claims'] = []
    review._write_json(review._run_path('fi-synthetic'), run)
    return run, record


@pytest.mark.parametrize('boundary', ['wrong-workspace','missing-workspace','conflicting-document',
    'conflicting-enterprise','claim-scope','missing-acl','denied-acl','revoked-membership',
    'no-capability','wildcard-wrong-workspace','malformed-claims'])
@pytest.mark.parametrize('entry', ['http','service'])
def test_financial_reads_intersect_scope_capability_membership_and_acl(authority,tmp_path,browser,boundary,entry):
    store=authority[0]; authenticate(authority,tmp_path,browser)
    run,record=financial(store)
    if boundary in {'wrong-workspace','wildcard-wrong-workspace'}:run['workspace_id']='other-workspace'
    if boundary=='missing-workspace':run.pop('workspace_id')
    if boundary=='conflicting-document':run['document']['workspace_id']='other-workspace'
    if boundary=='conflicting-enterprise':run['document']['enterprise_id']='other-enterprise'
    if boundary=='claim-scope':run['claims']=[{'workspace_id':'other-workspace'}]
    if boundary=='malformed-claims':run['claims']=None
    repo=EnterpriseCanvasAccessRepository()
    if boundary=='missing-acl':repo.path.unlink()
    if boundary=='denied-acl':repo.save(replace(record,owner_account='other-human',acl=({'principal_id':'other-human'},)))
    with store.transaction() as db:
        if boundary=='revoked-membership':db.execute('UPDATE memberships SET active=0,version=version+1')
        if boundary=='no-capability':db.execute('UPDATE memberships SET roles=?',(canonical(['commercial_context.view']),))
        if boundary=='wildcard-wrong-workspace':db.execute('UPDATE memberships SET enterprises=?',(canonical(['*']),))
    review._write_json(review._run_path('fi-synthetic'),run)
    before=hashes(store.path.parent.parent)
    from cios.applications.flora.access import can_view_financial_intelligence_run
    headers={'Cookie': '; '.join(k+'='+v for k,v in browser.cookies.items())}
    assert not can_view_financial_intelligence_run(headers,run)
    if entry=='http':
        assert browser.request('GET','/ai-financial-report/fi-synthetic')[0]==403
    else:
        headers={'Cookie': '; '.join(k+'='+v for k,v in browser.cookies.items())}
        with pytest.raises(PermissionError):review.read_run('fi-synthetic',headers=headers)
        with pytest.raises(PermissionError):review.run_page('fi-synthetic',headers=headers)
    assert hashes(store.path.parent.parent)==before


@pytest.mark.parametrize('role',['cios_owner','package.inspect'])
def test_financial_authorised_read_does_not_require_write_capability(authority,tmp_path,browser,role):
    store=authority[0];authenticate(authority,tmp_path,browser);financial(store)
    with store.transaction() as db:db.execute('UPDATE memberships SET roles=?',(canonical([role]),))
    headers={'Cookie': '; '.join(k+'='+v for k,v in browser.cookies.items())}
    from cios.applications.flora.access import can_view_financial_intelligence_run
    assert can_view_financial_intelligence_run(headers,review.load_run('fi-synthetic'))
    assert review.read_run('fi-synthetic',headers=headers)['workspace_id']=='synthetic-workspace'
    assert browser.request('GET','/ai-financial-report/fi-synthetic')[0]==200
    if role=='package.inspect':
        with pytest.raises(PermissionError):review.update_reviews('fi-synthetic',{},headers=headers)


@pytest.mark.parametrize('entry', ['read_run','run_page','financial_intelligence_run_page',
    'financial_intelligence_run_response','financial_intelligence_progress_status',
    'financial_intelligence_progress_page','financial_intelligence_support_diagnostic_payload',
    'financial_intelligence_safe_support_report_payload','financial_intelligence_support_diagnostic_page'])
def test_financial_read_services_require_verified_authority(authority,entry):
    financial(authority[0])
    with pytest.raises(PermissionError):getattr(review,entry)('fi-synthetic')


def fail_service_commit(monkeypatch):
    connect=sqlite3.connect
    with SecurityStore().transaction() as db:
        initial=db.execute("SELECT count(*) FROM audit WHERE event='service_authorized'").fetchone()[0]
    class FailingCommit(sqlite3.Connection):
        def commit(self):
            if self.execute("SELECT count(*) FROM audit WHERE event='service_authorized'").fetchone()[0] > initial:
                raise sqlite3.OperationalError('synthetic late commit')
            return super().commit()
    monkeypatch.setattr(security_store.sqlite3,'connect',lambda *a,**kw:connect(*a,**dict(kw,factory=FailingCommit)))


def evidence(tmp_path,store,before,kind):
    after=hashes(store.path.parent.parent)
    (tmp_path/'01c-integrity.json').write_text(json.dumps({'kind':kind,'before':before,'after':after,'unchanged':before==after},indent=2))
    assert before==after


@pytest.mark.parametrize('phase',['audit','partial-persistence','data-fsync','late-commit'])
def test_protected_review_failure_restores_full_store(authority,tmp_path,monkeypatch,phase):
    store,_,_,headers,_=signed(authority,tmp_path);financial(store)
    before=hashes(store.path.parent.parent)
    if phase=='audit':
        monkeypatch.setattr(SecurityStore,'audit',lambda *a,**k:(_ for _ in ()).throw(sqlite3.OperationalError('synthetic audit failure')))
    if phase=='partial-persistence':
        def partial(path,data):
            path.write_text('partial protected record')
            new=path.parent/'partial-new.json';new.write_text('partial new record')
            raise OSError('synthetic partial persistence')
        monkeypatch.setattr(review,'_write_json',partial)
    if phase=='data-fsync':
        original=ProtectedJournal.flush_data;calls=[]
        def once(self):
            calls.append(1)
            if len(calls)==1:raise OSError('synthetic data fsync')
            return original(self)
        monkeypatch.setattr(ProtectedJournal,'flush_data',once)
    if phase=='late-commit':fail_service_commit(monkeypatch)
    with pytest.raises((OSError,sqlite3.Error)):review.update_reviews('fi-synthetic',{},headers=headers)
    evidence(tmp_path,store,before,phase)


def test_actual_canonical_promotion_late_commit_is_undone(authority,tmp_path,monkeypatch):
    from cios.applications.flora.blueprint_import.promotion import CanonicalPromotionService
    store,_,_,headers,_=signed(authority,tmp_path);financial(store)
    package,plan=plan_for(headers)
    service=CanonicalPromotionService()
    approval=service.approve_plan(package.import_run_id,plan.plan_id,'synthetic-human','Explicit synthetic approval',headers)
    before=hashes(store.path.parent.parent)
    fail_service_commit(monkeypatch)
    with pytest.raises(sqlite3.OperationalError):
        service.execute_approved_plan(package.import_run_id,approval.approval_id,'synthetic-human',headers)
    evidence(tmp_path,store,before,'canonical-promotion-late-commit')


def test_http_does_not_acknowledge_before_authority_commit(authority,tmp_path,browser,monkeypatch):
    store=authority[0];csrf=authenticate(authority,tmp_path,browser);financial(store)
    before=hashes(store.path.parent.parent);fail_service_commit(monkeypatch)
    status,headers,body=browser.request('POST','/ai-financial-report/fi-synthetic/review',{'csrf':csrf})
    assert status==503 and 'Location' not in headers and 'Storage unavailable' in body
    evidence(tmp_path,store,before,'http-late-commit')


def test_failed_recovery_denies_authority_until_undo_completes(authority,tmp_path,monkeypatch):
    store,_,_,headers,_=signed(authority,tmp_path);financial(store)
    before=hashes(store.path.parent.parent)
    original=ProtectedJournal.restore
    monkeypatch.setattr(ProtectedJournal,'restore',lambda *a:(_ for _ in ()).throw(OSError('synthetic recovery unavailable')))
    with pytest.raises(OSError):
        with store.transaction() as db:
            ProtectedJournal(store).begin(db)
            review._run_path('fi-synthetic').write_text('partial protected record')
            raise OSError('synthetic persistence failure')
    assert security.verified_context(headers) is None
    assert ProtectedJournal(store).path.exists()
    monkeypatch.setattr(ProtectedJournal,'restore',original)
    assert security.verified_context(headers) is not None
    evidence(tmp_path,store,before,'recovery-retry')


@pytest.mark.parametrize('committed',[False,True])
def test_process_interruption_recovers_before_next_authority_read(authority,tmp_path,committed):
    store,_,_,headers,_=signed(authority,tmp_path);financial(store)
    before=review._run_path('fi-synthetic').read_bytes()
    # os._exit bypasses Python finally/rollback. No bearer values are logged.
    script='''import json,os,sys
from cios.applications.flora.security_store import SecurityStore
from cios.applications.flora.protected_storage import ProtectedJournal
from cios.applications.flora import document_review as r
payload=json.load(sys.stdin);s=SecurityStore()
with s.transaction() as db:
 j=ProtectedJournal(s);j.begin(db)
 s.audit(db,'service_authorized',operation='synthetic-crash-test')
 p=r._run_path('fi-synthetic');run=r.load_run('fi-synthetic');run['status']='reviewed';r._write_json(p,run)
 if payload['committed']:
  j.flush_data();db.commit()
 os._exit(17)
'''
    result=subprocess.run([sys.executable,'-c',script],input=json.dumps({'committed':committed}),text=True,capture_output=True)
    assert result.returncode==17,result.stderr
    assert security.verified_context(headers) is not None
    assert not ProtectedJournal(store).path.exists()
    after=review._run_path('fi-synthetic').read_bytes()
    assert (after!=before) == committed
    with store.transaction() as db:
        assert db.execute("SELECT count(*) FROM audit WHERE event='service_authorized'").fetchone()[0]==int(committed)


@pytest.mark.parametrize('worker',['generic','financial','collection'])
def test_concurrent_writer_waits_and_is_not_erased_by_undo(authority,tmp_path,monkeypatch,worker):
    store,_,_,headers,_=signed(authority,tmp_path);financial(store)
    inside=threading.Event();release=threading.Event();second_started=threading.Event()
    @security.verified_service_write('package.review')
    def failing(*,headers):
        review._run_path('fi-synthetic').write_text('partial protected record')
        inside.set();assert release.wait(10)
        raise OSError('synthetic first writer failure')
    @serialized_runtime_writer
    def second():
        second_started.set()
        review._write_json(review._run_path('fi-second'),{'run_id':'fi-second','status':'durable-second-writer'})
    with ThreadPoolExecutor(max_workers=2) as pool:
        one=pool.submit(failing,headers=headers);assert inside.wait(5)
        if worker=='financial':
            monkeypatch.setattr(review,'refresh_financial_intelligence',lambda *a,**k:second())
            run_second=lambda:review._background_refresh('synthetic-enterprise','fi-second')
        elif worker=='collection':
            from cios.applications.flora.live.worker import _run
            from cios.applications.flora.live import progress
            monkeypatch.setattr(progress,'STATE_DIR',store.path.parent.parent/'live_evidence')
            monkeypatch.setattr(progress,'STATE_PATH',progress.STATE_DIR/'collection_run_state.json')
            import importlib
            collect_module=importlib.import_module('cios.applications.flora.live.collect')
            monkeypatch.setattr(collect_module,'collect',lambda *a,**k:second())
            run_second=lambda:_run('synthetic-enterprise',None,None,'synthetic-worker',None)
        else:run_second=second
        two=pool.submit(run_second)
        assert not second_started.wait(.1)
        release.set()
        with pytest.raises(OSError):one.result(10)
        two.result(10)
    assert review.load_run('fi-synthetic')['status']=='ready_for_review'
    assert review.load_run('fi-second')['status']=='durable-second-writer'


def test_visible_logout_clears_cookies_and_old_session_is_rejected_over_http(authority,tmp_path,browser):
    store=authority[0];authenticate(authority,tmp_path,browser)
    old=dict(browser.cookies)
    status,_,body=browser.request('GET','/flora');assert status==200
    assert "href='/settings/general'" in body
    forms=Forms();forms.feed(body);action=next(f for f in forms.forms if 'Sign out' in f['text'])
    status,headers,_=browser.request('POST',action['action'],action['fields'])
    assert status==303 and headers['Location']=='/flora'
    assert COOKIE not in browser.cookies and '__Host-flora_csrf' not in browser.cookies
    assert len(browser.last_response_cookies)==2
    assert all('Max-Age=0' in c for c in browser.last_response_cookies)
    browser.cookies=old
    assert browser.request('GET','/settings/general')[0]==403
    assert browser.request('POST','/ai-financial-report/fi-synthetic/review',{'csrf':old['__Host-flora_csrf']})[0]==403


@pytest.mark.parametrize('kind',['successful-read','successful-write','denied-read','denied-write','anonymous','absolute-expiry'])
def test_session_activity_policy_with_deterministic_clock(authority,tmp_path,browser,monkeypatch,kind):
    store=authority[0];csrf=authenticate(authority,tmp_path,browser);financial(store)
    token=browser.cookies[COOKIE]
    base=time.time()
    with store.transaction() as db:
        row=db.execute('SELECT * FROM tokens WHERE hash=?',(digest(token),)).fetchone()
        initial_touched=row['touched'];absolute=row['expires']
    monkeypatch.setattr(security_store.time,'time',lambda:base+25*60)
    if kind=='successful-read':assert browser.request('GET','/settings/general')[0]==200
    elif kind=='successful-write':assert browser.request('POST','/ai-financial-report/fi-synthetic/review',{'csrf':csrf})[0]==303
    elif kind=='denied-read':assert browser.request('GET','/ai-financial-report/fi-missing')[0]==403
    elif kind=='denied-write':assert browser.request('POST','/ai-financial-report/fi-synthetic/review',{'csrf':'forged'})[0]==403
    elif kind=='anonymous':
        browser.cookies.clear();assert browser.request('GET','/settings/general')[0]==403
    with store.transaction() as db:current=db.execute('SELECT touched FROM tokens WHERE hash=?',(digest(token),)).fetchone()[0]
    if kind.startswith('successful'):
        assert current==base+25*60
        projection=store.resolve(token)
        assert projection.session.idle_expires_at.timestamp()==pytest.approx(min(absolute,current+IDLE),abs=1e-6,rel=0)
        monkeypatch.setattr(security_store.time,'time',lambda:base+40*60)
        assert store.resolve(token).workspace=='synthetic-workspace'
    elif kind=='absolute-expiry':
        # Recent activity never extends the fixed absolute lifetime.
        with store.transaction() as db:db.execute('UPDATE tokens SET touched=? WHERE hash=?',(absolute-10,digest(token)))
        monkeypatch.setattr(security_store.time,'time',lambda:absolute)
        assert security.verified_context({'Cookie':COOKIE+'='+token}) is None
    else:
        assert current==initial_touched
        monkeypatch.setattr(security_store.time,'time',lambda:base+40*60)
        assert security.verified_context({'Cookie':COOKIE+'='+token}) is None


def test_http_dispatcher_error_does_not_touch_or_commit(authority,tmp_path,browser,monkeypatch):
    from cios.applications.flora.web.app import FloraWebHandler
    store=authority[0];csrf=authenticate(authority,tmp_path,browser);financial(store)
    before=hashes(store.path.parent.parent)
    monkeypatch.setattr(FloraWebHandler,'_dispatch_verified_post',lambda self:self.send_error(409,'Synthetic domain rejection'))
    status,_,_=browser.request('POST','/ai-financial-report/fi-synthetic/review',{'csrf':csrf})
    assert status==403
    evidence(tmp_path,store,before,'http-domain-rejection')


def test_audit_failure_after_partial_effects_is_undone(authority,tmp_path,monkeypatch):
    store,_,_,headers,_=signed(authority,tmp_path);financial(store)
    before=hashes(store.path.parent.parent)
    original=SecurityStore.audit
    def fault(self,db,event,**payload):
        if event=='synthetic_domain_completion':raise sqlite3.OperationalError('synthetic completion audit failure')
        return original(self,db,event,**payload)
    monkeypatch.setattr(SecurityStore,'audit',fault)
    @security.verified_service_write('package.review')
    def consequential(*,headers):
        review._run_path('fi-synthetic').write_text('partial protected record')
        with store.transaction() as db:store.audit(db,'synthetic_domain_completion')
    with pytest.raises(sqlite3.OperationalError):consequential(headers=headers)
    evidence(tmp_path,store,before,'audit-after-effects')


def test_corrupt_recovery_backup_cannot_grant_authority(authority,tmp_path,monkeypatch):
    store,_,_,headers,_=signed(authority,tmp_path);financial(store)
    original=ProtectedJournal.restore
    monkeypatch.setattr(ProtectedJournal,'restore',lambda *a:(_ for _ in ()).throw(OSError('synthetic undo interruption')))
    with pytest.raises(OSError):
        with store.transaction() as db:
            ProtectedJournal(store).begin(db)
            raise OSError('synthetic failed write')
    monkeypatch.setattr(ProtectedJournal,'restore',original)
    journal=ProtectedJournal(store)
    manifest=json.loads((journal.path/'manifest.json').read_text())
    backup=journal.path/'files'/next(iter(manifest['files'].values()))['backup']
    backup.write_text('corrupt synthetic backup')
    assert security.verified_context(headers) is None
    assert journal.path.exists()
    with pytest.raises(OSError):
        store.resolve(security_store.cookie_token(headers))


def test_symlink_in_protected_tree_denies_without_changing_target(authority,tmp_path):
    store,_,_,headers,_=signed(authority,tmp_path);financial(store)
    external=tmp_path/'outside-protected.txt';external.write_text('outside content')
    link=store.path.parent.parent/'untrusted-link';link.symlink_to(external)
    before=review._run_path('fi-synthetic').read_bytes()
    with pytest.raises(PermissionError):review.update_reviews('fi-synthetic',{},headers=headers)
    assert review._run_path('fi-synthetic').read_bytes()==before
    assert external.read_text()=='outside content'
    assert not ProtectedJournal(store).path.exists()
