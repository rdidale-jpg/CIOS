"""HTML views for the visible Flora Runtime Increment 1 workspace slice."""
from __future__ import annotations

from html import escape
from typing import Any

from cios.applications.flora.runtime.increment1 import SUPPORTED_OBJECT_ID, load_fixture, open_focus_object


def _value(value: Any) -> str:
    if value is None or value == "":
        return "Unknown / unavailable"
    return escape(str(value))


def _pill(label: str, value: Any) -> str:
    return f"<span class='pill'><strong>{escape(label)}:</strong> {_value(value)}</span>"


def _safe_notice(notice: dict[str, Any]) -> str:
    return (
        "<article class='notice safe-unavailable'>"
        "<h3>Safe-unavailable state</h3>"
        f"<p><strong>Status:</strong> {_value(notice.get('status', 'safe_unavailable'))}</p>"
        f"<p><strong>Reason:</strong> {_value(notice.get('reason_code'))}</p>"
        f"<p>{_value(notice.get('user_safe_explanation') or notice.get('message'))}</p>"
        f"<p><strong>Retryable:</strong> {_value(notice.get('retryable'))}</p>"
        "</article>"
    )


def increment1_workspace_page(object_id: str = SUPPORTED_OBJECT_ID) -> tuple[str, int]:
    result = open_focus_object(object_id)
    if isinstance(result, dict):
        return _page("Flora Increment 1 workspace unavailable", f"<main class='i1-shell'>{_safe_notice(result)}<p><a href='/flora'>Return to Flora</a></p></main>"), 200
    w = result.to_dict()
    focus = w["focus_object"]
    ident = focus["identity"]
    body = f"""
    <main class='i1-shell' data-contract-version='flora-runtime-v0.1' data-fixture-source='uk-banking-governed-corpus'>
      <nav class='boundary'><a href='/flora'>Flora home</a> / <strong>Increment 1 Lloyds workspace</strong><span>Legacy prototype remains at /flora and is labelled as pre-Increment-1 navigation.</span></nav>
      <section class='hero focus-object' aria-labelledby='focus-title'>
        <p class='eyebrow'>Focus Object · Frozen V0.1 read projection · UK Banking governed corpus</p>
        <h1 id='focus-title'>Lloyds Banking Group</h1>
        <p><strong>Projection label:</strong> {_value(focus.get('display_name'))}</p>
        <p>{_value(focus.get('short_description'))}</p>
        <div class='pill-row'>
          {_pill('Object ID', ident.get('object_id'))}{_pill('Object type', ident.get('object_type'))}{_pill('Canonical owner', ident.get('canonical_owner'))}
          {_pill('Authority', ident.get('authority_status'))}{_pill('Lifecycle', ident.get('lifecycle_status'))}{_pill('Freshness', ident.get('freshness_status'))}
          {_pill('Persistence', focus.get('persistence_class'))}
        </div>
        <p><strong>Provenance access:</strong> {_value(ident.get('provenance_reference'))}</p>
      </section>
      {_relationships(w['relationships'])}
      {_availability(w['evidence_observation_availability'])}
      {_unknowns(w['unknowns'])}
      {_contradictions(w['contradictions'])}
      {_lineage(w['lineage'])}
      {_lineage_examples()}
      {_workspace_state(w['workspace_state'])}
      <section class='card'><h2>Safe-unavailable test states</h2><p>Contract-defined unavailable responses are rendered without fabricated fallback content.</p><p><a href='/flora/object/unsupported-object'>Open unresolved identity safe-unavailable state</a></p>{''.join(_safe_notice(n) for n in w['safe_unavailable_notices']) or '<p>No runtime section notices for this read projection.</p>'}</section>
    </main>
    """
    return _page("Flora Increment 1 Lloyds workspace", body), 200


def _relationships(items: list[dict[str, Any]]) -> str:
    rows = "".join(f"<tr><td>{_value(r.get('relationship_type'))}</td><td>{_value(r.get('source_object_id'))}</td><td>{_value(r.get('target_object_id') or r.get('target_original_identifier'))}</td><td>{_value(r.get('authority_status'))}</td><td>{_value(r.get('resolution_status'))}</td><td>{_value(r.get('provenance'))}</td></tr>" for r in items)
    return f"<section class='card'><h2>Governed relationships only</h2><p>No inferred relationships are shown; unresolved targets stay explicit.</p><table><thead><tr><th>Type</th><th>Source</th><th>Target</th><th>Authority</th><th>Resolution</th><th>Provenance</th></tr></thead><tbody>{rows}</tbody></table></section>"


def _availability(a: dict[str, Any]) -> str:
    return f"<section class='card'><h2>Intelligence availability</h2><div class='metric-grid'><article><h3>Evidence available</h3><p>{_value(a.get('evidence_count'))}</p></article><article><h3>Observations available</h3><p>{_value(a.get('observation_count'))}</p><small>Accepted: {_value(a.get('accepted_observation_count'))}</small></article><article><h3>Inaccessible records</h3><p>{_value(a.get('inaccessible_count'))}</p></article><article><h3>Unavailable records</h3><p>{_value(a.get('unavailable_count'))}</p></article><article><h3>Lineage coverage</h3><p>{_value(a.get('lineage_coverage'))}</p></article></div><p><strong>Freshness:</strong> {_value(a.get('freshness_summary'))}</p><p><strong>Authority:</strong> {_value(a.get('authority_summary'))}</p></section>"


