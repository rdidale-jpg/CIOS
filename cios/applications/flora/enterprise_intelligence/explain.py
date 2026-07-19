from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field

from .models import stable_hash, now_iso

ROOT = Path(__file__).resolve().parents[4]
DATASET = ROOT / "enterprise-knowledge/banking/flora/semantic-evaluation/Lloyds-Semantic-Evaluation-Dataset.json"
QUESTION = "What has changed at Lloyds Banking Group, and what evidence supports that assessment?"
FOCUS_OBJECT = "Lloyds Banking Group"
BASELINE_COMMIT = "e7dca8e"


class FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class SourcePassage(FrozenModel):
    passage_id: str
    source_id: str
    date: str
    content: str
    coverage_tags: tuple[str, ...]
    authority: str
    freshness: str = "fixed-evaluation-corpus"
    access_state: str = "available"


class ContextEvidence(FrozenModel):
    evidence_id: str
    claim: str
    lineage: tuple[str, ...]
    authority: str
    lloyds_direct: bool
    sector_context: bool = False
    access_state: str = "available"
    freshness: str = "fixed-evaluation-corpus"


class ContextObservation(FrozenModel):
    observation_id: str
    statement: str
    lineage: tuple[str, ...]
    confidence: str


class ContextUnknown(FrozenModel):
    unknown_id: str
    statement: str
    evidence_demand: str
    lineage: tuple[str, ...]


class ContextTension(FrozenModel):
    contradiction_id: str
    interpretation: str
    expected_status: str
    lineage: tuple[str, ...]


class ContextPackage(FrozenModel):
    package_id: str
    focus_object: str
    focus_object_id: str
    approved_question: str
    approved_question_id: str
    retrieval_policy_version: str
    corpus_baseline: str
    evaluation_baseline: str
    baseline_commit: str
    created_at: str
    source_dataset_id: str
    source_dataset_path: str
    authority_note: str
    source_passages: tuple[SourcePassage, ...]
    evidence: tuple[ContextEvidence, ...]
    observations: tuple[ContextObservation, ...]
    unknowns: tuple[ContextUnknown, ...]
    tensions: tuple[ContextTension, ...]
    source_manifest: tuple[dict[str, Any], ...]
    exclusions: tuple[dict[str, str], ...]
    limitations: tuple[str, ...]
    package_hash: str = ""

    def with_hash(self) -> "ContextPackage":
        payload = self.model_dump(exclude={"package_hash"})
        return self.model_copy(update={"package_hash": stable_hash(payload)})


class ChangeAssessment(FrozenModel):
    change_id: str
    what_changed: str
    fact_basis: tuple[str, ...]
    interpretation: str
    observation_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    limits: tuple[str, ...]
    confidence: Literal["low", "medium", "medium-high", "high"]


class BoundedExplanation(FrozenModel):
    explanation_id: str
    context_package_id: str
    context_package_hash: str
    focus_object: str
    question: str
    answer_scope: str
    changes: tuple[ChangeAssessment, ...]
    why_evidence_belongs_together: tuple[str, ...]
    directly_about_lloyds: tuple[str, ...]
    sector_context_only: tuple[str, ...]
    unknowns: tuple[ContextUnknown, ...]
    contradictions_and_competing_interpretations: tuple[ContextTension, ...]
    confidence_limits: tuple[str, ...]
    inspect_next: tuple[str, ...]
    prohibited_outputs: tuple[str, ...]


def _dataset(path: Path = DATASET) -> dict[str, Any]:
    return json.loads(path.read_text())


