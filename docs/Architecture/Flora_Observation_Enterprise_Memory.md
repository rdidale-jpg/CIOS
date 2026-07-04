# Flora Observation Enterprise Memory

Flora enterprise memory currently supports a single writer per memory store.

The Observation ledger is the durable intelligence history. Enterprise Model files are derived projections, written as atomic JSON snapshots for inspectability and restart durability. Reports and Observatory pages are views over the projected model state and can be deleted or regenerated without removing Observation or Enterprise Model memory.

Persisted Observations and Enterprise Model snapshots use `schema_version: 1`. Observation fingerprints use `fingerprint_schema_version: 1` and are based on stable normalised enterprise ID, domain, attribute, value and effective date. Volatile collection timestamps and evidence IDs are excluded so recollection is idempotent and corroboration strengthens the same Observation.

The current file-backed implementation detects malformed JSONL records during retrieval and raises an error instead of silently skipping corruption. Full rebuild tooling from the Observation ledger is deferred, but stored lineage is sufficient to support it later.
