"""HTML views for Flora's read-only Enterprise Canvas."""
from __future__ import annotations

from html import escape

from cios.applications.flora.enterprise_canvas.service import EnterpriseCanvasAccessError, EnterpriseCanvasNotFoundError, EnterpriseCanvasService
from cios.applications.flora.enterprise_canvas.feedback import ACTIONS, EnterpriseCanvasFeedbackService, FeedbackAccessError
from cios.applications.flora.enterprise_intelligence.runtime import latest_result
from cios.applications.flora.enterprise_intelligence.provider import provider_diagnostics
from cios.applications.flora.workspace.views import _page

EXEC_NAV = ("Overview","How Enterprise Works","Material Pressures","Change Portfolio","Decision Landscape","Commercial Relevance","Unknowns & Contradictions","Recommended Next Moves","Model Explorer","Evidence & Lineage")

def enterprise_canvas_page(enterprise_id: str, headers, selected_tile_id: str = "") -> tuple[str, int]:
    """Render the executive commercial Canvas without mutating canonical state."""
    try:
        canvas = EnterpriseCanvasService().get_canvas(enterprise_id, headers)
    except EnterpriseCanvasAccessError:
        return _page("Enterprise Canvas access denied", "<section class='hero'><h1>Access denied</h1><p>You do not have access to this Enterprise Canvas.</p></section>"), 403
    except EnterpriseCanvasNotFoundError as exc:
        return _page("Enterprise Canvas not found", f"<section class='hero'><h1>Enterprise Canvas not found</h1><p>{escape(str(exc))}</p></section>"), 404
    except ValueError as exc:
        return _page("Enterprise Canvas unavailable", f"<section class='hero'><h1>Canvas unavailable</h1><p>{escape(str(exc))}</p></section>"), 404

    selected = next((tile for tile in canvas.tiles if tile.tile_view_id == selected_tile_id), None)
    if not selected and selected_tile_id:
        return _page("Enterprise Canvas tile unavailable", "<section class='hero'><h1>Tile unavailable</h1><p>The requested area is not available in this Canvas read model.</p></section>"), 404
    if selected:
        body = _styles() + _nav(canvas.enterprise_id) + _tile_detail(canvas.enterprise_id, selected, headers)
        return _page(f"Enterprise Canvas — {canvas.header.enterprise_name}", body), 200
    body = _styles() + _nav(canvas.enterprise_id) + _executive_canvas(canvas, headers)
    return _page(f"Enterprise Canvas — {canvas.header.enterprise_name}", body), 200


def _styles() -> str:
    return """<style>.exec-nav{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}.exec-nav a{border:1px solid #185c4d;border-radius:999px;padding:7px 10px;text-decoration:none;background:#fff}.brief-grid,.card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:14px}.statement,.pressure,.opportunity,.stakeholder{border:1px solid #ded8ce;border-radius:16px;padding:16px;background:#fff}.label{display:inline-block;border-radius:999px;padding:3px 8px;margin:2px;background:#eef3ff;border:1px solid #c8d4ef}.projection{background:#fff7df}.human{background:#f2eefb}.unknown{background:#eef3ff}.contradiction{background:#fff0f0}.recommendation{background:#eef8f0}.model-explorer{background:#fbfaf8}.muted{color:#68736c}.lineage{font-size:.95em}</style>"""


def _nav(enterprise_id: str) -> str:
    names = tuple("How MOD Works" if (enterprise_id == "MOD" and n == "How Enterprise Works") else n for n in EXEC_NAV)
    links = "".join(f"<a href='/digital-twins/{escape(enterprise_id)}/canvas#{escape(n.lower().replace(' ', '-').replace('&','and'))}'>{escape(n)}</a>" for n in names)
    return f"<nav class='exec-nav' aria-label='Twin view navigation'>{links}</nav>"


