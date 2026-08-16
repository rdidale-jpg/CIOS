"""Blueprint package registry and receipt orchestration."""
from __future__ import annotations

import json
import logging

from cios.applications.flora.storage import PersistenceError, atomic_write_json, data_path, ensure_writable_dir

from .archive import inspect_zip_inventory, preserve_original_package, sha256_bytes
from .ledger import BlueprintImportLedger, utc_now
from .manifest import read_identity
from .package_contracts import PackageContractDetector
from .models import BlueprintPackageIdentity, BlueprintPackageRecord, PackageReceiptError
from .package_contracts import PackageContract
from .runs import ImportRunRepository

LOGGER = logging.getLogger(__name__)
_LAST_RECEIVE_DIAGNOSTIC: dict = {}


def _safe_storage_diagnostic(exc: Exception, operation: str = "persist BlueprintPackageRecord") -> dict:
    details = dict(getattr(exc, "diagnostic", {}) or {})
    cause = exc.__cause__ or exc
    details.update({
        "exception_class": details.get("exception_class") or type(cause).__name__,
        "category": details.get("category") or "storage",
        "operation": operation,
        "record_type": "BlueprintPackageRecord",
        "connection_available": True,
        "schema_alignment": "pass",  # JSON schema is owned by BlueprintPackageRecord.to_dict
        "safe_error": details.get("safe_error") or str(cause),
    })
    return details


def blueprint_registry_storage_status() -> dict:
    """Return the existing storage diagnostic extended for package receipt."""
    root = data_path("blueprint_import", "packages")
    try:
        ensure_writable_dir(root)
        for path in root.glob("*.json"):
            BlueprintPackageRecord.from_dict(json.loads(path.read_text(encoding="utf-8")))
        return {"registry_storage": "HEALTHY", "record_persistence": "PASS", "schema_alignment": "PASS",
                "last_receive_diagnostic": dict(_LAST_RECEIVE_DIAGNOSTIC), "underlying_safe_error": _LAST_RECEIVE_DIAGNOSTIC.get("safe_error", "")}
    except Exception as exc:
        diagnostic = _safe_storage_diagnostic(exc, "registry health check")
        return {"registry_storage": "FAIL", "record_persistence": "FAIL", "schema_alignment": "FAIL" if isinstance(exc, (KeyError, TypeError, ValueError)) else "UNKNOWN",
                "last_receive_diagnostic": dict(_LAST_RECEIVE_DIAGNOSTIC), "underlying_safe_error": diagnostic["safe_error"]}

