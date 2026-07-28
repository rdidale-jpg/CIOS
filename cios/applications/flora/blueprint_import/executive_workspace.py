"""Mission-aware, evidence-governed projection over an imported candidate Twin."""
from __future__ import annotations
from collections import Counter
from html import escape
from typing import Any

from cios.applications.flora.access import can_access_enterprise
from cios.applications.flora.commercial_mission import CommercialMission, resolve_commercial_mission
from cios.applications.flora.workspace.views import _page
from .registry import BlueprintPackageRegistry
from .semantic_twin import SemanticEnterprise, SemanticObject, SemanticTwin, assemble_semantic_twin
from .twin_governance import project_twin_identity
from .validator import BlueprintPackageValidator, can_inspect_blueprint_package

THEMES = (("market-condition", "Industry outlook", ("market", "industry", "sector", "economic")),
          ("financial-pressure", "Transformation pressures", ("financial", "cost", "revenue", "margin", "productivity", "resilience")),
          ("regulation", "Regulation", ("regulat", "policy", "compliance", "mandate")),
          ("technology", "Technology and data", ("technology", "digital", "data", "cloud", "ai ", "network")),
          ("customer", "Client problems", ("customer", "adoption", "demand", "experience", "operating model")),
          ("ecosystem", "Competitor and partner context", ("compet", "partner", "supplier", "ecosystem")))


def executive_workspace_page(import_run_id: str, headers: Any, *, view: str = "workspace",
                             enterprise_id: str = "") -> tuple[str, int]:
    package = next((p for p in BlueprintPackageRegistry().list() if p.import_run_id == import_run_id), None)
    if package is None:
        return _page("Executive Intelligence Workspace unavailable", "<section class='hero'><h1>Executive Intelligence Workspace unavailable</h1><p>The import record could not be found.</p></section>"), 404
    if not can_access_enterprise(headers, package.identity.enterprise_id, package.workspace_id) or not can_inspect_blueprint_package(headers, package):
        return _page("Access denied", "<section class='hero'><h1>Access denied</h1></section>"), 403
    summary = BlueprintPackageValidator().staging_summary(import_run_id) or {}
    candidates = list(summary.get("candidates") or ())
    twin = assemble_semantic_twin(candidates)
    mission = resolve_commercial_mission(headers)
    inspection = package.package_inspection or {}
    identity = project_twin_identity(package)
    title = str(inspection.get("twin_title") or inspection.get("package_title") or identity.primary_subject_name or package.identity.package_id)
    if view == "explore":
        return _page(f"Explore Twin — {title}", _styles() + _explorer(twin, import_run_id, mission)), 200
    if view == "enterprise":
        ent = next((e for e in twin.enterprises if e.identity_key == enterprise_id), None)
        if ent is None:
            return _page("Enterprise dossier unavailable", "<section class='hero'><h1>Enterprise dossier unavailable</h1></section>"), 404
        return _page(f"Enterprise Intelligence — {ent.name}", _styles() + _dossier(ent, twin, import_run_id, mission)), 200
    unresolved = identity.status == "ambiguous" or not (identity.primary_subject_id and identity.governed_scope and identity.canonical_owner)
    body = _styles() + _hero(title, inspection, unresolved, len(candidates), mission)
    body += _narrative(twin, mission) + _themes(twin, import_run_id) + _enterprise_index(twin, import_run_id)
    body += _reasoning_trace(twin, mission) + _attention(twin, import_run_id) + _limitations(twin, summary, mission, unresolved)
    body += _navigation(import_run_id)
    return _page(f"Executive Intelligence — {title}", body), 200


def _hero(title, inspection, unresolved, count, mission):
    caveat = "the Twin identity and governed scope have not yet been confirmed" if unresolved else "imported intelligence remains a candidate"
    composed = (f"<p class='mission'><strong>Composed for: {escape(mission.executive_role)} · {escape(mission.employer)}</strong> · <a href='#active-mission'>Inspect mission</a></p>" if mission else "")
    return f"""<nav class='executive-path'><strong>Executive understanding</strong><span>Commercial relevance</span><span>Why now</span><span>Why believe it</span><a href='#candidate-governance'>Candidate governance</a></nav><header class='hero'><p class='eyebrow'>Executive Intelligence Workspace</p><h1>{escape(title)}</h1><p>{count} staged intelligence records</p>{composed}<p class='workspace-caveat'><strong>Executive understanding is provisional because {caveat}.</strong></p><div class='status-key'><span><b>Candidate intelligence</b> — imported, not governed</span><span><b>Provisional interpretation</b> — not persisted</span></div></header>"""


