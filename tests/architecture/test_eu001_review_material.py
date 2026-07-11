from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EU001 = ROOT / "architecture/enterprise-intelligence/contracts/EU-001-Enterprise-Understanding-Contract.md"
ADR023 = ROOT / "architecture/decisions/ADR-023-Enterprise-Understanding-as-the-Primary-Governed-Asset.md"
CHECKLIST = ROOT / "architecture/reviews/EU-001-Review-and-Acceptance-Checklist.md"
REGISTRY = ROOT / "architecture/reference-architecture/Architecture-Authority-Registry.md"
MANIFEST = ROOT / "FLORA_ARCHITECTURE_DOWNLOAD_MANIFEST.json"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_eu001_and_adr023_statuses_remain_review_only() -> None:
    assert "**Status:** Review" in _read(EU001)
    assert "**Status:** Proposed" in _read(ADR023)
    assert "not accepted and not authoritative" in _read(REGISTRY)


def test_review_material_paths_and_ids_are_unique() -> None:
    paths = [EU001, ADR023, CHECKLIST, REGISTRY]
    assert all(path.exists() for path in paths)
    assert len({path.relative_to(ROOT).as_posix() for path in paths}) == len(paths)
    ids = ["EU-001", "ADR-023"]
    for document_id in ids:
        matches = [path for path in paths if document_id in _read(path)]
        assert matches


def test_review_material_excluded_from_production_export_profile() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    exported = {
        item["path"]
        for profile in manifest["export_profiles"].values()
        for item in profile["files"]
    }
    assert EU001.relative_to(ROOT).as_posix() not in exported
    assert ADR023.relative_to(ROOT).as_posix() not in exported
    assert CHECKLIST.relative_to(ROOT).as_posix() not in exported


def test_registry_records_dependencies_and_validation_trigger() -> None:
    text = _read(REGISTRY)
    for dependency in ["Reference Architecture", "EI-001", "EI-002", "EI-003", "EI-012", "FP-009", "ADR-009"]:
        assert dependency in text
    assert "MOD and one materially different enterprise" in text
    assert "excluded from `architecture-authority`, `researcher-pack` and `reviewer-pack`" in text
