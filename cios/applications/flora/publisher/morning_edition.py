"""Generate Flora Morning Edition PDF and HTML publications."""
from __future__ import annotations

import json
import os
import zipfile
from collections import defaultdict
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from cios.applications.flora.intelligence.evidence_engine import get_seed_evidence
from cios.applications.flora.pipeline import generate_daily_brief, generate_weekly_brief
from cios.applications.flora.publisher.html_renderer import write_html
from cios.applications.flora.publisher.pdf_renderer import render_pdf
from cios.applications.flora.live.store import read_jsonl

VERSION = "0.2"
PUBLICATIONS_DIR = Path(os.environ.get("FLORA_PILOT_DIR", ".flora_pilot")) / "publications"
PREVIEW_DIR = Path("docs/Applications/Flora_Pilot_Preview")
COMPETITORS = ("IBM", "Accenture", "Capgemini", "Deloitte")
CANONICAL_NAMES = {"bt": "BT", "sse": "SSE", "bbc": "BBC"}
CONDITION_CARDS = [
    "Regulatory Pressure", "Operational Resilience", "Customer Trust", "Technology Debt",
    "AI Modernisation", "Operational Efficiency", "Digital Leadership", "Cost Pressure",
]
ACTION_GUIDANCE = {
    "Thames Water": {
        "target": "COO, Customer Operations and Asset Operations leads",
        "proposition": "Customer Operations or Asset Intelligence reinvention discovery",
        "why_now": "seeded resilience, leakage and customer trust pressure combine into a practical operating-performance conversation",
        "action": "Validate whether operational resilience and customer trust pressure are creating a Customer Operations or Asset Intelligence reinvention window.",
        "time_required": "20 minutes",
        "matters": "Thames Water is the clearest utilities-sector test of Rob's Commercial DNA: regulated pressure, operational resilience and customer trust all point to an executive conversation about measurable reinvention rather than generic AI. The likely proposition is asset intelligence or customer operations analytics, with incumbent and competitor context still unverified.",
    },
    "National Grid": {
        "target": "COO, Asset Management, Grid Planning and CIO functions",
        "proposition": "asset intelligence or grid forecasting discovery",
        "why_now": "seeded grid resilience and transition-complexity evidence suggest planning and forecasting pressure",
        "action": "Review grid investment and operational resilience evidence before proposing an asset intelligence or grid forecasting conversation.",
        "time_required": "15 minutes",
        "matters": "National Grid fits Rob's communications-adjacent infrastructure focus because network resilience, forecasting and asset planning mirror large-scale communications operating problems. The executive conversation should be about operational certainty and capital productivity, not broad transformation.",
    },
    "BT": {
        "target": "Network Operations, Enterprise Operations, COO and CIO functions",
        "proposition": "Network Operations AI reinvention discovery",
        "why_now": "seeded network automation and enterprise simplification signals support a focused service-assurance hypothesis",
        "action": "Assess whether network automation and enterprise simplification signals support a Network Operations AI reinvention conversation.",
        "time_required": "10 minutes",
        "matters": "BT is the strongest communications-sector fit. Flora believes the conversation should centre on network operations, service assurance and enterprise simplification because those areas connect Rob's AI reinvention lens to a credible executive operating agenda. Competitor activity is named only as context until evidenced.",
    },
    "Vodafone": {
        "target": "COO, Commercial Operations, Service Assurance and Sales Operations leaders",
        "proposition": "AI-enabled service assurance or sales operations automation discovery",
        "why_now": "seeded competitive pressure and simplification signals create a plausible entry point",
        "action": "Validate whether competitive pressure and operational simplification create an entry point for AI-enabled service assurance or sales operations automation.",
        "time_required": "15 minutes",
        "matters": "Vodafone gives Rob a communications-sector conversation where competitive pressure can be translated into operational simplification. The likely proposition is narrower than transformation: service assurance or sales operations automation with measurable productivity and retention outcomes.",
    },
    "United Utilities": {
        "target": "COO, Asset Operations, Leakage and Regulatory Performance teams",
        "proposition": "AI-enabled asset operations and leakage analytics discovery",
        "why_now": "seeded leakage analytics and regulated performance reporting evidence make the hypothesis specific",
        "action": "Validate whether leakage analytics and regulated performance reporting create an AI-enabled asset operations conversation.",
        "time_required": "15 minutes",
        "matters": "United Utilities is useful because it converts a regulated utilities problem into a precise AI operations discussion. Rob can test whether leakage analytics and performance reporting are strong enough to justify outreach before investing more time.",
    },
}


