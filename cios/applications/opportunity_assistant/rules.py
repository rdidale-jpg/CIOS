"""Deterministic commercial rule detection for the Sprint 7A vertical slice."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RuleDetection:
    """A deterministic commercial rule detection without scoring policy."""

    rule_id: str
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


HIGH_VALUE_THRESHOLD = 10_000_000
LONG_TERM_MONTHS = 36
MULTI_COMPETITOR_COUNT = 3

HIGH_VALUE_RULE_ID = "oa.rule.high_value_opportunity"
ORACLE_TRANSFORMATION_RULE_ID = "oa.rule.oracle_transformation"
SECURITY_CRITICAL_RULE_ID = "oa.rule.security_critical"
MANAGED_SERVICE_RULE_ID = "oa.rule.managed_service"
LONG_TERM_CONTRACT_RULE_ID = "oa.rule.long_term_contract"
MULTI_COMPETITOR_RULE_ID = "oa.rule.multi_competitor"


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
    has_oracle_transformation = "oracle" in text and any(
        term in text
        for term in ["modernisation", "modernization", "migration", "transformation"]
    )
    has_security = any(
        term in text
        for term in ["security", "secure", "accreditation", "data protection"]
    )
    has_managed_service = "managed service" in text or "24/7" in text

    return [
        RuleDetection(
            rule_id=HIGH_VALUE_RULE_ID,
            name="High Value Opportunity",
            matched=value >= HIGH_VALUE_THRESHOLD,
            observation=f"Opportunity value is {value:,.0f}.",
            signal_name="High commercial value",
            signal_strength="high" if value >= HIGH_VALUE_THRESHOLD else "low",
            matched_rationale=f"Value meets the {HIGH_VALUE_THRESHOLD:,.0f} high-value threshold.",
            absent_rationale=f"Value is below the {HIGH_VALUE_THRESHOLD:,.0f} high-value threshold.",
        ),
        RuleDetection(
            rule_id=ORACLE_TRANSFORMATION_RULE_ID,
            name="Oracle Transformation",
            matched=has_oracle_transformation,
            observation="Opportunity references Oracle and transformation or migration context.",
            signal_name="Oracle transformation pressure",
            signal_strength="high" if has_oracle_transformation else "low",
            matched_rationale="Oracle estate modernisation creates a clear transformation narrative.",
            absent_rationale="No Oracle transformation driver detected.",
        ),
        RuleDetection(
            rule_id=SECURITY_CRITICAL_RULE_ID,
            name="Security Critical",
            matched=has_security,
            observation="Security, accreditation, or data protection requirements are present.",
            signal_name="Security criticality",
            signal_strength="high" if has_security else "low",
            matched_rationale="Security requirements increase delivery scrutiny and confidence requirements.",
            absent_rationale="No security, accreditation, or data protection requirement detected.",
        ),
        RuleDetection(
            rule_id=MANAGED_SERVICE_RULE_ID,
            name="Managed Service",
            matched=has_managed_service,
            observation="Managed service or 24/7 operating model is required.",
            signal_name="Managed service fit",
            signal_strength="high" if has_managed_service else "low",
            matched_rationale="Managed service requirements support a lifecycle-led commercial position.",
            absent_rationale="No managed service or 24/7 operating model requirement detected.",
        ),
        RuleDetection(
            rule_id=LONG_TERM_CONTRACT_RULE_ID,
            name="Long-Term Contract",
            matched=duration_months >= LONG_TERM_MONTHS,
            observation=f"Contract duration is {duration_months} months.",
            signal_name="Long-term contract potential",
            signal_strength="high" if duration_months >= LONG_TERM_MONTHS else "low",
            matched_rationale=f"Duration meets the {LONG_TERM_MONTHS}-month long-term contract threshold.",
            absent_rationale=f"Duration is below the {LONG_TERM_MONTHS}-month long-term threshold.",
        ),
        RuleDetection(
            rule_id=MULTI_COMPETITOR_RULE_ID,
            name="Multi-Competitor",
            matched=len(competitors) >= MULTI_COMPETITOR_COUNT,
            observation=f"{len(competitors)} named competitors are present.",
            signal_name="Competitive intensity",
            signal_strength=(
                "high" if len(competitors) >= MULTI_COMPETITOR_COUNT else "low"
            ),
            matched_rationale="Multiple competitors require explicit differentiation and capture discipline.",
            absent_rationale="Fewer than three named competitors are present.",
        ),
    ]
