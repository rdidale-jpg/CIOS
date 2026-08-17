import importlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

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


def test_atomic_json_writes_use_request_unique_temporary_paths(monkeypatch, tmp_path):
    from cios.applications.flora import storage

    destination = tmp_path / "blueprint_import" / "packages" / "receipt.json"
    temporary_paths = []
    real_replace = storage.os.replace

    def record_replace(source, target):
        temporary_paths.append(Path(source))
        return real_replace(source, target)

    monkeypatch.setattr(storage.os, "replace", record_replace)
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda value: storage.atomic_write_json(destination, {"value": value}), range(32)))

    assert len(temporary_paths) == len(set(temporary_paths)) == 32
    assert destination.exists()
    assert not list(destination.parent.glob(".*.tmp"))


def test_persistence_error_preserves_enospc_filesystem_context(monkeypatch, tmp_path):
    from cios.applications.flora import storage

    destination = tmp_path / "packages" / "receipt.json"
    real_open = Path.open

    def no_space(path, *args, **kwargs):
        if Path(path).name.startswith(".receipt.json"):
            raise OSError(28, "No space left on device", str(path))
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", no_space)
    with pytest.raises(storage.PersistenceError) as raised:
        storage.atomic_write_json(destination, {"status": "received"})

    context = raised.value.context
    assert context["errno"] == 28
    assert context["operation"] == "atomic_write"
    assert context["path"] == str(destination.resolve())
    assert context["available_bytes"] >= 0
    assert context["available_inodes"] >= 0
    assert context["filesystem_device_id"] == tmp_path.stat().st_dev


def test_web_process_fails_before_listening_when_storage_probe_fails(monkeypatch):
    from cios.applications.flora.web import app

    monkeypatch.setattr(app, "startup_storage_status", lambda: {
        "ready": False,
        "status": "storage unavailable",
        "data_root": "/var/data/flora",
        "storage_mode": "persistent pilot storage",
        "error": "safe storage failure",
    })
    monkeypatch.setattr(app, "ThreadingHTTPServer", lambda *args: pytest.fail("server must not listen"))

    with pytest.raises(SystemExit, match="persistent storage is unavailable"):
        app.run()


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
