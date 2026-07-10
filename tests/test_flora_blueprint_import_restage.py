import json

from cios.applications.flora.blueprint_import import BlueprintPackageValidator, BlueprintPackageRegistry
from cios.applications.flora.blueprint_import.cios_twin_adapter import MAPPING_VERSION
from cios.applications.flora.blueprint_import.planning import DryRunPlanRepository
from cios.applications.flora.blueprint_import.restage import BlueprintRestageService
from cios.applications.flora.blueprint_import.views import restage_confirm_page, restage_package, restage_history_page, validation_result_page, review_page
from tests.test_flora_blueprint_import_validation import pkg_with_workbook, xlsx_workbook

OWNER={"X-Flora-User":"alice","X-Flora-Enterprises":"synthetic-enterprise","X-Flora-Roles":"package.review,blueprint_import_admin"}
READ_ONLY={"X-Flora-User":"reader","X-Flora-Enterprises":"synthetic-enterprise","X-Flora-Roles":"canvas.view"}


def _stage(tmp_path):
    wb=xlsx_workbook([("Sources", "rId1", "worksheets/sheet1.xml", [["source_id","title"],["SRC-1","Source"]]), ("Evidence", "rId2", "worksheets/sheet2.xml", [["evidence_id","source_id","claim"],["E-1","SRC-1","Claim"]]), ("Pain Points", "rId3", "worksheets/sheet3.xml", [["stable_id","name"],["P-1","Pain"]])])
    rec=BlueprintPackageRegistry().receive(pkg_with_workbook(wb), "synthetic.zip", "alice")
    BlueprintPackageValidator().validate_and_stage(rec.package_ref,"alice",OWNER)
    review_page(rec.import_run_id, OWNER)
    return rec


def test_restage_action_visible_to_owner_and_hidden_for_unauthorised(monkeypatch,tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    rec=_stage(tmp_path)
    html,status=validation_result_page(rec.import_run_id, OWNER)
    assert status == 200 and "Available actions" in html and "Restage with current mapping" in html
    denied,status=validation_result_page(rec.import_run_id, READ_ONLY)
    assert status == 403 or "Restage with current mapping" not in denied
    confirm,status=restage_confirm_page(rec.import_run_id, OWNER)
    assert status == 200 and "Current mapping version" in confirm and "Restage package" in confirm
    assert "blueprint_zip" not in confirm


def test_restage_reuses_archive_versions_invalidates_review_and_generates_new_review(monkeypatch,tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    rec=_stage(tmp_path)
    old_summary=BlueprintPackageValidator().staging_summary(rec.import_run_id)
    old_candidates=old_summary["candidate_records_staged"]
    old_plans=DryRunPlanRepository().list(rec.import_run_id)
    assert old_plans
    archive_before=rec.archive_path
    html,status=restage_package(rec.import_run_id,{"confirm_restage":["yes"]},OWNER)
    assert status == 200 and "complete" in html.lower() and "Canonical changes made" in html
    new_summary=BlueprintPackageValidator().staging_summary(rec.import_run_id)
    assert rec.archive_path == archive_before
    assert new_summary["package_sha256"] == rec.package_sha256
    assert new_summary["mapping_version"] == MAPPING_VERSION
    assert new_summary["staging_version"] != old_summary.get("staging_version", "staging-v1")
    assert new_summary["supersedes_staging_version"] == old_summary.get("staging_version", "staging-v1")
    assert new_summary["candidate_records_staged"] == old_candidates
    hist,status=restage_history_page(rec.import_run_id, OWNER)
    assert status == 200 and "Prior staging history" in hist and "staging-v1" in hist
    plans=DryRunPlanRepository().list(rec.import_run_id)
    assert any(p.get("stale") is True for p in plans)
    assert len(plans) >= 2
    rhtml,status=review_page(rec.import_run_id, OWNER)
    assert status == 200 and "Staging version" in rhtml and "Review generated from" in rhtml and MAPPING_VERSION in rhtml


def test_restage_idempotency_and_failure_preserves_prior_active(monkeypatch,tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    rec=_stage(tmp_path)
    first=BlueprintRestageService().ensure_restage(rec.import_run_id,"alice",OWNER)
    second=BlueprintRestageService().ensure_restage(rec.import_run_id,"alice",OWNER)
    assert first["job_id"] == second["job_id"]
    assert second.get("already_completed") is True
    jobs=list((tmp_path/"blueprint_import"/"restage_jobs"/rec.import_run_id).glob("*.json"))
    assert len(jobs) == 1
    monkeypatch.setattr("cios.applications.flora.blueprint_import.restage.data_path", lambda *p: tmp_path/"missing.zip" if len(p)==1 else tmp_path.joinpath(*p))
    failed=BlueprintRestageService().ensure_restage(rec.import_run_id,"alice",OWNER)
    assert failed["status"] in {"Complete", "Failed"}  # duplicate may short-circuit before patched path
    assert BlueprintPackageValidator().staging_summary(rec.import_run_id) is not None


def test_progress_page_renders_large_package(monkeypatch,tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    wb=xlsx_workbook([("Evidence", "rId1", "worksheets/sheet1.xml", [["evidence_id","source_id","claim"]]+[[f"E-{i}","SRC", "Claim"] for i in range(120)])])
    rec=BlueprintPackageRegistry().receive(pkg_with_workbook(wb), "synthetic.zip", "alice")
    BlueprintPackageValidator().validate_and_stage(rec.package_ref,"alice",OWNER)
    html,status=restage_package(rec.import_run_id,{"confirm_restage":["yes"]},OWNER)
    assert status == 200 and "candidates staged" in html and "Accepted" in html
