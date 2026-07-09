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
