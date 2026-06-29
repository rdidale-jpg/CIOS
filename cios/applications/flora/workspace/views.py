"""HTML rendering for the dependency-light Flora Pilot Workspace."""
from __future__ import annotations

from html import escape

from cios.applications.flora.live.views import live_banner_html
from cios.applications.flora.workspace.state import commercial_dna_context, watchlist_rows, workspace_context, case_context


def _page(title: str, body: str) -> str:
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><title>{escape(title)}</title><style>
    body{{font-family:Inter,Arial,sans-serif;margin:0;background:#f6f3ee;color:#17211b}} a{{color:#185c4d}} .shell{{max-width:1180px;margin:auto;padding:28px}} .hero,.card{{background:#fff;border:1px solid #ded8ce;border-radius:18px;padding:22px;margin:16px 0;box-shadow:0 1px 3px #0001}} .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:14px}} .metric{{font-size:32px;font-weight:750}} .pill{{display:inline-block;border-radius:999px;padding:4px 10px;background:#e6f2ec;margin:3px}} .priority-high{{background:#173d33;color:white}} .priority-medium{{background:#f3d99b}} .priority-low{{background:#e1e1e1}} .section{{border-top:1px solid #ece5da;padding-top:14px;margin-top:18px}} button,input,textarea,select{{font:inherit;padding:9px;border:1px solid #cfc6ba;border-radius:10px}} textarea{{width:100%;min-height:56px}} button{{background:#173d33;color:#fff;cursor:pointer}} .nav a{{margin-right:14px}} table{{width:100%;border-collapse:collapse}} td,th{{border-bottom:1px solid #eee;padding:10px;text-align:left}} .muted{{color:#68736c}} .action{{background:#f8fbf9;border-left:5px solid #185c4d}}
    </style></head><body><div class='shell'><nav class='nav'><a href='/'>Morning Edition</a><a href='/live'>Live Evidence</a><a href='/logbook'>Teach Flora / Pilot Logbook</a><a href='/settings'>Commercial DNA</a></nav>{body}</div></body></html>"""


def landing_page() -> str:
    ctx = workspace_context(); daily = ctx["daily"]; weekly = ctx["weekly"]
    top = "".join(f"<li><a href='/case/{escape(item.organisation.replace(' ', ''))}'>{escape(item.organisation)}</a> — {item.scores.ai_reinvention_opportunity_score}: {escape(item.why_interesting)}</li>" for item in daily.items[:3])
    movers = "".join(f"<li>{escape(m.organisation)} <strong>+{m.score_change}</strong> to {m.current_score}</li>" for m in weekly.biggest_movers)
    watch = "".join(f"<tr><td><a href='/case/{escape(row.slug)}'>{escape(row.organisation)}</a></td><td>{escape(row.sector)}</td><td>{row.score}</td><td>{'+' + str(row.movement) if row.movement is not None else '—'}</td><td><span class='pill priority-{escape(row.priority)}'>{escape(row.priority)}</span></td></tr>" for row in watchlist_rows())
    body = f"""<section class='hero'><h1>Good Morning Rob</h1><p class='muted'>{escape(str(ctx['date_label']))} · Estimated reading time: {ctx['reading_time']} minutes</p><div class='grid'><div><div class='metric'>{ctx['new_evidence_count']}</div><p>new evidence items</p></div><div><div class='metric'>{len(weekly.organisations_to_watch)}</div><p>organisations requiring attention</p></div><div><div class='metric'>{len(weekly.biggest_movers)}</div><p>biggest movers</p></div></div></section>
    {live_banner_html()}
    <section class='card'><h2>What changed?</h2><ul>{movers}</ul></section>
    <section class='card'><h2>Why does it matter?</h2><p>Top AI reinvention opportunities are ranked by deterministic commercial pressure, suitability, readiness, attractiveness and influence potential.</p><ul>{top}</ul></section>
    <section class='card action'><h2>What should I do?</h2><p><strong>Recommended priority action:</strong> {escape(str(ctx['priority_action']))}</p></section>
    <section class='card'><h2>Watchlist</h2><table><thead><tr><th>Organisation</th><th>Sector</th><th>AI Reinvention Opportunity Score</th><th>Movement</th><th>Priority</th></tr></thead><tbody>{watch}</tbody></table></section>"""
    return _page("Flora Morning Edition", body)


def case_page(slug: str) -> str:
    case = case_context(slug)["case"]
    evidence = "".join(f"<li>{escape(ev.evidence_id)} · {escape(ev.source_name)} · {ev.publication_date}: {escape(ev.summary)}</li>" for ev in case.evidence)
    timeline = "".join(f"<li>{entry.entry_date}: {escape(entry.title)} — {escape(entry.description)}</li>" for entry in case.timeline)
    insights = "".join(f"<li><strong>{escape(i.title)}</strong> — {escape(i.narrative)} Next: {escape(i.recommended_next_step)}</li>" for i in case.insights)
    heatmap = "".join(f"<li>{escape(k)}: {escape(v)}</li>" for k, v in case.capability_heatmap.items())
    actions = "".join(_action_block(case.organisation, action, case) for action in case.recommended_actions)
    body = f"<section class='hero'><h1>{escape(case.organisation)}</h1><p>{escape(case.sector)} · Review date {case.review_date}</p></section>" + "".join([
        f"<section class='card'><h2>Executive Summary</h2><p>{escape(case.executive_summary)}</p></section>",
        f"<section class='card'><h2>Commercial DNA View</h2><p>{escape(case.commercial_dna_summary)}</p></section>",
        f"<section class='card'><h2>Commercial Timeline</h2><ul>{timeline}</ul></section>",
        f"<section class='card'><h2>Evidence Ledger</h2><ul>{evidence}</ul></section>",
        f"<section class='card'><h2>Commercial Insights</h2><ul>{insights}</ul></section>",
        f"<section class='card'><h2>Pressure Profile</h2><p>{escape(case.pressure_profile)}</p></section>",
        f"<section class='card'><h2>AI Reinvention Assessment</h2><p>{escape(case.ai_reinvention_profile)}</p></section>",
        f"<section class='card'><h2>Capability Heatmap</h2><ul>{heatmap}</ul></section>",
        f"<section class='card'><h2>Competitive Context</h2><p>{escape(case.competitive_landscape)}</p></section>",
        f"<section class='card'><h2>Open Intelligence Questions</h2><ul>{''.join(f'<li>{escape(q)}</li>' for q in case.open_questions)}</ul></section>",
        f"<section class='card'><h2>Recommended Actions</h2>{actions}</section>",
    ])
    return _page(f"Flora Case File — {case.organisation}", body)


def _action_block(org: str, action: str, case) -> str:
    support = "; ".join(ev.summary for ev in case.evidence[:2])
    missing = "; ".join(case.open_questions[:3])
    return f"""<div class='card action'><h3>{escape(action)}</h3><h4>Explainability panel</h4><ul><li><strong>why this organisation:</strong> {escape(case.pressure_profile)}</li><li><strong>why now:</strong> Seeded evidence shows current pressure and movement.</li><li><strong>why this capability:</strong> {escape(case.ai_reinvention_profile)}</li><li><strong>why this executive:</strong> {escape(', '.join(case.executive_landscape) or 'Executive owner requires validation.')}</li><li><strong>why this proposition:</strong> Evidence-led AI reinvention discovery is low-friction.</li><li><strong>supporting evidence:</strong> {escape(support)}</li><li><strong>missing evidence:</strong> {escape(missing)}</li></ul><form method='post' action='/feedback'><input type='hidden' name='organisation' value='{escape(org)}'><input type='hidden' name='action_text' value='{escape(action)}'><input type='hidden' name='source_page' value='/case/{escape(org.replace(' ', ''))}'><textarea name='optional_comment' placeholder='Optional comment'></textarea><p><button name='feedback_type' value='Useful'>Useful</button> <button name='feedback_type' value='Not useful'>Not useful</button> <button name='feedback_type' value='I acted'>I acted</button> <button name='feedback_type' value='Needs correction'>Needs correction</button></p></form></div>"""


def logbook_page(saved: bool = False) -> str:
    notice = "<p class='pill'>Saved locally.</p>" if saved else ""
    body = f"""<section class='hero'><h1>Teach Flora / Pilot Logbook</h1><p>Capture learning in seconds after the morning review.</p>{notice}</section><section class='card'><form method='post' action='/logbook'><label>Biggest insight</label><textarea name='biggest_insight'></textarea><label>Biggest miss</label><textarea name='biggest_miss'></textarea><label>Action taken</label><textarea name='action_taken'></textarea><label>What Flora should learn</label><textarea name='flora_should_learn'></textarea><label>Flora Value Score 0–5</label><input name='value_score' type='number' min='0' max='5' value='3'><p><button>Save logbook entry</button></p></form></section>"""
    return _page("Teach Flora / Pilot Logbook", body)


def settings_page() -> str:
    dna = commercial_dna_context()["dna"]
    fields = [("employer", dna.employer), ("business unit", dna.business_unit), ("sectors", ", ".join(dna.sectors)), ("strategic offerings", ", ".join(dna.strategic_offerings)), ("competitors", ", ".join(dna.competitors)), ("differentiators", ", ".join(dna.differentiators)), ("reference clients", ", ".join(dna.reference_clients)), ("target geographies", ", ".join(dna.target_geographies))]
    rows = "".join(f"<tr><th>{escape(k.title())}</th><td>{escape(v)}</td></tr>" for k, v in fields)
    return _page("Commercial DNA", f"<section class='hero'><h1>Commercial DNA</h1><p>Read-only v0.3 pilot settings from seeded local configuration.</p></section><section class='card'><table>{rows}</table></section>")
