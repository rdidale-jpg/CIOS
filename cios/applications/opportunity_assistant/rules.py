"""Deterministic commercial rules for the Sprint 7A vertical slice."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RuleDetection:
    """A deterministic commercial rule detection without scoring policy."""

    name: str
    matched: bool
    observation: str
    signal_name: str
    signal_strength: str
    matched_rationale: str
    absent_rationale: str

    @property
    def rationale(self) -> str:
        """Return the rationale that corresponds to the detection outcome."""

        return self.matched_rationale if self.matched else self.absent_rationale


@dataclass(frozen=True)
class RuleScore:
    """Scoring policy assigned to a detected rule outcome."""

    matched_score: float
    absent_score: float


@dataclass(frozen=True)
class RuleMatch:
    """Backward-compatible rule result with detection and score."""

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

DEFAULT_SCORING_POLICY: dict[str, RuleScore] = {
    "High Value Opportunity": RuleScore(matched_score=90, absent_score=35),
    "Oracle Transformation": RuleScore(matched_score=85, absent_score=20),
    "Security Critical": RuleScore(matched_score=80, absent_score=25),
    "Managed Service": RuleScore(matched_score=75, absent_score=30),
    "Long-Term Contract": RuleScore(matched_score=70, absent_score=30),
    "Multi-Competitor": RuleScore(matched_score=65, absent_score=40),
}


def detect_rules(opportunity: dict[str, Any]) -> list[RuleDetection]:
    """Detect the minimal Sprint 7A commercial rule conditions without scoring."""

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
    has_oracle_transformation = "oracle" in text and any(term in text for term in ["modernisation", "modernization", "migration", "transformation"])
    has_security = any(term in text for term in ["security", "secure", "accreditation", "data protection"])
    has_managed_service = "managed service" in text or "24/7" in text

    return [
        RuleDetection(
            name="High Value Opportunity",
            matched=value >= HIGH_VALUE_THRESHOLD,
            observation=f"Opportunity value is {value:,.0f}.",
            signal_name="High commercial value",
            signal_strength="high" if value >= HIGH_VALUE_THRESHOLD else "low",
            matched_rationale=f"Value meets the {HIGH_VALUE_THRESHOLD:,.0f} high-value threshold.",
            absent_rationale=f"Value is below the {HIGH_VALUE_THRESHOLD:,.0f} high-value threshold.",
        ),
        RuleDetection(
            name="Oracle Transformation",
            matched=has_oracle_transformation,
            observation="Opportunity references Oracle and transformation or migration context.",
            signal_name="Oracle transformation pressure",
            signal_strength="high" if has_oracle_transformation else "low",
            matched_rationale="Oracle estate modernisation creates a clear transformation narrative.",
            absent_rationale="No Oracle transformation driver detected.",
        ),
        RuleDetection(
            name="Security Critical",
            matched=has_security,
            observation="Security, accreditation, or data protection requirements are present.",
            signal_name="Security criticality",
            signal_strength="high" if has_security else "low",
            matched_rationale="Security requirements increase delivery scrutiny and confidence requirements.",
            absent_rationale="No security, accreditation, or data protection requirement detected.",
        ),
        RuleDetection(
            name="Managed Service",
            matched=has_managed_service,
            observation="Managed service or 24/7 operating model is required.",
            signal_name="Managed service fit",
            signal_strength="high" if has_managed_service else "low",
            matched_rationale="Managed service requirements support a lifecycle-led commercial position.",
            absent_rationale="No managed service or 24/7 operating model requirement detected.",
        ),
        RuleDetection(
            name="Long-Term Contract",
            matched=duration_months >= LONG_TERM_MONTHS,
            observation=f"Contract duration is {duration_months} months.",
            signal_name="Long-term contract potential",
            signal_strength="high" if duration_months >= LONG_TERM_MONTHS else "low",
            matched_rationale=f"Duration meets the {LONG_TERM_MONTHS}-month long-term contract threshold.",
            absent_rationale=f"Duration is below the {LONG_TERM_MONTHS}-month long-term threshold.",
        ),
        RuleDetection(
            name="Multi-Competitor",
            matched=len(competitors) >= MULTI_COMPETITOR_COUNT,
            observation=f"{len(competitors)} named competitors are present.",
            signal_name="Competitive intensity",
            signal_strength="high" if len(competitors) >= MULTI_COMPETITOR_COUNT else "low",
            matched_rationale="Multiple competitors require explicit differentiation and capture discipline.",
            absent_rationale="Fewer than three named competitors are present.",
        ),
    ]


def score_rule_detections(detections: list[RuleDetection], policy: dict[str, RuleScore] | None = None) -> list[RuleMatch]:
    """Apply a scoring policy to rule detections."""

    active_policy = policy or DEFAULT_SCORING_POLICY
    return [
        RuleMatch(
            name=detection.name,
            matched=detection.matched,
            observation=detection.observation,
            signal_name=detection.signal_name,
            signal_strength=detection.signal_strength,
            score=active_policy[detection.name].matched_score if detection.matched else active_policy[detection.name].absent_score,
            rationale=detection.rationale,
        )
        for detection in detections
    ]


def evaluate_rules(opportunity: dict[str, Any]) -> list[RuleMatch]:
    """Evaluate rules with the default Sprint 7A scoring policy."""

    return score_rule_detections(detect_rules(opportunity))
