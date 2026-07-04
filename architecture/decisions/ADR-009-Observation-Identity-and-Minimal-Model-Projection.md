# ADR-009: Observation Identity and Minimal Model Projection

Status: Proposed
Date: 2026-07-04

## Context

ADR-001 defines Observations as atomic intelligence units and ADR-002 defines the Enterprise Model as durable memory. Flora needs a first implementation choice for Observation identity, duplicate handling, persistence safety and current-state projection before the full Enterprise Model and database-backed graph exist.

Report artefacts are not memory. Accepted Evidence is transformed into durable Observations, and the Observatory renders a maintained Enterprise Model projection rather than reconstructing memory from raw Evidence or generated report text.

## Decision

Propose the Observation ledger as the authoritative intelligence history. It is stored as JSONL with one complete Observation record per line. Each record carries `schema_version = flora-memory-v1`; unsupported versions fail load rather than being interpreted silently.

Propose deterministic Observation identity using a versioned fingerprint with prefix `obs-v1-`. The fingerprint normalises and hashes enterprise ID, Observation type, atomic statement, affected Enterprise Model attribute and effective Observation date. Volatile collection timestamps are excluded. Reprocessing the same fact for the same effective date returns the same Observation; the same fact for a different effective date remains distinct.

Propose a minimal current-state Enterprise Model projection as a derived snapshot. Projection files also carry `schema_version = flora-memory-v1`. They are not canonical memory and may be rebuilt from the ledger if the snapshot is missing or suspected stale.

Corroborating Evidence mutates the existing Observation record to preserve all supporting Evidence IDs and update inspectable confidence metadata. This is a pragmatic file-backed mutation of an append-oriented ledger; future stores may represent corroboration as separate immutable events.

Contradictory Observations coexist. The projection marks the affected attribute as contradicted and retains conflicting Observation IDs. There is no automatic latest-wins resolution, and product views must not render contradicted state as certain.

Unknowns are first-class projection records with stable ID, enterprise ID, question or missing fact, affected domain, lifecycle status, created/review timing and related Observation IDs.

The file-backed repositories are single-writer. JSONL appends flush and `fsync` after each record. Enterprise Model snapshots are written by serialising to a temporary file, flushing, `fsync`ing and then using `os.replace`. Enterprise path names use a normalised slug plus hash to prevent traversal, invalid-character writes, case collisions, similarly named enterprise collisions and rename ambiguity.

## Snapshot rebuild expectations

The ledger should be sufficient to rebuild Enterprise Model snapshots. Rebuilds must apply accepted Observations in ledger order, retain Unknowns, retain contradiction metadata and avoid report artefacts as inputs.

## File-backed persistence limitations

This proposal deliberately avoids a database dependency. The trade-off is a single-process/single-writer constraint, linear scans for deduplication and whole-file rewrites when corroborating Evidence mutates an existing Observation.

## Future database migration triggers

Migrate to a database-backed store when any of the following become true:

- more than one writer can accept Evidence concurrently;
- ledger scans or snapshot rewrites become operationally expensive;
- immutable event history for corroboration and confidence changes is required;
- graph queries across enterprises become product-critical;
- human governance requires transaction boundaries, row-level audit, locks or recovery tooling.

## Alternatives considered

- Evidence ID as Observation ID: rejected because multiple Evidence records can corroborate one Observation.
- Report section as memory: rejected because reports must remain views.
- Semantic similarity deduplication: deferred because it requires governance thresholds not yet approved.
- Full append-only model events only: deferred because current Flora views need a simple projection.
- Database-backed store now: deferred until concurrency, query and governance needs justify the additional dependency and migration work.

## Consequences

- Safe retry and repeated collection are supported.
- Corroborating Evidence strengthens lineage without destroying provenance.
- Similar but differently worded claims can still create separate Observations until governed similarity matching is approved.
- Corrupt JSONL records and unsupported schemas fail loudly.
- Snapshot writes should not destroy the previous valid projection on failed serialisation or temporary-file write.
- Human architecture approval is required before treating this as the permanent identity strategy.
