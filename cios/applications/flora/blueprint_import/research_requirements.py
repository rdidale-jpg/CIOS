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


def research_requirements(twin: SemanticTwin, projections: tuple[ExecutiveAssessmentProjection, ...]) -> tuple[ResearchRequirement, ...]:
    """Translate owner deficiencies and current content; never assess a pass."""
    collections = {c.key: c.objects for c in business_collections(twin, include_empty=True)}
    by_key = {p.key: p for p in projections}
    requirements = []
    for key, (dimension, version, fields, sources) in _CONTRACTS.items():
        projection = by_key[key]
        subjects = _subjects(key, twin, collections.get(key, ()))
        for subject, objects in subjects:
            missing = tuple(field for field in fields if not _present(field, objects))
            # An absent owner dimension remains researchable even where package
            # content happens to carry a field; only genuinely absent facts are requested.
            if not missing and not projection.deficiencies:
                continue
            ids = tuple(dict.fromkeys(o.original_id or o.record_id for o in objects))
            evidence = tuple(dict.fromkeys(ref for o in objects for ref in o.evidence_refs))
            requested = missing or fields
            requirements.append(ResearchRequirement(
                key, subject, ids, requested,
                f"These facts are needed to understand and safely use {subject} in {projection.label.lower()} decisions.",
                sources, f"Return import-compatible {projection.label.lower()} and evidence records with explicit Unknowns and Contradictions.",
                _BUSINESS_ACCEPTANCE[key],
                projection.canonical_owner, dimension, version, evidence, projection.eligibility_authority))
    return tuple(requirements)


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
