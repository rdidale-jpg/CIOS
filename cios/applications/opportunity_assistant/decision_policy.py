"""Decision policy for the Opportunity Assistant."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from cios.core import ConfidenceLevel, DecisionStatus, Evidence, Observation, Recommendation
from cios.core.models import CIOSBaseModel
from cios.decision_engine import DecisionAssessment, DecisionCriteria, DecisionInput, DecisionOption, DecisionOutput, DecisionRationale
from cios.graph import KnowledgeGraphRecord

from cios.applications.opportunity_assistant.reasoning_mapping import OpportunityReasoningResult
from cios.applications.opportunity_assistant.scoring_policy import OpportunityScoringResult


class OpportunityDecisionPolicy(CIOSBaseModel):
    """Inspectable deterministic decision policy for Opportunity Assistant runs."""

    question: str = "Should this opportunity be qualified for active pursuit?"
    option_title: str = "Qualify for active pursuit"
    option_description: str = "Proceed with capture planning focused on transformation, security, managed service operations, and differentiation."
    option_actions: list[str] = Field(
        default_factory=lambda: [
            "Build an Oracle transformation win theme.",
            "Validate security accreditation evidence.",
            "Prepare managed-service operating model proof points.",
            "Create competitor differentiation plan.",
        ]
    )
    criteria: list[DecisionCriteria] = Field(
        default_factory=lambda: [
            DecisionCriteria(name="Commercial attractiveness", weight=0.4),
            DecisionCriteria(name="Strategic fit", weight=0.3),
            DecisionCriteria(name="Delivery confidence", weight=0.3),
        ]
    )
    assessment_rationale: str = "The deterministic vertical slice score supports active pursuit with explicit risk management."
    rationale_summary: str = (
        "Qualify because the opportunity combines high value, Oracle transformation pressure, security criticality, "
        "managed-service fit, long-term contract potential, and known competitive intensity."
    )
    recommendation_title: str = "Qualify opportunity with focused capture plan"
    decision_title: str = "Opportunity qualification decision"
    status: DecisionStatus = DecisionStatus.APPROVED
    confidence: ConfidenceLevel = ConfidenceLevel.HIGH
    outcome: str = "selected"

    def decide(
        self,
        source: dict[str, Any],
        graph: KnowledgeGraphRecord,
        evidence: list[Evidence],
        observations: list[Observation],
        reasoning: OpportunityReasoningResult,
        scoring: OpportunityScoringResult,
    ) -> DecisionOutput:
        """Create the deterministic qualification decision using this policy."""

        evidence_ids = [item.id for item in evidence]
        input_bundle = self._create_input(source, graph, evidence, observations, reasoning, scoring)
        option = DecisionOption(
            title=self.option_title,
            description=self.option_description,
            actions=self.option_actions,
            evidence_ids=evidence_ids,
        )
        assessment = DecisionAssessment(
            option_id=option.id,
            overall_score=scoring.result.overall_score,
            rationale=self.assessment_rationale,
            evidence_ids=evidence_ids,
            reasoning_trace_ids=[reasoning.trace.id],
            scoring_result_ids=[scoring.result.id],
        )
        rationale = DecisionRationale(
            summary=self.rationale_summary,
            evidence_ids=evidence_ids,
            reasoning_trace_ids=[reasoning.trace.id],
            reasoning_result_ids=[reasoning.result.id],
            score_ids=[scoring.result.overall_score.id],
            scoring_result_ids=[scoring.result.id],
            confidence=self.confidence,
        )
        recommendation = Recommendation(title=self.recommendation_title, rationale=rationale.summary, actions=option.actions, evidence_ids=evidence_ids)
        return DecisionOutput(
            title=self.decision_title,
            input_id=input_bundle.id,
            selected_option_id=option.id,
            status=self.status,
            options=[option],
            criteria=self.criteria,
            assessments=[assessment],
            rationales=[rationale],
            recommendations=[recommendation],
            confidence=self.confidence,
            outcome=self.outcome,
            metadata={"decision_input": input_bundle.model_dump()},
        )

    def _create_input(
        self,
        source: dict[str, Any],
        graph: KnowledgeGraphRecord,
        evidence: list[Evidence],
        observations: list[Observation],
        reasoning: OpportunityReasoningResult,
        scoring: OpportunityScoringResult,
    ) -> DecisionInput:
        return DecisionInput(
            name=f"{source['name']} Decision Input",
            question=self.question,
            graph_records=[graph],
            reasoning_traces=[reasoning.trace],
            reasoning_results=[reasoning.result],
            scoring_results=[scoring.result],
            evidence=evidence,
            observations=observations,
        )


DEFAULT_DECISION_POLICY = OpportunityDecisionPolicy()


def create_decision(
    source: dict[str, Any],
    graph: KnowledgeGraphRecord,
    evidence: list[Evidence],
    observations: list[Observation],
    reasoning: OpportunityReasoningResult,
    scoring: OpportunityScoringResult,
) -> DecisionOutput:
    """Create the deterministic qualification decision."""

    return DEFAULT_DECISION_POLICY.decide(source, graph, evidence, observations, reasoning, scoring)
