"""Generate Flora Morning Edition PDF and HTML publications."""
from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from cios.applications.flora.intelligence.evidence_engine import EvidenceCategory, get_seed_evidence
from cios.applications.flora.pipeline import generate_daily_brief, generate_weekly_brief
from cios.applications.flora.publisher.html_renderer import write_html
from cios.applications.flora.publisher.pdf_renderer import render_pdf

VERSION = "0.1"
PUBLICATIONS_DIR = Path(os.environ.get("FLORA_PILOT_DIR", ".flora_pilot")) / "publications"
COMPETITORS = ("IBM", "Accenture", "Capgemini", "Deloitte")


def _reading_time(ctx_items: int, evidence_count: int) -> int:
    return max(5, round((ctx_items * 140 + evidence_count * 30 + 900) / 220))


def _movement(change: int | None) -> str:
    if change is None:
        return "No seeded movement"
    return f"+{change}" if change > 0 else str(change)


def build_publication_context(publication_date: date | None = None) -> dict[str, Any]:
    publication_date = publication_date or date.today()
    daily = generate_daily_brief()
    weekly = generate_weekly_brief()
    evidence = get_seed_evidence()
    movement_by_org = {m.organisation: m.score_change for m in weekly.score_changes}
    evidence_by_org = defaultdict(list)
    for ev in evidence:
        evidence_by_org[ev.organisation].append(ev)

    top = daily.items[0]
    assessment = top.assessment
    assert assessment is not None
    actions = [item.assessment.recommended_actions[0] for item in daily.items if item.assessment and item.assessment.recommended_actions][:5]
    evidence_count = sum(len(item.assessment.evidence) for item in daily.items if item.assessment)

    executive_summary = [
        f"{daily.items[0].organisation} is today's highest-ranked seeded opportunity with an AI reinvention score of {daily.items[0].scores.ai_reinvention_opportunity_score}.",
        f"The top five watchlist organisations span {', '.join(sorted({item.sector for item in daily.items}))}.",
        f"Seeded evidence contributes {evidence_count} traceable signal references across the top five organisations.",
        "Recommended actions remain discovery-led because sponsorship, funding, timing and competitor engagement are explicit evidence gaps.",
        "All observations are deterministic Flora outputs; no external APIs, LLMs or databases are used.",
    ][:5]

    priority_opportunity = {
        "Organisation": top.organisation,
        "Commercial Condition Profile": top.why_interesting,
        "AI Reinvention Assessment": assessment.commercial_summary,
        "Recommended Action": top.recommended_next_action,
        "Why Now": assessment.why_now,
        "Supporting Evidence": "; ".join(ev.evidence_summary for ev in assessment.evidence[:3]) or "No seeded supporting evidence available.",
        "Missing Evidence": "; ".join(assessment.missing_evidence),
    }

    top_orgs = [{
        "organisation": item.organisation,
        "sector": item.sector,
        "condition_strength": item.scores.commercial_pressure_index,
        "ai_opportunity": item.scores.ai_reinvention_opportunity_score,
        "movement": _movement(movement_by_org.get(item.organisation)),
        "confidence": item.assessment.confidence if item.assessment else item.scores.ai_reinvention_opportunity_score,
    } for item in daily.items]

    condition_strength: Counter[str] = Counter()
    condition_orgs: dict[str, set[str]] = defaultdict(set)
    condition_drivers: dict[str, list[str]] = defaultdict(list)
    for item in daily.items:
        for signal in item.strongest_detected_signals:
            condition_strength[signal] += item.scores.commercial_pressure_index
            condition_orgs[signal].add(item.organisation)
            condition_drivers[signal].extend(item.likely_capability_areas[:2])
    conditions = [{
        "condition": name,
        "strength": score,
        "trend": "Increasing" if score >= 160 else "Stable",
        "affected_organisations": sorted(condition_orgs[name]),
        "primary_drivers": ", ".join(sorted(set(condition_drivers[name]))[:4]),
    } for name, score in condition_strength.most_common(5)]

    by_category = defaultdict(list)
    for ev in evidence:
        by_category[ev.evidence_category].append(f"{ev.organisation}: {ev.extracted_observation}")
    movements = [
        {"title": "Executive appointments", "items": by_category.get(EvidenceCategory.EXECUTIVE_APPOINTMENT, ["No deterministic observations available."])[:5]},
        {"title": "Technology announcements", "items": by_category.get(EvidenceCategory.TECHNOLOGY_INVESTMENT, ["No deterministic observations available."])[:5]},
        {"title": "Regulatory developments", "items": by_category.get(EvidenceCategory.REGULATORY_PUBLICATION, ["No deterministic observations available."])[:5]},
        {"title": "Commercial interpretation", "items": ["Seeded movements indicate discovery should validate sponsor, funding, timing and incumbent activity before pursuit escalation."]},
    ]

    competitor_observations = {}
    competitor_text = "\n".join(item.assessment.competitive_context for item in daily.items if item.assessment)
    for competitor in COMPETITORS:
        if competitor in competitor_text:
            orgs = [item.organisation for item in daily.items if item.assessment and competitor in item.assessment.competitive_context]
            competitor_observations[competitor] = f"Named in deterministic competitive context for: {', '.join(orgs)}. No further observation is available in seeded evidence."
        else:
            competitor_observations[competitor] = "No deterministic observation available in seeded Flora evidence."

    recommended_actions = [{
        "priority": idx,
        "organisation": action.action_id.replace("FLORA-ACT-", "").replace("-001", "").replace("-", " ").title(),
        "reason": action.why_this_action,
        "expected_value": action.why_this_proposition,
        "confidence": action.confidence,
        "evidence_references": [ev.related_signal for ev in daily.items[idx-1].assessment.evidence] if daily.items[idx-1].assessment else [],
    } for idx, action in enumerate(actions, start=1)]

    return {
        "product": "Flora Publisher",
        "edition": "Morning Edition",
        "version": VERSION,
        "publication_date": publication_date.isoformat(),
        "publication_date_label": publication_date.strftime("%A %d %B %Y"),
        "generated_timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "reading_time": _reading_time(len(daily.items), evidence_count),
        "executive_summary": executive_summary,
        "priority_opportunity": priority_opportunity,
        "top_organisations": top_orgs,
        "conditions": conditions,
        "movements": movements,
        "competitive_intelligence": competitor_observations,
        "recommended_actions": recommended_actions,
        "teach_flora": {
            "Biggest Insight": "",
            "Biggest Surprise": "",
            "Action Taken": "",
            "What Flora Should Learn": "",
            "Flora Value Score (0–5)": "",
        },
        "case_files": sorted({ev.organisation for ev in evidence}),
        "playbooks": sorted({pb for item in daily.items if item.assessment for pb in item.assessment.supporting_playbooks}),
        "commercial_laws": ["Validate sponsor", "Validate funding", "Validate timing", "Validate incumbent and competitor activity"],
        "known_limitations": ["Seeded local evidence only", "No external APIs", "No LLMs", "No databases", "Pilot placeholders remain blank on Teach Flora page"],
    }


