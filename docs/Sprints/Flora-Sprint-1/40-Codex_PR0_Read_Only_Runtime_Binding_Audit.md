# Codex Task — Flora Blueprint Import and Enterprise Canvas Code-Binding Audit

## Mission

Map the accepted Blueprint-import and Enterprise-Canvas architecture to the current Flora codebase before any runtime implementation.

The audit must identify the safest bounded implementation path for durable package receipt, candidate staging, canonical promotion, analytical projections, lineage and enterprise-first navigation.

This is a documentation-only task.

## Scope

### Files and modules in scope

Inspect:

- current Flora application and service structure;
- upload and file-storage code;
- persistence models and migrations;
- Source, Evidence, Observation and Enterprise Model runtime code;
- Knowledge Graph or relationship code;
- authentication and authorisation;
- current workspace, report and dashboard UI;
- API and frontend state management;
- test fixtures and CI;
- relevant architecture and runtime documentation.

Create:

- `docs/Architecture/Flora_Blueprint_Import_Code_Binding_Audit_v0.1.md`

Update the Document Map only if repository paths differ from the approved architecture package.

### Out of scope

- no runtime code changes;
- no database migrations;
- no package upload feature;
- no UI implementation;
- no opportunistic refactoring;
- no new canonical object or field;
- no change to Accepted ADRs.

## Architecture references

Read and follow:

- `CIOS-AI.md`
- `architecture/reference-architecture/CIOS-Reference-Architecture-v1.0.md`
- `architecture/reference-architecture/CIOS-Design-Doctrine.md`
- `architecture/reference-architecture/Architecture-Principles.md`
- `architecture/handbook/CIOS-Chief-Architect-Handbook.md`
- `architecture/reference-architecture/Glossary.md`
- `architecture/reference-architecture/Document-Map.md`
- `architecture/decisions/ADR-012-Governed-Blueprint-Package-Import-and-Canonical-Acceptance-Boundary.md`
- `architecture/decisions/ADR-013-Enterprise-Canvas-as-Primary-Living-Twin-Navigation.md`
- `architecture/founding-papers/FP-003-Flora-Intelligence-Architecture.md`
- EI-001, EI-002 and EI-012
- `docs/Architecture/Flora_Governed_Blueprint_Import_Runtime_Specification_v0.1.md`
- `docs/Architecture/CIOS_Blueprint_Package_Import_Profile_v0.1.md`
- `docs/Architecture/CIOS_Enterprise_Intelligence_Experience_Standard_v0.1.md`
- `docs/Architecture/Flora_Enterprise_Canvas_and_Drill_Down_Pattern_v0.1.md`
- `docs/Sprints/Flora-Sprint-1/Flora_Sprint_1_Governed_Blueprint_Import_and_Enterprise_Canvas_Delivery_Plan_v0.1.md`

## Objects affected

This task does not create runtime objects. It maps proposed runtime ownership for:

- Package Registry;
- Import Run;
- Candidate Import Record;
- Import Mapping;
- Import Ledger;
- Analytical Projection;
- existing Source, Evidence, Observation, Enterprise Model, Unknown, Contradiction and human-knowledge services;
- Enterprise Canvas read model.

## CIOS constraints

- Evidence is proof, not intelligence.
- Enterprise Models are durable memory.
- Reports and tiles are views.
- Package acceptance is not canonical acceptance.
- Do not propose direct persistence writes that bypass owning services.
- Preserve state-semantics separation.
- Preserve Unknowns and Contradictions.
- Label human knowledge.
- Do not create Pain Point as a canonical object.
- Do not infer Provider Fit or commercial opportunity.
- Use existing terminology.
- Expose uncertainty and architecture debt.

## Required audit content

The audit must include:

1. Repository and runtime overview.
2. Current upload and immutable-storage capability.
3. Current canonical services and owned validation.
4. Current data models and migrations relevant to import.
5. Existing object IDs and external-ID support.
6. Existing lineage and provenance support.
7. Existing UI architecture and navigation.
8. Existing auth and permission boundaries.
9. Current tests and fixtures.
10. Exact proposed bindings for every runtime component in the Import Runtime Specification.
11. Exact proposed bindings for the Enterprise Canvas read model and components.
12. Files likely to change in PRs 1–7.
13. Gaps where the architecture assumes a capability that code does not have.
14. Conflicts, duplicated concepts or terminology drift.
15. Recommended PR sequence and dependencies.
16. Risks, deferrals and review triggers.

For each proposed binding state:

- existing component or file;
- responsibility it already owns;
- proposed extension;
- why that location is appropriate;
- tests required;
- architecture risk;
- alternative considered.

## Acceptance criteria

The task is complete when:

- the audit names exact repository paths and symbols;
- no runtime code is changed;
- every new runtime object has a proposed owner;
- every canonical update identifies an existing owning service or a documented gap;
- the package adapter boundary is isolated;
- the projection/read-model boundary is explicit;
- import-run state is separated from EI lifecycles;
- idempotency and reversal have proposed persistence support;
- lineage has an end-to-end proposed route;
- UI implementation is bounded to the approved Sprint 1 Canvas;
- access-control assumptions are explicit;
- unresolved architecture questions are listed rather than guessed;
- the next PR can be issued without rediscovering the codebase.

## Validation

Perform:

- repository-wide search for relevant types and services;
- migration inventory;
- test inventory;
- current route and component map;
- current persistence and file-storage map;
- terminology search for conflicts;
- manual architecture compliance review.

Do not claim runtime tests were run if the task does not change runtime. Run existing documentation/link checks where available.

## Documentation

Create only the audit document unless a broken repository path requires a minimal documented correction.

## Commit

`docs(flora): map blueprint import and canvas runtime bindings`

## Pull Request

**PR title**

`Document Flora Blueprint import and Enterprise Canvas code bindings`

**PR summary must include**

- mission;
- scope;
- architecture alignment;
- files inspected and changed;
- proposed component bindings;
- principles implemented;
- unresolved gaps;
- validation;
- limitations;
- architecture debt;
- next recommended PR.

## Completion report

Return:

1. Summary.
2. Files changed.
3. Architecture references followed.
4. Accepted ADRs followed.
5. Components and objects mapped.
6. Principles implemented.
7. Principles deferred.
8. Validation performed.
9. Known limitations.
10. Architecture debt.
11. Documentation updated.
12. Commit message.
13. PR title and summary.
14. Recommended follow-up.