def assemble_lloyds_context_package(path: Path = DATASET) -> ContextPackage:
    data = _dataset(path)
    source_by_id = {s["source_id"]: s for s in data["source_documents"]}
    passage_by_id = {p["passage_id"]: p for p in data["passages"]}

    def is_direct(lineage: list[str]) -> bool:
        for ref in lineage:
            src = source_by_id.get(ref)
            passage = passage_by_id.get(ref)
            tags = passage.get("coverage_tags", []) if passage else []
            if src and src["source_id"].startswith("SRC-LBG"):
                return True
            if "lloyds_specific" in tags or "material_lloyds_implication" in tags:
                return True
        return False

    source_passages = tuple(
        SourcePassage(
            passage_id=p["passage_id"],
            source_id=p["source_id"],
            date=p["date"],
            content=p["content"],
            coverage_tags=tuple(p.get("coverage_tags", ())),
            authority=source_by_id[p["source_id"]]["authority"],
        )
        for p in sorted(data["passages"], key=lambda p: p["passage_id"])
    )
    evidence = tuple(
        ContextEvidence(
            evidence_id=e["evidence_id"],
            claim=e["claim"],
            lineage=tuple(e["lineage"]),
            authority=e["authority"],
            lloyds_direct=is_direct(e["lineage"]),
            sector_context=any(ref == "SRC-UK-CTP-2026" or ref == "P10" for ref in e["lineage"]),
        )
        for e in sorted(data["derived_evidence"], key=lambda e: e["evidence_id"])
    )
    observations = tuple(ContextObservation(observation_id=o["observation_id"], statement=o["statement"], lineage=tuple(o["lineage"]), confidence=o["confidence"]) for o in sorted(data["observations"], key=lambda o: o["observation_id"]))
    unknowns = tuple(ContextUnknown(unknown_id=u["unknown_id"], statement=u["statement"], evidence_demand=u["evidence_demand"], lineage=tuple(u["lineage"])) for u in sorted(data["unknowns"], key=lambda u: u["unknown_id"]))
    tensions = tuple(ContextTension(contradiction_id=c["contradiction_id"], interpretation=f"{c['proposition_a']} / {c['proposition_b']}", expected_status=c["expected_status"], lineage=tuple(c["lineage"])) for c in sorted(data["candidate_contradictions"], key=lambda c: c["contradiction_id"]))
    source_manifest = tuple({"source_id": s["source_id"], "title": s["title"], "date": s["date"], "authority": s["authority"], "url": s["url"]} for s in data["source_documents"])
    package = ContextPackage(
        package_id="cp-" + stable_hash({"dataset": data["dataset_id"], "question": QUESTION, "baseline": BASELINE_COMMIT})[:16],
        focus_object=FOCUS_OBJECT,
        focus_object_id="BK-ENT-001",
        approved_question=QUESTION,
        approved_question_id="Q-LBG-CHANGE-EXPLAIN-001",
        retrieval_policy_version="flora-increment-2-retrieval-policy-v0.1",
        corpus_baseline=data["dataset_id"],
        evaluation_baseline="lloyds-semantic-evaluation-v1",
        baseline_commit=BASELINE_COMMIT,
        created_at=now_iso(),
        source_dataset_id=data["dataset_id"],
        source_dataset_path=str(path.relative_to(ROOT)),
        authority_note="Runtime explanation is derived only from the immutable semantic evaluation fixture and is not accepted enterprise knowledge.",
        source_passages=source_passages,
        evidence=evidence,
        observations=observations,
        unknowns=unknowns,
        tensions=tensions,
        source_manifest=source_manifest,
        exclusions=(
            {"excluded_id": "P10-as-direct-Lloyds-fact", "reason": "Sector CTP designation is included only as related context through Lloyds Google Cloud usage."},
            {"excluded_id": "recommendations-and-scoring", "reason": "Increment 2 explain is bounded and cannot recommend pursuit or score opportunities."},
        ),
        limitations=(
            "The package is a fixed runtime evaluation view and not canonical Enterprise Knowledge.",
            "Temporal change claims require passage dates or explicit source dates in lineage.",
            "Unknowns and competing interpretations must remain visible in any explanation.",
        ),
    )
    return package.with_hash()


