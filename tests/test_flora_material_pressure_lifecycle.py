"""Synthetic ADR-026 golden path; existing canonical owners and model snapshots."""
import copy
import json

import pytest

from cios.applications.flora.memory.service import ObservationMemoryService
from cios.applications.flora.memory.repository import EvidenceRepository, ObservationRepository, EnterpriseModelRepository, ContradictionRepository
from cios.applications.flora.blueprint_import.material_pressure import PressureCandidate, qualify_candidates

ENT='synthetic-pressure-airline'
TEXT=('Fuel cost inflation persists. Unhedged exposure constrains operating margin. '
      'Operating cash headroom is constrained. This constraint limits ongoing operations.')


def descriptor(**changes):
    return dict(condition='Rising aviation fuel costs',condition_concept='fuel-cost-inflation',
        condition_basis='Fuel cost inflation persists.',mechanism='Unhedged exposure constrains operating margin.',
        affected_domain='financial/economic',scope='aviation fuel cost base',time_context='2026-Q4',
        consequence='Operating cash headroom is constrained.',consequence_domain='financial/economic',
        materiality_rationale='This constraint limits ongoing operations.',
        identity_rationale='Unhedged exposure constrains operating margin.',effective_at='2026-10-01')|changes


@pytest.fixture
def memory(tmp_path,monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR',str(tmp_path));monkeypatch.setenv('FLORA_PILOT_DIR',str(tmp_path))
    return ObservationMemoryService()


def ingest(memory,eid='EV-1',statement='Synthetic fuel inflation constrains operating margin.',annotation=None,**changes):
    item=dict(evidence_id=eid,enterprise_id=ENT,organisation=ENT,source_id='SYNTHETIC',summary=TEXT,
        cleaned_observation=statement,commercial_condition='enterprise_event_announced',affected_attribute='events.pressure.fuel',
        observation_date='2026-11-01',collection_date='2026-11-02',publication_date='2026-11-01',
        extraction_timestamp='2026-11-02T12:00:00Z',confidence=85,page_number=1,period='2026-Q4',
        human_provenance={'material_pressure':descriptor() if annotation is None else annotation})|changes
    report=memory.process_evidence(item)
    assert report.factual_claims_accepted==1
    return memory.observations.get(report.results[0].observation_id)


def only_pressure(memory):
    values=memory.models.get(ENT).material_pressures
    assert len(values)==1
    return next(iter(values.values()))


def candidate(source,**changes):
    data=source.human_provenance['material_pressure']
    return PressureCandidate(source.observation_id,'observation',source.enterprise_id,data['condition'],
        data['affected_domain'],data['consequence'],data['consequence_domain'],source.supporting_evidence_ids,
        time_context=data['time_context'],**changes)


def test_verified_pressure_qualifies_and_survives_repository_reconstruction(memory):
    obs=ingest(memory)
    p=only_pressure(memory)
    assert p.qualification=='QUALIFIED'
    assert p.enterprise_id==ENT and p.evidence_refs==('EV-1',) and p.observation_refs==(obs.observation_id,)
    assert p.consequence==descriptor()['consequence'] and p.effective_at=='2026-10-01'
    assert EnterpriseModelRepository().get(ENT).material_pressures[p.pressure_id].pressure_id==p.pressure_id


def test_missing_evidence_fails_even_when_candidate_flags_are_true(memory):
    obs=ingest(memory)
    memory.evidence._rewrite([])
    result=qualify_candidates((candidate(obs),))
    assert not result.qualified and result.rejected


@pytest.mark.parametrize('field,value',[('lifecycle_state','rejected'),('lifecycle_state','quarantined'),('freshness','expired'),('status','rejected')])
def test_ineligible_evidence_is_not_current_support(memory,field,value):
    obs=ingest(memory)
    memory.evidence.save(memory.evidence.get('EV-1')|{field:value})
    result=memory.assess_material_pressure(obs.observation_id)
    assert not result.qualified
    assert only_pressure(memory).qualification!='QUALIFIED'


@pytest.mark.parametrize('state',['rejected','quarantined','retired'])
def test_ineligible_canonical_source_cannot_qualify(memory,state):
    obs=ingest(memory)
    obs.lifecycle_state=state;memory.observations._rewrite([obs])
    assert not qualify_candidates((candidate(obs),)).qualified


def test_paraphrases_reconcile_via_governed_semantic_basis_not_words(memory):
    a=ingest(memory)
    pid=only_pressure(memory).pressure_id
    b=ingest(memory,eid='EV-2',statement='Synthetic unhedged expenditure constrains margins.',
        annotation=descriptor(condition='Increased jet-fuel expenditure pressure'))
    c=ingest(memory,eid='EV-3',statement='Synthetic fuel inflation reduces margin headroom.',
        annotation=descriptor(condition='Fuel-price inflation affecting airline margins'))
    p=only_pressure(memory)
    assert p.pressure_id==pid
    assert {a.observation_id,b.observation_id,c.observation_id}==set(p.observation_refs)
    assert set(p.evidence_refs)=={'EV-1','EV-2','EV-3'}


def test_distinct_supported_conditions_are_not_merged(memory):
    ingest(memory)
    ingest(memory,eid='EV-DEBT',statement='Synthetic refinancing constrains investment.',
        affected_attribute='events.pressure.debt',annotation=descriptor(condition='Refinancing constrains investment',
        condition_concept='debt-refinancing',scope='debt refinancing',condition_basis='Debt refinancing is required.',
        mechanism='Debt repayment limits investment.',consequence='Investment headroom is constrained.',
        materiality_rationale='The constraint affects committed capital investment.',identity_rationale='Debt repayment limits investment.'),
        summary='Debt refinancing is required. Debt repayment limits investment. Investment headroom is constrained. The constraint affects committed capital investment.')
    assert len(memory.models.get(ENT).material_pressures)==2


def test_uncertain_equivalence_is_unresolved_not_silently_split_or_merged(memory):
    ingest(memory)
    second=ingest(memory,eid='EV-2',statement='Synthetic fuel expenditure constrains margin headroom.',
        annotation=descriptor(condition_concept='uncertain-alternative-fuel-concept'))
    model=memory.models.get(ENT)
    assert len(model.material_pressures)==1
    assert any(a['qualification']=='UNRESOLVED' and 'reconciliation' in a['reason'].lower() for a in model.pressure_assessments.values())
    assert memory.observations.get(second.observation_id) is not None


def test_corroboration_and_identical_replay_do_not_duplicate_pressure_history(memory):
    ingest(memory)
    ingest(memory,eid='EV-2')
    p=only_pressure(memory)
    assert set(p.evidence_refs)=={'EV-1','EV-2'}
    before=memory.models.get(ENT).to_dict()
    ingest(memory,eid='EV-2')
    assert memory.models.get(ENT).to_dict()==before


def test_core_same_period_contradiction_is_unresolved_and_keeps_facts(memory):
    first=ingest(memory)
    ingest(memory,eid='EV-COUNTER',statement='Synthetic fuel inflation no longer constrains operating margin.',
        human_provenance={},summary='Synthetic fuel inflation no longer constrains operating margin.')
    p=only_pressure(memory)
    assert p.qualification=='UNRESOLVED' and p.contradiction_refs
    assert memory.observations.get(first.observation_id) is not None
    assert len(memory.observations.list())==2 and p.history


def test_non_core_contradiction_is_linked_without_invalidating_core(memory):
    memory.evidence.save(dict(evidence_id='EV-COUNTER',enterprise_id=ENT,summary='The severity estimate is lower.',confidence=60))
    ContradictionRepository().save(dict(contradiction_id='CON-SEVERITY',enterprise_id=ENT,status='open',
        affected_field='severity',supporting_evidence_ids=['EV-1'],counter_evidence_ids=['EV-COUNTER']))
    ingest(memory,annotation=descriptor(contradiction_refs=['CON-SEVERITY']))
    p=only_pressure(memory)
    assert p.qualification=='QUALIFIED' and 'CON-SEVERITY' in p.contradiction_refs
    assert 'EV-COUNTER' in p.counter_evidence_refs


def test_lower_confidence_evidence_weakens_existing_pressure(memory):
    ingest(memory)
    previous=only_pressure(memory).confidence
    ingest(memory,eid='EV-WEAK',statement='Synthetic fuel expenditure constrains operating cash headroom.',confidence=45)
    p=only_pressure(memory)
    assert p.confidence<previous and p.history
    assert 'weaken' in p.last_change.lower()


def test_resolution_retains_original_condition_history_and_lineage(memory):
    first=ingest(memory);pid=only_pressure(memory).pressure_id
    resolution=descriptor(resolved_at='2026-11-05',resolves_pressure_id=pid,
        resolution_basis='The fuel-cost constraint is resolved.',resolution_evidence_refs=['EV-RESOLUTION'],
        observation_refs=[first.observation_id])
    ingest(memory,eid='EV-RESOLUTION',statement='Synthetic fuel-cost constraint is resolved.',annotation=resolution,
        affected_attribute='events.pressure.resolution',observation_date='2026-11-05',summary=TEXT+' The fuel-cost constraint is resolved.')
    p=only_pressure(memory)
    assert p.resolved_at=='2026-11-05' and p.qualification!='QUALIFIED'
    assert p.history and 'EV-1' in p.evidence_refs and 'EV-RESOLUTION' in p.resolution_evidence_refs


@pytest.mark.parametrize('owner,scope',[('synthetic-industry','industry'),('another-enterprise','enterprise')])
def test_industry_or_other_enterprise_evidence_cannot_be_borrowed(memory,owner,scope):
    obs=ingest(memory)
    memory.evidence.save(memory.evidence.get('EV-1')|{'enterprise_id':owner,'scope':scope})
    assert not qualify_candidates((candidate(obs),)).qualified


def test_plain_observation_does_not_automatically_become_pressure(memory):
    ingest(memory,human_provenance={})
    assert not memory.models.get(ENT).material_pressures


def test_pressure_creation_never_creates_commercial_domain_objects(memory,tmp_path):
    ingest(memory)
    assert only_pressure(memory).qualification=='QUALIFIED'
    for name in ('material_pressure','opportunity','procurement','watchpoint'):
        assert not (tmp_path/'memory'/(name+'.jsonl')).exists()


def test_approved_import_uses_same_owner_and_bounded_retrieval(memory,tmp_path,monkeypatch):
    from tests.test_flora_import_model_reconciliation import promote,records,ENT as IMPORT_ENT,HEADERS
    from cios.applications.flora.enterprise_intelligence.retrieval import BoundedTwinRetrievalService
    from cios.applications.flora.enterprise_intelligence.models import ReasoningRequestV1
    rows=records(observation_type='enterprise_event_announced',affected_attribute='events.pressure.fuel',
        atomic_statement='Synthetic fuel inflation constrains operating margin.',period='2026-Q4',human_provenance={'material_pressure':descriptor()})
    rows[0]['payload']['summary']=TEXT
    promote(monkeypatch,tmp_path,rows)
    model=EnterpriseModelRepository().get(IMPORT_ENT)
    assert len(model.material_pressures)==1
    package=BoundedTwinRetrievalService().retrieve(ReasoningRequestV1.create(IMPORT_ENT,IMPORT_ENT,'alice',evidence_cut_off='2026-11-08'))
    assert any(i.object_class=='material_pressure' for i in package.selected_entities_and_relationships)


def test_existing_model_json_without_pressures_remains_readable(memory,tmp_path):
    path=memory.models.path_for(ENT);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(dict(schema_version='flora-memory-v1',enterprise_id=ENT,attributes={},unknowns={})))
    model=memory.models.get(ENT)
    assert model.material_pressures=={} and model.pressure_assessments=={}


