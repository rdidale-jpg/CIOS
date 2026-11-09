"""01D real-producer authority, recovery and deterministic interleaving evidence."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import errno
import json
import os
from pathlib import Path
import sqlite3
import threading
import time

import pytest
from tests.test_flora_security_repair_01b import authority,signed
from tests.test_flora_security_workspace_boundary import resource,hashes
from tests.test_flora_security_independent_readiness import feedback
from tests.test_flora_security_adversarial_remediation import fail_service_commit
from tests.test_flora_blueprint_import_validation import pkg
from cios.applications.flora import security,security_store,protected_storage
from cios.applications.flora.security_store import canonical,SecurityStore,RECENT
from cios.applications.flora.enterprise_canvas.feedback import EnterpriseCanvasFeedbackService,FeedbackAccessError
from cios.applications.flora.enterprise_canvas.access import EnterpriseCanvasAccessRepository
from cios.applications.flora.commercial_mission import save_commercial_mission,save_employer_context,save_commercial_context,resolve_commercial_mission,resolve_employer_context
from cios.applications.flora.storage_maintenance import cleanup_superseded_staging_history,execute_storage_recovery,DISPOSABLE_HISTORY,RECOVERY_CONFIRMATION

pytestmark=pytest.mark.real_security_boundary


def unchanged(tmp_path,store,before,kind):
    after=hashes(store.path.parent.parent)
    (tmp_path/'01d-integrity.json').write_text(json.dumps({'kind':kind,'before':before,'after':after,'unchanged':before==after},indent=2)+'\n')
    assert before==after


def roles(store,values):
    with store.transaction() as db:db.execute('UPDATE memberships SET roles=?,version=version+1',(canonical(values),))


def employer(headers):return save_employer_context(headers,{'organisation':'Synthetic employer'})
def mission(headers):return save_commercial_mission(headers,{'executive_role':'Synthetic director','commercial_objective':'Synthetic objective'})
def pair(headers):return save_commercial_context(headers,{'executive_role':'Synthetic director','commercial_objective':'Synthetic objective'},{'organisation':'Synthetic employer'})


@pytest.mark.parametrize('operation',['submit','status'])
@pytest.mark.parametrize('boundary',['revoked-member','missing-capability','acl-denied','wrong-workspace','revoked-session'])
def test_feedback_rejects_current_denied_authority_without_changes(authority,tmp_path,operation,boundary):
    store,token,csrf,headers,_=signed(authority,tmp_path);_,acl=resource(store)
    service=EnterpriseCanvasFeedbackService();initial=feedback(service,headers)
    if boundary=='revoked-member':store.revoke_offline('synthetic-human','synthetic-workspace')
    if boundary=='revoked-session':store.logout(token,csrf)
    if boundary=='missing-capability':roles(store,['package.inspect'])
    if boundary=='acl-denied':EnterpriseCanvasAccessRepository().save(replace(acl,acl=({'principal_id':'other-human'},),owner_account='other-human'))
    if boundary=='wrong-workspace':EnterpriseCanvasAccessRepository().save(replace(acl,workspace_id='other-workspace'))
    before=hashes(store.path.parent.parent)
    with pytest.raises(FeedbackAccessError):
        if operation=='submit':feedback(service,headers)
        else:service.change_status(headers,initial.feedback_id,'under_review')
    assert service.visible_feedback(headers,'synthetic-enterprise')==[]
    unchanged(tmp_path,store,before,operation+'-'+boundary)


@pytest.mark.parametrize('boundary',['missing-scope','conflicting-scope','revoked-membership','no-read-capability'])
def test_feedback_reads_fail_closed_on_persisted_or_authority_conflict(authority,tmp_path,boundary):
    store,_,_,headers,_=signed(authority,tmp_path);resource(store)
    service=EnterpriseCanvasFeedbackService();initial=feedback(service,headers)
    if boundary in {'missing-scope','conflicting-scope'}:
        row=initial.to_dict()
        if boundary=='missing-scope':row.pop('workspace_id')
        else:row['workspace_id']='other-workspace'
        service.repo.path.write_text(json.dumps(row)+'\n')
    if boundary=='revoked-membership':store.revoke_offline('synthetic-human','synthetic-workspace')
    if boundary=='no-read-capability':roles(store,['package.inspect'])
    before=hashes(store.path.parent.parent)
    assert service.visible_feedback(headers,'synthetic-enterprise')==[]
    with pytest.raises(FeedbackAccessError):service.change_status(headers,initial.feedback_id,'under_review')
    unchanged(tmp_path,store,before,'feedback-read-'+boundary)


@pytest.mark.parametrize('boundary',['membership','capability','acl'])
def test_feedback_rechecks_revocation_immediately_before_append(authority,tmp_path,monkeypatch,boundary):
    store,_,_,headers,_=signed(authority,tmp_path);_,acl=resource(store)
    service=EnterpriseCanvasFeedbackService();append=service.repo.append
    def revoke(row):
        if boundary=='membership':
            with store.transaction() as db:db.execute('UPDATE memberships SET active=0,version=version+1')
        elif boundary=='capability':roles(store,['package.inspect'])
        else:EnterpriseCanvasAccessRepository().save(replace(acl,acl=({'principal_id':'other-human'},),owner_account='other-human'))
        return append(row)
    monkeypatch.setattr(service.repo,'append',revoke)
    before=hashes(store.path.parent.parent)
    with pytest.raises(FeedbackAccessError):feedback(service,headers)
    unchanged(tmp_path,store,before,'append-point-'+boundary)


@pytest.mark.parametrize('role',['cios_owner','package.review','feedback.submit'])
def test_feedback_positive_scope_capability_and_resource_audit(authority,tmp_path,role):
    store,_,_,headers,_=signed(authority,tmp_path);resource(store)
    roles(store,[role])
    service=EnterpriseCanvasFeedbackService()
    result=service.submit(headers,enterprise_id='synthetic-enterprise',action_type='context',user_statement='Synthetic fact',rationale='Synthetic reason',workspace_id='browser-override')
    assert result.workspace_id=='synthetic-workspace'
    assert service.visible_feedback(headers,'synthetic-enterprise')[0].feedback_id==result.feedback_id
    if role=='feedback.submit':
        with pytest.raises(FeedbackAccessError):service.change_status(headers,result.feedback_id,'under_review')
    else:assert service.change_status(headers,result.feedback_id,'under_review').status=='under_review'
    with store.transaction() as db:
        audits=[json.loads(r[0]) for r in db.execute("SELECT payload FROM audit WHERE event='feedback_mutation'")]
    assert audits and all(r['resource_id']==result.feedback_id and r['workspace_id']=='synthetic-workspace' and r['user_id']=='synthetic-human' and r['session_ref'] for r in audits)
    from cios.applications.flora.security_store import digest
    committed={digest(canonical(r.to_dict())) for r in service.repo.list_all()}
    assert all(r['record_digest'] in committed for r in audits)


def test_feedback_external_revocation_serializes_after_current_commit(authority,tmp_path,monkeypatch):
    store,_,_,headers,_=signed(authority,tmp_path);resource(store)
    service=EnterpriseCanvasFeedbackService();append=service.repo.append
    inside=threading.Event();release=threading.Event();revoking=threading.Event();revoked=threading.Event()
    def paused(row):
        inside.set();assert release.wait(10)
        return append(row)
    def revoke():
        revoking.set();store.revoke_offline('synthetic-human','synthetic-workspace');revoked.set()
    monkeypatch.setattr(service.repo,'append',paused)
    with ThreadPoolExecutor(max_workers=2) as pool:
        writer=pool.submit(feedback,service,headers);assert inside.wait(5)
        revoker=pool.submit(revoke);assert revoking.wait(5);assert not revoked.wait(.1)
        release.set();accepted=writer.result(10);revoker.result(10)
    assert revoked.is_set() and security.verified_context(headers) is None
    assert any(r.feedback_id==accepted.feedback_id for r in service.repo.list_all())
    with pytest.raises(FeedbackAccessError):feedback(service,headers)


@pytest.mark.parametrize('phase',['resource-audit','partial-append','late-commit'])
def test_feedback_failure_cannot_leave_data_without_authority_audit(authority,tmp_path,monkeypatch,phase):
    store,_,_,headers,_=signed(authority,tmp_path);resource(store)
    service=EnterpriseCanvasFeedbackService();before=hashes(store.path.parent.parent)
    if phase=='resource-audit':
        original=SecurityStore.audit
        def fail(self,db,event,**payload):
            if event=='feedback_mutation':raise sqlite3.OperationalError('synthetic feedback audit failure')
            return original(self,db,event,**payload)
        monkeypatch.setattr(SecurityStore,'audit',fail)
    if phase=='partial-append':
        def fail(row):
            service.repo.path.write_text('partial feedback write')
            raise OSError('synthetic append failure')
        monkeypatch.setattr(service.repo,'append',fail)
    if phase=='late-commit':fail_service_commit(monkeypatch)
    with pytest.raises((OSError,sqlite3.Error)):feedback(service,headers)
    unchanged(tmp_path,store,before,'feedback-'+phase)


@pytest.mark.parametrize('edit',[mission,employer,pair],ids=['mission','employer','paired'])
@pytest.mark.parametrize('boundary',['read-only','revoked','conflicting-scope','missing-scope'])
def test_profile_edit_intersects_current_membership_capability_and_scope(authority,tmp_path,edit,boundary):
    from cios.applications.flora.commercial_mission import _mission_path,_employer_path
    store,_,_,headers,_=signed(authority,tmp_path)
    if boundary in {'conflicting-scope','missing-scope'}:
        pair(headers)
        for path in [_mission_path(),_employer_path()]:
            rows=json.loads(path.read_text())
            if boundary=='missing-scope':rows['synthetic-human'].pop('workspace_id')
            else:rows['synthetic-human']['workspace_id']='other-workspace'
            path.write_text(json.dumps(rows))
    if boundary=='read-only':roles(store,['package.inspect','commercial_context.view'])
    if boundary=='revoked':store.revoke_offline('synthetic-human','synthetic-workspace')
    before=hashes(store.path.parent.parent)
    with pytest.raises(PermissionError):edit(headers)
    unchanged(tmp_path,store,before,'profile-'+boundary)


@pytest.mark.parametrize('edit',[mission,employer,pair],ids=['mission','employer','paired'])
def test_profile_authorised_edit_is_scoped_and_audited(authority,tmp_path,edit):
    store,_,_,headers,_=signed(authority,tmp_path);edit(headers)
    root=store.path.parent.parent/'commercial_context'
    for p in root.glob('*.json'):assert json.loads(p.read_text())['synthetic-human']['workspace_id']=='synthetic-workspace'
    with store.transaction() as db:
        rows=[json.loads(r[0]) for r in db.execute("SELECT payload FROM audit WHERE event='commercial_profile_mutation'")]
    assert rows and all(r['user_id']=='synthetic-human' and r['workspace_id']=='synthetic-workspace' and r['session_ref'] for r in rows)
    from cios.applications.flora.security_store import digest
    for row in rows:
        filename=row['resource_id'].split(':',1)[0]
        committed=json.loads((root/filename).read_text())['synthetic-human']
        assert row['record_digest']==digest(canonical(committed))
    if edit in {mission,pair}:assert resolve_commercial_mission(headers).executive_role=='Synthetic director'
    if edit in {employer,pair}:assert resolve_employer_context(headers).organisation=='Synthetic employer'


@pytest.mark.parametrize('phase',['resource-audit','second-file','late-commit'])
def test_paired_profile_failure_restores_both_profiles_and_audits(authority,tmp_path,monkeypatch,phase):
    from cios.applications.flora import commercial_mission as profiles
    store,_,_,headers,_=signed(authority,tmp_path);pair(headers)
    before=hashes(store.path.parent.parent)
    if phase=='resource-audit':
        original=SecurityStore.audit
        def fail(self,db,event,**payload):
            if event=='commercial_profile_mutation':raise sqlite3.OperationalError('synthetic profile audit failure')
            return original(self,db,event,**payload)
        monkeypatch.setattr(SecurityStore,'audit',fail)
    if phase=='second-file':
        original=profiles.atomic_write_json
        def fail(path,value):
            if path==profiles._employer_path():
                path.write_text('partial employer record');raise OSError('synthetic second profile failure')
            return original(path,value)
        monkeypatch.setattr(profiles,'atomic_write_json',fail)
    if phase=='late-commit':fail_service_commit(monkeypatch)
    with pytest.raises((OSError,ValueError,sqlite3.Error)):pair(headers)
    unchanged(tmp_path,store,before,'paired-profile-'+phase)


def history(store,headers,workspace='synthetic-workspace'):
    from cios.applications.flora.blueprint_import.registry import BlueprintPackageRegistry
    package=BlueprintPackageRegistry().receive(pkg(),'synthetic-history.zip','synthetic-human',workspace)
    version=store.path.parent.parent/DISPOSABLE_HISTORY/package.import_run_id/'synthetic-version'
    version.mkdir(parents=True);(version/'snapshot.json').write_text('synthetic staging history')
    with store.transaction() as db:db.execute('UPDATE memberships SET recovery=1')
    return version


@pytest.mark.parametrize('boundary',['no-grant','stale','wrong-workspace','acl-denied','unresolved-run'])
def test_direct_cleanup_requires_current_resource_authority(authority,tmp_path,monkeypatch,boundary):
    store,_,_,headers,_=signed(authority,tmp_path);_,acl=resource(store)
    version=history(store,headers,'other-workspace' if boundary=='wrong-workspace' else 'synthetic-workspace')
    if boundary=='no-grant':
        with store.transaction() as db:db.execute('UPDATE memberships SET recovery=0')
    if boundary=='stale':
        now=time.time();monkeypatch.setattr(security_store.time,'time',lambda:now+RECENT+1)
    if boundary=='acl-denied':EnterpriseCanvasAccessRepository().save(replace(acl,acl=({'principal_id':'other-human'},),owner_account='other-human'))
    if boundary=='unresolved-run':
        alternate=version.parent.with_name('unknown-synthetic-run');version.parent.rename(alternate);version=alternate/version.name
    before=hashes(store.path.parent.parent)
    with pytest.raises(PermissionError):cleanup_superseded_staging_history(keep_versions=0,dry_run=False,headers=headers)
    unchanged(tmp_path,store,before,'cleanup-'+boundary)


def test_authorised_cleanup_removes_only_scoped_disposable_history_with_audit(authority,tmp_path):
    store,_,_,headers,_=signed(authority,tmp_path);resource(store);version=history(store,headers)
    result=cleanup_superseded_staging_history(keep_versions=0,dry_run=False,headers=headers)
    assert result['files_removed']==1 and not version.exists() and result['canonical_data_affected']=='NO'
    with store.transaction() as db:
        row=json.loads(db.execute("SELECT payload FROM audit WHERE event='storage_history_cleanup' ORDER BY seq DESC").fetchone()[0])
    assert row['workspace_id']=='synthetic-workspace' and row['resource_ids'] and row['session_ref']


@pytest.mark.parametrize('phase',['audit','partial-deletion','late-commit'])
def test_cleanup_failure_undo_is_durable_and_lossless(authority,tmp_path,monkeypatch,phase):
    from cios.applications.flora import storage_maintenance as cleanup
    store,_,_,headers,_=signed(authority,tmp_path);resource(store);version=history(store,headers)
    os.chmod(version,0o700);before=hashes(store.path.parent.parent)
    if phase=='audit':
        original=SecurityStore.audit
        def fail(self,db,event,**payload):
            if event=='storage_history_cleanup':raise sqlite3.OperationalError('synthetic cleanup audit failure')
            return original(self,db,event,**payload)
        monkeypatch.setattr(SecurityStore,'audit',fail)
    if phase=='partial-deletion':
        original=cleanup.shutil.rmtree
        def fail(path,*a,**k):
            result=original(path,*a,**k)
            if Path(path)==version:raise OSError('synthetic partial deletion')
            return result
        monkeypatch.setattr(cleanup.shutil,'rmtree',fail)
    if phase=='late-commit':fail_service_commit(monkeypatch)
    with pytest.raises((OSError,sqlite3.Error)):cleanup_superseded_staging_history(keep_versions=0,dry_run=False,headers=headers)
    assert version.stat().st_mode & 0o777==0o700
    unchanged(tmp_path,store,before,'cleanup-'+phase)


def test_caught_nested_service_failure_poison_outer_transaction(authority,tmp_path):
    store,_,_,headers,_=signed(authority,tmp_path);resource(store)
    path=store.path.parent.parent/'synthetic-nested.json';before=hashes(store.path.parent.parent)
    @security.verified_service_write('package.review')
    def inner(*,headers):
        path.write_text('partial protected write');raise OSError('synthetic nested service failure')
    with pytest.raises(PermissionError,match='transaction was rejected'):
        with store.transaction():
            try:inner(headers=headers)
            except OSError:pass
    unchanged(tmp_path,store,before,'caught-nested-service-failure')


@pytest.mark.parametrize('phase',['replace-interruption','verification-failure'])
def test_recovery_retains_evidence_until_exact_restoration_is_verified(authority,tmp_path,monkeypatch,phase):
    store,_,_,headers,_=signed(authority,tmp_path);resource(store)
    root=store.path.parent.parent;path=root/'synthetic-recovery.json';path.write_text('original protected value')
    before=hashes(root);journal=protected_storage.ProtectedJournal(store)
    original=protected_storage.os.replace
    def fail(source,target):
        if Path(source).parent.name=='restoring':
            if phase=='replace-interruption':raise OSError('synthetic recovery interruption')
            result=original(source,target);Path(target).write_text('synthetic corrupt restoration');return result
        return original(source,target)
    monkeypatch.setattr(protected_storage.os,'replace',fail)
    with pytest.raises(OSError):
        with store.transaction() as db:
            journal.begin(db);path.write_text('partial protected value');raise OSError('synthetic mutation failure')
    assert journal.path.exists()
    if phase=='replace-interruption':
        assert list((journal.path/'restoring').iterdir())
    assert security.verified_context(headers) is None
    monkeypatch.setattr(protected_storage.os,'replace',original)
    assert security.verified_context(headers) is not None and not journal.path.exists()
    unchanged(tmp_path,store,before,'recovery-'+phase)


def test_reservation_failure_prevents_effects_and_preserves_store(authority,tmp_path,monkeypatch):
    store,_,_,headers,_=signed(authority,tmp_path);resource(store)
    before=hashes(store.path.parent.parent);effects=[]
    @security.verified_service_write('package.review')
    def action(*,headers):effects.append(True)
    monkeypatch.setattr(protected_storage.os,'posix_fallocate',lambda *a:(_ for _ in ()).throw(OSError(errno.ENOSPC,'synthetic reserve capacity')))
    with pytest.raises(OSError):action(headers=headers)
    assert effects==[]
    unchanged(tmp_path,store,before,'reservation-enospc')


@pytest.mark.parametrize('entry',['begin','recover','restore','flush_data'])
def test_recovery_primitives_require_the_current_writer_lock(authority,entry):
    journal=protected_storage.ProtectedJournal(authority[0])
    with pytest.raises(PermissionError):
        if entry in {'begin','recover'}:getattr(journal,entry)(None)
        elif entry=='restore':journal.restore({})
        else:journal.flush_data()


@pytest.mark.parametrize('boundary',['body-workspace','outside-root'])
def test_profile_payload_and_storage_override_cannot_select_other_scope(authority,tmp_path,monkeypatch,boundary):
    store,_,_,headers,_=signed(authority,tmp_path)
    value={'organisation':'Synthetic employer'}
    if boundary=='body-workspace':value['workspace_id']='other-workspace'
    else:monkeypatch.setenv('FLORA_EMPLOYER_CONTEXTS_FILE',str(tmp_path/'outside-protected.json'))
    before=hashes(store.path.parent.parent)
    with pytest.raises(PermissionError):save_employer_context(headers,value)
    assert not (tmp_path/'outside-protected.json').exists()
    unchanged(tmp_path,store,before,'profile-'+boundary)


def test_edit_only_profile_versions_advance_without_implicit_view_permission(authority,tmp_path):
    store,_,_,headers,_=signed(authority,tmp_path);roles(store,['commercial_context.edit'])
    first=pair(headers);second=pair(headers)
    assert first[0].version==first[1].version==1
    assert second[0].version==second[1].version==2
    assert resolve_commercial_mission(headers) is None and resolve_employer_context(headers) is None


@pytest.mark.parametrize('boundary',['capability','membership','workspace'])
def test_profile_revalidates_authority_and_persisted_scope_after_write(authority,tmp_path,monkeypatch,boundary):
    from cios.applications.flora import commercial_mission as profiles
    store,_,_,headers,_=signed(authority,tmp_path);original=profiles.atomic_write_json
    def fault(path,rows):
        if boundary=='capability':roles(store,['package.inspect'])
        if boundary=='membership':
            with store.transaction() as db:db.execute('UPDATE memberships SET active=0,version=version+1')
        if boundary=='workspace':rows['synthetic-human']['workspace_id']='other-workspace'
        return original(path,rows)
    monkeypatch.setattr(profiles,'atomic_write_json',fault)
    before=hashes(store.path.parent.parent)
    with pytest.raises(PermissionError):employer(headers)
    unchanged(tmp_path,store,before,'postwrite-profile-'+boundary)


@pytest.mark.parametrize('boundary',['capability','acl'])
def test_feedback_revalidates_after_append_before_commit(authority,tmp_path,monkeypatch,boundary):
    store,_,_,headers,_=signed(authority,tmp_path);_,acl=resource(store)
    service=EnterpriseCanvasFeedbackService();original=service.repo.append
    def append_then_revoke(row):
        result=original(row)
        if boundary=='capability':roles(store,['package.inspect'])
        else:EnterpriseCanvasAccessRepository().save(replace(acl,owner_account='other-human',acl=({'principal_id':'other-human'},)))
        return result
    monkeypatch.setattr(service.repo,'append',append_then_revoke)
    before=hashes(store.path.parent.parent)
    with pytest.raises(FeedbackAccessError):feedback(service,headers)
    unchanged(tmp_path,store,before,'postappend-'+boundary)


def test_cleanup_internal_destructive_helper_cannot_skip_write_envelope(authority,tmp_path):
    from cios.applications.flora.storage_maintenance import _cleanup_history
    store,_,_,headers,_=signed(authority,tmp_path);resource(store);version=history(store,headers)
    before=hashes(store.path.parent.parent)
    with pytest.raises(PermissionError):_cleanup_history(keep_versions=0,dry_run=False,headers=headers)
    assert version.exists()
    unchanged(tmp_path,store,before,'cleanup-helper-envelope')


def test_cleanup_acl_revocation_before_commit_rolls_back_deletion(authority,tmp_path,monkeypatch):
    from cios.applications.flora import storage_maintenance as cleanup
    store,_,_,headers,_=signed(authority,tmp_path);_,acl=resource(store);version=history(store,headers)
    original=cleanup.shutil.rmtree
    def revoke(path,*a,**k):
        result=original(path,*a,**k)
        if Path(path)==version:EnterpriseCanvasAccessRepository().save(replace(acl,owner_account='other-human',acl=({'principal_id':'other-human'},)))
        return result
    monkeypatch.setattr(cleanup.shutil,'rmtree',revoke)
    before=hashes(store.path.parent.parent)
    with pytest.raises(PermissionError):cleanup_superseded_staging_history(keep_versions=0,dry_run=False,headers=headers)
    unchanged(tmp_path,store,before,'cleanup-commit-acl-revocation')


def test_repeated_rollback_preserves_collision_names_and_directory_permissions(authority,tmp_path):
    store,_,_,headers,_=signed(authority,tmp_path)
    root=store.path.parent.parent;folder=root/'synthetic-private-directory';folder.mkdir(mode=0o700)
    path=folder/'record.json';path.write_text('original protected record')
    (folder/'.record.json.recovery').write_text('independent original recovery-looking name')
    before=hashes(root)
    @security.verified_service_write('package.review')
    def fail(*,headers):path.write_text('partial');raise OSError('synthetic repeated rollback')
    for _ in range(3):
        with pytest.raises(OSError):fail(headers=headers)
        assert folder.stat().st_mode & 0o777==0o700
        assert hashes(root)==before
    unchanged(tmp_path,store,before,'repeated-rollback')


def test_profile_reads_do_not_disclose_uncommitted_values_before_rollback(authority,tmp_path,monkeypatch):
    from cios.applications.flora import commercial_mission as profiles
    store,_,_,headers,_=signed(authority,tmp_path);employer(headers)
    original=profiles.atomic_write_json
    written=threading.Event();release=threading.Event();reading=threading.Event()
    def partial(path,value):
        original(path,value);written.set();assert release.wait(10)
        raise OSError('synthetic profile write failure')
    def read():reading.set();return resolve_employer_context(headers)
    monkeypatch.setattr(profiles,'atomic_write_json',partial)
    with ThreadPoolExecutor(max_workers=2) as pool:
        writer=pool.submit(save_employer_context,headers,{'organisation':'UNCOMMITTED_SYNTHETIC_EMPLOYER'})
        assert written.wait(5)
        reader=pool.submit(read);assert reading.wait(5);assert not reader.done()
        release.set()
        with pytest.raises(OSError):writer.result(10)
        assert reader.result(10).organisation=='Synthetic employer'


def test_silent_profile_content_corruption_is_not_acknowledged(authority,tmp_path,monkeypatch):
    from cios.applications.flora import commercial_mission as profiles
    store,_,_,headers,_=signed(authority,tmp_path);before=hashes(store.path.parent.parent)
    original=profiles.atomic_write_json
    def corrupt(path,value):
        copied=json.loads(json.dumps(value));copied['synthetic-human']['organisation']='incorrect synthetic value'
        return original(path,copied)
    monkeypatch.setattr(profiles,'atomic_write_json',corrupt)
    with pytest.raises(OSError):employer(headers)
    unchanged(tmp_path,store,before,'silent-profile-corruption')


@pytest.mark.parametrize('boundary',['membership','capability','acl'])
def test_previously_valid_request_is_rechecked_after_waiting_for_write(authority,tmp_path,monkeypatch,boundary):
    store,_,_,headers,_=signed(authority,tmp_path);_,acl=resource(store)
    service=EnterpriseCanvasFeedbackService()
    original=security.require_service_capability
    initial=threading.Event();release=threading.Event();first=[True]
    def pause_after_actual_validation(*args,**kwargs):
        context=original(*args,**kwargs)
        if first[0]:
            first[0]=False;initial.set();assert release.wait(10)
        return context
    monkeypatch.setattr(security,'require_service_capability',pause_after_actual_validation)
    with ThreadPoolExecutor(max_workers=1) as pool:
        pending=pool.submit(feedback,service,headers);assert initial.wait(5)
        try:
            if boundary=='membership':store.revoke_offline('synthetic-human','synthetic-workspace')
            elif boundary=='capability':roles(store,['package.inspect'])
            else:EnterpriseCanvasAccessRepository().save(replace(acl,owner_account='other-human',acl=({'principal_id':'other-human'},)))
            before=hashes(store.path.parent.parent)
        finally:release.set()
        with pytest.raises(FeedbackAccessError):pending.result(10)
    unchanged(tmp_path,store,before,'stale-initial-context-'+boundary)


@pytest.mark.parametrize('role,expected',[('feedback.view',{'standard'}),('feedback.submit',{'standard'}),('feedback.review',{'restricted'}),('feedback.restricted',{'restricted'}),('package.review',{'standard','restricted'})])
def test_feedback_visibility_preserves_existing_capability_policy(authority,tmp_path,role,expected):
    store,_,_,headers,_=signed(authority,tmp_path);resource(store)
    service=EnterpriseCanvasFeedbackService()
    service.submit(headers,enterprise_id='synthetic-enterprise',action_type='context',user_statement='Synthetic public-to-members feedback',rationale='Synthetic rationale',visibility='standard')
    feedback(service,headers)
    roles(store,[role])
    assert {r.visibility for r in service.visible_feedback(headers,'synthetic-enterprise')}==expected


def test_second_authority_database_cannot_recover_the_shared_root(authority,tmp_path):
    import shutil
    store,_,_,headers,_=signed(authority,tmp_path);resource(store)
    alternate=store.path.with_name('synthetic-secondary.sqlite3')
    shutil.copyfile(store.path,alternate);os.chmod(alternate,0o600)
    before=hashes(store.path.parent.parent)
    with pytest.raises(PermissionError):
        with SecurityStore(alternate).transaction():
            pytest.fail('An independent lock must not control the same undo root')
    assert security.verified_context(headers) is not None
    unchanged(tmp_path,store,before,'secondary-authority-store')
