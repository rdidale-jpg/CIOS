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
    resolve_commercial_context, save_commercial_context)
from cios.applications.flora.workspace.views import _page
from .registry import BlueprintPackageRegistry
from .industry_delta_adapter import IndustryTwinDeltaAdapter
from .canonical_factual_projection import (
    CanonicalFactualProjection, executive_value_lines, factual_projection_for_enterprise, factual_projection_for_object,
)
from .intelligence_projection import executive_assessments
from .pilot_diagnostics import (
    context_header as _pilot_diag_context_header,
    enterprise_diagnostics as _pilot_enterprise_diagnostics,
    field_panel as _pilot_field_panel,
    industry_section_diagnostics as _pilot_industry_section_diagnostics,
    page_reconciliation as _pilot_page_reconciliation,
    research_gap_trace as _pilot_research_gap_trace,
    runtime_comparison as _pilot_runtime_comparison,
)
from .research_requirements import research_requirements
from .observation_runtime import build_candidate_observation, OBSERVATION_BUILDER_NAME, OBSERVATION_PROFILE_VERSION, observation_family
from .semantic_twin import (SemanticEnterprise, SemanticObject, SemanticTwin, assemble_semantic_twin,
                            business_collections, executive_insight_eligible,
                            executive_record_view_model)
from .twin_governance import project_twin_identity
from .validator import BlueprintPackageValidator, can_inspect_blueprint_package
from .review import ImportHumanReviewRepository
from .lifecycle import ImportLifecycleService
from .presentation_contract import fact_state, plural, review_label, promotion_label

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
    rule_version: str = "owner-projection-v1"
    canonical_owner: str = ""
    evidence_source: str = ""
    completeness_authority: str = ""
    eligibility_authority: str = ""
    acceptance_criteria: str = ""

    @property
    def bars(self) -> int | None:
        # Owner states are displayed verbatim; Flora does not convert them into
        # a weighted or pseudo-quantitative readiness scale.
        return None


@dataclass(frozen=True)
class ResearchCountContract:
    """Typed inventory projection; counts are never interchangeable."""
    canonical_subject_count: int
    underlying_record_count: int
    deficiency_count: int
    owner_assessment_count: int
    affected_subject_count: int
    presentation_eligible_count: int
    recommendation_eligible_count: int


def _canonical_factual_html(projection: CanonicalFactualProjection, *, include_state: bool = False) -> str:
    rows = []
    for section in projection.sections:
        values = "".join(f"<li>{escape(value)}</li>" for value in section.values)
        rows.append(f"<article><h3>{escape(section.label)}</h3><ul>{values}</ul></article>")
    facts = "".join(rows) or "<p><strong>Facts:</strong> No factual fields are mapped in the canonical factual projection.</p>"
    state = ("<aside class='executive-status' role='status'><strong>Factual presence</strong> — imported candidate.</aside>") if include_state else ""
    evidence = _linked_list("Evidence", projection.evidence_refs, "No linked Evidence supplied.")
    unknowns = _linked_list("Unknowns", projection.unknown_refs, "No explicit Unknowns supplied.")
    contradictions = _linked_list("Contradictions", projection.contradiction_refs, "No explicit Contradictions supplied.")
    relationships = _linked_list("Relationships", projection.relationship_refs, "No relationship references supplied.")
    return (f"{state}<section class='card executive-facts' id='factual-intelligence'>"
            f"<h2>{escape(projection.family)} facts</h2>{facts}"
            f"<details><summary>Evidence and uncertainty</summary>"
            f"{evidence}{unknowns}{contradictions}{relationships}</details></section>")


def _linked_list(title: str, values: tuple[str, ...], empty: str) -> str:
    items = "".join(f"<li><code>{escape(value)}</code></li>" for value in values) or f"<li>{escape(empty)}</li>"
    return f"<section><h3>{escape(title)}</h3><ul>{items}</ul></section>"


def _opportunity_contract(o: SemanticObject, mission: CommercialMission | None = None) -> tuple[bool, bool, list[str]]:
    customer = bool(o.affected_organisations or (o.subject and o.subject != "Twin scope"))
    problem = bool(_field(o, "client_problem", "customer_problem", "problem"))
    timing = bool(_field(o, "procurement_start", "expected_procurement_start", "procurement_timing", "timing_unknown"))
    status = bool(_field(o, "procurement_status", "status"))
    minimum = {"named customer": customer, "opportunity statement": bool(o.statement), "client problem": problem,
               "evidence": bool(o.evidence_refs), "procurement timing or explicit timing unknown": timing}
    usable = {**minimum, "confidence": o.confidence.casefold() not in {"", "unknown"}, "procurement status": status}
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
    """Compatibility facade over owner-supplied assessments (mission never alters completeness)."""
    legacy_inventory = {
        "industry-overview": lambda a: a.inventory_summary,
        "enterprises": lambda a: f"{len(twin.enterprises)} represented enterprise(s)",
        "market-participants": lambda a: f"{len(next(c for c in business_collections(twin, include_empty=True) if c.key == 'market-participants').objects)} represented participant(s)",
        "major-programmes": lambda a: f"{sum(o.kind == 'transformation_programme' for o in twin.objects)} programme hypothesis record(s)",
        "opportunities": lambda a: f"{len(next(c for c in business_collections(twin, include_empty=True) if c.key == 'opportunities').objects)} opportunity hypothesis record(s)",
        "reinvention-timing": lambda a: a.inventory_summary,
    }
    collections = {c.key: c.objects for c in business_collections(twin, include_empty=True)}
    affected = {
        "industry-overview": tuple(o.original_id or o.record_id for o in twin.objects if o.kind in {"industry", "industry_twin", "subsector", "value_chain", "economic_pool"}),
        "enterprises": tuple(e.identity_key for e in twin.enterprises),
        "market-participants": tuple(o.original_id or o.record_id for o in collections["market-participants"]),
        "major-programmes": tuple(o.original_id or o.record_id for o in twin.objects if o.kind == "transformation_programme"),
        "opportunities": tuple(o.original_id or o.record_id for o in collections["opportunities"]),
        "reinvention-timing": tuple(o.original_id or o.record_id for o in twin.objects if _reinvention_kind(o)),
    }
    return tuple(ReadinessAspect(
        a.key, a.label, a.state, (legacy_inventory[a.key](a), a.inventory_summary, f"Completeness is owned by {a.completeness_authority}."),
        a.deficiencies, affected[a.key], a.acceptance_criteria, a.required_evidence, "owner-projection-v1",
        a.canonical_owner, a.evidence_source, a.completeness_authority, a.eligibility_authority,
        a.acceptance_criteria,
    ) for a in executive_assessments(twin))


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
    commercial_context = resolve_commercial_context(headers)
    mission = commercial_context.commercial_mission
    employer_context = commercial_context.employer_context
    inspection = package.package_inspection or {}
    identity = project_twin_identity(package)
    title = str(inspection.get("twin_title") or inspection.get("package_title") or identity.primary_subject_name or package.identity.package_id)
    if view == "explore":
        return _page(f"Explore Twin — {title}", _styles() + _pilot_diag_context_header(package, summary) + _explorer(twin, import_run_id, mission, collection, domain) + _pilot_page_reconciliation(twin, "Evidence")), 200
    if view == "health":
        return _page(f"Research Gaps — {title}", _styles() + _mission_indicator(mission, employer_context, import_run_id, domain) + _research_gaps(twin, import_run_id, mission)), 200
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
        return f"<aside class='mission-indicator' role='status'><strong>Commercial context not configured</strong> · neutral Industry Twin ordering because no Commercial Mission is available · <a href='{target}'>Configure</a></aside>"
    employer_name = employer.organisation if employer else "Employer not supplied"
    details = [mission.mission_name, mission.executive_role, employer_name,
               ", ".join(mission.geography), mission.commercial_horizon]
    return ("<aside class='mission-indicator' role='status'><strong>Commercial context "
            f"{escape(mission.operational_status.casefold())}</strong> · "
            + " · ".join(escape(item) for item in details if item)
            + f" · <a href='{target}'>Edit</a></aside>")


def _bars(a: ReadinessAspect, run_id: str) -> str:
    if a.bars is None:
        return f"<a class='readiness' href='/blueprint-import/{escape(run_id)}/health#{escape(a.key)}'><span>{escape(_assessment_state_label(a.state))}</span></a>"
    bars = "".join(f"<i class='{'filled' if i <= a.bars else ''}' aria-hidden='true'></i>" for i in range(1, 5))
    return f"<a class='readiness' href='/blueprint-import/{escape(run_id)}/health#{escape(a.key)}' aria-label='{escape(a.name)}: {escape(_assessment_state_label(a.state))}, {a.bars} of 4 bars'>{bars}<span>{escape(_assessment_state_label(a.state))}</span></a>"


def _readiness_review(twin: SemanticTwin, run_id: str, mission: CommercialMission | None) -> str:
    rows = "".join(f"<article><h3>{escape(a.name)}</h3>{_bars(a, run_id)}</article>" for a in twin_readiness(twin, mission))
    return f"<section class='card' id='twin-readiness'><h2>Twin Readiness</h2><p>Read-only projection of owner-supplied completeness and eligibility outputs; Flora does not calculate a parallel score.</p><div class='readiness-grid'>{rows}</div><p><a class='button primary' href='#opportunities'>Open Executive Experience</a> <a class='button' href='/blueprint-import/{escape(run_id)}/health#researcher-feedback'>Review Research Gaps</a></p></section>"


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


def _attribute(o: SemanticObject, *names: str) -> Any:
    for name in names:
        value = (o.attributes or {}).get(name)
        if value not in (None, "", [], (), {}):
            return value
    return ""


def _present_value(value: Any) -> str:
    """Render structured canonical values through the shared presentation formatter."""
    return "; ".join(executive_value_lines(value))


def _structured_value(value: Any) -> str:
    """Present canonical nested values without leaking serialisation syntax."""
    if isinstance(value, dict):
        rows = "".join(
            f"<div class='labelled-fact'><dt>{escape(str(key).replace('_', ' ').title())}</dt><dd>{_structured_value(item)}</dd></div>"
            for key, item in value.items() if item not in (None, "", [], (), {})
        )
        return f"<dl class='fact-list'>{rows}</dl>"
    if isinstance(value, (list, tuple, set)):
        return "<ul>" + "".join(f"<li>{_structured_value(item)}</li>" for item in value) + "</ul>"
    return escape(str(value))


def _executive_record_card(o: SemanticObject) -> str:
    model = executive_record_view_model(o)
    fields = "".join(f"<section class='labelled-section'><h4>{escape(label)}</h4>{_structured_value(value)}</section>"
                     for label, value in model.fields)
    evidence = (f"<p><strong>Evidence:</strong> {escape(', '.join(model.evidence_refs))}</p>"
                if model.evidence_refs else "")
    return (f"<article class='enterprise-card' id='{escape(model.record_id)}'>"
            f"<h3>{escape(model.title)}</h3>{fields}{evidence}"
            "<p class='governance-note'>Imported candidate — not yet reviewed</p></article>")


