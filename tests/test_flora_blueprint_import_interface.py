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
    assert "Owner recognised</th><td>no" in html
    assert "No active workspace" in html
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


def test_denied_entry_page_renders_when_audit_persistence_fails(monkeypatch, tmp_path, caplog):
    from cios.applications.flora.blueprint_import import ledger
    from cios.applications.flora.storage import PersistenceError

    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))

    def fail_append(self, event_type, payload):
        raise PersistenceError("Flora storage directory is not writable: /var/data/flora/blueprint_import/audit: permission denied")

    monkeypatch.setattr(ledger.BlueprintImportLedger, "append", fail_append)
    caplog.set_level("WARNING")

    html, status = import_blueprint_entry_page(READ_ONLY)

    assert status == 403
    assert "Blueprint import needs attention" in html
    assert "You do not have permission to import Blueprints in this workspace." in html
    assert "Canonical changes occurred: no" in html
    assert "Diagnostic reference" in html and "bpi-diag-" in html
    assert "Blueprint diagnostics could not be persisted." in html
    assert "No canonical changes occurred." in html
    assert not (tmp_path / "memory").exists()
    assert not (tmp_path / "blueprint_import" / "packages").exists()
    assert any(record.message.startswith("blueprint_audit_persistence_failed") for record in caplog.records)
    warning = next(record.flora_event for record in caplog.records if record.message.startswith("blueprint_audit_persistence_failed"))
    assert warning["event_type"] == "package_upload_authorisation_denied"
    assert warning["diagnostic_reference"].startswith("bpi-diag-")
    assert warning["exception_type"] == "PersistenceError"
    assert "blueprint_import/audit" in warning["storage_path"]


def test_unavailable_var_data_style_path_no_longer_crashes_denied_page(monkeypatch, tmp_path, caplog):
    blocked_root = tmp_path / "var" / "data" / "flora"
    blocked_root.parent.mkdir(parents=True)
    blocked_root.write_text("not a directory", encoding="utf-8")
    monkeypatch.setenv("FLORA_DATA_DIR", str(blocked_root))
    caplog.set_level("WARNING")

    html, status = import_blueprint_entry_page(READ_ONLY)

    assert status == 403
    assert "Blueprint import needs attention" in html
    assert "Blueprint diagnostics could not be persisted." in html
    assert "Blueprint upload capability resolved</th><td>Failed" in html
    assert "Diagnostic reference" in html and "bpi-diag-" in html
    assert not (tmp_path / "memory").exists()
    assert any(record.message.startswith("blueprint_audit_persistence_failed") for record in caplog.records)


def test_writable_configured_directory_records_authorisation_audit(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path / "flora-data"))

    html, status = import_blueprint_entry_page(READ_ONLY)

    assert status == 403
    assert "Blueprint diagnostics could not be persisted" not in html
    events = (tmp_path / "flora-data" / "blueprint_import" / "audit" / "events.jsonl").read_text(encoding="utf-8")
    assert "package_upload_authorisation_denied" in events
    assert "diagnostic_reference" in events


def test_owner_and_non_owner_authorisation_outcomes_unchanged_by_audit_fix(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))

    owner_page, owner_status = import_blueprint_entry_page(OWNER)
    reader_page, reader_status = import_blueprint_entry_page(READ_ONLY)

    assert owner_status == 200 and "Upload and validate" in owner_page
    assert reader_status == 403 and "Blueprint upload capability resolved</th><td>Failed" in reader_page


def test_anonymous_blueprint_diagnostics_stop_after_account_failure(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    html, status = import_blueprint_entry_page({})
    assert status == 403
    assert "Account recognised</th><td>Failed" in html
    assert "Workspace recognised</th><td>Not started" in html
    assert "Membership resolved</th><td>Not started" in html
    assert "Owner status resolved</th><td>Not started" in html
    assert "Blueprint upload capability resolved</th><td>Not started" in html


def test_blueprint_get_and_post_share_cookie_session_identity(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    cookie_headers = {"Cookie": "flora_user=rob; flora_enterprises=synthetic-enterprise; flora_active_workspace=synthetic-enterprise; flora_roles=owner%2Ccanvas.view"}
    html, status = import_blueprint_entry_page(cookie_headers)
    assert status == 200
    assert "Upload and validate" in html
    result_html, post_status, _ = upload_and_validate_blueprint({"blueprint_zip": pkg()}, {"blueprint_zip.filename": "synthetic.zip", "blueprint_zip.content_type": "application/zip"}, cookie_headers)
    assert post_status == 200
    assert "Validation result" in result_html


def test_failed_validation_disables_review_and_promotion(monkeypatch,tmp_path):
    from tests.test_flora_blueprint_import_validation import pkg_with_workbook, xlsx_workbook
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    wb=xlsx_workbook([('00_Control','rId1','worksheets/sheet1.xml',[['external_id'],['X']])], missing_parts={'xl/worksheets/sheet1.xml'})
    html,status,target=upload_and_validate_blueprint({"blueprint_zip":pkg_with_workbook(wb)}, {"blueprint_zip.filename":"synthetic.zip","blueprint_zip.content_type":"application/zip"}, HEADERS)
    assert status == 200
    run_id=target.rsplit("/",1)[-1]
    val,vs=validation_result_page(run_id, HEADERS)
    assert vs == 200 and "Validation failed" in val and "approval are disabled" in val
    review,rs=review_page(run_id, HEADERS)
    assert rs == 200 and "Approval controls are disabled" in review and "disabled>Approve" in review
    blocked,bs=approve_and_promote(run_id,{"plan_id":["anything"],"confirm_plan":["yes"],"confirm_mutations":["yes"],"rationale":["reviewed"]}, HEADERS)
    assert bs == 400 and "Validation failed" in blocked
    assert not (tmp_path/"memory").exists()
