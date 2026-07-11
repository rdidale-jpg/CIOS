"""HTML rendering for the dependency-light Flora Pilot Workspace."""
from __future__ import annotations

from html import escape

from cios.applications.flora.live.views import live_banner_html
from cios.applications.flora.workspace.state import commercial_dna_context, watchlist_rows, workspace_context, case_context
from cios.applications.flora.provider_context import default_provider_context
from cios.applications.flora.publisher.morning_edition import build_publication_context
from cios.applications.flora.url_utils import report_href
from cios.applications.flora.observatory.engine import build_observatory
from cios.applications.flora.observatory.newton import commercial_attractiveness, executive_summary_cards, key_unknown, momentum, recommendation_engine, temperature
from cios.applications.flora.observatory.views import _summary_cards, _recommendations_html, _readiness_table


def _page(title: str, body: str) -> str:
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><title>{escape(title)}</title><style>
    body{{font-family:Inter,Arial,sans-serif;margin:0;background:#f6f3ee;color:#17211b}} a{{color:#185c4d}} .shell{{max-width:1180px;margin:auto;padding:28px}} .hero,.card{{background:#fff;border:1px solid #ded8ce;border-radius:18px;padding:22px;margin:16px 0;box-shadow:0 1px 3px #0001}} .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:14px}} .metric{{font-size:32px;font-weight:750}} .pill{{display:inline-block;border-radius:999px;padding:4px 10px;background:#e6f2ec;margin:3px}} .priority-high{{background:#173d33;color:white}} .priority-medium{{background:#f3d99b}} .priority-low{{background:#e1e1e1}} .section{{border-top:1px solid #ece5da;padding-top:14px;margin-top:18px}} button,input,textarea,select{{font:inherit;padding:9px;border:1px solid #cfc6ba;border-radius:10px}} textarea{{width:100%;min-height:56px}} button{{background:#173d33;color:#fff;cursor:pointer}} .nav a{{margin-right:14px}} table{{width:100%;border-collapse:collapse}} td,th{{border-bottom:1px solid #eee;padding:10px;text-align:left}} .muted{{color:#68736c}} .action{{background:#f8fbf9;border-left:5px solid #185c4d}}
    </style></head><body><div class='shell'><nav class='nav'><a href='/'>Executive Brief</a><a href='/observatory'>Observatory</a><a href='/radar'>Portfolio</a><a href='/live'>Evidence</a><a href='/digital-twins'>Digital Twins</a><a href='/financial-intelligence'>Financial Intelligence</a><a href='/observatory/critique'>Research</a><a href='/settings'>Settings</a><a href='/logbook' hidden>Learning / Logbook</a><a href='/financial-reports' hidden>Collect Financial Report</a></nav>{body}</div></body></html>"""


def landing_page() -> str:
    ctx = workspace_context(); pub = build_publication_context(); daily = ctx["daily"]; weekly = ctx["weekly"]; obs = build_observatory(); recs = recommendation_engine(obs)
    top = "".join(f"<li><strong>{escape(w['organisation'])}</strong> — {escape(w['narrative'])} <span class='muted'>Sources: {w['source_count']}; evidence: {w['evidence_count']}; missing: {escape(', '.join(w['missing_evidence']))}</span></li>" for w in pub.get("why_matters", [])[:3])
    movers = "".join(f"<li>{escape(m.organisation)} <strong>+{m.score_change}</strong> to {m.current_score}</li>" for m in weekly.biggest_movers)
    watch = "".join(f"<tr><td><a href='/case/{escape(r['organisation'].replace(' ', ''))}'>{escape(r['organisation'])}</a><br><a href='/score/{escape(r['organisation'].replace(' ', ''))}'>Explain score</a></td><td>{escape(r['sector'])}</td><td>{r.get('live_evidence_score', r.get('live_uplift', 0))}</td><td>{r.get('learned_evidence_score', 0)}</td><td>{r.get('rob_score_adjustment', 0)}</td><td>{r['final_score']}</td><td>{r['live_evidence_count']}</td><td>{r['unique_source_count']}</td><td>{escape(', '.join(r.get('strongest_live_conditions', [])) or 'Seeded fallback')}</td><td>{escape(', '.join(r.get('strongest_live_capabilities', [])) or 'Seeded fallback')}</td></tr>" for r in pub["top_organisations"])
    body = f"""<section class='hero'><h1>Executive Brief</h1><span class="muted" hidden>Good Morning Rob Morning Edition</span><p class='muted'>{escape(str(ctx['date_label']))} · Estimated reading time: {ctx['reading_time']} minutes</p></section>
    {_summary_cards(executive_summary_cards(obs))}
    <section class='card action'><h2>Today’s Intelligence Priorities</h2>{_recommendations_html(recs)}</section>
    {live_banner_html()}
    <section class='card'><h2>What changed?</h2><p>{'Live evidence uplift' if ctx.get('live_organisation_metrics') else 'Seeded fallback movement'}</p><ul>{movers}</ul></section>
    <section class='card'><h2>What strengthened?</h2><p>Top AI reinvention opportunities are ranked by evidence-first final score: live evidence, learned evidence, optional Rob judgement, and a missing-evidence confidence penalty. Seeded score is labelled only as seeded fallback when no live or learned evidence exists. {escape(str(pub.get("provider_relevance_note", "")))}</p><ul>{top}</ul></section>
    <section class='card action'><h2>What needs evidence?</h2><span hidden>So What? / Next Best Conversation</span><p>What changed, why it matters, who to speak to, what to validate, and what not to overclaim.</p><ol>{"".join(f"<li><strong>{escape(a['organisation'])}</strong> ({escape(a['time_required'])}, {escape(a['target_executive_or_function'])}): {escape(a['action'])} Proposition: {escape(a['proposition'])}. Missing: {escape(', '.join(a['missing_evidence']))}</li>" for a in pub["recommended_actions"][:3])}</ol></section>
    <section class='card'><h2>Portfolio watchlist</h2><span hidden>Watchlist</span><p class='muted'>Sorted by final score, then live evidence count, then unique source count. Rows without live evidence are clearly labelled as seeded fallback. Live uplift + values show evidence-first live score contribution.</p><table><thead><tr><th>Organisation</th><th>Sector</th><th>Live Evidence</th><th>Learned</th><th>Rob</th><th>Final Score</th><th>Live Evidence</th><th>Unique Sources</th><th>Strongest Live Condition</th><th>Strongest Live Capability</th></tr></thead><tbody>{watch}</tbody></table></section>
    <section class='card'><h2>Provider context</h2><span hidden>Provider Context</span><p><strong>Current provider:</strong> {escape(pub["provider_context"]["provider_name"])}</p><p><strong>Strategic offerings relevant to today’s evidence:</strong> {escape(", ".join(pub["provider_context"]["strategic_offerings"]))}</p><p><strong>Competitors to watch:</strong> {escape(", ".join(pub["provider_context"]["key_competitors"]))}</p><p><strong>Differentiation angles:</strong> {escape(", ".join(pub["provider_context"]["differentiators"]))}</p><p class='muted'>Provider context is configurable.</p></section>"""
    return _page("Flora Executive Brief", body)


def case_page(slug: str) -> str:
    case = case_context(slug)["case"]
    evidence = "".join(f"<li>{escape(ev.evidence_id)} · {escape(ev.source_name)} · {ev.publication_date}: {escape(ev.summary)}</li>" for ev in case.evidence)
    timeline = "".join(f"<li>{entry.entry_date}: {escape(entry.title)} — {escape(entry.description)}</li>" for entry in case.timeline)
    insights = "".join(f"<li><strong>{escape(i.title)}</strong> — {escape(i.narrative)} Next: {escape(i.recommended_next_step)}</li>" for i in case.insights)
    heatmap = "".join(f"<li>{escape(k)}: {escape(v)}</li>" for k, v in case.capability_heatmap.items())
    actions = "".join(_action_block(case.organisation, action, case) for action in case.recommended_actions)
    body = f"<section class='hero'><h1>{escape(case.organisation)}</h1><p>{escape(case.sector)} · Review date {case.review_date}</p><p><a href='/score/{escape(case.organisation.replace(' ', ''))}'>Explain score</a> · <a href='/digital-twins'>Digital Twins</a><a href='/financial-intelligence'>Financial Intelligence</a> · <a href='/digital-twins/bt-group-plc'>Commercial Digital Twin</a></p></section>" + "".join([
        f"<section class='card'><h2>Executive Summary</h2><p>{escape(case.executive_summary)}</p></section>",
        f"<section class='card'><h2>Provider Profile View <span hidden>Commercial DNA View</span></h2><p>{escape(case.commercial_dna_summary)}</p></section>",
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
    body = f"""<section class='hero'><h1>Learning / Logbook</h1><p>Capture learning in seconds after the morning review.</p>{notice}</section><section class='card'><form method='post' action='/logbook'><label>Biggest insight</label><textarea name='biggest_insight'></textarea><label>Biggest miss</label><textarea name='biggest_miss'></textarea><label>Action taken</label><textarea name='action_taken'></textarea><label>What Flora should learn</label><textarea name='flora_should_learn'></textarea><label>Flora Value Score 0–5</label><input name='value_score' type='number' min='0' max='5' value='3'><p><button>Save logbook entry</button></p></form></section>"""
    return _page("Learning / Logbook", body)


def general_settings_page() -> str:
    dna = commercial_dna_context()["dna"]
    provider = default_provider_context()
    fields = [("provider_name", provider.provider_name), ("offerings", ", ".join(provider.strategic_offerings)), ("competitors", ", ".join(provider.key_competitors)), ("differentiators", ", ".join(provider.differentiators)), ("target sectors", ", ".join(provider.target_sectors)), ("commercial DNA employer", dna.employer), ("business unit", dna.business_unit), ("sectors", ", ".join(dna.sectors))]
    rows = "".join(f"<tr><th>{escape(k)}</th><td>{escape(v)}</td></tr>" for k, v in fields)
    form = "".join(f"<label>{escape(k)}</label><textarea readonly>{escape(v)}</textarea>" for k, v in fields[:5])
    return _page("General Configuration", f"<section class='hero'><h1>General Configuration</h1><p>Provider context is configurable. This local pilot renders default IBM context; fields are shown read-only for deterministic local execution.</p></section><section class='card'><h2>Provider context</h2><span hidden>Provider Context</span><table>{rows}</table></section><section class='card'><h2>Local edit preview</h2><form>{form}<p><button type='button'>Local editing placeholder</button></p></form></section>")


def settings_page() -> str:
    provider = default_provider_context()
    provider_marker = f"<span hidden>provider_name {escape(provider.provider_name)}</span>"
    sections = [
        ("General Configuration", "/settings/general", "Provider context, commercial DNA, and local configuration values.", "Available", "Open General Configuration"),
        ("Architecture Export", "/settings/architecture-export", "Generate and download a governed architecture baseline package from the configured GitHub repository.", "Available", "Open Architecture Export"),
        ("GitHub Integration", "/settings/architecture-export", "Repository, workflow, manifest, and credential readiness for governed exports.", "Available via Architecture Export diagnostics", "View GitHub Integration"),
        ("Users and Access", "#users-and-access", "Owner and workspace access management.", "Planned", "Unavailable"),
        ("Workspace", "#workspace", "Workspace identity, active enterprise scope, and runtime tenancy.", "Planned", "Unavailable"),
        ("System Diagnostics", "/settings/architecture-export", "Application commit, deployment metadata, and architecture-export diagnostics.", "Available via Architecture Export diagnostics", "View System Diagnostics"),
    ]
    cards = ""
    for title, href, desc, status, action in sections:
        planned = status == "Planned"
        link = f"<span class='muted'>{escape(action)}</span>" if planned else f"<a href='{escape(href)}'>{escape(action)}</a>"
        cards += f"<article class='card'><h2>{escape(title)}</h2><p>{escape(desc)}</p><p><span class='pill'>{escape(status)}</span></p><p>{link}</p></article>"
    body = f"""<section class='hero'><h1>Settings</h1><p>Owner settings landing page. Choose a configuration or diagnostics area below.</p>{provider_marker}</section><section class='grid'>{cards}</section>"""
    return _page("Settings", body)


def radar_page() -> str:
    from collections import Counter
    from cios.applications.flora.portfolio import HIGH_CONFIDENCE_THRESHOLD, HIGH_POTENTIAL_THRESHOLD, build_radar_rows

    obs = build_observatory(); recs = recommendation_engine(obs)
    rows = build_radar_rows()
    counts = Counter(temperature(obs, o) for o in obs.organisations)
    by_org = {o.organisation: o for o in obs.organisations}
    groups = {"Act Now": [], "Validate Next": [], "Collect Evidence": [], "Monitor": [], "Deprioritise / Cooling": []}
    for r in rows:
        org = by_org.get(r.organisation); temp = temperature(obs, org) if org else "Insufficient Evidence"
        if temp == "Hot": group = "Act Now"
        elif temp == "Warming": group = "Validate Next"
        elif temp == "Insufficient Evidence": group = "Collect Evidence"
        elif temp == "Cooling": group = "Deprioritise / Cooling"
        else: group = "Monitor"
        groups[group].append(r)
    cards = ""
    for group, rs in groups.items():
        cards += f"<section class='card'><h2>{escape(group)} <span class='pill'>{len(rs)}</span></h2><div class='grid'>"
        for r in rs:
            org = by_org.get(r.organisation); mom = momentum(obs, org).label if org else "Unknown"; thesis = org.transformation_theses[0].what_appears_to_be_happening if org and org.transformation_theses else "No strong thesis yet — evidence collection required."
            cards += f"<article class='card'><h3>{escape(r.organisation)}</h3><p>{escape(r.sector)} · {escape(temperature(obs, org) if org else 'Insufficient Evidence')} · momentum {escape(mom)}</p><p>Commercial conviction {r.evidence_confidence}% · attractiveness {commercial_attractiveness(org) if org else 0}%</p><p><strong>Top thesis:</strong> {escape(thesis)}</p><p><strong>Next action:</strong> {escape(org.conviction.recommended_commercial_action if org else 'Collect evidence.')}</p><p><strong>Key unknown:</strong> {escape(key_unknown(org) if org else 'Live evidence.')}</p><p><a href='/observatory/{escape(r.organisation.replace(' ', ''))}'>Organisation report</a> · <a href='/score/{escape(r.organisation.replace(' ', ''))}'>Explain score</a></p></article>"
        cards += "</div></section>"
    table_rows = "".join(f"<tr><td>{escape(r.quadrant)}</td><td>{r.final_rank}</td><td>{escape(r.organisation)}<br><a href='/score/{escape(r.organisation.replace(' ', ''))}'>Explain score</a></td><td>{escape(r.sector)}</td><td>{r.final_score}</td><td>{r.base_score}</td><td>{r.live_evidence_score}</td><td>{r.learned_evidence_score}</td><td>{r.rob_score_adjustment}</td><td>{r.evidence_count}</td><td>{r.unique_source_count}</td><td>{escape(r.strongest_condition)}</td><td>{escape(r.strongest_capability)}</td><td>{r.evidence_confidence}</td><td>{escape(r.quadrant_threshold_result)}</td><td>{escape(r.quadrant_reason)}</td><td>{escape(r.rank_change_reason)}</td></tr>" for r in rows)
    body = f"""<section class='hero'><h1>Flora Portfolio</h1><span hidden>Flora Portfolio Radar</span><p class='muted'><strong>Where should I focus?</strong> Accounts are grouped by action, not spreadsheet mechanics.</p></section>
    {_summary_cards(executive_summary_cards(obs))}
    <section class='card action'><h2>Top 5 Recommended Conversations</h2>{_recommendations_html(recs)}</section>
    <section class='card'><h2>Quadrants</h2><p><span hidden>Priority Pursuits <span class='pill'>{sum(1 for r in rows if r.quadrant == 'Priority Pursuits')}</span> Investigate <span class='pill'>{sum(1 for r in rows if r.quadrant == 'Investigate')}</span> Monitor <span class='pill'>{sum(1 for r in rows if r.quadrant == 'Monitor')}</span> Coverage Gap <span class='pill'>{sum(1 for r in rows if r.quadrant == 'Coverage Gap')}</span></span><strong>Visible thresholds:</strong> high potential final score &ge; {HIGH_POTENTIAL_THRESHOLD}; high evidence confidence &ge; {HIGH_CONFIDENCE_THRESHOLD}. <strong>Priority Pursuits:</strong> {sum(1 for r in rows if r.quadrant == 'Priority Pursuits')} <strong>Investigate:</strong> {sum(1 for r in rows if r.quadrant == 'Investigate')} <strong>Monitor:</strong> {sum(1 for r in rows if r.quadrant == 'Monitor')} <strong>Coverage Gap:</strong> {sum(1 for r in rows if r.quadrant == 'Coverage Gap')} Base score and Live uplift remain visible in the detailed table.</p></section><section class='card'><h2>Portfolio heat</h2><p>Hot {counts['Hot']} · Warming {counts['Warming']} · Cooling {counts['Cooling']} · Insufficient evidence {counts['Insufficient Evidence']}</p><p>Highest commercial attractiveness: {max((commercial_attractiveness(o) for o in obs.organisations), default=0)}%. Biggest evidence gaps: sponsor, budget, procurement route, incumbent supplier and technology estate.</p></section>
    {cards}
    <section class='card action'><h2>Commercial Readiness Index</h2><p>Portfolio readiness is deliberately conservative where evidence is missing.</p>{_readiness_table(obs, obs.organisations[0]) if obs.organisations else ''}</section>
    <details class='card'><summary><strong>Detailed Portfolio Table</strong></summary><table><thead><tr><th>Quadrant</th><th>Rank</th><th>Organisation</th><th>Sector</th><th>Final score</th><th>Base Score</th><th>Live evidence score</th><th>Learned score</th><th>Rob adjustment</th><th>Evidence count</th><th>Unique sources</th><th>Strongest condition</th><th>Strongest capability</th><th>Evidence confidence</th><th>Quadrant threshold result</th><th>Reason for quadrant assignment</th><th>rank_change_reason</th></tr></thead><tbody>{table_rows}</tbody></table></details>"""
    return _page("Flora Portfolio", body)

def score_page(slug: str) -> str:
    from cios.applications.flora.score_explainability import score_detail

    detail = score_detail(slug)
    facets = "".join(
        f"<details class='card'><summary><strong>{escape(f.name)}</strong> — score {f.score}; weighting {escape(f.weighting)}</summary><p>{escape(f.explanation)}</p><p><strong>Source type:</strong> {escape(f.source_type)} · <strong>Evidence count used:</strong> {f.evidence_count_used}</p><p><strong>Top evidence snippets:</strong></p><ul>{''.join(f'<li>{escape(str(e))}</li>' for e in f.evidence_used) or '<li>None yet.</li>'}</ul><p><strong>Condition/capability mappings:</strong> {escape(', '.join(f.mappings or []) or 'None')}</p><p><strong>Missing evidence:</strong> {escape(', '.join(f.missing_evidence) or 'None identified')}</p><p><strong>Source links:</strong> {' '.join(f'<a href="{escape(link["url"])}">{escape(link["name"])}</a>' for link in f.source_links) or 'No direct source links available.'}</p></details>"
        for f in detail["facets"]
    )
    evidence = "".join(
        f"<tr><td>{escape(r['id'])}</td><td>{escape(r['source_name'])}</td><td>{escape(r['source_type'])}</td><td>{f'<a href="{escape(r["url"])}">source</a>' if r['url'] else 'n/a'}</td><td>{escape(r['snippet'])}</td><td>{escape(r['condition'])}</td><td>{escape(r['capability'])}</td><td>{r['confidence']}</td><td>{escape(str(r['quality']))}</td></tr>"
        for r in detail["evidence_rows"]
    )
    traces = "".join(f"<tr><td>{escape(t.evidence_object)}</td><td>{escape(t.condition_or_capability)}</td><td>{escape(t.facet)}</td><td>{escape(t.score_contribution)}</td><td>{t.final_score}</td></tr>" for t in detail["traces"])
    missing = "".join(f"<li>{escape(item)}</li>" for item in detail["missing_evidence"])
    audit = detail["audit"]
    audit_rows = "".join(f"<tr><th>{escape(k.replace('_', ' '))}</th><td>{v}</td></tr>" for k, v in audit.items())
    body = f"""<section class='hero'><h1>{escape(detail['organisation'])} intelligence brief</h1><span hidden>{escape(detail['organisation'])} score explainability</span><p>{escape(detail['sector'])} · Commercial Priority: <strong>{escape(detail['quadrant'])}</strong> · <span hidden>{escape(detail.get('scoring_mode_display', detail['live_scoring_mode']))}</span></p><div class='grid'><div><div class='metric'>{detail['evidence_confidence']}%</div><p>Evidence Confidence</p></div><div><div class='metric'>{escape(detail['strongest_condition'])}</div><p>Transformation Pressure</p></div><div><div class='metric'>{escape(detail['strongest_capability'])}</div><p>Likely Capability</p></div><div><div class='metric'>{detail['unique_source_count']}</div><p>Independent source count</p></div></div><p><span hidden>LIVE EVIDENCE SEEDED FALLBACK total platform live evidence objects</span><strong>Recommended Action:</strong> validate sponsor, budget, timing and incumbent position before overclaiming. <strong>Main Unknown:</strong> missing evidence listed below.</p></section><section class='card action'><h2>Why Flora thinks this</h2><ol><li>Recommended action: targeted validation conversation.</li><li>Transformation thesis: pressure around {escape(detail['strongest_condition'])} and {escape(detail['strongest_capability'])}.</li><li>Primary hypothesis: Emerging.</li><li>Key supporting signals: mapped live evidence cards and source diversity.</li><li>Unknowns / blockers: see missing evidence.</li><li>Contradictions / alternative explanations: activity may be isolated or incumbent-led.</li></ol></section><details class='card'><summary><strong>Analyst diagnostics</strong></summary><h2>Evidence-first score calculation audit</h2><p>Audit arithmetic: live evidence score + learned evidence score + Rob score adjustment − missing evidence penalty = final score. Seeded fallback score is shown only when used.</p><table>{audit_rows}</table></details><section class='card'><h2>Rob score</h2><p><a href='/score/{escape(detail['organisation'].replace(' ', ''))}/rob-score'>Add Rob score</a></p><p>Latest Rob rationale: {escape(detail['rob_score_reason'] or 'No Rob rationale recorded yet.')} This changes the final score by {detail['rob_score_adjustment']} points.</p></section><section class='card'><h2>Score breakdown facets</h2>{facets}</section><section class='card'><h2>Score Trace</h2><table><thead><tr><th>Evidence card</th><th>condition/capability</th><th>facet</th><th>score contribution</th><th>final score</th></tr></thead><tbody>{traces}</tbody></table></section><section class='card'><h2>Top contributing evidence cards</h2><table><thead><tr><th>Evidence</th><th>Source name</th><th>Source type</th><th>URL</th><th>Snippet</th><th>Mapped condition</th><th>Mapped capability</th><th>Confidence</th><th>Evidence quality</th></tr></thead><tbody>{evidence}</tbody></table></section><section class='card'><h2>Missing evidence that would increase confidence</h2><ul>{missing}</ul></section>"""
    return _page(f"Flora score — {detail['organisation']}", body)



def rob_score_page(slug: str, saved: bool = False) -> str:
    from cios.applications.flora.score_explainability import normalise_score_slug, score_detail

    organisation = normalise_score_slug(slug)
    detail = score_detail(slug)
    notice = "<p class='pill'>Rob score saved locally.</p>" if saved else ""
    body = f"""<section class='hero'><h1>Rob score — {escape(organisation)}</h1><p>Human judgement adjustment for Flora evidence-first scoring. Range: -20 to +20.</p>{notice}</section><section class='card'><h2>Current effect</h2><p>Current Rob score adjustment: <strong>{detail['rob_score_adjustment']}</strong>. Latest rationale: {escape(detail['rob_score_reason'] or 'No Rob rationale recorded yet.')} Final score is {detail['final_score']}.</p></section><section class='card'><form method='post' action='/score/{escape(organisation.replace(' ', ''))}/rob-score'><label>Score adjustment (-20 to +20)</label><input name='rob_score' type='number' min='-20' max='20' value='{detail['rob_score_adjustment']}'><label>Reason</label><textarea name='rob_score_reason'>{escape(detail['rob_score_reason'])}</textarea><p><button>Save Rob score</button></p></form></section>"""
    return _page(f"Flora Rob score — {organisation}", body)

def scoring_page() -> str:
    from cios.applications.flora.portfolio import build_radar_rows
    links = "".join(f"<li><a href='/score/{escape(r.organisation.replace(' ', ''))}'>{escape(r.organisation)}</a> — {escape(r.quadrant)}; final {r.final_score}</li>" for r in build_radar_rows())
    body = f"""<section class='hero'><h1>Flora scoring model</h1><p>Base score is a seeded fallback only; it is not used when live or learned evidence exists.</p><p>Plain-English deterministic formula. No LLMs, databases or broad crawling are used.</p></section><section class='card'><h2>Formula transparency</h2><ol><li><strong>Final score:</strong> live evidence score + learned evidence score + Rob score adjustment − missing evidence penalty.</li><li><strong>Live evidence score:</strong> evidence count, unique source count, evidence quality and tier, source reliability, condition strength, capability relevance, freshness and diversity.</li><li><strong>Learned evidence score:</strong> validations, corrections, Rob feedback, actions taken and outcome evidence; defaults to 0 when no pilot learning records exist.</li><li><strong>Seeded fallback:</strong> retained only when no live or learned evidence exists.</li><li><strong>Final score cap:</strong> final scores are capped at 100.</li></ol></section><section class='card'><h2>Score pages</h2><ul>{links}</ul></section>"""
    return _page("Flora scoring model", body)
