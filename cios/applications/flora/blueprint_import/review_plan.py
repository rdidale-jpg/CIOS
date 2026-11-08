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
from .planning import DryRunPlanRepository, DryRunPlanningService, PERSISTABLE_CANONICAL_CLASSES, SUPPORT_RECORD_CLASSES
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
        from .mapping import ImportMappingRepository
        from .review import CandidateReviewRepository
        from .twin_governance import project_twin_identity
        package=self.registry.get(str(candidates[0]['source_package_ref'])) if candidates else None
        payload.update(identity=project_twin_identity(package).to_dict() if package else None,
                       mappings=ImportMappingRepository().list(import_run_id),
                       reviews=CandidateReviewRepository().latest_by_candidate(import_run_id))
        return sha256_bytes(json.dumps(payload, sort_keys=True).encode())
    def latest_job(self, import_run_id: str) -> dict[str, Any] | None:
        root = self.job_dir(import_run_id)
        if not root.exists(): return None
        jobs = [json.loads(path.read_text()) for path in root.glob("*.json")]
        return max(jobs,key=lambda row:row.get("started_at",0)) if jobs else None
    def completed_summary(self, import_run_id: str, fp: str) -> dict[str, Any] | None:
        path = self.summary_path(import_run_id)
        if not path.exists(): return None
        data = json.loads(path.read_text())
        if data.get("mapping_version") != MAPPING_VERSION:
            data.update(status="Stale", stale=True, stale_reason="Review was generated with an older mapping or validation version", current_mapping_version=MAPPING_VERSION)
            atomic_write_json(path, data)
            return None
        return data if data.get("staging_fingerprint") == fp and data.get("status") == "Ready" else None
    def ensure_job(self, import_run_id: str, actor: str, headers: Any, ensure_defaults) -> dict[str, Any]:
        from cios.applications.flora.access import require_capability
        context = require_capability(headers, "package.review")
        if actor != context.user_id:
            raise PermissionError("Review preparation actor does not match verified authority")
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
            job["staging_fingerprint"]=self.fingerprint(job["import_run_id"])
            for stage in STAGES[1:5]: job.update(stage=stage); self._save_job(job)
            plan = DryRunPlanningService().create_plan(job["import_run_id"], actor, headers)
            effects = [e.to_dict() for e in plan.effects]
            totals = Counter(e["effect_type"] for e in effects)
            candidates = {c["candidate_record_id"]: c for c in self.staging.list_candidates(job["import_run_id"])}
            job.update(stage=STAGES[5], records_processed=len(effects)); self._save_job(job)
            q = Counter(_finding_reason(c) for c in candidates.values() if c.get("validation_status") == "quarantined")
            constructor_failures = sum(1 for c in candidates.values() if any((f.get("code") == "quarantined_non_atomic_observation") for f in (c.get("validation_findings") or [])))
            rejected = [c for c in candidates.values() if c.get("validation_status") == "rejected"]
            proposed,reconciliation=review_effect_counts(list(candidates.values()),effects)
            support_records=proposed.get('Accepted support records',0)
            non_persistable=proposed.get('Accepted but non-persistable',0)
            accepted_canonical=proposed.get('Accepted canonical candidates',0)
            reconciles=reconciliation['passes']
            summary = {**job, "status":"Ready" if reconciles else "Not ready", "stage":"Complete", "completed_at":time.time(), "plan_id":plan.plan_id, "plan_persisted":True, "proposed": proposed, "accepted_canonical": accepted_canonical, "constructor_validation_failures": constructor_failures, "non_atomic_observations": constructor_failures, "reconciliation": reconciliation, "class_persistence_readiness": _class_persistence_readiness(candidates.values(), effects), "mapping_version": MAPPING_VERSION, "candidate_summary": _candidate_counts(candidates.values(), accepted_canonical), "class_summary": _class_counts(candidates.values()), "sheet_mapping_summary": _sheet_counts(candidates.values()), "examples_by_class": _examples_by_class(candidates.values()), "quarantine_reasons": dict(q), "ignored_reasons": _ignored_reasons(candidates.values()), "rejected_reasons": _rejected_reasons(rejected), "mapping_quality": _mapping_quality(candidates.values()), "rejected_count": len(rejected), "deployment_commit_sha": deployment_metadata().get("commit_sha") or "Unavailable"}
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

