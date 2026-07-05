"""Model-backed user-facing memory views for Flora."""
from __future__ import annotations

from html import escape
import re

from cios.applications.flora.memory.repository import EnterpriseModelRepository, ObservationRepository, EvidenceRepository
from cios.applications.flora.live.source_registry import canonical_enterprise_id
from cios.applications.flora.memory.calibration import inspection_rows


def enterprise_memory_panel(enterprise_id: str, models: EnterpriseModelRepository | None = None, observations: ObservationRepository | None = None) -> str:
    """Render maintained Enterprise Model state without rebuilding it from raw Evidence."""
    enterprise_id = canonical_enterprise_id(enterprise_id) or enterprise_id
    model = (models or EnterpriseModelRepository()).get(enterprise_id)
    obs_repo = observations or ObservationRepository()
    rows = []
    for key, attr in sorted(model.attributes.items()):
        certainty = "Contradicted — do not present as certain" if attr.contradiction_state == "contradicted" else "Maintained model state"
        rows.append(f"<tr><th>{escape(key)}</th><td>{escape(str(attr.current_value))}</td><td>{attr.confidence}</td><td>{escape(attr.freshness)}</td><td>{escape(attr.last_observed_date)}</td><td>{escape(certainty)}</td><td>{''.join(f"<a href='#obs-{escape(str(oid))}'>{escape(str(oid))}</a> " for oid in attr.observation_ids)}</td><td>{''.join(f"<a href='#evidence-{escape(str(eid))}'>{escape(str(eid))}</a> " for eid in attr.evidence_ids)}</td></tr>")
    unknowns = "".join(f"<li>{escape(u.question)} · {escape(u.status)} · related observations: {escape(', '.join(u.related_observation_ids))}</li>" for u in model.unknowns.values()) or "<li>No persisted Unknowns for this enterprise.</li>"
    lineage = []
    for obs_id in {oid for a in model.attributes.values() for oid in a.observation_ids}:
        obs = obs_repo.get(obs_id)
        if obs:
            lineage.append(f"<li><strong>{escape(obs.observation_id or '')}</strong>: {escape(obs.atomic_statement)} · Evidence {escape(', '.join(obs.supporting_evidence_ids))}</li>")
    return f"""<section class='card action'><h2>Enterprise Memory</h2><p class='muted'>Maintained Enterprise Model projection rendered from durable Observation memory; reports are views, not memory.</p><table><thead><tr><th>Attribute</th><th>Current value</th><th>Confidence</th><th>Freshness</th><th>Last observed</th><th>State</th><th>Observation lineage</th><th>Evidence lineage</th></tr></thead><tbody>{''.join(rows) or '<tr><td colspan="8">No maintained Enterprise Model state yet.</td></tr>'}</tbody></table><h3>Unknowns</h3><ul>{unknowns}</ul><details><summary><strong>Observation lineage</strong></summary><ul>{''.join(lineage) or '<li>No Observation lineage available.</li>'}</ul></details></section>"""


def calibration_inspection_panel(enterprise_id: str, models: EnterpriseModelRepository | None = None, observations: ObservationRepository | None = None) -> str:
    """Render Evidence → Observation → Enterprise Model diagnostic lineage."""
    rows = inspection_rows(enterprise_id, observations, models)
    html_rows = "".join(f"<tr><td>{escape(str(r['observation_id']))}</td><td>{escape(r['atomic_statement'])}</td><td>{escape(', '.join(r['evidence_ids']))}</td><td>{escape(r['enterprise_id'])}</td><td>{escape(r['affected_model_domain'])}</td><td>{escape(r['affected_attribute'])}</td><td>{escape(r['update_result'])}</td><td>{r['confidence']}</td><td>{escape(r['freshness'])}</td><td>{escape(str(r['rejection_reason'] or ""))}</td></tr>" for r in rows)
    return f"""<section class='card'><h2>Calibration lineage</h2><p>Evidence → Observation → affected Enterprise Model attribute.</p><table><thead><tr><th>Observation ID</th><th>Atomic statement</th><th>Evidence IDs</th><th>Enterprise ID</th><th>Domain</th><th>Attribute</th><th>Update result</th><th>Confidence</th><th>Freshness</th><th>Rejection reason</th></tr></thead><tbody>{html_rows or '<tr><td colspan="10">No accepted Observations for this enterprise.</td></tr>'}</tbody></table></section>"""

from cios.applications.flora.memory.factual_twin import coverage_for_model, maturity_for_model


