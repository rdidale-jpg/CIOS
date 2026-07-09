"""Governed candidate review decisions for Blueprint imports.

Review decisions are append-only audit records. They do not promote candidates or
mutate canonical Evidence, Observations or Enterprise Model state.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

from cios.applications.flora.access import authenticated_flora_user, user_enterprise_access
from cios.applications.flora.storage import atomic_write_json, data_path

from .archive import sha256_bytes
from .candidates import CandidateStagingRepository
from .ledger import BlueprintImportLedger, utc_now
from .registry import BlueprintPackageRegistry

ReviewDecisionValue = Literal["approve", "reject", "defer", "quarantine", "unsupported"]


class BlueprintReviewError(PermissionError):
    """Raised when a review decision cannot be recorded."""


def _roles(headers: Any) -> set[str]:
    raw = headers.get("X-Flora-Roles", "") or ""
    return {item.strip() for item in str(raw).replace("|", ",").split(",") if item.strip()}


def can_review_blueprint_candidate(headers: Any, enterprise_id: str) -> bool:
    if not authenticated_flora_user(headers):
        return False
    allowed = user_enterprise_access(headers)
    if "*" not in allowed and enterprise_id not in allowed:
        return False
    return bool(_roles(headers) & {"package.review", "blueprint_import_admin"})


@dataclass(frozen=True)
class CandidateReviewDecision:
    schema_version: str
    review_decision_id: str
    candidate_id: str
    import_run_id: str
    package_ref: str
    original_source_id: str
    object_class: str
    decision: ReviewDecisionValue
    reviewer_identity: str
    timestamp: str
    rationale: str
    validation_findings: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    unresolved_issues: tuple[str, ...] = field(default_factory=tuple)
    mapped_canonical_target_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["validation_findings"] = list(self.validation_findings)
        data["unresolved_issues"] = list(self.unresolved_issues)
        return data


def review_decision_id(candidate_id: str, decision: str, reviewer: str, mapped_target: str = "") -> str:
    return "bpi-review-" + sha256_bytes(f"{candidate_id}\n{decision}\n{reviewer}\n{mapped_target}".encode())[:24]


class CandidateReviewRepository:
    def _dir(self, import_run_id: str):
        return data_path("blueprint_import", "reviews", import_run_id)

    def save(self, decision: CandidateReviewDecision) -> CandidateReviewDecision:
        atomic_write_json(self._dir(decision.import_run_id) / f"{decision.review_decision_id}.json", decision.to_dict())
        return decision

    def latest_by_candidate(self, import_run_id: str) -> dict[str, dict[str, Any]]:
        root = self._dir(import_run_id)
        if not root.exists():
            return {}
        out: dict[str, dict[str, Any]] = {}
        for path in sorted(root.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            out[str(data["candidate_id"])] = data
        return out


class CandidateReviewService:
    def __init__(self, registry=None, staging=None, repository=None, ledger=None):
        self.registry = registry or BlueprintPackageRegistry()
        self.staging = staging or CandidateStagingRepository()
        self.repository = repository or CandidateReviewRepository()
        self.ledger = ledger or BlueprintImportLedger()

    def record_decision(self, candidate_id: str, decision: ReviewDecisionValue, reviewer: str, rationale: str, headers: Any, mapped_canonical_target_id: str = "", unresolved_issues: tuple[str, ...] = ()) -> CandidateReviewDecision:
        candidate = self._candidate(candidate_id)
        package = self.registry.get(str(candidate["source_package_ref"]))
        if not package or not can_review_blueprint_candidate(headers, package.identity.enterprise_id):
            raise BlueprintReviewError("Actor is not authorised to record Blueprint review decisions")
        if decision not in {"approve", "reject", "defer", "quarantine", "unsupported"}:
            raise BlueprintReviewError("Unsupported review decision")
        record = CandidateReviewDecision(
            "1.0", review_decision_id(candidate_id, decision, reviewer, mapped_canonical_target_id), candidate_id,
            str(candidate["import_run_id"]), str(candidate["source_package_ref"]), str(candidate["original_source_id"]),
            str(candidate["candidate_object_class"]), decision, reviewer, utc_now(), rationale,
            tuple(candidate.get("validation_findings", [])), tuple(unresolved_issues), mapped_canonical_target_id,
        )
        saved = self.repository.save(record)
        self.ledger.append("candidate_review_decision_recorded", saved.to_dict())
        return saved

    def _candidate(self, candidate_id: str) -> dict[str, Any]:
        for stage_root in data_path("blueprint_import", "staging").glob("*/candidates/*.json"):
            data = json.loads(stage_root.read_text(encoding="utf-8"))
            if data.get("candidate_record_id") == candidate_id:
                return data
        raise BlueprintReviewError("Unknown candidate")
