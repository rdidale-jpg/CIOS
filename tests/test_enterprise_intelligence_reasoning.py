from __future__ import annotations
import json
from pathlib import Path
from cios.applications.flora.memory.models import EnterpriseModel, EnterpriseModelAttribute, EnterpriseUnknown, Observation
from cios.applications.flora.memory.repository import EnterpriseModelRepository, ObservationRepository, EvidenceRepository
from cios.applications.flora.enterprise_intelligence.models import ReasoningRequestV1
from cios.applications.flora.enterprise_intelligence.retrieval import BoundedTwinRetrievalService
from cios.applications.flora.enterprise_intelligence.runtime import EnterpriseIntelligenceRuntime, deterministic_brief, output_schema, safe_fallback
from cios.applications.flora.enterprise_intelligence.validator import ClaimValidator
from cios.applications.flora.enterprise_intelligence.profile import PROFILE
from cios.applications.flora.enterprise_intelligence.persistence import InterpretationPersistenceService
from cios.applications.flora.enterprise_intelligence.views import executive_intelligence_brief_page


def repos(tmp_path):
    return (EnterpriseModelRepository(tmp_path/'models'), ObservationRepository(tmp_path/'obs.jsonl'), EvidenceRepository(tmp_path/'ev.jsonl'))

def seed(tmp_path):
    models, obs, ev = repos(tmp_path)
    ev.path.write_text('\n'.join(json.dumps({'evidence_id':f'E-{i}','enterprise_id':'mod','summary':f'MOD evidence {i}','confidence':80,'freshness':'current'}) for i in range(1,8))+'\n')
    items=[
      Observation('mod','fact','MOD affordability pressure is material.','2026-07-01','2026-07-02','pressure.affordability',90,('E-1',),importance=100,commercial_value=90),
      Observation('mod','fact','MOD readiness pressure is material.','2026-07-01','2026-07-02','pressure.readiness',90,('E-2',),importance=95,commercial_value=85),
      Observation('mod','fact','MOD artificial intelligence adoption pressure is material.','2026-07-01','2026-07-02','pressure.ai',90,('E-3',),importance=90,commercial_value=95),
      Observation('mod','fact','MOD supplier resilience pressure is material.','2026-07-01','2026-07-02','pressure.supplier',90,('E-4',),importance=85,commercial_value=80, contradiction_state='contested', contradicted_by_observation_ids=('OBS-X',)),
      Observation('mod','fact','MOD commercial accessibility pressure is material.','2026-07-01','2026-07-02','pressure.commercial',85,('E-5',),importance=80,commercial_value=100),
      Observation('mod','fact','MOD human validated stakeholder role is recorded.','2026-07-01','2026-07-02','stakeholder.role',70,(),provenance_type='human-supplied', human_provenance={'supplied_by':'analyst'}),
      Observation('other','fact','Other enterprise pressure is material.','2026-07-01','2026-07-02','pressure.other',99,('E-6',)),
      Observation('mod','fact','MOD stale old pressure is material.','2027-01-01','2027-01-02','pressure.old',99,('E-7',)),
    ]
    for o in items: obs.save(o)
    model=EnterpriseModel('mod', attributes={'role.owner':EnterpriseModelAttribute('organisation','role.owner','Chief Commercial Officer',80,'2026-07-01','current',(items[0].observation_id,),('E-1',),'evidence-backed'), 'programme.alpha':EnterpriseModelAttribute('programme','programme.alpha','Availability improvement programme',80,'2026-07-01','current',(items[1].observation_id,),('E-2',),'evidence-backed')}, unknowns={'UNK-1':EnterpriseUnknown('UNK-1','mod','Who owns the cross-cutting MOD route to market?','commercial', related_observation_ids=(items[0].observation_id,))})
    models.save(model)
    return models, obs, ev

def req(cutoff='2026-12-31'):
    return ReasoningRequestV1.create('mod','mod','alice', evidence_cut_off=cutoff, maximum_evidence_volume=8000)

def test_retrieval_guards_truth_labels_and_materiality(tmp_path):
    models, obs, ev=seed(tmp_path); pkg=BoundedTwinRetrievalService(models,obs,ev).retrieve(req('2026-07-10'))
    text=json.dumps(pkg.to_dict())
    assert 'Other enterprise' not in text
    assert 'old pressure' not in text
    assert pkg.selected_observations[0].statement != 'Other enterprise pressure is material.'
    assert any(i.truth_status=='unknown' for i in pkg.selected_unknowns)
    assert pkg.selected_contradictions
    assert any(i.truth_status=='human_supplied_knowledge' for i in pkg.selected_human_supplied_knowledge)

def test_validation_rejects_invalid_ids_and_requires_recommendation_lineage(tmp_path):
    models, obs, ev=seed(tmp_path); pkg=BoundedTwinRetrievalService(models,obs,ev).retrieve(req())
    brief=deterministic_brief(req(),pkg)
    brief['material_pressures'][0]['supporting_observation_ids']=['BAD-ID']
    brief['recommended_next_moves'][0]['lineage']=[]
    out=ClaimValidator().validate(brief,pkg)
    assert out['validation_status']['status']=='invalid'
    assert len(out['validation_status']['rejected_claims']) >= 2

def test_runtime_fallback_no_canonical_mutation_and_telemetry(tmp_path, monkeypatch):
    models, obs, ev=seed(tmp_path); before=[o.to_dict() for o in obs.list()]
    rt=EnterpriseIntelligenceRuntime(BoundedTwinRetrievalService(models,obs,ev))
    result=rt.generate(req())
    assert result['audit']['status']=='Failed'
    assert result['audit']['fallback_active'] is True
    assert result['brief']['unavailable_reason']
    assert result['audit']['execution_duration_ms'] >= 0
    assert [o.to_dict() for o in obs.list()] == before
    assert safe_fallback('provider unavailable')['title']=='Executive Intelligence Brief unavailable'

