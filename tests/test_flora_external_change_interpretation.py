"""Industry-independent, isolated external-to-enterprise interpretation contracts."""
import json

import pytest

from cios.applications.flora.blueprint_import.promotion import CanonicalJsonlRepository
from cios.applications.flora.memory.models import Observation
from cios.applications.flora.memory.service import ObservationMemoryService

AIR=('air-one','air-two')
BANK=('bank-one','bank-two')
CYBER=('sector-one','sector-two')
ALL=(*AIR,*BANK,*CYBER,'unrelated')
DATE='2026-11-08'


@pytest.fixture
def memory(tmp_path,monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR',str(tmp_path));monkeypatch.setenv('FLORA_PILOT_DIR',str(tmp_path))
    memory=ObservationMemoryService()
    entities=CanonicalJsonlRepository('entity');relationships=CanonicalJsonlRepository('relationship')
    for scope,enterprises in [('S-AIR',AIR),('S-BANK',BANK),('S-CYBER',CYBER),('S-OTHER',('unrelated',))]:
        entities.save(dict(canonical_id=scope,entity_type='industry',name=scope))
        for ent in enterprises:
            entities.save(dict(canonical_id='ENT-'+ent,entity_type='enterprise',enterprise_id=ent,name=ent))
            eid='EV-LINK-'+ent
            memory.evidence.save(dict(evidence_id=eid,enterprise_id=scope,summary=f'{ent} is related to {scope}.'))
            relationships.save(dict(canonical_id='REL-'+ent,source='ENT-'+ent,target=scope,
                relationship_type='participates_in',evidence_refs=[eid]))
    return memory


def service(memory):
    from cios.applications.flora.enterprise_intelligence.change_interpretation import ExternalChangeInterpretationService
    return ExternalChangeInterpretationService(observations=memory.observations,evidence=memory.evidence,models=memory.models)


def event(memory,scope='S-AIR',eid='EV-EVENT',statement='The jet-fuel benchmark increased by 15%.',**changes):
    row=dict(evidence_id=eid,enterprise_id=scope,scope='industry',summary=statement,
        publication_date='2026-11-01',collection_date='2026-11-02',
        human_provenance={'external_change':dict(scope_id=scope,statement=statement,time_context='2026-Q4')})|changes
    memory.evidence.save(row)
    return eid


def support(memory,ent=AIR[0],oid=None,eid=None,state='applicable',basis=None,mechanism=None,consequence='',mitigation='',**changes):
    oid=oid or 'OBS-'+ent;eid=eid or 'EV-'+ent
    basis=basis or f'{ent} has exposure to this development.'
    mechanism=mechanism if mechanism is not None else 'The unhedged fuel exposure transmits cost increases.'
    descriptor=dict(evidence_id='EV-EVENT',time_context='2026-Q4',applicability=state,
        applicability_basis=basis,mechanism=mechanism,consequence=consequence,mitigation=mitigation)
    descriptor.update(changes.pop('descriptor',{}))
    memory.evidence.save(dict(evidence_id=eid,enterprise_id=ent,
        summary=' '.join(s for s in (basis,mechanism,consequence,mitigation) if s),
        publication_date='2026-11-01',collection_date='2026-11-02',confidence=80))
    obs=Observation(ent,'enterprise_event_announced',basis,
        '2026-11-01','2026-11-02','events.external.exposure',80,(eid,),
        observation_id=oid,human_provenance={'external_change_interpretation':descriptor},**changes)
    memory.observations.save(obs);memory.apply_observation(obs)
    return obs


def assess(memory,eid='EV-EVENT',allowed=ALL):
    return service(memory).assess(eid,allowed_enterprise_ids=allowed,cutoff=DATE)


def rows(result):
    return {row['enterprise_id']:row for row in result['assessments']}


def test_aviation_distinguishes_exposure_mitigation_and_consequence(memory):
    event(memory)
    support(memory,AIR[0],consequence='Unhedged fuel costs constrain operating margin.',mitigation='A small hedge covers part of fuel needs.')
    support(memory,AIR[1],mechanism='The current hedge limits near-term fuel exposure.',mitigation='Most fuel requirements are hedged.')
    result=rows(assess(memory))
    assert set(result)==set(AIR)
    assert result[AIR[0]]['state']=='APPLICABLE_WITH_EVIDENCED_CONSEQUENCE'
    assert result[AIR[1]]['state']=='POTENTIALLY_APPLICABLE'
    assert result[AIR[0]]['consequences']==['Unhedged fuel costs constrain operating margin.']
    assert result[AIR[1]]['mitigations']==['Most fuel requirements are hedged.']
    assert result[AIR[1]]['evidence_demands']
    assert result[AIR[0]]['evidence_roles']['external_context']==['EV-EVENT']
    assert result[AIR[0]]['evidence_roles']['enterprise_support']==['EV-air-one']
    assert result[AIR[0]]['applicability_explanations']==['air-one has exposure to this development.']
    assert 'net_financial_impact' not in result[AIR[0]]


def test_banking_uses_same_contract_without_sector_calculations(memory):
    event(memory,'S-BANK',statement='The policy interest rate decreased.')
    support(memory,BANK[0],mechanism='Deposit repricing reduces funding cost.',consequence='Funding flexibility improves.')
    support(memory,BANK[1],mechanism='Fixed-rate assets delay repricing.',mitigation='Long-duration assets defer the repricing effect.')
    result=rows(assess(memory))
    assert result[BANK[0]]['state']=='APPLICABLE_WITH_EVIDENCED_CONSEQUENCE'
    assert result[BANK[1]]['state']=='POTENTIALLY_APPLICABLE'
    assert result[BANK[0]]['mechanisms']==['Deposit repricing reduces funding cost.']
    assert result[BANK[1]]['mechanisms']==['Fixed-rate assets delay repricing.']


def test_sector_security_incident_does_not_imply_enterprise_incident(memory):
    event(memory,'S-CYBER',statement='An external security incident affects a sector supplier.')
    result=rows(assess(memory))
    assert set(result)==set(CYBER)
    assert all(row['state']=='POTENTIALLY_APPLICABLE' and not row['consequences'] for row in result.values())
    assert all(row['evidence_demands'] and not row['observation_refs'] for row in result.values())


def test_explicit_evidenced_non_applicability_is_not_a_consequence(memory):
    event(memory)
    support(memory,AIR[1],state='not_applicable',basis='The enterprise has no exposure in this effective period.',mechanism='')
    row=rows(assess(memory))[AIR[1]]
    assert row['state']=='NOT_APPLICABLE' and not row['consequences']
    assert not row['pressure_qualification_previews']


def test_unrelated_enterprise_and_all_canonical_state_remain_unchanged(memory,tmp_path):
    event(memory);support(memory,consequence='Operating headroom is constrained.')
    before={str(p.relative_to(tmp_path)):p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    result=assess(memory)
    after={str(p.relative_to(tmp_path)):p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    assert 'unrelated' not in rows(result) and before==after


def test_opposing_same_period_applicability_remains_unresolved(memory):
    event(memory)
    a=support(memory,consequence='Operating headroom is constrained.')
    support(memory,oid='OBS-COUNTER',eid='EV-COUNTER',state='not_applicable',basis='The exposure does not apply to this enterprise.',mechanism='')
    row=rows(assess(memory))[AIR[0]]
    assert row['state']=='UNRESOLVED' and set(row['observation_refs'])=={a.observation_id,'OBS-COUNTER'}
    assert 'EV-COUNTER' in row['evidence_roles']['enterprise_support'] and row['contradictions']
    assert not row['pressure_qualification_previews']


def test_replay_has_stable_assessment_id_and_no_duplicate_result(memory):
    event(memory);support(memory,consequence='Operating margin is constrained.')
    first=assess(memory);event(memory);second=assess(memory)
    assert first==second
    assert len({row['assessment_id'] for row in first['assessments']})==len(first['assessments'])


@pytest.mark.parametrize('field,value',[('lifecycle_state','rejected'),('freshness','expired'),('publication_date','2027-01-01')])
def test_ineligible_external_source_cannot_become_current_change(memory,field,value):
    event(memory,**{field:value})
    result=assess(memory)
    assert result['event_state']=='REJECTED' and not result['assessments']


def test_nonexistent_external_evidence_is_rejected(memory):
    result=assess(memory,'MISSING')
    assert result['event_state']=='REJECTED' and not result['assessments']


def test_unsupported_external_statement_is_rejected(memory):
    event(memory,summary='A benchmark report is available.')
    assert assess(memory)['event_state']=='REJECTED'


@pytest.mark.parametrize('field,value',[('lifecycle_state','retired'),('freshness','expired')])
def test_inactive_enterprise_support_remains_incomplete(memory,field,value):
    event(memory);obs=support(memory,consequence='Operating headroom is constrained.')
    setattr(obs,field,value);memory.observations._rewrite([obs])
    row=rows(assess(memory))[AIR[0]]
    assert row['state']=='POTENTIALLY_APPLICABLE' and not row['consequences']


def test_other_enterprise_evidence_cannot_supply_target_consequence(memory):
    event(memory);support(memory,consequence='Operating margin is constrained.')
    memory.evidence.save(memory.evidence.get('EV-air-one')|{'enterprise_id':AIR[1]})
    row=rows(assess(memory))[AIR[0]]
    assert row['state']=='POTENTIALLY_APPLICABLE' and not row['consequences']


def test_industry_evidence_cannot_replace_enterprise_evidence(memory):
    event(memory);support(memory,consequence='Operating margin is constrained.')
    memory.evidence.save(memory.evidence.get('EV-air-one')|{'scope':'industry'})
    assert rows(assess(memory))[AIR[0]]['state']=='POTENTIALLY_APPLICABLE'


def test_unsupported_consequence_does_not_use_plausibility_to_fill_gap(memory):
    event(memory);obs=support(memory,consequence='Operating margin is constrained.')
    obs.human_provenance['external_change_interpretation']['consequence']='Net earnings decline by £90m.'
    memory.observations._rewrite([obs])
    row=rows(assess(memory))[AIR[0]]
    assert row['state']=='POTENTIALLY_APPLICABLE' and not row['consequences'] and row['evidence_demands']


def test_different_event_or_period_support_does_not_apply(memory):
    event(memory);support(memory,consequence='Operating margin is constrained.',descriptor={'time_context':'2026-Q3'})
    assert rows(assess(memory))[AIR[0]]['state']=='POTENTIALLY_APPLICABLE'


def test_candidate_discovery_requires_resolvable_evidenced_canonical_relationship(memory):
    event(memory)
    repo=CanonicalJsonlRepository('relationship')
    repo.save(repo.get('REL-air-one')|{'target':'MISSING'})
    memory.evidence.save(memory.evidence.get('EV-LINK-air-two')|{'lifecycle_state':'rejected'})
    result=assess(memory)
    assert not result['assessments'] and result['evidence_demands']


def test_candidate_discovery_does_not_follow_indirect_or_name_only_edges(memory):
    event(memory)
    CanonicalJsonlRepository('relationship').save(dict(canonical_id='REL-INDIRECT',source='ENT-unrelated',target='ENT-air-one',relationship_type='supplier_to',evidence_refs=['EV-LINK-unrelated']))
    assert set(rows(assess(memory)))==set(AIR)


def test_allowed_enterprise_scope_is_required_and_filters_results(memory):
    event(memory)
    assert set(rows(assess(memory,allowed=(AIR[0],))))=={AIR[0]}
    assert not assess(memory,allowed=())['assessments']


def test_existing_model_dependencies_are_reassessment_targets_not_writes(memory):
    event(memory);obs=support(memory,consequence='Operating margin is constrained.')
    before=memory.models.get(AIR[0]).to_dict()
    row=rows(assess(memory))[AIR[0]]
    assert row['reassessment_targets']['model_attributes']==[obs.affected_attribute]
    assert memory.models.get(AIR[0]).to_dict()==before


def test_core_conflict_links_are_visible_even_with_one_positive_annotation(memory):
    event(memory);obs=support(memory,consequence='Operating margin is constrained.')
    counter=support(memory,ent=AIR[0],oid='OBS-NEG',eid='EV-NEG',state='potential',basis='The impact remains disputed.',mechanism='')
    obs.contradiction_state='unresolved';obs.contradicted_by_observation_ids=(counter.observation_id,)
    memory.observations._rewrite([obs,counter])
    row=rows(assess(memory))[AIR[0]]
    assert row['state']=='UNRESOLVED' and 'EV-NEG' in row['evidence_roles']['counter_evidence']


def test_retrieval_exposes_only_requested_enterprise_diagnostics(memory):
    from cios.applications.flora.enterprise_intelligence.retrieval import BoundedTwinRetrievalService
    from cios.applications.flora.enterprise_intelligence.models import ReasoningRequestV1
    event(memory);support(memory,consequence='Operating margin is constrained.')
    request=ReasoningRequestV1.create(AIR[0],AIR[0],'alice',evidence_cut_off=DATE)
    package=BoundedTwinRetrievalService().retrieve(request)
    diagnostic=package.enterprise_context['external_change_assessments']
    assert len(diagnostic)==1 and diagnostic[0]['enterprise_id']==AIR[0]
    assert 'air-two' not in json.dumps(diagnostic)
    assert not any(item.object_class=='external_change' for item in package.selected_observations)


def test_existing_memory_panel_exposes_qualification_lineage_and_demands(memory):
    from cios.applications.flora.memory.views import enterprise_memory_panel
    event(memory)
    html=enterprise_memory_panel(AIR[0])
    assert 'External change assessments' in html and 'POTENTIALLY_APPLICABLE' in html
    assert 'EV-EVENT' in html and 'Evidence needed' in html


def test_read_only_interpretation_creates_no_new_commercial_or_event_store(memory,tmp_path):
    event(memory);support(memory,consequence='Operating margin is constrained.')
    assess(memory)
    assert not any(p.name in {'change_event.jsonl','external_change.jsonl','opportunity.jsonl','procurement.jsonl','programme.jsonl','watchpoint.jsonl'} for p in tmp_path.rglob('*'))
    assert len(memory.observations.list())==1


def test_pressure_preview_reuses_adr026_and_never_mutates_model(memory):
    from tests.test_flora_material_pressure_lifecycle import TEXT,descriptor
    event(memory)
    observation=support(memory,consequence=descriptor()['consequence'],mechanism=descriptor()['mechanism'])
    observation.human_provenance['material_pressure']=descriptor()
    memory.evidence.save(memory.evidence.get('EV-air-one')|{'summary':TEXT+' '+observation.human_provenance['external_change_interpretation']['applicability_basis']})
    memory.observations._rewrite([observation]);memory.assess_material_pressure(observation.observation_id)
    before=memory.models.get(AIR[0]).to_dict()
    row=rows(assess(memory))[AIR[0]]
    assert row['pressure_qualification_previews'][0]['qualification']=='QUALIFIED'
    assert all(value=='PASS' for value in row['pressure_qualification_previews'][0]['gates'].values())
    assert row['reassessment_targets']['material_pressures']==list(before['material_pressures'])
    assert memory.models.get(AIR[0]).to_dict()==before
    memory.evidence.save(memory.evidence.get('EV-air-one')|{'lifecycle_state':'rejected'})
    row=rows(assess(memory))[AIR[0]]
    assert row['state']=='POTENTIALLY_APPLICABLE' and not row['pressure_qualification_previews']
    assert memory.models.get(AIR[0]).to_dict()==before


def test_governed_import_reaches_existing_interpretation_read_boundary(memory,tmp_path,monkeypatch):
    from tests.test_flora_import_model_reconciliation import records,promote,ENT
    basis='The synthetic enterprise has exposure to this development.'
    consequence='Operating margin is constrained.'
    mechanism='Exposure transmits operating cost increases.'
    description=dict(evidence_id='EV-EXTERNAL',time_context='2026-Q4',applicability='applicable',
        applicability_basis=basis,mechanism=mechanism,consequence=consequence)
    imported=records(observation_type='enterprise_event_announced',affected_attribute='events.external.exposure',
        atomic_statement=basis,period='2026-Q4',human_provenance={'external_change_interpretation':description})
    imported[0]['payload']['summary']=basis+' '+mechanism+' '+consequence
    imported.extend([
        dict(external_id='SCOPE-IMPORT',record_class='entity',truth_class='observed',payload=dict(entity_id='SCOPE-IMPORT',entity_type='industry',enterprise_id=ENT)),
        dict(external_id='ENTERPRISE-IMPORT',record_class='entity',truth_class='observed',payload=dict(entity_id='ENTERPRISE-IMPORT',entity_type='enterprise',enterprise_id=ENT)),
        dict(external_id='LINK-IMPORT',record_class='relationship',truth_class='observed',payload=dict(source='ENTERPRISE-IMPORT',target='SCOPE-IMPORT',relationship_type='participates_in',evidence_refs=['EV-1'],enterprise_id=ENT)),
        dict(external_id='EV-EXTERNAL',record_class='evidence',truth_class='evidence_backed',payload=dict(evidence_id='EV-EXTERNAL',enterprise_id=ENT,scope='industry',summary='The external benchmark changed.',human_provenance={'external_change':dict(scope_id='SCOPE-IMPORT',statement='The external benchmark changed.',time_context='2026-Q4')}))])
    promote(monkeypatch,tmp_path,imported)
    result=service(memory).assess('EV-EXTERNAL',allowed_enterprise_ids=(ENT,),cutoff=DATE)
    assert rows(result)[ENT]['state']=='APPLICABLE_WITH_EVIDENCED_CONSEQUENCE'
    assert len(memory.observations.list())==1


def test_external_only_event_never_creates_observation_or_pressure(memory):
    event(memory)
    assess(memory)
    assert not memory.observations.list()
    assert all(not memory.models.get(ent).material_pressures for ent in ALL)


def test_canonical_consequence_conflict_preserves_both_evidence_paths(memory):
    from cios.applications.flora.memory.repository import ContradictionRepository
    event(memory);obs=support(memory,consequence='Operating margin is constrained.',descriptor={'contradiction_refs':['CON-1']})
    memory.evidence.save(dict(evidence_id='EV-COUNTER',enterprise_id=AIR[0],summary='Operating margin is unaffected.'))
    ContradictionRepository().save(dict(contradiction_id='CON-1',enterprise_id=AIR[0],affected_field='consequence',status='open',counter_evidence_ids=['EV-COUNTER']))
    row=rows(assess(memory))[AIR[0]]
    assert row['state']=='UNRESOLVED' and row['contradiction_refs']==['CON-1']
    assert row['evidence_roles']['counter_evidence']==['EV-COUNTER']
    assert row['evidence_roles']['enterprise_support']==list(obs.supporting_evidence_ids)


def test_unknown_applicability_is_explicit_and_does_not_change_model(memory):
    event(memory);support(memory,consequence='Operating margin is constrained.',descriptor={'unknown_refs':['UN-1']})
    CanonicalJsonlRepository('unknown').save(dict(canonical_id='UN-1',enterprise_id=AIR[0],status='open',question='Does the condition apply?'))
    before=memory.models.get(AIR[0]).to_dict()
    row=rows(assess(memory))[AIR[0]]
    assert row['state']=='POTENTIALLY_APPLICABLE' and row['unknown_refs']==['UN-1'] and row['evidence_demands']
    assert memory.models.get(AIR[0]).to_dict()==before


def test_historical_cutoff_excludes_future_effective_support(memory):
    event(memory);obs=support(memory,consequence='Operating margin is constrained.')
    obs.human_provenance['effective_date']='2027-01-01';memory.observations._rewrite([obs])
    assert rows(assess(memory))[AIR[0]]['state']=='POTENTIALLY_APPLICABLE'


def test_superseded_enterprise_support_is_excluded(memory):
    from dataclasses import replace
    event(memory);obs=support(memory,consequence='Operating margin is constrained.')
    memory.observations.save(replace(obs,observation_id='OBS-SUCCESSOR',observation_fingerprint='successor',
        supersedes_observation_id=obs.observation_id,human_provenance={}))
    assert rows(assess(memory))[AIR[0]]['state']=='POTENTIALLY_APPLICABLE'


def test_period_metadata_disagreement_cannot_establish_consequence(memory):
    event(memory);obs=support(memory,consequence='Operating margin is constrained.')
    obs.human_provenance['effective_period']='2026-Q3';memory.observations._rewrite([obs])
    assert rows(assess(memory))[AIR[0]]['state']=='POTENTIALLY_APPLICABLE'


def test_unresolved_external_conflict_cannot_be_silently_preferred(memory):
    event(memory,contradiction_state='unresolved')
    support(memory,consequence='Operating margin is constrained.')
    assert rows(assess(memory))[AIR[0]]['state']=='UNRESOLVED'


def test_missing_counter_evidence_creates_explicit_demand(memory):
    from cios.applications.flora.memory.repository import ContradictionRepository
    event(memory);support(memory,consequence='Operating margin is constrained.',descriptor={'contradiction_refs':['CON-1']})
    ContradictionRepository().save(dict(contradiction_id='CON-1',enterprise_id=AIR[0],status='open',counter_evidence_ids=['MISSING']))
    row=rows(assess(memory))[AIR[0]]
    assert row['state']=='UNRESOLVED' and any('MISSING' in demand for demand in row['evidence_demands'])


def test_resolved_observation_conflict_remains_historical_not_current_conflict(memory):
    event(memory);obs=support(memory,consequence='Operating margin is constrained.')
    obs.contradiction_state='resolved';obs.contradicted_by_observation_ids=('OBS-HISTORIC',)
    memory.observations._rewrite([obs])
    row=rows(assess(memory))[AIR[0]]
    assert row['state']=='APPLICABLE_WITH_EVIDENCED_CONSEQUENCE'
    assert 'OBS-HISTORIC' in row['contradiction_refs']


def test_noncore_unknown_remains_visible_with_evidenced_consequence(memory):
    event(memory);support(memory,consequence='Operating margin is constrained.',descriptor={'unknown_refs':['UN-SEVERITY']})
    CanonicalJsonlRepository('unknown').save(dict(canonical_id='UN-SEVERITY',enterprise_id=AIR[0],status='open',affected_field='severity'))
    row=rows(assess(memory))[AIR[0]]
    assert row['state']=='APPLICABLE_WITH_EVIDENCED_CONSEQUENCE' and row['unknown_refs']==['UN-SEVERITY']


def test_zero_confidence_observation_cannot_prove_applicability(memory):
    event(memory);obs=support(memory,consequence='Operating margin is constrained.')
    obs.confidence=0;memory.observations._rewrite([obs])
    assert rows(assess(memory))[AIR[0]]['state']=='POTENTIALLY_APPLICABLE'


def test_missing_and_staged_descriptors_cannot_authorize_interpretation(memory):
    from cios.applications.flora.blueprint_import import BlueprintPackageRegistry,BlueprintPackageValidator
    from tests.test_flora_blueprint_import_validation import pkg
    event(memory,human_provenance=None)
    BlueprintPackageValidator().validate_and_stage(BlueprintPackageRegistry().receive(pkg(), 'synthetic.zip','alice').package_ref,'alice')
    assert assess(memory)['event_state']=='REJECTED'
    assert not service(memory).for_enterprise(AIR[0])


def test_existing_canonical_conflict_is_detected_without_redundant_annotation(memory):
    from cios.applications.flora.memory.repository import ContradictionRepository
    event(memory);support(memory,consequence='Operating margin is constrained.')
    memory.evidence.save(dict(evidence_id='EV-NEG',enterprise_id=AIR[0],summary='Operating margin is unaffected.'))
    ContradictionRepository().save(dict(contradiction_id='CON-EVIDENCE',enterprise_id=AIR[0],status='open',
        supporting_evidence_ids=['EV-air-one'],counter_evidence_ids=['EV-NEG']))
    row=rows(assess(memory))[AIR[0]]
    assert row['state']=='UNRESOLVED' and 'CON-EVIDENCE' in row['contradiction_refs']


def test_external_canonical_conflict_is_retained_as_context_not_enterprise_fact(memory):
    from cios.applications.flora.memory.repository import ContradictionRepository
    event(memory);support(memory,consequence='Operating margin is constrained.')
    memory.evidence.save(dict(evidence_id='EV-EVENT-COUNTER',enterprise_id='S-AIR',scope='industry',summary='The benchmark did not increase.'))
    ContradictionRepository().save(dict(contradiction_id='CON-EXTERNAL',enterprise_id='S-AIR',status='open',
        supporting_evidence_ids=['EV-EVENT'],counter_evidence_ids=['EV-EVENT-COUNTER']))
    row=rows(assess(memory))[AIR[0]]
    assert row['state']=='UNRESOLVED' and row['evidence_roles']['external_counter_evidence']==['EV-EVENT-COUNTER']
    assert 'EV-EVENT-COUNTER' not in row['evidence_roles']['enterprise_support']
