# Flora Blueprint Import package contract

This directory is the complete, portable producer boundary for Flora's manual **Import Twin** function. The build exports `blueprint_manifest.schema.json` from Flora's canonical `BlueprintManifest`; do not edit or independently maintain that schema. The Researcher needs only this directory and Python 3, not the CIOS repository or `cios.applications`.

## Package layout and rules

The ZIP has no enclosing directory. It contains exactly one `blueprint_manifest.json` at its root, plus governed Twin content at the relative paths declared by the manifest. Schema version `1.0` is supported. Required identifiers are `package_id`, `package_version`, `enterprise_id`, and `profile_version`; each is 2–128 characters, starts alphanumerically, and thereafter uses only letters, digits, `_`, `.`, `:`, or `-`.

Optional `final_twin_spine_workbook` names a declared file. `files` declares objects with `path` and optional `role`, `required` (default false), and lowercase 64-hex `sha256`. Every declared file must be present when packaging (regardless of `required`). `record_sets` declares `record_class`, `path`, non-negative `count`, and optional `required`; its content path must also exist. Record-set content intended for Flora candidate inspection uses NDJSON. Checksums cover the exact content bytes, not the ZIP member.

All paths are normalized relative POSIX paths (`content/file.json`): no absolute paths, backslashes, empty/dot/`..` segments, or non-normalized aliases. Duplicate declarations and duplicate ZIP entries are rejected. `blueprint_manifest.json` cannot be declared as content. Additional manifest, file, and record-set properties are unsupported and rejected.

## Build and validate

Start with `blueprint_manifest.example.json`, copy it to the content folder as `blueprint_manifest.json`, set its identifiers and declarations, then run:

```sh
python3 build_flora_import.py CONTENT_FOLDER --output flora-import.zip
```

Alternatively construct the minimal manifest when none exists:

```sh
python3 build_flora_import.py CONTENT_FOLDER --output flora-import.zip \
  --package-id example-twin --package-version 1.0.0 \
  --enterprise-id example-enterprise --profile-version 1.0
```

The utility loads the adjacent exported schema, validates the manifest, verifies declarations and checksums, writes a root manifest, reopens and validates the ZIP, and prints `VALID` followed by its inventory. The resulting ZIP is a mission output: submit it manually to Flora separately from the governed release/checkpoint package; do not add generated ZIPs to the repository.

## Four distinct artefacts

* **Twin release manifest** governs the research release and its lineage.
* **Researcher checkpoint package** preserves resumable mission state and governed evidence.
* **Flora Blueprint import manifest** is only `blueprint_manifest.json`, governed by the exported Flora schema.
* **Flora Import ZIP** is the separate archive accepted by manual Import Twin; it does not replace or silently promote either research artefact.
