"""Bounded closure checks: real authority, synthetic data, no policy mocks."""
import json
import sqlite3
import os
from dataclasses import replace
import pytest
from tests.test_flora_security_repair_01b import authority, signed
from tests.test_flora_security_workspace_boundary import resource, hashes
from tests.test_flora_security_01d_pr_review import candidate
from cios.applications.flora.blueprint_import.lifecycle import TwinImportLifecycleService, ImportLifecycleService
from cios.applications.flora.protected_storage import ProtectedJournal, file_digest
from cios.applications.flora.security_store import SecurityStore, RECENT
from cios.applications.flora.memory.service import ObservationMemoryService

pytestmark=pytest.mark.real_security_boundary


def integrity(tmp_path, store, before, label, *, retained_journal=False):
    after=hashes(store.path.parent.parent)
    full_after = after
    if retained_journal:
        # Corruption must retain private recovery evidence. Compare every
        # protected data file separately; preserve the full observed hash map.
        after = {k:v for k,v in after.items() if not k.startswith('security/protected-undo/')}
    (tmp_path/'01e-integrity.json').write_text(json.dumps({'label':label,'before':before,'after':after,'full_after':full_after,'retained_journal':retained_journal,'unchanged':before==after},indent=2))
    assert before==after


def test_authorised_candidate_deletion_commits_resource_audit(authority,tmp_path):
    store,_,_,headers,_=signed(authority,tmp_path);resource(store);package,staging=candidate(store)
    row=TwinImportLifecycleService().delete_candidate(package.import_run_id,'synthetic-human','DELETE CANDIDATE IMPORT',headers=headers)
    assert not staging.exists() and row['canonical_impact']=='none'
    with store.transaction() as db:
        audits=[json.loads(r[0]) for r in db.execute("SELECT payload FROM audit WHERE event='candidate_import_deleted'")]
    assert len(audits)==1
    assert audits[0]['import_run_id']==package.import_run_id and audits[0]['workspace_id']=='synthetic-workspace'
    assert audits[0]['session_ref'] and audits[0]['membership_version']>=1


@pytest.mark.parametrize('fault',['authority-audit','stale-auth','actor','confirmation'])
def test_candidate_deletion_failure_is_unchanged(authority,tmp_path,monkeypatch,fault):
    store,_,_,headers,_=signed(authority,tmp_path);resource(store);package,_=candidate(store)
    if fault=='stale-auth':
        with store.transaction() as db:db.execute('UPDATE tokens SET created=created-?',(RECENT+60,))
    if fault=='authority-audit':
        original=SecurityStore.audit
        def audit(self,db,event,**payload):
            if event=='candidate_import_deleted':raise OSError('synthetic authority audit failure')
            return original(self,db,event,**payload)
        monkeypatch.setattr(SecurityStore,'audit',audit)
    before=hashes(store.path.parent.parent)
    with pytest.raises((PermissionError,ValueError,OSError)):
        TwinImportLifecycleService().delete_candidate(package.import_run_id,'other-human' if fault=='actor' else 'synthetic-human',
            'bad' if fault=='confirmation' else 'DELETE CANDIDATE IMPORT',headers=headers)
    integrity(tmp_path,store,before,fault)


@pytest.mark.parametrize('boundary',['allowed','missing-scope','denied-acl'])
def test_adjacent_cancel_uses_same_authority_boundary(authority,tmp_path,boundary):
    from cios.applications.flora.enterprise_canvas.access import EnterpriseCanvasAccessRepository
    store,_,_,headers,_=signed(authority,tmp_path);_,acl=resource(store)
    package,_=candidate(store,'' if boundary=='missing-scope' else 'synthetic-workspace')
    if boundary=='denied-acl':EnterpriseCanvasAccessRepository().save(replace(acl,owner_account='other-human',acl=({'principal_id':'other-human'},)))
    before=hashes(store.path.parent.parent)
    if boundary=='allowed':
        row=ImportLifecycleService().cancel(package.import_run_id,'synthetic-human','review',headers=headers)
        assert row.state=='cancelled'
    else:
        with pytest.raises(PermissionError):ImportLifecycleService().cancel(package.import_run_id,'synthetic-human','review',headers=headers)
        integrity(tmp_path,store,before,boundary)


def financial(store):
    from tests.test_flora_ai_financial_report_review import fact
    from cios.applications.flora import document_review as review
    run,_=resource(store)
    claim=review.fact_to_review_claim(fact(canonical_enterprise_id='synthetic-enterprise'),'fi-synthetic')
    claim.update(review_state='accept',enterprise_id='synthetic-enterprise')
    run.update(document={'enterprise_id':'synthetic-enterprise','workspace_id':'synthetic-workspace','document_id':'synthetic-document',
        'title':'Synthetic report','source_url':'https://example.invalid/report','checksum':'synthetic-checksum'},claims=[claim])
    review._write_json(review._run_path('fi-synthetic'),run)
    return run,claim,review


