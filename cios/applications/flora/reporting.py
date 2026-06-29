"""Console reporting for Flora v0.2."""

from __future__ import annotations

from cios.applications.flora.models import DailyBrief, WeeklyIntelligenceBrief


def render_daily_brief(brief: DailyBrief) -> str:
    """Render a readable intelligence briefing."""

    lines = [brief.title, f"Generated for: {brief.generated_for} — {brief.business_unit}", f"Geographies: {', '.join(brief.target_geographies)}", "", "Top AI Reinvention opportunities:"]
    for item in brief.items:
        assessment = item.assessment
        lines.extend([
            f"{item.rank}. {item.organisation} ({item.sector}) — Score {item.scores.ai_reinvention_opportunity_score}",
            f"   Why interesting: {item.why_interesting}",
            f"   Strongest signals: {'; '.join(item.strongest_detected_signals)}",
            f"   Capability areas: {', '.join(item.likely_capability_areas)}",
            f"   Competitors to watch: {', '.join(item.main_competitors_to_watch)}",
            f"   Recommended next action: {item.recommended_next_action}",
        ])
        if assessment:
            action = assessment.recommended_actions[0]
            lines.extend([
                "   Assessment:",
                f"     Why now: {assessment.why_now}",
                f"     Why capability: {assessment.why_this_capability}",
                f"     Why executive: {assessment.why_this_executive}",
                f"     Why proposition: {assessment.why_this_proposition}",
                f"     Why action: {action.why_this_action}",
                f"     Pattern: {action.commercial_pattern}",
                f"     Playbooks: {', '.join(assessment.supporting_playbooks)}",
                f"     Proposition: {action.proposition}",
                f"     Missing evidence: {', '.join(assessment.missing_evidence)}",
            ])
    return "\n".join(lines)


def render_weekly_brief(brief: WeeklyIntelligenceBrief) -> str:
    """Render a readable weekly intelligence briefing."""

    lines = [brief.title, f"Generated for: {brief.generated_for} — {brief.business_unit}", "", "Biggest movers:"]
    for mover in brief.biggest_movers:
        lines.append(f"- {mover.organisation}: {mover.previous_score} → {mover.current_score} ({mover.score_change:+}) — {mover.reason}")
    lines.extend(["", "New evidence:"])
    for evidence in brief.new_evidence:
        lines.append(f"- {evidence.source_name} / {evidence.related_signal}: {evidence.evidence_summary}")
    lines.extend(["", f"Organisations to watch: {', '.join(brief.organisations_to_watch)}", f"Organisations to deprioritise: {', '.join(brief.organisations_to_deprioritise)}"])
    return "\n".join(lines)
