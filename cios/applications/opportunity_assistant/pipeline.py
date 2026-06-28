"""Opportunity Assistant pipeline orchestration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import Field

from cios.core import Evidence, Observation
from cios.core.models import CIOSBaseModel
from cios.decision_engine import DecisionOutput
from cios.graph import KnowledgeGraphRecord
from cios.memory import MemoryRepository

from cios.applications.opportunity_assistant.decision_policy import DEFAULT_DECISION_POLICY, OpportunityDecisionPolicy
from cios.applications.opportunity_assistant.explainability import OpportunityExplainabilityReport, create_explainability_report
from cios.applications.opportunity_assistant.graph_mapping import create_graph
from cios.applications.opportunity_assistant.input import SAMPLE_PATH, create_evidence, load_sample_opportunity
from cios.applications.opportunity_assistant.memory_mapping import persist_memory_records
from cios.applications.opportunity_assistant.observation_mapping import create_observations
from cios.applications.opportunity_assistant.ontology_mapping import OpportunityOntologyResult, create_ontology
from cios.applications.opportunity_assistant.reasoning_mapping import OpportunityReasoningResult, create_reasoning
from cios.applications.opportunity_assistant.reporting import render_console_report
from cios.applications.opportunity_assistant.rules import RuleDetection, RuleMatch, detect_rules, score_rule_detections
from cios.applications.opportunity_assistant.scoring_policy import DEFAULT_SCORING_POLICY, OpportunityScoringPolicy, OpportunityScoringResult


class OpportunityPipelineResult(CIOSBaseModel):
    """Typed end-to-end result for the deterministic vertical slice."""

    source: dict[str, Any]
    evidence: list[Evidence] = Field(default_factory=list)
    ontology: OpportunityOntologyResult
    graph: KnowledgeGraphRecord
    rule_detections: list[RuleDetection] = Field(default_factory=list)
    rule_matches: list[RuleMatch] = Field(default_factory=list)
    observations: list[Observation] = Field(default_factory=list)
    reasoning: OpportunityReasoningResult
    scoring: OpportunityScoringResult
    decision: DecisionOutput
    explainability_report: OpportunityExplainabilityReport


def run_pipeline(
    path: Path = SAMPLE_PATH,
    memory_repository: MemoryRepository | None = None,
    scoring_policy: OpportunityScoringPolicy = DEFAULT_SCORING_POLICY,
    decision_policy: OpportunityDecisionPolicy = DEFAULT_DECISION_POLICY,
) -> OpportunityPipelineResult:
    """Run the deterministic evidence-to-recommendation vertical slice.

    When a memory repository is provided, passive snapshots of the evidence,
    assessment, and decision artefacts are written after the vertical slice is
    produced. Omitting the repository preserves the original in-memory-only CLI
    behaviour.
    """

    source = load_sample_opportunity(path)
    evidence = create_evidence(source)
    ontology = create_ontology(source)
    graph = create_graph(ontology, evidence)
    rule_detections = detect_rules(source)
    rule_matches = score_rule_detections(rule_detections)
    observations = create_observations(rule_matches, evidence)
    reasoning = create_reasoning(rule_matches, observations)
    scoring = scoring_policy.score(rule_matches, reasoning.trace, evidence)
    decision = decision_policy.decide(source, graph, evidence, observations, reasoning, scoring)
    explainability_report = create_explainability_report(ontology, evidence, rule_matches, observations, reasoning, scoring, decision)

    result = OpportunityPipelineResult(
        source=source,
        evidence=evidence,
        ontology=ontology,
        graph=graph,
        rule_detections=rule_detections,
        rule_matches=rule_matches,
        observations=observations,
        reasoning=reasoning,
        scoring=scoring,
        decision=decision,
        explainability_report=explainability_report,
    )
    if memory_repository is not None:
        persist_memory_records(memory_repository, result)
    return result
