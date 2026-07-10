"""Governed canonical promotion for approved Blueprint dry-run plans."""
from __future__ import annotations

import json, os, shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

from cios.applications.flora.access import authenticated_flora_user, can_access_enterprise, flora_roles
from cios.applications.flora.memory.models import Observation
from cios.applications.flora.blueprint_import.atomicity import validate_atomic_statement, normalise_statement
from cios.applications.flora.live.source_registry import canonical_enterprise_id
from cios.applications.flora.memory.repository import EvidenceRepository, ObservationRepository, ContradictionRepository
from cios.applications.flora.storage import atomic_write_json, data_path, ensure_writable_dir

from .archive import sha256_bytes
from .candidates import CandidateStagingRepository
from .ledger import BlueprintImportLedger, utc_now
from .mapping import ImportMappingRepository
from .planning import DryRunPlanRepository, ProposedCanonicalEffect
from .registry import BlueprintPackageRegistry
from .review import CandidateReviewRepository

PromotionStatus = Literal["succeeded", "repeat_no_change", "failed"]
SUPPORTED_PROMOTION_CLASSES = {"evidence", "observation", "contradiction", "unknown", "entity", "relationship", "human_knowledge"}
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
    def __init__(self, registry=None, staging=None, reviews=None, mappings=None, plans=None, repo=None, ledger=None, evidence_repo=None, observation_repo=None):
        self.registry=registry or BlueprintPackageRegistry(); self.staging=staging or CandidateStagingRepository(); self.reviews=reviews or CandidateReviewRepository(); self.mappings=mappings or ImportMappingRepository(); self.plans=plans or DryRunPlanRepository(); self.repo=repo or CanonicalPromotionRepository(); self.ledger=ledger or BlueprintImportLedger(); self.evidence_repo=evidence_repo or EvidenceRepository(); self.observation_repo=observation_repo or ObservationRepository(); self.contradiction_repo=ContradictionRepository(); self.generic_repos={rc: CanonicalJsonlRepository(rc) for rc in ("unknown", "entity", "relationship", "human_knowledge")}
    def approve_plan(self, import_run_id: str, plan_id: str, approver: str, rationale: str, headers: Any, unresolved_warnings_accepted: tuple[str,...]=(), expiry_or_invalidation_condition: str="invalid if plan, package, review decisions or mappings change"):
        plan=self._load_plan(import_run_id, plan_id); package=self.registry.get(plan["package_ref"])
        if not package or not can_approve_blueprint_promotion(headers, package.identity.enterprise_id): raise BlueprintPromotionError("Actor is not authorised to approve Blueprint canonical promotion")
        if any(e["effect_type"]=="conflict" for e in plan["effects"]): raise BlueprintPromotionError("Unresolved blocking conflicts remain")
        if not _plan_reconciles(plan): raise BlueprintPromotionError("Accepted canonical candidates do not reconcile with create, update and unchanged effects")
        self._assert_constructor_valid(import_run_id, plan)
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
                if e.effect_type not in {"create","update"} or e.record_class not in SUPPORTED_PROMOTION_CLASSES:
                    skipped.append(f"{e.record_class}:{e.candidate_id}"); continue
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
                    if not (payload.get("statement_a") or payload.get("position_a") or payload.get("claim_a")): raise BlueprintPromotionError("statement_a missing")
                    if not (payload.get("statement_b") or payload.get("position_b") or payload.get("claim_b")): raise BlueprintPromotionError("statement_b missing")
                elif e.record_class == "evidence": pass
                elif e.record_class in self.generic_repos: self._generic_row(e, c, payload, self._lineage(e,c,d,m,dummy,"prevalidation"), {})
            except Exception as exc: failures.append(f"{e.candidate_id} ({c.get('original_source_id')}): {exc}")
        if failures: raise BlueprintPromotionError("Constructor validation failed before approval: " + "; ".join(failures))
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
            obs = self._observation_from_payload(e, c, payload, lineage, a)
            return self.observation_repo.save(obs).observation_id or ""
        if e.record_class=="contradiction":
            cid=e.canonical_id or m.get("canonical_id") or m.get("proposed_canonical_id") or payload.get("contradiction_id") or c["original_source_id"] or "CON-"+sha256_bytes(e.effect_id.encode())[:16].upper()
            prior=self.contradiction_repo.get(cid)
            row={**payload, "contradiction_id": cid, "statement_a": payload.get("statement_a") or payload.get("position_a") or payload.get("claim_a") or "", "statement_b": payload.get("statement_b") or payload.get("position_b") or payload.get("claim_b") or "", "contradiction_class": payload.get("contradiction_class") or payload.get("class") or "", "judgement": payload.get("current_judgement") or payload.get("judgement") or "", "evidence_need": payload.get("evidence_needed") or payload.get("evidence_need") or "", "affected_outputs": payload.get("affected_outputs") or "", "status": payload.get("status") or "open", "blueprint_import_lineage": {**lineage, "canonical_id": cid, "prior_canonical_version": prior}}
            return self.contradiction_repo.save(row)["contradiction_id"]
        if e.record_class in self.generic_repos:
            row = self._generic_row(e, c, payload, lineage, m)
            return self.generic_repos[e.record_class].save(row)["canonical_id"]
        raise BlueprintPromotionError("Unsupported canonical class")

    def _generic_row(self, e, c, payload, lineage, m):
        ids = {"unknown":"unknown_id", "entity":"entity_id", "relationship":"relationship_id", "human_knowledge":"human_knowledge_id"}
        key = ids[e.record_class]
        cid = e.canonical_id or m.get("canonical_id") or m.get("proposed_canonical_id") or payload.get(key) or c.get("original_source_id") or f"{e.record_class.upper()}-" + sha256_bytes(e.effect_id.encode())[:16].upper()
        return {**payload, key: cid, "canonical_id": cid, "record_class": e.record_class, "blueprint_import_lineage": {**lineage, "canonical_id": cid, "prior_canonical_version": self.generic_repos[e.record_class].get(cid)}}

    def _observation_from_payload(self, e: ProposedCanonicalEffect, c: dict[str, Any], payload: dict[str, Any], lineage: dict[str, Any], a: CanonicalPromotionApproval) -> Observation:
        package = self.registry.get(a.package_ref)
        enterprise_id = _clean(payload.get("enterprise_id")) or _clean(getattr(package.identity, "enterprise_id", "") if package else "")
        enterprise_id = canonical_enterprise_id(enterprise_id) or enterprise_id
        observation_type = _clean(payload.get("observation_type") or payload.get("type") or payload.get("record_type") or payload.get("truth_class") or c.get("truth_class"))
        observation_date, observation_date_source = _first_present(payload, ("event_date", "evidence_date", "collection_date", "last_confirmed", "last_confirmed_date", "observation_date", "observed_at"))
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
        return Observation(
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
            observation_fingerprint=_clean(payload.get("observation_fingerprint")) or None,
        )
    def _backup_paths(self):
        paths=[self.evidence_repo.path, self.observation_repo.path, self.contradiction_repo.path] + [r.path for r in self.generic_repos.values()]; b=[]
        for p in paths:
            bp=Path(str(p)+".bpi_backup")
            if p.exists(): ensure_writable_dir(bp.parent); shutil.copy2(p,bp); b.append((p,bp,True))
            else: b.append((p,bp,False))
        return b
    def _restore_paths(self, backups):
        for p,bp,existed in backups:
            if existed and bp.exists(): shutil.copy2(bp,p); bp.unlink(missing_ok=True)
            elif not existed and p.exists(): p.unlink()
