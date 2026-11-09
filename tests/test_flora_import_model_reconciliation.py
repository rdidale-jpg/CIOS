"""Approved import -> canonical Observation -> existing model/consumer regressions."""
import json

import pytest

from cios.applications.flora.blueprint_import import BlueprintPackageRegistry, BlueprintPackageValidator, CandidateReviewService, DryRunPlanningService
from cios.applications.flora.blueprint_import.promotion import CanonicalPromotionService, BlueprintPromotionError
from cios.applications.flora.memory.repository import EnterpriseModelRepository, ObservationRepository, EvidenceRepository
from cios.applications.flora.memory.service import ObservationMemoryService
from cios.applications.flora.enterprise_intelligence.models import ReasoningRequestV1
from cios.applications.flora.enterprise_intelligence.retrieval import BoundedTwinRetrievalService
from tests.test_flora_blueprint_import_validation import pkg

ENT='synthetic-enterprise'
ATTR='financial_performance.metrics.revenue.FY26.actual'
HEADERS={'X-Flora-User':'alice','X-Flora-Enterprises':ENT,'X-Flora-Roles':'package.review,candidate.promote','X-Flora-Active-Workspace':ENT}


def records(value=120, eid='EV-1', oid='OBS-1', period='FY26', **changes):
    observation=dict(observation_id=oid,enterprise_id=ENT,observation_type='financial_metric_reported',
        atomic_statement=f'Synthetic Airline reported revenue of £{value}m for {period}.',
        observation_date='2026-10-01',collection_date='2026-10-02',evidence_publication_date='2026-10-01',
        affected_attribute=f'financial_performance.metrics.revenue.{period}.actual',confidence=80,
        supporting_evidence_ids=[eid],period=period)
    observation.update(changes)
    evidence=dict(evidence_id=eid,enterprise_id=ENT,summary=observation['atomic_statement'],publication_date='2026-10-01')
    return [dict(external_id=eid,record_class='evidence',truth_class='evidence_backed',payload=evidence),
            dict(external_id=oid,record_class='observation',truth_class='observed',payload=observation)]


def stage(monkeypatch,tmp_path,rows,version='1',review=True):
    monkeypatch.setenv('FLORA_DATA_DIR',str(tmp_path));monkeypatch.setenv('FLORA_PILOT_DIR',str(tmp_path))
    package=BlueprintPackageRegistry().receive(pkg(records=rows,manifest_extra={'package_version':version+'.0.0'}), 'synthetic.zip','alice',ENT)
    validator=BlueprintPackageValidator();validator.validate_and_stage(package.package_ref,'alice',HEADERS)
    candidates=validator.staging_summary(package.import_run_id)['candidates']
    if review:
        for candidate in candidates:
            CandidateReviewService().record_decision(candidate['candidate_record_id'],'approve','alice','Synthetic owner-approved fact',HEADERS)
        plan=DryRunPlanningService().create_plan(package.import_run_id,'alice',HEADERS)
        return package,plan
    return package,None


def promote(monkeypatch,tmp_path,rows=None,version='1'):
    package,plan=stage(monkeypatch,tmp_path,records() if rows is None else rows,version)
    service=CanonicalPromotionService()
    approval=service.approve_plan(package.import_run_id,plan.plan_id,'alice','Synthetic governed import',HEADERS)
    result=service.execute_approved_plan(package.import_run_id,approval.approval_id,'alice',HEADERS)
    return package,approval,result


def retrieval():
    return BoundedTwinRetrievalService().retrieve(ReasoningRequestV1.create(ENT,ENT,'alice',evidence_cut_off='2026-11-08'))


