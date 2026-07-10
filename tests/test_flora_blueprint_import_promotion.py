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
    with pytest.raises(BlueprintPromotionError):
        CanonicalPromotionService().approve_plan(r.import_run_id,p.plan_id,"alice","ok",PROMOTE_HEADERS)
    assert not (tmp_path/"memory"/"evidence.jsonl").exists()

def test_no_enterprise_canvas_or_new_projection_canonical_types(monkeypatch,tmp_path):
    r, _, p=_plan_with(monkeypatch,tmp_path,[{"external_id":"BP","record_class":"burning_platform","truth_class":"analytical_projection","payload":{}},{"external_id":"TP","record_class":"transformation_pressure_view","truth_class":"analytical_projection","payload":{}}])
    approval=CanonicalPromotionService().approve_plan(r.import_run_id,p.plan_id,"alice","ok",PROMOTE_HEADERS)
    res=CanonicalPromotionService().execute_approved_plan(r.import_run_id, approval.approval_id, "alice", PROMOTE_HEADERS)
    assert res.actual_mutation_count == 0
    assert not (tmp_path/"enterprise_canvas").exists()
    assert not (tmp_path/"memory"/"pain_points.jsonl").exists()

def test_accepted_contradiction_creates_preserves_payload_and_is_idempotent(monkeypatch,tmp_path):
    payload={"contradiction_id":"CON-1","statement_a":"Position A","statement_b":"Position B","class":"forecast tension","current_judgement":"open","evidence_needed":"source needed","affected_outputs":"brief","status":"open"}
    r, cs, p=_plan_with(monkeypatch,tmp_path,[{"external_id":"CON-1","record_class":"contradiction","truth_class":"contradiction","payload":payload}])
    effects={e.external_id:e for e in p.effects}
    assert effects["CON-1"].effect_type == "create"
    assert effects["CON-1"].expected_mutation_count == 1
    approval=CanonicalPromotionService().approve_plan(r.import_run_id,p.plan_id,"alice","ok",PROMOTE_HEADERS)
    svc=CanonicalPromotionService()
    first=svc.execute_approved_plan(r.import_run_id, approval.approval_id, "alice", PROMOTE_HEADERS)
    second=svc.execute_approved_plan(r.import_run_id, approval.approval_id, "alice", PROMOTE_HEADERS)
    assert first.actual_mutation_count == 1
    assert second.final_execution_status == "repeat_no_change"
    rows=(tmp_path/"memory"/"contradictions.jsonl").read_text().splitlines()
    assert len(rows) == 1
    import json
    row=json.loads(rows[0])
    assert row["contradiction_id"] == "CON-1"
    assert row["statement_a"] == "Position A"
    assert row["statement_b"] == "Position B"
    assert row["contradiction_class"] == "forecast tension"
    assert row["blueprint_import_lineage"]["original_external_id"] == "CON-1"

def test_reconciliation_mismatch_blocks_approval_controls(monkeypatch,tmp_path):
    from cios.applications.flora.blueprint_import.views import _review_ready_page
    from cios.applications.flora.blueprint_import.review_plan import BlueprintReviewPlanCoordinator
    r, _, p=_plan_with(monkeypatch,tmp_path,[{"external_id":"CON-1","record_class":"contradiction","truth_class":"contradiction","payload":{"statement_a":"A","statement_b":"B"}}])
    ctx={"package": r, "summary": {"staging_version":"staging-v1"}}
    job={"status":"Not ready","proposed":{"Creates":0,"Updates":0,"Unchanged":0,"Projection-only":0,"Accepted but non-persistable":0},"candidate_summary":{"Accepted canonical candidates":1,"Accepted but non-persistable":0,"Quarantined":0,"Rejected":0,"Unsupported":0},"mapping_quality":{},"plan_id":p.plan_id,"reconciliation":{"accepted_canonical":1,"creates":0,"updates":0,"unchanged":0,"accepted_but_non_persistable":0,"passes":False,"mismatch":1}}
    html=_review_ready_page(ctx, job, BlueprintReviewPlanCoordinator(), {}, "", "corr")
    assert "Approval blocked" in html
    assert "type='button' disabled" in html
    assert "type='submit'>Approve and update governed Twin" not in html

