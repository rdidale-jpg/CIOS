"""Tests for CIOS Sprint 2 ontology Pydantic models."""

from __future__ import annotations

import importlib

from cios.core import Entity
from cios.ontology import Capability, CommercialObject, Competitor, Contract, Customer, Market, Opportunity, Supplier


def test_ontology_models_construct_with_sample_data() -> None:
    """Every Sprint 2 ontology model can be instantiated."""

    customer = Customer(name="Acme Corp", sector="Public Sector", region="UK")
    competitor = Competitor(name="Rival Ltd", strengths=["incumbency"])
    supplier = Supplier(name="Partner Co", capabilities=["implementation"])
    market = Market(name="Resilience Services", segments=["advisory"])
    capability = Capability(name="Resilience advisory", evidence_ids=["evidence_123"])
    contract = Contract(name="Digital Framework", customer_id=customer.id, value=500000)
    opportunity = Opportunity(
        name="Resilience Modernisation",
        customer_id=customer.id,
        capability_ids=[capability.id],
        competitor_ids=[competitor.id],
        supplier_ids=[supplier.id],
        market_id=market.id,
        contract_id=contract.id,
        value=1000000,
    )
    commercial_object = CommercialObject(name="Generic commercial object")

    assert customer.id.startswith("customer_")
    assert competitor.object_type == "competitor"
    assert supplier.capabilities == ["implementation"]
    assert market.segments == ["advisory"]
    assert contract.customer_id == customer.id
    assert opportunity.capability_ids == [capability.id]
    assert commercial_object.object_type == "commercial_object"


def test_ontology_models_can_reference_core_entity_identifiers() -> None:
    """Ontology concepts can link to foundational core Entity IDs."""

    entity = Entity(name="Acme Corp", entity_type="organisation")
    customer = Customer(name="Acme Corp", entity_id=entity.id)
    opportunity = Opportunity(name="Resilience Modernisation", customer_id=entity.id)

    assert customer.entity_id == entity.id
    assert opportunity.customer_id == entity.id


def test_ontology_models_serialize_to_dictionaries() -> None:
    """Ontology models remain Pydantic-serializable without services."""

    customer = Customer(name="Acme Corp", metadata={"tier": "strategic"})

    serialized = customer.model_dump(mode="json")

    assert serialized["id"] == customer.id
    assert serialized["object_type"] == "customer"
    assert serialized["metadata"] == {"tier": "strategic"}
    assert "created_at" in serialized


def test_no_circular_imports_between_core_and_ontology() -> None:
    """Core and ontology modules import independently without circular failures."""

    core_models = importlib.import_module("cios.core.models")
    ontology_models = importlib.import_module("cios.ontology.models")

    assert core_models.Entity(name="Core Entity", entity_type="organisation")
    assert ontology_models.Customer(name="Ontology Customer")
