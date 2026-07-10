"""Blueprint package validation and candidate staging dry-run."""
from __future__ import annotations

import json
import zipfile
from io import BytesIO
from pathlib import PurePosixPath
from typing import Any

from cios.applications.flora.access import authenticated_flora_user, can_access_enterprise, flora_roles
from cios.applications.flora.storage import data_path

from .archive import _validate_zip_member, sha256_bytes
from .candidates import (CandidateImportRecord, CandidateStagingRepository, ImportRunDryRunResult,
    PROJECTION_ONLY_CLASSES, SUPPORTED_RECORD_CLASSES, ValidationFinding, candidate_id)
from .ledger import BlueprintImportLedger, utc_now
from .manifest import DUPLICATE_MANIFEST_MESSAGE, INVALID_SCHEMA_MESSAGE, ROOT_MANIFEST, read_root_manifest
from .models import BlueprintPackageRecord, PackageReceiptError
from .registry import BlueprintPackageRegistry
from .cios_twin_adapter import CiosCommercialTwinAdapter, MAPPING_VERSION

class BlueprintValidationError(PackageReceiptError):
    pass

def can_inspect_blueprint_package(headers: Any, package: BlueprintPackageRecord) -> bool:
    if not authenticated_flora_user(headers):
        return False
    if not can_access_enterprise(headers, package.identity.enterprise_id, getattr(package, "workspace_id", "")):
        return False
    return bool(flora_roles(headers) & {"package.review", "blueprint_import_admin"})

class BlueprintPackageValidator:
    def __init__(self, registry: BlueprintPackageRegistry | None = None, staging: CandidateStagingRepository | None = None, ledger: BlueprintImportLedger | None = None):
        self.registry = registry or BlueprintPackageRegistry()
        self.staging = staging or CandidateStagingRepository()
        self.ledger = ledger or BlueprintImportLedger()
        self.twin_adapter = CiosCommercialTwinAdapter()

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
        accepted = sum(1 for c in candidates if c.validation_status == "accepted")
        quarantined = sum(1 for c in candidates if c.validation_status == "quarantined")
        rejected = sum(1 for c in candidates if c.validation_status == "rejected")
        for candidate in candidates:
            self.staging.save_candidate(candidate)
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
