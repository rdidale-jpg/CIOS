"""Scoring policy for the Opportunity Assistant."""

from __future__ import annotations


from cios.core import Evidence
from cios.core.models import CIOSBaseModel
from cios.reasoning import ReasoningTrace
from cios.scoring import Score, ScoreBand, ScoreComponent, ScoringModel, ScoringResult, TransformationPressureScore

from cios.applications.opportunity_assistant.rules import (
    HIGH_VALUE_RULE_ID,
    LONG_TERM_CONTRACT_RULE_ID,
    ORACLE_TRANSFORMATION_RULE_ID,
    SECURITY_CRITICAL_RULE_ID,
    RuleMatch,
)


class OpportunityScoringResult(CIOSBaseModel):
    """Typed scoring artefacts created by the active scoring policy."""

    result: ScoringResult
    transformation_pressure: TransformationPressureScore


def create_scoring(rule_matches: list[RuleMatch], trace: ReasoningTrace, evidence: list[Evidence]) -> OpportunityScoringResult:
    """Create scoring artefacts from rule matches using the active deterministic policy."""

    components = [
        ScoreComponent(
            name=rule.name,
            score=Score(
                name=rule.name,
                value=rule.score,
                rationale=rule.rationale,
                evidence_ids=[item.id for item in evidence],
                metadata={"rule": rule.name, "rule_id": rule.rule_id},
            ),
            weight=1.0,
            rationale=rule.rationale,
            metadata={"rule": rule.name, "rule_id": rule.rule_id, "matched": rule.matched},
        )
        for rule in rule_matches
    ]
    overall_value = round(sum(component.score.value for component in components) / len(components), 2)
    bands = [ScoreBand(name="Low", minimum=0, maximum=49), ScoreBand(name="Medium", minimum=50, maximum=74), ScoreBand(name="High", minimum=75, maximum=100)]
    band = next(item for item in bands if item.minimum <= overall_value <= item.maximum)
    model = ScoringModel(name="Sprint 7A Deterministic Opportunity Score", version="0.1.0", bands=bands)
    result = ScoringResult(
        scoring_model=model,
        overall_score=Score(name="Overall Opportunity Score", value=overall_value, rationale="Average of deterministic Sprint 7A rule components."),
        components=components,
        band=band,
        reasoning_trace=trace,
    )
    components_by_rule_id = {component.metadata["rule_id"]: component for component in components}
    return OpportunityScoringResult(
        result=result,
        transformation_pressure=TransformationPressureScore(
            result=result,
            urgency_score=components_by_rule_id[LONG_TERM_CONTRACT_RULE_ID].score,
            strategic_importance_score=components_by_rule_id[HIGH_VALUE_RULE_ID].score,
            change_pressure_score=components_by_rule_id[ORACLE_TRANSFORMATION_RULE_ID].score,
            capability_gap_score=components_by_rule_id[SECURITY_CRITICAL_RULE_ID].score,
        ),
    )