def test_approved_financial_import_reaches_model_retrieval_and_canvas(monkeypatch,tmp_path):
    package,approval,result=promote(monkeypatch,tmp_path)
    model=EnterpriseModelRepository().get(ENT)
    assert model.attributes[ATTR].current_value=='120000000'
    assert result.model_projection_status=='complete'
    assert model.attributes[ATTR].observation_ids==('OBS-1',)
    assert model.attributes[ATTR].evidence_ids==('EV-1',)
    obs=ObservationRepository().get('OBS-1')
    assert obs.human_provenance['blueprint_import_lineage']['approval_id']==approval.approval_id
    assert obs.observation_date=='2026-10-01' and obs.collection_date=='2026-10-02'
    assert obs.human_provenance['effective_period']=='FY26'
    text=json.dumps(retrieval().to_dict())
    assert '120000000' in text and 'EV-1' in text and 'OBS-1' in text
    from cios.applications.flora.enterprise_canvas.access import repair_blueprint_canvas_access
    from cios.applications.flora.enterprise_canvas.service import EnterpriseCanvasService
    repair_blueprint_canvas_access(package.import_run_id,HEADERS)
    canvas=EnterpriseCanvasService().get_canvas(ENT,HEADERS)
    assert any('120000000' in str(tile.core_facts) for tile in canvas.tiles)
    assert all(not tile.analytical_projections for tile in canvas.tiles)
    assert not (tmp_path/'memory'/'opportunity.jsonl').exists()
    assert not (tmp_path/'memory'/'material_pressure.jsonl').exists()


def test_receipt_staging_review_dry_run_and_approval_do_not_mutate_model(monkeypatch,tmp_path):
    package,_=stage(monkeypatch,tmp_path,records(),review=False)
    assert not (tmp_path/'memory').exists()
    candidates=BlueprintPackageValidator().staging_summary(package.import_run_id)['candidates']
    for candidate in candidates:
        CandidateReviewService().record_decision(candidate['candidate_record_id'],'approve','alice','Review only',HEADERS)
    plan=DryRunPlanningService().create_plan(package.import_run_id,'alice',HEADERS)
    CanonicalPromotionService().approve_plan(package.import_run_id,plan.plan_id,'alice','Approval only',HEADERS)
    assert not (tmp_path/'memory').exists()


def test_identical_reimport_and_repeat_execution_are_idempotent(monkeypatch,tmp_path):
    package,approval,_=promote(monkeypatch,tmp_path)
    before=EnterpriseModelRepository().get(ENT).to_dict()
    repeat=CanonicalPromotionService().execute_approved_plan(package.import_run_id,approval.approval_id,'alice',HEADERS)
    assert repeat.final_execution_status=='repeat_no_change'
    promote(monkeypatch,tmp_path,version='2')
    assert len(ObservationRepository().list())==1
    assert EnterpriseModelRepository().get(ENT).to_dict()==before


def test_corroborating_import_merges_evidence_without_duplicate_confidence(monkeypatch,tmp_path):
    promote(monkeypatch,tmp_path)
    promote(monkeypatch,tmp_path,records(eid='EV-2',oid='OBS-2'),version='2')
    assert len(ObservationRepository().list())==1
    attribute=EnterpriseModelRepository().get(ENT).attributes[ATTR]
    assert set(attribute.evidence_ids)=={'EV-1','EV-2'}
    assert len(attribute.confidence_history)==1


def test_same_period_conflict_preserves_both_positions_and_reasoning_visibility(monkeypatch,tmp_path):
    promote(monkeypatch,tmp_path)
    promote(monkeypatch,tmp_path,records(value=100,eid='EV-2',oid='OBS-2'),version='2')
    assert len(ObservationRepository().list())==2
    assert EnterpriseModelRepository().get(ENT).attributes[ATTR].contradiction_state!='none'
    assert {i.stable_id for i in retrieval().selected_contradictions}=={'OBS-1','OBS-2'}


def test_different_period_is_not_a_conflict(monkeypatch,tmp_path):
    promote(monkeypatch,tmp_path)
    promote(monkeypatch,tmp_path,records(value=100,eid='EV-2',oid='OBS-2',period='FY27'),version='2')
    attrs=EnterpriseModelRepository().get(ENT).attributes
    assert len(attrs)==2 and all(a.contradiction_state=='none' for a in attrs.values())


