"""Executable Sprint 7A opportunity assistant vertical slice."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import Field

from cios.core import ConfidenceLevel, DecisionStatus, Evidence, EvidenceKind, Observation, Recommendation
from cios.core.models import CIOSBaseModel
from cios.decision_engine import (
    DecisionAssessment,
    DecisionCriteria,
    DecisionInput,
    DecisionOption,
    DecisionOutput,
    DecisionRationale,
)
from cios.graph import EvidenceLink, GraphEdge, GraphNode, KnowledgeGraphRecord
from cios.ontology import Capability, Competitor, Contract, Customer, Opportunity
from cios.reasoning import Explanation, Hypothesis, Inference, ReasoningResult, ReasoningStep, ReasoningTrace, Signal
from cios.scoring import Score, ScoreBand, ScoreComponent, ScoringModel, ScoringResult, TransformationPressureScore

from cios.applications.opportunity_assistant.rules import RuleDetection, RuleMatch, detect_rules, score_rule_detections


class OpportunityOntologyResult(CIOSBaseModel):
    """Typed ontology artefacts created by the opportunity assistant."""

    customer: Customer
    opportunity: Opportunity
    contract: Contract
    capabilities: list[Capability] = Field(default_factory=list)
    competitors: list[Competitor] = Field(default_factory=list)


class OpportunityReasoningResult(CIOSBaseModel):
    """Typed reasoning artefacts created by rule detections."""

    signals: list[Signal] = Field(default_factory=list)
    hypotheses: list[Hypothesis] = Field(default_factory=list)
    inferences: list[Inference] = Field(default_factory=list)
    explanations: list[Explanation] = Field(default_factory=list)
    trace: ReasoningTrace
    result: ReasoningResult


class OpportunityScoringResult(CIOSBaseModel):
    """Typed scoring artefacts created by the active scoring policy."""

    result: ScoringResult
    transformation_pressure: TransformationPressureScore


class RecommendationExplainability(CIOSBaseModel):
    """Machine-readable explanation for a single recommendation."""

    recommendation_id: str
    recommendation_title: str
    supporting_observation_ids: list[str] = Field(default_factory=list)
    supporting_observations: list[str] = Field(default_factory=list)
    triggered_rules: list[str] = Field(default_factory=list)
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
    recommendation_explanations: list[RecommendationExplainability] = Field(default_factory=list)


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

SAMPLE_PATH = Path(__file__).with_name("sample_opportunity.json")


def load_sample_opportunity(path: Path = SAMPLE_PATH) -> dict[str, Any]:
    """Load the structured sample opportunity JSON."""

    return json.loads(path.read_text(encoding="utf-8"))


def run_pipeline(path: Path = SAMPLE_PATH) -> OpportunityPipelineResult:
    """Run the deterministic evidence-to-recommendation vertical slice."""

    source = load_sample_opportunity(path)
    evidence = _create_evidence(source)
    ontology = _create_ontology(source)
    graph = _create_graph(ontology, evidence)
    rule_detections = detect_rules(source)
    rule_matches = score_rule_detections(rule_detections)
    observations = _create_observations(rule_matches, evidence)
    reasoning = _create_reasoning(rule_matches, observations)
    scoring = _create_scoring(rule_matches, reasoning.trace, evidence)
    decision = _create_decision(source, graph, evidence, observations, reasoning, scoring)
    explainability_report = _create_explainability_report(ontology, evidence, rule_matches, observations, reasoning, scoring, decision)

    return OpportunityPipelineResult(
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


def _create_evidence(source: dict[str, Any]) -> list[Evidence]:
    return [
        Evidence(
            title=item["title"],
            kind=EvidenceKind.DATA,
            source=item["source"],
            summary=item.get("summary"),
            confidence=ConfidenceLevel.HIGH,
        )
        for item in source.get("evidence", [])
    ]


def _create_ontology(source: dict[str, Any]) -> OpportunityOntologyResult:
    customer = Customer(
        name=source["customer"]["name"],
        sector=source["customer"].get("sector"),
        region=source["customer"].get("region"),
    )
    capabilities = [Capability(name=name) for name in source.get("capabilities", [])]
    competitors = [Competitor(name=name) for name in source.get("competitors", [])]
    contract = Contract(name=f"{source['name']} Contract", customer_id=customer.id, value=source.get("value"))
    opportunity = Opportunity(
        name=source["name"],
        description=source.get("description"),
        customer_id=customer.id,
        capability_ids=[capability.id for capability in capabilities],
        competitor_ids=[competitor.id for competitor in competitors],
        contract_id=contract.id,
        value=source.get("value"),
        metadata={"duration_months": source.get("duration_months")},
    )
    return OpportunityOntologyResult(customer=customer, opportunity=opportunity, contract=contract, capabilities=capabilities, competitors=competitors)


def _create_graph(ontology: OpportunityOntologyResult, evidence: list[Evidence]) -> KnowledgeGraphRecord:
    objects = [ontology.customer, ontology.opportunity, ontology.contract, *ontology.capabilities, *ontology.competitors]
    nodes = [GraphNode(wrapped_id=obj.id, wrapped_type=obj.__class__.__name__, source_package="ontology", label=obj.name) for obj in objects]
    by_wrapped_id = {node.wrapped_id: node for node in nodes}
    opportunity_node = by_wrapped_id[ontology.opportunity.id]
    edges = [
        GraphEdge(source_node_id=opportunity_node.id, target_node_id=by_wrapped_id[ontology.customer.id].id, edge_type="for_customer"),
        GraphEdge(source_node_id=opportunity_node.id, target_node_id=by_wrapped_id[ontology.contract.id].id, edge_type="governed_by_contract"),
    ]
    edges.extend(
        GraphEdge(source_node_id=opportunity_node.id, target_node_id=by_wrapped_id[item.id].id, edge_type=edge_type)
        for edge_type, items in [("requires_capability", ontology.capabilities), ("competes_against", ontology.competitors)]
        for item in items
    )
    return KnowledgeGraphRecord(
        name="Opportunity Assistant Knowledge Graph",
        description="In-memory graph record created for the Sprint 7A vertical slice.",
        nodes=nodes,
        edges=edges,
        evidence_links=[EvidenceLink(subject_id=opportunity_node.id, evidence_ids=[item.id for item in evidence])],
    )


def _create_observations(rule_matches: list[RuleMatch], evidence: list[Evidence]) -> list[Observation]:
    evidence_ids = [item.id for item in evidence]
    return [Observation(statement=rule.observation, evidence_ids=evidence_ids, confidence=ConfidenceLevel.HIGH if rule.matched else ConfidenceLevel.MEDIUM, metadata={"rule": rule.name}) for rule in rule_matches]


def _create_reasoning(rule_matches: list[RuleMatch], observations: list[Observation]) -> OpportunityReasoningResult:
    signals = [Signal(name=rule.signal_name, description=rule.rationale, source_ids=[observations[index].id], strength=rule.signal_strength, metadata={"rule": rule.name, "matched": rule.matched}) for index, rule in enumerate(rule_matches)]
    hypotheses = [Hypothesis(statement="The opportunity is a strong candidate for qualified pursuit.", evidence_ids=[obs.id for obs in observations], confidence=ConfidenceLevel.HIGH)]
    inferences = [Inference(statement=f"{rule.name}: {'matched' if rule.matched else 'not matched'}; {rule.rationale}", premise_ids=[observations[index].id, signals[index].id], confidence=ConfidenceLevel.HIGH if rule.matched else ConfidenceLevel.MEDIUM) for index, rule in enumerate(rule_matches)]
    explanation = Explanation(summary="Deterministic rules indicate a high-value, security-sensitive transformation opportunity with managed-service and competitive differentiation needs.", observation_ids=[obs.id for obs in observations], inference_ids=[inf.id for inf in inferences])
    steps = [ReasoningStep(sequence=index + 1, description=f"Evaluate rule: {rule.name}.", input_ids=[observations[index].id], output_ids=[signals[index].id, inferences[index].id], metadata={"matched": rule.matched}) for index, rule in enumerate(rule_matches)]
    trace = ReasoningTrace(name="Opportunity Assistant Rule Trace", description="Rule-by-rule deterministic reasoning trace.", steps=steps, hypothesis_ids=[h.id for h in hypotheses], inference_ids=[i.id for i in inferences], explanation_ids=[explanation.id])
    return OpportunityReasoningResult(signals=signals, hypotheses=hypotheses, inferences=inferences, explanations=[explanation], trace=trace, result=ReasoningResult(summary=explanation.summary, trace=trace, hypotheses=hypotheses, signals=signals, inferences=inferences, explanations=[explanation]))


def _create_scoring(rule_matches: list[RuleMatch], trace: ReasoningTrace, evidence: list[Evidence]) -> OpportunityScoringResult:
    components = [ScoreComponent(name=rule.name, score=Score(name=rule.name, value=rule.score, rationale=rule.rationale, evidence_ids=[item.id for item in evidence]), weight=1.0, rationale=rule.rationale) for rule in rule_matches]
    overall_value = round(sum(component.score.value for component in components) / len(components), 2)
    bands = [ScoreBand(name="Low", minimum=0, maximum=49), ScoreBand(name="Medium", minimum=50, maximum=74), ScoreBand(name="High", minimum=75, maximum=100)]
    band = next(item for item in bands if item.minimum <= overall_value <= item.maximum)
    model = ScoringModel(name="Sprint 7A Deterministic Opportunity Score", version="0.1.0", bands=bands)
    result = ScoringResult(scoring_model=model, overall_score=Score(name="Overall Opportunity Score", value=overall_value, rationale="Average of deterministic Sprint 7A rule components."), components=components, band=band, reasoning_trace=trace)
    return OpportunityScoringResult(result=result, transformation_pressure=TransformationPressureScore(result=result, urgency_score=components[4].score, strategic_importance_score=components[0].score, change_pressure_score=components[1].score, capability_gap_score=components[2].score))


def _create_decision(source: dict[str, Any], graph: KnowledgeGraphRecord, evidence: list[Evidence], observations: list[Observation], reasoning: OpportunityReasoningResult, scoring: OpportunityScoringResult) -> DecisionOutput:
    input_bundle = DecisionInput(name=f"{source['name']} Decision Input", question="Should this opportunity be qualified for active pursuit?", graph_records=[graph], reasoning_traces=[reasoning.trace], reasoning_results=[reasoning.result], scoring_results=[scoring.result], evidence=evidence, observations=observations)
    option = DecisionOption(title="Qualify for active pursuit", description="Proceed with capture planning focused on transformation, security, managed service operations, and differentiation.", actions=["Build an Oracle transformation win theme.", "Validate security accreditation evidence.", "Prepare managed-service operating model proof points.", "Create competitor differentiation plan."], evidence_ids=[item.id for item in evidence])
    criteria = [DecisionCriteria(name="Commercial attractiveness", weight=0.4), DecisionCriteria(name="Strategic fit", weight=0.3), DecisionCriteria(name="Delivery confidence", weight=0.3)]
    assessment = DecisionAssessment(option_id=option.id, overall_score=scoring.result.overall_score, rationale="The deterministic vertical slice score supports active pursuit with explicit risk management.", evidence_ids=[item.id for item in evidence], reasoning_trace_ids=[reasoning.trace.id], scoring_result_ids=[scoring.result.id])
    rationale = DecisionRationale(summary="Qualify because the opportunity combines high value, Oracle transformation pressure, security criticality, managed-service fit, long-term contract potential, and known competitive intensity.", evidence_ids=[item.id for item in evidence], reasoning_trace_ids=[reasoning.trace.id], reasoning_result_ids=[reasoning.result.id], score_ids=[scoring.result.overall_score.id], scoring_result_ids=[scoring.result.id], confidence=ConfidenceLevel.HIGH)
    recommendation = Recommendation(title="Qualify opportunity with focused capture plan", rationale=rationale.summary, actions=option.actions, evidence_ids=[item.id for item in evidence])
    return DecisionOutput(title="Opportunity qualification decision", input_id=input_bundle.id, selected_option_id=option.id, status=DecisionStatus.APPROVED, options=[option], criteria=criteria, assessments=[assessment], rationales=[rationale], recommendations=[recommendation], confidence=ConfidenceLevel.HIGH, outcome="selected", metadata={"decision_input": input_bundle.model_dump()})


def _create_explainability_report(
    ontology: OpportunityOntologyResult,
    evidence: list[Evidence],
    rule_matches: list[RuleMatch],
    observations: list[Observation],
    reasoning: OpportunityReasoningResult,
    scoring: OpportunityScoringResult,
    decision: DecisionOutput,
) -> OpportunityExplainabilityReport:
    matched_indexes = [index for index, rule in enumerate(rule_matches) if rule.matched]
    supporting_indexes = matched_indexes or list(range(len(rule_matches)))
    supporting_observations = [observations[index] for index in supporting_indexes]
    supporting_components = [scoring.result.components[index] for index in supporting_indexes]
    reasoning_steps = [reasoning.trace.steps[index] for index in supporting_indexes]

    explanations = [
        RecommendationExplainability(
            recommendation_id=recommendation.id,
            recommendation_title=recommendation.title,
            supporting_observation_ids=[observation.id for observation in supporting_observations],
            supporting_observations=[observation.statement for observation in supporting_observations],
            triggered_rules=[rule.name for rule in rule_matches if rule.matched],
            evidence_ids=sorted({evidence_id for item in evidence for evidence_id in [item.id]}),
            score_ids=[component.score.id for component in supporting_components] + [scoring.result.overall_score.id],
            scores_used={component.name: component.score.value for component in supporting_components}
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


def render_console_report(result: OpportunityPipelineResult) -> str:
    """Render a human-readable report for console execution."""

    lines = ["CIOS Opportunity Assistant – Sprint 7A Vertical Slice", "=" * 57, "", f"Opportunity: {result.source['name']}", "", "Observations:"]
    lines.extend(f"- {item.statement}" for item in result.observations)
    lines.append("")
    lines.append("Signals:")
    lines.extend(f"- {item.name} ({item.strength}): {item.description}" for item in result.reasoning.signals)
    lines.append("")
    lines.append("Scores:")
    for component in result.scoring.result.components:
        lines.append(f"- {component.name}: {component.score.value:.0f}/100")
    lines.append(f"- Overall: {result.scoring.result.overall_score.value:.2f}/100 ({result.scoring.result.band.name})")
    decision = result.decision
    lines.extend(["", f"Recommendation: {decision.recommendations[0].title}", f"Confidence: {decision.confidence}", "Reasoning Trace Summary:", f"- {result.reasoning.result.summary}", f"- Trace steps: {len(result.reasoning.trace.steps)}"])
    return "\n".join(lines)