def _executive_canvas(canvas, headers) -> str:
    h = canvas.header
    pressures = _pressure_cards(canvas)
    unknowns = _unknown_and_contradiction_items(canvas)
    opportunities = _commercial_opportunities(canvas)
    stakeholders = _stakeholders(canvas)
    changes = _change_portfolio(canvas)
    recs = _recommendations(canvas)
    explorer = _model_explorer(canvas)
    if canvas.enterprise_id.upper() == 'MOD' and not _has_successful_reasoning(canvas):
        return _reasoning_panel(canvas) + f"""<section class='card model-explorer' id='model-explorer'><h2>Model Explorer</h2><p class='muted'>Legacy diagnostic view only; not the Executive Intelligence Brief.</p><div class='card-grid'>{explorer}</div></section><section class='card' id='evidence-and-lineage'><h2>Evidence &amp; Lineage</h2><p>Executive statements can be inspected for Evidence, Observations, Unknowns, Contradictions, confidence, freshness and source lineage. Select any Model Explorer area to inspect detailed lineage.</p></section>"""
    return _reasoning_panel(canvas) + f"""
    <section class='hero' id='overview'><p><a href='/digital-twins'>Digital Twins</a></p><p class='pill'>Executive Commercial Canvas · governed read model · Overview default</p><h1>{escape(h.enterprise_name)} executive situation briefing</h1><p>{escape(_summary(h, canvas))}</p><dl><div><dt>Twin version</dt><dd>{escape(h.twin_version)}</dd></div><div><dt>Source cut-off</dt><dd>{escape(h.source_cut_off)}</dd></div><div><dt>Progressive Assurance status</dt><dd>{escape(h.maturity_or_acceptance_state)}</dd></div></dl><div class='brief-grid'>
    {_brief('Enterprise summary', h.enterprise_purpose if h.enterprise_purpose != 'Unknown' else 'Evidence incomplete')}
    {_brief('Current strategic context', h.governing_thesis if h.governing_thesis != 'Unknown' else 'Evidence-backed interpretation: MOD is being read through accepted Twin pressures and changes; strategic context needs stronger evidence.')}
    {_brief('Major transformation agenda', _join_pressures(h.current_material_pressures) or 'Evidence incomplete')}
    {_brief('Latest material changes', h.latest_material_change or 'Evidence incomplete')}
    {_brief('Dominant pressures', _join_pressures(h.current_material_pressures) or 'Evidence incomplete')}
    {_brief('Evidence confidence', _confidence(canvas))}
    {_brief('Important caveats', 'Unknowns and Contradictions remain visible; projections are labelled and are not treated as facts. Human-supplied knowledge remains labelled and separate from canonical fact.')}
    {_brief('Source cut-off', h.source_cut_off)}{_brief('Latest refresh', h.last_refreshed_date)}{_brief('Progressive Assurance status', h.maturity_or_acceptance_state)}
    </div></section>
    <section class='card' id='how-mod-works'><h2>{escape('How MOD Works' if canvas.enterprise_id == 'MOD' else 'How Enterprise Works')}</h2><p>Human-readable enterprise map. Who decides, who owns delivery, who controls budget or access, and where handoffs remain uncertain.</p><div class='card-grid'>{_operating_model(canvas)}</div></section>
    <section class='card' id='material-pressures'><h2>Material Pressures</h2><p>Prioritised by materiality, recency, evidence strength, decision relevance, commercial relevance, uncertainty and change significance — not by record count.</p><div class='card-grid'>{pressures}</div></section>
    <section class='card' id='change-portfolio'><h2>Change Portfolio</h2><div class='card-grid'>{changes}</div></section>
    <section class='card' id='decision-landscape'><h2>Decision and Stakeholder Landscape</h2><div class='card-grid'>{stakeholders}</div></section>
    <section class='card' id='commercial-relevance'><h2>Commercial Relevance</h2><div class='card-grid'>{opportunities}</div></section>
    <section class='card' id='unknowns-and-contradictions'><h2>Unknowns &amp; Contradictions</h2><div class='card-grid'>{unknowns}</div></section>
    <section class='card' id='recommended-next-moves'><h2>Recommended Next Moves</h2><div class='card-grid'>{recs}</div></section>
    <section class='card model-explorer' id='model-explorer'><h2>Model Explorer</h2><p class='muted'>Organisation lens</p><p>Select an organisation tile to inspect core facts, pressures, responses, unresolved issues and evidence.</p><p>Secondary architecture, research, audit, lineage and data-quality view. Governed record structure remains inspectable here.</p><div class='card-grid'>{explorer}</div></section>
    <section class='card' id='evidence-and-lineage'><h2>Evidence &amp; Lineage</h2><p>Executive statements can be inspected for Evidence, Observations, Unknowns, Contradictions, confidence, freshness and source lineage. Select any Model Explorer area to inspect detailed lineage.</p></section>
    """