def factual_digital_twin_workspace(enterprise_id: str, models: EnterpriseModelRepository | None = None, observations: ObservationRepository | None = None, evidence_items: list[dict] | None = None) -> str:
    """Render model-first factual Digital Twin workspace with drill-down lineage."""
    enterprise_id = canonical_enterprise_id(enterprise_id) or enterprise_id
    model = (models or EnterpriseModelRepository()).get(enterprise_id)
    obs_repo = observations or ObservationRepository()
    evidence_items = evidence_items or EvidenceRepository().list()
    evidence_by_id = {str(e.get("evidence_id")): e for e in evidence_items}
    coverage = coverage_for_model(model)
    maturity = maturity_for_model(model)
    obs_ids = {oid for a in model.attributes.values() for oid in a.observation_ids}
    evidence_ids = {eid for a in model.attributes.values() for eid in a.evidence_ids}
    overview = f"""<section class='card action'><h1>BT Digital Twin</h1><p>Status: <strong>{escape(maturity)}</strong></p><p>Canonical ID: {escape(enterprise_id)}</p><p>Sector: {escape(str(model.attributes.get('identity.sector').current_value if model.attributes.get('identity.sector') else 'Unknown'))}</p><p>Last refreshed: {escape(model.updated_at)}</p><p><a href='/financial-intelligence'>Financial Intelligence</a> · <a href='/financial-intelligence'>Refresh Financial Intelligence</a></p><p>Active Observation count: {len(obs_ids)} · Supporting Evidence count: {len(evidence_ids)} · Retired or superseded Observation count: {len([o for o in obs_repo.list() if o.retired_at or o.lifecycle_state in {'retired','superseded'}])} · Unknown count: {len(model.unknowns)} · Contradiction count: {len([a for a in model.attributes.values() if a.contradiction_state == 'contradicted'])} · Stale attribute count: 0</p></section>"""
    cov_rows = ''.join(f"<tr><th>{escape(d)}</th><td>{c['coverage_percent']}%</td><td>{len(c['expected_attributes'])}</td><td>{len(c['populated_attributes'])}</td><td>{len(c['unsupported_attributes'])}</td><td>{len(c['contradicted_attributes'])}</td><td>{c['source_count']}</td></tr>" for d,c in coverage.items())
    tabs = "<nav>Overview | Structure | Financials | Strategy | Leadership | Timeline | Unknowns | Evidence</nav>"
    attr_rows=[]
    for key, attr in sorted(model.attributes.items()):
        ev_pages=[]
        for eid in attr.evidence_ids:
            ev=evidence_by_id.get(eid,{})
            page=ev.get('page_number') or ev.get('page_range') or 'unknown page'
            ev_pages.append(f"{escape(eid)} page {escape(str(page))}")
        attr_rows.append(f"<tr><th>{escape(key)}</th><td>{escape(str(attr.current_value))}</td><td>{escape(attr.freshness)}</td><td>{attr.confidence}</td><td>{escape(attr.last_observed_date)}</td><td>{''.join(f"<a href='#obs-{escape(str(oid))}'>{escape(str(oid))}</a> " for oid in attr.observation_ids)}</td><td>{escape('; '.join(ev_pages) or ', '.join(attr.evidence_ids))}</td><td>{escape(str(attr.prior_values))}</td></tr>")
    def _business_financial_row(key: str, attr) -> str:
        parts = key.split('.')
        metric = parts[2].replace('_', ' ').title().replace('Ebitda', 'EBITDA') if len(parts) > 2 else key
        period = parts[3] if len(parts) > 3 else 'reported period'
        state = parts[4] if len(parts) > 4 else 'actual'
        display_value = str(attr.current_value)
        for oid in attr.observation_ids:
            obs = obs_repo.get(oid)
            if obs:
                m = re.search(r'(£\s*[0-9][0-9,]*(?:\.[0-9]+)?\s*(?:bn|billion|m|million)?)', obs.atomic_statement, re.I)
                if m:
                    display_value = m.group(1).replace(' ', '').replace('billion', 'bn').replace('million', 'm')
                    break
        return f"<tr><th>{escape(metric)}</th><td>{escape(display_value)}</td><td>{escape(period)}</td><td>{escape(state)}</td><td>{escape(attr.freshness)}</td><td>{attr.confidence}</td><td>{''.join(f"<a href='#obs-{escape(str(oid))}'>{escape(str(oid))}</a> " for oid in attr.observation_ids)}</td><td>{''.join(f"<a href='#evidence-{escape(str(eid))}'>{escape(str(eid))}</a> " for eid in attr.evidence_ids)}</td></tr>"

    def domain_panel(title: str, prefix: str) -> str:
        if prefix == 'financial_performance.':
            rows = [_business_financial_row(k, model.attributes[k]) for k in sorted(model.attributes) if k.startswith(prefix)]
            head = '<thead><tr><th>Metric</th><th>Value</th><th>Period</th><th>State</th><th>Freshness</th><th>Confidence</th><th>Observations</th><th>Evidence</th></tr></thead>'
            return f"<section class='card'><h2>{escape(title)}</h2>{'<table>'+head+'<tbody>'+''.join(rows)+'</tbody></table>' if rows else '<p>Not yet established</p>'}</section>"
        rows = [r for k, r in zip(sorted(model.attributes), attr_rows) if k.startswith(prefix)]
        return f"<section class='card'><h2>{escape(title)}</h2>{'<table><tbody>'+''.join(rows)+'</tbody></table>' if rows else '<p>Not yet established</p>'}</section>"
    ev_rows=''.join(f"<tr id='evidence-{escape(str(e.get('evidence_id')))}'><th><a href='#evidence-{escape(str(e.get('evidence_id')))}'>{escape(str(e.get('evidence_id')))}</a></th><td>{escape(str(e.get('metric_identity') or e.get('metric_label') or e.get('commercial_condition')))}</td><td>{escape(str(e.get('display_value') or e.get('value')))}</td><td>{escape(str(e.get('normalised_amount')))}</td><td>{escape(str(e.get('period')))} / {escape(str(e.get('state')))} / {escape(str(e.get('enterprise_scope')))} / {escape(str(e.get('accounting_basis')))}</td><td><a href='{escape(str(e.get('source_url') or '#'))}'>source</a> page {escape(str(e.get('page_number') or e.get('page_range')))}</td><td>{escape(str((e.get('financial_table_evidence_bundle') or {}).get('table_title') or ''))} · {escape(str((e.get('financial_table_evidence_bundle') or {}).get('row_label') or ''))} / {escape(str((e.get('financial_table_evidence_bundle') or {}).get('column_heading') or ''))}</td><td>{escape(str(e.get('source_excerpt') or e.get('extracted_text') or e.get('snippet'))[:360])}</td><td>{escape(str(e.get('extractor_name') or e.get('extraction_method')))} · {escape(str(e.get('extraction_timestamp')))}</td><td>{escape(str(e.get('observation_id')))} · {escape(str(e.get('enterprise_model_path') or e.get('affected_attribute')))}</td></tr>" for e in evidence_items if str(e.get('evidence_id')) in evidence_ids)
    domains_html = domain_panel("Financials", "financial_performance.") + domain_panel("Structure", "structure.") + domain_panel("Strategy", "strategy.") + domain_panel("Leadership", "leadership.") + domain_panel("Identity", "identity.")
    return overview + tabs + domains_html + f"<section class='card'><h2>Domain coverage</h2><table><thead><tr><th>Domain</th><th>Coverage</th><th>Expected</th><th>Populated</th><th>Unsupported</th><th>Contradicted</th><th>Sources</th></tr></thead><tbody>{cov_rows}</tbody></table></section>" + f"<section class='card'><h2>Attribute Detail</h2><table><tbody>{''.join(attr_rows) or '<tr><td>No factual attributes yet.</td></tr>'}</tbody></table></section>" + f"<section class='card'><h2>Evidence Detail</h2><table><thead><tr><th>Evidence</th><th>Metric</th><th>Reported</th><th>Normalised</th><th>Period / state / scope / basis</th><th>Source page</th><th>Table context</th><th>Excerpt</th><th>Extraction</th><th>Lineage</th></tr></thead><tbody>{ev_rows or '<tr><td>No evidence detail loaded.</td></tr>'}</tbody></table></section>"


