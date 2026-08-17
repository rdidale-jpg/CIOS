import json

import pytest

from cios.applications.flora.blueprint_import.lifecycle import (
    ImportLifecycleService,
    TwinImportLifecycleService,
)
from cios.applications.flora.blueprint_import.models import (
    BlueprintPackageIdentity,
    BlueprintPackageRecord,
)
from cios.applications.flora.blueprint_import.registry import BlueprintPackageRegistry
from cios.applications.flora.blueprint_import.views import delete_candidate_preview_page, history_page
from cios.applications.flora.storage import atomic_write_json, data_path

HEADERS = {"X-Flora-User": "alice", "X-Flora-Enterprises": "BNK-001", "X-Flora-Roles": "blueprint_import_admin"}


def _package(run_id, twin_id="BNK-001", version="1"):
    inspection = {"twin_id": twin_id, "twin_type": "industry", "primary_subject_id": twin_id,
                  "primary_subject_name": "UK Banking" if twin_id == "BNK-001" else "Energy",
                  "primary_subject_class": "industry", "governed_scope": "UK",
                  "canonical_owner": twin_id, "package_version": version,
                  "contract_type": "Governed Industry Twin Package"}
    record = BlueprintPackageRecord("1", f"pkg-ref-{run_id}", BlueprintPackageIdentity(twin_id, version, twin_id, "1"),
                                    (run_id * 64)[:64], 3, f"{run_id}.zip",
                                    f"blueprint_import/archives/{run_id}/{run_id}.zip", (), "received",
                                    f"2026-08-17T00:00:0{version}+00:00", "alice", run_id, "", inspection)
    atomic_write_json(BlueprintPackageRegistry()._path_for_ref(record.package_ref), record.to_dict())
    archive = data_path(record.archive_path); archive.parent.mkdir(parents=True, exist_ok=True); archive.write_bytes(b"zip")
    return record


def test_candidate_delete_preview_confirmation_tombstone_and_storage_safety(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path)); package = _package("candidate")
    atomic_write_json(data_path("blueprint_import", "staging", "candidate", "candidates", "one.json"), {"candidate_record_id": "one"})
    canonical = data_path("memory", "evidence.jsonl"); canonical.parent.mkdir(parents=True); canonical.write_text("canonical\n")

    preview, status = delete_candidate_preview_page("candidate", HEADERS)
    assert status == 200 and "Canonical intelligence affected</th><td>NO" in preview
    with pytest.raises(ValueError, match="Type DELETE"):
        TwinImportLifecycleService().delete_candidate("candidate", "alice", "yes")
    result = TwinImportLifecycleService().delete_candidate("candidate", "alice", "DELETE CANDIDATE IMPORT")

    assert result["canonical_impact"] == "none" and result["recovered_files"] == 2
    assert canonical.read_text() == "canonical\n"
    assert BlueprintPackageRegistry().get(package.package_ref) is None
    assert data_path("blueprint_import", "tombstones", "candidate.json").exists()
    assert any(e["event_type"] == "candidate_import_deleted" for e in TwinImportLifecycleService().registry.ledger.list())


def test_promoted_delete_blocked_and_same_twin_superseded_only_after_promotion(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path)); old = _package("old", version="1")
    ImportLifecycleService().mark_promoted(old.import_run_id, "alice", 4)
    service = TwinImportLifecycleService()
    assert service.delete_preview("old")["permitted"] is False
    with pytest.raises(ValueError, match="cannot be hard-deleted"):
        service.delete_candidate("old", "alice", "DELETE CANDIDATE IMPORT")

    replacement = _package("new", version="2")
    assert service.current_release(replacement).import_run_id == "old"
    # Validation and review alone never change the current release.
    assert ImportLifecycleService().get("old").state == "promoted"
    ImportLifecycleService().mark_promoted("new", "alice", 5)
    previous = service.supersede_previous_after_promotion(replacement, "alice")
    assert previous.import_run_id == "old"
    assert ImportLifecycleService().get("new").current is True
    assert ImportLifecycleService().get("old").state == "superseded"
    assert ImportLifecycleService().get("old").superseded_by == "new"


def test_different_twin_and_failed_candidate_leave_current_unchanged(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path)); old = _package("bank", version="1")
    ImportLifecycleService().mark_promoted(old.import_run_id, "alice", 1)
    energy = _package("energy", "NRG-001", "2")
    failed_same_twin = _package("failed", version="3")
    service = TwinImportLifecycleService()
    assert service.current_release(energy) is None
    assert service.current_release(failed_same_twin).import_run_id == "bank"
    assert ImportLifecycleService().get("bank").state == "promoted"
    assert ImportLifecycleService().get("failed").state == "received"

    html, status = history_page(HEADERS | {"X-Flora-Enterprises": "BNK-001,NRG-001"})
    assert status == 200 and "Delete candidate import" in html and "Import newer release" in html
    assert "Twin ID" in html and "Current / superseded" in html
