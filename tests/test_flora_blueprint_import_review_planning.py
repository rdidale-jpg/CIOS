from __future__ import annotations

from cios.applications.flora.blueprint_import import CandidateReviewService, DryRunPlanningService, ImportMappingService, BlueprintReviewError
from tests.test_flora_blueprint_import_validation import pkg, receive

HEADERS={"X-Flora-User":"alice","X-Flora-Enterprises":"synthetic-enterprise","X-Flora-Roles":"package.review"}

def stage(monkeypatch,tmp_path,records):
    r=receive(monkeypatch,tmp_path,pkg(records=records))
    from cios.applications.flora.blueprint_import import BlueprintPackageValidator
    BlueprintPackageValidator().validate_and_stage(r.package_ref,"alice")
    return r, BlueprintPackageValidator().staging_summary(r.import_run_id)["candidates"]

def approve(c, **kw):
    return CandidateReviewService().record_decision(c["candidate_record_id"], kw.get("decision","approve"), "alice", kw.get("rationale","ok"), HEADERS, kw.get("mapped", ""))

def test_authorised_and_unauthorised_review_decision_creation(monkeypatch,tmp_path):
    _, cs=stage(monkeypatch,tmp_path,[{"external_id":"OBS-1","record_class":"observation","truth_class":"evidence_backed","payload":{}}])
    d=approve(cs[0], rationale="reviewed")
    assert d.candidate_id == cs[0]["candidate_record_id"]
    try:
        CandidateReviewService().record_decision(cs[0]["candidate_record_id"], "approve", "mallory", "bad", {"X-Flora-User":"mallory","X-Flora-Enterprises":"other","X-Flora-Roles":"package.review"})
        assert False
    except BlueprintReviewError:
        pass

def test_mapping_to_existing_proposed_create_update_unchanged_duplicate_conflict_contradiction_unresolved(monkeypatch,tmp_path):
    records=[
        {"external_id":"SRC-1","record_class":"source","truth_class":"package_metadata","payload":{}},
        {"external_id":"EV-1","record_class":"evidence","truth_class":"evidence_backed","payload":{"proposed_effect":"update"}},
        {"external_id":"OBS-1","record_class":"observation","truth_class":"evidence_backed","payload":{"proposed_effect":"unchanged"}},
        {"external_id":"OBS-2","record_class":"observation","truth_class":"evidence_backed","payload":{}},
        {"external_id":"OBS-3","record_class":"observation","truth_class":"evidence_backed","payload":{"conflicts":["existing differs"]}},
        {"external_id":"CON-1","record_class":"contradiction","truth_class":"human_supplied","payload":{}},
        {"external_id":"UNK-1","record_class":"unknown","truth_class":"unknown","payload":{}},
    ]
    r, cs=stage(monkeypatch,tmp_path,records)
    by={c["original_source_id"]:c for c in cs}
    for c in cs: approve(c)
    ms=ImportMappingService()
    ms.record_mapping(by["SRC-1"], "map_existing", "alice", HEADERS, "Source", "src-123")
    ms.record_mapping(by["OBS-2"], "propose_create", "alice", HEADERS, "Observation")
    ms.record_mapping(by["OBS-3"], "conflict", "alice", HEADERS, "Observation", "obs-3", "existing differs")
    ms.record_mapping(by["UNK-1"], "unresolved", "alice", HEADERS)
    plan=DryRunPlanningService().create_plan(r.import_run_id,"alice",HEADERS)
    effects={e.external_id:e for e in plan.effects}
    assert effects["SRC-1"].effect_type == "mapped"
    assert effects["OBS-2"].effect_type == "create"
    assert effects["EV-1"].effect_type == "update"
    assert effects["OBS-1"].effect_type == "unchanged"
    assert effects["OBS-3"].effect_type == "conflict"
    assert effects["CON-1"].effect_type == "contradiction"
    assert effects["UNK-1"].effect_type == "unresolved"
    assert plan.actual_canonical_mutation_count == 0

def test_rejected_deferred_quarantine_unsupported_and_projection_blocked(monkeypatch,tmp_path):
    records=[
        {"external_id":"R","record_class":"observation","truth_class":"evidence_backed","payload":{}},
        {"external_id":"D","record_class":"observation","truth_class":"evidence_backed","payload":{}},
        {"external_id":"Q","record_class":"observation","truth_class":"evidence_backed","payload":{}},
        {"external_id":"U","record_class":"observation","truth_class":"evidence_backed","payload":{}},
        {"external_id":"PP","record_class":"pain_point","truth_class":"analytical_projection","payload":{}},
    ]
    r, cs=stage(monkeypatch,tmp_path,records); by={c["original_source_id"]:c for c in cs}
    approve(by["R"], decision="reject"); approve(by["D"], decision="defer"); approve(by["Q"], decision="quarantine"); approve(by["U"], decision="unsupported"); approve(by["PP"])
    effects={e.external_id:e for e in DryRunPlanningService().create_plan(r.import_run_id,"alice",HEADERS).effects}
    assert effects["R"].effect_type == "reject"
    assert effects["D"].effect_type == "defer"
    assert effects["Q"].effect_type == "quarantine"
    assert effects["U"].effect_type == "unsupported"
    assert effects["PP"].effect_type == "projection"

def test_idempotent_repeated_dry_runs_deterministic_identities_and_no_canonical_mutation(monkeypatch,tmp_path):
    r, cs=stage(monkeypatch,tmp_path,[{"external_id":"OBS-1","record_class":"observation","truth_class":"evidence_backed","payload":{}}])
    approve(cs[0]); m1=ImportMappingService().record_mapping(cs[0], "propose_create", "alice", HEADERS, "Observation")
    m2=ImportMappingService().record_mapping(cs[0], "propose_create", "alice", HEADERS, "Observation")
    p1=DryRunPlanningService().create_plan(r.import_run_id,"alice",HEADERS); p2=DryRunPlanningService().create_plan(r.import_run_id,"alice",HEADERS)
    assert m1.mapping_id == m2.mapping_id
    assert p1.plan_id == p2.plan_id
    assert len((tmp_path/"blueprint_import"/"plans"/r.import_run_id).glob("*.json").__iter__().__length_hint__() if False else list((tmp_path/"blueprint_import"/"plans"/r.import_run_id).glob("*.json"))) == 1
    assert not (tmp_path/"memory"/"evidence.jsonl").exists()
    assert not (tmp_path/"memory"/"observations.jsonl").exists()
    assert not (tmp_path/"memory"/"enterprise_models").exists()