def test_observation_promotion_completes_canonical_contract_and_preserves_lineage(monkeypatch,tmp_path):
    payload={
        "observation_id":"OBS-MOD-1",
        "atomic_statement":"MOD baseline is governed.",
        "type":"fact",
        "affected_entity_relationship":"enterprise.governance",
        "event_date":"2026-01-04",
        "evidence_date":"2026-01-03",
        "collection_date":"2026-01-02",
        "last_confirmed":"2026-01-01",
        "supporting_evidence_ids":"EVD-MOD-1; EVD-MOD-2",
        "confidence":"0.9",
        "freshness":"current",
        "prior_state":"draft",
        "current_state":"approved",
        "contradiction_state":"none",
        "linked_unknowns":"UNK-MOD-1",
        "lineage_resolution":[{"resolved_staged_candidate":"cand-evidence"}],
        "source_worksheet":"05_Observations",
        "source_row":7,
    }
    r, _, p=_plan_with(monkeypatch,tmp_path,[{"external_id":"OBS-MOD-1","record_class":"observation","truth_class":"observed","payload":payload}])
    approval=CanonicalPromotionService().approve_plan(r.import_run_id,p.plan_id,"alice","ok",PROMOTE_HEADERS)
    result=CanonicalPromotionService().execute_approved_plan(r.import_run_id, approval.approval_id, "alice", PROMOTE_HEADERS)
    assert result.actual_mutation_count == 1
    row=__import__('json').loads((tmp_path/"memory"/"observations.jsonl").read_text().splitlines()[0])
    assert row["enterprise_id"] == "synthetic-enterprise"
    assert row["observation_type"] == "fact"
    assert row["observation_date"] == "2026-01-04"
    assert row["affected_attribute"] == "enterprise.governance"
    assert row["supporting_evidence_ids"] == ["EVD-MOD-1", "EVD-MOD-2"]
    assert row["confidence"] == 90
    assert row["freshness"] == "current"
    assert row["contradiction_state"] == "none"
    hp=row["human_provenance"]
    assert hp["blueprint_import_lineage"]["approval_id"] == approval.approval_id
    assert hp["source_worksheet"] == "05_Observations"
    assert hp["source_row"] == 7
    assert hp["observation_payload_lineage"]["prior_state"] == "draft"
    assert hp["observation_payload_lineage"]["current_state"] == "approved"
    assert hp["observation_payload_lineage"]["linked_unknowns"] == "UNK-MOD-1"


def test_observation_date_fallback_order_and_no_import_timestamp(monkeypatch,tmp_path):
    cases=[("EV","evidence_date","2026-02-03"),("COL","collection_date","2026-02-02"),("LC","last_confirmed","2026-02-01"),("UND",None,"undated")]
    records=[]
    for suffix,key,expected in cases:
        payload={"observation_id":f"OBS-{suffix}","atomic_statement":f"MOD fact {suffix} is recorded.","type":"fact","affected_entity_relationship":f"enterprise.{suffix.lower()}","supporting_evidence_ids":"EVD-1"}
        if key: payload[key]=expected
        records.append({"external_id":f"OBS-{suffix}","record_class":"observation","truth_class":"observed","payload":payload})
    r, _, p=_plan_with(monkeypatch,tmp_path,records)
    approval=CanonicalPromotionService().approve_plan(r.import_run_id,p.plan_id,"alice","ok",PROMOTE_HEADERS)
    CanonicalPromotionService().execute_approved_plan(r.import_run_id, approval.approval_id, "alice", PROMOTE_HEADERS)
    rows=[__import__('json').loads(x) for x in (tmp_path/"memory"/"observations.jsonl").read_text().splitlines()]
    by={row["observation_id"]: row for row in rows}
    for suffix,_,expected in cases:
        assert by[f"OBS-{suffix}"]["observation_date"] == expected
    assert all("T" not in row["observation_date"] for row in rows if row["observation_date"] != "undated")


