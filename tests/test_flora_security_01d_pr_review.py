"""Final independent PR audit: newly distinct destructive-service/undo risks.

Required-safe assertions against the real producer and synthetic filesystem.
No authority provider is mocked. Recovery corruption is local fault injection,
not a claim that an anonymous caller can write the private security directory.
"""
from dataclasses import replace
import json
import os
import sqlite3

import pytest
from tests.test_flora_security_repair_01b import authority,signed
from tests.test_flora_security_workspace_boundary import resource,hashes
from tests.test_flora_blueprint_import_validation import pkg
from cios.applications.flora import security
from cios.applications.flora.blueprint_import.registry import BlueprintPackageRegistry
from cios.applications.flora.blueprint_import.lifecycle import TwinImportLifecycleService
from cios.applications.flora.blueprint_import.ledger import BlueprintImportLedger
from cios.applications.flora.enterprise_canvas.access import EnterpriseCanvasAccessRepository,can_access_canvas_record
from cios.applications.flora.protected_storage import ProtectedJournal

pytestmark=pytest.mark.real_security_boundary


def observe(tmp_path,**facts):
    (tmp_path/'pr-review-observation.json').write_text(json.dumps(facts,indent=2)+'\n')


def candidate(store,workspace='synthetic-workspace'):
    package=BlueprintPackageRegistry().receive(pkg(),'synthetic-delete.zip','synthetic-human',workspace)
    staging=store.path.parent.parent/'blueprint_import/staging'/package.import_run_id
    staging.mkdir(parents=True,exist_ok=True);(staging/'synthetic-staged.json').write_text('synthetic protected candidate')
    return package,staging


@pytest.mark.parametrize('boundary',['denied-resource-acl','missing-persisted-workspace'])
def test_candidate_delete_intersects_persisted_scope_and_existing_acl(authority,tmp_path,boundary):
    store,_,_,headers,_=signed(authority,tmp_path);_,acl=resource(store)
    package,staging=candidate(store,'' if boundary=='missing-persisted-workspace' else 'synthetic-workspace')
    if boundary=='denied-resource-acl':
        EnterpriseCanvasAccessRepository().save(replace(acl,owner_account='other-human',acl=({'principal_id':'other-human'},)))
        assert not can_access_canvas_record(headers,'synthetic-enterprise')
    before=hashes(store.path.parent.parent);denied=False
    try:TwinImportLifecycleService().delete_candidate(package.import_run_id,'synthetic-human','DELETE CANDIDATE IMPORT',headers=headers)
    except PermissionError:denied=True
    after=hashes(store.path.parent.parent)
    observe(tmp_path,boundary=boundary,denied=denied,staged_data_preserved=staging.exists(),protected_store_unchanged=before==after)
    assert denied and before==after


def test_direct_candidate_deletion_cannot_continue_after_committed_revocation(authority,tmp_path,monkeypatch):
    store,_,_,headers,_=signed(authority,tmp_path);resource(store);package,staging=candidate(store)
    service=TwinImportLifecycleService();preview=service.delete_preview
    def revoke_after_validation(run_id):
        result=preview(run_id)
        store.revoke_offline('synthetic-human','synthetic-workspace')
        return result
    monkeypatch.setattr(service,'delete_preview',revoke_after_validation)
    denied=False
    try:service.delete_candidate(package.import_run_id,'synthetic-human','DELETE CANDIDATE IMPORT',headers=headers)
    except PermissionError:denied=True
    observe(tmp_path,denied=denied,revoked_session_resolves=security.verified_context(headers) is not None,
        candidate_data_preserved=staging.exists(),package_preserved=service.registry.get(package.package_ref) is not None)
    assert denied and staging.exists() and service.registry.get(package.package_ref) is not None


def test_candidate_deletion_audit_failure_preserves_protected_data(authority,tmp_path,monkeypatch):
    store,_,_,headers,_=signed(authority,tmp_path);resource(store);package,staging=candidate(store)
    before=hashes(store.path.parent.parent);append=BlueprintImportLedger.append
    def fail(self,event,*args,**kwargs):
        if event=='candidate_import_deleted':raise OSError('synthetic mandatory deletion audit failure')
        return append(self,event,*args,**kwargs)
    monkeypatch.setattr(BlueprintImportLedger,'append',fail)
    with pytest.raises(OSError,match='synthetic mandatory deletion audit failure'):
        TwinImportLifecycleService().delete_candidate(package.import_run_id,'synthetic-human','DELETE CANDIDATE IMPORT',headers=headers)
    after=hashes(store.path.parent.parent)
    observe(tmp_path,staged_data_preserved=staging.exists(),package_preserved=BlueprintPackageRegistry().get(package.package_ref) is not None,
        protected_store_unchanged=before==after,before_sha256=before,after_sha256=after)
    assert before==after