def explain_lloyds_changes(package: ContextPackage | None = None) -> BoundedExplanation:
    package = package or assemble_lloyds_context_package()
    changes = (
        ChangeAssessment(
            change_id="CHG-LBG-001",
            what_changed="Digital scale and mobile current-account opening are now stronger evidence of channel activity and acquisition efficiency.",
            fact_basis=("23.6m digitally active customers", "around 21.5m app users", "around 85% of 2025 current-account openings through the mobile journey"),
            interpretation="This supports a Lloyds digital engagement change, but it does not prove main-bank primacy or challenger displacement.",
            observation_ids=("OBS-LBG-001",), evidence_ids=("EV-LBG-001", "EV-LBG-002"),
            limits=("Salary-flow capture, direct-debit concentration and main-bank status are not evidenced.",), confidence="medium"),
        ChangeAssessment(
            change_id="CHG-LBG-002",
            what_changed="The Lloyds deposit, structural-hedge and NII mechanism has become the strongest evidenced commercial spine.",
            fact_basis=("£246bn Q1 2026 sterling structural hedge balance", "£1.6bn Q1 2026 hedge income versus £1.2bn in Q1 2025", "expected hedge earnings above £7bn in 2026 and above £8bn in 2027"),
            interpretation="The evidence belongs together because the passages connect personal current accounts and stable liabilities to hedge balances and hedge income.",
            observation_ids=("OBS-LBG-002",), evidence_ids=("EV-LBG-003",),
            limits=("Internal allocation of NII/capital between transformation, distributions, buffers and growth remains unknown.",), confidence="medium-high"),
        ChangeAssessment(
            change_id="CHG-LBG-003",
            what_changed="Simplification, cloud and AI activity are more visible, but they carry supplier-control and migration-risk uncertainty.",
            fact_basis=("£1.9bn gross cost savings since 2021", "c.30% gross reduction in run/change technology costs", "Google Cloud Vertex AI use and 15 modelling systems migrated"),
            interpretation="This is transformation evidence, not proof of net productivity benefit; sector CTP evidence is relevant only because Lloyds uses Google Cloud AI services.",
            observation_ids=("OBS-LBG-003",), evidence_ids=("EV-LBG-004", "EV-LBG-006"),
            limits=("Core-system map, workload criticality, outage root causes and migration sequencing are not exposed.",), confidence="medium"),
        ChangeAssessment(
            change_id="CHG-LBG-004",
            what_changed="Halifax-to-Lloyds brand/app migration strengthens a Lloyds-specific simplification candidate while preserving continuity signals.",
            fact_basis=("Halifax customers will start to use the Lloyds app", "accounts will be rebranded over time", "sort codes, account numbers and existing FSCS protection arrangements stay unchanged"),
            interpretation="This is not a contradiction: brand/app presentation can change while some operational identifiers and protections remain stable.",
            observation_ids=(), evidence_ids=("EV-LBG-005",),
            limits=("Customer trust, attrition, confusion and scam-risk outcomes are not proven by the selected passages.",), confidence="medium"),
    )
    return BoundedExplanation(
        explanation_id="explain-" + stable_hash({"package": package.package_hash, "question": package.approved_question})[:16],
        context_package_id=package.package_id, context_package_hash=package.package_hash,
        focus_object=package.focus_object, question=package.approved_question,
        answer_scope="Bounded Lloyds explanation derived only from the Context Package; no recommendations; bounded evidence-only explanation; prohibited capabilities remain absent.",
        changes=changes,
        why_evidence_belongs_together=("Evidence is linked by explicit lineage from source passages to derived evidence and governed observations.", "Lloyds-specific claims are separated from sector context; the Critical Third Party item is related only through Lloyds' Google Cloud usage.", "Unknowns and tensions are retained beside supporting facts rather than hidden."),
        directly_about_lloyds=tuple(e.evidence_id for e in package.evidence if e.lloyds_direct),
        sector_context_only=tuple(e.evidence_id for e in package.evidence if e.sector_context and not e.lloyds_direct),
        unknowns=package.unknowns,
        contradictions_and_competing_interpretations=package.tensions,
        confidence_limits=("Company-reported figures are treated as evidence, not independent validation of outcomes.", "Digital engagement is not equivalent to primary-account primacy.", "Transformation activity can coexist with operational and supplier risk.", "The runtime result is inspectable and transient; it does not mutate governed knowledge."),
        inspect_next=("Comparable Lloyds transaction-flow or primary-bank data.", "Board/investment governance or programme funding evidence.", "Technology estate and resilience evidence below public-report granularity.", "Customer outcome evidence from Halifax/Lloyds brand and app migration."),
        prohibited_outputs=("recommendation", "opportunity_score", "named sponsor assertion", "budget assertion", "causality beyond package lineage"),
    )


