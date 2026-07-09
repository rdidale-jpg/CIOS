# Flora Sprint 1 — Governed Blueprint Import and Enterprise Canvas Delivery Plan v0.1

**Status:** Ready for Codex planning after architecture merge  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-09  
**Task type:** Runtime-changing, delivered through bounded PRs

## Mission

Make the accepted MOD Commercial Digital Twin durable, inspectable and understandable inside Flora.

Sprint 1 must prove that Flora can:

- receive an accepted Blueprint package;
- preserve it immutably;
- stage and validate candidate intelligence;
- selectively promote eligible records without bypassing canonical governance;
- register pain and related analysis as versioned projections;
- render a simple enterprise-first Canvas;
- allow users to inspect lineage, uncertainty and freshness;
- accept governed feedback without silent overwrite.

The sprint improves durable memory, explainability, executive understanding and institutional learning.

## Product outcome

A user opens Flora and sees MOD as a navigable Living Twin rather than a folder of documents.

Within five minutes, the user can explain:

- what MOD exists to do;
- how its main domains are organised;
- the principal pressures and pains;
- what MOD is already doing;
- what remains unresolved;
- where the Evidence and uncertainty sit.

## Architecture references

Read and follow:

- `CIOS-AI.md`
- `architecture/reference-architecture/CIOS-Reference-Architecture-v1.0.md`
- `architecture/reference-architecture/CIOS-Design-Doctrine.md`
- `architecture/reference-architecture/Architecture-Principles.md`
- `architecture/handbook/CIOS-Chief-Architect-Handbook.md`
- `architecture/reference-architecture/Glossary.md`
- `architecture/reference-architecture/Document-Map.md`
- ADR-001, ADR-002, ADR-004, ADR-005, ADR-010, ADR-012 and ADR-013
- `architecture/founding-papers/FP-003-Flora-Intelligence-Architecture.md`
- EI-001, EI-002 and EI-012
- `docs/Architecture/Flora_Governed_Blueprint_Import_Runtime_Specification_v0.1.md`
- `docs/Architecture/CIOS_Blueprint_Package_Import_Profile_v0.1.md`
- `docs/Architecture/CIOS_Enterprise_Intelligence_Experience_Standard_v0.1.md`
- `docs/Architecture/Flora_Enterprise_Canvas_and_Drill_Down_Pattern_v0.1.md`

## Global constraints

- Do not treat package acceptance as canonical acceptance.
- Do not edit the received archive.
- Do not create new canonical EI fields, states or paths without an owning specification.
- Do not turn Pain Point, Burning Platform, Transformation Pressure or solution pattern into canonical EI objects.
- Do not reason directly from publication prose when governed structured state exists.
- Preserve external IDs and original package locations.
- Preserve Unknowns and Contradictions.
- Label human-supplied knowledge.
- Keep import-run state separate from intelligence-object state.
- No Provider Fit, Pursue, wallet share, award probability or opportunity scoring.
- Avoid opportunistic refactoring outside each PR.
- Report discovered architecture gaps instead of hiding them.

## Sprint delivery sequence

### PR 0 — Read-only runtime binding audit

**Mission**

Map the accepted architecture to the current Flora codebase before changing runtime behaviour.

**In scope**

- current upload/storage path;
- existing Source, Evidence, Observation and Enterprise Model services;
- current persistence and migrations;
- current report/workspace UI;
- authentication and permissions;
- test strategy;
- likely integration points.

**Deliverables**

- `docs/Architecture/Flora_Blueprint_Import_Code_Binding_Audit_v0.1.md`
- component and data-flow map;
- implementation risks;
- exact files proposed for PRs 1–6;
- architecture gaps requiring decision.

**Acceptance criteria**

- no runtime code changed;
- all relevant existing services identified;
- direct-database shortcuts rejected;
- unresolved canonical semantics listed;
- proposed PR sequence is bounded.

**Validation**

- repository search;
- test inventory;
- migration inventory;
- architecture review.

**Commit**

`docs(flora): map blueprint import and canvas runtime bindings`

**PR title**

`Document Flora Blueprint import and Enterprise Canvas code bindings`

### PR 1 — Immutable package receipt and registry

**Mission**

Create durable package identity and preserve the exact received archive.

