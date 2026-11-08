"""Governed canonical promotion for approved Blueprint dry-run plans."""
from __future__ import annotations

import json, os, shutil
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Literal

from cios.applications.flora.access import authenticated_flora_user, can_access_enterprise, flora_roles
from cios.applications.flora.memory.models import Observation
from cios.applications.flora.blueprint_import.atomicity import validate_atomic_statement, normalise_statement
from cios.applications.flora.live.source_registry import canonical_enterprise_id
from cios.applications.flora.memory.repository import EvidenceRepository, ObservationRepository, ContradictionRepository, EnterpriseModelRepository
from cios.applications.flora.storage import atomic_write_json, atomic_write_bytes, data_path, ensure_writable_dir
from cios.applications.flora.memory.service import ObservationMemoryService, CLAIM_VOCABULARY

from .archive import sha256_bytes
from .candidates import CandidateStagingRepository
from .ledger import BlueprintImportLedger, utc_now
from .mapping import ImportMappingRepository
from .planning import DryRunPlanRepository, ProposedCanonicalEffect
from .registry import BlueprintPackageRegistry
from .review import CandidateReviewRepository

_PROMOTION_LOCK = Lock()

PromotionStatus = Literal["running", "succeeded", "repeat_no_change", "failed"]
SUPPORTED_PROMOTION_CLASSES = {"evidence", "observation", "contradiction", "unknown", "entity", "relationship", "human_knowledge", "fact", "reasoning_lineage"}
SUPPORT_RECORD_CLASSES = {"source", "enterprise_model_candidate"}
NON_MUTATING_EFFECTS = {"mapped", "unchanged", "duplicate", "reject", "defer", "quarantine", "unsupported", "unresolved", "projection", "conflict"}


def _clean(value: Any) -> str:
    return str(value or "").strip()

def _split_refs(value: Any) -> tuple[str, ...]:
    if isinstance(value, (list, tuple)):
        return tuple(dict.fromkeys(_clean(v) for v in value if _clean(v)))
    text = _clean(value)
    if not text:
        return ()
    import re
    return tuple(dict.fromkeys(part.strip() for part in re.split(r"[,;|\t]\s*|\n+", text) if part.strip()))

def _as_confidence(value: Any) -> int:
    if value in (None, ""):
        return 50
    try:
        n = float(value)
    except (TypeError, ValueError):
        labels = {"low": 30, "medium": 60, "high": 85}
        return labels.get(str(value).strip().casefold(), 50)
    return int(round(n * 100)) if 0 <= n <= 1 else int(round(n))

def _first_present(payload: dict[str, Any], keys: tuple[str, ...]) -> tuple[str, str]:
    for key in keys:
        value = _clean(payload.get(key))
        if value:
            return value, key
    return "", ""

def _record_enterprise(payload, package):
    declared=[canonical_enterprise_id(str(payload[key])) for key in ('enterprise_id','canonical_enterprise_id') if payload.get(key)]
    if len(set(declared))>1: raise BlueprintPromotionError("Conflicting canonical Enterprise identifiers")
    return declared[0] if declared else canonical_enterprise_id(package.identity.enterprise_id)

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
    twin_identity_fingerprint: str = ''
    candidate_fingerprint: str = ''
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
    model_projection_status: str = "not_assessed"
    model_projection_results: tuple[dict[str, Any], ...] = ()
    def to_dict(self):
        d=asdict(self)
        d["model_projection_results"]=list(self.model_projection_results)
        for k in ("records_created","records_updated","records_mapped","records_unchanged","records_skipped","records_blocked","records_failed"):
            d[k]=list(getattr(self,k))
        return d



def _plan_reconciles(plan: dict[str, Any]) -> bool:
    effects = plan.get("effects") or []
    account = {"create", "update", "unchanged", "mapped", "duplicate"}
    return all(e.get("effect_type") in account or e.get("effect_type") not in {"create", "update", "unchanged", "mapped", "duplicate"} for e in effects)

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


class CanonicalJsonlRepository:
    """Generic durable JSONL canonical store for Blueprint-owned classes."""
    def __init__(self, record_class: str):
        self.record_class = record_class
        self.path = data_path("memory", f"{record_class}.jsonl")

    def list(self) -> list[dict[str, Any]]:
        if not self.path.exists(): return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def get(self, canonical_id: str) -> dict[str, Any] | None:
        return next((r for r in self.list() if str(r.get("canonical_id")) == str(canonical_id)), None)

    def save(self, row: dict[str, Any]) -> dict[str, Any]:
        if not row.get("canonical_id"): raise ValueError(f"{self.record_class} requires canonical_id")
        rows = self.list()
        for i, existing in enumerate(rows):
            if str(existing.get("canonical_id")) == str(row.get("canonical_id")):
                rows[i] = {**existing, **{k:v for k,v in row.items() if v not in (None, "", [])}}
                self._rewrite(rows); return rows[i]
        ensure_writable_dir(self.path.parent)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"); handle.flush(); os.fsync(handle.fileno())
        return row

    def _rewrite(self, rows):
        from cios.applications.flora.storage import atomic_write_text
        atomic_write_text(self.path, "".join(json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for r in rows))

def _fp(obj: Any) -> str: return sha256_bytes(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode())
def _execution_id(plan_id: str, approval_id: str) -> str: return "bpi-promote-"+sha256_bytes(f"{plan_id}\n{approval_id}".encode())[:24]
def _approval_id(plan_id: str, approver: str) -> str: return "bpi-approval-"+sha256_bytes(f"{plan_id}\n{approver}".encode())[:24]

