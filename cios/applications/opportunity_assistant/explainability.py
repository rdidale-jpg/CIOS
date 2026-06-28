"""Explainability reporting models and mapping for the Opportunity Assistant."""

from __future__ import annotations

from pydantic import Field

from cios.core import ConfidenceLevel, Evidence, Observation
from cios.core.models import CIOSBaseModel
from cios.decision_engine import DecisionOutput

from cios.applications.opportunity_assistant.ontology_mapping import (
    OpportunityOntologyResult,
)
from cios.applications.opportunity_assistant.reasoning_mapping import (
    OpportunityReasoningResult,
)
from cios.applications.opportunity_assistant.scoring_policy import RuleMatch
from cios.applications.opportunity_assistant.scoring_policy import (
    OpportunityScoringResult,
)


class RecommendationExplainability(CIOSBaseModel):
    """Machine-readable explanation for a single recommendation."""

    recommendation_id: str
    recommendation_title: str
    supporting_observation_ids: list[str] = Field(default_factory=list)
    supporting_observations: list[str] = Field(default_factory=list)
    triggered_rules: list[str] = Field(default_factory=list)
    triggered_rule_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    score_ids: list[str] = Field(default_factory=list)
    scores_used: dict[str, float] = Field(default_factory=dict)
    reasoning_trace_ids: list[str] = Field(default_factory=list)
    reasoning_step_ids: list[str] = Field(default_factory=list)
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM


class OpportunityExplainabilityReport(CIOSBaseModel):
    """Structured report linking recommendations back to evidence, rules, scores, and reasoning."""

    opportunity_id: str
    decision_id: str
    recommendation_explanations: list[RecommendationExplainability] = Field(
        default_factory=list
    )


def create_explainability_report(
    ontology: OpportunityOntologyResult,
    evidence: list[Evidence],
    rule_matches: list[RuleMatch],
    observations: list[Observation],
    reasoning: OpportunityReasoningResult,
    scoring: OpportunityScoringResult,
    decision: DecisionOutput,
) -> OpportunityExplainabilityReport:
    """Create recommendation explainability links for evidence, rules, scores, and reasoning."""

    matched_rule_ids = [rule.rule_id for rule in rule_matches if rule.matched]
    supporting_rule_ids = matched_rule_ids or [rule.rule_id for rule in rule_matches]
    observations_by_rule_id = {
        observation.metadata["rule_id"]: observation for observation in observations
    }
    components_by_rule_id = {
        component.metadata["rule_id"]: component
        for component in scoring.result.components
    }
    reasoning_steps_by_rule_id = {
        step.metadata["rule_id"]: step for step in reasoning.trace.steps
    }
    supporting_observations = [
        observations_by_rule_id[rule_id] for rule_id in supporting_rule_ids
    ]
    supporting_components = [
        components_by_rule_id[rule_id] for rule_id in supporting_rule_ids
    ]
    reasoning_steps = [
        reasoning_steps_by_rule_id[rule_id] for rule_id in supporting_rule_ids
    ]

    explanations = [
        RecommendationExplainability(
            recommendation_id=recommendation.id,
            recommendation_title=recommendation.title,
            supporting_observation_ids=[
                observation.id for observation in supporting_observations
            ],
            supporting_observations=[
                observation.statement for observation in supporting_observations
            ],
            triggered_rules=[rule.name for rule in rule_matches if rule.matched],
            triggered_rule_ids=matched_rule_ids,
            evidence_ids=sorted(
                {evidence_id for item in evidence for evidence_id in [item.id]}
            ),
            score_ids=[component.score.id for component in supporting_components]
            + [scoring.result.overall_score.id],
            scores_used={
                component.name: component.score.value
                for component in supporting_components
            }
            | {scoring.result.overall_score.name: scoring.result.overall_score.value},
            reasoning_trace_ids=[reasoning.trace.id],
            reasoning_step_ids=[step.id for step in reasoning_steps],
            confidence=decision.confidence,
        )
        for recommendation in decision.recommendations
    ]

    return OpportunityExplainabilityReport(
        opportunity_id=ontology.opportunity.id,
        decision_id=decision.id,
        recommendation_explanations=explanations,
    )