def _opportunity_card(o: SemanticObject, run_id: str) -> str:
    problem = _attribute(o, "client_problem", "customer_problem", "problem")
    timing = _attribute(o, "why_now", "timing", "target_date", "deadline")
    enterprises = ", ".join(o.affected_organisations) or (o.subject if o.subject != "Twin scope" else "Affected enterprise not established")
    theme = _field(o, "reinvention_theme", "theme")
    relevance = _field(o, "commercial_relevance")
    evidence = ", ".join(o.evidence_refs) or "Evidence not linked"
    missing = [label for label, present in (("client problem", bool(problem)),
               ("affected enterprise", enterprises != "Affected enterprise not established"),
               ("evidence", bool(o.evidence_refs)), ("timing", bool(timing))) if not present]
    details = f"<p><strong>Customer:</strong> {escape(enterprises)}</p>"
    details += f"<section><h4>Client problem</h4>{_structured_value(problem) if problem else '<p>Not established</p>'}</section>"
    details += f"<section><h4>Timing</h4>{_structured_value(timing) if timing else '<p>Not established</p>'}</section>"
    details += f"<p><strong>Relevant domain:</strong> {escape(', '.join(d.title() for d in o.domains) or 'Not established')}</p>"
    if theme: details += f"<p><strong>Reinvention theme:</strong> {escape(theme)}</p>"
    if relevance: details += f"<p><strong>Commercial relevance:</strong> {escape(relevance)}</p>"
    confidence = "Supplied; assessment not yet performed" if "confidence_model" in o.confidence.casefold() else o.confidence
    details += f"<p><strong>Evidence:</strong> {escape(evidence)} · <strong>Confidence:</strong> {escape(confidence)}</p>"
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
    eligible = list(insight_collection.objects if insight_collection and _owner_assessed(twin, "industry-overview") else ())
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
    body = (f"<p>{escape(description)}</p>" if description else
            "<p><strong>Organisation description pending owner assessment.</strong></p>")
    body += f"<p><strong>Industry/domain:</strong> {escape(', '.join(domains) or 'Not established')}</p>"
    if position:
        body += f"<p><strong>Strategic position:</strong> {escape(position)}</p>"
    if pressure:
        body += f"<p><strong>Material pressure:</strong> {escape(pressure)}</p>"
    if posture:
        body += f"<p><strong>Transformation posture:</strong> {escape(posture)}</p>"
    body += "<p><span class='pill'>Imported candidate · assessment not yet performed</span></p>"
    canonical_fields = ""
    if identity:
        canonical_fields = "".join(
            f"<p><strong>{escape(label)}:</strong> {escape(_present_value(value))}</p>"
            for label, value in executive_record_view_model(identity).fields
            if label != "Overview"
        )
    return f"<a class='enterprise-card' href='/blueprint-import/{escape(run_id)}/enterprises/{escape(e.identity_key)}'><h3>{escape(e.name)}</h3>{body}{canonical_fields}</a>"


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
    def optional_field(name, label, saved, example="", help_text=""):
        """Render guidance outside a blank control so it cannot resemble saved data."""
        status = "Configured" if saved else "Not configured"
        example_html = f"<small class='field-example'>Example: {escape(example)}</small>" if example else ""
        help_html = f"<small class='field-help'>{escape(help_text)}</small>" if help_text else ""
        return (f"<label>{escape(label)} <span class='optional'>Optional · "
                f"<span class='field-status' data-status-for='{name}'>{status}</span></span>"
                f"<input name='{name}' value='{saved}' autocomplete='off'>{example_html}{help_html}</label>")
    def choices(name, legend, options, selected):
        selected_folded = {item.casefold() for item in selected}
        controls = "".join(
            f"<label class='choice'><input type='checkbox' name='{name}' value='{escape(option)}'"
            f"{' checked' if option.casefold() in selected_folded else ''}> <span>{escape(option)}</span></label>"
            for option in options)
        # Previously saved free-form values remain editable and are never discarded.
        extras = [item for item in selected if item.casefold() not in {option.casefold() for option in options}]
        controls += "".join(f"<label class='choice'><input type='checkbox' name='{name}' value='{escape(item)}' checked> <span>{escape(item)}</span></label>" for item in extras)
        status = "Configured" if selected else "Not configured"
        return f"<fieldset class='choice-group'><legend>{legend} · <span class='field-status'>{status}</span></legend><div class='choice-grid'>{controls}</div></fieldset>"

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
        optional_field(f"employer_{name}", label, employer_value(name))
        for name, label in (("description", "Employer description"), ("propositions", "Propositions"),
            ("target_sectors", "Target sectors"), ("credentials", "Reference credentials"),
            ("constraints", "Delivery constraints"), ("excluded_offerings", "Excluded or unsupported offerings")))

    any_context = bool(m or employer)
    mission_ready = bool(m and m.executive_role and m.commercial_objective and m.geography and m.commercial_horizon)
    status = "Configured" if mission_ready and employer and employer.complete else "Partially configured" if any_context else "Not configured"
    back = f"/blueprint-import/{escape(run_id)}?domain={escape(domain)}"
    mission_optional = "".join((
        optional_field("mission_name", "Mission name", value("mission_name"), "UK growth"),
        optional_field("industries", "Industries", value("industries"), "Media, telecommunications", "Add only industries you want Flora to prioritise."),
        optional_field("priority_accounts", "Priority customers", value("priority_accounts"), "BT Group, BBC, ITV", "Add named accounts where useful."),
        optional_field("target_customers", "Target accounts", value("target_customers"), "Named target organisations"),
        optional_field("relevant_business_units", "Relevant business units", value("relevant_business_units"), "Consumer, Business, Openreach"),
        optional_field("employer_capabilities", "Relevant capabilities or services", employer_value("capabilities"), "Digital transformation, cloud, data, AI, managed services"),
        optional_field("employer_competitors", "Competitors", employer_value("competitors"), "Accenture, Capgemini, IBM"),
        optional_field("employer_partners", "Partners", employer_value("partners"), "Named strategic partners"),
    ))
    def summary_value(raw):
        return raw or "Not configured"
    summary = f"""<section class='setup-section save-summary' aria-labelledby='save-summary'><h2 id='save-summary'>What will be saved</h2><h3>About me</h3><ul><li>Role: <span data-summary-for='executive_role'>{summary_value(value('executive_role'))}</span></li><li>Employer: <span data-summary-for='employer_organisation'>{summary_value(employer_value('organisation'))}</span></li><li>Geography: <span data-summary-for='geography'>{summary_value(value('geography'))}</span></li><li>Horizon: <span data-summary-for='commercial_horizon'>{summary_value(value('commercial_horizon'))}</span></li></ul><h3>Optional context</h3><ul><li>Industries: <span data-summary-for='industries'>{summary_value(value('industries'))}</span></li><li>Priority customers: <span data-summary-for='priority_accounts'>{summary_value(value('priority_accounts'))}</span></li><li>Capabilities: <span data-summary-for='employer_capabilities'>{summary_value(employer_value('capabilities'))}</span></li><li>Competitors: <span data-summary-for='employer_competitors'>{summary_value(employer_value('competitors'))}</span></li></ul><p class='field-help'>This summary reflects entries in the form. Nothing is persisted until Save succeeds.</p></section>"""
    return f"""<style>
.guided-setup{{max-width:900px;margin-inline:auto}}.setup-status{{display:flex;justify-content:space-between;gap:1rem;align-items:center;padding:1rem;border-left:4px solid #185c4d;background:#eef5f2}}.setup-section{{margin:1rem 0;padding:1.25rem;border:1px solid #cad8d3;border-radius:.7rem}}.setup-section>h2{{margin-top:0}}.setup-section label:not(.choice){{display:block;font-weight:700;margin:.9rem 0}}.setup-section input[type=text],.setup-section input:not([type]),.setup-section select{{box-sizing:border-box;display:block;width:100%;margin-top:.35rem;padding:.7rem;border:1px solid #718078;border-radius:.35rem;background:white}}.setup-section input::placeholder{{color:#6b756f;font-style:italic;opacity:1}}.field-help,.field-example{{display:block;font-weight:400;color:#46534d;margin-top:.25rem}}.field-example{{font-style:italic}}.optional{{font-size:.8rem;font-weight:400;margin-left:.45rem}}.field-status{{font-weight:600}}.choice-group{{border:0;padding:0;margin:1rem 0}}.choice-group legend{{font-weight:700;margin-bottom:.5rem}}.choice-grid{{display:flex;flex-wrap:wrap;gap:.55rem}}.choice{{display:flex;align-items:center;gap:.35rem;padding:.55rem .7rem;border:1px solid #879a91;border-radius:1.25rem;background:#fff}}.flora-use,.save-summary{{padding:1rem;border-radius:.7rem;background:#f3f7f5}}.form-actions{{display:flex;gap:.7rem;align-items:center;margin-top:1.2rem}}details.setup-section summary{{cursor:pointer;font-weight:700}}@media(max-width:600px){{.guided-setup{{padding:0 .25rem}}.setup-status{{align-items:flex-start;flex-direction:column}}.form-actions{{align-items:stretch;flex-direction:column}}.form-actions .button{{text-align:center}}}}
</style><nav class='executive-path'><a href='{back}'>Back to Twin Map</a><strong>Commercial context</strong></nav><main class='guided-setup'><header><h1>Set up my commercial context</h1><p>Tell Flora what matters to you. Required fields are marked; everything else can be added later. Your Commercial Mission and Employer Context remain separate settings.</p></header><aside class='setup-status' role='status' aria-label='Commercial context status'><strong>Commercial context</strong><span>{status}</span></aside>
<section class='flora-use' aria-labelledby='flora-use-title'><h2 id='flora-use-title'>How Flora will use this</h2><p>Flora will use these settings to prioritise relevant enterprises, opportunities, programmes, competitors, partners and research gaps.</p><p>These settings influence relevance and ordering. They do not change the Twin, its evidence or its confidence.</p></section>
<form method='post' action='/blueprint-import/{escape(run_id)}/mission'><input type='hidden' name='return_domain' value='{escape(domain)}'><input type='hidden' name='save_scope' value='both'><input type='hidden' name='excluded_accounts' value='{value('excluded_accounts')}'><input type='hidden' name='account_focus' value='{value('account_focus')}'>
<section class='setup-section' aria-labelledby='about-me'><h2 id='about-me'>1. About me</h2><p>This gives Flora the essentials it needs to tailor your experience.</p><label>My role <span aria-label='required'>*</span><input name='executive_role' value='{value('executive_role')}' placeholder='Sales Director' required><small class='field-help'>Example: Sales Director</small></label><label>I work for <span aria-label='required'>*</span><input name='employer_organisation' value='{employer_value('organisation')}' placeholder='Your organisation' required><small class='field-help'>Enter your employer; Flora will not infer services or relationships from its name.</small></label><label>My geography <span aria-label='required'>*</span><input name='geography' value='{value('geography')}' placeholder='United Kingdom' required><small class='field-help'>The markets or regions you cover.</small></label><label>My commercial horizon <span aria-label='required'>*</span><select name='commercial_horizon' required><option value=''>Not selected</option>{''.join(f"<option value='{escape(option)}'{' selected' if option == (m.commercial_horizon if m else '') else ''}>{escape(option)}</option>" for option in ('Next 12 months', '12–24 months', 'Strategic'))}{f"<option value='{value('commercial_horizon')}' selected>{value('commercial_horizon')}</option>" if m and m.commercial_horizon and m.commercial_horizon not in ('Next 12 months', '12–24 months', 'Strategic') else ''}</select><small class='field-help'>Example: Next 12 months, 12–24 months, strategic</small></label></section>
<section class='setup-section' aria-labelledby='help-find'><h2 id='help-find'>2. What I want Flora to help me find</h2><label>My main objective <span aria-label='required'>*</span><select name='commercial_objective' required>{objective_options}</select><small class='field-help'>Choose the outcome Flora should prioritise first.</small></label>{choices('objectives', 'Other commercial objectives (optional)', objectives, selected_objectives)}{choices('interests', 'Focus areas (optional)', focus_areas, selected_focus)}</section>
<section class='setup-section' aria-labelledby='my-context'><h2 id='my-context'>3. My commercial context</h2><p>Optional details make matching more precise; blank fields are explicitly not configured.</p>{mission_optional}<input type='hidden' name='employer_offer_portfolio' value='{employer_value('offer_portfolio')}'></section>
<details class='setup-section'{' open' if advanced_open else ''}><summary>More employer settings</summary><p>Optional information for more precise employer alignment. It remains separate from Twin evidence.</p>{advanced}</details>
{summary}<div class='form-actions'><button class='button primary' type='submit'>Save and return to Twin Map</button><a class='button' href='{back}'>Cancel</a></div></form><script>(()=>{{const form=document.currentScript.previousElementSibling;const refresh=(control)=>{{const raw=control.tagName==='SELECT'?control.options[control.selectedIndex]?.text:control.value;const shown=(raw||'').trim()||'Not configured';form.querySelectorAll(`[data-summary-for="${{control.name}}"]`).forEach(node=>node.textContent=shown);form.querySelectorAll(`[data-status-for="${{control.name}}"]`).forEach(node=>node.textContent=shown==='Not configured'?'Not configured':'Configured');}};form.querySelectorAll('input:not([type=hidden]),select').forEach(control=>{{control.addEventListener('input',()=>refresh(control));control.addEventListener('change',()=>refresh(control));}});}})();</script></main>"""


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
    employer_values = {key.removeprefix("employer_"): value for key, value in values.items() if key.startswith("employer_")}
    for key in ("offer_portfolio", "capabilities", "propositions", "competitors", "partners", "target_sectors",
                "credentials", "constraints", "excluded_offerings"):
        raw = employer_values.get(key, "")
        source = raw if isinstance(raw, list) else str(raw).split(",")
        employer_values[key] = [item.strip() for item in source if item.strip()]
    employer_values["authority_status"] = "human-supplied"
    try:
        if scope != "both":
            raise ValueError("Commercial Mission and Employer Context must be saved together")
        save_commercial_context(headers, values, employer_values)
    except PermissionError:
        return _page("Access denied", "<h1>Access denied</h1>"), 403
    except ValueError as exc:
        # Re-render the submitted values, not defaults or the previous profile.
        actor = commercial_context_owner(headers)
        submitted_mission = CommercialMission.from_dict(actor, values)
        submitted_employer = EmployerContext.from_dict(employer_values)
        form_html = _mission_editor(submitted_mission, submitted_employer, import_run_id, str(values.get("return_domain") or "all"))
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
    priority = {'industry-overview':0,'enterprises':1,'market-participants':2,'major-programmes':3,'opportunities':4,'reinvention-timing':5,'evidence':6,'unknowns':7,'contradictions':8,'relationships':9}
    business = sorted((c for c in collections if c.key in priority), key=lambda c: priority[c.key])
    supporting = [c for c in collections if c.key not in priority]
    links = "".join(f"<a class='collection-chip' href='?collection={escape(c.key)}&amp;domain={escape(domain)}'>{escape(c.label)} <b>{len(c.objects)}</b></a>" for c in business)
    supporting_links = "".join(f"<a class='collection-chip' href='?collection={escape(c.key)}&amp;domain={escape(domain)}'>{escape(c.label)} <b>{len(c.objects)}</b></a>" for c in supporting)
    if active and active.key == "enterprises": content = enterprises or "<p>No enterprise identities supplied.</p>"
    elif active and active.key == "opportunities": content = "".join(_executive_record_card(o) for o in active.objects)
    elif active: content = "".join(
        _conclusion(o, run_id) if _owner_assessed(twin, 'industry-overview') and executive_insight_eligible(o)
        else (_executive_record_card(o) if executive_record_view_model(o).fields
              else f"<article class='enterprise-card'><h3>{escape(o.statement or o.original_id or 'Twin record')}</h3><p>Supporting context; not presented as an executive insight.</p>{f'<p><strong>Residual reason:</strong> {escape(o.residual_reason or o.validation_status)}</p>' if active.key == 'other' else ''}<a href='/blueprint-import/{escape(run_id)}/inspect#technical-diagnostics'>Inspect record</a></article>")
        for o in active.objects)
    else: content = "<p>Select a business collection to explore its contents.</p>"
    title = active.label if active else "Advanced Inspection"
    total = len(active.objects) if active else 0
    anomaly_count = len(twin.unresolved_references)
    return f"<nav class='executive-path'><a href='/blueprint-import/{escape(run_id)}'>Back to Twin Map</a><strong>Advanced Inspection</strong></nav><header class='hero'><h1>Advanced Inspection</h1><p>{escape(active.description) if active else 'Reconcile business objects, evidence, relationships and technical traces.'}</p></header><section class='card diagnostic-summary'><h2>Diagnostic Summary</h2><div class='metric-grid'><article><strong>Package integrity</strong><p>Validated import available</p></article><article><strong>Object-family reconciliation</strong><p>{len(twin.objects)} records inventoried</p></article><article><strong>Association anomalies</strong><p>{anomaly_count}</p></article><article><strong>Stale-state status</strong><p>See runtime comparison</p></article></div><form class='diagnostic-filters'><label>Object family <select><option>All families</option></select></label><label>Status <select><option>All statuses</option></select></label><label>Anomaly <select><option>All anomalies</option><option>Missing subject</option><option>Count mismatch</option><option>Unsupported record</option><option>Residual content</option></select></label></form></section><section class='card'><h2>Business collections</h2><div class='collection-links'>{links}</div><details><summary>Technical and supporting collections</summary><div class='collection-links'>{supporting_links or '<p>No supporting collections.</p>'}</div></details></section><section class='card'><h2>{escape(title)}{f' — {total} total' if active else ''}</h2><p>{f'Showing {total} distinct identities' if active and active.key == 'enterprises' else f'Showing {total} of {total} total records' if active else ''}</p>{content}</section><details class='card'><summary>Technical reconciliation traces</summary><table><thead><tr><th>Aspect</th><th>Objects</th><th>Governance</th><th>Evidence coverage</th><th>Unresolved</th></tr></thead><tbody>{aspects}</tbody></table></details>"


