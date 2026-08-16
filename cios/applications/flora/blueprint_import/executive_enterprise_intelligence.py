"""Read-only executive orientation over the governed TEL Enterprise read model.

This module deliberately owns no persistence and performs no recommendation or
promotion.  It selects and labels facts and associated business objects already
returned by the canonical factual and relationship owners.
"""
from __future__ import annotations

from dataclasses import dataclass

from .canonical_factual_projection import factual_projection_for_enterprise, enterprise_factual_dimensions
from .semantic_twin import SemanticEnterprise, SemanticObject, SemanticTwin, business_object_id, enterprise_associations
from .presentation_semantics import executive_fact_parts


@dataclass(frozen=True)
class ExecutiveSignal:
    title: str
    explanation: str
    source_type: str
    source_id: str
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class ExecutiveOpportunity:
    """Small presentation projection over (and linked back to) one Opportunity."""
    source: SemanticObject
    name: str
    why_it_matters: str
    timing: str
    maturity: str


@dataclass(frozen=True)
class ExecutiveEnterpriseIntelligence:
    situation: str
    commercial_significance: str
    signals: tuple[ExecutiveSignal, ...]
    opportunities: tuple[ExecutiveOpportunity, ...]
    watchpoints: tuple[ExecutiveSignal, ...]
    evidence_statement: str
    source_dimensions: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    unknown_refs: tuple[str, ...]
    contradiction_refs: tuple[str, ...]
    source_fact_ids: tuple[str, ...]
    content_status: str


@dataclass(frozen=True)
class ExecutiveQuality:
    """Deterministic acceptance diagnostic, deliberately not a score."""
    sections: tuple[tuple[str, str, str], ...]
    unknown_integrity: str
    contradiction_integrity: str
    overall: str


def _field(obj: SemanticObject, *names: str) -> str:
    for name in names:
        value = (obj.attributes or {}).get(name)
        if isinstance(value, (list, tuple)):
            value = "; ".join(str(item) for item in value if item not in (None, ""))
        if value not in (None, "", [], {}):
            return str(value)
    return ""


def _nested_field(obj: SemanticObject, container: str, name: str) -> str:
    value = (obj.attributes or {}).get(container)
    if isinstance(value, dict) and value.get(name) not in (None, "", [], {}):
        return str(value[name])
    return ""


def executive_enterprise_intelligence(ent: SemanticEnterprise, twin: SemanticTwin) -> ExecutiveEnterpriseIntelligence:
    """Select an executive derivative without changing any source runtime object."""
    factual = factual_projection_for_enterprise(ent)
    synthesis = factual.enterprise_synthesis
    dimensions = {dimension.key: dimension for dimension in enterprise_factual_dimensions(ent)}
    situation = synthesis.statement if synthesis and synthesis.status == "SUPPORTED" else ""
    # The governed synthesis remains verbatim below in the dossier.  Here only
    # presentation labels are joined into prose; no proposition is added.
    situation = situation.replace("Business Model:", "It operates as").replace(
        "Current Challenges:", "Current pressures include")

    programmes = tuple(row[0] for row in enterprise_associations(twin, ent, {"transformation_programme"}))
    opportunities = tuple(row[0] for row in enterprise_associations(
        twin, ent, {"opportunity_hypothesis", "opportunity", "ranked_opportunity", "opportunity_twin"}))

    signals: list[ExecutiveSignal] = []
    seen_signal_ids: set[str] = set()
    for programme in programmes:
        canonical_id = business_object_id(programme)
        if canonical_id in seen_signal_ids:
            continue
        seen_signal_ids.add(canonical_id)
        title = _field(programme, "title", "objective", "business_objective") or programme.statement
        if title:
            explanation = _field(programme, "objective", "strategic_objective", "summary") or programme.statement
            # A title and explanation are two presentation fields on one
            # canonical Programme, not independent executive signals.  Older
            # candidates can carry the same governed statement in both fields;
            # render that concept once while retaining its canonical lineage.
            if explanation == title:
                explanation = ""
            signals.append(ExecutiveSignal(title, explanation, "Programme", canonical_id, tuple(programme.evidence_refs)))
    for key in ("transformation", "technology", "financial", "strategy", "pressures", "procurements"):
        dimension = dimensions[key]
        if dimension.present:
            title, explanation = executive_fact_parts(dimension.values[0])
            signals.append(ExecutiveSignal(title, explanation, dimension.label, f"DIM-{key.upper()}", dimension.evidence_refs))
    signals = signals[:5]

    relevance = [(_field(item, "commercial_relevance") or _field(item, "client_problem", "customer_problem", "problem"))
                 for item in opportunities]
    relevance = [item for item in relevance if item]
    if signals:
        lead = signals[0]
        basis = f" — {lead.explanation.rstrip('.')}" if lead.explanation else ""
        commercial = (f"{ent.name}'s evidenced change is centred on {lead.title.rstrip('.')}{basis}. "
                      "Associated governed opportunities identify a potential supplier change surface; "
                      "the evidence does not by itself establish an active procurement.")
    else:
        commercial = "Commercial significance is not established from the currently supported Enterprise facts."

    executive_opportunities = tuple(ExecutiveOpportunity(
        item,
        _field(item, "opportunity_title", "title") or item.statement or "Unnamed opportunity",
        _field(item, "commercial_relevance") or _field(item, "client_problem", "customer_problem", "problem") or "Commercial relevance is not yet established.",
        _field(item, "procurement_timing", "expected_procurement_timing", "estimated_procurement_window", "expected_procurement_start", "timing") or "Timing not established",
        " — ".join(filter(None, (_field(item, "commercial_type", "commercial_type_wave5"), _field(item, "procurement_status", "procurement_stage", "status")))) or "Commercial maturity not established",
    ) for item in opportunities[:3])

    watchpoints: list[ExecutiveSignal] = []
    for opportunity in opportunities:
        values = []
        for label, fields in (("Next monitoring date", ("next_monitoring_date",)),
                              ("Expected decision point", ("expected_decision_point",)),
                              ("Procurement window", ("estimated_procurement_window", "procurement_timing", "expected_procurement_start"))):
            value = _field(opportunity, *fields) or next(
                (_nested_field(opportunity, "timing", field) for field in fields
                 if _nested_field(opportunity, "timing", field)), "")
            if value:
                values.append(f"{label}: {value}")
        if values:
            name = _field(opportunity, "opportunity_title", "title") or opportunity.statement
            watchpoints.append(ExecutiveSignal(name, " · ".join(values), "Opportunity timing", business_object_id(opportunity), tuple(opportunity.evidence_refs)))

    evidence_statement = (
        f"Supported by {len(factual.evidence_refs)} linked evidence source{'s' if len(factual.evidence_refs) != 1 else ''}. "
        f"Material uncertainty remains in {len(factual.unknown_refs)} area{'s' if len(factual.unknown_refs) != 1 else ''}, with "
        f"{len(factual.contradiction_refs)} source contradiction{'s' if len(factual.contradiction_refs) != 1 else ''} preserved for review."
    ) if factual.evidence_refs else "No linked evidence supports an executive synthesis; unresolved items remain retained."
    return ExecutiveEnterpriseIntelligence(
        situation, commercial, tuple(signals), executive_opportunities, tuple(watchpoints[:3]), evidence_statement,
        synthesis.input_dimensions if synthesis else (), factual.evidence_refs, factual.unknown_refs,
        factual.contradiction_refs, synthesis.input_fact_ids if synthesis else (),
        "synthesized from governed facts" if situation else "truthful absence",
    )


