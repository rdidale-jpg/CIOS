"""Decision policy for the Opportunity Assistant."""

from __future__ import annotations

from typing import Any

from cios.core import ConfidenceLevel, DecisionStatus, Evidence, Observation, Recommendation
from cios.decision_engine import DecisionAssessment, DecisionCriteria, DecisionInput, DecisionOption, DecisionOutput, DecisionRationale
from cios.graph import KnowledgeGraphRecord

from cios.applications.opportunity_assistant.reasoning_mapping import OpportunityReasoningResult
from cios.applications.opportunity_assistant.scoring_policy import OpportunityScoringResult


def create_decision(
    source: dict[str, Any],
    graph: KnowledgeGraphRecord,
    evidence: list[Evidence],
    observations: list[Observation],
    reasoning: OpportunityReasoningResult,
    scoring: OpportunityScoringResult,
) -> DecisionOutput:
    """Create the deterministic qualification decision."""

    input_bundle = DecisionInput(
        name=f"{source['name']} Decision Input",
        question="Should this opportunity be qualified for active pursuit?",
        graph_records=[graph],
        reasoning_traces=[reasoning.trace],
        reasoning_results=[reasoning.result],
        scoring_results=[scoring.result],
        evidence=evidence,
        observations=observations,
    )
    option = DecisionOption(
        title="Qualify for active pursuit",
        description="Proceed with capture planning focused on transformation, security, managed service operations, and differentiation.",
        actions=[
            "Build an Oracle transformation win theme.",
            "Validate security accreditation evidence.",
            "Prepare managed-service operating model proof points.",
            "Create competitor differentiation plan.",
        ],
        evidence_ids=[item.id for item in evidence],
    )
    criteria = [DecisionCriteria(name="Commercial attractiveness", weight=0.4), DecisionCriteria(name="Strategic fit", weight=0.3), DecisionCriteria(name="Delivery confidence", weight=0.3)]
    assessment = DecisionAssessment(
        option_id=option.id,
        overall_score=scoring.result.overall_score,
        rationale="The deterministic vertical slice score supports active pursuit with explicit risk management.",
        evidence_ids=[item.id for item in evidence],
        reasoning_trace_ids=[reasoning.trace.id],
        scoring_result_ids=[scoring.result.id],
    )
    rationale = DecisionRationale(
        summary="Qualify because the opportunity combines high value, Oracle transformation pressure, security criticality, managed-service fit, long-term contract potential, and known competitive intensity.",
        evidence_ids=[item.id for item in evidence],
        reasoning_trace_ids=[reasoning.trace.id],
        reasoning_result_ids=[reasoning.result.id],
        score_ids=[scoring.result.overall_score.id],
        scoring_result_ids=[scoring.result.id],
        confidence=ConfidenceLevel.HIGH,
    )
    recommendation = Recommendation(title="Qualify opportunity with focused capture plan", rationale=rationale.summary, actions=option.actions, evidence_ids=[item.id for item in evidence])
    return DecisionOutput(
        title="Opportunity qualification decision",
        input_id=input_bundle.id,
        selected_option_id=option.id,
        status=DecisionStatus.APPROVED,
        options=[option],
        criteria=criteria,
        assessments=[assessment],
        rationales=[rationale],
        recommendations=[recommendation],
        confidence=ConfidenceLevel.HIGH,
        outcome="selected",
        metadata={"decision_input": input_bundle.model_dump()},
    )