@pytest.mark.parametrize('destination',['allowed','conflicting-alias','foreign-target','missing-authority'])
def test_downstream_reviewed_ingestion_checks_actual_destination(authority,tmp_path,destination):
    from cios.applications.flora.memory.repository import EvidenceRepository
    store,_,_,headers,_=signed(authority,tmp_path);run,claim,review=financial(store)
    item=review.claim_to_evidence(run,claim)
    if destination=='conflicting-alias':item['canonical_enterprise_id']='other-enterprise'
    if destination=='foreign-target':
        for key in ('enterprise_id','canonical_enterprise_id','organisation'):item[key]='other-enterprise'
    before=hashes(store.path.parent.parent)
    if destination=='allowed':
        ObservationMemoryService().process_reviewed_evidence('fi-synthetic',item,headers=headers)
        assert EvidenceRepository().get(item['evidence_id'])['enterprise_id']=='synthetic-enterprise'
    else:
        with pytest.raises(PermissionError):ObservationMemoryService().process_reviewed_evidence('fi-synthetic',item,headers=None if destination=='missing-authority' else headers)
        integrity(tmp_path,store,before,destination)


def test_authorised_financial_apply_still_writes(authority,tmp_path):
    from cios.applications.flora.memory.repository import EvidenceRepository
    store,_,_,headers,_=signed(authority,tmp_path);_,claim,review=financial(store)
    applied=review.apply_accepted('fi-synthetic',headers=headers)
    assert applied['status']=='applied' and applied['applied_results']
    from cios.applications.flora.memory.repository import EnterpriseModelRepository
    assert EnterpriseModelRepository().get('synthetic-enterprise').attributes
    assert EvidenceRepository().get(claim['evidence_id'])['enterprise_id']=='synthetic-enterprise'


@pytest.mark.parametrize('corruption',['missing-entry','extra-backup','backup-content','directory-mode'])
def test_corrupt_snapshot_denies_without_touching_data_and_retains_evidence(authority,tmp_path,corruption):
    store,_,_,headers,_=signed(authority,tmp_path);resource(store)
    root=store.path.parent.parent;victim=root/'original-synthetic.json';victim.write_text('original')
    journal=ProtectedJournal(store);before=hashes(root)
    with pytest.raises(sqlite3.OperationalError):
        with store.transaction() as db:
            journal.begin(db)
            manifest=json.loads((journal.path/'manifest.json').read_text())
            if corruption=='missing-entry':
                manifest['files'].pop(victim.name)
                (journal.path/'manifest.json').write_text(json.dumps(manifest))
                # Verify completeness independently even if a valid JSON edit
                # is accompanied by an updated metadata checksum.
                (journal.path/'manifest.sha256').write_text(file_digest(journal.path/'manifest.json'))
            elif corruption=='extra-backup':(journal.path/'files'/'999999').write_text('unexpected')
            elif corruption=='backup-content':(journal.path/'files'/manifest['files'][victim.name]['backup']).write_text('corrupt')
            else:
                manifest['directory_modes'].clear()
                (journal.path/'manifest.json').write_text(json.dumps(manifest))
                # Even a syntactically updated seal cannot hide missing metadata.
                (journal.path/'manifest.sha256').write_text(file_digest(journal.path/'manifest.json'))
            raise sqlite3.OperationalError('synthetic failed transaction')
    assert journal.path.exists() and victim.read_text()=='original'
    integrity(tmp_path,store,before,corruption,retained_journal=True)
    with pytest.raises((OSError,PermissionError)):
        with store.transaction():pass
    assert journal.path.exists()


def test_interrupted_restore_retries_from_retained_valid_snapshot(authority,tmp_path,monkeypatch):
    import cios.applications.flora.protected_storage as storage
    store,_,_,headers,_=signed(authority,tmp_path);resource(store);root=store.path.parent.parent
    victim=root/'original-synthetic.json';victim.write_text('original');before=hashes(root)
    original=storage.os.replace;interrupted=[]
    def fail(source,target):
        if str(source).find('/restoring/')>=0 and not interrupted:
            interrupted.append(True);raise OSError('synthetic interrupted restore')
        return original(source,target)
    monkeypatch.setattr(storage.os,'replace',fail)
    with pytest.raises(sqlite3.OperationalError):
        with store.transaction() as db:
            ProtectedJournal(store).begin(db);victim.write_text('changed')
            raise sqlite3.OperationalError('synthetic transaction failure')
    assert interrupted and ProtectedJournal(store).path.exists()
    monkeypatch.setattr(storage.os,'replace',original)
    with store.transaction():pass
    assert victim.read_text()=='original' and not ProtectedJournal(store).path.exists()
    integrity(tmp_path,store,before,'retry-after-interruption')


