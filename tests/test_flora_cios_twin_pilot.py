import json, zipfile
from io import BytesIO

import pytest

from cios.applications.flora.blueprint_import import BlueprintPackageRegistry, BlueprintPackageValidator, CandidateReviewService, DryRunPlanningService
from cios.applications.flora.blueprint_import.promotion import CanonicalPromotionService
from cios.applications.flora.enterprise_canvas import EnterpriseCanvasService, EnterpriseCanvasAccessError
from cios.applications.flora.enterprise_canvas.feedback import EnterpriseCanvasFeedbackService, FeedbackAccessError

HEADERS={"X-Flora-User":"alice","X-Flora-Enterprises":"synthetic-enterprise","X-Flora-Roles":"blueprint_import_admin,package.review,candidate.promote,feedback.submit,feedback.view"}
BAD={"X-Flora-User":"mallory","X-Flora-Enterprises":"other","X-Flora-Roles":""}

def xlsx():
    sheets={
        "Enterprise Facts":[["stable_id","record_class","attribute","current_value","domain","last_observed_date"],["fact-1","enterprise_model_candidate","name","Synthetic Agency","organisation","2026-01-01"]],
        "Evidence":[["stable_id","record_class","evidence_id","source_title","summary","source_locator"],["ev-1","evidence","EV-SYN-1","Synthetic source","Authorised metadata only","Twin Spine row"]],
        "Observations":[["stable_id","record_class","observation_id","enterprise_id","atomic_statement","observed_at","confidence","observation_type","observation_date","collection_date","affected_attribute","provenance_type"],["obs-1","observation","OBS-SYN-1","synthetic-enterprise","Synthetic agency has a governed Twin baseline.","2026-01-01","90","fact","2026-01-01","2026-01-01","enterprise.name","human-supplied"]],
        "Pain Points":[["stable_id","display_label","status","effective_date"],["pain-1","Synthetic workload pressure","open","2026-01-01"]],
        "Unknowns":[["stable_id","record_class","question"],["unk-1","unknown","Which delivery owner confirms this?"]],
        "Unsupported Things":[["stable_id","record_class","name"],["x-1","invented_class","Do not canonicalise"]],
    }
    ns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    strings=[]
    def si(v): strings.append(str(v)); return len(strings)-1
    bio=BytesIO()
    with zipfile.ZipFile(bio,'w') as z:
        z.writestr('[Content_Types].xml','')
        z.writestr('xl/workbook.xml','<workbook xmlns="%s" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>%s</sheets></workbook>'%(ns,''.join(f'<sheet name="{name}" sheetId="{i}" r:id="rId{i}"/>' for i,name in enumerate(sheets,1))))
        z.writestr('xl/_rels/workbook.xml.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">%s</Relationships>'%''.join(f'<Relationship Id="rId{i}" Type="worksheet" Target="worksheets/sheet{i}.xml"/>' for i in range(1,len(sheets)+1)))
        for i,(name,rows) in enumerate(sheets.items(),1):
            body=''.join('<row>'+''.join(f'<c t="s"><v>{si(c)}</v></c>' for c in r)+'</row>' for r in rows)
            z.writestr(f'xl/worksheets/sheet{i}.xml',f'<worksheet xmlns="{ns}"><sheetData>{body}</sheetData></worksheet>')
        z.writestr('xl/sharedStrings.xml','<sst xmlns="%s">%s</sst>'%(ns,''.join(f'<si><t>{s}</t></si>' for s in strings)))
    return bio.getvalue()

def package():
    wb=xlsx(); manifest={"package_id":"cios-commercial-twin-synthetic","package_version":"twin-v1","enterprise_id":"synthetic-enterprise","profile_version":"0.1","final_twin_spine_workbook":"twin_spine/final.xlsx","files":[{"path":"twin_spine/final.xlsx","role":"final_twin_spine_workbook","sha256":__import__('hashlib').sha256(wb).hexdigest(),"required":True},{"path":"docs/narrative.pdf","role":"narrative_publication"}]}
    bio=BytesIO()
    with zipfile.ZipFile(bio,'w') as z:
        z.writestr('blueprint_manifest.json',json.dumps(manifest))
        z.writestr('twin_spine/final.xlsx',wb)
        z.writestr('docs/narrative.pdf',b'%PDF synthetic narrative not canonical')
    return bio.getvalue()

def test_cios_twin_end_to_end_pilot(tmp_path, monkeypatch):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    rec=BlueprintPackageRegistry().receive(package(),'synthetic_twin.zip','alice')
    staged=BlueprintPackageValidator().validate_and_stage(rec.package_ref,'alice',HEADERS)
    assert staged.candidate_records_staged == 6
    candidates=BlueprintPackageValidator().staging_summary(rec.import_run_id)['candidates']
    assert any(c['source_sheet']=='Pain Points' and c['validation_status']=='quarantined' for c in candidates)
    assert any(c['candidate_object_class']=='invented_class' for c in candidates)
    assert all('MOD' not in json.dumps(c) for c in candidates)
    reviewer=CandidateReviewService();
    for c in candidates:
        if c['candidate_object_class'] in {'evidence','observation'}:
            reviewer.record_decision(c['candidate_record_id'],'approve','alice','pilot approval',HEADERS)
    plan=DryRunPlanningService().create_plan(rec.import_run_id,'alice',HEADERS)
    assert any(e.effect_type=='projection' for e in plan.effects)
    approval=CanonicalPromotionService().approve_plan(rec.import_run_id, plan.plan_id, 'alice', 'pilot', HEADERS)
    promoted=CanonicalPromotionService().execute_approved_plan(rec.import_run_id, approval.approval_id, 'alice', HEADERS)
    again=CanonicalPromotionService().execute_approved_plan(rec.import_run_id, approval.approval_id, 'alice', HEADERS)
    assert promoted.actual_mutation_count == 2
    assert again.final_execution_status == 'repeat_no_change'
    canvas=EnterpriseCanvasService().get_canvas('synthetic-enterprise', HEADERS)
    assert canvas.tiles and canvas.header.twin_version in {'twin-v1','Not established'}
    assert any(t.analytical_projections for t in canvas.tiles)
    detail=EnterpriseCanvasService().get_lineage_inspection('synthetic-enterprise', canvas.tiles[0].tile_view_id, HEADERS)
    assert detail.packages
    fb=EnterpriseCanvasFeedbackService().submit(HEADERS, enterprise_id='synthetic-enterprise', tile_view_id=canvas.tiles[0].tile_view_id, action_type='confirm', user_statement='Validated in synthetic pilot', rationale='test')
    assert fb.feedback_id
    with pytest.raises(Exception):
        BlueprintPackageValidator().validate_and_stage(rec.package_ref,'mallory',BAD)
    with pytest.raises(EnterpriseCanvasAccessError):
        EnterpriseCanvasService().get_canvas('synthetic-enterprise', BAD)
    with pytest.raises(FeedbackAccessError):
        EnterpriseCanvasFeedbackService().submit(BAD, enterprise_id='synthetic-enterprise', action_type='confirm', user_statement='x')
