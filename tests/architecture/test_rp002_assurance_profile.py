from __future__ import annotations

from pathlib import Path

from cios.architecture import (
    compile_architecture_profile,
    compile_assurance_runtime_package,
    parse_authority_registry,
)

ROOT = Path(__file__).resolve().parents[2]
RP002 = ROOT / "architecture/reference-architecture/profiles/RP-002-Enterprise-Intelligence-Assurance-Profile.md"
REGISTRY = ROOT / "architecture/reference-architecture/Architecture-Authority-Registry.md"
DOCUMENT_MAP = ROOT / "architecture/reference-architecture/Document-Map.md"

EXPECTED_ASSURANCE_IDS = {
    "AP-001", "AP-002", "RP-002", "DD-001", "RA-001", "EI-001", "EI-012",
    "EI-002", "EI-003", "FP-009", "GL-001", "ADR-001", "ADR-002",
    "ADR-003", "ADR-004", "ADR-005", "ADR-009", "ADR-010", "ADR-011",
    "ADR-012", "ADR-013", "ADR-014", "ADR-016",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_rp002_defines_assurance_role_and_boundaries() -> None:
    text = _read(RP002)

    assert "# RP-002" in text
    assert "**Status:** Accepted" in text
    assert "Documentation-only role profile" in text
    assert "does not change runtime behaviour" in text
    for phrase in [
        "Purpose",
        "Role responsibilities",
        "Assurance profile membership",
        "Documents never included",
        "Dependencies",
        "Acceptance criteria for a compiled Assurance profile",
    ]:
        assert phrase in text


def test_registry_registers_rp002_and_assurance_pack_membership() -> None:
    documents = parse_authority_registry(_read(REGISTRY))
    by_id = {document.document_id: document for document in documents}

    assert {"AP-001", "AP-002", "RP-002"}.issubset(by_id)
    for document_id in ["AP-001", "AP-002", "RP-002"]:
        document = by_id[document_id]
        assert document.status == "Accepted"
        assert document.is_authoritative
        assert "assurance-pack" in document.release_profile_membership


def test_assurance_pack_compiles_non_empty_and_traceable_to_registry() -> None:
    registry_ids = {document.document_id for document in parse_authority_registry(_read(REGISTRY))}
    compilation = compile_architecture_profile("assurance-pack", ROOT)
    included_ids = {document.document_id for document in compilation.included_documents}

    assert included_ids == EXPECTED_ASSURANCE_IDS
    assert included_ids.issubset(registry_ids)
    assert compilation.dependencies
    assert compilation.non_promotion_statement
    for document in compilation.included_documents:
        assert document.status == "Accepted"
        assert document.is_authoritative
        assert "assurance-pack" in document.release_profile_membership


def test_assurance_pack_excludes_researcher_profile_and_review_material() -> None:
    compilation = compile_architecture_profile("assurance-pack", ROOT)
    included_ids = {document.document_id for document in compilation.included_documents}
    excluded_ids = {document.document_id for document in compilation.excluded_documents}

    assert "RP-001" not in included_ids
    assert "EU-001" not in included_ids
    assert "ADR-023" not in included_ids
    assert {"RP-001", "EU-001", "ADR-023"}.issubset(excluded_ids)


def test_assurance_runtime_package_matches_rp001_runtime_model() -> None:
    package = compile_assurance_runtime_package(ROOT)

    assert package.upload_file_count == 17
    assert package.validate_zip()
    standalone_names = {file.name for file in package.upload_files if not file.generated}
    assert "RP-002-Enterprise-Intelligence-Assurance-Profile.md" in standalone_names
    assert "RP-001-Enterprise-Blueprint-Researcher-Profile.md" not in standalone_names
    generated_names = {file.name for file in package.upload_files if file.generated}
    assert generated_names == {
        "Assurance-ADR-Foundation-Pack.md",
        "Assurance-ADR-Governance-Pack.md",
        "Assurance-ADR-Evidence-Acquisition-Pack.md",
        "Assurance-ADR-Financial-Intelligence-Pack.md",
        "Assurance-ADR-Blueprint-and-Canvas-Pack.md",
        "Assurance-ADR-Reasoning-and-Exchange-Pack.md",
    }


def test_document_map_points_to_rp002() -> None:
    text = _read(DOCUMENT_MAP)

    assert "RP-002" in text
    assert "profiles/RP-002-Enterprise-Intelligence-Assurance-Profile.md" in text
