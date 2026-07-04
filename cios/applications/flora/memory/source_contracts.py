"""Source-type factual extraction contracts for Flora foundation facts."""
from __future__ import annotations

from dataclasses import dataclass
import re

@dataclass(frozen=True)
class SourceFactualContract:
    source_type: str
    permitted_claim_types: tuple[str, ...]
    foundation_eligible: bool
    notes: str

CONTRACTS: dict[str, SourceFactualContract] = {
    "annual_report": SourceFactualContract("annual_report", ("enterprise_identity_confirmed", "business_unit_disclosed", "financial_metric_reported", "strategic_pillar_stated", "strategic_commitment_stated", "executive_role_confirmed"), True, "Annual reports may update foundation state when claims are explicit and page-backed."),
    "investor_results": SourceFactualContract("investor_results", ("financial_metric_reported", "financial_guidance_stated", "financial_target_stated"), True, "Results sources are financial-state eligible only."),
    "strategy_page": SourceFactualContract("strategy_page", ("strategic_pillar_stated", "strategic_commitment_stated"), True, "Only named pillars or measurable commitments are factual."),
    "leadership_page": SourceFactualContract("leadership_page", ("executive_role_confirmed", "executive_appointment_announced", "executive_departure_confirmed"), True, "Only person-role/change facts are factual."),
    "official_newsroom": SourceFactualContract("official_newsroom", ("enterprise_event_announced", "partnership_announced", "programme_announced", "leadership_change_announced"), False, "Newsroom evidence is event or context by default; it must not update foundation financial or organisational state automatically."),
    "company_newsroom": SourceFactualContract("company_newsroom", ("enterprise_event_announced", "partnership_announced", "programme_announced", "leadership_change_announced"), False, "Newsroom evidence is event or context by default."),
}
PROMOTIONAL_RE = re.compile(r"\b(shows how|demonstrates|benefits|world[- ]class|innovative|collaboration shows|help customers|trusted partner)\b", re.I)

def contract_for(source_type: str | None) -> SourceFactualContract:
    return CONTRACTS.get(str(source_type or ""), SourceFactualContract(str(source_type or "unknown"), (), False, "No factual foundation contract registered."))

def classify_foundation_eligibility(evidence: dict) -> dict:
    contract = contract_for(evidence.get("source_type"))
    claim_type = str(evidence.get("commercial_condition") or evidence.get("mapped_condition") or evidence.get("claim_type") or "")
    text = str(evidence.get("snippet") or evidence.get("cleaned_observation") or evidence.get("extracted_text") or "")
    if PROMOTIONAL_RE.search(text):
        return {"evidence_disposition": "accepted + context_only", "foundation_eligible": False, "foundation_eligibility_reason": "Promotional or interpretive language is context-only.", "signal_eligible": True}
    if claim_type in contract.permitted_claim_types and contract.foundation_eligible:
        return {"evidence_disposition": "accepted + foundation_eligible", "foundation_eligible": True, "foundation_eligibility_reason": f"{contract.source_type} permits {claim_type}.", "signal_eligible": False}
    if contract.permitted_claim_types:
        return {"evidence_disposition": "accepted + signal_eligible", "foundation_eligible": False, "foundation_eligibility_reason": f"{claim_type or 'classification'} is not eligible for foundation model construction from {contract.source_type}.", "signal_eligible": True}
    return {"evidence_disposition": "accepted + context_only", "foundation_eligible": False, "foundation_eligibility_reason": contract.notes, "signal_eligible": True}