def _mission(m: CommercialMission | None) -> str:
    if not m: return ""
    offers = ", ".join(m.offer_portfolio) or "No governed or explicitly human-supplied offer portfolio; offer alignment is incomplete."
    return f"""<section class='card' id='active-mission'><h2>Active Commercial Mission</h2><p><strong>{escape(m.executive_role)} · {escape(m.employer)}</strong></p><p>{escape(m.commercial_objective)}</p><p><strong>Offers:</strong> {escape(offers)}</p><p><strong>Geography:</strong> {escape(', '.join(m.geography) or 'not supplied')} · <strong>Inspection depth:</strong> {escape(m.inspection_depth)}</p><p class='pill'>{escape(m.authority_status)} · {escape(m.supplied_by)} · not Enterprise Intelligence</p></section>"""


def _narrative(twin: SemanticTwin, mission: CommercialMission | None) -> str:
    eligible = [o for o in twin.objects if o.eligible_conclusion]
    timing = next((o.statement for o in eligible if "timing" in o.statement.casefold() or "urgency" in o.statement.casefold()), "No supported timing conclusion; investigate observation dates and material events.")
    mission_text = (f"Composition foregrounds the declared objective: {mission.commercial_objective}" if mission else "Personal commercial prioritisation is not yet applied because no Commercial Mission is available.")
    offer = ("Offer alignment remains incomplete and no fit is inferred." if mission and not mission.offer_portfolio else "Potential offer alignment is a hypothesis requiring evidence validation.")
    return f"""<section class='card'><h2>Executive understanding</h2><p>The runtime semantically assembled <strong>{len(twin.objects)} objects</strong>; {len(eligible)} contain an evidence-bounded interpretation eligible for executive prominence. Labels and context-free metrics remain inspectable but are excluded here.</p><div class='grid executive-summary-grid'><article><h3>Industry and enterprise change</h3><p>{len(twin.enterprises)} enterprise identities and {len(eligible)} interpretable observations or claims warrant investigation.</p></article><article><h3>Commercial relevance</h3><p>{escape(mission_text)}</p><p>{escape(offer)}</p></article><article><h3>Why now?</h3><p>{escape(timing)}</p></article><article><h3>Recommended investigation</h3><p>Validate subject, consequence, owner, currency, evidence and any offer linkage before commercial action. This is not lead scoring or procurement prediction.</p></article></div></section>""" + _mission(mission)


def _themes(twin: SemanticTwin, run_id: str) -> str:
    eligible = [o for o in twin.objects if o.eligible_conclusion and o.kind not in {"unknown", "contradiction"}]
    used: set[str] = set(); sections = []
    for key, label, terms in THEMES:
        rows = [o for o in eligible if o.record_id not in used and any(t in (o.statement + " " + o.kind).casefold() for t in terms)][:5]
        if rows:
            used.update(o.record_id for o in rows); sections.append(f"<section class='theme-group' id='{key}'><h3>{label}</h3>{''.join(_conclusion(o, run_id) for o in rows)}</section>")
    other = [o for o in eligible if o.record_id not in used][:5]
    if other: sections.append("<section class='theme-group'><h3>Other supported observations</h3>" + "".join(_conclusion(o, run_id) for o in other) + "</section>")
    if not sections: sections = ["<p>No semantically complete conclusion is available. Inspect typed coverage and gather evidence rather than treating raw records as meaning.</p>"]
    return "<section class='card'><h2>Material candidate intelligence</h2>" + "".join(sections) + "</section>"


def _conclusion(o: SemanticObject, run_id: str) -> str:
    support = ", ".join(o.evidence_refs) or "No explicit Evidence reference; treat as unsupported"
    return f"""<article class='executive-conclusion'><p class='pill'>{escape(o.governance.title())} · {escape(o.kind)}</p><h4>{escape(o.statement)}</h4><p><strong>Subject:</strong> {escape(o.subject)} · <strong>Confidence:</strong> {escape(o.confidence)} · <strong>Freshness:</strong> {escape(o.freshness)}</p><details><summary>Why believe this? View evidence and freshness</summary><p><strong>Evidence:</strong> {escape(support)}</p><p><strong>Contradiction state:</strong> inspect linked Contradictions; none is inferred from absence.</p><p><strong>Lineage:</strong> {escape(o.source_file)} · {escape(o.source_location)} · <code>{escape(o.record_id)}</code></p><a href='/blueprint-import/{escape(run_id)}/inspect#technical-diagnostics'>View source and lineage</a></details></article>"""


def _enterprise_index(twin, run_id):
    cards = "".join(_enterprise_card(e, run_id) for e in twin.enterprises) or "<p>No enterprise identity could be assembled from the supplied records.</p>"
    return f"<section class='card' id='enterprises'><h2>Priority enterprises</h2><p>All {len(twin.enterprises)} represented enterprises are shown; order is alphabetical and is not an opaque score.</p>{cards}<p><a class='button primary' href='/blueprint-import/{escape(run_id)}/explore'>Explore Twin intelligence</a></p></section>"


