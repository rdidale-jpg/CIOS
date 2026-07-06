import json, os

import pytest

from cios.applications.flora import document_review as review


@pytest.mark.skipif(os.getenv('FLORA_LIVE_RAPID_INTEGRATION_TEST') != '1', reason='opt-in live rapid integration smoke test')
def test_live_rapid_integration_smoke(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    stage = 'start'
    try:
        stage = 'coordinate'
        run = review.coordinate_dual_speed_financial_intelligence_run(run_id='fi-live-rapid-smoke')
        lane = run['rapid_intelligence']
        stage = 'assertions'
        assert lane['source_validation_result'] == 'accepted'
        assert lane['candidate_count'] == 3
        assert all(c.get('source_locator') for c in lane['candidates'])
        assert lane['ai_call_count'] == 0
        assert lane['canonical_write_count'] == 0
        assert lane['source_temporary_file_removed'] is True
        result = {'status': 'PASS', 'stage': stage, 'run_id': run['run_id'], 'candidate_count': lane['candidate_count']}
        print('PASS live rapid integration smoke')
    except Exception as exc:
        result = {'status': 'FAIL', 'stage': stage, 'error': f'{type(exc).__name__}: {exc}'}
        print(f'FAIL live rapid integration smoke at {stage}: {type(exc).__name__}: {exc}')
        raise
    finally:
        out = tmp_path / 'live_rapid_integration_smoke.json'
        out.write_text(json.dumps(result, indent=2, sort_keys=True))
