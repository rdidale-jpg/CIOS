"""Application service that turns accepted Evidence into maintained Enterprise Model memory."""
from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Any

from cios.applications.flora.memory.models import EnterpriseModelAttribute, EnterpriseUnknown, ModelUpdateResult, Observation, now_iso
from cios.applications.flora.memory.repository import EnterpriseModelRepository, ObservationRepository

DOMAIN_MAP = {
    "AI Modernisation": "technology_events",
    "AI Readiness": "technology_events",
    "Technology Debt": "technology_events",
    "Procurement Readiness": "procurement_events",
    "Cost Pressure": "financial_pressure",
    "Investment Pressure": "financial_pressure",
    "Spending Pressure": "financial_pressure",
    "Operational Resilience": "transformation_programmes",
    "Network Resilience": "transformation_programmes",
    "Digital Leadership": "transformation_programmes",
    "Regulatory Pressure": "transformation_programmes",
}

CONFLICT_TERMS = ("cancelled", "paused", "delayed", "ended", "withdrawn", "terminated", "no longer")
UNKNOWN_MARKERS = ("unknown", "insufficient", "unclear", "unconfirmed")


def _domain_for(condition: str) -> str:
    return DOMAIN_MAP.get(condition or "", "enterprise_identity")


def _evidence_id(item: dict[str, Any]) -> str:
    return str(item.get("evidence_id") or item.get("id") or item.get("evidence_fingerprint") or hashlib.sha256(str(item).encode()).hexdigest()[:16])


class ObservationMemoryService:
    def __init__(self, observations: ObservationRepository | None = None, models: EnterpriseModelRepository | None = None):
        self.observations = observations or ObservationRepository()
        self.models = models or EnterpriseModelRepository()

    def observation_from_evidence(self, item: dict[str, Any]) -> Observation:
        statement = str(item.get("cleaned_observation") or item.get("extracted_observation") or item.get("snippet") or "").strip()
        condition = str(item.get("commercial_condition") or item.get("mapped_condition") or "enterprise identity")
        collected = str(item.get("extraction_timestamp") or item.get("collection_date") or now_iso())
        observed = str(item.get("observation_date") or collected[:10])
        publication = item.get("publication_date") or item.get("evidence_publication_date")
        return Observation(
            enterprise_id=str(item.get("organisation") or item.get("enterprise_id") or "Unknown enterprise"),
            observation_type=condition,
            atomic_statement=statement,
            observation_date=observed,
            evidence_publication_date=str(publication) if publication else None,
            collection_date=collected,
            supporting_evidence_ids=(_evidence_id(item),),
            provenance_type="evidence-backed",
            confidence=int(item.get("confidence") or item.get("overall_evidence_quality") or 50),
            freshness=str(item.get("evidence_freshness") or "current"),
            affected_attribute=f"{_domain_for(condition)}.{condition}",
            importance=int(item["importance"]) if item.get("importance") is not None else None,
            commercial_value=int(item["commercial_value"]) if item.get("commercial_value") is not None else None,
        )

    def accept_evidence(self, item: dict[str, Any]) -> ModelUpdateResult:
        observation = self.observations.save(self.observation_from_evidence(item))
        return self.apply_observation(observation)

    def apply_observation(self, observation: Observation) -> ModelUpdateResult:
        if observation.lifecycle_state != "accepted":
            return ModelUpdateResult(observation.enterprise_id, observation.observation_id or "", observation.affected_attribute, "ignored")
        model = self.models.get(observation.enterprise_id)
        key = observation.affected_attribute
        domain = key.split(".", 1)[0]
        lower = observation.atomic_statement.casefold()
        if any(marker in lower for marker in UNKNOWN_MARKERS):
            unknown_id = f"UNK-{hashlib.sha256((observation.enterprise_id + key).encode()).hexdigest()[:12].upper()}"
            existing = model.unknowns.get(unknown_id)
            related = tuple(dict.fromkeys([*(existing.related_observation_ids if existing else ()), observation.observation_id or ""]))
            model.unknowns[unknown_id] = EnterpriseUnknown(unknown_id, observation.enterprise_id, f"Unknown model state for {key}", domain, "medium", ("accepted corroborating evidence",), "open", related)
            model.updated_at = now_iso(); self.models.save(model)
            return ModelUpdateResult(observation.enterprise_id, observation.observation_id or "", key, "unknown_created", unknown_created=True)

        existing = model.attributes.get(key)
        contradiction = bool(existing and existing.current_value and existing.current_value != observation.atomic_statement and any(t in lower or t in existing.current_value.casefold() for t in CONFLICT_TERMS))
        if existing:
            prior = tuple(existing.prior_values)
            if existing.current_value != observation.atomic_statement and not contradiction:
                prior = (*prior, {"value": existing.current_value, "confidence": existing.confidence, "superseded_at": now_iso(), "observation_ids": existing.observation_ids})
            observation_ids = tuple(dict.fromkeys([*existing.observation_ids, observation.observation_id or ""]))
            evidence_ids = tuple(dict.fromkeys([*existing.evidence_ids, *observation.supporting_evidence_ids]))
            value = existing.current_value if contradiction else observation.atomic_statement
            conflicts = tuple(dict.fromkeys([*existing.conflicting_observation_ids, observation.observation_id or ""])) if contradiction else existing.conflicting_observation_ids
            state = "contradicted" if contradiction else observation.contradiction_state
        else:
            prior = ()
            observation_ids = (observation.observation_id or "",)
            evidence_ids = observation.supporting_evidence_ids
            value = observation.atomic_statement
            conflicts = ()
            state = observation.contradiction_state
        model.attributes[key] = EnterpriseModelAttribute(domain, key, value, max(observation.confidence, existing.confidence if existing else 0), observation.last_confirmed_date or observation.observation_date, observation.freshness, observation_ids, evidence_ids, observation.provenance_type, state, conflicts, prior)
        model.updated_at = now_iso()
        self.models.save(model)
        return ModelUpdateResult(observation.enterprise_id, observation.observation_id or "", key, "contradiction_recorded" if contradiction else ("updated" if existing else "created"), contradiction=contradiction)

    def rebuild_from_ledger(self) -> list[ModelUpdateResult]:
        results = []
        for obs in self.observations.list():
            results.append(self.apply_observation(obs))
        return results
