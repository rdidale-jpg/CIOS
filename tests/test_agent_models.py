from __future__ import annotations

import ast
from pathlib import Path

from cios.agents import (
    AgentExecutionContext,
    AgentFinding,
    AgentInput,
    AgentOutput,
    AgentRecommendation,
    AgentRole,
    AgentTrace,
)

AGENTS_PACKAGE = Path(__file__).resolve().parents[1] / "cios" / "agents"


def test_agent_contracts_instantiate_correctly() -> None:
    context = AgentExecutionContext(
        role=AgentRole.REASONING_ASSISTANT,
        user_id="user-1",
        session_id="session-1",
        evidence_ids=["evidence-1"],
        observation_ids=["observation-1"],
        reasoning_trace_ids=["reasoning_trace-1"],
        score_ids=["score-1"],
        decision_ids=["decision-1"],
        recommendation_ids=["recommendation-1"],
        rule_ids=["rule-1"],
    )
    agent_input = AgentInput(
        role=AgentRole.REASONING_ASSISTANT,
        objective="Summarize existing reasoning traceability.",
        context=context,
        allowed_reference_ids=["evidence-1", "reasoning_trace-1"],
        constraints=["Return structured output only."],
    )
    finding = AgentFinding(
        title="High urgency signal",
        statement="Existing observations indicate urgent buyer pressure.",
        evidence_ids=["evidence-1"],
        observation_ids=["observation-1"],
        reasoning_trace_ids=["reasoning_trace-1"],
        score_ids=["score-1"],
        rule_ids=["rule-1"],
    )
    recommendation = AgentRecommendation(
        title="Review decision rationale",
        rationale="Use the existing decision output and score before taking action.",
        decision_ids=["decision-1"],
        recommendation_ids=["recommendation-1"],
        evidence_ids=["evidence-1"],
    )
    trace = AgentTrace(
        agent_input_id=agent_input.id,
        context_id=context.id,
        referenced_evidence_ids=["evidence-1"],
        referenced_observation_ids=["observation-1"],
        referenced_reasoning_trace_ids=["reasoning_trace-1"],
        referenced_score_ids=["score-1"],
        referenced_decision_ids=["decision-1"],
        referenced_recommendation_ids=["recommendation-1"],
        referenced_rule_ids=["rule-1"],
    )
    output = AgentOutput(
        role=AgentRole.REASONING_ASSISTANT,
        input_id=agent_input.id,
        summary="Structured review completed.",
        findings=[finding],
        recommendations=[recommendation],
        trace=trace,
    )

    assert context.role == "reasoning_assistant"
    assert agent_input.context == context
    assert output.findings == [finding]
    assert output.recommendations == [recommendation]
    assert output.trace == trace


def test_outputs_can_reference_existing_traceability_ids() -> None:
    output = AgentOutput(
        role=AgentRole.EXPLAINABILITY_ASSISTANT,
        input_id="agent_input-1",
        summary="References existing pipeline artefacts only.",
        findings=[
            AgentFinding(
                title="Traceable finding",
                statement="Finding references existing artefact identifiers.",
                evidence_ids=["evidence-123"],
                observation_ids=["observation-123"],
                reasoning_trace_ids=["reasoning_trace-123"],
                score_ids=["score-123"],
                rule_ids=["rule-123"],
            )
        ],
        recommendations=[
            AgentRecommendation(
                title="Candidate follow-up",
                rationale="Candidate remains linked to policy-governed decision artefacts.",
                evidence_ids=["evidence-123"],
                observation_ids=["observation-123"],
                reasoning_trace_ids=["reasoning_trace-123"],
                score_ids=["score-123"],
                decision_ids=["decision-123"],
                recommendation_ids=["recommendation-123"],
                rule_ids=["rule-123"],
            )
        ],
    )

    assert output.findings[0].evidence_ids == ["evidence-123"]
    assert output.recommendations[0].decision_ids == ["decision-123"]
    assert output.recommendations[0].recommendation_ids == ["recommendation-123"]


def test_models_serialize_correctly() -> None:
    output = AgentOutput(
        role=AgentRole.OBSERVER,
        summary="Serializable structured output.",
        findings=[AgentFinding(title="Finding", statement="A structured finding.")],
    )

    payload = output.model_dump(mode="json")

    assert payload["role"] == "observer"
    assert payload["findings"][0]["title"] == "Finding"
    assert payload["created_at"].endswith("Z") or "+00:00" in payload["created_at"]


def test_agents_package_has_no_forbidden_imports() -> None:
    forbidden_prefixes = (
        "cios.memory",
        "cios.applications",
        "requests",
        "httpx",
        "openai",
        "anthropic",
        "sqlalchemy",
        "fastapi",
        "django",
        "flask",
    )

    for path in AGENTS_PACKAGE.glob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            module = None
            if isinstance(node, ast.ImportFrom):
                module = node.module
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith(forbidden_prefixes), f"forbidden import {alias.name} in {path}"
                continue
            if module is not None:
                assert not module.startswith(forbidden_prefixes), f"forbidden import {module} in {path}"


def test_no_autonomous_behaviour_exists() -> None:
    forbidden_method_names = {
        "act",
        "execute",
        "invoke",
        "persist",
        "run",
        "save",
        "start",
        "call_llm",
        "call_model",
    }

    for path in AGENTS_PACKAGE.glob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            assert not (
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in forbidden_method_names
            ), f"autonomous behaviour method {node.name} found in {path}"
