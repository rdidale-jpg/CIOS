"""Flora v0.2 intelligence assessment and briefing generation pipeline."""

from __future__ import annotations

from collections import defaultdict
from datetime import date

from cios.applications.flora.models import (
    BriefingItem,
    CommercialDNA,
    DailyBrief,
    EvidenceItem,
    IntelligenceAssessment,
    RecommendedAction,
    Signal,
    TargetAccount,
    WeeklyIntelligenceBrief,
    WeeklyMover,
)
from cios.applications.flora.scoring import calculate_scores, strongest_signals, top_capabilities
from cios.applications.flora.seed_data import sample_commercial_dna, sample_signals, sample_watchlist

MISSING_EVIDENCE_GAPS = [
    "Funding not confirmed",
    "Executive sponsor unknown",
    "Procurement timing unknown",
    "Competitor engagement unknown",
]

SECTOR_PLAYBOOKS = {
    "Utilities": "SECTOR_PLAYBOOK_UTILITIES",
    "Energy": "SECTOR_PLAYBOOK_ENERGY",
    "Telecommunications": "SECTOR_PLAYBOOK_TELECOMMUNICATIONS",
    "Media": "SECTOR_PLAYBOOK_MEDIA",
    "Sport": "SECTOR_PLAYBOOK_SPORT",
}

CAPABILITY_PLAYBOOKS = {
    "customer": "CAPABILITY_PLAYBOOK_CUSTOMER_OPERATIONS",
    "field": "CAPABILITY_PLAYBOOK_FIELD_OPERATIONS",
    "asset": "CAPABILITY_PLAYBOOK_ASSET_MANAGEMENT",
    "network": "CAPABILITY_PLAYBOOK_CONTACT_CENTRE",
    "content": "CAPABILITY_PLAYBOOK_CUSTOMER_OPERATIONS",
}


def _executive_for(capability: str) -> str:
    lowered = capability.lower()
    if any(term in lowered for term in ("asset", "field", "grid", "network", "operations")):
        return "COO"
    if any(term in lowered for term in ("data", "platform", "content", "knowledge")):
        return "CIO"
    return "CDO"


def _capability_playbook(capability: str) -> str:
    lowered = capability.lower()
    for key, playbook in CAPABILITY_PLAYBOOKS.items():
        if key in lowered:
            return playbook
    return "CAPABILITY_PLAYBOOK_CUSTOMER_OPERATIONS"


def _proposition(capability: str) -> str:
    return f"AI Reinvention Discovery for {capability.title()}"


def _evidence_from_signals(signals: list[Signal]) -> list[EvidenceItem]:
    return [
        EvidenceItem(
            source_name=signal.source,
            source_type=signal.source_type,
            publication_date=signal.detected_date,
            evidence_summary=signal.evidence_text,
            related_signal=signal.signal_id,
            confidence=signal.confidence,
        )
        for signal in signals
    ]


def build_assessment(account: TargetAccount, signals: list[Signal], dna: CommercialDNA) -> IntelligenceAssessment:
    """Build an explainable seeded assessment for one target account."""

    scores = calculate_scores(account, signals, dna)
    capabilities = top_capabilities(signals) or ["AI opportunity discovery"]
    primary_capability = capabilities[0]
    executive = _executive_for(primary_capability)
    sector_playbook = SECTOR_PLAYBOOKS.get(account.sector, "SECTOR_PLAYBOOK_MEDIA")
    capability_playbook = _capability_playbook(primary_capability)
    executive_playbook = f"EXECUTIVE_PLAYBOOK_{executive}"
    pattern = "Commercial Pattern: Pressure-led AI reinvention opening"
    proposition = _proposition(primary_capability)
    signal_summary = signals[0].signal_summary if signals else account.notes
    competitors = ", ".join(account.known_competitors) or "No named competitors in seeded watchlist"

    action = RecommendedAction(
        action_id=f"FLORA-ACT-{account.organisation_name.upper().replace(' ', '-')}-001",
        action_summary=f"Run an executive discovery conversation on {primary_capability} with the {executive} community.",
        why_this_organisation=f"{account.organisation_name} is a {account.priority.value}-priority {account.sector} account aligned to {dna.business_unit}.",
        why_now=f"Current seeded signals show {signal_summary.lower()} and a score of {scores.ai_reinvention_opportunity_score}.",
        why_this_capability=f"{primary_capability} is the strongest recurring capability in the available signal evidence.",
        why_this_executive=f"The {executive} is the most likely owner for outcomes linked to {primary_capability}.",
        why_this_proposition=f"{proposition} packages the capability into a low-friction, evidence-led conversation.",
        why_this_action="A short discovery session validates sponsorship, timing, funding and competitor presence before deeper pursuit.",
        commercial_pattern=pattern,
        sector_playbook=sector_playbook,
        capability_playbook=capability_playbook,
        executive_playbook=executive_playbook,
        proposition=proposition,
        confidence=min(100, max(0, scores.ai_reinvention_opportunity_score)),
    )
    return IntelligenceAssessment(
        assessment_id=f"FLORA-ASMT-{account.organisation_name.upper().replace(' ', '-')}-20260629",
        organisation=account.organisation_name,
        assessment_date=date(2026, 6, 29),
        commercial_summary=f"{account.organisation_name} has a deterministic opportunity score of {scores.ai_reinvention_opportunity_score} driven by {account.notes}",
        why_now=action.why_now,
        why_this_capability=action.why_this_capability,
        why_this_proposition=action.why_this_proposition,
        why_this_executive=action.why_this_executive,
        competitive_context=f"Known competitors to watch: {competitors}. Known incumbents: {', '.join(account.known_incumbents) or 'unknown'}.",
        confidence=action.confidence,
        missing_evidence=MISSING_EVIDENCE_GAPS.copy(),
        supporting_patterns=[pattern],
        supporting_playbooks=[sector_playbook, capability_playbook, executive_playbook],
        supporting_propositions=[proposition],
        evidence=_evidence_from_signals(signals),
        recommended_actions=[action],
    )