def display_name(name: str) -> str:
    return CANONICAL_NAMES.get(name.lower(), name)


def _reading_time(ctx_items: int, evidence_count: int) -> int:
    return max(7, round((ctx_items * 170 + evidence_count * 35 + 1300) / 220))


def _movement(change: int | None) -> str:
    if change is None or change == 0:
        return "No verified change"
    return f"+{change}" if change > 0 else str(change)


def _receipt(evts: list[Any]) -> list[dict[str, str]]:
    return [{"signal_ids": ", ".join(e.related_signals) or "missing", "summary": e.summary, "source_type": e.source_type, "evidence_status": "seeded"} for e in evts[:3]]


def build_publication_context(publication_date: date | None = None) -> dict[str, Any]:
    publication_date = publication_date or date.today()
    daily = generate_daily_brief()
    weekly = generate_weekly_brief()
    evidence = get_seed_evidence()
    live_evidence = read_jsonl()
    pilot_orgs = {"Thames Water", "National Grid", "BT", "Vodafone"}
    live_evidence = [item for item in live_evidence if item.get("organisation") in pilot_orgs]
    movement_by_org = {m.organisation: m.score_change for m in weekly.score_changes}
    evidence_by_org: dict[str, list[Any]] = defaultdict(list)
    for ev in evidence:
        evidence_by_org[ev.organisation].append(ev)

    top = daily.items[0]
    assessment = top.assessment
    assert assessment is not None
    evidence_count = sum(len(item.assessment.evidence) for item in daily.items if item.assessment)
    top_five = daily.items[:5]

    executive_summary = [
        "This is a seeded pilot edition. Treat movement as pilot movement inside Flora's deterministic sample set, not live market movement.",
        f"{display_name(top.organisation)} remains the priority because resilience, customer trust and AI reinvention fit are strongest in the current evidence.",
        "The report is now organised around change, commercial conditions, recommended action and evidence gaps rather than static ranking.",
        "No LLMs or databases are used. Live evidence, when present, is source-specific governed public HTML evidence stored locally as JSONL.",
    ]

    movers = sorted(top_five, key=lambda i: abs(movement_by_org.get(i.organisation, 0)), reverse=True)
    what_changed = {
        "summary": "Pilot movement is visible in the seeded weekly comparison. Live evidence receipts are shown first when locally available; otherwise these changes should guide review priorities rather than be read as real-world freshness.",
        "strongest_movers": [{"organisation": display_name(i.organisation), "movement": _movement(movement_by_org.get(i.organisation)), "reason": i.why_interesting} for i in movers[:3]],
        "meaningful_movement": [{"organisation": display_name(i.organisation), "movement": _movement(movement_by_org.get(i.organisation))} for i in top_five if abs(movement_by_org.get(i.organisation, 0)) >= 3],
        "strengthened": ["Operational Resilience", "Customer Trust", "AI Modernisation"],
        "weakened": ["No verified weakening detected in current pilot evidence."],
        "no_verified_change": [display_name(i.organisation) for i in daily.items if movement_by_org.get(i.organisation, 0) == 0],
    }

    priority_opportunity = {
        "Organisation": display_name(top.organisation),
        "What changed": f"{_movement(movement_by_org.get(top.organisation))} pilot movement in the seeded weekly comparison.",
        "AI Reinvention Assessment": assessment.commercial_summary,
        "Recommended Action": ACTION_GUIDANCE[top.organisation]["action"],
        "Why this matters to Rob": ACTION_GUIDANCE[top.organisation]["matters"],
        "Why Flora believes this": "; ".join(ev.evidence_summary for ev in assessment.evidence[:3]),
        "What evidence is missing": "; ".join(assessment.missing_evidence),
    }

    top_orgs = [{"organisation": display_name(item.organisation), "sector": item.sector, "condition_strength": item.scores.commercial_pressure_index, "ai_opportunity": item.scores.ai_reinvention_opportunity_score, "movement": _movement(movement_by_org.get(item.organisation)), "confidence": item.assessment.confidence if item.assessment else item.scores.ai_reinvention_opportunity_score} for item in top_five]

    condition_map = {name: {"condition": name, "strength": 0, "trend": "No verified change", "affected_organisations": [], "why_it_matters": "Evidence missing; retain as a watch condition until real evidence is ingested.", "evidence_status": "missing"} for name in CONDITION_CARDS}
    condition_orgs = {
        "Regulatory Pressure": ["Thames Water", "United Utilities"],
        "Operational Resilience": ["Thames Water", "National Grid"],
        "Customer Trust": ["Thames Water", "United Utilities"],
        "Technology Debt": ["BT", "Vodafone"],
        "AI Modernisation": ["BT", "Vodafone", "National Grid"],
        "Operational Efficiency": ["Vodafone", "United Utilities"],
        "Digital Leadership": ["BT", "National Grid"],
        "Cost Pressure": ["Thames Water", "Vodafone"],
    }
    items_by_org = {item.organisation: item for item in daily.items}
    for name, org_names in condition_orgs.items():
        orgs = [items_by_org[org] for org in org_names if org in items_by_org]
        if orgs:
            avg = round(sum(i.scores.commercial_pressure_index for i in orgs) / len(orgs))
            condition_map[name].update({
                "strength": avg,
                "trend": "Strengthened" if avg >= 75 else "Stable",
                "affected_organisations": [display_name(i.organisation) for i in orgs],
                "why_it_matters": f"Creates a focused executive conversation for {', '.join(display_name(i.organisation) for i in orgs[:3])} where AI can be tied to operating outcomes.",
                "evidence_status": "seeded",
            })
    conditions = [condition_map[name] for name in CONDITION_CARDS]

    # Sprint 3 editorial rule: do not turn generic seeded category placeholders into
    # executive, technology or regulatory movement claims. These sections require
    # verified movement evidence; the current pilot seed set does not provide it.
    movements = [
        {"title": "Executive appointments", "items": ["No verified executive movement detected in the current pilot evidence."]},
        {"title": "Technology announcements", "items": ["No verified technology movement detected in current pilot evidence."]},
        {"title": "Regulatory developments", "items": ["No verified regulatory movement detected in current pilot evidence."]},
    ]

    competitor_text = "\n".join(item.assessment.competitive_context for item in daily.items if item.assessment)
    competitive = {c: (f"Named in deterministic competitive context for: {', '.join(display_name(item.organisation) for item in daily.items if item.assessment and c in item.assessment.competitive_context)}. Validate incumbent position and competitor engagement before pursuit." if c in competitor_text else "No deterministic observation available in seeded Flora evidence.") for c in COMPETITORS}

    recommended_actions = []
    for idx, item in enumerate(top_five, start=1):
        a = item.assessment
        assert a is not None
        guide = ACTION_GUIDANCE[item.organisation]
        evts = evidence_by_org[item.organisation]
        recommended_actions.append({
            "priority": idx, "organisation": display_name(item.organisation), "target_executive_or_function": guide["target"], "proposition": guide["proposition"], "action": guide["action"], "why_now": guide["why_now"],
            "why_this_matters_to_rob": guide["matters"], "evidence_receipt": _receipt(evts), "live_evidence_receipt": [le for le in live_evidence if le.get("organisation") == item.organisation][:3],
            "missing_evidence": ["funding", "sponsor", "procurement timing", "incumbent position", "competitor engagement"], "time_required": guide["time_required"], "confidence": a.confidence,
        })

    today = [
        "10 minutes: Review Thames Water case file for operational resilience and customer trust conditions.",
        "15 minutes: Validate National Grid asset intelligence hypothesis with account knowledge.",
        "5 minutes: Decide whether BT should remain in the top-five watchlist for this week.",
    ]
    cannot_know = [
        "Live evidence v0.1 reads only configured public HTML pages; it does not ingest PDFs yet.", "No broad crawling is used.", "No real executive appointment feed has been ingested yet.",
        "This edition should be judged on structure, reasoning and usefulness — not real-world freshness.",
    ]

    live_banner = "LIVE EVIDENCE USED" if live_evidence else "NO LIVE EVIDENCE AVAILABLE — FALLING BACK TO SEEDED PILOT EVIDENCE"

    return {"product": "Flora Publisher", "edition": "Morning Edition", "version": VERSION, "publication_date": publication_date.isoformat(), "publication_date_label": publication_date.strftime("%A %d %B %Y"), "generated_timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC"), "live_evidence_banner": live_banner, "live_evidence": live_evidence[:12], "reading_time": _reading_time(len(daily.items), evidence_count), "executive_summary": executive_summary, "what_changed": what_changed, "priority_opportunity": priority_opportunity, "top_organisations": top_orgs, "conditions": conditions, "movements": movements, "competitive_intelligence": competitive, "recommended_actions": recommended_actions, "three_things_today": today, "cannot_know": cannot_know, "teach_flora": {"Biggest Insight": "", "Biggest Surprise": "", "Action Taken": "", "What Flora Should Learn": "", "Flora Value Score (0–5)": ""}, "case_files": sorted({display_name(ev.organisation) for ev in evidence}), "playbooks": sorted({pb for item in daily.items if item.assessment for pb in item.assessment.supporting_playbooks}), "commercial_laws": ["Validate sponsor", "Validate funding", "Validate timing", "Validate incumbent and competitor activity"], "known_limitations": ["Live evidence limited to configured public HTML source pages", "PDF ingestion not implemented", "No LLMs", "No databases", "No broad crawling", "Pilot placeholders remain blank on Teach Flora page"]}


