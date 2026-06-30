"""Portfolio radar and source effectiveness calculations for Flora v0.8."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Iterable

from cios.applications.flora.live.aggregation import aggregate_live_evidence, adjust_score, unique_live_evidence
from cios.applications.flora.live.source_registry import SOURCES
from cios.applications.flora.live.store import DEFAULT_DIAGNOSTICS_PATH, DEFAULT_PATH, read_jsonl
from cios.applications.flora.pipeline import _ranked_items
from cios.applications.flora.seed_data import sample_commercial_dna, sample_signals, sample_watchlist

HIGH_POTENTIAL_THRESHOLD = 65
HIGH_CONFIDENCE_THRESHOLD = 40
TIER_WEIGHT = {"tier_1_regulator": 95, "tier_1_company": 88, "tier_1_public_body": 88, "tier_2_feed": 62, "unknown": 35}


@dataclass(frozen=True)
class RadarOrganisation:
    organisation: str
    sector: str
    final_score: int
    base_score: int
    live_uplift: int
    evidence_count: int
    unique_source_count: int
    strongest_condition: str
    strongest_capability: str
    evidence_confidence: int
    quadrant: str
    quadrant_threshold_result: str
    quadrant_reason: str
    rank_change_reason: str
    seeded_rank: int
    final_rank: int


@dataclass(frozen=True)
class SourceEffectiveness:
    source_id: str
    organisation: str
    source_name: str
    source_type: str
    evidence_tier: str
    access_success_rate: float
    evidence_yield: float
    unique_evidence_count: int
    duplicate_count: int
    latest_success: str
    latest_failure: str
    failure_reason: str
    evidence_quality_average: float
    relevance_score: float
    source_effectiveness_score: float
    recommendation: str


def evidence_confidence(metrics: Any | None) -> int:
    """Return deterministic source-quality confidence for an organisation."""
    if not metrics or metrics.live_evidence_count <= 0:
        return 0
    tier_values = [TIER_WEIGHT.get(tier, 35) * count for tier, count in metrics.evidence_tier_mix.items()]
    tier_total = sum(metrics.evidence_tier_mix.values()) or 1
    tier_score = sum(tier_values) / tier_total
    source_diversity = min(15, metrics.unique_source_count * 5)
    evidence_depth = min(12, metrics.live_evidence_count * 2)
    relevance = min(13, metrics.condition_relevance * 2)
    return max(0, min(100, round(tier_score * 0.6 + source_diversity + evidence_depth + relevance)))


def quadrant_for(final_score: int, confidence: int) -> str:
    high_potential = final_score >= HIGH_POTENTIAL_THRESHOLD
    high_confidence = confidence >= HIGH_CONFIDENCE_THRESHOLD
    if high_potential and high_confidence:
        return "Priority Pursuits"
    if high_potential:
        return "Investigate"
    if high_confidence:
        return "Monitor"
    return "Coverage Gap"


def quadrant_diagnostic(final_score: int, confidence: int, metrics: Any | None, mode: str) -> tuple[str, str]:
    potential = "passes" if final_score >= HIGH_POTENTIAL_THRESHOLD else "fails"
    evidence = "passes" if confidence >= HIGH_CONFIDENCE_THRESHOLD else "fails"
    result = f"potential {potential} {HIGH_POTENTIAL_THRESHOLD}; confidence {evidence} {HIGH_CONFIDENCE_THRESHOLD}"
    reasons = []
    if final_score < HIGH_POTENTIAL_THRESHOLD:
        reasons.append("low final score")
    if confidence < HIGH_CONFIDENCE_THRESHOLD:
        reasons.append("low evidence confidence")
    if not metrics or metrics.unique_source_count < 2:
        reasons.append("insufficient source diversity")
    if not metrics or metrics.condition_relevance <= 0:
        reasons.append("low condition relevance")
    if mode != "LIVE":
        reasons.append("fallback mode" if mode == "SEEDED FALLBACK" else "mixed live/seeded mode")
    if not reasons:
        reasons.append("passes early-pilot score and evidence thresholds")
    return result, "; ".join(reasons)


def build_radar_rows(evidence: Iterable[dict[str, Any]] | None = None) -> list[RadarOrganisation]:
    evidence_items = unique_live_evidence(evidence if evidence is not None else read_jsonl(DEFAULT_PATH))
    pilot_orgs = {a.organisation_name for a in sample_watchlist()}
    metrics_by_org = aggregate_live_evidence([e for e in evidence_items if e.get("organisation") in pilot_orgs])
    ranked_seeded = _ranked_items(sample_commercial_dna(), sample_watchlist(), sample_signals())
    seeded_rank = {item.organisation: idx for idx, item in enumerate(ranked_seeded, 1)}
    provisional = []
    for item in ranked_seeded:
        adjustment = adjust_score(item.organisation, item.scores.ai_reinvention_opportunity_score, metrics_by_org.get(item.organisation))
        metrics = metrics_by_org.get(item.organisation)
        confidence = evidence_confidence(metrics)
        live_uplift = adjustment.live_evidence_bonus + adjustment.confidence_adjustment
        provisional.append((item, adjustment, metrics, confidence, live_uplift))
    final_rank = {item.organisation: idx for idx, (item, *_rest) in enumerate(sorted(provisional, key=lambda row: (row[1].final_score, row[3], row[2].live_evidence_count if row[2] else 0), reverse=True), 1)}
    rows = []
    for item, adjustment, metrics, confidence, live_uplift in provisional:
        sr = seeded_rank[item.organisation]
        fr = final_rank[item.organisation]
        if live_uplift and fr < sr:
            reason = f"Live evidence improved rank from {sr} to {fr}; base score {adjustment.base_score}, live uplift +{live_uplift}."
        elif live_uplift:
            reason = f"Live evidence added +{live_uplift}, but seeded base score still dominates rank behaviour."
        else:
            reason = f"No live uplift; rank is driven by seeded base score {adjustment.base_score}."
        threshold_result, quadrant_reason = quadrant_diagnostic(adjustment.final_score, confidence, metrics, adjustment.scoring_mode)
        rows.append(RadarOrganisation(
            organisation=item.organisation,
            sector=item.sector,
            final_score=adjustment.final_score,
            base_score=adjustment.base_score,
            live_uplift=live_uplift,
            evidence_count=metrics.live_evidence_count if metrics else 0,
            unique_source_count=metrics.unique_source_count if metrics else 0,
            strongest_condition=(metrics.strongest_conditions[0] if metrics and metrics.strongest_conditions else (item.strongest_detected_signals[0] if item.strongest_detected_signals else "Seeded fallback")),
            strongest_capability=(metrics.strongest_capabilities[0] if metrics and metrics.strongest_capabilities else (item.likely_capability_areas[0] if item.likely_capability_areas else "AI opportunity discovery")),
            evidence_confidence=confidence,
            quadrant=quadrant_for(adjustment.final_score, confidence),
            quadrant_threshold_result=threshold_result,
            quadrant_reason=quadrant_reason,
            rank_change_reason=reason,
            seeded_rank=sr,
            final_rank=fr,
        ))
    return sorted(rows, key=lambda r: (r.quadrant, -r.final_score, -r.evidence_confidence, r.organisation))


def source_effectiveness_rows(diagnostics: Iterable[dict[str, Any]] | None = None, evidence: Iterable[dict[str, Any]] | None = None) -> list[SourceEffectiveness]:
    diagnostics_list = list(diagnostics if diagnostics is not None else read_jsonl(DEFAULT_DIAGNOSTICS_PATH))
    evidence_list = unique_live_evidence(evidence if evidence is not None else read_jsonl(DEFAULT_PATH))
    attempts_by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for d in diagnostics_list:
        attempts_by_source[str(d.get("source_id") or "")].append(d)
    evidence_by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for e in evidence_list:
        evidence_by_source[str(e.get("source_id") or e.get("source_name") or "")].append(e)
    configured = {s.source_id: s for s in SOURCES}
    rows = []
    for source_id in sorted(set(configured) | set(attempts_by_source) | set(evidence_by_source)):
        src = configured.get(source_id)
        attempts = attempts_by_source.get(source_id, [])
        evs = evidence_by_source.get(source_id, [])
        successes = [d for d in attempts if d.get("status") in {"succeeded", "no evidence"} or d.get("success")]
        failures = [d for d in attempts if d.get("status") == "failed"]
        with_evidence = [d for d in attempts if int(d.get("evidence_count") or 0) > 0]
        access_rate = len(successes) / len(attempts) if attempts else 0.0
        evidence_yield = sum(int(d.get("evidence_count") or 0) for d in attempts) / len(attempts) if attempts else 0.0
        qualities = [int(e.get("overall_evidence_quality") or e.get("confidence") or 0) for e in evs]
        quality = sum(qualities) / len(qualities) if qualities else 0.0
        tier = (src.evidence_tier if src else (evs[0].get("evidence_tier") if evs else "unknown"))
        relevance = min(100.0, (TIER_WEIGHT.get(str(tier), 35) * 0.45) + min(30, len(evs) * 6) + (quality * 0.25))
        score = round(access_rate * 30 + min(25, evidence_yield * 5) + min(20, len(evs) * 3) + quality * 0.15 + relevance * 0.10, 1)
        latest_success = max((str(d.get("last_attempted") or d.get("attempted_at") or "") for d in successes), default="")
        latest_failure = max((str(d.get("last_attempted") or d.get("attempted_at") or "") for d in failures), default="")
        failure_reason = str((failures[-1].get("failure_reason") if failures else "") or "")
        duplicate_count = max(0, sum(int(d.get("evidence_count") or 0) for d in with_evidence) - len(evs))
        if not attempts:
            rec = "needs better URL"
        elif failures and not successes:
            rec = "replace" if failure_reason in {"access_blocked", "non_html"} else "needs better URL"
        elif len(evs) == 0:
            rec = "review"
        elif duplicate_count > len(evs):
            rec = "disable"
        elif score >= 55:
            rec = "keep"
        else:
            rec = "review"
        rows.append(SourceEffectiveness(source_id, src.organisation if src else str((attempts or evs)[0].get("organisation", "Unknown")), src.source_name if src else source_id, src.source_type if src else str((attempts or evs)[0].get("source_type", "unknown")), str(tier), round(access_rate, 2), round(evidence_yield, 2), len(evs), duplicate_count, latest_success, latest_failure, failure_reason, round(quality, 1), round(relevance, 1), score, rec))
    return sorted(rows, key=lambda r: r.source_effectiveness_score, reverse=True)


def portfolio_summary() -> dict[str, Any]:
    radar = build_radar_rows()
    counts = Counter(r.quadrant for r in radar)
    high_under = sorted([r for r in radar if r.final_score >= HIGH_POTENTIAL_THRESHOLD], key=lambda r: (r.evidence_confidence, -r.final_score, r.organisation))
    mover = sorted(radar, key=lambda r: (r.live_uplift, r.evidence_confidence), reverse=True)
    sources = source_effectiveness_rows()
    weak_types = Counter(r.source_type for r in sources if r.recommendation in {"review", "replace", "disable", "needs better URL"})
    return {"priority_pursuits": counts["Priority Pursuits"], "investigate": counts["Investigate"], "monitor": counts["Monitor"], "coverage_gaps": counts["Coverage Gap"], "most_under_covered_high_potential": high_under[0].organisation if high_under else "None", "strongest_evidence_backed_mover": mover[0].organisation if mover and mover[0].live_uplift else "None", "best_performing_source": sources[0].source_name if sources else "None", "weakest_source_category": weak_types.most_common(1)[0][0] if weak_types else "None"}
