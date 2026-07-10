from __future__ import annotations

from cios.applications.flora.blueprint_import.views import (
    approve_and_promote,
    decline_promotion,
    history_page,
    import_blueprint_entry_page,
    review_page,
    upload_and_validate_blueprint,
    validation_result_page,
)
from tests.test_flora_blueprint_import_validation import pkg

HEADERS={"X-Flora-User":"alice","X-Flora-Enterprises":"synthetic-enterprise","X-Flora-Roles":"package.upload,package.review,candidate.promote"}
BAD={"X-Flora-User":"mallory","X-Flora-Enterprises":"other","X-Flora-Roles":"canvas.view"}


def test_authorised_upload_validation_history_and_no_git_write(monkeypatch,tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    before=set(tmp_path.rglob("*"))
    html,status,target=upload_and_validate_blueprint({"blueprint_zip":pkg()}, {"blueprint_zip.filename":"synthetic.zip","blueprint_zip.content_type":"application/zip"}, HEADERS)
    assert status == 200
    assert "Validation result" in html and "Checksum" in html and "Accepted" in html
    assert target.startswith("/blueprint-import/bpi-run-")
    assert (tmp_path/"blueprint_import"/"archives").exists()
    assert not any(".git" in str(p) for p in set(tmp_path.rglob("*"))-before)
    hist,hs=history_page(HEADERS)
    assert hs == 200 and "Blueprint import history" in hist and "synthetic-blueprint" in hist
    assert not (tmp_path/"memory"/"evidence.jsonl").exists()
    assert not (tmp_path/"memory"/"observations.jsonl").exists()


def test_upload_security_rejections_and_accessible_entry(monkeypatch,tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    page,status=import_blueprint_entry_page(HEADERS)
    assert status == 200 and "Upload and validate" in page and "type='file'" in page
    denied,ds=import_blueprint_entry_page(BAD)
    assert ds == 403 and "access denied" in denied.lower()
    html,status,_=upload_and_validate_blueprint({"blueprint_zip":b"not zip"}, {"blueprint_zip.filename":"synthetic.zip","blueprint_zip.content_type":"application/zip"}, HEADERS)
    assert status == 400 and "Canonical changes occurred: no" in html
    html,status,_=upload_and_validate_blueprint({"blueprint_zip":pkg()}, {"blueprint_zip.filename":"synthetic.exe","blueprint_zip.content_type":"application/octet-stream"}, HEADERS)
    assert status == 400
    html,status,_=upload_and_validate_blueprint({"blueprint_zip":pkg()}, {"blueprint_zip.filename":"synthetic.zip","blueprint_zip.content_type":"application/zip"}, BAD)
    assert status == 403


def test_validation_review_decline_approval_completion_and_canvas_link(monkeypatch,tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    records=[
        {"external_id":"OBS-1","record_class":"observation","truth_class":"evidence_backed","payload":{"proposed_effect":"unchanged"}},
        {"external_id":"PP-1","record_class":"pain_point","truth_class":"analytical_projection","payload":{}},
        {"external_id":"BAD-1","record_class":"unsupported_kind","truth_class":"unknown","payload":{}},
    ]
    _,status,target=upload_and_validate_blueprint({"blueprint_zip":pkg(records=records)}, {"blueprint_zip.filename":"synthetic.zip","blueprint_zip.content_type":"application/zip"}, HEADERS)
    assert status == 200
    run_id=target.rsplit("/",1)[-1]
    val,vs=validation_result_page(run_id, HEADERS)
    assert vs == 200 and "Quarantined" in val and "Unsupported" in val
    review,rs=review_page(run_id, HEADERS)
    assert rs == 200 and "Review proposed changes" in review and "Approve and update governed Twin" in review and "analytical projections retained outside canonical memory" in review
    declined,ds=decline_promotion(run_id, HEADERS)
    assert ds == 200 and "Promotion declined" in declined and not (tmp_path/"memory"/"observations.jsonl").exists()
    import re
    plan_id=re.search(r"name='plan_id' value='([^']+)'", review).group(1)
    failed,fs=approve_and_promote(run_id,{"plan_id":[plan_id],"confirm_plan":["yes"],"confirm_mutations":["yes"],"rationale":["reviewed"]}, BAD)
    assert fs == 403
    done,ok=approve_and_promote(run_id,{"plan_id":[plan_id],"confirm_plan":["yes"],"confirm_mutations":["yes"],"rationale":["reviewed"]}, HEADERS)
    assert ok == 200 and "Open Enterprise Canvas" in done and "/digital-twins/synthetic-enterprise/canvas" in done
    assert "original ZIP was preserved" in done

OWNER={"X-Flora-User":"rob","X-Flora-Enterprises":"synthetic-enterprise","X-Flora-Roles":"cios_owner"}
READ_ONLY={"X-Flora-User":"reader","X-Flora-Enterprises":"synthetic-enterprise","X-Flora-Roles":"canvas.view"}
UNAUTH={"X-Flora-Enterprises":"synthetic-enterprise","X-Flora-Roles":"cios_owner"}
OTHER_OWNER={"X-Flora-User":"other-owner","X-Flora-Enterprises":"other-enterprise","X-Flora-Roles":"cios_owner"}


def test_owner_can_upload_review_and_import_without_explicit_blueprint_roles(monkeypatch,tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    html,status,target=upload_and_validate_blueprint({"blueprint_zip":pkg(records=[{"external_id":"OBS-OWNER","record_class":"observation","truth_class":"evidence_backed","payload":{"proposed_effect":"unchanged"}}])}, {"blueprint_zip.filename":"synthetic.zip","blueprint_zip.content_type":"application/zip"}, OWNER)
    assert status == 200
    assert "Validation result" in html
    run_id=target.rsplit("/",1)[-1]
    review,rs=review_page(run_id, OWNER)
    assert rs == 200 and "Approve and update governed Twin" in review
    import re
    plan_id=re.search(r"name='plan_id' value='([^']+)'", review).group(1)
    done,ok=approve_and_promote(run_id,{"plan_id":[plan_id],"confirm_plan":["yes"],"confirm_mutations":["yes"],"rationale":["owner reviewed"]}, OWNER)
    assert ok == 200 and "Blueprint import complete" in done
    events=(tmp_path/"blueprint_import"/"audit"/"events.jsonl").read_text()
    assert "package_received" in events and "canonical_promotion_execution_recorded" in events


def test_denied_uploads_have_role_aware_message_audit_and_no_state(monkeypatch,tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    page,status=import_blueprint_entry_page(READ_ONLY)
    assert status == 403
    assert "You do not have permission to import Blueprints in this workspace." in page
    assert "Ask an administrator" not in page
    html,status,_=upload_and_validate_blueprint({"blueprint_zip":pkg()}, {"blueprint_zip.filename":"synthetic.zip","blueprint_zip.content_type":"application/zip"}, READ_ONLY)
    assert status == 403
    assert "Canonical changes occurred: no" in html
    assert not (tmp_path/"memory").exists()
    assert not (tmp_path/"blueprint_import"/"packages").exists()
    assert "package_upload_authorisation_denied" in (tmp_path/"blueprint_import"/"audit"/"events.jsonl").read_text()
    html,status,_=upload_and_validate_blueprint({"blueprint_zip":pkg()}, {"blueprint_zip.filename":"synthetic.zip","blueprint_zip.content_type":"application/zip"}, UNAUTH)
    assert status == 403


def test_denied_upload_screen_shows_live_diagnostics_for_non_owner(monkeypatch,tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    html,status,_=upload_and_validate_blueprint({"blueprint_zip":pkg()}, {"blueprint_zip.filename":"synthetic.zip","blueprint_zip.content_type":"application/zip"}, READ_ONLY)
    assert status == 403
    assert "Signed-in account" in html and "reader" in html
    assert "Active workspace" in html and "synthetic-enterprise" in html
    assert "Owner recognised</th><td>no" in html
    assert "Required Blueprint capability" in html and "package.upload" in html
    assert "Blueprint upload capability resolved</th><td>Failed" in html
    assert "Canonical import committed</th><td>Not started" in html
    assert "Diagnostic reference" in html and "bpi-diag-" in html
    assert "Ask an administrator" not in html
    events=(tmp_path/"blueprint_import"/"audit"/"events.jsonl").read_text()
    assert "request_correlation_id" in events and "denial_reason" in events and "deployment_version" in events


def test_owner_denial_gets_owner_recovery_not_admin(monkeypatch,tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    owner_without_workspace={"X-Flora-User":"rob","X-Flora-Roles":"cios_owner"}
    html,status,_=upload_and_validate_blueprint({"blueprint_zip":pkg()}, {"blueprint_zip.filename":"synthetic.zip","blueprint_zip.content_type":"application/zip"}, owner_without_workspace)
    assert status == 403
    assert "Owner recognised</th><td>yes" in html
    assert "Switch to the owning workspace." in html
    assert "Ask an administrator" not in html
    assert "Canonical changes occurred: no" in html


def test_owner_enterprise_boundary_still_blocks_cross_workspace(monkeypatch,tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    _,status,target=upload_and_validate_blueprint({"blueprint_zip":pkg()}, {"blueprint_zip.filename":"synthetic.zip","blueprint_zip.content_type":"application/zip"}, OWNER)
    assert status == 200
    run_id=target.rsplit("/",1)[-1]
    val,vs=validation_result_page(run_id, OTHER_OWNER)
    assert vs == 403
    review,rs=review_page(run_id, OTHER_OWNER)
    assert rs == 403


def test_owner_cookie_upload_audit_captures_authorisation_decision(monkeypatch,tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    headers={"Cookie":"flora_user=rob; flora_enterprises=synthetic-enterprise; flora_roles=owner%2Ccanvas.view"}
    html,status,target=upload_and_validate_blueprint({"blueprint_zip":pkg()}, {"blueprint_zip.filename":"synthetic.zip","blueprint_zip.content_type":"application/zip"}, headers)
    assert status == 200
    assert "Validation result" in html
    events=(tmp_path/"blueprint_import"/"audit"/"events.jsonl").read_text()
    assert "package_upload_authorisation_allowed" in events
    assert "required_permission" in events and "package.upload" in events
    assert "policy_name" in events and "can_receive_blueprint_package" in events
    assert "effective_permissions" in events and "candidate.promote" in events
    assert target.startswith("/blueprint-import/bpi-run-")
