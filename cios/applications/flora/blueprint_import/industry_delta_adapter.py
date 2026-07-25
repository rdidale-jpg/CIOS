"""Industry Twin Delta adapter for the existing Blueprint candidate boundary."""
from __future__ import annotations

from typing import Any

from .archive import sha256_bytes
from .candidates import CandidateImportRecord, ValidationFinding, candidate_id
from .ledger import utc_now
from .models import BlueprintPackageRecord


class IndustryTwinDeltaAdapter:
    """Translate delta records; staging, review and promotion remain unchanged."""

    def candidates(self, package: BlueprintPackageRecord, delta: dict[str, Any], source_file: str) -> tuple[CandidateImportRecord, ...]:
        records = delta.get("records", [])
        if not isinstance(records, list):
            return ()
        output: list[CandidateImportRecord] = []
        for index, row in enumerate(records, 1):
            if not isinstance(row, dict):
                continue
            external_id = str(row.get("external_id") or f"delta-{index}")
            object_class = str(row.get("record_class") or "")
            findings: tuple[ValidationFinding, ...] = ()
            status = "accepted"
            if not object_class:
                status = "quarantined"
                findings = (ValidationFinding("error", "missing_record_class", "Delta record does not declare record_class", f"{source_file}#L{index}"),)
            payload = row.get("payload", {}) if isinstance(row.get("payload"), dict) else {}
            output.append(CandidateImportRecord(
                "1.0", candidate_id(package.package_ref, source_file, external_id, object_class),
                package.package_ref, package.package_sha256, source_file, "", {"record": index}, external_id,
                object_class, str(row.get("truth_class") or "unknown"), payload, status, findings,
                sha256_bytes(__import__("json").dumps(payload, sort_keys=True).encode()), utc_now(),
                package.import_run_id, 0,
            ))
        return tuple(output)
