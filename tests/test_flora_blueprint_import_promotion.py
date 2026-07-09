from __future__ import annotations

import pytest

from cios.applications.flora.blueprint_import import CandidateReviewService, DryRunPlanningService, ImportMappingService
from cios.applications.flora.blueprint_import.promotion import CanonicalPromotionService, BlueprintPromotionError
from tests.test_flora_blueprint_import_review_planning import stage, HEADERS

PROMOTE_HEADERS={"X-Flora-User":"alice","X-Flora-Enterprises":"synthetic-enterprise","X-Flora-Roles":"package.review,candidate.promote"}
BAD_HEADERS={"X-Flora-User":"mallory","X-Flora-Enterprises":"synthetic-enterprise","X-Flora-Roles":"package.review"}

def _approve_candidate(c):
    return CandidateReviewService().record_decision(c["candidate_record_id"], "approve", "alice", "approved", PROMOTE_HEADERS)

def _plan_with(monkeypatch,tmp_path,records, mappings=()):
    r, cs=stage(monkeypatch,tmp_path,records)
    for c in cs: _approve_candidate(c)
    ms=ImportMappingService()
    by={c["original_source_id"]:c for c in cs}
    for ext, disp, typ, cid in mappings:
        ms.record_mapping(by[ext], disp, "alice", PROMOTE_HEADERS, typ, cid)
    p=DryRunPlanningService().create_plan(r.import_run_id,"alice",PROMOTE_HEADERS)
    return r, cs, p

def test_authorised_plan_approval_and_unauthorised_rejection(monkeypatch,tmp_path):
    r, _, p=_plan_with(monkeypatch,tmp_path,[{"external_id":"EV-1","record_class":"evidence","truth_class":"evidence_backed","payload":{"source_url":"u"}}])
    approval=CanonicalPromotionService().approve_plan(r.import_run_id,p.plan_id,"alice","rationale",PROMOTE_HEADERS, ("warning accepted",))
    assert approval.approved_plan_id == p.plan_id
    with pytest.raises(BlueprintPromotionError):
        CanonicalPromotionService().approve_plan(r.import_run_id,p.plan_id,"mallory","no",BAD_HEADERS)

def test_plan_change_invalidation_after_approval(monkeypatch,tmp_path):
    r, cs, p=_plan_with(monkeypatch,tmp_path,[{"external_id":"EV-1","record_class":"evidence","truth_class":"evidence_backed","payload":{}}])
    approval=CanonicalPromotionService().approve_plan(r.import_run_id,p.plan_id,"alice","ok",PROMOTE_HEADERS)
    CandidateReviewService().record_decision(cs[0]["candidate_record_id"], "defer", "alice", "changed", PROMOTE_HEADERS)
    with pytest.raises(BlueprintPromotionError):
        CanonicalPromotionService().execute_approved_plan(r.import_run_id, approval.approval_id, "alice", PROMOTE_HEADERS)

def test_successful_evidence_create_update_mapping_unchanged_duplicate_and_skips(monkeypatch,tmp_path):
    records=[
        {"external_id":"EV-C","record_class":"evidence","truth_class":"evidence_backed","payload":{"quote":"new"}},
        {"external_id":"EV-U","record_class":"evidence","truth_class":"evidence_backed","payload":{"proposed_effect":"update","quote":"updated"}},
        {"external_id":"SRC","record_class":"source","truth_class":"package_metadata","payload":{}},
        {"external_id":"OBS-UNCH","record_class":"observation","truth_class":"evidence_backed","payload":{"proposed_effect":"unchanged"}},
        {"external_id":"OBS-DUP","record_class":"observation","truth_class":"evidence_backed","payload":{"proposed_effect":"duplicate"}},
        {"external_id":"REJ","record_class":"observation","truth_class":"evidence_backed","payload":{"proposed_effect":"defer"}},
        {"external_id":"PP","record_class":"pain_point","truth_class":"analytical_projection","payload":{}},
    ]
    r, cs, p=_plan_with(monkeypatch,tmp_path,records, [("SRC","map_existing","Source","src-1"),("EV-U","propose_update","Evidence","EVID-existing")])
    approval=CanonicalPromotionService().approve_plan(r.import_run_id,p.plan_id,"alice","ok",PROMOTE_HEADERS)
    result=CanonicalPromotionService().execute_approved_plan(r.import_run_id, approval.approval_id, "alice", PROMOTE_HEADERS)
    assert result.final_execution_status == "succeeded"
    assert result.actual_mutation_count == result.expected_mutation_count == 2
    assert len(result.records_created) == 1 and result.records_updated == ("EVID-existing",)
    rows=(tmp_path/"memory"/"evidence.jsonl").read_text()
    assert "blueprint_import_lineage" in rows and "approval_id" in rows
    assert "pain_point" not in rows

