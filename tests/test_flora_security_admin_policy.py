"""Real stored administrator policy, resource scopes and no blanket bypass."""
from dataclasses import replace
import json
import pytest
from tests.test_flora_security_repair_01b import authority, signed
from tests.test_flora_security_workspace_boundary import hashes, resource, assert_unchanged
from tests.test_flora_blueprint_import_validation import pkg
from cios.applications.flora import access,security
from cios.applications.flora.security_store import canonical
from cios.applications.flora.blueprint_import import BlueprintPackageRegistry,BlueprintPackageValidator,CandidateReviewService,ImportMappingService,DryRunPlanningService
from cios.applications.flora.blueprint_import.promotion import CanonicalPromotionService,can_approve_blueprint_promotion,can_execute_blueprint_promotion
from cios.applications.flora.enterprise_canvas.access import EnterpriseCanvasAccessRepository

pytestmark=pytest.mark.real_security_boundary


def administrator(authority,tmp_path,role='blueprint_import_admin'):
    store,token,csrf,headers,old=signed(authority,tmp_path)
    # Explicit test-only server administration of an existing approved binding.
    # No browser assertion or environment variable supplies this assignment.
    with store.transaction() as db:
        db.execute('UPDATE memberships SET roles=?,version=version+1',(canonical([role]),))
        store.audit(db,'synthetic_role_assignment',user_id='synthetic-human',role=role)
    return store,headers


def plan_for(headers,workspace='synthetic-workspace',target='synthetic-enterprise'):
    content=pkg(records=[{'external_id':'EV-ADMIN','record_class':'evidence','truth_class':'evidence_backed','payload':{'quote':'Synthetic administrator-reviewed evidence','enterprise_id':target}}])
    reg=BlueprintPackageRegistry();package=reg.receive(content,'synthetic-admin.zip','synthetic-human',workspace)
    BlueprintPackageValidator().validate_and_stage(package.package_ref,'synthetic-human',headers)
    candidate=BlueprintPackageValidator().staging_summary(package.import_run_id)['candidates'][0]
    CandidateReviewService().record_decision(candidate['candidate_record_id'],'approve','synthetic-human','Explicit synthetic evidence review',headers)
    ImportMappingService().record_mapping(candidate,'propose_create','synthetic-human',headers,'Evidence')
    plan=DryRunPlanningService().create_plan(package.import_run_id,'synthetic-human',headers)
    return package,plan


def test_real_administrator_policy_and_service_allow_scoped_promotion(authority,tmp_path):
    store,headers=administrator(authority,tmp_path)
    _,record=resource(store)
    context=security.verified_context(headers)
    assert context.roles==frozenset({'blueprint_import_admin'})
    assert 'candidate.promote' in context.effective_capabilities
    assert not access.is_cios_owner(headers)
    assert can_approve_blueprint_promotion(headers,'synthetic-enterprise')
    assert can_execute_blueprint_promotion(headers,'synthetic-enterprise')
    with pytest.raises(PermissionError):access.require_capability(headers,'storage.recover')
    with pytest.raises(PermissionError):access.require_capability(headers,'commercial_context.edit')
    package,plan=plan_for(headers)
    service=CanonicalPromotionService()
    approval=service.approve_plan(package.import_run_id,plan.plan_id,'synthetic-human','Explicit synthetic administrator approval',headers)
    result=service.execute_approved_plan(package.import_run_id,approval.approval_id,'synthetic-human',headers)
    assert result.final_execution_status=='succeeded' and result.actual_mutation_count==1
    assert result.actor==approval.approver_identity=='synthetic-human'


@pytest.mark.parametrize('case',['reviewer-only','missing-membership','wrong-workspace','missing-scope','conflicting-acl','missing-acl-principal','wrong-enterprise'])
def test_administrator_cannot_bypass_membership_scope_or_acl(authority,tmp_path,case):
    store,headers=administrator(authority,tmp_path)
    _,record=resource(store)
    package,plan=plan_for(headers)
    reg=BlueprintPackageRegistry()
    package_path=store.path.parent.parent/'blueprint_import/packages'/f'{package.package_ref}.json'
    if case in {'wrong-workspace','missing-scope'}:
        persisted=json.loads(package_path.read_text())
        persisted['workspace_id']='other-workspace' if case=='wrong-workspace' else ''
        package_path.write_text(json.dumps(persisted))
    repo=EnterpriseCanvasAccessRepository()
    if case=='conflicting-acl':repo.save(replace(record,workspace_id='other-workspace'))
    if case=='missing-acl-principal':repo.save(replace(record,owner_account='other-human',acl=({'principal_id':'other-human'},)))
    with store.transaction() as db:
        if case=='reviewer-only':db.execute('UPDATE memberships SET roles=?',(canonical(['package.review']),))
        if case=='missing-membership':db.execute('UPDATE memberships SET active=0,version=version+1')
        if case=='wrong-enterprise':db.execute('UPDATE memberships SET enterprises=?',(canonical(['other-enterprise']),))
    before=hashes(store.path.parent.parent)
    if case in {'reviewer-only','missing-membership','wrong-enterprise'}:
        assert not can_approve_blueprint_promotion(headers,'synthetic-enterprise')
    with pytest.raises(PermissionError):
        CanonicalPromotionService().approve_plan(package.import_run_id,plan.plan_id,'synthetic-human','Denied synthetic attempt',headers)
    assert_unchanged(store,before,tmp_path)


@pytest.mark.parametrize('case',['target-acl-workspace','target-acl-principal'])
def test_admin_enterprise_grant_does_not_bypass_canonical_target_acl(authority,tmp_path,case):
    store,headers=administrator(authority,tmp_path)
    _,record=resource(store)
    with store.transaction() as db:
        db.execute('UPDATE memberships SET enterprises=?',(canonical(['synthetic-enterprise','second-enterprise']),))
    other=replace(record,canvas_id='canvas-second',enterprise_id='second-enterprise',
        workspace_id='other-workspace' if case=='target-acl-workspace' else 'synthetic-workspace',
        owner_account='other-human',acl=({'principal_id':'other-human'},))
    EnterpriseCanvasAccessRepository().save(other)
    package,plan=plan_for(headers,target='second-enterprise')
    assert plan.expected_canonical_mutation_count==1
    assert access.can_access_enterprise(headers,'second-enterprise','synthetic-workspace')
    assert not can_approve_blueprint_promotion(headers,'second-enterprise')
    before=hashes(store.path.parent.parent)
    with pytest.raises(PermissionError,match='Resource unavailable'):
        CanonicalPromotionService().approve_plan(package.import_run_id,plan.plan_id,'synthetic-human','Denied target ACL attempt',headers)
    assert_unchanged(store,before,tmp_path)


@pytest.mark.parametrize('scope',['other-workspace','',None])
def test_existing_canonical_target_requires_authoritative_matching_scope(authority,tmp_path,scope):
    store,headers=administrator(authority,tmp_path)
    package,plan=plan_for(headers)
    effect=plan.effects[0]
    from cios.applications.flora.memory.repository import EvidenceRepository
    row={'evidence_id':effect.canonical_id,'enterprise_id':'synthetic-enterprise','quote':'Existing synthetic canonical content'}
    if scope is not None:row['workspace_id']=scope
    EvidenceRepository().save(row)
    before=hashes(store.path.parent.parent)
    with pytest.raises(PermissionError,match='workspace'):
        CanonicalPromotionService().approve_plan(package.import_run_id,plan.plan_id,'synthetic-human','Denied ambiguous target',headers)
    assert_unchanged(store,before,tmp_path)
