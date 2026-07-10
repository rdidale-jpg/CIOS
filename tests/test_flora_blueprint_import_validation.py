from __future__ import annotations

import io, json, zipfile
import pytest

from cios.applications.flora.blueprint_import import BlueprintPackageRegistry, BlueprintPackageValidator, BlueprintValidationError
from cios.applications.flora.blueprint_import.archive import sha256_bytes


def pkg(manifest_extra=None, records=None, extra=None, duplicate=False):
    records = records if records is not None else [
        {"external_id":"SRC-1","record_class":"source","truth_class":"package_metadata","payload":{"name":"Synthetic source"},"source_location":{"sheet":"Sources","row":2}},
        {"external_id":"OBS-1","record_class":"observation","truth_class":"evidence_backed","payload":{"statement":"A factual claim"}},
    ]
    files={"records/sources.ndjson":"\n".join(json.dumps(r) for r in records).encode()}
    if extra: files.update(extra)
    manifest={"package_id":"synthetic-blueprint","package_version":"1.0.0","enterprise_id":"synthetic-enterprise","profile_version":"0.1",
        "files":[{"path":"records/sources.ndjson","sha256":sha256_bytes(files["records/sources.ndjson"]),"required":True}],
        "record_sets":[{"record_class":"source","path":"records/sources.ndjson","count":len(records),"required":False}]}
    if manifest_extra: manifest.update(manifest_extra)
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("blueprint_manifest.json", json.dumps(manifest))
        for k,v in files.items(): z.writestr(k,v)
        if duplicate: z.writestr("records/sources.ndjson", b"{}\n")
    return b.getvalue()


def receive(monkeypatch,tmp_path,content=None):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    return BlueprintPackageRegistry().receive(content or pkg(), "synthetic.zip", "alice")


def test_valid_package_validation_and_supported_record_staging(monkeypatch,tmp_path):
    r=receive(monkeypatch,tmp_path)
    result=BlueprintPackageValidator().validate_and_stage(r.package_ref,"alice", {"X-Flora-User":"alice","X-Flora-Enterprises":"synthetic-enterprise","X-Flora-Roles":"package.review"})
    assert result.files_inspected == ("blueprint_manifest.json","records/sources.ndjson")
    assert result.supported_records_discovered == 2
    assert result.candidate_records_staged == 2
    assert result.records_accepted_into_staging == 2
    assert result.canonical_mutations == 0
    summary=BlueprintPackageValidator().staging_summary(r.import_run_id)
    assert all(c["source_package_ref"] == r.package_ref for c in summary["candidates"])
    assert all(c["canonical_mutation_count"] == 0 for c in summary["candidates"])
    assert any(c["source_sheet"] == "Sources" for c in summary["candidates"])


def test_manifest_to_registry_mismatch_is_rejected_inspectably(monkeypatch,tmp_path):
    r=receive(monkeypatch,tmp_path)
    p=tmp_path / r.archive_path
    p.write_bytes(pkg({"enterprise_id":"other-enterprise"}))
    # keep archive checksum same impossible, so adjust registry file only for this manifest mismatch path
    import json as js
    f=tmp_path/'blueprint_import'/'packages'/f'{r.package_ref}.json'
    d=js.loads(f.read_text()); d['package_sha256']=sha256_bytes(p.read_bytes()); f.write_text(js.dumps(d))
    result=BlueprintPackageValidator().validate_and_stage(r.package_ref,"alice")
    assert any("enterprise_id" in e for e in result.errors)
    assert result.records_rejected == 1


def test_checksum_mismatch_stops_processing(monkeypatch,tmp_path):
    r=receive(monkeypatch,tmp_path)
    (tmp_path / r.archive_path).write_bytes(b"changed")
    with pytest.raises(BlueprintValidationError):
        BlueprintPackageValidator().validate_and_stage(r.package_ref,"alice")