def _latest_morning_stem(ctx: dict[str, Any]) -> str:
    return f"Morning_Edition_{ctx['publication_date']}"


def render_markdown(ctx: dict[str, Any]) -> str:
    lines = [f"# Flora Morning Edition — {ctx['publication_date']}", "", "**Confidential pilot preview.**", "", f"**Publication date:** {ctx['publication_date_label']}", f"**Version:** {ctx['version']}", f"**Reading time:** {ctx['reading_time']} minutes", f"**Generated:** {ctx['generated_timestamp']}", "", f"## {ctx['live_evidence_banner']}"]
    if ctx["live_evidence"]:
        lines += ["", "| Organisation | Source | URL | Snippet | Extracted | Condition | Missing evidence |", "| --- | --- | --- | --- | --- | --- | --- |"]
        lines += [f"| {e['organisation']} | {e['source_name']} | {e['source_url']} | {e['snippet']} | {e['extraction_timestamp']} | {e['commercial_condition']} | {'; '.join(e['missing_evidence'])} |" for e in ctx["live_evidence"]]
    else:
        lines += ["", "Seeded pilot evidence is used because no local live evidence JSONL was found."]
    lines += ["", "## Executive Summary"]
    lines += [f"- {x}" for x in ctx["executive_summary"]]
    wc = ctx["what_changed"]
    lines += ["", "## What Changed", "", wc["summary"], "", "### Strongest movers"]
    lines += [f"- **{m['organisation']}** — {m['movement']}: {m['reason']}" for m in wc["strongest_movers"]]
    lines += ["", "### Organisations with meaningful movement"] + [f"- **{m['organisation']}** — {m['movement']}" for m in wc["meaningful_movement"]]
    lines += ["", "### Conditions that strengthened"] + [f"- {x}" for x in wc["strengthened"]]
    lines += ["", "### Conditions that weakened"] + [f"- {x}" for x in wc["weakened"]]
    lines += ["", "### No verified change"] + ([f"- {x}" for x in wc["no_verified_change"]] or ["- No verified unchanged top-five organisations in the current pilot comparison."])
    lines += ["", "## Commercial Radar"]
    for c in ctx["conditions"]:
        lines += ["", f"### {c['condition']}", f"- **Condition strength:** {c['strength']}", f"- **Trend:** {c['trend']}", f"- **Affected organisations:** {', '.join(c['affected_organisations']) or 'None in seeded evidence'}", f"- **Why it matters:** {c['why_it_matters']}", f"- **Evidence status:** {c['evidence_status']}"]
    lines += ["", "## Today's Priority Opportunity"]
    for k, v in ctx["priority_opportunity"].items():
        lines += ["", f"### {k}", str(v)]
    lines += ["", "## Top Five Organisations", "", "| Organisation | Sector | Condition Strength | AI Opportunity | Movement | Confidence |", "| --- | --- | ---: | ---: | --- | ---: |"]
    lines += [f"| {r['organisation']} | {r['sector']} | {r['condition_strength']} | {r['ai_opportunity']} | {r['movement']} | {r['confidence']} |" for r in ctx["top_organisations"]]
    lines += ["", "## Executive & Market Movements"]
    for s in ctx["movements"]:
        lines += ["", f"### {s['title']}"] + [f"- {x}" for x in s["items"]]
    lines += ["", "## Competitive Intelligence"] + [f"- **{k}:** {v}" for k, v in ctx["competitive_intelligence"].items()]
    lines += ["", "## Recommended Actions"]
    for a in ctx["recommended_actions"]:
        lines += ["", f"### Priority {a['priority']} — {a['organisation']}", "", "## Why this matters to Rob", a["why_this_matters_to_rob"], "", f"- **Target executive or function:** {a['target_executive_or_function']}", f"- **Proposition:** {a['proposition']}", f"- **Action:** {a['action']}", f"- **Why now:** {a['why_now']}", f"- **Time required:** {a['time_required']}", f"- **Missing evidence:** {', '.join(a['missing_evidence'])}", "", "## Evidence Receipt", "", "| Signal IDs | Evidence summary | Source type | Evidence status |", "| --- | --- | --- | --- |"]
        if a.get("live_evidence_receipt"):
            lines += ["| Live evidence | " + e["snippet"] + " | " + e["source_type"] + " | " + e["source_name"] + " — " + e["source_url"] + " |" for e in a["live_evidence_receipt"]]
        lines += [f"| {e['signal_ids']} | {e['summary']} | {e['source_type']} | {e['evidence_status']} |" for e in a["evidence_receipt"]]
    lines += ["", "## Three Things Worth Doing Today"] + [f"- {x}" for x in ctx["three_things_today"]]
    lines += ["", "## What Flora Cannot Yet Know"] + [f"- {x}" for x in ctx["cannot_know"]]
    lines += ["", "## Teach Flora Notes"] + [f"- **{k}:** (blank for pilot feedback)" for k in ctx["teach_flora"]]
    lines += ["", "## Known Limitations"] + [f"- {x}" for x in ctx["known_limitations"]]
    return "\n".join(lines) + "\n"


