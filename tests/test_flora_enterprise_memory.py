import json
import os
from pathlib import Path

import pytest

from cios.applications.flora.memory.enterprise_memory import (
    ENTERPRISE_MODEL_SCHEMA_VERSION,
    FINGERPRINT_SCHEMA_VERSION,
    OBSERVATION_SCHEMA_VERSION,
    EnterpriseMemoryService,
    EnterpriseModel,
    EnterpriseObservation,
    FileEnterpriseModelRepository,
    JsonlObservationLedger,
    render_memory_panel,
    safe_enterprise_id,
)


def service(tmp_path):
    return EnterpriseMemoryService(JsonlObservationLedger(tmp_path / "ledger"), FileEnterpriseModelRepository(tmp_path / "models"))


def test_stable_observation_fingerprint_and_version() -> None:
    one = EnterpriseObservation("bt-group", "profile", "strategy", "AI network operations", "2026-07-04", ["ev-1"], 0.8)
    two = EnterpriseObservation("BT Group", " Profile ", "Strategy", " ai   network operations ", "2026-07-04", ["ev-2"], 0.9)
    assert one.observation_id == two.observation_id
    assert one.fingerprint_schema_version == FINGERPRINT_SCHEMA_VERSION
    assert one.schema_version == OBSERVATION_SCHEMA_VERSION


def test_materially_different_effective_date_or_fact_changes_identity() -> None:
    base = EnterpriseObservation("bt", "profile", "strategy", "AI network operations", "2026-07-04", ["ev-1"], 0.8)
    later = EnterpriseObservation("bt", "profile", "strategy", "AI network operations", "2026-08-01", ["ev-1"], 0.8)
    different = EnterpriseObservation("bt", "profile", "strategy", "cloud migration", "2026-07-04", ["ev-1"], 0.8)
    assert base.observation_id != later.observation_id
    assert base.observation_id != different.observation_id


def test_duplicate_recollection_is_idempotent_and_corroboration_preserves_lineage(tmp_path: Path) -> None:
    s = service(tmp_path)
    first = s.process_evidence(enterprise_id="bt", evidence_id="ev-1", domain="profile", attribute="strategy", value="AI", effective_date="2026-07-04", confidence=0.7)
    same = s.process_evidence(enterprise_id="bt", evidence_id="ev-1", domain="profile", attribute="strategy", value="AI", effective_date="2026-07-04", confidence=0.7)
    corroborated = s.process_evidence(enterprise_id="bt", evidence_id="ev-2", domain="profile", attribute="strategy", value="AI", effective_date="2026-07-04", confidence=0.9)
    rows = s.ledger.list()
    assert first.observation_id == same.observation_id == corroborated.observation_id
    assert len(rows) == 1
    assert rows[0].evidence_ids == ["ev-1", "ev-2"]
    assert len(rows[0].confidence_history) == 2


def test_contradictory_observations_coexist_and_projection_is_marked(tmp_path: Path) -> None:
    s = service(tmp_path)
    a = s.process_evidence(enterprise_id="bt", evidence_id="ev-1", domain="profile", attribute="strategy", value="AI first", effective_date="2026", confidence=0.7)
    b = s.process_evidence(enterprise_id="bt", evidence_id="ev-2", domain="profile", attribute="strategy", value="Cost first", effective_date="2026", confidence=0.8)
    observations = s.ledger.list()
    model = s.load_model("bt")
    assert {o.observation_id for o in observations} == {a.observation_id, b.observation_id}
    assert all(o.status == "contradictory" for o in observations)
    assert model is not None
    assert model.attributes["profile.strategy"]["contradiction_state"] == "contradicted"
    assert set(model.contradictions["profile.strategy"]) == {a.observation_id, b.observation_id}


def test_snapshot_write_is_atomic_when_replace_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = FileEnterpriseModelRepository(tmp_path)
    repo.save(EnterpriseModel(enterprise_id="bt", attributes={"profile.strategy": {"value": "old"}}))
    original = repo.path_for("bt").read_text(encoding="utf-8")
    def fail_replace(src, dst):
        raise RuntimeError("simulated replace failure")
    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(RuntimeError):
        repo.save(EnterpriseModel(enterprise_id="bt", attributes={"profile.strategy": {"value": "new"}}))
    assert repo.path_for("bt").read_text(encoding="utf-8") == original


def test_unsafe_enterprise_identifiers_cannot_escape_memory_directory(tmp_path: Path) -> None:
    repo = FileEnterpriseModelRepository(tmp_path)
    with pytest.raises(ValueError):
        safe_enterprise_id("../../etc/passwd")
    path = repo.path_for("BT Group Plc")
    assert path.parent == tmp_path.resolve()
    assert path.name == "bt-group-plc.json"


def test_persisted_records_have_schema_versions_and_future_versions_are_rejected(tmp_path: Path) -> None:
    s = service(tmp_path)
    s.process_evidence(enterprise_id="bt", evidence_id="ev-1", domain="profile", attribute="strategy", value="AI", effective_date="2026", confidence=0.7)
    observation_record = json.loads((tmp_path / "ledger" / "observations.jsonl").read_text(encoding="utf-8").splitlines()[0])
    model_record = json.loads((tmp_path / "models" / "bt.json").read_text(encoding="utf-8"))
    assert observation_record["schema_version"] == OBSERVATION_SCHEMA_VERSION
    assert model_record["schema_version"] == ENTERPRISE_MODEL_SCHEMA_VERSION
    observation_record["schema_version"] = 99
    with pytest.raises(ValueError):
        EnterpriseObservation.from_record(observation_record)
    model_record["schema_version"] = 99
    with pytest.raises(ValueError):
        EnterpriseModel.from_record(model_record)


def test_malformed_trailing_jsonl_record_is_reported_and_valid_records_survive(tmp_path: Path) -> None:
    ledger = JsonlObservationLedger(tmp_path)
    good = EnterpriseObservation("bt", "profile", "strategy", "AI", "2026", ["ev-1"], 0.7)
    ledger.append(good)
    with ledger.path.open("ab") as fh:
        fh.write(b'{"schema_version": 1')
    assert ledger.path.read_text(encoding="utf-8").splitlines()[0]
    with pytest.raises(ValueError, match="malformed trailing Observation record"):
        ledger.list()


def test_restart_durability_observatory_view_and_idempotent_reprocessing(tmp_path: Path) -> None:
    s1 = service(tmp_path)
    created = s1.process_evidence(enterprise_id="bt", evidence_id="ev-1", domain="profile", attribute="strategy", value="AI network operations", effective_date="2026", confidence=0.8)
    del s1
    s2 = service(tmp_path)
    loaded = s2.load_model("bt")
    assert loaded is not None
    html = render_memory_panel(loaded)
    assert "AI network operations" in html
    assert "profile.strategy" in html
    repeated = s2.process_evidence(enterprise_id="bt", evidence_id="ev-1", domain="profile", attribute="strategy", value="AI network operations", effective_date="2026", confidence=0.8)
    assert repeated.observation_id == created.observation_id
    assert len(s2.ledger.list()) == 1


def test_report_deletion_or_regeneration_does_not_delete_enterprise_memory(tmp_path: Path) -> None:
    s = service(tmp_path / "memory")
    s.process_evidence(enterprise_id="bt", evidence_id="ev-1", domain="profile", attribute="strategy", value="AI", effective_date="2026", confidence=0.8)
    report = tmp_path / "report.html"
    report.write_text(render_memory_panel(s.load_model("bt")), encoding="utf-8")
    report.unlink()
    assert s.load_model("bt") is not None
    assert len(s.ledger.list()) == 1