def test_conflict_blocks_approval_and_unresolved_blocks_execution(monkeypatch,tmp_path):
    r, _, p=_plan_with(monkeypatch,tmp_path,[{"external_id":"EV","record_class":"evidence","truth_class":"evidence_backed","payload":{"conflicts":["diff"]}}], [("EV","conflict","Evidence","EVID-1")])
    with pytest.raises(BlueprintPromotionError):
        CanonicalPromotionService().approve_plan(r.import_run_id,p.plan_id,"alice","ok",PROMOTE_HEADERS)

def test_repeat_execution_idempotency_and_no_duplicate_records(monkeypatch,tmp_path):
    r, _, p=_plan_with(monkeypatch,tmp_path,[{"external_id":"EV-1","record_class":"evidence","truth_class":"evidence_backed","payload":{"quote":"new"}}])
    approval=CanonicalPromotionService().approve_plan(r.import_run_id,p.plan_id,"alice","ok",PROMOTE_HEADERS)
    s=CanonicalPromotionService(); first=s.execute_approved_plan(r.import_run_id, approval.approval_id, "alice", PROMOTE_HEADERS); second=s.execute_approved_plan(r.import_run_id, approval.approval_id, "alice", PROMOTE_HEADERS)
    assert first.final_execution_status == "succeeded"
    assert second.final_execution_status == "repeat_no_change"
    assert len((tmp_path/"memory"/"evidence.jsonl").read_text().splitlines()) == 1

def test_atomic_failure_rolls_back_partial_canonical_state(monkeypatch,tmp_path):
    records=[{"external_id":"EV-1","record_class":"evidence","truth_class":"evidence_backed","payload":{"quote":"ok"}}, {"external_id":"OBS-BAD","record_class":"observation","truth_class":"evidence_backed","payload":{"enterprise_id":"e"}}]
    r, _, p=_plan_with(monkeypatch,tmp_path,records)
    approval=CanonicalPromotionService().approve_plan(r.import_run_id,p.plan_id,"alice","ok",PROMOTE_HEADERS)
    with pytest.raises(BlueprintPromotionError):
        CanonicalPromotionService().execute_approved_plan(r.import_run_id, approval.approval_id, "alice", PROMOTE_HEADERS)
    assert not (tmp_path/"memory"/"evidence.jsonl").exists()
    events=(tmp_path/"blueprint_import"/"audit"/"events.jsonl").read_text()
    assert "canonical_promotion_execution_recorded" in events and "failed" in events

def test_no_enterprise_canvas_or_new_projection_canonical_types(monkeypatch,tmp_path):
    r, _, p=_plan_with(monkeypatch,tmp_path,[{"external_id":"BP","record_class":"burning_platform","truth_class":"analytical_projection","payload":{}},{"external_id":"TP","record_class":"transformation_pressure_view","truth_class":"analytical_projection","payload":{}}])
    approval=CanonicalPromotionService().approve_plan(r.import_run_id,p.plan_id,"alice","ok",PROMOTE_HEADERS)
    res=CanonicalPromotionService().execute_approved_plan(r.import_run_id, approval.approval_id, "alice", PROMOTE_HEADERS)
    assert res.actual_mutation_count == 0
    assert not (tmp_path/"enterprise_canvas").exists()
    assert not (tmp_path/"memory"/"pain_points.jsonl").exists()
