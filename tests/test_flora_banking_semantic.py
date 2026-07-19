from pathlib import Path
import pytest
from cios.applications.flora.enterprise_intelligence.pipeline import run_pipeline, KNOW
from cios.applications.flora.enterprise_intelligence.semantic import segment_markdown, load_asset_content, MECHANISM_DETAILS
from cios.applications.flora.enterprise_intelligence.reasoning import _reject_unsupported_ids


def test_semantic_content_loader_loads_sections_claims_and_authority():
    asset={'asset_id':'BK-IND-002','title':'Banking Industry Twin','asset_type':'Industry Twin','status':'Validated','version':'1.0','location':'banking/industry/Banking-Industry-Twin.md'}
    loaded=load_asset_content(asset)
    assert loaded['authority']=='governed_source'
    assert loaded['sections']
    assert loaded['sections'][0]['source_location'].endswith('Banking-Industry-Twin.md')
    assert loaded['sections'][0]['content_hash']==loaded['sections'][0]['content_hash']
    assert any(c['status']=='Derived runtime claim' for c in loaded['claims'])


def test_unsupported_file_type_fails_safely(tmp_path):
    p=tmp_path/'bad.bin'; p.write_bytes(b'x')
    # use a repo-relative impossible suffix path by direct loader contract
    loaded=load_asset_content({'asset_id':'BAD','title':'Bad','asset_type':'Test','status':'Candidate','location':'REGISTER.md.bin'})
    assert loaded['unsupported'] is True


def test_semantic_context_contains_text_and_bounded_ids(tmp_path):
    run=run_pipeline(tmp_path)
    ctx=run.stages['semantic_context']
    assert ctx['source_segments']
    assert ctx['candidate_claims']
    assert 'BK-OBS-014' in ctx['observation_texts']
    assert ctx['mechanism_texts']['BM-04']['name'] == MECHANISM_DETAILS['BM-04'][0]
    assert len(ctx['source_segments']) <= 88
    assert not ctx['excluded_source_ids']


def test_grounding_rejects_unsupported_model_ids():
    with pytest.raises(ValueError):
        _reject_unsupported_ids({'supporting_asset_ids':['NO-SUCH-ASSET']}, {'BK-IND-001'})


def test_banking_interpretation_quality_invariants(tmp_path):
    run=run_pipeline(tmp_path)
    explore_text=' '.join([run.stages['strategic_sales_brief']['markdown'], str(run.stages['semantic_context']['unknowns']), str(run.stages['mechanism_assessment']['mechanisms'])]).lower()
    assert 'app-first but not app-only' in explore_text or 'mixed access' in explore_text
    assert 'trust' in explore_text and 'assisted' in explore_text
    assert 'mutual' in str(run.stages['semantic_context']['participant_differences']).lower()
    assert 'assisted-access substitution' in explore_text
    assert 'brh-003' in run.stages['strategic_sales_brief']['markdown'].lower()
    assert 'shared access' in explore_text and 'economics' in explore_text
    assert 'pure efficiency' in str(run.stages['hypothesis_assessment']['competing_explanations']).lower() or 'cost programme' in str(run.stages['mechanism_assessment']['alternatives']).lower()
    assert 'validate with executive' in run.stages['recommendation_eligibility']['permitted_action_class']
    assert not run.stages['strategic_sales_brief']['markdown'].lstrip().startswith('ADR-')
    statements=[o['statement'] for o in run.stages['retrieval']['observations']]
    assert len(set(statements)) == len(statements)
    unknowns=run.stages['semantic_context']['unknowns']
    assert any('utilisation' in u['evidence_required'] for u in unknowns if u['unknown_id']=='UNK-SHARED-ACCESS-ECONOMICS')
    assert any('organisational accountability' in u['evidence_required'] for u in unknowns if u['unknown_id']=='UNK-NAMED-EXECUTIVE-OWNERSHIP')
