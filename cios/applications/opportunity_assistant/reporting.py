"""Console reporting for the Opportunity Assistant."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cios.applications.opportunity_assistant.pipeline import OpportunityPipelineResult


def render_console_report(result: "OpportunityPipelineResult") -> str:
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
