# ADR-009 — Observation Identity and Minimal Model Projection

**Status:** Proposed
**Date:** 2026-07-04
**Owner:** Rob / CIOS

## Context

Flora is moving from report-centred output toward Observation-backed Enterprise Memory. The pilot file-backed store must be deterministic, inspectable and recoverable without expanding scope into graph infrastructure, database migration or recommendation behaviour.

## Decision

The durable source of truth for this pilot is the Observation ledger. Enterprise Model snapshot files are derived projections of persisted Observations and projection rules. Reports and Observatory pages are views over projected model state; they must not become memory or an independent competing source of truth.

Snapshot rebuild from the ledger is conceptually required but deferred as a complete operational feature. The persisted lineage is sufficient for rebuild because every projected attribute stores source Observation IDs, and every Observation stores evidence IDs and identity metadata.

## Observation identity

Observation fingerprints use `fingerprint_schema_version: 1` and stable normalised fields:

- stable internal `enterprise_id`, not display name;
- model `domain`;
- model `attribute`;
- observed `value`;
- material `effective_date` when known.

Collection timestamps and evidence collection times are excluded because they are volatile. Evidence IDs are excluded from the fingerprint so corroborating evidence strengthens the same Observation instead of creating duplicates.

## Schema versioning

Persisted Observation records and Enterprise Model snapshots include `schema_version: 1`. Readers must reject unsupported future versions rather than silently interpreting them.

## Corroboration and append-only behaviour

The pilot ledger stores one JSON Observation record per line. New Observations are appended. Corroboration of an existing Observation updates that Observation record in place by preserving existing evidence IDs, adding new evidence IDs and recording confidence changes in `confidence_history`.

This is an explicit pilot compromise: it is mutable-record provenance, not a full event-sourced ledger. A later database-backed store should split Observation creation and corroboration into immutable events if audit depth requires it.

## Contradictions

Contradictory Observations persist independently. Projection does not resolve conflicts by latest-wins. The affected Enterprise Model attribute records `contradiction_state: contradicted` and links all competing Observation IDs so the Observatory can avoid rendering the claim as certain.

## Concurrency model

Flora enterprise memory currently supports a single writer per memory store. The file-backed repositories do not claim multi-process or distributed writer safety.

## Persistence safety

Enterprise Model snapshots use atomic replacement: serialise, write a temporary file, flush/fsync, then replace the destination. JSONL ledger retrieval raises an error for malformed records or malformed trailing lines rather than silently ignoring corruption.

## File-backed limitations and migration triggers

The file-backed store is appropriate for pilot maturity and local inspectability. Migration to a database-backed store is triggered by any of the following:

- multiple concurrent writers per memory store;
- required immutable event history for corroboration or contradiction review;
- large ledger sizes that make full-scan projection too slow;
- cross-enterprise query requirements;
- operational backup, locking, auditing or recovery requirements beyond atomic local files.

## Consequences

- Observation ledger authority is explicit.
- Enterprise Model snapshots are rebuildable projections, not independent truth.
- Reports can be deleted or regenerated without deleting memory.
- Unknowns and contradictions remain first-class model state.
- Human architecture approval is required before this ADR can become Accepted.
