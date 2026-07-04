"""Calibration-only import path for governed golden facts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from cios.applications.flora.memory.service import FactualClaim, ObservationMemoryService, validate_factual_claim

DEFAULT_GOLDEN_FACTS = Path("docs/Architecture/experiments/BT_Foundation_Golden_Facts.yaml")

def load_golden_facts(path: Path = DEFAULT_GOLDEN_FACTS) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("facts", []))

def claim_from_fact(fact: dict[str, Any]) -> FactualClaim:
    return FactualClaim(
        str(fact["canonical_enterprise_id"]), str(fact["claim_type"]), str(fact["atomic_statement"]), str(fact["domain"]), str(fact["affected_attribute"]),
        fact.get("structured_value"), fact.get("unit") or None, fact.get("currency") or None, fact.get("period") or None, str(fact.get("state") or "actual"),
        str(fact["fact_id"]), str(fact["page"]), int(fact.get("confidence") or 95), str(fact["fact_id"]),
    )

def evidence_from_fact(fact: dict[str, Any]) -> dict[str, Any]:
    return {
        "evidence_id": fact["fact_id"], "canonical_enterprise_id": fact["canonical_enterprise_id"], "enterprise_id": fact["canonical_enterprise_id"], "organisation": fact["canonical_enterprise_id"],
        "source_id": fact["source_id"], "source_name": fact["source_title"], "source_url": fact["source_url"], "source_type": "golden_calibration", "document_checksum": fact["document_checksum"],
        "page_number": fact["page"], "page_range": str(fact["page"]), "extracted_text": fact["source_excerpt"], "snippet": fact["source_excerpt"],
        "cleaned_observation": fact["atomic_statement"], "extracted_observation": fact["atomic_statement"], "commercial_condition": fact["claim_type"], "affected_attribute": fact["affected_attribute"],
        "confidence": fact["confidence"], "overall_evidence_quality": fact["confidence"], "publication_date": fact["publication_date"], "extraction_timestamp": fact["curated_at"] + "T00:00:00+00:00", "provenance": "evidence_curated", "source_provenance": "evidence_curated",
        "period": fact.get("period"), "state": fact.get("state"), "value": fact.get("structured_value"), "unit": fact.get("unit"), "currency": fact.get("currency"),
        "evidence_disposition": "accepted + foundation_eligible", "foundation_eligible": True, "foundation_eligibility_reason": "Governed evidence-backed human-curated extraction.",
    }

def validate_golden_facts(path: Path = DEFAULT_GOLDEN_FACTS) -> list[FactualClaim]:
    claims = [claim_from_fact(f) for f in load_golden_facts(path)]
    for claim in claims:
        validate_factual_claim(claim)
    return claims

def import_golden_facts(path: Path = DEFAULT_GOLDEN_FACTS, service: ObservationMemoryService | None = None) -> dict[str, Any]:
    service = service or ObservationMemoryService()
    facts = load_golden_facts(path)
    for fact in facts:
        validate_factual_claim(claim_from_fact(fact))
    reports = [service.process_evidence(evidence_from_fact(fact)) for fact in facts]
    return {"facts": len(facts), "observations_created": len(service.observations.list()), "model_attributes_created": len(service.models.get("bt-group-plc").attributes), "rejected_claims": [c for r in reports for c in r.rejected_claims]}
