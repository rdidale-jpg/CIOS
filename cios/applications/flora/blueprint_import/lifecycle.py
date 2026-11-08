"""Durable lifecycle termination for the existing governed importer."""
from __future__ import annotations
import json
import shutil
from dataclasses import dataclass, replace
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
    acceptance_execution_id: str = ""
    acceptance_run_id: str = ""
    prior_lifecycle_state: dict | None = None
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
        # A staged lifecycle transition is visible only with its successful
        # existing promotion receipt. This also fails closed after hard interruption.
        for _ in range(32):
            execution=data.get('acceptance_execution_id')
            if not execution: break
            receipt=data_path('blueprint_import','promotion','executions',data['acceptance_run_id'],execution+'.json')
            try: committed=json.loads(receipt.read_text()).get('final_execution_status')=='succeeded'
            except (OSError,ValueError): committed=False
            if committed: break
            data=data.get('prior_lifecycle_state') or {'import_run_id':run_id}
        else: return ImportLifecycle(run_id)
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
    def mark_promoted(self,run_id,actor,writes,execution_id=""):
        self.assert_active(run_id)
        row=ImportLifecycle(run_id,"promoted",utc_now(),actor,"explore","",writes,True,"")
        if execution_id:
            row=replace(row,acceptance_execution_id=execution_id,acceptance_run_id=run_id,
                        prior_lifecycle_state=self.get(run_id).to_dict())
        atomic_write_json(self.path(run_id),row.to_dict()); return row

    def mark_superseded(self, run_id, actor, replacement_run_id, execution_id=""):
        old = self.get(run_id)
        if old.state != "promoted": raise ValueError("Only a promoted release can be superseded.")
        row = ImportLifecycle(run_id, "superseded", utc_now(), actor, "history",
                              "Replaced by a successfully reviewed and promoted release.",
                              old.canonical_writes, False, replacement_run_id)
        if execution_id:
            row=replace(row,acceptance_execution_id=execution_id,acceptance_run_id=replacement_run_id,
                        prior_lifecycle_state=old.to_dict())
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
                    and identity.status == "recognised" and self.same_scope(package,other)):
                matches.append(other)
        if len(matches)>1: raise ValueError('Multiple current releases require explicit reconciliation')
        return next(iter(matches),None)

    @staticmethod
    def same_scope(left,right):
        from .twin_governance import project_twin_identity
        a,b=project_twin_identity(left),project_twin_identity(right)
        keys=('twin_id','twin_type','primary_subject_id','primary_subject_class','canonical_owner','governed_scope')
        return (a.status==b.status=='recognised' and left.workspace_id==right.workspace_id
                and left.identity.enterprise_id.casefold()==right.identity.enterprise_id.casefold()
                and all(getattr(a,key)==getattr(b,key) for key in keys))

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

    def delete_candidate(self, run_id, actor, confirmation, reason="Operator deleted obsolete candidate import", *, headers=None):
        from cios.applications.flora.access import require_capability
        context = require_capability(headers, "blueprint_import_admin")
        package = self.package_for_run(run_id)
        if not package:
            raise PermissionError("Import unavailable")
        require_capability(headers, "blueprint_import_admin", package.identity.enterprise_id, package.workspace_id)
        if actor != context.user_id:
            raise PermissionError("Deletion actor does not match verified authority")
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
        if self.lifecycle.get(package.import_run_id).state != "promoted":
            raise ValueError("Only successful promoted releases can supersede a prior release")
        previous = self.current_release(package)
        if previous: self.lifecycle.mark_superseded(previous.import_run_id, actor, package.import_run_id)
        return previous