def test_retirement_updates_history_without_remaining_current_support(monkeypatch,tmp_path):
    promote(monkeypatch,tmp_path)
    rows=records(lifecycle_state='retired',retired_at='2026-10-05',proposed_effect='update')
    promote(monkeypatch,tmp_path,rows,version='2')
    assert ObservationRepository().get('OBS-1').lifecycle_state=='retired'
    assert EnterpriseModelRepository().get(ENT).attributes[ATTR].trust_state=='retired'
    assert not retrieval().selected_entities_and_relationships
    assert not any(i.object_class=='observation' for i in retrieval().selected_observations)


def test_supersession_keeps_old_record_without_reintroducing_old_truth(monkeypatch,tmp_path):
    promote(monkeypatch,tmp_path)
    promote(monkeypatch,tmp_path,records(value=100,eid='EV-2',oid='OBS-2',supersedes_observation_id='OBS-1'),version='2')
    assert ObservationRepository().get('OBS-1') is not None
    assert EnterpriseModelRepository().get(ENT).attributes[ATTR].current_value=='100000000'
    assert {i.stable_id for i in retrieval().selected_observations if i.object_class=='observation'}=={'OBS-2'}


def test_unsupported_mapping_is_canonical_but_explicitly_partial(monkeypatch,tmp_path):
    package,_,result=promote(monkeypatch,tmp_path,records(observation_type='fact',affected_attribute='unowned.custom'))
    assert ObservationRepository().get('OBS-1') is not None
    assert not EnterpriseModelRepository().get(ENT).attributes
    assert result.model_projection_status=='partial'
    assert any('unsupported' in row.get('reason','').lower() for row in result.model_projection_results)
    from cios.applications.flora.blueprint_import.views import completion_page
    html=completion_page(package.import_run_id,result.to_dict(),HEADERS)
    assert 'partial' in html.lower() and 'unsupported' in html.lower()


def test_missing_support_is_not_invented_for_projection(monkeypatch,tmp_path):
    rows=records();rows[1]['payload']['supporting_evidence_ids']=['MISSING']
    _,_,result=promote(monkeypatch,tmp_path,rows)
    assert ObservationRepository().get('OBS-1') is not None
    assert not EnterpriseModelRepository().get(ENT).attributes
    assert result.model_projection_status=='partial'


def test_projection_failure_restores_canonical_files_models_and_can_retry(monkeypatch,tmp_path):
    promote(monkeypatch,tmp_path)
    before=EnterpriseModelRepository().get(ENT).to_dict()
    obs_before=ObservationRepository().path.read_bytes();ev_before=EvidenceRepository().path.read_bytes()
    package,plan=stage(monkeypatch,tmp_path,records(value=100,eid='EV-2',oid='OBS-2'),version='2')
    service=CanonicalPromotionService()
    approval=service.approve_plan(package.import_run_id,plan.plan_id,'alice','Synthetic retry case',HEADERS)
    original=ObservationMemoryService.apply_observation
    def fail_after_write(self,observation):
        original(self,observation)
        raise OSError('Synthetic projection write failure')
    monkeypatch.setattr(ObservationMemoryService,'apply_observation',fail_after_write)
    with pytest.raises(BlueprintPromotionError):
        service.execute_approved_plan(package.import_run_id,approval.approval_id,'alice',HEADERS)
    assert EnterpriseModelRepository().get(ENT).to_dict()==before
    assert ObservationRepository().path.read_bytes()==obs_before
    assert EvidenceRepository().path.read_bytes()==ev_before
    assert service.repo.successful_for(package.import_run_id,plan.plan_id,approval.approval_id) is None
    monkeypatch.setattr(ObservationMemoryService,'apply_observation',original)
    assert service.execute_approved_plan(package.import_run_id,approval.approval_id,'alice',HEADERS).model_projection_status=='complete'


