import json, zipfile, hashlib
from io import BytesIO

from cios.applications.flora.blueprint_import import BlueprintPackageRegistry, BlueprintPackageValidator
from cios.applications.flora.blueprint_import.review_plan import BlueprintReviewPlanCoordinator
from cios.applications.flora.blueprint_import.cios_twin_adapter import MAPPING_VERSION

HEADERS={"X-Flora-User":"alice","X-Flora-Enterprises":"mod","X-Flora-Roles":"blueprint_import_admin,package.review"}

def xlsx(sheets):
    ns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'; strings=[]
    def esc(s): return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    def si(v): strings.append(str(v)); return len(strings)-1
    bio=BytesIO()
    with zipfile.ZipFile(bio,'w') as z:
        z.writestr('[Content_Types].xml','')
        z.writestr('xl/workbook.xml','<workbook xmlns="%s" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>%s</sheets></workbook>'%(ns,''.join(f'<sheet name="{esc(name)}" sheetId="{i}" r:id="rId{i}"/>' for i,name in enumerate(sheets,1))))
        z.writestr('xl/_rels/workbook.xml.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">%s</Relationships>'%''.join(f'<Relationship Id="rId{i}" Type="worksheet" Target="worksheets/sheet{i}.xml"/>' for i in range(1,len(sheets)+1)))
        for i,(name,rows) in enumerate(sheets.items(),1):
            body=''
            for r in rows:
                cells=''.join('<c t="s"><v>%s</v></c>'%si(c) for c in r)
                body += '<row>'+cells+'</row>'
            z.writestr(f'xl/worksheets/sheet{i}.xml',f'<worksheet xmlns="{ns}"><sheetData>{body}</sheetData></worksheet>')
        z.writestr('xl/sharedStrings.xml','<sst xmlns="%s">%s</sst>'%(ns,''.join(f'<si><t>{esc(s)}</t></si>' for s in strings)))
    return bio.getvalue()

def package(wb):
    manifest={"package_id":"mod-blueprint","package_version":"v1.3","enterprise_id":"mod","profile_version":"0.1","final_twin_spine_workbook":"twin_spine/final.xlsx","files":[{"path":"twin_spine/final.xlsx","role":"final_twin_spine_workbook","sha256":hashlib.sha256(wb).hexdigest(),"required":True}]}
    bio=BytesIO()
    with zipfile.ZipFile(bio,'w') as z:
        z.writestr('blueprint_manifest.json',json.dumps(manifest)); z.writestr('twin_spine/final.xlsx',wb)
    return bio.getvalue()

def stage(tmp_path, monkeypatch, sheets):
    monkeypatch.setenv('FLORA_DATA_DIR', str(tmp_path))
    rec=BlueprintPackageRegistry().receive(package(xlsx(sheets)),'MOD-CDT-v1.3-Flora-Blueprint.zip','alice')
    result=BlueprintPackageValidator().validate_and_stage(rec.package_ref,'alice',HEADERS)
    return rec, result, BlueprintPackageValidator().staging_summary(rec.import_run_id)['candidates']

def test_mod_core_canonical_projection_and_ignore_mapping(tmp_path, monkeypatch):
    sheets={
        '03_Sources': [['source_id','source_title','url'], ['SRC-1','MOD source','https://example.test/src']],
        '04A_Evidence': [['evidence_id','source_id','summary','source_locator'], ['EV-1','SRC-1','Evidence summary','p.1']],
        '05_Observations': [['observation_id','source_id','atomic_statement','confidence'], ['OBS-1','SRC-1','Observed fact','0.8']],
        '16_Unknowns': [['unknown_id','source_id','question'], ['UNK-1','SRC-1','Open question']],
        '17_Contradictions': [['contradiction_id','source_id','statement_a','statement_b'], ['CON-1','SRC-1','A','B']],
        '24_Human_Knowledge': [['stable_id','source_id','statement'], ['HK-1','interview','Human supplied context']],
        '06_Entities_Rels': [['stable_id','record_type','name','source_id'], ['ENT-1','entity','Entity A','SRC-1'], ['REL-1','relationship','A owns B','SRC-1']],
        '30_Pain_Portfolio': [['stable_id','pain','evidence_id'], ['PAIN-1','Pain exists','EV-1']],
        '00_Control': [['stable_id','note'], ['CTRL-1','should be ignored']],
        '99_Mystery': [['stable_id','name'], ['X-1','Unsupported']],
    }
    rec, result, candidates = stage(tmp_path, monkeypatch, sheets)
    classes={c['candidate_object_class'] for c in candidates}
    assert {'source','evidence','observation','unknown','contradiction','human_knowledge','entity','relationship','pain_point','unsupported_twin_spine_row'} <= classes
    assert any(c['source_sheet']=='00_Control' and c['validation_status']=='ignored' for c in candidates)
    assert any(c['candidate_object_class']=='pain_point' and c['validation_status']=='quarantined' for c in candidates)
    assert any(c['candidate_object_class']=='human_knowledge' and c['payload'].get('human_supplied') is True for c in candidates)
    assert result.canonical_mutations == 0
    summary = BlueprintReviewPlanCoordinator().ensure_job(rec.import_run_id, 'alice', HEADERS, lambda: None)
    assert summary['mapping_version'] == MAPPING_VERSION
    assert summary['class_summary']['accepted']['source'] == 1