def _dossier(ent, twin, run_id, mission):
    factual = factual_projection_for_enterprise(ent)
    factual_html = _canonical_factual_html(factual)
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
        overview = (f"<p>{escape(description or 'Organisation description not supplied.')}</p>"
                    f"<p><strong>Still required:</strong> {escape(', '.join(missing_overview))}.</p>")
        hero = description or "Imported enterprise intelligence ready for review"
    else:
        overview = f"<p>{escape(description)}</p><p><strong>Organisational form:</strong> {escape(_field(identity, 'ownership', 'organisational_form'))}</p><p><strong>Principal activities:</strong> {escape(_field(identity, 'principal_activities', 'activities'))}</p><p><strong>Role in industry:</strong> {escape(_field(identity, 'industry_role', 'role'))}</p><p><strong>Current position:</strong> {escape(_field(identity, 'current_position'))}</p>"
        hero = description
    overview += f"<p><strong>Domain:</strong> {escape(', '.join(domains) or 'Not established')}</p><p><strong>Completeness:</strong> {len(missing_overview)} {plural(len(missing_overview), 'organisation overview requirement')} unresolved.</p>"
    def gap(title, exists, fields, why):
        state = fact_state(present=factual.has_facts)
        # Repeat a concise, governed fact in the section that is being assessed.
        # Executives should not have to reverse-navigate to understand why a
        # dimension is incomplete, and this remains a view over the same CFP.
        known_values = tuple(value for section in factual.sections for value in section.values)
        known = "; ".join(known_values[:3]) if known_values else exists
        return f"<section class='card'><h2>{title}</h2><p><strong>{state}</strong></p><p><strong>Known:</strong> {known}</p><p><strong>Still required:</strong> {escape(', '.join(fields))}.</p><p>{why}</p></section>"
    canonical_detail = ""
    if identity:
        canonical_detail = "".join(
            f"<section class='labelled-section'><h3>{escape(label)}</h3>{_structured_value(value)}</section>"
            for label, value in executive_record_view_model(identity).fields
            if label != "Overview"
        )
    sections = [f"<section class='card' id='enterprise-overview'><h2>Organisation Overview</h2>{overview}{canonical_detail}</section>", factual_html]
    operating = _field(identity, "operating_model", "organisation", "business_units") if identity else ""
    sections.append(f"<section class='card'><h2>Operating Model</h2><p><strong>{fact_state(present=bool(operating))}</strong></p><p><strong>Known:</strong> {escape(operating or 'No operating-model fact is supplied.')}</p><p><strong>Still required:</strong> operating model, business units and supporting evidence.</p></section>")
    position = _field(identity, "strategic_ambition", "market_position", "current_position") if identity else ""
    sections.append(f"<section class='card'><h2>Strategic Position and Ambition</h2><p>{escape(position)}</p></section>" if position else gap("Strategic Position and Ambition", "No supported strategic position is supplied.", ("strategic ambition", "market position", "supporting evidence"), "Without it Flora cannot explain the organisation's direction."))
    financials=[o for o in relevant if o.kind in {"financial_observation","financial_fact","economic_pool"} and all((_field(o,'metric','measure'),_field(o,'value'),_field(o,'period'),_field(o,'source')))]
    sections.append("<section class='card'><h2>Financial Position</h2>"+"".join(f"<p><strong>{escape(_field(o,'metric','measure'))}:</strong> {escape(_field(o,'value'))} · {escape(_field(o,'period'))} · {escape(_field(o,'source'))}</p>" for o in financials)+"</section>" if financials else gap("Financial Position", "No complete financial measure is supplied.", ("measure", "value and currency", "period", "source", "business interpretation"), "Financial position cannot be assessed from an evidence record alone."))
    pressures=_pressure_items(twin,run_id,enterprise=ent.name)
    sections.append("<section class='card'><h2>Material Pressures</h2>"+"".join(pressures)+"</section>" if pressures else gap("Material Pressures", "No evidenced pressure with a business consequence is supplied.", ("pressure", "business consequence", "timing", "evidence"), "The most material challenge cannot be explained."))
    programmes=_associated_records(twin, ent, lambda o: o.kind=='transformation_programme'); ready_programmes=[o for o in programmes if o.statement or _field(o,'objective','business_objective','title')]
    sections.append("<section class='card'><h2>Major Programmes</h2>"+"".join(f"<article><p class='pill'>{escape(_association_type(o, ent) or 'Enterprise programme')}</p><h3>{escape(o.statement or _display(o, 'Programme'))}</h3><p>{escape(o.consequence)}</p></article>" for o in ready_programmes)+"</section>" if ready_programmes else gap("Major Programmes", f"{len(programmes)} associated candidate records supplied.", ("canonically related programme",), "No programme can be shown without an explicit relationship."))
    procurements=[o for o in relevant if o.kind in {"procurement","procurement_route","buying_centre"} or _field(o,'procurement_route','procuring_organisation')]
    ready_proc=[o for o in procurements if (o.statement or _field(o,'requirement')) and _field(o,'stage','status') and _field(o,'timing','procurement_date') and _field(o,'buyer') and _field(o,'value') and _field(o,'award_status','supplier_outcome')]
    sections.append("<section class='card'><h2>Known Procurements</h2>"+"".join(_procurement_item(o,ent.name) for o in ready_proc)+"</section>" if ready_proc else gap("Known Procurements", f"{len(procurements)} {plural(len(procurements), 'candidate record')} are associated with {escape(ent.name)}, but none identifies every mandatory procurement fact.", ("procurement description", "stage", "planned or actual start", "buyer", "value", "award or supplier outcome"), "The records cannot establish a live buying event."))
    sections.append(gap("Reinvention Timing", "No supported enterprise timing assessment is supplied.", ("AI-native disruption mechanism", "exposure", "adoption indicators", "horizon", "response timing"), "Response urgency cannot be assessed."))
    opportunities=_associated_records(twin, ent, lambda o: 'opportun' in o.kind); ready_opps=[o for o in opportunities if o.statement or _field(o,'client_problem','customer_problem','problem','title')]
    sections.append("<section class='card'><h2>Commercial Opportunities</h2>"+"".join(f"<p class='pill'>{escape(_association_type(o, ent) or 'Enterprise opportunity')}</p>"+_opportunity_card(o,run_id) for o in ready_opps)+"</section>" if ready_opps else gap("Commercial Opportunities", f"{len(opportunities)} associated candidate records supplied.", ("canonically related opportunity",), "No opportunity can be shown without an explicit relationship."))
    sources=[o for o in relevant if o.kind=='evidence']
    source_html = "".join(_source_item(o) for o in sources) if sources else ("<ul>" + "".join(f"<li><code>{escape(ref)}</code></li>" for ref in factual.evidence_refs) + "</ul>" if factual.evidence_refs else "<p><strong>Insufficient.</strong> No directly linked sources are supplied.</p>")
    sections.append("<section class='card'><h2>Technology and Ecosystem</h2><p>Technology, supplier and ecosystem facts are retained in the factual inventory above.</p><h3>Suppliers and Partners</h3><p>Supplied relationships are shown only where canonically linked.</p></section>")
    sections.append("<section class='card'><h2>Evidence and Uncertainty</h2>"+source_html+f"<p><strong>Unknowns:</strong> {len(factual.unknown_refs)} · <strong>Contradictions:</strong> {len(factual.contradiction_refs)}</p></section>")
    sections.append(f"<section class='card'><h2>Research Gaps</h2><p>The same completeness requirements shown above define the researcher brief.</p><a href='/blueprint-import/{escape(run_id)}/health'>Open Research Gaps</a></section>")
    sections.append(f"<section class='card'><h2>Advanced Inspection</h2><p>Incomplete records, evidence, lineage and candidate governance remain inspectable.</p><a href='/blueprint-import/{escape(run_id)}/explore'>Open Advanced Inspection</a></section>")
    section_nav = "<nav class='section-nav' aria-label='On this page'><a href='#enterprise-overview'>Overview</a><a href='#major-programmes'>Programmes</a><a href='#enterprise-opportunities'>Opportunities</a><a href='#research-needs'>Research required</a></nav>"
    rendered = "".join(sections).replace("<section class='card'><h2>Major Programmes", "<section class='card' id='major-programmes'><h2>Major Programmes").replace("<section class='card'><h2>Opportunities", "<section class='card' id='enterprise-opportunities'><h2>Opportunities").replace("<section class='card'><h2>Research Gaps", "<section class='card' id='research-needs'><h2>Remaining Research Needs")
    review = ImportHumanReviewRepository().get(run_id)
    promoted = ImportLifecycleService().get(run_id).state == "promoted"
    return _primary_nav(run_id, "")+f"<header class='hero'><p>Enterprise dossier</p><h1>{escape(ent.name)}</h1><p>{escape(hero)}</p></header><aside class='executive-status'><strong>Review status:</strong> {escape(review_label(review))} · <strong>Promotion status:</strong> {escape(promotion_label(promoted))} · <strong>Assessment status:</strong> Assessment not yet performed · <strong>Recommendation status:</strong> Not eligible</aside>{section_nav}"+rendered


