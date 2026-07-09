# Flora Sprint 1 PR3 — Review Mapping and Dry-Run Canonical Effects Completion Report

**Date:** 2026-07-09  
**Commit boundary:** governed candidate review, source-ID mapping and dry-run canonical effect planning only

## What now works

- Staged Blueprint candidates can be reviewed individually after PR2 staging.
- Review decisions are persisted as inspectable, append-only JSON records.
- External source IDs can be mapped to existing canonical IDs or represented as proposed, duplicate, conflict, unresolved, rejected, deferred, quarantined or unsupported mappings.
- Approved review sets can be planned through a dry-run canonical effect plan.
- The dry-run explicitly reports what would be created, updated, unchanged, mapped without mutation, duplicated, conflicted, contradicted, rejected, deferred, quarantined, unsupported or unresolved if a later promotion PR implemented execution.
- The dry-run reports expected canonical mutation counts for planning and actual canonical mutation count as zero.

## Review decisions supported

PR3 supports candidate-level decisions:

- `approve`
- `reject`
- `defer`
- `quarantine`
- `unsupported`

Each review decision stores candidate ID, import-run ID, package reference, original source ID, object class, reviewer identity, timestamp, rationale, validation findings, unresolved issues and mapped canonical target ID where applicable.

## Mapping behaviour

PR3 mapping supports:

- map to an existing canonical record;
- propose a new canonical record;
- propose an update to an existing record;
- mark duplicate;
- mark conflict;
- mark unresolved;
- reject;
- defer;
- retain in quarantine;
- unsupported.

Mappings are deterministic and inspectable. They preserve package lineage and original external IDs. They do not overwrite existing records and they do not silently resolve conflicts.

## Dry-run effect types

Dry-run planning supports effect types:

- `create`
- `update`
- `unchanged`
- `mapped`
- `duplicate`
- `conflict`
- `contradiction`
- `reject`
- `defer`
- `quarantine`
- `unsupported`
- `unresolved`
- `projection`

## Conflict and duplicate handling

Conflicts and duplicates remain visible in mapping and plan records. Conflict plans can preserve inspectable conflict details from candidate payloads. Duplicate records are classified as non-mutating dry-run effects.

## Idempotency

Repeated mapping and planning calls over the same package, candidate set, review decisions and mappings reuse deterministic identities. Equivalent repeated dry-runs do not create duplicate plan files.

## Storage paths

No database migration was added. New file-backed state is stored at:

- `blueprint_import/reviews/{import_run_id}/{review_decision_id}.json`
- `blueprint_import/mappings/{import_run_id}/{mapping_id}.json`
- `blueprint_import/plans/{import_run_id}/{plan_id}.json`
- existing `blueprint_import/audit/events.jsonl` events for review, mapping and planning audit records

## Security

Review, mapping and planning APIs preserve Flora's existing product-session style checks. Mutating review/mapping/planning state requires:

- authenticated `X-Flora-User` or equivalent cookie;
- enterprise access through `X-Flora-Enterprises` or equivalent cookie;
- `package.review` or `blueprint_import_admin` role.

Unauthorised users cannot record review decisions, create mappings or create dry-run plans.

## Tests and results

PR1, PR2 and PR3 Blueprint tests were run together:

```text
pytest -q tests/test_flora_blueprint_import_registry.py tests/test_flora_blueprint_import_validation.py tests/test_flora_blueprint_import_review_planning.py
21 passed, 1 warning
```

The warning is the existing intentional duplicate-ZIP fixture warning used to test duplicate package-member detection.

## Repository-wide baseline comparison

The repository-wide baseline supplied for this PR is:

- 48 failed;
- 495 passed;
- 2 skipped;
- 1 warning.

A repository-wide run after PR3 reported 48 failed, 499 passed, 2 skipped and 1 warning. This preserves the supplied failure count baseline of 48 failures and increases passing tests by the PR3 coverage. No new repository-wide regressions were introduced by PR3.

## Deferred canonical promotion work

Still deferred:

- actual canonical writes;
- canonical promotion execution;
- promotion rollback;
- reversal of canonical changes;
- Source, Unknown, Contradiction and human-knowledge owner expansions beyond dry-run planning;
- Enterprise Canvas;
- UI screens;
- MOD-specific business logic;
- canonical Pain Point, Burning Platform or Transformation Pressure objects.

## Canonical mutation confirmation

PR3 does not write canonical Evidence, Observation or Enterprise Model state. Dry-run plans report actual canonical mutation count as zero.

## Enterprise Canvas confirmation

Enterprise Canvas remains deferred and is not implemented by PR3.
