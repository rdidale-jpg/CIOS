#!/usr/bin/env python3
"""Portable, standard-library Flora Blueprint ZIP producer."""
import argparse, hashlib, json, re, sys, zipfile
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
MANIFEST = "blueprint_manifest.json"

def fail(message): raise ValueError(message)
def safe_path(value):
    if not isinstance(value, str): fail("path must be a string")
    path = PurePosixPath(value)
    if not value or value.startswith(("/", "\\")) or "\\" in value or any(p in ("", ".", "..") for p in path.parts) or path.as_posix() != value:
        fail(f"unsafe or non-normalized relative POSIX path: {value!r}")
    return value

def resolve(schema, root):
    while "$ref" in schema:
        reference = schema["$ref"]
        schema = root
        for part in reference.removeprefix("#/").split("/"): schema = schema[part]
    return schema

def validate_schema(value, schema, root, where="$"):
    schema = resolve(schema, root)
    if "anyOf" in schema:
        errors=[]
        for choice in schema["anyOf"]:
            try: validate_schema(value, choice, root, where); return
            except ValueError as exc: errors.append(str(exc))
        fail(f"{where}: does not match any supported schema choice")
    if "const" in schema and value != schema["const"]: fail(f"{where}: must equal {schema['const']!r}")
    kind=schema.get("type")
    checks={"object":dict,"array":list,"string":str,"integer":int,"boolean":bool,"null":type(None)}
    if kind in checks and (not isinstance(value, checks[kind]) or kind == "integer" and isinstance(value, bool)): fail(f"{where}: expected {kind}")
    if isinstance(value, dict):
        props=schema.get("properties", {}); missing=set(schema.get("required", []))-set(value)
        if missing: fail(f"{where}: missing required properties {sorted(missing)}")
        if schema.get("additionalProperties") is False and set(value)-set(props): fail(f"{where}: unsupported additional properties {sorted(set(value)-set(props))}")
        for key,item in value.items():
            if key in props: validate_schema(item, props[key], root, f"{where}.{key}")
    if isinstance(value, list):
        for i,item in enumerate(value): validate_schema(item, schema.get("items", {}), root, f"{where}[{i}]")
    if isinstance(value, str) and "pattern" in schema and not re.fullmatch(schema["pattern"], value): fail(f"{where}: does not match required pattern")
    if isinstance(value, int) and not isinstance(value,bool) and "minimum" in schema and value < schema["minimum"]: fail(f"{where}: below minimum")

def validate_content(folder, manifest, schema):
    validate_schema(manifest, schema, schema)
    identifier = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{1,127}")
    for key in ("package_id", "package_version", "enterprise_id", "profile_version"):
        if not identifier.fullmatch(manifest[key]) or manifest[key] != manifest[key].strip(): fail(f"{key}: invalid identifier")
    declared=[]
    for section in ("files", "record_sets"):
        for item in manifest.get(section, []):
            rel=safe_path(item["path"])
            if rel == MANIFEST: fail("blueprint_manifest.json cannot be declared as content")
            if rel in declared: fail(f"duplicate declared path: {rel}")
            declared.append(rel); target=folder.joinpath(*PurePosixPath(rel).parts)
            if not target.is_file(): fail(f"missing declared file: {rel}")
            if section == "files" and item.get("sha256"):
                actual=hashlib.sha256(target.read_bytes()).hexdigest()
                if actual != item["sha256"]: fail(f"SHA-256 mismatch: {rel}")
    workbook=manifest.get("final_twin_spine_workbook")
    if workbook is not None and (safe_path(workbook) not in [x["path"] for x in manifest.get("files", [])]): fail("final_twin_spine_workbook must reference a declared file")
    return declared

def inventory(archive):
    with zipfile.ZipFile(archive) as zf:
        names=[safe_path(i.filename) for i in zf.infolist() if not i.is_dir()]
        if len(names) != len(set(names)): fail("duplicate ZIP paths")
        if names.count(MANIFEST) != 1: fail("ZIP must contain exactly one blueprint_manifest.json at root")
        return [(n, zf.getinfo(n).file_size, hashlib.sha256(zf.read(n)).hexdigest()) for n in names]

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("folder", type=Path); p.add_argument("--output", required=True, type=Path)
    for flag in ("package-id","package-version","enterprise-id","profile-version"): p.add_argument("--"+flag)
    a=p.parse_args(argv); schema=json.loads((HERE/"blueprint_manifest.schema.json").read_text())
    source=a.folder/MANIFEST
    if source.exists(): manifest=json.loads(source.read_text())
    else:
        values={k:getattr(a,k) for k in ("package_id","package_version","enterprise_id","profile_version")}
        if any(v is None for v in values.values()): fail("manifest missing; all four identifier options are required to construct it")
        manifest={"schema_version":"1.0", **values, "files":[], "record_sets":[]}
    declared=validate_content(a.folder, manifest, schema); a.output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(a.output,"w",zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(MANIFEST,json.dumps(manifest,indent=2,sort_keys=True)+"\n")
        for rel in declared: zf.write(a.folder.joinpath(*PurePosixPath(rel).parts),rel)
    rows=inventory(a.output)
    print(f"VALID: {a.output} ({len(rows)} files)")
    for name,size,digest in rows: print(f"{digest}  {size:>10}  {name}")
    return 0

if __name__ == "__main__":
    try: raise SystemExit(main())
    except (ValueError, json.JSONDecodeError, OSError, zipfile.BadZipFile) as exc: print(f"INVALID: {exc}",file=sys.stderr); raise SystemExit(2)