def test_missing_required_file_duplicate_and_unsafe_archive_paths(monkeypatch,tmp_path):
    r=receive(monkeypatch,tmp_path,pkg({"files":[{"path":"records/missing.ndjson","required":True}],"record_sets":[]}))
    assert "Missing required file" in "\n".join(BlueprintPackageValidator().validate_and_stage(r.package_ref,"alice").errors)
    r2=receive(monkeypatch,tmp_path,pkg(duplicate=True))
    assert "Duplicate package files" in "\n".join(BlueprintPackageValidator().validate_and_stage(r2.package_ref,"alice").errors)
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w") as z:
        z.writestr("blueprint_manifest.json", json.dumps({"package_id":"p1","package_version":"1","enterprise_id":"e1","profile_version":"0.1"}))
        z.writestr("/absolute.ndjson", "")
    with pytest.raises(Exception):
        receive(monkeypatch,tmp_path,b.getvalue())


def test_unsupported_projection_unresolved_partial_and_idempotent(monkeypatch,tmp_path):
    records=[
        {"external_id":"OBS-1","record_class":"observation","truth_class":"evidence_backed","payload":{"statement":"ok"}},
        {"external_id":"PP-1","record_class":"pain_point","truth_class":"analytical_projection","payload":{"text":"projection"}},
        {"external_id":"X-1","record_class":"provider_fit","truth_class":"inferred","payload":{}},
        {"external_id":"OBS-2","record_class":"observation","truth_class":"evidence_backed","payload":{},"references":["missing:E-404"]},
    ]
    r=receive(monkeypatch,tmp_path,pkg(records=records))
    v=BlueprintPackageValidator(); first=v.validate_and_stage(r.package_ref,"alice"); second=v.validate_and_stage(r.package_ref,"alice")
    assert first == second
    assert first.records_accepted_into_staging == 1
    assert first.records_quarantined == 3
    assert "provider_fit" in first.unsupported_classes
    assert "missing:E-404" in first.unresolved_references
    assert len(v.staging_summary(r.import_run_id)["candidates"]) == 4


def test_authorised_unauthorised_failed_cleanup_and_no_canonical_mutation(monkeypatch,tmp_path):
    r=receive(monkeypatch,tmp_path)
    with pytest.raises(BlueprintValidationError):
        BlueprintPackageValidator().validate_and_stage(r.package_ref,"alice", {"X-Flora-User":"alice","X-Flora-Enterprises":"other","X-Flora-Roles":"package.review"})
    BlueprintPackageValidator().validate_and_stage(r.package_ref,"alice", {"X-Flora-User":"alice","X-Flora-Enterprises":"*","X-Flora-Roles":"blueprint_import_admin"})
    assert not (tmp_path/"memory"/"evidence.jsonl").exists()
    assert not (tmp_path/"memory"/"observations.jsonl").exists()
    assert not (tmp_path/"memory"/"enterprise_models").exists()


def zip_bytes(entries):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in entries:
            z.writestr(name, data)
    return b.getvalue()


def assert_receipt_error(monkeypatch, tmp_path, content, message):
    monkeypatch.setenv("FLORA_DATA_DIR", str(tmp_path))
    with pytest.raises(Exception) as exc:
        BlueprintPackageRegistry().receive(content, "synthetic.zip", "alice")
    assert message in str(exc.value)
    assert not (tmp_path / "memory" / "evidence.jsonl").exists()
    assert not (tmp_path / "memory" / "observations.jsonl").exists()
    assert not (tmp_path / "memory" / "enterprise_models").exists()


def test_manifest_missing_nested_duplicate_invalid_json_and_schema_messages(monkeypatch, tmp_path):
    assert_receipt_error(
        monkeypatch, tmp_path, zip_bytes([("records/sources.ndjson", b"")]),
        "Blueprint package is missing blueprint_manifest.json. Place blueprint_manifest.json at the root of the ZIP package.",
    )
    assert_receipt_error(
        monkeypatch, tmp_path, zip_bytes([("nested/blueprint_manifest.json", b"{}")]),
        "blueprint_manifest.json was found inside a folder. Move it to the root of the ZIP package and try again.",
    )
    valid = json.dumps({"package_id":"p1","package_version":"1","enterprise_id":"e1","profile_version":"0.1"})
    assert_receipt_error(
        monkeypatch, tmp_path, zip_bytes([("blueprint_manifest.json", valid), ("copy/blueprint_manifest.json", valid)]),
        "The package contains more than one blueprint_manifest.json. Keep one canonical manifest at the ZIP root.",
    )
    assert_receipt_error(
        monkeypatch, tmp_path, zip_bytes([("blueprint_manifest.json", b"{")]),
        "blueprint_manifest.json is not valid JSON.",
    )
    assert_receipt_error(
        monkeypatch, tmp_path, zip_bytes([("blueprint_manifest.json", b"[]")]),
        "blueprint_manifest.json does not match the required Blueprint manifest structure.",
    )