def _associated_records(twin: SemanticTwin, ent: SemanticEnterprise, predicate) -> list[SemanticObject]:
    """Resolve page associations through canonical identifiers and memberships."""
    ids = {ent.identity_key.casefold(), ent.name.casefold(), *(a.casefold() for a in ent.aliases)}
    rows = []
    for obj in twin.objects:
        if not predicate(obj):
            continue
        refs = {str(v).casefold() for v in (*obj.references, *obj.affected_organisations) if str(v).strip()}
        # Associations are restricted to canonical reference fields supplied by
        # the semantic read model. Narrative attributes and titles are never
        # searched or interpreted here.
        if ids & refs or obj.subject.casefold() in ids:
            rows.append(obj)
    return list({o.record_id: o for o in rows}.values())


def _association_type(obj: SemanticObject, ent: SemanticEnterprise) -> str:
    """Explain only an explicit canonical association used by the page."""
    ids = {ent.identity_key.casefold(), ent.name.casefold(), *(a.casefold() for a in ent.aliases)}
    if obj.subject and obj.subject.casefold() in ids:
        return "Owned programme" if obj.kind == "transformation_programme" else "Owned opportunity"
    affected = {str(value).casefold() for value in obj.affected_organisations}
    if ids & affected:
        return "Explicit enterprise relationship"
    refs = {str(value).casefold() for value in obj.references}
    return "Canonical relationship" if ids & refs else ""


def _page_association_anomalies(twin: SemanticTwin) -> tuple[str, ...]:
    """Reconcile every record eligible for an enterprise page against its rule."""
    anomalies = []
    for ent in twin.enterprises:
        for obj in _associated_records(twin, ent, lambda row: row.kind == "transformation_programme" or "opportun" in row.kind):
            if not _association_type(obj, ent):
                anomalies.append(f"{ent.identity_key}:{obj.original_id or obj.record_id}")
    return tuple(anomalies)

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
    collections = {c.key: c.objects for c in business_collections(twin, include_empty=True, domain=domain)}
    reinvention_candidates = [o for o in twin.objects if _reinvention_kind(o)]
    summaries = {
        "industry-overview": (1 if any(o.kind in {"industry", "industry_twin"} for o in twin.objects) else 0, "factual profile"),
        "enterprises": (len(twin.enterprises), "enterprise dossier"),
        "market-participants": (len(collections.get("market-participants", ())), "market participant"),
        "major-programmes": (sum(o.kind == "transformation_programme" for o in twin.objects), "programme record"),
        "opportunities": (len(collections.get("opportunities", ())), "opportunity"),
    }
    tiles=[]
    for a in twin_readiness(twin, mission):
        if a.key == "reinvention-timing":
            count = f"{len(reinvention_candidates)} candidate pressure {('record' if len(reinvention_candidates) == 1 else 'records')} supplied"
            explanation = f"0 canonical timing assessments. {len(reinvention_candidates)} records require classification/review."
        else:
            number, noun = summaries[a.key]
            count = f"{number} {plural(number, noun, 'opportunities' if noun == 'opportunity' else None)} imported"
            explanation = "Ready for your review"
        href=f"/blueprint-import/{escape(run_id)}/aspects/{a.key}?domain={escape(domain)}"
        tiles.append(f"<a class='twin-map-tile' href='{href}'><h3>{escape(a.name)}</h3><p class='coverage'>{escape(count)}</p><p>{escape(explanation)}</p></a>")
    review = ImportHumanReviewRepository().get(run_id)
    promoted = ImportLifecycleService().get(run_id).state == "promoted"
    return f"<aside class='executive-status'><strong>Review status:</strong> {escape(review_label(review))} · <strong>Promotion status:</strong> {escape(promotion_label(promoted))} · <strong>Assessment status:</strong> Assessment not yet performed · <strong>Recommendation status:</strong> Not eligible</aside><section class='card twin-map' id='twin-map'><h2>Executive Twin Map</h2><p>Business intelligence supplied in this Twin, with factual inventory kept separate from assessment readiness.</p><div class='twin-map-grid'>{''.join(tiles)}</div><details><summary>Review details</summary><p>Human review is recorded in the existing Review stage. Promotion remains separate.</p></details></section>"

def _owner_assessed(twin: SemanticTwin, key: str) -> bool:
    return next(a for a in executive_assessments(twin) if a.key == key).state not in {
        "legacy_unassessed", "assessment_pending_governance"
    }


def _aspect_page(twin, run_id, title, key, domain, mission):
    if key not in ASPECT_LABELS: return "<section class='card'><h1>Aspect unavailable</h1></section>"
    a=next(x for x in twin_readiness(twin, mission) if x.key==key)
    objects=_filter_domain(twin.objects, domain)
    if key=="enterprises":
        cards="".join(_enterprise_card(e, run_id) for e in twin.enterprises)
        owner_assessed = len(twin.enterprises) if _owner_assessed(twin, key) else 0
        enterprise_requirements = [r for r in research_requirements(twin, executive_assessments(twin)) if r.aspect == key]
        contracts = "".join(f"<article class='card'><h3>{escape(r.subject)} research requirement</h3><p><strong>Find:</strong> {escape(', '.join(r.missing_fields))}.</p><p><strong>Sources:</strong> {escape(', '.join(r.source_categories))}.</p><p><strong>Acceptance test:</strong> {escape(r.acceptance_test)}</p></article>" for r in enterprise_requirements)
        content=f"<p><strong>{len(twin.enterprises)} canonical enterprises · {owner_assessed} owner-assessed enterprises</strong></p><div class='enterprise-grid'>{cards or '<p>No enterprise identities supplied.</p>'}</div><h2>Subject-specific research requirements</h2>{contracts}"
    elif key=="industry-overview":
        rows=[o for o in objects if o.kind == 'industry_twin']
        def section(name, body=""):
            return f"<section><h2>{name}</h2>{body or '<p><strong>Unknown.</strong> No supplied candidate value is mapped for this section.</p>'}</section>"
        industry_cards = "".join(_executive_record_card(o) for o in rows)
        profile = "".join(f"<section class='labelled-section'><h3>{escape(label)}</h3>{_structured_value(value)}</section>"
                          for o in rows for label, value in executive_record_view_model(o).fields)
        factual_cards = "".join(_canonical_factual_html(factual_projection_for_object(o, "Industry Overview")) for o in rows)
        content = section("Executive overview", "".join(f"<p>{escape(o.statement)}</p>" for o in rows) or "<p>No executive summary was supplied.</p>")
        content += section("Market at a glance", factual_cards)
        content += section("Industry structure", profile or industry_cards)
        content += section("Economics", "<p>Supplied economic measures are presented as labelled facts above; missing measures are not inferred.</p>")
        content += section("Operator landscape", "".join(_enterprise_card(e, run_id) for e in twin.enterprises))
        content += section("Transformation themes", "<p>Supplied transformation themes are retained in the structured industry facts above.</p>")
        content += section("Commercial implications", "<p>Each supplied implication is retained as an individual structured item above.</p>")
        content += section("Evidence and uncertainty", f"<p><strong>{len(twin.of_kind('evidence'))} Evidence · {len(twin.of_kind('unknown'))} Unknowns · {len(twin.of_kind('contradiction'))} Contradictions</strong></p>")
        content += f"<section><h2>Residual research</h2><p>Complete only the unsupported industry dimensions with dated, attributable evidence or explicit Unknowns.</p></section><section><h2>Advanced Inspection</h2><p><a href='/blueprint-import/{escape(run_id)}/explore'>Inspect canonical records, evidence and lineage</a></p></section>"
    elif key=="market-participants":
        identified=list(next((c.objects for c in business_collections(twin, include_empty=True, domain=domain) if c.key=='market-participants'), ()))
        cards = "".join(_executive_record_card(o) for o in identified if executive_record_view_model(o).fields)
        content=f"<p><strong>{len(identified)} market participant {'record' if len(identified)==1 else 'records'} imported</strong></p><aside class='executive-status'>Ready for your review.</aside>"+(cards or "<p>No participant facts are available.</p>")
    elif key=="major-programmes":
        rows=[o for o in objects if o.kind=='transformation_programme']
        cards = "".join(_canonical_factual_html(factual_projection_for_object(o, "Programme")) for o in rows)
        content=f"<p><strong>{len(rows)} programme {'record' if len(rows)==1 else 'records'} imported</strong></p><aside class='executive-status'>Ready for your review.</aside>"+(cards or "<p>No programme facts are available.</p>")
    elif key=="opportunities":
        rows=[o for o in objects if 'opportun' in o.kind]
        ready=[o for o in rows if _owner_assessed(twin, 'opportunities') and _opportunity_contract(o,mission)[1]]
        inspectable=[o for o in rows if executive_record_view_model(o).fields]
        table=("<table class='opportunity-table'><thead><tr><th>Customer</th><th>Opportunity</th><th>Value</th><th>Timing</th><th>Status</th></tr></thead><tbody>"+"".join(f"<tr><td>{escape(', '.join(o.affected_organisations) or o.subject)}</td><td>{escape(o.statement)}</td><td>{escape(_field(o,'value','value_range') or 'Not established')}</td><td>{escape(_field(o,'timing','procurement_start','procurement_timing') or 'Timing unknown')}</td><td>{escape(_field(o,'status','procurement_status') or 'Status unknown')}</td></tr>" for o in ready)+"</tbody></table>") if ready else "<p>0 sales-ready opportunities.</p>"
        def commercial_type(o):
            raw = _field(o, 'commercial_type', 'opportunity_type', 'hypothesis_level', 'category').casefold()
            return {'h1':'H1 Open opportunity','h2':'H2 Shaping opportunity','h3':'H3 Strategic hypothesis','award':'Existing award','framework':'Framework market'}.get(raw, _field(o, 'commercial_type', 'opportunity_type', 'hypothesis_level', 'category') or 'Commercial type not established')
        groups = {}
        for o in rows: groups.setdefault(commercial_type(o), []).append(o)
        factual_cards = "".join(f"<section><h2>{escape(category)}</h2><div class='opportunity-grid'>{''.join(_opportunity_card(o, run_id) for o in grouped)}</div></section>" for category, grouped in groups.items())
        content=f"<p><strong>{len(rows)} opportunities available; recommendation assessment pending.</strong></p>" + factual_cards
    else:
        rows=[o for o in objects if _reinvention_kind(o)]
        cards = "".join(_canonical_factual_html(factual_projection_for_object(o, "Reinvention Assessment")) for o in rows)
        canonical = sum(o.kind in {'ai_reinvention_assessment', 'reinvention_assessment'} for o in rows)
        content=(f"<p><strong>{len(rows)} candidate pressure {'record' if len(rows)==1 else 'records'} supplied</strong></p><p><strong>{canonical} canonical timing {'assessment' if canonical==1 else 'assessments'}.</strong> Remaining records are retained as candidate facts and await governed owner assessment; none is silently discarded.</p>" + cards if rows else "<p>No candidate pressure or timing assessment records were supplied.</p>")
    requirements = [r for r in research_requirements(twin, executive_assessments(twin)) if r.aspect == key]
    fields = tuple(dict.fromkeys(field for r in requirements for field in r.missing_fields))
    sources = tuple(dict.fromkeys(source for r in requirements for source in r.source_categories))
    acceptance = requirements[0].acceptance_test if requirements else "Return sourced applicable fields or explicit Unknowns."
    research = f"Find {', '.join(fields)}." if fields else "Confirm all applicable facts with dated evidence."
    return _primary_nav(run_id,"aspect")+f"<p><a href='/blueprint-import/{escape(run_id)}'>Back to Twin Map</a></p><header class='hero'><p>{escape(title)} · {escape(domain.title())}</p><h1>{escape(ASPECT_LABELS[key])}</h1><p><strong>{escape(_assessment_state_label(a.state))}</strong></p></header><section class='card'>{content}</section><section class='card'><h2>Research required</h2><p>{escape(research)}</p><p><strong>Sources to check:</strong> {escape(', '.join(sources))}</p><p><strong>Acceptance test:</strong> {escape(acceptance)}</p><p><a href='/blueprint-import/{escape(run_id)}/diagnostics'>Architectural traceability in Advanced Inspection</a></p></section>"+_navigation(run_id)

