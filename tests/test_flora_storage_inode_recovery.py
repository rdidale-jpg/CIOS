import json
import os
from pathlib import Path

import pytest

from cios.applications.flora import storage
from cios.applications.flora.storage_maintenance import cleanup_superseded_staging_history, storage_inventory


def test_inode_threshold_fails_before_write(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(storage, "inode_capacity", lambda path=None: {
        "healthy": False, "minimum_available_inodes": 128, "total_inodes": 65536,
        "available_inodes": 0, "free_inodes": 0,
    })
    with pytest.raises(storage.PersistenceError) as caught:
        storage.atomic_write_json(tmp_path / "record.json", {"safe": True})
    assert caught.value.context["operation"] == "inode_preflight"
    assert not (tmp_path / "record.json").exists()


def test_inventory_counts_without_reading_contents(tmp_path):
    (tmp_path / "memory").mkdir(); (tmp_path / "memory" / "evidence.jsonl").write_text("secret")
    hist = tmp_path / "blueprint_import" / "staging_history" / "run" / "v1" / "candidates"
    hist.mkdir(parents=True); (hist / "candidate.json").write_text("not-json-and-confidential")
    diag = tmp_path / "ai_financial_reports" / "diagnostics"; diag.mkdir(parents=True); (diag / "d.json").write_text("private")
    (diag / ".orphan.tmp").write_text("private")
    report = storage_inventory(tmp_path)
    assert report["total_file_count"] == 4
    assert report["temporary_file_count"] == 1
    assert report["diagnostic_file_count"] == 2
    assert report["import_candidate_history_file_count"] == 1
    assert report["contents_inspected"] is False


def test_cleanup_cannot_touch_active_or_canonical_state(tmp_path):
    for version in ("v1", "v2", "v3"):
        path = tmp_path / "blueprint_import" / "staging_history" / "run" / version
        path.mkdir(parents=True); (path / "candidate.json").write_text(version)
        os.utime(path, (int(version[-1]), int(version[-1])))
    active = tmp_path / "blueprint_import" / "staging" / "run" / "candidates"
    active.mkdir(parents=True); (active / "live.json").write_text("live")
    evidence = tmp_path / "memory"; evidence.mkdir(); (evidence / "evidence.jsonl").write_text("canonical")
    result = cleanup_superseded_staging_history(tmp_path, keep_versions=2, dry_run=False)
    assert result["files_selected"] == 1
    assert not (tmp_path / "blueprint_import" / "staging_history" / "run" / "v1").exists()
    assert (active / "live.json").read_text() == "live"
    assert (evidence / "evidence.jsonl").read_text() == "canonical"
