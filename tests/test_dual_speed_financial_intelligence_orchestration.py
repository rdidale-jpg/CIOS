import pytest

from cios.applications.flora import document_review as review
from cios.applications.flora.memory.repository import EvidenceRepository, EnterpriseModelRepository, ObservationRepository


def _repo_snapshot():
    model = EnterpriseModelRepository().get('bt-group-plc')
    return {
        'evidence': len(EvidenceRepository().list()),
        'observations': len(ObservationRepository().list()),
        'attributes': dict(model.attributes),
    }


def test_dual_speed_mode_persists_combined_standard_run_and_preserves_rapid_result(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    monkeypatch.setattr(review, 'fetch_document', lambda *a, **k: pytest.fail('dual-speed slice 1 must not retrieve live sources'))
    monkeypatch.setattr(review.OpenAIDirectPDFProvider, 'extract_facts', lambda *a, **k: pytest.fail('dual-speed slice 1 must not call OpenAI'))
    monkeypatch.setattr(review.SectionAwareOpenAIProvider, 'extract_packets', lambda *a, **k: pytest.fail('dual-speed slice 1 must not call OpenAI packets'))

    before = _repo_snapshot()
    run = review.refresh_financial_intelligence(run_id='fi-dual-speed', extraction_mode='dual_speed_financial_intelligence')
    after = _repo_snapshot()

    assert (tmp_path / 'ai_financial_reports' / 'runs' / 'fi-dual-speed.json').exists()
    assert run['execution_mode'] == 'dual_speed_financial_intelligence'
    assert run['overall_status'] == 'completed'
    assert run['completion_class'] == 'unverified'
    assert run['rapid_intelligence']['status'] == 'ready'
    assert run['rapid_intelligence']['evidence_status'] == 'fixture_only'
    assert run['rapid_intelligence']['user_result']
    assert run['verification']['status'] == 'unavailable'
    assert run['verification']['adapter_handoff_attempted'] is False
    assert run['verification']['adapter_result'] is None
    assert run['verification']['exceptions']
    assert run['canonical_update']['status'] == 'not_applicable'
    assert run['canonical_update']['enterprise_model_updated'] is False
    assert run['canonical_update']['evidence_ids'] == []
    assert run['canonical_update']['observation_ids'] == []
    assert run['canonical_update']['attributes_updated'] == []
    assert run['cost_summary']['ai_call_count'] == 0
    assert run['cost_summary']['estimated_provider_cost_usd'] == 0
    assert run['cost_summary']['external_source_call_count'] == 0
    assert before == after


def test_dual_speed_progress_and_result_render_from_standard_run_only(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    run = review.refresh_financial_intelligence(run_id='fi-dual-render', extraction_mode='dual_speed_financial_intelligence')
    legacy = tmp_path / 'ai_financial_reports' / 'rapid_runs' / 'fi-dual-render.json'
    assert legacy.exists()
    legacy.unlink()

    status = review.financial_intelligence_progress_status('fi-dual-render')
    html, code = review.financial_intelligence_run_response('fi-dual-render')

    assert status['terminal'] is True
    assert status['final_result_url'] == '/financial-intelligence/fi-dual-render'
    assert code == 200
    assert 'Rapid Financial Pressure and Transformation Outlook' in html
    assert 'Verification summary' in html
    assert 'Status: unavailable' in html
    assert 'Canonical update summary' in html
    assert 'Status: not_applicable' in html
    assert 'Fixture-only evidence warning' in html
    assert 'not verified official evidence' in html
    assert run['rapid_intelligence']['user_result'].splitlines()[0] in html


def test_dual_speed_fixture_is_not_default(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    created = {}

    def fake_background(enterprise_id, run_id, extraction_mode='structured_standard_financials'):
        created['mode'] = extraction_mode

    monkeypatch.setattr(review.threading, 'Thread', lambda target, args, daemon: type('T', (), {'start': lambda self: target(*args)})())
    monkeypatch.setattr(review, '_background_refresh', fake_background)
    run = review.create_financial_intelligence_progress_run('bt-group-plc')
    assert run['extraction_mode'] == 'structured_standard_financials'
    assert created['mode'] == 'structured_standard_financials'


def test_unsupported_mode_still_rejected(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    with pytest.raises(ValueError):
        review.refresh_financial_intelligence(run_id='fi-bad-mode', extraction_mode='unsupported_mode')
