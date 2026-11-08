# Flora Intelligence Integrity Hardening — Increment 01

Date: 8 November 2026. Baseline: GitHub `main` at
`bd22fd4aa4efffeaf9967140ca149e8bdb598fa6`, checked against the remote before
implementation and before publication. No intervening main-branch fix was found.

## Result and scope

The four original strict audit failures applicable to this increment now pass
as ordinary assertions. The three Material Pressure qualification/identity
failures remain outside this increment; `blueprint_import/material_pressure.py`
is unchanged. No claim is made that all seven original failures are resolved.
The new regression file also covers the requested missing-Evidence boundary in
Enterprise Intelligence validation, contradiction handling and replay integrity.

Changes reuse the existing memory ledger, Enterprise Model snapshots,
ClaimValidator, runtime audit/failure artifacts and presentation paths.
No canonical store, schema, agent framework, Navigator, ADR amendment,
production data migration or import/model reconciliation was introduced.
ADR-002, ADR-009, ADR-014, ADR-024 and ADR-026 ownership boundaries are retained.
No production intelligence was read or rewritten by these test runs.

## Corrected behaviors and regression evidence

All test names below are in `tests/test_flora_intelligence_integrity.py`.

| Boundary | Before | After | Regression evidence |
| --- | --- | --- | --- |
| Missing Evidence | An Observation ID could be treated as sufficient support without resolving its Evidence | Material claims need resolvable same-enterprise Evidence roots in the bounded package | `test_missing_evidence_cannot_support_a_governed_claim` |
| Commercial support | Valid pressure citations could accompany unsupported funded procurement, contract-value or buying-intent assertions | Existing validator checks commercial sections, nested claims and citations; consequential assertions need direct cited source support | `test_pressure_citations_do_not_support_commercial_facts`, `test_nested_invalid_citation_is_rejected_even_with_valid_outer_lineage` |
| Hypothesis boundary | An unsupported commercial statement could pass with valid citations | Explicitly labelled conditional hypotheses remain interpretations; a hypothesis label cannot launder a categorical funded fact | `test_supported_procurement_and_labelled_conditional_hypothesis_survive`, `test_hypothesis_label_cannot_launder_funded_fact` |
| Provider versus intelligence success | Provider success persisted even when claim validation failed | Audit distinguishes `provider_status`, `intelligence_status` and overall `status`; invalid intelligence is `Rejected` | `test_invalid_provider_output_is_audited_without_replacing_valid_brief`, `test_raw_missing_schema_is_provider_success_but_intelligence_rejection` |
| Rejected output retention | Invalid output could replace the successful brief | Raw rejected output and diagnostics remain in the existing per-request audit; existing last-failure artifact retains the result; the previous validated brief remains untouched | `test_invalid_provider_output_is_audited_without_replacing_valid_brief`, `test_validator_exception_is_fail_closed_and_retains_raw_output` |
| Presentation | Canvas trusted provider `Succeeded`; the brief page rendered invalid output | Both paths require validation eligibility; the newest failure remains visible instead of silently showing an older successful result | `test_canvas_and_brief_page_do_not_render_legacy_invalid_success` |
| Lifecycle filtering | Retired/expired support and derived model values could enter current reasoning | Ineligible Observations and dependent model values are excluded from the package; ledger records remain | `test_inactive_observation_and_derived_model_are_not_current_support`, `test_retired_current_value_cannot_borrow_prior_active_support` |
| Historical boundary | Current model attributes bypassed the evidence cut-off | Model dates and supporting Observation dates are checked against the cut-off; future state remains stored for lineage | `test_future_model_attribute_is_excluded_from_historical_package`, `test_future_observation_dates_do_not_support_historical_reasoning` |
| Contradictions | Opposing same-period numeric movements silently replaced the value | Both claims receive bidirectional unresolved conflict links; retrieval includes both positions as contradictions, not unqualified facts | `test_same_period_numeric_contradiction_is_bidirectional_and_visible` |
| Normal change | Conflict detection was not consistently period-aware | Effective period, enterprise, attribute, supplied scope and quarter/year context distinguish changes from conflicts | `test_different_effective_period_is_change_not_contradiction`, `test_same_quarter_different_year_or_scope_is_not_a_conflict` |
| Dates and supersession | Several supplied dates/supersession fields were dropped by the memory-service path | Existing provenance/lifecycle fields retain source/effective dates and explicit supersession; transient package context includes dates | `test_source_and_effective_dates_are_preserved_in_transient_context`, `test_explicit_supersession_resolves_current_support_without_erasing_history` |
| Replay | Repeated evidence appended confidence history and could restore an older value | Identical replay is unchanged; corroboration extends lineage without duplicating assessments; replay does not restore prior values | `test_duplicate_replay_does_not_mutate_model_or_confidence_history`, `test_corroboration_merges_lineage_without_inflating_confidence_history`, `test_replaying_old_claim_does_not_restore_superseded_value`, `test_lower_confidence_replay_does_not_rewrite_observation_or_model` |

