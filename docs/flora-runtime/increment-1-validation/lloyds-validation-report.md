# Flora Runtime Increment 1 Lloyds Validation Evidence

Date: 2026-07-19 UTC

## Navigation path

`/flora` → “Open Lloyds Banking Group Increment 1 workspace” → `/flora/object/BK-ENT-001`.

Direct aliases validated: `/flora/lloyds` and `/workspace/enterprise/BK-ENT-001`.

## Rendered route evidence

| Path | HTTP status | Page title | Bytes |
|---|---:|---|---:|
| `/flora` | 200 | Flora Enterprise Intelligence | 7441 |
| `/flora/object/BK-ENT-001` | 200 | Flora Increment 1 Lloyds workspace | 7026 |
| `/flora/lloyds` | 200 | Flora Increment 1 Lloyds workspace | 7026 |
| `/workspace/enterprise/BK-ENT-001` | 200 | Flora Increment 1 Lloyds workspace | 7026 |
| `/flora/object/unsupported-object` | 200 | Flora Increment 1 workspace unavailable | 1582 |

## Capability acceptance

| Capability | Visible | Usable | Governed data | Safe failure | Result |
|---|---:|---:|---:|---:|---|
| Focus Object | Yes | Yes | Yes | Yes | Accepted |
| Identity | Yes | Yes | Yes | Yes | Accepted |
| Authority | Yes | Yes | Yes | Yes | Accepted |
| Freshness | Yes | Yes | Yes | Yes | Accepted |
| Relationships | Yes | Yes | Yes | Yes | Accepted |
| Evidence availability | Yes | Yes | Yes | Yes | Accepted |
| Observation availability | Yes | Yes | Yes | Yes | Accepted |
| Unknowns | Yes | Yes | Yes | Yes | Accepted |
| Contradictions | Yes | Yes | Yes | Yes | Accepted |
| Lineage | Yes | Yes | Yes | Yes | Accepted |
| Workspace state | Yes | Yes | Yes | Yes | Accepted |
| Safe unavailable | Yes | Yes | Yes | Yes | Accepted |

## Rendered evidence artifacts

- `lloyds-workspace.html` captures the rendered Lloyds Focus Object workspace, relationships, Evidence/Observation availability, Unknown, Contradiction, lineage, partial/access-redacted lineage labels, and workspace state.
- `safe-unavailable.html` captures the unresolved identity safe-unavailable state.

## Architecture compliance findings

- No second source of truth: Increment 1 reads frozen contract fixtures and governed UK Banking source references only.
- No canonical mutation: workspace state is labelled non-canonical and short-lived.
- No GPT invocation, Recommendation generation, opportunity scoring, or inferred relationship was used for Increment 1 workspace validation.
- Evidence counts remain separate from Observation counts.
- Unknowns and Contradictions remain explicit and inspectable.
- Partial, access-redacted, unresolved and safe-unavailable states are labelled in user-facing language.

## Browser/application logs

Startup and route verification produced no material application failures in `/tmp/flora.log` during validation.
