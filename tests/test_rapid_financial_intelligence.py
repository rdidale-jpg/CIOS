from cios.applications.flora.financial_intelligence.rapid import run_rapid_financial_intelligence
from tests.fixtures.rapid_financial import bt_fy26_seeded_rapid_result


def test_production_rapid_requires_accepted_source_receipt(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    run = run_rapid_financial_intelligence('bt-group-plc', run_id='rfi-bt')
    assert run['status'] == 'unavailable_source_precondition_failed'
    assert run['reported_financial_reality'] == []
    assert run['candidate_fact_count'] == 0
    assert run['accepted_canonical_fact_count'] == 0
    assert run['canonical_update']['enterprise_model_updated'] is False
    assert run['metrics']['ai_call_count'] == 0
    assert 'accepted Slice 2A source receipt' in run['user_result']


def test_seeded_bt_fixture_remains_explicitly_test_only():
    run = bt_fy26_seeded_rapid_result('rfi-bt')
    facts = {f['concept']: f for f in run['reported_financial_reality']}
    assert facts['revenue']['value'] == '19,654'
    assert facts['operating_profit']['value'] == '2,897'
    assert facts['profit_before_tax']['value'] == '1,436'
    assert all(f['source_id'] and f['location'] for f in facts.values())
    assert run['accepted_canonical_fact_count'] == 0
    assert run['canonical_update']['enterprise_model_updated'] is False
    assert run['metrics']['ai_call_count'] == 0


def test_rapid_outlook_persists_missing_source_shape(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    first = run_rapid_financial_intelligence('bt-group-plc', run_id='rfi-repeat')
    second = run_rapid_financial_intelligence('bt-group-plc', run_id='rfi-repeat')
    assert first['candidate_fact_count'] == second['candidate_fact_count'] == 0
    assert (tmp_path / 'ai_financial_reports' / 'rapid_runs' / 'rfi-repeat.json').exists()
    assert second['sources'] == []


def test_portability_enterprises_do_not_generate_from_id_and_period(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    for enterprise_id in ('vodafone-group-plc', 'tesco-plc'):
        run = run_rapid_financial_intelligence(enterprise_id, run_id=f'rfi-{enterprise_id}')
        assert run['sources'] == []
        assert run['candidate_fact_count'] == 0
        assert run['accepted_canonical_fact_count'] == 0
        assert run['reported_financial_reality'] == []
        assert run['metrics']['estimated_provider_cost_usd'] == 0
