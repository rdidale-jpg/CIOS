"""Tests for CIOS Sprint 1 core Pydantic models."""

from __future__ import annotations

from pydantic import ValidationError

from cios.core import (
    Capability,
    ConfidenceLevel,
    Decision,
    Entity,
    Evidence,
    EvidenceKind,
    Observation,
    Opportunity,
    Recommendation,
    Relationship,
    generate_identifier,
)


def test_core_models_construct_with_sample_data() -> None:
    """Every Sprint 1 foundational model can be instantiated."""

    entity = Entity(name="Acme Corp", entity_type="organisation")
    related = Entity(name="Programme Alpha", entity_type="programme")
    relationship = Relationship(
        source_entity_id=entity.id,
        target_entity_id=related.id,
        relationship_type="sponsors",
    )
    evidence = Evidence(
        title="Customer strategy note",
        kind=EvidenceKind.DOCUMENT,
        source="strategy-note.md",
        confidence=ConfidenceLevel.HIGH,
    )
    observation = Observation(statement="Customer is prioritising resilience.", evidence_ids=[evidence.id])
    recommendation = Recommendation(
        title="Lead with resilience theme",
        rationale="Evidence indicates resilience is a priority.",
        actions=["Prepare resilience proof points"],
        evidence_ids=[evidence.id],
    )
    decision = Decision(
        title="Pursue opportunity",
        rationale="The opportunity aligns to existing strengths.",
        recommendation_ids=[recommendation.id],
        evidence_ids=[evidence.id],
    )
    opportunity = Opportunity(name="Resilience Modernisation", customer="Acme Corp", value=1000000)
    capability = Capability(name="Resilience advisory", evidence_ids=[evidence.id])

    assert entity.id.startswith("entity_")
    assert relationship.source_entity_id == entity.id
    assert observation.evidence_ids == [evidence.id]
    assert decision.recommendation_ids == [recommendation.id]
    assert opportunity.value == 1000000
    assert capability.name == "Resilience advisory"


def test_models_serialize_to_dictionaries() -> None:
    """Core models remain Pydantic-serializable without custom services."""

    evidence = Evidence(title="Interview notes", source="interview.md")

    serialized = evidence.model_dump(mode="json")

    assert serialized["id"] == evidence.id
    assert serialized["kind"] == "note"
    assert serialized["confidence"] == "medium"
    assert "created_at" in serialized


def test_required_field_validation_failure() -> None:
    """Blank required text fields are rejected."""

    try:
        Entity(name="  ", entity_type="organisation")
    except ValidationError as exc:
        assert "name must not be empty" in str(exc)
    else:  # pragma: no cover - makes the expected validation explicit
        raise AssertionError("Expected Entity validation to fail for a blank name")


def test_opportunity_value_must_be_non_negative() -> None:
    """Numeric validation rejects invalid opportunity values."""

    try:
        Opportunity(name="Invalid", customer="Acme Corp", value=-1)
    except ValidationError as exc:
        assert "greater than or equal to 0" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected Opportunity validation to fail for a negative value")


def test_identifier_generation_is_unique() -> None:
    """Identifier helper returns unique prefixed identifiers."""

    identifiers = {generate_identifier("test") for _ in range(100)}

    assert len(identifiers) == 100
    assert all(identifier.startswith("test_") for identifier in identifiers)
