"""Tests for Sprint 7E passive memory repositories."""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

from cios.memory import (
    DecisionMemoryRecord,
    EvidenceMemoryRecord,
    InMemoryRepository,
    MemoryRecord,
    MemoryRepository,
)


def test_in_memory_repository_saves_and_retrieves_records() -> None:
    """Records saved into the repository can be retrieved by ID."""

    repository: MemoryRepository = InMemoryRepository()
    record = MemoryRecord(record_type="generic", subject_id="subject_123")

    saved = repository.save(record)

    assert saved == record
    assert repository.get(record.id) == record


def test_in_memory_repository_lists_records() -> None:
    """The repository lists all stored records in insertion order."""

    repository = InMemoryRepository()
    first = MemoryRecord(record_type="generic")
    second = EvidenceMemoryRecord(subject_id="evidence_123", evidence_ids=["evidence_123"])

    repository.save(first)
    repository.save(second)

    assert repository.list() == [first, second]


def test_in_memory_repository_filters_by_record_type() -> None:
    """The repository can find records with a matching record type."""

    repository = InMemoryRepository()
    evidence_record = EvidenceMemoryRecord(subject_id="evidence_123", evidence_ids=["evidence_123"])
    decision_record = DecisionMemoryRecord(decision_id="decision_123")

    repository.save(evidence_record)
    repository.save(decision_record)

    assert repository.find_by_record_type("evidence") == [evidence_record]
    assert repository.find_by_record_type("decision") == [decision_record]
    assert repository.find_by_record_type("outcome") == []


def test_in_memory_repository_unknown_ids_return_none() -> None:
    """Unknown IDs produce a safe empty result instead of raising."""

    repository = InMemoryRepository()

    assert repository.get("missing_memory_record") is None


def test_memory_repository_does_not_import_forbidden_modules() -> None:
    """Memory repositories do not import active modules or persistence frameworks."""

    module = importlib.import_module("cios.memory.repository")
    source = Path(module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden_roots = {
        "cios.reasoning",
        "cios.scoring",
        "cios.decision_engine",
        "cios.agents",
        "cios.applications",
    }
    forbidden_external_names = {
        "openai",
        "anthropic",
        "sqlalchemy",
        "psycopg",
        "requests",
        "httpx",
        "sqlite3",
        "pymongo",
    }
    imported_modules: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)

    assert not any(
        imported == root or imported.startswith(f"{root}.")
        for imported in imported_modules
        for root in forbidden_roots
    )
    assert not any(imported.split(".")[0] in forbidden_external_names for imported in imported_modules)
