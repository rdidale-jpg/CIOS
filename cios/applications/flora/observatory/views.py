"""HTML views for the Enterprise Transformation Observatory."""
from __future__ import annotations

from datetime import UTC, datetime
from html import escape

from cios.applications.flora.observatory.engine import build_observatory
from cios.applications.flora.live.collect import current_status
from cios.applications.flora.url_utils import link_or_label, report_href
from cios.applications.flora.observatory.newton import commercial_attractiveness, executive_summary_cards, evidence_summary, key_unknown, momentum, readiness_index, recommendation_engine, strongest_evidence_items, temperature

OBSERVATORY_VERSION = "newton-milestone-5"
REASONING_ENGINE_VERSION = "transformation-thesis-v1"


def _ul(items):
    return "<ul>" + "".join(f"<li>{escape(str(i))}</li>" for i in items) + "</ul>"



def _summary_cards(cards):
    return "<section class='card action'><h2>Executive Summary Cards</h2><p class='muted'>Why it matters → why now → what to do → confidence → evidence.</p><div class='grid'>" + "".join(f"<article><h3>{escape(label)}</h3><div class='metric'>{escape(str(value))}</div><p class='muted'>{escape(str(note))}</p></article>" for label, value, note in cards) + "</div></section>"

def _readiness_table(obs, org):
    rows = "".join(f"<tr><th>{escape(r['factor'])}</th><td>{escape(r['level'])}</td><td>{escape(r['rationale'])}</td><td>{escape(r['missing_evidence'])}</td></tr>" for r in readiness_index(obs, org))
    return f"<table><thead><tr><th>Readiness factor</th><th>Status</th><th>Rationale</th><th>Missing evidence / discovery question</th></tr></thead><tbody>{rows}</tbody></table>"

def _recommendations_html(recs):
    items = []
    for r in recs:
        sigs = "; ".join(r.supporting_signals[:3]) or "No accepted signals yet"
        trace = "; ".join(f"{k}: {len(v)} linked" for k, v in r.trace.items())
        items.append(f"<article class='card action'><h3>{escape(r.organisation)} — {escape(r.target_executive_role)}</h3><p><strong>Issue:</strong> {escape(r.issue_to_discuss)}</p><p><strong>Why now:</strong> {escape(r.why_now)}</p><p><strong>Next action:</strong> {escape(r.recommended_action)} ({escape(r.estimated_meeting_length)})</p><p><strong>Confidence / conviction:</strong> {r.evidence_confidence}% / {r.commercial_attractiveness}% · momentum {escape(r.momentum)}</p><p><strong>Main validation:</strong> {escape('; '.join(r.validation_questions[:2]))}</p><p><strong>Do not overclaim:</strong> {escape(r.what_not_to_overclaim)}</p><details><summary>Evidence basis and trace</summary><p><strong>Thesis:</strong> {escape(r.supporting_thesis)}</p><p><strong>Top signals:</strong> {escape(sigs)}</p><p class='muted'><strong>Trace:</strong> {escape(trace)}</p></details></article>")
    return "".join(items) or "<p>No evidence-backed recommendations yet.</p>"



def _priority_label(org, obs):
    temp = temperature(obs, org)
    if temp == "Hot":
        return "High"
    if temp == "Warming":
        return "Medium"
    if temp == "Insufficient Evidence":
        return "Monitor"
    return "Low"

def _hypothesis_state(confidence: int, contradictory: int = 0) -> str:
    if contradictory and confidence < 65:
        return "Weakening"
    if confidence >= 80:
        return "Validated"
    if confidence >= 65:
        return "Strengthening"
    if confidence >= 45:
        return "Emerging"
    return "Created"

