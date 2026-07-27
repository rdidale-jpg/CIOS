# WP2-001 — Executive Intelligence Inspection

**Date:** 2026-07-27  
**Implementation boundary:** Flora Twin Inspection Shell presentation layer

## Pre-flight assessment

The assessment used three deliberately separate readings:

1. **Architectural intent** describes the desired authority and composition boundary.
2. **Implemented runtime** means executable code and durable providers found in this repository.
3. **Current programme state** describes what this increment can honestly expose; it is not a deployment claim.

| Capability | Architectural intent | Implemented runtime | Current programme state / decision |
| --- | --- | --- | --- |
| Twin Inspection Shell | Type-neutral composition over a common inspection contract. | Existing `twin_inspection` shell, Enterprise adapter and route fallback. | Extended rather than replaced; remains presentation-only. |
| Industry inspection | Industry-first executive landing with governed Evidence and relationships. | The UK Banking runtime supplies outlook, PESTLE/market forces, signals, enterprises, opportunity and Evidence routes. | Supported through an adapter for `uk-banking`; no second Industry is implied. |
| Enterprise inspection | Recompose the Living Enterprise Twin. | Enterprise Canvas service/view supplies header, tiles, projections, Observations, Evidence, Unknowns, Contradictions and lineage inspection. | Supported by the existing adapter; conclusion references point back to Canvas lineage. |
| Enterprise Canvas | Primary Living Enterprise Twin navigation/read model. | Implemented and governed through Canvas service, access repository and views. | Composed unchanged; no replacement Canvas or copied DTO store. |
| Import Review / Import Inspect | Govern pre-acceptance validation, proposed mutations and promotion. | Blueprint Import registry, validator, candidate staging, Review and promotion views are implemented. | Candidate adapter links to those owners and never promotes. Candidate styling and language are explicitly distinct. |
| Executive Intelligence Brief | Optional governed-input interpretation. | Enterprise brief and deterministic Canvas overview exist. | Existing Canvas opening policy is retained. The shell does not require or persist a generated brief. |
| Evidence inspection | Claim-to-Observation/Evidence/source inspection. | Canvas lineage, Banking Evidence and specialist Evidence views exist. | Reused through direct targets; no Evidence persistence or source-quality inference added. |
| Research lineage | Package/import provenance and owner workflows. | Canvas lineage references include package and import-run identities; Import history is implemented. | Existing links are composed at Architect depth. Missing lineage stays explicit. |
| Unknowns / Contradictions | First-class challenge, never collapsed into certainty. | Canvas and Blueprint candidates expose both; Banking runtime retains bounded gaps and competing pressures. | Shown in conclusion trust panels and profile context; absence is not described as corroboration. |
| Source Quality | Owner-defined assessment only. | Some specialist/canonical records expose source fields; there is no universal quality projection across supported types. | Gap recorded. The shell does not invent a tier or score. |
| Presentation Models | Owner-provided read payloads, not canonical truth. | Canvas and Banking presentation functions are executable; no universal accepted Presentation Model resolver was found. | Existing functions are composed conditionally. No new taxonomy/model is established. |
| Twin assessment | Scoped confidence, completeness and freshness from owners. | Canvas qualifications/dates and candidate package maturity are available; no universal governed-Twin completeness measure exists. | Values retain context. No combined or universal trust score is calculated. |

## Twin assessment

| Twin | Canonical owner | Lifecycle | Inspection route | Read model | Evidence | Relationship provider | Inspection maturity |
| --- | --- | --- | --- | --- | --- | --- | --- |
| UK Banking Industry | Existing Flora Banking runtime | Governed presentation over current Banking intelligence | `/industries/uk-banking` | Banking outlook, signals, PESTLE and portfolio functions | Banking signal provenance and enterprise Evidence routes | Existing Banking portfolio/enterprise links | Supported pilot; UK Banking only |
| Enterprise | Enterprise Model and Enterprise Canvas owners | Accepted/governed, with owner-supplied maturity | `/digital-twins/{enterprise_id}` | `EnterpriseCanvasService` | Canvas lineage inspection to Observations, Evidence, sources and packages | Canvas/nested markers and existing specialist routes only | Supported |
| Candidate Import | Blueprint Package registry, validator, candidate staging and Review owners | Received → inspected → reviewed → promoted/cancelled; explicitly pre-acceptance | `/blueprint-import/{run_id}/intelligence` | Package inspection plus staging summary | Candidate Evidence only, retaining candidate semantics | Import impact/read views | Supported, visibly distinct |
| Market Participant | Canonical specification exists; no accepted runtime owner/read repository was found | Candidate fragments/specification only in the inspected runtime | `/market-participants/{id}/inspect` returns an honest unsupported state | None | No canonical participant inspection projection found | None proven routable | Gap recorded; adapter deliberately not fabricated |

## Delivered composition

The common contract adds presentation-only material conclusions with direct support, challenge, Evidence and lineage targets. The shell renders the same identity, lifecycle, conclusion and progressive-disclosure structure for supported adapters. Industry values remain owned by Banking, Enterprise values by Canvas/canonical memory, and candidate values by Blueprint Import.

The increment adds no runtime service, canonical model, persistence location, trust score, relationship graph or business-intelligence taxonomy. Existing owner views remain the destination for detailed Evidence, Review, governance and diagnostics.
