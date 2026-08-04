"""Human research contracts projected from governed assessment output.

This is a read-only translation adapter.  The field schedules below are
presentation bindings to the named owner contracts; they are not completeness
rules and never create, score, or pass an assessment.
"""
from __future__ import annotations

from dataclasses import dataclass

from .intelligence_projection import ExecutiveAssessmentProjection
from .semantic_twin import SemanticObject, SemanticTwin, business_collections


@dataclass(frozen=True)
class ResearchRequirement:
    aspect: str
    subject: str
    canonical_ids: tuple[str, ...]
    missing_fields: tuple[str, ...]
    why: str
    source_categories: tuple[str, ...]
    structured_output: str
    acceptance_test: str
    canonical_owner: str
    dimension: str
    rule_version: str
    existing_evidence: tuple[str, ...]
    eligibility_authority: str
    source_dispositions: tuple[tuple[str, str], ...] = ()


# Versioned owner-schedule bindings only. Their named authorities retain rules.
_CONTRACTS = {
    "industry-overview": ("Industry Fidelity", "IT-001 §10 Industry Fidelity schedule v1", (
        "industry boundary and definition", "subsectors", "value chain and market structure",
        "size and economics", "major enterprises and participants", "regulatory, economic, social, technological, legal and environmental pressures",
        "transformation mechanisms", "dated evidence"),
        ("industry and regulator publications", "official statistics", "company filings", "dated specialist research")),
    "enterprises": ("Enterprise Intelligence Density", "EI-001 / EIF-001 governed information schedule v1", (
        "organisation description", "purpose and strategy", "business units", "operating model", "financial context",
        "technology", "ecosystem", "risks and pressures", "change portfolio", "opportunities", "evidence and freshness"),
        ("annual reports", "strategy publications", "regulatory filings", "investor materials", "public procurement notices")),
    "market-participants": ("Market Participant Intelligence Density", "IT-001 delegated participant schedule v1", (
        "legitimate identity", "participant role", "domain", "capabilities", "customers and relationships",
        "market significance", "delivery evidence", "constraints", "supporting sources"),
        ("company filings", "official company publications", "customer case studies", "procurement notices", "regulatory publications")),
    "major-programmes": ("Enterprise Intelligence Density", "EIF-001 Change Landscape schedule v1", (
        "programme name", "owner", "business unit", "objective", "phase", "timing", "milestones",
        "investment where evidenced", "dependencies", "procurement", "evidence"),
        ("annual reports", "strategy and transformation updates", "investor materials", "public procurement notices", "regulatory publications")),
    "opportunities": ("Opportunity Completeness", "IT-001 Opportunity Completeness schedule v1", (
        "customer", "business unit", "client problem", "target outcome", "value", "buyer", "procurement status",
        "timing", "trigger", "competition", "partner context", "evidence", "confidence", "Unknowns and Contradictions"),
        ("customer publications", "annual reports", "procurement notices", "regulatory publications", "partner and competitor disclosures")),
    "reinvention-timing": ("Temporal Fidelity", "IT-001 Temporal Fidelity / FP-012 schedule v1", (
        "pressure or disruption mechanism", "affected enterprise and business unit", "observed adoption signal",
        "timing horizon", "response mechanism", "history and freshness", "evidence", "uncertainty"),
        ("dated company disclosures", "regulatory publications", "official statistics", "technology adoption research", "procurement notices")),
}