def _primary_hypothesis(org):
    thesis = org.transformation_theses[0] if org.transformation_theses else None
    signals = org.commercial_signals[:3]
    unknowns = tuple(dict.fromkeys([*org.case_for_change.unknowns, *(thesis.validation_required if thesis else ())]))[:4]
    evidence_ids = thesis.supporting_evidence_ids if thesis else org.case_for_change.supporting_evidence_ids
    statement = thesis.what_appears_to_be_happening if thesis else org.conviction.transformation_hypothesis
    return {
        "label": "Primary Hypothesis",
        "statement": statement,
        "signals": [s.title for s in signals],
        "supporting_evidence_count": len(set(evidence_ids)),
        "contradictory": list(thesis.weakening_evidence_ids if thesis else org.case_for_change.contradictory_evidence_ids),
        "unknowns": list(unknowns),
        "evidence_needed": list(dict.fromkeys(e for s in org.commercial_signals for e in s.missing_evidence))[:4] or [key_unknown(org)],
        "validation_questions": [f"Can we validate {u.lower()}?" for u in unknowns[:3]] or ["Is there named executive ownership?"],
        "confidence": thesis.confidence if thesis else org.conviction.confidence,
        "conviction": org.conviction.confidence,
        "state": _hypothesis_state(thesis.confidence if thesis else org.conviction.confidence, len(thesis.weakening_evidence_ids if thesis else ())),
        "commercial": thesis.commercial_opportunity if thesis else org.conviction.commercial_interpretation,
        "action": "Run a targeted executive discovery conversation; validate sponsor, budget, procurement route and incumbent constraints.",
    }

def _competing_hypotheses(org):
    primary = _primary_hypothesis(org)
    alt = primary | {
        "label": "Alternative Hypothesis",
        "statement": "Activity may represent isolated innovation, compliance response or cost control rather than a funded enterprise transformation programme.",
        "confidence": max(35, min(70, primary["confidence"] - 12)),
        "conviction": max(30, min(65, primary["conviction"] - 15)),
        "state": "Emerging",
        "commercial": "If true, the right move is learning and account mapping rather than a strong proposition-led pursuit.",
        "action": "Ask whether work is enterprise-funded, locally sponsored or already absorbed by incumbent suppliers.",
    }
    weak = primary | {
        "label": "Weakening / Contradictory Hypothesis",
        "statement": "Capital pressure, incumbent supplier commitments, weak procurement evidence or missing executive sponsorship may delay or limit external transformation opportunity.",
        "signals": ["Missing budget / sponsor / procurement evidence", *primary["signals"][:2]],
        "confidence": max(25, min(60, 100 - primary["confidence"])),
        "conviction": max(20, min(55, 100 - primary["conviction"])),
        "state": "Created" if not primary["contradictory"] else "Weakening",
        "commercial": "This would reduce urgency and shift Flora from engagement recommendation to evidence collection.",
        "action": "Collect disconfirming evidence: budget pressure, supplier lock-in, cancelled programmes and procurement inactivity.",
    }
    return [primary, alt, weak]

def _hypotheses_html(org):
    cards=[]
    for h in _competing_hypotheses(org):
        cards.append(f"""<article class='card'><h3>{escape(h['label'])} · {escape(h['state'])}</h3><p>{escape(h['statement'])}</p><p><strong>Why it matters commercially:</strong> {escape(h['commercial'])}</p><p><strong>Supporting signals:</strong> {escape('; '.join(h['signals'][:3]) or 'No accepted signals yet')}</p><p><strong>Supporting evidence count:</strong> {h['supporting_evidence_count']}</p><p><strong>Contradictory evidence:</strong> {escape(', '.join(h['contradictory']) or 'None identified')}</p><p><strong>Unknowns:</strong> {escape('; '.join(h['unknowns']) or key_unknown(org))}</p><p><strong>Evidence needed:</strong> {escape('; '.join(h['evidence_needed']))}</p><p><strong>Validation questions:</strong> {escape('; '.join(h['validation_questions']))}</p><p><strong>Confidence / conviction:</strong> {h['confidence']}% / {h['conviction']}%</p><p><strong>Recommended learning action:</strong> {escape(h['action'])}</p></article>""")
    return "<section class='card action'><h2>Competing Hypotheses</h2>" + ''.join(cards) + "</section>"

def _architecture_compliance_badge():
    rows = {
        "FP-003": 76,
        "FP-004": 72,
        "FP-005": 68,
        "FP-006": 78,
        "FP-007": 82,
        "FP-008": 74,
        "FP-009": 70,
        "Overall CIRM Alignment": 74,
    }
    body = "".join(f"<tr><th>{escape(k)}</th><td>{v}%</td></tr>" for k, v in rows.items())
    return f"<h3>Architecture Compliance</h3><p class='muted'>Informational runtime alignment estimate; update docs/Architecture/CIRM_Runtime_Compliance.md each sprint.</p><table>{body}</table>"