def _has_successful_reasoning(canvas):
    result=latest_result(canvas.enterprise_id)
    return ((result or {}).get('audit') or {}).get('status') == 'Succeeded'

def _reasoning_panel(canvas):
    if canvas.enterprise_id.upper() != 'MOD': return ''
    result=latest_result(canvas.enterprise_id)
    audit=(result or {}).get('audit') or {}; brief=(result or {}).get('brief') or {}; lineage=brief.get('lineage_manifest') or {}; cfg=provider_diagnostics()
    status=audit.get('status') or ('Ready' if cfg.get('configured') else 'Not configured'); reason=audit.get('failure') or brief.get('unavailable_reason') or ('No successful Executive Intelligence Brief has been generated.' if not result else '')
    if status != 'Succeeded':
        unavailable=f"""<section class='card warning' id='executive-intelligence-brief'><h2>Executive Intelligence Brief unavailable</h2><p><strong>Reason:</strong> {escape(reason or status)}</p><h3>Actions</h3><form method='post' action='/digital-twins/{escape(canvas.enterprise_id)}/executive-intelligence-brief/generate'><button type='submit'>Generate Executive Intelligence Brief</button></form><form method='post' action='/digital-twins/{escape(canvas.enterprise_id)}/executive-intelligence-brief/generate'><button type='submit'>Retry generation</button></form><p><a href='#model-explorer'>Open Model Explorer</a> · <a href='#evidence-and-lineage'>Open Evidence &amp; Lineage</a> · <a href='#reasoning-diagnostics'>View reasoning diagnostics</a></p></section>"""
    else:
        summary=brief.get('executive_summary') or {}
        pressures=''.join(f"<article class='pressure'><h3>{escape(str(p.get('title','')))}</h3><p>{escape(str(p.get('situation','')))}</p><p><strong>Why now:</strong> {escape(str(p.get('why_now','')))}</p><details><summary>Inspectable lineage</summary><p>{escape(', '.join((p.get('supporting_observation_ids') or [])+(p.get('supporting_evidence_ids') or [])))}</p></details></article>" for p in brief.get('material_pressures',[])[:5])
        unavailable=f"""<section class='card' id='executive-intelligence-brief'><h2>Executive Intelligence Brief</h2><p>{escape(str(summary.get('what_is_happening') or ''))}</p><p>{escape(str(summary.get('why_it_matters') or ''))}</p>{pressures}</section>"""
    diag={'Reasoning status':status,'Provider configured':'yes' if cfg.get('configured') else 'no','API key available':'yes' if cfg.get('api_key_available') else 'no','Timeout':cfg.get('timeout_seconds',''),'Max input tokens':cfg.get('max_input_tokens',''),'Max output tokens':cfg.get('max_output_tokens',''),'Reasoning request ID':audit.get('request_id',''),'Brief ID':audit.get('generated_brief_id',''),'Enterprise':canvas.enterprise_id,'Twin version':audit.get('twin_version',''),'Reasoning profile':audit.get('reasoning_profile',''),'Evidence package hash':audit.get('evidence_package_hash') or lineage.get('evidence_package_hash',''),'Evidence object count':audit.get('evidence_object_count',''),'Model provider':audit.get('model_provider') or cfg.get('provider',''),'Model name':audit.get('model_name') or cfg.get('model',''),'Prompt version':audit.get('prompt_version',''),'Validation status':audit.get('validation_outcome',''),'Rejected claim count':len(audit.get('rejected_claims') or []),'Execution duration':str(audit.get('execution_duration_ms',''))+' ms' if audit.get('execution_duration_ms') is not None else '','Last generated':brief.get('generated_at',''),'Fallback reason':reason if status!='Succeeded' else ''}
    rows=''.join(f"<tr><th>{escape(k)}</th><td>{escape(str(v))}</td></tr>" for k,v in diag.items())
    return unavailable + f"<section class='card diagnostics' id='reasoning-diagnostics'><h2>Reasoning diagnostics</h2><table>{rows}</table></section>"

def _brief(title, value): return f"<article class='statement'><h3>{escape(title)}</h3><p>{escape(str(value or 'Evidence incomplete'))}</p></article>"
def _join_pressures(items): return '; '.join(items[:5])
def _summary(h, canvas): return f"{h.enterprise_name} is presented through an executive commercial read model over the governed Twin. The briefing highlights what is changing, where pressures sit, who matters, what remains uncertain and what a trusted adviser should validate next."
def _confidence(canvas):
    if any(t.lineage_references for t in canvas.tiles): return "Mixed: evidence-backed statements are present, but confidence varies by pressure and lineage completeness."
    return "Evidence incomplete"