## Before/after verification

All tests used synthetic fixtures or existing repository test fixtures in isolated
checkouts. Runtime data roots were temporary directories outside production data.
Each existing test module ran in its own Python process with a fresh data root,
using the same invocation before and after. No live provider credentials or
production deployment were required. Dependencies were already installed.

| Selection | Baseline | Increment 01 |
| --- | --- | --- |
| New regression file, 44 tests | 39 failed, 5 passed | 44 passed |
| Four applicable original strict audit probes, with `--runxfail` | 4 failed | 4 passed |
| 21 relevant existing test modules, 200 tests | 185 passed, 15 failed | 185 passed, same 15 failed |
| Python compilation and `git diff --check` | — | Passed |

No new failure was observed in the selected existing suites. This is focused
verification, not a full-suite or live-deployment certification.

The original audit probes were rerun from the retained isolated audit test file:

```sh
FLORA_DATA_DIR="$flora_test_data" FLORA_PILOT_DIR="$flora_test_data" PYTHONPATH=. \
  /workspace/cios-venv/bin/python -m pytest -q --runxfail \
  /workspace/work/audit-evidence/test_continuous_lifecycle_audit.py \
  -k 'retired_expired or future_model_state or unsupported_commercial_claim or invalid_brief_must'
```

Those four cases are also represented by committed regression tests; the external
audit file is not a required dependency of this PR.

The regression command, run unchanged in baseline and implementation checkouts:

```sh
flora_test_data="$(mktemp -d /tmp/flora-integrity-01.XXXXXX)"
FLORA_DATA_DIR="$flora_test_data" FLORA_PILOT_DIR="$flora_test_data" PYTHONPATH=. \
  /workspace/cios-venv/bin/python -m pytest -q tests/test_flora_intelligence_integrity.py
```

For each existing module listed below, the command was:

```sh
flora_test_data="$(mktemp -d /tmp/flora-integrity-01.XXXXXX)"
FLORA_DATA_DIR="$flora_test_data" FLORA_PILOT_DIR="$flora_test_data" PYTHONPATH=. \
  /workspace/cios-venv/bin/python -m pytest -q "tests/$test_file"
```

