"""Mission-aware, evidence-governed projection over an imported candidate Twin."""
from __future__ import annotations
from collections import Counter
from html import escape
from typing import Any
import json
import os
from pathlib import Path
from zipfile import ZipFile

from cios.applications.flora.access import can_access_enterprise
from cios.applications.flora.pilot_import import pilot_import_bypass_enabled, pilot_import_warning
from cios.applications.flora.commercial_mission import CommercialMission, resolve_commercial_mission, save_commercial_mission
from cios.applications.flora.workspace.views import _page
from .registry import BlueprintPackageRegistry
from .industry_delta_adapter import IndustryTwinDeltaAdapter
from .semantic_twin import SemanticEnterprise, SemanticObject, SemanticTwin, assemble_semantic_twin, business_collections
from .twin_governance import project_twin_identity
from .validator import BlueprintPackageValidator, can_inspect_blueprint_package

THEMES = (("market-condition", "Industry outlook", ("market", "industry", "sector", "economic")),
          ("financial-pressure", "Transformation pressures", ("financial", "cost", "revenue", "margin", "productivity", "resilience")),
          ("regulation", "Regulation", ("regulat", "policy", "compliance", "mandate")),
          ("technology", "Technology and data", ("technology", "digital", "data", "cloud", "ai ", "network")),
          ("customer", "Client problems", ("customer", "adoption", "demand", "experience", "operating model")),
          ("ecosystem", "Competitor and partner context", ("compet", "partner", "supplier", "ecosystem")))


def executive_workspace_page(import_run_id: str, headers: Any, *, view: str = "workspace",
                             enterprise_id: str = "", collection: str = "") -> tuple[str, int]:
    package = next((p for p in BlueprintPackageRegistry().list() if p.import_run_id == import_run_id), None)
    if package is None:
        return _page("Executive Intelligence Workspace unavailable", "<section class='hero'><h1>Executive Intelligence Workspace unavailable</h1><p>The import record could not be found.</p></section>"), 404
    bypass_candidate_read = pilot_import_bypass_enabled() and view in {"workspace", "explore", "enterprise"}
    if not bypass_candidate_read and (not can_access_enterprise(headers, package.identity.enterprise_id, package.workspace_id) or not can_inspect_blueprint_package(headers, package)):
        return _page("Access denied", "<section class='hero'><h1>Access denied</h1></section>"), 403
    warning = pilot_import_warning()
    summary = BlueprintPackageValidator().staging_summary(import_run_id) or {}
    candidates = _semantic_candidates(package, list(summary.get("candidates") or ()))
    twin = assemble_semantic_twin(candidates)
    mission = resolve_commercial_mission(headers)
    inspection = package.package_inspection or {}
    identity = project_twin_identity(package)
    title = str(inspection.get("twin_title") or inspection.get("package_title") or identity.primary_subject_name or package.identity.package_id)
    if view == "explore":
        return _page(f"Explore Twin — {title}", warning + _styles() + _explorer(twin, import_run_id, mission, collection)), 200
    if view == "enterprise":
        ent = next((e for e in twin.enterprises if e.identity_key == enterprise_id), None)
        if ent is None:
            return _page("Enterprise dossier unavailable", "<section class='hero'><h1>Enterprise dossier unavailable</h1></section>"), 404
        return _page(f"Enterprise Intelligence — {ent.name}", warning + _styles() + _dossier(ent, twin, import_run_id, mission)), 200
    if view == "mission":
        return _page("Edit Commercial Mission", _styles() + _mission_editor(mission, import_run_id)), 200
    unresolved = identity.status == "ambiguous" or not (identity.primary_subject_id and identity.governed_scope and identity.canonical_owner)
    body = warning + _styles() + _hero(title, inspection, unresolved, len(candidates), mission)
    body += _narrative(twin, mission) + _composition(twin, import_run_id) + _themes(twin, import_run_id) + _enterprise_index(twin, import_run_id)
    body += _reasoning_trace(twin, mission) + _attention(twin, import_run_id) + _validation_report(twin) + _limitations(twin, summary, mission, unresolved)
    body += _navigation(import_run_id)
    return _page(f"Executive Intelligence — {title}", body), 200


