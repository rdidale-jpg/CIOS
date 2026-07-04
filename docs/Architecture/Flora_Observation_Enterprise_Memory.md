# Flora Observation Enterprise Memory

Flora persists accepted Evidence as durable, schema-versioned Observations in a single canonical memory implementation under `cios/applications/flora/memory/`. The Observation ledger is the authoritative intelligence history; Enterprise Model JSON files are derived projections used by product views.

`ObservationMemoryService` owns the update path. It converts accepted Evidence into atomic Observations, deduplicates with an `obs-v1-` fingerprint over normalised enterprise ID, Observation type, statement, affected attribute and effective date, and excludes volatile collection timestamps. Reprocessing identical Evidence is idempotent; corroborating Evidence is attached to the existing Observation without erasing original lineage.

`ObservationRepository` stores one JSON record per ledger line, validates `schema_version`, detects malformed JSONL, and flushes/fsyncs appends. `EnterpriseModelRepository` writes projections through temporary files, flush, fsync and `os.replace`, with safe enterprise file identifiers based on normalised names plus hashes.

The minimal Enterprise Model projection currently covers enterprise identity, transformation programmes, financial pressure, technology events and procurement events. Attributes expose current value, Observation IDs, Evidence IDs, confidence, confidence history, freshness, last observed date, provenance, prior values and contradiction state. Unknowns expose stable ID, enterprise ID, question, affected domain, lifecycle status, review timing and related Observations.

The Observatory renders the model-backed Enterprise Memory panel from persisted projections. Reports are views; deleting or regenerating reports must not remove memory. Contradictory Observations coexist, affected attributes are marked contradicted, and output must not present contradicted state as certain.

The file-backed implementation is single-writer. Future migration to a database-backed store is expected when Flora requires concurrent writers, immutable event-level corroboration history, cross-enterprise graph queries, transactional governance or operational recovery tooling.
