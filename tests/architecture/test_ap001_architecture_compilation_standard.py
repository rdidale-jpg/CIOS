from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AP001 = ROOT / "architecture/reference-architecture/standards/AP-001-Architecture-Compilation-Standard.md"
REGISTRY = ROOT / "architecture/reference-architecture/Architecture-Authority-Registry.md"
DOCUMENT_MAP = ROOT / "architecture/reference-architecture/Document-Map.md"
MANIFEST = ROOT / "FLORA_ARCHITECTURE_DOWNLOAD_MANIFEST.json"
EU001 = ROOT / "architecture/enterprise-intelligence/contracts/EU-001-Enterprise-Understanding-Contract.md"
ADR023 = ROOT / "architecture/decisions/ADR-023-Enterprise-Understanding-as-the-Primary-Governed-Asset.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_ap001_exists_as_documentation_only_architecture_standard() -> None:
    text = _read(AP001)
    assert "# AP-001" in text
    assert "**Status:** Accepted" in text
    assert "Documentation-only governance standard" in text
    assert "does not change runtime behaviour" in text


def test_ap001_uses_authority_registry_as_compilation_foundation() -> None:
    text = _read(AP001)
    assert "Authority Registry is the control plane for architecture compilation" in text
    assert "the registry wins" in text
    for profile in ["architecture-authority", "researcher-pack", "reviewer-pack", "review-context"]:
        assert profile in text


def test_registry_registers_ap001_and_preserves_review_exclusions() -> None:
    text = _read(REGISTRY)
    assert "AP-001" in text
    assert AP001.relative_to(ROOT).as_posix() in text
    assert "Architecture Authority Registry; Reference Architecture; Document Map" in text
    assert "EU-001" in text and "ADR-023" in text
    assert "excluded from `architecture-authority`, `researcher-pack` and `reviewer-pack`" in text


def test_document_map_points_to_ap001() -> None:
    text = _read(DOCUMENT_MAP)
    assert "AP-001" in text
    assert "standards/AP-001-Architecture-Compilation-Standard.md" in text


def test_ap001_does_not_change_production_export_profile() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    exported = {
        item["path"]
        for profile in manifest["export_profiles"].values()
        for item in profile["files"]
    }
    assert AP001.relative_to(ROOT).as_posix() not in exported
    assert EU001.relative_to(ROOT).as_posix() not in exported
    assert ADR023.relative_to(ROOT).as_posix() not in exported
