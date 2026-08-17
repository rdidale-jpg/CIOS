"""Durable lifecycle termination for the existing governed importer."""
from __future__ import annotations
import json
import shutil
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
    current: bool = False
    superseded_by: str = ""
    def to_dict(self): return self.__dict__.copy()

class ImportLifecycleService:
    """Owns cancellation state; archive retention remains with archive storage."""
    def path(self, run_id): return data_path("blueprint_import", "lifecycle", f"{run_id}.json")
    def get(self, run_id):
        p=self.path(run_id)
        if not p.exists(): return ImportLifecycle(run_id)
        data=json.loads(p.read_text())
        # Lifecycle records written before release management represented a
        # promoted release as the sole current release implicitly.
        if data.get("state") == "promoted" and "current" not in data: data["current"] = True
        return ImportLifecycle(**data)
    def assert_active(self, run_id):
        if self.get(run_id).state in {"cancelled", "deleted", "superseded", "archived"}: raise ValueError("This import is terminal and cannot be reviewed or promoted.")
    def cancel(self, run_id, actor, stage, reason=""):
        old=self.get(run_id)
        if old.state == "promoted": raise ValueError("A promoted import cannot be cancelled. Use governed correction or supersession.")
        if old.state == "cancelled": return old
        row=ImportLifecycle(run_id,"cancelled",utc_now(),actor,stage,reason.strip(),0,False,"")
        atomic_write_json(self.path(run_id),row.to_dict())
        BlueprintImportLedger().append("import_cancelled",{**row.to_dict(),"staged_candidates_invalidated":True,"archive_disposition":"retained under existing archive policy","canonical_writes_occurred":False})
        return row
    def mark_promoted(self,run_id,actor,writes):
        self.assert_active(run_id)
        row=ImportLifecycle(run_id,"promoted",utc_now(),actor,"explore","",writes,True,"")
        atomic_write_json(self.path(run_id),row.to_dict()); return row

    def mark_superseded(self, run_id, actor, replacement_run_id):
        old = self.get(run_id)
        if old.state != "promoted": raise ValueError("Only a promoted release can be superseded.")
        row = ImportLifecycle(run_id, "superseded", utc_now(), actor, "history",
                              "Replaced by a successfully reviewed and promoted release.",
                              old.canonical_writes, False, replacement_run_id)
        atomic_write_json(self.path(run_id), row.to_dict())
        BlueprintImportLedger().append("twin_release_superseded", row.to_dict())
        return row


class TwinImportLifecycleService:
    """Lifecycle operations over the existing registry, staging and audit owners."""

    DISPOSABLE_DIRS = ("staging", "staging_history", "restage_jobs", "review_jobs",
                       "review_summaries", "reviews", "human_reviews", "plans",
                       "mappings", "guidance", "identity_resolution")

    def __init__(self):
        from .registry import BlueprintPackageRegistry
        self.registry = BlueprintPackageRegistry()
        self.lifecycle = ImportLifecycleService()

    def package_for_run(self, run_id):
        return next((p for p in self.registry.list() if p.import_run_id == run_id), None)

    def current_release(self, package):
        from .twin_governance import project_twin_identity
        wanted = project_twin_identity(package)
        if wanted.status != "recognised": return None
        matches = []
        for other in self.registry.list():
            identity = project_twin_identity(other); state = self.lifecycle.get(other.import_run_id)
            if (other.import_run_id != package.import_run_id and state.state == "promoted" and state.current
                    and identity.status == "recognised" and identity.twin_id == wanted.twin_id):
                matches.append(other)
        return max(matches, key=lambda p: p.received_at, default=None)

    def delete_preview(self, run_id):
        from .twin_governance import project_twin_identity
        package = self.package_for_run(run_id)
        if not package: raise ValueError("Import record is unavailable.")
        state = self.lifecycle.get(run_id)
        promoted = state.state in {"promoted", "superseded", "archived"} or state.canonical_writes > 0
        staging = data_path("blueprint_import", "staging", run_id)
        history = data_path("blueprint_import", "staging_history", run_id)
        archive = data_path(package.archive_path)
        shared = any(p.import_run_id != run_id and p.archive_path == package.archive_path for p in self.registry.list())
        identity = project_twin_identity(package)
        return {"import_run_id": run_id, "twin_id": identity.twin_id or package.identity.enterprise_id,
                "release": identity.package_version, "package_id": package.identity.package_id,
                "lifecycle": state.state, "promoted": promoted, "permitted": not promoted,
                "candidate_records": len(list(staging.glob("candidates/*.json"))) if staging.exists() else 0,
                "staging_artifacts": sum(1 for p in (staging, history) if p.exists() for x in p.rglob("*") if x.is_file()),
                "package_artifacts": 1 if archive.exists() and not shared else 0,
                "audit_records_retained": "import receipt and deletion tombstone",
                "canonical_intelligence_affected": False if not promoted else True}

    def delete_candidate(self, run_id, actor, confirmation, reason="Operator deleted obsolete candidate import"):
        preview = self.delete_preview(run_id)
        if not preview["permitted"] or preview["canonical_intelligence_affected"]:
            raise ValueError("Promoted/canonical releases cannot be hard-deleted; import a newer release to supersede them.")
        if confirmation != "DELETE CANDIDATE IMPORT":
            raise ValueError("Type DELETE CANDIDATE IMPORT to confirm deletion.")
        package = self.package_for_run(run_id); removed_files = 0; removed_bytes = 0
        for name in self.DISPOSABLE_DIRS:
            path = data_path("blueprint_import", name, run_id)
            if path.is_file():
                removed_bytes += path.stat().st_size; path.unlink(); removed_files += 1
            elif path.exists():
                files = [p for p in path.rglob("*") if p.is_file()]
                removed_files += len(files); removed_bytes += sum(p.stat().st_size for p in files); shutil.rmtree(path)
        for path in (data_path("blueprint_import", "human_reviews", f"{run_id}.json"),
                     data_path("blueprint_import", "guidance", f"{run_id}.json"),
                     data_path("blueprint_import", "identity_resolution", f"{run_id}.json")):
            if path.exists(): removed_bytes += path.stat().st_size; path.unlink(); removed_files += 1
        archive = data_path(package.archive_path)
        shared = any(p.import_run_id != run_id and p.archive_path == package.archive_path for p in self.registry.list())
        if archive.exists() and not shared:
            removed_bytes += archive.stat().st_size; archive.unlink(); removed_files += 1
            try: archive.parent.rmdir()
            except OSError: pass
        self.registry._path_for_ref(package.package_ref).unlink(missing_ok=True)
        tombstone = {**preview, "deleted_at": utc_now(), "deleted_by": actor, "reason": reason.strip(),
                     "canonical_impact": "none", "recovered_files": removed_files, "recovered_bytes": removed_bytes}
        atomic_write_json(data_path("blueprint_import", "tombstones", f"{run_id}.json"), tombstone)
        BlueprintImportLedger().append("candidate_import_deleted", tombstone)
        return tombstone

    def supersede_previous_after_promotion(self, package, actor):
        previous = self.current_release(package)
        if previous: self.lifecycle.mark_superseded(previous.import_run_id, actor, package.import_run_id)
        return previous