def test_schema_profile_persistence_and_render_quality(tmp_path, monkeypatch):
    models, obs, ev=seed(tmp_path)
    pkg=BoundedTwinRetrievalService(models,obs,ev).retrieve(req())
    brief=ClaimValidator().validate(deterministic_brief(req(),pkg),pkg)
    assert output_schema()['name']=='ExecutiveCommercialBriefV1'
    assert {'Who?','Why now?','Why them?','What evidence?','What next?'} <= set(PROFILE['must_answer'])
    rec=InterpretationPersistenceService().approve_selected(brief=brief, selected_claims=brief['recommended_next_moves'][:1], approving_user='alice')
    assert rec['originating_brief']==brief['brief_id'] and rec['claim_lineage']
    rendered=json.dumps(brief)
    for bad in ['burning platform from 39 Burning Platform','Governed Twin owner','Enterprise lens built from accepted records','Confidence not confirmed','validate ownership']:
        assert bad not in rendered
    assert len({p['title'] for p in brief['material_pressures']}) >= 3
    assert all((p['supporting_observation_ids'] or p['supporting_evidence_ids'] or p['linked_unknown_ids']) for p in brief['material_pressures'])


def test_canvas_diagnostics_missing_provider_and_no_secret(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    models, obs, ev=seed(tmp_path)
    from cios.applications.flora.enterprise_canvas.access import repair_enterprise_canvas_access
    repair_enterprise_canvas_access('mod','mod','alice','run-1')
    from cios.applications.flora.enterprise_canvas.views import enterprise_canvas_page
    html, status=enterprise_canvas_page('mod', {'X-Flora-User':'alice','X-Flora-Enterprises':'mod','X-Flora-Active-Workspace':'mod'})
    assert status==200
    assert 'Executive Intelligence Brief unavailable' in html
    assert 'Reasoning diagnostics' in html
    assert 'Generate Executive Intelligence Brief' in html
    assert 'FLORA_REASONING_API_KEY' not in html and 'secret' not in html.lower()

class RecordingProvider:
    provider_name='recording'
    def __init__(self, payload): self.payload=payload; self.called=False
    def generate_structured(self, *, prompt, schema, timeout_s, token_budget):
        from cios.applications.flora.enterprise_intelligence.provider import LLMResult
        self.called=True
        assert schema['name']=='ExecutiveCommercialBriefV1'
        assert 'Other enterprise pressure' not in prompt
        return LLMResult(self.payload, 'recording', 'unit-model', {'prompt_tokens':1,'completion_tokens':1}, 7)

def test_successful_reasoning_provider_validation_and_transient_store(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    models, obs, ev=seed(tmp_path); request=req()
    pkg=BoundedTwinRetrievalService(models,obs,ev).retrieve(request)
    oid=pkg.selected_observations[0].stable_id
    payload={'brief_id':'brief-unit','enterprise_id':'mod','twin_version':'accepted','reasoning_profile':'strategic_sales_director_v1','generated_at':'2026-07-10T00:00:00Z','evidence_cut_off':'','executive_summary':{'what_is_happening':'Distinct MOD affordability and readiness themes','why_it_matters':'They shape commercial access'},'material_pressures':[{'title':'Affordability pressure','situation':'MOD affordability pressure is material.','why_now':'Evidence says now','supporting_observation_ids':[oid],'supporting_evidence_ids':[],'linked_unknown_ids':[],'linked_contradiction_ids':[],'confidence':'medium'}],'unknowns':[],'contradictions':[],'recommended_next_moves':[{'action':'Inspect pressure lineage','lineage':[oid]}],'lineage_manifest':{'evidence_package_id':pkg.package_id,'evidence_package_hash':'x','retrieved_object_ids':[oid]},'validation_status':{}}
    provider=RecordingProvider(payload)
    before=[o.to_dict() for o in obs.list()]
    result=EnterpriseIntelligenceRuntime(BoundedTwinRetrievalService(models,obs,ev), provider=provider).generate(request)
    assert provider.called
    assert result['audit']['status']=='Succeeded'
    assert result['audit']['validation_outcome']=='valid'
    assert (tmp_path/'enterprise_intelligence'/'briefs'/'mod.json').exists()
    assert [o.to_dict() for o in obs.list()] == before


def test_canvas_diagnostics_configured_provider_ready_without_secret(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    monkeypatch.setenv('FLORA_REASONING_PROVIDER', 'openai')
    monkeypatch.setenv('FLORA_REASONING_MODEL', 'gpt-test')
    monkeypatch.setenv('FLORA_REASONING_API_KEY', 'super-secret-key')
    monkeypatch.setenv('FLORA_REASONING_TIMEOUT_SECONDS', '45')
    from cios.applications.flora.enterprise_canvas.access import repair_enterprise_canvas_access
    repair_enterprise_canvas_access('mod','mod','alice','run-1')
    from cios.applications.flora.enterprise_canvas.views import enterprise_canvas_page
    html, status=enterprise_canvas_page('mod', {'X-Flora-User':'alice','X-Flora-Enterprises':'mod','X-Flora-Active-Workspace':'mod'})
    assert status == 200
    assert '<th>Reasoning status</th><td>Ready</td>' in html
    assert '<th>API key available</th><td>yes</td>' in html
    assert '<th>Timeout</th><td>45</td>' in html
    assert 'super-secret-key' not in html
    assert 'Executive Commercial Canvas · governed read model · Overview default' not in html
    assert 'Legacy diagnostic view only' in html
