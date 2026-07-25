"""Industry Twin Delta adapter for the existing Blueprint candidate boundary.

The producer contract has existed in both row-oriented (``records``) and
operation-oriented (``creates``/``updates``) forms.  This adapter deliberately
normalises those shapes at the one existing ingestion boundary; it does not
look in the repository, infer a mission, or substitute fixture data.
"""
from __future__ import annotations

from typing import Any

from .archive import sha256_bytes
from .candidates import CandidateImportRecord, ValidationFinding, candidate_id
from .ledger import utc_now
from .models import BlueprintPackageRecord


class IndustryTwinDeltaAdapter:
    """Translate delta records; staging, review and promotion remain unchanged."""

    def candidates(self, package: BlueprintPackageRecord, delta: dict[str, Any], source_file: str) -> tuple[CandidateImportRecord, ...]:
        records = self._records(delta)
        if not records:
            keys = ", ".join(sorted(str(key) for key in delta)) or "<empty document>"
            raise ValueError(
                "no staging candidates could be extracted from the governed Delta "
                f"at {source_file}; inspected top-level fields: {keys}"
            )
        output: list[CandidateImportRecord] = []
        for index, (row, collection_class) in enumerate(records, 1):
            external_id = str(row.get("external_id") or row.get("stable_id") or row.get("object_id") or row.get("id") or f"delta-{index}")
            object_class = self._object_class(row, collection_class)
            findings: tuple[ValidationFinding, ...] = ()
            status = "accepted"
            if not object_class:
                status = "quarantined"
                findings = (ValidationFinding("error", "missing_record_class", "Delta record does not declare record_class", f"{source_file}#L{index}"),)
            payload_value = row.get("payload") if isinstance(row.get("payload"), dict) else row.get("data")
            payload = dict(payload_value) if isinstance(payload_value, dict) else {
                key: value for key, value in row.items()
                if key not in {"external_id", "stable_id", "object_id", "id", "record_class", "object_class", "object_type", "type", "truth_class"}
            }
            # The governed contract itself supplies the routing type.  Recording
            # it on candidates makes the generic review UI deterministic without
            # inventing or replacing the package's identity.
            payload.setdefault("twin_type", "industry")
            output.append(CandidateImportRecord(
                "1.0", candidate_id(package.package_ref, source_file, external_id, object_class),
                package.package_ref, package.package_sha256, source_file, "", {"record": index}, external_id,
                object_class, str(row.get("truth_class") or "unknown"), payload, status, findings,
                sha256_bytes(__import__("json").dumps(payload, sort_keys=True).encode()), utc_now(),
                package.import_run_id, 0,
            ))
        return tuple(output)

    @staticmethod
    def _records(delta: dict[str, Any]) -> list[tuple[dict[str, Any], str]]:
        """Return records from supported governed-delta envelopes.

        Collection names are schema vocabulary, not mission identifiers.  A
        nested ``delta``/``changes`` envelope and operation buckets are accepted
        because producers use both representations.
        """
        output: list[tuple[dict[str, Any], str]] = []
        containers = [delta]
        for key in ("delta", "changes", "operations"):
            if isinstance(delta.get(key), dict):
                containers.append(delta[key])
        generic = {"records", "objects", "candidates", "upserts", "creates", "updates", "additions"}
        grouped = {
            "twins": "twin", "industry_twins": "twin", "sources": "source", "evidence": "evidence",
            "observations": "observation", "entities": "entity", "relationships": "relationship",
            "unknowns": "unknown", "contradictions": "contradiction", "human_knowledge": "human_knowledge",
            "refresh_triggers": "refresh_trigger", "publication_references": "publication_reference",
        }
        for container in containers:
            for key, value in container.items():
                if key not in generic and key not in grouped:
                    continue
                values = value if isinstance(value, list) else []
                for row in values:
                    if isinstance(row, dict):
                        output.append((row, grouped.get(key, "")))
        return output

    @staticmethod
    def _object_class(row: dict[str, Any], collection_class: str) -> str:
        value = str(row.get("record_class") or row.get("object_class") or row.get("object_type") or row.get("type") or collection_class).strip().casefold()
        value = value.replace("-", "_").replace(" ", "_")
        aliases = {"industry_twin": "twin", "twin_record": "twin", "knowledge_source": "source", "evidence_record": "evidence", "observation_record": "observation"}
        return aliases.get(value, value.removesuffix("_record"))