def test_missing_lineage_quarantines_specifically_and_restaging_idempotent(tmp_path, monkeypatch):
    sheets={'05_Observations': [['observation_id','atomic_statement'], ['OBS-NO-LINEAGE','No source']], '01_Plan': [['x'], ['ignored']], '04A_Evidence': [['evidence_id','source_id','summary'], ['EV-1','SRC-1','Ok']]}
    rec, result, candidates = stage(tmp_path, monkeypatch, sheets)
    bad=[c for c in candidates if c['original_source_id']=='OBS-NO-LINEAGE'][0]
    assert bad['validation_status']=='quarantined'
    assert bad['validation_findings'][0]['code']=='quarantined_missing_lineage'
    again=BlueprintPackageValidator().validate_and_stage(rec.package_ref,'alice',HEADERS)
    assert again.candidate_records_staged == result.candidate_records_staged
    assert all(c['candidate_object_class'] != 'package_metadata' for c in candidates)


def test_v11_mapping_quality_counts_and_ignored_rows(tmp_path, monkeypatch):
    sheets={
        '03_Sources': [['source_id','source_title','url'], ['SRC-1','MOD source','https://example.test/src']],
        '04A_Evidence': [['evidence_id','source_id','summary','source_locator'], ['EV-1','SRC-1','Evidence summary','p.1']],
        '05_Observations': [['observation_id','source_id','atomic_statement','confidence'], ['OBS-1',' SRC-1 ; EV-1 ','Observed fact','0.8'], ['OBS-NO','', 'No lineage','0.2']],
        '16_Unknowns': [['question','scope','significance','status'], ['What is missing?','MOD','High','open']],
        '17_Contradictions': [['statement_a','statement_b','severity','source_id'], ['A','B','high','SRC-1']],
        '06_Entities_Rels': [['record_type','name','source_id','target','relationship_type'], ['entity','Entity A','SRC-1','',''], ['relationship','Entity A','SRC-1','Entity B','owns']],
        '13_Causal_Edges': [['source','target','relationship_type','evidence_id'], ['A','B','influences','EV-1']],
        '24_Human_Knowledge': [['stable_id','source_id','statement','caveat'], ['HK-1','human interview','Human supplied context','unverified']],
        '04_Claims': [['claim','truth_class','source_id'], ['Backed claim','asserted','SRC-1'], ['Unsupported claim','','']],
        '15_Theses': [['thesis_id','thesis'], ['T-1','Projection only thesis']],
        '00_Control': [['stable_id','note'], ['CTRL-1','should be ignored']],
        '02_Dashboard': [['metric','formula'], ['=SUM(A1:A2)','=A1']],
    }
    rec, result, candidates = stage(tmp_path, monkeypatch, sheets)
    summary = BlueprintReviewPlanCoordinator().ensure_job(rec.import_run_id, 'alice', HEADERS, lambda: None)
    accepted = summary['class_summary']['accepted']
    assert accepted['source'] == 1
    assert accepted['evidence'] == 1
    assert accepted['observation'] == 1
    assert accepted['unknown'] == 1
    assert accepted['contradiction'] == 1
    assert accepted['entity'] == 1
    assert accepted['relationship'] >= 1
    assert accepted['human_knowledge'] == 1
    assert summary['candidate_summary']['Ignored'] >= 2
    assert summary['ignored_reasons']['ignored_control_row'] == 1
    assert summary['mapping_quality']['derived_id_count'] >= 4
    assert summary['mapping_quality']['twin_completeness_indicators']['observation'] is True
    obs = [c for c in candidates if c['original_source_id']=='OBS-1'][0]
    refs = obs['payload']['lineage_resolution']
    assert [r['normalized_reference'] for r in refs] == ['1', '1']
    bad = [c for c in candidates if c['original_source_id']=='OBS-NO'][0]
    assert bad['validation_status'] == 'quarantined'
    assert bad['validation_findings'][0]['code'] == 'quarantined_missing_lineage'
    hk = [c for c in candidates if c['candidate_object_class']=='human_knowledge'][0]
    assert hk['payload']['human_supplied'] is True
    thesis = [c for c in candidates if c['source_sheet']=='15_Theses'][0]
    assert thesis['payload']['mapping_disposition'] == 'reasoning_artifact'
    assert any(c['candidate_object_class']=='ignored_row' for c in candidates)
    assert result.canonical_mutations == 0