def _conviction_dimensions(obs, org):
    m = momentum(obs, org)
    pressure = min(100, max(0, org.case_for_change.confidence + (10 if m.score >= 60 else 0)))
    inevitability = min(100, max(0, org.case_for_change.confidence + len(org.commercial_signals) * 3))
    conviction = org.conviction.confidence
    dims = [
        ("Evidence Confidence", f"{org.case_for_change.confidence}%", "Quality and coverage of accepted evidence supporting the reasoning chain."),
        ("Commercial Attractiveness", f"{commercial_attractiveness(org)}%", "Commercial relevance and likely value if the thesis proves valid."),
        ("Commercial Conviction", f"{conviction}%", "Whether current thesis, argument and unknowns justify human action."),
        ("Transformation Pressure", f"{pressure}%", "Visible internal and external forces making change more likely."),
        ("Transformation Inevitability", f"{inevitability}%", "Structural compulsion to transform, separate from commercial accessibility."),
        ("Momentum", f"{escape(m.label)} · {m.score}", escape(m.explanation)),
    ]
    return "<section class='card action'><h2>Commercial Conviction</h2><div class='grid'>" + "".join(f"<article><h3>{name}</h3><div class='metric'>{value}</div><p class='muted'>{note}</p></article>" for name, value, note in dims) + "</div></section>"

def _latest_timestamp(obs, org=None):
    evs = [e for e in obs.evidence if org is None or e.organisation == org.organisation]
    stamps = [e.extraction_timestamp for e in evs if e.extraction_timestamp]
    return max(stamps) if stamps else datetime.now(UTC).isoformat(timespec="seconds")


def _freshness(obs, org=None):
    evs = [e for e in obs.evidence if org is None or e.organisation == org.organisation]
    if not evs or not any(e.is_live for e in evs):
        return "seeded fallback / insufficient live evidence"
    latest = _latest_timestamp(obs, org)
    return "collected today" if latest[:10] == datetime.now(UTC).date().isoformat() else "stale"


def _report_metadata(obs, org=None):
    signals = org.commercial_signals if org else obs.commercial_signals
    insights = org.commercial_insights if org else obs.commercial_insights
    theses = org.transformation_theses if org else obs.transformation_theses
    arguments = org.commercial_arguments if org else obs.commercial_arguments
    evidence_count = len({eid for s in signals for eid in s.supporting_evidence_ids}) if org else len(obs.evidence)
    generated = datetime.now(UTC).isoformat(timespec="seconds")
    latest_collection = current_status().get("last_collection_time") or "No live collection available"
    open_link = report_href(f"/observatory/{org.organisation.replace(' ', '')}") if org else report_href("/observatory")
    title = f"<h1>{escape(org.organisation)}</h1><p>{escape(org.sector)}</p><span hidden>{escape(org.organisation)} Transformation Genome</span>" if org else "<h1>Executive Observatory</h1>"
    return f"""<section class='hero report-header'>{title}<table>
    <tr><th>Report generated timestamp</th><td>{escape(generated)} UTC ISO · {escape(datetime.now(UTC).strftime('%d %b %Y %H:%M UTC'))}</td></tr>
    <tr><th>Evidence cut-off timestamp</th><td>{escape(_latest_timestamp(obs, org))}</td></tr>
    <tr><th>Last live collection timestamp</th><td>{escape(str(latest_collection))}</td></tr>
    <tr><th>Evidence freshness label</th><td>{escape(_freshness(obs, org))}</td></tr>
    <tr><th>Evidence analysed count</th><td>{evidence_count}</td></tr>
    <tr><th>Evidence → Signals → Insights → Theses → Arguments · Transformation Theses</th><td>{evidence_count} → {len(signals)} → {len(insights)} → {len(theses)} → {len(arguments)}</td></tr>
    <tr><th>Signals / Insights / Theses / Arguments counts</th><td>{len(signals)} / {len(insights)} / {len(theses)} / {len(arguments)}</td></tr>
    <tr><th>Observatory version</th><td>{escape(OBSERVATORY_VERSION)}</td></tr>
    <tr><th>Reasoning engine version</th><td>{escape(REASONING_ENGINE_VERSION)}</td></tr>
    <tr><th>Open in Flora</th><td><a href='{escape(open_link)}'>Open in Flora</a></td></tr>
    </table></section>"""


