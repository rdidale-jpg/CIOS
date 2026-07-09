# Flora Sprint 1 PR7 Enterprise Canvas Lineage Inspection Completion Report

**Status:** Complete  
**Date:** 2026-07-09  
**Scope:** Read-only lineage inspection behind the existing Enterprise Canvas **Inspect evidence** entry point.

## 1. What a user can now inspect

An authorised user can open a material Enterprise Canvas tile statement and inspect why Flora shows it without opening raw JSON or searching Blueprint files. The inspection starts with the displayed statement and then exposes the available support chain in plain English.

## 2. Route or entry point

The existing tile detail **Inspect evidence** section now links to:

`/digital-twins/{enterprise_id}/canvas/tiles/{tile_id}/lineage`

The lineage page includes a return link to the originating tile detail route.

## 3. Lineage levels supported

The lineage inspection supports partial or complete chains across:

1. displayed statement;
2. analytical projection or canonical Enterprise Model attribute;
3. Observation reference;
4. Evidence reference;
5. Source details;
6. imported package and original package file inventory.

The view does not require every chain to contain every level.

## 4. Treatment of projections and canonical records

Canvas tiles remain read-model DTOs. Analytical projections remain projection-only staged records. Canonical records are read through the existing Enterprise Model, Observation and Evidence repositories. PR7 does not create canonical Pain Point, Burning Platform, Transformation Pressure or analytical-projection objects.

## 5. Evidence and Source presentation

Evidence is presented with source title, source type, publication or effective date, short summary, exact source location where supplied, freshness, confidence or qualification, whether it supports or is contrary to the displayed judgement, and package/import reference where available.

Source details are displayed separately from Evidence so the user can distinguish the evidence item from where it came from.

## 6. Human-Supplied Knowledge treatment

Human-supplied knowledge is displayed in a dedicated section and labelled as human-supplied. Contributor or authorised role, supplied date and purpose are shown where authorised and available. It is not presented as independently proven external Evidence.

## 7. Unknown and Contradiction treatment

Unknowns and Contradictions are separate sections. Unknowns explain what remains uncertain, why it matters and what could resolve it. Contradictions retain conflicting positions and explain that Flora preserves conflict until fresher governed Evidence resolves it.

## 8. Incomplete-lineage behaviour

Missing Observations, Evidence, Source details or imported package locations are shown as incomplete lineage rather than hidden. Broken references are also displayed in a technical inspection section so users can distinguish missing lineage from an application error.

## 9. Access control

Lineage uses the same server-side enterprise/product-session access boundary as the Canvas read model. Unauthorised users receive a 403 page and no Canvas intelligence, evidence summaries, source details, package metadata, human-supplied knowledge or lineage references.

## 10. Accessibility

The lineage route uses headings, ordered lists and text labels instead of requiring a graph. The tile detail keeps a keyboard-usable link to the lineage view and the lineage view includes a return link to the same tile detail.

## 11. Tests and results

Targeted Enterprise Canvas lineage tests pass locally. Repository-wide test execution was run for comparison with the current merged baseline and remains affected by pre-existing baseline failures.

## 12. Repository-wide baseline comparison

Expected baseline supplied by the brief: 48 failed, 511 passed, 2 skipped, 1 warning. The actual run on the latest merged state after adding PR7 tests reported 48 failed, 513 passed, 2 skipped, 1 warning; the two additional passes are the new PR7 lineage tests and the failure count did not increase.

## 13. Deferred work

Feedback/correction capture, Blueprint upload UI, candidate review/promotion UI, graph visualisation, automatic research, Provider Fit, opportunity scoring and additional Canvas lenses remain deferred.

## 14. Read-only confirmation

PR7 is read-only. It performs no canonical writes, introduces no storage migration and adds no canonical analytical-projection types.
