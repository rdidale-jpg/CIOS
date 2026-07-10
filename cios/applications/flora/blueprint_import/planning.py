"""Dry-run canonical effect planning for reviewed Blueprint candidates."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

from cios.applications.flora.storage import atomic_write_json, data_path

from .archive import sha256_bytes
from .candidates import PROJECTION_ONLY_CLASSES, CandidateStagingRepository

PERSISTABLE_CANONICAL_CLASSES = {"evidence", "observation", "contradiction", "unknown", "entity", "relationship", "human_knowledge"}
SUPPORT_RECORD_CLASSES = {"source", "enterprise_model_candidate"}
from .ledger import BlueprintImportLedger, utc_now
from .mapping import ImportMappingRepository
from .review import CandidateReviewRepository, BlueprintReviewError, can_review_blueprint_candidate
from .registry import BlueprintPackageRegistry
from .atomicity import validate_atomic_statement

EffectType = Literal["create", "update", "unchanged", "mapped", "duplicate", "conflict", "contradiction", "reject", "defer", "quarantine", "unsupported", "unresolved", "projection", "ignored"]

@dataclass(frozen=True)
class ProposedCanonicalEffect:
    effect_id: str
    candidate_id: str
    external_id: str
    record_class: str
    effect_type: EffectType
    canonical_id: str = ""
    reason: str = ""
    expected_mutation_count: int = 0
    actual_mutation_count: int = 0
    conflicts: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self):
        d = asdict(self); d["conflicts"] = list(self.conflicts); return d

@dataclass(frozen=True)
class DryRunCanonicalEffectPlan:
    schema_version: str
    plan_id: str
    package_ref: str
    import_run_id: str
    created_at: str
    effects: tuple[ProposedCanonicalEffect, ...]
    expected_canonical_mutation_count: int
    actual_canonical_mutation_count: int = 0

    def to_dict(self):
        return asdict(self) | {"effects": [e.to_dict() for e in self.effects]}


def effect_id(import_run_id: str, candidate_id: str, effect_type: str) -> str:
    return "bpi-effect-" + sha256_bytes(f"{import_run_id}\n{candidate_id}\n{effect_type}".encode())[:24]

def plan_id(import_run_id: str, decisions_fp: str, mappings_fp: str) -> str:
    return "bpi-plan-" + sha256_bytes(f"{import_run_id}\n{decisions_fp}\n{mappings_fp}".encode())[:24]

class DryRunPlanRepository:
    def _dir(self, import_run_id: str): return data_path("blueprint_import", "plans", import_run_id)
    def save(self, plan: DryRunCanonicalEffectPlan):
        path = self._dir(plan.import_run_id) / f"{plan.plan_id}.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return DryRunCanonicalEffectPlan("1.0", data["plan_id"], data["package_ref"], data["import_run_id"], data["created_at"], tuple(ProposedCanonicalEffect(**e) for e in data["effects"]), data["expected_canonical_mutation_count"], data.get("actual_canonical_mutation_count", 0))
        atomic_write_json(path, plan.to_dict()); return plan
    def list(self, import_run_id: str) -> list[dict[str, Any]]:
        root = self._dir(import_run_id)
        if not root.exists(): return []
        return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(root.glob("*.json"))]

class DryRunPlanningService:
    def __init__(self, registry=None, staging=None, reviews=None, mappings=None, repository=None, ledger=None):
        self.registry=registry or BlueprintPackageRegistry(); self.staging=staging or CandidateStagingRepository(); self.reviews=reviews or CandidateReviewRepository(); self.mappings=mappings or ImportMappingRepository(); self.repository=repository or DryRunPlanRepository(); self.ledger=ledger or BlueprintImportLedger()
    def create_plan(self, import_run_id: str, actor: str, headers: Any) -> DryRunCanonicalEffectPlan:
        candidates = self.staging.list_candidates(import_run_id)
        if not candidates: raise BlueprintReviewError("No staged candidates for import run")
        package = self.registry.get(str(candidates[0]["source_package_ref"]))
        if not package or not can_review_blueprint_candidate(headers, package.identity.enterprise_id):
            raise BlueprintReviewError("Actor is not authorised to run Blueprint dry-run planning")
        decisions = self.reviews.latest_by_candidate(import_run_id)
        mappings = {m["candidate_id"]: m for m in self.mappings.list(import_run_id)}
        effects = tuple(self._effect(c, decisions.get(c["candidate_record_id"]), mappings.get(c["candidate_record_id"])) for c in candidates)
        expected = sum(e.expected_mutation_count for e in effects)
        summary = self.staging.load_summary(import_run_id) or {}
        staging_version = str(summary.get("staging_version") or "staging-v1")
        dfp = sha256_bytes(json.dumps(decisions, sort_keys=True).encode())
        mfp = sha256_bytes(json.dumps(mappings | {"__staging_version__": staging_version}, sort_keys=True).encode())
        plan = DryRunCanonicalEffectPlan("1.0", plan_id(import_run_id, dfp, mfp), package.package_ref, import_run_id, utc_now(), effects, expected, 0)
        saved = self.repository.save(plan)
        self.ledger.append("dry_run_canonical_effect_plan_recorded", saved.to_dict() | {"actor": actor})
        return saved
    def _effect(self, c, d, m):
        cid=c["candidate_record_id"]; rc=c["candidate_object_class"]; ext=c["original_source_id"]
        if rc in PROJECTION_ONLY_CLASSES: typ="projection"; reason="Analytical projection remains non-canonical"
        elif c.get("validation_status") == "ignored": typ="ignored"; reason="Non-intelligence/control row ignored"
        elif c.get("validation_status") == "quarantined":
            typ="quarantine"
            reason=next((str(f.get("message") or f.get("code")) for f in (c.get("validation_findings") or []) if f.get("code") == "quarantined_non_atomic_observation"), "Candidate is quarantined")
        elif c.get("validation_status") == "rejected": typ="reject"; reason="Candidate is rejected by staging validation"
        elif c.get("validation_status") == "accepted" and rc in SUPPORT_RECORD_CLASSES:
            typ="mapped"; reason="Accepted support metadata; retained in import lineage, not a standalone canonical mutation"
        elif not d: typ="unresolved"; reason="No review decision recorded"
        elif rc == "observation" and d.get("decision") == "approve" and str((c.get("payload") or {}).get("proposed_effect") or "create") in {"create", "update"} and ((c.get("payload") or {}).get("atomic_statement") or (c.get("payload") or {}).get("statement") or (c.get("payload") or {}).get("claim") or (c.get("payload") or {}).get("summary")) and not validate_atomic_statement((c.get("payload") or {}).get("atomic_statement") or (c.get("payload") or {}).get("statement") or (c.get("payload") or {}).get("claim") or (c.get("payload") or {}).get("summary")).atomic:
            finding = validate_atomic_statement((c.get("payload") or {}).get("atomic_statement") or (c.get("payload") or {}).get("statement") or (c.get("payload") or {}).get("claim") or (c.get("payload") or {}).get("summary"))
            typ="quarantine"; reason="quarantined_non_atomic_observation: " + finding.reason
        elif d["decision"] == "reject": typ="reject"; reason=d.get("rationale", "")
        elif d["decision"] == "defer": typ="defer"; reason=d.get("rationale", "")
        elif d["decision"] == "quarantine": typ="quarantine"; reason=d.get("rationale", "")
        elif d["decision"] == "unsupported": typ="unsupported"; reason=d.get("rationale", "")
        elif m:
            disp=m["disposition"]
            typ={"map_existing":"mapped","propose_create":"create","propose_update":"update","duplicate":"duplicate","conflict":"conflict","unresolved":"unresolved","reject":"reject","defer":"defer","quarantine":"quarantine","unsupported":"unsupported"}.get(disp,"unresolved")
            reason=m.get("rationale", "") or disp
        else:
            # payload test hook: unchanged/conflict/duplicate/unresolved can be expressed without canonical writes
            proposed=str(c.get("payload",{}).get("proposed_effect") or "create")
            typ=proposed if proposed in EffectType.__args__ else "create"; reason="Approved candidate dry-run proposal"
        mutations = 1 if typ in {"create","update"} and rc in PERSISTABLE_CANONICAL_CLASSES else 0
        canonical_id = (m or {}).get("canonical_id", "") or (m or {}).get("proposed_canonical_id", "")
        conflicts = tuple(c.get("payload",{}).get("conflicts", [])) if isinstance(c.get("payload",{}).get("conflicts", []), list) else ()
        return ProposedCanonicalEffect(effect_id(str(c["import_run_id"]), cid, typ), cid, ext, rc, typ, canonical_id, reason, mutations, 0, conflicts)