def _semantic_candidates(package, staged: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build a read-only canonical projection without changing promotion scope."""
    enriched = []
    for candidate in staged:
        copy = dict(candidate)
        payload = dict(copy.get("payload") or {})
        if payload.get("governed_object_category") == "objects" and payload.get("object_type"):
            copy["candidate_object_class"] = str(payload["object_type"])
        enriched.append(copy)
    if package.identity.package_id != "TMS-001":
        return enriched
    archive = Path(os.getenv("FLORA_DATA_DIR", "data")) / package.archive_path
    with ZipFile(archive) as bundle:
        names = bundle.namelist()
        def document(path):
            name = next(name for name in names if name.endswith("/" + path) or name == path)
            return json.loads(bundle.read(name))
        for _category, (path, key, kind) in IndustryTwinDeltaAdapter.TMS_CANONICAL.items():
            doc = document(path)
            rows = doc.get(key) if key else [doc]
            if kind == "executive_intelligence":
                shared = {k: doc.get(k) for k in ("status", "evidence_refs", "confidence", "freshness", "checkpoint_lineage")}
                rows = [{**shared, "id": f"{doc['id']}-{section}-{position}", "statement": statement,
                         "executive_section": section, "candidate_status": doc.get("status"),
                         "unknowns": doc.get("what_remains_uncertain") or ()}
                        for section in ("what_is_changing", "why_it_matters", "why_now", "why_them", "what_should_happen_next")
                        for position, statement in enumerate(doc.get(section) or (), 1)]
            for row in rows or ():
                if not isinstance(row, dict): continue
                identifier = str(row.get("id") or f"{kind}-{len(enriched)}")
                enriched.append({"candidate_record_id": f"canonical:{identifier}", "original_source_id": identifier,
                    "candidate_object_class": kind, "truth_class": "candidate", "payload": dict(row),
                    "validation_status": "accepted", "source_file": path, "source_location": identifier})
    return enriched


def _hero(title, inspection, unresolved, count, mission):
    caveat = "the Twin identity and governed scope have not yet been confirmed" if unresolved else "imported intelligence remains a candidate"
    composed = (f"<p class='mission'><strong>Composed for: {escape(mission.executive_role)} · {escape(mission.employer)}</strong> · <a href='#active-mission'>Inspect mission</a></p>" if mission else "")
    description = inspection.get("twin_description") or inspection.get("description") or "Explore the organisations, change, opportunities and supporting intelligence represented in this Twin."
    return f"""<nav class='executive-path'><strong>Overview</strong><a href='#composition'>Twin composition</a><a href='#material-insights'>Material insights</a><a href='#candidate-governance'>Governance</a></nav><header class='hero'><p class='eyebrow'>Executive Intelligence Workspace</p><p>Imported Twin · Candidate</p><h1>{escape(title)}</h1><p>{escape(str(description))}</p>{composed}<p class='workspace-caveat'>This understanding is provisional because {escape(caveat)}.</p></header>"""


def _mission(m: CommercialMission | None) -> str:
    if not m: return ""
    offers = ", ".join(m.offer_portfolio) or "No governed or explicitly human-supplied offer portfolio; offer alignment is incomplete."
    missing = [label for label, values in (("offer context", m.offer_portfolio), ("named accounts", m.named_accounts), ("campaigns", m.campaigns)) if not values]
    return f"""<section class='card' id='active-mission'><h2>Active Commercial Mission</h2><p><strong>{escape(m.executive_role)} · {escape(m.employer)}</strong></p><p>{escape(m.commercial_objective)}</p><p><strong>Offers:</strong> {escape(offers)}</p><p><strong>Interests:</strong> {escape(', '.join(m.interests) or 'not supplied')}</p><p><strong>Geography:</strong> {escape(', '.join(m.geography) or 'not supplied')} · <strong>Inspection depth:</strong> {escape(m.inspection_depth)}</p><p><strong>Missing mission information:</strong> {escape(', '.join(missing) or 'none declared missing')}</p><p class='pill'>{escape(m.authority_status)} · {escape(m.supplied_by)} · not Enterprise Intelligence</p><p><a href='mission'>Inspect and amend mission fields</a></p></section>"""


def _narrative(twin: SemanticTwin, mission: CommercialMission | None) -> str:
    eligible = [o for o in twin.objects if o.eligible_conclusion]
    timing = next((o.statement for o in eligible if "-why_now-" in o.original_id or "timing" in o.statement.casefold() or "urgency" in o.statement.casefold()), "No supported timing conclusion; investigate observation dates and material events.")
    mission_text = (f"Composition foregrounds the declared objective: {mission.commercial_objective}" if mission else "Neutral Twin intelligence is shown because no Commercial Mission is available; optionally establish one to tailor relevance.")
    offer = ("Offer alignment remains incomplete and no fit is inferred." if mission and not mission.offer_portfolio else "Potential offer alignment is a hypothesis requiring evidence validation.")
    return f"""<section class='card'><h2>Executive understanding</h2><p>This Twin brings together represented organisations and material change to support informed exploration.</p><div class='grid executive-summary-grid'><article><h3>Industry and enterprise change</h3><p>{len(twin.enterprises)} organisations and {len(eligible)} material insights warrant attention.</p></article><article><h3>Commercial relevance</h3><p>{escape(mission_text)}</p><p>{escape(offer)}</p></article><article><h3>Why now?</h3><p>{escape(timing)}</p></article></div></section>""" + _mission(mission)


def _composition(twin: SemanticTwin, run_id: str) -> str:
    tiles = "".join(f"<a class='composition-tile' href='/blueprint-import/{escape(run_id)}/explore?collection={escape(c.key)}'><strong>{escape(c.label)}</strong><b>{len(c.objects)}</b><span>{escape(c.description)}</span></a>" for c in business_collections(twin) if c.key != "other")
    return f"<section class='card' id='composition'><h2>Twin composition</h2><div class='composition-grid'>{tiles}</div><p><a href='/blueprint-import/{escape(run_id)}/explore'>Explore all Twin content</a></p></section>"


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
    return "<section class='card' id='material-insights'><h2>Material insights</h2>" + "".join(sections) + "</section>"


def _conclusion(o: SemanticObject, run_id: str) -> str:
    support = ", ".join(o.evidence_refs) or "No explicit Evidence reference; treat as unsupported"
    return f"""<article class='executive-conclusion'><h4>{escape(o.statement)}</h4>{f'<p>{escape(o.subject)}</p>' if o.subject not in ('', 'Twin scope') else ''}<details><summary>Explain this insight</summary><p><strong>Evidence:</strong> {escape(support)}</p><p><strong>Confidence:</strong> {escape(o.confidence)} · <strong>Freshness:</strong> {escape(o.freshness)}</p><p><strong>Contradiction status:</strong> inspect linked contradictions; absence is not inferred.</p><p><strong>Permitted use:</strong> {escape(o.permitted_use)} · <strong>State:</strong> {escape(o.governance)}</p><p><strong>Lineage:</strong> {escape(o.source_file)} · {escape(o.source_location)} · <code>{escape(o.original_id or o.record_id)}</code></p><a href='/blueprint-import/{escape(run_id)}/inspect#technical-diagnostics'>View source and lineage</a></details></article>"""


def _enterprise_index(twin, run_id):
    cards = "".join(_enterprise_card(e, run_id) for e in twin.enterprises) or "<p>No enterprise identity could be assembled from the supplied records.</p>"
    return f"<section class='card' id='enterprises'><h2>Priority enterprises</h2><p>All {len(twin.enterprises)} represented enterprises are shown; order is alphabetical and is not an opaque score.</p>{cards}<p><a class='button primary' href='/blueprint-import/{escape(run_id)}/explore'>Explore Twin intelligence</a></p></section>"


def _enterprise_card(e, run_id):
    ev = len({x for o in e.records for x in o.evidence_refs}); unk = sum(o.kind == 'unknown' for o in e.records); con = sum(o.kind == 'contradiction' for o in e.records); opp = sum('opportun' in o.kind for o in e.records)
    latest = next((o.statement for o in e.records if o.eligible_conclusion and o.kind not in {'evidence','unknown','contradiction'}), "No interpreted material change")
    latest_date = max((o.freshness for o in e.records if o.freshness != 'unknown'), default="unknown")
    state = "ambiguous identity — not merged" if e.ambiguous else ("governed" if any(o.governance == 'governed' for o in e.records) else "candidate")
    return f"""<article class='enterprise-card'><h3>{escape(e.name)}</h3><p>{escape(latest)}</p><p>Priority organisation represented in this Twin · {opp} opportunities · {unk} unknowns · {con} contradictions</p><p><a href='/blueprint-import/{escape(run_id)}/enterprises/{escape(e.identity_key)}'>Explore {escape(e.name)}</a></p></article>"""


def _validation_report(twin: SemanticTwin) -> str:
    counts = Counter(o.kind for o in twin.objects)
    evidenced = sum(bool(o.evidence_refs) for o in twin.objects)
    claims = [o for o in twin.objects if o.eligible_conclusion]
    unused_evidence = sum(o.kind == "evidence" and not any(o.original_id in c.evidence_refs for c in claims) for o in twin.objects)
    rows = "".join(f"<tr><td>{escape(kind)}</td><td>{count}</td></tr>" for kind, count in sorted(counts.items()))
    capabilities = ", ".join(o.statement for o in twin.objects if o.kind == "capability_offer" and o.statement) or "none supplied"
    return f"""<section class='card' id='package-validation'><h2>Deterministic package validation</h2><p><strong>Canonical priority enterprises: {len(twin.enterprises)}</strong> · Market Participants: {counts['market_participant_twin']} · Capabilities/offers: {counts['capability_offer']} · Opportunities: {counts['opportunity_hypothesis']} · Evidence: {counts['evidence']} · Unknowns: {counts['unknown']} · Contradictions: {counts['contradiction']}</p><p><strong>Capabilities and offers (not enterprises):</strong> {escape(capabilities)}</p><p>Evidence-reference coverage: {evidenced}/{len(twin.objects)} objects · Claims without evidence: {sum(not o.evidence_refs for o in claims)} · Evidence without claims: {unused_evidence} · Missing dates: {sum(o.freshness == 'unknown' for o in twin.objects)} · Unresolved references: {len(twin.unresolved_references)}</p><details><summary>Counts by canonical/runtime type and unresolved IDs</summary><table><tbody>{rows}</tbody></table><p>{escape(', '.join(twin.unresolved_references) or 'No unresolved canonical references')}</p></details></section>"""


def _mission_editor(m: CommercialMission | None, run_id: str) -> str:
    def value(name): return escape(", ".join(getattr(m, name)) if m and isinstance(getattr(m, name), tuple) else (getattr(m, name) if m else ""))
    fields = "".join(f"<label>{label}<input name='{name}' value='{value(name)}'></label>" for name, label in (
        ("executive_role", "Executive role"), ("employer", "Employer"), ("commercial_objective", "Primary objective"),
        ("industries", "Sectors"), ("geography", "Geography"), ("offer_portfolio", "Human-supplied offer context"),
        ("named_accounts", "Named accounts"), ("campaigns", "Campaigns"), ("interests", "Interests"),
        ("inspection_depth", "Inspection depth")))
    return f"<nav class='executive-path'><a href='/blueprint-import/{escape(run_id)}'>Executive Workspace</a><strong>Commercial Mission</strong></nav><section class='card'><h1>Inspect and amend Commercial Mission</h1><p>Every field is human-supplied operational context, not Enterprise Intelligence. Empty offer context remains incomplete; it is never inferred.</p><form method='post' action='/blueprint-import/{escape(run_id)}/mission'>{fields}<button class='button primary'>Save mission</button></form></section>"


def update_commercial_mission(import_run_id: str, headers: Any, form: dict[str, list[str]]) -> tuple[str, int]:
    values = {key: (items[0] if items else "") for key, items in form.items()}
    for key in ("industries", "geography", "offer_portfolio", "named_accounts", "campaigns", "interests"):
        values[key] = [item.strip() for item in str(values.get(key, "")).split(",") if item.strip()]
    values.update(authority_status="human-supplied operational context", supplied_by="authenticated user profile edit")
    try:
        save_commercial_mission(headers, values)
    except PermissionError:
        return _page("Access denied", "<h1>Access denied</h1>"), 403
    except ValueError as exc:
        return _page("Mission not saved", f"<h1>Mission not saved</h1><p>{escape(str(exc))}</p>"), 400
    return executive_workspace_page(import_run_id, headers)


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


def _explorer(twin, run_id, mission, selected=""):
    counts = Counter(o.kind for o in twin.objects); governed = sum(o.governance == 'governed' for o in twin.objects)
    aspects = "".join(f"<tr><td>{escape(k)}</td><td>{v}</td><td>{sum(o.governance=='candidate' for o in twin.objects if o.kind==k)} candidate / {sum(o.governance=='governed' for o in twin.objects if o.kind==k)} governed</td><td>{sum(bool(o.evidence_refs) for o in twin.objects if o.kind==k)} evidenced</td><td>{sum(not o.eligible_conclusion for o in twin.objects if o.kind==k)} unresolved</td></tr>" for k,v in sorted(counts.items()))
    enterprises = "".join(_enterprise_card(e, run_id) for e in twin.enterprises)
    collections = business_collections(twin)
    active = next((c for c in collections if c.key == selected), None)
    links = "".join(f"<a class='collection-chip' href='?collection={escape(c.key)}'>{escape(c.label)} <b>{len(c.objects)}</b></a>" for c in collections)
    if active and active.key == "enterprises": content = enterprises or "<p>No enterprise identities supplied.</p>"
    elif active: content = "".join(_conclusion(o, run_id) if o.statement else f"<article class='enterprise-card'><h3>{escape(o.original_id or 'Twin record')}</h3><p>Available for advanced inspection.</p><a href='/blueprint-import/{escape(run_id)}/inspect#technical-diagnostics'>Inspect record</a></article>" for o in active.objects)
    else: content = "<p>Select a business collection to explore its contents.</p>"
    title = active.label if active else "Explore Twin intelligence"
    return f"<nav class='executive-path'><a href='/blueprint-import/{escape(run_id)}'>Twin overview</a><strong>Twin Explorer</strong><a href='/blueprint-import/{escape(run_id)}/review'>Governance</a></nav><header class='hero'><h1>{escape(title)}</h1><p>{escape(active.description) if active else 'Explore the Twin through business-facing collections.'}</p></header><section class='card'><h2>Twin collections</h2><div class='collection-links'>{links}</div></section><section class='card'><h2>{escape(title)}</h2>{content}</section><details class='card'><summary>Advanced aspect coverage</summary><table><thead><tr><th>Aspect</th><th>Objects</th><th>Governance</th><th>Evidence coverage</th><th>Unresolved</th></tr></thead><tbody>{aspects}</tbody></table></details>"


def _dossier(ent, twin, run_id, mission):
    relevant = list(ent.records)
    domains = Counter(o.kind for o in relevant)
    sections = (("Overview", ("enterprise", "enterprise_twin", "entity", "observation", "fact", "executive_intelligence")), ("Financials", ("financial_observation", "financial_fact", "economic_pool")), ("Transformation", ("transformation_programme",)), ("Technology and capabilities", ("capability_offer",)), ("Relationships", ("relationship", "supplier_relationship")), ("Opportunities", ("opportunity_hypothesis", "ranked_opportunity")), ("Unknowns and contradictions", ("unknown", "contradiction")), ("Evidence", ("evidence",)))
    rendered = []
    for label, kinds in sections:
        rows = [o for o in relevant if o.kind in kinds and (o.eligible_conclusion or o.kind in {"evidence", "enterprise", "enterprise_twin", "entity"})]
        if rows: rendered.append(f"<section class='card'><h2>{label}</h2>{''.join(_conclusion(o, run_id) if o.statement else '<p>Identity represented in this Twin.</p>' for o in rows)}</section>")
    gaps = [d for d in ("strategy", "financial", "leadership", "customer", "operating_model", "technology", "programme", "supplier", "procurement", "opportunity_hypothesis") if not any(d in k.casefold() for k in domains)]
    signal = next((o.statement for o in relevant if o.eligible_conclusion), "Explore the intelligence explicitly associated with this organisation.")
    return f"<nav class='executive-path'><a href='/blueprint-import/{escape(run_id)}'>Twin overview</a><a href='/blueprint-import/{escape(run_id)}/explore?collection=enterprises'>Enterprises</a><strong>Enterprise dossier</strong></nav><header class='hero'><h1>{escape(ent.name)}</h1><p>Priority organisation represented in this Twin.</p><p>{escape(signal)}</p></header>{''.join(rendered)}<details class='card'><summary>Advanced inspection and governance</summary><p>Canonical identifiers and excluded records remain available in package inspection.</p><a href='/blueprint-import/{escape(run_id)}/inspect'>View evidence and provenance</a> · <a href='/blueprint-import/{escape(run_id)}/review'>Review candidate governance</a></details>"


def _navigation(run_id):
    r = escape(run_id)
    return f"<section class='card'><h2>Continue investigation</h2><a class='button primary' href='/blueprint-import/{r}/explore'>Explore Twin intelligence</a> · <a href='/blueprint-import/{r}/inspect#technical-diagnostics'>View evidence</a></section><section class='card' id='candidate-governance'><h2>Candidate governance</h2><p><a href='/blueprint-import/{r}/review'>Review candidate governance</a> · <a href='/blueprint-import/{r}/review#identity-resolution'>Resolve Twin scope</a> · <a href='/blueprint-import/{r}/inspect'>Inspect import decisions</a> · <a href='/blueprint-import/{r}/inspect'>View package validation</a></p></section>"


def _styles():
    return """<style>.executive-path{display:flex;gap:.65rem;flex-wrap:wrap;align-items:center;margin-bottom:1rem}.executive-path span,.executive-path a,.executive-path strong,.pill,.collection-chip{padding:.45rem .7rem;border-radius:1rem;background:#eef5f2}.workspace-caveat{border-left:4px solid #b46b00;padding:.75rem;background:#fff8e8}.executive-summary-grid article{border-top:3px solid #185c4d}.theme-group{margin:1.5rem 0}.executive-conclusion,.enterprise-card{border-left:4px solid #c98b2e;padding:1rem;margin:.75rem 0;background:#fffdf8}.mission{padding:.7rem;background:#edf7f3}.composition-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem}.composition-tile{display:flex;min-height:9rem;flex-direction:column;gap:.5rem;padding:1rem;border:1px solid #cad8d3;border-radius:.7rem;text-decoration:none;color:inherit}.composition-tile:focus,.composition-tile:hover{outline:3px solid #185c4d}.composition-tile b{font-size:2rem}.collection-links{display:flex;gap:.6rem;flex-wrap:wrap}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:.6rem;border-bottom:1px solid #ddd}@media(max-width:600px){.composition-grid{grid-template-columns:1fr}}</style>"""
