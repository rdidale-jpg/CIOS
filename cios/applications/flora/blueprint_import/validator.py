"""Blueprint package validation and candidate staging dry-run."""
from __future__ import annotations

import json
import shutil
from dataclasses import replace
import zipfile
from io import BytesIO
from pathlib import PurePosixPath
from typing import Any

from cios.applications.flora.access import BLUEPRINT_INSPECT_PERMISSION, authenticated_flora_user, can_access_enterprise, flora_roles
from cios.applications.flora.storage import data_path

from .archive import _validate_zip_member, sha256_bytes
from .candidates import (CandidateImportRecord, CandidateStagingRepository, ImportRunDryRunResult,
    PROJECTION_ONLY_CLASSES, SUPPORTED_RECORD_CLASSES, ValidationFinding, candidate_id)
from .ledger import BlueprintImportLedger, utc_now
from .manifest import DUPLICATE_MANIFEST_MESSAGE, INVALID_SCHEMA_MESSAGE, ROOT_MANIFEST, read_root_manifest
from .models import BlueprintPackageRecord, PackageReceiptError
from .registry import BlueprintPackageRegistry
from .cios_twin_adapter import CiosCommercialTwinAdapter, MAPPING_VERSION
from .atomicity import validate_atomic_statement, normalise_statement
from .industry_delta_adapter import IndustryTwinDeltaAdapter

class BlueprintValidationError(PackageReceiptError):
    pass


def _manifest_collection_paths(document: Any) -> dict[str, tuple[str, ...]]:
    """Read category-to-path declarations without imposing a producer layout."""
    if not isinstance(document, dict):
        return {}
    output: dict[str, tuple[str, ...]] = {}
    containers = [document.get(key) for key in ("collections", "collection_files", "object_collections", "primary_object_collections")]
    for container in containers:
        if not isinstance(container, dict):
            continue
        for category, declaration in container.items():
            paths: list[str] = []
            if isinstance(declaration, str):
                paths.append(declaration)
            elif isinstance(declaration, dict):
                paths.extend(str(declaration[key]) for key in ("path", "file", "location") if isinstance(declaration.get(key), str))
            elif isinstance(declaration, list):
                paths.extend(str(value) for value in declaration if isinstance(value, str))
            if paths:
                output[str(category)] = tuple(dict.fromkeys(path.lstrip("./") for path in paths))
    return output

def can_inspect_blueprint_package(headers: Any, package: BlueprintPackageRecord) -> bool:
    if not authenticated_flora_user(headers):
        return False
    if not can_access_enterprise(headers, package.identity.enterprise_id, getattr(package, "workspace_id", "")):
        return False
    # Review remains a superset for existing roles, while package.inspect gives
    # inspectors a non-canonical boundary that does not grant review/promotion.
    return bool(flora_roles(headers) & {BLUEPRINT_INSPECT_PERMISSION, "package.review", "blueprint_import_admin"})

