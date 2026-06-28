"""Scoring policy for the Opportunity Assistant."""

from __future__ import annotations

from pydantic import Field

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


class TransformationPressureMapping(CIOSBaseModel):
    """Rule IDs used to expose the transformation-pressure score dimensions."""

    urgency_rule_id: str = LONG_TERM_CONTRACT_RULE_ID
    strategic_importance_rule_id: str = HIGH_VALUE_RULE_ID
    change_pressure_rule_id: str = ORACLE_TRANSFORMATION_RULE_ID
    capability_gap_rule_id: str = SECURITY_CRITICAL_RULE_ID


class OpportunityScoringPolicy(CIOSBaseModel):
    """Inspectable deterministic scoring policy for Opportunity Assistant runs."""

    model_name: str = "Sprint 7A Deterministic Opportunity Score"
    model_version: str = "0.1.0"
    overall_score_name: str = "Overall Opportunity Score"
    overall_score_rationale: str = "Average of deterministic Sprint 7A rule components."
    component_weight: float = 1.0
    bands: list[ScoreBand] = Field(
        default_factory=lambda: [
            ScoreBand(name="Low", minimum=0, maximum=49),
            ScoreBand(name="Medium", minimum=50, maximum=74),
            ScoreBand(name="High", minimum=75, maximum=100),
        ]
    )
    transformation_pressure_mapping: TransformationPressureMapping = Field(default_factory=TransformationPressureMapping)

    def score(self, rule_matches: list[RuleMatch], trace: ReasoningTrace, evidence: list[Evidence]) -> OpportunityScoringResult:
        """Create scoring artefacts from rule matches using this policy."""

        evidence_ids = [item.id for item in evidence]
        components = [self._create_component(rule, evidence_ids) for rule in rule_matches]
        overall_value = round(sum(component.score.value for component in components) / len(components), 2)
        band = self.band_for(overall_value)
        model = ScoringModel(name=self.model_name, version=self.model_version, bands=self.bands)
        result = ScoringResult(
            scoring_model=model,
            overall_score=Score(name=self.overall_score_name, value=overall_value, rationale=self.overall_score_rationale),
            components=components,
            band=band,
            reasoning_trace=trace,
        )
        return OpportunityScoringResult(
            result=result,
            transformation_pressure=self._create_transformation_pressure(result, components),
        )

    def band_for(self, score_value: float) -> ScoreBand:
        """Return the configured band that contains the provided score."""

        return next(item for item in self.bands if item.minimum <= score_value <= item.maximum)

    def _create_component(self, rule: RuleMatch, evidence_ids: list[str]) -> ScoreComponent:
        metadata = {"rule": rule.name, "rule_id": rule.rule_id}
        return ScoreComponent(
            name=rule.name,
            score=Score(
                name=rule.name,
                value=rule.score,
                rationale=rule.rationale,
                evidence_ids=evidence_ids,
                metadata=metadata,
            ),
            weight=self.component_weight,
            rationale=rule.rationale,
            metadata={**metadata, "matched": rule.matched},
        )

    def _create_transformation_pressure(
        self,
        result: ScoringResult,
        components: list[ScoreComponent],
    ) -> TransformationPressureScore:
        components_by_rule_id = {component.metadata["rule_id"]: component for component in components}
        mapping = self.transformation_pressure_mapping
        return TransformationPressureScore(
            result=result,
            urgency_score=components_by_rule_id[mapping.urgency_rule_id].score,
            strategic_importance_score=components_by_rule_id[mapping.strategic_importance_rule_id].score,
            change_pressure_score=components_by_rule_id[mapping.change_pressure_rule_id].score,
            capability_gap_score=components_by_rule_id[mapping.capability_gap_rule_id].score,
        )


DEFAULT_SCORING_POLICY = OpportunityScoringPolicy()


def create_scoring(rule_matches: list[RuleMatch], trace: ReasoningTrace, evidence: list[Evidence]) -> OpportunityScoringResult:
    """Create scoring artefacts from rule matches using the active deterministic policy."""

    return DEFAULT_SCORING_POLICY.score(rule_matches, trace, evidence)
