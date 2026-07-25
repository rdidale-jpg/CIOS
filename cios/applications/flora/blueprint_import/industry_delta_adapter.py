"""Translate governed Industry Twin Delta objects at the existing staging boundary."""
from __future__ import annotations

import json
from typing import Any, Callable

from .archive import sha256_bytes
from .candidates import CandidateImportRecord, ValidationFinding, candidate_id
from .ledger import utc_now
from .models import BlueprintPackageRecord


CollectionReader = Callable[[str, tuple[str, ...]], tuple[tuple[str, Any], ...]]


class IndustryTwinDeltaAdapter:
    """Translate inline or referenced governed objects without mission-specific rules."""

    PROMOTABLE = {
        "enterprise_twins": "twin",
        "market_participant_twins": "twin",
        "opportunity_twins": "twin",
        "flow_twins": "twin",
    }
    IDENTIFIERS = ("external_id", "stable_id", "object_id", "twin_id", "id")

    def __init__(self) -> None:
        self.diagnostics: dict[str, Any] = {}

    def candidates(self, package: BlueprintPackageRecord, delta: dict[str, Any], source_file: str,
                   read_collection: CollectionReader | None = None) -> tuple[CandidateImportRecord, ...]:
        records = self._records(delta)
        primary = self._primary_objects(delta)
        diag: dict[str, Any] = {
            "primary_object_categories": sorted(primary), "primary_object_shapes": {},
            "collection_files_selected": [], "collection_root_shapes": {},
            "identifier_fields_used": {}, "objects_indexed": {}, "references_requested": {},
            "references_resolved": {}, "unresolved_identifiers": {}, "resolved_counts_by_category": {},
        }
        for category, declared in primary.items():
            shape = self._shape(declared)
            diag["primary_object_shapes"][category] = shape
            inline, references = self._declared_objects(declared)
            if inline:
                records.extend((row, self.PROMOTABLE.get(category, category.removesuffix("s"))) for row in inline)
            diag["references_requested"][category] = len(references)
            if not references:
                diag["references_resolved"][category] = 0
                continue
            if read_collection is None:
                raise ValueError(f"primary_objects category {category} contains references but no governed collection reader was supplied")
            paths = self._declared_paths(delta, category)
            selected = read_collection(category, paths)
            if not selected:
                raise ValueError(f"missing governed collection for primary_objects category {category}")
            index: dict[str, tuple[dict[str, Any], str, str]] = {}
            for path, document in selected:
                diag["collection_files_selected"].append(path)
                rows, root_shape = self._collection_rows(document, category)
                diag["collection_root_shapes"][path] = root_shape
                for row in rows:
                    identifier_field = next((field for field in self.IDENTIFIERS if row.get(field) not in (None, "")), None)
                    if identifier_field is None:
                        raise ValueError(f"governed collection {path} for {category} contains an object with no stable identifier ({', '.join(self.IDENTIFIERS)})")
                    identifier = str(row[identifier_field])
                    index[identifier] = (row, path, identifier_field)
                    diag["identifier_fields_used"].setdefault(category, identifier_field)
            diag["objects_indexed"][category] = len(index)
            missing = [identifier for identifier in references if identifier not in index]
            diag["unresolved_identifiers"][category] = missing
            diag["references_resolved"][category] = len(references) - len(missing)
            if missing:
                raise ValueError(f"unresolved governed identifiers in {category}: {', '.join(missing)}")
            for identifier in references:
                row, path, _ = index[identifier]
                records.append((dict(row) | {"_governed_collection_path": path, "_governed_category": category}, self.PROMOTABLE.get(category, category.removesuffix("s"))))
            diag["resolved_counts_by_category"][category] = len(references)
        self.diagnostics = diag
        if not records:
            keys = ", ".join(sorted(str(key) for key in delta)) or "<empty document>"
            raise ValueError(f"no staging candidates could be extracted from the governed Delta at {source_file}; inspected top-level fields: {keys}")
        output = [self._candidate(package, row, collection_class, source_file, index) for index, (row, collection_class) in enumerate(records, 1)]
        self.diagnostics["staging_candidates_created"] = len(output)
        return tuple(output)

    def _candidate(self, package, row, collection_class, source_file, index):
        external_id = str(next((row.get(k) for k in self.IDENTIFIERS if row.get(k) not in (None, "")), f"delta-{index}"))
        object_class = self._object_class(row, collection_class)
        findings: tuple[ValidationFinding, ...] = ()
        status = "accepted"
        if not object_class:
            status = "quarantined"
            findings = (ValidationFinding("error", "missing_record_class", "Delta record does not declare record_class", f"{source_file}#L{index}"),)
        payload_value = row.get("payload") if isinstance(row.get("payload"), dict) else row.get("data")
        payload = dict(payload_value) if isinstance(payload_value, dict) else {k: v for k, v in row.items() if k not in {*self.IDENTIFIERS, "record_class", "object_class", "object_type", "type", "truth_class", "_governed_collection_path", "_governed_category"}}
        payload.setdefault("twin_type", "industry")
        if row.get("_governed_category"):
            payload.setdefault("governed_object_category", row["_governed_category"])
        actual_source = str(row.get("_governed_collection_path") or source_file)
        return CandidateImportRecord("1.0", candidate_id(package.package_ref, actual_source, external_id, object_class), package.package_ref,
            package.package_sha256, actual_source, "", {"record": index}, external_id, object_class,
            str(row.get("truth_class") or "unknown"), payload, status, findings,
            sha256_bytes(json.dumps(payload, sort_keys=True).encode()), utc_now(), package.import_run_id, 0)

    @staticmethod
    def _primary_objects(delta: dict[str, Any]) -> dict[str, Any]:
        value = delta.get("primary_objects")
        if not isinstance(value, dict) and isinstance(delta.get("delta"), dict):
            value = delta["delta"].get("primary_objects")
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _shape(value: Any) -> str:
        if isinstance(value, list):
            return "list of inline objects" if value and all(isinstance(v, dict) for v in value) else "list of identifiers"
        return "mapping" if isinstance(value, dict) else type(value).__name__

    @staticmethod
    def _declared_objects(value: Any) -> tuple[list[dict[str, Any]], list[str]]:
        if isinstance(value, list):
            return ([dict(v) for v in value if isinstance(v, dict)], [str(v) for v in value if not isinstance(v, dict)])
        if isinstance(value, dict):
            for key in ("ids", "identifiers", "references", "objects", "items"):
                if key in value:
                    return IndustryTwinDeltaAdapter._declared_objects(value[key])
            # An id -> inline object mapping is a governed collection in place.
            if value and all(isinstance(v, dict) for v in value.values()):
                return ([dict(v) if any(v.get(k) for k in IndustryTwinDeltaAdapter.IDENTIFIERS) else dict(v) | {"id": k} for k, v in value.items()], [])
        return [], []

    @staticmethod
    def _declared_paths(delta: dict[str, Any], category: str) -> tuple[str, ...]:
        paths: list[str] = []
        for container_key in ("collections", "collection_files", "object_collections", "files"):
            container = delta.get(container_key)
            if isinstance(container, dict):
                value = container.get(category)
                if isinstance(value, str): paths.append(value)
                elif isinstance(value, dict): paths.extend(str(value[k]) for k in ("path", "file", "location") if isinstance(value.get(k), str))
        declared = IndustryTwinDeltaAdapter._primary_objects(delta).get(category)
        if isinstance(declared, dict):
            paths.extend(str(declared[k]) for k in ("path", "file", "collection", "collection_path") if isinstance(declared.get(k), str))
        return tuple(dict.fromkeys(p.lstrip("./") for p in paths))

    @staticmethod
    def _collection_rows(document: Any, category: str) -> tuple[list[dict[str, Any]], str]:
        if isinstance(document, list): return [v for v in document if isinstance(v, dict)], "list"
        if isinstance(document, dict):
            for key in (category, "records", "items", "objects", "entries", "data"):
                if isinstance(document.get(key), list): return [v for v in document[key] if isinstance(v, dict)], f"mapping.{key} list"
            if document and all(isinstance(v, dict) for v in document.values()):
                return [dict(v) if any(v.get(k) for k in IndustryTwinDeltaAdapter.IDENTIFIERS) else dict(v) | {"id": k} for k, v in document.items()], "identifier mapping"
        return [], type(document).__name__

    @staticmethod
    def _records(delta: dict[str, Any]) -> list[tuple[dict[str, Any], str]]:
        output = []
        containers = [delta] + [delta[k] for k in ("delta", "changes", "operations") if isinstance(delta.get(k), dict)]
        generic = {"records", "objects", "candidates", "upserts", "creates", "updates", "additions"}
        grouped = {"twins": "twin", "industry_twins": "twin", "sources": "source", "evidence": "evidence", "observations": "observation", "entities": "entity", "relationships": "relationship", "unknowns": "unknown", "contradictions": "contradiction", "human_knowledge": "human_knowledge", "refresh_triggers": "refresh_trigger", "publication_references": "publication_reference"}
        for container in containers:
            for key, value in container.items():
                if key in generic or key in grouped:
                    output.extend((row, grouped.get(key, "")) for row in (value if isinstance(value, list) else []) if isinstance(row, dict))
        return output

    @staticmethod
    def _object_class(row: dict[str, Any], collection_class: str) -> str:
        value = str(row.get("record_class") or row.get("object_class") or row.get("object_type") or row.get("type") or collection_class).strip().casefold().replace("-", "_").replace(" ", "_")
        return {"industry_twin": "twin", "twin_record": "twin", "knowledge_source": "source", "evidence_record": "evidence", "observation_record": "observation"}.get(value, value.removesuffix("_record"))
