"""Tests for Sprint 7D passive memory record models."""

from __future__ import annotations

import ast
import importlib
from pathlib import Path
from typing import Any

from cios.core import Evidence
from cios.graph import GraphNode, KnowledgeGraphRecord
from cios.memory import (
    MEMORY_SCHEMA_VERSION,
    AssessmentMemoryRecord,
    DecisionMemoryRecord,
    EvidenceMemoryRecord,
    MemoryRecord,
    OutcomeMemoryRecord,
)


def test_memory_records_instantiate_correctly() -> None:
    """All memory record variants instantiate as thin passive data models."""

    evidence = Evidence(title="Customer note", source="crm")
    node = GraphNode(wrapped_id="entity_123", wrapped_type="Entity", source_package="core")
    graph_record = KnowledgeGraphRecord(name="Remembered graph", nodes=[node])

    base = MemoryRecord(record_type="generic", subject_id="subject_123")
    evidence_record = EvidenceMemoryRecord(subject_id=evidence.id, evidence_ids=[evidence.id], evidence=[evidence])
    assessment_record = AssessmentMemoryRecord(assessment_id="assessment_123", graph_record_ids=[graph_record.id], graph_records=[graph_record])
    decision_record = DecisionMemoryRecord(decision_id="decision_output_123", decision_payload={"title": "Approve"})
    outcome_record = OutcomeMemoryRecord(outcome="Win rate improved", decision_id=decision_record.decision_id)

    assert base.schema_version == MEMORY_SCHEMA_VERSION
    assert evidence_record.record_type == "evidence"
    assert assessment_record.graph_records == [graph_record]
    assert decision_record.decision_payload == {"title": "Approve"}
    assert outcome_record.decision_id == "decision_output_123"


def test_memory_records_serialize_to_json_compatible_dicts() -> None:
    """Memory records serialize nested core and graph models with JSON-compatible values."""

    evidence = Evidence(title="Board minutes", source="document")
    node = GraphNode(wrapped_id=evidence.id, wrapped_type="Evidence", source_package="core")
    record = EvidenceMemoryRecord(
        subject_id=evidence.id,
        evidence_ids=[evidence.id],
        graph_record_ids=["knowledge_graph_record_123"],
        evidence=[evidence],
        payload={"tags": ["transformation"], "confidence": 0.9},
    )
    assessment = AssessmentMemoryRecord(graph_records=[KnowledgeGraphRecord(name="Evidence graph", nodes=[node])])

    serialized = record.model_dump(mode="json")
    assessment_serialized = assessment.model_dump(mode="json")

    assert serialized["schema_version"] == MEMORY_SCHEMA_VERSION
    assert serialized["created_at"].endswith("Z") or "+00:00" in serialized["created_at"]
    assert serialized["evidence"][0]["id"] == evidence.id
    assert serialized["payload"] == {"tags": ["transformation"], "confidence": 0.9}
    assert assessment_serialized["graph_records"][0]["nodes"][0]["wrapped_id"] == evidence.id


def test_memory_does_not_import_forbidden_modules() -> None:
    """Memory models import only permitted CIOS dependencies and no active modules."""

    module = importlib.import_module("cios.memory.models")
    source = Path(module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden_roots = {
        "cios.reasoning",
        "cios.scoring",
        "cios.decision_engine",
        "cios.agents",
        "cios.applications",
    }
    forbidden_external_names = {"openai", "anthropic", "sqlalchemy", "psycopg", "requests", "httpx"}
    imported_modules: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)

    assert not any(imported == root or imported.startswith(f"{root}.") for imported in imported_modules for root in forbidden_roots)
    assert not any(imported.split(".")[0] in forbidden_external_names for imported in imported_modules)


def test_decision_outputs_can_be_referenced_without_importing_decision_engine() -> None:
    """Decision memory stores IDs and payloads without requiring decision_engine models."""

    decision_payload: dict[str, Any] = {
        "id": "decision_output_abc",
        "title": "Opportunity qualification decision",
        "status": "approved",
        "metadata": {"source": "unit-test"},
    }

    record = DecisionMemoryRecord(
        decision_id=decision_payload["id"],
        subject_id="opportunity_123",
        related_ids=["recommendation_123"],
        decision_payload=decision_payload,
    )
    serialized = record.model_dump(mode="json")

    assert serialized["decision_id"] == "decision_output_abc"
    assert serialized["decision_payload"]["title"] == "Opportunity qualification decision"
    assert "cios.decision_engine" not in importlib.import_module("cios.memory.models").__dict__