def test_caller_cannot_assert_semantics_or_consequence_without_source_support(memory):
    obs=ingest(memory)
    false=copy.deepcopy(obs);false.human_provenance['material_pressure']['consequence']='A funded procurement is confirmed.'
    memory.observations._rewrite([false])
    req=candidate(false)
    assert not qualify_candidates((req,)).qualified


def test_missing_semantic_basis_remains_unresolved(memory):
    obs=ingest(memory,annotation=descriptor(condition_concept=''))
    result=qualify_candidates((candidate(obs),))
    assert result.unresolved and 'identity' in result.unresolved[0].reason.lower()


def test_rejected_assessment_is_diagnostic_not_a_new_durable_pressure(memory):
    obs=ingest(memory,annotation=descriptor(consequence='Unsupported consequence.'))
    model=memory.models.get(ENT)
    assert model.material_pressures=={} and model.pressure_assessments
    assert memory.observations.get(obs.observation_id) is not None


@pytest.mark.parametrize('field',['applicable','pressure_semantics','materiality_established','consequence_established'])
def test_governed_negative_gate_cannot_be_overridden_by_caller(memory,field):
    obs=ingest(memory,annotation=descriptor(**{field:False}))
    assert not qualify_candidates((candidate(obs),)).qualified
    assert not memory.models.get(ENT).material_pressures


