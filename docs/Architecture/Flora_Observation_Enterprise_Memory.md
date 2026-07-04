# Flora Observation-backed Enterprise Memory Foundation

Implemented on 2026-07-04.

Accepted Evidence now creates durable atomic Observations in `.flora_pilot/memory/observations.jsonl`. Observation identity is deterministic: enterprise ID, observation type, atomic statement and affected model attribute are normalised and SHA-256 hashed. Reprocessing the same claim returns the existing Observation; new supporting Evidence IDs are appended as corroboration without deleting original provenance.

The minimal Enterprise Model projection is stored per enterprise under `.flora_pilot/memory/enterprise_models/`. Implemented domains are enterprise identity, transformation programmes, financial pressure, technology events and procurement events. Each attribute stores current value, Observation IDs, reachable Evidence IDs, confidence, freshness, last observed date, provenance type, prior values and contradiction state.

`ObservationMemoryService` owns the update path: accepted Evidence is converted to an Observation, validated for lineage, atomic non-speculative wording and no Recommendation language, then applied to the model. Unknown statements create explicit Unknown records. Contradictory observations are retained as conflicts and do not silently overwrite current state.

The selected model-backed output is the organisation Observatory page because it is the narrowest existing user-facing enterprise briefing with lineage expectations. It now renders an Enterprise Memory panel from maintained model state before the generated reasoning layers. The panel exposes confidence, freshness, Unknowns, contradiction warnings, Observation IDs and Evidence IDs.

Deferred capabilities: full EI-001 model coverage, graph persistence, decay formula, automatic contradiction resolution, complete human knowledge governance, historical backfill, Recommendation-engine redesign and Commercial Digital Twin maturity.
