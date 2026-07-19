"""Reference Flora Enterprise Intelligence Workspace slice.

This module is an isolated presentation adapter over existing governed Banking
runtime objects. It intentionally creates no canonical Enterprise Intelligence
objects and stores only resumable workspace state in a cookie.
"""
from __future__ import annotations

from dataclasses import dataclass
from html import escape
from cios.applications.flora.enterprise_intelligence.opportunity_pipeline import generate_banking_opportunity_pipeline
from cios.applications.flora.enterprise_intelligence.pipeline import run_pipeline

RESUME_COOKIE = "flora_reference_investigation"
VALIDATION_PATH = "/workspace/reference/validation-action"


@dataclass(frozen=True)
class ReferenceNode:
    node_id: str
    label: str
    object_class: str
    summary: str
    href: str


def _cookie(headers, name: str) -> str:
    raw = headers.get("Cookie", "") if headers else ""
    for part in raw.split(";"):
        if "=" not in part:
            continue
        key, value = part.strip().split("=", 1)
        if key == name:
            return value
    return ""


def reference_resume_cookie() -> str:
    return f"{RESUME_COOKIE}=uk-banking-app-fraud-lloyds; Path=/; SameSite=Lax; Max-Age=2592000"


def _nodes() -> list[ReferenceNode]:
    return [
        ReferenceNode("industry:uk-banking", "UK Banking", "Industry Twin view", "UK retail banking change context rendered from governed Banking runtime observations.", "#uk-banking"),
        ReferenceNode("observation:app-fraud", "APP Fraud", "Observation-focused topic view", "APP fraud is represented as a reference change pressure requiring evidence-backed validation, not a new banking ontology.", "#app-fraud"),
        ReferenceNode("enterprise:lloyds", "Lloyds Banking Group", "Enterprise object focus", "Lloyds is shown only as a reference focus where enterprise specificity and account evidence boundaries remain visible.", "#lloyds"),
    ]


def _panel(title: str, body: str, klass: str = "card") -> str:
    return f"<section class='{klass}'><h2>{escape(title)}</h2>{body}</section>"