@pytest.mark.parametrize('field,expected',[('severity','QUALIFIED'),('condition','UNRESOLVED')])
def test_unknowns_are_resolved_scoped_and_preserved(memory,field,expected):
    from cios.applications.flora.blueprint_import.promotion import CanonicalJsonlRepository
    repo=CanonicalJsonlRepository('unknown')
    repo.save(dict(canonical_id='UN-1',enterprise_id=ENT,status='open',affected_field=field))
    obs=ingest(memory,annotation=descriptor(unknown_refs=['UN-1']))
    assessed=memory.assess_material_pressure(obs.observation_id)
    assert assessed.assessments[0].qualification==expected
    if expected=='QUALIFIED':
        ingest(memory,eid='EV-2',statement='Synthetic fuel inflation constrains cash reserves.')
        assert only_pressure(memory).unknown_refs==('UN-1',)
    else:
        repo.save(dict(canonical_id='UN-1',enterprise_id=ENT,status='resolved',affected_field=field))
        memory.assess_material_pressure(obs.observation_id)
        assert only_pressure(memory).qualification=='QUALIFIED'
        assert only_pressure(memory).unknown_refs==('UN-1',)


def test_unresolvable_counter_evidence_fails_lineage(memory):
    ContradictionRepository().save(dict(contradiction_id='CON-1',enterprise_id=ENT,status='open',
        affected_field='severity',counter_evidence_ids=['MISSING']))
    obs=ingest(memory,annotation=descriptor(contradiction_refs=['CON-1']))
    result=memory.assess_material_pressure(obs.observation_id)
    assert not result.qualified and result.assessments[0].lineage=='FAIL'


