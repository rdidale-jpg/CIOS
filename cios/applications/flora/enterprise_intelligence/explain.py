from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field

from .models import stable_hash, now_iso

ROOT = Path(__file__).resolve().parents[4]
DATASET = ROOT / "enterprise-knowledge/banking/flora/semantic-evaluation/Lloyds-Semantic-Evaluation-Dataset.json"
QUESTION = "What has changed at Lloyds Banking Group, and what evidence supports that assessment?"
FOCUS_OBJECT = "Lloyds Banking Group"
BASELINE_COMMIT = "e7dca8e"


class FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ContextEvidence(FrozenModel):
    evidence_id: str
    claim: str
    lineage: tuple[str, ...]
    authority: str
    lloyds_direct: bool
    sector_context: bool = False


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
    approved_question: str
    baseline_commit: str
    created_at: str
    source_dataset_id: str
    source_dataset_path: str
    authority_note: str
    evidence: tuple[ContextEvidence, ...]
    observations: tuple[ContextObservation, ...]
    unknowns: tuple[ContextUnknown, ...]
    tensions: tuple[ContextTension, ...]
    source_manifest: tuple[dict[str, Any], ...]
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

    evidence = tuple(
        ContextEvidence(
            evidence_id=e["evidence_id"],
            claim=e["claim"],
            lineage=tuple(e["lineage"]),
            authority=e["authority"],
            lloyds_direct=is_direct(e["lineage"]),
            sector_context=any(ref == "SRC-UK-CTP-2026" or ref == "P10" for ref in e["lineage"]),
        )
        for e in data["derived_evidence"]
    )
    observations = tuple(ContextObservation(observation_id=o["observation_id"], statement=o["statement"], lineage=tuple(o["lineage"]), confidence=o["confidence"]) for o in data["observations"])
    unknowns = tuple(ContextUnknown(unknown_id=u["unknown_id"], statement=u["statement"], evidence_demand=u["evidence_demand"], lineage=tuple(u["lineage"])) for u in data["unknowns"])
    tensions = tuple(ContextTension(contradiction_id=c["contradiction_id"], interpretation=f"{c['proposition_a']} / {c['proposition_b']}", expected_status=c["expected_status"], lineage=tuple(c["lineage"])) for c in data["candidate_contradictions"])
    source_manifest = tuple({"source_id": s["source_id"], "title": s["title"], "date": s["date"], "authority": s["authority"], "url": s["url"]} for s in data["source_documents"])
    package = ContextPackage(
        package_id="cp-" + stable_hash({"dataset": data["dataset_id"], "question": QUESTION, "baseline": BASELINE_COMMIT})[:16],
        focus_object=FOCUS_OBJECT,
        approved_question=QUESTION,
        baseline_commit=BASELINE_COMMIT,
        created_at=now_iso(),
        source_dataset_id=data["dataset_id"],
        source_dataset_path=str(path.relative_to(ROOT)),
        authority_note="Runtime explanation is derived only from the immutable semantic evaluation fixture and is not accepted enterprise knowledge.",
        evidence=evidence,
        observations=observations,
        unknowns=unknowns,
        tensions=tensions,
        source_manifest=source_manifest,
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
        answer_scope="Bounded Lloyds explanation derived only from the Context Package; no recommendations, opportunity scores, broad strategy, or uncited claims.",
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


def run_increment2_explain(output_path: Path | None = None) -> dict[str, Any]:
    package = assemble_lloyds_context_package()
    explanation = explain_lloyds_changes(package)
    result = {"context_package": package.model_dump(), "explanation": explanation.model_dump()}
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2, sort_keys=True))
    return result