def factual_digital_twin_page(enterprise_id: str) -> str:
    """Render canonical factual Digital Twin route, including empty BT model state."""
    from cios.applications.flora.live.store import DEFAULT_PATH, read_jsonl
    from cios.applications.flora.workspace.views import _page
    canonical = canonical_enterprise_id(enterprise_id)
    aliases = {"btgroupplc": "bt-group-plc", "bt": "bt-group-plc", "bt-group-plc": "bt-group-plc"}
    canonical = canonical or aliases.get(str(enterprise_id).replace(" ", "").casefold())
    if canonical != "bt-group-plc":
        raise ValueError("Digital Twin enterprise route not found")
    model = EnterpriseModelRepository().get(canonical)
    if not model.attributes:
        body = """<section class='card action'><h1>BT Digital Twin</h1><p>Status: <strong>Not established</strong></p><p><a href='/financial-intelligence'>Financial Intelligence</a> · <a href='/financial-intelligence'>Refresh Financial Intelligence</a></p><p>No accepted factual model state exists yet.</p></section>"""
    else:
        evidence = [e for e in read_jsonl(DEFAULT_PATH) if (e.get("canonical_enterprise_id") or e.get("enterprise_id") or e.get("organisation")) == canonical]
        evidence.extend([e for e in EvidenceRepository().list() if (e.get("canonical_enterprise_id") or e.get("enterprise_id") or e.get("organisation")) == canonical])
        body = factual_digital_twin_workspace(canonical, evidence_items=evidence)
    return _page("BT Digital Twin", body)