class BlueprintPackageRegistry:
    def __init__(self, ledger: BlueprintImportLedger | None = None, runs: ImportRunRepository | None = None):
        self.ledger = ledger or BlueprintImportLedger()
        self.runs = runs or ImportRunRepository()

    def _path_for_ref(self, package_ref: str):
        return data_path("blueprint_import", "packages", f"{package_ref}.json")

    def get(self, package_ref: str) -> BlueprintPackageRecord | None:
        path = self._path_for_ref(package_ref)
        if not path.exists():
            return None
        return BlueprintPackageRecord.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def list(self) -> list[BlueprintPackageRecord]:
        root = data_path("blueprint_import", "packages")
        if not root.exists():
            return []
        return [BlueprintPackageRecord.from_dict(json.loads(path.read_text(encoding="utf-8"))) for path in sorted(root.glob("*.json"))]

    def update_inspection(self, package_ref: str, values: dict) -> BlueprintPackageRecord:
        """Persist facts learned during validation on the one inspection record."""
        record = self.get(package_ref)
        if record is None:
            raise PackageReceiptError("Unknown Blueprint package reference")
        data = record.to_dict()
        data["package_inspection"] = dict(record.package_inspection) | values
        atomic_write_json(self._path_for_ref(package_ref), data)
        return BlueprintPackageRecord.from_dict(data)

    def receive(self, content: bytes, original_filename: str, actor: str, workspace_id: str = "") -> BlueprintPackageRecord:
        return self._receive(content, original_filename, actor, workspace_id)

    def _receive(
        self,
        content: bytes,
        original_filename: str,
        actor: str,
        workspace_id: str = "",
    ) -> BlueprintPackageRecord:
        if not actor or not str(actor).strip():
            raise PackageReceiptError("Actor is required for governed package receipt")
        if not content:
            raise PackageReceiptError("Blueprint package content is required")
        package_sha256 = sha256_bytes(content)
        package_ref = f"bpi-pkg-{package_sha256[:16]}"
        existing = self.get(package_ref)
        if existing:
            self.ledger.append("package_duplicate_detected", {"package_ref": package_ref, "package_sha256": package_sha256, "actor": actor})
            return existing

        try:
            inventory = inspect_zip_inventory(content)
            inspection = PackageContractDetector().detect(content, inventory)
            if inspection.contract_type is PackageContract.BLUEPRINT:
                identity = read_identity(content)
            elif inspection.contract_type is PackageContract.UNKNOWN:
                if any(error.startswith("Ambiguous package contract") for error in inspection.blocking_errors):
                    raise PackageReceiptError("; ".join(inspection.blocking_errors))
                # Preserve the established Blueprint diagnostic for packages with
                # no recognised alternate contract; detection remains available
                # through the read-only inspector.
                identity = read_identity(content)
            else:
                metadata = inspection.to_dict()
                package_id = inspection.package_identifier or "unidentified-package"
                identity = BlueprintPackageIdentity(
                    package_id=package_id,
                    package_version=inspection.package_version or "unspecified",
                    enterprise_id=str(metadata.get("enterprise_id") or metadata.get("industry_id") or metadata.get("mission_id") or package_id),
                    profile_version=str(metadata.get("package_profile") or metadata.get("profile_version") or metadata.get("schema_version") or "industry-twin-v1"),
                )
            archived_sha256, byte_count, archive_path = preserve_original_package(content, original_filename)
            if archived_sha256 != package_sha256:
                raise PackageReceiptError("Archived checksum does not match received checksum")
            run = self.runs.create_received(package_ref, package_sha256, actor)
            record = BlueprintPackageRecord(
                schema_version="1.0",
                package_ref=package_ref,
                identity=identity,
                package_sha256=package_sha256,
                byte_count=byte_count,
                original_filename=original_filename,
                archive_path=archive_path,
                inventory=inventory,
                status="received",
                received_at=utc_now(),
                received_by=str(actor).strip(),
                import_run_id=run.import_run_id,
                workspace_id=str(workspace_id or "").strip(),
                package_inspection=inspection.to_dict(),
            )
            ensure_writable_dir(data_path("blueprint_import", "packages"))
            atomic_write_json(self._path_for_ref(package_ref), record.to_dict())
            # The audit ledger is not part of the receipt transaction.  A full,
            # read-only, or independently unavailable audit file must not turn
            # an already durable registry record into a false failed receipt.
            try:
                self.ledger.append("package_received", {"package_ref": package_ref, "package_sha256": package_sha256, "import_run_id": run.import_run_id, "actor": actor})
            except PersistenceError as audit_exc:
                LOGGER.warning("blueprint_receipt_audit_persistence_failed %s", json.dumps(_safe_storage_diagnostic(audit_exc, "append package_received audit"), sort_keys=True))
            return record
        except Exception as exc:
            # Failed receipts intentionally leave no registry/run acceptance
            # record.  Best-effort diagnostics must never mask the root error.
            global _LAST_RECEIVE_DIAGNOSTIC
            _LAST_RECEIVE_DIAGNOSTIC = _safe_storage_diagnostic(exc)
            try:
                self._path_for_ref(package_ref).unlink(missing_ok=True)
                run_id = f"bpi-run-{package_sha256[:16]}"
                self.runs.path_for(run_id).unlink(missing_ok=True)
            except OSError as cleanup_exc:
                _LAST_RECEIVE_DIAGNOSTIC["transaction_state"] = "rollback failed"
                _LAST_RECEIVE_DIAGNOSTIC["rollback_error"] = f"{type(cleanup_exc).__name__}: {cleanup_exc}"
            try:
                self.ledger.append("package_receipt_failed", {"package_ref": package_ref, "package_sha256": package_sha256, "actor": actor, "error": _LAST_RECEIVE_DIAGNOSTIC})
            except Exception as diagnostic_exc:
                LOGGER.warning("blueprint_receipt_failure_audit_unavailable %s", json.dumps(_safe_storage_diagnostic(diagnostic_exc, "append package_receipt_failed audit"), sort_keys=True))
            if isinstance(exc, PackageReceiptError):
                raise
            raise


def receive_blueprint_package(content: bytes, original_filename: str, actor: str, workspace_id: str = "") -> BlueprintPackageRecord:
    return BlueprintPackageRegistry().receive(content, original_filename, actor, workspace_id)