def test_failed_deletion_releases_lock_before_waiting_promotion_commits(authority,tmp_path,monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    import threading
    from tests.test_flora_security_admin_policy import plan_for
    from cios.applications.flora.blueprint_import.promotion import CanonicalPromotionService
    from cios.applications.flora.blueprint_import.ledger import BlueprintImportLedger
    store,_,_,headers,_=signed(authority,tmp_path);resource(store)
    package,plan=plan_for(headers);promotion=CanonicalPromotionService()
    approved=promotion.approve_plan(package.import_run_id,plan.plan_id,'synthetic-human','Synthetic approval',headers)
    attempted=threading.Event();worker_id=[];pending=[];connect=sqlite3.connect;append=BlueprintImportLedger.append
    def traced_connect(*args,**kwargs):
        db=connect(*args,**kwargs)
        if worker_id and threading.get_ident()==worker_id[0]:
            db.set_trace_callback(lambda sql:attempted.set() if sql=='BEGIN IMMEDIATE' else None)
        return db
    monkeypatch.setattr(sqlite3,'connect',traced_connect)
    def promote():
        worker_id.append(threading.get_ident())
        return promotion.execute_approved_plan(package.import_run_id,approved.approval_id,'synthetic-human',headers)
    with ThreadPoolExecutor(max_workers=1) as pool:
        def failed_audit(self,event,*args,**kwargs):
            if event=='candidate_import_deleted':
                pending.append(pool.submit(promote));assert attempted.wait(5)
                assert not pending[0].done()
                raise OSError('synthetic failed deletion audit')
            return append(self,event,*args,**kwargs)
        monkeypatch.setattr(BlueprintImportLedger,'append',failed_audit)
        with pytest.raises(OSError,match='synthetic failed deletion audit'):
            TwinImportLifecycleService().delete_candidate(package.import_run_id,'synthetic-human','DELETE CANDIDATE IMPORT',headers=headers)
        result=pending[0].result(10)
    assert result.final_execution_status=='succeeded' and result.actual_mutation_count==1
    assert TwinImportLifecycleService().package_for_run(package.import_run_id) is not None
    assert (store.path.parent.parent/package.archive_path).exists()
    assert ImportLifecycleService().get(package.import_run_id).state=='promoted'


def test_revocation_serializes_after_inflight_deletion_and_denies_next_call(authority,tmp_path,monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    import threading
    from cios.applications.flora import security
    store,_,_,headers,_=signed(authority,tmp_path);resource(store);package,_=candidate(store)
    service=TwinImportLifecycleService();preview=service.delete_preview
    attempted=threading.Event();worker_id=[];pending=[];connect=sqlite3.connect
    def traced_connect(*args,**kwargs):
        db=connect(*args,**kwargs)
        if worker_id and threading.get_ident()==worker_id[0]:
            db.set_trace_callback(lambda sql:attempted.set() if sql=='BEGIN IMMEDIATE' else None)
        return db
    monkeypatch.setattr(sqlite3,'connect',traced_connect)
    def revoke():
        worker_id.append(threading.get_ident());store.revoke_offline('synthetic-human','synthetic-workspace')
    with ThreadPoolExecutor(max_workers=1) as pool:
        def racing_preview(run_id):
            result=preview(run_id);pending.append(pool.submit(revoke))
            assert attempted.wait(5) and not pending[0].done()
            return result
        monkeypatch.setattr(service,'delete_preview',racing_preview)
        service.delete_candidate(package.import_run_id,'synthetic-human','DELETE CANDIDATE IMPORT',headers=headers)
        pending[0].result(10)
    assert security.verified_context(headers) is None
    before=hashes(store.path.parent.parent)
    with pytest.raises(PermissionError):service.delete_candidate(package.import_run_id,'synthetic-human','DELETE CANDIDATE IMPORT',headers=headers)
    integrity(tmp_path,store,before,'committed-revocation')
    with store.transaction() as db:
        assert db.execute("SELECT count(*) FROM audit WHERE event='candidate_import_deleted'").fetchone()[0]==1


@pytest.mark.parametrize('boundary',['changed-workspace','acl-before','acl-after'])
def test_deletion_rechecks_persisted_scope_and_acl_at_effect_boundary(authority,tmp_path,monkeypatch,boundary):
    from cios.applications.flora.enterprise_canvas.access import EnterpriseCanvasAccessRepository
    from cios.applications.flora.blueprint_import.ledger import BlueprintImportLedger
    store,_,_,headers,_=signed(authority,tmp_path);_,acl=resource(store);package,_=candidate(store)
    service=TwinImportLifecycleService();preview=service.delete_preview;append=BlueprintImportLedger.append
    def deny_acl():EnterpriseCanvasAccessRepository().save(replace(acl,owner_account='other-human',acl=({'principal_id':'other-human'},)))
    def changed_preview(run_id):
        result=preview(run_id)
        if boundary=='changed-workspace':
            path=service.registry._path_for_ref(package.package_ref)
            row=json.loads(path.read_text());row['workspace_id']='other-workspace';path.write_text(json.dumps(row))
        elif boundary=='acl-before':deny_acl()
        return result
    def changed_audit(self,event,*args,**kwargs):
        if event=='candidate_import_deleted' and boundary=='acl-after':deny_acl()
        return append(self,event,*args,**kwargs)
    monkeypatch.setattr(service,'delete_preview',changed_preview);monkeypatch.setattr(BlueprintImportLedger,'append',changed_audit)
    before=hashes(store.path.parent.parent)
    with pytest.raises(PermissionError):service.delete_candidate(package.import_run_id,'synthetic-human','DELETE CANDIDATE IMPORT',headers=headers)
    integrity(tmp_path,store,before,boundary)
