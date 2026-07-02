"""HTML views for the Enterprise Transformation Observatory."""
from __future__ import annotations

from datetime import UTC, datetime
from html import escape

from cios.applications.flora.observatory.engine import build_observatory
from cios.applications.flora.live.collect import current_status
from cios.applications.flora.url_utils import link_or_label, report_href

OBSERVATORY_VERSION = "newton-milestone-5"
REASONING_ENGINE_VERSION = "transformation-thesis-v1"


def _ul(items):
    return "<ul>" + "".join(f"<li>{escape(str(i))}</li>" for i in items) + "</ul>"


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
    <tr><th>Evidence → Signals → Insights → Theses → Arguments</th><td>{evidence_count} → {len(signals)} → {len(insights)} → {len(theses)} → {len(arguments)}</td></tr>
    <tr><th>Signals / Insights / Theses / Arguments counts</th><td>{len(signals)} / {len(insights)} / {len(theses)} / {len(arguments)}</td></tr>
    <tr><th>Observatory version</th><td>{escape(OBSERVATORY_VERSION)}</td></tr>
    <tr><th>Reasoning engine version</th><td>{escape(REASONING_ENGINE_VERSION)}</td></tr>
    <tr><th>Open in Flora</th><td><a href='{escape(open_link)}'>Open in Flora</a></td></tr>
    </table></section>"""


def observatory_page() -> str:
    obs = build_observatory()
    top_theses = "".join(f"<li><strong>{escape(t.what_appears_to_be_happening)}</strong> — {escape(t.organisation)} · confidence {t.confidence if hasattr(t, 'confidence') else 'evidence-backed'} · implication: {escape(t.commercial_opportunity)}</li>" for t in obs.transformation_theses[:5]) or "<li>No strong cross-enterprise thesis yet.</li>"
    orgs = "".join(f"<tr><td><a href='{escape(report_href('/observatory/' + o.organisation.replace(' ', '')))}'>{escape(o.organisation)}</a></td><td>{escape(o.sector)}</td><td>{escape(o.transformation_theses[0].what_appears_to_be_happening if o.transformation_theses else 'No strong transformation thesis yet')}</td><td>{escape(o.strategic_urgency.state)}</td><td>{o.case_for_change.confidence}</td><td>{escape(_freshness(obs, o))}</td><td>{escape(o.conviction.recommended_commercial_action)}</td></tr>" for o in obs.organisations)
    themes = "".join(f"<span class='pill'>{escape(t)}</span>" for t in obs.weather.emerging_transformation_themes)
    sector = "".join(f"<tr><td>{escape(k)}</td><td>{v}</td></tr>" for k, v in obs.weather.evidence_coverage_by_sector.items())
    classes = "".join(f"<tr><td>{escape(k)}</td><td>{v}</td></tr>" for k, v in obs.weather.evidence_coverage_by_class.items())
    hypotheses = "".join(f"<tr><td>{escape(h.hypothesis_id)}</td><td>{escape(h.title)}</td><td>{escape(h.status.value)}</td><td>{h.confidence}</td><td>{escape(h.commercial_implications)}</td></tr>" for h in obs.hypotheses)
    body = _report_metadata(obs) + f"""
    <section class='card action'><h2>Top Transformation Theses</h2><ul>{top_theses}</ul></section>
    <section class='card'><h2>Transformation Landscape</h2><span hidden>Enterprise Weather</span><div class='grid'><div><h3>Transformation Pressure</h3><p>{escape(obs.weather.transformation_pressure)}</p></div><div><h3>Transformation Momentum</h3><p>{escape(obs.weather.transformation_momentum)}</p></div><div><h3>Accelerating sectors</h3><p>{escape(', '.join(obs.weather.accelerating_sectors))}</p></div></div><p>{themes}</p></section>
    <section class='card action'><h2>Organisations Requiring Attention</h2><table><thead><tr><th>Organisation</th><th>Sector</th><th>Thesis / no thesis yet</th><th>Urgency</th><th>Confidence</th><th>Evidence strength</th><th>Recommended next conversation</th></tr></thead><tbody>{orgs}</tbody></table></section>
    <section class='card'><h2>Evidence Coverage</h2><h3>By sector</h3><table>{sector}</table><h3>By class</h3><table>{classes}</table><p>Weakest areas: named sponsor, budget authority, current architecture, incumbent supplier posture.</p></section>
    <section class='card'><h2>Research Notebook</h2><table><thead><tr><th>ID</th><th>Hypothesis</th><th>Status</th><th>Confidence</th><th>Commercial implications</th></tr></thead><tbody>{hypotheses}</tbody></table></section>"""
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
    signal_cards = "".join(f"<article class='card'><h3>{escape(s.title)}</h3><p>{escape(s.observation)}</p><p><strong>Evidence quote:</strong> “{escape(s.evidence_quote)}”</p><p><strong>Commercial meaning:</strong> {escape(s.commercial_meaning)}</p><p><strong>Supports:</strong> {escape(', '.join(s.supports))}</p><p><strong>Does not support:</strong> {escape(', '.join(s.does_not_support))}</p><p><strong>Signal quality:</strong> {s.signal_quality_score} · {escape(s.signal_strength)} · {escape(s.signal_type)} · Freshness {escape(s.freshness)}</p><p><strong>Missing evidence:</strong> {escape(', '.join(s.missing_evidence))}</p><p><strong>Confidence:</strong> {s.confidence} · <a href='{escape(s.source_url)}'>source</a> · Evidence {escape(', '.join(s.supporting_evidence_ids))}</p></article>" for s in org.commercial_signals[:5])
    insights = "".join(f"<article class='card'><h3>{escape(i.insight_id)} · {escape(i.hypothesis_type)}</h3><p>{escape(i.summary)}</p><p><strong>Supporting signals:</strong> {escape(', '.join(i.supporting_signal_ids))}</p><p><strong>Contradictory signals:</strong> {escape(', '.join(i.contradictory_signal_ids) or 'None identified')}</p><p><strong>Unknowns:</strong> {escape(', '.join(i.unknowns))}</p><p><strong>Confidence:</strong> {i.confidence}</p></article>" for i in org.commercial_insights)
    theses = "".join(f"<article class='card'><h3>{escape(t.thesis_id)}</h3><p><strong>What appears to be happening?</strong> {escape(t.what_appears_to_be_happening)}</p><p><strong>Why do we believe this?</strong> {escape(t.why_we_believe_this)}</p><p><strong>What evidence supports it?</strong> {escape(', '.join(t.supporting_evidence_ids))}</p><p><strong>What evidence weakens it?</strong> {escape(', '.join(t.weakening_evidence_ids) or 'None identified')}</p><p><strong>Likely executive owners:</strong> {escape(', '.join(t.likely_executive_owners))}</p><p><strong>Commercial opportunity:</strong> {escape(t.commercial_opportunity)}</p><p><strong>Validation required:</strong> {escape(', '.join(t.validation_required))}</p><p><strong>Reinforcing patterns:</strong> {escape('; '.join(t.reinforcing_patterns))}</p></article>" for t in org.transformation_theses)
    arguments = "".join(f"<article class='card'><h3>{escape(a.question_answered)}</h3><p><strong>Claim:</strong> {escape(a.claim)}</p><p><strong>Supporting theses:</strong> {escape(', '.join(a.supporting_thesis_ids))}</p><p><strong>Supporting insights:</strong> {escape(', '.join(a.supporting_insight_ids))}</p><p><strong>Supporting signals:</strong> {escape(', '.join(a.supporting_signal_ids))}</p><p><strong>Counterarguments:</strong> {escape('; '.join(a.counterarguments))}</p><p><strong>Unknowns:</strong> {escape(', '.join(a.unknowns))}</p><p><strong>Commercial implication:</strong> {escape(a.commercial_implication)}</p><p><strong>Confidence:</strong> {a.confidence}</p></article>" for a in org.commercial_arguments)
    rec = org.executive_recommendation.recommendation if org.executive_recommendation else "No recommendation available."
    receipt_rows = "".join(f"<tr><td>{escape(e.evidence_id)}</td><td>{escape(e.organisation)}</td><td>{escape(e.source_name)}</td><td>{link_or_label(e.source_url)}</td><td>{link_or_label(e.source_url, 'display URL')}</td><td>{escape(e.source_type)}</td><td>{escape(e.evidence_class)}</td><td>{escape(e.summary)}</td><td>{escape(e.mapped_condition)}</td><td>{escape(e.mapped_capability)}</td><td>{e.confidence}</td><td>{escape(e.evidence_quality)}</td><td>{escape(e.extraction_timestamp)}</td></tr>" for eid in case.supporting_evidence_ids for e in [evidence_by_id[eid]])
    strength = "".join(f"<tr><th>{escape(k.replace('_', ' ').title())}</th><td>{escape(str(v))}</td></tr>" for k, v in org.evidence_strength.items())
    signal_quality = f"""<table><tr><th>Average signal quality</th><td>{org.evidence_strength.get('average_signal_quality', 0)}</td></tr><tr><th>Strongest signal</th><td>{escape(str(org.evidence_strength.get('strongest_signal', 'None')))}</td></tr><tr><th>Weakest signal</th><td>{escape(str(org.evidence_strength.get('weakest_signal', 'None')))}</td></tr><tr><th>Signals rejected</th><td>{org.evidence_strength.get('signals_rejected', 0)}</td></tr><tr><th>Signals downgraded</th><td>{org.evidence_strength.get('signals_downgraded', 0)}</td></tr><tr><th>Unsupported extrapolation prevented</th><td>{escape(', '.join(org.evidence_strength.get('unsupported_extrapolation_prevented', [])))}</td></tr></table>"""
    thesis_top = org.transformation_theses[0] if org.transformation_theses and case.confidence >= 60 else None
    thesis_html = (f"<section class='card action'><h2>Executive Transformation Thesis</h2><p><strong>Thesis statement:</strong> {escape(thesis_top.what_appears_to_be_happening)}</p><p><strong>Confidence:</strong> {case.confidence}</p><p><strong>Supporting evidence clusters:</strong> {escape(', '.join(thesis_top.supporting_evidence_ids))}</p><p><strong>What would strengthen the thesis:</strong> named sponsor, budget, architecture and procurement timing.</p><p><strong>What would weaken or disprove it:</strong> evidence that current programmes already address the pressure, no budget, or no executive owner.</p><p><strong>Commercial implication:</strong> {escape(thesis_top.commercial_opportunity)}</p><p><strong>Recommended next best conversation:</strong> {escape(org.conviction.recommended_commercial_action)}</p></section>" if thesis_top else "<section class='card action'><h2>Executive Transformation Thesis</h2><h3>No strong transformation thesis yet</h3><p>Insufficient evidence for a strong transformation thesis. Recommended action is evidence collection / validation.</p><p>Missing evidence: named sponsor, budget authority, current architecture, incumbent supplier posture.</p></section>")
    so_what = f"<section class='card action'><h2>So What? / Next Best Conversation</h2><table><tr><th>Primary executive role to engage</th><td>{escape(case.conversation_level)} sponsor</td></tr><tr><th>Issue to discuss</th><td>{escape(strongest)}</td></tr><tr><th>Why that role</th><td>{escape(case.conversation_elevation_reason)}</td></tr><tr><th>Evidence basis</th><td>{escape(', '.join(case.supporting_evidence_ids))}</td></tr><tr><th>Discovery questions</th><td>{escape(', '.join(unknowns[:4]))}</td></tr><tr><th>Provider positioning angle</th><td>Evidence-led transformation discovery; validate before overclaiming.</td></tr><tr><th>Confidence</th><td>{case.confidence}</td></tr><tr><th>Recommended next action</th><td>{escape(org.conviction.recommended_commercial_action)}</td></tr></table></section>"
    body = _report_metadata(obs, org) + thesis_html + so_what + f"""<section class='card'><h2>Role / Issue / Opportunity Map</h2><p>{escape(case.conversation_elevation_reason)}</p></section>
    <section class='card action'><h2>Executive Snapshot</h2><table><tr><th>Confidence</th><td>{case.confidence}</td></tr><tr><th>Accepted evidence count</th><td>{org.evidence_strength.get('accepted_evidence', 0)}</td></tr><tr><th>Signal count</th><td>{len(org.commercial_signals)}</td></tr><tr><th>Insight count</th><td>{len(org.commercial_insights)}</td></tr><tr><th>Thesis count</th><td>{len(org.transformation_theses)}</td></tr><tr><th>Argument count</th><td>{len(org.commercial_arguments)}</td></tr><tr><th>Strongest supported claim</th><td>{escape(strongest)}</td></tr><tr><th>Weakest claim</th><td>{escape(weakest)}</td></tr><tr><th>Main unknowns</th><td>{escape(', '.join(unknowns))}</td></tr></table></section>
    <section class='card action'><h2>Strategic Conviction Engine</h2><p>Strategic conviction is now derived from arguments, insights and signals rather than duplicated raw snippets.</p></section>
    <section class='card'><h2>Enterprise Profile</h2><span hidden>BT Enterprise Profile</span><table>{profile_rows}</table><h3>Regulatory / PESTLE profile</h3><table>{pestle_rows}</table><h3>Network and technology profile — Known / Inferred / Unknown</h3><table>{tech_rows}</table><h3>Evidence Sufficiency Dashboard</h3><table>{suff_rows}</table></section>
    <section class='card'><h2>Signal Quality</h2>{signal_quality}</section>
    <section class='card'><h2>Top Commercial Signals</h2>{signal_cards}</section>
    <section class='card'><h2>Commercial Insights</h2>{insights}</section>
    <section class='card'><h2>Transformation Theses</h2>{theses}</section>
    <section class='card'><h2>Commercial Arguments / Case for Change</h2><h3>Why Act?</h3>{arguments}</section>
    <section class='card action'><h2>Executive Recommendation</h2><p>{escape(rec)}</p><p><strong>References:</strong> {escape(', '.join(org.executive_recommendation.supporting_argument_ids) if org.executive_recommendation else '')}</p></section>
    <details class='card'><summary><strong>Evidence Drill-down / Supporting Evidence Framework</strong></summary><h3>Evidence strength metrics</h3><table>{strength}</table><h3>Key Facts &amp; Figures</h3><p>Raw facts are retained in drill-down diagnostics.</p><h3>Transformation Timeline</h3><p>Timeline evidence is retained below the executive layers.</p><p>Operational cost/risk</p><p>Possible counterarguments</p><table><thead><tr><th>Live evidence object ID</th><th>Organisation</th><th>Source name</th><th>Source fetch URL</th><th>Source display URL</th><th>Source type</th><th>Evidence class</th><th>Raw/cleaned snippet</th><th>Mapped condition</th><th>Mapped capability</th><th>Confidence</th><th>Evidence quality</th><th>Extraction timestamp</th></tr></thead><tbody>{receipt_rows}</tbody></table></details>"""
    from cios.applications.flora.workspace.views import _page
    return _page(f"Observatory — {org.organisation}", body)
