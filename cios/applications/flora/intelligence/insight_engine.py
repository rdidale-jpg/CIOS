"""Deterministic commercial insight generation from governed evidence."""
from __future__ import annotations
from pydantic import BaseModel, Field
from cios.applications.flora.intelligence.evidence_engine import CommercialEvidence

class CommercialInsight(BaseModel):
    insight_id: str
    organisation: str
    title: str
    narrative: str
    supporting_evidence: list[str] = Field(default_factory=list)
    supporting_patterns: list[str] = Field(default_factory=list)
    supporting_assessments: list[str] = Field(default_factory=list)
    confidence: int = Field(ge=0, le=100)
    recommended_next_step: str


def generate_insights(organisation: str, evidence: list[CommercialEvidence], assessments: list[str] | None = None) -> list[CommercialInsight]:
    """Combine multiple evidence objects into deterministic human-readable insights."""
    assessments = assessments or []
    caps = [tag for ev in evidence for tag in ev.capability_tags]
    patterns = sorted({p for ev in evidence for p in ev.related_patterns})
    ids = [ev.evidence_id for ev in evidence]
    avg = round(sum(ev.confidence for ev in evidence) / len(evidence)) if evidence else 0
    insights: list[CommercialInsight] = []
    if any("customer" in cap for cap in caps):
        insights.append(CommercialInsight(
            insight_id=f"INS-{organisation.upper().replace(' ', '-')}-CUSTOMER-001", organisation=organisation,
            title="Customer Operations has become a strategic AI reinvention candidate.",
            narrative="Seeded customer, regulatory, technology and leadership evidence combine to indicate that service performance can be positioned as an AI-enabled reinvention conversation rather than a narrow scoring signal.",
            supporting_evidence=ids, supporting_patterns=[p for p in patterns if p in {"PAT-001", "PAT-003", "PAT-005", "PAT-007"}], supporting_assessments=assessments,
            confidence=min(100, avg + 4), recommended_next_step="Validate the executive owner, funding status and active incumbent transformation activity for Customer Operations.",
        ))
    if any(cap in {"asset management", "field operations", "network intelligence", "grid forecasting", "leakage analytics"} for cap in caps):
        insights.append(CommercialInsight(
            insight_id=f"INS-{organisation.upper().replace(' ', '-')}-OPS-001", organisation=organisation,
            title="Operational resilience evidence supports an AI-enabled performance improvement case.",
            narrative="Annual, regulatory and technology themes point to pressure on resilience, planning and operational transparency, creating a governed opening for asset, network or field-force AI discovery.",
            supporting_evidence=ids, supporting_patterns=[p for p in patterns if p in {"PAT-001", "PAT-004", "PAT-006", "PAT-007"}], supporting_assessments=assessments,
            confidence=avg, recommended_next_step="Run an outside-in operational resilience hypothesis review with operations and technology stakeholders.",
        ))
    return insights[:2]
