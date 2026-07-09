"""HTML views for Flora's read-only Enterprise Canvas."""
from __future__ import annotations

from html import escape

from cios.applications.flora.enterprise_canvas.service import EnterpriseCanvasAccessError, EnterpriseCanvasService
from cios.applications.flora.workspace.views import _page


def enterprise_canvas_page(enterprise_id: str, headers, selected_tile_id: str = "") -> tuple[str, int]:
    """Render the organisation-lens Canvas without mutating canonical state."""
    try:
        canvas = EnterpriseCanvasService().get_canvas(enterprise_id, headers)
    except EnterpriseCanvasAccessError:
        return _page("Enterprise Canvas access denied", "<section class='hero'><h1>Access denied</h1><p>You do not have access to this Enterprise Canvas.</p></section>"), 403
    except ValueError as exc:
        return _page("Enterprise Canvas unavailable", f"<section class='hero'><h1>Canvas unavailable</h1><p>{escape(str(exc))}</p></section>"), 404

    h = canvas.header
    selected = next((tile for tile in canvas.tiles if tile.tile_view_id == selected_tile_id), None)
    if not selected and selected_tile_id:
        return _page("Enterprise Canvas tile unavailable", "<section class='hero'><h1>Tile unavailable</h1><p>The requested area is not available in this Canvas read model.</p></section>"), 404
    tiles = "".join(_tile_card(canvas.enterprise_id, tile, selected and tile.tile_view_id == selected.tile_view_id) for tile in canvas.tiles)
    detail = _tile_detail(canvas.enterprise_id, selected) if selected else _empty_detail()
    empty = "<section class='card'><h2>No organisation areas available</h2><p>Flora has access to this enterprise, but the governed read model does not yet contain accepted organisation areas.</p></section>" if not canvas.tiles else ""
    freshness = f"<p class='pill' aria-label='Freshness warning'>{escape(h.freshness_warning)}</p>" if h.freshness_warning else ""
    pressures = "".join(f"<li>{escape(p)}</li>" for p in h.current_material_pressures) or "<li>None supplied by the read model.</li>"
    body = f"""
    <style>
    .canvas-header dl{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}} .canvas-header dt{{font-weight:700}} .canvas-header dd{{margin:0}}
    .canvas-layout{{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(300px,.9fr);gap:18px;align-items:start}} .tile-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px}}
    .canvas-tile{{display:block;text-decoration:none;color:inherit;border:2px solid #ded8ce;border-radius:16px;padding:16px;background:#fff}} .canvas-tile:focus,.canvas-tile:hover{{outline:3px solid #185c4d;outline-offset:2px}} .canvas-tile[aria-current='true']{{border-color:#185c4d;background:#f8fbf9}}
    .marker{{display:inline-block;border:1px solid #8b8177;border-radius:999px;padding:3px 8px;margin:2px;background:#fff7df}} .marker-unknown{{background:#eef3ff}} .marker-contradiction{{background:#fff0f0}} .marker-stale{{background:#fff7df}} .marker-nested{{background:#eef8f0}}
    .detail-panel{{position:sticky;top:12px}} .evidence-list li{{margin-bottom:8px}} @media(max-width:820px){{.canvas-layout{{grid-template-columns:1fr}} .detail-panel{{position:static}}}}
    </style>
    <section class='hero canvas-header'><p><a href='/digital-twins'>Digital Twins</a></p><h1>{escape(h.enterprise_name)}</h1><p>{escape(h.enterprise_purpose)}</p>{freshness}<dl>
    <div><dt>Twin version</dt><dd>{escape(h.twin_version)}</dd></div><div><dt>Effective date</dt><dd>{escape(h.effective_date)}</dd></div><div><dt>Source cut-off</dt><dd>{escape(h.source_cut_off)}</dd></div><div><dt>Maturity or acceptance</dt><dd>{escape(h.maturity_or_acceptance_state)}</dd></div><div><dt>Latest material change</dt><dd>{escape(h.latest_material_change or 'Not supplied')}</dd></div><div><dt>Last refreshed</dt><dd>{escape(h.last_refreshed_date)}</dd></div></dl>
    <details><summary><strong>Current material pressures supplied by the read model</strong></summary><ul>{pressures}</ul></details></section>
    <main class='canvas-layout'><section aria-labelledby='organisation-lens'><h2 id='organisation-lens'>Organisation lens</h2>{empty}<div class='tile-grid'>{tiles}</div></section>{detail}</main>
    """
    return _page(f"Enterprise Canvas — {h.enterprise_name}", body), 200