def test_success_receipt_write_failure_is_compensated(monkeypatch,tmp_path):
    package,plan=stage(monkeypatch,tmp_path,records())
    service=CanonicalPromotionService();approval=service.approve_plan(package.import_run_id,plan.plan_id,'alice','Receipt failure',HEADERS)
    original=service.repo.save_result
    def fail_success(run,result):
        if result.final_execution_status=='succeeded': raise OSError('Synthetic receipt failure')
        return original(run,result)
    monkeypatch.setattr(service.repo,'save_result',fail_success)
    with pytest.raises(BlueprintPromotionError): service.execute_approved_plan(package.import_run_id,approval.approval_id,'alice',HEADERS)
    assert not EnterpriseModelRepository().get(ENT).attributes
    assert not ObservationRepository().list()
    assert not EvidenceRepository().list()


def test_record_target_requires_its_own_enterprise_authorisation(monkeypatch,tmp_path):
    rows=records(enterprise_id='other-enterprise')
    package,plan=stage(monkeypatch,tmp_path,rows)
    with pytest.raises(BlueprintPromotionError):
        service=CanonicalPromotionService();approval=service.approve_plan(package.import_run_id,plan.plan_id,'alice','Wrong enterprise',HEADERS)
        service.execute_approved_plan(package.import_run_id,approval.approval_id,'alice',HEADERS)
    assert not ObservationRepository().list() and not EvidenceRepository().list()


