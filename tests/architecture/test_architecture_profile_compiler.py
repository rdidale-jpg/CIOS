from __future__ import annotations

from pathlib import Path

import pytest

from cios.architecture import compile_architecture_profile, parse_authority_registry

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "architecture/reference-architecture/Architecture-Authority-Registry.md"


def test_compiler_parses_registry_rows() -> None:
    documents = parse_authority_registry(REGISTRY.read_text(encoding="utf-8"))

    ids = {document.document_id for document in documents}
    assert {"AP-001", "AP-002", "RP-001", "RP-002", "EIF-001", "EOD-001", "EU-001", "OT-001", "EI-014", "EI-015", "OPI-001", "RTP-001", "ADR-023", "VAL-ROADMAP-001"}.issubset(ids)


def test_architecture_authority_profile_includes_only_accepted_authority() -> None:
    compilation = compile_architecture_profile("architecture-authority", ROOT)

    included_ids = {document.document_id for document in compilation.included_documents}
    excluded_ids = {document.document_id for document in compilation.excluded_documents}
    assert included_ids == {
        "AP-001", "AP-002", "RP-001", "RP-002", "DD-001", "RA-001", "EI-001", "EI-012",
        "EI-002", "EI-003", "FP-009", "GL-001", "ADR-001", "ADR-002",
        "ADR-003", "ADR-004", "ADR-005", "ADR-009", "ADR-010", "ADR-011",
        "ADR-012", "ADR-013", "ADR-014", "ADR-016",
    }
    assert {"EIF-001", "EOD-001", "EU-001", "OT-001", "EI-014", "EI-015", "OPI-001", "RTP-001", "ADR-023", "VAL-ROADMAP-001"}.issubset(excluded_ids)
    assert compilation.source_registry_path == "architecture/reference-architecture/Architecture-Authority-Registry.md"
    assert compilation.non_promotion_statement


def test_review_context_preserves_review_and_proposed_statuses() -> None:
    compilation = compile_architecture_profile("review-context", ROOT)

    status_by_id = {document.document_id: document.status for document in compilation.included_documents}
    assert status_by_id == {"EIF-001": "Review", "EOD-001": "Review", "EU-001": "Review", "OT-001": "Review", "EI-014": "Review", "EI-015": "Review", "OPI-001": "Review", "RTP-001": "Review", "ADR-023": "Proposed", "VAL-ROADMAP-001": "Review", "IC-001": "Review"}


def test_production_agent_profiles_do_not_infer_membership() -> None:
    researcher_ids = {document.document_id for document in compile_architecture_profile("researcher-pack", ROOT).included_documents}
    assert researcher_ids == {
        "AP-001", "AP-002", "RP-001", "DD-001", "RA-001", "EI-001", "EI-012",
        "EI-002", "EI-003", "FP-009", "GL-001", "ADR-001", "ADR-002",
        "ADR-003", "ADR-004", "ADR-005", "ADR-009", "ADR-010", "ADR-011",
        "ADR-012", "ADR-013", "ADR-014", "ADR-016",
    }
    assert compile_architecture_profile("reviewer-pack", ROOT).included_documents == ()


def test_compilation_record_contains_required_metadata() -> None:
    record = compile_architecture_profile("architecture-authority", ROOT).to_dict()

    for key in [
        "compilation_profile",
        "source_registry_path",
        "registry_last_updated",
        "included_documents",
        "excluded_documents",
        "dependencies",
        "outstanding_validation_triggers",
        "non_promotion_statement",
        "architecture_version",
        "registry_version",
        "compiler_version",
        "compilation_timestamp",
    ]:
        assert key in record


def test_unknown_profile_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported architecture profile"):
        compile_architecture_profile("production", ROOT)


def test_researcher_runtime_package_compiles_to_exactly_17_upload_files() -> None:
    from cios.architecture import compile_researcher_runtime_package

    package = compile_researcher_runtime_package(ROOT)

    assert package.upload_file_count == 17
    standalone_names = {file.name for file in package.upload_files if not file.generated}
    assert standalone_names == {
        "AP-001-Architecture-Compilation-Standard.md",
        "AP-002-Architecture-Metadata-Standard.md",
        "RP-001-Enterprise-Blueprint-Researcher-Profile.md",
        "CIOS-Design-Doctrine.md",
        "CIOS-Reference-Architecture-v1.0.md",
        "EI-001-Enterprise-Model-Specification.md",
        "EI-012-Enterprise-Observation-Model.md",
        "EI-002-Enterprise-Knowledge-Graph.md",
        "EI-003-Enterprise-Behaviour-Model.md",
        "FP-009-Hypothesis-Validation-Standard.md",
        "Glossary.md",
    }
    generated_names = {file.name for file in package.upload_files if file.generated}
    assert generated_names == {
        "ADR-Foundation-Pack.md",
        "ADR-Governance-Pack.md",
        "ADR-Evidence-Acquisition-Pack.md",
        "ADR-Financial-Intelligence-Pack.md",
        "ADR-Blueprint-and-Canvas-Pack.md",
        "ADR-Reasoning-and-Exchange-Pack.md",
    }


def test_generated_adr_runtime_packs_preserve_traceability_and_content() -> None:
    from cios.architecture import compile_researcher_runtime_package

    package = compile_researcher_runtime_package(ROOT)
    packs = {file.name: file for file in package.upload_files if file.generated}

    expected = {
        "ADR-Foundation-Pack.md": ["ADR-001", "ADR-002", "ADR-003"],
        "ADR-Governance-Pack.md": ["ADR-004", "ADR-005", "ADR-009"],
        "ADR-Evidence-Acquisition-Pack.md": ["ADR-010"],
        "ADR-Financial-Intelligence-Pack.md": ["ADR-011"],
        "ADR-Blueprint-and-Canvas-Pack.md": ["ADR-012", "ADR-013"],
        "ADR-Reasoning-and-Exchange-Pack.md": ["ADR-014", "ADR-016"],
    }
    by_id = {document.document_id: document for document in package.source_profile.included_documents}
    for pack_name, adr_ids in expected.items():
        pack = packs[pack_name]
        assert "Generated Researcher GPT runtime artefact" in pack.content
        assert "Not canonical architecture" in pack.content
        for adr_id in adr_ids:
            document = by_id[adr_id]
            source_text = (ROOT / document.path).read_text(encoding="utf-8").rstrip()
            assert f"**Original ADR ID:** {adr_id}" in pack.content
            assert f"**Original title:** {document.title}" in pack.content
            assert f"**Original status:** {document.status}" in pack.content
            assert f"`{document.path}`" in pack.content
            assert source_text in pack.content


def test_researcher_runtime_zip_is_valid_and_deterministic() -> None:
    from cios.architecture import compile_researcher_runtime_package

    first = compile_researcher_runtime_package(ROOT)
    second = compile_researcher_runtime_package(ROOT)

    assert first.validate_zip()
    assert first.to_zip_bytes() == second.to_zip_bytes()