def reference_workspace_page(headers=None, saved: bool = False) -> str:
    run = run_pipeline()
    opps = generate_banking_opportunity_pipeline().opportunities
    opportunity = next((o for o in opps if o.opportunity_id == "BK-OPP-001"), opps[0])
    resumed = bool(_cookie(headers, RESUME_COOKIE))
    node_cards = "".join(f"<article class='mini-card'><h3><a href='{n.href}'>{escape(n.label)}</a></h3><p><strong>{escape(n.object_class)}</strong></p><p>{escape(n.summary)}</p></article>" for n in _nodes())
    observations = run.stages["retrieval"]["observations"]
    obs_list = "".join(f"<li><a href='/evidence/{escape(o['observation_id'])}'>{escape(o['observation_id'])}</a> — {escape(o['statement'])}</li>" for o in observations[:4])
    unknowns = [*run.stages["recommendation_eligibility"].get("unknowns", []), *(u.what for u in opportunity.unknowns)]
    contradictions = [*run.stages["recommendation_eligibility"].get("contradictions", []), *(c.effect for c in opportunity.contradictions)]
    unknown_html = "".join(f"<li>{escape(str(u))}</li>" for u in dict.fromkeys(unknowns))
    contra_html = "".join(f"<li>{escape(str(c))}</li>" for c in dict.fromkeys(contradictions)) or "<li>No material contradiction recorded for this candidate.</li>"
    saved_html = "<p class='pill'>Validation action created. Investigation state preserved.</p>" if saved else ""
    resume_html = "<p class='pill'>Resume previous investigation: UK Banking → APP Fraud → Lloyds → Opportunity → Validation.</p>" if resumed else "<p class='muted'>No previous reference investigation cookie found; opening this workspace starts one.</p>"
    body = f"""
    <section class='hero'><p class='eyebrow'>Reference Slice</p><h1>Flora Enterprise Intelligence Workspace</h1><p class='lead'>Home → What Changed → UK Banking → APP Fraud → Lloyds → Explain → Opportunity → Validation Action</p>{resume_html}{saved_html}<p><a class='button-link' href='#what-changed'>Start with What Changed</a></p></section>
    {_panel('What Changed', '<p>Banking change is rendered as a model-backed view: observations, mechanisms, Unknowns and Contradictions remain inspectable. APP Fraud is included as architecture-safe placeholder pressure where governed service coverage is incomplete.</p><div class="mini-grid">'+node_cards+'</div>', 'card action')}
    {_panel('UK Banking', '<p id="uk-banking">Flora is a workspace over governed Enterprise Intelligence. This page reuses the Banking runtime and does not create duplicate canonical objects.</p><ul>'+obs_list+'</ul>')}
    {_panel('APP Fraud', '<p id="app-fraud"><strong>Architecture-safe placeholder:</strong> APP Fraud is a visible reference object for the journey. It is labelled as requiring governed APP-fraud observations before stronger enterprise claims.</p><p><strong>Unknown:</strong> accountable Lloyds programme, budget, supplier and current fraud operations evidence are not present in this slice.</p>')}
    {_panel('Lloyds', '<p id="lloyds">Lloyds Banking Group is opened as the object focus for the reference journey. Relevance is explained through UK Banking pressure and APP Fraud validation demand; no named sponsor, CRM record or opportunity score is invented.</p>')}
    {_panel('Explainability panel', '<ol><li>Industry context: UK Banking change pressure.</li><li>Topic focus: APP Fraud creates a validation question.</li><li>Enterprise focus: Lloyds is commercially relevant only if governed enterprise evidence confirms exposure, owner and timing.</li><li>Opportunity view: projection over governed observations and hypotheses; not durable memory.</li></ol><p><strong>Lineage:</strong> Evidence → Observation → Mechanism → Hypothesis BRH-003 → Commercial Opportunity → Validation Action.</p>', 'card action')}
    {_panel('Evidence panel', '<p>Inspectable governed IDs from the existing Banking runtime:</p><ul>'+obs_list+'</ul><p><a href="/evidence/BRH-003">Inspect BRH-003</a></p>')}
    {_panel('Unknowns panel', '<ul>'+unknown_html+'</ul>', 'card unknown')}
    {_panel('Contradictions panel', '<ul>'+contra_html+'</ul>', 'card contradiction')}
    {_panel('Opportunity panel', f'<h3>{escape(opportunity.title)}</h3><p>{escape(opportunity.summary)}</p><div class="grid"><article><h3>Enterprise Need</h3><p>{escape(opportunity.commercial_problem)}</p></article><article><h3>Provider Fit</h3><p>Not inferred in this slice; requires separate provider model and inspectable lineage.</p></article><article><h3>Commercial Accessibility</h3><p>Unknown until sponsor, route, incumbent and engagement path are evidenced.</p></article><article><h3>Commercial Conviction</h3><p>{escape(opportunity.confidence)} — constrained by Unknowns and Contradictions.</p></article></div><p><strong>Opportunity status:</strong> {escape(opportunity.status)}; <strong>persistence:</strong> {escape(opportunity.persistence_class)}.</p>')}
    <section class='card action'><h2>Validation Action creation</h2><form method='post' action='{VALIDATION_PATH}'><input type='hidden' name='journey' value='uk-banking-app-fraud-lloyds'><label>Validation action</label><textarea name='action'>Validate with Lloyds account knowledge whether APP Fraud is a current executive concern, who owns it, what evidence exists and what must not be overclaimed.</textarea><p><button type='submit'>Create validation action</button></p></form></section>
    <section class='card'><h2>Architecture checks</h2><ul><li>No duplicate enterprise objects are introduced.</li><li>No UI-local truth is promoted to governed knowledge.</li><li>Unknowns and Contradictions remain visible.</li><li>Opportunity is a projection over governed intelligence.</li><li>No banking-specific rule enters reusable architecture.</li></ul></section>
    """
    from cios.applications.flora.web.app import _flora_v2_page, _account_context_html
    from cios.applications.flora.access import blueprint_upload_authorisation
    return _flora_v2_page("Flora Reference Workspace", "home", body, _account_context_html(blueprint_upload_authorisation(headers or {})))