def test_numeric_metric_alone_is_not_material_consequence(memory):
    obs=ingest(memory,annotation=descriptor(consequence='Fuel benchmark is 115.',materiality_rationale='Fuel benchmark is 115.'),
        summary=TEXT+' Fuel benchmark is 115.')
    assert not qualify_candidates((candidate(obs),)).qualified
    assert not memory.models.get(ENT).material_pressures


def test_canonical_fact_input_uses_same_enterprise_model_owner(memory):
    from cios.applications.flora.blueprint_import.promotion import CanonicalJsonlRepository
    memory.evidence.save(dict(evidence_id='EV-FACT',enterprise_id=ENT,summary=TEXT,confidence=75))
    CanonicalJsonlRepository('fact').save(dict(canonical_id='FACT-1',enterprise_id=ENT,truth_class='observed',
        evidence_refs=['EV-FACT'],material_pressure=descriptor(),observed_at='2026-11-01'))
    result=memory.assess_material_pressure('FACT-1','canonical_factual_object')
    assert result.qualified and only_pressure(memory).source_input_id=='FACT-1'


def test_explicit_supersession_keeps_history_and_cannot_be_replayed_current(memory):
    first=ingest(memory);old=only_pressure(memory).pressure_id
    ingest(memory,eid='EV-2',statement='Synthetic fuel exposure limits operating margins.',
        annotation=descriptor(condition_concept='revised-fuel-exposure',supersedes_pressure_id=old,
            supersession_basis='Revised exposure replaces the prior constraint.'),
        summary=TEXT+' Revised exposure replaces the prior constraint.')
    model=memory.models.get(ENT)
    previous=model.material_pressures[old]
    assert len(model.material_pressures)==2 and previous.superseded_by
    assert previous.qualification=='NOT_QUALIFIED' and previous.superseded_at=='2026-10-01' and previous.history
    before=previous.to_dict() if hasattr(previous,'to_dict') else copy.deepcopy(previous.__dict__)
    memory.assess_material_pressure(first.observation_id)
    assert memory.models.get(ENT).material_pressures[old].__dict__==before


def test_resolved_pressure_cannot_be_revived_by_unrelated_replay(memory):
    first=ingest(memory);pid=only_pressure(memory).pressure_id
    ingest(memory,eid='EV-R',statement='Synthetic fuel constraint is resolved.',affected_attribute='events.pressure.resolved',
        annotation=descriptor(resolves_pressure_id=pid,resolved_at='2026-11-05',
            resolution_basis='The fuel constraint is resolved.',resolution_evidence_refs=['EV-R']),
        summary=TEXT+' The fuel constraint is resolved.')
    ingest(memory,eid='EV-NEW',statement='Synthetic fuel exposure constrains cash margins.')
    p=only_pressure(memory)
    assert p.resolved_at=='2026-11-05' and p.qualification=='NOT_QUALIFIED'


