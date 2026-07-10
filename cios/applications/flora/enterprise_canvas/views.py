"""HTML views for Flora's read-only Enterprise Canvas."""
from __future__ import annotations

from html import escape

from cios.applications.flora.enterprise_canvas.service import EnterpriseCanvasAccessError, EnterpriseCanvasNotFoundError, EnterpriseCanvasService
from cios.applications.flora.enterprise_canvas.feedback import ACTIONS, EnterpriseCanvasFeedbackService, FeedbackAccessError
from cios.applications.flora.workspace.views import _page


def enterprise_canvas_page(enterprise_id: str, headers, selected_tile_id: str = "") -> tuple[str, int]:
    """Render the organisation-lens Canvas without mutating canonical state."""
    try:
        canvas = EnterpriseCanvasService().get_canvas(enterprise_id, headers)
    except EnterpriseCanvasAccessError:
        return _page("Enterprise Canvas access denied", "<section class='hero'><h1>Access denied</h1><p>You do not have access to this Enterprise Canvas.</p></section>"), 403
    except EnterpriseCanvasNotFoundError as exc:
        return _page("Enterprise Canvas not found", f"<section class='hero'><h1>Enterprise Canvas not found</h1><p>{escape(str(exc))}</p></section>"), 404
    except ValueError as exc:
        return _page("Enterprise Canvas unavailable", f"<section class='hero'><h1>Canvas unavailable</h1><p>{escape(str(exc))}</p></section>"), 404

    h = canvas.header
    selected = next((tile for tile in canvas.tiles if tile.tile_view_id == selected_tile_id), None)
    if not selected and selected_tile_id:
        return _page("Enterprise Canvas tile unavailable", "<section class='hero'><h1>Tile unavailable</h1><p>The requested area is not available in this Canvas read model.</p></section>"), 404
    tiles = "".join(_tile_card(canvas.enterprise_id, tile, selected and tile.tile_view_id == selected.tile_view_id) for tile in canvas.tiles)
    detail = _tile_detail(canvas.enterprise_id, selected, headers) if selected else _empty_detail()
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


def _tile_detail(enterprise_id: str, tile, headers) -> str:
    facts = ''.join(f'<li>{escape(f)}</li>' for f in tile.core_facts) or '<li>No core facts supplied.</li>'
    pains = ''.join(_projection_item(p) for p in tile.analytical_projections if p.projection_type in {'pain_point','burning_platform','transformation_pressure_view'}) or f'<li>{escape(tile.principal_pain_or_pressure)}</li>'
    responses = ''.join(_projection_item(p) for p in tile.analytical_projections if p.projection_type in {'current_response','response_effectiveness'}) or f'<li>{escape(tile.what_has_been_done_so_far)}</li>'
    unresolved = ''.join(_projection_item(p) for p in tile.analytical_projections if p.projection_type == 'residual_pain') or f'<li>{escape(tile.what_remains_unresolved)}</li>'
    evidence = f"<li><a href='/digital-twins/{escape(enterprise_id)}/canvas/tiles/{escape(tile.tile_view_id)}/lineage'>Inspect evidence and lineage</a><br><span class='muted'>Source type/reference and Evidence/date reference are available in the lineage inspection.</span></li>"
    return f"""<aside class='card detail-panel' role='region' aria-labelledby='tile-detail'><p><a href='/digital-twins/{escape(enterprise_id)}/canvas'>Close detail panel</a></p><h2 id='tile-detail'>{escape(tile.display_name)} detail</h2>
    <h3>What this area does</h3><p>{escape(tile.plain_english_role)}</p><h3>Why it matters</h3><p>This area is part of the governed enterprise organisation lens and is material enough to appear in the read-model tile order.</p><h3>Core facts</h3><ul>{facts}</ul><h3>What has changed</h3><p>{escape(tile.material_change)}</p><h3>What is causing pressure</h3><ul>{pains}</ul><h3>What has been done so far</h3><ul>{responses}</ul><h3>What remains unresolved</h3><ul>{unresolved}</ul><h3>Stakeholders or accountable roles</h3><p>{escape(tile.accountable_role)}</p><h3>What we still do not know</h3>{_markers(tile)}<h3>Evidence freshness</h3><p>Effective date: {escape(tile.effective_date)}. Source cut-off: {escape(tile.source_cut_off)}. Last refreshed: {escape(tile.last_refreshed_date)}.</p><h3>Suggested next posture</h3><p>{escape(_next_posture(tile))}</p><h3>Inspect evidence</h3><ul class='evidence-list'>{evidence}</ul>{_feedback_panel(enterprise_id, tile.tile_view_id, tile.principal_pain_or_pressure, '', headers)}</aside>"""


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


