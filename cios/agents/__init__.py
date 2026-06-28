"""Agent-facing contracts for CIOS.

The agents package exposes passive Pydantic contracts only. It does not provide
autonomous execution, LLM calls, persistence, APIs, UI, databases, or external
service integrations.
"""

from cios.agents.models import (
    AgentExecutionContext,
    AgentFinding,
    AgentInput,
    AgentOutput,
    AgentRecommendation,
    AgentRole,
    AgentTrace,
)

__all__ = [
    "AgentExecutionContext",
    "AgentFinding",
    "AgentInput",
    "AgentOutput",
    "AgentRecommendation",
    "AgentRole",
    "AgentTrace",
]
