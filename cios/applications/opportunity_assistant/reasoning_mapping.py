"""Reasoning mapping for the Opportunity Assistant."""

from __future__ import annotations

from pydantic import Field

from cios.core import ConfidenceLevel, Observation
from cios.core.models import CIOSBaseModel
from cios.reasoning import Explanation, Hypothesis, Inference, ReasoningResult, ReasoningStep, ReasoningTrace, Signal

from cios.applications.opportunity_assistant.rules import RuleMatch


class OpportunityReasoningResult(CIOSBaseModel):
    """Typed reasoning artefacts created by rule detections."""

    signals: list[Signal] = Field(default_factory=list)
    hypotheses: list[Hypothesis] = Field(default_factory=list)
    inferences: list[Inference] = Field(default_factory=list)
    explanations: list[Explanation] = Field(default_factory=list)
    trace: ReasoningTrace
    result: ReasoningResult


def create_reasoning(rule_matches: list[RuleMatch], observations: list[Observation]) -> OpportunityReasoningResult:
    """Map rule matches and observations into reasoning artefacts."""

    observations_by_rule_id = {observation.metadata["rule_id"]: observation for observation in observations}
    signals = [
        Signal(
            name=rule.signal_name,
            description=rule.rationale,
            source_ids=[observations_by_rule_id[rule.rule_id].id],
            strength=rule.signal_strength,
            metadata={"rule": rule.name, "rule_id": rule.rule_id, "matched": rule.matched},
        )
        for rule in rule_matches
    ]
    hypotheses = [
        Hypothesis(
            statement="The opportunity is a strong candidate for qualified pursuit.",
            evidence_ids=[obs.id for obs in observations],
            confidence=ConfidenceLevel.HIGH,
        )
    ]
    signals_by_rule_id = {signal.metadata["rule_id"]: signal for signal in signals}
    inferences = [
        Inference(
            statement=f"{rule.name}: {'matched' if rule.matched else 'not matched'}; {rule.rationale}",
            premise_ids=[observations_by_rule_id[rule.rule_id].id, signals_by_rule_id[rule.rule_id].id],
            confidence=ConfidenceLevel.HIGH if rule.matched else ConfidenceLevel.MEDIUM,
            metadata={"rule": rule.name, "rule_id": rule.rule_id, "matched": rule.matched},
        )
        for rule in rule_matches
    ]
    explanation = Explanation(
        summary="Deterministic rules indicate a high-value, security-sensitive transformation opportunity with managed-service and competitive differentiation needs.",
        observation_ids=[obs.id for obs in observations],
        inference_ids=[inf.id for inf in inferences],
    )
    inferences_by_rule_id = {inference.metadata["rule_id"]: inference for inference in inferences}
    steps = [
        ReasoningStep(
            sequence=index + 1,
            description=f"Evaluate rule: {rule.name}.",
            input_ids=[observations_by_rule_id[rule.rule_id].id],
            output_ids=[signals_by_rule_id[rule.rule_id].id, inferences_by_rule_id[rule.rule_id].id],
            metadata={"rule": rule.name, "rule_id": rule.rule_id, "matched": rule.matched},
        )
        for index, rule in enumerate(rule_matches)
    ]
    trace = ReasoningTrace(
        name="Opportunity Assistant Rule Trace",
        description="Rule-by-rule deterministic reasoning trace.",
        steps=steps,
        hypothesis_ids=[h.id for h in hypotheses],
        inference_ids=[i.id for i in inferences],
        explanation_ids=[explanation.id],
    )
    return OpportunityReasoningResult(
        signals=signals,
        hypotheses=hypotheses,
        inferences=inferences,
        explanations=[explanation],
        trace=trace,
        result=ReasoningResult(summary=explanation.summary, trace=trace, hypotheses=hypotheses, signals=signals, inferences=inferences, explanations=[explanation]),
    )
