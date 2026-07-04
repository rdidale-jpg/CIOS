# Migration: Observation-backed Enterprise Memory

Date: 2026-07-04

Flora has no database migration framework in the current runtime and existing tests guard against database-driver imports. This migration is therefore a deterministic file-backed migration:

- create `.flora_pilot/memory/observations.jsonl` on first Observation write;
- create `.flora_pilot/memory/enterprise_models/<enterprise>.json` on first Enterprise Model update;
- do not backfill historical reports because reports are not canonical Evidence;
- existing live evidence JSONL remains intact and is used only for new accepted Evidence-to-Observation processing.

Rollback is deleting the new memory files. Existing evidence, diagnostics, feedback and reports are unaffected.
