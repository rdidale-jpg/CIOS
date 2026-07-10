"""Candidate staging for governed Blueprint package import.

Staged candidates are review records only. They never create Evidence,
Observations, Enterprise Model state, or canonical promotion side effects.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

from cios.applications.flora.storage import atomic_write_json, data_path, ensure_writable_dir

from .archive import sha256_bytes
from .ledger import utc_now

CandidateStatus = Literal["accepted", "quarantined", "rejected"]

SUPPORTED_CANONICAL_CLASSES = {
    "enterprise", "twin", "source", "evidence", "observation", "entity", "relationship",
    "enterprise_model_candidate", "unknown", "contradiction", "human_knowledge",
    "refresh_trigger", "publication_reference",
}
PROJECTION_ONLY_CLASSES = {
    "pain_point", "current_response", "response_effectiveness", "residual_pain",
    "burning_platform", "transformation_pressure_view", "priority_disposition",
    "stakeholder_hot_button", "solution_pattern", "executive_publication",
}
SUPPORTED_RECORD_CLASSES = SUPPORTED_CANONICAL_CLASSES | PROJECTION_ONLY_CLASSES

@dataclass(frozen=True)
class ValidationFinding:
    severity: Literal["warning", "error"]
    code: str
    message: str
    location: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class CandidateImportRecord:
    schema_version: str
    candidate_record_id: str
    source_package_ref: str
    source_package_sha256: str
    source_file: str
    source_sheet: str
    source_location: dict[str, Any]
    original_source_id: str
    candidate_object_class: str
    truth_class: str
    payload: dict[str, Any]
    validation_status: CandidateStatus
    validation_findings: tuple[ValidationFinding, ...]
    source_fingerprint: str
    created_at: str
    import_run_id: str
    canonical_mutation_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["validation_findings"] = [f.to_dict() for f in self.validation_findings]
        return data

@dataclass(frozen=True)
class ImportRunDryRunResult:
    schema_version: str
    import_run_id: str
    package_ref: str
    package_sha256: str
    files_inspected: tuple[str, ...]
    supported_records_discovered: int
    candidate_records_staged: int
    records_accepted_into_staging: int
    records_quarantined: int
    records_rejected: int
    unsupported_classes: tuple[str, ...]
    unresolved_references: tuple[str, ...]
    warnings: tuple[str, ...]
    errors: tuple[str, ...]
    canonical_mutations: int = 0
    execution_trace: tuple[dict[str, Any], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key in ("files_inspected", "unsupported_classes", "unresolved_references", "warnings", "errors", "execution_trace"):
            data[key] = list(data[key])
        return data

class CandidateStagingRepository:
    def root_for(self, import_run_id: str):
        return data_path("blueprint_import", "staging", import_run_id)

    def save_candidate(self, candidate: CandidateImportRecord) -> None:
        atomic_write_json(self.root_for(candidate.import_run_id) / "candidates" / f"{candidate.candidate_record_id}.json", candidate.to_dict())

    def save_result(self, result: ImportRunDryRunResult) -> None:
        root = self.root_for(result.import_run_id)
        ensure_writable_dir(root)
        atomic_write_json(root / "summary.json", result.to_dict())

    def load_summary(self, import_run_id: str) -> dict[str, Any] | None:
        path = self.root_for(import_run_id) / "summary.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def list_candidates(self, import_run_id: str) -> list[dict[str, Any]]:
        root = self.root_for(import_run_id) / "candidates"
        if not root.exists():
            return []
        return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(root.glob("*.json"))]

def candidate_id(package_ref: str, source_file: str, external_id: str, record_class: str) -> str:
    return "bpi-cand-" + sha256_bytes(f"{package_ref}\n{source_file}\n{external_id}\n{record_class}".encode("utf-8"))[:24]