def test_v11_deterministic_ids_collision_and_package_metadata_removed(tmp_path, monkeypatch):
    sheets={
        '03_Sources': [['source_id','title'], ['SRC-1','Source']],
        '04A_Evidence': [['evidence_id','source_id','summary'], ['EV-1','SRC-1','Evidence']],
        '16_Unknowns': [['question','scope'], ['Same unknown','MOD'], ['Same unknown','MOD']],
        '17_Contradictions': [['statement_a','statement_b','source_id'], ['A','B','SRC-1']],
        '06_Entities_Rels': [['record_type','name','source_id'], ['entity','Entity A','SRC-1']],
        '13_Causal_Edges': [['source','target','evidence_id'], ['A','B','EV-1']],
    }
    rec, result, candidates = stage(tmp_path, monkeypatch, sheets)
    ids = [c['original_source_id'] for c in candidates if c['candidate_object_class'] in {'unknown','contradiction','entity','relationship'}]
    again = BlueprintPackageValidator().validate_and_stage(rec.package_ref,'alice',HEADERS)
    candidates2 = BlueprintPackageValidator().staging_summary(rec.import_run_id)['candidates']
    ids2 = [c['original_source_id'] for c in candidates2 if c['candidate_object_class'] in {'unknown','contradiction','entity','relationship'}]
    assert ids == ids2
    assert len(ids) == len(set(ids))
    assert all(c['payload'].get('identifier_derivation',{}).get('derived') for c in candidates if c['candidate_object_class'] in {'unknown','contradiction','entity','relationship'})
    assert all(c['candidate_object_class'] != 'package_metadata' for c in candidates)
    assert again.candidate_records_staged == result.candidate_records_staged


