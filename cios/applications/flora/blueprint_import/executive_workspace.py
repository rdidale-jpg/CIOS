"""Mission-aware, evidence-governed projection over an imported candidate Twin."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from html import escape
from typing import Any
import json
import os
from pathlib import Path
from zipfile import ZipFile

from cios.applications.flora.access import can_access_enterprise
from cios.applications.flora.pilot_import import pilot_import_bypass_enabled
from cios.applications.flora.commercial_mission import CommercialMission, resolve_commercial_mission, save_commercial_mission
from cios.applications.flora.workspace.views import _page
from .registry import BlueprintPackageRegistry
from .industry_delta_adapter import IndustryTwinDeltaAdapter
from .semantic_twin import (SemanticEnterprise, SemanticObject, SemanticTwin, assemble_semantic_twin,
                            business_collections, executive_insight_eligible)
from .twin_governance import project_twin_identity
from .validator import BlueprintPackageValidator, can_inspect_blueprint_package

THEMES = (("market-condition", "Industry outlook", ("market", "industry", "sector", "economic")),
          ("financial-pressure", "Transformation pressures", ("financial", "cost", "revenue", "margin", "productivity", "resilience")),
          ("regulation", "Regulation", ("regulat", "policy", "compliance", "mandate")),
          ("technology", "Technology and data", ("technology", "digital", "data", "cloud", "ai ", "network")),
          ("customer", "Client problems", ("customer", "adoption", "demand", "experience", "operating model")),
          ("ecosystem", "Competitor and partner context", ("compet", "partner", "supplier", "ecosystem")))


@dataclass(frozen=True)
class CompletenessAspect:
    name: str
    state: str
    missing: tuple[str, ...] = ()


def executive_workspace_page(import_run_id: str, headers: Any, *, view: str = "workspace",
                             enterprise_id: str = "", collection: str = "", domain: str = "all") -> tuple[str, int]:
    package = next((p for p in BlueprintPackageRegistry().list() if p.import_run_id == import_run_id), None)
    if package is None:
        return _page("Executive Intelligence Workspace unavailable", "<section class='hero'><h1>Executive Intelligence Workspace unavailable</h1><p>The import record could not be found.</p></section>"), 404
    bypass_candidate_read = pilot_import_bypass_enabled() and view in {"workspace", "explore", "enterprise", "health"}
    if not bypass_candidate_read and (not can_access_enterprise(headers, package.identity.enterprise_id, package.workspace_id) or not can_inspect_blueprint_package(headers, package)):
        return _page("Access denied", "<section class='hero'><h1>Access denied</h1></section>"), 403
    summary = BlueprintPackageValidator().staging_summary(import_run_id) or {}
    candidates = _semantic_candidates(package, list(summary.get("candidates") or ()))
    twin = assemble_semantic_twin(candidates)
    mission = resolve_commercial_mission(headers)
    inspection = package.package_inspection or {}
    identity = project_twin_identity(package)
    title = str(inspection.get("twin_title") or inspection.get("package_title") or identity.primary_subject_name or package.identity.package_id)
    if view == "explore":
        return _page(f"Explore Twin — {title}", _styles() + _explorer(twin, import_run_id, mission, collection, domain)), 200
    if view == "health":
        return _page(f"Twin Health — {title}", _styles() + _health(twin, import_run_id, summary)), 200
    if view == "enterprise":
        ent = next((e for e in twin.enterprises if e.identity_key == enterprise_id), None)
        if ent is None:
            return _page("Enterprise dossier unavailable", "<section class='hero'><h1>Enterprise dossier unavailable</h1></section>"), 404
        return _page(f"Enterprise Intelligence — {ent.name}", _styles() + _dossier(ent, twin, import_run_id, mission)), 200
    if view == "mission":
        return _page("Edit Commercial Mission", _styles() + _mission_editor(mission, import_run_id)), 200
    body = _styles() + _hero(title)
    body += (_domain_lenses(import_run_id, domain) + _composition(twin, import_run_id, domain)
             + _opportunities(twin, import_run_id, mission, domain)
             + _reinvention_themes(twin, import_run_id, domain) + _pressure(twin, import_run_id, domain)
             + _themes(twin, import_run_id, domain) + _enterprise_index(twin, import_run_id, domain))
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
                consequences = list(doc.get("why_it_matters") or ())
                timing = list(doc.get("why_now") or ())
                rows = [{**shared, "id": f"{doc['id']}-{section}-{position}", "statement": statement,
                         "executive_section": section, "candidate_status": doc.get("status"),
                         "subject": ("Telecoms" if "telecom" in statement.casefold() else "Media" if "media" in statement.casefold() else "Sport" if "sport" in statement.casefold() else "TMS industry"),
                         "domains": ([d for d in ("Telecoms", "Media", "Sport") if d.casefold() in statement.casefold()] or list(doc.get("subsectors") or ())),
                         "business_consequence": (consequences[position-1] if section == "what_is_changing" and position <= len(consequences) else ""),
                         "important_next_event": (timing[position-1] if section == "what_is_changing" and position <= len(timing) else ""),
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


def _hero(title):
    return f"<header class='compact-twin-header'><h1><span class='pilot-badge'>PILOT</span><span aria-hidden='true'> · </span>{escape(title)}</h1></header>"


def _domain_lenses(run_id: str, active: str) -> str:
    labels = (("all", "All Twin"), ("telecoms", "Telecoms"), ("media", "Media"), ("sport", "Sport"), ("cross-domain", "Cross-domain"))
    links = "".join(f"<a class='domain-lens{' active' if key == active else ''}' href='/blueprint-import/{escape(run_id)}?domain={key}' aria-current='{'page' if key == active else 'false'}'>{label}</a>" for key, label in labels)
    return f"<nav class='domain-lenses' aria-label='Twin domains'>{links}</nav>"


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


def _composition(twin: SemanticTwin, run_id: str, domain="all") -> str:
    tiles = "".join(f"<a class='composition-tile' href='/blueprint-import/{escape(run_id)}/explore?collection={escape(c.key)}&amp;domain={escape(domain)}'><strong>{escape(c.label)}</strong><b>{len(c.objects)}</b><span>{escape(c.description)}</span></a>" for c in business_collections(twin, domain=domain) if c.key != "other")
    return f"<section class='card' id='composition'><h2>Twin Composition</h2><div class='composition-grid'>{tiles}</div></section>"


def _field(o: SemanticObject, *names: str) -> str:
    data = o.attributes or {}
    for name in names:
        value = data.get(name)
        if value not in (None, "", [], ()):
            return ", ".join(map(str, value)) if isinstance(value, (list, tuple)) else str(value)
    return ""


def _opportunity_card(o: SemanticObject, run_id: str) -> str:
    problem = _field(o, "client_problem", "customer_problem", "problem") or "Client problem not established"
    timing = _field(o, "why_now", "timing", "target_date", "deadline") or "Timing not established"
    enterprises = ", ".join(o.affected_organisations) or (o.subject if o.subject != "Twin scope" else "Affected enterprise not established")
    theme = _field(o, "reinvention_theme", "theme")
    relevance = _field(o, "commercial_relevance")
    evidence = ", ".join(o.evidence_refs) or "Evidence not linked"
    missing = [label for label, present in (("client problem", problem != "Client problem not established"),
               ("affected enterprise", enterprises != "Affected enterprise not established"),
               ("evidence", bool(o.evidence_refs)), ("timing", timing != "Timing not established")) if not present]
    details = "".join(f"<p><strong>{label}:</strong> {escape(value)}</p>" for label, value in
                      (("Affected enterprises", enterprises), ("Client problem", problem),
                       ("Relevant domain", ", ".join(d.title() for d in o.domains) or "Domain not established"),
                       ("Reinvention theme", theme or "Theme not established"), ("Why now", timing)) if value)
    if relevance: details += f"<p><strong>Commercial relevance:</strong> {escape(relevance)}</p>"
    details += f"<p><strong>Evidence:</strong> {escape(evidence)} · <strong>Confidence:</strong> {escape(o.confidence)}</p>"
    details += f"<p><strong>Missing information:</strong> {escape(', '.join(missing) or 'None under the presentation contract')}</p>"
    return f"<article class='executive-conclusion opportunity-card'><h3>{escape(o.statement)}</h3>{details}<a href='/blueprint-import/{escape(run_id)}/explore?collection=opportunities#{escape(o.record_id)}'>Open opportunity</a></article>"


def _opportunities(twin: SemanticTwin, run_id: str, mission: CommercialMission | None, domain="all") -> str:
    collection = next((c for c in business_collections(twin, domain=domain) if c.key == "opportunities"), None)
    rows = tuple(collection.objects if collection else ())
    if not rows: return ""
    label = "Opportunities for you" if mission else "Commercial Opportunities"
    return f"<section class='card' id='opportunities'><h2>{label}</h2><div class='theme-grid'>{''.join(_opportunity_card(o, run_id) for o in rows[:4])}</div><a href='/blueprint-import/{escape(run_id)}/explore?collection=opportunities&amp;domain={escape(domain)}'>Explore all opportunities</a></section>"


def _reinvention_kind(o: SemanticObject) -> str:
    text = (o.kind + " " + o.statement + " " + o.consequence).casefold()
    rules = (("Regulation", ("regulat", "compliance", "policy")), ("Technology and infrastructure", ("technology", "cloud", "network", "migration", "platform")),
             ("Cost and financial pressure", ("cost", "financial", "revenue", "margin", "funding")),
             ("Customer and audience change", ("customer", "audience", "subscriber", "demand")),
             ("Data and platform control", ("data", "platform control")), ("Operating-model change", ("operating model", "operating-model", "workforce")))
    supported_kind = o.kind in {"transformation_programme", "executive_intelligence", "supported_interpreted_observation", "financial_observation", "financial_fact"}
    if o.kind in {"observation", "fact"}:
        # Generic observations are not silently promoted into a reinvention
        # classification; the canonical record must explicitly classify the
        # material change.
        supported_kind = bool(_field(o, "change_type", "pressure_type", "reinvention_theme"))
    return next((label for label, terms in rules if supported_kind and any(t in text for t in terms)), "")


def _reinvention_themes(twin: SemanticTwin, run_id: str, domain="all") -> str:
    groups: dict[str, list[SemanticObject]] = {}
    for o in twin.objects:
        if not _in_lens(o, domain): continue
        theme = _reinvention_kind(o)
        if theme and (o.evidence_refs or o.kind == "transformation_programme"): groups.setdefault(theme, []).append(o)
    if not groups: return ""
    cards = []
    for theme, rows in groups.items():
        enterprises = sorted({x for o in rows for x in ((*o.affected_organisations,) if o.affected_organisations else (() if o.subject == "Twin scope" else (o.subject,)))})
        domains = sorted({d.title() for o in rows for d in o.domains})
        consequence = next((o.consequence for o in rows if o.consequence), "Commercial consequence not established")
        state = "Complete enough for executive use" if enterprises and domains and consequence != "Commercial consequence not established" else "Partial"
        cards.append(f"<article class='theme-tile'><h3>{escape(theme)}</h3><p><strong>Affected domains:</strong> {escape(', '.join(domains) or 'Not established')}</p><p><strong>Affected enterprises:</strong> {escape(', '.join(enterprises) or 'Not established')}</p><p><strong>Supporting changes or programmes:</strong> {escape('; '.join(o.statement for o in rows[:3]))}</p><p><strong>Commercial consequence:</strong> {escape(consequence)}</p><p class='pill'>{state}</p></article>")
    return "<section class='card' id='reinvention-themes'><h2>Reinvention Themes</h2><div class='theme-grid'>" + "".join(cards) + "</div></section>"


def _in_lens(o: SemanticObject, domain: str) -> bool:
    lens = domain.casefold().replace("-", " ")
    return lens in {"", "all", "all twin"} or (lens == "cross domain" and len(o.domains) >= 2) or lens in o.domains


def _pressure_items(twin: SemanticTwin, run_id: str, domain="all", enterprise: str = "") -> list[str]:
    result = []
    for o in twin.objects:
        if not _in_lens(o, domain) or (enterprise and o.subject.casefold() != enterprise.casefold() and enterprise.casefold() not in {x.casefold() for x in o.affected_organisations}): continue
        theme = _reinvention_kind(o)
        if not theme or not o.consequence or not o.evidence_refs: continue
        timing = _field(o, "deadline", "timing", "why_now", "target_date", "programme_date")
        if not timing and o.freshness != "unknown" and any(x in (o.statement + " " + o.kind).casefold() for x in ("deadline", "timetable", "migration", "transition", "programme")): timing = o.freshness
        organisations = ", ".join(o.affected_organisations) or (o.subject if o.subject != "Twin scope" else "Affected organisation not established")
        result.append(f"<article class='executive-conclusion'><h3>{escape(o.statement)}</h3><p><strong>Pressure:</strong> {escape(theme)}</p><p><strong>Consequence of inaction:</strong> {escape(o.consequence)}</p><p><strong>Timing:</strong> {escape(timing or 'Timing not established')}</p><p><strong>Affected organisations:</strong> {escape(organisations)}</p><p><strong>Evidence:</strong> {escape(', '.join(o.evidence_refs))} · <strong>Confidence:</strong> {escape(o.confidence)}</p></article>")
    return result


def _pressure(twin: SemanticTwin, run_id: str, domain="all") -> str:
    rows = _pressure_items(twin, run_id, domain)[:4]
    return ("<section class='card' id='pressure-urgency'><h2>Pressure and Urgency</h2><div class='theme-grid'>" + "".join(rows) + "</div></section>") if rows else ""


def _themes(twin: SemanticTwin, run_id: str, domain="all") -> str:
    insight_collection = next((c for c in business_collections(twin, domain=domain) if c.key == "insights"), None)
    eligible = list(insight_collection.objects if insight_collection else ())
    used: set[str] = set(); sections = []
    for key, label, terms in THEMES:
        rows = [o for o in eligible if o.record_id not in used and any(t in (o.statement + " " + o.kind).casefold() for t in terms)][:5]
        if rows:
            used.update(o.record_id for o in rows); sections.append(f"<a class='theme-tile' href='/blueprint-import/{escape(run_id)}/explore?collection=insights&amp;theme={key}&amp;domain={escape(domain)}'><strong>{label}</strong><b>{len(rows)}</b><span>{escape(rows[0].consequence)}</span></a>")
    other = [o for o in eligible if o.record_id not in used][:5]
    if other: sections.append(f"<a class='theme-tile' href='/blueprint-import/{escape(run_id)}/explore?collection=insights&amp;theme=other&amp;domain={escape(domain)}'><strong>Other supported observations</strong><b>{len(other)}</b><span>{escape(other[0].consequence)}</span></a>")
    if not sections: sections = ["<p>No semantically complete conclusion is available. Inspect typed coverage and gather evidence rather than treating raw records as meaning.</p>"]
    return "<section class='card' id='material-insights'><h2>Material Insights</h2><div class='theme-grid'>" + "".join(sections) + "</div></section>"


def _conclusion(o: SemanticObject, run_id: str) -> str:
    if not executive_insight_eligible(o):
        return ""
    support = ", ".join(o.evidence_refs) or "No explicit Evidence reference; treat as unsupported"
    affected = ", ".join(o.affected_organisations) or o.subject
    domains = " · ".join(d.title() for d in o.domains)
    watch = _field(o, "important_next_event", "why_now", "timing", "deadline") or "Timing not established"
    return f"""<a class='executive-conclusion' href='#explanation-{escape(o.record_id)}'><h3>{escape(o.statement)}</h3><p><strong>Why it matters:</strong> {escape(o.consequence)}</p><p class='insight-meta'>{escape(domains)}{(' · '+escape(affected)) if affected else ''}</p></a><section class='insight-explanation' id='explanation-{escape(o.record_id)}' tabindex='-1'><h3>Executive explanation</h3><h4>What is happening?</h4><p>{escape(o.statement)}</p><h4>Why does it matter?</h4><p>{escape(o.consequence)}</p><h4>Who is affected?</h4><p>{escape(affected)}</p><h4>What should I watch?</h4><p>{escape(watch)}</p><details><summary>Key Sources</summary><p>{escape(support)}</p></details><details><summary>Advanced explanation</summary><p><strong>Confidence:</strong> {escape(o.confidence)} · <strong>Freshness:</strong> {escape(o.freshness)}</p><p><strong>Lineage:</strong> {escape(o.source_file)} · {escape(o.source_location)} · <code>{escape(o.original_id or o.record_id)}</code></p><p><strong>Permitted use:</strong> {escape(o.permitted_use)} · <strong>State:</strong> {escape(o.governance)}</p><a href='/blueprint-import/{escape(run_id)}/inspect#technical-diagnostics'>Inspect evidence and lineage</a></details></section>"""


def _enterprise_index(twin, run_id, domain="all"):
    cards = "".join(_enterprise_card(e, run_id) for e in twin.enterprises if domain == "all" or any(domain.replace('-', ' ') in o.domains for o in e.records)) or "<p>No enterprise identity is explicitly associated with this domain.</p>"
    return f"<section class='card' id='enterprises'><h2>Priority Enterprises</h2><div class='enterprise-grid'>{cards}</div></section>"


def _enterprise_card(e, run_id):
    unk = sum(o.kind == 'unknown' for o in e.records); con = sum(o.kind == 'contradiction' for o in e.records); opp = sum('opportun' in o.kind for o in e.records)
    domains = sorted({d.title() for o in e.records for d in o.domains})
    facts = ["Priority organisation represented in this Twin", *domains]
    if opp: facts.append("1 opportunity" if opp == 1 else f"{opp} opportunities")
    if unk: facts.append(f"{unk} uncertaint{'ies' if unk != 1 else 'y'}")
    if con: facts.append(f"{con} contradiction{'s' if con != 1 else ''}")
    return f"<a class='enterprise-card' href='/blueprint-import/{escape(run_id)}/enterprises/{escape(e.identity_key)}'><h3>{escape(e.name)}</h3><p>{escape(' · '.join(facts))}</p></a>"


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


def _explorer(twin, run_id, mission, selected="", domain="all"):
    counts = Counter(o.kind for o in twin.objects); governed = sum(o.governance == 'governed' for o in twin.objects)
    aspects = "".join(f"<tr><td>{escape(k)}</td><td>{v}</td><td>{sum(o.governance=='candidate' for o in twin.objects if o.kind==k)} candidate / {sum(o.governance=='governed' for o in twin.objects if o.kind==k)} governed</td><td>{sum(bool(o.evidence_refs) for o in twin.objects if o.kind==k)} evidenced</td><td>{sum(not o.eligible_conclusion for o in twin.objects if o.kind==k)} unresolved</td></tr>" for k,v in sorted(counts.items()))
    visible_enterprises = [e for e in twin.enterprises if domain in {"", "all"} or any(_in_lens(o, domain) for o in e.records)]
    enterprises = "".join(_enterprise_card(e, run_id) for e in visible_enterprises)
    collections = business_collections(twin, domain=domain)
    active = next((c for c in collections if c.key == selected), None)
    links = "".join(f"<a class='collection-chip' href='?collection={escape(c.key)}&amp;domain={escape(domain)}'>{escape(c.label)} <b>{len(c.objects)}</b></a>" for c in collections)
    if active and active.key == "enterprises": content = enterprises or "<p>No enterprise identities supplied.</p>"
    elif active and active.key == "opportunities": content = "".join(_opportunity_card(o, run_id) for o in active.objects)
    elif active: content = "".join(_conclusion(o, run_id) if executive_insight_eligible(o) else f"<article class='enterprise-card'><h3>{escape(o.statement or o.original_id or 'Twin record')}</h3><p>Supporting context; not presented as an executive insight.</p><a href='/blueprint-import/{escape(run_id)}/inspect#technical-diagnostics'>Inspect record</a></article>" for o in active.objects)
    else: content = "<p>Select a business collection to explore its contents.</p>"
    title = active.label if active else "Explore Twin intelligence"
    total = len(active.objects) if active else 0
    return f"<nav class='executive-path'><a href='/blueprint-import/{escape(run_id)}'>Twin overview</a><strong>Twin Explorer</strong><a href='/blueprint-import/{escape(run_id)}/review'>Governance</a></nav><header class='hero'><h1>{escape(title)}</h1><p>{escape(active.description) if active else 'Explore the Twin through business-facing collections.'}</p></header><section class='card'><h2>Twin collections</h2><div class='collection-links'>{links}</div></section><section class='card'><h2>{escape(title)}{f' — {total} total' if active else ''}</h2><p>{f'Showing {total} distinct identities' if active and active.key == 'enterprises' else f'Showing {total} of {total} total records' if active else ''}</p>{content}</section><details class='card'><summary>Advanced aspect coverage</summary><table><thead><tr><th>Aspect</th><th>Objects</th><th>Governance</th><th>Evidence coverage</th><th>Unresolved</th></tr></thead><tbody>{aspects}</tbody></table></details>"


def _dossier(ent, twin, run_id, mission):
    relevant = list(ent.records)
    kinds = Counter(o.kind for o in relevant)
    identities = [o for o in relevant if o.kind in {"enterprise", "enterprise_twin", "entity"}]
    description = next((_field(o, "organisation_description", "overview", "description", "summary") for o in identities if _field(o, "organisation_description", "overview", "description", "summary")), "")
    if not description:
        description = f"{ent.name} is an organisation represented in this Twin for executive interpretation; its detailed business description remains a research gap."
    domain_names = sorted({d.title() for o in relevant for d in o.domains})
    material = next((o for o in relevant if executive_insight_eligible(o)), None)
    statuses = _enterprise_completeness(ent, mission)
    complete = sum(s.state == "Complete enough for executive use" for s in statuses)
    overview = f"<section class='card' id='enterprise-overview'><h2>Overview</h2><p>{escape(description)}</p><p><strong>Role in the Twin:</strong> Priority enterprise associated through canonical identity and relationships.</p><p><strong>Relevant domains:</strong> {escape(', '.join(domain_names) or 'Domain association not established')}</p><p><strong>Current position:</strong> {escape(_field(identities[0], 'current_position') if identities else '') or 'Current position requires further structured research.'}</p><p><strong>Most material supported change:</strong> {escape(material.statement if material else 'No complete executive insight is available for this enterprise.')}</p><p><strong>Completeness:</strong> {complete} of {len(statuses)} aspects are complete enough; inspect aspect states below.</p></section>"
    rendered = [overview]
    financials = [o for o in relevant if o.kind in {"financial_observation", "financial_fact", "economic_pool"} and _field(o, "metric", "measure") and _field(o, "value") and _field(o, "period") and _field(o, "source")]
    if financials:
        body = "".join(f"<article><h3>{escape(_field(o, 'metric', 'measure'))}</h3><p><strong>Value:</strong> {escape(_field(o, 'value'))} {escape(_field(o, 'currency', 'unit'))} · <strong>Period:</strong> {escape(_field(o, 'period'))}</p><p><strong>Source:</strong> {escape(_field(o, 'source'))}</p>{f'<p><strong>Interpretation:</strong> {escape(o.consequence)}</p>' if o.consequence else ''}</article>" for o in financials)
        rendered.append(f"<section class='card'><h2>Key financials</h2>{body}</section>")
    changes = [o for o in relevant if executive_insight_eligible(o)]
    if changes: rendered.append("<section class='card'><h2>Material changes</h2>" + "".join(_conclusion(o, run_id) for o in changes) + "</section>")
    themes = sorted({_reinvention_kind(o) for o in relevant if _reinvention_kind(o) and (o.evidence_refs or o.kind == 'transformation_programme')})
    if themes: rendered.append("<section class='card'><h2>Reinvention themes</h2><ul>" + "".join(f"<li>{escape(t)}</li>" for t in themes) + "</ul></section>")
    pressure = _pressure_items(twin, run_id, enterprise=ent.name)
    if pressure: rendered.append("<section class='card'><h2>Pressure and urgency</h2>" + "".join(pressure) + "</section>")
    programmes = [o for o in relevant if o.kind == "transformation_programme"]
    if programmes: rendered.append("<section class='card'><h2>Transformation programmes</h2>" + "".join(f"<article><h3>{escape(o.statement)}</h3><p>{escape(o.consequence or 'Business consequence not structured')}</p></article>" for o in programmes) + "</section>")
    procurements = [o for o in relevant if o.kind in {"procurement", "procurement_route", "buying_centre"} or _field(o, "procurement_route", "procuring_organisation")]
    if procurements:
        rendered.append("<section class='card'><h2>Known procurements</h2>" + "".join(_procurement_item(o, ent.name) for o in procurements) + "</section>")
    opportunities = [o for o in relevant if "opportun" in o.kind]
    if opportunities: rendered.append("<section class='card'><h2>Opportunities</h2>" + "".join(_opportunity_card(o, run_id) for o in opportunities) + "</section>")
    relationships = [o for o in relevant if o.kind in {"relationship", "supplier_relationship"}]
    if relationships: rendered.append("<section class='card'><h2>Relationships</h2>" + "".join(f"<p>{escape(o.statement)}</p>" for o in relationships if o.statement) + "</section>")
    sources = [o for o in relevant if o.kind == "evidence"]
    if sources: rendered.append("<section class='card'><h2>Key Sources</h2>" + "".join(_source_item(o) for o in sources) + "</section>")
    uncertainties = [o for o in relevant if o.kind in {"unknown", "contradiction"}]
    if uncertainties: rendered.append("<section class='card'><h2>Important unknowns and contradictions</h2>" + "".join(f"<article><h3>{escape(o.statement)}</h3><p><strong>Why it matters:</strong> {escape(o.consequence or 'Research gap: consequence and affected decision are not established.')}</p><p><strong>Evidence needed:</strong> {escape(_field(o, 'evidence_needed', 'resolution') or 'Resolving evidence not specified.')}</p></article>" for o in uncertainties) + "</section>")
    completeness = _completeness_html(ent, statuses)
    return f"<nav class='executive-path'><a href='/blueprint-import/{escape(run_id)}'>Twin overview</a><a href='/blueprint-import/{escape(run_id)}/explore?collection=enterprises'>Enterprises</a><strong>Enterprise dossier</strong></nav><header class='hero'><h1>{escape(ent.name)}</h1><p>{escape(description)}</p></header>{''.join(rendered)}{completeness}<details class='card'><summary>Advanced inspection and governance</summary><p>Canonical identifiers and excluded records remain available in package inspection.</p><a href='/blueprint-import/{escape(run_id)}/inspect'>View evidence and provenance</a> · <a href='/blueprint-import/{escape(run_id)}/review'>Review candidate governance</a></details>"


def _procurement_item(o: SemanticObject, enterprise: str) -> str:
    return f"<article><h3>{escape(o.statement or _field(o, 'requirement', 'programme'))}</h3><p><strong>Procuring organisation:</strong> {escape(_field(o, 'procuring_organisation') or enterprise)}</p><p><strong>Stage/status:</strong> {escape(_field(o, 'stage', 'status') or 'Not established')} · <strong>Timing:</strong> {escape(_field(o, 'timing', 'deadline') or 'Timing not established')}</p><p><strong>Route:</strong> {escape(_field(o, 'route', 'procurement_route') or 'Not established')} · <strong>Buyer/buying centre:</strong> {escape(_field(o, 'buyer', 'buying_centre') or 'Not established')}</p><p><strong>Source:</strong> {escape(', '.join(o.evidence_refs) or 'Evidence not linked')} · <strong>Uncertainty:</strong> {escape(_field(o, 'uncertainty') or 'No explicit uncertainty supplied')}</p></article>"


def _source_item(o: SemanticObject) -> str:
    url = _field(o, "url", "source_url", "link")
    title = _field(o, "title") or o.statement or o.original_id
    linked = f"<a href='{escape(url)}' rel='noopener'>{escape(title)}</a>" if url else escape(title)
    return f"<article><h3>{linked}</h3><p><strong>Publisher/origin:</strong> {escape(_field(o, 'publisher', 'origin') or o.source_file)}</p><p><strong>Publication date:</strong> {escape(_field(o, 'publication_date', 'date') or 'Date not established')}</p><p><strong>What it supports:</strong> {escape(_field(o, 'supports', 'what_it_supports') or 'Claim linkage requires review')}</p><details><summary>Advanced evidence metadata</summary><code>{escape(o.original_id or o.record_id)}</code> · {escape(o.governance)}</details></article>"


def _navigation(run_id):
    r = escape(run_id)
    return f"<section class='secondary-actions'><a class='button primary' href='/blueprint-import/{r}/explore'>Browse full Twin</a><a href='/blueprint-import/{r}/health'>Twin Health</a></section>"


def _enterprise_completeness(ent: SemanticEnterprise, mission: CommercialMission | None) -> tuple[CompletenessAspect, ...]:
    """Deterministic presentation sufficiency; never a truth assessment."""
    records = ent.records
    kinds = {o.kind for o in records}
    identity = next((o for o in records if o.kind in {"enterprise", "enterprise_twin", "entity"}), None)
    overview = bool(identity and _field(identity, "description", "summary", "overview", "organisation_description"))
    domains = any(o.domains for o in records)
    financial = [o for o in records if o.kind in {"financial_observation", "financial_fact", "economic_pool"}]
    full_financial = any(all(_field(o, x) for x in ("metric", "value", "period", "source")) for o in financial)
    changes = [o for o in records if executive_insight_eligible(o)]
    programmes = [o for o in records if o.kind == "transformation_programme"]
    themes = [o for o in records if _reinvention_kind(o) and (o.evidence_refs or o.kind == "transformation_programme")]
    pressure = [o for o in themes if o.consequence and o.evidence_refs]
    procurements = [o for o in records if o.kind in {"procurement", "procurement_route", "buying_centre"} or _field(o, "procurement_route", "procuring_organisation")]
    opportunities = [o for o in records if "opportun" in o.kind]
    full_opportunity = any(o.statement and o.affected_organisations and _field(o, "client_problem", "customer_problem", "problem") and o.evidence_refs and (_field(o, "timing", "why_now", "deadline") or o.freshness == "unknown") for o in opportunities)
    relationships = [o for o in records if o.kind in {"relationship", "supplier_relationship"}]
    claims = [o for o in records if o.statement and o.kind != "evidence"]
    unknowns = [o for o in records if o.kind in {"unknown", "contradiction"}]
    def present(name, rows, missing):
        return CompletenessAspect(name, "Complete enough for executive use" if rows else "Insufficient", () if rows else (missing,))
    return (
        CompletenessAspect("Identity and overview", "Complete enough for executive use" if overview else "Partial", () if overview else ("Plain-language organisation description not structured",)),
        present("Domain association", domains, "No supported enterprise/domain association"),
        CompletenessAspect("Financials", "Complete enough for executive use" if full_financial else ("Partial" if financial or any("annual report" in o.statement.casefold() for o in records if o.kind == "evidence") else "Insufficient"), () if full_financial else ("Current measure, value, currency, period and source are not fully structured",)),
        present("Material changes", changes, "No observation satisfies the executive insight contract"),
        present("Transformation programmes", programmes, "No transformation programme is associated"),
        present("Reinvention themes", themes, "No supported reinvention classification is available"),
        present("Pressure and urgency", pressure, "No evidenced pressure with a supported consequence is available"),
        present("Known procurements", procurements, f"No explicit procurement, buying-centre or procurement-route record is associated with {ent.name}."),
        CompletenessAspect("Opportunities", "Complete enough for executive use" if full_opportunity else ("Partial" if opportunities else "Insufficient"), () if full_opportunity else ("Opportunity statement, affected enterprise, client problem, evidence and timing/timing gap are not all structured",)),
        present("Relationships", relationships, "No explicit relationship is associated"),
        CompletenessAspect("Evidence linkage", "Complete enough for executive use" if claims and all(o.evidence_refs for o in claims if o.kind not in {"unknown", "contradiction"}) else "Partial", tuple(f"Evidence not linked to {o.original_id or o.record_id}" for o in claims if not o.evidence_refs) or ("No linked claims",)),
        CompletenessAspect("Dates and freshness", "Complete enough for executive use" if records and all(o.freshness != "unknown" for o in claims) else "Partial", tuple(f"Date missing for {o.original_id or o.record_id}" for o in claims if o.freshness == "unknown")),
        CompletenessAspect("Contradictions and unknowns", "Complete enough for executive use" if unknowns and all(o.consequence and _field(o, "resolution", "evidence_needed") for o in unknowns) else ("Partial" if unknowns else "Insufficient"), () if unknowns else ("Unknowns and contradictions have not been assessed",)),
        CompletenessAspect("Commercial Mission relevance", "Partial" if mission else "Not applicable", ("Mission relevance is operational context and remains incomplete" if mission else "No Commercial Mission is available",)),
    )


def _completeness_html(ent: SemanticEnterprise, aspects: tuple[CompletenessAspect, ...]) -> str:
    rows = "".join(f"<tr><td>{escape(a.name)}</td><td>{escape(a.state)}</td><td>{escape('; '.join(a.missing) or 'No presentation gap')}</td></tr>" for a in aspects)
    return f"<section class='card' id='enterprise-completeness'><h2>Twin Completeness — {escape(ent.name)}</h2><p>This deterministic assessment measures structured presentation sufficiency, not truth. No aggregate score is calculated.</p><table><thead><tr><th>Aspect</th><th>State</th><th>Missing information</th></tr></thead><tbody>{rows}</tbody></table></section>"


def _researcher_feedback(twin: SemanticTwin) -> str:
    """Non-blocking diagnostics over immutable canonical records."""
    groups = {
        "Records unable to become insights": [o for o in twin.objects if o.kind in {"fact", "observation", "executive_intelligence"} and not executive_insight_eligible(o)],
        "Incomplete financial measures": [o for o in twin.objects if "Metric meaning" in o.exclusion_reason],
        "Missing dates": [o for o in twin.objects if o.freshness == "unknown"],
        "Claims without evidence": [o for o in twin.objects if o.statement and not o.evidence_refs and o.kind != "evidence"],
        "Evidence not linked to claims": [o for o in twin.objects if o.kind == "evidence" and not any(o.original_id in c.evidence_refs for c in twin.objects)],
        "Unresolved enterprise or domain association": [o for o in twin.objects if o.statement and (o.subject in {"", "Twin scope"} or not o.domains)],
    }
    sections = []
    for label, records in groups.items():
        if not records:
            continue
        entries = []
        for o in records[:20]:
            missing = []
            if o.subject in {"", "Twin scope"}: missing.append("subject")
            if not o.consequence: missing.append("business consequence")
            if not o.domains: missing.append("domain")
            if o.freshness == "unknown": missing.append("date")
            if not o.evidence_refs: missing.append("evidence reference")
            entries.append(f"<li><code>{escape(o.original_id or o.record_id)}</code>: {escape(', '.join(missing) or o.exclusion_reason or 'linkage requires review')}</li>")
        sections.append(f"<section><h3>{label} <span class='pill'>{len(records)}</span></h3><ul>{''.join(entries)}</ul></section>")
    enterprise_reports = []
    for ent in twin.enterprises:
        aspects = _enterprise_completeness(ent, None)
        gaps = "".join(f"<li><strong>{escape(a.name)}</strong> · {escape(a.state)}<br>{escape('; '.join(a.missing))}</li>" for a in aspects if a.state != "Complete enough for executive use")
        enterprise_reports.append(f"<details><summary>Twin → domain → {escape(ent.name)}</summary><ul>{gaps}</ul></details>")
    return "<section class='card' id='researcher-feedback'><h2>Researcher Feedback Report</h2><p>This advisory import diagnostic does not block import, mutate canonical records, resolve missing evidence or authorise promotion.</p><h3>Aspect-level enterprise feedback</h3>" + "".join(enterprise_reports) + "".join(sections) + "</section>"


def _health(twin: SemanticTwin, run_id: str, summary: dict) -> str:
    r = escape(run_id)
    return (f"<nav class='executive-path'><a href='/blueprint-import/{r}'>Twin overview</a><strong>Twin Health</strong></nav>"
            "<header class='hero'><h1>Twin Health</h1><p>Evidence, quality and governance are available here when deliberately requested.</p></header>"
            + _validation_report(twin) + _limitations(twin, summary, None, bool(twin.unresolved_references))
            + _attention(twin, run_id) + _reasoning_trace(twin, None) + _researcher_feedback(twin)
            + f"<section class='card'><h2>Candidate state and promotion readiness</h2><p>Candidate records remain separate from governed intelligence. No automatic promotion occurs.</p><a href='/blueprint-import/{r}/review'>Protected governance actions</a> · <a href='/blueprint-import/{r}/inspect'>Inspect evidence and import decisions</a></section>")


def _styles():
    return """<style>.compact-twin-header h1{font-size:clamp(1.35rem,3vw,2rem);display:flex;align-items:center;gap:.35rem;flex-wrap:wrap}.pilot-badge{font-size:.65em;letter-spacing:.08em;background:#f3c969;color:#302400;padding:.25rem .45rem;border-radius:.25rem}.executive-path,.domain-lenses,.secondary-actions{display:flex;gap:.65rem;flex-wrap:wrap;align-items:center;margin:1rem 0}.executive-path span,.executive-path a,.executive-path strong,.pill,.collection-chip,.domain-lens{padding:.45rem .7rem;border-radius:1rem;background:#eef5f2}.domain-lens.active{background:#185c4d;color:white}.composition-grid,.theme-grid,.enterprise-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem}.composition-tile,.theme-tile,.executive-conclusion,.enterprise-card{display:flex;flex-direction:column;gap:.5rem;padding:1rem;border:1px solid #cad8d3;border-radius:.7rem;text-decoration:none;color:inherit;background:#fffdf8}.composition-tile{min-height:9rem}.composition-tile:focus,.composition-tile:hover,.theme-tile:focus,.theme-tile:hover,.executive-conclusion:focus,.executive-conclusion:hover,.enterprise-card:focus,.enterprise-card:hover{outline:3px solid #185c4d}.composition-tile b,.theme-tile b{font-size:2rem}.insight-explanation{border-left:4px solid #185c4d;padding:1rem;margin:1rem 0}.collection-links{display:flex;gap:.6rem;flex-wrap:wrap}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:.6rem;border-bottom:1px solid #ddd}@media(max-width:600px){.composition-grid,.theme-grid,.enterprise-grid{grid-template-columns:1fr}.compact-twin-header h1{align-items:flex-start}}</style>"""
