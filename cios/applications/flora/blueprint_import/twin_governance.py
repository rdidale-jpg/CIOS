"""Read-only Twin identity, dependency and downstream-review projections.

This module deliberately does not own canonical intelligence.  It projects
explicit package metadata and stable identifiers through the existing import
lifecycle, then records reconciliation work without changing a dependent Twin.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Any, Literal

from cios.applications.flora.storage import atomic_write_json, data_path, ensure_writable_dir

from .candidates import CandidateStagingRepository
from .ledger import BlueprintImportLedger, utc_now
from .models import BlueprintPackageRecord
from .registry import BlueprintPackageRegistry

SUPPORTED_TWIN_TYPES = ("industry", "enterprise", "market_participant", "opportunity")
COMMERCIAL_ROLES = ("supplier", "buyer", "regulator", "operator", "intermediary", "partner", "competitor")


@dataclass(frozen=True)
class TwinIdentityProjection:
    twin_id: str | None
    twin_type: str | None
    primary_subject_id: str | None
    primary_subject_name: str | None
    primary_subject_class: str | None
    governed_scope: Any
    canonical_owner: str | None
    package_version: str
    research_state: str | None
    decision_maturity: str | None
    source_package_identity: str
    status: Literal["recognised", "ambiguous"]
    ambiguity_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def project_twin_identity(package: BlueprintPackageRecord) -> TwinIdentityProjection:
    """Project only explicit governed identity; never derive it from a label."""
    inspection = dict(package.package_inspection or {})
    # A confirmation is an overlay on preserved package metadata, never a rewrite.
    confirmation = GovernedIdentityResolutionRepository().get(package.import_run_id)
    if confirmation:
        inspection.update(confirmation["resolved_identity"])
    twin_type = str(inspection.get("twin_type") or "").casefold() or None
    subject_id = inspection.get("primary_subject_id")
    subject_name = inspection.get("primary_subject_name")
    subject_class = inspection.get("primary_subject_class")
    scope = inspection.get("governed_scope")
    owner = inspection.get("canonical_owner")
    # The accepted Blueprint envelope explicitly declares enterprise identity.
    if inspection.get("contract_type") == "Blueprint Package" and package.identity.enterprise_id:
        twin_type = twin_type or "enterprise"
        subject_id = subject_id or package.identity.enterprise_id
        subject_name = subject_name or inspection.get("enterprise_name")
        subject_class = subject_class or "enterprise"
        owner = owner or package.identity.enterprise_id
    complete = bool(twin_type in SUPPORTED_TWIN_TYPES and subject_id and subject_name and subject_class and scope not in (None, "") and owner)
    return TwinIdentityProjection(
        twin_id=str(inspection.get("twin_id") or subject_id) if (inspection.get("twin_id") or subject_id) else None,
        twin_type=twin_type,
        primary_subject_id=str(subject_id) if subject_id else None,
        primary_subject_name=str(subject_name) if subject_name else None,
        primary_subject_class=str(subject_class).casefold() if subject_class else None,
        governed_scope=scope,
        canonical_owner=str(owner) if owner else None,
        package_version=str(inspection.get("package_version") or package.identity.package_version),
        research_state=str(inspection.get("research_state")) if inspection.get("research_state") else None,
        decision_maturity=str(inspection.get("decision_maturity")) if inspection.get("decision_maturity") else None,
        source_package_identity=package.identity.package_id,
        status="recognised" if complete else "ambiguous",
        ambiguity_reason=None if complete else "Explicit primary-subject, scope or canonical-owner metadata is incomplete.",
    )


class GovernedIdentityResolutionRepository:
    """Audit explicit linkage to an already governed Twin identity."""

    def path(self, import_run_id: str):
        return data_path("blueprint_import", "identity_resolution", f"{import_run_id}.json")

    def get(self, import_run_id: str) -> dict[str, Any] | None:
        path = self.path(import_run_id)
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None

    def confirm_existing(self, package: BlueprintPackageRecord, existing_package_ref: str,
                         actor: str, rationale: str) -> dict[str, Any]:
        """Confirm only an identity backed by an existing governed registry record."""
        if not actor.strip() or not rationale.strip():
            raise ValueError("Identity confirmation requires an actor and rationale.")
        existing = BlueprintPackageRegistry().get(existing_package_ref)
        if existing is None or existing.package_ref == package.package_ref:
            raise ValueError("Select an existing governed Twin identity; free-text identity creation is not permitted.")
        identity = project_twin_identity(existing)
        if identity.status != "recognised":
            raise ValueError("The selected existing Twin does not have a complete governed identity.")
        source = dict(package.package_inspection or {})
        resolved = {
            "twin_id": identity.twin_id, "twin_type": identity.twin_type,
            "primary_subject_id": identity.primary_subject_id,
            "primary_subject_name": identity.primary_subject_name,
            "primary_subject_class": identity.primary_subject_class,
            "governed_scope": identity.governed_scope, "canonical_owner": identity.canonical_owner,
        }
        row = {"import_run_id": package.import_run_id, "actor": actor.strip(), "confirmed_at": utc_now(),
               "rationale": rationale.strip(), "source_package": package.identity.package_id,
               "source_package_checksum": package.package_sha256, "matched_package_ref": existing_package_ref,
               "original_package_metadata": source, "resolved_identity": resolved}
        atomic_write_json(self.path(package.import_run_id), row)
        BlueprintImportLedger().append("twin_identity_confirmed", row)
        return row


def governed_semantics(candidate: dict[str, Any]) -> dict[str, Any]:
    """Keep identity, commercial, package and projection roles separate."""
    payload = candidate.get("payload") or {}
    identity_type = payload.get("object_type") or payload.get("entity_type") or payload.get("record_type")
    roles = payload.get("commercial_roles") or payload.get("roles") or payload.get("role") or []
    if isinstance(roles, str):
        roles = [roles]
    return {
        "canonical_identity_type": str(identity_type).casefold() if identity_type else None,
        "commercial_roles": [str(role).casefold() for role in roles if str(role).casefold() in COMMERCIAL_ROLES],
        "package_role": payload.get("package_role"),
        "projection_role": payload.get("projection_role") or ("contained projection" if payload.get("canonical_owner_id") and payload.get("canonical_owner_id") != payload.get("twin_id") else None),
    }


class TwinDependencyService:
    """Discover promoted dependants using stable IDs, never names."""

    def discover(self, source: BlueprintPackageRecord) -> list[dict[str, Any]]:
        identity = project_twin_identity(source)
        if identity.status != "recognised" or not identity.primary_subject_id:
            return []
        matches: list[dict[str, Any]] = []
        for package in BlueprintPackageRegistry().list():
            if package.package_ref == source.package_ref or not self._is_promoted(package.import_run_id):
                continue
            dependent_identity = project_twin_identity(package)
            for candidate in CandidateStagingRepository().list_candidates(package.import_run_id):
                payload = candidate.get("payload") or {}
                stable_values = self._stable_values(payload)
                if identity.primary_subject_id not in stable_values:
                    continue
                matches.append({
                    "dependent_twin_id": dependent_identity.twin_id or package.identity.package_id,
                    "dependent_twin_name": dependent_identity.primary_subject_name or package.identity.package_id,
                    "dependent_twin_type": dependent_identity.twin_type or "unavailable",
                    "dependency_reason": "Contains a governed projection or relationship to the canonical subject.",
                    "affected_canonical_object": identity.primary_subject_id,
                    "supporting_lineage": {"package_ref": package.package_ref, "candidate_record_id": candidate.get("candidate_record_id"), "stable_id": identity.primary_subject_id},
                    "confidence": "confirmed",
                    "review_required": True,
                    "dependent_import_run_id": package.import_run_id,
                })
                break
        return matches

    @staticmethod
    def _is_promoted(import_run_id: str) -> bool:
        path = data_path("blueprint_import", "lifecycle", f"{import_run_id}.json")
        return path.exists() and json.loads(path.read_text(encoding="utf-8")).get("state") == "promoted"

    @staticmethod
    def _stable_values(value: Any) -> set[str]:
        found: set[str] = set()
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"id", "stable_id", "external_id", "canonical_id", "enterprise_id", "source_object_id", "target_object_id", "subject_id", "canonical_owner_id"}:
                    if isinstance(item, str): found.add(item)
                elif isinstance(item, (dict, list)): found.update(TwinDependencyService._stable_values(item))
        elif isinstance(value, list):
            for item in value: found.update(TwinDependencyService._stable_values(item))
        return found


def assess_impacts(source: BlueprintPackageRecord, dependencies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates = CandidateStagingRepository().list_candidates(source.import_run_id)
    counts: dict[str, int] = {}
    for candidate in candidates:
        cls = str(candidate.get("candidate_object_class") or "unclassified")
        counts[cls] = counts.get(cls, 0) + 1
    for dependency in dependencies:
        dependency.update({
            "impact_class": "reconciliation required",
            "changed_objects": counts,
            "new_unknowns": counts.get("unknown", 0),
            "new_contradictions": counts.get("contradiction", 0),
            "recommended_action": "Create a downstream Twin reconciliation review after promotion.",
        })
    return dependencies


class DownstreamReconciliationRepository:
    def create_pending(self, source: BlueprintPackageRecord, promoted_version: str, impacts: list[dict[str, Any]], actor: str) -> list[dict[str, Any]]:
        created = []
        root = data_path("blueprint_import", "downstream_reconciliation")
        ensure_writable_dir(root)
        for impact in impacts:
            review_id = f"reconcile-{source.package_sha256[:12]}-{impact['dependent_twin_id']}"
            path = root / f"{review_id}.json"
            if path.exists():
                created.append(json.loads(path.read_text(encoding="utf-8")))
                continue
            record = {"review_id": review_id, "source_twin": project_twin_identity(source).to_dict(), "promoted_version": promoted_version,
                      "dependent_twin_id": impact["dependent_twin_id"], "affected_projections": impact["affected_canonical_object"],
                      "proposed_changes": impact["changed_objects"], "evidence_and_lineage": impact["supporting_lineage"],
                      "unknowns": impact["new_unknowns"], "contradictions": impact["new_contradictions"], "supersession_information": "Preserved in source candidate lineage",
                      "approval_status": "pending", "audit_history": [{"event": "created_after_source_promotion", "actor": actor, "at": utc_now()}],
                      "dependent_twin_mutated": False}
            atomic_write_json(path, record); created.append(record)
        return created

    def list_for_source(self, source_package_id: str) -> list[dict[str, Any]]:
        root = data_path("blueprint_import", "downstream_reconciliation")
        if not root.exists(): return []
        return [row for path in sorted(root.glob("*.json")) if (row := json.loads(path.read_text(encoding="utf-8")))["source_twin"]["source_package_identity"] == source_package_id]