def _enterprise_card(e, run_id):
    ev = len({x for o in e.records for x in o.evidence_refs}); unk = sum(o.kind == 'unknown' for o in e.records); con = sum(o.kind == 'contradiction' for o in e.records); opp = sum('opportun' in o.kind for o in e.records)
    latest = next((o.statement for o in e.records if o.eligible_conclusion), "No interpreted material change")
    state = "ambiguous identity — not merged" if e.ambiguous else ("governed" if any(o.governance == 'governed' for o in e.records) else "candidate")
    return f"""<article class='enterprise-card'><h3>{escape(e.name)}</h3><p>{escape(latest)}</p><p>Role: enterprise/participant in Twin · Coverage: {len(e.records)} objects · Evidence: {ev} · Unknowns: {unk} · Contradictions: {con} · Opportunity Hypotheses: {opp} · State: {escape(state)}</p><p><a href='/blueprint-import/{escape(run_id)}/enterprises/{escape(e.identity_key)}'>Open Enterprise Intelligence dossier</a></p></article>"""


def _attention(twin, run_id):
    rows = [o for o in twin.objects if o.kind in {"unknown", "contradiction"} and o.eligible_conclusion]
    body = "".join(_conclusion(o, run_id) for o in rows[:8]) or "<p>No explicit Unknown or Contradiction was supplied; this does not establish completeness.</p>"
    return "<section class='card' id='unknowns'><h2>Unknowns and contradictions</h2>" + body + "</section>"


def _reasoning_trace(twin, mission):
    """Expose the ADR-014 bounded deterministic path used for candidate imports.

    The provider-backed EnterpriseIntelligenceRuntime retrieves accepted
    Enterprise Twins and must not be pointed at unpromoted staging records.
    This fallback records that boundary rather than silently bypassing it.
    """
    eligible = sum(o.eligible_conclusion for o in twin.objects)
    stages = [
        ("Question or trigger", "applied", "Imported Twin plus active Commercial Mission" if mission else "Imported Twin; mission unavailable"),
        ("Context planning", "applied", "Candidate scope, identity, evidence and governance boundaries"),
        ("Knowledge retrieval", "applied", f"{len(twin.objects)} staged objects; no public model memory"),
        ("Observation selection", "applied", f"{eligible} semantically eligible; {len(twin.objects)-eligible} retained inspection-only"),
        ("Mechanism interpretation", "bounded", "Only explicit supplied interpretations; no relationship manufactured"),
        ("Enterprise-context assessment", "applied", f"{len(twin.enterprises)} runtime identities"),
        ("Competing hypothesis generation", "skipped when absent", "Candidate hypotheses are preserved, not generated from model memory"),
        ("Challenge and contradiction analysis", "applied", f"{len(twin.of_kind('contradiction'))} explicit Contradictions"),
        ("Executive relevance assessment", "applied", "Deterministic mission-aware prominence"),
        ("Commercial action assessment", "bounded", "Investigation only; no procurement prediction"),
        ("Validation", "applied", "Semantic eligibility, evidence and governance status retained"),
        ("Presentation", "applied", "Executive composition with progressive inspection"),
    ]
    rows = "".join(f"<tr><td>{escape(a)}</td><td>{escape(b)}</td><td>{escape(c)}</td></tr>" for a,b,c in stages)
    return f"<section class='card' id='reasoning-audit'><h2>Evidence-governed reasoning audit</h2><p>The accepted provider runtime is restricted to its governed Enterprise Twin retrieval contract. For unpromoted import candidates, the existing deterministic bounded path is used and skipped stages are explicit.</p><details><summary>Inspect reasoning stages</summary><table><thead><tr><th>Stage</th><th>Status</th><th>Basis</th></tr></thead><tbody>{rows}</tbody></table></details></section>"


def _limitations(twin, summary, mission, unresolved):
    excluded = [o for o in twin.objects if not o.eligible_conclusion]
    reasons = Counter(o.exclusion_reason for o in excluded)
    items = (["Twin identity and governed scope are not confirmed"] if unresolved else []) + (["Commercial Mission is unavailable"] if not mission else [])
    if mission and not mission.offer_portfolio: items.append("Offer alignment is incomplete because no governed or declared portfolio is supplied")
    items += [f"{n} record(s): {reason}" for reason, n in reasons.items() if reason]
    return f"<section class='card'><h2>Coverage and Limitations</h2><p>{len(twin.objects)} objects · {len(twin.of_kind('unknown'))} Unknowns · {len(twin.of_kind('contradiction'))} Contradictions · {len(excluded)} excluded from executive conclusions.</p><ul>{''.join('<li>'+escape(x)+'</li>' for x in items)}</ul></section>"


