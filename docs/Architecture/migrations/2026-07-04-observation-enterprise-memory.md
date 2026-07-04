# 2026-07-04 Observation Enterprise Memory Migration

This pilot introduces file-backed Observation memory for Flora:

1. accepted evidence creates durable Observation records in `observations.jsonl`;
2. Enterprise Model JSON files are derived projections;
3. Observatory memory views read the persisted projection rather than raw evidence;
4. schema version `1` is written to persisted Observation and Enterprise Model records.

Current operational constraint: single writer per memory store. Migration to a database-backed store is deferred until concurrency, immutable event auditing or cross-enterprise query requirements demand it.
