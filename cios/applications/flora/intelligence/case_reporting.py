"""Console rendering for Living Commercial Case Files."""
from __future__ import annotations
from cios.applications.flora.intelligence.case_file import CommercialCaseFile

def render_case_file(case: CommercialCaseFile) -> str:
    lines = [f"Living Commercial Case File: {case.organisation}", f"Sector: {case.sector}", "", "Executive Summary", case.executive_summary, "", "Commercial DNA View", case.commercial_dna_summary, "", "Commercial Timeline"]
    for entry in case.timeline:
        lines.append(f"- {entry.entry_date:%B %d, %Y} [{entry.entry_type}] {entry.title} — {entry.description}")
    lines.extend(["", "Evidence Ledger"])
    for ev in case.evidence:
        lines.append(f"- {ev.evidence_id}: {ev.evidence_category.value} / {ev.source_name} ({ev.publication_date}) — {ev.summary}")
    lines.extend(["", "Commercial Insights"])
    for insight in case.insights:
        lines.append(f"- {insight.title} Confidence {insight.confidence}. {insight.narrative} Next: {insight.recommended_next_step}")
    lines.extend(["", "Pressure Profile", case.pressure_profile, "", "AI Reinvention Assessment", case.ai_reinvention_profile, "", "Capability Heatmap"])
    for cap, heat in case.capability_heatmap.items():
        lines.append(f"- {cap}: {heat}")
    lines.extend(["", "Competitive Context", case.competitive_landscape, "", "Open Intelligence Questions"])
    lines.extend(f"- {q}" for q in case.open_questions)
    lines.extend(["", "Recommended Actions"])
    lines.extend(f"- {a}" for a in case.recommended_actions)
    return "\n".join(lines)