_ALIASES = {
    "legitimate identity": ("name", "organisation_name", "participant_name"),
    "programme name": ("name", "title", "programme_name"), "customer": ("customer", "customer_name"),
    "business unit": ("business_unit", "relevant_business_unit"), "client problem": ("client_problem", "customer_problem", "problem"),
    "target outcome": ("target_outcome", "outcome", "objective"), "buyer": ("buyer", "buying_centre"),
    "procurement status": ("procurement_status", "status"), "timing": ("timing", "procurement_start", "expected_procurement_start"),
    "confidence": ("confidence",), "evidence": ("evidence_refs", "sources"), "dated evidence": ("evidence_refs", "sources"),
    "supporting sources": ("evidence_refs", "sources"), "evidence and freshness": ("evidence_refs", "freshness"),
    "organisation description": ("description", "summary"), "domain": ("domain", "domains", "subsector"),
    "owner": ("owner", "programme_owner"), "objective": ("objective", "business_objective"), "phase": ("phase",),
    "pressure or disruption mechanism": ("pressure", "disruption_mechanism", "mechanism"),
    "timing horizon": ("expected_horizon", "timing", "horizon"), "observed adoption signal": ("adoption_signal", "adoption_indicators"),
}

_BUSINESS_ACCEPTANCE = {
    "industry-overview": "The Industry Twin contains sourced coverage of scope, subsectors, value chain, market structure, size, economics, major enterprises and participants, PESTLE pressures and transformation mechanisms, with explicit Unknowns where evidence remains unavailable.",
    "enterprises": "All enterprise profiles contain sourced descriptions, purpose and strategy, business units, operating model, financial context, technology, ecosystem, risks, pressures and change portfolio—or explicit Unknowns recording evidence searched, reason unresolved and decision impact.",
    "market-participants": "All participants have supported identity, role, domain, relevant relationships, market significance, capabilities, constraints and evidence—or explicit Unknowns.",
    "major-programmes": "All programme hypotheses identify owner, business unit, objective, phase, timing, milestones, dependencies, procurement relevance and evidence—or explicit Unknowns.",
    "opportunities": "All opportunity hypotheses identify customer, business unit, problem, buyer, value or explicit value unknown, timing, procurement stage, trigger, competition, partner context and evidence—or explicit Unknowns.",
    "reinvention-timing": "Every applicable domain and material enterprise has evidence-backed transformation pressure, affected functions, adoption signals, timing horizon, response mechanism and uncertainty.",
}

_ENTERPRISE_FIELDS = {
    "regulator": ("statutory mandate", "jurisdiction", "powers", "leadership", "implementation timetable", "regulatory priorities", "enforcement mechanisms", "regulated entities", "funding", "technology and data capability", "procurements", "evidence"),
    "public body": ("mandate", "funding model", "beneficiaries", "strategy", "programmes", "grants or procurement", "public outcomes", "transformation priorities", "evidence"),
    "governing body": ("governance role", "members", "rights and revenue model", "regulation", "competitions", "commercial partners", "data and technology", "programmes", "procurements", "strategic pressures", "evidence"),
    "league": ("governance role", "members", "rights and revenue model", "regulation", "competitions", "commercial partners", "data and technology", "programmes", "procurements", "strategic pressures", "evidence"),
    "broadcaster": ("ownership", "remit", "audience", "revenue or funding model", "content model", "distribution", "advertising or subscription economics", "technology", "programmes", "procurement", "regulation", "evidence"),
    "commercial company": ("ownership", "corporate purpose", "strategy", "operating segments", "revenue", "profitability", "investment capacity", "operating model", "technology", "suppliers", "customers", "programmes", "procurements", "risks", "AI adoption", "evidence"),
    "public corporation": ("statutory remit", "public ownership", "audience or beneficiaries", "funding and revenue model", "strategy", "operating structure", "technology", "programmes", "procurement", "regulation", "public outcomes", "evidence"),
    "infrastructure operator": ("ownership", "licensed or regulated remit", "network footprint", "customers", "revenue", "investment capacity", "operating model", "assets and technology", "suppliers", "programmes", "procurements", "resilience", "regulation", "evidence"),
    "association": ("mandate", "members", "governance", "funding model", "services", "industry role", "policy priorities", "technology", "programmes", "procurement", "evidence"),
    "composite group": ("group boundary", "member organisations", "ownership", "distinct remits", "business units", "consolidated and member economics", "operating relationships", "technology", "programmes", "procurement", "evidence"),
}

