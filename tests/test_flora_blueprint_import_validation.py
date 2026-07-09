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