def _ranked_items(dna: CommercialDNA, watchlist: list[TargetAccount], signals: list[Signal]) -> list[BriefingItem]:
    signals_by_org: dict[str, list[Signal]] = defaultdict(list)
    for signal in signals:
        signals_by_org[signal.organisation].append(signal)
    ranked: list[BriefingItem] = []
    for account in watchlist:
        org_signals = signals_by_org.get(account.organisation_name, [])
        scores = calculate_scores(account, org_signals, dna)
        capabilities = top_capabilities(org_signals) or ["AI opportunity discovery"]
        assessment = build_assessment(account, org_signals, dna)
        ranked.append(BriefingItem(
            rank=0,
            organisation=account.organisation_name,
            sector=account.sector,
            scores=scores,
            why_interesting=f"{account.organisation_name} combines {account.sector} sector relevance, {account.priority.value} watchlist priority and {len(org_signals)} detected signal(s).",
            strongest_detected_signals=[signal.signal_summary for signal in strongest_signals(org_signals)],
            likely_capability_areas=capabilities,
            main_competitors_to_watch=account.known_competitors,
            recommended_next_action=assessment.recommended_actions[0].action_summary,
            assessment=assessment,
        ))
    return sorted(ranked, key=lambda item: item.scores.ai_reinvention_opportunity_score, reverse=True)


def generate_daily_brief(dna: CommercialDNA | None = None, watchlist: list[TargetAccount] | None = None, signals: list[Signal] | None = None) -> DailyBrief:
    """Generate a deterministic Flora Daily Intelligence Brief."""

    dna = dna or sample_commercial_dna()
    ranked = _ranked_items(dna, watchlist or sample_watchlist(), signals or sample_signals())
    top_items = [item.model_copy(update={"rank": index}) for index, item in enumerate(ranked[:5], start=1)]
    return DailyBrief(generated_for=dna.employer, business_unit=dna.business_unit, target_geographies=dna.target_geographies, items=top_items)


def generate_weekly_brief(dna: CommercialDNA | None = None, watchlist: list[TargetAccount] | None = None, signals: list[Signal] | None = None) -> WeeklyIntelligenceBrief:
    """Generate a deterministic weekly intelligence brief with seeded score movement."""

    dna = dna or sample_commercial_dna()
    ranked = _ranked_items(dna, watchlist or sample_watchlist(), signals or sample_signals())
    movers: list[WeeklyMover] = []
    for index, item in enumerate(ranked, start=1):
        previous = max(0, item.scores.ai_reinvention_opportunity_score - (8 - index))
        movers.append(WeeklyMover(organisation=item.organisation, sector=item.sector, previous_score=previous, current_score=item.scores.ai_reinvention_opportunity_score, score_change=item.scores.ai_reinvention_opportunity_score - previous, reason=item.why_interesting))
    new_evidence = [evidence for item in ranked[:5] if item.assessment for evidence in item.assessment.evidence]
    return WeeklyIntelligenceBrief(
        generated_for=dna.employer,
        business_unit=dna.business_unit,
        biggest_movers=sorted(movers, key=lambda mover: mover.score_change, reverse=True)[:5],
        score_changes=movers,
        new_evidence=new_evidence,
        organisations_to_watch=[item.organisation for item in ranked[:3]],
        organisations_to_deprioritise=[item.organisation for item in ranked[-2:]],
    )
