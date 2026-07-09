from __future__ import annotations

import io
import json
import stat
import zipfile
from pathlib import Path

import pytest

from cios.applications.flora.access import can_receive_blueprint_package
from cios.applications.flora.blueprint_import import BlueprintPackageRegistry, PackageReceiptError
from cios.applications.flora.blueprint_import.archive import sha256_bytes


def package_bytes(files: dict[str, bytes] | None = None, manifest: dict | None = None) -> bytes:
    manifest = manifest or {
        "package_id": "synthetic-blueprint",
        "package_version": "1.0.0",
        "enterprise_id": "synthetic-enterprise",
        "profile_version": "0.1",
    }
    files = files or {"records/example.json": b'{"kind":"synthetic"}\n'}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("blueprint_manifest.json", json.dumps(manifest))
        for name, content in files.items():
            zf.writestr(name, content)
    return buf.getvalue()


def test_successful_package_receipt_checksum_inventory_import_run_and_audit(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    content = package_bytes({"records/example.json": b"hello"})

    record = BlueprintPackageRegistry().receive(content, "synthetic.zip", "alice")

    assert record.status == "received"
    assert record.identity.package_id == "synthetic-blueprint"
    assert record.package_sha256 == sha256_bytes(content)
    assert {item.path for item in record.inventory} == {"blueprint_manifest.json", "records/example.json"}
    assert any(item.sha256 == sha256_bytes(b"hello") for item in record.inventory)
    assert record.import_run_id.startswith("bpi-run-")
    assert (tmp_path / "blueprint_import" / "packages" / f"{record.package_ref}.json").exists()
    assert (tmp_path / "blueprint_import" / "runs" / f"{record.import_run_id}.json").exists()
    events = (tmp_path / "blueprint_import" / "audit" / "events.jsonl").read_text(encoding="utf-8")
    assert "package_received" in events


def test_duplicate_receipt_returns_existing_record_and_logs_duplicate(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    content = package_bytes()
    registry = BlueprintPackageRegistry()

    first = registry.receive(content, "synthetic.zip", "alice")
    second = registry.receive(content, "synthetic.zip", "bob")

    assert second == first
    package_files = list((tmp_path / "blueprint_import" / "packages").glob("*.json"))
    assert len(package_files) == 1
    events = (tmp_path / "blueprint_import" / "audit" / "events.jsonl").read_text(encoding="utf-8")
    assert "package_duplicate_detected" in events


def test_original_archive_is_preserved_immutably(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    content = package_bytes()

    record = BlueprintPackageRegistry().receive(content, "synthetic.zip", "alice")

    archived = tmp_path / record.archive_path
    assert archived.read_bytes() == content
    assert stat.S_IMODE(archived.stat().st_mode) & 0o222 == 0


@pytest.mark.parametrize(
    "content,filename,actor",
    [
        (b"", "synthetic.zip", "alice"),
        (b"not a zip", "synthetic.zip", "alice"),
        (package_bytes(), "../synthetic.zip", "alice"),
        (package_bytes(), "synthetic.txt", "alice"),
        (package_bytes(), "synthetic.zip", ""),
    ],
)
def test_invalid_input_rejected_and_no_acceptance_record(monkeypatch, tmp_path, content, filename, actor):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))

    with pytest.raises(PackageReceiptError):
        BlueprintPackageRegistry().receive(content, filename, actor)

    assert not (tmp_path / "blueprint_import" / "packages").exists()
    assert not (tmp_path / "blueprint_import" / "runs").exists()


def test_unsafe_zip_member_rolls_back_acceptance_records(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("blueprint_manifest.json", json.dumps({
            "package_id": "synthetic-blueprint",
            "package_version": "1.0.0",
            "enterprise_id": "synthetic-enterprise",
            "profile_version": "0.1",
        }))
        zf.writestr("../escape.txt", "bad")

    with pytest.raises(PackageReceiptError):
        BlueprintPackageRegistry().receive(buf.getvalue(), "synthetic.zip", "alice")

    assert not (tmp_path / "blueprint_import" / "packages").exists()
    assert not (tmp_path / "blueprint_import" / "runs").exists()
    assert "package_receipt_failed" in (tmp_path / "blueprint_import" / "audit" / "events.jsonl").read_text(encoding="utf-8")


def test_receipt_does_not_mutate_canonical_memory(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))

    BlueprintPackageRegistry().receive(package_bytes(), "synthetic.zip", "alice")

    assert not (tmp_path / "memory" / "evidence.jsonl").exists()
    assert not (tmp_path / "memory" / "observations.jsonl").exists()
    assert not (tmp_path / "memory" / "enterprise_models").exists()


def test_access_control_for_blueprint_package_receipt():
    assert can_receive_blueprint_package({"X-Flora-User": "alice", "X-Flora-Roles": "package.upload"})
    assert can_receive_blueprint_package({"X-Flora-User": "alice", "X-Flora-Roles": "blueprint_import_admin"})
    assert not can_receive_blueprint_package({"X-Flora-Roles": "package.upload"})
    assert not can_receive_blueprint_package({"X-Flora-User": "alice", "X-Flora-Roles": "canvas.view"})