class CanonicalPromotionService:
    def __init__(self, registry=None, staging=None, reviews=None, mappings=None, plans=None, repo=None, ledger=None, evidence_repo=None, observation_repo=None, model_repo=None):
        self.registry=registry or BlueprintPackageRegistry(); self.staging=staging or CandidateStagingRepository(); self.reviews=reviews or CandidateReviewRepository(); self.mappings=mappings or ImportMappingRepository(); self.plans=plans or DryRunPlanRepository(); self.repo=repo or CanonicalPromotionRepository(); self.ledger=ledger or BlueprintImportLedger(); self.evidence_repo=evidence_repo or EvidenceRepository(); self.observation_repo=observation_repo or ObservationRepository(); self.contradiction_repo=ContradictionRepository(); self.generic_repos={rc: CanonicalJsonlRepository(rc) for rc in ("unknown", "entity", "relationship", "human_knowledge", "fact", "reasoning_lineage")}
        self._industry_flags={}
        self.models=model_repo or EnterpriseModelRepository()
        self.memory=ObservationMemoryService(self.observation_repo,self.models)
    def approve_plan(self, import_run_id: str, plan_id: str, approver: str, rationale: str, headers: Any, unresolved_warnings_accepted: tuple[str,...]=(), expiry_or_invalidation_condition: str="invalid if plan, package, review decisions or mappings change"):
        plan=self._load_plan(import_run_id, plan_id); package=self.registry.get(plan["package_ref"])
        if not package or not can_approve_blueprint_promotion(headers, package.identity.enterprise_id): raise BlueprintPromotionError("Actor is not authorised to approve Blueprint canonical promotion")
        if not str(rationale or "").strip(): raise BlueprintPromotionError("Promotion approval requires a rationale")
        if any(e["effect_type"]=="conflict" for e in plan["effects"]): raise BlueprintPromotionError("Unresolved blocking conflicts remain")
        if not _plan_reconciles(plan): raise BlueprintPromotionError("Accepted canonical candidates do not reconcile with create, update and unchanged effects")
        self._assert_constructor_valid(import_run_id, plan)
        self._assert_target_ownership(import_run_id, plan, headers)
        existing=self.repo.load_approval(import_run_id,_approval_id(plan_id,approver))
        if existing and self.repo.successful_for(import_run_id,plan_id,existing.approval_id):
            self._assert_still_valid(existing,plan,package.package_sha256)
            return existing
        self._validate_evidence_plan(import_run_id,plan,package)
        a=CanonicalPromotionApproval("1.0", _approval_id(plan_id, approver), plan_id, import_run_id, plan["package_ref"], package.package_sha256, approver, utc_now(), rationale, tuple(plan["effects"]), int(plan["expected_canonical_mutation_count"]), unresolved_warnings_accepted, expiry_or_invalidation_condition, _fp(plan), self._reviews_fingerprint(import_run_id), _fp(self.mappings.list(import_run_id)))
        from dataclasses import replace
        from .twin_governance import project_twin_identity
        a=replace(a,twin_identity_fingerprint=_fp(project_twin_identity(package).to_dict()),candidate_fingerprint=_fp(self.staging.list_candidates(import_run_id)))
        self.repo.save_approval(a); self.ledger.append("canonical_promotion_approved", a.to_dict()); return a
    def execute_approved_plan(self, import_run_id: str, approval_id: str, actor: str, headers: Any) -> CanonicalPromotionResult:
        # Serializes importer threads only; file compensation is not a database
        # transaction and requires the existing single-writer operating model.
        if not _PROMOTION_LOCK.acquire(blocking=False):
            raise BlueprintPromotionError("Another canonical promotion is running; retry after it completes")
        try:
            return self._execute_approved_plan(import_run_id, approval_id, actor, headers)
        except BlueprintPromotionError:
            raise
        except Exception as exc:
            raise BlueprintPromotionError("Promotion stopped before completion; inspect execution receipts and recovery backups before retry: "+type(exc).__name__) from exc
        finally:
            _PROMOTION_LOCK.release()

    def _execute_approved_plan(self, import_run_id, approval_id, actor, headers):
        a=self.repo.load_approval(import_run_id, approval_id)
        if not a: raise BlueprintPromotionError("Unknown promotion approval")
        plan=self._load_plan(import_run_id, a.approved_plan_id); package=self.registry.get(a.package_ref)
        if not package or not can_execute_blueprint_promotion(headers, package.identity.enterprise_id):
            raise BlueprintPromotionError("Actor is not authorised to execute Blueprint canonical promotion")
        self._assert_still_valid(a, plan, package.package_sha256)
        self._assert_target_ownership(import_run_id, plan, headers)
        from .twin_governance import project_twin_identity
        if a.twin_identity_fingerprint and a.twin_identity_fingerprint!=_fp(project_twin_identity(package).to_dict()):
            raise BlueprintPromotionError('Governed Twin identity changed after approval')
        candidates={c["candidate_record_id"]:c for c in self.staging.list_candidates(import_run_id)}
        targets={_record_enterprise(candidates[e["candidate_id"]].get("payload") or {},package)
                 for e in plan["effects"] if e["record_class"]=="observation" and e["effect_type"] in {"create","update"}}
        from .lifecycle import ImportLifecycleService,TwinImportLifecycleService
        lifecycle=ImportLifecycleService();releases=TwinImportLifecycleService()
        previous_release=releases.current_release(package)
        paths=self._canonical_paths()+[self.models.path_for(target) for target in targets]+[self.ledger.path,lifecycle.path(import_run_id)]
        if previous_release: paths.append(lifecycle.path(previous_release.import_run_id))
        if any(Path(str(path)+".bpi_backup").exists() for path in paths):
            raise BlueprintPromotionError("Unrecovered promotion backup exists; single-writer recovery review is required before retry")
        eid=_execution_id(a.approved_plan_id,a.approval_id)
        execution_path=self.repo._execution_dir(import_run_id)/f"{eid}.json"
        if execution_path.exists():
            previous=json.loads(execution_path.read_text())
            if previous.get("final_execution_status")=="running" or previous.get("rollback_or_compensation_result")=="recovery_required":
                raise BlueprintPromotionError("Interrupted promotion requires recovery review before retry")
        prior=self.repo.successful_for(import_run_id,a.approved_plan_id,a.approval_id)
        if prior: return CanonicalPromotionResult(**{**prior.to_dict(),"final_execution_status":"repeat_no_change"})
        bindings=self._validate_evidence_plan(import_run_id,plan,package)
        started=utc_now(); backups=self._backup_paths(paths)
        created=[]; updated=[]; mapped=[]; unchanged=[]; skipped=[]; blocked=[]; observations=[]; projections=[]
        self.repo.save_result(import_run_id,CanonicalPromotionResult("1.0",eid,a.approved_plan_id,a.approval_id,actor,started,"",final_execution_status="running"))
        try:
            reviews=self.reviews.latest_by_candidate(import_run_id); maps={m["candidate_id"]:m for m in self.mappings.list(import_run_id)}
            for e in (ProposedCanonicalEffect(**x) for x in plan["effects"]):
                c=candidates.get(e.candidate_id); d=reviews.get(e.candidate_id); m=maps.get(e.candidate_id)
                if not c or not d or d.get("decision")!="approve": blocked.append(e.candidate_id); continue
                if e.effect_type in NON_MUTATING_EFFECTS:
                    if e.record_class=='evidence' and e.effect_type in {'mapped','unchanged','duplicate'}:
                        self._retain_evidence_release(e,c,m or {},a,actor)
                    (mapped if e.effect_type=="mapped" else unchanged if e.effect_type in {"unchanged","duplicate"} else skipped).append(e.candidate_id)
                    continue
                if e.effect_type not in {"create","update"} or e.record_class not in SUPPORTED_PROMOTION_CLASSES:
                    skipped.append(f"{e.record_class}:{e.candidate_id}"); continue
                c,bound=self._bind_candidate_evidence(c,package,bindings)
                if e.record_class=='relationship':
                    from .semantic_twin import canonical_relationship_endpoints
                    endpoints=canonical_relationship_endpoints(c,package,list(candidates.values()),list(maps.values()),reviews,headers)
                    if endpoints['unresolved']: raise BlueprintPromotionError('Canonical graph endpoints became unresolved')
                    c=dict(c,payload=dict(c['payload'],source=endpoints['source'],target=endpoints['target'],
                                         relationship_source=endpoints['source'],relationship_target=endpoints['target']))
                cid=self._promote(e,c,d,m or {},a,actor)
                (created if e.effect_type=="create" else updated).append(cid)
                if e.record_class=="observation": observations.append(cid)
            actual=len(created)+len(updated)
            if actual!=a.approved_expected_mutation_count:
                raise BlueprintPromotionError(f"Actual mutation count {actual} did not match approved expected count {a.approved_expected_mutation_count}")
            # All canonical writes precede projection, so package ordering does
            # not determine whether supporting Evidence can be resolved.
            projections=[self._project_observation(cid) for cid in dict.fromkeys(observations)]
            projection_status='partial' if any(p['status']=='not_projected' for p in projections) else ('complete' if projections else 'not_applicable')
            result=CanonicalPromotionResult("1.0",eid,a.approved_plan_id,a.approval_id,actor,started,utc_now(),
                tuple(created),tuple(updated),tuple(mapped),tuple(unchanged),tuple(skipped),tuple(blocked),(),
                a.approved_expected_mutation_count,actual,"not_required","succeeded",model_projection_status=projection_status,model_projection_results=tuple(projections))
            lifecycle.mark_promoted(import_run_id,actor,actual,eid)
            if previous_release: lifecycle.mark_superseded(previous_release.import_run_id,actor,import_run_id,eid)
            # Receipt and audit errors are promotion errors, not successful
            # reconciliation. Keep these inside the compensated operation.
            self.repo.save_result(import_run_id,result)
            self.ledger.append("canonical_promotion_execution_recorded",result.to_dict())
        except Exception as exc:
            recovery='restored_canonical_and_model_file_backups'
            try: self._restore_paths(backups)
            except OSError: recovery='recovery_required'
            failed=CanonicalPromotionResult("1.0",eid,a.approved_plan_id,a.approval_id,actor,started,utc_now(),
                records_failed=("promotion_or_projection",),expected_mutation_count=a.approved_expected_mutation_count,
                rollback_or_compensation_result=recovery,final_execution_status="failed",error=str(exc),model_projection_status="failed")
            try:
                self.repo.save_result(import_run_id,failed)
                self.ledger.append("canonical_promotion_execution_recorded",failed.to_dict())
            except Exception as receipt_error:
                raise BlueprintPromotionError("Promotion failed; audit persistence failed and recovery review is required") from receipt_error
            if recovery!='recovery_required': self._discard_backups(backups)
            raise BlueprintPromotionError(str(exc)+("; recovery review is required" if recovery=='recovery_required' else "")) from exc
        self._discard_backups(backups)
        return result

    def _validate_evidence_plan(self, import_run_id, plan, package):
        from .review import BlueprintReviewError
        try: return self._evidence_bindings(import_run_id,plan,package)
        except BlueprintReviewError as exc: raise BlueprintPromotionError(str(exc)) from exc

    def _evidence_bindings(self, import_run_id, plan, package):
        from .mapping import (industry_package,governed_source_scope,record_owner,
                              target_fingerprint,content_fingerprint,evidence_is_current)
        candidates={c['candidate_record_id']:c for c in self.staging.list_candidates(import_run_id)}
        from .researcher_profile_adapter import validate_handoff
        handoff_mappings=self.mappings.list(import_run_id)
        handoff_effects={e['candidate_id'] for e in plan['effects'] if e['record_class']=='observation' and e['effect_type'] in {'create','update'}}
        for c in candidates.values():
            if c['candidate_record_id'] not in handoff_effects or not c.get('payload',{}).get('researcher_handoff'): continue
            try: validate_handoff(c,list(candidates.values()),handoff_mappings)
            except ValueError as exc: raise BlueprintPromotionError(str(exc)) from exc
        maps={m['candidate_id']:m for m in self.mappings.list(import_run_id)}
        reviews=self.reviews.latest_by_candidate(import_run_id)
        industrial=industry_package(package)
        self._industry_flags[package.package_ref]=industrial
        if industrial: governed_source_scope(package,record_owner({},package),is_industry=True)
        bindings={}
        for effect in plan['effects']:
            if effect['record_class']!='evidence': continue
            c=candidates[effect['candidate_id']];payload=c.get('payload') or {};m=maps.get(c['candidate_record_id']) or {}
            owner=record_owner(payload,package)
            scope=governed_source_scope(package,owner,is_industry=industrial)
            decision=reviews.get(c['candidate_record_id']) or {}
            eligible=(c.get('validation_status')=='accepted' and decision.get('decision')=='approve'
                      and effect['effect_type'] in {'create','update','mapped','unchanged','duplicate'})
            if effect['effect_type'] in {'unresolved','conflict'}:
                raise BlueprintPromotionError('Unresolved Evidence identity or source collision blocks acceptance')
            target=effect['canonical_id'] or payload.get('evidence_id') or c['original_source_id']
            if eligible:
                prior=self.evidence_repo.get(target)
                if not evidence_is_current(payload):
                    # Enterprise imports already retain explicitly historical
                    # records for comparison. They remain ineligible to model
                    # projection/qualified reasoning under the existing checks.
                    historical=any(str(payload.get(key,'')).casefold() in {'retired','expired','superseded'} for key in ('lifecycle_state','freshness'))
                    rejected=any(str(payload.get(key,'')).casefold() in {'rejected','quarantined','invalid'} for key in ('status','validation_status','acceptance_state'))
                    if industrial or rejected or not historical:
                        raise BlueprintPromotionError('Rejected or inactive Evidence is not eligible for promotion')
                if prior and (record_owner(prior,package)!=owner or (prior.get('governed_source_scope') and prior['governed_source_scope']!=scope)):
                    raise BlueprintPromotionError('Evidence target crosses Enterprise or governed source scope')
                if prior and not evidence_is_current(prior): raise BlueprintPromotionError('Canonical Evidence target is not current accepted support')
                if m.get('source_scope') and m['source_scope']!=scope: raise BlueprintPromotionError('Evidence scope changed; regenerate mappings')
                if m.get('source_content_fingerprint') and m['source_content_fingerprint']!=content_fingerprint(payload):
                    raise BlueprintPromotionError('Source Evidence changed after mapping')
                if m.get('expected_target_fingerprint') and m['expected_target_fingerprint']!=target_fingerprint(prior):
                    raise BlueprintPromotionError('Canonical Evidence changed after review; regenerate mapping')
                if effect['effect_type']=='create' and prior and content_fingerprint(prior)!=content_fingerprint(payload):
                    raise BlueprintPromotionError('Canonical Evidence target already exists with different content; explicit reconciliation mapping required')
                if effect['effect_type'] in {'mapped','unchanged','duplicate','update'} and not prior:
                    raise BlueprintPromotionError('Approved canonical Evidence target does not exist')
            for ref in {str(v) for v in (c['original_source_id'],payload.get('evidence_id'),payload.get('id')) if v}:
                key=(owner,ref)
                binding={'target':target,'eligible':eligible,'source_fingerprint':content_fingerprint(payload)}
                if key in bindings and bindings[key]!=binding: raise BlueprintPromotionError('Ambiguous source Evidence alias in approved plan')
                bindings[key]=binding
        return bindings

    def _bind_candidate_evidence(self, candidate, package, bindings):
        from copy import deepcopy
        from .mapping import record_owner,evidence_is_current,industry_package,governed_source_scope
        owner=record_owner(candidate.get('payload') or {},package);used={};ineligible=[]
        industrial=self._industry_flags.get(package.package_ref)
        if industrial is None: industrial=industry_package(package)
        fields={'supporting_evidence_ids','evidence_refs','evidence_ids','evidence','resolution_evidence_refs','counter_evidence_ids','source_evidence_ids'}
        def bind(ref):
            binding=bindings.get((owner,ref))
            if binding:
                if not binding['eligible']: raise BlueprintPromotionError('Citation points to rejected or unapproved package Evidence: '+ref)
                used[ref]=binding['target'];return binding['target']
            row=self.evidence_repo.get(ref)
            if row and (record_owner(row,package)!=owner or not evidence_is_current(row)
                        or (industrial and row.get('governed_source_scope') and row['governed_source_scope']!=governed_source_scope(package,owner,is_industry=True))):
                if industrial: raise BlueprintPromotionError('Citation points to foreign or inactive canonical Evidence: '+ref)
                ineligible.append(ref)
                # Preserve existing partial Enterprise imports for lineage;
                # model projection/ClaimValidator must reject this support.
            if not row: ineligible.append(ref)
            return ref
        def walk(value,depth=0):
            if isinstance(value,dict):
                output={}
                for key,item in value.items():
                    if key in {'source_payload','blueprint_import_lineage'}:output[key]=item;continue
                    reference=key in fields or (depth==0 and key=='evidence_id' and candidate['candidate_object_class']!='evidence')
                    if reference and isinstance(item,(str,list,tuple)):
                        refs=_split_refs(item);mapped=[bind(ref) for ref in refs]
                        output[key]=mapped[0] if isinstance(item,str) and len(mapped)==1 else mapped
                    elif candidate['candidate_object_class']=='relationship' and depth==0 and key in {'source','target','relationship_source','relationship_target'} and isinstance(item,str):
                        output[key]=bind(item) if (owner,item) in bindings else item
                    elif key=='references' and isinstance(item,list):
                        output[key]=[bind(ref) if isinstance(ref,str) and (owner,ref) in bindings else ref for ref in item]
                    else: output[key]=walk(item,depth+1)
                return output
            if isinstance(value,list):return [walk(item,depth+1) for item in value]
            return value
        result=dict(candidate,payload=walk(deepcopy(candidate.get('payload') or {})),approved_evidence_bindings=used,ineligible_evidence_refs=list(dict.fromkeys(ineligible)))
        return result,used

    def _retain_evidence_release(self, effect, candidate, mapping, approval, actor):
        from .mapping import governed_source_scope,record_owner,content_fingerprint
        package=self.registry.get(approval.package_ref)
        target=effect.canonical_id or mapping.get('canonical_id') or candidate['original_source_id']
        prior=self.evidence_repo.get(target)
        if not prior: raise BlueprintPromotionError('Reused Evidence target is unavailable')
        lineage=self._lineage(effect,candidate,self.reviews.latest_by_candidate(approval.import_run_id)[candidate['candidate_record_id']],mapping,approval,actor)
        releases=list(prior.get('source_release_provenance') or [])
        if not any(row.get('package_checksum')==lineage['package_checksum'] and row.get('original_external_id')==lineage['original_external_id'] for row in releases):
            releases.append(lineage)
            row={**prior,'source_release_provenance':releases,'source_external_id':prior.get('source_external_id') or candidate['original_source_id'],
                 'governed_source_scope':governed_source_scope(package,record_owner(candidate.get('payload') or {},package),is_industry=self._industry_flags.get(package.package_ref)),
                 'source_content_fingerprint':content_fingerprint(candidate.get('payload') or {})}
            self.evidence_repo.save(row)

    def _project_observation(self, canonical_id):
        observation=self.observation_repo.get(canonical_id)
        if observation is None: raise BlueprintPromotionError("Promoted Observation is unavailable for projection")
        result={"observation_id":canonical_id,"enterprise_id":observation.enterprise_id,"affected_attribute":observation.affected_attribute}
        contract=CLAIM_VOCABULARY.get(observation.observation_type)
        if not contract or not observation.affected_attribute.startswith(contract['attribute_prefix']):
            return result|{"status":"not_projected","reason":"Unsupported Observation type or Enterprise Model attribute mapping"}
        for successor in self.observation_repo.list():
            if (successor.supersedes_observation_id==canonical_id and successor.enterprise_id==observation.enterprise_id
                    and successor.affected_attribute==observation.affected_attribute
                    and successor.lifecycle_state in {'accepted','Validated'} and not successor.retired_at
                    and not any(word in successor.freshness.casefold() for word in ('retired','expired','superseded'))):
                try: effective=datetime.fromisoformat(successor.observation_date.replace('Z','+00:00')).date()
                except ValueError: continue
                if effective<=datetime.now(timezone.utc).date():
                    action=self.memory.apply_observation(replace(observation,lifecycle_state='superseded'))
                    return result|{"status":"historical","action":action.action,"reason":"Explicit canonical supersession retained; no old truth reintroduced"}
        if observation.lifecycle_state in {'retired','superseded'} or observation.retired_at or 'expired' in observation.freshness.casefold():
            action=self.memory.apply_observation(observation)
            return result|{"status":"historical","action":action.action,"reason":"Inactive canonical Observation retained for history"}
        if observation.lifecycle_state not in {'accepted','Validated'}:
            return result|{"status":"historical","reason":"Observation is not accepted current support"}
        if not observation.supporting_evidence_ids:
            return result|{"status":"not_projected","reason":"Factual model projection requires supporting Evidence"}
        try: observed=datetime.fromisoformat(observation.observation_date.replace('Z','+00:00')).date()
        except ValueError: return result|{"status":"not_projected","reason":"Observation has no safely mapped observed date"}
        if observed>datetime.now(timezone.utc).date():
            return result|{"status":"historical","reason":"Future Observation is not current model support"}
        for ref in observation.supporting_evidence_ids:
            evidence=self.evidence_repo.get(ref)
            if not evidence:
                return result|{"status":"not_projected","reason":f"Supporting Evidence {ref} is unavailable"}
            owner=canonical_enterprise_id(str(evidence.get('enterprise_id') or evidence.get('canonical_enterprise_id') or evidence.get('organisation') or ''))
            if owner!=observation.enterprise_id:
                return result|{"status":"not_projected","reason":f"Supporting Evidence {ref} has unresolved or different Enterprise ownership"}
            status=str(evidence.get('lifecycle_state') or evidence.get('truth_status') or '').casefold()
            freshness=str(evidence.get('freshness') or evidence.get('evidence_freshness') or '').casefold()
            if status in {'retired','superseded','expired','rejected'} or any(word in freshness for word in ('retired','superseded','expired')):
                return result|{"status":"not_projected","reason":f"Supporting Evidence {ref} is not current accepted support"}
        action=self.memory.apply_observation(observation)
        return result|{"status":"applied","action":action.action}

    def _assert_target_ownership(self, import_run_id, plan, headers):
        package=self.registry.get(plan['package_ref'])
        candidates={c['candidate_record_id']:c for c in self.staging.list_candidates(import_run_id)}
        for raw in plan['effects']:
            e=ProposedCanonicalEffect(**raw)
            if e.effect_type not in {'create','update'} or e.record_class not in SUPPORTED_PROMOTION_CLASSES: continue
            c=candidates[e.candidate_id]; payload=c.get('payload') or {}
            target=_record_enterprise(payload,package)
            if not _has(headers,target,{'candidate.promote','blueprint_import_admin'}):
                raise BlueprintPromotionError("Actor is not authorised for the canonical record's Enterprise")
            if e.record_class=='observation':
                identifier=_clean(payload.get('observation_id')) or e.canonical_id
                prior=self.observation_repo.get(identifier) if identifier else None
            elif e.record_class=='evidence':
                identifier=e.canonical_id or _clean(payload.get('evidence_id')) or c.get('original_source_id')
                prior=self.evidence_repo.get(identifier)
            else:
                key={'unknown':'unknown_id','entity':'entity_id','relationship':'relationship_id','human_knowledge':'human_knowledge_id',
                     'fact':'fact_id','reasoning_lineage':'reasoning_lineage_id','contradiction':'contradiction_id'}[e.record_class]
                identifier=e.canonical_id or payload.get(key) or c.get('original_source_id')
                prior=self.generic_repos[e.record_class].get(identifier) if e.record_class in self.generic_repos else self.contradiction_repo.get(identifier)
            if prior:
                owner=prior.enterprise_id if isinstance(prior,Observation) else prior.get('enterprise_id') or prior.get('canonical_enterprise_id') or prior.get('organisation')
                if not owner and isinstance(prior,dict):
                    lineage=prior.get('blueprint_import_lineage') or {}
                    prior_package=self.registry.get(lineage.get('package_id',''))
                    owner=prior_package.identity.enterprise_id if prior_package else ''
                if canonical_enterprise_id(str(owner or ''))!=target:
                    raise BlueprintPromotionError("Canonical identifier belongs to a different or unresolved Enterprise owner")

    def _reviews_fingerprint(self, import_run_id: str) -> str:
        root=data_path("blueprint_import", "reviews", import_run_id)
        rows=[]
        if root.exists():
            rows=[json.loads(p.read_text(encoding="utf-8")) for p in sorted(root.glob("*.json"))]
        return _fp(rows)
    def _assert_constructor_valid(self, import_run_id: str, plan: dict[str, Any]) -> None:
        candidates={c["candidate_record_id"]: c for c in self.staging.list_candidates(import_run_id)}; reviews=self.reviews.latest_by_candidate(import_run_id); maps={m["candidate_id"]:m for m in self.mappings.list(import_run_id)}
        failures=[]
        dummy=CanonicalPromotionApproval("1.0", "prevalidation", plan["plan_id"], import_run_id, plan["package_ref"], "", "prevalidation", utc_now(), "", tuple(plan["effects"]), int(plan.get("expected_canonical_mutation_count",0)), (), "", "", "", "")
        for raw in plan.get("effects") or []:
            e=ProposedCanonicalEffect(**raw); c=candidates.get(e.candidate_id); d=reviews.get(e.candidate_id); m=maps.get(e.candidate_id, {})
            if e.effect_type not in {"create","update"} or e.record_class not in SUPPORTED_PROMOTION_CLASSES: continue
            if not c or not d or d.get("decision") != "approve": failures.append(f"{e.candidate_id}: approved candidate/review missing"); continue
            try:
                payload=dict(c.get("payload") or {})
                if e.record_class == "observation": self._observation_from_payload(e, c, payload, self._lineage(e,c,d,m,dummy,"prevalidation"), dummy)
                elif e.record_class == "contradiction":
                    if not (payload.get("statement") or payload.get("statement_a") or payload.get("position_a") or payload.get("claim_a")): raise BlueprintPromotionError("contradiction statement missing")
                elif e.record_class == "evidence": pass
                elif e.record_class in self.generic_repos: self._generic_row(e, c, payload, self._lineage(e,c,d,m,dummy,"prevalidation"), {})
            except Exception as exc: failures.append(f"{e.candidate_id} ({c.get('original_source_id')}): {exc}")
        if failures: raise BlueprintPromotionError("Constructor validation failed before approval: " + "; ".join(failures))
    def _load_plan(self, import_run_id, plan_id):
        for p in self.plans.list(import_run_id):
            if p.get("plan_id")==plan_id: return p
        raise BlueprintPromotionError("Unknown dry-run plan")
    def _assert_still_valid(self,a,plan,sha):
        if a.candidate_fingerprint and a.candidate_fingerprint!=_fp(self.staging.list_candidates(a.import_run_id)):
            raise BlueprintPromotionError('Staged candidates changed after approval')
        if a.superseded or a.package_sha256 != sha or a.plan_fingerprint != _fp(plan) or a.review_fingerprint != self._reviews_fingerprint(a.import_run_id) or a.mapping_fingerprint != _fp(self.mappings.list(a.import_run_id)):
            raise BlueprintPromotionError("Approved plan is no longer valid")
    def _lineage(self,e,c,d,m,a,actor):
        return {"package_id": a.package_ref, "package_version": self.registry.get(a.package_ref).identity.package_version, "package_checksum": a.package_sha256, "import_run_id": a.import_run_id, "candidate_id": e.candidate_id, "review_decision_id": d["review_decision_id"], "mapping_id": m.get("mapping_id",""), "dry_run_plan_id": a.approved_plan_id, "approval_id": a.approval_id, "original_external_id": c["original_source_id"], "source_file": c["source_file"], "source_location": c["source_location"], "source_fingerprint": c["source_fingerprint"], "approving_actor": a.approver_identity, "executing_actor": actor, "promotion_timestamp": utc_now(),"evidence_id_bindings":c.get('approved_evidence_bindings',{}),"ineligible_evidence_refs":c.get("ineligible_evidence_refs",[])}
    def _promote(self,e,c,d,m,a,actor):
        lineage=self._lineage(e,c,d,m,a,actor); payload=dict(c.get("payload") or {})
        if e.record_class=="evidence":
            eid=e.canonical_id or m.get("canonical_id") or m.get("proposed_canonical_id") or payload.get("evidence_id") or c.get("original_source_id") or "EVID-"+sha256_bytes(e.effect_id.encode())[:16].upper(); prior=self.evidence_repo.get(eid)
            from .mapping import governed_source_scope,content_fingerprint,record_owner
            package=self.registry.get(a.package_ref)
            row={**payload, "enterprise_id": _record_enterprise(payload,package), "evidence_id": eid, "blueprint_import_lineage": {**lineage, "canonical_id": eid, "prior_canonical_version": prior},
                 'source_external_id':c['original_source_id'],'governed_source_scope':governed_source_scope(package,record_owner(payload,package),is_industry=self._industry_flags.get(package.package_ref)),
                 'source_content_fingerprint':content_fingerprint(payload),
                 'source_release_provenance':[item for item in (prior or {}).get('source_release_provenance',[]) if not (item.get('package_checksum')==a.package_sha256 and item.get('original_external_id')==c['original_source_id'])]+[lineage]}
            return self.evidence_repo.save(row)["evidence_id"]
        if e.record_class=="observation":
            obs = self._observation_from_payload(e, c, payload, lineage, a)
            prior=self.observation_repo.get(obs.observation_id or '')
            if prior and prior.observation_fingerprint!=obs.observation_fingerprint:
                raise BlueprintPromotionError("Observation ID already identifies a different canonical assertion; use a new Observation ID")
            saved=self.observation_repo.save(obs)
            if e.effect_type=='update':
                updates={key:getattr(obs,key) for key in ('lifecycle_state','freshness','retired_at','supersedes_observation_id','contradiction_state','contradicted_by_observation_ids') if key in payload}
                if updates: saved=self.observation_repo.update_lifecycle(saved.observation_id,updates,import_lineage=lineage)
            return saved.observation_id or ""
        if e.record_class=="contradiction":
            cid=e.canonical_id or m.get("canonical_id") or m.get("proposed_canonical_id") or payload.get("contradiction_id") or c["original_source_id"] or "CON-"+sha256_bytes(e.effect_id.encode())[:16].upper()
            prior=self.contradiction_repo.get(cid)
            row={**payload, "contradiction_id": cid, "statement_a": payload.get("statement_a") or payload.get("position_a") or payload.get("claim_a") or payload.get("statement") or "", "statement_b": payload.get("statement_b") or payload.get("position_b") or payload.get("claim_b") or "", "contradiction_class": payload.get("contradiction_class") or payload.get("class") or "summary_assertion", "judgement": payload.get("current_judgement") or payload.get("judgement") or "", "evidence_need": payload.get("evidence_needed") or payload.get("evidence_need") or "", "affected_outputs": payload.get("affected_outputs") or payload.get("affected_objects") or "", "status": payload.get("status") or "open", "blueprint_import_lineage": {**lineage, "canonical_id": cid, "prior_canonical_version": prior}}
            return self.contradiction_repo.save(row)["contradiction_id"]
        if e.record_class in self.generic_repos:
            row = self._generic_row(e, c, payload, lineage, m)
            return self.generic_repos[e.record_class].save(row)["canonical_id"]
        raise BlueprintPromotionError("Unsupported canonical class")

    def _generic_row(self, e, c, payload, lineage, m):
        ids = {"unknown":"unknown_id", "entity":"entity_id", "relationship":"relationship_id", "human_knowledge":"human_knowledge_id", "fact":"fact_id", "reasoning_lineage":"reasoning_lineage_id"}
        key = ids[e.record_class]
        cid = e.canonical_id or m.get("canonical_id") or m.get("proposed_canonical_id") or payload.get(key) or c.get("original_source_id") or f"{e.record_class.upper()}-" + sha256_bytes(e.effect_id.encode())[:16].upper()
        return {**payload, key: cid, "canonical_id": cid, "record_class": e.record_class, "blueprint_import_lineage": {**lineage, "canonical_id": cid, "prior_canonical_version": self.generic_repos[e.record_class].get(cid)}}

    def _observation_from_payload(self, e: ProposedCanonicalEffect, c: dict[str, Any], payload: dict[str, Any], lineage: dict[str, Any], a: CanonicalPromotionApproval) -> Observation:
        package = self.registry.get(a.package_ref)
        enterprise_id = _record_enterprise(payload,package)
        observation_type = _clean(payload.get("observation_type") or payload.get("type") or payload.get("record_type") or payload.get("truth_class") or c.get("truth_class"))
        observation_date, observation_date_source = _first_present(payload, ("event_date", "observation_date", "observed_at", "evidence_date", "collection_date", "last_confirmed", "last_confirmed_date"))
        if not observation_date:
            observation_date = "undated"
            observation_date_source = "canonical-undated"
        collection_date = _clean(payload.get("collection_date") or payload.get("collected_at") or payload.get("source_row_collected_at") or observation_date)
        affected_attribute = _clean(payload.get("affected_attribute") or payload.get("affected_entity_relationship") or payload.get("affected_entity") or payload.get("relationship_id") or payload.get("entity_id"))
        atomic_statement = _clean(payload.get("atomic_statement") or payload.get("statement") or payload.get("claim") or payload.get("summary"))
        missing = []
        if not enterprise_id: missing.append("enterprise_id")
        if not observation_type: missing.append("observation_type")
        if not observation_date: missing.append("observation_date")
        if not collection_date: missing.append("collection_date")
        if not affected_attribute: missing.append("affected_attribute")
        if not atomic_statement: missing.append("atomic_statement")
        supporting = _split_refs(payload.get("supporting_evidence_ids") or payload.get("evidence_ids") or payload.get("evidence_id"))
        provenance = _clean(payload.get("provenance_type") or ("human-supplied" if payload.get("human_supplied") else "evidence-backed"))
        if provenance in {"evidence-backed", "evidence_curated"} and not supporting:
            missing.append("supporting_evidence_ids")
        if missing:
            raise BlueprintPromotionError(f"Observation candidate {e.candidate_id} ({c.get('original_source_id')}) missing required canonical field(s): {', '.join(missing)}")
        atomicity = validate_atomic_statement(atomic_statement)
        if not atomicity.atomic:
            raise BlueprintPromotionError(f"Observation candidate {e.candidate_id} ({c.get('original_source_id')}) failed atomicity: {atomicity.reason}; original={atomic_statement!r}; normalized={normalise_statement(atomic_statement)!r}")
        hp = dict(payload.get("human_provenance") or {})
        hp["blueprint_import_lineage"] = lineage
        hp["source_worksheet"] = payload.get("source_worksheet") or c.get("source_sheet")
        hp["source_row"] = payload.get("source_row") or (c.get("source_location") or {}).get("row")
        hp["observation_payload_lineage"] = {k: payload.get(k) for k in ("prior_state", "current_state", "linked_unknowns", "lineage_resolution", "candidate_downstream_signals") if k in payload}
        hp["observation_date_source"] = observation_date_source
        hp.update({key:payload[key] for key in ('effective_date','effective_period','source_date','scope') if payload.get(key)})
        if payload.get('period'): hp['effective_period']=payload['period']
        observation=Observation(
            enterprise_id=enterprise_id,
            observation_type=observation_type,
            atomic_statement=atomic_statement,
            observation_date=observation_date,
            collection_date=collection_date,
            affected_attribute=affected_attribute,
            confidence=_as_confidence(payload.get("confidence")),
            supporting_evidence_ids=supporting,
            evidence_publication_date=_clean(payload.get("evidence_publication_date") or payload.get("evidence_date")) or None,
            provenance_type=provenance,
            freshness=_clean(payload.get("freshness")) or "current",
            last_confirmed_date=_clean(payload.get("last_confirmed_date") or payload.get("last_confirmed")) or None,
            lifecycle_state=_clean(payload.get("lifecycle_state")) or "accepted",
            importance=int(payload["importance"]) if payload.get("importance") not in (None, "") else None,
            commercial_value=int(payload["commercial_value"]) if payload.get("commercial_value") not in (None, "") else None,
            contradiction_state=_clean(payload.get("contradiction_state")) or "none",
            contradicted_by_observation_ids=_split_refs(payload.get("contradicted_by_observation_ids")),
            supersedes_observation_id=_clean(payload.get("supersedes_observation_id")) or None,
            retired_at=_clean(payload.get("retired_at")) or None,
            human_provenance=hp,
            observation_id=_clean(payload.get("observation_id")) or e.canonical_id or None,
            observation_fingerprint=None,
        )
        if payload.get('observation_fingerprint') and payload['observation_fingerprint']!=observation.observation_fingerprint:
            raise BlueprintPromotionError("Supplied fingerprint does not match the owned canonical Observation identity")
        prior=self.observation_repo.get(observation.observation_id or '')
        if prior and prior.observation_fingerprint!=observation.observation_fingerprint:
            raise BlueprintPromotionError("Observation ID already identifies a different canonical assertion; use a new Observation ID")
        return observation

    def _canonical_paths(self):
        return [self.evidence_repo.path,self.observation_repo.path,self.contradiction_repo.path]+[r.path for r in self.generic_repos.values()]

    def _backup_paths(self, paths):
        backups=[]
        for path in dict.fromkeys(paths):
            backup=Path(str(path)+'.bpi_backup')
            if path.exists():
                ensure_writable_dir(backup.parent); shutil.copy2(path,backup)
            backups.append((path,backup,path.exists()))
        return backups

    def _restore_paths(self, backups):
        for path,backup,existed in backups:
            if existed:
                if not backup.exists(): raise OSError("Promotion recovery backup is unavailable")
                atomic_write_bytes(path,backup.read_bytes())
            elif path.exists(): path.unlink()

    def _discard_backups(self, backups):
        for _,backup,_ in backups: backup.unlink(missing_ok=True)
