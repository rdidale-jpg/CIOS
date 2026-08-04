from pathlib import Path

from cios.applications.flora.blueprint_import.executive_workspace import executive_workspace_page
from cios.applications.flora.blueprint_import.views import upload_and_validate_blueprint

TEL001 = Path("docs/industry-twins/TEL-001_UK_Telecoms_Twin_Wave5_Corrected_Flora_Import 3.zip")


def _stage_tel001(monkeypatch, tmp_path, diagnostics=True):
    monkeypatch.setenv("FLORA_ENVIRONMENT", "pilot")
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    monkeypatch.delenv("FLORA_PILOT_IMPORT_BYPASS", raising=False)
    if diagnostics:
        monkeypatch.setenv("FLORA_PILOT_DIAGNOSTICS", "1")
    else:
        monkeypatch.delenv("FLORA_PILOT_DIAGNOSTICS", raising=False)
    html, status, target = upload_and_validate_blueprint(
        {"blueprint_zip": TEL001.read_bytes()},
        {"expected_type": "industry", "blueprint_zip.filename": TEL001.name, "blueprint_zip.content_type": "application/zip", "_form_submission": "true"},
        {},
    )
    assert status == 200, html[:1000]
    return target.rsplit("/", 1)[-1]


def test_pilot_diagnostics_market_participant_success_and_disabled(monkeypatch, tmp_path):
    run_id = _stage_tel001(monkeypatch, tmp_path, diagnostics=True)
    html, status = executive_workspace_page(run_id, {}, view="aspect", collection="market-participants")
    assert status == 200
    assert "PILOT DIAGNOSTICS — NOT EXECUTIVE OUTPUT" in html
    assert "source_field_present_rendered" in html
    assert "payload.role" in html or "payload.capabilities" in html
    assert "MP-VERIZON" in html
    assert "Page-level diagnostic summary" in html
    assert "loaded profile version" in html
    assert "loaded profile checksum" in html
    assert "selector used from researcher_v1.json" in html
    for stage in (
        "Stage 1 — Candidate",
        "Stage 2 — Source and semantic field availability",
        "Stage 3 — Observation generation",
        "Stage 4 — Canonical owner assessment",
        "Stage 5 — Executive projection",
        "Stage 6 — Rendered page",
    ):
        assert stage in html

    monkeypatch.delenv("FLORA_PILOT_DIAGNOSTICS", raising=False)
    html, status = executive_workspace_page(run_id, {}, view="aspect", collection="market-participants")
    assert status == 200
    assert "PILOT DIAGNOSTICS — NOT EXECUTIVE OUTPUT" not in html
    assert "field-diagnostic" not in html


def test_pilot_diagnostics_industry_enterprise_research_and_stale(monkeypatch, tmp_path):
    monkeypatch.setenv("FLORA_DIAGNOSTICS_FORCE_STALE", "1")
    run_id = _stage_tel001(monkeypatch, tmp_path, diagnostics=True)

    industry, status = executive_workspace_page(run_id, {}, view="aspect", collection="industry-overview")
    assert status == 200
    for section in ("industry definition and scope", "subsectors", "value chain", "market structure", "qualified insights"):
        assert section in industry
    assert any(code in industry for code in ("source_field_absent", "source_field_unmapped", "mapped_value_not_persisted", "projection_field_missing", "projection_filtered_assessment_pending"))
    assert "stale_candidate_representation" in industry
    assert "Pilot Diagnostic Mode flag" in industry
    assert "FLORA_PILOT_DIAGNOSTICS=1" in industry
    advanced, status = executive_workspace_page(run_id, {}, view="diagnostics")
    assert status == 200
    assert "Observation Pipeline runtime comparison" in advanced
    assert "Industry Overview failure" in advanced
    assert "BT Group failure" in advanced
    assert "Market Participant success" in advanced

    bt, status = executive_workspace_page(run_id, {}, view="enterprise", enterprise_id="ent-bt")
    assert status == 200
    assert "BT Group" in bt
    assert "description/purpose diagnostic" in bt
    assert any(code in bt for code in ("source_field_absent", "projection_field_missing", "source_field_present_rendered"))
    assert "assessment required for judgement/eligibility/completeness" in bt

    gaps, status = executive_workspace_page(run_id, {}, view="health")
    assert status == 200
    assert "Research Gap diagnostic" in gaps
    assert "exact reason emitted" in gaps
    assert "source_field_absent" in gaps or "explicit_unknown" in gaps or "assessment_pending_governance" in gaps
