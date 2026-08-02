"""Read-only composition of owner-supplied Enterprise Intelligence assessments.

This adapter deliberately does not assess content.  It only selects outputs
already emitted by the architectural owners and makes their provenance
available to the Executive Workspace.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .semantic_twin import SemanticTwin


@dataclass(frozen=True)
class ExecutiveAssessmentProjection:
    key: str
    label: str
    canonical_owner: str
    evidence_source: str
    completeness_authority: str
    eligibility_authority: str
    research_gap_authority: str
    dimensions: tuple[str, ...]
    state: str
    owner_result_id: str
    deficiencies: tuple[str, ...]
    required_evidence: str
    acceptance_criteria: str
    inventory_summary: str


# Presentation bindings only. The named documents retain all semantics/rules.
_BINDINGS: Mapping[str, tuple[str, str, str, str, tuple[str, ...]]] = {
    "industry-overview": ("Industry Overview", "IT-001", "IT-001 High-Fidelity Completeness Contract", "EIRP-001 S09-S12", ("Industry Fidelity", "Temporal Fidelity", "Evidence Maturity", "Source Diversity")),
    "enterprises": ("Enterprises", "EI-001 / EIF-001", "IT-001: Enterprise Intelligence Density", "EIRP-001 S09-S12", ("Enterprise Intelligence Density", "Financial Intelligence", "Temporal Fidelity", "Relationship and Graph Integrity")),
    "market-participants": ("Market Participants", "IT-001 participant delegation (owner unresolved)", "IT-001: Market Participant Intelligence Density", "EIRP-001 S09-S12", ("Market Participant Intelligence Density", "Capability and Offer Intelligence", "Relationship and Graph Integrity")),
    "major-programmes": ("Major Programmes", "EI-001 / EIF-001 Change Landscape / EI-002", "IT-001: Enterprise Intelligence Density", "EIRP-001 S09-S12", ("Enterprise Intelligence Density", "Temporal Fidelity", "Relationship and Graph Integrity", "Evidence Maturity")),
    "opportunities": ("Opportunities", "EI-004 / FP-009", "IT-001: Opportunity Completeness", "EIRP-001 S09-S12", ("Opportunity Completeness", "Commercial Reasoning Lineage", "Evidence Maturity", "Decision Maturity")),
    "reinvention-timing": ("Reinvention Timing", "EI-001 / EIF-001 / EI-003 / FP-012", "IT-001: Temporal Fidelity", "FP-014 composed presentation; EIRP-001 S09-S12", ("Temporal Fidelity", "Observation and Explanation Maturity", "Evidence Maturity", "Decision Maturity")),
}


def executive_assessments(twin: SemanticTwin) -> tuple[ExecutiveAssessmentProjection, ...]:
    """Compose declared IT-001 results; never infer a result from record fields."""
    declared = next((o for o in twin.objects if o.kind == "high_fidelity_completeness_assessment"), None)
    data = dict(declared.attributes or {}) if declared else {}
    raw_dimensions = data.get("dimensions") if isinstance(data.get("dimensions"), list) else []
    by_name = {str(d.get("dimension")): d for d in raw_dimensions if isinstance(d, dict)}
    inventory = _inventory(twin)
    projections = []
    for key, (label, owner, completeness, eligibility, dimensions) in _BINDINGS.items():
        supplied = [by_name[name] for name in dimensions if name in by_name]
        missing = tuple(name for name in dimensions if name not in by_name)
        # State is copied only from a complete owner output. No scores, weights,
        # thresholds, caps, or field-presence rules live in this adapter.
        state = str(data.get("state") or "") if declared and not missing else "legacy_unassessed"
        deficiencies = tuple(str(x) for d in supplied for x in (d.get("deficiencies") or ()))
        if missing:
            deficiencies = ("Missing owner-produced assessment dimensions: " + ", ".join(missing),) + deficiencies
        projections.append(ExecutiveAssessmentProjection(
            key, label, owner, declared.source_file if declared else "No owner-produced assessment supplied",
            completeness, eligibility, "IT-001 §10; EI-001 / EIF-001 governed information requirements",
            dimensions, state or "legacy_unassessed", declared.original_id if declared else "",
            deficiencies, "A governed assessment result with linked evidence, deficiencies, Unknowns, Contradictions, exhaustion and review references.",
            "The named canonical owner supplies every applicable dimension and its acceptance/promotion effect; presentation does not infer a pass.",
            inventory[key],
        ))
    return tuple(projections)


def _inventory(twin: SemanticTwin) -> dict[str, str]:
    count = lambda *kinds: sum(o.kind in kinds for o in twin.objects)
    return {
        "industry-overview": f"{count('industry_twin')} Industry Twin record(s) · {count('executive_intelligence', 'fact', 'observation', 'supported_interpreted_observation')} insight record(s)",
        "enterprises": f"{len(twin.enterprises)} represented enterprise(s)",
        "market-participants": f"{count('market_participant', 'market_participant_twin')} represented participant(s)",
        "major-programmes": f"{count('transformation_programme')} programme hypothesis record(s)",
        "opportunities": f"{count('opportunity_hypothesis', 'ranked_opportunity', 'opportunity_twin')} opportunity hypothesis record(s)",
        "reinvention-timing": f"{count('ai_reinvention_assessment')} reinvention assessment record(s)",
    }
