# ADR-012 — Governed Blueprint Package Import and Canonical Acceptance Boundary

**Identifier:** ADR-012
**Version:** 1.0
**Document Type:** Architecture Decision Record
**Authority Classification:** Accepted canonical ADR
**Status:** Accepted
**Decision date:** 2026-07-09
**Owner:** Rob / CIOS
**Decision class:** Governance, durable memory and cross-cutting runtime
**Supersedes:** None
**Related decisions:** ADR-001, ADR-002, ADR-003, ADR-004, ADR-005, ADR-010

## Context

CIOS can now create accepted Commercial Digital Twin Blueprint packages through specialist GPT workflows. Those packages contain valuable structured and narrative intelligence, including Sources, Evidence, Observations, Enterprise Model candidates, Unknowns, Contradictions, human-supplied knowledge and analytical views.

Flora is intended to maintain living Commercial Digital Twins. Importing a completed Blueprint therefore creates an important boundary:

> Approval of a research package is not the same as automatic acceptance of every package record into canonical Enterprise Memory.

Without an explicit decision, runtime implementation could:

- treat reports or spreadsheets as canonical memory;
- copy inferred or analytical content into Enterprise Model state without object-level validation;
- duplicate records when a package is re-imported;
- lose original stable IDs and package lineage;
- conflate import workflow state with Observation or domain lifecycle state;
- overwrite Contradictions or historical state;
- make pain points, Burning Platforms or solution patterns into accidental canonical objects;
- silently repair missing information by inference.

This would conflict with the CIOS doctrine that Evidence proves change, Observations remember change, Enterprise Models accumulate change and reports remain views.

## Decision

### 1. Package acceptance and canonical acceptance are separate

Acceptance of a Blueprint package means that the package is approved as a governed analytical baseline for its stated boundary, effective date and decisions.

It does not mean that every row, claim, relationship, inference or analytical conclusion is automatically canonical.

Canonical promotion is object-specific. A Candidate Import Record must satisfy the owning CIOS object contract before it may create or update canonical state.

### 2. The original package is immutable

Flora must retain the exact received package without editing it.

The Package Registry must preserve at least:

- package identifier;
- package version;
- enterprise identifier;
- parent Twin identifier where applicable;
- package checksum;
- file inventory and checksums;
- effective date;
- source cut-off;
- governing contract/profile version;
- acceptance state;
- received timestamp;
- importing actor;
- source archive location.

Any normalised or generated manifest is stored alongside the immutable package, not inside or instead of it.

### 3. Structured governed state takes precedence over prose

Where package contents disagree, Flora applies this precedence for import interpretation:

1. final governed structured state, including the final Twin Spine or equivalent register;
2. governed object registers and ledgers;
3. package manifest and validation records;
4. governed narrative;
5. executive publications and one-page views.

This precedence determines import interpretation only. Contradictions are preserved and exposed; lower-precedence content is not silently discarded.

### 4. Source identity and location are preserved

Every imported candidate must preserve:

- original package ID and version;
- original external stable ID;
- source file;
- worksheet, section or record location;
- record class;
- source checksum where practical;
- Flora canonical ID where promoted;
- mapping state;
- import-run ID.

Flora may allocate canonical IDs, but original identifiers remain inspectable and queryable.

### 5. Import-run state is distinct from intelligence-object state

Import workflow states are runtime states, for example:

`received → integrity_validated → parsed → staged → reviewed → partially_accepted | accepted | rejected | reversed`

They must not be reused as:

- Observation lifecycle state;
- Evidence acceptance state;
- domain measurement state;
- freshness or temporal relevance;
- Hypothesis lifecycle;
- Enterprise Model attribute state.

### 6. Import uses staging and explicit promotion

All parsed records enter a staging boundary as Candidate Import Records.

Before canonical mutation, Flora must show the proposed effect:

- create;
- update;
- unchanged;
- conflict;
- contradiction;
- reject;
- quarantine;
- unresolved mapping.

Promotion must be explicit, transactional and attributable to an authorised actor or governed automated policy.

### 7. Partial acceptance is valid and visible

A package may be accepted as an analytical baseline while only part of its structured content is promoted.

Flora must report:

- accepted records;
- rejected records;
- quarantined records;
- unsupported record classes;
- unresolved mappings;
- contradictions created;
- architecture gaps discovered.

The resulting Twin must visibly state when an import is partial.

### 8. Re-import is idempotent

Re-importing an identical package must not create duplicate Sources, Evidence, Observations, entities, attributes, Unknowns, Contradictions, relationships or human-supplied knowledge.

A newer package version must produce an explicit delta against the relevant prior package and canonical state.

Identity is determined by owned canonical rules, external stable IDs, package lineage and content fingerprints. Runtime convenience must not invent a new canonical identity rule where an owning specification is silent.

### 9. Analytical projections remain views

The following are imported as versioned analytical projections unless and until an owning architecture paper promotes them to canonical objects:

