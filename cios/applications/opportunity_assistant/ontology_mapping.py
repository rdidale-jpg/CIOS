"""Ontology mapping for the Opportunity Assistant."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from cios.core.models import CIOSBaseModel
from cios.ontology import Capability, Competitor, Contract, Customer, Opportunity


class OpportunityOntologyResult(CIOSBaseModel):
    """Typed ontology artefacts created by the opportunity assistant."""

    customer: Customer
    opportunity: Opportunity
    contract: Contract
    capabilities: list[Capability] = Field(default_factory=list)
    competitors: list[Competitor] = Field(default_factory=list)


def create_ontology(source: dict[str, Any]) -> OpportunityOntologyResult:
    """Map structured opportunity source data into ontology records."""

    customer = Customer(
        name=source["customer"]["name"],
        sector=source["customer"].get("sector"),
        region=source["customer"].get("region"),
    )
    capabilities = [Capability(name=name) for name in source.get("capabilities", [])]
    competitors = [Competitor(name=name) for name in source.get("competitors", [])]
    contract = Contract(name=f"{source['name']} Contract", customer_id=customer.id, value=source.get("value"))
    opportunity = Opportunity(
        name=source["name"],
        description=source.get("description"),
        customer_id=customer.id,
        capability_ids=[capability.id for capability in capabilities],
        competitor_ids=[competitor.id for competitor in competitors],
        contract_id=contract.id,
        value=source.get("value"),
        metadata={"duration_months": source.get("duration_months")},
    )
    return OpportunityOntologyResult(customer=customer, opportunity=opportunity, contract=contract, capabilities=capabilities, competitors=competitors)