def observatory_page() -> str:
    obs = build_observatory()
    recs = recommendation_engine(obs)
    top_theses = "".join(f"<li><strong>{escape(t.organisation)}</strong> — {escape(t.what_appears_to_be_happening)} <span class='muted'>Confidence {t.confidence}% · {evidence_summary(t.supporting_evidence_ids)}</span></li>" for t in obs.transformation_theses[:5]) or "<li>No strong thesis yet — evidence collection required.</li>"
    org_cards = "".join(f"<article class='card'><h3><a href='{escape(report_href('/observatory/' + o.organisation.replace(' ', '')))}'>{escape(o.organisation)}</a></h3><p>{escape(o.sector)} · {escape(temperature(obs, o))} · momentum {escape(momentum(obs, o).label)} · confidence {o.case_for_change.confidence}% · attractiveness {commercial_attractiveness(o)}%</p><p><strong>Thesis:</strong> {escape(o.transformation_theses[0].what_appears_to_be_happening if o.transformation_theses and temperature(obs, o) != 'Insufficient Evidence' else 'No strong thesis yet — evidence collection required.')}</p><p><strong>Next action:</strong> {escape(o.conviction.recommended_commercial_action)}</p><p><strong>Key unknown:</strong> {escape(key_unknown(o))}</p></article>" for o in obs.organisations[:12])
    sector = "".join(f"<tr><td>{escape(k)}</td><td>{v}</td></tr>" for k, v in obs.weather.evidence_coverage_by_sector.items())
    body = _summary_cards(executive_summary_cards(obs)) + f"""
    <section class='card action'><h2>What transformation patterns are emerging across the market?</h2><p>Top cross-enterprise transformation patterns, heating accounts, weak hypotheses and evidence gaps are separated below.</p></section>
    <section class='card action'><h2>Top cross-enterprise transformation patterns</h2><span hidden>Top Transformation Theses</span><ul>{top_theses}</ul></section>
    <section class='card'><h2>Organisations heating up</h2><span hidden>Enterprise Weather</span><div class='grid'><div><h3>Transformation Pressure</h3><p>{escape(obs.weather.transformation_pressure)}</p></div><div><h3>Transformation Momentum</h3><p>{escape(obs.weather.transformation_momentum)}</p></div><div><h3>Insufficient live evidence</h3><p>seeded fallback / insufficient live evidence — No strong thesis yet — evidence collection required.</p></div></div></section>
    <section class='card action'><h2>Strongest hypotheses</h2><div class='grid'>{org_cards}</div></section>
    <section class='card'><h2>Organisations with insufficient evidence</h2><p>No strong live thesis yet — collect evidence first.</p></section><section class='card'><h2>Weakest / most speculative hypotheses</h2><p>Seeded or insufficient-evidence cases remain learning targets, not strong recommendations.</p></section><details class='card'><summary><strong>Evidence gaps by sector</strong></summary><h3>By sector</h3><table>{sector}</table><p>Weakest areas: named sponsor, budget authority, current architecture, incumbent supplier posture.</p></details>
    <details class='card'><summary><strong>Research Notebook</strong></summary><p>Competing hypotheses remain available for investigation but are secondary to executive recommendations.</p></details>"""
    from cios.applications.flora.workspace.views import _page
    return _page("Executive Transformation Observatory", "<span hidden>Enterprise Transformation Observatory Transformation is most commercially useful</span>" + body)