- Pain Point;
- current-response assessment;
- response effectiveness;
- residual pain;
- Burning Platform classification;
- Transformation Pressure view;
- prioritisation and disposition matrix;
- stakeholder hot-button view;
- solution pattern portfolio;
- executive synthesis;
- publication.

An Analytical Projection may be displayed, filtered, compared and linked to its supporting objects. It does not become an EI-001 or EI-012 canonical object merely because it appears in a Blueprint workbook.

### 10. Imports are reversible and auditable

Flora must record every canonical mutation caused by an Import Run.

A reversal must:

- restore the prior canonical state where technically safe;
- preserve the original package and Import Ledger;
- preserve historical lineage and audit records;
- avoid deleting Evidence or history required by other accepted state;
- report any non-reversible dependency.

Reversal is a governed compensating transaction, not destructive erasure.

### 11. Import performs no silent research

The import runtime may validate, map, compare, identify gaps and propose candidate mappings.

It must not:

- invent missing enterprise facts;
- infer a private intention or commercial opportunity;
- silently create Evidence;
- convert an Unknown into a negative fact;
- repair a package by unlabelled model generation;
- promote human interpretation as Evidence.

### 12. A generic workflow uses package-specific adapters

Flora owns a generic import workflow.

A Package Adapter translates a supported external package format into Candidate Import Records. MOD-specific workbook rules must remain isolated in a MOD package adapter rather than becoming generic canonical semantics.

## Decision rationale

This approach allows CIOS to gain durable value from high-quality Blueprint packages without reducing Flora to a document repository or compromising canonical memory.

It preserves three separate things:

1. the immutable research artefact;
2. the candidate structured intelligence extracted from it;
3. the governed canonical state Flora accepts.

## Alternatives considered

### Import the accepted workbook directly into canonical tables

Rejected. Package-level approval is too coarse, workbook classes do not necessarily map one-to-one to canonical objects and analytical views could become accidental memory.

### Store only the package and render its files

Rejected as the final architecture. This preserves documents but does not create living Enterprise Memory or object-level lineage.

### Require every future package to use a perfect universal schema before import

Rejected for Sprint 1. It would delay learning and over-design the exchange model. The architecture instead uses a generic workflow with bounded adapters and a versioned import profile.

### Let an AI agent repair and normalise the package during import

Rejected unless every generated record remains explicitly candidate, labelled and reviewable. Silent repair conflicts with trust and lineage requirements.

### Create Pain Point as a canonical object now

Deferred. Pain is commercially valuable, but current doctrine treats it as an analytical view derived from governed state. Promotion requires an owning specification or later ADR.

## Consequences

### Positive

- Accepted research can become durable, inspectable memory.
- Original package lineage is retained.
- Runtime state remains separate from intelligence state.
- Re-import and refresh can be governed.
- Analytical views can be valuable without redefining canonical objects.
- Import failures become visible architecture learning.

### Costs and constraints

- Import requires staging, mapping, validation and acceptance surfaces.
- The first MOD adapter will contain package-specific mapping logic.
- Partial acceptance is more complex than a one-click database load.
- Some Blueprint fields will remain view-only until their owning contracts mature.
- Reversal requires an Import Ledger and careful dependency handling.

## Runtime implications

Flora Sprint 1 must implement:

- immutable package receipt;
- Package Registry;
- Import Run;
- Package Adapter boundary;
- candidate staging;
- Mapping Registry;
- validation results;
- acceptance and promotion;
- Import Ledger;
- idempotency;
- delta and reversal design;
- lineage from displayed projection to original package location.

## Affected documents

- CIOS Reference Architecture v1.0
- CIOS Reference Architecture Glossary
- CIOS Architecture Document Map
- Flora Governed Blueprint Import Runtime Specification v0.1
- CIOS Blueprint Package Import Profile v0.1
- CIOS Enterprise Intelligence Experience Standard v0.1
- Flora Enterprise Canvas and Drill-Down Pattern v0.1

No change is made to EI-001 or EI-012 object semantics by this ADR.

## Validation

The decision is implemented correctly when:

- an identical package can be re-imported without duplicate canonical state;
- a package can be staged without canonical mutation;
- object-level effects can be inspected before acceptance;
- unsupported records can be quarantined while valid records are accepted;
- original IDs and locations remain traceable;
- analytical projections remain distinguishable from canonical objects;
- every accepted mutation appears in an Import Ledger;
- a safe reversal can be demonstrated;
- import does not generate unsupported enterprise facts.

## Architecture debt and deferrals

- A universal cross-enterprise package exchange standard is deferred.
- Canonical status of Pain Point remains deferred.
- Automated promotion policies are deferred until manual acceptance has been validated.
- Cross-package semantic reconciliation beyond stable IDs and owned canonical rules is deferred.

## Review and supersession conditions

Revisit this decision when:

- more than three materially different Blueprint package formats are supported;
- a canonical Pain Point or Transformation Programme view is proposed;
- automated promotion is introduced;
- cross-enterprise import requires shared exchange semantics;
- nested-Twin imports expose unresolved ownership or versioning problems;
- reversal cannot safely preserve dependent canonical state.
