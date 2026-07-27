"""Universal, adapter-driven Twin Inspection Shell view."""
from html import escape
from cios.applications.flora.enterprise_canvas.service import EnterpriseCanvasAccessError, EnterpriseCanvasNotFoundError
from cios.applications.flora.workspace.views import _page
from .enterprise import enterprise_inspection_adapter
from .industry import industry_inspection_adapter
from .candidate import candidate_inspection_adapter

def twin_inspection_page(twin_id: str, headers, twin_type: str = "enterprise") -> tuple[str, int]:
    try:
        adapters = {"enterprise": enterprise_inspection_adapter, "industry": industry_inspection_adapter,
                    "candidate": candidate_inspection_adapter}
        if twin_type == "market-participant":
            return _page("Market Participant inspection unavailable", "<section class='hero'><h1>Market Participant inspection unavailable</h1><p>The repository contains specification and candidate fragments, but no canonical governed Market Participant read runtime. No capability has been fabricated.</p></section>"), 404
        adapter = adapters[twin_type](twin_id, headers)
    except EnterpriseCanvasAccessError:
        return _page("Twin inspection access denied", "<section class='hero'><h1>Access denied</h1><p>You do not have access to inspect this governed Twin.</p></section>"), 403
    except EnterpriseCanvasNotFoundError:
        return _page("Twin inspection unavailable", "<section class='hero'><h1>Twin inspection unavailable</h1><p>No supported governed inspection adapter is available for this Twin.</p></section>"), 404
    except PermissionError:
        return _page("Twin inspection access denied", "<section class='hero'><h1>Access denied</h1><p>You do not have access to inspect this Twin context.</p></section>"), 403
    except (LookupError, KeyError):
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
    conclusions = _conclusions(adapter)
    rows = "".join(f"<tr><td>{escape(s.key)}</td><td>{escape(s.truth_class)}</td><td>{escape(s.freshness)}</td><td>{escape(s.effective_date)}</td><td><a href='{escape(s.lineage_target)}'>Inspect lineage</a></td></tr>" for s in visible)
    state = "<aside class='card candidate-banner' role='status'><strong>Candidate intelligence — not accepted or governed.</strong> Inspection cannot promote or mutate canonical state.</aside>" if adapter.context == "candidate" else ""
    body = f"""<style>.inspection-nav{{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0}}.inspection-nav a{{padding:7px 11px;border:1px solid #185c4d;border-radius:999px;text-decoration:none}}.profile-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}}.profile-grid div{{padding:10px;border-top:1px solid #ddd}}.profile-grid dt{{font-weight:700}}.profile-grid dd{{margin:4px 0}}.candidate-banner{{border:3px solid #a34b00;background:#fff2df}}.conclusion{{border-left:5px solid #185c4d}}.trust-panel{{margin-top:12px}}</style><nav class='inspection-nav' aria-label='Inspection navigation'>{nav}</nav>{state}<section class='hero' id='twin-intelligence-profile'><p class='pill'>Twin Inspection Shell · {escape(adapter.adapter_key)} adapter</p><h1>Twin Intelligence Profile</h1><h2>{escape(p.identity)}</h2><dl class='profile-grid'>{facts}</dl></section>{conclusions}<div id='executive-intelligence'>{content}</div><details class='card'><summary>Architect inspection contract</summary><p>Presentation metadata only; section data remains with its governed provider. No universal trust score is calculated.</p><table><tr><th>Section</th><th>Truth class</th><th>Freshness</th><th>Effective date</th><th>Lineage target</th></tr>{rows}</table></details><details class='card'><summary>Technical inspection</summary><p>Adapter: <code>{escape(adapter.adapter_key)}</code>. Context: <code>{escape(adapter.context)}</code>. This shell owns no canonical values or persistence.</p></details>"""
    return _page(f"Twin Inspection — {p.identity}", body), 200


def _conclusions(adapter) -> str:
    if not adapter.conclusions:
        return ""
    cards = []
    for item in adapter.conclusions:
        cards.append(f"<article class='card conclusion' id='{escape(item.conclusion_id)}'><p class='pill'>{escape(item.truth_class)}</p><h3>{escape(item.statement)}</h3><p><strong>Why it matters commercially:</strong> {escape(item.commercial_consequence)}</p><p><strong>Confidence:</strong> {escape(item.confidence)} · <strong>Freshness:</strong> {escape(item.freshness)}</p><details class='trust-panel'><summary><strong>Why should I believe this?</strong></summary><h4>What supports it?</h4><p>{escape(item.support_summary)}</p><p><a href='{escape(item.evidence_target)}'>Inspect supporting Evidence</a></p><h4>What challenges it?</h4><p>{escape(item.challenge_summary)}</p><h4>What remains unknown?</h4><p>{escape(item.challenge_summary)}</p><h4>Who owns this understanding?</h4><p>{escape(adapter.profile.canonical_owner)}</p><p><a href='{escape(item.lineage_target)}'>Inspect reasoning and research lineage</a></p></details></article>")
    return "<section class='card' id='material-conclusions'><h2>Material conclusions</h2><p>Understand → Assess → Inspect → Challenge → Decide</p>" + "".join(cards) + "</section>"
