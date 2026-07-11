from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AP002 = ROOT / "architecture/reference-architecture/standards/AP-002-Architecture-Metadata-Standard.md"
REGISTRY = ROOT / "architecture/reference-architecture/Architecture-Authority-Registry.md"
DOCUMENT_MAP = ROOT / "architecture/reference-architecture/Document-Map.md"
MANIFEST = ROOT / "FLORA_ARCHITECTURE_DOWNLOAD_MANIFEST.json"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_ap002_exists_as_documentation_only_architecture_standard() -> None:
    text = _read(AP002)
    assert "# AP-002" in text
    assert "**Status:** Accepted" in text
    assert "Documentation-only governance standard" in text
    assert "does not change runtime behaviour" in text


def test_ap002_defines_required_canonical_metadata_groups() -> None:
    text = _read(AP002)
    for group in [
        "`identity`",
        "`type`",
        "`status`",
        "`authority`",
        "`owner`",
        "`dependencies`",
        "`profiles`",
        "`lifecycle`",
    ]:
        assert group in text


def test_ap002_aligns_with_authority_registry_and_profile_compilation() -> None:
    text = _read(AP002)
    assert "The Authority Registry remains the control plane" in text
    assert "the registry wins" in text
    assert "A compiler can determine profile membership by reading `profiles.membership` and `profiles.exclusions`" in text
    for profile in ["architecture-authority", "researcher-pack", "reviewer-pack", "review-context", "none"]:
        assert profile in text


def test_registry_registers_ap002_with_backward_compatible_columns() -> None:
    text = _read(REGISTRY)
    assert "AP-002" in text
    assert AP002.relative_to(ROOT).as_posix() in text
    assert "Architecture Authority Registry; AP-001; Document Map" in text
    assert "architecture-authority" in text


def test_document_map_points_to_ap002() -> None:
    text = _read(DOCUMENT_MAP)
    assert "AP-002" in text
    assert "standards/AP-002-Architecture-Metadata-Standard.md" in text


def test_ap002_does_not_change_production_export_profile() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    exported = {
        item["path"]
        for profile in manifest["export_profiles"].values()
        for item in profile["files"]
    }
    assert AP002.relative_to(ROOT).as_posix() not in exported
