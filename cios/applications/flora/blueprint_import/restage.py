"""Owner-triggered restaging for preserved Blueprint packages."""
from __future__ import annotations

import json, time, traceback
from typing import Any

from cios.applications.flora.access import authenticated_flora_user
from cios.applications.flora.storage import atomic_write_json, data_path, ensure_writable_dir
from .archive import sha256_bytes
from .candidates import CandidateStagingRepository, PROJECTION_ONLY_CLASSES
from .cios_twin_adapter import MAPPING_VERSION
from .ledger import BlueprintImportLedger, utc_now
from .registry import BlueprintPackageRegistry
from .review_plan import BlueprintReviewPlanCoordinator
from .validator import BlueprintPackageValidator, can_inspect_blueprint_package

RESTAGE_STAGES = [
    "package located", "immutable archive verified", "mapping version selected", "workbook loaded",
    "sheets mapped", "candidates staged", "prior review plan invalidated", "new review plan generated", "complete",
]


def can_restage_blueprint_package(headers: Any, package) -> bool:
    return bool(authenticated_flora_user(headers) and can_inspect_blueprint_package(headers, package))


class BlueprintRestageService:
    def __init__(self, registry=None, staging=None, ledger=None):
        self.registry = registry or BlueprintPackageRegistry(); self.staging = staging or CandidateStagingRepository(); self.ledger = ledger or BlueprintImportLedger()

    def job_dir(self, import_run_id: str): return data_path("blueprint_import", "restage_jobs", import_run_id)
    def history_dir(self, import_run_id: str): return data_path("blueprint_import", "staging_history", import_run_id)
    def active_path(self, import_run_id: str): return data_path("blueprint_import", "staging", import_run_id, "active.json")

    def active_version(self, import_run_id: str) -> str:
        p = self.active_path(import_run_id)
        if p.exists(): return str(json.loads(p.read_text()).get("staging_version") or "")
        s = self.staging.load_summary(import_run_id) or {}
        return str(s.get("staging_version") or "staging-v1") if s else ""

    def history(self, import_run_id: str) -> list[dict[str, Any]]:
        root = self.history_dir(import_run_id)
        if not root.exists(): return []
        out=[]
        for p in sorted(root.glob("*/summary.json")):
            d=json.loads(p.read_text()); out.append(d)
        return out

    def ensure_restage(self, import_run_id: str, actor: str, headers: Any) -> dict[str, Any]:
        package = next((p for p in self.registry.list() if p.import_run_id == import_run_id), None)
        if not package: raise PermissionError("Blueprint import record is unavailable or access is denied.")
        if not can_restage_blueprint_package(headers, package): raise PermissionError("You are not authorised to restage this Blueprint package.")
        current = self.staging.load_summary(import_run_id) or {}
        package_checksum = package.package_sha256
        state_fp = self._state_fingerprint(import_run_id)
        completed = self._completed(import_run_id, package_checksum, MAPPING_VERSION, state_fp)
        if completed:
            completed["already_completed"] = True
            return completed
        running = self._running(import_run_id, package_checksum, MAPPING_VERSION, state_fp)
        if running: return running
        job_id = "bpi-restage-" + sha256_bytes(f"{import_run_id}\n{package_checksum}\n{MAPPING_VERSION}\n{state_fp}".encode())[:24]
        job = {"job_id": job_id, "import_run_id": import_run_id, "package_ref": package.package_ref, "package_checksum": package_checksum, "mapping_version": MAPPING_VERSION, "staging_state_fingerprint": state_fp, "status": "Running", "stage": RESTAGE_STAGES[0], "started_at": time.time(), "created_by": actor, "records_processed": 0, "canonical_changes_made": "no", "prior_active_staging_available": "yes" if current else "no"}
        self._save(job)
        # Synchronous for fast initial implementation; route renders progress/final page.
        return self._run(job, package, actor, headers)

    def _run(self, job, package, actor, headers):
        try:
            content = data_path(package.archive_path).read_bytes()
            if sha256_bytes(content) != package.package_sha256: raise ValueError("Immutable archive checksum does not match registry record")
            self._stage(job, 1); self._stage(job, 2)
            old_version = self.active_version(package.import_run_id) or "staging-v1"
            self._snapshot_active(package.import_run_id, old_version)
            self._stage(job, 3); self._stage(job, 4)
            # Force current adapter to restage even when the same mapping was previously present.
            summary_path = self.staging.root_for(package.import_run_id) / "summary.json"
            if summary_path.exists():
                data = json.loads(summary_path.read_text()); data["mapping_version"] = "__restage_in_progress__"; atomic_write_json(summary_path, data)
            result = BlueprintPackageValidator(self.registry, self.staging, self.ledger).validate_and_stage(package.package_ref, actor, headers)
            self._stage(job, 5, result.candidate_records_staged)
            new_summary = self.staging.load_summary(package.import_run_id) or result.to_dict()
            new_version = "staging-" + sha256_bytes(f"{package.import_run_id}\n{MAPPING_VERSION}\n{time.time()}".encode())[:12]
            meta = {"staging_version": new_version, "mapping_version": MAPPING_VERSION, "created_at": utc_now(), "created_by": actor, "supersedes_staging_version": old_version, "package_checksum": package.package_sha256, "active": True}
            new_summary.update(meta)
            atomic_write_json(summary_path, new_summary)
            atomic_write_json(self.active_path(package.import_run_id), meta)
            self._snapshot_active(package.import_run_id, new_version)
            stale = self._invalidate_plans(package.import_run_id, old_version, new_version)
            self._stage(job, 6, result.candidate_records_staged)
            def defaults():
                from .views import _ensure_reviews_and_mappings
                _ensure_reviews_and_mappings({"package": package, "candidates": self.staging.list_candidates(package.import_run_id)}, headers)
            review = BlueprintReviewPlanCoordinator().ensure_job(package.import_run_id, actor, headers, defaults)
            self._stage(job, 7, result.candidate_records_staged)
            job.update(status="Complete", stage=RESTAGE_STAGES[-1], completed_at=time.time(), staging_version=new_version, supersedes_staging_version=old_version, review_plan_id=review.get("plan_id",""), old_review_plans_marked_stale=stale, candidate_summary=_counts(self.staging.list_candidates(package.import_run_id)))
            self._save(job); self.ledger.append("blueprint_package_restaged", job); return job
        except Exception:
            ref = "bpi-restage-error-" + sha256_bytes(traceback.format_exc().encode())[:12]
            job.update(status="Failed", diagnostic_reference=ref, completed_at=time.time(), error_category="BlueprintRestageError")
            self._save(job); self.ledger.append("blueprint_package_restage_failed", job); return job

    def _snapshot_active(self, import_run_id, version):
        root = self.staging.root_for(import_run_id); hist = self.history_dir(import_run_id) / version
        if (root / "summary.json").exists(): atomic_write_json(hist / "summary.json", json.loads((root/"summary.json").read_text()) | {"staging_version": version})
        croot = root / "candidates"
        if croot.exists():
            for p in croot.glob("*.json"):
                atomic_write_json(hist / "candidates" / p.name, json.loads(p.read_text()))

    def _invalidate_plans(self, import_run_id, old_version, new_version):
        count=0
        for p in data_path("blueprint_import", "plans", import_run_id).glob("*.json") if data_path("blueprint_import", "plans", import_run_id).exists() else []:
            d=json.loads(p.read_text());
            if d.get("stale") is not True:
                d.update(stale=True, stale_reason="Superseded by Blueprint restaging", invalidated_at=utc_now(), invalidated_by_staging_version=new_version, staging_version=old_version); atomic_write_json(p,d); count+=1
        for rel in [("review_summaries", import_run_id, "summary.json")]:
            p=data_path("blueprint_import", *rel)
            if p.exists():
                d=json.loads(p.read_text()); d.update(status="Stale", stale=True, invalidated_by_staging_version=new_version); atomic_write_json(p,d)
        return count

    def _state_fingerprint(self, import_run_id):
        s=self.staging.load_summary(import_run_id) or {}; c=self.staging.list_candidates(import_run_id)
        return sha256_bytes(json.dumps({"ids":[x.get("candidate_record_id") for x in c], "counts":{k:s.get(k) for k in ("candidate_records_staged","records_accepted_into_staging","records_quarantined","records_rejected")}}, sort_keys=True).encode())
    def _save(self, job): atomic_write_json(self.job_dir(job["import_run_id"]) / f"{job['job_id']}.json", job)
    def _stage(self, job, idx, records=0): job.update(stage=RESTAGE_STAGES[idx], records_processed=records); self._save(job)
    def _jobs(self, import_run_id):
        root=self.job_dir(import_run_id); return [json.loads(p.read_text()) for p in sorted(root.glob("*.json"))] if root.exists() else []
    def _running(self, i,c,m,f): return next((j for j in self._jobs(i) if j.get("package_checksum")==c and j.get("mapping_version")==m and j.get("staging_state_fingerprint")==f and j.get("status")=="Running"), None)
    def _completed(self, i,c,m,f): return next((j for j in reversed(self._jobs(i)) if j.get("package_checksum")==c and j.get("mapping_version")==m and j.get("staging_state_fingerprint")==f and j.get("status")=="Complete"), None)

def _counts(candidates):
    from collections import Counter
    c=Counter(x.get("validation_status") for x in candidates); p=sum(1 for x in candidates if x.get("candidate_object_class") in PROJECTION_ONLY_CLASSES)
    return {"Accepted": c["accepted"], "Quarantined": c["quarantined"], "Rejected": c["rejected"], "Projection-only": p}
