from cios.applications.flora.blueprint_import.lifecycle import ImportLifecycleService
from cios.applications.flora.blueprint_import.views import cancel_import, cancellation_confirmation_page, import_blueprint_entry_page, promotion_confirmation_page, review_page, upload_and_validate_blueprint, validation_result_page
from tests.test_flora_blueprint_import_validation import pkg
from tests.test_flora_package_contracts import package as governed_package

HEADERS={"X-Flora-User":"alice","X-Flora-Enterprises":"synthetic-enterprise","X-Flora-Roles":"blueprint_import_admin,package.review,candidate.promote"}

def uploaded():
    _,status,target=upload_and_validate_blueprint({"blueprint_zip":pkg()},{"blueprint_zip.filename":"twin.zip","blueprint_zip.content_type":"application/zip","expected_type":"enterprise"},HEADERS)
    assert status==200
    return target.split("/")[-1]

def test_upload_and_inspect_workflow(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR",str(tmp_path))
    html,status=import_blueprint_entry_page(HEADERS)
    assert status==200 and "Import Commercial Digital Twin" in html and "Upload and validate" in html and "aria-label='Import progress'" in html
    run=uploaded(); html,status=validation_result_page(run,HEADERS)
    assert status==200 and "Validation outcomes" in html and "Blocking errors" in html and "Cancel import" in html


def test_dist_shaped_package_uses_normal_upload_and_enables_review(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    headers = HEADERS | {"X-Flora-Enterprises": "DIST-001"}
    content = governed_package(
        ("00_manifest.json", {"package_id": "DIST-001", "version": "1.0", "industry": "Distribution"}),
        ("flora/industry-twin-delta-for-flora.json", {"primary_objects": {
            "enterprise_twins": ["DIST-ENT-001"], "market_participant_twins": ["DIST-MP-001"],
            "opportunity_twins": ["DIST-OPP-001"], "flow_twins": ["DIST-FLOW-001"],
        }}),
        ("twins/enterprise-twins.json", [{"stable_id": "DIST-ENT-001", "object_type": "enterprise_twin"}]),
        ("twins/market-participant-twins.json", [{"stable_id": "DIST-MP-001", "object_type": "market_participant_twin"}]),
        ("twins/opportunity-twins.json", [{"stable_id": "DIST-OPP-001", "object_type": "opportunity_twin"}]),
        ("machine-inspectable/flow-twins.json", [{"stable_id": "DIST-FLOW-001", "object_type": "flow_twin"}]),
    )

    html, status, target = upload_and_validate_blueprint(
        {"blueprint_zip": content},
        {"blueprint_zip.filename": "DIST-001.zip", "blueprint_zip.content_type": "application/zip", "expected_type": "industry"},
        headers,
    )

    assert status == 200
    assert target.startswith("/blueprint-import/")
    assert "Governed Industry Twin Package" in html
    assert "Detected package type</th><td>Industry" in html
    assert "DIST-001.zip" in html
    assert "Review proposed changes" in html
    assert "No staging candidates" not in html
    assert "Enterprise Twin: 1" in html and "Market Participant Twin: 1" in html
    assert "Opportunity Twin: 1" in html and "Flow Twin: 1" in html
    assert "Governed Industry Twin package diagnostics" in html
    assert "candidates passed to staging" in html

def test_cancellation_is_durable_audited_and_blocks_review(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR",str(tmp_path)); run=uploaded()
    html,status=cancellation_confirmation_page(run,"review",HEADERS)
    assert status==200 and "role='alertdialog'" in html and "Continue reviewing" in html
    html,status=cancel_import(run,{"stage":["review"],"reason":["incomplete evidence"]},HEADERS)
    assert status==200 and "No canonical writes occurred" in html
    row=ImportLifecycleService().get(run)
    assert row.state=="cancelled" and row.reason=="incomplete evidence" and row.canonical_writes==0
    assert "import_cancelled" in (tmp_path/"blueprint_import/audit/events.jsonl").read_text()
    _,status=review_page(run,HEADERS); assert status==409

def test_cancelled_import_cannot_reach_promotion(tmp_path, monkeypatch):
    monkeypatch.setenv("FLORA_DATA_DIR",str(tmp_path)); run=uploaded()
    cancel_import(run,{"stage":["inspect"]},HEADERS)
    html,status=promotion_confirmation_page(run,HEADERS)
    assert status==409 and "Cancelled Twin import" in html
