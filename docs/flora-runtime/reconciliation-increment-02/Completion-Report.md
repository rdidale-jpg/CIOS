# Flora Increment 02 — governed import-to-model reconciliation

Baseline: `6f76511a5708e5e5820119c611af5b1d71258a63`, latest GitHub main at
start and final verification, including merged PR #530. Date: 8 November 2026.
This increment is delivered for PR review; no merge, deployment or migration is
performed. The delivery response supplies the PR URL and verified merge status.

## Ownership and exact change

The [pre-implementation ownership assessment](Ownership-and-Integration.md)
traces upload, validation, staging, review, mapping, dry-run, approval, canonical
acceptance and existing model ownership, including contract mismatches identified
before implementation.

Canonical Evidence and Observations still become authoritative only through
approved `CanonicalPromotionService._promote` effects. The new integration is
inside `execute_approved_plan`, after canonical writes and expected-mutation
reconciliation, before its success receipt/audit is committed. Actual canonical
Observation IDs returned by the existing repository are passed to the existing
`ObservationMemoryService.apply_observation`; affected snapshots remain owned by
`EnterpriseModelRepository`. No alternate ledger, projection service or canonical
store is created.

Only typed Observations with a factual vocabulary/attribute-prefix mapping and
same-enterprise supporting Evidence are admitted to current model projection.
Unsupported types/attributes, missing dates or missing/cross-enterprise/inactive
Evidence remain canonical where promotion is already authorised, but receive an
explicit partial projection result. Evidence alone is supporting material, not a
reason to manufacture an Observation or model update. Future or inactive
Observations remain historical rather than current support.

Approval/rationale, role and enterprise access, fingerprints, object-level review,
quarantine, immutable package retention and expected canonical mutation checks
remain in place. Target-owner checks are repeated at execution; canonical ID
collisions and supplied fingerprints cannot cross enterprise ownership.

## Files changed

- `blueprint_import/promotion.py`: reuse the model owner after canonical acceptance;
  scope/identity checks, temporal/provenance preservation, projection diagnostics,
  running receipts and compensated failure handling.
- `blueprint_import/views.py`: display canonical promotion and model reconciliation
  as distinct outcomes, including partial projection reasons.
- `memory/repository.py`: explicitly approved lifecycle corrections in the same
  ledger, retaining prior lifecycle state and approval lineage.
- `memory/service.py`: mark affected current support inactive through its existing
  owner, preserving the value/history and avoiding retirement of a different
  current value.
- `enterprise_canvas/service.py`: omit inactive model attributes from current
  Canvas support; underlying records remain retained.
- `tests/test_flora_import_model_reconciliation.py`: isolated synthetic regression
  and consumer/failure/retry tests.
- This completion report and the ownership/contract assessment.

## Before/after tests

The new regression file was copied unchanged into a separate checkout of the
baseline commit. Existing modules ran in separate processes with fresh temporary
runtime roots, using the same commands before and after.

| Selection | Baseline | Increment 02 |
| --- | --- | --- |
| 35 new regression tests | 30 failed, 5 passed | 35 passed |
| 14 relevant existing modules, 169 tests | 164 passed, 5 failed | 164 passed, the same 5 failed |
| Python compilation and `git diff --check` | — | Passed |

No newly failing existing node was observed. This is focused verification, not a
full-suite or live-deployment certification. The archive validation suite also
emits its existing duplicate-ZIP-member fixture warning.

The first fixture draft used a non-semver package version and was rejected by
existing manifest validation. It was corrected before recording the baseline;
this was a test fixture error, not an implementation defect.

Representative invocation, run from each checkout:

```sh
flora_test_data="$(mktemp -d /tmp/flora-reconciliation-02.XXXXXX)"
FLORA_DATA_DIR="$flora_test_data" FLORA_PILOT_DIR="$flora_test_data" PYTHONPATH=. \
  /workspace/cios-venv/bin/python -m pytest -q tests/test_flora_import_model_reconciliation.py
```

For every existing module in the following table, a new process and root were
used with the same environment and `python -m pytest -q "tests/$test_file"`.

| Existing module | Before and after |
| --- | --- |
| `test_flora_blueprint_import_registry.py` | 13 passed |
| `test_flora_blueprint_import_validation.py` | 17 passed, 1 warning |
| `test_flora_blueprint_import_review_planning.py` | 4 passed |
| `test_flora_blueprint_import_promotion.py` | 21 passed |
| `test_flora_blueprint_import_restage.py` | 2 failed, 3 passed |
| `test_flora_twin_import_lifecycle.py` | 3 passed |
| `test_flora_enterprise_memory.py` | 16 passed |
| `test_flora_intelligence_integrity.py` | 44 passed |
| `test_enterprise_intelligence_reasoning.py` | 7 passed |
| `test_flora_enterprise_canvas.py` | 3 failed, 12 passed |
| `test_flora_enterprise_canvas_feedback.py` | 13 passed |
| `test_evidence_provenance_applicability.py` | 4 passed |
| `test_flora_financial_canonicalisation.py` | 5 passed |
| `test_industry_twin_semantic_reconciliation.py` | 2 passed |

