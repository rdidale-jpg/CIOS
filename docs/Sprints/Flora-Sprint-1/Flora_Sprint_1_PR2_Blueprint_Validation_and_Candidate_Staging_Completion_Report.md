# Flora Sprint 1 PR2 — Blueprint Validation and Candidate Staging Completion Report

**Date:** 2026-07-09
**Commit boundary:** governed Blueprint package validation and candidate staging only

## Audit boundary confirmation

`docs/Architecture/Flora_Blueprint_Import_Code_Binding_Audit_v0.1.md` recommends PR2 as the Adapter Boundary and Candidate Staging step after PR1 package receipt and registry. This implementation matches that next bounded boundary and does not expand into canonical promotion, mapping review, Enterprise Canvas, Provider Fit, opportunity logic, MOD-specific business rules, or UI work.

## What now works

- Flora validates the exact immutable archive stored by PR1 before processing.
- Flora verifies the archive checksum against the PR1 package registry record.
- Flora validates `blueprint_manifest.json` identity against the registry record.
- Flora detects missing required files, duplicate archive members, unexpected files, invalid JSON records, unsupported classes, unresolved synthetic references and unsafe archive paths.
- Flora discovers supported `.ndjson` record sets declared by the manifest and stages candidate import records for review.
- Flora retains package-relative source file and structured source location, including sheet or line location where supplied.
- Flora writes inspectable staging summaries and candidate JSON records under `FLORA_DATA_DIR/blueprint_import/staging/{import_run_id}/`.
- Flora supports partial staging: valid candidates can be accepted into staging while invalid, projection-only or unsupported records are quarantined.
- Repeat validation of the same package reuses the existing staging summary and does not duplicate candidate records.
- Dry-run summaries always report `canonical_mutations: 0`.

## Existing PR1 capabilities reused

- PR1 package registry records and package references.
- PR1 immutable archive path and package checksum.
- PR1 import-run identifiers.
- PR1 JSON/JSONL storage pattern and audit ledger.
- PR1 safe archive member path validation.
- Existing Flora data-root helpers and access-control header/cookie patterns.

## Candidate classes supported

Canonical-eligible classes are staged only: `enterprise`, `twin`, `source`, `evidence`, `observation`, `entity`, `relationship`, `enterprise_model_candidate`, `unknown`, `contradiction`, `human_knowledge`, `refresh_trigger`, and `publication_reference`.

Projection-only classes are retained as quarantined staging records rather than canonical objects: `pain_point`, `current_response`, `response_effectiveness`, `residual_pain`, `burning_platform`, `transformation_pressure_view`, `priority_disposition`, `stakeholder_hot_button`, `solution_pattern`, and `executive_publication`.

Unsupported classes, including `provider_fit`, remain quarantined and reported.

## Validation and quarantine behaviour

- Package-level checksum mismatch stops processing.
- Manifest identity mismatches are reported as validation errors and produce an inspectable rejected package-metadata staging record.
- Missing required files and duplicate package files are reported as validation errors.
- Supported candidate classes with required envelope fields are accepted into staging.
- Missing external IDs, unsupported classes, projection-only classes and unresolved references are quarantined.
- Invalid record JSON is rejected.
- No missing values are inferred or invented.

## Storage paths

No database migration is introduced. New file-backed state is stored at:

- `blueprint_import/staging/{import_run_id}/summary.json`
- `blueprint_import/staging/{import_run_id}/candidates/{candidate_record_id}.json`
- existing PR1 `blueprint_import/audit/events.jsonl` events for validation staging and validation failure.

## Security treatment

- Validation reads the exact immutable PR1 archive rather than copied or user-supplied bytes.
- Archive checksum verification happens before parsing.
- Archive contents are inspected with safe ZIP APIs; contents are never executed.
- Unsafe archive paths remain rejected by the PR1 receipt boundary and the PR2 validator reuses the same path validation.
- Candidate inspection requires a product-session user with package-review/admin role and matching enterprise access when headers are supplied.
- Package contents are not exposed through a UI in this PR.

## Tests and results

- `pytest -q tests/test_flora_blueprint_import_registry.py tests/test_flora_blueprint_import_validation.py` passed: 17 tests, 1 duplicate-ZIP fixture warning.
- Repository-wide baseline command `pytest -q` currently reports 48 failed, 495 passed, 2 skipped, 1 warning. The failures are in pre-existing financial intelligence, web route/static export and live evidence tests, not in the new Blueprint import test module.

## Remaining deferred work

- Mapping review and proposed canonical effects.
- Canonical Evidence, Observation, Source, Relationship, Unknown, Contradiction, Human Knowledge, or Enterprise Model promotion.
- Canonical promotion ledgers and reversal.
- Analytical projection rendering and lineage navigation.
- Enterprise Canvas read model and UI.
- MOD-specific business adapter rules.
- Provider Fit, opportunity, pursuit, and commercial-action logic.
