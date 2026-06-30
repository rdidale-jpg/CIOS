"""Deterministic Flora score explainability views and data."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from cios.applications.flora.intelligence.evidence_engine import evidence_for_organisation
from cios.applications.flora.live.aggregation import aggregate_live_evidence, adjust_score, unique_live_evidence
from cios.applications.flora.live.store import DEFAULT_PATH, read_jsonl
from cios.applications.flora.pipeline import _ranked_items
from cios.applications.flora.portfolio import build_radar_rows, evidence_confidence
from cios.applications.flora.provider_context import default_provider_context
from cios.applications.flora.seed_data import sample_commercial_dna, sample_signals, sample_watchlist

MISSING_EVIDENCE = [
    "executive sponsor",
    "funding",
    "procurement timing",
    "incumbent supplier",
    "competitor engagement",
    "current transformation programme",
    "internal pain owner",
]


def slug_for_score(name: str) -> str:
    return "".join(ch for ch in name if ch.isalnum())


def normalise_score_slug(slug: str) -> str:
    key = "".join(ch for ch in slug.lower() if ch.isalnum())
    for account in sample_watchlist():
        if slug_for_score(account.organisation_name).lower() == key:
            return account.organisation_name
    raise ValueError("Flora score route not found")


@dataclass(frozen=True)
class ScoreFacet:
    name: str
    score: int
    weighting: str
    explanation: str
    evidence_used: list[str]
    missing_evidence: list[str]
    source_links: list[dict[str, str]]


@dataclass(frozen=True)
class ScoreTraceRow:
    evidence_object: str
    condition_or_capability: str
    facet: str
    score_contribution: str
    final_score: int


def score_detail(slug: str) -> dict[str, Any]:
    organisation = normalise_score_slug(slug)
    dna = sample_commercial_dna()
    ranked = _ranked_items(dna, sample_watchlist(), sample_signals())
    item = next(i for i in ranked if i.organisation == organisation)
    live_items = [e for e in unique_live_evidence(read_jsonl(DEFAULT_PATH)) if e.get("organisation") == organisation]
    live_metrics = aggregate_live_evidence(live_items).get(organisation)
    adjustment = adjust_score(organisation, item.scores.ai_reinvention_opportunity_score, live_metrics)
    radar = next(r for r in build_radar_rows() if r.organisation == organisation)
    seeded_evidence = evidence_for_organisation(organisation)
    provider = default_provider_context()
    live_links = [{"name": str(e.get("source_name") or e.get("source_id") or "Live source"), "url": str(e.get("source_url") or e.get("url") or "")} for e in live_items if str(e.get("source_url") or e.get("url") or "")]
    seeded_labels = [f"{e.evidence_id}: {e.summary}" for e in seeded_evidence[:4]]
    strongest_condition = radar.strongest_condition
    strongest_capability = radar.strongest_capability
    confidence = evidence_confidence(live_metrics)
    source_diversity = min(100, radar.unique_source_count * 20)
    condition_strength = item.scores.commercial_pressure_index
    capability_relevance = item.scores.ai_suitability_index
    provider_relevance = 100 if item.sector in provider.target_sectors else 55
    freshness_score = 0 if not live_metrics else (80 if "today" in live_metrics.evidence_freshness else 65 if "recent" in live_metrics.evidence_freshness else 45)
    missing_penalty = max(0, len(MISSING_EVIDENCE) - radar.evidence_count)
    facets = [
        ScoreFacet("Base strategic fit", adjustment.base_score, "seeded base", "Average of pressure, AI suitability, readiness, attractiveness and influence potential.", seeded_labels, [], []),
        ScoreFacet("Live evidence uplift", adjustment.live_evidence_bonus, "capped at +14", adjustment.reason, [str(e.get("snippet") or e.get("title") or e.get("source_name") or "live evidence") for e in live_items[:4]], MISSING_EVIDENCE if not live_items else [], live_links),
        ScoreFacet("Evidence confidence", confidence, "source quality", "Calculated from evidence tier, source diversity, evidence depth and mapped condition relevance.", [r.get("snippet", "") for r in (live_metrics.top_receipts if live_metrics else [])], MISSING_EVIDENCE, live_links),
        ScoreFacet("Source diversity", source_diversity, "unique sources", f"{radar.unique_source_count} unique source(s) are currently attached to the organisation.", [l["name"] for l in live_links], ["additional independent sources"] if radar.unique_source_count < 2 else [], live_links),
        ScoreFacet("Condition strength", condition_strength, "25% of base", f"Strongest mapped condition is {strongest_condition}.", seeded_labels[:2], [], []),
        ScoreFacet("Capability relevance", capability_relevance, "25% of base", f"Strongest mapped capability is {strongest_capability}.", seeded_labels[:2], [], []),
        ScoreFacet("Provider relevance", provider_relevance, "contextual", f"Sector fit against {provider.provider_name} configured target sectors and offerings.", provider.strategic_offerings[:3], [], []),
        ScoreFacet("Freshness / recency", freshness_score, "live recency", live_metrics.evidence_freshness if live_metrics else "No live evidence freshness; seeded fallback only.", [str(e.get("publication_date") or e.get("extraction_timestamp") or "") for e in live_items[:4]], ["recent governed live evidence"] if not live_items else [], live_links),
        ScoreFacet("Missing evidence penalty", missing_penalty, "confidence limiter", "Missing evidence does not reduce the seeded base directly; it limits confidence and explains what to validate next.", [], MISSING_EVIDENCE, []),
    ]
    evidence_rows = []
    for e in seeded_evidence[:6]:
        evidence_rows.append({"id": e.evidence_id, "source_name": e.source_name, "source_type": e.source_type, "url": "", "snippet": e.summary, "condition": e.evidence_category.value, "capability": ", ".join(e.capability_tags), "confidence": e.confidence, "quality": "seeded"})
    for idx, e in enumerate(live_items[:6], 1):
        evidence_rows.append({"id": str(e.get("evidence_id") or e.get("evidence_fingerprint") or f"LIVE-{idx}"), "source_name": str(e.get("source_name") or e.get("source_id") or "Live source"), "source_type": str(e.get("source_type") or "unknown"), "url": str(e.get("source_url") or e.get("url") or ""), "snippet": str(e.get("snippet") or ""), "condition": str(e.get("commercial_condition") or e.get("condition") or "Unmapped"), "capability": str(e.get("likely_capability") or e.get("capability") or "AI opportunity discovery"), "confidence": int(e.get("confidence") or 70), "quality": str(e.get("overall_evidence_quality") or e.get("evidence_tier") or "live")})
    traces = [ScoreTraceRow(r["id"], f"{r['condition']} / {r['capability']}", "Condition strength" if r["quality"] == "seeded" else "Live evidence uplift", "+seeded base" if r["quality"] == "seeded" else f"+{adjustment.live_evidence_bonus} capped live uplift pool", adjustment.final_score) for r in evidence_rows]
    return {"organisation": organisation, "sector": item.sector, "final_score": adjustment.final_score, "base_score": adjustment.base_score, "live_uplift": adjustment.live_evidence_bonus + adjustment.confidence_adjustment, "evidence_confidence": confidence, "unique_evidence_count": radar.evidence_count, "unique_source_count": radar.unique_source_count, "strongest_condition": strongest_condition, "strongest_capability": strongest_capability, "quadrant": radar.quadrant, "facets": facets, "evidence_rows": evidence_rows, "missing_evidence": MISSING_EVIDENCE, "traces": traces}