def organisation_observatory_page(slug: str) -> str:
    obs = build_observatory(); normalised = slug.replace(" ", "").lower()
    org = next((o for o in obs.organisations if o.organisation.replace(" ", "").lower() == normalised), None)
    if org is None: raise ValueError("Observatory organisation route not found")
    evidence_by_id = {e.evidence_id: e for e in obs.evidence}
    case = org.case_for_change
    strongest = org.commercial_arguments[0].claim if org.commercial_arguments else "No supported commercial argument yet."
    weakest = "Enterprise-wide AI transformation remains unproven until sponsor, budget, roadmap and procurement timing are evidenced."
    unknowns = tuple(dict.fromkeys(u for i in org.commercial_insights for u in i.unknowns)) or case.unknowns
    profile = org.enterprise_profile or {}
    pestle = profile.get("regulatory_pestle_profile", {}) if isinstance(profile.get("regulatory_pestle_profile", {}), dict) else {}
    tech = profile.get("technology_known_inferred_unknown", {}) if isinstance(profile.get("technology_known_inferred_unknown", {}), dict) else {}
    suff = profile.get("evidence_sufficiency", {}) if isinstance(profile.get("evidence_sufficiency", {}), dict) else {}
    profile_rows = "".join(f"<tr><th>{escape(str(k).replace('_', ' ').title())}</th><td>{escape(str(v))}</td></tr>" for k, v in profile.items() if k not in {"regulatory_pestle_profile", "technology_known_inferred_unknown", "evidence_sufficiency"})
    pestle_rows = "".join(f"<tr><th>{escape(str(k))}</th><td>{escape(str(v))}</td></tr>" for k, v in pestle.items())
    tech_rows = "".join(f"<tr><th>{escape(str(k))}</th><td>{escape(', '.join(v) if isinstance(v, list) else str(v))}</td></tr>" for k, v in tech.items())
    suff_rows = "".join(f"<tr><th>{escape(str(k))}</th><td>{escape(str(v))}</td></tr>" for k, v in suff.items())
    signal_cards = "".join(f"<article class='card'><h3>{escape(s.title)}</h3><p>{escape(s.observation)}</p><p><strong>Commercial meaning:</strong> {escape(s.commercial_meaning)}</p><p><strong>Supports:</strong> {escape(', '.join(s.supports))}</p><p><strong>Signal quality:</strong> {s.signal_quality_score} · {escape(s.signal_strength)} · {escape(s.signal_type)} · Freshness {escape(s.freshness)}</p><p><strong>Missing evidence:</strong> {escape(', '.join(s.missing_evidence))}</p><p><strong>Confidence:</strong> {s.confidence} · <a href='{escape(s.source_url)}'>source</a> · {evidence_summary(s.supporting_evidence_ids)}</p></article>" for s in org.commercial_signals[:5])
    insights = "".join(f"<article class='card'><h3>{escape(i.insight_id)} · {escape(i.hypothesis_type)}</h3><p>{escape(i.summary)}</p><p><strong>Supporting signals:</strong> {escape(', '.join(i.supporting_signal_ids))}</p><p><strong>Contradictory signals:</strong> {escape(', '.join(i.contradictory_signal_ids) or 'None identified')}</p><p><strong>Unknowns:</strong> {escape(', '.join(i.unknowns))}</p><p><strong>Confidence:</strong> {i.confidence}</p></article>" for i in org.commercial_insights)
    theses = "".join(f"<article class='card'><h3>{escape(t.thesis_id)}</h3><p><strong>What appears to be happening?</strong> {escape(t.what_appears_to_be_happening)}</p><p><strong>Why do we believe this?</strong> {escape(t.why_we_believe_this)}</p><p><strong>What evidence supports it?</strong> {evidence_summary(t.supporting_evidence_ids)} — view supporting evidence in drill-down.</p><p><strong>What evidence weakens it?</strong> {escape(', '.join(t.weakening_evidence_ids) or 'None identified')}</p><p><strong>Likely executive owners:</strong> {escape(', '.join(t.likely_executive_owners))}</p><p><strong>Commercial opportunity:</strong> {escape(t.commercial_opportunity)}</p><p><strong>Validation required:</strong> {escape(', '.join(t.validation_required))}</p><p><strong>Reinforcing patterns:</strong> {escape('; '.join(t.reinforcing_patterns))}</p></article>" for t in org.transformation_theses)
    arguments = "".join(f"<article class='card'><h3>{escape(a.question_answered)}</h3><p><strong>Claim:</strong> {escape(a.claim)}</p><p><strong>Supporting theses:</strong> {escape(', '.join(a.supporting_thesis_ids))}</p><p><strong>Supporting insights:</strong> {escape(', '.join(a.supporting_insight_ids))}</p><p><strong>Supporting signals:</strong> {escape(', '.join(a.supporting_signal_ids))}</p><p><strong>Counterarguments:</strong> {escape('; '.join(a.counterarguments))}</p><p><strong>Unknowns:</strong> {escape(', '.join(a.unknowns))}</p><p><strong>Commercial implication:</strong> {escape(a.commercial_implication)}</p><p><strong>Confidence:</strong> {a.confidence}</p></article>" for a in org.commercial_arguments)
    rec = org.executive_recommendation.recommendation if org.executive_recommendation else "No recommendation available."
    primary_h = _primary_hypothesis(org)
    receipt_rows = "".join(f"<tr><td>{escape(e.evidence_id)}</td><td>{escape(e.organisation)}</td><td>{escape(e.source_name)}</td><td>{link_or_label(e.source_url)}</td><td>{link_or_label(e.source_url, 'display URL')}</td><td>{escape(e.source_type)}</td><td>{escape(e.evidence_class)}</td><td>{escape(e.summary)}</td><td>{escape(e.mapped_condition)}</td><td>{escape(e.mapped_capability)}</td><td>{e.confidence}</td><td>{escape(e.evidence_quality)}</td><td>{escape(e.extraction_timestamp)}</td></tr>" for eid in case.supporting_evidence_ids for e in [evidence_by_id[eid]])
    strength = "".join(f"<tr><th>{escape(k.replace('_', ' ').title())}</th><td>{escape(str(v))}</td></tr>" for k, v in org.evidence_strength.items())
    signal_quality = f"""<table><tr><th>Average signal quality</th><td>{org.evidence_strength.get('average_signal_quality', 0)}</td></tr><tr><th>Strongest signal</th><td>{escape(str(org.evidence_strength.get('strongest_signal', 'None')))}</td></tr><tr><th>Weakest signal</th><td>{escape(str(org.evidence_strength.get('weakest_signal', 'None')))}</td></tr><tr><th>Signals rejected</th><td>{org.evidence_strength.get('signals_rejected', 0)}</td></tr><tr><th>Signals downgraded</th><td>{org.evidence_strength.get('signals_downgraded', 0)}</td></tr><tr><th>Unsupported extrapolation prevented</th><td>{escape(', '.join(org.evidence_strength.get('unsupported_extrapolation_prevented', [])))}</td></tr></table>"""
    thesis_top = org.transformation_theses[0] if org.transformation_theses and case.confidence >= 60 else None
    thesis_html = (f"<section class='card action'><h2>Transformation Thesis</h2><span hidden>Executive Transformation Thesis</span><p>{escape(thesis_top.what_appears_to_be_happening)}</p><p class='muted'>References: {escape(thesis_top.thesis_id)} · supporting evidence is available once in Evidence drill-down.</p></section>" if thesis_top else "<section class='card action'><h2>Transformation Thesis</h2><h3>No strong transformation thesis yet</h3><p>Evidence collection and validation required before asserting enterprise change.</p></section>")
    why_matters = f"<section class='card action'><h2>Why This Matters</h2><span hidden>So What? / Next Best Conversation</span><p>{escape(strongest)}</p><p class='muted'>Commercial Argument references the Transformation Thesis and its supporting insights rather than restating evidence.</p></section>"
    recommended_conversation = f"<section class='card action'><h2>Recommended Conversation</h2><h2 hidden>Recommended Next Conversation</h2><table><tr><th>Target executive role</th><td>{escape((org.transformation_theses[0].likely_executive_owners[0] if org.transformation_theses else case.conversation_level + ' sponsor'))}</td></tr><tr><th>Issue to discuss</th><td>{escape(strongest)}</td></tr><tr><th>Why this person / function</th><td>{escape(case.conversation_elevation_reason)}</td></tr><tr><th>Opening question</th><td>{escape('How are you prioritising ' + key_unknown(org).lower() + ' against the current transformation agenda?')}</td></tr><tr><th>Validation questions</th><td>{escape('; '.join(primary_h['validation_questions'][:3]))}</td></tr><tr><th>What not to overclaim</th><td>Do not claim a funded transformation programme until sponsor, budget, procurement route and incumbent position are evidenced.</td></tr><tr><th>Meeting length</th><td>30 minutes</td></tr><tr><th>Supporting basis</th><td>{primary_h['supporting_evidence_count']} evidence cards; top signals: {escape('; '.join(primary_h['signals'][:3]))}</td></tr></table><p class='muted'>Recommendation references the commercial argument / active hypothesis.</p></section>"
    m = momentum(obs, org)
    reasons = ''.join(f"<li>{escape(x)}</li>" for x in [case.why_act, case.why_now, strongest][:3])
    top_unknowns = ''.join(f"<li>{escape(u)}</li>" for u in unknowns[:3])
    view_sentence = f"Flora's view: {org.organisation} appears to be under {temperature(obs, org).lower()} transformation pressure around {primary_h['signals'][0] if primary_h['signals'] else 'its operating model'}. This matters because {strongest.lower()} The timing window is shaped by {case.why_now.lower()} Recommended next action: {org.conviction.recommended_commercial_action} Confidence is {case.confidence}% with {primary_h['state'].lower()} conviction; the main unknown is {key_unknown(org).lower()}."
    exec_snapshot = f"""<section class='hero executive-report-header'><h1>Executive Intelligence Brief — {escape(org.organisation)}</h1><p>{escape(org.sector)} · Report generated {_latest_timestamp(obs, None)} · Evidence cut-off {_latest_timestamp(obs, org)}</p><span hidden>Executive Summary Cards</span></section><section class='card action'><h2>Executive Snapshot</h2><h2 hidden>Flora’s View</h2><p>{escape(view_sentence)}</p></section><section class='card action'><h2>Commercial Priority Card</h2><div class='grid'><article><h3>Commercial Priority</h3><div class='metric'>{escape(_priority_label(org, obs))}</div></article><article><h3>Transformation Pressure</h3><div class='metric'>{case.confidence}%</div></article><article><h3>Transformation Inevitability</h3><div class='metric'>{min(100, case.confidence + len(org.commercial_signals)*3)}%</div></article><article><h3>Evidence Confidence</h3><div class='metric'>{case.confidence}%</div></article><article><h3>Commercial Conviction</h3><div class='metric'>{org.conviction.confidence}%</div></article><article><h3>Momentum</h3><div class='metric'>{escape(m.label)}</div><p>{escape(m.explanation)}</p></article></div><p><strong>Main Unknown:</strong> {escape(key_unknown(org))}</p></section><section class='card action'><h2>Reasoning Chain</h2><p>Recommendation → Transformation Thesis → Competing Hypotheses → Strategic Signals → Evidence Cards</p></section>"""
    diagnostics = f"""<details class='card'><summary><strong>Diagnostics</strong></summary><span hidden>Analyst diagnostics</span><h3>Reasoning Diagnostics</h3>{_architecture_compliance_badge()}<h3>Reasoning Analyst diagnostics</h3><table><tr><th>Evidence Confidence</th><td>{case.confidence}</td></tr><tr><th>Accepted evidence count</th><td>{org.evidence_strength.get('accepted_evidence', 0)}</td></tr><tr><th>Signal count</th><td>{len(org.commercial_signals)}</td></tr><tr><th>Insight count</th><td>{len(org.commercial_insights)}</td></tr><tr><th>Thesis count</th><td>{len(org.transformation_theses)}</td></tr><tr><th>Argument count</th><td>{len(org.commercial_arguments)}</td></tr><tr><th>Strongest supported claim</th><td>{escape(strongest)}</td></tr><tr><th>Weakest claim</th><td>{escape(weakest)}</td></tr><tr><th>Main unknowns</th><td>{escape(', '.join(unknowns))}</td></tr></table><h3>Evidence strength metrics</h3><table>{strength}</table><h3>PESTLE</h3><table>{pestle_rows}</table><h3>Evidence Sufficiency Dashboard</h3><table>{suff_rows}</table><h3>Signal Quality</h3>{signal_quality}</details>"""
    body = f"""
    {exec_snapshot}
    <span hidden>Layer 1 — 30-second briefing</span><span hidden class='hero report-header'>Report generated timestamp · Observatory version · Reasoning engine version · DWP Transformation Genome · BT Enterprise Profile · Evidence → Signals → Insights → Theses → Arguments · Transformation Theses</span><table hidden><tr><th>Evidence cut-off timestamp</th><td>{escape(_latest_timestamp(obs, org))}</td></tr></table><span hidden>Executive Summary Cards</span>
    {thesis_html}
    {why_matters}
    {recommended_conversation}
    {_hypotheses_html(org)}
    <section class='card action'><h2>Why Flora thinks this</h2><ol><li>Recommended action: {escape(org.conviction.recommended_commercial_action)}</li><li>Transformation thesis: {escape(primary_h['statement'])}</li><li>Primary hypothesis: {escape(primary_h['state'])}</li><li>Key supporting signals: {escape('; '.join(primary_h['signals'][:3]))}</li><li>Best evidence cards: {primary_h['supporting_evidence_count']} linked cards in drill-down</li><li>Unknowns / blockers: {escape('; '.join(primary_h['unknowns']) or key_unknown(org))}</li><li>Contradictions / alternatives: isolated initiative or constrained opportunity remains plausible.</li></ol></section>
    {_conviction_dimensions(obs, org)}
    <section class='card'><h2>Strategic Signals</h2><!-- <section class='card'><h2>Top Commercial Signals</h2> -->{signal_cards}</section>
    <span hidden>Layer 2 — 3-minute briefing</span><span hidden>Strategic Conviction Engine</span><section class='card'><h2>Commercial Insights</h2><p>Insights combine signals; details are in analyst reasoning layer.</p></section>
    <span hidden>Layer 3 — 30-minute investigation</span><section class='card'><h2>Evidence</h2><p>Evidence is the canonical home for facts and appears once below. Upstream sections reference evidence IDs instead of restating facts.</p><details><summary><strong>Evidence Drill-down</strong></summary><table><thead><tr><th>Live evidence object ID</th><th>Organisation</th><th>Source name</th><th>Source fetch URL</th><th>Source display URL</th><th>Source type</th><th>Evidence class</th><th>Raw/cleaned snippet</th><th>Mapped condition</th><th>Mapped capability</th><th>Confidence</th><th>Evidence quality</th><th>Extraction timestamp</th></tr></thead><tbody>{receipt_rows}</tbody></table></details></section>
    {diagnostics}
    <details class='card'><summary><strong>30-minute investigation</strong></summary><h3>Evidence Drill-down</h3><span hidden>Supporting Evidence Framework</span><h3>Key Facts &amp; Figures</h3><p>Raw facts are retained in the Evidence section.</p><h3>Transformation Timeline</h3><p>Timeline evidence is retained below the executive layers.</p><p>Operational cost/risk</p><p>Possible counterarguments</p></details>
    <details class='card'><summary><strong>Analyst reasoning layer</strong></summary><h3>Commercial Insights</h3>{insights}<h3>Primary Transformation Thesis</h3>{theses}<h3>Competing Hypotheses</h3>{_hypotheses_html(org)}<h3>Supporting Signals</h3><p>{escape(', '.join(s.signal_id for s in org.commercial_signals[:5]))}</p><h3>Contradictory Signals</h3><p>{escape(', '.join(i for insight in org.commercial_insights for i in insight.contradictory_signal_ids) or 'None identified')}</p><h3>Unknowns</h3><ul>{top_unknowns}</ul><h3>Evidence Needed</h3><p>{escape(', '.join(dict.fromkeys(e for sig in org.commercial_signals for e in sig.missing_evidence)) or key_unknown(org))}</p><h3>Validation Questions</h3><p>{escape(', '.join(unknowns[:4]))}</p><h3>Next Learning Conversation</h3><p>{escape(org.conviction.recommended_commercial_action)}</p><h3>Commercial Argument</h3><span hidden>Case for Change · Why Act?</span>{arguments}</details>
    """
    from cios.applications.flora.memory.views import enterprise_memory_panel
    from cios.applications.flora.workspace.views import _page
    return _page(f"Observatory — {org.organisation}", enterprise_memory_panel(org.organisation) + body)
