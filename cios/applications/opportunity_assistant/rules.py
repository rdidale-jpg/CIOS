"""Deterministic commercial rules for the Sprint 7A vertical slice."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RuleMatch:
    """A deterministic commercial rule result."""

    name: str
    matched: bool
    observation: str
    signal_name: str
    signal_strength: str
    score: float
    rationale: str


HIGH_VALUE_THRESHOLD = 10_000_000
LONG_TERM_MONTHS = 36
MULTI_COMPETITOR_COUNT = 3


def evaluate_rules(opportunity: dict[str, Any]) -> list[RuleMatch]:
    """Evaluate the minimal Sprint 7A commercial rule set."""

    value = float(opportunity.get("value") or 0)
    duration_months = int(opportunity.get("duration_months") or 0)
    competitors = opportunity.get("competitors", [])
    text = " ".join(
        [
            opportunity.get("description", ""),
            " ".join(opportunity.get("current_platforms", [])),
            " ".join(opportunity.get("requirements", [])),
            " ".join(opportunity.get("capabilities", [])),
        ]
    ).lower()

    return [
        RuleMatch(
            name="High Value Opportunity",
            matched=value >= HIGH_VALUE_THRESHOLD,
            observation=f"Opportunity value is {value:,.0f}.",
            signal_name="High commercial value",
            signal_strength="high" if value >= HIGH_VALUE_THRESHOLD else "low",
            score=90 if value >= HIGH_VALUE_THRESHOLD else 35,
            rationale=f"Value meets the {HIGH_VALUE_THRESHOLD:,.0f} high-value threshold."
            if value >= HIGH_VALUE_THRESHOLD
            else f"Value is below the {HIGH_VALUE_THRESHOLD:,.0f} high-value threshold.",
        ),
        RuleMatch(
            name="Oracle Transformation",
            matched="oracle" in text and any(term in text for term in ["modernisation", "modernization", "migration", "transformation"]),
            observation="Opportunity references Oracle and transformation or migration context.",
            signal_name="Oracle transformation pressure",
            signal_strength="high" if "oracle" in text else "low",
            score=85 if "oracle" in text else 20,
            rationale="Oracle estate modernisation creates a clear transformation narrative."
            if "oracle" in text
            else "No Oracle transformation driver detected.",
        ),
        RuleMatch(
            name="Security Critical",
            matched=any(term in text for term in ["security", "secure", "accreditation", "data protection"]),
            observation="Security, accreditation, or data protection requirements are present.",
            signal_name="Security criticality",
            signal_strength="high" if "security" in text or "secure" in text else "medium",
            score=80 if any(term in text for term in ["security", "secure", "accreditation", "data protection"]) else 25,
            rationale="Security requirements increase delivery scrutiny and confidence requirements.",
        ),
        RuleMatch(
            name="Managed Service",
            matched="managed service" in text or "24/7" in text,
            observation="Managed service or 24/7 operating model is required.",
            signal_name="Managed service fit",
            signal_strength="high" if "managed service" in text or "24/7" in text else "low",
            score=75 if "managed service" in text or "24/7" in text else 30,
            rationale="Managed service requirements support a lifecycle-led commercial position.",
        ),
        RuleMatch(
            name="Long-Term Contract",
            matched=duration_months >= LONG_TERM_MONTHS,
            observation=f"Contract duration is {duration_months} months.",
            signal_name="Long-term contract potential",
            signal_strength="high" if duration_months >= LONG_TERM_MONTHS else "low",
            score=70 if duration_months >= LONG_TERM_MONTHS else 30,
            rationale=f"Duration meets the {LONG_TERM_MONTHS}-month long-term contract threshold."
            if duration_months >= LONG_TERM_MONTHS
            else f"Duration is below the {LONG_TERM_MONTHS}-month long-term threshold.",
        ),
        RuleMatch(
            name="Multi-Competitor",
            matched=len(competitors) >= MULTI_COMPETITOR_COUNT,
            observation=f"{len(competitors)} named competitors are present.",
            signal_name="Competitive intensity",
            signal_strength="high" if len(competitors) >= MULTI_COMPETITOR_COUNT else "medium",
            score=65 if len(competitors) >= MULTI_COMPETITOR_COUNT else 40,
            rationale="Multiple competitors require explicit differentiation and capture discipline.",
        ),
    ]
