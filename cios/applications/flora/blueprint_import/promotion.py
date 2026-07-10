"""Governed canonical promotion for approved Blueprint dry-run plans."""
from __future__ import annotations

import json, os, shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

from cios.applications.flora.access import authenticated_flora_user, can_access_enterprise, flora_roles
from cios.applications.flora.memory.models import Observation
from cios.applications.flora.memory.repository import EvidenceRepository, ObservationRepository
from cios.applications.flora.storage import atomic_write_json, data_path, ensure_writable_dir

from .archive import sha256_bytes
from .candidates import CandidateStagingRepository
from .ledger import BlueprintImportLedger, utc_now
from .mapping import ImportMappingRepository
from .planning import DryRunPlanRepository, ProposedCanonicalEffect
from .registry import BlueprintPackageRegistry
from .review import CandidateReviewRepository

PromotionStatus = Literal["succeeded", "repeat_no_change", "failed"]
SUPPORTED_PROMOTION_CLASSES = {"evidence", "observation"}
NON_MUTATING_EFFECTS = {"mapped", "unchanged", "duplicate", "reject", "defer", "quarantine", "unsupported", "unresolved", "projection", "conflict"}

class BlueprintPromotionError(PermissionError):
    """Raised when approved canonical promotion cannot proceed."""

def can_approve_blueprint_promotion(headers: Any, enterprise_id: str) -> bool:
    return _has(headers, enterprise_id, {"candidate.promote", "blueprint_import_admin"})

def can_execute_blueprint_promotion(headers: Any, enterprise_id: str) -> bool:
    return _has(headers, enterprise_id, {"candidate.promote", "blueprint_import_admin"})

def _has(headers: Any, enterprise_id: str, roles: set[str]) -> bool:
    if not authenticated_flora_user(headers): return False
    return can_access_enterprise(headers, enterprise_id) and bool(flora_roles(headers) & roles)

@dataclass(frozen=True)
class CanonicalPromotionApproval:
    schema_version: str
    approval_id: str
    approved_plan_id: str
    import_run_id: str
    package_ref: str
    package_sha256: str
    approver_identity: str
    approval_timestamp: str
    approval_rationale: str
    approved_expected_effects: tuple[dict[str, Any], ...]
    approved_expected_mutation_count: int
    unresolved_warnings_accepted: tuple[str, ...]
    expiry_or_invalidation_condition: str
    plan_fingerprint: str
    review_fingerprint: str
    mapping_fingerprint: str
    superseded: bool = False
    def to_dict(self):
        d=asdict(self); d["approved_expected_effects"]=list(self.approved_expected_effects); d["unresolved_warnings_accepted"]=list(self.unresolved_warnings_accepted); return d

@dataclass(frozen=True)
class CanonicalPromotionResult:
    schema_version: str
    promotion_execution_id: str
    approved_plan_id: str
    approval_id: str
    actor: str
    started_at: str
    completed_at: str
    records_created: tuple[str, ...] = ()
    records_updated: tuple[str, ...] = ()
    records_mapped: tuple[str, ...] = ()
    records_unchanged: tuple[str, ...] = ()
    records_skipped: tuple[str, ...] = ()
    records_blocked: tuple[str, ...] = ()
    records_failed: tuple[str, ...] = ()
    expected_mutation_count: int = 0
    actual_mutation_count: int = 0
    rollback_or_compensation_result: str = "not_required"
    final_execution_status: PromotionStatus = "succeeded"
    error: str = ""
    def to_dict(self):
        d=asdict(self)
        for k in ("records_created","records_updated","records_mapped","records_unchanged","records_skipped","records_blocked","records_failed"):
            d[k]=list(getattr(self,k))
        return d

class CanonicalPromotionRepository:
    def _approval_dir(self, import_run_id: str): return data_path("blueprint_import", "promotion", "approvals", import_run_id)
    def _execution_dir(self, import_run_id: str): return data_path("blueprint_import", "promotion", "executions", import_run_id)
    def save_approval(self, a: CanonicalPromotionApproval): atomic_write_json(self._approval_dir(a.import_run_id)/f"{a.approval_id}.json", a.to_dict()); return a
    def load_approval(self, import_run_id: str, approval_id: str):
        p=self._approval_dir(import_run_id)/f"{approval_id}.json"
        if not p.exists(): return None
        d=json.loads(p.read_text(encoding="utf-8")); return CanonicalPromotionApproval(**{**d,"approved_expected_effects":tuple(d.get("approved_expected_effects",())),"unresolved_warnings_accepted":tuple(d.get("unresolved_warnings_accepted",()))})
    def save_result(self, import_run_id: str, r: CanonicalPromotionResult): atomic_write_json(self._execution_dir(import_run_id)/f"{r.promotion_execution_id}.json", r.to_dict()); return r
    def successful_for(self, import_run_id: str, plan_id: str, approval_id: str):
        root=self._execution_dir(import_run_id)
        if not root.exists(): return None
        for p in sorted(root.glob("*.json")):
            d=json.loads(p.read_text(encoding="utf-8"))
            if d.get("approved_plan_id")==plan_id and d.get("approval_id")==approval_id and d.get("final_execution_status")=="succeeded":
                return CanonicalPromotionResult(**{**d, **{k:tuple(d.get(k,())) for k in ("records_created","records_updated","records_mapped","records_unchanged","records_skipped","records_blocked","records_failed")}})
        return None