def test_older_source_replay_cannot_restore_weakened_confidence(memory):
    first=ingest(memory)
    ingest(memory,eid='EV-W',statement='Synthetic fuel costs constrain cash headroom.',confidence=40)
    memory.assess_material_pressure(first.observation_id)
    assert only_pressure(memory).confidence==40


def test_superseded_observation_relation_excludes_predecessor(memory):
    first=ingest(memory)
    from dataclasses import replace
    successor=replace(first,observation_id='OBS-SUCCESSOR',observation_fingerprint='successor',
        supersedes_observation_id=first.observation_id,human_provenance={})
    memory.observations.save(successor)
    assert not qualify_candidates((candidate(first),)).qualified


def test_read_models_revalidate_current_evidence_without_writing(memory):
    from cios.applications.flora.blueprint_import.material_pressure import model_pressure_assessments
    ingest(memory)
    model=memory.models.get(ENT);before=model.to_dict()
    rows=model_pressure_assessments(model)
    assert rows[0]['qualification']=='QUALIFIED' and rows[0]['evidence_refs']==('EV-1',)
    memory.evidence.save(memory.evidence.get('EV-1')|{'freshness':'expired'})
    rows=model_pressure_assessments(model)
    assert rows[0]['qualification']=='REJECTED' and rows[0]['gates']['eligible_input']=='FAIL'
    assert memory.models.get(ENT).to_dict()==before
    assert model_pressure_assessments(model,cutoff='2026-09-01')[0]['qualification']!='QUALIFIED'


def test_unresolved_pressure_is_retrieved_as_conflict_not_qualified_truth(memory):
    from cios.applications.flora.enterprise_intelligence.retrieval import BoundedTwinRetrievalService
    from cios.applications.flora.enterprise_intelligence.models import ReasoningRequestV1
    ingest(memory)
    ingest(memory,eid='EV-C',statement='Synthetic fuel inflation no longer constrains operating margin.',human_provenance={})
    package=BoundedTwinRetrievalService().retrieve(ReasoningRequestV1.create(ENT,ENT,'alice',evidence_cut_off='2026-11-08'))
    assert any(i.object_class=='material_pressure' for i in package.selected_contradictions)
    assert not any(i.object_class=='material_pressure' for i in package.selected_entities_and_relationships)


def test_strengthening_retains_prior_confidence_and_evidence(memory):
    ingest(memory,confidence=45)
    ingest(memory,eid='EV-S',statement='Synthetic fuel costs restrict margin headroom.',confidence=90)
    p=only_pressure(memory)
    assert p.confidence==90 and p.last_change=='strengthened'
    assert p.history[-1]['confidence']==45 and set(p.evidence_refs)=={'EV-1','EV-S'}


def test_different_period_change_does_not_create_false_pressure_conflict(memory):
    ingest(memory)
    ingest(memory,eid='EV-Q1',statement='Synthetic fuel inflation no longer constrains operating margin.',
        human_provenance={},period='2027-Q1',observation_date='2027-01-01')
    assert only_pressure(memory).qualification=='QUALIFIED'


def test_historical_retrieval_excludes_future_pressure_diagnostics(memory):
    from cios.applications.flora.enterprise_intelligence.retrieval import BoundedTwinRetrievalService
    from cios.applications.flora.enterprise_intelligence.models import ReasoningRequestV1
    ingest(memory)
    package=BoundedTwinRetrievalService().retrieve(ReasoningRequestV1.create(ENT,ENT,'alice',evidence_cut_off='2026-09-01'))
    assert not package.enterprise_context.get('material_pressure_assessments')
    assert not any(i.object_class=='material_pressure' for i in package.selected_entities_and_relationships)


def test_failed_pressure_persistence_uses_existing_import_compensation(memory,tmp_path,monkeypatch):
    from tests.test_flora_import_model_reconciliation import promote,records,ENT as IMPORT_ENT
    from cios.applications.flora.blueprint_import.promotion import BlueprintPromotionError
    original=EnterpriseModelRepository.save
    def fail_pressure(self,model):
        if model.material_pressures: raise OSError('synthetic pressure snapshot failure')
        return original(self,model)
    monkeypatch.setattr(EnterpriseModelRepository,'save',fail_pressure)
    rows=records(observation_type='enterprise_event_announced',affected_attribute='events.pressure.fuel',
        atomic_statement='Synthetic fuel inflation constrains operating margin.',period='2026-Q4',human_provenance={'material_pressure':descriptor()})
    rows[0]['payload']['summary']=TEXT
    with pytest.raises(BlueprintPromotionError): promote(monkeypatch,tmp_path,rows)
    assert not ObservationRepository().list() and not EvidenceRepository().list()
    assert not EnterpriseModelRepository().get(IMPORT_ENT).material_pressures