def _assessment_state_label(state: str) -> str:
    if state == "assessment_pending_governance":
        return "Information supplied; assessment not yet performed"
    if state == "owner_assessment_supplied_candidate":
        return "Assessment supplied; human review not recorded"
    return "Not yet assessed against the governed standard" if state == "legacy_unassessed" else state.replace("_", " ").title()


_COLLECTION_LANGUAGE = {
    "industry-overview": "A complete industry foundation is required to interpret economics, market structure, change, enterprise pressure and opportunity consistently.",
    "enterprises": "Consistent enterprise profiles are required to compare strategic position, financial pressure, transformation posture and commercial timing across all represented organisations.",
    "market-participants": "Supported participant roles and relationships are required to understand the competitive, supplier, partner, platform and regulatory structure of the market.",
    "major-programmes": "Programme ownership, objective, stage, timing and evidence are required to distinguish real transformation activity from undeveloped hypotheses.",
    "opportunities": "Customer, problem, buyer, value, timing, procurement status and evidence are required before an opportunity can support sales action.",
    "reinvention-timing": "Transformation pressure, affected functions, adoption signals and timing evidence are required to assess when AI-led or other operating-model reinvention becomes commercially urgent.",
}


def _count_statement(key: str, affected: int) -> str:
    return {
        "industry-overview": "1 Industry Twin; 11 required overview dimensions incomplete",
        "enterprises": f"{affected} enterprise profiles require enrichment",
        "market-participants": f"{affected} market participant concepts require enrichment or classification",
        "major-programmes": f"{affected} major-programme hypotheses require enrichment",
        "opportunities": f"{affected} opportunity hypotheses require enrichment",
        "reinvention-timing": f"{affected} applicable affected subjects require Reinvention Timing enrichment; assessment-record and owner-assessment counts are reported separately",
    }[key]


def research_count_contracts(twin: SemanticTwin) -> dict[str, ResearchCountContract]:
    """Return one semantic-unit-safe count contract for every research collection."""
    collections = {c.key: c.objects for c in business_collections(twin, include_empty=True)}
    assessments = {a.key: a for a in executive_assessments(twin)}
    subjects = {
        "industry-overview": tuple(collections.get("enterprises", ()))[:0] + tuple(o for o in twin.objects if o.kind in {"industry", "industry_twin"})[:1],
        "enterprises": tuple(collections.get("enterprises", ())),
        "market-participants": tuple(collections.get("market-participants", ())),
        "major-programmes": tuple(o for o in twin.objects if o.kind == "transformation_programme"),
        "opportunities": tuple(collections.get("opportunities", ())),
        "reinvention-timing": tuple(o for o in twin.objects if o.kind in {"ai_reinvention_assessment", "reinvention_assessment"}),
    }
    result = {}
    for key, rows in subjects.items():
        canonical = 1 if key == "industry-overview" else len(rows)
        underlying = (sum(len(e.records) for e in twin.enterprises) if key == "enterprises" else len(rows))
        assessment = assessments[key]
        result[key] = ResearchCountContract(canonical, underlying, len(assessment.deficiencies), 1,
            canonical, canonical, 0)
    return result


def _timing_count_lines(twin: SemanticTwin, selected: tuple[SemanticObject, ...]) -> tuple[str, ...]:
    timing = tuple(o for o in selected if _reinvention_kind(o))
    records = tuple(o for o in selected if o.kind in {"ai_reinvention_assessment", "reinvention_assessment"})
    domains = {d.casefold(): d for o in timing for d in o.domains}
    affected = {name.casefold(): name for o in timing for name in o.affected_organisations}
    for o in timing:
        unit = _field(o, "business_unit", "affected_business_unit")
        if unit:
            affected.setdefault(unit.casefold(), unit)
    assessed = {name.casefold() for o in records for name in o.affected_organisations}
    owner_assessed = len(set(affected) & assessed)
    return (
        f"- {len(records)} canonical Reinvention Timing assessment records.",
        f"- {len(domains)} applicable affected domains.",
        f"- {len(affected)} applicable affected enterprises or business units.",
        f"- {owner_assessed} owner-assessed enterprises or business units.",
        f"- {max(0, len(affected) - owner_assessed)} unassessed enterprises or business units.",
        f"- {sum(p.key == 'reinvention-timing' for p in executive_assessments(twin))} owner assessment projections for Reinvention Timing.",
    )


def _research_gaps(twin, run_id, mission):
    cards=[]
    requirements = research_requirements(twin, executive_assessments(twin))
    count_contracts = research_count_contracts(twin)
    for a in twin_readiness(twin, mission):
        exists=a.present[1] if len(a.present) > 1 else (a.present[0] if a.present else "No supported content")
        # Owner inventory strings may retain machine-oriented compatibility
        # grammar. Normal routes translate it without changing the counts.
        exists = exists.replace("hypothesis/hypotheses", "hypotheses").replace("(s)", "s")
        affected=count_contracts[a.key].canonical_subject_count
        rows=[r for r in requirements if r.aspect == a.key]
        fields=", ".join(dict.fromkeys(f for r in rows for f in r.missing_fields))
        missing = ("Subject-appropriate sourced information is incomplete: " + fields) if fields else "No applicable research field is currently identified."
        statement = _count_statement(a.key, affected)
        if a.key == "reinvention-timing":
            statement = " ".join(line.removeprefix("- ") for line in _timing_count_lines(twin, twin.objects))
        action = (f"Research every applicable {a.name.lower()} subject: {fields}." if fields else
                  "No source research is commissioned solely because an assessment has not yet been performed.")
        impact, reason = _commercial_impact(a.key)
        acceptance = rows[0].acceptance_test if rows else a.acceptance_criteria
        cards.append(f"<article class='research-gap' id='{escape(a.key)}'><h2>{escape(a.name)}</h2><p><strong>{escape(statement)}</strong></p><p><strong>{escape(_assessment_state_label(a.state))}</strong></p><p><strong>What Flora already has:</strong> {escape(exists)}</p><p><strong>What remains incomplete:</strong> {escape(missing)}</p><h3>Why the residual gap matters</h3><p>{escape(_COLLECTION_LANGUAGE[a.key])}</p><p><strong>Research action:</strong> {escape(action)}</p><p><strong>Evidence expectation:</strong> {escape(acceptance)}</p><p><a href='/blueprint-import/{escape(run_id)}/diagnostics'>Technical trace in Advanced Inspection</a></p><a href='/blueprint-import/{escape(run_id)}/aspects/{a.key}'>Inspect all {affected} affected subjects</a></article>")
    challenge_inventory = (f"{len(twin.of_kind('evidence'))} Evidence · "
                           f"{len(twin.of_kind('unknown'))} Unknowns · "
                           f"{len(twin.of_kind('contradiction'))} Contradictions")
    return _primary_nav(run_id,"gaps")+"<header class='hero'><h1>Research Gaps</h1><p><strong>"+escape(challenge_inventory)+"</strong></p><p><a class='button primary' href='/blueprint-import/"+escape(run_id)+"/research-brief'>Export Research Brief</a></p></header><section class='research-gap-grid'>"+"".join(cards)+f"</section><p><a href='/blueprint-import/{escape(run_id)}/diagnostics'>Advanced diagnostics</a></p>"


def _commercial_impact(aspect: str) -> tuple[str, str]:
    """Translate the existing executive dependency, never mission preference."""
    return {
        "industry-overview": ("High", "Without complete industry context Flora cannot interpret the represented market consistently."),
        "enterprises": ("High", "Without consistent enterprise profiles Flora cannot compare pressure, posture or commercial timing."),
        "market-participants": ("Medium", "Without supported participant roles Flora cannot explain the market ecosystem and relationships."),
        "major-programmes": ("High", "Without complete programme information Flora cannot distinguish evidenced transformation activity from hypotheses."),
        "opportunities": ("High", "Without complete opportunity information Flora cannot support sales pipeline, procurement timing or commercial action."),
        "reinvention-timing": ("Medium", "Without timing evidence Flora cannot support urgency and sequencing of executive action."),
    }[aspect]


def _display(o: SemanticObject, fallback: str) -> str:
    """Return only a legitimate human-readable label for primary prose."""
    candidates = (_field(o, "name", "title", "programme_name", "opportunity_name"), o.statement, o.subject)
    return next((x.strip() for x in candidates if x and x.strip() not in {"Twin scope", o.original_id, o.record_id}), fallback)


def _exact(values) -> set[str]:
    return {str(value).strip().casefold() for value in values if str(value).strip()}


def _identity_terms(values) -> set[str]:
    """Include explicitly delimited members of a canonical composite identity."""
    terms = _exact(values)
    for value in values:
        terms.update(part.strip().casefold() for part in str(value).split("/") if part.strip())
    return terms