def _fp(obj: Any) -> str: return sha256_bytes(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode())
def _execution_id(plan_id: str, approval_id: str) -> str: return "bpi-promote-"+sha256_bytes(f"{plan_id}\n{approval_id}".encode())[:24]
def _approval_id(plan_id: str, approver: str) -> str: return "bpi-approval-"+sha256_bytes(f"{plan_id}\n{approver}".encode())[:24]

class CanonicalPromotionService:
    def __init__(self, registry=None, staging=None, reviews=None, mappings=None, plans=None, repo=None, ledger=None, evidence_repo=None, observation_repo=None):
        self.registry=registry or BlueprintPackageRegistry(); self.staging=staging or CandidateStagingRepository(); self.reviews=reviews or CandidateReviewRepository(); self.mappings=mappings or ImportMappingRepository(); self.plans=plans or DryRunPlanRepository(); self.repo=repo or CanonicalPromotionRepository(); self.ledger=ledger or BlueprintImportLedger(); self.evidence_repo=evidence_repo or EvidenceRepository(); self.observation_repo=observation_repo or ObservationRepository()
    def approve_plan(self, import_run_id: str, plan_id: str, approver: str, rationale: str, headers: Any, unresolved_warnings_accepted: tuple[str,...]=(), expiry_or_invalidation_condition: str="invalid if plan, package, review decisions or mappings change"):
        plan=self._load_plan(import_run_id, plan_id); package=self.registry.get(plan["package_ref"])
        if not package or not can_approve_blueprint_promotion(headers, package.identity.enterprise_id): raise BlueprintPromotionError("Actor is not authorised to approve Blueprint canonical promotion")
        if any(e["effect_type"]=="conflict" for e in plan["effects"]): raise BlueprintPromotionError("Unresolved blocking conflicts remain")
        a=CanonicalPromotionApproval("1.0", _approval_id(plan_id, approver), plan_id, import_run_id, plan["package_ref"], package.package_sha256, approver, utc_now(), rationale, tuple(plan["effects"]), int(plan["expected_canonical_mutation_count"]), unresolved_warnings_accepted, expiry_or_invalidation_condition, _fp(plan), self._reviews_fingerprint(import_run_id), _fp(self.mappings.list(import_run_id)))
        self.repo.save_approval(a); self.ledger.append("canonical_promotion_approved", a.to_dict()); return a
    def execute_approved_plan(self, import_run_id: str, approval_id: str, actor: str, headers: Any) -> CanonicalPromotionResult:
        a=self.repo.load_approval(import_run_id, approval_id)
        if not a: raise BlueprintPromotionError("Unknown promotion approval")
        plan=self._load_plan(import_run_id, a.approved_plan_id); package=self.registry.get(a.package_ref)
        if not package or not can_execute_blueprint_promotion(headers, package.identity.enterprise_id): raise BlueprintPromotionError("Actor is not authorised to execute Blueprint canonical promotion")
        self._assert_still_valid(a, plan, package.package_sha256)
        prior=self.repo.successful_for(import_run_id, a.approved_plan_id, a.approval_id)
        if prior: return CanonicalPromotionResult(**{**prior.to_dict(),"final_execution_status":"repeat_no_change"})
        started=utc_now(); eid=_execution_id(a.approved_plan_id, a.approval_id); backups=self._backup_paths(); created=[]; updated=[]; mapped=[]; unchanged=[]; skipped=[]; blocked=[]; failed=[]
        try:
            candidates={c["candidate_record_id"]: c for c in self.staging.list_candidates(import_run_id)}; reviews=self.reviews.latest_by_candidate(import_run_id); maps={m["candidate_id"]:m for m in self.mappings.list(import_run_id)}
            for e in (ProposedCanonicalEffect(**x) for x in plan["effects"]):
                c=candidates.get(e.candidate_id); d=reviews.get(e.candidate_id); m=maps.get(e.candidate_id)
                if not c or not d or d.get("decision")!="approve": blocked.append(e.candidate_id); continue
                if e.effect_type in NON_MUTATING_EFFECTS: (mapped if e.effect_type=="mapped" else unchanged if e.effect_type in {"unchanged","duplicate"} else skipped).append(e.candidate_id); continue
                if e.effect_type not in {"create","update"} or e.record_class not in SUPPORTED_PROMOTION_CLASSES: skipped.append(e.candidate_id); continue
                cid=self._promote(e, c, d, m or {}, a, actor)
                (created if e.effect_type=="create" else updated).append(cid)
            actual=len(created)+len(updated)
            if actual != a.approved_expected_mutation_count: raise BlueprintPromotionError(f"Actual mutation count {actual} did not match approved expected count {a.approved_expected_mutation_count}")
            result=CanonicalPromotionResult("1.0", eid, a.approved_plan_id, a.approval_id, actor, started, utc_now(), tuple(created), tuple(updated), tuple(mapped), tuple(unchanged), tuple(skipped), tuple(blocked), tuple(failed), a.approved_expected_mutation_count, actual, "not_required", "succeeded")
        except Exception as exc:
            self._restore_paths(backups); failed=failed or ["promotion"]
            result=CanonicalPromotionResult("1.0", eid, a.approved_plan_id, a.approval_id, actor, started, utc_now(), tuple(created), tuple(updated), tuple(mapped), tuple(unchanged), tuple(skipped), tuple(blocked), tuple(failed), a.approved_expected_mutation_count, len(created)+len(updated), "restored_canonical_file_backups", "failed", str(exc))
            self.repo.save_result(import_run_id,result); self.ledger.append("canonical_promotion_execution_recorded", result.to_dict()); raise BlueprintPromotionError(str(exc)) from exc
        self.repo.save_result(import_run_id,result); self.ledger.append("canonical_promotion_execution_recorded", result.to_dict()); return result
    def _reviews_fingerprint(self, import_run_id: str) -> str:
        root=data_path("blueprint_import", "reviews", import_run_id)
        rows=[]
        if root.exists():
            rows=[json.loads(p.read_text(encoding="utf-8")) for p in sorted(root.glob("*.json"))]
        return _fp(rows)
    def _load_plan(self, import_run_id, plan_id):
        for p in self.plans.list(import_run_id):
            if p.get("plan_id")==plan_id: return p
        raise BlueprintPromotionError("Unknown dry-run plan")
    def _assert_still_valid(self,a,plan,sha):
        if a.superseded or a.package_sha256 != sha or a.plan_fingerprint != _fp(plan) or a.review_fingerprint != self._reviews_fingerprint(a.import_run_id) or a.mapping_fingerprint != _fp(self.mappings.list(a.import_run_id)):
            raise BlueprintPromotionError("Approved plan is no longer valid")
    def _lineage(self,e,c,d,m,a,actor):
        return {"package_id": a.package_ref, "package_version": self.registry.get(a.package_ref).identity.package_version, "package_checksum": a.package_sha256, "import_run_id": a.import_run_id, "candidate_id": e.candidate_id, "review_decision_id": d["review_decision_id"], "mapping_id": m.get("mapping_id",""), "dry_run_plan_id": a.approved_plan_id, "approval_id": a.approval_id, "original_external_id": c["original_source_id"], "source_file": c["source_file"], "source_location": c["source_location"], "source_fingerprint": c["source_fingerprint"], "approving_actor": a.approver_identity, "executing_actor": actor, "promotion_timestamp": utc_now()}
    def _promote(self,e,c,d,m,a,actor):
        lineage=self._lineage(e,c,d,m,a,actor); payload=dict(c.get("payload") or {})
        if e.record_class=="evidence":
            eid=e.canonical_id or m.get("canonical_id") or m.get("proposed_canonical_id") or payload.get("evidence_id") or "EVID-"+sha256_bytes(e.effect_id.encode())[:16].upper(); prior=self.evidence_repo.get(eid)
            row={**payload, "evidence_id": eid, "blueprint_import_lineage": {**lineage, "canonical_id": eid, "prior_canonical_version": prior}}
            return self.evidence_repo.save(row)["evidence_id"]
        if e.record_class=="observation":
            obs=Observation(**{k:v for k,v in payload.items() if k in Observation.__dataclass_fields__}, human_provenance={**payload.get("human_provenance",{}), "blueprint_import_lineage": lineage} if payload.get("provenance_type")=="human-supplied" else payload.get("human_provenance",{}))
            return self.observation_repo.save(obs).observation_id or ""
        raise BlueprintPromotionError("Unsupported canonical class")
    def _backup_paths(self):
        paths=[self.evidence_repo.path, self.observation_repo.path]; b=[]
        for p in paths:
            bp=Path(str(p)+".bpi_backup")
            if p.exists(): ensure_writable_dir(bp.parent); shutil.copy2(p,bp); b.append((p,bp,True))
            else: b.append((p,bp,False))
        return b
    def _restore_paths(self, backups):
        for p,bp,existed in backups:
            if existed and bp.exists(): shutil.copy2(bp,p); bp.unlink(missing_ok=True)
            elif not existed and p.exists(): p.unlink()
