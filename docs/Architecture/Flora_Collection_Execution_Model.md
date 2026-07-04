# Flora Collection Execution Model

## Browser/request boundary

`POST /live/collect/start` now creates a run manifest state with a non-empty run ID, records the BT profile, mode, pass and start time, then submits the collection to a bounded in-process worker. The response is a prompt `303` redirect to `/live/collect/progress?run_id=...`; source retrieval, parsing, Evidence extraction, Observation creation and Enterprise Model updates do not run in the response-rendering path.

The legacy blocking behaviour was caused by the web handler calling `collect(...)` directly before redirecting. The browser therefore waited for network retrieval, document parsing and memory writes and only saw progress after refresh.

## Worker behaviour

The pilot worker uses a `ThreadPoolExecutor(max_workers=1)` and an in-process lock. This enforces one file-backed writer at a time and prevents duplicate simultaneous submissions. It is intentionally pilot-grade: it is not a durable job queue and does not claim production survivability across process death.

Run states are explicit: `queued`, `starting`, `collecting`, `parsing`, `extracting_evidence`, `accepting_evidence`, `creating_observations`, `updating_model`, `completed`, `completed_with_no_accepted_intelligence`, `failed` and `interrupted`.

## Status persistence and polling

Run state is persisted in `.flora_pilot/live_evidence/collection_run_state.json`. The progress page polls `/live/collect/status` and renders run identity, scope, current stage/source, source counts, document/PDF counts, Evidence dispositions, Observation counts, model-update counts, warnings and concise errors. Polling stops at terminal states.

## Single-writer lock

The worker accepts one active run. If a run is not terminal, subsequent submissions return the existing state with `duplicate_blocked` rather than starting concurrent file writes.

## Interruption behaviour

The status endpoint checks for stale in-progress state. If a run is older than the configured threshold and the process is no longer actively updating it, it is marked `interrupted` with a terminal progress state so the UI does not spin forever after a restart.

## Deployment limitations and migration trigger

This model is suitable for a single-process, file-backed pilot. Migrate to a durable queue and database when Flora needs multiple workers, cross-process locking, resumable jobs, guaranteed retry semantics, or production-grade collection SLAs.
