"""Presentation-only scope and relevance projection for candidate Review.

This module deliberately interprets only explicit, owner-supplied fields.  It
does not classify candidates, score relevance, or persist any new semantics.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from .models import BlueprintPackageRecord
from .twin_governance import TwinIdentityProjection

RelevanceStatus = Literal["core", "relevant sub-sector", "adjacent", "unresolved", "out of scope"]
ALLOWED_RELEVANCE_STATUSES = frozenset({"core", "relevant sub-sector", "adjacent", "unresolved", "out of scope"})


@dataclass(frozen=True)
class CandidateRelevance:
    """Non-canonical Review contract composed from current data owners."""

    candidate_id: str
    proposed_twin_identity: str | None
    governed_subject: str | None
    industry: str | None
    sub_sector_or_domain: str | None
    geography: str | None
    temporal_scope: str | None
    status: RelevanceStatus
    relevance_basis: str | None
    decision_relevance: str | None
    commercial_consequence: str | None
    owner: str | None
    supporting_relationship: str | None
    unresolved_scope_reason: str | None
    truth_class: str | None
    evidence_state: str | None
    freshness: str | None

    @property
    def inspectable(self) -> bool:
        return bool(self.relevance_basis and self.owner and self.supporting_relationship)

    @property
    def primary_eligible(self) -> bool:
        return bool(
            self.status in {"core", "relevant sub-sector"}
            and self.proposed_twin_identity
            and self.governed_subject
            and self.inspectable
            and self.truth_class
            and self.evidence_state
            and not self.unresolved_scope_reason
        )


def _first(source: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = source.get(key)
        if value not in (None, "", [], {}):
            if isinstance(value, (list, tuple)):
                return ", ".join(str(item) for item in value)
            return str(value)
    return None


def project_candidate_relevance(candidate: dict[str, Any], package: BlueprintPackageRecord,
                                identity: TwinIdentityProjection) -> CandidateRelevance:
    """Compose explicit package/candidate metadata without keyword inference."""
    payload = candidate.get("payload") or {}
    inspection = package.package_inspection or {}
    raw_status = (_first(payload, "relevance_status", "scope_relevance") or "unresolved").casefold().replace("_", " ").strip()
    status: RelevanceStatus = raw_status if raw_status in ALLOWED_RELEVANCE_STATUSES else "unresolved"  # type: ignore[assignment]
    relationship = _first(payload, "supporting_relationship", "candidate_to_twin_relationship", "scope_relationship")
    basis = _first(payload, "relevance_basis", "classification_basis")
    target = _first(payload, "proposed_twin_id", "twin_id", "governed_subject_id", "relevant_to")
    unresolved = _first(payload, "unresolved_scope_reason", "relevance_uncertainty")
    if status == "unresolved" and not unresolved:
        unresolved = "Owner-backed relevance status, relationship or classification was not supplied."
    # Identity is package-owner metadata, but a candidate is linked to it only by
    # an explicit candidate target/relationship; co-location is never a link.
    linked_identity = (identity.twin_id or identity.primary_subject_id) if target and relationship else None
    return CandidateRelevance(
        candidate_id=str(candidate.get("candidate_record_id") or candidate.get("original_source_id") or "candidate"),
        proposed_twin_identity=linked_identity,
        governed_subject=identity.primary_subject_name if linked_identity else None,
        industry=_first(payload, "industry", "industry_classification") or _first(inspection, "industry", "industry_classification"),
        sub_sector_or_domain=_first(payload, "sub_sector", "subsector", "governed_domain", "domain"),
        geography=_first(payload, "geography", "geographic_scope") or _first(inspection, "geography", "geographic_scope"),
        temporal_scope=_first(payload, "temporal_scope", "time_horizon", "period") or _first(inspection, "temporal_scope", "time_horizon"),
        status=status,
        relevance_basis=basis,
        decision_relevance=_first(payload, "decision_relevance"),
        commercial_consequence=_first(payload, "commercial_consequence", "commercial_significance"),
        owner=_first(payload, "relevance_owner", "owner", "package_owner") or identity.canonical_owner,
        supporting_relationship=relationship,
        unresolved_scope_reason=unresolved,
        truth_class=_first(payload, "truth_class") or _first(candidate, "truth_class"),
        evidence_state=_first(payload, "evidence_state", "evidence_status", "evidence_basis", "lineage_state", "lineage"),
        freshness=_first(payload, "freshness", "evidence_cut_off", "as_of"),
    )


def relevance_counts(projected: list[CandidateRelevance]) -> dict[str, int]:
    return {status: sum(item.status == status for item in projected) for status in ALLOWED_RELEVANCE_STATUSES}