def _candidate_counts(candidates, accepted_canonical: int | None = None):
    c = Counter(x.get("validation_status") for x in candidates)
    return {"Accepted": c["accepted"], "Accepted canonical candidates": c["accepted"] if accepted_canonical is None else accepted_canonical, "Accepted support records": 0, "Accepted but non-persistable": 0, "Collapsed/deduplicated candidates": 0, "Quarantined": c["quarantined"], "Rejected": c["rejected"], "Ignored": c["ignored"], "Unsupported": 0}

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
        "derived_id_collisions": sum(1 for c in rows if isinstance((c.get("payload") or {}).get("identifier_collision_resolution"), dict)),
        "derived_id_failures": sum(1 for c in rows if any((f.get("code") == "quarantined_missing_identifier") for f in (c.get("validation_findings") or []))),
        "twin_completeness_indicators": {name: (name in classes) for name in ["source", "evidence", "observation", "unknown", "contradiction", "entity", "relationship", "human_knowledge"]} | {"projection_layer": bool(projection)},
    }


def _class_persistence_readiness(candidates, effects):
    accepted = Counter(c.get("candidate_object_class") for c in candidates if c.get("validation_status") == "accepted")
    by_class = defaultdict(lambda: Counter())
    for e in effects:
        by_class[e["record_class"]][e["effect_type"]] += 1
        by_class[e["record_class"]]["expected_mutations"] += int(e.get("expected_mutation_count") or 0)
    rows = []
    for rc in sorted(accepted):
        disposition = "persistable" if rc in PERSISTABLE_CANONICAL_CLASSES else "support_metadata" if rc in SUPPORT_RECORD_CLASSES else "non_persistable"
        rows.append({"class": rc, "accepted": accepted[rc], "persistable": rc in PERSISTABLE_CANONICAL_CLASSES, "planned_effects": dict(by_class[rc]), "expected_mutations": by_class[rc]["expected_mutations"], "disposition": disposition})
    return rows


def review_effect_counts(candidates, effects):
    """Read-only partitions over existing class-persistence and plan owners.

    Staging acceptance is not canonical acceptance. A non-persistable create
    proposal must not be counted as a canonical create or counted twice.
    """
    by_id={e['candidate_id']:e for e in effects}
    accepted=[c for c in candidates if c.get('validation_status')=='accepted']
    counts=Counter();blocking=[]
    for c in accepted:
        rc=c['candidate_object_class'];cid=c['candidate_record_id']
        e=by_id.get(cid,{'effect_type':'unresolved'});kind=e['effect_type']
        if rc in SUPPORT_RECORD_CLASSES: counts['Accepted support records']+=1
        elif rc not in PERSISTABLE_CANONICAL_CLASSES: counts['Accepted but non-persistable']+=1
        else:
            counts['Accepted canonical candidates']+=1
            if kind in {'create','update'} and e.get('expected_mutation_count')==1:
                counts['Creates' if kind=='create' else 'Updates']+=1
            elif kind in {'mapped','unchanged'}: counts['Unchanged']+=1
            elif kind=='duplicate': counts['Collapsed/deduplicated candidates']+=1
            else:
                counts['Deferred or excluded canonical candidates']+=1
                if kind in {'conflict','unresolved','create','update'}: blocking.append(cid)
    counts.update({'Projection-only':sum(e['effect_type']=='projection' for e in effects),
                   'Ignored':sum(e['effect_type']=='ignored' for e in effects),
                   'Conflicts':sum(e['effect_type']=='conflict' for e in effects),
                   'Unresolved references':sum(e['effect_type']=='unresolved' for e in effects),
                   'Deferred for review':sum(e['effect_type']=='defer' for e in effects),
                   'Expected canonical mutations':sum(int(e.get('expected_mutation_count') or 0) for e in effects)})
    partitions=('Creates','Updates','Unchanged','Collapsed/deduplicated candidates',
                'Accepted support records','Accepted but non-persistable','Deferred or excluded canonical candidates')
    accounted=sum(counts[key] for key in partitions)
    rec={'accepted_staged':len(accepted),'accepted_canonical':counts['Accepted canonical candidates'],
         'creates':counts['Creates'],'updates':counts['Updates'],'unchanged':counts['Unchanged'],
         'accepted_support_records':counts['Accepted support records'],
         'accepted_but_non_persistable':counts['Accepted but non-persistable'],
         'collapsed_deduplicated_candidates':counts['Collapsed/deduplicated candidates'],
         'deferred_or_excluded_canonical_candidates':counts['Deferred or excluded canonical candidates'],
         'expected_mutations':counts['Expected canonical mutations'],'accounted_staged':accounted,
         'mismatch':len(accepted)-accounted,'counts_reconcile':len(accepted)==accounted,
         'blocking_canonical_candidates':blocking,'passes':len(accepted)==accounted and not blocking}
    for key in (*partitions,'Accepted canonical candidates'): counts.setdefault(key,0)
    return dict(counts),rec