def _tile_card(enterprise_id: str, tile, selected: bool) -> str:
    markers = _markers(tile)
    return f"""<a class='canvas-tile' href='/digital-twins/{escape(enterprise_id)}/canvas/tiles/{escape(tile.tile_view_id)}' aria-current='{str(bool(selected)).lower()}' aria-label='Open {escape(tile.display_name)} organisation tile, state {escape(tile.current_state)}'>
    <article><p class='muted'>Tile {tile.sort_order}</p><h3>{escape(tile.display_name)}</h3><p>{escape(tile.plain_english_role)}</p><p><strong>Accountable role:</strong> {escape(tile.accountable_role)}</p><p><strong>Current state:</strong> {escape(tile.current_state)}</p><p><strong>Principal pain or pressure:</strong> {escape(tile.principal_pain_or_pressure)}</p><p><strong>Attention:</strong> {escape(tile.material_change)}</p>{markers}</article></a>"""


def _markers(tile) -> str:
    items = []
    if tile.unknown_indicator: items.append("<span class='marker marker-unknown'>Unknown present</span>")
    if tile.contradiction_indicator: items.append("<span class='marker marker-contradiction'>Contradiction present</span>")
    if tile.stale_evidence_indicator: items.append("<span class='marker marker-stale'>Stale evidence</span>")
    if tile.nested_twin_available: items.append("<span class='marker marker-nested'>Nested Twin available</span>")
    return "<p>" + " ".join(items or ["<span class='marker'>No special indicators supplied</span>"]) + "</p>"


def _empty_detail() -> str:
    return "<aside class='card detail-panel' aria-labelledby='tile-detail'><h2 id='tile-detail'>Tile detail</h2><p>Select an organisation tile to inspect core facts, pressures, responses, unresolved issues and evidence.</p></aside>"


def _tile_detail(enterprise_id: str, tile) -> str:
    facts = ''.join(f'<li>{escape(f)}</li>' for f in tile.core_facts) or '<li>No core facts supplied.</li>'
    pains = ''.join(_projection_item(p) for p in tile.analytical_projections if p.projection_type in {'pain_point','burning_platform','transformation_pressure_view'}) or f'<li>{escape(tile.principal_pain_or_pressure)}</li>'
    responses = ''.join(_projection_item(p) for p in tile.analytical_projections if p.projection_type in {'current_response','response_effectiveness'}) or f'<li>{escape(tile.what_has_been_done_so_far)}</li>'
    unresolved = ''.join(_projection_item(p) for p in tile.analytical_projections if p.projection_type == 'residual_pain') or f'<li>{escape(tile.what_remains_unresolved)}</li>'
    evidence = ''.join(_lineage_item(ref) for ref in tile.lineage_references[:12]) or '<li>No lineage references supplied for this tile.</li>'
    return f"""<aside class='card detail-panel' role='region' aria-labelledby='tile-detail'><p><a href='/digital-twins/{escape(enterprise_id)}/canvas'>Close detail panel</a></p><h2 id='tile-detail'>{escape(tile.display_name)} detail</h2>
    <h3>What this area does</h3><p>{escape(tile.plain_english_role)}</p><h3>Why it matters</h3><p>This area is part of the governed enterprise organisation lens and is material enough to appear in the read-model tile order.</p><h3>Core facts</h3><ul>{facts}</ul><h3>What has changed</h3><p>{escape(tile.material_change)}</p><h3>What is causing pressure</h3><ul>{pains}</ul><h3>What has been done so far</h3><ul>{responses}</ul><h3>What remains unresolved</h3><ul>{unresolved}</ul><h3>Stakeholders or accountable roles</h3><p>{escape(tile.accountable_role)}</p><h3>What we still do not know</h3>{_markers(tile)}<h3>Evidence freshness</h3><p>Effective date: {escape(tile.effective_date)}. Source cut-off: {escape(tile.source_cut_off)}. Last refreshed: {escape(tile.last_refreshed_date)}.</p><h3>Suggested next posture</h3><p>{escape(_next_posture(tile))}</p><h3>Inspect evidence</h3><ul class='evidence-list'>{evidence}</ul></aside>"""


def _projection_item(p) -> str:
    q = f" Governed qualification: {p.confidence_or_qualification}." if p.confidence_or_qualification else ""
    return f"<li><strong>{escape(p.display_label)}</strong><br><span class='muted'>Current or future-facing status: {escape(p.status or 'not supplied')}. Response or proof state is shown separately where the read model supplies it.{escape(q)}</span></li>"


def _lineage_item(ref) -> str:
    source = ', '.join(ref.source_ids) or ref.package_ref or ref.reference_id
    dates = ', '.join(ref.evidence_ids) or ref.import_run_id or 'date not supplied'
    return f"<li><strong>{escape(ref.reference_type.replace('_',' '))}</strong>: {escape(ref.displayed_judgement)}<br><span class='muted'>Source type/reference: {escape(source)} · Evidence/date reference: {escape(dates)}</span></li>"


def _next_posture(tile) -> str:
    for p in tile.analytical_projections:
        if p.projection_type in {'suggested_next_posture','analytical_posture'}:
            return p.display_label
    return 'No suggested next posture supplied by the read model.'
