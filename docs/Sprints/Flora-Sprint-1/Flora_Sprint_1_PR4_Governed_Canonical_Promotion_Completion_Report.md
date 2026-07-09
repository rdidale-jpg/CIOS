# Flora Sprint 1 PR4 — Governed Canonical Promotion Completion Report

**Date:** 2026-07-09
**Commit boundary:** controlled canonical promotion of already reviewed and approved dry-run plans only

## Audit boundary confirmation

The audit's next bounded implementation step is governed canonical promotion: explicit approval of a reviewed dry-run plan, authorised execution, append-only promotion ledgering, idempotency, expected-versus-actual mutation reporting and atomic failure handling. PR4 follows that boundary and does not implement Enterprise Canvas, visual review screens, MOD-specific logic, Provider Fit, pursuit/opportunity logic or new canonical analytical projection objects.

## What now works

- A dry-run canonical effect plan can be explicitly approved by an attributable approver.
- Promotion execution requires an authorised actor with promotion permission.
- Approval is invalidated when the approved plan, review decisions, mappings or package checksum changes.
- Blocking conflict effects prevent approval.
- Approved create/update effects can write through existing canonical repositories.
- Non-mutating planned outcomes are preserved in the execution result without canonical writes.
- Promotion execution records expected and actual mutation counts.
- Repeat execution of the same approved plan returns a no-change repeat result.
- Failed execution restores touched canonical JSONL files and records a failed append-only execution event.

## Canonical classes supported

PR4 supports only canonical classes with existing repository and object contracts:

- `evidence`, through `EvidenceRepository`.
- `observation`, through `ObservationRepository` when the payload satisfies the existing Observation dataclass contract.

## Classes deferred

The following remain deferred because the repository does not yet expose safe authoritative owners or contracts for PR4 promotion:

- Source registry canonical writes;
- Unknown as standalone import promotion beyond existing Enterprise Model internals;
- Contradiction owner expansion;
- Human-Supplied Knowledge as a distinct canonical store;
- Entity and relationship graph persistence;
- Enterprise Model candidate updates;
- Refresh triggers;
- Publication references;
- Pain Point, Burning Platform, Transformation Pressure and all other analytical projections;
- Provider Fit, opportunity, pursuit and commercial-action objects.

## Approval behaviour

Approvals record the approved plan ID, import-run ID, package reference and checksum, approver identity, timestamp, rationale, approved effects, expected mutation count, accepted warnings and invalidation condition. Approval requires the existing Flora user/enterprise access pattern plus `candidate.promote` or `blueprint_import_admin` role.

## Promotion behaviour

Only approved `create` and `update` effects for supported classes mutate canonical state. `mapped`, `unchanged`, `duplicate`, `reject`, `defer`, `quarantine`, `unsupported`, `unresolved`, `projection` and `conflict` outcomes do not mutate canonical stores.

## Lineage retained

Created/updated canonical records retain package, import-run, candidate, review, mapping, plan, approval, source-location, source-fingerprint, approver, executor and promotion-time lineage. Evidence updates also retain the prior canonical version in lineage.

## Conflict treatment

Blocking conflict effects prevent approval. Promotion does not silently overwrite existing canonical records simply because an external ID matches; updates must be explicit in the approved dry-run plan.

## Ledger behaviour

Approvals and execution results are written as append-only Blueprint import audit events. Execution result files record records created, updated, mapped, unchanged, skipped, blocked and failed, expected and actual mutation counts, rollback/compensation result and final status.

## Idempotency

A repeated execution of the same approved successful plan returns a `repeat_no_change` result and does not append duplicate canonical Evidence or Observation records.

## Atomicity and rollback

PR4 uses the safest existing file-backed repository mechanism: backups of the touched canonical JSONL files are taken before promotion. On failure, those files are restored and a failed execution result records the compensation outcome.

## Reversal status

Reversal execution is deferred. PR4 preserves ledger and lineage information needed for a future reversal PR but does not delete or reverse canonical intelligence.

## Storage or migration impact

No database migration is introduced. New JSON files are stored under:

- `blueprint_import/promotion/approvals/{import_run_id}/`
- `blueprint_import/promotion/executions/{import_run_id}/`

Existing canonical JSONL stores are used for supported Evidence and Observation writes.

## Security treatment

PR4 preserves existing Flora product-session access checks and separates approval/execution from review by requiring promotion roles. Unauthorised actors cannot approve or execute canonical promotion.

## Tests and results

PR1, PR2, PR3 and PR4 Blueprint tests were run together:

- `pytest -q tests/test_flora_blueprint_import_registry.py tests/test_flora_blueprint_import_validation.py tests/test_flora_blueprint_import_review_planning.py tests/test_flora_blueprint_import_promotion.py` — 28 passed, 1 duplicate-ZIP fixture warning.

Repository-wide baseline comparison is recorded in the PR completion response. The supplied baseline is 48 failed, 499 passed, 2 skipped and 1 warning.

## Remaining gaps

- Owner-backed promotion for Source, Unknown, Contradiction, Human-Supplied Knowledge, graph entities/relationships and Enterprise Model candidates.
- Full safe reversal execution.
- Promotion history UI.
- Enterprise Canvas read model and UI.

## Enterprise Canvas confirmation

Enterprise Canvas remains deferred. PR4 implements no Canvas route, UI, tile model or analytical projection canonicalisation.