def test_v12_core_mapping_contract_and_review_summary(tmp_path, monkeypatch):
    sheets={
        '03_Sources': [['source_id','source_title','url'], ['SRC-1','MOD source','https://example.test/src']],
        '04A_Evidence': [['evidence_id','source_id','summary','source_locator'], ['EVD-1','SRC-1','Evidence summary','p.1']],
        '05_Observations': [['observation_id','supporting_source','supporting_evidence','atomic_statement','confidence','freshness'], ['OBS-S',' src-1 ','','Source-backed obs','0.8','2026-01-01'], ['OBS-E','','evd-1','Evidence-backed obs','0.9','2026-01-02'], ['OBS-M','SRC-1 | EVD-1; missing-ref','','Multi-backed obs','0.7','2026-01-03'], ['OBS-BAD','','','No lineage','0.1','']],
        '16_Unknowns': [['question','scope','significance','evidence_gap','owner','status'], ['What is unresolved?','MOD','High','No evidence yet','Owner A','open']],
        '22_Provenance_Risk': [['statement','scope','significance','status'], ['Unresolved provenance risk','MOD','Medium','open']],
        '17_Contradictions': [['statement_a','statement_b','scope','evidence_id','significance','status'], ['A','B','MOD','EVD-1','High','open']],
        '06_Entities_Rels': [['record_type','entity_type','name','source','target','relationship_type'], ['entity','organisation','Entity A','','',''], ['relationship','','','Entity A','Entity B','owns']],
        '07_Executives_Rights': [['record_type','entity_type','name'], ['entity','person','Jane Doe']],
        '08_Programmes': [['record_type','entity_type','name'], ['entity','programme','Programme A']],
        '09_Capabilities': [['record_type','entity_type','name'], ['entity','capability','Capability A']],
        '10_Systems_Data': [['record_type','entity_type','name'], ['entity','system','System A']],
        '11_Suppliers_Contracts': [['record_type','entity_type','name'], ['entity','supplier','Supplier A']],
        '12_Measures_Resources': [['record_type','entity_type','name'], ['entity','measure','Measure A']],
        '13_Causal_Edges': [['source','target','relationship_type','evidence_id'], ['Capability A','Outcome B','influences','EVD-1']],
        '24_Human_Knowledge': [['provider','statement','confidence','caveat','date','evidence_id'], ['SME','Human supplied context','low','unverified','2026-01-04','EVD-1']],
        '00_Control': [['stable_id','note'], ['CTRL-1','ignored']],
        '02_Dashboard': [['metric','formula'], ['Rows','=A1']],
        'Workflow': [['step','owner'], ['route','alice']],
        '99_Mystery': [['stable_id','name'], ['X-1','Unsupported']],
    }
    rec, result, candidates = stage(tmp_path, monkeypatch, sheets)
    summary = BlueprintReviewPlanCoordinator().ensure_job(rec.import_run_id, 'alice', HEADERS, lambda: None)
    accepted = summary['mapping_quality']['accepted_by_class']
    assert accepted['observation'] == 3
    assert accepted['unknown'] == 2
    assert accepted['contradiction'] == 1
    assert accepted['entity'] >= 7
    assert accepted['relationship'] >= 2
    assert accepted['human_knowledge'] == 1
    assert summary['mapping_version'] == 'mod-cdt-twin-spine-mapping-v1.2.0'
    assert summary['candidate_summary']['Rejected'] == 0
    assert summary['ignored_reasons']['ignored_control_row'] == 1
    assert summary['ignored_reasons']['ignored_dashboard_row'] == 1
    assert summary['ignored_reasons']['ignored_workflow_row'] == 1
    bad = [c for c in candidates if c['original_source_id']=='OBS-BAD'][0]
    assert bad['validation_status'] == 'quarantined'
    assert bad['validation_findings'][0]['code'] == 'quarantined_missing_lineage'
    multi = [c for c in candidates if c['original_source_id']=='OBS-M'][0]
    assert len(multi['payload']['lineage_resolution']) == 3
    assert any(r['resolved_staged_candidate'] for r in multi['payload']['lineage_resolution'])
    assert any(not r['resolved_staged_candidate'] for r in multi['payload']['lineage_resolution'])
    hk = [c for c in candidates if c['candidate_object_class']=='human_knowledge'][0]
    assert hk['payload']['human_supplied'] is True
    assert hk['truth_class'] == 'human-supplied'
    assert result.canonical_mutations == 0
    assert all(c['candidate_object_class'] != 'package_metadata' for c in candidates)


def test_v12_ignored_rows_collision_and_stable_derived_ids(tmp_path, monkeypatch):
    sheets={
        '03_Sources': [['source_id','title'], ['SRC-1','Source']],
        '04A_Evidence': [['evidence_id','source_id','summary'], ['EVD-1','SRC-1','Evidence']],
        '16_Unknowns': [['question','scope'], ['question','scope'], ['Same unknown','MOD'], ['Same unknown','MOD'], ['', '']],
        '02_Dashboard': [['metric','formula'], ['=SUM(A1:A2)','=A1']],
        'Workflow': [['step','owner'], ['handoff','bob']],
    }
    rec, result, candidates = stage(tmp_path, monkeypatch, sheets)
    ids = [c['original_source_id'] for c in candidates if c['candidate_object_class']=='unknown']
    assert len(ids) == 2 and len(set(ids)) == 2
    assert any((c['payload'].get('identifier_collision_resolution')) for c in candidates if c['candidate_object_class']=='unknown')
    assert any(c['validation_status']=='ignored' and c['payload']['ignore_reason']=='ignored_repeated_header' for c in candidates)
    assert any(c['validation_status']=='ignored' and c['payload']['ignore_reason']=='ignored_blank_row' for c in candidates)
    assert any(c['validation_status']=='ignored' and c['payload']['ignore_reason']=='ignored_dashboard_row' for c in candidates)
    assert any(c['validation_status']=='ignored' and c['payload']['ignore_reason']=='ignored_workflow_row' for c in candidates)
    BlueprintPackageValidator().validate_and_stage(rec.package_ref,'alice',HEADERS)
    candidates2 = BlueprintPackageValidator().staging_summary(rec.import_run_id)['candidates']
    ids2 = [c['original_source_id'] for c in candidates2 if c['candidate_object_class']=='unknown']
    assert ids == ids2
    summary = BlueprintReviewPlanCoordinator().ensure_job(rec.import_run_id, 'alice', HEADERS, lambda: None)
    assert summary['mapping_quality']['derived_id_collisions'] >= 1
    assert result.canonical_mutations == 0
