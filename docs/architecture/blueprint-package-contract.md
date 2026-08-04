# Blueprint package contract and receipt path

## Root cause and canonical owner

Before this change, Flora's implemented contract existed only in
`blueprint_import/manifest.py`: four identifiers were extracted by a hard-coded
parser while optional file declarations were interpreted later by the validator.
There was no exported schema or producer API. The rejected TEL-001 manifest was
therefore inferred from the unrelated CIOS Twin release shape, not serialized
from Flora's implementation.

`cios/applications/flora/blueprint_import/contract.py::BlueprintManifest` is now
the single canonical owner. It is a strict Pydantic model. Flora receipt parses
that model, builders call `build_manifest`, and consumers may export JSON Schema
with `BlueprintManifest.model_json_schema()`; no separately maintained schema is
committed.

## Exact profile 1.0 structure

The root, case-sensitive `blueprint_manifest.json` is a JSON object. Unknown
properties are prohibited. Required string identifiers are `package_id`,
`package_version`, `enterprise_id`, and `profile_version`; each is 2-128
characters, starts alphanumerically, and thereafter uses alphanumerics, `_`,
`.`, `:`, or `-`. `schema_version` is optional for compatibility, defaults to
`1.0`, and rejects any explicitly unsupported value.

Optional `files` is an array of strict objects: required `path`; optional `role`,
`required` (default false), and lowercase 64-hex `sha256`. Optional `record_sets`
contains strict objects with `record_class`, `path`, non-negative `count`, and
optional `required`. Optional `final_twin_spine_workbook` must name an entry in
`files`. All paths are normalized relative POSIX paths: absolute paths,
backslashes, `..`, empty paths, and duplicates within either declaration list
are rejected. A supplied checksum is checked against Flora's archive inventory.

## Receipt and validation path

The upload view authorizes the request before `BlueprintPackageRegistry.receive`.
Receipt calculates the archive checksum, calls `inspect_zip_inventory` (ZIP
format, member type, path traversal, duplicate/size/ratio safety), detects the
package contract, reads the one exact root manifest, parses `BlueprintManifest`,
preserves immutable bytes, and only then creates receipt/run records. Errors are
recorded in the audit ledger without a receipt record. `validate_and_stage`
rechecks immutable bytes, reparses the same model, verifies identity, declared
file presence and checksums, rejects malformed records, and creates candidate
staging only. Promotion remains a separate explicitly approved service.

Researcher preflight command:

```bash
python tools/blueprints/validate_package.py path/to/package.zip
```

It uses a temporary data directory and the real Flora receipt and inspection
classes. Generated ZIPs belong in workflow artifacts, never source control.

## TEL-001 status

No governed TEL-001 Wave 5 Blueprint payload is present in this repository; the
checked-in TEL-001 files are research-mission instructions, not the governed
intelligence package. Consequently this change deliberately does not infer a
payload, alter intelligence, or commit/generate a ZIP. The artifact workflow can
run the command above when the existing governed payload is supplied.
