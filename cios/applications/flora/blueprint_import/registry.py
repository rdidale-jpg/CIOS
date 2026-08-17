"""Blueprint package registry and receipt orchestration."""
from __future__ import annotations

import json
from uuid import uuid4

from cios.applications.flora.storage import (PersistenceError, atomic_write_json,
                                             data_path, ensure_writable_dir,
                                             root_exception,
                                             safe_exception_summary,
                                             storage_mode)

from .archive import inspect_zip_inventory, preserve_original_package, sha256_bytes
from .ledger import BlueprintImportLedger, utc_now
from .manifest import read_identity
from .package_contracts import PackageContractDetector
from .models import (BlueprintPackageIdentity, BlueprintPackageRecord,
                     PackageImportOperationalDiagnostic, PackageReceiptError)
from .package_contracts import PackageContract
from .runs import ImportRunRepository


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

    def storage_health(self) -> dict[str, str]:
        """Exercise the receipt-record path with a disposable, non-canonical probe."""
        result = {
            "storage_connection": "FAIL",
            "schema_reachable": "FAIL",
            "minimal_persistence": "FAIL",
            "schema_alignment": "UNKNOWN",
        }
        probe = None
        try:
            # Health reporting runs while handling a persistence exception.  Path
            # resolution is itself storage work and therefore belongs inside this
            # best-effort boundary; it must not replace the exception being
            # diagnosed.
            root = data_path("blueprint_import", "packages")
            probe = root / f".blueprint-package-health-{uuid4().hex}.json"
            ensure_writable_dir(root)
            result["storage_connection"] = "PASS"
            # This deliberately uses the same JSON adapter and receipt-record
            # directory, but never a registry filename or canonical memory.
            atomic_write_json(probe, {"record_type": "BlueprintPackageRecord", "health_probe": True})
            result["schema_reachable"] = "PASS"
            if json.loads(probe.read_text(encoding="utf-8")).get("record_type") == "BlueprintPackageRecord":
                result["minimal_persistence"] = "PASS"
                result["schema_alignment"] = "PASS"
        except Exception:
            pass
        finally:
            if probe is not None:
                try:
                    probe.unlink(missing_ok=True)
                except OSError:
                    pass
        return result

    @staticmethod
    def persistence_diagnostic(exc: PersistenceError, health: dict[str, str]) -> PackageImportOperationalDiagnostic:
        root = root_exception(exc)
        name = f"{type(root).__module__}.{type(root).__qualname__}"
        lowered = type(root).__name__.lower()
        connection = "YES" if ("operational" in lowered or isinstance(root, (ConnectionError, TimeoutError))) else "NO"
        serialization = "YES" if ("serial" in lowered or isinstance(root, (TypeError, ValueError))) else "NO"
        schema = "YES" if "programming" in lowered else ("NO" if "integrity" in lowered else "UNKNOWN")
        constraint = "integrity constraint (details in server log)" if "integrity" in lowered else "not safely available"
        return PackageImportOperationalDiagnostic(
            underlying_exception_class=name,
            underlying_safe_message=safe_exception_summary(root),
            persistence_operation="create",
            record_model="BlueprintPackageRecord",
            storage_backend=f"{storage_mode().get('mode') or 'UNKNOWN'} (filesystem JSON)",
            constraint_location=constraint,
            transaction_state="no database transaction; receipt not committed",
            schema_mismatch_detected=schema,
            connection_failure_detected=connection,
            serialization_failure_detected=serialization,
            storage_connection=health.get("storage_connection") or "UNKNOWN",
            schema_reachable=health.get("schema_reachable") or "UNKNOWN",
            minimal_persistence=health.get("minimal_persistence") or "UNKNOWN",
            schema_alignment=health.get("schema_alignment") or "UNKNOWN",
        )

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
            package_path = self._path_for_ref(package_ref)
            try:
                ensure_writable_dir(package_path.parent)
                atomic_write_json(package_path, record.to_dict())
            except Exception as exc:
                underlying = root_exception(exc)
                raise PersistenceError(
                    "Blueprint package receipt persistence failed; "
                    "operation=create; model=BlueprintPackageRecord; "
                    "field_or_constraint=package registry JSON record"
                ) from underlying
            self.ledger.append("package_received", {"package_ref": package_ref, "package_sha256": package_sha256, "import_run_id": run.import_run_id, "actor": actor})
            return record
        except Exception as exc:
            # Failed receipts intentionally leave no registry/run acceptance record.
            try:
                self.ledger.append("package_receipt_failed", {"package_ref": package_ref, "package_sha256": package_sha256, "actor": actor, "error": str(exc)})
            except Exception:
                # A best-effort diagnostic must never replace the persistence
                # exception (and its cause) that actually failed receipt.
                pass
            if isinstance(exc, PackageReceiptError):
                raise
            raise


def receive_blueprint_package(content: bytes, original_filename: str, actor: str, workspace_id: str = "") -> BlueprintPackageRecord:
    return BlueprintPackageRegistry().receive(content, original_filename, actor, workspace_id)
