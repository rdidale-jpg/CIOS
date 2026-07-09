"""Import-run identity and status persistence for Blueprint package receipt."""
from __future__ import annotations

from cios.applications.flora.storage import atomic_write_json, data_path

from .ledger import utc_now
from .models import ImportRunRecord


class ImportRunRepository:
    def path_for(self, import_run_id: str):
        return data_path("blueprint_import", "runs", f"{import_run_id}.json")

    def save(self, run: ImportRunRecord) -> None:
        atomic_write_json(self.path_for(run.import_run_id), run.to_dict())

    def create_received(self, package_ref: str, package_sha256: str, actor: str) -> ImportRunRecord:
        now = utc_now()
        run_id = f"bpi-run-{package_sha256[:16]}"
        run = ImportRunRecord(
            schema_version="1.0",
            import_run_id=run_id,
            package_ref=package_ref,
            package_sha256=package_sha256,
            status="received",
            actor=actor,
            created_at=now,
            updated_at=now,
        )
        self.save(run)
        return run
