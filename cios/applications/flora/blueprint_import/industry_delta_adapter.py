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
    IDENTIFIERS = (
        "external_id", "stable_id", "object_id", "twin_id", "enterprise_twin_id",
        "market_participant_twin_id", "opportunity_twin_id", "flow_twin_id", "id",
    )
    DEFAULT_COLLECTION_PATHS = {
        "enterprise_twins": ("collections/enterprise-twins.json", "twins/enterprise-twins.json"),
        "market_participant_twins": ("collections/market-participant-twins.json", "twins/market-participant-twins.json"),
        "opportunity_twins": ("collections/opportunity-twins.json", "twins/opportunity-twins.json"),
        "flow_twins": ("collections/flow-twins.json", "collections/flow-twins.csv", "twins/flow-twins.json"),
    }
    TMS_INVENTORIES = {
        "objects": ("HFT_Upgrade/Inventories/object_inventory.json", "objects", "entity"),
        "facts": ("HFT_Upgrade/Inventories/fact_inventory.json", "facts", "fact"),
        "evidence": ("HFT_Upgrade/Evidence/source_evidence_register.json", "sources", "evidence"),
        "relationships": ("HFT_Upgrade/Inventories/relationship_graph.json", "relationships", "relationship"),
        "unknowns": ("HFT_Upgrade/Inventories/uncertainty_inventory.json", "unknowns", "unknown"),
        "contradictions": ("HFT_Upgrade/Inventories/uncertainty_inventory.json", "contradictions", "contradiction"),
        "reasoning_lineage": ("HFT_Upgrade/Lineage/reasoning_lineage.json", "", "reasoning_lineage"),
    }

    def __init__(self) -> None:
        self.diagnostics: dict[str, Any] = {}

    def candidates(self, package: BlueprintPackageRecord, delta: dict[str, Any], source_file: str,
                   read_collection: CollectionReader | None = None,
                   manifest_collection_paths: dict[str, tuple[str, ...]] | None = None) -> tuple[CandidateImportRecord, ...]:
        records = self._records(delta)
        primary = self._primary_objects(delta)
        diag: dict[str, Any] = {
            "primary_object_categories": sorted(primary), "primary_object_shapes": {},
            "collection_files_selected": [], "collection_root_shapes": {},
            "identifier_fields_used": {}, "objects_indexed": {}, "references_requested": {},
            "references_resolved": {}, "unresolved_identifiers": {}, "resolved_counts_by_category": {},
            "declared_identifiers": {}, "expected_collection_paths": {}, "actual_collection_paths": {},
            "duplicate_identifier_counts": {}, "unresolved_counts": {},
        }
        # Publish diagnostics before I/O so a failure can never inherit the
        # previous validation run's successful diagnostics.
        self.diagnostics = diag
        if self._is_tms_inventory_delta(delta):
            if read_collection is None:
                raise ValueError("TMS inventory projection requires the governed collection reader")
            records.extend(self._tms_inventory_records(read_collection, diag))
        for category, declared in primary.items():
            shape = self._shape(declared)
            diag["primary_object_shapes"][category] = shape
            inline, references = self._declared_objects(declared)
            if inline:
                records.extend((row, self.PROMOTABLE.get(category, category.removesuffix("s"))) for row in inline)
            diag["references_requested"][category] = len(references)
            diag["declared_identifiers"][category] = list(references)
            diag["unresolved_counts"][category] = len(references)
            diag["duplicate_identifier_counts"][category] = 0
            if not references:
                diag["references_resolved"][category] = 0
                continue
            if read_collection is None:
                raise ValueError(f"primary_objects category {category} contains references but no governed collection reader was supplied")
            paths = self._declared_paths(delta, category)
            if manifest_collection_paths and manifest_collection_paths.get(category):
                paths = manifest_collection_paths[category]
            if not paths:
                paths = self.DEFAULT_COLLECTION_PATHS.get(category, ())
            diag["expected_collection_paths"][category] = list(paths)
            selected = read_collection(category, paths)
            if not selected:
                shown = ", ".join(paths) or "<no contract-defined path>"
                raise ValueError(f"missing governed collection for primary_objects category {category}; attempted path(s): {shown}")
            index: dict[str, tuple[dict[str, Any], str, str]] = {}
            for path, document in selected:
                diag["collection_files_selected"].append(path)
                diag["actual_collection_paths"].setdefault(category, []).append(path)
                rows, root_shape = self._collection_rows(document, category)
                diag["collection_root_shapes"][path] = root_shape
                for row_number, row in enumerate(rows, 1):
                    identifier_field = next((field for field in self.IDENTIFIERS if row.get(field) not in (None, "")), None)
                    if identifier_field is None:
                        raise ValueError(f"governed object {category}[{row_number}] in {path} has no stable identifier; missing required field ({', '.join(self.IDENTIFIERS)})")
                    identifier = str(row[identifier_field])
                    if identifier in index:
                        diag["duplicate_identifier_counts"][category] += 1
                        first_path = index[identifier][1]
                        raise ValueError(f"duplicate governed identifier {identifier!r} in {category}: {first_path} and {path}")
                    index[identifier] = (row, path, identifier_field)
                    diag["identifier_fields_used"].setdefault(category, identifier_field)
            diag["objects_indexed"][category] = len(index)
            missing = [identifier for identifier in references if identifier not in index]
            diag["unresolved_identifiers"][category] = missing
            diag["references_resolved"][category] = len(references) - len(missing)
            diag["unresolved_counts"][category] = len(missing)
            if missing:
                raise ValueError(f"unresolved governed identifiers in {category}: {', '.join(missing)}")
            for identifier in references:
                row, path, _ = index[identifier]
                records.append((dict(row) | {"_governed_collection_path": path, "_governed_category": category}, self.PROMOTABLE.get(category, category.removesuffix("s"))))
            diag["resolved_counts_by_category"][category] = len(references)
        if not records:
            keys = ", ".join(sorted(str(key) for key in delta)) or "<empty document>"
            raise ValueError(f"no staging candidates could be extracted from the governed Delta at {source_file}; inspected top-level fields: {keys}")
        output = [self._candidate(package, row, collection_class, source_file, index) for index, (row, collection_class) in enumerate(records, 1)]
        self.diagnostics["staging_candidates_created"] = len(output)
        return tuple(output)

    @staticmethod
    def _is_tms_inventory_delta(delta: dict[str, Any]) -> bool:
        return str(delta.get("mission_id") or "") == "TMS-001" and any(
            isinstance(delta.get(key), list) for key in ("new_twins", "new_relationships", "new_unknowns")
        )

    def _tms_inventory_records(self, read_collection: CollectionReader, diag: dict[str, Any]) -> list[tuple[dict[str, Any], str]]:
        """Project canonical inventories; never infer candidates from executive/workspace products."""
        output: list[tuple[dict[str, Any], str]] = []
        object_ids: set[str] = set()
        relationships: list[dict[str, Any]] = []
        for category, (path, key, record_class) in self.TMS_INVENTORIES.items():
            selected = read_collection(category, (path,))
            if not selected:
                raise ValueError(f"missing declared TMS canonical inventory: {path}")
            actual_path, document = next(((p, d) for p, d in selected if p == path), selected[0])
            diag["collection_files_selected"].append(actual_path)
            if key:
                rows = document.get(key) if isinstance(document, dict) else None
                if not isinstance(rows, list):
                    raise ValueError(f"TMS canonical inventory {path} does not contain list {key!r}")
            else:
                rows = [document] if isinstance(document, dict) else []
            if category == "objects":
                object_ids = {str(row.get("id")) for row in rows if isinstance(row, dict) and row.get("id")}
            if category == "relationships":
                relationships = [row for row in rows if isinstance(row, dict)]
            diag["objects_indexed"][category] = len(rows)
            diag["references_requested"][category] = len(rows)
            diag["references_resolved"][category] = len(rows)
            diag["resolved_counts_by_category"][category] = len(rows)
            for row in rows:
                if isinstance(row, dict):
                    output.append((dict(row) | {"_governed_collection_path": actual_path, "_governed_category": category}, record_class))
        missing = sorted({str(endpoint) for row in relationships for endpoint in
                          (row.get("source_object_id"), row.get("target_object_id"))
                          if endpoint and str(endpoint) not in object_ids})
        diag["relationship_endpoint_count"] = len(relationships) * 2
        diag["relationship_endpoints_resolved"] = len(relationships) * 2 - len(missing)
        diag["unresolved_relationship_endpoints"] = missing
        if missing:
            raise ValueError("unresolved TMS relationship endpoints: " + ", ".join(missing))
        return output

    def _candidate(self, package, row, collection_class, source_file, index):
        external_id = str(next((row.get(k) for k in self.IDENTIFIERS if row.get(k) not in (None, "")), f"delta-{index}"))
        object_class = collection_class if row.get("_governed_category") == "objects" else self._object_class(row, collection_class)
        findings: tuple[ValidationFinding, ...] = ()
        status = "accepted"
        if not object_class:
            status = "quarantined"
            findings = (ValidationFinding("error", "missing_record_class", "Delta record does not declare record_class", f"{source_file}#L{index}"),)
        payload_value = row.get("payload") if isinstance(row.get("payload"), dict) else row.get("data")
        payload = dict(payload_value) if isinstance(payload_value, dict) else {k: v for k, v in row.items() if k not in {*self.IDENTIFIERS, "record_class", "object_class", "type", "truth_class", "_governed_collection_path", "_governed_category"}}
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
            inline: list[dict[str, Any]] = []
            references: list[str] = []
            for item in value:
                if not isinstance(item, dict):
                    references.append(str(item))
                    continue
                reference = next((item.get(key) for key in ("reference", "ref", "identifier") if item.get(key) not in (None, "")), None)
                if reference is None and len(item) == 1:
                    reference = next((item.get(key) for key in IndustryTwinDeltaAdapter.IDENTIFIERS if item.get(key) not in (None, "")), None)
                if reference is not None:
                    references.append(str(reference))
                else:
                    inline.append(dict(item))
            return inline, references
        if isinstance(value, dict):
            for key in ("ids", "identifiers", "references", "objects", "items"):
                if key in value:
                    return IndustryTwinDeltaAdapter._declared_objects(value[key])
            for key, nested in value.items():
                if str(key).casefold().endswith(("_ids", "_identifiers", "_references")):
                    return IndustryTwinDeltaAdapter._declared_objects(nested)
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
                value = document.get(key)
                if isinstance(value, list): return [v for v in value if isinstance(v, dict)], f"mapping.{key} list"
                if isinstance(value, dict) and value and all(isinstance(v, dict) for v in value.values()):
                    return [dict(v) if any(v.get(k) for k in IndustryTwinDeltaAdapter.IDENTIFIERS) else dict(v) | {"id": k} for k, v in value.items()], f"mapping.{key} identifier mapping"
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
