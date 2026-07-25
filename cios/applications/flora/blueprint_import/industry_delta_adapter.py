"""Industry Twin Delta adapter for the existing Blueprint candidate boundary.

The producer contract has existed in both row-oriented (``records``) and
operation-oriented (``creates``/``updates``) forms.  This adapter deliberately
normalises those shapes at the one existing ingestion boundary; it does not
look in the repository, infer a mission, or substitute fixture data.
"""
from __future__ import annotations

import json
from typing import Any, Callable

from .archive import sha256_bytes
from .candidates import CandidateImportRecord, ValidationFinding, candidate_id
from .ledger import utc_now
from .models import BlueprintPackageRecord


class IndustryTwinDeltaAdapter:
    """Translate delta records; staging, review and promotion remain unchanged."""

    # Contract vocabulary is kept here rather than in mission/package-specific
    # code.  A producer may override a path with ``object_collections`` metadata.
    COLLECTIONS = {
        "enterprise_twins": ("twins/enterprise-twins.json", "enterprise_twin"),
        "market_participant_twins": ("twins/market-participant-twins.json", "market_participant_twin"),
        "opportunity_twins": ("twins/opportunity-twins.json", "opportunity_twin"),
        "flow_twins": ("machine-inspectable/flow-twins.json", "flow_twin"),
    }

    def candidates(
        self, package: BlueprintPackageRecord, delta: dict[str, Any], source_file: str,
        read_collection: Callable[[str], bytes] | None = None,
    ) -> tuple[CandidateImportRecord, ...]:
        records = self._records(delta)
        primary = delta.get("primary_objects")
        if isinstance(primary, dict) and any(isinstance(value, list) for value in primary.values()):
            records = self._resolve_references(delta, primary, read_collection)
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

    def _resolve_references(self, delta, primary, read_collection):
        if read_collection is None:
            raise ValueError("referenced primary_objects require package collection access")
        errors: list[str] = []
        resolved: list[tuple[dict[str, Any], str]] = []
        declared = delta.get("object_collections") if isinstance(delta.get("object_collections"), dict) else {}
        for category, references in primary.items():
            if category not in self.COLLECTIONS:
                continue
            if not isinstance(references, list):
                errors.append(f"primary_objects.{category} must be a list of stable identifiers")
                continue
            default_path, expected_type = self.COLLECTIONS[category]
            declaration = declared.get(category)
            path = str(declaration.get("path") if isinstance(declaration, dict) else declaration or default_path)
            try:
                document = json.loads(read_collection(path).decode("utf-8"))
            except KeyError:
                errors.append(f"missing governed object collection for {category}: {path}")
                continue
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                errors.append(f"invalid governed object collection {path}: {exc}")
                continue
            rows = self._collection_rows(document, category)
            index: dict[str, dict[str, Any]] = {}
            duplicates: set[str] = set()
            for row in rows:
                stable_id = self._stable_id(row)
                if not stable_id:
                    continue
                if stable_id in index:
                    duplicates.add(stable_id)
                index[stable_id] = row
            if duplicates:
                errors.append(f"duplicate stable identifier(s) in {path}: {', '.join(sorted(duplicates))}")
            for reference in references:
                stable_id = str(reference)
                row = index.get(stable_id)
                if row is None:
                    errors.append(f"unresolved {category} stable identifier: {stable_id}")
                    continue
                actual_type = self._normalise_type(row.get("object_type") or row.get("record_class") or row.get("type") or expected_type)
                if actual_type != expected_type:
                    errors.append(f"object type conflict for {stable_id}: expected {expected_type}, found {actual_type or '<missing>'}")
                    continue
                if row.get("promotable") is False or str(row.get("promotion_status") or "").casefold() in {"non-promotable", "non_promotable", "excluded"}:
                    errors.append(f"referenced governed object is explicitly non-promotable: {stable_id}")
                    continue
                governed = dict(row)
                governed.setdefault("stable_id", stable_id)
                governed["governed_object_category"] = category
                # All four governed definitions enter the established Twin
                # staging class; their precise contract type remains in payload.
                governed["record_class"] = "twin"
                resolved.append((governed, "twin"))
        if errors:
            raise ValueError("; ".join(errors))
        return resolved

    @staticmethod
    def _collection_rows(document: Any, category: str) -> list[dict[str, Any]]:
        if isinstance(document, list):
            return [row for row in document if isinstance(row, dict)]
        if isinstance(document, dict):
            for key in (category, "objects", "records", "twins"):
                value = document.get(key)
                if isinstance(value, list):
                    return [row for row in value if isinstance(row, dict)]
        return []

    @staticmethod
    def _stable_id(row: dict[str, Any]) -> str:
        return str(row.get("stable_id") or row.get("stable_identifier") or row.get("object_id") or row.get("external_id") or row.get("id") or "")

    @staticmethod
    def _normalise_type(value: Any) -> str:
        text = str(value or "").strip().casefold().replace("-", "_").replace(" ", "_")
        aliases = {
            "enterprise": "enterprise_twin", "enterprisetwin": "enterprise_twin",
            "market_participant": "market_participant_twin", "marketparticipanttwin": "market_participant_twin",
            "opportunity": "opportunity_twin", "opportunitytwin": "opportunity_twin",
            "flow": "flow_twin", "flowtwin": "flow_twin",
        }
        return aliases.get(text, text)

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
