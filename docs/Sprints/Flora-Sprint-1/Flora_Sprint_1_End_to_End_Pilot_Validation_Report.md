# Flora Sprint 1 — End-to-End Pilot Validation Report

## Validation status
Synthetic representative CIOS Commercial Digital Twin package validation is implemented and covered by `tests/test_flora_cios_twin_pilot.py`. Real MOD execution remains an operator-local activity because the real archive and derived sensitive contents must not enter GitHub.

## Machine-readable pilot fields
```json
{
  "package_identity": "recorded from blueprint_manifest.json",
  "checksum": "sha256 recorded at package receipt",
  "package_profile_versions": ["CIOS Blueprint Package Import Profile v0.1", "package manifest profile_version"],
  "files_inspected": ["blueprint_manifest.json", "final Twin Spine workbook"],
  "worksheets_discovered": "recorded as validation warnings metadata",
  "candidate_records_staged": "summary count",
  "records_quarantined": "summary count including analytical projections and unsupported rows",
  "records_rejected": "summary count",
  "mappings_proposed": "dry-run plan effects",
  "review_decisions": "candidate review records",
  "canonical_records_created_or_updated": "promotion result counts",
  "analytical_projections_retained": "projection dry-run effects and Canvas projection DTOs",
  "unresolved_references": "validation summary",
  "conflicts": "dry-run effect conflicts",
  "unknowns_and_contradictions": "staged classifications retained",
  "expected_and_actual_mutation_counts": "promotion approval and execution result",
  "canvas_tiles_produced": "EnterpriseCanvas tiles",
  "lineage_paths_validated": "package, workbook, sheet and source record metadata",
  "feedback_workflow_validated": "EnterpriseCanvasFeedback record",
  "idempotent_repeat_run_result": "duplicate package receipt and repeat_no_change promotion",
  "access_control_result": "unauthorised import, Canvas and feedback access blocked",
  "cleanup_result": "operator removes FLORA_DATA_DIR after pilot",
  "remaining_gaps": "real MOD run is intentionally local-only"
}
```

## Human-readable result
The synthetic pilot proves package receipt, immutable checksum preservation, manifest validation, final Twin Spine workbook discovery, safe worksheet inspection, candidate staging, review, dry-run planning, explicit promotion, Canvas assembly, tile lineage inspection and governed feedback capture. Analytical projections remain staged/read-model data rather than canonical state. Unsupported rows are quarantined rather than invented into canonical classes.

## Sensitive-content controls
The report format records metadata and counts only. It must not include real MOD source text, pain-point details, workbook row contents, extracted files or generated sensitive fixtures.