def _lineage_link(eid, tile): return f"<p class='lineage'><a href='/digital-twins/{escape(eid)}/canvas/tiles/{escape(tile.tile_view_id)}/lineage'>Inspect evidence lineage</a></p>"

def _pressure_cards(canvas):
    tiles = sorted(canvas.tiles, key=lambda t: (not bool(t.lineage_references), t.sort_order))
    if not tiles: return "<article class='pressure'><h3>Evidence incomplete</h3><p>No material pressure can be evidenced yet.</p></article>"
    out=[]
    for t in tiles[:6]:
        title = t.principal_pain_or_pressure if t.principal_pain_or_pressure not in {'Unknown','No governed pressure linked yet'} else t.display_name
        out.append(f"<article class='pressure'><span class='label'>Evidence-backed interpretation</span><h3>{escape(title)}</h3><p>{escape(t.plain_english_role)}</p><p><strong>Why now:</strong> {escape(t.material_change if t.material_change!='Unknown' else 'Evidence incomplete')}</p><p><strong>Affected areas:</strong> {escape(t.display_name)}</p><p><strong>Supporting evidence:</strong> {len(t.lineage_references) or 'Evidence incomplete'} lineage item(s) available for inspection.</p><p><strong>Linked observations:</strong> {'Present' if any(r.observation_ids for r in t.lineage_references) else 'Evidence incomplete'}</p><p><strong>Linked unknowns:</strong> {'Unknown present' if t.unknown_indicator else 'No high-impact Unknown linked'}</p><p><strong>Linked contradictions:</strong> {'Contradiction present' if t.contradiction_indicator else 'No high-impact Contradiction linked'}</p><p><strong>Confidence:</strong> {escape(_tile_confidence(t))}</p><p><strong>Freshness:</strong> {escape(t.last_refreshed_date or t.effective_date or 'Evidence incomplete')}</p><p><strong>Commercial consequence:</strong> Validate whether this pressure creates an addressable route to change before claiming fit.</p>{_lineage_link(canvas.enterprise_id,t)}</article>")
    return ''.join(out)

def _tile_confidence(t): return next((p.confidence_or_qualification for p in t.analytical_projections if p.confidence_or_qualification), 'Confidence not confirmed')

def _operating_model(canvas):
    if not canvas.tiles: return _brief('Evidence incomplete','Owner not confirmed; decision authority unresolved.')
    return ''.join(f"<article class='statement'><h3>{escape(t.display_name)}</h3><p><strong>Role:</strong> {escape(t.plain_english_role)}</p><p><strong>Delivery owner:</strong> {escape(t.accountable_role if t.accountable_role!='Unknown' else 'Owner not confirmed')}</p><p><strong>Budget/access:</strong> Decision authority unresolved.</p><p><strong>Handoffs/dependencies:</strong> {escape(t.principal_pain_or_pressure)}</p><p><strong>Authority confidence:</strong> {escape(_tile_confidence(t))}</p></article>" for t in canvas.tiles[:6])

def _change_portfolio(canvas):
    projs=[p for t in canvas.tiles for p in t.analytical_projections if p.projection_type in {'programme','current_response','response_effectiveness','transformation_pressure_view','burning_platform'}]
    if not projs: return "<article class='statement'><h3>Evidence incomplete</h3><p>No current recommendation. Evidence gaps prevent a ranked change portfolio.</p></article>"
    return ''.join(f"<article class='statement'><h3>{escape(p.display_label)}</h3><p><strong>Intended outcome:</strong> Evidence-backed interpretation of accepted Twin change signal.</p><p><strong>Current state:</strong> <span class='label projection'>Projection</span> {escape(p.status or 'accepted projection')}</p><p><strong>Owner:</strong> Owner not confirmed</p><p><strong>Dependencies/blockers:</strong> Evidence gaps and decision authority unresolved.</p><p><strong>Confidence:</strong> {escape(p.confidence_or_qualification or 'Confidence not confirmed')}</p><p><strong>Likely decision horizon:</strong> Validate with accountable owner.</p></article>" for p in projs[:6])

