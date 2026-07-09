# Flora Sprint 1 PR6 — Enterprise Canvas Organisation Experience Completion Report

## Bounded-step confirmation

The latest merged repository state already contains PR5's governed Enterprise Canvas read model. The next bounded implementation step is therefore the first visible Enterprise Canvas experience: an organisation-lens page with understandable tiles and a read-only tile detail panel using the PR5 read model. This PR implements that step only.

## What a user can now see and do

An authorised Flora user can open an enterprise Canvas, read a plain-English enterprise header, review organisation-lens tiles in deterministic read-model order, and open a tile to inspect core facts, pressures, current responses, unresolved items, uncertainty markers, freshness and evidence references.

## Route or entry point

The Canvas is available at:

- `/digital-twins/{enterprise_id}/canvas`
- `/digital-twins/{enterprise_id}/canvas/tiles/{tile_view_id}`

## Tile and detail-panel behaviour

Tiles are keyboard-activatable links. Each tile shows display name, role, accountable role, current state, principal pain or pressure, material change, Unknown, Contradiction, stale-evidence and nested-Twin markers where supplied by the read model.

Opening a tile renders a read-only detail panel with plain-language sections for what the area does, why it matters, core facts, change, pressure, responses, unresolved items, stakeholders, unknowns and contradictions, evidence freshness, suggested next posture and Inspect evidence.

## Plain-language treatment

The UI avoids internal analytical headings as the primary language. Pain and pressure entries include the statement plus qualification/status context where supplied by the PR5 read model.

## Uncertainty and freshness treatment

Unknowns, Contradictions, stale Evidence and nested-Twin availability are separate text markers and do not rely on colour alone. Effective date, source cut-off and last-refreshed information are shown in the header and detail panel.

## Lineage entry point

The detail panel includes an Inspect evidence section. It summarises lineage references with reference type, displayed judgement, source/package reference and evidence/date reference without exposing raw lineage payloads as the primary experience.

## Accessibility

Tiles are links with meaningful accessible labels, visible focus styles and no hover-only information. The detail panel is a labelled region with a close link. The layout uses logical heading order and collapses to a single column on narrow screens.

## Access control

The route calls the PR5 EnterpriseCanvasService and therefore uses the existing product-session enterprise-access checks. Unauthorised requests return an access-denied page and receive no tile data, pain summaries, sensitive facts, lineage references or package metadata.

## Tests and results

New UI tests cover authorised page rendering, header fields, deterministic tile links, tile summaries, plain-English labels, keyboard-link activation semantics, tile detail opening/closing, pain/current-response presentation, unresolved issue presentation, Unknown, Contradiction and stale-evidence markers, nested-Twin marker, lineage entry point, empty and access-denied states, no write forms, no MOD-specific content and no canonical analytical-projection objects.

Targeted result recorded during implementation:

- `pytest -q tests/test_flora_enterprise_canvas.py` — 5 passed.

## Repository-wide baseline comparison

The latest provided merged baseline is 48 failed, 508 passed, 2 skipped and 1 warning. PR6 adds focused passing Enterprise Canvas UI coverage. Repository-wide execution during PR6 produced 48 failed, 511 passed, 2 skipped and 1 warning. The failure count matches the latest provided merged baseline, while the pass count increases with the new Enterprise Canvas UI coverage; no new repository-wide regressions were introduced.

## Deferred work

Additional Canvas lenses, a complete lineage explorer, graph visualisation, feedback capture, editable intelligence, Blueprint upload/review/promotion screens, configurable dashboards and Provider Fit/opportunity scoring remain deferred.

## Canonical mutation confirmation

The UI creates no canonical mutations. It renders the governed PR5 read model and provides no POST route, write form or editing capability.