def test_governed_requalification_requires_all_gates_and_preserves_resolution(memory):
    ingest(memory);pid=only_pressure(memory).pressure_id
    ingest(memory,eid='EV-R',statement='Synthetic fuel constraint is resolved.',affected_attribute='events.pressure.resolved',
        annotation=descriptor(resolves_pressure_id=pid,resolved_at='2026-11-05',
            resolution_basis='The fuel constraint is resolved.',resolution_evidence_refs=['EV-R']),
        summary=TEXT+' The fuel constraint is resolved.')
    ingest(memory,eid='EV-REOPEN',statement='Synthetic fuel exposure constrains operations again.',
        affected_attribute='events.pressure.recurred',observation_date='2026-11-07',
        annotation=descriptor(reopens_pressure_id=pid,effective_at='2026-11-07',
            requalification_basis='The constraint has recurred.'),summary=TEXT+' The constraint has recurred.')
    p=only_pressure(memory)
    assert p.qualification=='QUALIFIED' and not p.resolved_at
    assert p.resolution_evidence_refs==('EV-R',) and any(row['resolved_at']=='2026-11-05' for row in p.history)


def test_existing_enterprise_memory_view_exposes_assurance_diagnostics(memory):
    from cios.applications.flora.memory.views import enterprise_memory_panel
    ingest(memory)
    html=enterprise_memory_panel(ENT)
    assert 'Material Pressure assessments' in html and 'QUALIFIED' in html
    assert descriptor()['consequence'] in html and 'EV-1' in html
    memory.evidence.save(memory.evidence.get('EV-1')|{'lifecycle_state':'rejected'})
    html=enterprise_memory_panel(ENT)
    assert 'REJECTED' in html and 'ineligible input' in html


def test_source_identity_mutation_requires_explicit_reconciliation(memory):
    obs=ingest(memory);prior=only_pressure(memory)
    obs.human_provenance['material_pressure']=descriptor(scope='different business scope',time_context='2026-Q3')
    memory.observations._rewrite([obs])
    result=memory.assess_material_pressure(obs.observation_id)
    p=only_pressure(memory)
    assert result.unresolved and p.qualification=='UNRESOLVED'
    assert p.pressure_id==prior.pressure_id and p.scope==prior.scope and p.time_context==prior.time_context


def test_caller_cannot_omit_canonical_core_unknown_references(memory):
    from cios.applications.flora.blueprint_import.promotion import CanonicalJsonlRepository
    CanonicalJsonlRepository('unknown').save(dict(canonical_id='UN-CORE',enterprise_id=ENT,status='open',affected_field='existence'))
    obs=ingest(memory,annotation=descriptor(unknown_refs=['UN-CORE']))
    result=qualify_candidates((candidate(obs),))
    assert result.unresolved and result.unresolved[0].candidate.unknown_refs==('UN-CORE',)


def test_caller_cannot_omit_canonical_core_contradictions(memory):
    memory.evidence.save(dict(evidence_id='EV-C',enterprise_id=ENT,summary='The constraint is disputed.'))
    ContradictionRepository().save(dict(contradiction_id='CON-CORE',enterprise_id=ENT,status='open',
        affected_field='existence',counter_evidence_ids=['EV-C']))
    obs=ingest(memory,annotation=descriptor(contradiction_refs=['CON-CORE']))
    result=qualify_candidates((candidate(obs),))
    assert result.unresolved and result.unresolved[0].counter_evidence_refs==('EV-C',)


def test_future_effective_source_provenance_cannot_support_historical_pressure(memory):
    obs=ingest(memory)
    obs.human_provenance['effective_date']='2027-01-01'
    memory.observations._rewrite([obs])
    result=qualify_candidates((candidate(obs),),cutoff='2026-11-08')
    assert not result.qualified and dict(result.assessments[0].gate_results)['eligible_input']=='FAIL'
