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
    receipt_rows = "".join(f"<tr><td>{escape(e.evidence_id)}</td><td>{escape(e.organisation)}</td><td>{escape(e.source_name)}</td><td>{escape(e.source_url)}</td><td>{escape(e.source_type)}</td><td>{escape(e.evidence_class)}</td><td>{escape(e.summary)}</td><td>{escape(e.mapped_condition)}</td><td>{escape(e.mapped_capability)}</td><td>{e.confidence}</td><td>{escape(e.evidence_quality)}</td><td>{escape(e.extraction_timestamp)}</td></tr>" for eid in case.supporting_evidence_ids for e in [evidence_by_id[eid]])
    facts = "".join(f"<tr><td>{escape(f['fact'])}</td><td>{escape(f['source_name'])}</td><td>{escape(f['source_url'])}</td><td>{escape(f['evidence_id'])}</td><td>{escape(f['snippet'])}</td></tr>" for f in org.key_facts)
    strength = "".join(f"<tr><th>{escape(k.replace('_', ' ').title())}</th><td>{escape(str(v))}</td></tr>" for k, v in org.evidence_strength.items())
    timeline = "".join(f"<tr><td>{escape(t['date'])}</td><td>{escape(t['source'])}</td><td>{escape(t['evidence_class'])}</td><td>{escape(t['signal'])}</td><td>{escape(t['transformation_dimension'])}</td><td>{escape(t['interpretation'])}</td></tr>" for t in org.transformation_timeline)
    costs = "".join(f"<tr><td>{escape(str(c['category']))}</td><td>{escape(str(c['claim']))}</td><td>{escape(', '.join(c['supporting_evidence']))}</td><td>{c['confidence']}</td><td>{escape(str(c['unknowns']))}</td></tr>" for c in org.cost_of_waiting_categories)
    case_html = "".join(f"<details class='card'><summary><strong>{escape(label)}</strong></summary><pre>{escape(text)}</pre></details>" for label, text in [("Why Act?", case.why_act), ("Why Now?", case.why_now), ("Why AI?", case.why_ai), ("Why Cloud?", case.why_cloud), ("Why Secure by Design?", case.why_secure_by_design), ("Why this Transformation?", case.why_this_transformation), ("Cost of Waiting", case.cost_of_waiting)])
    body = f"""<section class='hero'><h1>{escape(org.organisation)} Transformation Genome</h1><p>{escape(org.sector)} · Conversation level: <strong>{escape(case.conversation_level)}</strong> · Confidence {case.confidence}</p><p>{escape(case.conversation_elevation_reason)}</p></section>
    <section class='card'><h2>Evidence strength metrics</h2><table>{strength}</table></section>
    <section class='card'><h2>Key Facts &amp; Figures</h2><table><thead><tr><th>Fact</th><th>Source</th><th>URL</th><th>Evidence ID</th><th>Snippet</th></tr></thead><tbody>{facts}</tbody></table></section>
    <section class='card action'><h2>Strategic Conviction Engine</h2><p><strong>Commercial interpretation:</strong> {escape(org.conviction.commercial_interpretation)}</p><p><strong>Transformation hypothesis:</strong> {escape(org.conviction.transformation_hypothesis)}</p><p><strong>Recommended action:</strong> {escape(org.conviction.recommended_commercial_action)}</p><p><strong>Unknowns:</strong> {escape(', '.join(org.conviction.unknowns))}</p></section>
    <section class='card'><h2>Transformation Timeline</h2><table><thead><tr><th>Date</th><th>Source</th><th>Class</th><th>Signal</th><th>Dimension</th><th>Interpretation</th></tr></thead><tbody>{timeline}</tbody></table></section>
    <section class='card'><h2>Case for Change</h2>{case_html}<p><strong>Commercial risks:</strong> {escape(', '.join(case.commercial_risks))}</p></section>
    <section class='card'><h2>Structured Cost of Waiting</h2><table><thead><tr><th>Category</th><th>Claim</th><th>Supporting evidence</th><th>Confidence</th><th>Unknowns</th></tr></thead><tbody>{costs}</tbody></table></section>
    <section class='card'><h2>Contradictory evidence and counterarguments</h2>{_ul(org.counterarguments)}</section>
    <section class='card'><h2>Supporting Evidence Framework</h2><table><thead><tr><th>Live evidence object ID</th><th>Organisation</th><th>Source name</th><th>Source URL</th><th>Source type</th><th>Evidence class</th><th>Extracted snippet</th><th>Mapped condition</th><th>Mapped capability</th><th>Confidence</th><th>Evidence quality</th><th>Extraction timestamp</th></tr></thead><tbody>{receipt_rows}</tbody></table></section>"""
    from cios.applications.flora.workspace.views import _page
    return _page(f"Observatory — {org.organisation}", body)
