from __future__ import annotations

from pathlib import Path

import pytest

from cios.architecture import compile_architecture_profile, parse_authority_registry

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "architecture/reference-architecture/Architecture-Authority-Registry.md"


def test_compiler_parses_registry_rows() -> None:
    documents = parse_authority_registry(REGISTRY.read_text(encoding="utf-8"))

    ids = {document.document_id for document in documents}
    assert {"AP-001", "AP-002", "EU-001", "ADR-023"}.issubset(ids)


def test_architecture_authority_profile_includes_only_accepted_authority() -> None:
    compilation = compile_architecture_profile("architecture-authority", ROOT)

    included_ids = {document.document_id for document in compilation.included_documents}
    excluded_ids = {document.document_id for document in compilation.excluded_documents}
    assert included_ids == {"AP-001", "AP-002"}
    assert {"EU-001", "ADR-023"}.issubset(excluded_ids)
    assert compilation.source_registry_path == "architecture/reference-architecture/Architecture-Authority-Registry.md"
    assert compilation.non_promotion_statement


def test_review_context_preserves_review_and_proposed_statuses() -> None:
    compilation = compile_architecture_profile("review-context", ROOT)

    status_by_id = {document.document_id: document.status for document in compilation.included_documents}
    assert status_by_id == {"EU-001": "Review", "ADR-023": "Proposed"}


def test_production_agent_profiles_do_not_infer_membership() -> None:
    assert compile_architecture_profile("researcher-pack", ROOT).included_documents == ()
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
