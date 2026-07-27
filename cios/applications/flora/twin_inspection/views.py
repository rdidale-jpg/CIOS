"""Universal, adapter-driven Twin Inspection Shell view."""
from html import escape
from cios.applications.flora.enterprise_canvas.service import EnterpriseCanvasAccessError, EnterpriseCanvasNotFoundError
from cios.applications.flora.workspace.views import _page
from .enterprise import enterprise_inspection_adapter

def twin_inspection_page(twin_id: str, headers) -> tuple[str, int]:
    try:
        adapter = enterprise_inspection_adapter(twin_id, headers)
    except EnterpriseCanvasAccessError:
        return _page("Twin inspection access denied", "<section class='hero'><h1>Access denied</h1><p>You do not have access to inspect this governed Twin.</p></section>"), 403
    except EnterpriseCanvasNotFoundError:
        return _page("Twin inspection unavailable", "<section class='hero'><h1>Twin inspection unavailable</h1><p>No supported governed inspection adapter is available for this Twin.</p></section>"), 404
    visible = tuple(sorted((s for s in adapter.sections if s.availability and s.authorization), key=lambda s: s.order))
    nav = "".join(f"<a href='{escape('#executive-intelligence' if s.key == 'executive-intelligence' else s.lineage_target)}'>{escape(s.label)}</a>" for s in visible)
    p = adapter.profile
    fields = (("Identity",p.identity),("Twin type",p.twin_type),("Canonical owner",p.canonical_owner),("Status",p.status),("Version",p.version),("Last refresh",p.last_refresh),("Source cut-off",p.source_cut_off),("Research maturity",p.research_maturity),("Commercial maturity",p.commercial_maturity),("Evidence coverage",p.evidence_coverage),("Evidence freshness",p.evidence_freshness),("Confidence",p.confidence),("Unknowns",p.unknowns),("Contradictions",p.contradictions),("Package lineage",p.package_lineage))
    facts = "".join(f"<div><dt>{escape(k)}</dt><dd>{escape(v)}</dd></div>" for k,v in fields)
    content_parts = []
    for section in visible:
        rendered = section.provider()
        if rendered:
            content_parts.append(rendered)
    content = "".join(content_parts)
    rows = "".join(f"<tr><td>{escape(s.key)}</td><td>{escape(s.truth_class)}</td><td>{escape(s.freshness)}</td><td>{escape(s.effective_date)}</td><td><a href='{escape(s.lineage_target)}'>Inspect lineage</a></td></tr>" for s in visible)
    body = f"""<style>.inspection-nav{{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0}}.inspection-nav a{{padding:7px 11px;border:1px solid #185c4d;border-radius:999px;text-decoration:none}}.profile-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}}.profile-grid div{{padding:10px;border-top:1px solid #ddd}}.profile-grid dt{{font-weight:700}}.profile-grid dd{{margin:4px 0}}</style><nav class='inspection-nav' aria-label='Inspection navigation'>{nav}</nav><section class='hero' id='twin-intelligence-profile'><p class='pill'>Twin Inspection Shell · {escape(adapter.adapter_key)} adapter</p><h1>Twin Intelligence Profile</h1><h2>{escape(p.identity)}</h2><dl class='profile-grid'>{facts}</dl></section><div id='executive-intelligence'>{content}</div><details class='card'><summary>Inspection contract</summary><p>Presentation metadata only; section data remains with its governed provider.</p><table><tr><th>Section</th><th>Truth class</th><th>Freshness</th><th>Effective date</th><th>Lineage target</th></tr>{rows}</table></details>"""
    return _page(f"Twin Inspection — {p.identity}", body), 200