def participant_classification(obj: SemanticObject) -> str:
    """Project an explicitly supplied canonical type; never infer one from its label."""
    attrs = obj.attributes or {}
    raw = str(next((attrs.get(k) for k in ("canonical_type", "participant_type", "entity_type", "identity_type", "record_type", "type") if attrs.get(k)), "")).strip().casefold()
    aliases = {"company": "organisation", "organization": "organisation", "organisation": "organisation",
               "organisation_group": "organisation group", "category": "participant category",
               "participant_category": "participant category", "participant class": "participant category", "regulatory_body": "regulator",
               "unresolved": "unresolved identity"}
    value = aliases.get(raw, raw.replace("_", " "))
    allowed = {"organisation", "organisation group", "participant category", "capability", "relationship",
               "programme", "opportunity", "regulator", "unresolved identity"}
    return value if value in allowed else "unresolved identity"

def enterprise_subject_type(objects: tuple[SemanticObject, ...]) -> str:
    """Use the owner's supplied organisational form, otherwise preserve the gap."""
    for obj in objects:
        attrs = obj.attributes or {}
        raw = str(next((attrs.get(k) for k in ("subject_type", "organisational_form", "organization_type", "enterprise_type") if attrs.get(k)), "")).strip().casefold()
        aliases = {"company": "commercial company", "corporation": "commercial company", "regulatory body": "regulator",
                   "funding body": "public body", "media organisation": "broadcaster"}
        value = aliases.get(raw, raw)
        if value in _ENTERPRISE_FIELDS:
            return value
        # ``role`` is canonical supplied evidence, unlike a display-name guess.
        # Use it only where the record states an unambiguous organisational form.
        role = str(attrs.get("role") or "").casefold()
        role_markers = (
            ("regulator", ("regulator", "regulatory body")),
            ("public corporation", ("public corporation",)),
            ("public body", ("public body", "funding body", "funding/outcomes body", "funding and performance-system body")),
            ("broadcaster", ("broadcaster", "broadcasting organisation", " psb", "psb ")),
            ("infrastructure operator", ("infrastructure operator", "infrastructure provider")),
            ("league", ("sports league", "football league", "professional league body", "top-tier english football competition")),
            ("governing body", ("governing body",)),
            ("association", ("association",)),
            ("composite group", ("composite group", "group of organisations")),
            ("commercial company", ("commercial company", "commercial broadcaster", "commercial operator")),
        )
        for subject_type, markers in role_markers:
            if any(marker in role for marker in markers):
                return subject_type
    return "unresolved"


def research_requirements(twin: SemanticTwin, projections: tuple[ExecutiveAssessmentProjection, ...]) -> tuple[ResearchRequirement, ...]:
    """Translate owner deficiencies and current content; never assess a pass."""
    collections = {c.key: c.objects for c in business_collections(twin, include_empty=True)}
    by_key = {p.key: p for p in projections}
    requirements = []
    for key, (dimension, version, fields, sources) in _CONTRACTS.items():
        projection = by_key[key]
        subjects = _subjects(key, twin, collections.get(key, ()))
        for subject, objects in subjects:
            requested_fields = fields
            if key == "enterprises":
                requested_fields = _ENTERPRISE_FIELDS.get(enterprise_subject_type(objects),
                    ("subject classification", "identity", "purpose", "strategy", "operating structure", "financial or funding context", "technology", "ecosystem", "pressures", "programmes", "change", "evidence"))
            elif key == "market-participants" and objects:
                classification = participant_classification(objects[0])
                requested_fields = {
                    "organisation": fields,
                    "organisation group": ("group definition", "legitimate member identities", "role", "relationships", "market significance", "evidence"),
                    "participant category": ("category definition", "inclusion criteria", "representative members", "role", "relationships", "market significance", "evidence"),
                    "capability": ("capability definition", "providers", "users", "business application", "relationships", "evidence"),
                    "relationship": ("source", "target", "relationship type", "business significance", "timing", "evidence"),
                    "regulator": ("legitimate identity", "mandate", "jurisdiction", "regulated entities", "market role", "relationships", "evidence"),
                    "unresolved identity": ("identity resolution", "candidate type", "source record interpretation", "role", "relationships", "evidence"),
                }.get(classification, ("identity resolution", "candidate type", "evidence"))
            dispositions = tuple((field, assessment_field_disposition(field, objects, projection))
                                 for field in requested_fields)
            missing = tuple(field for field, disposition in dispositions
                            if disposition in {"source_field_absent", "source_field_invalid", "genuine_unknown"})
            # Owner execution and source research are separate concerns.  A
            # candidate with all scheduled source fields present is awaiting
            # governance, not missing research; never re-commission every field
            # merely because the owner result is deferred.
            if not missing:
                continue
            ids = tuple(dict.fromkeys(o.original_id or o.record_id for o in objects))
            evidence = tuple(dict.fromkeys(ref for o in objects for ref in o.evidence_refs))
            requested = missing
            requirements.append(ResearchRequirement(
                key, subject, ids, requested,
                f"These facts are needed to understand and safely use {subject} in {projection.label.lower()} decisions.",
                sources, f"Return import-compatible {projection.label.lower()} and evidence records with explicit Unknowns and Contradictions.",
                _BUSINESS_ACCEPTANCE[key],
                projection.canonical_owner, dimension, version, evidence, projection.eligibility_authority,
                dispositions))
    return tuple(requirements)


