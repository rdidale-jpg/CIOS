"""Aggregate governed live evidence into Flora reporting metrics."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Iterable

from cios.applications.flora.live.store import evidence_fingerprint
from cios.applications.flora.models import BriefingItem, TargetAccount

RELEVANT_CONDITIONS = {
    "Network Intelligence", "Operational Efficiency", "AI Modernisation", "Operational Resilience",
    "Customer Trust", "Regulatory Pressure", "Data Modernisation", "Digital Leadership", "Technology Debt",
    "Cost Pressure", "Customer Experience", "Competition", "Service Transformation", "Digital Modernisation", "Legacy Technology", "Spending Pressure", "Citizen Experience", "Cyber Resilience", "AI Readiness", "Procurement Readiness",
}

TIER_WEIGHT = {"tier_1_regulator": 5, "tier_1_company": 4, "tier_1_public_body": 4, "tier_2_feed": 2}


@dataclass(frozen=True)
class ScoreAdjustment:
    organisation: str
    base_score: int
    live_evidence_bonus: int
    confidence_adjustment: int
    final_score: int
    reason: str


@dataclass
class OrganisationEvidenceMetrics:
    organisation: str
    sector: str = "Unknown"
    live_evidence_count: int = 0
    unique_source_count: int = 0
    latest_evidence_timestamp: str | None = None
    condition_counts: dict[str, int] = field(default_factory=dict)
    capability_counts: dict[str, int] = field(default_factory=dict)
    strongest_conditions: list[str] = field(default_factory=list)
    strongest_capabilities: list[str] = field(default_factory=list)
    evidence_tier_mix: dict[str, int] = field(default_factory=dict)
    source_type_mix: dict[str, int] = field(default_factory=dict)
    evidence_freshness: str = "no live evidence"
    top_receipts: list[dict[str, Any]] = field(default_factory=list)
    tier_score: int = 0
    condition_relevance: int = 0


def _parse_timestamp(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _freshness(latest: datetime | None, now: datetime | None = None) -> str:
    if latest is None:
        return "unknown freshness"
    now = now or datetime.now(UTC)
    if latest.tzinfo is None:
        latest = latest.replace(tzinfo=UTC)
    days = max(0, (now - latest).days)
    if days == 0:
        return "collected today"
    if days <= 7:
        return f"collected {days} day(s) ago"
    if days <= 30:
        return f"collected {days} day(s) ago; still recent"
    return f"collected {days} day(s) ago; ageing"


def unique_live_evidence(items: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for item in items:
        fp = str(item.get("evidence_fingerprint") or evidence_fingerprint(item))
        if fp in seen:
            continue
        seen.add(fp)
        unique.append(item)
    return unique


def aggregate_live_evidence(items: Iterable[dict[str, Any]]) -> dict[str, OrganisationEvidenceMetrics]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in unique_live_evidence(items):
        org = str(item.get("organisation") or "Unknown")
        grouped[org].append(item)

    output: dict[str, OrganisationEvidenceMetrics] = {}
    for org, rows in grouped.items():
        sources = {str(r.get("source_id") or r.get("source_name") or r.get("source_url") or "unknown") for r in rows}
        conditions = Counter(str(r.get("commercial_condition") or r.get("condition") or "Unmapped") for r in rows)
        capabilities = Counter(str(r.get("likely_capability") or r.get("capability") or "AI opportunity discovery") for r in rows)
        tiers = Counter(str(r.get("evidence_tier") or "unknown") for r in rows)
        source_types = Counter(str(r.get("source_type") or "unknown") for r in rows)
        timestamps = [_parse_timestamp(r.get("extraction_timestamp") or r.get("publication_date")) for r in rows]
        latest = max((ts for ts in timestamps if ts is not None), default=None)
        sorted_rows = sorted(rows, key=lambda r: (TIER_WEIGHT.get(str(r.get("evidence_tier")), 0), str(r.get("extraction_timestamp") or "")), reverse=True)
        output[org] = OrganisationEvidenceMetrics(
            organisation=org,
            sector=str(rows[0].get("sector") or "Unknown"),
            live_evidence_count=len(rows),
            unique_source_count=len(sources),
            latest_evidence_timestamp=latest.isoformat() if latest else None,
            condition_counts=dict(conditions),
            capability_counts=dict(capabilities),
            strongest_conditions=[k for k, _ in conditions.most_common(3)],
            strongest_capabilities=[k for k, _ in capabilities.most_common(3)],
            evidence_tier_mix=dict(tiers),
            source_type_mix=dict(source_types),
            evidence_freshness=_freshness(latest),
            top_receipts=[{
                "source_name": str(r.get("source_name") or r.get("source_id") or "Unknown source"),
                "url": str(r.get("source_url") or r.get("url") or ""),
                "snippet": str(r.get("snippet") or ""),
                "condition": str(r.get("commercial_condition") or "Unmapped"),
                "capability": str(r.get("likely_capability") or "AI opportunity discovery"),
                "confidence": int(r.get("confidence") or 70),
                "source_type": str(r.get("source_type") or "unknown"),
            } for r in sorted_rows[:3]],
            tier_score=max((TIER_WEIGHT.get(str(t), 0) for t in tiers), default=0),
            condition_relevance=sum(c for cond, c in conditions.items() if cond in RELEVANT_CONDITIONS),
        )
    return output


def adjust_score(organisation: str, base_score: int, metrics: OrganisationEvidenceMetrics | None) -> ScoreAdjustment:
    if not metrics or metrics.live_evidence_count == 0:
        return ScoreAdjustment(organisation, base_score, 0, 0, base_score, "No live evidence; seeded score retained.")
    live_bonus = min(14, metrics.unique_source_count * 3 + metrics.condition_relevance * 2)
    diversity = len(metrics.evidence_tier_mix) + len(metrics.source_type_mix)
    confidence = min(6, metrics.tier_score + max(0, diversity - 1))
    final = min(100, base_score + live_bonus + confidence)
    reason = f"Live uplift from {metrics.live_evidence_count} evidence object(s), {metrics.unique_source_count} source(s), strongest condition(s): {', '.join(metrics.strongest_conditions) or 'unmapped'}."
    return ScoreAdjustment(organisation, base_score, live_bonus, confidence, final, reason)


def attention_organisations(items: list[BriefingItem], metrics_by_org: dict[str, OrganisationEvidenceMetrics], accounts: list[TargetAccount]) -> list[str]:
    priority = {a.organisation_name: {"high": 3, "medium": 2, "low": 1}[a.priority.value] for a in accounts}
    base = {i.organisation: i.scores.ai_reinvention_opportunity_score for i in items}
    candidates = {org for org, m in metrics_by_org.items() if m.live_evidence_count > 0 or m.condition_relevance > 0}
    candidates |= {org for org, score in base.items() if score >= 75 and metrics_by_org.get(org, OrganisationEvidenceMetrics(org)).live_evidence_count > 0}
    if not candidates:
        return [i.organisation for i in items[:3]]
    return sorted(candidates, key=lambda org: (
        metrics_by_org.get(org, OrganisationEvidenceMetrics(org)).live_evidence_count,
        metrics_by_org.get(org, OrganisationEvidenceMetrics(org)).tier_score,
        metrics_by_org.get(org, OrganisationEvidenceMetrics(org)).condition_relevance,
        priority.get(org, 0),
        base.get(org, 0),
    ), reverse=True)