def write_markdown(ctx: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown(ctx), encoding="utf-8")
    return output_path


def write_preview_html(ctx: dict[str, Any], output_path: Path) -> Path:
    md = render_markdown(ctx)
    html = "<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>Flora Morning Edition</title><style>body{font-family:Arial,sans-serif;line-height:1.5;max-width:980px;margin:2rem auto;padding:0 1rem;color:#102033}h1,h2,h3{color:#0b4f8a}table{border-collapse:collapse;width:100%}th,td{border:1px solid #dbe4ef;padding:.5rem;text-align:left;vertical-align:top}th{background:#eaf2fb}</style></head><body><pre style='white-space:pre-wrap;font-family:inherit'>" + md.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") + "</pre></body></html>"
    output_path.write_text(html, encoding="utf-8")
    return output_path


def write_release_notes(ctx: dict[str, Any], output_dir: Path, package_name: str) -> Path:
    notes = ["# Flora Morning Edition Release Notes", "", f"**Morning Edition version:** {ctx['version']}", f"**Publication date:** {ctx['publication_date']}", "", "## Files included", f"- `{package_name}`", f"- `{package_name.replace('.zip', '.pdf')}`", f"- `{package_name.replace('.zip', '.html')}`", "- `VERSION.json`", "- `index.html`", "- `previews/`", "", "## Known limitations", *(f"- {limitation}" for limitation in ctx["known_limitations"]), "", "## Instructions for downloading", "1. Download the Pilot Package ZIP from the GitHub Release assets.", "2. Extract the ZIP locally.", "3. Open `index.html` to browse publication files.", "", "Do not publish automatically; attach these prepared artefacts to a GitHub Release manually.", ""]
    path = output_dir / "RELEASE_NOTES.md"
    path.write_text("\n".join(notes), encoding="utf-8")
    return path


