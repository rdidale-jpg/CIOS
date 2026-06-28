"""Passive agent adapter for Opportunity Assistant pipeline artefacts."""

from __future__ import annotations

from cios.agents import (
    AgentFinding,
    AgentOutput,
    AgentRecommendation,
    AgentRole,
    AgentTrace,
)
from cios.applications.opportunity_assistant.pipeline import OpportunityPipelineResult


class OpportunityAssessmentAgent:
    """Summarize an existing Opportunity Assistant result as agent output.

    The adapter is intentionally passive: it consumes a completed
    :class:`OpportunityPipelineResult` and maps existing evidence, rule,
    reasoning, score, decision, and explainability artefacts into the shared
    agent contract. It does not execute the pipeline, call memory, persist
    records, invoke LLMs, or create decisions outside the configured policy.
    """

    role: AgentRole = AgentRole.EXPLAINABILITY_ASSISTANT

    def assess(self, result: OpportunityPipelineResult) -> AgentOutput:
        """Return a deterministic agent-facing summary of a pipeline result."""

        evidence_ids = [item.id for item in result.evidence]
        observation_ids = [item.id for item in result.observations]
        rule_ids = [rule.rule_id for rule in result.rule_matches]
        reasoning_trace_ids = [result.reasoning.trace.id]
        score_ids = [
            component.score.id for component in result.scoring.result.components
        ]
        score_ids.append(result.scoring.result.overall_score.id)
        decision_ids = [result.decision.id]
        recommendation_ids = [item.id for item in result.decision.recommendations]
        matched_rules = [rule.name for rule in result.rule_matches if rule.matched]

        findings = [
            AgentFinding(
                title="Opportunity assessment score",
                statement=(
                    f"The existing scoring result places the opportunity in the "
                    f"{result.scoring.result.band.name} band with an overall score "
                    f"of {result.scoring.result.overall_score.value}."
                ),
                confidence=result.decision.confidence,
                evidence_ids=evidence_ids,
                observation_ids=observation_ids,
                reasoning_trace_ids=reasoning_trace_ids,
                score_ids=score_ids,
                rule_ids=rule_ids,
                metadata={
                    "decision_id": result.decision.id,
                    "scoring_result_id": result.scoring.result.id,
                    "reasoning_result_id": result.reasoning.result.id,
                    "matched_rule_count": len(matched_rules),
                },
            ),
            AgentFinding(
                title="Decision policy outcome",
                statement=(
                    f"The existing decision policy outcome is {result.decision.outcome} "
                    f"with {result.decision.confidence} confidence."
                ),
                confidence=result.decision.confidence,
                evidence_ids=evidence_ids,
                observation_ids=observation_ids,
                reasoning_trace_ids=reasoning_trace_ids,
                score_ids=[result.scoring.result.overall_score.id],
                rule_ids=rule_ids,
                metadata={
                    "decision_id": result.decision.id,
                    "decision_status": str(result.decision.status),
                    "recommendation_ids": recommendation_ids,
                },
            ),
        ]

        recommendations = [
            AgentRecommendation(
                title=recommendation.title,
                rationale=recommendation.rationale,
                recommendation_type="explanation",
                evidence_ids=recommendation.evidence_ids,
                observation_ids=explanation.supporting_observation_ids,
                reasoning_trace_ids=explanation.reasoning_trace_ids,
                score_ids=explanation.score_ids,
                decision_ids=decision_ids,
                recommendation_ids=[recommendation.id],
                rule_ids=explanation.triggered_rule_ids,
                confidence=explanation.confidence,
                metadata={
                    "decision_id": result.decision.id,
                    "reasoning_step_ids": explanation.reasoning_step_ids,
                    "scores_used": explanation.scores_used,
                },
            )
            for recommendation, explanation in zip(
                result.decision.recommendations,
                result.explainability_report.recommendation_explanations,
                strict=True,
            )
        ]

        trace = AgentTrace(
            referenced_evidence_ids=evidence_ids,
            referenced_observation_ids=observation_ids,
            referenced_reasoning_trace_ids=reasoning_trace_ids,
            referenced_score_ids=score_ids,
            referenced_decision_ids=decision_ids,
            referenced_recommendation_ids=recommendation_ids,
            referenced_rule_ids=rule_ids,
            notes=[
                "Derived only from an existing OpportunityPipelineResult.",
                "No memory, persistence, pipeline execution, external service, or LLM call was performed.",
            ],
            metadata={
                "opportunity_id": result.ontology.opportunity.id,
                "explainability_report_decision_id": result.explainability_report.decision_id,
            },
        )

        return AgentOutput(
            role=self.role,
            summary=(
                f"Opportunity '{result.ontology.opportunity.name}' is "
                f"{result.decision.outcome} by the existing decision policy; "
                f"{len(matched_rules)} rules matched and "
                f"{len(result.decision.recommendations)} recommendation(s) are explained."
            ),
            findings=findings,
            recommendations=recommendations,
            trace=trace,
            metadata={
                "adapter": self.__class__.__name__,
                "source_pipeline_result": True,
                "decision_id": result.decision.id,
            },
        )


__all__ = ["OpportunityAssessmentAgent"]
