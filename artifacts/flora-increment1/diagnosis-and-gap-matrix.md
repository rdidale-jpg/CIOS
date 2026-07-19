# Increment 1 diagnosis and implementation gap matrix

## Diagnosis from runtime inspection

- Implemented runtime components before this slice: frozen V0.1 JSON schemas, UK Banking fixtures, `open_focus_object`, contract validation, safe-unavailable responses, and runtime tests.
- UI consumption before this slice: the default `/flora` page consumed the Banking V2 pipeline and legacy workspace components, not the frozen Increment 1 runtime contracts.
- Exposure before this slice: `/workspace/reference` existed, but there was no obvious Lloyds object route or default entry point consuming `open_focus_object`.
- Reachability: the Increment 1 workspace data existed as a service/runtime projection but was not user-reachable as a composed workspace.
- Default route ownership: legacy Flora V2 navigation still owned `/flora`.
- Rendered data before this slice: `/flora` rendered legacy Banking pipeline/fixture-derived prototype content rather than the governed Lloyds object projection.
- Service-only finding: Increment 1 was effectively service-only for Lloyds until the new `/flora/object/BK-ENT-001` view connected it.
- Acceptance concern: contract/runtime criteria were represented by tests, but visible workspace acceptance criteria had no user-visible evidence until this slice.

## Migration boundary

- `/flora` remains the temporary home route but now exposes an obvious Increment 1 entry point and labels the Explore/Focus/Shape cards as legacy prototype navigation.
- `/flora/object/BK-ENT-001`, `/workspace/enterprise/BK-ENT-001`, and `/flora/lloyds` render the same Increment 1 Lloyds workspace.
- Unsupported object routes under `/flora/object/` fail closed into a safe-unavailable presentation.

## Gap matrix

| Capability | Implemented | Connected to UI | User visible | Contract used | Gap |
|---|---:|---:|---:|---|---|
| Focus Object | Yes | Yes | Yes | `focus-object-projection-v0.1` | Completed: Lloyds header renders identity and statuses. |
| Identity | Yes | Yes | Yes | `common-definitions` via focus object | Completed: object id/type, owner, authority, lifecycle, freshness and provenance render. |
| Relationships | Yes | Yes | Yes | `relationship-projection-v0.1` | Completed: governed relationship table; no inferred relationships. |
| Evidence availability | Yes | Yes | Yes | `evidence-observation-availability-v0.1` | Completed: evidence count distinct from observations/inaccessible/unavailable. |
| Observation availability | Yes | Yes | Yes | `evidence-observation-availability-v0.1` | Completed: observation and accepted observation counts render separately. |
| Unknowns | Yes | Yes | Yes | `unknown-response-v0.1` | Completed: governed Unknown appears as first-class intelligence. |
| Contradictions | Yes | Yes | Yes | `contradiction-response-v0.1` | Completed: both conflicting references remain visible. |
| Lineage | Yes | Yes | Yes | `lineage-response-v0.1` | Completed: Source → Evidence → Observation → Object → Projection chain visible. |
| Workspace state | Yes | Yes | Yes | `workspace-state-v0.1` | Completed: non-canonical workspace state label visible. |
| Safe unavailable | Yes | Yes | Yes | `safe-unavailable-response-v0.1` | Completed: unsupported object route renders unresolved identity safely. |

## Built / wired / rendered / validated distinction

- Built: schemas, fixtures, runtime loader, validator, and safe-unavailable contracts.
- Wired: the web handler now routes Lloyds object paths to the Increment 1 view.
- Rendered: the composed page shows focus, identity, relationships, availability, Unknowns, Contradictions, lineage, workspace state and safe-unavailable test access.
- Validated: runtime contract tests pass; view tests assert visible contract sections and safe-unavailable rendering; running-service HTML captures are included in this directory.

## Architecture validation

This slice remains read-only. It does not mutate canonical state, invoke GPT, create Recommendations, score intelligence, infer relationships, hide Unknowns, collapse Contradictions, or promote workspace state to canonical Enterprise Knowledge.