def _stakeholders(canvas):
    return ''.join(f"<article class='stakeholder'><h3>{escape(t.accountable_role if t.accountable_role!='Unknown' else t.display_name + ' owner')}</h3><p><strong>Relevance:</strong> Related to {escape(t.display_name)} and pressure conversion.</p><p><strong>Decision authority:</strong> {escape('Inferred from governed role' if t.accountable_role!='Unknown' else 'Decision authority unresolved')}</p><p><strong>Evidence:</strong> {_safe_count(t.lineage_references)} lineage item(s).</p><p><strong>Confidence:</strong> {escape(_tile_confidence(t))}</p><p><strong>Unknowns:</strong> {escape('Role attribution needs validation' if t.accountable_role=='Unknown' or t.unknown_indicator else 'No linked Unknown surfaced')}</p><p><strong>Recommended engagement posture:</strong> Validate authority and problem ownership before shaping.</p></article>" for t in canvas.tiles[:6]) or _brief('Evidence incomplete','Decision authority unresolved')

def _commercial_opportunities(canvas):
    tiles=sorted(canvas.tiles, key=lambda t: (not t.lineage_references, not t.analytical_projections, t.sort_order))
    if not tiles: return _brief('Commercial route not yet evidenced','No opportunity should be claimed.')
    return ''.join(f"<article class='opportunity'><h3>{escape(t.principal_pain_or_pressure if t.principal_pain_or_pressure!='No governed pressure linked yet' else t.display_name)}</h3><p><strong>Enterprise need:</strong> {escape(t.plain_english_role)}</p><p><strong>Evidence of materiality:</strong> {_safe_count(t.lineage_references)} lineage item(s), with confidence {escape(_tile_confidence(t))}.</p><p><strong>Why now:</strong> {escape(t.material_change if t.material_change!='Unknown' else 'Evidence incomplete')}</p><p><strong>Likely buyer/problem owner:</strong> {escape(t.accountable_role if t.accountable_role!='Unknown' else 'Owner not confirmed')}</p><p><strong>Route to market:</strong> Commercial route not yet evidenced.</p><p><strong>Incumbent or access constraints:</strong> Access constraints require validation; avoid claiming incumbency displacement.</p><p><strong>Plausible intervention:</strong> Learn, validate and shape around the evidenced pressure.</p><p><strong>Commercial addressability:</strong> Plausible but unconfirmed.</p><p><strong>Unresolved questions:</strong> Who owns budget, access and approval?</p><p><strong>Recommended posture:</strong> validate</p></article>" for t in tiles[:6])

def _unknown_and_contradiction_items(canvas):
    items=[]
    for t in canvas.tiles:
        if t.unknown_indicator: items.append(f"<article class='statement'><span class='label unknown'>Unknown</span><h3>{escape(t.display_name)} unresolved evidence</h3><p>Affected opportunity or decision: {escape(t.principal_pain_or_pressure)}</p><p>Current evidence boundary: evidence incomplete.</p><p>Who could resolve it: accountable owner or source authority.</p><p>Validation action: ask what evidence confirms ownership, budget and delivery state.</p><p>Commercial consequence: avoid claiming until resolved.</p></article>")
        if t.contradiction_indicator: items.append(f"<article class='statement'><span class='label contradiction'>Contradiction</span><h3>{escape(t.display_name)} conflicting position retained</h3><p>Both positions remain preserved in the governed Twin until stronger evidence resolves them.</p><p>Commercial consequence: qualify any recommendation.</p></article>")
    return ''.join(items) or "<article class='statement'><h3>Evidence incomplete</h3><p>No high-impact Unknown or Contradiction is linked in this view.</p></article>"

def _recommendations(canvas):
    cards=[]
    for t in canvas.tiles[:4]:
        if not t.lineage_references: continue
        cards.append(f"<article class='statement'><span class='label recommendation'>Recommendation</span><h3>Validate {escape(t.display_name)} pressure ownership</h3><p><strong>Who:</strong> {escape(t.accountable_role if t.accountable_role!='Unknown' else 'Owner not confirmed')}</p><p><strong>Why now:</strong> {escape(t.material_change if t.material_change!='Unknown' else 'Evidence incomplete')}</p><p><strong>Why them:</strong> They are linked to the affected area in the read model.</p><p><strong>Evidence supports:</strong> {_safe_count(t.lineage_references)} lineage item(s).</p><p><strong>Question to ask:</strong> What decision, funding or access route controls this pressure?</p><p><strong>Evidence to seek:</strong> Fresh confirmation of owner, budget, access and current blocker.</p><p><strong>What not to claim:</strong> Do not claim confirmed authority, route to market or outcome until evidenced.</p><p><strong>Outcome increasing conviction:</strong> Named accountable sponsor plus source-backed decision horizon.</p><p><strong>Confidence:</strong> {escape(_tile_confidence(t))}</p>{_lineage_link(canvas.enterprise_id,t)}</article>")
    return ''.join(cards) or "<article class='statement'><h3>No current recommendation</h3><p>Recommendations require evidence lineage.</p></article>"