def executive_intelligence_quality(ent: SemanticEnterprise, twin: SemanticTwin) -> ExecutiveQuality:
    """Apply explicit sufficiency and truth rules to canonical presentation owners."""
    result = executive_enterprise_intelligence(ent, twin)
    factual = factual_projection_for_enterprise(ent)
    dimensions = {item.key: item for item in enterprise_factual_dimensions(ent)}
    programmes = enterprise_associations(twin, ent, {"transformation_programme"})
    opportunities = enterprise_associations(twin, ent, {"opportunity_hypothesis", "opportunity", "ranked_opportunity", "opportunity_twin"})

    def dimension(name: str, key: str) -> tuple[str, str, str]:
        item = dimensions[key]
        if not item.present:
            return name, "EMPTY", "No qualifying governed fact is supplied; truthful absence is acceptable."
        if not item.evidence_refs:
            return name, "WEAK", "A presented fact has no linked Evidence."
        return name, ("STRONG" if len(item.values) > 1 else "ACCEPTABLE"), ""

    rows = [
        ("Overview", "STRONG" if result.situation and len(result.source_dimensions) > 1 else "ACCEPTABLE" if result.situation else "EMPTY",
         "" if result.situation else "No supported organisation synthesis is available."),
        dimension("Strategic Position", "strategy"), dimension("Operating Model", "operating-model"),
        dimension("Technology / Platform", "technology"), dimension("Change / Investment", "transformation"),
        dimension("Financial Position", "financial"),
        ("Key Reports", "ACCEPTABLE", "Four-state truth is assessed by the canonical Key Reports selector."),
        dimension("Material Pressures", "pressures"),
        ("Programmes", "STRONG" if programmes else "EMPTY", "" if programmes else "No canonically associated Programme is supplied."),
        ("Opportunities", "STRONG" if opportunities else "EMPTY", "" if opportunities else "No canonically associated Opportunity is supplied."),
        ("Watchpoints", "STRONG" if result.watchpoints else "EMPTY", "" if result.watchpoints else "No governed monitoring event or timing is supplied."),
    ]
    unknown_integrity = "PASS" if result.unknown_refs == factual.unknown_refs else "FAIL"
    contradiction_integrity = "PASS" if result.contradiction_refs == factual.contradiction_refs else "FAIL"
    overall = "FAIL" if any(state == "WEAK" for _, state, _ in rows) or "FAIL" in (unknown_integrity, contradiction_integrity) else "PASS"
    return ExecutiveQuality(tuple(rows), unknown_integrity, contradiction_integrity, overall)
