"""Deterministic scoring policy for Flora v0.1."""

from __future__ import annotations

from collections import Counter

from cios.applications.flora.models import CommercialDNA, ReinventionScores, Signal, TargetAccount

PRESSURE_CATEGORIES = {"financial pressure", "regulatory pressure", "competition", "customer experience", "operational resilience"}
AI_CATEGORIES = {"automation", "data modernisation", "customer experience", "network intelligence", "content intelligence", "workforce productivity"}
READINESS_CATEGORIES = {"digital transformation", "cloud migration", "data modernisation", "ai adoption", "platform modernisation"}


def clamp_score(value: float) -> int:
    """Round and clamp a score into the inclusive 0-100 range."""

    return max(0, min(100, round(value)))


def calculate_scores(account: TargetAccount, signals: list[Signal], dna: CommercialDNA) -> ReinventionScores:
    """Calculate deterministic AI reinvention scores for a target account."""

    if not signals:
        priority_base = {"high": 55, "medium": 40, "low": 25}[account.priority.value]
        return ReinventionScores(
            commercial_pressure_index=priority_base,
            ai_suitability_index=35,
            organisational_readiness_index=30,
            commercial_attractiveness_index=priority_base,
            influence_potential_index=30,
            ai_reinvention_opportunity_score=clamp_score((priority_base + 35 + 30 + priority_base + 30) / 5),
        )

    avg_strength = sum(signal.strength for signal in signals) / len(signals)
    avg_confidence = sum(signal.confidence for signal in signals) / len(signals)
    avg_freshness = sum(signal.freshness for signal in signals) / len(signals)
    categories = {signal.signal_category.lower() for signal in signals}
    capabilities = {capability for signal in signals for capability in signal.related_capabilities}

    pressure = clamp_score(avg_strength * 0.55 + avg_freshness * 0.25 + 8 * len(categories & PRESSURE_CATEGORIES))
    ai_suitability = clamp_score(avg_confidence * 0.35 + avg_strength * 0.25 + 7 * len(capabilities) + 6 * len(categories & AI_CATEGORIES))
    readiness = clamp_score(avg_confidence * 0.35 + avg_freshness * 0.25 + 8 * len(categories & READINESS_CATEGORIES))

    priority_weight = {"high": 18, "medium": 10, "low": 4}[account.priority.value]
    sector_fit = 12 if account.sector in dna.sectors else 4
    commercial_attractiveness = clamp_score(avg_strength * 0.35 + priority_weight + sector_fit + 3 * len(account.known_incumbents))

    competitor_overlap = set(account.known_competitors) & set(dna.competitors)
    incumbent_opening = 8 if account.known_incumbents else 2
    influence_potential = clamp_score(avg_confidence * 0.25 + avg_freshness * 0.2 + incumbent_opening + 5 * len(competitor_overlap) + 3 * len(dna.differentiators))

    opportunity = clamp_score(
        pressure * 0.25
        + ai_suitability * 0.25
        + readiness * 0.15
        + commercial_attractiveness * 0.2
        + influence_potential * 0.15
    )

    return ReinventionScores(
        commercial_pressure_index=pressure,
        ai_suitability_index=ai_suitability,
        organisational_readiness_index=readiness,
        commercial_attractiveness_index=commercial_attractiveness,
        influence_potential_index=influence_potential,
        ai_reinvention_opportunity_score=opportunity,
    )


def strongest_signals(signals: list[Signal], limit: int = 3) -> list[Signal]:
    """Return strongest signals by strength, confidence and freshness."""

    return sorted(signals, key=lambda signal: (signal.strength, signal.confidence, signal.freshness), reverse=True)[:limit]


def top_capabilities(signals: list[Signal], limit: int = 4) -> list[str]:
    """Return the most frequent related capabilities across signals."""

    counts = Counter(capability for signal in signals for capability in signal.related_capabilities)
    return [capability for capability, _ in counts.most_common(limit)]
