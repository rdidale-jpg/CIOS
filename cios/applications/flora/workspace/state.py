"""Deterministic view state for the Flora Pilot Workspace."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from cios.applications.flora.pipeline import generate_daily_brief, generate_weekly_brief
from cios.applications.flora.seed_data import sample_commercial_dna, sample_signals, sample_watchlist
from cios.applications.flora.scoring import calculate_scores
from cios.applications.flora.models import WeeklyMover
from cios.applications.flora.live.aggregation import aggregate_live_evidence, adjust_score, attention_organisations, unique_live_evidence
from cios.applications.flora.live.store import read_jsonl
from cios.applications.flora.intelligence.case_file import generate_case_file


@dataclass(frozen=True)
class WatchlistRow:
    slug: str
    organisation: str
    sector: str
    score: int
    movement: int | None
    priority: str


def slug_for(name: str) -> str:
    return name.replace(" ", "")


def today_label() -> str:
    return date.today().strftime("%A %d %B %Y")


def reading_time_minutes(item_count: int, evidence_count: int) -> int:
    return max(3, round((item_count * 110 + evidence_count * 35) / 220))


def workspace_context() -> dict[str, object]:
    daily = generate_daily_brief()
    weekly = generate_weekly_brief()
    live_evidence = unique_live_evidence(read_jsonl())
    live_metrics = aggregate_live_evidence(live_evidence)
    evidence_count = len(live_evidence) if live_evidence else sum(len(item.assessment.evidence) for item in daily.items if item.assessment)
    if live_evidence:
        adjustments = {item.organisation: adjust_score(item.organisation, item.scores.ai_reinvention_opportunity_score, live_metrics.get(item.organisation)) for item in daily.items}
        live_movers = [WeeklyMover(organisation=item.organisation, sector=item.sector, previous_score=adj.base_score, current_score=adj.final_score, score_change=adj.final_score - adj.base_score, reason=adj.reason) for item in daily.items if (adj := adjustments[item.organisation]).final_score > adj.base_score]
        weekly = weekly.model_copy(update={"organisations_to_watch": attention_organisations(daily.items, live_metrics, sample_watchlist()), "biggest_movers": sorted(live_movers, key=lambda mover: mover.score_change, reverse=True)[:5]})
    return {
        "daily": daily,
        "weekly": weekly,
        "date_label": today_label(),
        "reading_time": reading_time_minutes(len(daily.items), evidence_count),
        "new_evidence_count": evidence_count,
        "new_evidence_label": "live unique evidence objects" if live_evidence else "seeded fallback evidence items",
        "live_organisation_metrics": live_metrics,
        "priority_action": daily.items[0].recommended_next_action if daily.items else "Review seeded watchlist.",
    }


def watchlist_rows() -> list[WatchlistRow]:
    dna = sample_commercial_dna()
    signals = sample_signals()
    weekly = generate_weekly_brief()
    live_metrics = aggregate_live_evidence(unique_live_evidence(read_jsonl()))
    movement_by_org = {m.organisation: m.score_change for m in weekly.score_changes}
    rows: list[WatchlistRow] = []
    for account in sample_watchlist():
        account_signals = [signal for signal in signals if signal.organisation == account.organisation_name]
        scores = calculate_scores(account, account_signals, dna)
        adj = adjust_score(account.organisation_name, scores.ai_reinvention_opportunity_score, live_metrics.get(account.organisation_name))
        rows.append(WatchlistRow(slug=slug_for(account.organisation_name), organisation=account.organisation_name, sector=account.sector, score=adj.final_score, movement=(adj.final_score - adj.base_score) or movement_by_org.get(account.organisation_name), priority=account.priority.value))
    return rows


def case_context(slug: str) -> dict[str, object]:
    case = generate_case_file(slug)
    return {"case": case, "slug": slug_for(case.organisation)}


def commercial_dna_context() -> dict[str, object]:
    return {"dna": sample_commercial_dna()}