def enterprise_canvas_lineage_page(enterprise_id: str, tile_id: str, headers) -> tuple[str, int]:
    """Render the read-only lineage inspection behind Inspect evidence."""
    try:
        inspection = EnterpriseCanvasService().get_lineage_inspection(enterprise_id, tile_id, headers)
    except EnterpriseCanvasAccessError:
        return _page("Lineage access denied", "<section class='hero'><h1>Access denied</h1><p>You do not have access to this lineage inspection.</p></section>"), 403
    except ValueError as exc:
        return _page("Lineage unavailable", f"<section class='hero'><h1>Lineage unavailable</h1><p>{escape(str(exc))}</p></section>"), 404
    obs = ''.join(f"<li><strong>{escape(o.get('plain_english_summary',''))}</strong><br><span class='muted'>Observation reference: {escape(o.get('observation_id',''))}. Effective date: {escape(o.get('observation_date','Unknown'))}. Confidence: {escape(str(o.get('confidence','Not supplied')))}. Provenance: {escape(o.get('provenance_type','Unknown'))}.</span></li>" for o in inspection.observations) or '<li>No Observation is linked to this displayed statement.</li>'
    evs = ''.join(_evidence_detail(e) for e in inspection.evidence) or '<li>No Evidence is linked to this displayed statement.</li>'
    srcs = ''.join(f"<li><strong>{escape(s.get('title',''))}</strong><br>Type: {escape(s.get('type','Unknown'))}. Reference: {escape(s.get('url_or_reference','Not supplied'))}.<br><span class='muted'>Source ID: {escape(str(s.get('source_id','')))}</span></li>" for s in inspection.sources) or '<li>No Source details are available.</li>'
    pkgs = ''.join(f"<li><strong>{escape(p.get('package_ref',''))}</strong><br>Package: {escape(p.get('package_id',''))} {escape(p.get('package_version',''))}. Import run: {escape(p.get('import_run_id',''))}.<br>Original Blueprint location: {escape(', '.join(p.get('source_files',[])[:6]) or p.get('archive_path','Not supplied'))}</li>" for p in inspection.packages) or '<li>No imported package location is available.</li>'
    human = ''.join(f"<li><strong>Human-supplied knowledge</strong>: {escape(h.get('statement',''))}<br>Contributor or role: {escape(str(h.get('contributor') or h.get('role') or 'authorised user not disclosed'))}. Date supplied: {escape(str(h.get('date_supplied') or h.get('supplied_at') or 'not supplied'))}. Purpose: {escape(str(h.get('purpose','not supplied')))}. Relationship: calibration, account knowledge or validation as governed by provenance.</li>" for h in inspection.human_supplied_knowledge) or '<li>No human-supplied knowledge is linked to this statement.</li>'
    unks = ''.join(f"<li><strong>{escape(u.get('question',''))}</strong><br>Why it matters: {escape(u.get('why_it_matters',''))}. What could resolve it: {escape(u.get('what_could_resolve_it',''))}.</li>" for u in inspection.unknowns) or '<li>No Unknown is linked to this statement.</li>'
    cons = ''.join(f"<li><strong>{escape(c.get('statement',''))}</strong><br>Conflicting positions: {escape(', '.join(c.get('conflicting_positions',[])) or 'not supplied')}. Why retained: {escape(c.get('why_retained',''))}. Resolution path: compare the competing Observations with fresher governed Evidence.</li>" for c in inspection.contradictions) or '<li>No Contradiction is linked to this statement.</li>'
    missing = ''.join(f"<li>{escape(m)} Flora can still display the judgement when it is an accepted projection or canonical record, but stronger Observation, Evidence, Source and package references would improve confidence.</li>" for m in inspection.missing_lineage) or '<li>No incomplete lineage gaps detected.</li>'
    broken = ''.join(f"<li>{escape(b)}</li>" for b in inspection.broken_references) or '<li>No broken references detected.</li>'
    body=f"""<section class='hero'><p><a href='/digital-twins/{escape(enterprise_id)}/canvas/tiles/{escape(tile_id)}'>Return to tile detail</a></p><h1>Why Flora shows this</h1><p>{escape(inspection.displayed_statement)}</p><p class='pill'>Read-only lineage inspection</p></section><main class='card'><h2>What was observed</h2><ol>{obs}</ol><h2>Evidence supporting this</h2><ol>{evs}</ol><h2>Where the evidence came from</h2><ol>{srcs}</ol><h2>Human-supplied knowledge</h2><ol>{human}</ol><h2>What remains uncertain</h2><ol>{unks}</ol><h2>Conflicting evidence</h2><ol>{cons}</ol><h2>Original Blueprint location</h2><ol>{pkgs}</ol><h2>Missing or incomplete lineage</h2><ol>{missing}</ol><h2>Technical inspection references</h2><p>Displayed statement → analytical projection or canonical record → Observation → Evidence → Source → imported package.</p><p>Projection or record reference: {escape(inspection.projection_or_record)}.</p><h3>Broken references</h3><ol>{broken}</ol>{_feedback_panel(enterprise_id, tile_id, inspection.displayed_statement, inspection.projection_or_record, headers)}</main>"""
    return _page("Enterprise Canvas lineage inspection", body), 200