**In scope**

- package upload/register endpoint;
- content checksum;
- immutable storage adapter;
- Package Registry;
- Import Run creation;
- file inventory extraction;
- generated receipt manifest;
- permission checks.

**Out of scope**

- workbook parsing;
- canonical promotion;
- Canvas.

**Acceptance criteria**

- MOD archive checksum is stored;
- original archive remains unchanged;
- file inventory and checksums are inspectable;
- duplicate package checksum is detected;
- invalid archive fails before staging;
- package and Import Run states remain separate.

**Validation**

- unit tests;
- corrupted ZIP fixture;
- duplicate upload fixture;
- permission test;
- migration test.

**Commit**

`feat(flora): add immutable blueprint package receipt`

**PR title**

`Add governed Blueprint package receipt and registry`

### PR 2 — MOD v1.2 adapter and candidate staging

**Mission**

Parse the accepted MOD package into candidate envelopes without canonical mutation.

**In scope**

- `mod_cdt_v1_2_adapter`;
- adapter identification;
- final Twin Spine selection;
- original stable IDs and locations;
- Candidate Staging Store;
- package metadata;
- supported record enumeration;
- analytical projection registration candidates;
- unsupported-sheet report.

**Out of scope**

- automatic canonical acceptance;
- universal adapter;
- all workbook sheets.

**Acceptance criteria**

- supported records stage with record class, truth class and location;
- 24 pain candidates stage as projections;
- HSK remains labelled;
- narrative files are indexed but not converted into Observations;
- adapter limitations are visible;
- MOD-specific mappings remain isolated.

**Validation**

- adapter fixture tests against the clean MOD release;
- record-count snapshots;
- duplicate external-ID test;
- unsupported-sheet test.

**Commit**

`feat(flora): stage MOD blueprint candidate records`

**PR title**

`Add MOD v1.2 Blueprint adapter and candidate staging`

### PR 3 — Validation, mapping and delta

**Mission**

Determine which staged records are valid, mapped, unchanged, conflicting or unsupported.

**In scope**

- Validation Engine;
- Mapping Registry;
- structural and lineage checks;
- proposed actions;
- package and prior-version delta;
- idempotency;
- quarantine state;
- architecture-gap reporting.

**Out of scope**

- canonical writes;
- automated semantic matching beyond owned identity rules.

**Acceptance criteria**

- identical re-import proposes no canonical changes;
- invalid Observation candidate without Evidence is blocked;
- unsupported canonical path is quarantined;
- ambiguous identity requires review;
- package removal does not imply canonical deletion;
- validation results are attributable and inspectable.

**Validation**

- duplicate import test;
- changed-version fixture;
- broken-reference fixture;
- ambiguous mapping fixture;
- architecture protection tests.

**Commit**

`feat(flora): validate and map blueprint import candidates`

**PR title**

`Add Blueprint candidate validation, mapping and delta`

### PR 4 — Acceptance workspace, promotion and Import Ledger

**Mission**

Allow object-level human acceptance and record every canonical effect.

**In scope**

- acceptance UI/API;
- filters and source inspection;
- preview;
- partial acceptance;
- canonical service calls;
- promotion transaction;
- Import Ledger;
- completion report;
- test reversal.

**Out of scope**

- automated promotion;
- bulk direct database writes.

**Acceptance criteria**

- user can accept selected valid candidates;
- invalid and unsupported candidates cannot be promoted;
- canonical services enforce owned contracts;
- partial acceptance is visible;
- every decision creates a ledger entry;
- failed grouped promotion rolls back;
- a test import can be safely reversed.

**Validation**

- integration tests;
- rollback test;
- partial-acceptance test;
- permission tests;
- reversal test;
- ledger audit.

**Commit**

`feat(flora): govern blueprint canonical promotion`

**PR title**

`Add Blueprint acceptance workspace, promotion and Import Ledger`

### PR 5 — Living Twin read model and lineage resolver

**Mission**

Create a queryable read model for the MOD Canvas without copying reports into memory.

**In scope**

- Twin summary;
- organisation-domain projection;
- core facts;
- pain projections;
- current-response projections;
- Unknown and Contradiction summaries;
- freshness;
- lineage resolver;
- package-location links.

**Out of scope**