def _model_explorer(canvas):
    if not canvas.tiles: return _brief('Governed record structure','Evidence incomplete')
    return ''.join(_tile_card(canvas.enterprise_id, tile, False) for tile in canvas.tiles)

def _safe_count(items): return str(len(items)) if items else 'Evidence incomplete'

# Legacy detail/model explorer helpers retained for inspection.
def _tile_card(enterprise_id: str, tile, selected: bool) -> str:
    markers = _markers(tile)
    return f"""<a class='canvas-tile' href='/digital-twins/{escape(enterprise_id)}/canvas/tiles/{escape(tile.tile_view_id)}' aria-current='{str(bool(selected)).lower()}' aria-label='Open {escape(tile.display_name)} organisation tile, state {escape(tile.current_state)}'><article><p class='muted'>Model Explorer area {tile.sort_order}</p><h3>{escape(tile.display_name)}</h3><p>{escape(tile.plain_english_role)}</p><p><strong>Accountable role:</strong> {escape(tile.accountable_role)}</p><p><strong>Current state:</strong> {escape(tile.current_state)}</p><p><strong>Principal pain or pressure:</strong> {escape(tile.principal_pain_or_pressure)}</p>{markers}</article></a>"""

def _markers(tile) -> str:
    items=[]
    if tile.unknown_indicator: items.append("<span class='marker marker-unknown'>Unknown present</span>")
    if tile.contradiction_indicator: items.append("<span class='marker marker-contradiction'>Contradiction present</span>")
    if tile.stale_evidence_indicator: items.append("<span class='marker marker-stale'>Stale evidence</span>")
    if tile.nested_twin_available: items.append("<span class='marker marker-nested'>Nested Twin available</span>")
    return "<p>"+" ".join(items or ["<span class='marker'>No special indicators supplied</span>"])+"</p>"

def _tile_detail(enterprise_id: str, tile, headers) -> str:
    facts=''.join(f'<li>{escape(f)}</li>' for f in tile.core_facts) or '<li>No core facts supplied.</li>'
    evidence=f"<li><a href='/digital-twins/{escape(enterprise_id)}/canvas/tiles/{escape(tile.tile_view_id)}/lineage'>Inspect evidence and lineage</a><br><span class='muted'>Source type/reference and Evidence/date reference are available in the lineage inspection.</span></li>"
    return f"""<main class='card detail-panel' role='region' aria-labelledby='tile-detail'><p><a href='/digital-twins/{escape(enterprise_id)}/canvas'>Close detail panel</a> · <a href='/digital-twins/{escape(enterprise_id)}/canvas#model-explorer'>Back to Model Explorer</a></p><h1 id='tile-detail'>{escape(tile.display_name)} model explorer detail</h1><p>This secondary view exposes governed record structure for architecture, research, audit, lineage and data-quality inspection.</p><h2>What this area does</h2><p>{escape(tile.plain_english_role)}</p><h2>Why it matters</h2><p>This area is material to the executive commercial read model.</p><h2>Core facts</h2><ul>{facts}</ul><h2>What has changed</h2><p>{escape(tile.material_change)}</p><h2>What is causing pressure</h2><p>{escape(tile.principal_pain_or_pressure)}</p><h2>What has been done so far</h2><p>{escape(tile.what_has_been_done_so_far)}</p><h2>What remains unresolved</h2><p>{escape(tile.what_remains_unresolved)}</p><h2>Stakeholders or accountable roles</h2><p>{escape(tile.accountable_role)}</p><h2>What we still do not know</h2><p>{'Unknown present' if tile.unknown_indicator else 'No linked Unknown surfaced'}</p><h2>Suggested next posture</h2><p>{escape(_next_posture(tile))}</p><h2>Projection labels</h2>{''.join(_projection_item(p) for p in tile.analytical_projections) or '<p>No projections linked.</p>'}<h2>Uncertainty</h2>{_markers(tile)}<h2>Evidence freshness</h2><p>Effective date: {escape(tile.effective_date)}. Source cut-off: {escape(tile.source_cut_off)}. Last refreshed: {escape(tile.last_refreshed_date)}.</p><h2>Inspect evidence</h2><ul>{evidence}</ul>{_feedback_panel(enterprise_id,tile.tile_view_id,tile.principal_pain_or_pressure,'',headers)}</main>"""

