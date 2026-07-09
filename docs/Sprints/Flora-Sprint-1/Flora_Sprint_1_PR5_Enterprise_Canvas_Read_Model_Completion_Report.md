# Flora Sprint 1 PR5 — Enterprise Canvas Read-Model Foundation Completion Report

## Scope confirmation

PR5 implements the Enterprise Canvas read-model foundation: a governed, read-only structure suitable for later visual tiles and drill-down. This follows the next bounded step after PR4 in the current merged repository state. The implementation does not create a visual Canvas UI, full drill-down panel, configurable dashboard, graph visualisation, opportunity scoring, Provider Fit, pursuit recommendations, MOD-specific paths or canonical analytical projection objects.

## What the Canvas read model provides

- Enterprise header with name, purpose, Twin version, effective date, source cut-off, acceptance state, latest material change, governing thesis, material pressures, freshness warning and last refreshed date.
- Deterministic top-level organisation tiles with stable tile-view IDs, ordering, display name, plain-English role, accountable role, current state, principal pain or pressure, material change, current response, unresolved issue, uncertainty indicators, freshness markers, nested-Twin marker, core facts and lineage.
- DTO serialization for API or UI retrieval without making the Canvas itself canonical memory.

## First supported lens

The first supported lens is `organisation`. Additional lenses remain deferred.

## Tile types supported

The implementation supports top-level organisation-area tiles assembled from governed Enterprise Model attributes whose domain is organisation, unit, domain or programme. If an enterprise has governed attributes but no organisation-domain attributes, the service safely falls back to a single enterprise-level tile rather than failing.

## Canonical and projection sources used

Canonical sources:

- Enterprise Model attributes.
- Enterprise Unknown records.
- Evidence records for lineage source references.

Projection sources:

- Blueprint-import staged analytical projection candidates for Pain Points, Burning Platforms, Transformation Pressures, current responses, response-effectiveness and residual-pain style views.

Projection records remain non-canonical and are displayed only as analytical projections.

## Freshness and uncertainty treatment

The header and tile model distinguish effective date, source cut-off, last refreshed date, stale evidence, Unknown indicators, Contradiction indicators, human-supplied provenance through canonical attributes and accepted Evidence-backed state. These are not collapsed into a single score.

## Lineage treatment

Every material tile judgement can carry lineage references to canonical attributes or analytical projections, Observation IDs, Evidence IDs, Source IDs when present, package reference, import run and package location. The visual lineage explorer remains deferred.

## Access control

The read service uses existing Flora product-session enterprise-access headers. Users without enterprise access receive no Canvas content.

## Tests and results

New tests cover enterprise header creation, deterministic tile identities, organisation-lens tile assembly, plain-English fields, core facts, analytical projection display, current response and unresolved issue display, Unknown, Contradiction, stale evidence, nested-Twin marker, retained lineage, incomplete data safety, unauthorised access blocking, deterministic repeated reads, no canonical analytical projection classes and no MOD-specific code paths.

## Repository-wide baseline comparison

The most recent PR4 completion report records the repository-wide baseline as 48 failed, 499 passed, 2 skipped and 1 warning. PR5 repository-wide results are recorded in the PR completion response.

## Deferred work

Deferred work includes the visual Enterprise Canvas UI, full drill-down panels, lineage explorer, additional lenses, configurable dashboards, graph views, automated tile generation, opportunity scoring, Provider Fit and pursuit recommendations.

## Read-only mutation confirmation

Canvas reads assemble DTOs from repositories and do not save Canvas records or mutate canonical Evidence, Observation, Enterprise Model, Pain Point, Burning Platform or Transformation Pressure objects.