def test_existing_evidence_owner_cannot_be_overwritten_by_id_collision(monkeypatch,tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR',str(tmp_path))
    EvidenceRepository().save({'evidence_id':'EV-1','enterprise_id':'other-enterprise','summary':'Unrelated canonical fact'})
    before=EvidenceRepository().path.read_bytes()
    package,plan=stage(monkeypatch,tmp_path,records())
    with pytest.raises(BlueprintPromotionError):
        service=CanonicalPromotionService();approval=service.approve_plan(package.import_run_id,plan.plan_id,'alice','Wrong owner',HEADERS)
        service.execute_approved_plan(package.import_run_id,approval.approval_id,'alice',HEADERS)
    assert EvidenceRepository().path.read_bytes()==before
    assert not EnterpriseModelRepository().get(ENT).attributes


def test_supplied_fingerprint_cannot_merge_another_enterprises_observation(monkeypatch,tmp_path):
    from cios.applications.flora.memory.models import Observation
    monkeypatch.setenv('FLORA_DATA_DIR',str(tmp_path))
    other=Observation('other-enterprise','fact','Other enterprise owns this fact.','2026-10-01','2026-10-02','identity.other',80,('OTHER-EV',))
    ObservationRepository().save(other);before=ObservationRepository().path.read_bytes()
    package,plan=stage(monkeypatch,tmp_path,records(observation_fingerprint=other.observation_fingerprint))
    with pytest.raises(BlueprintPromotionError):
        service=CanonicalPromotionService();approval=service.approve_plan(package.import_run_id,plan.plan_id,'alice','Wrong fingerprint',HEADERS)
        service.execute_approved_plan(package.import_run_id,approval.approval_id,'alice',HEADERS)
    assert ObservationRepository().path.read_bytes()==before


def test_reversed_record_order_still_resolves_evidence_before_projection(monkeypatch,tmp_path):
    promote(monkeypatch,tmp_path,list(reversed(records())))
    assert EnterpriseModelRepository().get(ENT).attributes[ATTR].current_value=='120000000'


def test_only_affected_enterprise_snapshot_is_written(monkeypatch,tmp_path):
    from cios.applications.flora.memory.models import EnterpriseModel
    monkeypatch.setenv('FLORA_DATA_DIR',str(tmp_path))
    repo=EnterpriseModelRepository();repo.save(EnterpriseModel('unaffected-enterprise'))
    before=repo.path_for('unaffected-enterprise').read_bytes()
    promote(monkeypatch,tmp_path)
    assert repo.path_for('unaffected-enterprise').read_bytes()==before


def test_expired_approved_update_is_inactive_in_model_and_canvas(monkeypatch,tmp_path):
    package,_,_=promote(monkeypatch,tmp_path)
    promote(monkeypatch,tmp_path,records(freshness='expired',proposed_effect='update'),version='2')
    assert ObservationRepository().get('OBS-1').freshness=='expired'
    assert EnterpriseModelRepository().get(ENT).attributes[ATTR].trust_state=='retired'
    from cios.applications.flora.enterprise_canvas.access import repair_blueprint_canvas_access
    from cios.applications.flora.enterprise_canvas.service import EnterpriseCanvasService
    repair_blueprint_canvas_access(package.import_run_id,HEADERS)
    canvas=EnterpriseCanvasService().get_canvas(ENT,HEADERS)
    assert not any('120000000' in str(tile.core_facts) for tile in canvas.tiles)


def test_reimporting_superseded_fact_cannot_restore_old_truth(monkeypatch,tmp_path):
    promote(monkeypatch,tmp_path)
    promote(monkeypatch,tmp_path,records(value=100,eid='EV-2',oid='OBS-2',supersedes_observation_id='OBS-1'),version='2')
    promote(monkeypatch,tmp_path,version='3')
    assert EnterpriseModelRepository().get(ENT).attributes[ATTR].current_value=='100000000'
    assert len(ObservationRepository().list())==2


def test_existing_observation_id_cannot_be_reused_for_a_different_fact(monkeypatch,tmp_path):
    promote(monkeypatch,tmp_path)
    before=EnterpriseModelRepository().get(ENT).to_dict()
    package,plan=stage(monkeypatch,tmp_path,records(value=100,eid='EV-2',oid='OBS-1'),version='2')
    with pytest.raises(BlueprintPromotionError,match='different canonical assertion'):
        CanonicalPromotionService().approve_plan(package.import_run_id,plan.plan_id,'alice','Changed identity',HEADERS)
    assert EnterpriseModelRepository().get(ENT).to_dict()==before
    assert EvidenceRepository().get('EV-2') is None


def test_future_observation_is_canonical_history_not_current_model(monkeypatch,tmp_path):
    _,_,result=promote(monkeypatch,tmp_path,records(observation_date='2099-10-01'))
    assert ObservationRepository().get('OBS-1') is not None
    assert not EnterpriseModelRepository().get(ENT).attributes
    assert result.model_projection_results[0]['status']=='historical'


def test_cross_enterprise_support_is_reported_without_model_write(monkeypatch,tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR',str(tmp_path))
    EvidenceRepository().save({'evidence_id':'OTHER-EV','enterprise_id':'other-enterprise','summary':'Other enterprise fact'})
    rows=records();rows[1]['payload']['supporting_evidence_ids']=['OTHER-EV']
    _,_,result=promote(monkeypatch,tmp_path,rows)
    assert result.model_projection_status=='partial'
    assert not EnterpriseModelRepository().get(ENT).attributes
    assert 'ownership' in result.model_projection_results[0]['reason']


def test_running_receipt_blocks_retry_without_new_canonical_writes(monkeypatch,tmp_path):
    from cios.applications.flora.blueprint_import.promotion import CanonicalPromotionResult,_execution_id
    package,plan=stage(monkeypatch,tmp_path,records())
    service=CanonicalPromotionService();approval=service.approve_plan(package.import_run_id,plan.plan_id,'alice','Interrupted run',HEADERS)
    service.repo.save_result(package.import_run_id,CanonicalPromotionResult('1.0',_execution_id(plan.plan_id,approval.approval_id),plan.plan_id,approval.approval_id,'alice','start','',final_execution_status='running'))
    with pytest.raises(BlueprintPromotionError,match='recovery'):
        service.execute_approved_plan(package.import_run_id,approval.approval_id,'alice',HEADERS)
    assert not ObservationRepository().list() and not EnterpriseModelRepository().get(ENT).attributes


def test_failed_compensation_is_not_successful_and_blocks_automatic_retry(monkeypatch,tmp_path):
    package,plan=stage(monkeypatch,tmp_path,records())
    service=CanonicalPromotionService();approval=service.approve_plan(package.import_run_id,plan.plan_id,'alice','Recovery boundary',HEADERS)
    def fail_projection(_): raise OSError('Synthetic projection failure')
    def fail_restore(_): raise OSError('Synthetic restore failure')
    monkeypatch.setattr(service,'_project_observation',fail_projection)
    monkeypatch.setattr(service,'_restore_paths',fail_restore)
    with pytest.raises(BlueprintPromotionError,match='recovery'):
        service.execute_approved_plan(package.import_run_id,approval.approval_id,'alice',HEADERS)
    assert service.repo.successful_for(package.import_run_id,plan.plan_id,approval.approval_id) is None
    paths=list(service.repo._execution_dir(package.import_run_id).glob('*.json'))
    result=json.loads(paths[0].read_text())
    assert result['rollback_or_compensation_result']=='recovery_required'
    assert result['model_projection_status']=='failed'
    with pytest.raises(BlueprintPromotionError,match='recovery'):
        service.execute_approved_plan(package.import_run_id,approval.approval_id,'alice',HEADERS)


def test_audit_failure_is_compensated_instead_of_leaving_success_receipt(monkeypatch,tmp_path):
    package,plan=stage(monkeypatch,tmp_path,records())
    service=CanonicalPromotionService();approval=service.approve_plan(package.import_run_id,plan.plan_id,'alice','Audit failure',HEADERS)
    original=service.ledger.append
    def fail_success(event,payload):
        if payload.get('final_execution_status')=='succeeded': raise OSError('Synthetic audit failure')
        return original(event,payload)
    monkeypatch.setattr(service.ledger,'append',fail_success)
    with pytest.raises(BlueprintPromotionError): service.execute_approved_plan(package.import_run_id,approval.approval_id,'alice',HEADERS)
    assert not ObservationRepository().list() and not EnterpriseModelRepository().get(ENT).attributes
    assert service.repo.successful_for(package.import_run_id,plan.plan_id,approval.approval_id) is None


def test_evidence_only_import_does_not_invent_model_observation(monkeypatch,tmp_path):
    _,_,result=promote(monkeypatch,tmp_path,records()[:1])
    assert result.model_projection_status=='not_applicable'
    assert EvidenceRepository().get('EV-1') is not None
    assert not ObservationRepository().list() and not EnterpriseModelRepository().get(ENT).attributes


def test_non_promotable_class_is_reported_without_becoming_model_truth(monkeypatch,tmp_path):
    rows=[{'external_id':'WRAPPER','record_class':'enterprise_twin','truth_class':'observed','payload':{'name':'Synthetic Airline'}}]
    _,_,result=promote(monkeypatch,tmp_path,rows)
    assert any('enterprise_twin' in value for value in result.records_skipped)
    assert not ObservationRepository().list() and not EnterpriseModelRepository().get(ENT).attributes


def test_same_batch_supersession_is_independent_of_projection_order(monkeypatch,tmp_path):
    first=records()
    second=records(value=100,eid='EV-2',oid='OBS-2',supersedes_observation_id='OBS-1')
    promote(monkeypatch,tmp_path,second+first)
    attr=EnterpriseModelRepository().get(ENT).attributes[ATTR]
    assert attr.current_value=='100000000' and attr.trust_state=='trusted'
    assert attr.contradiction_state=='none'
    assert len(ObservationRepository().list())==2


def test_retirement_of_old_claim_does_not_retire_new_current_value(monkeypatch,tmp_path):
    promote(monkeypatch,tmp_path)
    promote(monkeypatch,tmp_path,records(value=100,eid='EV-2',oid='OBS-2',supersedes_observation_id='OBS-1'),version='2')
    promote(monkeypatch,tmp_path,records(lifecycle_state='retired',proposed_effect='update'),version='3')
    current=EnterpriseModelRepository().get(ENT).attributes[ATTR]
    assert current.current_value=='100000000' and current.trust_state=='trusted'


def test_generic_payload_identifier_collision_is_also_owner_checked(monkeypatch,tmp_path):
    from cios.applications.flora.blueprint_import.promotion import CanonicalJsonlRepository
    monkeypatch.setenv('FLORA_DATA_DIR',str(tmp_path))
    repo=CanonicalJsonlRepository('entity');repo.save({'canonical_id':'ENTITY-OTHER','entity_id':'ENTITY-OTHER','enterprise_id':'other-enterprise','workspace_id':ENT})
    before=repo.path.read_bytes()
    rows=[dict(external_id='DIFFERENT-EXTERNAL-ID',record_class='entity',truth_class='entity',payload={'entity_id':'ENTITY-OTHER'})]
    package,plan=stage(monkeypatch,tmp_path,rows)
    with pytest.raises(BlueprintPromotionError,match='owner'):
        CanonicalPromotionService().approve_plan(package.import_run_id,plan.plan_id,'alice','Collision test',HEADERS)
    assert repo.path.read_bytes()==before


def test_expired_evidence_is_not_projected_as_current_support(monkeypatch,tmp_path):
    rows=records();rows[0]['payload']['freshness']='expired'
    _,_,result=promote(monkeypatch,tmp_path,rows)
    assert result.model_projection_status=='partial'
    assert not EnterpriseModelRepository().get(ENT).attributes


def test_execute_rechecks_target_authorisation_after_approval(monkeypatch,tmp_path):
    package,plan=stage(monkeypatch,tmp_path,records())
    service=CanonicalPromotionService();approval=service.approve_plan(package.import_run_id,plan.plan_id,'alice','Scope revocation',HEADERS)
    with pytest.raises(BlueprintPromotionError):
        service.execute_approved_plan(package.import_run_id,approval.approval_id,'alice',HEADERS|{'X-Flora-Enterprises':'other-enterprise'})
    assert not ObservationRepository().list() and not EnterpriseModelRepository().get(ENT).attributes


def test_lifecycle_correction_preserves_prior_acceptance_and_approval_lineage(monkeypatch,tmp_path):
    _,first,_=promote(monkeypatch,tmp_path)
    _,second,_=promote(monkeypatch,tmp_path,records(lifecycle_state='retired',proposed_effect='update'),version='2')
    row=ObservationRepository().get('OBS-1')
    assert row.human_provenance['blueprint_import_lineage']['approval_id']==first.approval_id
    assert row.human_provenance['lifecycle_import_lineage']['approval_id']==second.approval_id
    assert row.human_provenance['lifecycle_history'][0]['prior_state']['lifecycle_state']=='accepted'
    assert row.atomic_statement=='Synthetic Airline reported revenue of £120m for FY26.'


def test_importer_lock_fails_closed_without_model_mutation(monkeypatch,tmp_path):
    from cios.applications.flora.blueprint_import.promotion import _PROMOTION_LOCK
    package,plan=stage(monkeypatch,tmp_path,records())
    service=CanonicalPromotionService();approval=service.approve_plan(package.import_run_id,plan.plan_id,'alice','Serial writer test',HEADERS)
    _PROMOTION_LOCK.acquire()
    try:
        with pytest.raises(BlueprintPromotionError,match='running'):
            service.execute_approved_plan(package.import_run_id,approval.approval_id,'alice',HEADERS)
    finally: _PROMOTION_LOCK.release()
    assert not ObservationRepository().list() and not EnterpriseModelRepository().get(ENT).attributes


def test_projection_limitations_and_completion_survive_receipt_reload(monkeypatch,tmp_path):
    package,approval,first=promote(monkeypatch,tmp_path,records(observation_type='fact',affected_attribute='unowned.custom'))
    repeat=CanonicalPromotionService().execute_approved_plan(package.import_run_id,approval.approval_id,'alice',HEADERS)
    assert repeat.final_execution_status=='repeat_no_change' and repeat.model_projection_status=='partial'
    assert repeat.model_projection_results==first.to_dict()['model_projection_results']
