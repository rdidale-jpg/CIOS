"""Console reporting for Flora v0.1."""

from __future__ import annotations

from cios.applications.flora.models import DailyBrief


def render_daily_brief(brief: DailyBrief) -> str:
    """Render a readable morning briefing."""

    lines = [brief.title, f"Generated for: {brief.generated_for} — {brief.business_unit}", f"Geographies: {', '.join(brief.target_geographies)}", "", "Top AI Reinvention opportunities:"]
    for item in brief.items:
        lines.extend([
            f"{item.rank}. {item.organisation} ({item.sector}) — Score {item.scores.ai_reinvention_opportunity_score}",
            f"   Why interesting: {item.why_interesting}",
            f"   Strongest signals: {'; '.join(item.strongest_detected_signals)}",
            f"   Capability areas: {', '.join(item.likely_capability_areas)}",
            f"   Competitors to watch: {', '.join(item.main_competitors_to_watch)}",
            f"   Recommended next action: {item.recommended_next_action}",
        ])
    return "\n".join(lines)