def test_valid_json_manifest_omission_cannot_silently_delete_snapshot_data(authority,tmp_path):
    store,_,_,headers,_=signed(authority,tmp_path);resource(store)
    root=store.path.parent.parent;victim=root/'synthetic-manifest-victim.json';victim.write_text('original protected synthetic data')
    before=hashes(root);journal=ProtectedJournal(store)
    with pytest.raises(sqlite3.OperationalError,match='synthetic failed protected transaction'):
        with store.transaction() as db:
            journal.begin(db)
            manifest=json.loads((journal.path/'manifest.json').read_text())
            manifest['files'].pop(victim.name)
            # The backup remains present. Only its index reference is corrupted;
            # the JSON is valid and all remaining listed hashes remain valid.
            with (journal.path/'manifest.json').open('w') as handle:
                json.dump(manifest,handle,sort_keys=True);handle.flush();os.fsync(handle.fileno())
            raise sqlite3.OperationalError('synthetic failed protected transaction')
    after=hashes(root)
    observe(tmp_path,original_snapshot_file_preserved=victim.exists(),journal_retained=journal.path.exists(),
        authority_still_valid=security.verified_context(headers) is not None,protected_store_unchanged=before==after,
        before_sha256=before,after_sha256=after)
    assert victim.exists() and victim.read_text()=='original protected synthetic data'


def test_completed_promotion_cannot_be_deleted_using_stale_candidate_preview(authority,tmp_path,monkeypatch):
    from tests.test_flora_security_admin_policy import plan_for
    from cios.applications.flora.blueprint_import.promotion import CanonicalPromotionService
    store,_,_,headers,_=signed(authority,tmp_path);resource(store)
    package,review_plan=plan_for(headers)
    promotion=CanonicalPromotionService()
    approval=promotion.approve_plan(package.import_run_id,review_plan.plan_id,'synthetic-human','Synthetic explicit promotion approval',headers)
    deletion=TwinImportLifecycleService();preview=deletion.delete_preview;promoted=[]
    def promote_after_preview(run_id):
        result=preview(run_id);assert result['permitted'] and not result['promoted']
        promoted.append(promotion.execute_approved_plan(run_id,approval.approval_id,'synthetic-human',headers))
        return result
    monkeypatch.setattr(deletion,'delete_preview',promote_after_preview)
    denied=False
    try:deletion.delete_candidate(package.import_run_id,'synthetic-human','DELETE CANDIDATE IMPORT',headers=headers)
    except (PermissionError,ValueError):denied=True
    assert promoted[0].final_execution_status=='succeeded' and promoted[0].actual_mutation_count==1
    archive=store.path.parent.parent/package.archive_path
    present=deletion.registry.get(package.package_ref) is not None
    observe(tmp_path,promotion_succeeded=True,canonical_mutation_count=promoted[0].actual_mutation_count,
        deletion_denied=denied,source_archive_preserved=archive.exists(),package_preserved=present)
    assert denied and archive.exists() and present


def test_financial_apply_validates_actual_canonical_enterprise_target(authority,tmp_path):
    from tests.test_flora_ai_financial_report_review import fact
    from cios.applications.flora import document_review
    from cios.applications.flora.memory.repository import EvidenceRepository,EnterpriseModelRepository
    store,_,_,headers,_=signed(authority,tmp_path);run,acl=resource(store)
    other=replace(acl,canvas_id='synthetic-other-canvas',enterprise_id='other-enterprise',workspace_id='other-workspace',
        owner_account='other-human',acl=({'principal_id':'other-human'},))
    EnterpriseCanvasAccessRepository().save(other)
    assert not can_access_canvas_record(headers,'other-enterprise')
    claim=document_review.fact_to_review_claim(fact(canonical_enterprise_id='other-enterprise',
        subject_name='Other Synthetic Enterprise',source_excerpt='Other Synthetic Enterprise reported revenue of £20.4bn in FY26.'),'fi-synthetic')
    claim.update(review_state='accept',enterprise_id='synthetic-enterprise')
    run.update(document={'enterprise_id':'synthetic-enterprise','workspace_id':'synthetic-workspace',
        'document_id':'synthetic-document','title':'Synthetic approved financial report','source_url':'https://example.invalid/synthetic-report.pdf','checksum':'synthetic-checksum'},claims=[claim])
    document_review._write_json(document_review._run_path('fi-synthetic'),run)
    before=hashes(store.path.parent.parent);denied=False
    try:document_review.apply_accepted('fi-synthetic',headers=headers)
    except PermissionError:denied=True
    saved=EvidenceRepository().get(claim['evidence_id'])
    changed=bool(EnterpriseModelRepository().get('other-enterprise').attributes)
    after=hashes(store.path.parent.parent)
    observe(tmp_path,run_enterprise='synthetic-enterprise',claim_enterprise_alias='synthetic-enterprise',
        actual_canonical_target='other-enterprise',target_workspace='other-workspace',target_acl_denied=True,
        operation_denied=denied,foreign_enterprise_evidence_written=bool(saved and saved.get('enterprise_id')=='other-enterprise'),
        foreign_enterprise_model_changed=changed,protected_store_unchanged=before==after)
    assert denied and before==after