- full Knowledge Graph UI;
- new canonical objects;
- Provider Fit.

**Acceptance criteria**

- tile data is derived from canonical state or registered projections;
- source of each rendered field is known;
- displayed judgement resolves to package and Evidence lineage;
- missing links are visible;
- mixed freshness is not hidden;
- no publication prose becomes the read model source where structured state exists.

**Validation**

- API/read-model tests;
- lineage chain test;
- broken-lineage test;
- data provenance snapshots.

**Commit**

`feat(flora): add living twin read model and lineage resolution`

**PR title**

`Add MOD Living Twin read model and inspectable lineage`

### PR 6 — Enterprise Canvas and drill-down

**Mission**

Make the accepted MOD Twin understandable through an enterprise-first experience.

**In scope**

- enterprise header;
- Organisation Lens;
- six to ten Intelligence Tiles;
- tile detail;
- pains and responses;
- Unknown and Contradiction markers;
- lineage entry;
- search and filters;
- nested-Twin placeholder;
- responsive and accessible states.

**Out of scope**

- additional lenses;
- graph layouts;
- user-configurable dashboards;
- CSM bid workspace.

**Acceptance criteria**

- cold user passes five-minute comprehension test;
- one activation opens role, facts, pains, response and uncertainty;
- lineage is reached within three purposeful interactions;
- keyboard flow works;
- colour is not the only state carrier;
- partial, stale and restricted states are explained;
- internal IDs do not dominate Levels 1 and 2.

**Validation**

- component tests;
- accessibility automated tests;
- keyboard manual test;
- responsive test;
- cold-reader test with recorded findings;
- visual regression test.

**Commit**

`feat(flora): add enterprise canvas for living twins`

**PR title**

`Add Flora Enterprise Canvas and governed drill-down`

### PR 7 — Governed user feedback

**Mission**

Allow the user to improve the Twin without silently changing it.

**In scope**

- challenge statement;
- add human knowledge;
- create Unknown;
- flag Contradiction;
- request Evidence;
- request refresh or nested Twin;
- candidate/work-item persistence;
- attribution.

**Out of scope**

- automatic canonical update;
- collaborative workflow;
- account/provider overlays.

**Acceptance criteria**

- every submission is labelled and attributed;
- human knowledge is distinguishable from Evidence;
- feedback is linked to affected state;
- no submission mutates canonical state directly;
- user receives a clear outcome and next status.

**Validation**

- permission tests;
- type tests;
- state-transition tests;
- audit test;
- UX comprehension test.

**Commit**

`feat(flora): capture governed living twin feedback`

**PR title**

`Add governed feedback actions to the Enterprise Canvas`

## Sprint-level acceptance criteria

Sprint 1 is complete when:

- all accepted ADR obligations are implemented or explicitly deferred;
- the clean MOD package imports without mutation;
- duplicate import is idempotent;
- partial acceptance works;
- accepted canonical records use owning services;
- 24 pains remain projections;
- the user can understand and inspect the MOD Twin;
- lineage reaches the original package;
- Unknowns, Contradictions, human knowledge and freshness remain visible;
- accessibility and cold-reader tests pass;
- documentation and completion reports are current;
- architecture debt is explicit.

## Principles deferred

- full nested CSM Twin;
- universal package schema;
- automated canonical promotion;
- additional Canvas lenses;
- Provider Fit and bid strategy;
- automated outcome learning;
- cross-enterprise comparison.

## Required completion report for every PR

Return:

1. Summary.
2. Files changed.
3. Architecture references followed.
4. Accepted ADRs followed.
5. Objects affected.
6. Principles implemented.
7. Principles deferred.
8. Behaviour added or changed.
9. Validation performed.
10. Manual architecture review.
11. Known limitations.
12. Architecture debt.
13. Documentation updated.
14. Commit message.
15. PR title and summary.
16. Recommended follow-up.

## Sprint review

At completion, review:

- Did the imported Twin become durable memory?
- Did the interface improve enterprise understanding?
- Could users inspect why Flora believed a judgement?
- Did any view create unsupported meaning?
- Which package fields could not be mapped?
- Which UX terms confused cold readers?
- What should change in the Researcher package contract?
- Is the architecture ready for the CSM nested-Twin sprint?