class BlueprintPackageValidator:
    def __init__(self, registry: BlueprintPackageRegistry | None = None, staging: CandidateStagingRepository | None = None, ledger: BlueprintImportLedger | None = None):
        self.registry = registry or BlueprintPackageRegistry()
        self.staging = staging or CandidateStagingRepository()
        self.ledger = ledger or BlueprintImportLedger()
        self.twin_adapter = CiosCommercialTwinAdapter()
        self.delta_adapter = IndustryTwinDeltaAdapter()

    def validate_and_stage(self, package_ref: str, actor: str, headers: Any | None = None) -> ImportRunDryRunResult:
        package = self.registry.get(package_ref)
        if not package:
            raise BlueprintValidationError("Unknown Blueprint package reference")
        if headers is not None and not can_inspect_blueprint_package(headers, package):
            raise BlueprintValidationError("Actor is not authorised to inspect this Blueprint package")
        archive_path = data_path(package.archive_path)
        content = archive_path.read_bytes()
        if sha256_bytes(content) != package.package_sha256:
            self.ledger.append("package_validation_failed", {"package_ref": package_ref, "actor": actor, "error": "checksum mismatch"})
            raise BlueprintValidationError("Immutable archive checksum does not match registry record")
        existing = self.staging.load_summary(package.import_run_id)
        if existing and existing.get("execution_trace") and existing.get("mapping_version") == MAPPING_VERSION:
            return ImportRunDryRunResult(**{k: tuple(v) if isinstance(v, list) and k in {"files_inspected","unsupported_classes","unresolved_references","warnings","errors","execution_trace"} else v for k,v in existing.items() if k != "mapping_version"})
        candidates, warnings, errors, files, unsupported, unresolved, trace = self._inspect(package, content)
        candidates = [self._apply_constructor_validation(c) for c in candidates]
        accepted = sum(1 for c in candidates if c.validation_status == "accepted")
        quarantined = sum(1 for c in candidates if c.validation_status == "quarantined")
        rejected = sum(1 for c in candidates if c.validation_status == "rejected")
        shutil.rmtree(self.staging.root_for(package.import_run_id) / "candidates", ignore_errors=True)
        for candidate in candidates:
            self.staging.save_candidate(candidate)
        if (package.package_inspection or {}).get("contract_type") == "Governed Industry Twin Package" and candidates and not errors:
            trace.append({"timestamp": utc_now(), "step_id": 10, "component": "candidate_staging_repository",
                "action": "Staging completed", "safe_input_summary": f"{len(candidates)} candidates",
                "safe_output_summary": f"{len(candidates)} candidates persisted; validation passed",
                "status": "Passed", "failure_reason": "", "correlation_id": package.import_run_id,
                "package_checksum": package.package_sha256})
        result = ImportRunDryRunResult("1.0", package.import_run_id, package_ref, package.package_sha256, tuple(files),
            sum(1 for c in candidates if c.candidate_object_class in SUPPORTED_RECORD_CLASSES), len(candidates), accepted, quarantined, rejected,
            tuple(sorted(unsupported)), tuple(sorted(unresolved)), tuple(warnings), tuple(errors), 0, tuple(trace))
        self.staging.save_result(result)
        # Persist mapping_version alongside the dataclass result without changing older constructor callers.
        summary = self.staging.load_summary(package.import_run_id) or result.to_dict()
        summary["mapping_version"] = MAPPING_VERSION
        from cios.applications.flora.storage import atomic_write_json
        atomic_write_json(self.staging.root_for(package.import_run_id) / "summary.json", summary)
        self.ledger.append("package_validation_staged", summary | {"actor": actor})
        return result

    def _apply_constructor_validation(self, candidate: CandidateImportRecord) -> CandidateImportRecord:
        if candidate.validation_status != "accepted" or candidate.candidate_object_class != "observation":
            return candidate
        payload = candidate.payload or {}
        statement = payload.get("atomic_statement") or payload.get("statement") or payload.get("claim") or payload.get("summary")
        if not statement:
            return candidate
        finding = validate_atomic_statement(statement)
        if finding.atomic:
            return candidate
        preserved_payload = dict(payload)
        preserved_payload.setdefault("original_statement", normalise_statement(statement))
        preserved_payload["constructor_validation_failure"] = {
            "code": "quarantined_non_atomic_observation",
            "reason": finding.reason,
            "original_statement": normalise_statement(statement),
            "affected_entity": payload.get("entity_id") or payload.get("entity") or payload.get("subject") or "",
            "affected_relationship": payload.get("relationship_id") or payload.get("relationship") or "",
        }
        findings = tuple(candidate.validation_findings) + (ValidationFinding(
            "error",
            "quarantined_non_atomic_observation",
            f"quarantined_non_atomic_observation: {finding.reason}",
            f"{candidate.source_file}#{candidate.source_location.get('row') or candidate.source_location.get('line') or ''}",
        ),)
        return replace(candidate, payload=preserved_payload, validation_status="quarantined", validation_findings=findings, canonical_mutation_count=0)

    def staging_summary(self, import_run_id: str) -> dict[str, Any] | None:
        summary = self.staging.load_summary(import_run_id)
        if summary is None:
            return None
        summary["candidates"] = self.staging.list_candidates(import_run_id)
        return summary

    def _inspect(self, package: BlueprintPackageRecord, content: bytes):
        warnings: list[str] = []; errors: list[str] = []; unsupported: set[str] = set(); unresolved: set[str] = set(); files: list[str] = []
        candidates: list[CandidateImportRecord] = []
        names: list[str] = []
        trace: list[dict[str, Any]] = []
        try:
            with zipfile.ZipFile(BytesIO(content)) as zf:
                seen: set[str] = set(); duplicates: set[str] = set()
                for info in zf.infolist():
                    if info.is_dir():
                        continue
                    try: path = str(_validate_zip_member(info.filename))
                    except PackageReceiptError as exc:
                        errors.append(str(exc)); continue
                    if path in seen: duplicates.add(path)
                    seen.add(path); names.append(path); files.append(path)
                if duplicates:
                    if ROOT_MANIFEST in duplicates:
                        errors.append(DUPLICATE_MANIFEST_MESSAGE)
                    else:
                        errors.append("Duplicate package files: " + ", ".join(sorted(duplicates)))
                contract = (package.package_inspection or {}).get("contract_type", "Blueprint Package")
                if contract != "Blueprint Package":
                    inspection = package.package_inspection or {}
                    delta_items = [a for a in inspection.get("promotable_artefacts", []) if a.get("artefact_type") == "Industry Twin Delta"]
                    root = str(inspection.get("selected_package_root") or "")
                    def event(step_id, action, result, status="Passed", reason="", **extra):
                        trace.append({"timestamp": utc_now(), "step_id": step_id, "component": "industry_delta_adapter",
                            "action": action, "safe_input_summary": extra.pop("input", ""), "safe_output_summary": result,
                            "status": status, "failure_reason": reason, "correlation_id": package.import_run_id,
                            "manifest_location": inspection.get("manifest_location"), "delta_location": inspection.get("delta_location"),
                            "package_checksum": package.package_sha256, **extra})
                    event(1, "Package contract detected", contract)
                    event(2, "Package root selected", root or "archive root")
                    event(3, "Manifest parsed", str(inspection.get("manifest_location") or "Not supplied"))
                    if contract == "Governed Industry Twin Package":
                        self._validate_governed_manifest(zf, names, inspection, warnings, errors)
                    if inspection.get("blocking_errors"):
                        errors.extend(str(value) for value in inspection["blocking_errors"])
                        event(4, "Delta parsed", "Validation blocked by package inspection", "Failed", "; ".join(errors))
                        return candidates, warnings, errors, files, unsupported, unresolved, trace
                    if not delta_items:
                        errors.append("Package has no governed Industry Twin Delta and cannot be staged")
                        event(4, "Delta parsed", "No Delta", "Failed", errors[-1])
                    else:
                        delta_path = str(delta_items[0]["path"])
                        physical = next((n for n in names if n == root + delta_path or n == delta_path or n.endswith("/" + delta_path)), "")
                        def read_collection(category, declared_paths):
                            normalized = category.casefold().replace("_", "").removesuffix("s")
                            chosen = []
                            for name in names:
                                logical_name = name[len(root):] if root and name.startswith(root) else name
                                stem = PurePosixPath(logical_name).stem.casefold().replace("-", "").replace("_", "")
                                explicitly_declared = logical_name in declared_paths or name in declared_paths or name in {root + p for p in declared_paths}
                                convention_match = normalized in stem and logical_name != delta_path
                                if not (explicitly_declared or convention_match) or PurePosixPath(name).suffix.casefold() not in {".json", ".csv"}:
                                    continue
                                raw = zf.read(name)
                                if name.casefold().endswith(".csv"):
                                    import csv, io
                                    document = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
                                else:
                                    document = json.loads(raw.decode("utf-8"))
                                chosen.append((logical_name, document))
                            return tuple(chosen)
                        try:
                            self.delta_adapter.diagnostics = {}
                            delta = json.loads(zf.read(physical).decode("utf-8"))
                            if not isinstance(delta, dict): raise ValueError("Delta must be a JSON object")
                            event(4, "Delta parsed", delta_path)
                            event(5, "Metadata extracted", f"{len(inspection.get('metadata_sources', {}))} governed fields")
                            manifest_paths = _manifest_collection_paths(inspection.get("package_metadata"))
                            extracted = self.delta_adapter.candidates(
                                package, delta, delta_path, read_collection=read_collection,
                                manifest_collection_paths=manifest_paths,
                            )
                            diag = self.delta_adapter.diagnostics
                            event(6, "Object collections located", f"{len(diag.get('collection_files_selected', []))} collection files", collection_files_selected=diag.get("collection_files_selected", []), primary_object_categories=diag.get("primary_object_categories", []), primary_object_shapes=diag.get("primary_object_shapes", {}), collection_root_shapes=diag.get("collection_root_shapes", {}))
                            event(7, "References indexed", f"{sum(diag.get('objects_indexed', {}).values())} objects indexed", objects_indexed=diag.get("objects_indexed", {}), identifier_fields_used=diag.get("identifier_fields_used", {}), references_requested=diag.get("references_requested", {}))
                            resolved_total = sum(diag.get("references_resolved", {}).values())
                            requested_total = sum(diag.get("references_requested", {}).values())
                            event(8, "References resolved" if resolved_total else "Reference resolution not required",
                                  f"{resolved_total} of {requested_total} declared references resolved",
                                  references_resolved=diag.get("references_resolved", {}), unresolved_identifiers=diag.get("unresolved_identifiers", {}), resolved_counts_by_category=diag.get("resolved_counts_by_category", {}))
                            candidates.extend(extracted)
                            event(9, "Candidate conversion completed", f"{len(extracted)} candidates ready for staging")
                            self._persist_governed_resolution(package, diag, len(extracted))
                        except (KeyError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
                            errors.append(f"Industry Twin Delta is invalid: {exc}")
                            diag = self.delta_adapter.diagnostics
                            indexed = sum(diag.get("objects_indexed", {}).values())
                            resolved_count = sum(diag.get("references_resolved", {}).values())
                            event(6, "Collection lookup attempted", f"{len(diag.get('collection_files_selected', []))} collection files selected", "Failed", str(exc), collection_files_selected=diag.get("collection_files_selected", []), expected_collection_paths=diag.get("expected_collection_paths", {}), primary_object_categories=diag.get("primary_object_categories", []))
                            event(7, "Reference indexing attempted", f"{indexed} objects indexed", "Failed", str(exc), objects_indexed=diag.get("objects_indexed", {}), duplicate_identifier_counts=diag.get("duplicate_identifier_counts", {}))
                            event(8, "Reference resolution attempted", f"{resolved_count} references resolved", "Failed", str(exc), references_resolved=diag.get("references_resolved", {}), unresolved_identifiers=diag.get("unresolved_identifiers", {}))
                            event(9, "Candidate conversion", "0 candidates created", "Failed", str(exc))
                            event(10, "Staging result", "Staging not started; 0 candidates", "Failed", str(exc), input=delta_path)
                            self._persist_governed_resolution(package, diag, 0)
                    warnings.append("Research and workspace execution artefacts are retained as package lineage and excluded from staging")
                    return candidates, warnings, errors, files, unsupported, unresolved, trace
                try:
                    manifest = read_root_manifest(zf)
                except PackageReceiptError as exc:
                    errors.append(str(exc))
                    manifest = {}
                self._validate_manifest(package, manifest, seen, warnings, errors)
                inspection = self.twin_adapter.inspect(package, zf, manifest, trace) if isinstance(manifest, dict) else None
                if inspection:
                    files.append(inspection.workbook_path)
                    warnings.extend([f"Worksheets discovered: {', '.join(inspection.worksheets)}"] if inspection.worksheets else [])
                    warnings.extend(inspection.warnings)
                    errors.extend(inspection.errors)
                    candidates.extend(inspection.candidates)
                record_sets = manifest.get("record_sets") if isinstance(manifest, dict) else []
                if isinstance(record_sets, list):
                    for record_set in record_sets:
                        path = str(record_set.get("path") or "") if isinstance(record_set, dict) else ""
                        if not path or path not in seen or not path.endswith(".ndjson"): continue
                        candidates.extend(self._records(package, zf, path, unsupported, unresolved))
        except (zipfile.BadZipFile, json.JSONDecodeError, UnicodeDecodeError) as exc:
            errors.append(str(exc))
        if errors:
            # create a rejected package-metadata record so failed runs remain inspectable
            candidates.append(self._candidate(package, "blueprint_manifest.json", "package", "package_metadata", "package_metadata", {}, "rejected", [ValidationFinding("error", "package_invalid", "; ".join(errors))]))
        return candidates, warnings, errors, files, unsupported, unresolved, trace

    @staticmethod
    def _validate_governed_manifest(zf, names, inspection, warnings, errors) -> None:
        """Validate the producer's declared inventory at the selected logical root."""
        root = str(inspection.get("selected_package_root") or "")
        manifest_path = str(inspection.get("manifest_location") or "")
        physical_manifest = root + manifest_path if root + manifest_path in names else manifest_path
        try:
            manifest = json.loads(zf.read(physical_manifest).decode("utf-8"))
        except (KeyError, UnicodeDecodeError, json.JSONDecodeError):
            errors.append("Governed package manifest cannot be read for file validation")
            return
        declarations = manifest.get("files") if isinstance(manifest, dict) else None
        if declarations is None:
            warnings.append("Governed package manifest does not declare files; archive inventory remains retained")
            return
        if not isinstance(declarations, list) or not declarations:
            errors.append("Governed package manifest has an invalid empty file declaration")
            return
        declared: set[str] = set()
        for item in declarations:
            if not isinstance(item, dict):
                errors.append("Governed package manifest contains an invalid file declaration")
                continue
            logical = str(item.get("filename") or item.get("path") or "").lstrip("./")
            physical = root + logical
            declared.add(logical)
            if not logical or physical not in names:
                errors.append(f"Missing declared governed file: {logical or '<empty path>'}")
                continue
            content = zf.read(physical)
            if item.get("bytes") is not None and int(item["bytes"]) != len(content):
                errors.append(f"Declared byte count does not match for {logical}")
            checksum = str(item.get("sha256") or "")
            if not checksum:
                errors.append(f"Missing declared checksum for {logical}")
            elif checksum.casefold() != sha256_bytes(content):
                errors.append(f"Declared checksum does not match for {logical}")
        actual = {name[len(root):] for name in names if name.startswith(root)} - {manifest_path}
        undeclared = sorted(actual - declared)
        if undeclared:
            warnings.append("Retained undeclared governed files: " + ", ".join(undeclared))

    def _persist_governed_resolution(self, package, diagnostics: dict[str, Any], candidate_count: int) -> None:
        labels = {
            "enterprise_twins": "Enterprise Twins", "market_participant_twins": "Market Participant Twins",
            "opportunity_twins": "Opportunity Twins", "flow_twins": "Flow Twins",
            "industry_twins": "Industry Twins",
        }
        inspection = package.package_inspection or {}
        counts = dict(inspection.get("asset_counts") or {})
        for category, count in diagnostics.get("references_resolved", {}).items():
            if category in labels:
                counts[labels[category]] = int(count)
        declared = sum(diagnostics.get("references_requested", {}).values())
        resolved = sum(diagnostics.get("references_resolved", {}).values())
        counts.update({"Declared objects": declared, "Resolved objects": resolved,
                       "Promotable candidates": candidate_count,
                       "Unresolved references": max(0, declared - resolved),
                       "Lineage-only assets": len(inspection.get("excluded_research_only_objects") or [])})
        self.registry.update_inspection(package.package_ref, {
            "asset_counts": counts,
            "governed_resolution": diagnostics,
            "resolved_candidate_count": candidate_count,
            "unresolved_references": [identifier for values in diagnostics.get("unresolved_identifiers", {}).values() for identifier in values],
        })

    def _validate_manifest(self, package, manifest, seen, warnings, errors):
        if not isinstance(manifest, dict): errors.append(INVALID_SCHEMA_MESSAGE); return
        checks = {"package_id": package.identity.package_id, "enterprise_id": package.identity.enterprise_id, "profile_version": package.identity.profile_version}
        checks["package_version"] = package.identity.package_version
        for key, expected in checks.items():
            if str(manifest.get(key) or "") != expected: errors.append(f"Manifest {key} does not match registry identity")
        declared = {str(f.get("path") or "") for f in manifest.get("files", []) if isinstance(f, dict)}
        for f in manifest.get("files", []):
            if not isinstance(f, dict): continue
            path = str(f.get("path") or "")
            if f.get("required") and path not in seen: errors.append(f"Missing required file: {path}")
        unexpected = set(seen) - declared - {"blueprint_manifest.json"}
        if declared and unexpected: warnings.append("Unexpected package files: " + ", ".join(sorted(unexpected)))

    def _records(self, package, zf, path, unsupported, unresolved):
        out=[]
        for index, line in enumerate(zf.read(path).decode("utf-8").splitlines(), start=1):
            if not line.strip(): continue
            findings=[]; status="accepted"
            try: row=json.loads(line)
            except json.JSONDecodeError:
                row={}; status="rejected"; findings.append(ValidationFinding("error","invalid_json","Record line is not valid JSON",f"{path}#L{index}"))
            rc=str(row.get("record_class") or ""); ext=str(row.get("external_id") or "")
            if not ext: status="quarantined"; findings.append(ValidationFinding("error","missing_external_id","Record does not declare external_id",f"{path}#L{index}"))
            if rc not in SUPPORTED_RECORD_CLASSES:
                status="quarantined"; unsupported.add(rc or "<missing>"); findings.append(ValidationFinding("warning","unsupported_record_class",f"Unsupported record class: {rc}",f"{path}#L{index}"))
            elif rc in PROJECTION_ONLY_CLASSES:
                status="quarantined"; findings.append(ValidationFinding("warning","projection_only","Projection-only class retained outside canonical intelligence",f"{path}#L{index}"))
            for ref in row.get("references", []) if isinstance(row.get("references", []), list) else []:
                if str(ref).startswith("missing:"):
                    status="quarantined"; unresolved.add(str(ref)); findings.append(ValidationFinding("error","unresolved_reference",str(ref),f"{path}#L{index}"))
            out.append(self._candidate(package,path,ext or f"line-{index}",rc,row.get("truth_class","unknown"),row.get("payload",{}) if isinstance(row.get("payload",{}),dict) else {},status,findings,row.get("source_location",{"line":index})))
        return out

    def _candidate(self, package, path, ext, rc, truth, payload, status, findings, loc=None):
        loc = loc if isinstance(loc, dict) else {}
        return CandidateImportRecord("1.0", candidate_id(package.package_ref,path,ext,rc), package.package_ref, package.package_sha256, path, str(loc.get("sheet") or ""), loc, ext, rc, truth, payload, status, tuple(findings), sha256_bytes(json.dumps(payload, sort_keys=True).encode()), utc_now(), package.import_run_id, 0)
