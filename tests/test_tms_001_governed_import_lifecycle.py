from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from cios.applications.flora.blueprint_import import CandidateReviewService, DryRunPlanningService
from cios.applications.flora.blueprint_import.archive import sha256_bytes
from cios.applications.flora.blueprint_import.candidates import CandidateStagingRepository
from cios.applications.flora.blueprint_import.promotion import BlueprintPromotionError, CanonicalPromotionService
from cios.applications.flora.blueprint_import.registry import BlueprintPackageRegistry
from cios.applications.flora.blueprint_import.views import completion_page, upload_and_validate_blueprint


FIXTURE = Path(__file__).parents[1] / "enterprise-knowledge" / "TMS-001_High_Fidelity_Industry_Twin_Upgrade.zip"
HEADERS = {
    "X-Flora-User": "alice",
    "X-Flora-Enterprises": "TMS-001",
    "X-Flora-Active-Workspace": "TMS-001",
    "X-Flora-Roles": "blueprint_import_admin,package.review,candidate.promote",
}


def _canonical_files(root: Path) -> dict[str, bytes]:
    memory = root / "memory"
    return {p.name: p.read_bytes() for p in memory.glob("*.jsonl")} if memory.exists() else {}


def test_repository_tms_package_completes_existing_governed_lifecycle(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    assert FIXTURE.is_file() and FIXTURE.stat().st_size > 0
    content = FIXTURE.read_bytes()
    package_checksum = sha256_bytes(content)

    html, status, target = upload_and_validate_blueprint(
        {"blueprint_zip": content},
        {"blueprint_zip.filename": FIXTURE.name, "blueprint_zip.content_type": "application/zip", "expected_type": "industry"},
        HEADERS,
    )
    assert status == 200 and "Governed Industry Twin Package" in html
    assert "TMS-001 Industry Twin Import" in html
    assert "Safe to review" in html
    assert html.count("data-primary-action='true'") == 1
    assert ">Review proposed changes</a>" in html
    assert "Review</span> <small>(current and recommended)" in html
    assert "Blocked until identity and classification tasks are resolved" in html
    assert "Twin identity and nine Opportunity records require review" in html
    assert "315 resolved · 0 unresolved" in html
    assert "No live Twin changes have been made" in html
    assert "Change summary" in html and "14 quarantined and excluded from promotion" in html
    assert "9 require classification" in html
    assert "40 research, workspace or presentation artefacts retained as lineage" in html
    assert "Technical diagnostics" in html
    assert "research_ready_with_conditions" not in html.split("<details class='card' id='technical-diagnostics'>", 1)[0]
    assert "View current proposed changes" not in html
    run_id = target.rsplit("/", 1)[-1]
    package = next(p for p in BlueprintPackageRegistry().list() if p.import_run_id == run_id)
    archive = tmp_path / package.archive_path
    assert package.identity.enterprise_id == package.identity.package_id == "TMS-001"
    assert package.package_sha256 == package_checksum == sha256_bytes(archive.read_bytes())
    assert package.package_inspection["twin_type"] == "industry"
    assert package.package_inspection["unresolved_references"] == []

    summary = CandidateStagingRepository().load_summary(run_id)
    candidates = CandidateStagingRepository().list_candidates(run_id)
    classes = Counter(c["candidate_object_class"] for c in candidates)
    assert summary["candidate_records_staged"] == 315
    assert summary["records_accepted_into_staging"] == 301
    assert summary["records_quarantined"] == 14
    assert summary["records_rejected"] == 0
    assert classes == {"entity": 59, "fact": 63, "evidence": 56, "relationship": 102,
                       "unknown": 20, "contradiction": 14, "reasoning_lineage": 1}
    assert _canonical_files(tmp_path) == {}

    contradictions = [c for c in candidates if c["candidate_object_class"] == "contradiction"]
    assert all(c["validation_status"] == "quarantined" for c in contradictions)
    assert all(c["validation_findings"][0]["code"] == "structurally_incomplete_contradiction" for c in contradictions)
    fibre = next(c for c in contradictions if c["original_source_id"] == "CON-TEL-FIBRE")
    assert fibre["payload"]["statement"]
    assert fibre["payload"]["evidence_refs"] == ["E-FINAL-002", "E-FINAL-006"]
    assert fibre["payload"]["affected_objects"] == ["OPP-002"]
    assert fibre["payload"]["status"] == "open"
    assert fibre["payload"]["confidence"] == "High"

    entity_ids = {c["original_source_id"] for c in candidates if c["candidate_object_class"] == "entity"}
    for relationship in (c for c in candidates if c["candidate_object_class"] == "relationship"):
        assert relationship["payload"]["source_object_id"] in entity_ids
        assert relationship["payload"]["target_object_id"] in entity_ids

    for candidate in candidates:
        CandidateReviewService().record_decision(
            candidate["candidate_record_id"], "approve" if candidate["validation_status"] == "accepted" else "unsupported",
            "alice", "Reviewed canonical TMS inventory candidate", HEADERS
        )
    plan = DryRunPlanningService().create_plan(run_id, "alice", HEADERS)
    assert len(plan.effects) == len(candidates)
    assert Counter(effect.effect_type for effect in plan.effects) == {"create": 301, "quarantine": 14}
    assert plan.expected_canonical_mutation_count == 301
    assert _canonical_files(tmp_path) == {}

    service = CanonicalPromotionService()
    with pytest.raises(BlueprintPromotionError, match="not authorised"):
        service.approve_plan(run_id, plan.plan_id, "mallory", "", HEADERS | {"X-Flora-User": "mallory", "X-Flora-Roles": "package.review"})
    with pytest.raises(BlueprintPromotionError, match="requires a rationale"):
        service.approve_plan(run_id, plan.plan_id, "alice", "", HEADERS)
    approval = service.approve_plan(run_id, plan.plan_id, "alice", "Authorised promotion after inventory reconciliation", HEADERS)
    result = service.execute_approved_plan(run_id, approval.approval_id, "alice", HEADERS)
    assert result.actual_mutation_count == result.expected_mutation_count == 301
    assert len(result.records_created) == 301

    canonical = _canonical_files(tmp_path)
    for filename in ("entity.jsonl", "fact.jsonl", "evidence.jsonl", "relationship.jsonl", "unknown.jsonl", "reasoning_lineage.jsonl"):
        assert filename in canonical
    assert any(row["canonical_id"] == "IND-TMS-001" for row in map(json.loads, canonical["entity.jsonl"].splitlines()))
    assert any(row["evidence_id"] == "E-FINAL-001" for row in map(json.loads, canonical["evidence.jsonl"].splitlines()))
    assert any(row["canonical_id"] == "UNK-TEL-001" for row in map(json.loads, canonical["unknown.jsonl"].splitlines()))
    assert "contradictions.jsonl" not in canonical
    lineage = next(map(json.loads, canonical["reasoning_lineage.jsonl"].splitlines()))
    assert lineage["reasoning_lineage_id"] == "LINEAGE-TMS-001-HFT"
    assert lineage["chain_model"] == "Source → Evidence → Observation → Strategic Signal → Hypothesis → Commercial Thesis → Recommendation"
    for stage in ("sources", "observations", "strategic_signals", "hypotheses", "commercial_theses", "recommendations"):
        assert lineage[stage]
    assert lineage["strategic_signals"][0]["observation_ids"]
    assert lineage["hypotheses"][0]["strategic_signal_ids"]
    assert lineage["commercial_theses"][0]["hypothesis_ids"]
    assert lineage["recommendations"][0]["commercial_thesis_ids"]
    explore = completion_page(run_id, result.to_dict(), HEADERS)
    assert "Explore promoted Twin" in explore and "Records created</th><td>301" in explore

    classifications = package.package_inspection["artefact_classification"]
    excluded = [row for row in classifications if row["classification"] in {
        "mission or workspace state", "derived decision or presentation output", "release assurance or validation evidence", "unsupported or ambiguous"
    }]
    assert len(excluded) == 40
    assert all("exclude" in row["import_treatment"] or "retain" in row["import_treatment"] for row in excluded)
    assert any("Executive_Intelligence_Brief.md" in row["path"] for row in excluded)
    assert any("Research_Workspace" in row["path"] for row in excluded)

    before_repeat = _canonical_files(tmp_path)
    repeated = service.execute_approved_plan(run_id, approval.approval_id, "alice", HEADERS)
    assert repeated.final_execution_status == "repeat_no_change"
    assert _canonical_files(tmp_path) == before_repeat

    # A separately received corrupt package fails its producer checksum contract
    # and cannot affect the already promoted canonical state.
    corrupt = tmp_path / "corrupt.zip"
    with ZipFile(FIXTURE) as source, ZipFile(corrupt, "w", ZIP_DEFLATED) as target_zip:
        for info in source.infolist():
            data = source.read(info.filename)
            if info.filename.endswith("HFT_Upgrade/Inventories/fact_inventory.json"):
                data += b" "
            target_zip.writestr(info, data)
    failed_html, failed_status, _ = upload_and_validate_blueprint(
        {"blueprint_zip": corrupt.read_bytes()},
        {"blueprint_zip.filename": "TMS-001-corrupt.zip", "blueprint_zip.content_type": "application/zip", "expected_type": "industry"},
        HEADERS,
    )
    assert failed_status == 200 and "Declared byte count does not match" in failed_html
    assert "Declared checksum does not match" in failed_html
    assert _canonical_files(tmp_path) == before_repeat
