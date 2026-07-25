"""Durable lifecycle termination for the existing governed importer."""
from __future__ import annotations
import json
from dataclasses import dataclass
from cios.applications.flora.storage import atomic_write_json, data_path
from .ledger import BlueprintImportLedger, utc_now

@dataclass(frozen=True)
class ImportLifecycle:
    import_run_id: str
    state: str = "received"
    updated_at: str = ""
    actor: str = ""
    stage: str = "inspect"
    reason: str = ""
    canonical_writes: int = 0
    def to_dict(self): return self.__dict__.copy()

class ImportLifecycleService:
    """Owns cancellation state; archive retention remains with archive storage."""
    def path(self, run_id): return data_path("blueprint_import", "lifecycle", f"{run_id}.json")
    def get(self, run_id):
        p=self.path(run_id)
        return ImportLifecycle(**json.loads(p.read_text())) if p.exists() else ImportLifecycle(run_id)
    def assert_active(self, run_id):
        if self.get(run_id).state == "cancelled": raise ValueError("Cancelled imports are terminal and cannot be reviewed or promoted.")
    def cancel(self, run_id, actor, stage, reason=""):
        old=self.get(run_id)
        if old.state == "promoted": raise ValueError("A promoted import cannot be cancelled. Use governed correction or supersession.")
        if old.state == "cancelled": return old
        row=ImportLifecycle(run_id,"cancelled",utc_now(),actor,stage,reason.strip(),0)
        atomic_write_json(self.path(run_id),row.to_dict())
        BlueprintImportLedger().append("import_cancelled",{**row.to_dict(),"staged_candidates_invalidated":True,"archive_disposition":"retained under existing archive policy","canonical_writes_occurred":False})
        return row
    def mark_promoted(self,run_id,actor,writes):
        self.assert_active(run_id)
        row=ImportLifecycle(run_id,"promoted",utc_now(),actor,"explore","",writes)
        atomic_write_json(self.path(run_id),row.to_dict()); return row
