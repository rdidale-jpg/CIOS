"""Governed candidate feedback capture for the Enterprise Canvas.

Feedback records are workflow candidates only. They do not create Evidence,
Observations, Enterprise Model changes, pain-priority changes or automatic
research actions.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from cios.applications.flora.access import authenticated_flora_user, cookie_value, user_enterprise_access
from cios.applications.flora.storage import data_path, ensure_parent_writable

FEEDBACK_SCHEMA_VERSION = "flora-enterprise-canvas-feedback-v1"
ACTIONS = {
    "confirm": "Confirm this appears correct",
    "challenge": "Challenge this judgement",
    "correction": "Suggest a correction",
    "context": "Add context",
    "human_knowledge": "Add labelled human knowledge",
    "unknown": "Identify something unknown",
    "contradiction": "Flag contradictory information",
    "evidence_request": "Request further evidence",
    "refresh": "Suggest that the item needs refreshing",
}
HUMAN_KNOWLEDGE_TYPES = {"not_human_knowledge", "direct_knowledge", "interpretation", "account_knowledge", "calibration", "validation"}
VISIBILITY = {"standard", "restricted", "account_confidential"}
STATUSES = {"submitted", "under_review", "accepted_as_human_supplied_knowledge", "rejected", "deferred", "needs_evidence", "superseded", "withdrawn"}


@dataclass(frozen=True)
class FeedbackAuditEvent:
    event_type: str
    actor_id: str
    occurred_at: str
    note: str = ""
    status: str = ""
    supersedes_feedback_id: str = ""


@dataclass(frozen=True)
class EnterpriseCanvasFeedback:
    feedback_id: str
    enterprise_id: str
    action_type: str
    user_statement: str
    rationale: str
    contributor_identity: str
    contributor_role: str
    supplied_at: str
    status: str = "submitted"
    tile_view_id: str = ""
    displayed_judgement_ref: str = ""
    lineage_ref: str = ""
    related_canonical_refs: tuple[str, ...] = ()
    human_knowledge_classification: str = "not_human_knowledge"
    supports_weakens_or_contradicts: str = ""
    documentary_evidence_may_exist: str = "unknown"
    expected_consequence: str = ""
    visibility: str = "standard"
    review_owner: str = ""
    linked_unknown_candidate: dict[str, Any] = field(default_factory=dict)
    linked_contradiction_candidate: dict[str, Any] = field(default_factory=dict)
    evidence_request: dict[str, Any] = field(default_factory=dict)
    source_publication_or_package_version: str = ""
    effective_date: str = ""
    supersedes_feedback_id: str = ""
    audit_history: tuple[FeedbackAuditEvent, ...] = ()
    schema_version: str = FEEDBACK_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["related_canonical_refs"] = list(self.related_canonical_refs)
        data["audit_history"] = [asdict(e) for e in self.audit_history]
        return data

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "EnterpriseCanvasFeedback":
        row = dict(row)
        row["related_canonical_refs"] = tuple(row.get("related_canonical_refs") or ())
        row["audit_history"] = tuple(FeedbackAuditEvent(**e) for e in row.get("audit_history", ()))
        return cls(**row)


def _roles(headers: Any) -> set[str]:
    raw = headers.get("X-Flora-Roles") or cookie_value(headers, "flora_roles")
    return {item.strip() for item in str(raw or "").replace("|", ",").split(",") if item.strip()}


def can_submit_feedback(headers: Any, enterprise_id: str) -> bool:
    return bool(authenticated_flora_user(headers)) and ("*" in user_enterprise_access(headers) or enterprise_id in user_enterprise_access(headers)) and bool(_roles(headers) & {"feedback.submit", "package.review", "canvas.feedback"})


def can_view_feedback(headers: Any, enterprise_id: str, visibility: str = "standard") -> bool:
    if not (authenticated_flora_user(headers) and ("*" in user_enterprise_access(headers) or enterprise_id in user_enterprise_access(headers))):
        return False
    roles = _roles(headers)
    if visibility == "standard":
        return bool(roles & {"feedback.view", "feedback.submit", "package.review", "canvas.feedback"})
    return bool(roles & {"feedback.review", "feedback.restricted", "package.review"})


def can_review_feedback(headers: Any, enterprise_id: str) -> bool:
    return bool(authenticated_flora_user(headers)) and ("*" in user_enterprise_access(headers) or enterprise_id in user_enterprise_access(headers)) and bool(_roles(headers) & {"feedback.review", "package.review"})


class FeedbackAccessError(PermissionError):
    pass


class EnterpriseCanvasFeedbackRepository:
    def __init__(self, path: Path | None = None):
        self.path = path or data_path("enterprise_canvas", "feedback.jsonl")

    def list_all(self) -> list[EnterpriseCanvasFeedback]:
        if not self.path.exists():
            return []
        rows = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError(f"Malformed feedback record at {self.path}:{line_no}")
                rows.append(EnterpriseCanvasFeedback.from_dict(row))
        return rows

    def append(self, record: EnterpriseCanvasFeedback) -> EnterpriseCanvasFeedback:
        ensure_parent_writable(self.path)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
            handle.flush(); os.fsync(handle.fileno())
        return record

    def get(self, feedback_id: str) -> EnterpriseCanvasFeedback | None:
        return next((r for r in self.list_all() if r.feedback_id == feedback_id), None)


class EnterpriseCanvasFeedbackService:
    def __init__(self, repo: EnterpriseCanvasFeedbackRepository | None = None):
        self.repo = repo or EnterpriseCanvasFeedbackRepository()

    def submit(self, headers: Any, **payload: Any) -> EnterpriseCanvasFeedback:
        enterprise_id = str(payload.get("enterprise_id") or "").strip()
        if not can_submit_feedback(headers, enterprise_id):
            raise FeedbackAccessError("Actor is not authorised to submit Enterprise Canvas feedback")
        action = str(payload.get("action_type") or "").strip()
        if action not in ACTIONS:
            raise ValueError("Unsupported feedback action")
        statement = str(payload.get("user_statement") or "").strip()
        rationale = str(payload.get("rationale") or "").strip()
        if not statement or not rationale:
            raise ValueError("Feedback requires a statement and rationale")
        hsk = str(payload.get("human_knowledge_classification") or ("direct_knowledge" if action == "human_knowledge" else "not_human_knowledge"))
        if hsk not in HUMAN_KNOWLEDGE_TYPES or (action == "human_knowledge" and hsk == "not_human_knowledge"):
            raise ValueError("Human-Supplied Knowledge requires explicit labelling")
        visibility = str(payload.get("visibility") or "standard")
        if visibility not in VISIBILITY:
            raise ValueError("Unsupported visibility classification")
        now = str(payload.get("supplied_at") or datetime.now(timezone.utc).replace(microsecond=0).isoformat())
        contributor = authenticated_flora_user(headers)
        basis = str(payload.get("contributor_role") or headers.get("X-Flora-Role-Label") or "authorised contributor")
        fid = payload.get("feedback_id") or _feedback_id(enterprise_id, action, payload.get("tile_view_id", ""), payload.get("lineage_ref", ""), statement, now)
        unknown = {}
        contradiction = {}
        evidence_request = {}
        if action == "unknown":
            unknown = {"candidate_type": "unknown", "why_it_matters": rationale, "what_could_resolve_it": str(payload.get("what_could_resolve_it") or "Additional governed evidence or authorised validation")}
        if action == "contradiction":
            contradiction = {"candidate_type": "contradiction", "position_a": str(payload.get("position_a") or payload.get("displayed_judgement_ref") or "displayed judgement"), "position_b": statement, "why_it_matters": rationale, "what_could_resolve_it": str(payload.get("what_could_resolve_it") or "Fresher governed Evidence or review decision")}
        if action == "evidence_request":
            evidence_request = {"evidence_required": statement, "why_it_matters": rationale, "could_strengthen_weaken_or_retire": str(payload.get("supports_weakens_or_contradicts") or "not supplied"), "likely_owner_or_source": str(payload.get("likely_owner_or_source") or "not supplied"), "urgency_or_accountability_event": str(payload.get("urgency_or_accountability_event") or "not supplied")}
        record = EnterpriseCanvasFeedback(
            feedback_id=str(fid), enterprise_id=enterprise_id, tile_view_id=str(payload.get("tile_view_id") or ""), displayed_judgement_ref=str(payload.get("displayed_judgement_ref") or ""), lineage_ref=str(payload.get("lineage_ref") or ""), related_canonical_refs=tuple(payload.get("related_canonical_refs") or ()), action_type=action, user_statement=statement, rationale=rationale, contributor_identity=contributor, contributor_role=basis, supplied_at=now, human_knowledge_classification=hsk, supports_weakens_or_contradicts=str(payload.get("supports_weakens_or_contradicts") or ""), documentary_evidence_may_exist=str(payload.get("documentary_evidence_may_exist") or "unknown"), expected_consequence=str(payload.get("expected_consequence") or ""), visibility=visibility, review_owner=str(payload.get("review_owner") or ""), linked_unknown_candidate=unknown, linked_contradiction_candidate=contradiction, evidence_request=evidence_request, source_publication_or_package_version=str(payload.get("source_publication_or_package_version") or ""), effective_date=str(payload.get("effective_date") or ""), supersedes_feedback_id=str(payload.get("supersedes_feedback_id") or ""), audit_history=(FeedbackAuditEvent("submitted", contributor, now, "Stored as candidate human knowledge; canonical Twin unchanged.", "submitted", str(payload.get("supersedes_feedback_id") or "")),)
        )
        return self.repo.append(record)

    def visible_feedback(self, headers: Any, enterprise_id: str, tile_view_id: str = "", lineage_ref: str = "") -> list[EnterpriseCanvasFeedback]:
        out = []
        for record in self.repo.list_all():
            if record.enterprise_id != enterprise_id:
                continue
            if tile_view_id and record.tile_view_id != tile_view_id:
                continue
            if lineage_ref and record.lineage_ref != lineage_ref:
                continue
            if can_view_feedback(headers, enterprise_id, record.visibility):
                out.append(record)
        return out

    def change_status(self, headers: Any, feedback_id: str, status: str, note: str = "") -> EnterpriseCanvasFeedback:
        current = self.repo.get(feedback_id)
        if current is None:
            raise ValueError("Feedback record not found")
        if status not in STATUSES:
            raise ValueError("Unsupported feedback status")
        if not can_review_feedback(headers, current.enterprise_id):
            raise FeedbackAccessError("Actor is not authorised to review Enterprise Canvas feedback")
        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        actor = authenticated_flora_user(headers)
        updated = EnterpriseCanvasFeedback.from_dict({**current.to_dict(), "status": status, "audit_history": [*current.to_dict()["audit_history"], asdict(FeedbackAuditEvent("status_changed", actor, now, note, status))]})
        return self.repo.append(updated)


def _feedback_id(enterprise_id: str, action: str, tile_id: str, lineage_ref: str, statement: str, supplied_at: str) -> str:
    digest = hashlib.sha256("\n".join([enterprise_id, action, tile_id, lineage_ref, statement, supplied_at]).encode()).hexdigest()[:20]
    return f"ecf-{digest}"
