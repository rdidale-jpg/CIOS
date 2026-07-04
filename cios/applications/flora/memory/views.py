"""Model-backed user-facing memory views for Flora."""
from __future__ import annotations

from html import escape

from cios.applications.flora.memory.repository import EnterpriseModelRepository, ObservationRepository


def enterprise_memory_panel(enterprise_id: str, models: EnterpriseModelRepository | None = None, observations: ObservationRepository | None = None) -> str:
    """Render maintained Enterprise Model state without rebuilding it from raw Evidence."""
    model = (models or EnterpriseModelRepository()).get(enterprise_id)
    obs_repo = observations or ObservationRepository()
    rows = []
    for key, attr in sorted(model.attributes.items()):
        certainty = "Contradicted — do not present as certain" if attr.contradiction_state == "contradicted" else "Maintained model state"
        rows.append(f"<tr><th>{escape(key)}</th><td>{escape(str(attr.current_value))}</td><td>{attr.confidence}</td><td>{escape(attr.freshness)}</td><td>{escape(attr.last_observed_date)}</td><td>{escape(certainty)}</td><td>{escape(', '.join(attr.observation_ids))}</td><td>{escape(', '.join(attr.evidence_ids))}</td></tr>")
    unknowns = "".join(f"<li>{escape(u.question)} · {escape(u.status)} · related observations: {escape(', '.join(u.related_observation_ids))}</li>" for u in model.unknowns.values()) or "<li>No persisted Unknowns for this enterprise.</li>"
    lineage = []
    for obs_id in {oid for a in model.attributes.values() for oid in a.observation_ids}:
        obs = obs_repo.get(obs_id)
        if obs:
            lineage.append(f"<li><strong>{escape(obs.observation_id or '')}</strong>: {escape(obs.atomic_statement)} · Evidence {escape(', '.join(obs.supporting_evidence_ids))}</li>")
    return f"""<section class='card action'><h2>Enterprise Memory</h2><p class='muted'>Maintained Enterprise Model projection rendered from durable Observation memory; reports are views, not memory.</p><table><thead><tr><th>Attribute</th><th>Current value</th><th>Confidence</th><th>Freshness</th><th>Last observed</th><th>State</th><th>Observation lineage</th><th>Evidence lineage</th></tr></thead><tbody>{''.join(rows) or '<tr><td colspan="8">No maintained Enterprise Model state yet.</td></tr>'}</tbody></table><h3>Unknowns</h3><ul>{unknowns}</ul><details><summary><strong>Observation lineage</strong></summary><ul>{''.join(lineage) or '<li>No Observation lineage available.</li>'}</ul></details></section>"""