def write_version_manifest(ctx: dict[str, Any], output_dir: Path) -> Path:
    manifest = {key: ctx[key] for key in ("product", "edition", "version", "publication_date", "case_files", "conditions", "playbooks", "commercial_laws", "known_limitations")}
    path = output_dir / "VERSION.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path


def write_publication_index(output_dir: Path) -> Path:
    pdfs = sorted(output_dir.glob("Morning_Edition_*.pdf"), reverse=True)
    items = "".join(f"<li><a href='{p.name}'>{p.name}</a> · <a href='{p.with_suffix('.html').name}'>HTML</a></li>" for p in pdfs)
    html = f"<!doctype html><html><head><meta charset='utf-8'><title>Flora Publications</title><link rel='stylesheet' href='assets/flora_publisher.css'></head><body><main class='publication'><section class='page'><h1>FLORA</h1><h2>Publication Index</h2><ul>{items}</ul></section></main></body></html>"
    path = output_dir / "index.html"
    path.write_text(html, encoding="utf-8")
    return path


def generate_morning_edition(output_dir: Path | None = None, publication_date: date | None = None) -> dict[str, Path]:
    output_dir = output_dir or PUBLICATIONS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    ctx = build_publication_context(publication_date)
    stem = f"Morning_Edition_{ctx['publication_date']}"
    html_path = write_html(ctx, output_dir / f"{stem}.html")
    pdf_path = render_pdf(ctx, output_dir / f"{stem}.pdf")
    manifest_path = write_version_manifest(ctx, output_dir)
    index_path = write_publication_index(output_dir)
    return {"pdf": pdf_path, "html": html_path, "manifest": manifest_path, "index": index_path}


def main() -> None:
    paths = generate_morning_edition()
    print(f"Flora Morning Edition generated: {paths['pdf'].resolve()}")
    print(f"HTML version: {paths['html'].resolve()}")
    print(f"Publication index: {paths['index'].resolve()}")


if __name__ == "__main__":
    main()