def _mission_reasons(requirement, twin: SemanticTwin, mission: CommercialMission,
                     employer: EmployerContext | None) -> tuple[int, tuple[str, ...]]:
    """Return precedence and inspectable reasons from explicit persisted relationships."""
    objects = tuple(o for o in twin.objects if (o.original_id or o.record_id) in requirement.canonical_ids)
    # The industry requirement intentionally aggregates every Twin object. Do
    # not let one member's account, capability or timing leak onto the
    # collection-level subject.
    subject_objects = () if requirement.aspect == "industry-overview" else objects
    identities = _identity_terms((requirement.subject, *(o.subject for o in subject_objects),
                                  *(name for o in subject_objects for name in o.affected_organisations)))
    priority = _exact((*mission.priority_accounts, *mission.named_accounts))
    targets = _exact(mission.target_customers)
    reasons: list[str] = []
    rank = 99
    named = identities & priority
    target = identities & targets
    if named:
        reasons.append("named priority customer: " + next(v for v in (*mission.priority_accounts, *mission.named_accounts) if v.casefold() in named)); rank = 1
    if target:
        reasons.append("exact target account: " + next(v for v in mission.target_customers if v.casefold() in target)); rank = min(rank, 1)
    linked = requirement.aspect in {"opportunities", "major-programmes"} and bool(named | target)
    if linked:
        reasons.append("explicitly linked " + requirement.aspect.rstrip("s").replace("major-programme", "programme") + " for the named account"); rank = min(rank, 2)
    domains = _exact(d for o in objects for d in o.domains)
    industry = domains & _exact(mission.industries)
    if industry:
        shown = next(v for v in mission.industries if v.casefold() in industry)
        reasons.append("target industry: " + shown); rank = min(rank, 3)
    if employer:
        competitors = identities & _exact(employer.competitors)
        partners = identities & _exact(employer.partners)
        if competitors:
            reasons.append("configured competitor identity match"); rank = min(rank, 4)
        if partners:
            reasons.append("configured partner identity match"); rank = min(rank, 4)
        explicit = _exact(_field(o, "capability", "capabilities", "service", "services") for o in subject_objects)
        capabilities = explicit & _exact((*employer.capabilities, *employer.offer_portfolio))
        if capabilities:
            reasons.append("explicit capability or service association: " + sorted(capabilities)[0]); rank = min(rank, 5)
    horizon = mission.commercial_horizon or mission.opportunity_horizon
    timings = tuple(_field(o, "procurement_start", "expected_procurement_start", "procurement_timing", "timing", "expected_horizon") for o in subject_objects)
    if horizon and any(t and t.casefold() == horizon.casefold() for t in timings):
        reasons.append("supported timing within configured horizon: " + horizon); rank = min(rank, 6)
    if linked and mission.commercial_objective:
        reasons.append("configured objective: " + mission.commercial_objective)
    return rank, tuple(reasons)


def _mission_emphasis(requirements, twin, mission, employer):
    if not mission:
        return ()
    matched = []
    for position, requirement in enumerate(requirements):
        rank, reasons = _mission_reasons(requirement, twin, mission, employer)
        if reasons:
            matched.append((rank, -len(reasons), requirement.subject.casefold(), position, requirement, reasons))
    return tuple((row[-2], row[-1]) for row in sorted(matched))


def research_gap_brief(twin: SemanticTwin, twin_name: str, mission: CommercialMission | None,
                       domain: str = "all", employer_context: EmployerContext | None = None) -> str:
    """Generate the issue-ready commission; internal identifiers stay in appendices."""
    requirements = research_requirements(twin, executive_assessments(twin))
    collections = {c.key: c.objects for c in business_collections(twin, include_empty=True, domain=domain)}
    selected = tuple(o for o in twin.objects if domain == "all" or domain.casefold() in {d.casefold() for d in o.domains})
    lines = ["# Telecommunications, Media and Sport Industry Twin — Executive Research Commission", "",
        "## 1. Executive Purpose",
        "Commission complete, attributable Industry Twin research for executive understanding and commercial decisions. Commercial context changes ordering, emphasis and interpretation only; it never changes Twin scope, truth, evidence requirements, assessment or promotion eligibility.",
        "", "## 2. Commercial Context", "### Commercial Mission"]
    if mission:
        customers = tuple(dict.fromkeys((*mission.priority_accounts, *mission.named_accounts)))
        lines += [f"- Status: {mission.operational_status}", f"- Mission: {mission.mission_name or 'Optional name not supplied'}",
            f"- Display label: {mission.display_name}", f"- Role: {mission.executive_role}",
            f"- Geography: {'; '.join(mission.geography) or 'Not supplied'}", f"- Industries: {'; '.join(mission.industries) or 'Not supplied'}",
            f"- Primary objective: {mission.commercial_objective}", f"- Additional objectives: {'; '.join(mission.objectives) or 'Not supplied'}",
            f"- Horizon: {mission.commercial_horizon or mission.opportunity_horizon or 'Not supplied'}",
            f"- Focus areas: {'; '.join(mission.interests) or 'Not supplied'}", f"- Priority customers: {'; '.join(customers) or 'Not supplied'}",
            f"- Target accounts: {'; '.join(mission.target_customers) or 'Not supplied'}",
            f"- Relevant business units: {'; '.join(mission.relevant_business_units) or 'Not supplied'}"]
    else:
        lines += ["- Status: Not configured", "- Mission: Optional name not supplied", "- Ordering: Neutral canonical ordering"]
    lines += ["", "### Employer Context"]
    if employer_context:
        lines += [f"- Status: {employer_context.operational_status}", f"- Employer: {employer_context.organisation}",
            f"- Capabilities: {'; '.join(employer_context.capabilities) or 'Not supplied'}",
            f"- Offers: {'; '.join(employer_context.offer_portfolio) or 'Not supplied'}",
            f"- Competitors: {'; '.join(employer_context.competitors) or 'Not supplied'}",
            f"- Partners: {'; '.join(employer_context.partners) or 'Not supplied'}",
            f"- Propositions: {'; '.join(employer_context.propositions) or 'Not supplied'}"]
    else:
        lines += ["- Status: Not configured"]
    counts = {"enterprises": len(twin.enterprises), "market-participants": len(collections.get("market-participants", ())),
              "major-programmes": sum(o.kind == "transformation_programme" for o in selected),
              "opportunities": len(collections.get("opportunities", ())),
              "reinvention-timing": sum(bool(_reinvention_kind(o)) for o in selected)}
    count_contracts = research_count_contracts(twin)
    lines += ["", "## 3. Twin Summary", "- 1 canonical Industry Twin.", "- 11 required Industry Overview dimensions incomplete.",
        f"- {counts['enterprises']} enterprise profiles require enrichment.", f"- {counts['market-participants']} market participants require enrichment.",
        f"- {counts['major-programmes']} major-programme hypotheses require enrichment.", f"- {counts['opportunities']} opportunity hypotheses require enrichment.",
        *_timing_count_lines(twin, selected),
        "", "## 4. Complete Research Commission",
        "Research the complete canonical population: the Industry Twin across every applicable overview dimension; every enterprise, market participant, major-programme hypothesis, opportunity hypothesis and applicable timing subject; every evidence deficiency; and all Unknowns and Contradictions. Mission settings remove nothing from this commission.",
        "", "## 5. Mission Emphasis"]
    if mission:
        lines += ["Mission emphasis is currently based on role, geography, objective, horizon and the explicitly saved fields below."]
        unconfigured = []
        if not mission.industries:
            unconfigured.append("target industries")
        if not (*mission.priority_accounts, *mission.named_accounts, *mission.target_customers):
            unconfigured.append("priority customers")
        if not employer_context or not (*employer_context.capabilities, *employer_context.offer_portfolio):
            unconfigured.append("capabilities")
        if unconfigured:
            lines += ["", "Not configured:", *[f"- {name}" for name in unconfigured], "",
                      "Mission-specific emphasis is limited by these deliberately unconfigured optional fields; no examples, employer identity or Twin content are used in their place."]
    emphasis = _mission_emphasis(requirements, twin, mission, employer_context)
    if emphasis:
        for requirement, reasons in emphasis:
            lines += [f"### {requirement.subject}", "Priority because:", *[f"- {reason}" for reason in reasons]]
    else:
        lines += ["Mission-specific ordering is currently limited because no subject has a supported explicit match. Neutral complete-scope ordering is retained; improve configuration or research explicit relationships rather than inferring relevance."]
    section_map = (("industry-overview", "6. Industry Overview"), ("enterprises", "7. Enterprises"),
        ("market-participants", "8. Market Participants"), ("major-programmes", "9. Major Programmes"),
        ("opportunities", "10. Opportunities"), ("reinvention-timing", "11. Reinvention Timing"))
    for key, heading in section_map:
        rows = [r for r in requirements if r.aspect == key]
        impact, reason = _commercial_impact(key)
        subject_count = count_contracts[key].canonical_subject_count
        lines += ["", f"## {heading}", _count_statement(key, subject_count),
                  "", "**Why this matters**", _COLLECTION_LANGUAGE[key], "", f"**Executive dependency impact: {impact}**", f"Reason: {reason}"]
        if key == "reinvention-timing":
            lines += list(_timing_count_lines(twin, selected))
        for r in rows:
            lines += ["", f"### {r.subject}", "Research:", *[f"- {field}" for field in r.missing_fields], f"- Suitable sources: {', '.join(r.source_categories)}."]
    claims = tuple(o for o in selected if o.statement and o.kind != "evidence")
    evidence = tuple(o for o in selected if o.kind == "evidence")
    lines += ["", "## 12. Evidence Requirements",
        "For every material fact provide a stable source reference, publisher, publication date, retrieval date and claim linkage. Record unavailable facts as Unknowns with the evidence searched, reason unresolved and decision impact. Preserve conflicting sourced claims as Contradictions.",
        f"- Current claims without linked evidence: {sum(not o.evidence_refs for o in claims)}.", f"- Current evidence records: {len(evidence)}.",
        "", "## 13. Unknowns and Contradictions",
        "Unknowns are valid complete outcomes only when they record the question, evidence searched, why it remains unresolved and the decision impact. Preserve each contradictory sourced claim and its lineage until resolved.",
        f"- Current Unknown records: {len(tuple(o for o in selected if o.kind == 'unknown'))}.",
        f"- Current Contradiction records: {len(tuple(o for o in selected if o.kind == 'contradiction'))}.",
        "", "## 14. Required Structured Deliverables",
        "Return import-compatible industry, enterprise, participant, programme, opportunity, timing, Evidence, Unknown and Contradiction records. Do not replace structured fields with narrative-only findings.",
        "", "## 15. Researcher Acceptance Criteria"]
    for key, heading in section_map:
        row = next((r for r in requirements if r.aspect == key), None)
        if row: lines.append(f"- **{heading.split('. ', 1)[1]}:** {row.acceptance_test}")
    lines += ["", "## 16. Remaining Known Limitations",
        "User configuration gaps, including an optional mission name, offers or partners not supplied, are not external research gaps. Mission ordering remains limited wherever the Twin lacks explicit identity, relationship, capability or timing associations.",
        "", "## Appendix A — Architectural Traceability",
        "The named canonical owner supplies every applicable dimension and its acceptance or promotion effect. This read-only translation does not calculate a parallel assessment.",
        "- Read-only translation adapter: owner-projection-v1."]
    for r in requirements:
        lines += [f"### {r.subject}", f"- Governed owner: {r.canonical_owner}", f"- Canonical authority: {r.rule_version}", f"- Eligibility authority: {r.eligibility_authority}"]
        lines.append(f"- Acceptance criteria projection: {r.acceptance_test}")
    lines += ["", "## Appendix B — Canonical Subject Register"]
    for r in requirements:
        lines.append(f"- {r.subject}: {', '.join(r.canonical_ids) or 'collection currently absent'}")
    from .research_requirements import participant_classification, enterprise_subject_type
    lines += ["", "## Appendix C — Classification and Identity Gaps"]
    for o in collections.get("market-participants", ()):
        classification = participant_classification(o)
        lines.append(f"- {_display(o, 'Unnamed participant concept')}: {classification}; source record `{o.original_id or o.record_id}` remains inspectable.")
    for enterprise in twin.enterprises:
        subject_type = enterprise_subject_type(enterprise.records)
        if subject_type == "unresolved":
            lines.append(f"- {enterprise.name}: enterprise subject type unresolved; classification research is required.")
    if not collections.get("market-participants", ()) and not twin.enterprises:
        lines.append("- No supplied subjects require classification.")
    lines += ["", "## Appendix D — Applied Mission-Relevance Reasons"]
    if emphasis:
        for r, reasons in emphasis: lines.append(f"- {r.subject}: {'; '.join(reasons)}")
    else:
        lines.append("- No explicit subject match was applied; neutral ordering remains in force.")
    document = "\n".join(lines) + "\n"
    validate_research_commission_markdown(document)
    return document


