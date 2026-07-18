from pathlib import Path
import hashlib, pytest
from pydantic import BaseModel
from cios.applications.flora.enterprise_intelligence.pipeline import run_pipeline, KNOW, ASSETS, OBS, MECH, retrieve
from cios.applications.flora.enterprise_intelligence.models import ContextPlan


def file_hashes():
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (KNOW/'banking').rglob('*') if p.is_file()}

def test_complete_banking_run_succeeds_and_outputs(tmp_path):
    run=run_pipeline(tmp_path)
    assert run.validation.passed
    assert (tmp_path/'pipeline-run.json').exists()
    assert (tmp_path/'execution-trace.txt').exists()
    assert (tmp_path/'strategic-sales-brief.md').exists()
    assert 'BRH-003' in (tmp_path/'strategic-sales-brief.md').read_text()
    assert run.stages['retrieval']['hypothesis']['hypothesis_id']=='BRH-003'
    assert set(run.stages['hypothesis_assessment']['supporting_observations'])==set(OBS)
    assert set(run.stages['hypothesis_assessment']['supporting_mechanisms'])==set(MECH)

def test_authority_and_source_assets_unchanged(tmp_path):
    before=file_hashes(); run=run_pipeline(tmp_path); after=file_hashes()
    assert before==after
    assert all(stage['authority']!='governed_source' for stage in run.stages.values())
    assert run.stages['learning_capture']['repository_mutation_allowed'] is False

def test_hallucinated_asset_id_rejected():
    plan=ContextPlan(object_id='x',run_id='r',required_asset_classes=[],hypothesis_id='BRH-003',observation_ids=OBS,mechanism_ids=MECH,manifest_asset_ids=['NO-SUCH-ASSET'],required_stages=[],required_output='Strategic Sales Brief')
    with pytest.raises(ValueError, match='unsupported asset ID'):
        retrieve('r', plan)

def test_missing_enterprise_specificity_and_named_executive_are_downgraded(tmp_path):
    run=run_pipeline(tmp_path)
    assert run.stages['enterprise_context']['enterprise_specificity']=='Unknown'
    assert 'No named enterprise-specific claim' in run.stages['strategic_sales_brief']['markdown']
    assert run.stages['executive_relevance']['named_executive']=='Unknown'
    assert 'named executive: **Unknown**' in run.stages['strategic_sales_brief']['markdown']

def test_unknowns_and_contradictions_propagate_to_brief(tmp_path):
    run=run_pipeline(tmp_path)
    assert run.stages['strategic_sales_brief']['unknowns']
    assert run.stages['strategic_sales_brief']['contradictions']
    md=run.stages['strategic_sales_brief']['markdown']
    assert 'What remains Unknown?' in md and 'What contradicts the view?' in md

def test_recommendation_gate_prevents_proposal_level_action(tmp_path):
    run=run_pipeline(tmp_path)
    rec=run.stages['recommendation_eligibility']
    assert rec['permitted_action_class']=='validate with executive'
    assert rec['status']=='DOWNGRADED'
    assert 'proposal' in rec['prohibited_actions']

def test_lineage_resolves_from_recommendation_to_observations(tmp_path):
    run=run_pipeline(tmp_path)
    assert 'BRH-003' in run.stages['recommendation_eligibility']['source_asset_ids']
    assert set(OBS) <= set(run.stages['hypothesis_assessment']['supporting_observations'])
    retrieved={a['asset_id'] for a in run.stages['retrieval']['assets']}
    assert set(ASSETS) <= retrieved

def test_failure_safety_and_invalid_structured_output(tmp_path):
    before=file_hashes()
    with pytest.raises(ValueError):
        run_pipeline(tmp_path, extra_asset_ids=['FAKE-ID'])
    assert before==file_hashes()
    class BadAdapter:
        model_name='unavailable-model'; instruction_version='bad'
        def execute(self, task, context, output_schema): return {'not':'used'}
    run=run_pipeline(tmp_path, adapter=BadAdapter())
    assert run.validation.passed

# Architectural fitness tests

def test_fitness_controls(tmp_path):
    run=run_pipeline(tmp_path)
    assert 'hypothesis->challenge->executive role' in run.stages['commercial_assessment']['relationship_paths']
    assert all(o['object_type']!='observation' for o in run.stages.values())
    assert all(g['status']=='PASS' for g in run.validation.gates)
    assert run.stages['strategic_sales_brief']['unknowns']
    assert run.stages['strategic_sales_brief']['contradictions']
    assert run.stages['executive_relevance']['named_executive']=='Unknown'
    assert 'production' not in str(run.telemetry).lower()
    assert run.stages['learning_capture']['repository_mutation_allowed'] is False
    assert 'provider' not in ''.join(run.stages.keys()).lower()
    assert len(run.audit_events)==13