def xlsx_workbook(sheet_targets, missing_parts=(), extra_entries=None):
    """Build a minimal workbook with [(sheet_name, rel_id, target, rows)]."""
    def cell(ref, value):
        return f'<c r="{ref}" t="s"><v>{value}</v></c>'
    strings=[]; sheet_entries={}
    for idx,(name,rid,target,rows) in enumerate(sheet_targets, start=1):
        xml_rows=[]
        for rnum,row in enumerate(rows, start=1):
            cells=[]
            for cidx,value in enumerate(row, start=1):
                strings.append(str(value)); cells.append(cell(f"{chr(64+cidx)}{rnum}", len(strings)-1))
            xml_rows.append(f'<row r="{rnum}">{"".join(cells)}</row>')
        default=f"xl/worksheets/sheet{idx}.xml"
        part = target.lstrip('/') if target.startswith('/xl/') else (target if target.startswith('xl/') else 'xl/' + target.replace('../',''))
        if target == '../worksheets/sheet1.xml': part = 'worksheets/sheet1.xml'
        sheet_entries[default if default not in missing_parts else default] = f'<?xml version="1.0"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>{"".join(xml_rows)}</sheetData></worksheet>'
    sheets=''.join(f'<sheet name="{n}" sheetId="{i}" r:id="{rid}"/>' for i,(n,rid,_,__) in enumerate(sheet_targets, start=1))
    rels=''.join(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="{target}"/>' for _,rid,target,__ in sheet_targets)
    shared=''.join(f'<si><t>{s}</t></si>' for s in strings)
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        z.writestr('xl/workbook.xml', f'<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>{sheets}</sheets></workbook>')
        z.writestr('xl/_rels/workbook.xml.rels', f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{rels}</Relationships>')
        z.writestr('xl/sharedStrings.xml', f'<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">{shared}</sst>')
        for name, xml in sheet_entries.items():
            if name not in missing_parts: z.writestr(name, xml)
        for name, data in (extra_entries or {}).items(): z.writestr(name, data)
    return b.getvalue()


def pkg_with_workbook(workbook):
    files={'final.xlsx': workbook}
    manifest={"package_id":"synthetic-blueprint","package_version":"1.0.0","enterprise_id":"synthetic-enterprise","profile_version":"0.1",
        "files":[{"path":"final.xlsx","sha256":sha256_bytes(workbook),"required":True,"role":"final_twin_spine"}],"record_sets":[]}
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('blueprint_manifest.json', json.dumps(manifest)); z.writestr('final.xlsx', workbook)
    return b.getvalue()


def test_xlsx_relationship_targets_resolve_without_xl_duplication(monkeypatch,tmp_path):
    for target in ['worksheets/sheet1.xml','xl/worksheets/sheet1.xml','/xl/worksheets/sheet1.xml']:
        wb=xlsx_workbook([('Observations','rId1',target,[['external_id','record_class','statement'],['OBS-1','observation','ok']])])
        r=receive(monkeypatch,tmp_path,pkg_with_workbook(wb))
        result=BlueprintPackageValidator().validate_and_stage(r.package_ref,'alice')
        assert not result.errors
        assert 'Worksheets discovered: Observations' in result.warnings
        assert result.records_accepted_into_staging == 1
        assert 'xl/xl/worksheets/sheet1.xml' not in '\n'.join(result.errors + result.warnings)


def test_xlsx_multiple_sheets_ids_staging_and_macro_warning(monkeypatch,tmp_path):
    wb=xlsx_workbook([
        ('Observations','rIdObs','worksheets/sheet1.xml',[['external_id','record_class','statement'],['OBS-1','observation','ok']]),
        ('Pain Points','rIdPain','worksheets/sheet2.xml',[['external_id','text'],['PP-1','pain']]),
    ], extra_entries={'xl/vbaProject.bin': b'macro bytes', 'xl/externalLinks/externalLink1.xml': b'<x/>'})
    r=receive(monkeypatch,tmp_path,pkg_with_workbook(wb))
    result=BlueprintPackageValidator().validate_and_stage(r.package_ref,'alice')
    assert not result.errors
    assert any('Observations, Pain Points' in w for w in result.warnings)
    assert any('macros' in w for w in result.warnings)
    summary=BlueprintPackageValidator().staging_summary(r.import_run_id)
    assert {c['source_sheet'] for c in summary['candidates']} == {'Observations','Pain Points'}
    assert result.records_accepted_into_staging == 1 and result.records_quarantined == 1
    assert not (tmp_path/'memory').exists()


def test_xlsx_missing_malformed_and_traversal_targets_fail_safely(monkeypatch,tmp_path):
    cases=[
        xlsx_workbook([('00_Control','rId1','worksheets/sheet1.xml',[['external_id'],['X']])], missing_parts={'xl/worksheets/sheet1.xml'}),
        xlsx_workbook([('Bad','rId1','http://example.com/sheet.xml',[['external_id'],['X']])]),
        xlsx_workbook([('Bad','rId1','../../evil.xml',[['external_id'],['X']])]),
        xlsx_workbook([('Bad','rId1','worksheets\\sheet1.xml',[['external_id'],['X']])]),
    ]
    for wb in cases:
        r=receive(monkeypatch,tmp_path,pkg_with_workbook(wb))
        result=BlueprintPackageValidator().validate_and_stage(r.package_ref,'alice')
        joined='\n'.join(result.errors)
        assert 'Workbook could not be inspected safely' in joined
        assert result.records_rejected == 1
        assert not (tmp_path/'memory').exists()


def test_xlsx_relative_parent_target_uses_source_part_semantics():
    from cios.applications.flora.blueprint_import.cios_twin_adapter import CiosCommercialTwinAdapter, resolve_ooxml_relationship_target
    assert resolve_ooxml_relationship_target('xl/workbook.xml','worksheets/sheet1.xml') == 'xl/worksheets/sheet1.xml'
    assert resolve_ooxml_relationship_target('xl/workbook.xml','xl/worksheets/sheet1.xml') == 'xl/worksheets/sheet1.xml'
    assert resolve_ooxml_relationship_target('xl/workbook.xml','/xl/worksheets/sheet1.xml') == 'xl/worksheets/sheet1.xml'
    assert CiosCommercialTwinAdapter()._resolve_part_target('xl/workbook.xml','../worksheets/sheet1.xml') == 'worksheets/sheet1.xml'


def test_mod_blueprint_equivalent_workbook_proceeds_beyond_inspection(monkeypatch,tmp_path):
    # Representative MOD Blueprint-shaped workbook because MOD-CDT-v1.3-Flora-Blueprint.zip
    # is not present in this repository: a control sheet plus multiple governed Twin Spine sheets,
    # including a package-rooted worksheet target that previously produced xl/xl.
    wb=xlsx_workbook([
        ('00_Control','rIdCtrl','xl/worksheets/sheet1.xml',[['external_id','record_class','statement'],['CTRL-1','observation','control ok']]),
        ('Observations','rIdObs','worksheets/sheet2.xml',[['external_id','record_class','statement'],['OBS-1','observation','observation ok']]),
        ('Pain Points','rIdPain','/xl/worksheets/sheet3.xml',[['external_id','text'],['PP-1','pain']]),
    ])
    r=receive(monkeypatch,tmp_path,pkg_with_workbook(wb))
    result=BlueprintPackageValidator().validate_and_stage(r.package_ref,'alice')
    joined='\n'.join(result.errors + result.warnings)
    assert not result.errors
    assert 'Worksheets discovered: 00_Control, Observations, Pain Points' in result.warnings
    assert 'xl/xl/worksheets/sheet1.xml' not in joined
    assert result.candidate_records_staged > 0
    assert result.records_accepted_into_staging > 0
    assert result.records_quarantined > 0
    assert result.canonical_mutations == 0
