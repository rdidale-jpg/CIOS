# Flora Runtime Increment 1 Implementation Report

## Implemented components

- Governed UK Banking fixture ingestion with contract validation.
- Read-only runtime projection for the Lloyds focus object (`BK-ENT-001`).
- Workspace state handling limited to focus object, active perspective, navigation trail, filters, watch state, comparison state, user and tenant context.
- Relationship, Evidence/Observation availability, Unknown, Contradiction and Lineage sections.
- Safe-unavailable responses for unsupported identities and section-level degradation.

## Contracts satisfied

Increment 1 validates the frozen v0.1 contracts under `schemas/flora-runtime/v0.1` for focus object projection, relationship projection, evidence/observation availability, Unknown, Contradiction, Lineage, Workspace State, Ingestion Report and Safe Unavailable Response.

## Architecture compliance

- No second source of truth: runtime uses read projections loaded from governed fixtures and does not mutate Enterprise Knowledge.
- Evidence remains Evidence and Observations remain Observations: availability counts and lineage node types are preserved separately.
- Unknowns and Contradictions are displayed as first-class sections and are not collapsed or resolved by runtime logic.
- Lineage is inspectable through explicit Source → Evidence → Observation → Object → Projection nodes.
- Read-only behaviour: no canonical object creation, no write-back, no GPT invocation, no recommendations and no opportunity scoring.
- Authority boundaries respected: missing or unresolved authority returns safe-unavailable rather than fabricated metadata.

## Known limitations and technical debt

- Only Lloyds Banking Group / `BK-ENT-001` is supported.
- The schema validator is intentionally minimal and scoped to the frozen Increment 1 contracts; replace with a full JSON Schema implementation if an approved dependency is added.
- Runtime is module-level and not yet integrated into the local HTTP workspace.
- Fixture corpus is file-backed; no production object store or access-control adapter is included in Increment 1.

## Deferred Increment 2 scope

- Expand supported UK Banking objects beyond Lloyds.
- Add an HTTP/API presentation adapter over the read-only runtime projection.
- Add access-control integration for redacted lineage segments.
- Add broader fixture generation and negative semantic checks for ingestion collision outcomes.
