"""Commercial ontology models for the CIOS SDK.

Sprint 2 establishes ontology-level domain concepts as thin, serializable
Pydantic models. These models may reference foundational ``cios.core`` entity
identifiers, but they do not implement graph, scoring, decision engine, agent,
memory, UI, or application behaviour.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field, field_validator

from cios.core.identifiers import generate_identifier
from cios.core.models import CIOSBaseModel
from cios.core.validation import require_non_empty, utc_now


class OntologyBaseModel(CIOSBaseModel):
    """Base model for Sprint 2 commercial ontology concepts."""

    id: str
    name: str = Field(..., description="Human-readable ontology concept name.")
    description: str | None = Field(default=None, description="Optional concept description.")
    entity_id: str | None = Field(default=None, description="Optional linked core Entity identifier.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional serializable attributes.")
    created_at: datetime = Field(default_factory=utc_now, description="Timezone-aware creation timestamp.")

    @field_validator("name")
    @classmethod
    def _validate_name(cls, value: str) -> str:
        return require_non_empty(value, "name")

    @field_validator("entity_id")
    @classmethod
    def _validate_entity_id(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return require_non_empty(value, "entity_id")


class CommercialObject(OntologyBaseModel):
    """Base commercial object represented in the ontology layer."""

    id: str = Field(default_factory=lambda: generate_identifier("commercial_object"))
    object_type: str = Field(default="commercial_object", description="Commercial object category.")

    @field_validator("object_type")
    @classmethod
    def _validate_object_type(cls, value: str) -> str:
        return require_non_empty(value, "object_type")


class Customer(CommercialObject):
    """Buying organisation or accountable customer entity."""

    id: str = Field(default_factory=lambda: generate_identifier("customer"))
    object_type: str = "customer"
    sector: str | None = None
    region: str | None = None


class Competitor(CommercialObject):
    """Competing organisation in a commercial context."""

    id: str = Field(default_factory=lambda: generate_identifier("competitor"))
    object_type: str = "competitor"
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)


class Supplier(CommercialObject):
    """Supplier, partner, or subcontractor entity."""

    id: str = Field(default_factory=lambda: generate_identifier("supplier"))
    object_type: str = "supplier"
    capabilities: list[str] = Field(default_factory=list, description="Capability identifiers or names supplied.")


class Market(CommercialObject):
    """Market or segment in which commercial activity occurs."""

    id: str = Field(default_factory=lambda: generate_identifier("market"))
    object_type: str = "market"
    region: str | None = None
    segments: list[str] = Field(default_factory=list)


class Capability(CommercialObject):
    """Reusable organisational or supplier capability in the ontology."""

    id: str = Field(default_factory=lambda: generate_identifier("capability"))
    object_type: str = "capability"
    evidence_ids: list[str] = Field(default_factory=list)


class Contract(CommercialObject):
    """Commercial contract or vehicle relevant to an opportunity."""

    id: str = Field(default_factory=lambda: generate_identifier("contract"))
    object_type: str = "contract"
    customer_id: str | None = Field(default=None, description="Optional Customer or Entity identifier.")
    value: float | None = Field(default=None, ge=0, description="Optional non-negative contract value.")

    @field_validator("customer_id")
    @classmethod
    def _validate_customer_id(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return require_non_empty(value, "customer_id")


class Opportunity(CommercialObject):
    """Commercial opportunity represented as an ontology-level concept."""

    id: str = Field(default_factory=lambda: generate_identifier("opportunity"))
    object_type: str = "opportunity"
    customer_id: str | None = Field(default=None, description="Optional Customer or Entity identifier.")
    capability_ids: list[str] = Field(default_factory=list)
    competitor_ids: list[str] = Field(default_factory=list)
    supplier_ids: list[str] = Field(default_factory=list)
    market_id: str | None = None
    contract_id: str | None = None
    value: float | None = Field(default=None, ge=0, description="Optional non-negative opportunity value.")

    @field_validator("customer_id", "market_id", "contract_id")
    @classmethod
    def _validate_optional_identifier(cls, value: str | None, info: Any) -> str | None:
        if value is None:
            return value
        return require_non_empty(value, info.field_name)