def _explorer(twin, run_id, mission):
    counts = Counter(o.kind for o in twin.objects); governed = sum(o.governance == 'governed' for o in twin.objects)
    aspects = "".join(f"<tr><td>{escape(k)}</td><td>{v}</td><td>{sum(o.governance=='candidate' for o in twin.objects if o.kind==k)} candidate / {sum(o.governance=='governed' for o in twin.objects if o.kind==k)} governed</td><td>{sum(bool(o.evidence_refs) for o in twin.objects if o.kind==k)} evidenced</td><td>{sum(not o.eligible_conclusion for o in twin.objects if o.kind==k)} unresolved</td></tr>" for k,v in sorted(counts.items()))
    enterprises = "".join(_enterprise_card(e, run_id) for e in twin.enterprises)
    return f"<nav class='executive-path'><a href='/blueprint-import/{escape(run_id)}'>Executive Workspace</a><strong>Twin Explorer</strong><a href='/blueprint-import/{escape(run_id)}/review'>Candidate governance</a></nav><header class='hero'><h1>Explore Twin intelligence</h1><p>{len(twin.objects)} objects · {governed} governed · {len(twin.objects)-governed} candidate</p></header>{_mission(mission)}<section class='card'><h2>Aspect coverage</h2><table><thead><tr><th>Aspect</th><th>Objects</th><th>Governance</th><th>Evidence coverage</th><th>Unresolved</th></tr></thead><tbody>{aspects}</tbody></table></section><section class='card'><h2>Enterprise index ({len(twin.enterprises)})</h2>{enterprises or '<p>No enterprise identities supplied.</p>'}</section>"


def _dossier(ent, twin, run_id, mission):
    relevant = list(ent.records)
    relevant += [o for o in twin.objects if o not in relevant and o.kind in {"unknown", "contradiction"} and o.subject in {"", "Twin scope", ent.name}]
    domains = Counter(o.kind for o in relevant); records = "".join(_conclusion(o, run_id) if o.eligible_conclusion else f"<article class='executive-conclusion'><h4>Retained inspection-only record</h4><p>{escape(o.exclusion_reason)}</p><p><code>{escape(o.record_id)}</code> · {escape(o.governance)} · Freshness: {escape(o.freshness)}</p></article>" for o in relevant)
    gaps = [d for d in ("strategy", "financial", "leadership", "customer", "operating_model", "technology", "programme", "supplier", "procurement", "opportunity_hypothesis") if not any(d in k.casefold() for k in domains)]
    return f"<nav class='executive-path'><a href='/blueprint-import/{escape(run_id)}'>Executive Workspace</a><a href='/blueprint-import/{escape(run_id)}/explore'>Twin Explorer</a><strong>Enterprise dossier</strong></nav><header class='hero'><h1>{escape(ent.name)}</h1><p>Enterprise Intelligence dossier · {'ambiguous identity, not silently merged' if ent.ambiguous else 'resolved runtime identity'} · {len(ent.records)} objects</p></header>{_mission(mission)}<section class='card'><h2>Available intelligence</h2>{records}</section><section class='card'><h2>Coverage gaps</h2><p>{escape(', '.join(gaps) or 'No standard domain gap detected; completeness is not implied.')}</p></section><section class='card'><h2>Governance</h2><a href='/blueprint-import/{escape(run_id)}/review'>Review candidate governance</a> · <a href='/blueprint-import/{escape(run_id)}/inspect'>View evidence and provenance</a></section>"


def _navigation(run_id):
    r = escape(run_id)
    return f"<section class='card'><h2>Continue investigation</h2><a class='button primary' href='/blueprint-import/{r}/explore'>Explore Twin intelligence</a> · <a href='/blueprint-import/{r}/inspect#technical-diagnostics'>View evidence</a></section><section class='card' id='candidate-governance'><h2>Candidate governance</h2><p><a href='/blueprint-import/{r}/review'>Review candidate governance</a> · <a href='/blueprint-import/{r}/review#identity-resolution'>Resolve Twin scope</a> · <a href='/blueprint-import/{r}/inspect'>Inspect import decisions</a></p></section>"


def _styles():
    return """<style>.executive-path{display:flex;gap:.65rem;flex-wrap:wrap;align-items:center;margin-bottom:1rem}.executive-path span,.executive-path a,.executive-path strong,.pill{padding:.45rem .7rem;border-radius:1rem;background:#eef5f2}.workspace-caveat{border-left:4px solid #b46b00;padding:.75rem;background:#fff8e8}.status-key{display:flex;gap:1rem;flex-wrap:wrap}.executive-summary-grid article{border-top:3px solid #185c4d}.theme-group{margin:1.5rem 0}.executive-conclusion,.enterprise-card{border-left:4px solid #c98b2e;padding:1rem;margin:.75rem 0;background:#fffdf8}.mission{padding:.7rem;background:#edf7f3}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:.6rem;border-bottom:1px solid #ddd}</style>"""
