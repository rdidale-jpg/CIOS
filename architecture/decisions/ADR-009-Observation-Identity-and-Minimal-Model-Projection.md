# ADR-009: Observation Identity and Minimal Model Projection

Status: Accepted
Date: 2026-07-04
Accepted: 2026-07-04

## Context

ADR-001 defines Observations as atomic intelligence units and ADR-002 defines the Enterprise Model as durable memory. Flora needed a first implementation choice for Observation identity, duplicate handling, persistence safety and current-state projection before the full Enterprise Model and database-backed graph exist.

The merged Flora Observation-backed Enterprise Memory implementation has been reviewed against the runtime and accepted with pilot constraints. Report artefacts are not memory. Accepted Evidence is transformed into durable Observations, and the Observatory renders a maintained Enterprise Model projection rather than reconstructing memory from raw Evidence or generated report text.

Related implementation and architecture references:

- [Flora Observation Enterprise Memory](../../docs/Architecture/Flora_Observation_Enterprise_Memory.md)
- [Observation-backed Enterprise Memory migration](../../docs/Architecture/migrations/2026-07-04-observation-enterprise-memory.md)
- [EI-001 — Enterprise Model Specification](../enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md)
- [EI-012 — Enterprise Observation Model](../enterprise-intelligence/volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md)

## Decision

The Observation ledger is the authoritative durable history of accepted enterprise intelligence. Enterprise Model files are governed current-state projections derived from Observations and projection rules; they are not an independent competing source of truth. Reports and Observatory panels are views over Evidence, Observations or Enterprise Model projections.

Persisted Observation records and Enterprise Model snapshots carry `schema_version = flora-memory-v1`. Unsupported schema versions fail validation and must not be interpreted silently.

Observation identity uses a deterministic, versioned fingerprint with prefix `obs-v1-`. The fingerprint normalises and hashes stable fields: enterprise identity, Observation type, atomic statement, affected Enterprise Model attribute and effective Observation date. Volatile collection timestamps are excluded. Reprocessing the same fact for the same effective date returns the same Observation; the same fact for a different effective date remains distinct.

The minimal Enterprise Model projection stores governed current state while retaining inspectable lineage from Enterprise Model attribute to Observation ID to Evidence ID. Projected attributes retain current value, Observation IDs, Evidence IDs, confidence, confidence history, freshness, last observed date, provenance, prior values and contradiction state where implemented.

For the pilot, an Observation is a durable mutable intelligence record. Corroborating Evidence updates the existing Observation record and the current file-backed repository performs a whole-ledger rewrite for that update. This preserves stable Observation identity, supporting Evidence IDs, confidence history through the projection, and Observation lineage. The current implementation is therefore not a complete immutable event history and must not be described as a strictly append-only event ledger. A future persistence implementation may represent Observation changes through immutable versions or append-only events when audit, concurrency or scale requirements justify it.

Contradictory Observations coexist. The projection marks the affected attribute as contradicted, retains the existing Observation IDs and conflicting Observation IDs, avoids automatic latest-wins resolution, and product views must not render contradicted state as certain.

Unknowns are first-class projection records with stable ID, enterprise ID, question or missing fact, affected domain, lifecycle status, created/review timing and related Observation IDs. Unknown model state must remain explicit and must not be silently filled with generated inference.

The file-backed repositories are single-process / single-writer. They do not provide multi-writer, distributed or database-backed concurrency guarantees.

JSONL appends flush and `fsync` after each Observation record. Malformed JSONL records are detected during load. Enterprise Model snapshots are written by serialising to a temporary file, flushing, `fsync`ing and then using `os.replace` for atomic replacement. Enterprise path names use a normalised slug plus hash to prevent traversal, invalid-character writes, case collisions, similarly named enterprise collisions and rename ambiguity. Current recovery is limited to validation failure, preserving the previous snapshot on failed atomic replacement and operator intervention; no database recovery tooling exists.

## Snapshot rebuild expectations

Enterprise Model snapshots are conceptually rebuildable from durable Observations and projection rules. Rebuilds must apply accepted Observations in ledger order, retain Unknowns, retain contradiction metadata and avoid report artefacts as inputs. Automated operational projection replay and rebuild tooling is deferred; this ADR accepts the architectural expectation, not a production recovery command.

## File-backed persistence limitations

This decision deliberately accepts file-backed persistence for the pilot to avoid a database dependency. The trade-off is a single-process/single-writer constraint, linear scans for deduplication and whole-file rewrites when corroborating Evidence mutates an existing Observation. Enterprise Model coverage remains intentionally narrow.

## Future database migration triggers

Migrate away from file-backed persistence when any of the following become true:

- multiple concurrent writers can accept Evidence;
- ingestion volume makes linear ledger scans unacceptable;
- ledger scans or snapshot rewrites become operationally expensive;
- stronger transactional guarantees are required;
- richer immutable audit history for corroboration and confidence changes is required;
- cross-enterprise queries become product-critical;
- projection replay or rebuild requirements become operational rather than conceptual;
- operational backup, restore and recovery requirements exceed file-backed operator procedures;
- human governance requires transaction boundaries, row-level audit, locks or database recovery tooling.

## Alternatives considered

- Evidence ID as Observation ID: rejected because multiple Evidence records can corroborate one Observation.
- Report section as memory: rejected because reports must remain views.
- Semantic similarity deduplication: deferred because it requires governance thresholds not yet approved.
- Full append-only model events only: deferred because current Flora views need a simple projection and the pilot mutates durable Observation records during corroboration.
- Database-backed store now: deferred until concurrency, query and governance needs justify the additional dependency and migration work.

## Consequences

Positive consequences:

- Flora now has durable Observation-backed enterprise memory.
- Enterprise Model state remains independent of reports.
- Observation identity is deterministic and versioned.
- Model attributes retain inspectable Evidence lineage.
- Unknowns and contradictions remain explicit.
- The implementation remains dependency-light for the pilot.
- The architecture can evolve toward database-backed persistence later.

Negative consequences and constraints:

- File-backed storage is single-writer.
- Deduplication uses linear ledger scans.
- Corroboration currently rewrites the Observation ledger.
- Observation mutation is not a complete immutable event history.
- Enterprise Model coverage remains intentionally narrow.
- Automated projection replay and rebuild tooling are deferred.
- File-backed storage is not the target architecture for concurrent production scale.
- Corrupt JSONL records and unsupported schemas fail loudly and require operator remediation.
