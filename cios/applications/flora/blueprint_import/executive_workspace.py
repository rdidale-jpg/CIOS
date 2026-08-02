"""Mission-aware, evidence-governed projection over an imported candidate Twin."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from html import escape
from typing import Any
import json
import os
from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile

from cios.applications.flora.access import (COMMERCIAL_CONTEXT_EDIT, COMMERCIAL_CONTEXT_VIEW,
    can_access_enterprise, commercial_context_authorisation, commercial_context_owner)
from cios.applications.flora.pilot_import import PILOT_IMPORT_WORKSPACE, pilot_import_bypass_enabled
from cios.applications.flora.commercial_mission import (CommercialMission, EmployerContext,
    resolve_commercial_mission, resolve_employer_context, save_commercial_mission, save_employer_context)
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


@dataclass(frozen=True)
class ReadinessAspect:
    """A versioned, explainable presentation projection (never a quality score)."""
    key: str
    name: str
    state: str
    present: tuple[str, ...]
    missing: tuple[str, ...]
    affected: tuple[str, ...]
    next_requirement: str
    researcher_action: str
    rule_version: str = "executive-readiness-v1"

    @property
    def bars(self) -> int | None:
        return {"Absent": 0, "Insufficient": 1, "Partial": 2, "Usable": 3,
                "Executive-ready": 4}.get(self.state)


def _opportunity_contract(o: SemanticObject, mission: CommercialMission | None = None) -> tuple[bool, bool, list[str]]:
    customer = bool(o.affected_organisations or (o.subject and o.subject != "Twin scope"))
    problem = bool(_field(o, "client_problem", "customer_problem", "problem"))
    timing = bool(_field(o, "procurement_start", "expected_procurement_start", "procurement_timing", "timing_unknown"))
    status = bool(_field(o, "procurement_status", "status"))
    minimum = {"named customer": customer, "opportunity statement": bool(o.statement), "client problem": problem,
               "evidence": bool(o.evidence_refs), "procurement timing or explicit timing unknown": timing}
    usable = {**minimum, "confidence": o.confidence.casefold() not in {"", "unknown"}, "procurement status": status}
    if mission: usable["mission relevance"] = bool(_mission_relevance(o, mission)[0])
    return all(minimum.values()), all(usable.values()), [k for k, value in usable.items() if not value]


def _mission_relevance(o: SemanticObject, mission: CommercialMission) -> tuple[bool, str]:
    targets = {x.casefold() for x in (*mission.target_customers, *mission.priority_accounts,
                                     *mission.named_accounts, *mission.enterprises)}
    subjects = {o.subject.casefold(), *(x.casefold() for x in o.affected_organisations)}
    excluded = {x.casefold() for x in mission.excluded_accounts}
    if subjects & excluded: return False, "Excluded account: the customer is explicitly excluded by the selected mission."
    reasons = []
    matched = False
    if subjects & targets:
        matched = True; reasons.append("target account")
    domains = {d.casefold() for d in o.domains}
    industries = {x.casefold() for x in mission.industries}
    if domains & industries:
        matched = True; reasons.append("selected industry")
    text = " ".join((o.statement, o.consequence, o.kind, *o.domains)).casefold()
    focus_matches = [area for area in mission.interests if area.casefold() in text]
    if focus_matches:
        matched = True; reasons.append("selected focus area: " + ", ".join(focus_matches))
    horizon = mission.opportunity_horizon or mission.commercial_horizon
    timing = _field(o, "procurement_start", "expected_procurement_start", "procurement_timing", "timing", "expected_horizon")
    if horizon and timing and horizon.casefold() in timing.casefold():
        matched = True; reasons.append("commercial horizon")
    restricted = bool(targets or industries or mission.interests or horizon)
    if reasons:
        return True, "Relevant because: " + "; ".join(reasons) + "."
    if restricted:
        return False, "No configured target account, industry, focus area or commercial-horizon match."
    return True, "Neutral ordering: no account, industry, focus-area or horizon restriction is configured."


def twin_readiness(twin: SemanticTwin, mission: CommercialMission | None = None) -> tuple[ReadinessAspect, ...]:
    """Canonical six-aspect readiness result used by every presentation."""
    objects = twin.objects
    collections = {c.key: list(c.objects) for c in business_collections(twin, include_empty=True)}
    def ids(rows): return tuple(dict.fromkeys(o.original_id or o.record_id for o in rows))
    def result(key, name, rows, useful, state, count, explanation, missing, action):
        return ReadinessAspect(key, name, state, (count, explanation), tuple(missing), ids(rows),
                               "" if state == "Executive-ready" else action, action, "executive-readiness-v3")
    insights = collections.get("insights", [])
    enterprise_rows = collections.get("enterprises", [])
    participants = collections.get("market-participants", [])
    programmes = collections.get("transformation-programmes", [])
    opportunities = collections.get("opportunities", [])
    ready_opps = [o for o in opportunities if _opportunity_contract(o, mission)[1]]
    ready_enterprises = [o for o in enterprise_rows if _field(o, "description", "overview", "organisation_description") and o.domains and (_field(o, "current_position", "strategic_ambition", "market_position"))]
    classified = [o for o in participants if _field(o, "role", "participant_role", "market_role") and o.domains and o.evidence_refs and (o.consequence or _field(o, "why_it_matters"))]
    ready_programmes = [o for o in programmes if o.statement and (_field(o,"owner") or o.subject != "Twin scope") and o.consequence and _field(o,"phase","stage") and _field(o,"timing","expected_horizon") and o.evidence_refs]
    timing = [o for o in objects if _field(o, "reinvention_timing") or (_field(o, "expected_horizon") and _field(o, "tipping_point") and _field(o, "adoption_indicators") and o.evidence_refs)]
    overview_state = "Usable" if insights else "Absent"
    return (
      result("industry-overview", "Industry Overview", insights, insights, overview_state,
             f"{len(insights)} qualified insights", "Flora can partly explain evidenced change, but industry definition, composition, size, economics and a complete PESTLE outlook remain incomplete.",
             () if overview_state == "Executive-ready" else ("Industry definition and scope", "Composition and sub-sectors", "Industry size and economics", "Complete political, economic, social, technological, legal and environmental analysis"),
             "Research industry scope, sub-sector composition, size, economics, competitive structure and dated PESTLE evidence."),
      result("enterprises", "Enterprises", enterprise_rows, ready_enterprises, "Executive-ready" if enterprise_rows and len(ready_enterprises)==len(enterprise_rows) else "Insufficient" if enterprise_rows else "Absent",
             f"{len(enterprise_rows)} canonical enterprises · {len(ready_enterprises)} executive-ready enterprises", "Flora can identify the enterprises, but most profiles do not yet explain strategic position, material pressure and transformation posture.",
             () if enterprise_rows and len(ready_enterprises)==len(enterprise_rows) else ("Plain-language description, strategic position, material pressure and transformation posture",),
             "Research each enterprise's description, organisational form, activities, market role, strategic ambition, material pressure and transformation posture."),
      result("market-participants", "Market Participants", participants, classified, "Executive-ready" if participants and len(classified)==len(participants) else "Insufficient" if participants else "Absent",
             f"{len(participants)} participants identified · {len(classified)} sufficiently classified", "Flora can identify market participants, but supported roles and why each participant matters are incomplete.",
             () if participants and len(classified)==len(participants) else ("Supported role, domain and market significance for each participant",),
             "Research each participant's legitimate name, evidenced role, domain and reason it matters to the market."),
      result("major-programmes", "Major Programmes", programmes, ready_programmes, "Executive-ready" if programmes and len(ready_programmes)==len(programmes) else "Insufficient" if programmes else "Absent",
             f"{len(programmes)} programme hypotheses identified · {len(ready_programmes)} executive-ready programmes", "Flora can identify programme hypotheses, but ownership, objective, phase, timing or evidence is incomplete.",
             () if programmes and len(ready_programmes)==len(programmes) else ("Programme title, owner, business objective, phase, timing and evidence",),
             "Research each programme's meaningful title, owner, business objective, current phase, timing and supporting evidence."),
      result("opportunities", "Opportunities", opportunities, ready_opps, "Executive-ready" if opportunities and len(ready_opps)==len(opportunities) else "Insufficient" if opportunities else "Absent",
             f"{len(opportunities)} canonical opportunity hypotheses · {len(ready_opps)} sales-ready opportunities", "Flora can identify opportunity hypotheses, but they cannot support sales action until customer, problem, buyer, value, timing, status and evidence are resolved.",
             () if opportunities and len(ready_opps)==len(opportunities) else ("Customer, client problem, business unit, buyer, value, timing, status and evidence",),
             "Research customer, client problem, business unit, buyer, value, timing, status and supporting evidence."),
      result("reinvention-timing", "Reinvention Timing", timing, timing, "Executive-ready" if timing else "Absent",
             f"{len(timing)} supported assessments", "This Twin contains no structured assessment of AI-native disruption, exposure, adoption indicators, expected horizon or response timing." if not timing else "Flora can explain supported disruption exposure and response timing.",
             () if timing else ("AI-native disruption mechanism", "Enterprise or business-unit exposure", "Adoption indicators", "Expected horizon", "Response timing"),
             "Research the disruption mechanism, affected enterprise or business unit, adoption indicators, expected horizon, response timing and supporting evidence."),
    )


def executive_workspace_page(import_run_id: str, headers: Any, *, view: str = "workspace",
                             enterprise_id: str = "", collection: str = "", domain: str = "all") -> tuple[str, int]:
    package = next((p for p in BlueprintPackageRegistry().list() if p.import_run_id == import_run_id), None)
    if package is None:
        return _page("Executive Intelligence Workspace unavailable", "<section class='hero'><h1>Executive Intelligence Workspace unavailable</h1><p>The import record could not be found.</p></section>"), 404
    if view == "mission":
        context_scope = commercial_context_owner(headers)
        decision = commercial_context_authorisation(headers, COMMERCIAL_CONTEXT_VIEW, context_scope)
        if decision.decision != "allowed":
            return _commercial_access_denied(decision, headers), 403
    bypass_candidate_read = pilot_import_bypass_enabled() and view in {"workspace", "explore", "enterprise", "health", "aspect", "diagnostics", "mission"}
    if not bypass_candidate_read and (not can_access_enterprise(headers, package.identity.enterprise_id, package.workspace_id) or not can_inspect_blueprint_package(headers, package)):
        return _page("Access denied", "<section class='hero'><h1>Access denied</h1></section>"), 403
    summary = BlueprintPackageValidator().staging_summary(import_run_id) or {}
    candidates = _semantic_candidates(package, list(summary.get("candidates") or ()))
    twin = assemble_semantic_twin(candidates)
    mission = resolve_commercial_mission(headers)
    employer_context = resolve_employer_context(headers)
    inspection = package.package_inspection or {}
    identity = project_twin_identity(package)
    title = str(inspection.get("twin_title") or inspection.get("package_title") or identity.primary_subject_name or package.identity.package_id)
    if view == "explore":
        return _page(f"Explore Twin — {title}", _styles() + _explorer(twin, import_run_id, mission, collection, domain)), 200
    if view == "health":
        return _page(f"Research Gaps — {title}", _styles() + _research_gaps(twin, import_run_id, mission)), 200
    if view == "diagnostics":
        return _page(f"Advanced diagnostics — {title}", _styles() + _advanced_diagnostics(twin, import_run_id, summary, mission)), 200
    if view == "aspect":
        return _page(f"{collection.replace('-', ' ').title()} — {title}", _styles() + _aspect_page(twin, import_run_id, title, collection, domain, mission)), 200
    if view == "enterprise":
        ent = next((e for e in twin.enterprises if e.identity_key == enterprise_id), None)
        if ent is None:
            return _page("Enterprise dossier unavailable", "<section class='hero'><h1>Enterprise dossier unavailable</h1></section>"), 404
        return _page(f"Enterprise Intelligence — {ent.name}", _styles() + _dossier(ent, twin, import_run_id, mission)), 200
    if view == "mission":
        return _page("Configure Commercial Mission", _styles() + _mission_editor(mission, employer_context, import_run_id, domain)), 200
    body = _styles() + _hero(title) + _primary_nav(import_run_id, "map") + _mission_indicator(mission, employer_context, import_run_id, domain)
    if not twin.enterprises:
        body += f"<aside class='mission-indicator' role='status'>Twin identity and governed scope have not yet been confirmed. Resolve Twin scope through <a href='/blueprint-import/{escape(import_run_id)}/review'>Review candidate governance</a>. <a href='/blueprint-import/{escape(import_run_id)}/inspect'>Inspect import decisions</a>. <a href='/blueprint-import/{escape(import_run_id)}/validation'>View package validation</a>.</aside>"
    body += _domain_lenses(import_run_id, domain) + _twin_map(twin, import_run_id, mission, domain)
    body += _navigation(import_run_id)
    html = _page(f"Executive Intelligence — {title}", body)
    product_nav = "<nav class='nav'><a href='/'>Executive Brief</a><a href='/observatory'>Observatory</a><a href='/radar'>Portfolio</a><a href='/live'>Evidence</a><a href='/digital-twins'>Digital Twins</a><a href='/financial-intelligence'>Financial Intelligence</a><a href='/observatory/critique'>Research</a><a href='/settings'>Settings</a><a href='/logbook' hidden>Learning / Logbook</a><a href='/financial-reports' hidden>Collect Financial Report</a></nav>"
    html = html.replace(product_nav, "<header class='product-header'><a href='/digital-twins'>Flora</a></header>", 1)
    return html, 200


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
    return f"<header class='compact-twin-header'><p>Executive Intelligence Workspace</p><h1><span class='pilot-badge'>PILOT</span><span aria-hidden='true'> · </span>{escape(title)}</h1></header>"


def _mission_indicator(mission: CommercialMission | None, employer: EmployerContext | None, run_id: str, domain: str = "all") -> str:
    target = f"/blueprint-import/{escape(run_id)}/mission?domain={escape(domain)}"
    if not mission:
        employer_state = "Configured" if employer and employer.complete else "Partially configured" if employer else "Not configured"
        return f"<aside class='mission-indicator' role='status'><strong>PILOT · Commercial Mission not configured</strong> — no Commercial Mission is available · Employer Context: {employer_state} · neutral industry composition applies · <a href='{target}'>Configure</a></aside>"
    status = "Configured" if mission.mission_name and mission.executive_role and mission.commercial_objective and mission.industries and (mission.priority_accounts or mission.target_customers) else "Partially configured"
    name = mission.mission_name or "Unnamed mission"
    employer_state = "Configured" if employer and employer.complete else "Partially configured" if employer else "Not configured"
    return f"<aside class='mission-indicator' role='status'><strong>PILOT · Commercial Mission: {escape(name)}</strong> · {status} · Employer Context: {employer_state} · Commercial context saved. · <a href='{target}'>Select or edit</a></aside>"


def _bars(a: ReadinessAspect, run_id: str) -> str:
    if a.bars is None:
        return f"<span class='readiness-label'>Not applicable</span>"
    bars = "".join(f"<i class='{'filled' if i <= a.bars else ''}' aria-hidden='true'></i>" for i in range(1, 5))
    return f"<a class='readiness' href='/blueprint-import/{escape(run_id)}/health#{escape(a.key)}' aria-label='{escape(a.name)}: {escape(a.state)}, {a.bars} of 4 bars'>{bars}<span>{escape(a.state)}</span></a>"


def _readiness_review(twin: SemanticTwin, run_id: str, mission: CommercialMission | None) -> str:
    rows = "".join(f"<article><h3>{escape(a.name)}</h3>{_bars(a, run_id)}</article>" for a in twin_readiness(twin, mission))
    return f"<section class='card' id='twin-readiness'><h2>Twin Readiness</h2><p>Deterministic fitness for executive interpretation; not a truth or quality score.</p><div class='readiness-grid'>{rows}</div><p><a class='button primary' href='#opportunities'>Open Executive Experience</a> <a class='button' href='/blueprint-import/{escape(run_id)}/health#researcher-feedback'>Review Research Gaps</a></p></section>"


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
    ready = [o for o in rows if _opportunity_contract(o, mission)[1]]
    label = "Opportunities for you" if mission else "Commercial Opportunities"
    if not ready:
        problems = sorted({_field(o, "client_problem", "customer_problem", "problem") for o in rows} - {""})
        known = f"<p><strong>Known client-problem context:</strong> {escape('; '.join(problems))}</p>" if problems else ""
        return f"<section class='card' id='opportunities'><h2>{label}</h2><p><strong>{len(rows)} canonical opportunity hypotheses · 0 sales-ready opportunities</strong></p><p><strong>{'Absent' if not rows else 'Insufficient'}.</strong> No sales-ready opportunity is currently supported.</p>{known}<h3>Developing hypotheses</h3><p>{len(rows)} hypotheses require further research.</p><p><strong>Research required:</strong> customer, client problem, business unit, buyer, value, timing, status and evidence.</p><a href='/blueprint-import/{escape(run_id)}/explore?collection=opportunities&amp;domain={escape(domain)}'>Inspect incomplete records in Advanced Inspection</a></section>"
    def cell(o):
        customer = ", ".join(o.affected_organisations) or o.subject
        unit = _field(o, "business_unit")
        value = _field(o, "value", "value_range") or "Not established"
        timing = _field(o, "procurement_start", "expected_procurement_start", "procurement_timing") or "Timing unknown"
        status = _field(o, "procurement_status", "status") or "Timing unknown"
        cls = " class='procurement-active'" if status.casefold() == "procurement active" else ""
        rationale = _mission_relevance(o, mission)[1] if mission else "Neutral presentation; Commercial Mission not configured."
        return f"<tr><td>{escape(customer)}{('<br><small>'+escape(unit)+'</small>') if unit else ''}</td><td>{escape(o.statement)}</td><td>{escape(value)}</td><td>{escape(timing)}</td><td{cls}>{escape(status)}<details><summary>Why relevant?</summary>{escape(rationale)}</details></td></tr>"
    if mission: ready.sort(key=lambda o: (not _mission_relevance(o, mission)[0], o.statement.casefold()))
    incomplete = len(rows) - len(ready)
    return f"<section class='card' id='opportunities'><h2>{label}</h2><p><strong>{len(rows)} canonical opportunity hypotheses · {len(ready)} sales-ready opportunities</strong></p><table class='opportunity-table'><thead><tr><th>Customer</th><th>Opportunity</th><th>Value</th><th>Timing</th><th>Status</th></tr></thead><tbody>{''.join(cell(o) for o in ready)}</tbody></table><h3>Developing hypotheses</h3><p>{incomplete} hypotheses require further research.</p><a href='/blueprint-import/{escape(run_id)}/explore?collection=opportunities&amp;domain={escape(domain)}'>Inspect canonical records in Advanced Inspection</a></section>"


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
    identity = next((o for o in e.records if o.kind in {"enterprise", "enterprise_twin", "entity"}), None)
    domains = sorted({d.title() for o in e.records for d in o.domains})
    description = _field(identity, "organisation_description", "description", "overview", "summary") if identity else ""
    position = _field(identity, "strategic_ambition", "market_position", "current_position") if identity else ""
    pressure = next((o.consequence for o in e.records if o.consequence and o.evidence_refs), "")
    posture = _field(identity, "transformation_posture") if identity else ""
    complete = bool(description and position and pressure and posture)
    body = (f"<p>{escape(description)}</p><p><strong>Industry/domain:</strong> {escape(', '.join(domains) or 'Not established')}</p>"
            f"<p><strong>Strategic position:</strong> {escape(position)}</p><p><strong>Material pressure:</strong> {escape(pressure)}</p>"
            f"<p><strong>Transformation posture:</strong> {escape(posture)}</p>" if complete else
            f"<p><strong>Enterprise profile incomplete</strong></p><p>{escape(description or 'A plain-language organisation description is not supplied.')} Strategic position, material pressure or transformation posture requires supported research.</p><p><strong>Industry/domain:</strong> {escape(', '.join(domains) or 'Not established')}</p>")
    return f"<a class='enterprise-card' href='/blueprint-import/{escape(run_id)}/enterprises/{escape(e.identity_key)}'><h3>{escape(e.name)}</h3>{body}<p class='pill'>Enterprise intelligence readiness: {'Executive-ready' if complete else 'Insufficient'}</p></a>"


def _validation_report(twin: SemanticTwin) -> str:
    counts = Counter(o.kind for o in twin.objects)
    evidenced = sum(bool(o.evidence_refs) for o in twin.objects)
    claims = [o for o in twin.objects if o.eligible_conclusion]
    unused_evidence = sum(o.kind == "evidence" and not any(o.original_id in c.evidence_refs for c in claims) for o in twin.objects)
    rows = "".join(f"<tr><td>{escape(kind)}</td><td>{count}</td></tr>" for kind, count in sorted(counts.items()))
    capabilities = ", ".join(o.statement for o in twin.objects if o.kind == "capability_offer" and o.statement) or "none supplied"
    return f"""<section class='card' id='package-validation'><h2>Deterministic package validation</h2><p><strong>Canonical priority enterprises: {len(twin.enterprises)}</strong> · Market Participants: {counts['market_participant_twin']} · Capabilities/offers: {counts['capability_offer']} · Opportunities: {counts['opportunity_hypothesis']} · Evidence: {counts['evidence']} · Unknowns: {counts['unknown']} · Contradictions: {counts['contradiction']}</p><p><strong>Capabilities and offers (not enterprises):</strong> {escape(capabilities)}</p><p>Evidence-reference coverage: {evidenced}/{len(twin.objects)} objects · Claims without evidence: {sum(not o.evidence_refs for o in claims)} · Evidence without claims: {unused_evidence} · Missing dates: {sum(o.freshness == 'unknown' for o in twin.objects)} · Unresolved references: {len(twin.unresolved_references)}</p><details><summary>Counts by canonical/runtime type and unresolved IDs</summary><table><tbody>{rows}</tbody></table><p>{escape(', '.join(twin.unresolved_references) or 'No unresolved canonical references')}</p></details></section>"""


def _mission_editor(m: CommercialMission | None, employer: EmployerContext | None, run_id: str, domain: str = "all") -> str:
    def value(name):
        raw = getattr(m, name) if m else ""
        return escape(", ".join(raw) if isinstance(raw, tuple) else raw)
    def employer_value(name):
        raw = getattr(employer, name) if employer else ""
        return escape(", ".join(raw) if isinstance(raw, tuple) else raw)
    def choices(name, legend, options, selected):
        selected_folded = {item.casefold() for item in selected}
        controls = "".join(
            f"<label class='choice'><input type='checkbox' name='{name}' value='{escape(option)}'"
            f"{' checked' if option.casefold() in selected_folded else ''}> <span>{escape(option)}</span></label>"
            for option in options)
        # Previously saved free-form values remain editable and are never discarded.
        extras = [item for item in selected if item.casefold() not in {option.casefold() for option in options}]
        controls += "".join(f"<label class='choice'><input type='checkbox' name='{name}' value='{escape(item)}' checked> <span>{escape(item)}</span></label>" for item in extras)
        return f"<fieldset class='choice-group'><legend>{legend}</legend><div class='choice-grid'>{controls}</div></fieldset>"

    objectives = ("Client transformation problems", "Pre-procurement opportunities", "Active procurements",
                  "AI-led reinvention", "Major transformation programmes", "Competitor activity", "Partner opportunities")
    focus_areas = ("Consulting", "Digital transformation", "Outsourcing", "AI", "Cloud", "Data", "Managed services")
    selected_objectives = tuple(m.objectives) if m else ()
    selected_focus = tuple(m.interests) if m else ()
    primary = m.commercial_objective if m else ""
    objective_options = "<option value=''>Select what matters most</option>" + "".join(
        f"<option value='{escape(option)}'{' selected' if option == primary else ''}>{escape(option)}</option>" for option in objectives)
    if primary and primary not in objectives:
        objective_options += f"<option value='{escape(primary)}' selected>{escape(primary)}</option>"

    advanced_names = ("description", "propositions", "target_sectors", "credentials", "constraints", "excluded_offerings")
    advanced_open = bool(employer and any(getattr(employer, name) for name in advanced_names))
    advanced = "".join(
        f"<label>{label}<span class='optional'>Optional</span><input name='employer_{name}' value='{employer_value(name)}'></label>"
        for name, label in (("description", "Employer description"), ("propositions", "Propositions"),
            ("target_sectors", "Target sectors"), ("credentials", "Reference credentials"),
            ("constraints", "Delivery constraints"), ("excluded_offerings", "Excluded or unsupported offerings")))

    any_context = bool(m or employer)
    mission_ready = bool(m and m.executive_role and m.commercial_objective and m.geography and m.commercial_horizon)
    status = "Configured" if mission_ready and employer and employer.complete else "Partially configured" if any_context else "Not configured"
    back = f"/blueprint-import/{escape(run_id)}?domain={escape(domain)}"
    return f"""<style>
