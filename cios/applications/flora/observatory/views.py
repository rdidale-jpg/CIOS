"""HTML views for the Enterprise Transformation Observatory."""
from __future__ import annotations

from html import escape

from cios.applications.flora.observatory.engine import build_observatory


def observatory_page() -> str:
    obs = build_observatory()
    orgs = "".join(f"<li><strong><a href='/observatory/{escape(o.organisation.replace(' ', ''))}'>{escape(o.organisation)}</a></strong> · {escape(o.sector)} · urgency {escape(o.strategic_urgency.state)} · window {escape(o.transformation_window.estimated_window)} · confidence {o.case_for_change.confidence}</li>" for o in obs.organisations)
    themes = "".join(f"<span class='pill'>{escape(t)}</span>" for t in obs.weather.emerging_transformation_themes)
    evidence = "".join(f"<li>{escape(eid)}</li>" for eid in obs.weather.most_significant_evidence_today)
    hypotheses = "".join(f"<tr><td>{escape(h.hypothesis_id)}</td><td>{escape(h.title)}</td><td>{escape(h.status.value)}</td><td>{h.confidence}</td><td>{escape(h.commercial_implications)}</td></tr>" for h in obs.hypotheses)
    body = f"""<section class='hero'><h1>Enterprise Transformation Observatory</h1><p class='muted'>Flora now reasons over enterprise transformation evidence rather than ranking news or hiding opportunity scores.</p><p><a href='/observatory/critique'>Architectural critique completed before implementation</a></p></section>
    <section class='card'><h2>Enterprise Weather</h2><div class='grid'><div><h3>Transformation Pressure</h3><p>{escape(obs.weather.transformation_pressure)}</p></div><div><h3>Transformation Momentum</h3><p>{escape(obs.weather.transformation_momentum)}</p></div><div><h3>Accelerating sectors</h3><p>{escape(', '.join(obs.weather.accelerating_sectors))}</p></div></div><p>{themes}</p></section>
    <section class='card'><h2>Transformation tipping points</h2><ul>{''.join(f'<li>{escape(t)}</li>' for t in obs.weather.transformation_tipping_points)}</ul><h3>Cross-sector observations</h3><ul>{''.join(f'<li>{escape(o)}</li>' for o in obs.weather.cross_sector_observations)}</ul><h3>Most significant evidence received today</h3><ul>{evidence}</ul></section>
    <section class='card action'><h2>Monitored organisations</h2><ul>{orgs}</ul></section>
    <section class='card'><h2>Research Notebook</h2><p>Permanent hypothesis register. Nothing silently changes; each hypothesis retains evidence, confidence and implications.</p><table><thead><tr><th>ID</th><th>Hypothesis</th><th>Status</th><th>Confidence</th><th>Commercial implications</th></tr></thead><tbody>{hypotheses}</tbody></table></section>"""
    from cios.applications.flora.workspace.views import _page
    return _page("Enterprise Transformation Observatory", body)


