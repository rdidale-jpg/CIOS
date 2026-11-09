"""Independent final-acceptance probes; real producer, synthetic storage only."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
import sqlite3
import threading
import time

import pytest
from tests.test_flora_security_repair_01b import authority,signed,PASSWORD
from tests.test_flora_security_owner_journey import browser,authenticate
from tests.test_flora_security_workspace_boundary import resource,hashes
from tests.test_flora_security_independent_readiness import feedback
from tests.test_flora_security_integrity_repair import history
from tests.test_flora_security_adversarial_remediation import fail_service_commit
from cios.applications.flora import security_store
from cios.applications.flora.security_store import COOKIE,RECENT,canonical,digest
from cios.applications.flora.security_operator import reconcile,plan,apply
from cios.applications.flora.security_web import CSRF_COOKIE
from cios.applications.flora.protected_storage import ProtectedJournal
from cios.applications.flora.enterprise_canvas.feedback import EnterpriseCanvasFeedbackService
from cios.applications.flora.commercial_mission import save_employer_context
from cios.applications.flora.storage_maintenance import RECOVERY_CONFIRMATION,KEEP_STAGING_VERSIONS

pytestmark=pytest.mark.real_security_boundary


def evidence(tmp_path,**facts):
    (tmp_path/'acceptance-observation.json').write_text(json.dumps(facts,indent=2)+'\n')


def unchanged(tmp_path,store,before,kind):
    after=hashes(store.path.parent.parent)
    (tmp_path/'acceptance-integrity.json').write_text(json.dumps({'kind':kind,'before':before,'after':after,'unchanged':before==after},indent=2)+'\n')
    assert before==after


def test_native_sqlite_contention_precedes_rollback_and_feedback_commit(authority,tmp_path,monkeypatch):
    store,_,_,headers,_=signed(authority,tmp_path);resource(store)
    service=EnterpriseCanvasFeedbackService()
    busy=threading.Event();attempted=threading.Event();finished=threading.Event()
    worker_id=[];sequence=[]
    original_connect=sqlite3.connect
    def connect(*args,**kwargs):
        connection=original_connect(*args,**kwargs)
        if worker_id and threading.get_ident()==worker_id[0]:
            def trace(statement):
                if statement=='BEGIN IMMEDIATE':
                    sequence.append('feedback_native_begin');attempted.set()
            connection.set_trace_callback(trace)
        return connection
    monkeypatch.setattr(security_store.sqlite3,'connect',connect)
    def writer():
        worker_id.append(threading.get_ident())
        # Obtain an actual SQLITE_BUSY from the same database while the other
        # connection owns its writer reservation. No authority is mocked.
        connection=original_connect(store.path,timeout=0,isolation_level=None)
        try:
            try:connection.execute('BEGIN IMMEDIATE')
            except sqlite3.OperationalError as exc:
                assert exc.sqlite_errorcode==sqlite3.SQLITE_BUSY
                sequence.append('native_busy_observed');busy.set()
            else:pytest.fail('The simultaneous writer reservation was not exclusive')
        finally:connection.close()
        result=feedback(service,headers);sequence.append('feedback_committed');finished.set()
        return result
    with ThreadPoolExecutor(max_workers=1) as pool:
        with pytest.raises(sqlite3.OperationalError,match='synthetic failing transaction'):
            with store.transaction() as db:
                ProtectedJournal(store).begin(db);sequence.append('failing_writer_owns_lock')
                future=pool.submit(writer)
                assert busy.wait(5) and attempted.wait(5)
                assert not finished.wait(.1) and not future.done()
                assert service.repo.list_all()==[]
                sequence.append('rollback_requested')
                raise sqlite3.OperationalError('synthetic failing transaction')
        sequence.append('rollback_complete')
        accepted=future.result(10)
    rows=service.repo.list_all()
    assert any(r.feedback_id==accepted.feedback_id for r in rows)
    with store.transaction() as db:
        audits=[json.loads(r[0]) for r in db.execute("SELECT payload FROM audit WHERE event='feedback_mutation'")]
    assert any(r['resource_id']==accepted.feedback_id and r['record_digest']==digest(canonical(accepted.to_dict())) for r in audits)
    assert sequence.index('native_busy_observed')<sequence.index('rollback_requested')<sequence.index('feedback_committed')
    evidence(tmp_path,native_sqlite_busy_observed=True,actual_feedback_begin_observed=True,
        callback_completed_while_lock_held=False,accepted_feedback_survives=True,matching_resource_audit=True,sequence=sequence)


def test_concurrent_feedback_appends_have_no_lost_records_or_audits(authority,tmp_path):
    store,_,_,headers,_=signed(authority,tmp_path);resource(store)
    barrier=threading.Barrier(5);service=EnterpriseCanvasFeedbackService();worker_ids=[]
    def write(number):
        worker_ids.append(threading.get_ident());barrier.wait(10)
        return service.submit(headers,enterprise_id='synthetic-enterprise',action_type='context',
            user_statement='Synthetic concurrent feedback '+str(number),rationale='Synthetic acceptance')
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures=[pool.submit(write,i) for i in range(4)];barrier.wait(10)
        results=[f.result(20) for f in futures]
    assert len(set(worker_ids))==4
    assert len({r.feedback_id for r in results})==4
    stored=service.repo.list_all();assert {r.feedback_id for r in stored}=={r.feedback_id for r in results}
    with store.transaction() as db:audits=[json.loads(r[0]) for r in db.execute("SELECT payload FROM audit WHERE event='feedback_mutation'")]
    assert len(audits)==4 and {r['resource_id'] for r in audits}=={r.feedback_id for r in stored}
    assert {r['record_digest'] for r in audits}=={digest(canonical(r.to_dict())) for r in stored}
    evidence(tmp_path,concurrent_threads=4,accepted_records=4,persisted_records=len(stored),matching_resource_audits=len(audits),lost_updates=0)


def second_actor(authority,tmp_path):
    store,snapshot,manifest,_,_=authority
    # Explicit synthetic ownership evidence and approval. This never inspects or
    # provisions a production identity or invents a production workspace owner.
    (snapshot/'second-synthetic-binding.json').write_text(json.dumps({'actor_id':'synthetic-second-human','workspace_id':'synthetic-workspace'}))
    approval=json.loads(json.dumps(manifest));review=reconcile(snapshot)
    approval.update(snapshot_digest=digest(canonical(review)),evidence=review['files'],
        bindings=[{'user_id':'synthetic-second-human','workspace_id':'synthetic-workspace','roles':['cios_owner'],'enterprise_ids':['synthetic-enterprise']}])
    proposed=plan(store,snapshot,approval);apply(store,snapshot,proposed,proposed['digest'])
    delivery=tmp_path/'synthetic-second-enrollment';store.enroll_offline('synthetic-second-human',delivery)
    pre,csrf=store.preauth();store.enroll(delivery.read_text().strip(),PASSWORD,pre,csrf)
    pre,csrf=store.preauth();token,csrf=store.login('synthetic-second-human',PASSWORD,pre,csrf)
    token,csrf=store.select(token,csrf,'synthetic-workspace')
    return {'Cookie':COOKIE+'='+token+'; '+CSRF_COOKIE+'='+csrf}


def test_concurrent_actor_profiles_preserve_both_keys_in_shared_file(authority,tmp_path):
    store,_,_,first,_=signed(authority,tmp_path);second=second_actor(authority,tmp_path)
    barrier=threading.Barrier(3);worker_ids=[]
    def write(headers,name):
        worker_ids.append(threading.get_ident());barrier.wait(10)
        return save_employer_context(headers,{'organisation':name})
    with ThreadPoolExecutor(max_workers=2) as pool:
        a=pool.submit(write,first,'Synthetic first employer');b=pool.submit(write,second,'Synthetic second employer')
        barrier.wait(10);a.result(20);b.result(20)
    records=json.loads((store.path.parent.parent/'commercial_context/employer_contexts.json').read_text())
    assert len(set(worker_ids))==2 and set(records)=={'synthetic-human','synthetic-second-human'}
    assert records['synthetic-human']['organisation']=='Synthetic first employer'
    assert records['synthetic-second-human']['organisation']=='Synthetic second employer'
    with store.transaction() as db:audits=[json.loads(r[0]) for r in db.execute("SELECT payload FROM audit WHERE event='commercial_profile_mutation'")]
    assert len(audits)==2
    assert all(r['record_digest']==digest(canonical(records[r['user_id']])) for r in audits)
    evidence(tmp_path,concurrent_threads=2,independent_actor_records_preserved=2,matching_resource_audits=2,lost_updates=0)


def test_previously_accepted_feedback_survives_unrelated_failed_profile_commit(authority,tmp_path,monkeypatch):
    store,_,_,headers,_=signed(authority,tmp_path);resource(store)
    service=EnterpriseCanvasFeedbackService();accepted=feedback(service,headers)
    before=hashes(store.path.parent.parent);fail_service_commit(monkeypatch)
    with pytest.raises(sqlite3.OperationalError):save_employer_context(headers,{'organisation':'Uncommitted synthetic employer'})
    assert any(r.feedback_id==accepted.feedback_id for r in service.repo.list_all())
    unchanged(tmp_path,store,before,'accepted-feedback-before-profile-commit-failure')


def cleanup_setup(authority,tmp_path,browser,monkeypatch,workspace='synthetic-workspace'):
    from cios.applications.flora.web.app import FloraWebHandler
    monkeypatch.setattr(FloraWebHandler,'storage_status',dict(FloraWebHandler.storage_status))
    store=authority[0];csrf=authenticate(authority,tmp_path,browser)
    headers={'Cookie':'; '.join(k+'='+v for k,v in browser.cookies.items())}
    resource(store);version=history(store,headers,workspace)
    versions=[version]
    for i in range(KEEP_STAGING_VERSIONS):
        other=version.with_name('synthetic-extra-'+str(i));other.mkdir();(other/'snapshot.json').write_text('Synthetic disposable history');versions.append(other)
    for i,path in enumerate(versions):os.utime(path,(100+i,100+i))
    return store,csrf,versions


@pytest.mark.parametrize('boundary',['stale-authentication','missing-grant','revoked-membership','wrong-workspace'])
def test_http_cleanup_denials_preserve_every_protected_file(authority,tmp_path,browser,monkeypatch,boundary):
    store,csrf,versions=cleanup_setup(authority,tmp_path,browser,monkeypatch,'other-workspace' if boundary=='wrong-workspace' else 'synthetic-workspace')
    if boundary=='stale-authentication':
        base=time.time();monkeypatch.setattr(security_store.time,'time',lambda:base+RECENT+1)
    if boundary=='missing-grant':
        with store.transaction() as db:db.execute('UPDATE memberships SET recovery=0')
    if boundary=='revoked-membership':store.revoke_offline('synthetic-human','synthetic-workspace')
    if boundary=='stale-authentication':
        live=store.resolve(browser.cookies[COOKIE])
        assert 'storage.recover' in live.effective_capabilities
        assert time.time()-live.session.authenticated_at.timestamp()>RECENT
    before=hashes(store.path.parent.parent)
    status,_,_=browser.request('POST','/operations/storage-recovery',{'csrf':csrf,'confirmation':RECOVERY_CONFIRMATION,'canonical_acknowledgement':'no-canonical-data'})
    assert status==403 and all(p.exists() for p in versions)
    evidence(tmp_path,http_status=status,denial=boundary,all_disposable_versions_preserved=True,request_had_session_bound_csrf=True)
    unchanged(tmp_path,store,before,'http-cleanup-'+boundary)


def test_http_recent_scoped_cleanup_commits_history_deletion_and_audit(authority,tmp_path,browser,monkeypatch):
    store,csrf,versions=cleanup_setup(authority,tmp_path,browser,monkeypatch)
    status,_,_=browser.request('POST','/operations/storage-recovery',{'csrf':csrf,'confirmation':RECOVERY_CONFIRMATION,'canonical_acknowledgement':'no-canonical-data'})
    assert status==200
    removed=[p for p in versions if not p.exists()];assert len(removed)==1
    assert sum(p.exists() for p in versions)==KEEP_STAGING_VERSIONS
    with store.transaction() as db:
        audits=[json.loads(r[0]) for r in db.execute("SELECT payload FROM audit WHERE event='storage_history_cleanup'")]
    assert len(audits)==1 and audits[0]['workspace_id']=='synthetic-workspace'
    assert audits[0]['resource_ids']==[str(removed[0].relative_to(store.path.parent.parent))]
    evidence(tmp_path,http_status=status,deleted_disposable_versions=1,retained_versions=KEEP_STAGING_VERSIONS,
        matching_resource_audit=True,recent_verified_authentication=True)