def _unknowns(items):
    return "<section class='card unknowns'><h2>Governed Unknowns</h2>" + "".join(f"<article><h3>{_value(u.get('unknown_id'))}</h3><p>{_value(u.get('statement'))}</p><p><strong>Evidence demand:</strong> {_value(u.get('evidence_demand'))}</p><p><strong>Distinction:</strong> {_value(u.get('distinction'))}</p></article>" for u in items) + "</section>"


def _contradictions(items):
    cards=[]
    for c in items:
        sides="".join(f"<li>{_value(r.get('type'))} {_value(r.get('id'))} · source {_value(r.get('source_asset_id'))}</li>" for r in c.get('conflicting_references', []))
        cards.append(f"<article><h3>{_value(c.get('contradiction_id'))} · {_value(c.get('status'))}</h3><p>{_value(c.get('contradiction_statement'))}</p><h4>Both sides retained</h4><ul>{sides}</ul><p><strong>Materiality:</strong> {_value(c.get('materiality'))}</p></article>")
    return "<section class='card contradictions'><h2>Open Contradictions</h2>" + "".join(cards) + "</section>"


def _lineage(l):
    nodes="".join(f"<li><strong>{_value(n.get('node_type'))}</strong> → {_value(n.get('node_id'))} · {_value(n.get('provenance_reference'))}</li>" for n in l.get('lineage_nodes', []))
    edges="".join(f"<li>{_value(e.get('from'))} → {_value(e.get('to'))} ({_value(e.get('edge_type'))})</li>" for e in l.get('lineage_edges', []))
    return f"<section class='card lineage'><h2>Inspectable lineage</h2><p><strong>Completeness:</strong> {_value(l.get('completeness_status'))}</p><ol>{nodes}</ol><h3>Presentation projection path</h3><ul>{edges}</ul><p>Partial and access-redacted segments: {_value(len(l.get('unavailable_segments', [])))} unavailable; {_value(len(l.get('access_redacted_segments', [])))} redacted.</p></section>"


def _lineage_examples() -> str:
    partial = load_fixture("partial", "lineage-partial.json")
    redacted = load_fixture("partial", "lineage-access-redacted.json")
    unresolved = load_fixture("partial", "relationship-unresolved-target.json")
    partial_segments = "; ".join(partial.get("unavailable_segments", []))
    redacted_segments = "; ".join(redacted.get("access_redacted_segments", []))
    return (
        "<section class='card lineage'><h2>Partial and inaccessible lineage examples</h2>"
        "<p>Unavailable lineage is labelled as incomplete rather than shown as absent.</p>"
        f"<p><strong>Partial lineage:</strong> {_value(partial.get('completeness_status'))} — {_value(partial_segments)}</p>"
        f"<p><strong>Access-redacted lineage:</strong> {_value(redacted.get('completeness_status'))} — {_value(redacted_segments)}</p>"
        f"<p><strong>Unresolved relationship:</strong> {_value(unresolved.get('target_original_identifier'))}; status {_value(unresolved.get('resolution_status'))}.</p>"
        "</section>"
    )


def _workspace_state(s):
    return f"<section class='card'><h2>Workspace state (non-canonical)</h2><p>State ID {_value(s.get('workspace_state_id'))}; retention {_value(s.get('retention_class'))}; active perspective {_value(s.get('active_perspective'))}.</p></section>"


def _page(title: str, body: str) -> str:
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>body{{font-family:Inter,Arial,sans-serif;background:#f5f7fb;color:#172033;margin:0}}.i1-shell{{max-width:1180px;margin:auto;padding:28px}}.hero,.card{{background:white;border:1px solid #d7deea;border-radius:18px;padding:22px;margin:18px 0;box-shadow:0 8px 24px #14213d14}}.eyebrow{{text-transform:uppercase;letter-spacing:.08em;color:#3556a6;font-weight:700}}.pill-row{{display:flex;flex-wrap:wrap;gap:8px}}.pill{{background:#edf3ff;border:1px solid #cbd8f1;border-radius:999px;padding:8px 10px}}table{{width:100%;border-collapse:collapse}}th,td{{border-top:1px solid #e3e8f1;padding:10px;text-align:left;vertical-align:top}}.metric-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px}}.metric-grid article{{border:1px solid #e1e7f0;border-radius:12px;padding:12px}}.unknowns{{border-left:6px solid #8a5cf6}}.contradictions{{border-left:6px solid #d97706}}.lineage{{border-left:6px solid #0284c7}}.safe-unavailable{{border-left:6px solid #b91c1c;background:#fff7f7}}.boundary{{display:flex;gap:14px;align-items:center;flex-wrap:wrap}}</style></head><body>{body}</body></html>"