def organisation_observatory_page(slug: str) -> str:
    obs = build_observatory()
    normalised = slug.replace(" ", "").lower()
    org = next((o for o in obs.organisations if o.organisation.replace(" ", "").lower() == normalised), None)
    if org is None:
        raise ValueError("Observatory organisation route not found")
    evidence_by_id = {e.evidence_id: e for e in obs.evidence}
    genome = "".join(f"<details class='card'><summary><strong>{escape(g.pillar)} / {escape(g.name)}</strong> · confidence {g.confidence} · evidence quality {escape(g.evidence_quality)}</summary><p><strong>Hypothesis:</strong> {escape(g.hypothesis)}</p><p><strong>Reasoning:</strong> {escape(g.reasoning)}</p><p><strong>Evidence:</strong> {escape(', '.join(g.supporting_evidence_ids) or 'None')}</p><p><strong>Unknowns:</strong> {escape(', '.join(g.unknowns) or 'None')}</p></details>" for g in org.genome)
    forces = "".join(f"<tr><td>{escape(f.name)}</td><td>{escape(f.state)}</td><td>{escape(f.reasoning)}</td><td>{f.confidence}</td><td>{escape(', '.join(f.evidence_ids) or 'None')}</td><td>{escape(', '.join(f.unknowns) or 'None')}</td></tr>" for f in org.forces)
    case = org.case_for_change
    case_rows = [("Why Act?", case.why_act), ("Why Now?", case.why_now), ("Why AI?", case.why_ai), ("Why Cloud?", case.why_cloud), ("Why Secure by Design?", case.why_secure_by_design), ("Why this Transformation?", case.why_this_transformation), ("Cost of Waiting", case.cost_of_waiting)]
    evidence_rows = "".join(f"<tr><td>{escape(e.evidence_id)}</td><td>{escape(e.evidence_class)}</td><td>{escape(e.transformation_dimension)}</td><td>{escape(e.commercial_question_supported)}</td><td>{escape(e.summary)}</td><td>{e.confidence}</td><td>{escape(', '.join(e.unknowns))}</td></tr>" for eid in case.supporting_evidence_ids for e in [evidence_by_id[eid]])
    body = f"""<section class='hero'><h1>{escape(org.organisation)} Transformation Genome</h1><p>{escape(org.sector)} · Conversation level: <strong>{escape(case.conversation_level)}</strong> · Confidence {case.confidence}</p><p>{escape(case.conversation_elevation_reason)}</p></section>
    <section class='card action'><h2>Strategic Conviction Engine</h2><p><strong>Commercial interpretation:</strong> {escape(org.conviction.commercial_interpretation)}</p><p><strong>Transformation hypothesis:</strong> {escape(org.conviction.transformation_hypothesis)}</p><p><strong>Recommended commercial action:</strong> {escape(org.conviction.recommended_commercial_action)}</p><p><strong>Unknowns:</strong> {escape(', '.join(org.conviction.unknowns))}</p></section>
    <section class='card'><h2>Strategic Urgency</h2><p>{escape(org.strategic_urgency.reasoning)}</p><p>State: {escape(org.strategic_urgency.state)} · confidence {org.strategic_urgency.confidence}</p></section>
    <section class='card'><h2>Transformation Window</h2><p>{escape(org.transformation_window.estimated_window)} · momentum {escape(org.transformation_window.momentum)} · confidence {org.transformation_window.evidence_confidence}</p><p><strong>Drivers:</strong> {escape(', '.join(org.transformation_window.primary_drivers))}</p><p><strong>Constraints:</strong> {escape(', '.join(org.transformation_window.primary_constraints))}</p><p>{escape(org.transformation_window.reasoning)}</p></section>
    <section class='card'><h2>Case for Change</h2><table>{''.join(f'<tr><th>{escape(k)}</th><td>{escape(v)}</td></tr>' for k, v in case_rows)}</table><p><strong>Commercial risks:</strong> {escape(', '.join(case.commercial_risks))}</p><p><strong>Contradictory evidence:</strong> {escape(', '.join(case.contradictory_evidence_ids) or 'None yet')}</p><p><strong>Unknowns:</strong> {escape(', '.join(case.unknowns))}</p></section>
    <section class='card'><h2>Observable Forces</h2><table><thead><tr><th>Force</th><th>State</th><th>Reasoning</th><th>Confidence</th><th>Evidence</th><th>Unknowns</th></tr></thead><tbody>{forces}</tbody></table></section>
    <section><h2>Enterprise Transformation Genome</h2>{genome}</section>
    <section class='card'><h2>Supporting Evidence Framework</h2><table><thead><tr><th>ID</th><th>Class</th><th>Dimension</th><th>Question</th><th>Summary</th><th>Confidence</th><th>Unknowns</th></tr></thead><tbody>{evidence_rows}</tbody></table></section>"""
    from cios.applications.flora.workspace.views import _page
    return _page(f"Observatory — {org.organisation}", body)