def assessment_field_disposition(field: str, objects: tuple[SemanticObject, ...],
                                 projection: ExecutiveAssessmentProjection) -> str:
    """Classify research and assessment state without calculating completeness."""
    aliases = _ALIASES.get(field, (field.replace(" ", "_"),))
    if any(o.validation_status not in {"accepted", "ignored"} and
           any(alias in (o.attributes or {}) for alias in aliases) for o in objects):
        return "source_field_invalid"
    if any((o.attributes or {}).get("unknown_refs") or (o.attributes or {}).get("unknowns") for o in objects):
        if not _present(field, objects):
            return "genuine_unknown"
    if _present(field, objects):
        if projection.state == "assessment_pending_governance":
            return "source_field_present_unassessed"
        if any(field.casefold() in deficiency.casefold() for deficiency in projection.deficiencies):
            return "owner_assessed_deficiency"
        return "source_field_present"
    return "source_field_absent"


def _subjects(key: str, twin: SemanticTwin, objects: tuple[SemanticObject, ...]):
    if key == "enterprises":
        return tuple((e.name, e.records) for e in twin.enterprises)
    if key == "industry-overview":
        return (("the represented industry", objects or twin.objects),)
    if key == "major-programmes":
        programmes = tuple(o for o in twin.objects if o.kind == "transformation_programme")
        return tuple((_label(o, key), (o,)) for o in programmes) or (("the missing major programmes collection", ()),)
    if key == "reinvention-timing" and not objects:
        return (("the represented industry and affected enterprises", ()),)
    return tuple((_label(o, key), (o,)) for o in objects) or ((f"the missing {key.replace('-', ' ')} collection", ()),)


def _label(obj: SemanticObject, key: str) -> str:
    attrs = obj.attributes or {}
    return str(next((attrs.get(k) for k in ("name", "title", "programme_name", "opportunity_name") if attrs.get(k)), None)
               or obj.statement or obj.subject or f"unnamed {key.replace('-', ' ')}")


def _present(field: str, objects: tuple[SemanticObject, ...]) -> bool:
    aliases = _ALIASES.get(field, (field.replace(" ", "_"),))
    for obj in objects:
        attrs = obj.attributes or {}
        if any(attrs.get(alias) not in (None, "", [], ()) for alias in aliases):
            return True
        if field in {"evidence", "dated evidence", "supporting sources"} and obj.evidence_refs:
            return True
        if field == "confidence" and obj.confidence not in {"", "unknown", "bounded/unspecified"}:
            return True
    return False
