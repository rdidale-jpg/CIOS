"""Candidate Observation construction for imported Twin semantic objects.

This module adapts read-only candidate Twin objects into the implemented
Enterprise Observation pipeline shape.  It does not persist, promote or create a
new canonical Observation model; it supplies deterministic Observation-compatible
statements for the existing candidate runtime and diagnostics.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
import hashlib

from .semantic_twin import SemanticObject

OBSERVATION_PROFILE_VERSION = "imported-twin-observation-profile-v1"
OBSERVATION_BUILDER_NAME = "ImportedTwinSemanticObservationBuilder"

SUPPORTED_OBJECT_FAMILIES: dict[str, tuple[str, ...]] = {
    "Industry Overview": ("industry", "industry_twin", "industry_overview", "subsector", "value_chain", "economic_pool"),
    "Enterprise Dossier": ("enterprise", "enterprise_twin", "enterprise_dossier", "entity"),
    "Market Participant": ("market_participant", "market_participant_twin"),
    "Transformation Programme": ("transformation_programme",),
    "Opportunity": ("opportunity", "opportunity_hypothesis", "ranked_opportunity", "opportunity_twin"),
    "Reinvention Assessment": ("ai_reinvention_assessment",),
}

_KIND_TO_FAMILY = {kind: family for family, kinds in SUPPORTED_OBJECT_FAMILIES.items() for kind in kinds}

@dataclass(frozen=True)
class StatementSourceSelector:
    """Governed statement source for candidate Observation construction."""
    canonical_owner: str
    source_field: str
    semantic_meaning: str
    permitted_value_type: str
    subject_source: str
    evidence_source: str
    confidence_source: str
    temporal_source: str
    fallback_behaviour: str
    skip_reason: str


STATEMENT_SOURCE_SELECTORS: dict[str, tuple[StatementSourceSelector, ...]] = {
    "Industry Overview": (StatementSourceSelector("IT-001", "industry_profile", "industry economics, structure and commercial implications", "mapping/object or substantive string", "industry_name/name/title/id semantic subject", "evidence_refs/source_refs", "confidence", "freshness/observation_date", "fall back only to a substantive semantic statement", "missing_governed_statement_source"),),
    "Enterprise Dossier": (StatementSourceSelector("EI-001 / EIF-001", "description", "plain-language enterprise description", "non-empty string", "enterprise_name/organisation_name semantic subject", "evidence_refs/source_refs", "confidence", "freshness/observation_date", "fall back only to a substantive semantic statement", "missing_governed_statement_source"),),
    "Market Participant": (
        StatementSourceSelector("IT-001 participant delegation", "role", "supported participant market role", "non-empty string", "participant_name/organisation_name/name semantic subject", "evidence_refs/source_refs", "confidence", "freshness/observation_date", "try capabilities, relationships, then current_activity; otherwise fall back only to a substantive semantic statement", "missing_governed_statement_source"),
        StatementSourceSelector("IT-001 participant delegation", "capabilities", "supported participant capabilities", "non-empty string/list/mapping", "participant_name/organisation_name/name semantic subject", "evidence_refs/source_refs", "confidence", "freshness/observation_date", "try relationships, then current_activity; otherwise substantive statement only", "missing_governed_statement_source"),
        StatementSourceSelector("IT-001 participant delegation", "relationships", "supported participant relationships", "non-empty string/list/mapping", "participant_name/organisation_name/name semantic subject", "evidence_refs/source_refs", "confidence", "freshness/observation_date", "try current_activity; otherwise substantive statement only", "missing_governed_statement_source"),
        StatementSourceSelector("IT-001 participant delegation", "current_activity", "current participant activity", "non-empty string/list/mapping", "participant_name/organisation_name/name semantic subject", "evidence_refs/source_refs", "confidence", "freshness/observation_date", "fall back only to a substantive semantic statement", "missing_governed_statement_source")),
    "Transformation Programme": (StatementSourceSelector("EI-001 / EIF-001 Change Landscape / EI-002", "objective", "programme business objective", "non-empty string", "owner/affected_enterprises/business_unit/title semantic subject", "evidence_refs/source_refs", "confidence", "freshness/observation_date", "fall back only to a substantive semantic statement", "missing_governed_statement_source"),),
    "Opportunity": (StatementSourceSelector("EI-004 / FP-009", "client_problem", "customer problem or evidenced commercial need", "non-empty string", "title/opportunity_name semantic subject plus affected enterprises", "evidence_refs/source_refs", "confidence", "freshness/observation_date", "fall back only to a substantive semantic statement", "missing_governed_statement_source"),),
    "Reinvention Assessment": (
        StatementSourceSelector("EI-001 / EIF-001 / EI-003 / FP-012", "ai_disruption_mechanism", "AI disruption mechanism or reinvention pressure", "non-empty string", "enterprise_name/organisation_name/target/id semantic subject", "evidence_refs/source_refs", "confidence", "freshness/observation_date", "try summary; otherwise fall back only to a substantive semantic statement", "missing_governed_statement_source"),
        StatementSourceSelector("EI-001 / EIF-001 / EI-003 / FP-012", "summary", "current operating-model assessment", "non-empty string", "enterprise_name/organisation_name/target/id semantic subject", "evidence_refs/source_refs", "confidence", "freshness/observation_date", "fall back only to a substantive semantic statement", "missing_governed_statement_source")),
}

_DISPLAY_ONLY_FIELDS = {"id", "name", "title", "display_name", "enterprise_id", "canonical_id", "participant_name", "enterprise_name", "organisation_name"}

@dataclass(frozen=True)
class CandidateObservation:
    observation_id: str
    builder: str
    profile: str
    originating_object: str
    originating_fields: tuple[str, ...]
    statement: str
    evidence_refs: tuple[str, ...]
    confidence: str
    subject: str
    observation_type: str
    observed_at: str
    owner_assessment_state: str = "assessment_pending_governance"
    persistence_state: str = "candidate_read_projection_only"


def observation_family(kind: str) -> str:
    return _KIND_TO_FAMILY.get(kind, "Unsupported")


def build_candidate_observation(obj: SemanticObject, *, observed_at: str | None = None) -> tuple[CandidateObservation | None, str, str]:
    """Return an Observation-compatible candidate projection or an exact skip reason.

    The Programme path already succeeds because programmes carry an explicit
    semantic statement.  The same builder also derives a statement from the
    canonical executive view-model fields for supported factual object families.
    """
    family = observation_family(obj.kind)
    if family == "Unsupported":
        return None, "unsupported_object_family", "Object kind is not registered in the imported Twin Observation profile."
    if obj.validation_status and obj.validation_status not in {"accepted", ""}:
        return None, "candidate_state_suppressed", obj.residual_reason or "Candidate validation status is not accepted."
    if not obj.subject or obj.subject == "Twin scope":
        return None, "missing_subject", "Observation requires a canonical subject."
    statement, fields = _statement_and_fields(obj)
    if not statement:
        return None, "missing_governed_statement_source", "No substantive value is present in the family statement-source selectors; labels and identifiers are skipped."
    now = observed_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    oid = _observation_id(obj, statement, fields)
    return CandidateObservation(oid, OBSERVATION_BUILDER_NAME, OBSERVATION_PROFILE_VERSION,
        obj.original_id or obj.record_id, fields, statement, obj.evidence_refs, obj.confidence,
        obj.subject, _observation_type(obj), now), "observation_generated", "Generated by imported Twin semantic Observation builder."


def _statement_and_fields(obj: SemanticObject) -> tuple[str, tuple[str, ...]]:
    attrs = obj.attributes or {}
    family = observation_family(obj.kind)
    for selector in STATEMENT_SOURCE_SELECTORS.get(family, ()):
        value = attrs.get(selector.source_field)
        if _substantive_value(value):
            return f"{obj.subject} — {selector.semantic_meaning}: {_render_value(value)}", (selector.source_field,)
    display_values = {str(attrs.get(k) or "").strip() for k in _DISPLAY_ONLY_FIELDS}
    if obj.statement and not obj.statement.lstrip().startswith("{") and obj.statement.strip() not in display_values:
        return obj.statement, ("statement",)
    return "", ()


def _substantive_value(value: Any) -> bool:
    if value in (None, "", [], {}, ()): return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, dict):
        return any(_substantive_value(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return any(_substantive_value(v) for v in value)
    return True


def _render_value(value: Any) -> str:
    if isinstance(value, dict):
        return "; ".join(f"{str(k).replace('_',' ')}: {_render_value(v)}" for k, v in value.items() if v not in (None, "", [], {}))
    if isinstance(value, (list, tuple)):
        return "; ".join(_render_value(v) for v in value if v not in (None, "", [], {}))
    return str(value)


def _observation_id(obj: SemanticObject, statement: str, fields: tuple[str, ...]) -> str:
    seed = "|".join((obj.record_id, obj.original_id, obj.kind, statement, ",".join(fields)))
    return "OBS-CAND-" + hashlib.sha256(seed.encode()).hexdigest()[:16].upper()


def _observation_type(obj: SemanticObject) -> str:
    if obj.kind == "transformation_programme": return "programme_candidate_fact"
    if "opportun" in obj.kind: return "opportunity_candidate_fact"
    if obj.kind == "ai_reinvention_assessment": return "reinvention_candidate_fact"
    if "market_participant" in obj.kind: return "participant_candidate_fact"
    if "enterprise" in obj.kind or obj.kind == "entity": return "enterprise_candidate_fact"
    if "industry" in obj.kind or obj.kind in {"subsector", "value_chain", "economic_pool"}: return "industry_candidate_fact"
    return "candidate_fact"