| Existing module | Baseline and after result |
| --- | --- |
| `test_enterprise_intelligence_reasoning.py` | 7 passed |
| `test_flora_enterprise_memory.py` | 16 passed |
| `test_flora_enterprise_canvas.py` | 3 failed, 12 passed |
| `test_flora_enterprise_canvas_feedback.py` | 13 passed |
| `test_flora_blueprint_import_promotion.py` | 21 passed |
| `test_flora_blueprint_import_review_planning.py` | 4 passed |
| `test_flora_financial_canonicalisation.py` | 5 passed |
| `test_flora_financial_fact_capture_v2.py` | 1 failed |
| `test_flora_deterministic_financial_refresh.py` | 5 failed, 2 passed |
| `test_flora_observatory.py` | 10 passed |
| `test_commercial_signal_architecture.py` | 20 passed |
| `test_material_pressure_qualification.py` | 6 passed |
| `test_evidence_provenance_applicability.py` | 4 passed |
| `test_flora_factual_twin_foundation.py` | 4 passed |
| `test_financial_intelligence_normalisation.py` | 7 passed |
| `test_flora_single_enterprise_calibration.py` | 5 passed |
| `test_bt_foundation_golden_facts.py` | 4 passed |
| `test_flora_financial_twin_hardening.py` | 4 passed |
| `test_memory_models.py` | 4 passed |
| `test_memory_repository.py` | 5 passed |
| `test_flora_live.py` | 6 failed, 32 passed |

## Pre-existing failures, retained separately

- `tests/test_flora_enterprise_canvas.py::test_home_page_does_not_expose_synthetic_canvas_route`
- `tests/test_flora_enterprise_canvas.py::test_digital_twins_home_uses_governed_registry_and_import_breadcrumbs`
- `tests/test_flora_enterprise_canvas.py::test_mod_executive_commercial_canvas_read_model`
- `tests/test_flora_financial_fact_capture_v2.py::test_route_level_golden_deterministic_refresh_second_refresh_zero_openai`
- `tests/test_flora_deterministic_financial_refresh.py::test_standard_refresh_fails_closed_without_ai_fallback`
- `tests/test_flora_deterministic_financial_refresh.py::test_route_level_golden_persists_evidence_and_idempotent`
- `tests/test_flora_deterministic_financial_refresh.py::test_structured_standard_refresh_uses_structured_adapter_and_no_fallback`
- `tests/test_flora_deterministic_financial_refresh.py::test_structured_missing_source_preserves_existing_trusted_state`
- `tests/test_flora_deterministic_financial_refresh.py::test_structured_missing_source_marks_fresh_ephemeral_absence`
- `tests/test_flora_live.py::test_repeated_collection_does_not_increase_evidence_count`
- `tests/test_flora_live.py::test_current_status_reports_unique_evidence_objects`
- `tests/test_flora_live.py::test_morning_edition_coverage_summary`
- `tests/test_flora_live.py::test_flora_v07_sources_page_and_morning_summary`
- `tests/test_flora_live.py::test_flora_v08_portfolio_radar_and_source_effectiveness`
- `tests/test_flora_live.py::test_rejected_claims_link_and_route_states`

Canvas failures concern existing home/navigation/executive-text expectations.
The six financial-refresh failures encounter existing provider/execution-policy
expectations. The six live-module failures include shared-state/path assumptions
and missing fixture metadata; all six reproduce before the change. These
failures have not been hidden, reclassified as passes or fixed in this increment.

## Remaining limitations

- Commercial admission is deterministic and conservative, not general semantic
  entailment. Consequential factual assertions need direct cited source wording;
  legitimate paraphrases may be rejected. This does not justify treating every
  possible novel phrasing as semantically verified. Label conditional hypotheses
  explicitly and retain cited support.
- Contradiction recognition covers explicit status opposition and comparable
  numeric assertions within supplied scope/period. It does not resolve arbitrary
  semantic disagreements. Both positions remain available for review.
- No historical model reconstruction or production backfill runs. Historical
  retrieval omits ineligible current snapshots rather than inventing past state.
  Existing unflagged conflicts are not automatically migrated.
- Material Pressure semantic identity, durable qualification, cross-Twin
  propagation, import/model reconciliation, economic exposure calculation,
  scheduling and Navigator work remain outside Increment 01.
- The existing file-backed, single-writer persistence assumptions remain.

## Completion

Increment 01 implementation and focused verification are complete for review.
The original checkout and production data are unchanged. The PR is not a merge,
deployment or migration. No later increment was started.
