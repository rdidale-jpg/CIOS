"""Passive memory mapping for the Opportunity Assistant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cios.memory import AssessmentMemoryRecord, DecisionMemoryRecord, EvidenceMemoryRecord, MemoryRepository

if TYPE_CHECKING:
    from cios.applications.opportunity_assistant.pipeline import OpportunityPipelineResult


def persist_memory_records(memory_repository: MemoryRepository, result: "OpportunityPipelineResult") -> None:
    """Persist passive memory records for the completed vertical slice."""

    evidence_ids = [item.id for item in result.evidence]
    subject_id = result.ontology.opportunity.id
    memory_repository.save(
        EvidenceMemoryRecord(
            subject_id=subject_id,
            related_ids=[result.graph.id, result.decision.id],
            evidence_ids=evidence_ids,
            graph_record_ids=[result.graph.id],
            evidence=result.evidence,
            payload={
                "source_name": result.source["name"],
                "evidence_count": len(result.evidence),
                "evidence": [item.model_dump(mode="json") for item in result.evidence],
            },
        )
    )

    for assessment in result.decision.assessments:
        memory_repository.save(
            AssessmentMemoryRecord(
                subject_id=subject_id,
                related_ids=[result.decision.id, assessment.option_id],
                evidence_ids=list(assessment.evidence_ids),
                graph_record_ids=[result.graph.id],
                assessment_id=assessment.id,
                graph_records=[result.graph],
                payload={
                    "assessment": assessment.model_dump(mode="json"),
                    "overall_score": assessment.overall_score.model_dump(mode="json"),
                },
            )
        )

    memory_repository.save(
        DecisionMemoryRecord(
            subject_id=subject_id,
            related_ids=[recommendation.id for recommendation in result.decision.recommendations],
            evidence_ids=evidence_ids,
            graph_record_ids=[result.graph.id],
            decision_id=result.decision.id,
            decision_payload=result.decision.model_dump(mode="json"),
            payload={
                "status": result.decision.status,
                "outcome": result.decision.outcome,
                "confidence": result.decision.confidence,
                "recommendation_ids": [recommendation.id for recommendation in result.decision.recommendations],
            },
        )
    )