def write_preview_bundle(ctx: dict[str, Any], output_dir: Path = PREVIEW_DIR) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = _latest_morning_stem(ctx)
    md = write_markdown(ctx, output_dir / f"{stem}.md")
    html = write_preview_html(ctx, output_dir / f"{stem}.html")
    manifest = write_version_manifest(ctx, output_dir)
    readme = output_dir / "README.md"
    readme.write_text(f"# Flora Pilot Preview\n\nOpen `{stem}.md` in GitHub for the primary accessible text-only preview.\n\n## Files\n\n- `{stem}.md` — primary readable Morning Edition preview.\n- `{stem}.html` — text-only HTML fallback.\n- `VERSION.json` — deterministic preview manifest.\n- `RELEASE_NOTES.md` — release notes for this preview.\n\nNo PDFs, PNGs or ZIPs are committed in this preview directory.\n", encoding="utf-8")
    rn = output_dir / "RELEASE_NOTES.md"
    rn.write_text(f"# Flora Pilot Preview Release Notes\n\nThis PR delivers Flora Morning Edition v0.2 text-only preview for {ctx['publication_date']}.\n\n## Highlights\n\n- Adds What Changed.\n- Promotes Commercial Radar.\n- Adds Why this matters to Rob and Evidence Receipts.\n- Adds Three Things Worth Doing Today and What Flora Cannot Yet Know.\n\nPDF, PNG and ZIP artefacts remain local publisher outputs and are not committed.\n", encoding="utf-8")
    return {"markdown": md, "preview_html": html, "preview_manifest": manifest, "preview_readme": readme, "preview_release_notes": rn}


