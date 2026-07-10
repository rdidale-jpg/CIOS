"""Scalable persisted review-plan preparation for Blueprint imports."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import json, os, threading, time, traceback
from typing import Any

from cios.applications.flora.storage import atomic_write_json, data_path
from cios.applications.flora.live.runtime import deployment_metadata
from .archive import sha256_bytes
from .candidates import CandidateStagingRepository
from .planning import DryRunPlanRepository, DryRunPlanningService
from .registry import BlueprintPackageRegistry
from .cios_twin_adapter import MAPPING_VERSION

STAGES = [
    "Loading staged candidates", "Classifying records", "Detecting duplicates", "Resolving references",
    "Calculating proposed mutations", "Grouping quarantine reasons", "Preparing review summary", "Complete",
]
ASYNC_THRESHOLD = int(os.getenv("FLORA_BLUEPRINT_REVIEW_ASYNC_THRESHOLD", "1000"))
PAGE_SIZE_DEFAULT = 50
PAGE_SIZE_MAX = 100
_RUNNING: set[str] = set()
_LOCK = threading.Lock()

@dataclass(frozen=True)
class ReviewJob:
    job_id: str
    import_run_id: str
    package_ref: str
    package_checksum: str
    staging_fingerprint: str
    status: str
    stage: str
    records_total: int
    records_processed: int = 0
    error_category: str = ""
    diagnostic_reference: str = ""
    started_at: float = 0
    completed_at: float = 0
    plan_id: str = ""
    plan_persisted: bool = False

class BlueprintReviewPlanCoordinator:
    def __init__(self, staging=None, registry=None, plans=None):
        self.staging = staging or CandidateStagingRepository(); self.registry = registry or BlueprintPackageRegistry(); self.plans = plans or DryRunPlanRepository()
    def job_dir(self, import_run_id: str): return data_path("blueprint_import", "review_jobs", import_run_id)
    def summary_path(self, import_run_id: str): return data_path("blueprint_import", "review_summaries", import_run_id, "summary.json")
    def detail_path(self, import_run_id: str): return data_path("blueprint_import", "review_summaries", import_run_id, "details.json")
    def fingerprint(self, import_run_id: str, candidates: list[dict[str, Any]] | None = None) -> str:
        summary = self.staging.load_summary(import_run_id) or {}
        if candidates is None: candidates = self.staging.list_candidates(import_run_id)
        payload = {"summary": {k: summary.get(k) for k in ("package_sha256","candidate_records_staged","records_accepted_into_staging","records_quarantined","records_rejected","canonical_mutations")}, "candidate_ids": [c.get("candidate_record_id") for c in candidates]}
        return sha256_bytes(json.dumps(payload, sort_keys=True).encode())
    def latest_job(self, import_run_id: str) -> dict[str, Any] | None:
        root = self.job_dir(import_run_id)
        if not root.exists(): return None
        jobs = sorted(root.glob("*.json"))
        return json.loads(jobs[-1].read_text()) if jobs else None
    def completed_summary(self, import_run_id: str, fp: str) -> dict[str, Any] | None:
        path = self.summary_path(import_run_id)
        if not path.exists(): return None
        data = json.loads(path.read_text())
        return data if data.get("staging_fingerprint") == fp and data.get("status") == "Ready" else None
    def ensure_job(self, import_run_id: str, actor: str, headers: Any, ensure_defaults) -> dict[str, Any]:
        candidates = self.staging.list_candidates(import_run_id); fp = self.fingerprint(import_run_id, candidates)
        package = self.registry.get(str(candidates[0]["source_package_ref"])) if candidates else None
        ready = self.completed_summary(import_run_id, fp)
        if ready: return ready | {"candidate_count": len(candidates)}
        existing = self.latest_job(import_run_id)
        if existing and existing.get("staging_fingerprint") == fp and existing.get("status") in {"Preparing","Failed"}:
            return existing | {"candidate_count": len(candidates)}
        job_id = "bpi-review-job-" + sha256_bytes(f"{import_run_id}\n{fp}".encode())[:24]
        job = {"job_id": job_id, "import_run_id": import_run_id, "package_ref": getattr(package, "package_ref", ""), "package_checksum": getattr(package, "package_sha256", ""), "staging_fingerprint": fp, "status": "Preparing", "stage": STAGES[0], "records_total": len(candidates), "records_processed": 0, "started_at": time.time(), "plan_persisted": False}
        atomic_write_json(self.job_dir(import_run_id) / f"{job_id}.json", job)
        if len(candidates) >= ASYNC_THRESHOLD:
            with _LOCK:
                if job_id not in _RUNNING:
                    _RUNNING.add(job_id); threading.Thread(target=self._run, args=(job, actor, headers, ensure_defaults), daemon=True).start()
            return job | {"candidate_count": len(candidates)}
        return self._run(job, actor, headers, ensure_defaults) | {"candidate_count": len(candidates)}
    def _save_job(self, job): atomic_write_json(self.job_dir(job["import_run_id"]) / f"{job['job_id']}.json", job)
    def _run(self, job, actor, headers, ensure_defaults):
        try:
            ensure_defaults()
            for stage in STAGES[1:5]: job.update(stage=stage); self._save_job(job)
            plan = DryRunPlanningService().create_plan(job["import_run_id"], actor, headers)
            effects = [e.to_dict() for e in plan.effects]
            totals = Counter(e["effect_type"] for e in effects)
            candidates = {c["candidate_record_id"]: c for c in self.staging.list_candidates(job["import_run_id"])}
            job.update(stage=STAGES[5], records_processed=len(effects)); self._save_job(job)
            q = Counter(_finding_reason(c) for c in candidates.values() if c.get("validation_status") == "quarantined")
            rejected = [c for c in candidates.values() if c.get("validation_status") == "rejected"]
            summary = {**job, "status":"Ready", "stage":"Complete", "completed_at":time.time(), "plan_id":plan.plan_id, "plan_persisted":True, "proposed":{"Creates":totals["create"],"Updates":totals["update"],"Unchanged":totals["unchanged"]+totals["mapped"],"Conflicts":totals["conflict"],"Unresolved references":totals["unresolved"],"Projection-only":totals["projection"], "Ignored":totals["ignored"]}, "mapping_version": MAPPING_VERSION, "candidate_summary": _candidate_counts(candidates.values()), "class_summary": _class_counts(candidates.values()), "sheet_mapping_summary": _sheet_counts(candidates.values()), "examples_by_class": _examples_by_class(candidates.values()), "quarantine_reasons": dict(q), "ignored_reasons": _ignored_reasons(candidates.values()), "rejected_reasons": _rejected_reasons(rejected), "mapping_quality": _mapping_quality(candidates.values()), "rejected_count": len(rejected), "deployment_commit_sha": deployment_metadata().get("commit_sha") or "Unavailable"}
            atomic_write_json(self.detail_path(job["import_run_id"]), {"effects": effects, "candidates": list(candidates.values())})
            self._save_job(summary)
            atomic_write_json(self.summary_path(job["import_run_id"]), summary)
            return summary
        except Exception as exc:
            ref = "bpi-review-error-" + sha256_bytes(traceback.format_exc().encode())[:12]
            job.update(status="Failed", error_category=type(exc).__name__, diagnostic_reference=ref, completed_at=time.time())
            self._save_job(job); return job
        finally:
            with _LOCK: _RUNNING.discard(job["job_id"])

def _candidate_counts(candidates):
    c = Counter(x.get("validation_status") for x in candidates)
    return {"Accepted": c["accepted"], "Quarantined": c["quarantined"], "Rejected": c["rejected"], "Ignored": c["ignored"], "Unsupported": 0}

def _class_counts(candidates):
    by=defaultdict(Counter)
    for c in candidates: by[c.get("validation_status")][c.get("candidate_object_class")] += 1
    return {str(k): dict(v) for k,v in by.items()}

def _sheet_counts(candidates):
    by=defaultdict(Counter)
    for c in candidates: by[c.get("source_sheet")][c.get("candidate_object_class")] += 1
    return {str(k): dict(v) for k,v in by.items()}

def _examples_by_class(candidates):
    out={}
    for c in candidates:
        rc=str(c.get("candidate_object_class"))
        out.setdefault(rc, {"external_id": c.get("original_source_id"), "sheet": c.get("source_sheet"), "status": c.get("validation_status")})
    return out

def _finding_reason(candidate):
    findings = candidate.get("validation_findings") or []
    return str((findings[0] or {}).get("message") or (findings[0] or {}).get("code") or "Quarantined by staging validation") if findings else "Quarantined by staging validation"


def _ignored_reasons(candidates):
    out = Counter()
    for c in candidates:
        if c.get("validation_status") == "ignored":
            out[str((c.get("payload") or {}).get("ignore_reason") or "ignored_row")] += 1
    return dict(out)


def _rejected_reasons(candidates):
    out = Counter()
    for c in candidates:
        out[_finding_reason(c)] += 1
    return dict(out)


def _mapping_quality(candidates):
    rows = list(candidates)
    accepted = [c for c in rows if c.get("validation_status") == "accepted"]
    projection = [c for c in rows if c.get("candidate_object_class") in {"pain_point", "current_response", "response_effectiveness", "residual_pain", "burning_platform", "transformation_pressure_view", "priority_disposition", "stakeholder_hot_button", "solution_pattern", "executive_publication"}]
    derived = sum(1 for c in rows if isinstance((c.get("payload") or {}).get("identifier_derivation"), dict))
    source_supplied = sum(1 for c in rows if ((c.get("payload") or {}).get("identifier_metadata") or {}).get("source_supplied"))
    classes = {c.get("candidate_object_class") for c in accepted}
    return {
        "accepted_by_class": _class_counts(accepted).get("accepted", {}),
        "projection_only_by_class": dict(Counter(c.get("candidate_object_class") for c in projection)),
        "top_source_worksheets": dict(Counter(c.get("source_sheet") for c in rows).most_common(10)),
        "top_unresolved_lineage_patterns": dict(Counter(_finding_reason(c) for c in rows if "lineage" in _finding_reason(c).casefold()).most_common(10)),
        "derived_id_count": derived,
        "source_supplied_id_count": source_supplied,
        "twin_completeness_indicators": {name: (name in classes) for name in ["source", "evidence", "observation", "unknown", "contradiction", "entity", "relationship", "human_knowledge"]} | {"projection_layer": bool(projection)},
    }
