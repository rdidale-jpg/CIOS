"""HTML views for the Enterprise Transformation Observatory."""
from __future__ import annotations

from html import escape

from cios.applications.flora.observatory.engine import build_observatory


def _ul(items):
    return "<ul>" + "".join(f"<li>{escape(str(i))}</li>" for i in items) + "</ul>"


def observatory_page() -> str:
    obs = build_observatory()
    orgs = "".join(f"<li><strong><a href='/observatory/{escape(o.organisation.replace(' ', ''))}'>{escape(o.organisation)}</a></strong> · {escape(o.sector)} · live evidence {o.evidence_strength.get('total_live_evidence_objects', 0)} · urgency {escape(o.strategic_urgency.state)} · confidence {o.case_for_change.confidence}</li>" for o in obs.organisations)
    themes = "".join(f"<span class='pill'>{escape(t)}</span>" for t in obs.weather.emerging_transformation_themes)
    evidence = "".join(f"<li>{escape(eid)}</li>" for eid in obs.weather.most_significant_evidence_today)
    hypotheses = "".join(f"<tr><td>{escape(h.hypothesis_id)}</td><td>{escape(h.title)}</td><td>{escape(h.status.value)}</td><td>{h.confidence}</td><td>{escape(h.commercial_implications)}</td></tr>" for h in obs.hypotheses)
    sector = "".join(f"<tr><td>{escape(k)}</td><td>{v}</td></tr>" for k, v in obs.weather.evidence_coverage_by_sector.items())
    classes = "".join(f"<tr><td>{escape(k)}</td><td>{v}</td></tr>" for k, v in obs.weather.evidence_coverage_by_class.items())
    body = f"""<section class='hero'><h1>Enterprise Transformation Observatory</h1><p class='muted'>Flora reasons over enterprise transformation evidence, separating observed fact, interpretation, hypothesis, unknown and action.</p><p><a href='/observatory/critique'>Architectural critique completed before implementation</a></p></section>
    <section class='card'><h2>Evidence cockpit</h2><div class='grid'><div><div class='metric'>{obs.weather.total_live_evidence_objects}</div><p>total live evidence objects</p></div><div><div class='metric'>{obs.weather.total_organisations_covered}</div><p>organisations covered</p></div></div><h3>Evidence coverage by sector</h3><table>{sector}</table><h3>Evidence coverage by class</h3><table>{classes}</table></section>
    <section class='card'><h2>Enterprise Weather</h2><div class='grid'><div><h3>Transformation Pressure</h3><p>{escape(obs.weather.transformation_pressure)}</p></div><div><h3>Transformation Momentum</h3><p>{escape(obs.weather.transformation_momentum)}</p></div><div><h3>Accelerating sectors</h3><p>{escape(', '.join(obs.weather.accelerating_sectors))}</p></div></div><p>{themes}</p></section>
    <section class='card'><h2>Transformation tipping points</h2>{_ul(obs.weather.transformation_tipping_points)}<h3>Cross-sector observations</h3>{_ul(obs.weather.cross_sector_observations)}<h3>Top 5 strongest evidence-backed observations</h3>{_ul(obs.weather.most_significant_evidence_today[:5])}<h3>Top 5 weakest/least evidenced claims</h3>{_ul(['Named sponsor', 'Budget authority', 'Current architecture', 'Incumbent supplier posture', 'Quantified cost of waiting'])}<h3>Emerging hypotheses with supporting evidence counts</h3><ul>{''.join(f'<li>{escape(h.title)} — {len(h.supporting_evidence_ids)} supporting evidence object(s)</li>' for h in obs.hypotheses)}</ul></section>
    <section class='card action'><h2>Monitored organisations</h2><ul>{orgs}</ul></section>
    <section class='card'><h2>Research Notebook</h2><table><thead><tr><th>ID</th><th>Hypothesis</th><th>Status</th><th>Confidence</th><th>Commercial implications</th></tr></thead><tbody>{hypotheses}</tbody></table></section>"""
    from cios.applications.flora.workspace.views import _page
    return _page("Enterprise Transformation Observatory", body)


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
    arguments = "".join(f"<article class='card'><h3>{escape(a.question_answered)}</h3><p><strong>Claim:</strong> {escape(a.claim)}</p><p><strong>Supporting insights:</strong> {escape(', '.join(a.supporting_insight_ids))}</p><p><strong>Supporting signals:</strong> {escape(', '.join(a.supporting_signal_ids))}</p><p><strong>Counterarguments:</strong> {escape('; '.join(a.counterarguments))}</p><p><strong>Unknowns:</strong> {escape(', '.join(a.unknowns))}</p><p><strong>Commercial implication:</strong> {escape(a.commercial_implication)}</p><p><strong>Confidence:</strong> {a.confidence}</p></article>" for a in org.commercial_arguments)
    rec = org.executive_recommendation.recommendation if org.executive_recommendation else "No recommendation available."
    receipt_rows = "".join(f"<tr><td>{escape(e.evidence_id)}</td><td>{escape(e.organisation)}</td><td>{escape(e.source_name)}</td><td>{escape(e.source_url)}</td><td>{escape(e.source_type)}</td><td>{escape(e.evidence_class)}</td><td>{escape(e.summary)}</td><td>{escape(e.mapped_condition)}</td><td>{escape(e.mapped_capability)}</td><td>{e.confidence}</td><td>{escape(e.evidence_quality)}</td><td>{escape(e.extraction_timestamp)}</td></tr>" for eid in case.supporting_evidence_ids for e in [evidence_by_id[eid]])
    strength = "".join(f"<tr><th>{escape(k.replace('_', ' ').title())}</th><td>{escape(str(v))}</td></tr>" for k, v in org.evidence_strength.items())
    signal_quality = f"""<table><tr><th>Average signal quality</th><td>{org.evidence_strength.get('average_signal_quality', 0)}</td></tr><tr><th>Strongest signal</th><td>{escape(str(org.evidence_strength.get('strongest_signal', 'None')))}</td></tr><tr><th>Weakest signal</th><td>{escape(str(org.evidence_strength.get('weakest_signal', 'None')))}</td></tr><tr><th>Signals rejected</th><td>{org.evidence_strength.get('signals_rejected', 0)}</td></tr><tr><th>Signals downgraded</th><td>{org.evidence_strength.get('signals_downgraded', 0)}</td></tr><tr><th>Unsupported extrapolation prevented</th><td>{escape(', '.join(org.evidence_strength.get('unsupported_extrapolation_prevented', [])))}</td></tr></table>"""
    body = f"""<section class='hero'><h1>{escape(org.organisation)} Transformation Genome</h1><h2>Commercial Intelligence Briefing</h2><p>{escape(org.sector)} · Conversation level: <strong>{escape(case.conversation_level)}</strong> · Confidence {case.confidence}</p><p>{escape(case.conversation_elevation_reason)}</p></section>
    <section class='card action'><h2>Executive Snapshot</h2><table><tr><th>Confidence</th><td>{case.confidence}</td></tr><tr><th>Accepted evidence count</th><td>{org.evidence_strength.get('accepted_evidence', 0)}</td></tr><tr><th>Signal count</th><td>{len(org.commercial_signals)}</td></tr><tr><th>Insight count</th><td>{len(org.commercial_insights)}</td></tr><tr><th>Argument count</th><td>{len(org.commercial_arguments)}</td></tr><tr><th>Strongest supported claim</th><td>{escape(strongest)}</td></tr><tr><th>Weakest claim</th><td>{escape(weakest)}</td></tr><tr><th>Main unknowns</th><td>{escape(', '.join(unknowns))}</td></tr></table></section>
    <section class='card action'><h2>Strategic Conviction Engine</h2><p>Strategic conviction is now derived from arguments, insights and signals rather than duplicated raw snippets.</p></section>
    <section class='card'><h2>BT Enterprise Profile</h2><table>{profile_rows}</table><h3>Regulatory / PESTLE profile</h3><table>{pestle_rows}</table><h3>Network and technology profile — Known / Inferred / Unknown</h3><table>{tech_rows}</table><h3>Evidence Sufficiency Dashboard</h3><table>{suff_rows}</table></section>
    <section class='card'><h2>Signal Quality</h2>{signal_quality}</section>
    <section class='card'><h2>Top Commercial Signals</h2>{signal_cards}</section>
    <section class='card'><h2>Commercial Insights</h2>{insights}</section>
    <section class='card'><h2>Commercial Arguments / Case for Change</h2><h3>Why Act?</h3>{arguments}</section>
    <section class='card action'><h2>Executive Recommendation</h2><p>{escape(rec)}</p><p><strong>References:</strong> {escape(', '.join(org.executive_recommendation.supporting_argument_ids) if org.executive_recommendation else '')}</p></section>
    <details class='card'><summary><strong>Evidence Drill-down / Supporting Evidence Framework</strong></summary><h3>Evidence strength metrics</h3><table>{strength}</table><h3>Key Facts &amp; Figures</h3><p>Raw facts are retained in drill-down diagnostics.</p><h3>Transformation Timeline</h3><p>Timeline evidence is retained below the executive layers.</p><p>Operational cost/risk</p><p>Possible counterarguments</p><table><thead><tr><th>Live evidence object ID</th><th>Organisation</th><th>Source name</th><th>Source URL</th><th>Source type</th><th>Evidence class</th><th>Raw/cleaned snippet</th><th>Mapped condition</th><th>Mapped capability</th><th>Confidence</th><th>Evidence quality</th><th>Extraction timestamp</th></tr></thead><tbody>{receipt_rows}</tbody></table></details>"""
    from cios.applications.flora.workspace.views import _page
    return _page(f"Observatory — {org.organisation}", body)