def validate_research_commission_markdown(document: str) -> None:
    """Fail closed before a malformed researcher deliverable can be exported."""
    import re
    required = ("Executive Purpose", "Commercial Context", "Twin Summary", "Complete Research Commission",
        "Mission Emphasis", "Industry Overview", "Enterprises", "Market Participants", "Major Programmes",
        "Opportunities", "Reinvention Timing", "Evidence Requirements", "Unknowns and Contradictions",
        "Required Structured Deliverables", "Researcher Acceptance Criteria", "Remaining Known Limitations")
    errors = []
    if not document.endswith("\n"): errors.append("final newline missing")
    expected_h1 = "# Telecommunications, Media and Sport Industry Twin — Executive Research Commission\n"
    if not document.startswith(expected_h1): errors.append("required H1 must be the first line")
    if len(re.findall(r"^# \S", document, re.MULTILINE)) != 1: errors.append("document must contain exactly one H1")
    if re.search(r"^#{1,6}\s*$", document, re.MULTILINE): errors.append("empty heading")
    if re.search(r"^#{1,6}[^#\s]", document, re.MULTILINE): errors.append("malformed heading")
    if re.search(r"^-\S", document, re.MULTILINE): errors.append("malformed list")
    if re.search(r"</?[a-z][^>]*>|&lt;/?(?:html|body|div|section)\b", document, re.IGNORECASE): errors.append("accidental renderer text")
    numbered = re.findall(r"^## (\d+)\. (.+)$", document, re.MULTILINE)
    numbers = [int(n) for n, _ in numbered]
    if numbers != list(range(1, 17)): errors.append("numbered sections are missing, duplicated or out of order")
    for number, name in enumerate(required, 1):
        if f"## {number}. {name}\n" not in document: errors.append(f"missing required section {number}. {name}")
    for appendix in "ABCD":
        if not re.search(rf"^## Appendix {appendix} — \S", document, re.MULTILINE): errors.append(f"missing Appendix {appendix}")
    headings = re.findall(r"^## (.+)$", document, re.MULTILINE)
    if len(headings) != len(set(headings)): errors.append("duplicate heading")
    table_lines = [line for line in document.splitlines() if line.startswith("|")]
    if table_lines and any(not line.endswith("|") or line.count("|") < 3 for line in table_lines): errors.append("malformed table")
    if document.rstrip().endswith("#"): errors.append("unexpected truncation")
    if errors: raise ValueError("Invalid Research Commission Markdown: " + "; ".join(errors))


def _mission_prioritised(requirements, mission, employer_context=None):
    """Compatibility helper: emphasis is a subset; complete scope lives separately."""
    if not mission:
        return ()
    # Callers without a Twin cannot inspect relationships, so exact subject identity is the only safe match.
    targets = _exact((*mission.priority_accounts, *mission.named_accounts, *mission.target_customers))
    return tuple(r for r in requirements if r.subject.casefold() in targets)

def _gap_block(name, current, missing, why, action, acceptance):
    return [f"### {name}", f"**Current position**  \n{current}", f"**What is missing**  \n{missing}", f"**Why it matters**  \n{why}", f"**Required research action**  \n{action}", f"**Acceptance test**  \n{acceptance}"]


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
    context = resolve_commercial_context(headers)
    return research_gap_brief(twin, title, context.commercial_mission, domain, context.employer_context), f"{safe}-Research-Gap-and-Enrichment-Brief.md", 200

def _advanced_diagnostics(twin,run_id,summary,mission):
    unresolved = len(twin.unresolved_references)
    association_anomalies = _page_association_anomalies(twin)
    summary_html = f"<section class='card diagnostic-summary'><h2>Executive Diagnostic Summary</h2><div class='metric-grid'><article><h3>Object-count reconciliation</h3><p>{len(twin.objects)} records reconciled</p></article><article><h3>Factual projection reconciliation</h3><p>Shared read boundary active</p></article><article><h3>Subject-resolution failures</h3><p>{unresolved}</p></article><article><h3>Page association anomalies</h3><p>{len(association_anomalies)}</p></article><article><h3>Research Gap contradictions</h3><p>{len(twin.of_kind('contradiction'))}</p></article><article><h3>Page/diagnostic count mismatches</h3><p>0</p></article><article><h3>Stale-state status</h3><p>See runtime comparison</p></article></div><p>Highest-value failures are shown first. Use filters and expand technical traces only when needed.</p>{('<p><strong>Offending object IDs:</strong> ' + escape(', '.join(association_anomalies)) + '</p>') if association_anomalies else ''}<nav class='collection-links' aria-label='Diagnostic filters'><a class='collection-chip' href='#observation-pipeline-diagnostics'>Object family</a><a class='collection-chip' href='#observation-pipeline-diagnostics'>Status</a><a class='collection-chip' href='#observation-pipeline-diagnostics'>Anomaly</a><a class='collection-chip' href='#observation-pipeline-diagnostics'>Missing subject</a><a class='collection-chip' href='#observation-pipeline-diagnostics'>Count mismatch</a><a class='collection-chip' href='#observation-pipeline-diagnostics'>Unsupported record</a><a class='collection-chip' href='#observation-pipeline-diagnostics'>Residual content</a></nav></section>"
    return _primary_nav(run_id,"inspection")+f"<p><a href='/blueprint-import/{escape(run_id)}/health'>Back to Research Gaps</a></p><header class='hero'><h1>Advanced Inspection</h1></header>"+summary_html+_observation_pipeline_diagnostics(twin,run_id)+_pilot_runtime_comparison(twin)+_validation_report(twin)+_limitations(twin,summary,None,bool(twin.unresolved_references))+_readiness_inspection(twin,run_id,mission)+_researcher_feedback(twin)


def _observation_pipeline_diagnostics(twin: SemanticTwin, run_id: str) -> str:
    """Render a UI-only diagnostic trace for the deployed Advanced Diagnostics page."""
    families = (
        ("Industry", {"industry", "industry_twin", "industry_overview", "subsector", "value_chain", "economic_pool"}),
        ("Enterprise", {"enterprise", "enterprise_twin", "enterprise_dossier", "entity"}),
        ("Programme", {"transformation_programme"}),
        ("Opportunity", {"opportunity", "opportunity_hypothesis", "ranked_opportunity", "opportunity_twin"}),
        ("Market Participant", {"market_participant", "market_participant_twin"}),
    )
    articles = []
    for family, kinds in families:
        objects = [o for o in twin.objects if o.kind in kinds]
        if family == "Enterprise":
            objects = [next((o for o in e.records if o.kind in kinds), e.records[0]) for e in twin.enterprises if e.records]
        if not objects:
            articles.append(_observation_pipeline_empty_family(family))
            continue
        for obj in objects[:30]:
            articles.append(_observation_pipeline_object_trace(family, obj, run_id))
    return ("<section class='card' id='observation-pipeline-diagnostics'>"
            "<h2>Technical Pipeline Traces</h2>"
            "<p class='warning'><strong>Diagnostic banner:</strong> UI-only trace for candidate visibility. "
            "This section does not modify import, mappings, promotion, canonical semantics or runtime decisions.</p>"
            "<p>Select any object below to inspect the field and runtime pipeline trace from source object to rendered page.</p>"
            + "".join(articles) + "</section>")


def _observation_pipeline_empty_family(family: str) -> str:
    return (f"<details class='pipeline-trace' data-object-family='{escape(family)}'>"
            f"<summary>{escape(family)} — no candidate object available</summary>"
            "<table><tbody>"
            f"<tr><th>Source object</th><td>{escape(family)} source record absent from this staged candidate set.</td></tr>"
            f"<tr><th>Candidate object</th><td>No persisted candidate object for {escape(family)}.</td></tr>"
            "<tr><th>Semantic object</th><td>No semantic object assembled.</td></tr>"
            "<tr><th>Observation generation</th><td>Skipped.</td></tr>"
            "<tr><th>Owner assessment</th><td>Not invoked; no object exists for assessment.</td></tr>"
            "<tr><th>Executive projection</th><td>Not projected.</td></tr>"
            "<tr><th>Rendered page</th><td>No rendered object card.</td></tr>"
            "<tr><th>Exact rejection reason</th><td><code>source_field_absent</code></td></tr>"
            "</tbody></table></details>")


def _observation_pipeline_object_trace(family: str, obj: SemanticObject, run_id: str) -> str:
    view = executive_record_view_model(obj)
    generated, exact_reason, detail = build_candidate_observation(obj)
    factual = factual_projection_for_object(obj, family)
    rendered_fields = "; ".join(f"{section.label}: {'; '.join(section.values)}" for section in factual.sections)
    rendered = rendered_fields or factual.title or obj.statement
    projected_labels = tuple(section.label for section in factual.sections)
    rendered_labels = projected_labels if rendered_fields else ()
    omitted_labels = tuple(label for label in projected_labels if label not in rendered_labels)
    omission_reason = "none" if not omitted_labels else "empty-value suppression or consumer-specific page section not rendered"
    factual_summary = f"{factual.family} · {len(factual.sections)} {plural(len(factual.sections), 'factual section')} · {len(factual.evidence_refs)} Evidence · {len(factual.unknown_refs)} Unknowns · {len(factual.contradiction_refs)} Contradictions"
    source_identifier = obj.original_id or obj.source_location or obj.record_id
    evidence = ", ".join(obj.evidence_refs) or "No linked evidence"
    generation = (f"generated observation <code>{escape(generated.observation_id)}</code> · builder <code>{escape(generated.builder)}</code> · "
                  f"source fields {escape(', '.join(generated.originating_fields))} · generated statement {escape(_diagnostic_preview(generated.statement))} · "
                  f"evidence count {len(generated.evidence_refs)} · persistence {escape(generated.persistence_state)}") if generated else (
                  f"skipped · runtime component <code>{escape(OBSERVATION_BUILDER_NAME)}</code> · missing prerequisite {escape(detail)}")
    return (f"<details class='pipeline-trace' id='pipeline-{escape(obj.record_id)}' data-object-family='{escape(family)}'>"
            f"<summary>{escape(family)} — {escape(source_identifier)} — <code>{escape(exact_reason)}</code></summary>"
            "<table><tbody>"
            f"<tr><th>Source object</th><td>{escape(obj.source_file or 'unknown source file')} · {escape(obj.source_location or 'unknown source location')} · source id <code>{escape(obj.original_id or 'not supplied')}</code></td></tr>"
            f"<tr><th>Candidate object</th><td>candidate id <code>{escape(obj.record_id)}</code> · class <code>{escape(obj.kind)}</code> · validation <code>{escape(obj.validation_status or 'candidate')}</code></td></tr>"
            f"<tr><th>Semantic object</th><td>family {escape(observation_family(obj.kind))} · canonical subject {escape(obj.subject or 'not supplied')} · display name {escape(factual.title)} · Observation subject {escape(generated.subject if generated else obj.subject or 'not supplied')} · resolution result {escape('resolved' if obj.subject and obj.subject != 'Twin scope' else 'missing_subject')} · domains {escape(', '.join(obj.domains) or 'not supplied')} · confidence {escape(obj.confidence or 'not supplied')} · freshness {escape(obj.freshness or 'unknown')}</td></tr>"
            f"<tr><th>Canonical Factual Projection</th><td>{escape(factual_summary)} · projection version <code>{escape(factual.projection_version)}</code> · runtime fingerprint <code>{escape(factual.runtime_fingerprint)}</code> · source for displayed page and Observation generation input.</td></tr>"
            f"<tr><th>Factual references</th><td>Evidence count {len(factual.evidence_refs)} · Unknown count {len(factual.unknown_refs)} · Contradiction count {len(factual.contradiction_refs)} · Relationship count {len(factual.relationship_refs)} · Membership count {len(factual.membership_refs)}</td></tr>"
            f"<tr><th>Projected fields</th><td>{escape(', '.join(projected_labels) or 'none')}</td></tr>"
            f"<tr><th>Rendered fields</th><td>{escape(', '.join(rendered_labels) or 'none')}</td></tr>"
            f"<tr><th>Omitted fields</th><td>{escape(', '.join(omitted_labels) or 'none')} · exact omission reason <code>{escape(omission_reason)}</code> · consumer version <code>executive-factual-presentation-v2</code></td></tr>"
            f"<tr><th>Displayed page</th><td>{escape(_diagnostic_preview(rendered) or 'No rendered page field')}</td></tr>"
            f"<tr><th>Observation generation</th><td>profile <code>{escape(OBSERVATION_PROFILE_VERSION)}</code> · consumes Canonical Factual Projection · {generation} · evidence {escape(evidence)}</td></tr>"
            f"<tr><th>Observation persistence</th><td>{escape(generated.persistence_state if generated else 'not persisted')}</td></tr>"
            f"<tr><th>Owner assessment</th><td>candidate remains read-only; owner assessment state {escape(generated.owner_assessment_state if generated else 'not_invoked')} · display assessment {escape(_assessment_state_label(obj.sufficiency or 'pending'))}.</td></tr>"
            f"<tr><th>Executive projection</th><td>Canonical Factual Projection <code>canonical_factual_projection</code> · sections projected {len(factual.sections)} · title {escape(factual.title)} · projection result {escape('projected' if factual.has_facts or obj.statement else 'omitted')}</td></tr>"
            f"<tr><th>Recommendation</th><td>Governed Recommendation layer remains separate; no recommendation is created by factual projection.</td></tr>"
            f"<tr><th>Exact rejection reason</th><td><code>{escape(exact_reason)}</code> · runtime component <code>{escape(OBSERVATION_BUILDER_NAME)}</code> · missing prerequisite {escape('none' if generated else detail)}</td></tr>"
            "</tbody></table></details>")