def executive_presentation_for_explanation(package: ContextPackage, explanation: BoundedExplanation) -> dict[str, Any]:
    """Return a deterministic non-canonical presentation view for the bounded result."""
    titles_by_change_id = {
        "CHG-LBG-001": "Digital engagement has accelerated",
        "CHG-LBG-002": "Deposit economics have become more commercially significant",
        "CHG-LBG-003": "Technology transformation is visible, but outcome proof remains incomplete",
        "CHG-LBG-004": "Halifax is moving toward a unified Lloyds customer experience",
    }
    unknowns_by_text = {u.statement: u for u in package.unknowns}
    unknowns_by_lineage = {ref: u for u in package.unknowns for ref in u.lineage}
    cards = []
    for change in explanation.changes:
        linked_unknowns = []
        for limit in change.limits:
            match = unknowns_by_text.get(limit) or next((u for u in package.unknowns if limit.rstrip(".") in u.statement or u.statement.rstrip(".") in limit), None)
            if match and match not in linked_unknowns:
                linked_unknowns.append(match)
        for evidence_id in change.evidence_ids:
            evidence = next((e for e in package.evidence if e.evidence_id == evidence_id), None)
            if evidence:
                for ref in evidence.lineage:
                    match = unknowns_by_lineage.get(ref)
                    if match and match not in linked_unknowns:
                        linked_unknowns.append(match)
        next_evidence = tuple(u.evidence_demand for u in linked_unknowns) or tuple(change.limits)
        cards.append({
            "title": titles_by_change_id.get(change.change_id, change.what_changed),
            "change": change,
            "what_changed": change.what_changed,
            "why_it_matters": change.interpretation,
            "what_we_know": change.fact_basis,
            "what_we_do_not_know": change.limits,
            "what_to_learn_next": next_evidence,
            "unknowns": tuple(linked_unknowns),
        })
    return {
        "headline": "What has changed at Lloyds?",
        "introduction": f"{len(explanation.changes)} evidence-supported changes are visible in the governed Lloyds evidence. Each is separated from what remains uncertain.",
        "synthesis": (
            "Lloyds shows stronger evidence of digital engagement and mobile-led acquisition activity, anchored in reported digital customer scale and current-account opening patterns.",
            "The clearest commercial spine is deposit economics: the selected evidence connects current-account liabilities, structural hedge balances and hedge income without claiming how Lloyds will allocate the economics internally.",
            "Technology simplification, cloud and AI activity are visible, but the result remains bounded: cost and migration activity do not by themselves prove net productivity, resilience or supplier-control outcomes.",
            "The Halifax app and brand migration is a concrete Lloyds-specific simplification signal, while operational continuity indicators mean the change should not be read as full operational separation or disruption proof.",
            "Major Unknowns remain material, including primary-account primacy, investment allocation, technology estate detail and customer outcomes from the Halifax migration.",
        ),
        "cards": tuple(cards),
    }


SAFE_UNAVAILABLE_REASONS = {
    "unsupported_focus_object": "This Explain action is only approved for Lloyds Banking Group (BK-ENT-001).",
    "unsupported_question": "This route only supports the approved Increment 2 Lloyds change question.",
    "invalid_context_package": "The Context Package did not pass deterministic validation.",
    "insufficient_substantive_evidence": "There is not enough substantive Lloyds Evidence to answer safely.",
    "insufficient_temporal_baseline": "The package does not contain enough dated source content to support change claims.",
    "invalid_lineage": "One or more claims cannot be traced back to package Evidence and source passages.",
    "bounded_explanation_validation_failed": "The bounded explanation did not pass output validation.",
    "prohibited_output_detected": "The generated output contained prohibited capability language and was not rendered.",
    "source_content_inaccessible": "Required source content is not currently accessible.",
}


def audit_event(event_type: str, package: ContextPackage | None, *, correlation_id: str, route_identifier: str, validator_outcome: str = "not_applicable", failure_reason: str = "") -> dict[str, Any]:
    event = {
        "event_id": "audit-" + stable_hash({"event_type": event_type, "correlation_id": correlation_id, "route": route_identifier})[:16],
        "event_type": event_type,
        "correlation_id": correlation_id,
        "focus_object_id": package.focus_object_id if package else "BK-ENT-001",
        "approved_question_id": package.approved_question_id if package else "Q-LBG-CHANGE-EXPLAIN-001",
        "context_package_id": package.package_id if package else "not_available",
        "context_package_version": "increment-2-context-package-v0.2",
        "context_package_hash": package.package_hash if package else "not_available",
        "retrieval_policy_version": package.retrieval_policy_version if package else "flora-increment-2-retrieval-policy-v0.1",
        "corpus_baseline": package.corpus_baseline if package else "not_available",
        "evaluation_baseline": package.evaluation_baseline if package else "lloyds-semantic-evaluation-v1",
        "worker_or_model_identifier": "deterministic-bounded-explain-worker-v0.2",
        "prompt_version": "not_applicable",
        "execution_timestamp": now_iso(),
        "validator_outcome": validator_outcome,
        "failure_reason": failure_reason,
        "route_identifier": route_identifier,
        "lifecycle_classification": "non_canonical_runtime_audit_event",
    }
    append_runtime_audit_event(event)
    return event


