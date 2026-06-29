"""HTML rendering for the dependency-light Flora Pilot Workspace."""
from __future__ import annotations

from html import escape

from cios.applications.flora.live.views import live_banner_html
from cios.applications.flora.workspace.state import commercial_dna_context, watchlist_rows, workspace_context, case_context
from cios.applications.flora.provider_context import default_provider_context
from cios.applications.flora.publisher.morning_edition import build_publication_context


def _page(title: str, body: str) -> str:
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><title>{escape(title)}</title><style>
    body{{font-family:Inter,Arial,sans-serif;margin:0;background:#f6f3ee;color:#17211b}} a{{color:#185c4d}} .shell{{max-width:1180px;margin:auto;padding:28px}} .hero,.card{{background:#fff;border:1px solid #ded8ce;border-radius:18px;padding:22px;margin:16px 0;box-shadow:0 1px 3px #0001}} .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:14px}} .metric{{font-size:32px;font-weight:750}} .pill{{display:inline-block;border-radius:999px;padding:4px 10px;background:#e6f2ec;margin:3px}} .priority-high{{background:#173d33;color:white}} .priority-medium{{background:#f3d99b}} .priority-low{{background:#e1e1e1}} .section{{border-top:1px solid #ece5da;padding-top:14px;margin-top:18px}} button,input,textarea,select{{font:inherit;padding:9px;border:1px solid #cfc6ba;border-radius:10px}} textarea{{width:100%;min-height:56px}} button{{background:#173d33;color:#fff;cursor:pointer}} .nav a{{margin-right:14px}} table{{width:100%;border-collapse:collapse}} td,th{{border-bottom:1px solid #eee;padding:10px;text-align:left}} .muted{{color:#68736c}} .action{{background:#f8fbf9;border-left:5px solid #185c4d}}
    </style></head><body><div class='shell'><nav class='nav'><a href='/'>Morning Edition</a><a href='/radar'>Portfolio Radar</a><a href='/live'>Live Evidence</a><a href='/logbook'>Teach Flora / Pilot Logbook</a><a href='/settings'>Commercial DNA</a></nav>{body}</div></body></html>"""


def landing_page() -> str:
    ctx = workspace_context(); pub = build_publication_context(); daily = ctx["daily"]; weekly = ctx["weekly"]
    top = "".join(f"<li><strong>{escape(w['organisation'])}</strong> — {escape(w['narrative'])} <span class='muted'>Sources: {w['source_count']}; evidence: {w['evidence_count']}; missing: {escape(', '.join(w['missing_evidence']))}</span></li>" for w in pub.get("why_matters", [])[:3])
    movers = "".join(f"<li>{escape(m.organisation)} <strong>+{m.score_change}</strong> to {m.current_score}</li>" for m in weekly.biggest_movers)
    watch = "".join(f"<tr><td><a href='/case/{escape(r['organisation'].replace(' ', ''))}'>{escape(r['organisation'])}</a></td><td>{escape(r['sector'])}</td><td>{r['base_score']}</td><td><span class='pill'>{'Live uplift +' + str(r['live_uplift']) if r['live_uplift'] else 'Seeded fallback'}</span></td><td>{r['final_score']}</td><td>{r['live_evidence_count']}</td><td>{r['unique_source_count']}</td><td>{escape(', '.join(r.get('strongest_live_conditions', [])) or 'Seeded fallback')}</td><td>{escape(', '.join(r.get('strongest_live_capabilities', [])) or 'Seeded fallback')}</td></tr>" for r in pub["top_organisations"])
    body = f"""<section class='hero'><h1>Good Morning Rob</h1><p class='muted'>{escape(str(ctx['date_label']))} · Estimated reading time: {ctx['reading_time']} minutes</p><div class='grid'><div><div class='metric'>{ctx['new_evidence_count']}</div><p>{escape(str(ctx.get('new_evidence_label', 'new evidence items')))}</p></div><div><div class='metric'>{len(weekly.organisations_to_watch)}</div><p>organisations requiring attention</p></div><div><div class='metric'>{len(weekly.biggest_movers)}</div><p>biggest movers</p></div></div></section>
    {live_banner_html()}
    <section class='card'><h2>What changed?</h2><p>{'Live evidence uplift' if ctx.get('live_organisation_metrics') else 'Seeded fallback movement'}</p><ul>{movers}</ul></section>
    <section class='card'><h2>Why does it matter?</h2><p>Top AI reinvention opportunities are ranked by deterministic commercial pressure, suitability, readiness, attractiveness and influence potential. The Watchlist separates base score from live uplift so Rob can see whether rankings are seeded or evidence-backed. {escape(str(pub.get("provider_relevance_note", "")))}</p><ul>{top}</ul></section>
    <section class='card action'><h2>What should I do?</h2><ol>{"".join(f"<li><strong>{escape(a['organisation'])}</strong> ({escape(a['time_required'])}, {escape(a['target_executive_or_function'])}): {escape(a['action'])} Proposition: {escape(a['proposition'])}. Missing: {escape(', '.join(a['missing_evidence']))}</li>" for a in pub["recommended_actions"][:3])}</ol></section>
    <section class='card'><h2>Watchlist</h2><p class='muted'>Sorted by final score, then live evidence count, then unique source count. Rows without live evidence are clearly labelled as seeded fallback.</p><table><thead><tr><th>Organisation</th><th>Sector</th><th>Base Score</th><th>Live Uplift</th><th>Final Score</th><th>Live Evidence</th><th>Unique Sources</th><th>Strongest Live Condition</th><th>Strongest Live Capability</th></tr></thead><tbody>{watch}</tbody></table></section>
    <section class='card'><h2>Provider Context</h2><p><strong>Current provider:</strong> {escape(pub["provider_context"]["provider_name"])}</p><p><strong>Strategic offerings relevant to today’s evidence:</strong> {escape(", ".join(pub["provider_context"]["strategic_offerings"]))}</p><p><strong>Competitors to watch:</strong> {escape(", ".join(pub["provider_context"]["key_competitors"]))}</p><p><strong>Differentiation angles:</strong> {escape(", ".join(pub["provider_context"]["differentiators"]))}</p><p class='muted'>Provider context is configurable.</p></section>"""
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
    provider = default_provider_context()
    fields = [("provider_name", provider.provider_name), ("offerings", ", ".join(provider.strategic_offerings)), ("competitors", ", ".join(provider.key_competitors)), ("differentiators", ", ".join(provider.differentiators)), ("target sectors", ", ".join(provider.target_sectors)), ("commercial DNA employer", dna.employer), ("business unit", dna.business_unit), ("sectors", ", ".join(dna.sectors))]
    rows = "".join(f"<tr><th>{escape(k)}</th><td>{escape(v)}</td></tr>" for k, v in fields)
    form = "".join(f"<label>{escape(k)}</label><textarea readonly>{escape(v)}</textarea>" for k, v in fields[:5])
    return _page("Settings", f"<section class='hero'><h1>Settings</h1><p>Provider context is configurable. This local pilot renders default IBM context; fields are shown read-only for deterministic local execution.</p></section><section class='card'><h2>Provider Context</h2><table>{rows}</table></section><section class='card'><h2>Local edit preview</h2><form>{form}<p><button type='button'>Local editing placeholder</button></p></form></section>")


def radar_page() -> str:
    from collections import Counter
    from cios.applications.flora.portfolio import build_radar_rows

    rows = build_radar_rows()
    counts = Counter(r.quadrant for r in rows)
    dots = "".join(
        f"<div class='radar-dot' style='left:{min(98, max(2, r.final_score))}%;bottom:{min(98, max(2, r.evidence_confidence))}%' title='{escape(r.organisation)}'><strong>{escape(r.organisation)}</strong><br>{escape(r.sector)}<br>Final {r.final_score}; confidence {r.evidence_confidence}<br>{escape(r.quadrant)}</div>"
        for r in rows
    )
    table_rows = "".join(
        f"<tr><td>{escape(r.quadrant)}</td><td>{r.final_rank}</td><td>{escape(r.organisation)}</td><td>{escape(r.sector)}</td><td>{r.final_score}</td><td>{r.base_score}</td><td>+{r.live_uplift}</td><td>{r.evidence_count}</td><td>{r.unique_source_count}</td><td>{escape(r.strongest_condition)}</td><td>{escape(r.strongest_capability)}</td><td>{r.evidence_confidence}</td><td>{escape(r.rank_change_reason)}</td></tr>"
        for r in rows
    )
    body = f"""<section class='hero'><h1>Flora Portfolio Radar</h1><p class='muted'>A dependency-light 2D organisation grid: X-axis is AI Reinvention Potential / final score; Y-axis is Evidence Confidence / source quality.</p></section>
    <style>.radar{{position:relative;height:620px;background:linear-gradient(90deg,#fff7e8 50%,#eff8ef 50%);border:1px solid #ded8ce;border-radius:18px;margin:18px 0}}.radar:before{{content:'';position:absolute;left:50%;top:0;bottom:0;border-left:2px dashed #b7afa4}}.radar:after{{content:'';position:absolute;left:0;right:0;top:45%;border-top:2px dashed #b7afa4}}.quad{{position:absolute;font-weight:800;background:#ffffffcc;padding:6px;border-radius:8px}}.q1{{right:12px;top:12px}}.q2{{right:12px;bottom:12px}}.q3{{left:12px;top:12px}}.q4{{left:12px;bottom:12px}}.radar-dot{{position:absolute;transform:translate(-50%,50%);max-width:140px;background:#173d33;color:#fff;border-radius:10px;padding:5px;font-size:11px;box-shadow:0 2px 6px #0003}}</style>
    <section class='card'><h2>Quadrants</h2><ul><li><strong>Priority Pursuits:</strong> high potential, high evidence confidence ({counts['Priority Pursuits']})</li><li><strong>Investigate:</strong> high potential, low evidence confidence ({counts['Investigate']})</li><li><strong>Monitor:</strong> low potential, high evidence confidence ({counts['Monitor']})</li><li><strong>Coverage Gap:</strong> low potential, low evidence confidence ({counts['Coverage Gap']})</li></ul></section>
    <section class='radar'><div class='quad q1'>Monitor</div><div class='quad q2'>Priority Pursuits</div><div class='quad q3'>Coverage Gap</div><div class='quad q4'>Investigate</div>{dots}</section>
    <section class='card action'><h2>Scoring transparency</h2><p>Top organisations are ranked by deterministic seeded base score plus live uplift. Base score comes from commercial pressure, AI suitability, readiness, attractiveness and influence potential. Live uplift is capped and comes from governed live evidence count, source diversity, relevant conditions and source quality. The <code>rank_change_reason</code> column explains whether live evidence changed the rank or whether seeded base score still dominates.</p></section>
    <section class='card'><h2>Portfolio table grouped by quadrant</h2><table><thead><tr><th>Quadrant</th><th>Rank</th><th>Organisation</th><th>Sector</th><th>Final score</th><th>Base score</th><th>Live uplift</th><th>Evidence count</th><th>Unique sources</th><th>Strongest condition</th><th>Strongest capability</th><th>Evidence confidence</th><th>rank_change_reason</th></tr></thead><tbody>{table_rows}</tbody></table></section>"""
    return _page("Flora Portfolio Radar", body)