def write_pilot_package(output_dir: Path, stem: str) -> Path:
    zip_path = output_dir / f"{stem}.zip"
    required = [output_dir / f"{stem}.pdf", output_dir / f"{stem}.html", output_dir / "VERSION.json", output_dir / "index.html"]
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in required:
            if path.exists():
                archive.write(path, path.name)
        archive.writestr("previews/", "")
        previews_dir = output_dir / "previews"
        if previews_dir.exists():
            for preview in sorted(previews_dir.glob("*.png")):
                archive.write(preview, f"previews/{preview.name}")
    return zip_path


def write_version_manifest(ctx: dict[str, Any], output_dir: Path) -> Path:
    manifest = {key: ctx[key] for key in ("product", "edition", "version", "publication_date", "case_files", "conditions", "playbooks", "commercial_laws", "known_limitations")}
    path = output_dir / "VERSION.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path


def write_publication_index(output_dir: Path) -> Path:
    pdfs = sorted(output_dir.glob("Morning_Edition_*.pdf"), reverse=True)
    items = "".join(f"<li><a href='{p.name}'>{p.name}</a> · <a href='{p.with_suffix('.html').name}'>HTML</a></li>" for p in pdfs)
    path = output_dir / "index.html"
    path.write_text(f"<!doctype html><html><head><meta charset='utf-8'><title>Flora Publications</title><link rel='stylesheet' href='assets/flora_publisher.css'></head><body><main class='publication'><section class='page'><h1>FLORA</h1><h2>Publication Index</h2><ul>{items}</ul></section></main></body></html>", encoding="utf-8")
    return path


def generate_morning_edition(output_dir: Path | None = None, publication_date: date | None = None) -> dict[str, Path]:
    output_dir = output_dir or PUBLICATIONS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    ctx = build_publication_context(publication_date)
    stem = _latest_morning_stem(ctx)
    html_path = write_html(ctx, output_dir / f"{stem}.html")
    pdf_path = render_pdf(ctx, output_dir / f"{stem}.pdf")
    manifest_path = write_version_manifest(ctx, output_dir)
    index_path = write_publication_index(output_dir)
    release_notes_path = write_release_notes(ctx, output_dir, f"{stem}.zip")
    zip_path = write_pilot_package(output_dir, stem)
    paths = {"pdf": pdf_path, "html": html_path, "manifest": manifest_path, "index": index_path, "zip": zip_path, "release_notes": release_notes_path}
    return paths


def main() -> None:
    paths = generate_morning_edition()
    print(f"Flora Morning Edition generated: {paths['pdf'].resolve()}")
    print(f"HTML version: {paths['html'].resolve()}")
    print(f"Publication index: {paths['index'].resolve()}")
    print(f"Pilot Package ZIP: {paths['zip'].resolve()}")
    print(f"Release notes: {paths['release_notes'].resolve()}")


if __name__ == "__main__":
    main()
