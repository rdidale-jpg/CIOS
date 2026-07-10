from __future__ import annotations
from html import escape
from cios.applications.flora.access import authenticated_flora_user, can_access_enterprise
from cios.applications.flora.workspace.views import _page
from cios.applications.flora.enterprise_canvas.views import enterprise_canvas_page
from .models import ReasoningRequestV1
from .runtime import EnterpriseIntelligenceRuntime, safe_fallback

def _li(items): return ''.join(f'<li>{escape(str(x))}</li>' for x in items)
def _evidence_button(ids):
    refs=', '.join(escape(str(x)) for x in ids if x)
    return f"<details><summary>Inspect evidence</summary><p>Lineage: {refs or 'No lineage available'}</p></details>"

def executive_intelligence_brief_page(enterprise_id: str, headers) -> tuple[str,int]:
    if not authenticated_flora_user(headers) or not can_access_enterprise(headers, enterprise_id):
        return _page('Executive Intelligence Brief unavailable', "<section class='hero'><h1>Executive Intelligence Brief unavailable</h1><p>Reason: authenticated enterprise access required.</p><p><a href='/digital-twins/"+escape(enterprise_id)+"/canvas'>Model Explorer</a></p></section>"), 403
    req=ReasoningRequestV1.create(enterprise_id=enterprise_id, workspace_id=headers.get('X-Flora-Active-Workspace') or enterprise_id, requested_by=headers.get('X-Flora-User') or 'unknown')
    try: result=EnterpriseIntelligenceRuntime().generate(req)
    except Exception as exc:
        fb=safe_fallback(type(exc).__name__, evidence_cut_off=req.evidence_cut_off, enterprise_id=enterprise_id)
        return _page('Executive Intelligence Brief unavailable', f"<section class='hero'><h1>{escape(fb['title'])}</h1><p>Reason: {escape(fb['reason'])}</p><p>Evidence cut-off: {escape(fb['evidence_cut_off'])}</p><p>{escape(fb['retry_action'])}</p><p><a href='{escape(fb['model_explorer_url'])}'>Model Explorer</a></p></section>"), 200
    b=result['brief']; summary=b.get('executive_summary') or {}; lineage=b.get('lineage_manifest') or {}
    body=f"<section class='hero'><h1>Executive Intelligence Brief</h1><p>Strategic-sales interpretation from the governed Twin only. Generated interpretations are transient unless approved.</p><p><a href='/digital-twins/{escape(enterprise_id)}/canvas'>Model Explorer</a></p></section>"
    body += "<section class='card'><h2>Executive Summary</h2>"+''.join(f"<p><strong>{escape(k.replace('_',' ').title())}:</strong> {escape(str(v))}</p>" for k,v in summary.items())+"</section>"
    body += "<section class='card'><h2>What Has Changed</h2><ul>"+_li([m.get('statement') for m in b.get('material_changes',[])])+"</ul></section>"
    body += "<section class='card'><h2>Material Pressures</h2>"+''.join(f"<article><h3>{escape(p.get('title',''))}</h3><p>{escape(p.get('situation',''))}</p><p><strong>Why now:</strong> {escape(p.get('why_now',''))}</p><p><strong>Commercial implication:</strong> {escape(p.get('commercial_implication',''))}</p>{_evidence_button((p.get('supporting_observation_ids') or [])+(p.get('supporting_evidence_ids') or [])+(p.get('linked_unknown_ids') or [])+(p.get('linked_contradiction_ids') or []))}</article>" for p in b.get('material_pressures',[]))+"</section>"
    body += f"<section class='card'><h2>How MOD Works</h2><p>{escape(str(b.get('operating_model_summary','')))}</p></section>"
    body += "<section class='card'><h2>Change Portfolio</h2><ul>"+_li([c.get('initiative') for c in b.get('change_portfolio',[])])+"</ul></section>"
    body += "<section class='card'><h2>Decision and Stakeholder Landscape</h2>"+''.join(f"<article><h3>{escape(s.get('person_or_role',''))}</h3><p>{escape(s.get('relevance',''))}</p>{_evidence_button(s.get('evidence_basis') or [])}</article>" for s in b.get('stakeholder_assessments',[]))+"</section>"
    body += "<section class='card'><h2>Commercial Relevance</h2>"+''.join(f"<article><h3>{escape(c.get('enterprise_need',''))}</h3><p>{escape(c.get('plausible_intervention',''))}</p><p><strong>What not to claim:</strong> {escape(c.get('what_not_to_claim',''))}</p>{_evidence_button(c.get('evidence_basis') or [])}</article>" for c in b.get('commercial_relevance_assessments',[]))+"</section>"
    body += "<section class='card'><h2>Unknowns and Contradictions</h2><h3>Unknowns</h3><ul>"+_li([u.get('statement') for u in b.get('unknowns',[])])+"</ul><h3>Contradictions</h3><ul>"+_li([c.get('statement') for c in b.get('contradictions',[])])+"</ul></section>"
    body += "<section class='card'><h2>Recommended Next Moves</h2>"+''.join(f"<article><h3>{escape(n.get('action',''))}</h3><p><strong>Who:</strong> {escape(n.get('who',''))}</p><p><strong>Question:</strong> {escape(n.get('question_to_ask',''))}</p>{_evidence_button(n.get('lineage') or [])}</article>" for n in b.get('recommended_next_moves',[]))+"</section>"
    body += f"<section class='card'><h2>Evidence and Lineage</h2><p>Evidence package: {escape(str(lineage.get('evidence_package_id','')))}</p><p>Validation: {escape(str((b.get('validation_status') or {}).get('status','')))}</p><details><summary>Retrieved objects</summary><p>{escape(', '.join(lineage.get('retrieved_object_ids') or []))}</p></details></section>"
    return _page('Executive Intelligence Brief', body), 200

def model_explorer_page(enterprise_id: str, headers):
    return enterprise_canvas_page(enterprise_id, headers)