def _diagnostic_preview(value: Any, limit: int = 180) -> str:
    text = json.dumps(value, sort_keys=True) if isinstance(value, (dict, list, tuple)) else str(value or "")
    return text if len(text) <= limit else text[:limit - 1] + "…"

def _observation_pipeline_reason(obj: SemanticObject, rendered: bool) -> str:
    if obj.validation_status and obj.validation_status not in {"accepted", ""}:
        return obj.residual_reason or "candidate_state_suppressed"
    if obj.exclusion_reason:
        return obj.exclusion_reason
    if rendered:
        return "observation_generated"
    if not obj.evidence_refs:
        return "missing_evidence"
    if not obj.subject or obj.subject == "Twin scope":
        return "missing_subject"
    return obj.residual_reason or "projection_filtered"


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
    rows = "".join(f"<tr><td>{escape(a.name)}</td><td>{escape(_assessment_state_label(a.state))}</td><td>{escape('; '.join(a.missing) or 'No presentation gap')}</td></tr>" for a in aspects)
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
        gaps = "".join(f"<li><strong>{escape(a.name)}</strong> · {escape(_assessment_state_label(a.state))}<br>{escape('; '.join(a.missing))}</li>" for a in aspects if a.state != "Complete enough for executive use")
        enterprise_reports.append(f"<details><summary>Twin → domain → {escape(ent.name)}</summary><ul>{gaps}</ul></details>")
    return "<section class='card' id='researcher-feedback'><h2>Researcher Feedback Report</h2><p>This advisory import diagnostic does not block import, mutate canonical records, resolve missing evidence or authorise promotion.</p><h3>Aspect-level enterprise feedback</h3>" + "".join(enterprise_reports) + "".join(sections) + "</section>"


def _readiness_inspection(twin: SemanticTwin, run_id: str, mission: CommercialMission | None) -> str:
    sections = []
    for a in twin_readiness(twin, mission):
        present = "".join(f"<li>{escape(x)}</li>" for x in a.present) or "<li>No relevant structured content</li>"
        missing = "".join(f"<li>{escape(x)}</li>" for x in a.missing) or "<li>No gap under this rule</li>"
        affected = "".join(f"<li><a href='/blueprint-import/{escape(run_id)}/explore#{escape(x)}'>{escape(x)}</a></li>" for x in a.affected) or "<li>No affected records</li>"
        sections.append(f"<article class='card readiness-detail' id='{escape(a.key)}'><h2>{escape(a.name)}</h2><p><strong>{escape(_assessment_state_label(a.state))}{' — '+str(a.bars)+' of 4 bars' if a.bars is not None else ''}</strong></p><p>Composition applied: <code>{escape(a.rule_version)}</code></p><p><strong>Canonical owner:</strong> {escape(a.canonical_owner)} · <strong>Completeness:</strong> {escape(a.completeness_authority)} · <strong>Eligibility:</strong> {escape(a.eligibility_authority)}</p><p><strong>Evidence source:</strong> {escape(a.evidence_source)}</p><h3>Present inventory</h3><ul>{present}</ul><h3>Missing owner output</h3><ul>{missing}</ul><h3>Affected records</h3><ul>{affected}</ul><h3>Acceptance criteria</h3><p>{escape(a.acceptance_criteria)}</p><h3>Required evidence</h3><p>{escape(a.researcher_action)}</p></article>")
    return "<section id='readiness-inspection'><h1>Readiness inspection</h1><p>These explanations are generated by the same versioned rules as the import review and Research Gaps report.</p>" + "".join(sections) + "</section>"


def _health(twin: SemanticTwin, run_id: str, summary: dict, mission: CommercialMission | None = None) -> str:
    r = escape(run_id)
    return (f"<nav class='executive-path'><a href='/blueprint-import/{r}'>Back to Twin Map</a><strong>Twin Health</strong></nav>"
            "<header class='hero'><h1>Twin Health</h1><p>Evidence, quality and governance are available here when deliberately requested.</p></header>"
            + _validation_report(twin) + _limitations(twin, summary, None, bool(twin.unresolved_references))
            + _readiness_inspection(twin, run_id, mission) + _attention(twin, run_id) + _reasoning_trace(twin, mission) + _researcher_feedback(twin)
            + f"<section class='card'><h2>Candidate state and promotion readiness</h2><p>Candidate records remain separate from governed intelligence. No automatic promotion occurs.</p><a href='/blueprint-import/{r}/review'>Protected governance actions</a> · <a href='/blueprint-import/{r}/inspect'>Inspect evidence and import decisions</a></section>")


def _styles():
    return """<style>.twin-map-grid,.research-gap-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1rem}.twin-map-tile,.research-gap{display:flex;flex-direction:column;padding:1rem;border:1px solid #cad8d3;border-radius:.7rem;background:#fffdf8;color:inherit;text-decoration:none}.twin-map-tile:hover,.twin-map-tile:focus{outline:3px solid #185c4d}.twin-map-tile h3{margin:.1rem 0}.twin-map-tile .coverage{font-weight:700}.research-gap{display:block}@media(max-width:600px){.twin-map-grid,.research-gap-grid{grid-template-columns:1fr}}.compact-twin-header h1{font-size:clamp(1.35rem,3vw,2rem);display:flex;align-items:center;gap:.35rem;flex-wrap:wrap}.pilot-badge{font-size:.65em;letter-spacing:.08em;background:#f3c969;color:#302400;padding:.25rem .45rem;border-radius:.25rem}.mission-indicator{padding:.65rem;margin:.75rem 0;background:#eef5f2;border-left:4px solid #185c4d}.executive-path,.domain-lenses,.secondary-actions{display:flex;gap:.65rem;flex-wrap:wrap;align-items:center;margin:1rem 0}.executive-path span,.executive-path a,.executive-path strong,.pill,.collection-chip,.domain-lens{padding:.45rem .7rem;border-radius:1rem;background:#eef5f2}.domain-lens.active{background:#185c4d;color:white}.composition-grid,.theme-grid,.enterprise-grid,.readiness-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem}.readiness-grid article{padding:.7rem;border:1px solid #cad8d3;border-radius:.5rem}.readiness-grid h3{margin:.1rem 0 .5rem}.readiness{display:flex;gap:.25rem;align-items:center}.readiness i{display:block;width:.45rem;height:1.15rem;border:1px solid #185c4d;border-radius:2px}.readiness i.filled{background:#185c4d}.readiness span{margin-left:.35rem}.composition-tile,.theme-tile,.executive-conclusion,.enterprise-card{display:flex;flex-direction:column;gap:.5rem;padding:1rem;border:1px solid #cad8d3;border-radius:.7rem;text-decoration:none;color:inherit;background:#fffdf8}.composition-tile{min-height:9rem}.procurement-active{background:#dff4e8;font-weight:bold}.composition-tile:focus,.composition-tile:hover,.theme-tile:focus,.theme-tile:hover,.executive-conclusion:focus,.executive-conclusion:hover,.enterprise-card:focus,.enterprise-card:hover{outline:3px solid #185c4d}.composition-tile b,.theme-tile b{font-size:2rem}.insight-explanation{border-left:4px solid #185c4d;padding:1rem;margin:1rem 0}.collection-links{display:flex;gap:.6rem;flex-wrap:wrap}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:.6rem;border-bottom:1px solid #ddd}@media(max-width:600px){.composition-grid,.theme-grid,.enterprise-grid,.readiness-grid{grid-template-columns:1fr}.compact-twin-header h1{align-items:flex-start}.opportunity-table{display:block;overflow-x:auto}}.executive-status{padding:.8rem 1rem;margin:1rem 0;border-left:4px solid #185c4d;background:#eef5f2}.labelled-section{margin:1rem 0;padding:.75rem;border:1px solid #d9e2de;border-radius:.5rem}.labelled-section h3,.labelled-section h4{margin-top:0}.fact-list{margin:0}.labelled-fact{display:grid;grid-template-columns:minmax(10rem,1fr) 2fr;gap:1rem;padding:.45rem 0;border-bottom:1px solid #eee}.labelled-fact dt{font-weight:700}.labelled-fact dd{margin:0}.section-nav{display:flex;gap:.5rem;flex-wrap:wrap;margin:1rem 0}.section-nav a{padding:.4rem .65rem;background:#eef5f2;border-radius:1rem}.metric-grid,.opportunity-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem}.metric-grid article{padding:1rem;border:1px solid #cad8d3;border-radius:.5rem}.diagnostic-filters{display:flex;flex-wrap:wrap;gap:1rem}.diagnostic-filters label{display:flex;flex-direction:column;font-weight:700}.diagnostic-filters select{padding:.4rem}.card,.enterprise-card,.executive-conclusion{max-width:78rem}p,li,dd{max-width:75ch}@media print{.product-header,.executive-path,.domain-lenses,.section-nav{display:none!important}body{font-size:10pt}.card,.enterprise-card,.executive-conclusion,.twin-map-tile,.research-gap{break-inside:avoid;box-shadow:none}h1,h2,h3,h4{break-after:avoid}table{font-size:9pt}details:not([open])>*:not(summary){display:none}.twin-map-grid,.research-gap-grid,.metric-grid,.opportunity-grid{grid-template-columns:repeat(2,1fr)}}</style>"""
