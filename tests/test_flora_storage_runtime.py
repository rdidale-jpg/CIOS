import importlib
from pathlib import Path

from cios.applications.flora.memory.service import ObservationMemoryService


def evidence():
    return {
        'evidence_id': 'EV-DIR', 'organisation': 'BT Group plc', 'cleaned_observation': 'Revenue was £20.4bn.',
        'commercial_condition': 'financial_metric_reported', 'confidence': 90, 'extraction_timestamp': '2026-07-04T10:00:00+00:00',
        'publication_date': '2026-07-01', 'page_range': '5', 'page_number': 5,
    }


def test_startup_validation_is_idempotent_and_reports_durability(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path / 'flora'))
    from cios.applications.flora import storage
    first = storage.startup_storage_status()
    second = storage.startup_storage_status()
    assert first['ready'] and second['ready']
    assert first['status'] == 'configured pilot storage'
    assert Path(first['data_root']).exists()


def test_default_storage_uses_render_persistent_pilot_disk(monkeypatch):
    monkeypatch.delenv('FLORA_DATA_DIR', raising=False)
    monkeypatch.delenv('FLORA_PILOT_DIR', raising=False)
    from cios.applications.flora import storage

    status = storage.startup_storage_status()

    assert status['ready'] is True
    assert status['status'] == 'persistent pilot storage'
    assert status['data_root'] == '/var/data/flora'
    assert status['durable'] is True


def test_accepted_facts_observations_and_model_persist_under_flora_data_dir(monkeypatch, tmp_path):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path / 'flora'))
    import cios.applications.flora.memory.repository as repo
    repo = importlib.reload(repo)
    svc = ObservationMemoryService(repo.ObservationRepository(), repo.EnterpriseModelRepository())
    report = svc.process_evidence(evidence())
    assert report.factual_claims_accepted == 1
    assert (tmp_path / 'flora' / 'memory' / 'observations.jsonl').exists()
    assert list((tmp_path / 'flora' / 'memory' / 'enterprise_models').glob('*.json'))

    restarted = ObservationMemoryService(repo.ObservationRepository(), repo.EnterpriseModelRepository())
    assert restarted.observations.list()
    assert restarted.models.get('bt-group-plc').attributes


def test_no_runtime_module_has_hard_coded_production_flora_pilot_paths():
    root = Path('cios/applications/flora')
    offenders = []
    for path in root.rglob('*.py'):
        text = path.read_text(encoding='utf-8')
        if '.flora_pilot' in text and path.name != 'storage.py':
            offenders.append(str(path))
    assert offenders == []