.guided-setup{{max-width:900px;margin-inline:auto}}.setup-status{{display:flex;justify-content:space-between;gap:1rem;align-items:center;padding:1rem;border-left:4px solid #185c4d;background:#eef5f2}}.setup-section{{margin:1rem 0;padding:1.25rem;border:1px solid #cad8d3;border-radius:.7rem}}.setup-section>h2{{margin-top:0}}.setup-section label:not(.choice){{display:block;font-weight:700;margin:.9rem 0}}.setup-section input[type=text],.setup-section input:not([type]),.setup-section select{{box-sizing:border-box;display:block;width:100%;margin-top:.35rem;padding:.7rem;border:1px solid #718078;border-radius:.35rem;background:white}}.field-help{{display:block;font-weight:400;color:#46534d;margin-top:.25rem}}.optional{{font-size:.8rem;font-weight:400;margin-left:.45rem}}.choice-group{{border:0;padding:0;margin:1rem 0}}.choice-group legend{{font-weight:700;margin-bottom:.5rem}}.choice-grid{{display:flex;flex-wrap:wrap;gap:.55rem}}.choice{{display:flex;align-items:center;gap:.35rem;padding:.55rem .7rem;border:1px solid #879a91;border-radius:1.25rem;background:#fff}}.flora-use{{padding:1rem;border-radius:.7rem;background:#f3f7f5}}.form-actions{{display:flex;gap:.7rem;align-items:center;margin-top:1.2rem}}details.setup-section summary{{cursor:pointer;font-weight:700}}@media(max-width:600px){{.guided-setup{{padding:0 .25rem}}.setup-status{{align-items:flex-start;flex-direction:column}}.form-actions{{align-items:stretch;flex-direction:column}}.form-actions .button{{text-align:center}}}}
</style><nav class='executive-path'><a href='{back}'>Back to Twin Map</a><strong>Commercial context</strong></nav><main class='guided-setup'><header><h1>Set up my commercial context</h1><p>Tell Flora what matters to you. Required fields are marked; everything else can be added later. Your Commercial Mission and Employer Context remain separate settings.</p></header><aside class='setup-status' role='status' aria-label='Commercial context status'><strong>Commercial context</strong><span>{status}</span></aside>
<section class='flora-use' aria-labelledby='flora-use-title'><h2 id='flora-use-title'>How Flora will use this</h2><p>Flora will use these settings to prioritise relevant enterprises, opportunities, programmes, competitors, partners and research gaps.</p><p>These settings influence relevance and ordering. They do not change the Twin, its evidence or its confidence.</p></section>
<form method='post' action='/blueprint-import/{escape(run_id)}/mission'><input type='hidden' name='return_domain' value='{escape(domain)}'><input type='hidden' name='save_scope' value='both'><input type='hidden' name='target_customers' value='{value('target_customers')}'><input type='hidden' name='excluded_accounts' value='{value('excluded_accounts')}'><input type='hidden' name='relevant_business_units' value='{value('relevant_business_units')}'><input type='hidden' name='account_focus' value='{value('account_focus')}'>
<section class='setup-section' aria-labelledby='about-me'><h2 id='about-me'>1. About me</h2><p>This gives Flora the essentials it needs to tailor your experience.</p><label>My role <span aria-label='required'>*</span><input name='executive_role' value='{value('executive_role')}' placeholder='Sales Director' required><small class='field-help'>Example: Sales Director</small></label><label>I work for <span aria-label='required'>*</span><input name='employer_organisation' value='{employer_value('organisation')}' placeholder='Your organisation' required><small class='field-help'>Enter your employer; Flora will not infer services or relationships from its name.</small></label><label>My geography <span aria-label='required'>*</span><input name='geography' value='{value('geography')}' placeholder='United Kingdom' required><small class='field-help'>The markets or regions you cover.</small></label><label>My commercial horizon <span aria-label='required'>*</span><select name='commercial_horizon' required><option value=''>Not selected</option>{''.join(f"<option value='{escape(option)}'{' selected' if option == (m.commercial_horizon if m else '') else ''}>{escape(option)}</option>" for option in ('Next 12 months', '12–24 months', 'Strategic'))}{f"<option value='{value('commercial_horizon')}' selected>{value('commercial_horizon')}</option>" if m and m.commercial_horizon and m.commercial_horizon not in ('Next 12 months', '12–24 months', 'Strategic') else ''}</select><small class='field-help'>Example: Next 12 months, 12–24 months, strategic</small></label></section>
<section class='setup-section' aria-labelledby='help-find'><h2 id='help-find'>2. What I want Flora to help me find</h2><label>My main objective <span aria-label='required'>*</span><select name='commercial_objective' required>{objective_options}</select><small class='field-help'>Choose the outcome Flora should prioritise first.</small></label>{choices('objectives', 'Other commercial objectives (optional)', objectives, selected_objectives)}{choices('interests', 'Focus areas (optional)', focus_areas, selected_focus)}</section>
<section class='setup-section' aria-labelledby='my-context'><h2 id='my-context'>3. My commercial context</h2><p>Optional details make matching more precise; blank fields will not block saving.</p><label>Mission name <span class='optional'>Optional</span><input name='mission_name' value='{value('mission_name')}' placeholder='A short name for this context'></label><label>Industries <span class='optional'>Optional</span><input name='industries' value='{value('industries')}' placeholder='Media, telecommunications'><small class='field-help'>Add the industries you want Flora to prioritise.</small></label><label>Priority customers <span class='optional'>Optional</span><input name='priority_accounts' value='{value('priority_accounts')}' placeholder='BT Group, BBC, ITV'><small class='field-help'>Optional — add named accounts where useful. Example: BT Group, BBC, ITV</small></label><label>Relevant capabilities or services <span class='optional'>Optional</span><input name='employer_capabilities' value='{employer_value('capabilities')}' placeholder='Digital transformation, cloud, data, AI, managed services'><small class='field-help'>Optional — add the services or capability areas you want Flora to match.</small></label><label>Competitors <span class='optional'>Optional</span><input name='employer_competitors' value='{employer_value('competitors')}' placeholder='Accenture, Capgemini, IBM'><small class='field-help'>Optional — add organisations you want Flora to monitor.</small></label><label>Partners <span class='optional'>Optional</span><input name='employer_partners' value='{employer_value('partners')}' placeholder='Named strategic partners'><small class='field-help'>Optional — add organisations you work with.</small></label><input type='hidden' name='employer_offer_portfolio' value='{employer_value('offer_portfolio')}'></section>
<details class='setup-section'{' open' if advanced_open else ''}><summary>More employer settings</summary><p>Optional information for more precise employer alignment. It remains separate from Twin evidence.</p>{advanced}</details>
<div class='form-actions'><button class='button primary' type='submit'>Save and return to Twin Map</button><a class='button' href='{back}'>Cancel</a></div></form></main>"""


def update_commercial_mission(import_run_id: str, headers: Any, form: dict[str, list[str]]) -> tuple[str, int]:
    package = next((p for p in BlueprintPackageRegistry().list() if p.import_run_id == import_run_id), None)
    if package is None:
        return _page("Commercial context unavailable", "<h1>Commercial context unavailable</h1>"), 404
    context_scope = commercial_context_owner(headers)
    decision = commercial_context_authorisation(headers, COMMERCIAL_CONTEXT_EDIT, context_scope)
    if decision.decision != "allowed":
        return _commercial_access_denied(decision, headers), 403
    # Checkbox groups submit repeated keys; retain every selection while keeping
    # the established comma-separated contract compatible with older clients.
    values = {key: (items if len(items) > 1 else (items[0] if items else "")) for key, items in form.items()}
    for key in ("industries", "geography", "named_accounts", "campaigns", "interests", "target_customers",
                "priority_accounts", "excluded_accounts", "relevant_business_units", "objectives"):
        raw_items = values.get(key, "")
        source = raw_items if isinstance(raw_items, list) else str(raw_items).split(",")
        values[key] = [item.strip() for item in source if item.strip()]
    values.update(authority_status="human-supplied operational context", supplied_by="authenticated user profile edit")
    scope = values.get("save_scope") or "both"
    try:
        if scope in {"mission", "both"}:
            save_commercial_mission(headers, values)
        if scope in {"employer", "both"}:
            employer_values = {key.removeprefix("employer_"): value for key, value in values.items() if key.startswith("employer_")}
            for key in ("offer_portfolio", "capabilities", "propositions", "competitors", "partners", "target_sectors",
                        "credentials", "constraints", "excluded_offerings"):
                employer_values[key] = [item.strip() for item in str(employer_values.get(key, "")).split(",") if item.strip()]
            employer_values["authority_status"] = "human-supplied"
            save_employer_context(headers, employer_values)
    except PermissionError:
        return _page("Access denied", "<h1>Access denied</h1>"), 403
    except ValueError as exc:
        current_mission = resolve_commercial_mission(headers)
        current_employer = resolve_employer_context(headers)
        form_html = _mission_editor(current_mission, current_employer, import_run_id, str(values.get("return_domain") or "all"))
        return _page("Settings not saved", _styles() + f"<aside class='mission-indicator' role='alert'><strong>Settings not saved:</strong> {escape(str(exc))}</aside>" + form_html), 400
    domain = str(values.get("return_domain") or "all")
    return f"/blueprint-import/{import_run_id}?domain={domain}", 303


def _commercial_access_denied(decision, headers: Any) -> str:
    correlation = str(headers.get("X-Request-Id") or f"flora-{uuid4().hex}")
    body = ("<section class='hero'><h1>Access denied</h1><p>Commercial context configuration is unavailable.</p></section>"
            f"<section class='card'><h2>Access diagnostic</h2><ul><li>Resolved actor: {escape(decision.actor_id or 'unresolved')}</li>"
            f"<li>Context scope: {escape(decision.context_scope or 'unresolved')}</li><li>Required capability: <code>{escape(decision.required_capability)}</code></li>"
            f"<li>Scope class: {escape(decision.scope_class)}</li><li>Expected scope class: {escape(decision.expected_scope_class)}</li>"
            f"<li>Decision: {escape(decision.decision)}</li><li>Failed stage: {escape(decision.failed_stage)}</li>"
            f"<li>Denial reason: {escape(decision.denial_reason)}</li>"
            f"<li>Correlation ID: {escape(correlation)}</li></ul></section>")
    return _page("Access denied", body)


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
    items = (["Twin identity and governed scope have not yet been confirmed"] if unresolved else []) + (["Commercial Mission is unavailable"] if not mission else [])
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
    title = active.label if active else "Advanced Inspection"
    total = len(active.objects) if active else 0
    return f"<nav class='executive-path'><a href='/blueprint-import/{escape(run_id)}'>Back to Twin Map</a><strong>Advanced Inspection</strong></nav><header class='hero'><h1>Advanced Inspection</h1><p>{escape(active.description) if active else 'Inspect canonical records, evidence, relationships, unknowns, contradictions and technical diagnostics.'}</p></header><section class='card'><h2>Technical collections</h2><div class='collection-links'>{links}</div></section><section class='card'><h2>{escape(title)}{f' — {total} total' if active else ''}</h2><p>{f'Showing {total} distinct identities' if active and active.key == 'enterprises' else f'Showing {total} of {total} total records' if active else ''}</p>{content}</section><details class='card'><summary>Advanced aspect coverage</summary><table><thead><tr><th>Aspect</th><th>Objects</th><th>Governance</th><th>Evidence coverage</th><th>Unresolved</th></tr></thead><tbody>{aspects}</tbody></table></details>"


def _dossier(ent, twin, run_id, mission):
    relevant = list(ent.records)
    identity = next((o for o in relevant if o.kind in {"enterprise", "enterprise_twin", "entity"}), None)
    description = _field(identity, "organisation_description", "overview", "description", "summary") if identity else ""
    domains = sorted({d.title() for o in relevant for d in o.domains})
    missing_overview = [label for label, value in (("plain-language description", description),
        ("ownership or organisational form", _field(identity, "ownership", "organisational_form") if identity else ""),
        ("principal activities", _field(identity, "principal_activities", "activities") if identity else ""),
        ("industry role", _field(identity, "industry_role", "role") if identity else ""),
        ("material current position", _field(identity, "current_position") if identity else "")) if not value]
    if missing_overview:
        overview = f"<p><strong>Organisation overview incomplete</strong></p><p>Research required: {escape(', '.join(missing_overview))}.</p>"
        hero = "Organisation overview incomplete"
    else:
        overview = f"<p>{escape(description)}</p><p><strong>Organisational form:</strong> {escape(_field(identity, 'ownership', 'organisational_form'))}</p><p><strong>Principal activities:</strong> {escape(_field(identity, 'principal_activities', 'activities'))}</p><p><strong>Role in industry:</strong> {escape(_field(identity, 'industry_role', 'role'))}</p><p><strong>Current position:</strong> {escape(_field(identity, 'current_position'))}</p>"
        hero = description
    overview += f"<p><strong>Domain:</strong> {escape(', '.join(domains) or 'Not established')}</p><p><strong>Completeness:</strong> {len(missing_overview)} organisation overview requirement(s) unresolved.</p>"
    def gap(title, exists, fields, why):
        return f"<section class='card'><h2>{title}</h2><p><strong>Insufficient</strong></p><p>{exists}</p><p>{why}</p><p><strong>Research required:</strong> {', '.join(fields)}.</p></section>"
    sections = [f"<section class='card' id='enterprise-overview'><h2>Organisation Overview</h2>{overview}</section>"]
    position = _field(identity, "strategic_ambition", "market_position", "current_position") if identity else ""
    sections.append(f"<section class='card'><h2>Strategic Position and Ambition</h2><p>{escape(position)}</p></section>" if position else gap("Strategic Position and Ambition", "No supported strategic position is supplied.", ("strategic ambition", "market position", "supporting evidence"), "Without it Flora cannot explain the organisation's direction."))
    financials=[o for o in relevant if o.kind in {"financial_observation","financial_fact","economic_pool"} and all((_field(o,'metric','measure'),_field(o,'value'),_field(o,'period'),_field(o,'source')))]
    sections.append("<section class='card'><h2>Financial Position</h2>"+"".join(f"<p><strong>{escape(_field(o,'metric','measure'))}:</strong> {escape(_field(o,'value'))} · {escape(_field(o,'period'))} · {escape(_field(o,'source'))}</p>" for o in financials)+"</section>" if financials else gap("Financial Position", "No complete financial measure is supplied.", ("measure", "value and currency", "period", "source", "business interpretation"), "Financial position cannot be assessed from an evidence record alone."))
    pressures=_pressure_items(twin,run_id,enterprise=ent.name)
    sections.append("<section class='card'><h2>Material Pressures</h2>"+"".join(pressures)+"</section>" if pressures else gap("Material Pressures", "No evidenced pressure with a business consequence is supplied.", ("pressure", "business consequence", "timing", "evidence"), "The most material challenge cannot be explained."))
    programmes=[o for o in relevant if o.kind=='transformation_programme']; ready_programmes=[o for o in programmes if o.statement and o.consequence and _field(o,'stage','phase') and _field(o,'timing','expected_horizon') and o.evidence_refs]
    sections.append("<section class='card'><h2>Major Programmes</h2>"+"".join(f"<h3>{escape(o.statement)}</h3><p>{escape(o.consequence)}</p>" for o in ready_programmes)+"</section>" if ready_programmes else gap("Major Programmes", f"{len(programmes)} candidate record(s) are associated, but none is executive-ready.", ("meaningful title", "objective", "phase", "timing", "evidence"), "Incomplete programme hypotheses cannot support executive decisions."))
    procurements=[o for o in relevant if o.kind in {"procurement","procurement_route","buying_centre"} or _field(o,'procurement_route','procuring_organisation')]
    ready_proc=[o for o in procurements if (o.statement or _field(o,'requirement')) and _field(o,'stage','status') and _field(o,'timing','procurement_date') and _field(o,'buyer') and _field(o,'value') and _field(o,'award_status','supplier_outcome')]
    sections.append("<section class='card'><h2>Known Procurements</h2>"+"".join(_procurement_item(o,ent.name) for o in ready_proc)+"</section>" if ready_proc else gap("Known Procurements", f"{len(procurements)} candidate record(s) are associated with {escape(ent.name)}, but none identifies every mandatory procurement fact.", ("procurement description", "stage", "planned or actual start", "buyer", "value", "award or supplier outcome"), "The records cannot establish a live buying event."))
    sections.append(gap("Reinvention Timing", "No supported enterprise timing assessment is supplied.", ("AI-native disruption mechanism", "exposure", "adoption indicators", "horizon", "response timing"), "Response urgency cannot be assessed."))
    opportunities=[o for o in relevant if 'opportun' in o.kind]; ready_opps=[o for o in opportunities if _opportunity_contract(o,mission)[1]]
    sections.append("<section class='card'><h2>Opportunities</h2>"+"".join(_opportunity_card(o,run_id) for o in ready_opps)+"</section>" if ready_opps else gap("Opportunities", f"{len(opportunities)} hypothesis record(s) are associated with {escape(ent.name)}, but none is sales-ready.", ("customer", "client problem", "business unit", "buyer", "value", "timing", "status", "evidence"), "Incomplete hypotheses cannot support sales action."))
    sources=[o for o in relevant if o.kind=='evidence']
    sections.append("<section class='card'><h2>Key Sources</h2>"+("".join(_source_item(o) for o in sources) if sources else "<p><strong>Insufficient.</strong> No directly linked sources are supplied.</p>")+"</section>")
    sections.append(f"<section class='card'><h2>Research Gaps</h2><p>The same completeness requirements shown above define the researcher brief.</p><a href='/blueprint-import/{escape(run_id)}/health'>Open Research Gaps</a></section>")
    sections.append(f"<section class='card'><h2>Advanced Inspection</h2><p>Incomplete records, evidence, lineage and candidate governance remain inspectable.</p><a href='/blueprint-import/{escape(run_id)}/explore'>Open Advanced Inspection</a></section>")
    return _primary_nav(run_id, "")+f"<header class='hero'><h1>{escape(ent.name)}</h1><p>{escape(hero)}</p></header>"+"".join(sections)

def _procurement_item(o: SemanticObject, enterprise: str) -> str:
    return f"<article><h3>{escape(o.statement or _field(o, 'requirement', 'programme'))}</h3><p><strong>Procuring organisation:</strong> {escape(_field(o, 'procuring_organisation') or enterprise)}</p><p><strong>Stage/status:</strong> {escape(_field(o, 'stage', 'status') or 'Not established')} · <strong>Timing:</strong> {escape(_field(o, 'timing', 'deadline') or 'Timing not established')}</p><p><strong>Route:</strong> {escape(_field(o, 'route', 'procurement_route') or 'Not established')} · <strong>Buyer/buying centre:</strong> {escape(_field(o, 'buyer', 'buying_centre') or 'Not established')}</p><p><strong>Source:</strong> {escape(', '.join(o.evidence_refs) or 'Evidence not linked')} · <strong>Uncertainty:</strong> {escape(_field(o, 'uncertainty') or 'No explicit uncertainty supplied')}</p></article>"


def _source_item(o: SemanticObject) -> str:
    url = _field(o, "url", "source_url", "link")
    title = _field(o, "title") or o.statement or o.original_id
    linked = f"<a href='{escape(url)}' rel='noopener'>{escape(title)}</a>" if url else escape(title)
    link_gap = "" if url else "<p><strong>Direct source link not supplied</strong></p>"
    return f"<article><h3>{linked}</h3><p><strong>Publisher/origin:</strong> {escape(_field(o, 'publisher', 'origin') or o.source_file)}</p><p><strong>Publication date:</strong> {escape(_field(o, 'publication_date', 'date') or 'Date not established')}</p>{link_gap}<p><strong>What it supports:</strong> {escape(_field(o, 'supports', 'what_it_supports') or 'Claim support not mapped')}</p><details><summary>Advanced evidence metadata</summary><code>{escape(o.original_id or o.record_id)}</code> · {escape(o.governance)}</details></article>"


def _navigation(run_id):
    return _primary_nav(run_id, "")


ASPECT_LABELS = {"industry-overview": "Industry Overview", "enterprises": "Enterprises",
                 "market-participants": "Market Participants", "major-programmes": "Major Programmes",
                 "opportunities": "Opportunities", "reinvention-timing": "Reinvention Timing"}

def _filter_domain(objects, domain):
    if domain == "all": return list(objects)
    return [o for o in objects if domain.casefold() in {d.casefold() for d in o.domains}]

def _primary_nav(run_id: str, active: str) -> str:
    r = escape(run_id)
    links = (("map", f"/blueprint-import/{r}", "Twin Map"), ("gaps", f"/blueprint-import/{r}/health", "Research Gaps"),
             ("inspection", f"/blueprint-import/{r}/explore", "Advanced Inspection"))
    return "<nav class='executive-path' aria-label='Twin navigation'>" + "".join(
        f"<strong aria-current='page'>{label}</strong>" if key == active else f"<a href='{href}'>{label}</a>" for key, href, label in links) + "</nav>"

def _twin_map(twin: SemanticTwin, run_id: str, mission: CommercialMission | None, domain: str) -> str:
    tiles=[]
    for a in twin_readiness(twin, mission):
        count = a.present[0] if a.present else "No supported information"
        explanation = a.present[-1] if len(a.present)>1 else (a.missing[0] if a.missing else "Business-usefulness requirements are satisfied.")
        bars = "".join(f"<i class='{'filled' if n <= (a.bars or 0) else ''}' aria-hidden='true'></i>" for n in range(1,5))
        href=f"/blueprint-import/{escape(run_id)}/aspects/{a.key}?domain={escape(domain)}"
        tiles.append(f"<a class='twin-map-tile' href='{href}'><h3>{escape(a.name)}</h3><p class='coverage'>{escape(count)}</p><span class='readiness' aria-label='{escape(a.state)}, {a.bars or 0} of 4 bars'>{bars}<strong>{escape(a.state)}</strong></span><p>{escape(explanation)}</p></a>")
    return f"<section class='card twin-map' id='twin-map'><h2>Twin Map</h2><div class='twin-map-grid'>{''.join(tiles)}</div></section>"

def _aspect_page(twin, run_id, title, key, domain, mission):
    if key not in ASPECT_LABELS: return "<section class='card'><h1>Aspect unavailable</h1></section>"
    a=next(x for x in twin_readiness(twin, mission) if x.key==key)
    objects=_filter_domain(twin.objects, domain)
    if key=="enterprises":
        cards="".join(_enterprise_card(e, run_id) for e in twin.enterprises)
        ready=sum("Enterprise intelligence readiness: Executive-ready" in _enterprise_card(e, run_id) for e in twin.enterprises)
        content=f"<p><strong>{len(twin.enterprises)} canonical enterprises · {ready} executive-ready enterprises</strong></p><div class='enterprise-grid'>{cards or '<p>No enterprise identities supplied.</p>'}</div>"
    elif key=="industry-overview":
        rows=[o for o in objects if executive_insight_eligible(o)]
        identity=[o for o in objects if o.kind in {"industry", "subsector"}]
        def section(name, body=""):
            return f"<section><h2>{name}</h2>{body or '<p><strong>Research gap.</strong> No supported structured content is supplied for this section.</p>'}</section>"
        content = section("Industry definition and scope", "".join(f"<p>{escape(o.statement)}</p>" for o in identity if o.kind=="industry"))
        content += section("Composition and sub-sectors", "".join(f"<p>{escape(o.statement)}</p>" for o in identity if o.kind=="subsector"))
        for name in ("Size and economics", "Leading enterprises", "Market participants and competitive structure", "Political and regulatory pressures", "Economic pressures", "Social and customer change", "Technology change", "Legal and environmental factors where applicable", "Major transformation themes"):
            content += section(name)
        content += section("Qualified insights", "".join(_conclusion(o,run_id) for o in rows))
        content += f"<section><h2>Research Gaps</h2><p>{escape('; '.join(a.missing))}</p></section><section><h2>Advanced Inspection</h2><p><a href='/blueprint-import/{escape(run_id)}/explore'>Inspect canonical records, evidence and lineage</a></p></section>"
    elif key=="market-participants":
        identified=list(next((c.objects for c in business_collections(twin, include_empty=True, domain=domain) if c.key=='market-participants'), ()))
        rows=[o for o in identified if _field(o,'role','participant_role','market_role') and o.domains and o.evidence_refs and o.consequence]
        content=f"<p><strong>{len(identified)} participants identified</strong><br><strong>{len(rows)} sufficiently classified</strong></p>"+("".join(f"<article class='enterprise-card'><h3>{escape(o.subject if o.subject not in {'','Twin scope'} else o.statement)}</h3><p><strong>Role:</strong> {escape(_field(o,'role','participant_role','market_role'))}</p><p><strong>Domain:</strong> {escape(', '.join(o.domains))}</p><p>{escape(o.consequence)}</p></article>" for o in rows) if rows else "<p><strong>Insufficient</strong> — supported role, domain and market significance require research.</p>")
    elif key=="major-programmes":
        rows=[o for o in objects if o.kind=='transformation_programme']
        ready=[o for o in rows if o.statement and (_field(o,'owner') or o.subject!='Twin scope') and o.consequence and _field(o,'stage','phase') and _field(o,'timing','expected_horizon') and o.evidence_refs]
        content=f"<p><strong>{len(rows)} programme hypotheses identified</strong><br><strong>{len(ready)} executive-ready programmes</strong></p>"+("".join(f"<article class='enterprise-card'><h3>{escape(o.statement)}</h3><p><strong>Owning enterprise:</strong> {escape(_field(o,'owner') or o.subject)}</p><p><strong>Business objective:</strong> {escape(o.consequence)}</p></article>" for o in ready) if ready else "<p><strong>Insufficient.</strong> Programme owner, objective, phase, timing and evidence must be resolved before hypotheses appear here.</p>")
    elif key=="opportunities":
        rows=[o for o in objects if 'opportun' in o.kind]; ready=[o for o in rows if _opportunity_contract(o,mission)[1]]
        table=("<table class='opportunity-table'><thead><tr><th>Customer</th><th>Opportunity</th><th>Value</th><th>Timing</th><th>Status</th></tr></thead><tbody>"+"".join(f"<tr><td>{escape(', '.join(o.affected_organisations) or o.subject)}</td><td>{escape(o.statement)}</td><td>{escape(_field(o,'value','value_range') or 'Not established')}</td><td>{escape(_field(o,'timing','procurement_start') or 'Timing unknown')}</td><td>{escape(_field(o,'status','procurement_status') or 'Status unknown')}</td></tr>" for o in ready)+"</tbody></table>") if ready else "<p>0 sales-ready opportunities.</p>"
        content=f"<h2>Sales-ready opportunities</h2>{table}<h2>Developing hypotheses</h2><p><strong>{len(rows)-len(ready)} hypotheses require further research.</strong></p><h2>Research required</h2><ul><li>customer</li><li>client problem</li><li>business unit</li><li>timing</li><li>status</li><li>value</li><li>buyer</li><li>evidence</li></ul>"
    else:
        rows=[o for o in objects if _field(o,'expected_horizon','tipping_point','reinvention_timing')]
        content=("<p><strong>Absent</strong></p><p>This Twin contains no structured assessment of:</p><ul><li>AI-native disruption mechanism</li><li>enterprise or business-unit exposure</li><li>adoption indicators</li><li>expected horizon</li><li>response timing</li></ul><h2>Research required</h2><p>Research the disruption mechanism, exposure, adoption indicators, horizon, response timing and evidence.</p>" if not rows else "".join(_conclusion(o,run_id) for o in rows))
    gaps="; ".join(a.missing) or "No unresolved mandatory fields."
    return _primary_nav(run_id,"aspect")+f"<p><a href='/blueprint-import/{escape(run_id)}'>Back to Twin Map</a></p><header class='hero'><p>{escape(title)} · {escape(domain.title())}</p><h1>{escape(ASPECT_LABELS[key])}</h1><p><strong>{escape(a.state)}</strong> · {escape(a.present[-1] if a.present else gaps)}</p></header><section class='card'>{content}</section><section class='card'><h2>Research gaps for this aspect</h2><p>{escape(gaps)}</p><p><strong>Researcher action:</strong> {escape(a.researcher_action)}</p></section>"+_navigation(run_id)

def _research_gaps(twin, run_id, mission):
    cards=[]
    for a in twin_readiness(twin,mission):
        exists=a.present[0] if a.present else "No supported content"
        missing="; ".join(a.missing) or "No mandatory presentation gap"
        affected=len(set(a.affected))
        cards.append(f"<article class='research-gap'><h2>{escape(a.name)}</h2><p><strong>{escape(a.state)}</strong></p><p><strong>What exists:</strong> {escape(exists)}</p><p><strong>What is missing:</strong> {escape(missing)}</p><p><strong>Why it matters:</strong> Missing mandatory context prevents a stronger executive interpretation.</p><p><strong>Researcher action:</strong> {escape(a.researcher_action)}</p><a href='/blueprint-import/{escape(run_id)}/aspects/{a.key}'>Affected records ({affected})</a></article>")
    return _primary_nav(run_id,"gaps")+"<header class='hero'><h1>Research Gaps</h1><p><a class='button primary' href='/blueprint-import/"+escape(run_id)+"/research-brief'>Export Research Brief</a></p></header><section class='research-gap-grid'>"+"".join(cards)+f"</section><p><a href='/blueprint-import/{escape(run_id)}/diagnostics'>Advanced diagnostics</a></p>"


def _display(o: SemanticObject, fallback: str) -> str:
    """Return only a legitimate human-readable label for primary prose."""
    candidates = (_field(o, "name", "title", "programme_name", "opportunity_name"), o.statement, o.subject)
    return next((x.strip() for x in candidates if x and x.strip() not in {"Twin scope", o.original_id, o.record_id}), fallback)


def research_gap_brief(twin: SemanticTwin, twin_name: str, mission: CommercialMission | None,
                       domain: str = "all", employer_context: EmployerContext | None = None) -> str:
    """Render a commissioning paper from canonical readiness and completeness rules."""
    aspects = twin_readiness(twin, mission)
    context = employer_context
    selected = [o for o in twin.objects if domain == "all" or domain.casefold() in {d.casefold() for d in o.domains}]
    evidence = [o for o in selected if o.kind == "evidence"]
    programmes = [o for o in selected if o.kind == "transformation_programme"]
    opportunities = [o for o in selected if "opportun" in o.kind]
    lines = [f"# {twin_name}", "## Research Gap and Enrichment Brief", "", "## 1. Purpose",
             "Commission the evidence needed to make this imported Industry Twin usable for the six executive experiences, without treating hypotheses as findings.",
             "", "### Commercial Mission"]
    if mission:
        lines += [f"- Mission: {mission.mission_name or 'unnamed'}", f"- Role: {mission.executive_role or 'unresolved'}", f"- Objective: {mission.commercial_objective or 'unresolved'}",
                  f"- Objectives: {', '.join(mission.objectives) or 'unresolved'}",
                  f"- Target industries: {', '.join(mission.industries) or 'unresolved'}", f"- Target accounts: {', '.join((*mission.target_customers, *mission.priority_accounts, *mission.named_accounts)) or 'unresolved'}",
                  f"- Geography: {', '.join(mission.geography) or 'unresolved'}", f"- Commercial horizon: {mission.commercial_horizon or 'unresolved'}",
                  f"- Focus areas: {', '.join(mission.interests) or 'unresolved'}"]
    else:
        lines += ["- Status: unresolved (no active Commercial Mission)"]
    lines += ["", "### Employer Context"]
    if context:
        state = lambda values: "configured" if values else "not configured"
        lines += [f"- Status: {'Configured' if context.complete else 'Partially configured'}", f"- Organisation: {context.organisation or 'unresolved'} ({context.field_statuses.get('organisation', context.authority_status)})", f"- Offer portfolio: {state(context.offer_portfolio)}",
                  f"- Capabilities: {state(context.capabilities)}", f"- Propositions: {state(context.propositions)}",
                  f"- Competitors: {state(context.competitors)}", f"- Partners: {state(context.partners)}"]
    else:
        lines += ["- Status: Not configured", "- Organisation: unresolved", "- Offer portfolio: not configured", "- Competitors: not configured", "- Partners: not configured"]
    if not context or not context.complete:
        lines += ["", "Employer-specific opportunity alignment cannot yet be fully assessed."]
    lines += ["", "### Mission Readiness",
              f"- Target-account analysis: {'available' if mission and (mission.target_customers or mission.priority_accounts or mission.named_accounts) else 'configuration required'}",
              f"- Focus-area alignment: {'available' if mission and mission.interests else 'configuration required'}",
              f"- Employer-offer alignment: {'available from configured offers' if context and context.offer_portfolio else 'configuration required; no offer is inferred'}",
              f"- Competitor context: {'available from configured competitors' if context and context.competitors else 'configuration required'}",
              f"- Partner context: {'available from configured partners' if context and context.partners else 'configuration required'}",
              f"- Opportunity-horizon assessment: {'available' if mission and (mission.commercial_horizon or mission.opportunity_horizon) else 'configuration required'}"]
    counts = Counter(o.kind for o in selected)
    domains = sorted({d for o in selected for d in o.domains})
    lines += ["", "## 2. Current Twin Summary", f"- Twin: {twin_name}", f"- Domain lens: {domain}",
              f"- Domains: {', '.join(domains) or 'unresolved'}", f"- Canonical enterprises: {len(twin.enterprises)}",
              f"- Market participants: {counts['market_participant_twin']}", f"- Major programme hypotheses: {len(programmes)}",
              f"- Opportunity hypotheses: {len(opportunities)}", f"- Evidence sources: {len(evidence)}",
              "- Readiness: " + "; ".join(f"{a.name} — {a.state}" for a in aspects), "", "## 3. Executive Experience Readiness"]
    for a in aspects:
        lines += [f"### {a.name}", f"- Readiness state: {a.state}", f"- What exists: {a.present[0] if a.present else 'No supported content'}",
                  f"- What is usable: {a.present[-1] if a.present else 'Nothing is yet usable'}", f"- What is missing: {'; '.join(a.missing) or 'No mandatory readiness field'}",
                  f"- Why the gap matters: the experience cannot advance beyond {a.state} under Flora's {a.rule_version} rule until these fields and relationships are supported."]
    priority = ("Opportunities", "Reinvention Timing", "Major Programmes", "Enterprise Intelligence", "Industry Overview", "Market Participants")
    lines += ["", "## 4. Researcher Actions", "The following work requires external, attributable evidence. Configuration omissions are not Industry Twin truth gaps."] + [f"{i}. {name}" for i, name in enumerate(priority, 1)]
    configuration_actions = []
    if not mission: configuration_actions.append("Configure the user's Commercial Mission, role, objectives and focus.")
    if not context: configuration_actions.append("Configure the employer organisation and explicitly supplied portfolio context.")
    elif not context.offer_portfolio: configuration_actions.append("Configure relevant employer offers; do not ask a researcher to infer the internal portfolio.")
    if not context or not context.competitors: configuration_actions.append("Configure preferred competitors or leave competitor context unavailable.")
    if not context or not context.partners: configuration_actions.append("Configure preferred partners or leave partner context unavailable.")
    lines += ["", "## 4A. User Configuration Actions"] + (configuration_actions or ["No mandatory user or employer configuration action remains."])
    lines += ["", "## 5. Industry-Level Research Gaps"]
    industry_fields = "market size; economics; structure; competitive landscape; regulatory pressures; technology shifts; PESTLE coverage; transformation themes; qualified insights"
    for group in ("Telecoms", "Media", "Sport", "Cross-domain"):
        lines += [f"### {group}", f"- What is missing: validate and complete {industry_fields}.", "- Required research action: return dated, attributable evidence for every populated claim; leave unsupported fields unresolved."]
    lines += ["", "## 6. Enterprise Research Gaps"]
    for ent in twin.enterprises:
        gaps = [a for a in _enterprise_completeness(ent, mission) if a.state != "Complete enough for executive use"]
        missing = "; ".join(dict.fromkeys(m for a in gaps for m in a.missing)) or "No deterministic completeness gap"
        lines += _gap_block(ent.name, f"{sum(a.state == 'Complete enough for executive use' for a in _enterprise_completeness(ent, mission))}/{len(_enterprise_completeness(ent, mission))} completeness aspects usable", missing,
                            "Incomplete enterprise context prevents supported account, programme and opportunity interpretation.",
                            "Research overview, strategy, financials, material pressures, programmes, procurements, AI adoption, opportunities and key sources.",
                            "All applicable enterprise completeness checks shown in section 12 pass.")
    lines += ["", "## 7. Major Programme Research Gaps"]
    for o in programmes:
        lines += _record_gap(o, "programme", ("programme_name", "owner", "business_unit", "objective", "stage", "timing", "investment", "procurement", "buyer", "suppliers", "partners", "evidence"))
    if not programmes: lines += ["No named programme hypothesis is present; researchers must not invent one."]
    lines += ["", "## 8. Opportunity Research Gaps"]
    for o in opportunities:
        lines += _record_gap(o, "opportunity", ("customer", "business_unit", "client_problem", "opportunity", "value", "timing", "procurement_status", "buyer", "trigger", "programme", "evidence", "confidence"))
    if not opportunities: lines += ["No named opportunity hypothesis is present; researchers must not invent one."]
    lines += ["", "## 9. Reinvention Timing Research Gaps"]
    timing = next(a for a in aspects if a.key == "reinvention-timing")
    lines += _gap_block("Reinvention Timing", timing.present[0], "; ".join(timing.missing) or "No mandatory readiness field",
                        "Without supported timing Flora cannot distinguish an emerging disruption from a current commercial trigger.",
                        "Research AI-native disruption mechanism, tipping-point hypothesis, timing range, exposed enterprises, first-adopting units, adoption indicators, blockers, evidence and uncertainty.", timing.researcher_action)
    claims = [o for o in selected if o.statement and o.kind != "evidence"]
    lines += ["", "## 10. Evidence and Source Gaps", f"- Claims without evidence: {sum(not o.evidence_refs for o in claims)}",
              f"- Evidence without claim linkage: {sum(not any(o.original_id in c.evidence_refs for c in claims) for o in evidence)}",
              f"- Evidence with missing URL, publisher or publication date: {sum(not (_field(o,'url','source_url') and _field(o,'publisher') and _field(o,'publication_date','date')) for o in evidence)}",
              "- Required research action: add source URLs, publisher, publication date and claim linkage; refresh stale material and corroborate weak or vendor-only claims.",
              "", "## 11. Required Deliverables", "Return import-compatible structured enterprise, programme, opportunity, reinvention-timing and evidence records, with legitimate names, explicit unknowns, source links and claim-to-evidence relationships.",
              "", "## 12. Acceptance Criteria"]
    for a in aspects:
        lines += [f"- **{a.name}:** {a.researcher_action} Runtime rule: `{a.rule_version}`; target state: Executive-ready."]
    lines += ["", "## 13. Appendix — Canonical Traceability", "Technical identifiers appear only in this appendix."]
    for a in aspects:
        lines += [f"### {a.name}", f"- Readiness rule: {a.rule_version}", f"- Twin aspect: {a.key}", f"- Affected canonical record IDs: {', '.join(a.affected) or 'none'}", f"- Missing fields or relationships: {'; '.join(a.missing) or 'none'}"]
    lines += ["", "### Later Re-import Comparison", "Capture readiness before/after, gaps closed/retained, enterprises/programmes enriched, opportunities made sales-ready, evidence and source links added, and Reinvention Timing added. This does not block this export."]
    return "\n".join(lines) + "\n"


def _gap_block(name, current, missing, why, action, acceptance):
    return [f"### {name}", f"**Current position**  \n{current}", f"**What is missing**  \n{missing}", f"**Why it matters**  \n{why}", f"**Required research action**  \n{action}", f"**Acceptance test**  \n{acceptance}"]


def _record_gap(o, record_type, fields):
    present = {f for f in fields if (o.evidence_refs if f == "evidence" else _field(o, f))}
    if record_type == "opportunity" and (o.affected_organisations or o.subject not in {"", "Twin scope"}): present.add("customer")
    missing = [f.replace("_", " ") for f in fields if f not in present]
    return _gap_block(_display(o, f"Unnamed {record_type} hypothesis"), f"A {record_type} hypothesis exists; {len(present)} required attributes are structured.",
                      ", ".join(missing) or "No mandatory field under this contract",
                      f"Flora cannot determine whether this {record_type} supports an executive or commercial decision until the missing facts are evidenced.",
                      f"Investigate named owners and public evidence to resolve: {', '.join(missing) or 'source corroboration'}.",
                      f"The record resolves {', '.join(f.replace('_',' ') for f in fields)} with linked evidence, or explicitly records a governed unknown.")


def export_research_gap_brief(import_run_id: str, headers: Any, domain: str = "all") -> tuple[str, str, int]:
    """Authorise and generate the Markdown derivative without mutating import state."""
    package = next((p for p in BlueprintPackageRegistry().list() if p.import_run_id == import_run_id), None)
    if package is None: return "Import record not found\n", "Research-Gap-and-Enrichment-Brief.md", 404
    if not (pilot_import_bypass_enabled() or (can_access_enterprise(headers, package.identity.enterprise_id, package.workspace_id) and can_inspect_blueprint_package(headers, package))):
        return "Access denied\n", "Research-Gap-and-Enrichment-Brief.md", 403
    summary = BlueprintPackageValidator().staging_summary(import_run_id) or {}
    twin = assemble_semantic_twin(_semantic_candidates(package, list(summary.get("candidates") or ())))
    inspection = package.package_inspection or {}
    identity = project_twin_identity(package)
    title = str(inspection.get("twin_title") or inspection.get("package_title") or identity.primary_subject_name or package.identity.package_id)
    safe = "".join(c if c.isalnum() or c in "-_" else "-" for c in (package.identity.package_id or title)).strip("-") or "Twin"
    return research_gap_brief(twin, title, resolve_commercial_mission(headers), domain, resolve_employer_context(headers)), f"{safe}-Research-Gap-and-Enrichment-Brief.md", 200

def _advanced_diagnostics(twin,run_id,summary,mission):
    return _primary_nav(run_id,"inspection")+f"<p><a href='/blueprint-import/{escape(run_id)}/health'>Back to Research Gaps</a></p><header class='hero'><h1>Advanced Inspection</h1></header>"+_validation_report(twin)+_limitations(twin,summary,None,bool(twin.unresolved_references))+_readiness_inspection(twin,run_id,mission)+_researcher_feedback(twin)


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


def _readiness_inspection(twin: SemanticTwin, run_id: str, mission: CommercialMission | None) -> str:
    sections = []
    for a in twin_readiness(twin, mission):
        present = "".join(f"<li>{escape(x)}</li>" for x in a.present) or "<li>No relevant structured content</li>"
        missing = "".join(f"<li>{escape(x)}</li>" for x in a.missing) or "<li>No gap under this rule</li>"
        affected = "".join(f"<li><a href='/blueprint-import/{escape(run_id)}/explore#{escape(x)}'>{escape(x)}</a></li>" for x in a.affected) or "<li>No affected records</li>"
        sections.append(f"<article class='card readiness-detail' id='{escape(a.key)}'><h2>{escape(a.name)}</h2><p><strong>{escape(a.state)}{' — '+str(a.bars)+' of 4 bars' if a.bars is not None else ''}</strong></p><p>Rule applied: <code>{escape(a.rule_version)}</code></p><h3>Present</h3><ul>{present}</ul><h3>Missing</h3><ul>{missing}</ul><h3>Affected records</h3><ul>{affected}</ul><h3>Next state requires</h3><p>{escape(a.next_requirement)}</p><h3>Required researcher action</h3><p>{escape(a.researcher_action)}</p></article>")
    return "<section id='readiness-inspection'><h1>Readiness inspection</h1><p>These explanations are generated by the same versioned rules as the import review and Research Gaps report.</p>" + "".join(sections) + "</section>"


def _health(twin: SemanticTwin, run_id: str, summary: dict, mission: CommercialMission | None = None) -> str:
    r = escape(run_id)
    return (f"<nav class='executive-path'><a href='/blueprint-import/{r}'>Back to Twin Map</a><strong>Twin Health</strong></nav>"
            "<header class='hero'><h1>Twin Health</h1><p>Evidence, quality and governance are available here when deliberately requested.</p></header>"
            + _validation_report(twin) + _limitations(twin, summary, None, bool(twin.unresolved_references))
            + _readiness_inspection(twin, run_id, mission) + _attention(twin, run_id) + _reasoning_trace(twin, mission) + _researcher_feedback(twin)
            + f"<section class='card'><h2>Candidate state and promotion readiness</h2><p>Candidate records remain separate from governed intelligence. No automatic promotion occurs.</p><a href='/blueprint-import/{r}/review'>Protected governance actions</a> · <a href='/blueprint-import/{r}/inspect'>Inspect evidence and import decisions</a></section>")


def _styles():
    return """<style>.twin-map-grid,.research-gap-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1rem}.twin-map-tile,.research-gap{display:flex;flex-direction:column;padding:1rem;border:1px solid #cad8d3;border-radius:.7rem;background:#fffdf8;color:inherit;text-decoration:none}.twin-map-tile:hover,.twin-map-tile:focus{outline:3px solid #185c4d}.twin-map-tile h3{margin:.1rem 0}.twin-map-tile .coverage{font-weight:700}.research-gap{display:block}@media(max-width:600px){.twin-map-grid,.research-gap-grid{grid-template-columns:1fr}}.compact-twin-header h1{font-size:clamp(1.35rem,3vw,2rem);display:flex;align-items:center;gap:.35rem;flex-wrap:wrap}.pilot-badge{font-size:.65em;letter-spacing:.08em;background:#f3c969;color:#302400;padding:.25rem .45rem;border-radius:.25rem}.mission-indicator{padding:.65rem;margin:.75rem 0;background:#eef5f2;border-left:4px solid #185c4d}.executive-path,.domain-lenses,.secondary-actions{display:flex;gap:.65rem;flex-wrap:wrap;align-items:center;margin:1rem 0}.executive-path span,.executive-path a,.executive-path strong,.pill,.collection-chip,.domain-lens{padding:.45rem .7rem;border-radius:1rem;background:#eef5f2}.domain-lens.active{background:#185c4d;color:white}.composition-grid,.theme-grid,.enterprise-grid,.readiness-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem}.readiness-grid article{padding:.7rem;border:1px solid #cad8d3;border-radius:.5rem}.readiness-grid h3{margin:.1rem 0 .5rem}.readiness{display:flex;gap:.25rem;align-items:center}.readiness i{display:block;width:.45rem;height:1.15rem;border:1px solid #185c4d;border-radius:2px}.readiness i.filled{background:#185c4d}.readiness span{margin-left:.35rem}.composition-tile,.theme-tile,.executive-conclusion,.enterprise-card{display:flex;flex-direction:column;gap:.5rem;padding:1rem;border:1px solid #cad8d3;border-radius:.7rem;text-decoration:none;color:inherit;background:#fffdf8}.composition-tile{min-height:9rem}.procurement-active{background:#dff4e8;font-weight:bold}.composition-tile:focus,.composition-tile:hover,.theme-tile:focus,.theme-tile:hover,.executive-conclusion:focus,.executive-conclusion:hover,.enterprise-card:focus,.enterprise-card:hover{outline:3px solid #185c4d}.composition-tile b,.theme-tile b{font-size:2rem}.insight-explanation{border-left:4px solid #185c4d;padding:1rem;margin:1rem 0}.collection-links{display:flex;gap:.6rem;flex-wrap:wrap}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:.6rem;border-bottom:1px solid #ddd}@media(max-width:600px){.composition-grid,.theme-grid,.enterprise-grid,.readiness-grid{grid-template-columns:1fr}.compact-twin-header h1{align-items:flex-start}.opportunity-table{display:block;overflow-x:auto}}</style>"""