Pre-existing failures, reproduced unchanged:

- `tests/test_flora_blueprint_import_restage.py::test_restage_action_visible_to_owner_and_hidden_for_unauthorised`
- `tests/test_flora_blueprint_import_restage.py::test_regenerate_current_validation_quarantines_non_atomic_and_blocks_stale_approval`
- `tests/test_flora_enterprise_canvas.py::test_home_page_does_not_expose_synthetic_canvas_route`
- `tests/test_flora_enterprise_canvas.py::test_digital_twins_home_uses_governed_registry_and_import_breadcrumbs`
- `tests/test_flora_enterprise_canvas.py::test_mod_executive_commercial_canvas_read_model`

## Demonstrated scenarios

All fixtures use synthetic enterprise identifiers and statements. No easyJet or
other production intelligence was imported, amended or backfilled.

| Requested scenario | Demonstration in the committed regression file |
| --- | --- |
| A — approved financial Observation | `test_approved_financial_import_reaches_model_retrieval_and_canvas`: approved £120m revenue becomes the existing normalized model value `120000000`, with `OBS-1` / `EV-1` lineage |
| B — unapproved changes nothing | `test_receipt_staging_review_dry_run_and_approval_do_not_mutate_model`: no memory files through approval alone |
| C — identical import/replay | `test_identical_reimport_and_repeat_execution_are_idempotent`: one Observation and byte-equivalent model state |
| D — corroboration | `test_corroborating_import_merges_evidence_without_duplicate_confidence`: one Observation, two Evidence links, one confidence assessment |
| E — same-period conflict | `test_same_period_conflict_preserves_both_positions_and_reasoning_visibility`: both claims retained and both visible as contradictions |
| F — different periods | `test_different_period_is_not_a_conflict`: period-specific model attributes without false conflict |
| G — lifecycle/history | Retirement, expiry, supersession, package-order and old-fact replay tests preserve historical records while excluding old current truth; correction lineage is retained |
| H — failure/retry | Projection, success-receipt and audit failure tests prove compensation; successful retry after full compensation; failed compensation and running receipts block replay |
| I — enterprise scope | Target permissions, Evidence/Observation/generic ID collisions, fingerprints, cross-enterprise support and unaffected-snapshot tests |
| J — consumer path | The approved path reads the real existing model repository, bounded retrieval package and Canvas DTO; no opportunity, procurement or Material Pressure object is manufactured |

## Failure and recovery boundary

Importer threads are serialized by an in-process lock. The operation snapshots
existing canonical files, affected model snapshots and the import audit file,
then persists a running execution receipt before canonical writes. Canonical
updates precede model projection, so source record order does not determine
whether supporting Evidence can be resolved. Success receipt and success audit
publication are inside the compensated operation.

A caught write/projection/receipt/audit failure restores those file snapshots,
records a failed reconciliation and leaves package lifecycle promotion to the
existing route only after a successful service return. Fully compensated failures
can be retried using the existing approval; replay does not duplicate facts or
confidence history. Unsupported mappings are deliberate partial results, not
runtime success fabricated for model reconciliation.

If restoration fails, the receipt says `recovery_required` and backups are kept.
A running receipt or unrecovered backup blocks automatic replay; an operator must
review the affected execution receipt and `.bpi_backup` files, reconcile canonical
and model files under single-writer conditions, and only then clear the recovery
condition. There is no automatic production recovery or backfill in this PR.
Legacy backups without an unambiguous recovery history are also retained rather
than silently discarded.

This is **file compensation, not an ACID transaction**. The lock does not coordinate
other processes or non-import writers. There is no guarantee of multi-file atomic
read visibility or power-loss durability. The existing single-writer pilot must
quiesce competing writes and avoid consuming in-flight state. A hard interruption
requires recovery review; tests demonstrate controlled exceptions and persisted
interruption guards, not a production crash-recovery proof.

## Remaining limitations and unchanged boundaries

- This is not a general package-to-model mapper. Generic facts, business wrappers,
  model candidates and analytical classes do not acquire invented mappings.
- Existing completed promotions are not silently backfilled. Legacy receipts with
  no projection assessment remain `not_assessed` on replay. Legacy Observation ID
  or date/fingerprint mismatches require an explicit governed correction; the
  integration does not rewrite canonical identity.
- Current projection uses supported existing model logic; no new financial parser
  or economic inference is introduced. Retirement invalidates current authority
  without guessing a replacement historical value.
- The Increment 01 bounded retrieval and evidence/contradiction controls remain
  active; all 44 committed Increment 01 regression cases pass in the existing-test
  selection.
- No accepted ADR, canonical intelligence schema/store or owner is replaced.
  Additional projection fields extend only the existing operational promotion
  receipt, and lifecycle history uses existing provenance metadata.
- No scheduler, agent framework, Industry-to-Enterprise propagation, Material
  Pressure redesign, opportunity generation, Navigator, production migration or
  later lifecycle increment is implemented.

Increment 02 implementation and focused verification are complete for review.
The original checkout and production intelligence remain unchanged.