def _evidence_detail(e) -> str:
    rel = e.get('relationship_to_judgement','supports')
    label = 'Contrary Evidence' if 'contradict' in rel or 'weaken' in rel else 'Supporting Evidence'
    return f"<li><strong>{escape(label)} — {escape(e.get('source_title',''))}</strong><br>Source type: {escape(e.get('source_type','Unknown'))}. Publication or effective date: {escape(e.get('publication_or_effective_date','Unknown'))}. Freshness: {escape(e.get('freshness','Unknown'))}.<br>Summary: {escape(str(e.get('supporting_summary',''))[:500])}<br>Exact source location: {escape(str(e.get('source_location','Not supplied')))}. Confidence or qualification: {escape(str(e.get('confidence_or_qualification','Not supplied')))}.<br>Package and import reference: {escape(str(e.get('package_ref') or 'not supplied'))} {escape(str(e.get('import_run_id') or ''))}.</li>"


def _feedback_panel(enterprise_id: str, tile_id: str, judgement: str, lineage_ref: str, headers) -> str:
    options = ''.join(f"<option value='{escape(k)}'>{escape(v)}</option>" for k, v in ACTIONS.items())
    return f"""<section class='card' aria-labelledby='candidate-feedback'><h3 id='candidate-feedback'>Contribute governed feedback</h3><p><strong>This contribution will be stored as candidate human knowledge. It will not change the governed Twin until reviewed and accepted.</strong></p>
    <form method='post' action='/digital-twins/{escape(enterprise_id)}/canvas/feedback'>
    <input type='hidden' name='enterprise_id' value='{escape(enterprise_id)}'><input type='hidden' name='tile_view_id' value='{escape(tile_id)}'><input type='hidden' name='displayed_judgement_ref' value='{escape(judgement)}'><input type='hidden' name='lineage_ref' value='{escape(lineage_ref)}'>
    <label>Feedback action <select name='action_type'>{options}</select></label>
    <label>Statement <textarea name='user_statement' required></textarea></label>
    <label>Rationale <textarea name='rationale' required></textarea></label>
    <label>Expected consequence <input name='expected_consequence'></label>
    <label>Human-Supplied Knowledge label <select name='human_knowledge_classification'><option value='not_human_knowledge'>Not Human-Supplied Knowledge</option><option value='direct_knowledge'>Direct knowledge</option><option value='interpretation'>Interpretation</option><option value='account_knowledge'>Account knowledge</option><option value='calibration'>Calibration</option><option value='validation'>Validation</option></select></label>
    <label>Visibility <select name='visibility'><option value='standard'>Standard</option><option value='restricted'>Restricted</option><option value='account_confidential'>Account confidential</option></select></label>
    <button type='submit'>Submit candidate feedback</button></form>{_feedback_status_list(enterprise_id, tile_id, headers)}</section>"""


def _feedback_status_list(enterprise_id: str, tile_id: str, headers) -> str:
    records = EnterpriseCanvasFeedbackService().visible_feedback(headers, enterprise_id, tile_view_id=tile_id)
    if not records:
        return "<p class='muted'>No submitted feedback is visible to this user for this item.</p>"
    items = "".join(f"<li><strong>{escape(ACTIONS.get(r.action_type, r.action_type))}</strong>: {escape(r.status)}<br><span class='muted'>Feedback ID: {escape(r.feedback_id)}. Supplied by: {escape(r.contributor_identity)} ({escape(r.contributor_role)}). Visibility: {escape(r.visibility)}.</span></li>" for r in records)
    return f"<h4>Submitted feedback status</h4><ol>{items}</ol>"


def submit_enterprise_canvas_feedback(form: dict, headers) -> tuple[str, int, str]:
    try:
        record = EnterpriseCanvasFeedbackService().submit(headers, **{k: (v[0] if isinstance(v, list) else v) for k, v in form.items()})
    except FeedbackAccessError:
        return _page("Feedback access denied", "<section class='hero'><h1>Access denied</h1><p>You are not authorised to submit Enterprise Canvas feedback.</p></section>"), 403, ""
    except ValueError as exc:
        return _page("Feedback not submitted", f"<section class='hero'><h1>Feedback not submitted</h1><p>{escape(str(exc))}</p></section>"), 400, ""
    target = f"/digital-twins/{escape(record.enterprise_id)}/canvas/tiles/{escape(record.tile_view_id)}?feedback={escape(record.feedback_id)}"
    html = _page("Feedback submitted", f"<section class='hero'><h1>Feedback submitted</h1><p>Feedback {escape(record.feedback_id)} is now {escape(record.status)}.</p><p>This candidate contribution has not changed canonical Evidence, Observations or Enterprise Model state.</p><p><a href='{target}'>Return to Canvas</a></p></section>")
    return html, 201, target