def _next_posture(tile) -> str:
    for p in tile.analytical_projections:
        if p.projection_type in {'suggested_next_posture','analytical_posture'}:
            return p.display_label
    return 'No suggested next posture supplied by the read model.'

def _projection_item(p) -> str:
    q=f" Governed qualification: {p.confidence_or_qualification}." if p.confidence_or_qualification else ""
    return f"<li><span class='label projection'>Projection</span> <strong>{escape(p.display_label)}</strong><br><span class='muted'>Status: {escape(p.status or 'not supplied')}.{escape(q)}</span></li>"

# lineage and feedback functions from previous view
def enterprise_canvas_lineage_page(enterprise_id: str, tile_id: str, headers) -> tuple[str, int]:
    try: inspection=EnterpriseCanvasService().get_lineage_inspection(enterprise_id,tile_id,headers)
    except EnterpriseCanvasAccessError: return _page("Lineage access denied","<section class='hero'><h1>Access denied</h1><p>You do not have access to this lineage inspection.</p></section>"),403
    except ValueError as exc: return _page("Lineage unavailable",f"<section class='hero'><h1>Lineage unavailable</h1><p>{escape(str(exc))}</p></section>"),404
    obs=''.join(f"<li><strong>{escape(o.get('plain_english_summary',''))}</strong><br><span class='muted'>Observation reference: {escape(o.get('observation_id',''))}. Confidence: {escape(str(o.get('confidence','Not supplied')))}. Provenance: {escape(o.get('provenance_type','Unknown'))}.</span></li>" for o in inspection.observations) or '<li>No Observation is linked to this displayed statement.</li>'
    evs=''.join(_evidence_detail(e) for e in inspection.evidence) or '<li>No Evidence is linked to this displayed statement.</li>'
    srcs=''.join(f"<li><strong>{escape(s.get('title',''))}</strong><br>Type: {escape(s.get('type','Unknown'))}. Reference: {escape(s.get('url_or_reference','Not supplied'))}. Source ID: {escape(str(s.get('source_id','')))}.</li>" for s in inspection.sources) or '<li>No Source details are available.</li>'
    pkgs=''.join(f"<li><strong>{escape(p.get('package_ref',''))}</strong><br>Package: {escape(p.get('package_id',''))} {escape(p.get('package_version',''))}. Original Blueprint location: {escape(', '.join(p.get('source_files', [])[:6]))}.</li>" for p in inspection.packages) or '<li>No imported package location is available.</li>'
    missing=''.join(f"<li>{escape(m)}</li>" for m in inspection.missing_lineage) or '<li>No incomplete lineage gaps detected.</li>'
    human=''.join(f"<li><strong>Human-supplied knowledge</strong>: {escape(h.get('statement',''))}</li>" for h in inspection.human_supplied_knowledge) or '<li>No human-supplied knowledge is linked to this statement.</li>'
    unks=''.join(f"<li><strong>{escape(u.get('question',''))}</strong><br>Why it matters: {escape(u.get('why_it_matters',''))}. What could resolve it: {escape(u.get('what_could_resolve_it',''))}.</li>" for u in inspection.unknowns) or '<li>No Unknown is linked to this statement.</li>'
    cons=''.join(f"<li><strong>{escape(c.get('statement',''))}</strong><br>Why retained: {escape(c.get('why_retained',''))}.</li>" for c in inspection.contradictions) or '<li>No Contradiction is linked to this statement.</li>'
    body=f"""<section class='hero'><p><a href='/digital-twins/{escape(enterprise_id)}/canvas/tiles/{escape(tile_id)}'>Return to tile detail</a> · <a href='/digital-twins/{escape(enterprise_id)}/canvas#evidence-and-lineage'>Return to Evidence &amp; Lineage</a></p><h1>Why Flora shows this</h1><p>{escape(inspection.displayed_statement)}</p><p class='pill'>Read-only lineage inspection</p></section><main class='card'><h2>What was observed</h2><ol>{obs}</ol><h2>Evidence supporting this</h2><ol>{evs}</ol><h2>Where the evidence came from</h2><ol>{srcs}</ol><h2>Human-supplied knowledge</h2><ol>{human}</ol><h2>What remains uncertain</h2><ol>{unks}</ol><h2>Conflicting evidence</h2><ol>{cons}</ol><h2>Original Blueprint location</h2><ol>{pkgs}</ol><h2>Missing or incomplete lineage</h2><ol>{missing}</ol><h2>Technical inspection references</h2><p>Projection or record reference: {escape(inspection.projection_or_record)}.</p><h3>Broken references</h3><ol><li>No broken references detected.</li></ol>{_feedback_panel(enterprise_id,tile_id,inspection.displayed_statement,inspection.projection_or_record,headers)}</main>"""
    return _page("Enterprise Canvas lineage inspection", body), 200