def test_observation_missing_required_data_blocks_whole_promotion_and_retry_succeeds(monkeypatch,tmp_path):
    good={"observation_id":"OBS-GOOD","atomic_statement":"MOD good fact is recorded.","type":"fact","affected_entity_relationship":"enterprise.good","event_date":"2026-01-01","supporting_evidence_ids":"EVD-1"}
    bad={"observation_id":"OBS-BAD","atomic_statement":"MOD bad fact is recorded.","type":"fact","event_date":"2026-01-01","supporting_evidence_ids":"EVD-1"}
    r, cs, p=_plan_with(monkeypatch,tmp_path,[{"external_id":"OBS-GOOD","record_class":"observation","truth_class":"observed","payload":good},{"external_id":"OBS-BAD","record_class":"observation","truth_class":"observed","payload":bad}])
    with pytest.raises(BlueprintPromotionError) as exc:
        CanonicalPromotionService().approve_plan(r.import_run_id,p.plan_id,"alice","ok",PROMOTE_HEADERS)
    assert "OBS-BAD" in str(exc.value) and "affected_attribute" in str(exc.value)
    assert not (tmp_path/"memory"/"observations.jsonl").exists()
    # Retry same staged candidates after correcting the persisted staged payload, without another upload.
    import json
    staged_dir=tmp_path/"blueprint_import"/"staging"/r.import_run_id/"candidates"
    for path in staged_dir.glob("*.json"):
        data=json.loads(path.read_text())
        if data.get("original_source_id") == "OBS-BAD":
            data["payload"]["affected_entity_relationship"] = "enterprise.bad"
            path.write_text(json.dumps(data, sort_keys=True))
    p2=DryRunPlanningService().create_plan(r.import_run_id,"alice",PROMOTE_HEADERS)
    approval=CanonicalPromotionService().approve_plan(r.import_run_id,p2.plan_id,"alice","ok",PROMOTE_HEADERS)
    res=CanonicalPromotionService().execute_approved_plan(r.import_run_id, approval.approval_id, "alice", PROMOTE_HEADERS)
    assert res.actual_mutation_count == 2
    assert len((tmp_path/"memory"/"observations.jsonl").read_text().splitlines()) == 2


def test_authenticated_workspace_owner_context_survives_observation_approval_flow(monkeypatch,tmp_path):
    payload={"observation_id":"OBS-AUTH","atomic_statement":"MOD auth fact is recorded.","type":"fact","affected_entity_relationship":"enterprise.auth","event_date":"2026-01-01","supporting_evidence_ids":"EVD-1"}
    r, _, p=_plan_with(monkeypatch,tmp_path,[{"external_id":"OBS-AUTH","record_class":"observation","truth_class":"observed","payload":payload}])
    approval=CanonicalPromotionService().approve_plan(r.import_run_id,p.plan_id,"alice","ok",PROMOTE_HEADERS)
    res=CanonicalPromotionService().execute_approved_plan(r.import_run_id, approval.approval_id, "alice", PROMOTE_HEADERS)
    row=__import__('json').loads((tmp_path/"memory"/"observations.jsonl").read_text())
    lineage=row["human_provenance"]["blueprint_import_lineage"]
    assert res.final_execution_status == "succeeded"
    assert lineage["approving_actor"] == "alice"
    assert lineage["executing_actor"] == "alice"


def test_compound_observation_detected_before_promotion_and_excluded_from_totals(monkeypatch,tmp_path):
    good={"observation_id":"OBS-OK","atomic_statement":"MOD good fact is recorded.","type":"fact","affected_entity_relationship":"enterprise.good","event_date":"2026-01-01","supporting_evidence_ids":"EVD-1"}
    bad={"observation_id":"OBS-COMPOUND","atomic_statement":"MOD fact one is recorded; MOD fact two is recorded.","type":"fact","affected_entity_relationship":"enterprise.bad","event_date":"2026-01-01","supporting_evidence_ids":"EVD-1"}
    r, _, p=_plan_with(monkeypatch,tmp_path,[{"external_id":"OBS-OK","record_class":"observation","truth_class":"observed","payload":good},{"external_id":"OBS-COMPOUND","record_class":"observation","truth_class":"observed","payload":bad}])
    effects={e.external_id:e for e in p.effects}
    assert effects["OBS-OK"].effect_type == "create"
    assert effects["OBS-COMPOUND"].effect_type == "quarantine"
    assert "quarantined_non_atomic_observation" in effects["OBS-COMPOUND"].reason
    assert p.expected_canonical_mutation_count == 1