def runtime_audit_log_path() -> Path:
    base = Path(os.environ.get("FLORA_DATA_DIR", str(ROOT / ".flora_runtime")))
    return base / "non_canonical_runtime_audit" / "increment-2-lloyds-explain.jsonl"


def append_runtime_audit_event(event: dict[str, Any]) -> None:
    path = runtime_audit_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def increment2_runtime_path(*, focus_object_id: str = "BK-ENT-001", approved_question_id: str = "Q-LBG-CHANGE-EXPLAIN-001", correlation_id: str | None = None, route_identifier: str = "/flora/object/BK-ENT-001/explain") -> dict[str, Any]:
    correlation_id = correlation_id or "corr-" + uuid4().hex[:12]
    package = None
    events: list[dict[str, Any]] = []
    if focus_object_id != "BK-ENT-001":
        return safe_unavailable_payload("unsupported_focus_object", None, correlation_id, route_identifier, events)
    package = assemble_lloyds_context_package()
    events.append(audit_event("approved_question_validation", package, correlation_id=correlation_id, route_identifier=route_identifier, validator_outcome="pending"))
    if approved_question_id != package.approved_question_id:
        return safe_unavailable_payload("unsupported_question", package, correlation_id, route_identifier, events)
    for event_type in ("context_plan_creation", "governed_retrieval", "exclusions", "context_package_assembly"):
        events.append(audit_event(event_type, package, correlation_id=correlation_id, route_identifier=route_identifier))
    valid_package, package_failures = validate_context_package(package)
    events.append(audit_event("package_validation", package, correlation_id=correlation_id, route_identifier=route_identifier, validator_outcome="pass" if valid_package else "fail", failure_reason="; ".join(package_failures)))
    if not valid_package:
        reason = "invalid_lineage" if any("lineage" in f for f in package_failures) else "invalid_context_package"
        return safe_unavailable_payload(reason, package, correlation_id, route_identifier, events, package_failures)
    if not any(e.lloyds_direct for e in package.evidence):
        return safe_unavailable_payload("insufficient_substantive_evidence", package, correlation_id, route_identifier, events)
    if len({p.date for p in package.source_passages if p.date}) < 2:
        return safe_unavailable_payload("insufficient_temporal_baseline", package, correlation_id, route_identifier, events)
    if any(p.access_state != "available" for p in package.source_passages):
        return safe_unavailable_payload("source_content_inaccessible", package, correlation_id, route_identifier, events)
    events.append(audit_event("package_freezing", package, correlation_id=correlation_id, route_identifier=route_identifier, validator_outcome="pass"))
    explanation = explain_lloyds_changes(package)
    events.append(audit_event("bounded_explain_execution", package, correlation_id=correlation_id, route_identifier=route_identifier))
    valid_explanation, output_failures = validate_bounded_explanation(package, explanation)
    events.append(audit_event("output_validation", package, correlation_id=correlation_id, route_identifier=route_identifier, validator_outcome="pass" if valid_explanation else "fail", failure_reason="; ".join(output_failures)))
    if not valid_explanation:
        reason = "prohibited_output_detected" if any("prohibited" in f for f in output_failures) else "bounded_explanation_validation_failed"
        return safe_unavailable_payload(reason, package, correlation_id, route_identifier, events, output_failures)
    return {"status": "available", "correlation_id": correlation_id, "context_package": package, "explanation": explanation, "audit_events": tuple(events)}


def safe_unavailable_payload(reason_category: str, package: ContextPackage | None, correlation_id: str, route_identifier: str, events: list[dict[str, Any]], failures: tuple[str, ...] = ()) -> dict[str, Any]:
    events.append(audit_event("safe_unavailable_outcome", package, correlation_id=correlation_id, route_identifier=route_identifier, validator_outcome="fail", failure_reason=reason_category))
    return {
        "status": "safe_unavailable",
        "reason_category": reason_category,
        "user_text": SAFE_UNAVAILABLE_REASONS[reason_category],
        "affected_identifier": package.package_id if package else "BK-ENT-001",
        "evidence_required": ("Accessible Lloyds source passages with dates, claim lineage, governed Evidence, Observations, Unknowns and competing interpretations.",),
        "retained_evidence": package.evidence if package else (),
        "context_package": package,
        "failures": failures,
        "correlation_id": correlation_id,
        "audit_events": tuple(events),
    }


