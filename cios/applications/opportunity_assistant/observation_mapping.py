"""Observation mapping for the Opportunity Assistant."""

from __future__ import annotations

from cios.core import ConfidenceLevel, Evidence, Observation

from cios.applications.opportunity_assistant.scoring_policy import RuleMatch


def create_observations(
    rule_matches: list[RuleMatch], evidence: list[Evidence]
) -> list[Observation]:
    """Map scored rule outcomes into core observations."""

    evidence_ids = [item.id for item in evidence]
    return [
        Observation(
            statement=rule.observation,
            evidence_ids=evidence_ids,
            confidence=ConfidenceLevel.HIGH if rule.matched else ConfidenceLevel.MEDIUM,
            metadata={"rule": rule.name, "rule_id": rule.rule_id},
        )
        for rule in rule_matches
    ]
