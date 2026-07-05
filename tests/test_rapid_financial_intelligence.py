from cios.applications.flora.financial_intelligence.rapid import run_rapid_financial_intelligence


def test_bt_rapid_outlook_has_expected_candidate_facts_without_canonical_update(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    run = run_rapid_financial_intelligence('bt-group-plc', run_id='rfi-bt')
    facts = {f['concept']: f for f in run['reported_financial_reality']}
    assert facts['revenue']['value'] == '19,654'
    assert facts['operating_profit']['value'] == '2,897'
    assert facts['profit_before_tax']['value'] == '1,436'
    assert all(f['source_id'] and f['location'] for f in facts.values())
    assert run['accepted_canonical_fact_count'] == 0
    assert run['canonical_update']['enterprise_model_updated'] is False
    assert run['metrics']['ai_call_count'] == 0
    assert 'Hypothesis' not in ''.join(f['label'] for f in facts.values())


def test_rapid_outlook_persists_and_is_idempotent_shape(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    first = run_rapid_financial_intelligence('bt-group-plc', run_id='rfi-repeat')
    second = run_rapid_financial_intelligence('bt-group-plc', run_id='rfi-repeat')
    assert first['candidate_fact_count'] == second['candidate_fact_count']
    assert (tmp_path / 'ai_financial_reports' / 'rapid_runs' / 'rfi-repeat.json').exists()
    assert all(s['temporary_file_cleaned_up'] for s in second['sources'])


def test_portability_two_additional_enterprises_without_company_parser(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    for enterprise_id in ('vodafone-group-plc', 'tesco-plc'):
        run = run_rapid_financial_intelligence(enterprise_id, run_id=f'rfi-{enterprise_id}')
        assert run['sources'][0]['url'].startswith('https://')
        assert run['candidate_fact_count'] >= 1
        assert run['accepted_canonical_fact_count'] == 0
        assert run['reported_financial_reality'][0]['location']
        assert run['metrics']['estimated_provider_cost_usd'] == 0