def run_increment2_explain(output_path: Path | None = None) -> dict[str, Any]:
    package = assemble_lloyds_context_package()
    explanation = explain_lloyds_changes(package)
    result = {"context_package": package.model_dump(), "explanation": explanation.model_dump()}
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2, sort_keys=True))
    return result


def validate_context_package(package: ContextPackage) -> tuple[bool, tuple[str, ...]]:
    ids = {p.passage_id for p in package.source_passages} | {p.source_id for p in package.source_passages} | {s["source_id"] for s in package.source_manifest}
    ids |= {e.evidence_id for e in package.evidence} | {o.observation_id for o in package.observations} | {u.unknown_id for u in package.unknowns} | {t.contradiction_id for t in package.tensions}
    failures = []
    if package.focus_object_id != "BK-ENT-001": failures.append("unsupported focus object")
    if package.approved_question_id != "Q-LBG-CHANGE-EXPLAIN-001": failures.append("unsupported question")
    for group in (package.evidence, package.observations, package.unknowns, package.tensions):
        for item in group:
            for ref in item.lineage:
                if ref not in ids:
                    failures.append(f"unknown lineage reference: {ref}")
    if not package.source_passages: failures.append("missing substantive source passages")
    if not package.unknowns: failures.append("missing material Unknowns")
    if not package.tensions: failures.append("missing competing interpretations")
    return (not failures, tuple(failures))


def validate_bounded_explanation(package: ContextPackage, explanation: BoundedExplanation) -> tuple[bool, tuple[str, ...]]:
    evidence_ids = {e.evidence_id for e in package.evidence}
    observation_ids = {o.observation_id for o in package.observations}
    failures = []
    if explanation.context_package_hash != package.package_hash: failures.append("package hash mismatch")
    prohibited_claim_rules = {
        "prioritisation advice": ("prioritise ", "make this a priority", "highest priority"),
        "best route language": ("best route", "best path", "optimal route"),
        "benefit or opportunity assertion": ("opportunity to", "will benefit", "revenue upside", "margin upside"),
        "implied sales pursuit": ("pursue ", "sales motion", "go after", "target account"),
        "unsupported accountable-leader attribution": ("target executive", "accountable leader", "named sponsor", "ceo owns", "cfo owns"),
        "broad strategic conclusion": ("enterprise-wide strategy", "proves lloyds strategy", "lloyds must"),
        "confidence beyond evidence": ("certainly", "definitively", "proves causality", "high confidence"),
        "scoring": ("with an opportunity score", "score of", "ranked #"),
    }
    material_text = " ".join(
        [
            explanation.answer_scope,
            *explanation.why_evidence_belongs_together,
            *explanation.confidence_limits,
        ]
        + [c.what_changed + " " + " ".join(c.fact_basis) + " " + c.interpretation + " " + " ".join(c.limits) for c in explanation.changes]
    ).lower()
    for rule_name, phrases in prohibited_claim_rules.items():
        for phrase in phrases:
            if phrase in material_text:
                failures.append(f"prohibited language ({rule_name}): {phrase.strip()}")
    for change in explanation.changes:
        if not change.evidence_ids: failures.append(f"missing evidence support: {change.change_id}")
        if not set(change.evidence_ids) <= evidence_ids: failures.append(f"unknown evidence reference: {change.change_id}")
        if not set(change.observation_ids) <= observation_ids: failures.append(f"unknown observation reference: {change.change_id}")
        supported_refs = set(change.evidence_ids) | set(change.observation_ids)
        if not supported_refs:
            failures.append(f"no package support: {change.change_id}")
        if change.confidence == "high":
            failures.append(f"confidence beyond package support: {change.change_id}")
        if not change.limits: failures.append(f"missing limits: {change.change_id}")
    if not explanation.unknowns: failures.append("omitted Unknowns")
    if not explanation.contradictions_and_competing_interpretations: failures.append("omitted competing interpretations")
    return (not failures, tuple(failures))