def _evidence_detail(e) -> str:
    return f"<li><strong>Supporting Evidence — {escape(e.get('source_title',''))}</strong><br>Source type: {escape(e.get('source_type','Unknown'))}. Publication or effective date: {escape(e.get('publication_or_effective_date','Unknown'))}. Freshness: {escape(e.get('freshness','Unknown'))}.<br>Summary: {escape(str(e.get('supporting_summary',''))[:500])}. Confidence or qualification: {escape(str(e.get('confidence_or_qualification','Not supplied')))}.</li>"

def _feedback_panel(enterprise_id: str, tile_id: str, judgement: str, lineage_ref: str, headers) -> str:
    options=''.join(f"<option value='{escape(k)}'>{escape(v)}</option>" for k,v in ACTIONS.items())
    return f"""<section class='card' aria-labelledby='candidate-feedback'><h3 id='candidate-feedback'>Contribute governed feedback</h3><p><strong>This contribution will be stored as candidate human knowledge. It will not change the governed Twin until reviewed and accepted.</strong></p><form method='post' action='/digital-twins/{escape(enterprise_id)}/canvas/feedback'><input type='hidden' name='enterprise_id' value='{escape(enterprise_id)}'><input type='hidden' name='tile_view_id' value='{escape(tile_id)}'><input type='hidden' name='displayed_judgement_ref' value='{escape(judgement)}'><input type='hidden' name='lineage_ref' value='{escape(lineage_ref)}'><label>Feedback action <select name='action_type'>{options}</select></label><label>Statement <textarea name='user_statement' required></textarea></label><label>Rationale <textarea name='rationale' required></textarea></label><button type='submit'>Submit candidate feedback</button></form>{_feedback_status_list(enterprise_id,tile_id,headers)}</section>"""

def _feedback_status_list(enterprise_id: str, tile_id: str, headers) -> str:
    records=EnterpriseCanvasFeedbackService().visible_feedback(headers, enterprise_id, tile_view_id=tile_id)
    if not records: return "<p class='muted'>No submitted feedback is visible to this user for this item.</p>"
    return '<ol>'+''.join(f"<li><strong>{escape(ACTIONS.get(r.action_type,r.action_type))}</strong>: {escape(r.status)}</li>" for r in records)+'</ol>'

def submit_enterprise_canvas_feedback(form: dict, headers) -> tuple[str, int, str]:
    try: record=EnterpriseCanvasFeedbackService().submit(headers, **{k:(v[0] if isinstance(v,list) else v) for k,v in form.items()})
    except FeedbackAccessError: return _page("Feedback access denied","<section class='hero'><h1>Access denied</h1><p>You are not authorised to submit Enterprise Canvas feedback.</p></section>"),403,""
    except ValueError as exc: return _page("Feedback not submitted",f"<section class='hero'><h1>Feedback not submitted</h1><p>{escape(str(exc))}</p></section>"),400,""
    target=f"/digital-twins/{escape(record.enterprise_id)}/canvas/tiles/{escape(record.tile_view_id)}?feedback={escape(record.feedback_id)}"
    html=_page("Feedback submitted",f"<section class='hero'><h1>Feedback submitted</h1><p>Feedback {escape(record.feedback_id)} is now {escape(record.status)}.</p><p>This candidate contribution has not changed canonical Evidence, Observations or Enterprise Model state.</p><p><a href='{target}'>Return to Canvas</a></p></section>")
    return html,201,target
