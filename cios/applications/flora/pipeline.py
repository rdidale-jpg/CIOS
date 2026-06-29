"""Flora v0.1 briefing generation pipeline."""

from __future__ import annotations

from collections import defaultdict

from cios.applications.flora.models import BriefingItem, CommercialDNA, DailyBrief, Signal, TargetAccount
from cios.applications.flora.scoring import calculate_scores, strongest_signals, top_capabilities
from cios.applications.flora.seed_data import sample_commercial_dna, sample_signals, sample_watchlist


def generate_daily_brief(dna: CommercialDNA | None = None, watchlist: list[TargetAccount] | None = None, signals: list[Signal] | None = None) -> DailyBrief:
    """Generate a deterministic Flora Daily Intelligence Brief."""

    dna = dna or sample_commercial_dna()
    watchlist = watchlist or sample_watchlist()
    signals = signals or sample_signals()
    signals_by_org: dict[str, list[Signal]] = defaultdict(list)
    for signal in signals:
        signals_by_org[signal.organisation].append(signal)

    ranked: list[BriefingItem] = []
    for account in watchlist:
        org_signals = signals_by_org.get(account.organisation_name, [])
        scores = calculate_scores(account, org_signals, dna)
        strong = strongest_signals(org_signals)
        capabilities = top_capabilities(org_signals) or ["AI opportunity discovery"]
        why = f"{account.organisation_name} combines {account.sector} sector relevance, {account.priority.value} watchlist priority and {len(org_signals)} detected signal(s)."
        action = f"Prepare a 30-minute discovery hypothesis focused on {', '.join(capabilities[:2])}."
        ranked.append(BriefingItem(rank=0, organisation=account.organisation_name, sector=account.sector, scores=scores, why_interesting=why, strongest_detected_signals=[signal.signal_summary for signal in strong], likely_capability_areas=capabilities, main_competitors_to_watch=account.known_competitors, recommended_next_action=action))

    ranked.sort(key=lambda item: item.scores.ai_reinvention_opportunity_score, reverse=True)
    top_items = [item.model_copy(update={"rank": index}) for index, item in enumerate(ranked[:5], start=1)]
    return DailyBrief(generated_for=dna.employer, business_unit=dna.business_unit, target_geographies=dna.target_geographies, items=top_items)
