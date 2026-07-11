# Phase 3 Release Contract Report — Twin Releases and Knowledge Packs

**Status:** Complete  
**Date:** 2026-07-11  
**Scope:** Documentation and schemas only. Flora runtime code was not changed.

## Mission outcome

The Commercial Digital Twin Blueprint Contract has been aligned to the Architecture v2.0 Knowledge Pack architecture. Future Twin releases now use the Knowledge Pack release boundary rather than ad hoc report, ZIP or Blueprint-only publication conventions.

## Authorities applied

- ADR-016 — Knowledge Packs as the Standard Exchange Mechanism.
- FP-010 — Knowledge Pack Architecture.
- FP-011 — Knowledge Exchange Architecture.
- EI-013 — Knowledge Asset Exchange Model.
- Knowledge Pack Specification v1.0.
- Twin Presentation Model Specification v1.0.

## Required release structure

A compliant Twin release Knowledge Pack must contain:

```text
manifest.json
metadata.json
validation.json
lineage.json
checksums.sha256
payload/twin/
payload/presentation-model/
attachments/
```

## Release contract

The Twin Contract now requires `manifest.json` to declare:

- pack ID and pack version;
- Twin ID and Twin version;
- release ID;
- audience and purpose;
- source cut-off;
- producer identity;
- truth status;
- stable object ID policy;
- Evidence and Observation lineage references;
- Unknowns;
- Contradictions;
- human-supplied knowledge labels;
- validation state;
- supersession references;
- checksums.

## Manifest schema

A normative JSON Schema was added at:

`architecture/specifications/knowledge-packs/twin-release-manifest.schema.json`

The schema constrains the release manifest to the required Knowledge Pack structure and mandatory identity, lineage, validation, truth-status, supersession and checksum fields.

## Presentation Model requirement

The Twin Contract and Twin Presentation Model Specification now clarify that Presentation Models are governed interpretations for declared audiences and purposes. Multiple audience-specific Presentation Models may exist for one Twin release. Acceptance of a Presentation Model or its Knowledge Pack does not make the interpretation canonical fact.

## Lineage requirement

The contract requires stable object IDs and inspectable Evidence and Observation lineage. Lineage must cover Twin payloads, Presentation Model payloads, Unknowns, Contradictions and human-supplied knowledge labels.

## Unknown handling

Unknowns remain first-class release content. They must retain stable IDs, materiality, source context, affected claims or objects and next learning actions. Unknowns must not be replaced with invented precision.

## Contradiction handling

Contradictions remain first-class release content. They must retain stable IDs, competing claims, Evidence references, affected objects, adjudication state and next resolution action. Releases must not hide contradictions behind a single confident narrative.

## Backward compatibility

Existing Flora Blueprint ZIPs with `blueprint_manifest.json` may be received as legacy packages. A compatibility adapter should map legacy identity, source cut-off, files, checksums and validation records into the Knowledge Pack structure, preserve the original ZIP as an attachment or immutable source artefact, assign a new pack ID and release ID, and label imported content as candidate intelligence until governed acceptance.

## Runtime boundary

No Flora runtime code, application code or tests were changed. This phase updates only architecture documentation and the normative JSON Schema.

## Remaining risks

- Existing legacy Blueprint ZIPs will need adapter implementation before they can be automatically transformed into Knowledge Pack releases.
- The manifest schema is normative for the manifest but does not yet provide full schemas for `metadata.json`, `validation.json` or `lineage.json`.
- Runtime validation of Knowledge Packs remains a future implementation activity.
