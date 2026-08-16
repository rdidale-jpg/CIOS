"""ADR-026 Material Pressure qualification over canonical Enterprise facts.

The qualifier is deliberately read-only.  It neither persists a second model nor
creates Opportunities, Procurements, or Watchpoints.  Candidate discovery accepts
only the explicitly typed ``pressures`` Enterprise dimension; prose and rendered
output are never searched.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from .canonical_factual_projection import enterprise_factual_dimensions
from .semantic_twin import SemanticEnterprise


@dataclass(frozen=True)
class PressureCandidate:
    canonical_input_id: str
    canonical_input_type: str
    enterprise_id: str
    condition: str
    affected_domain: str
    consequence: str
    consequence_domain: str
    evidence_refs: tuple[str, ...]
    applicable: bool = True
    pressure_semantics: bool = True
    materiality_established: bool = True
    consequence_established: bool = True
    lineage_established: bool = True
    unknown_refs: tuple[str, ...] = ()
    contradiction_refs: tuple[str, ...] = ()
    core_contradiction: bool = False
    time_context: str = ""


@dataclass(frozen=True)
class PressureAssessment:
    candidate: PressureCandidate
    identity: str
    applicability: str
    pressure_semantics: str
    materiality: str
    enterprise_consequence: str
    lineage: str
    qualification: str
    reason: str

    @property
    def qualified(self) -> bool:
        return self.qualification == "QUALIFIED"


@dataclass(frozen=True)
class MaterialPressureQualification:
    assessments: tuple[PressureAssessment, ...]

    @property
    def qualified(self) -> tuple[PressureAssessment, ...]:
        return tuple(a for a in self.assessments if a.qualified)

    @property
    def rejected(self) -> tuple[PressureAssessment, ...]:
        return tuple(a for a in self.assessments if a.qualification == "REJECTED")

    @property
    def unresolved(self) -> tuple[PressureAssessment, ...]:
        return tuple(a for a in self.assessments if a.qualification == "UNRESOLVED")

    @property
    def projection_state(self) -> str:
        if self.qualified:
            return "STRONG" if all(len(a.candidate.evidence_refs) > 1 for a in self.qualified) else "ACCEPTABLE"
        return "EMPTY" if not self.unresolved else "ACCEPTABLE"


def semantic_identity(candidate: PressureCandidate) -> str:
    """ADR-026 identity basis, independent of wording and Evidence identifiers."""
    basis = "\x1f".join((candidate.enterprise_id, candidate.condition,
                         candidate.affected_domain, candidate.time_context))
    return "MP-" + sha256(basis.encode()).hexdigest()[:16].upper()


def qualify_candidates(candidates: tuple[PressureCandidate, ...]) -> MaterialPressureQualification:
    assessments: list[PressureAssessment] = []
    seen: set[str] = set()
    eligible_types = {"observation", "canonical_factual_object", "enterprise_pressure_dimension"}
    for candidate in candidates:
        identity = semantic_identity(candidate)
        gates = (candidate.canonical_input_type in eligible_types and bool(candidate.canonical_input_id),
                 candidate.applicable and bool(candidate.enterprise_id),
                 candidate.pressure_semantics and bool(candidate.condition),
                 candidate.materiality_established and bool(candidate.consequence_domain),
                 candidate.consequence_established and bool(candidate.consequence),
                 candidate.lineage_established and bool(candidate.evidence_refs))
        reasons = ("ineligible input", "wrong Enterprise", "insufficient Pressure semantics",
                   "materiality not established", "Enterprise consequence not established",
                   "insufficient lineage")
        if candidate.core_contradiction:
            qualification, reason = "UNRESOLVED", "core contradiction"
        elif identity in seen:
            qualification, reason = "REJECTED", "duplicate/same Pressure"
        elif not all(gates):
            qualification, reason = "REJECTED", reasons[gates.index(False)]
        else:
            qualification, reason = "QUALIFIED", "all ADR-026 mandatory gates passed"
            seen.add(identity)
        assessments.append(PressureAssessment(
            candidate, identity, "PASS" if gates[1] else "FAIL",
            "PASS" if gates[2] else "FAIL", "PASS" if gates[3] else "FAIL",
            "PASS" if gates[4] else "FAIL", "PASS" if gates[5] else "FAIL",
            qualification, reason))
    return MaterialPressureQualification(tuple(assessments))


def material_pressure_qualification(ent: SemanticEnterprise) -> MaterialPressureQualification:
    """Discover candidates from typed, governed TEL Enterprise intelligence."""
    identity = next((o for o in ent.records if o.kind in {"enterprise", "enterprise_twin", "entity"}), None)
    if not identity:
        return MaterialPressureQualification(())
    dimensions = {d.key: d for d in enterprise_factual_dimensions(ent)}
    pressure = dimensions["pressures"]
    financial = (identity.attributes or {}).get("financial_context")
    financial = financial if isinstance(financial, dict) else {}
    consequence = str(financial.get("financial_outlook") or "").strip()
    evidence = tuple(dict.fromkeys((*pressure.evidence_refs,
                                    *(financial.get("evidence") or ()))))
    if not pressure.present:
        return MaterialPressureQualification(())
    # One typed Enterprise condition is one candidate.  Its component labels
    # are not independently promoted, preventing list-item duplication.
    candidate = PressureCandidate(
        identity.original_id or identity.record_id, "enterprise_pressure_dimension",
        ent.identity_key, "; ".join(pressure.values), "financial/economic",
        consequence, "financial/economic" if consequence else "", evidence,
        applicable=True, pressure_semantics=True,
        materiality_established=bool(consequence), consequence_established=bool(consequence),
        lineage_established=bool(evidence), unknown_refs=pressure.unknown_refs,
        contradiction_refs=pressure.contradiction_refs,
    )
    return qualify_candidates((candidate,))
