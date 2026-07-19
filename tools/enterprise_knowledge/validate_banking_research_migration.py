#!/usr/bin/env python3
"""Validate Banking Workstream 0 source ZIP archive-member lineage."""
from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INV = ROOT / "enterprise-knowledge/banking/research-migration/package-validation-inventory.json"
REG = ROOT / "enterprise-knowledge/banking/research-migration/source-document-registry.json"
CAN = ROOT / "enterprise-knowledge/banking/canonical/banking-research-canonical-objects.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    inventory = json.loads(INV.read_text())
    registry = json.loads(REG.read_text())
    canonical = json.loads(CAN.read_text())

    package_members = {}
    for package in inventory["packages"]:
        zip_path = ROOT / package["source_zip_path"]
        if not zip_path.exists():
            fail(f"source ZIP does not exist: {package['source_zip_path']}")
        actual_sha = sha256_file(zip_path)
        if actual_sha != package["source_zip_sha256"]:
            fail(f"inventory ZIP hash mismatch for {package['source_zip_path']}")
        with zipfile.ZipFile(zip_path) as archive:
            bad_member = archive.testzip()
            if bad_member is not None:
                fail(f"ZIP integrity failed for {package['source_zip_path']} at {bad_member}")
            package_members[package["source_zip_path"]] = set(archive.namelist())
        inventoried = {member["archive_member_path"] for member in package["archive_members"]}
        if inventoried != package_members[package["source_zip_path"]]:
            fail(f"archive member inventory disagreement for {package['source_zip_path']}")

    registry_by_id = {doc["source_document_id"]: doc for doc in registry}
    registry_by_path = {(doc["source_zip_path"], doc["archive_member_path"]): doc for doc in registry}
    traced_by_zip = {package["source_zip_path"]: 0 for package in inventory["packages"]}

    for obj in canonical["canonical_objects"]:
        if not obj.get("source_zip_path"):
            fail(f"canonical object has no source ZIP: {obj.get('object_id')}")
        if not obj.get("archive_member_path"):
            fail(f"canonical object has no archive member path: {obj.get('object_id')}")
        zip_path = ROOT / obj["source_zip_path"]
        if not zip_path.exists():
            fail(f"object source ZIP missing on disk: {obj.get('object_id')}")
        if sha256_file(zip_path) != obj.get("source_zip_sha256"):
            fail(f"object ZIP hash mismatch: {obj.get('object_id')}")
        if obj["archive_member_path"] not in package_members.get(obj["source_zip_path"], set()):
            fail(f"object archive member not found in ZIP: {obj.get('object_id')}")
        doc = registry_by_id.get(obj.get("source_document_id"))
        if doc is None:
            fail(f"object source_document_id not in registry: {obj.get('object_id')}")
        key = (obj["source_zip_path"], obj["archive_member_path"])
        if registry_by_path.get(key) != doc:
            fail(f"registry disagrees with object lineage: {obj.get('object_id')}")
        if doc.get("source_zip_sha256") != obj.get("source_zip_sha256"):
            fail(f"registry ZIP hash disagrees for object: {obj.get('object_id')}")
        if doc.get("archive_member_sha256") != obj.get("archive_member_sha256"):
            fail(f"registry member hash disagrees for object: {obj.get('object_id')}")
        traced_by_zip[obj["source_zip_path"]] += 1

    missing = [zip_path for zip_path, count in traced_by_zip.items() if count == 0]
    if missing:
        fail(f"no canonical object traced for source ZIP(s): {', '.join(missing)}")

    print("Banking research migration lineage validation passed")
    for zip_path, count in sorted(traced_by_zip.items()):
        print(f"{zip_path}: {count} canonical objects traced")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
