"""Aggregate governed live evidence into Flora reporting metrics."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Iterable

from cios.applications.flora.live.store import evidence_fingerprint, read_jsonl
from cios.applications.flora.rob_score import latest_rob_score
from cios.applications.flora.workspace.feedback import runtime_dir
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
    live_evidence_score: int
    learned_evidence_score: int
    rob_score_adjustment: int
    final_score: int
    reason: str
    source_diversity_uplift: int = 0
    condition_relevance_uplift: int = 0
    evidence_quality_uplift: int = 0
    seeded_fallback_score: int | None = None
    missing_evidence_penalty: int = 0
    scoring_mode: str = "SEEDED FALLBACK"
    evidence_confidence: int = 0
    learned_evidence: dict[str, int] = field(default_factory=dict)
    audit_total: int = 0

    @property
    def live_evidence_bonus(self) -> int:
        return self.live_evidence_score

    @property
    def confidence_adjustment(self) -> int:
        return self.learned_evidence_score


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
    average_quality: int = 0
    accepted_evidence_count: int = 0
    rejected_evidence_count: int = 0
    downgraded_evidence_count: int = 0
    insufficient_claims: list[str] = field(default_factory=list)
    weakest_receipts: list[dict[str, Any]] = field(default_factory=list)
    primary_evidence_count: int = 0
    secondary_evidence_count: int = 0
    context_only_count: int = 0
    coverage_sufficient: bool = False
    coverage_status: str = "Evidence coverage insufficient — collect more specific sources."


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
        condition_sources: dict[str, set[str]] = defaultdict(set)
        condition_levels: dict[str, list[str]] = defaultdict(list)
        for r in rows:
            cond = str(r.get("commercial_condition") or r.get("condition") or "Unmapped")
            condition_sources[cond].add(str(r.get("source_id") or r.get("source_name") or r.get("source_url") or "unknown"))
            condition_levels[cond].append(str(r.get("relevance_level") or "HIGH"))
        strategic_rows = [r for r in rows if r.get("supports_strategic_signals", True) and r.get("evidence_type", "Primary Evidence") != "Context Only"]
        strategic_ids = {id(r) for r in strategic_rows}
        for cond in list(condition_levels):
            condition_levels[cond] = [str(r.get("relevance_level") or "HIGH") for r in rows if id(r) in strategic_ids and str(r.get("commercial_condition") or r.get("condition") or "Unmapped") == cond]
            condition_sources[cond] = {str(r.get("source_id") or r.get("source_name") or r.get("source_url") or "unknown") for r in rows if id(r) in strategic_ids and str(r.get("commercial_condition") or r.get("condition") or "Unmapped") == cond}
        supported_conditions = {cond for cond, levels in condition_levels.items() if levels and ("HIGH" in levels or (levels.count("MEDIUM") >= 2 and len(condition_sources[cond]) >= 2))}
        insufficient_claims = sorted(cond for cond in condition_levels if cond not in supported_conditions)
        conditions = Counter(str(r.get("commercial_condition") or r.get("condition") or "Unmapped") for r in rows if str(r.get("commercial_condition") or r.get("condition") or "Unmapped") in supported_conditions)
        capabilities = Counter(str(r.get("likely_capability") or r.get("capability") or "AI opportunity discovery") for r in strategic_rows)
        tiers = Counter(str(r.get("evidence_tier") or "unknown") for r in rows)
        source_types = Counter(str(r.get("source_type") or "unknown") for r in rows)
        timestamps = [_parse_timestamp(r.get("extraction_timestamp") or r.get("publication_date")) for r in rows]
        latest = max((ts for ts in timestamps if ts is not None), default=None)
        sorted_rows = sorted(rows, key=lambda r: (r.get("relevance_level") == "HIGH", int(r.get("confidence") or 0), TIER_WEIGHT.get(str(r.get("evidence_tier")), 0), str(r.get("extraction_timestamp") or "")), reverse=True)
        weak_rows = sorted(rows, key=lambda r: (r.get("relevance_level") == "HIGH", int(r.get("confidence") or 0)))
        primary_count = len([r for r in rows if r.get("evidence_type") == "Primary Evidence"])
        secondary_count = len([r for r in rows if r.get("evidence_type") == "Secondary Evidence"])
        context_count = len([r for r in rows if r.get("evidence_type") == "Context Only"])
        legacy_rows = [r for r in rows if "evidence_type" not in r]
        coverage_ok = (len(strategic_rows) >= 3 and len({str(r.get("source_type") or "unknown") for r in strategic_rows}) >= 2 and primary_count >= 1) or bool(legacy_rows)
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
            average_quality=round(sum(int(r.get("overall_evidence_quality") or r.get("confidence") or 70) for r in rows) / len(rows)),
            accepted_evidence_count=len([r for r in rows if r.get("accepted_for_claims", True)]),
            rejected_evidence_count=len([r for r in rows if r.get("accepted_for_claims") is False]),
            downgraded_evidence_count=len([r for r in rows if r.get("relevance_level") == "LOW"]),
            insufficient_claims=insufficient_claims,
            primary_evidence_count=primary_count,
            secondary_evidence_count=secondary_count,
            context_only_count=context_count,
            coverage_sufficient=coverage_ok,
            coverage_status="Evidence coverage sufficient." if coverage_ok else "Evidence coverage insufficient — collect more specific sources.",
            weakest_receipts=[{
                "source_name": str(r.get("source_name") or r.get("source_id") or "Unknown source"),
                "url": str(r.get("source_url") or r.get("url") or ""),
                "snippet": str(r.get("snippet") or ""),
                "condition": str(r.get("commercial_condition") or "Unmapped"),
                "confidence": int(r.get("confidence") or 0),
                "relevance_level": str(r.get("relevance_level") or "MEDIUM"),
                "rejection_reasons": r.get("rejection_reasons", []),
            } for r in weak_rows[:3]],
        )
    return output


MISSING_EVIDENCE_CATEGORIES = {
    "sponsor": ("sponsor", "executive owner", "decision maker"),
    "funding": ("funding", "budget", "investment", "spend"),
    "timing": ("timing", "deadline", "procurement", "tender", "contract"),
    "incumbent": ("incumbent", "supplier", "partner", "vendor"),
    "competitor engagement": ("competitor", "bidder", "engagement", "market engagement"),
    "internal pain owner": ("pain owner", "function", "department", "director", "chief"),
}


def learned_evidence_score(organisation: str) -> tuple[int, dict[str, int]]:
    """Return a small deterministic placeholder score for explicitly taught evidence."""
    feedback = [r for r in read_jsonl(runtime_dir() / "feedback.jsonl") if str(r.get("organisation") or "") == organisation]
    logbook = read_jsonl(runtime_dir() / "logbook.jsonl")
    validations = sum(1 for r in feedback if str(r.get("feedback_type") or "").lower() == "useful")
    corrections = sum(1 for r in feedback if "correction" in str(r.get("feedback_type") or "").lower())
    actions = sum(1 for r in feedback if "acted" in str(r.get("feedback_type") or "").lower()) + sum(1 for r in logbook if str(r.get("action_taken") or "").strip())
    rob_feedback = sum(1 for r in logbook if str(r.get("flora_should_learn") or "").strip())
    outcome_evidence = sum(1 for r in logbook if int(r.get("flora_value_score") or 0) >= 4)
    score = min(12, validations * 2 + actions * 2 + rob_feedback + outcome_evidence * 2 - corrections * 2)
    return max(0, score), {"validations": validations, "corrections": corrections, "rob_feedback": rob_feedback, "actions_taken": actions, "outcome_evidence": outcome_evidence}


def missing_evidence_penalty(metrics: OrganisationEvidenceMetrics | None) -> int:
    if not metrics or metrics.live_evidence_count <= 0:
        return 0
    haystack = " ".join([*metrics.condition_counts.keys(), *metrics.capability_counts.keys(), *(r.get("snippet", "") for r in metrics.top_receipts)]).lower()
    missing = [name for name, terms in MISSING_EVIDENCE_CATEGORIES.items() if not any(term in haystack for term in terms)]
    return min(4, len(missing))


def adjust_score(organisation: str, base_score: int, metrics: OrganisationEvidenceMetrics | None) -> ScoreAdjustment:
    learned_score, learned_breakdown = learned_evidence_score(organisation)
    rob = latest_rob_score(organisation)
    if (not metrics or metrics.live_evidence_count == 0) and learned_score == 0:
        final = min(100, max(0, base_score + rob.rob_score))
        return ScoreAdjustment(organisation, base_score, 0, 0, rob.rob_score, final, "No live or learned evidence; seeded fallback score retained.", scoring_mode="SEEDED FALLBACK", seeded_fallback_score=base_score, audit_total=final, learned_evidence=learned_breakdown)
    if not metrics or metrics.live_evidence_count == 0:
        penalty = 0
        live_score = 0
    else:
        evidence_count = min(20, metrics.live_evidence_count * 4)
        unique_sources = min(15, metrics.unique_source_count * 5)
        quality = min(15, round(metrics.average_quality * 0.15))
        tier = min(15, metrics.tier_score * 3)
        source_reliability = min(10, round(sum(TIER_WEIGHT.get(t, 1) * c for t, c in metrics.evidence_tier_mix.items()) / max(1, sum(metrics.evidence_tier_mix.values())) * 2))
        condition_strength = min(10, metrics.condition_relevance * 2)
        capability_relevance = min(5, len([c for c in metrics.capability_counts if c and c != "AI opportunity discovery"]) * 2)
        freshness = 7 if "today" in metrics.evidence_freshness else 5 if "recent" in metrics.evidence_freshness or "day" in metrics.evidence_freshness else 2
        diversity = min(8, len(metrics.evidence_tier_mix) + len(metrics.source_type_mix) + metrics.unique_source_count)
        live_score = min(100, 10 + evidence_count + unique_sources + quality + tier + source_reliability + condition_strength + capability_relevance + freshness + diversity)
        penalty = missing_evidence_penalty(metrics)
        if any(t == "unknown" for t in metrics.evidence_tier_mix):
            live_score = min(100, live_score + 10)
        if not metrics.coverage_sufficient:
            live_score = round(live_score * 0.55)
            penalty += 8
    final = min(100, max(0, live_score + learned_score + rob.rob_score - penalty))
    mode = "LIVE EVIDENCE"
    if rob.rob_score:
        mode = "LIVE + HUMAN"
    if learned_score and live_score:
        mode = "LEARNED + LIVE"
    elif learned_score and not live_score:
        mode = "LEARNED"
    reason = f"Evidence-first score from live evidence {live_score}, learned evidence {learned_score}, Rob adjustment {rob.rob_score}, missing evidence penalty {penalty}."
    return ScoreAdjustment(organisation, base_score, live_score, learned_score, rob.rob_score, final, reason, source_diversity_uplift=min(15, metrics.unique_source_count * 5) if metrics else 0, condition_relevance_uplift=min(10, metrics.condition_relevance * 2) if metrics else 0, evidence_quality_uplift=min(15, round(metrics.average_quality * 0.15)) if metrics else 0, missing_evidence_penalty=penalty, scoring_mode=mode, audit_total=final, learned_evidence=learned_breakdown)

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
