"""ADR-026 Material Pressure qualification over canonical Enterprise facts.

The qualifier is deliberately read-only.  It neither persists a second model nor
creates Opportunities, Procurements, or Watchpoints.  Candidate discovery consumes
the structured financial-condition fact already held by the canonical Enterprise
object; prose, presentation labels and rendered output are never searched.
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
    eligible_input_count: int = 0
    pipeline_error: str = ""

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
        if self.pipeline_error:
            return "FAILURE"
        if self.qualified:
            return "STRONG" if all(len(a.candidate.evidence_refs) > 1 for a in self.qualified) else "ACCEPTABLE"
        return "EMPTY" if not self.unresolved else "ACCEPTABLE"

    @property
    def candidates_assessed(self) -> int:
        return len(self.assessments)

    @property
    def discovery_state(self) -> str:
        if self.pipeline_error or (self.eligible_input_count and not self.assessments):
            return "PIPELINE_FAILURE"
        if not self.eligible_input_count:
            return "NO_ELIGIBLE_INPUT"
        if not self.qualified:
            return "ASSESSED_NONE_QUALIFIED"
        return "ASSESSED_WITH_RESULTS"


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
    eligible = sum(bool(c.canonical_input_id) and c.canonical_input_type in eligible_types for c in candidates)
    return MaterialPressureQualification(tuple(assessments), eligible)


def material_pressure_qualification(ent: SemanticEnterprise) -> MaterialPressureQualification:
    """Discover candidates from typed, governed TEL Enterprise intelligence."""
    try:
        identity = next((o for o in ent.records if o.kind == "enterprise_twin"), None)
        identity = identity or next((o for o in ent.records if o.kind in {"enterprise", "entity"}), None)
        if not identity:
            return MaterialPressureQualification(())
        # The lists named ``pressures`` and ``current_challenges`` are not
        # admitted merely because of their presentation labels.  The canonical
        # financial object co-locates a condition, consequence and Evidence.
        attrs = identity.attributes or {}
        financial = attrs.get("financial_intelligence") or attrs.get("financial_context")
        if not isinstance(financial, dict):
            return MaterialPressureQualification(())
        conditions = financial.get("major_financial_pressures")
        conditions = (conditions,) if isinstance(conditions, str) else tuple(conditions or ())
        if not conditions:
            # Some governed dossiers express the condition as typed executive
            # risk assertions rather than duplicating it into the financial
            # object.  Risks are claims; the similarly named overview pressure
            # list remains presentation-only and is deliberately not used.
            risks = attrs.get("executive_risks") or ()
            conditions = (risks,) if isinstance(risks, str) else tuple(risks)
        consequence = str(financial.get("financial_outlook") or "").strip()
        overview = attrs.get("executive_overview") if isinstance(attrs.get("executive_overview"), dict) else {}
        evidence = financial.get("evidence") or overview.get("evidence") or ()
        evidence = (evidence,) if isinstance(evidence, str) else tuple(evidence)
        if not conditions:
            return MaterialPressureQualification(())
        financial_dimension = {d.key: d for d in enterprise_factual_dimensions(ent)}["financial"]
        candidate = PressureCandidate(
            identity.original_id or identity.record_id, "canonical_factual_object",
            ent.identity_key, "; ".join(str(value) for value in conditions), "financial/economic",
            consequence, "financial/economic" if consequence else "", tuple(dict.fromkeys(evidence)),
            applicable=True, pressure_semantics=True,
            materiality_established=bool(consequence), consequence_established=bool(consequence),
            lineage_established=bool(evidence), unknown_refs=financial_dimension.unknown_refs,
            contradiction_refs=financial_dimension.contradiction_refs,
        )
        return qualify_candidates((candidate,))
    except (AttributeError, TypeError, ValueError) as exc:
        return MaterialPressureQualification((), 0, f"candidate discovery failed: {type(exc).__name__}")
