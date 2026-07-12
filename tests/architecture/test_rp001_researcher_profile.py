from __future__ import annotations

from pathlib import Path

from cios.architecture import compile_architecture_profile, parse_authority_registry

ROOT = Path(__file__).resolve().parents[2]
RP001 = ROOT / "architecture/reference-architecture/profiles/RP-001-Enterprise-Blueprint-Researcher-Profile.md"
REGISTRY = ROOT / "architecture/reference-architecture/Architecture-Authority-Registry.md"
DOCUMENT_MAP = ROOT / "architecture/reference-architecture/Document-Map.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_rp001_defines_researcher_role_and_boundaries() -> None:
    text = _read(RP001)

    assert "# RP-001" in text
    assert "**Status:** Accepted" in text
    assert "Documentation-only role profile" in text
    assert "does not change runtime behaviour" in text
    for phrase in [
        "Purpose",
        "Role responsibilities",
        "Researcher profile membership",
        "Documents never included",
        "Dependencies",
        "Acceptance criteria for a compiled Researcher profile",
    ]:
        assert phrase in text


def test_registry_registers_rp001_and_researcher_pack_membership() -> None:
    documents = parse_authority_registry(_read(REGISTRY))
    by_id = {document.document_id: document for document in documents}

    assert {"AP-001", "AP-002", "RP-001"}.issubset(by_id)
    for document_id in ["AP-001", "AP-002", "RP-001"]:
        document = by_id[document_id]
        assert document.status == "Accepted"
        assert document.is_authoritative
        assert "researcher-pack" in document.release_profile_membership


def test_researcher_pack_compiles_non_empty_and_traceable_to_registry() -> None:
    registry_ids = {document.document_id for document in parse_authority_registry(_read(REGISTRY))}
    compilation = compile_architecture_profile("researcher-pack", ROOT)
    included_ids = {document.document_id for document in compilation.included_documents}

    assert included_ids == {"AP-001", "AP-002", "RP-001"}
    assert included_ids.issubset(registry_ids)
    assert compilation.dependencies
    assert compilation.non_promotion_statement
    for document in compilation.included_documents:
        assert document.status == "Accepted"
        assert document.is_authoritative
        assert "researcher-pack" in document.release_profile_membership


def test_researcher_pack_excludes_review_material_and_none_membership() -> None:
    compilation = compile_architecture_profile("researcher-pack", ROOT)
    included_ids = {document.document_id for document in compilation.included_documents}
    excluded_ids = {document.document_id for document in compilation.excluded_documents}

    assert "EU-001" not in included_ids
    assert "ADR-023" not in included_ids
    assert {"EU-001", "ADR-023"}.issubset(excluded_ids)


def test_document_map_points_to_rp001() -> None:
    text = _read(DOCUMENT_MAP)

    assert "RP-001" in text
    assert "profiles/RP-001-Enterprise-Blueprint-Researcher-Profile.md" in text
