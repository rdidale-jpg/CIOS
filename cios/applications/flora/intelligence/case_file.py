"""Living Commercial Case File generation for Flora."""
from __future__ import annotations
from datetime import date
from pydantic import BaseModel, Field
from cios.applications.flora.intelligence.evidence_engine import CommercialEvidence, evidence_for_organisation
from cios.applications.flora.intelligence.insight_engine import CommercialInsight, generate_insights
from cios.applications.flora.intelligence.timeline import TimelineEntry, build_timeline
from cios.applications.flora.pipeline import build_assessment
from cios.applications.flora.seed_data import sample_commercial_dna, sample_signals, sample_watchlist

class CommercialCaseFile(BaseModel):
    organisation: str
    sector: str
    commercial_dna_summary: str
    executive_summary: str
    pressure_profile: str
    ai_reinvention_profile: str
    capability_heatmap: dict[str, str] = Field(default_factory=dict)
    executive_landscape: list[str] = Field(default_factory=list)
    board_and_ned_summary: str
    competitive_landscape: str
    propositions: list[str] = Field(default_factory=list)
    assessments: list[str] = Field(default_factory=list)
    insights: list[CommercialInsight] = Field(default_factory=list)
    evidence: list[CommercialEvidence] = Field(default_factory=list)
    timeline: list[TimelineEntry] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    review_date: date


def _find_account(name: str):
    norm = name.lower().replace(" ", "")
    for account in sample_watchlist():
        if account.organisation_name.lower().replace(" ", "") == norm:
            return account
    raise ValueError(f"Unknown seeded Flora case: {name}")


def _narrative(org: str, sector: str, evidence: list[CommercialEvidence], insights: list[CommercialInsight]) -> str:
    themes = sorted({tag for ev in evidence for tag in ev.capability_tags})[:4]
    insight = insights[0].title if insights else "No insight generated."
    text = (f"{org} is a seeded {sector} case file showing converging commercial pressure across annual-report, regulatory, investor, technology, executive and customer evidence. "
            f"The strongest deterministic themes are {', '.join(themes)}. {insight} "
            "For a Sales Director, the situation is best treated as a governed discovery opportunity: validate sponsor, funding, incumbent activity and whether the current transformation agenda already includes systems-integrator or enterprise-platform commitments. "
            "The case file is deliberately evidence-led and should be used to prepare a focused conversation, not as proof of intent.")
    return " ".join(text.split()[:400])


def generate_case_file(organisation: str) -> CommercialCaseFile:
    account = _find_account(organisation)
    dna = sample_commercial_dna()
    evidence = evidence_for_organisation(account.organisation_name)
    signals = [s for s in sample_signals() if s.organisation == account.organisation_name]
    assessment = build_assessment(account, signals, dna)
    insights = generate_insights(account.organisation_name, evidence, [assessment.assessment_id])
    caps = sorted({tag for ev in evidence for tag in ev.capability_tags})
    execs = sorted({tag for ev in evidence for tag in ev.executive_tags})
    incumbents = ", ".join(account.known_incumbents) or "unknown"
    challengers = ", ".join(account.known_competitors) or "unknown"
    return CommercialCaseFile(
        organisation=account.organisation_name, sector=account.sector,
        commercial_dna_summary=f"Organisation profile: {account.sector} account. Strategic priorities: {account.notes} Known pressures: regulatory, operational, customer and cost themes. Known AI themes: {', '.join(caps)}. Known executive priorities: {', '.join(execs)}. Sector characteristics: {account.sector} playbook context.",
        executive_summary=_narrative(account.organisation_name, account.sector, evidence, insights),
        pressure_profile=f"Commercial pressure is driven by {account.notes} Evidence categories include annual report, investor, regulatory, executive, technology and customer signals.",
        ai_reinvention_profile=f"Likely AI reinvention areas: {', '.join(caps)}. Readiness is inferred only from seeded technology and data themes.",
        capability_heatmap={cap: ("high" if i < 2 else "medium") for i, cap in enumerate(caps)}, executive_landscape=execs,
        board_and_ned_summary="Board and NED relevance is treated as an evidence gap unless public governance evidence confirms AI sponsorship.",
        competitive_landscape=f"Known incumbents: {incumbents}. Likely challengers: {challengers}. Watch items: awards, hiring, partner announcements and procurement references. Differentiation opportunities: faster evidence-led discovery, sector-specific outcomes and transparent governance, consistent with competitor playbook hypotheses.",
        propositions=assessment.supporting_propositions, assessments=[assessment.assessment_id], insights=insights, evidence=evidence,
        timeline=build_timeline(evidence, insights),
        open_questions=["Has transformation funding been approved?", "Is AI board-sponsored?", "Which executive owns Customer Operations?", "Has a systems integrator already engaged?", "Is Oracle/SAP transformation already planned?"],
        recommended_actions=[a.action_summary for a in assessment.recommended_actions] + [i.recommended_next_step for i in insights], review_date=date(2026, 7, 29),
    )
