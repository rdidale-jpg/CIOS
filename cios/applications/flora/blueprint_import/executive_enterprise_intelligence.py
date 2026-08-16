"""Read-only executive orientation over the governed TEL Enterprise read model.

This module deliberately owns no persistence and performs no recommendation or
promotion.  It selects and labels facts and associated business objects already
returned by the canonical factual and relationship owners.
"""
from __future__ import annotations

from dataclasses import dataclass

from .canonical_factual_projection import factual_projection_for_enterprise, enterprise_factual_dimensions
from .semantic_twin import SemanticEnterprise, SemanticObject, SemanticTwin, business_object_id, enterprise_associations


@dataclass(frozen=True)
class ExecutiveSignal:
    title: str
    source_type: str
    source_id: str
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class ExecutiveEnterpriseIntelligence:
    situation: str
    commercial_significance: str
    signals: tuple[ExecutiveSignal, ...]
    opportunities: tuple[SemanticObject, ...]
    watchpoints: tuple[ExecutiveSignal, ...]
    evidence_statement: str
    source_dimensions: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    unknown_refs: tuple[str, ...]
    contradiction_refs: tuple[str, ...]
    source_fact_ids: tuple[str, ...]
    content_status: str


def _field(obj: SemanticObject, *names: str) -> str:
    for name in names:
        value = (obj.attributes or {}).get(name)
        if isinstance(value, (list, tuple)):
            value = "; ".join(str(item) for item in value if item not in (None, ""))
        if value not in (None, "", [], {}):
            return str(value)
    return ""


def executive_enterprise_intelligence(ent: SemanticEnterprise, twin: SemanticTwin) -> ExecutiveEnterpriseIntelligence:
    """Select an executive derivative without changing any source runtime object."""
    factual = factual_projection_for_enterprise(ent)
    synthesis = factual.enterprise_synthesis
    dimensions = {dimension.key: dimension for dimension in enterprise_factual_dimensions(ent)}
    situation = synthesis.statement if synthesis and synthesis.status == "SUPPORTED" else ""

    programmes = tuple(row[0] for row in enterprise_associations(twin, ent, {"transformation_programme"}))
    opportunities = tuple(row[0] for row in enterprise_associations(
        twin, ent, {"opportunity_hypothesis", "opportunity", "ranked_opportunity", "opportunity_twin"}))

    signals: list[ExecutiveSignal] = []
    for programme in programmes:
        title = _field(programme, "title", "objective", "business_objective") or programme.statement
        if title:
            signals.append(ExecutiveSignal(title, "Programme", business_object_id(programme), tuple(programme.evidence_refs)))
    for key in ("transformation", "technology", "financial", "strategy", "pressures", "procurements"):
        dimension = dimensions[key]
        if dimension.present:
            signals.append(ExecutiveSignal(dimension.values[0], dimension.label, f"DIM-{key.upper()}", dimension.evidence_refs))
    signals = signals[:5]

    relevance = [(_field(item, "commercial_relevance") or _field(item, "client_problem", "customer_problem", "problem"))
                 for item in opportunities]
    relevance = [item for item in relevance if item]
    if signals:
        commercial = "Existing evidence shows change or pressure across " + ", ".join(signal.source_type for signal in signals[:3]) + "."
        if relevance:
            commercial += " Canonically associated Opportunity records describe commercial relevance to these conditions."
        commercial += " Observed change does not by itself establish an active procurement."
    else:
        commercial = "Commercial significance is not established from the currently supported Enterprise facts."

    watchpoints: list[ExecutiveSignal] = []
    for opportunity in opportunities:
        values = []
        for label, fields in (("Next monitoring date", ("next_monitoring_date",)),
                              ("Expected decision point", ("expected_decision_point",)),
                              ("Procurement window", ("estimated_procurement_window", "procurement_timing", "expected_procurement_start"))):
            value = _field(opportunity, *fields)
            if value:
                values.append(f"{label}: {value}")
        if values:
            watchpoints.append(ExecutiveSignal(" · ".join(values), "Opportunity timing", business_object_id(opportunity), tuple(opportunity.evidence_refs)))
    if factual.unknown_refs:
        watchpoints.append(ExecutiveSignal(f"{len(factual.unknown_refs)} explicit Unknown{'s' if len(factual.unknown_refs) != 1 else ''} remain unresolved.", "Unknown", factual.object_id, factual.evidence_refs))
    if factual.contradiction_refs:
        watchpoints.append(ExecutiveSignal(f"{len(factual.contradiction_refs)} explicit Contradiction{'s are' if len(factual.contradiction_refs) != 1 else ' is'} retained.", "Contradiction", factual.object_id, factual.evidence_refs))

    evidence_statement = (
        f"Supported by {len(factual.evidence_refs)} linked evidence reference{'s' if len(factual.evidence_refs) != 1 else ''}. "
        f"{len(factual.unknown_refs)} Unknown{'s' if len(factual.unknown_refs) != 1 else ''} and "
        f"{len(factual.contradiction_refs)} Contradiction{'s' if len(factual.contradiction_refs) != 1 else ''} remain retained."
    ) if factual.evidence_refs else "No linked evidence supports an executive synthesis; unresolved items remain retained."
    return ExecutiveEnterpriseIntelligence(
        situation, commercial, tuple(signals), opportunities, tuple(watchpoints[:5]), evidence_statement,
        synthesis.input_dimensions if synthesis else (), factual.evidence_refs, factual.unknown_refs,
        factual.contradiction_refs, synthesis.input_fact_ids if synthesis else (),
        "synthesized from governed facts" if situation else "truthful absence",
    )