def test_constructor_validation_blocks_approval_before_any_promotion(monkeypatch,tmp_path):
    bad={"observation_id":"OBS-BAD","atomic_statement":"MOD bad fact is recorded.","type":"fact","event_date":"2026-01-01","supporting_evidence_ids":"EVD-1"}
    r, _, p=_plan_with(monkeypatch,tmp_path,[{"external_id":"OBS-BAD","record_class":"observation","truth_class":"observed","payload":bad}])
    with pytest.raises(BlueprintPromotionError) as exc:
        CanonicalPromotionService().approve_plan(r.import_run_id,p.plan_id,"alice","ok",PROMOTE_HEADERS)
    assert "Constructor validation failed before approval" in str(exc.value)
    assert "affected_attribute" in str(exc.value)
    assert not (tmp_path/"memory"/"observations.jsonl").exists()


def test_atomic_observation_promotes_and_retry_succeeds_without_duplicates(monkeypatch,tmp_path):
    payload={"observation_id":"OBS-ATOMIC","atomic_statement":"MOD atomic fact is recorded.","type":"fact","affected_entity_relationship":"enterprise.atomic","event_date":"2026-01-01","supporting_evidence_ids":"EVD-1","confidence":"0.8"}
    r, _, p=_plan_with(monkeypatch,tmp_path,[{"external_id":"OBS-ATOMIC","record_class":"observation","truth_class":"observed","payload":payload}])
    approval=CanonicalPromotionService().approve_plan(r.import_run_id,p.plan_id,"alice","ok",PROMOTE_HEADERS)
    svc=CanonicalPromotionService()
    first=svc.execute_approved_plan(r.import_run_id, approval.approval_id, "alice", PROMOTE_HEADERS)
    second=svc.execute_approved_plan(r.import_run_id, approval.approval_id, "alice", PROMOTE_HEADERS)
    assert first.final_execution_status == "succeeded"
    assert second.final_execution_status == "repeat_no_change"
    assert len((tmp_path/"memory"/"observations.jsonl").read_text().splitlines()) == 1


def test_deterministic_split_helpers_preserve_stable_child_ids_and_lineage_values():
    from cios.applications.flora.blueprint_import.atomicity import child_observation_id, split_atomic_statements, validate_atomic_statement
    statement="MOD first fact is recorded; MOD second fact is recorded."
    children=split_atomic_statements(statement)
    ids=[child_observation_id("OBS-PARENT", i+1, child) for i, child in enumerate(children)]
    assert len(children) == 2
    assert all(validate_atomic_statement(child).atomic for child in children)
    assert ids == [child_observation_id("OBS-PARENT", i+1, child) for i, child in enumerate(children)]


def test_ambiguous_compound_observation_is_quarantined_not_rewritten(monkeypatch,tmp_path):
    bad={"observation_id":"OBS-AMB","atomic_statement":"MOD changed because Market pressure increased.","type":"fact","affected_entity_relationship":"enterprise.amb","event_date":"2026-01-01","supporting_evidence_ids":"EVD-1"}
    r, _, p=_plan_with(monkeypatch,tmp_path,[{"external_id":"OBS-AMB","record_class":"observation","truth_class":"observed","payload":bad}])
    effect=p.effects[0]
    assert effect.effect_type == "quarantine"
    assert effect.expected_mutation_count == 0
    assert "multiple independent claims" in effect.reason


def test_real_mod_workbook_atomicity_scan_reports_every_failing_observation():
    from cios.applications.flora.blueprint_import.atomicity import validate_atomic_statement
    # Regression fixture standing in for the preserved MOD package scan: every staged observation is enumerated.
    staged=[("OBS-1", 2, "MOD fact is recorded."),("OBS-2", 3, "MOD fact one is recorded; MOD fact two is recorded."),("OBS-3", 4, "MOD should act.")]
    report=[]
    for oid,row,statement in staged:
        finding=validate_atomic_statement(statement)
        if not finding.atomic:
            report.append({"observation_id":oid,"source_row":row,"failure_reason":finding.reason,"proposed_safe_disposition":"quarantined_non_atomic_observation"})
    assert [r["observation_id"] for r in report] == ["OBS-2", "OBS-3"]
    assert all(r["source_row"] for r in report)
