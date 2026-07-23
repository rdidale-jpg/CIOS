"""Blueprint package registry and receipt orchestration."""
from __future__ import annotations

import json

from cios.applications.flora.storage import atomic_write_json, data_path, ensure_writable_dir

from .archive import inspect_zip_inventory, preserve_original_package, sha256_bytes
from .ledger import BlueprintImportLedger, utc_now
from .manifest import read_identity
from .models import BlueprintPackageRecord, PackageReceiptError
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
            identity = read_identity(content)
            inventory = inspect_zip_inventory(content)
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
            )
            ensure_writable_dir(data_path("blueprint_import", "packages"))
            atomic_write_json(self._path_for_ref(package_ref), record.to_dict())
            self.ledger.append("package_received", {"package_ref": package_ref, "package_sha256": package_sha256, "import_run_id": run.import_run_id, "actor": actor})
            return record
        except Exception as exc:
            # Failed receipts intentionally leave no registry/run acceptance record.
            self.ledger.append("package_receipt_failed", {"package_ref": package_ref, "package_sha256": package_sha256, "actor": actor, "error": str(exc)})
            if isinstance(exc, PackageReceiptError):
                raise
            raise


def receive_blueprint_package(content: bytes, original_filename: str, actor: str, workspace_id: str = "") -> BlueprintPackageRecord:
    return BlueprintPackageRegistry().receive(content, original_filename, actor, workspace_id)
