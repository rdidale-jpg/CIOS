# Flora Blueprint Import Code-Binding Audit v0.1

**Status:** Read-only audit for Flora Sprint 1 PR0  
**Date:** 2026-07-09  
**Scope:** Blueprint package import, candidate staging, canonical promotion, analytical projections, lineage, and Enterprise Canvas binding to the current Flora codebase.  
**Runtime-change status:** No runtime code changes are proposed or made by this audit.

## 1. Audit summary

The current Flora runtime already has useful foundations for governed import: safe filesystem persistence, immutable-ish content-addressed PDF upload storage, durable JSONL Observation and Evidence ledgers, deterministic Observation fingerprints, Enterprise Model snapshot projection, source acquisition receipts with checksums, lineaged financial candidates, product session access checks, and a standard-library web route surface.

The codebase does **not** yet have Blueprint-package runtime objects, package-level registries, manifest validation, candidate import staging, import mapping review, import ledgers, reversal ledgers, durable analytical projections, a generic source registry, graph persistence, or an Enterprise Canvas read model. Those should be introduced as bounded documentation-aligned modules rather than by stretching the existing financial-report flow.

The safest implementation path is a documentation-led, service-owned import subsystem under `cios/applications/flora/blueprint_import/`, integrated with existing storage and memory services only at explicit promotion boundaries. Enterprise Canvas should be a read-model/view layer over accepted Enterprise Model state and versioned analytical projections, not a canonical object.

## 2. Architecture references followed

This audit was checked against:

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
- `architecture/enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md`
- `architecture/enterprise-intelligence/volume-1-enterprise-modelling/EI-002-Enterprise-Knowledge-Graph.md`
- `architecture/enterprise-intelligence/volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md`
- `docs/Architecture/Flora_Governed_Blueprint_Import_Runtime_Specification_v0.1.md`
- `docs/Architecture/CIOS_Blueprint_Package_Import_Profile_v0.1.md`
- `docs/Architecture/CIOS_Enterprise_Intelligence_Experience_Standard_v0.1.md`
- `docs/Architecture/Flora_Enterprise_Canvas_and_Drill_Down_Pattern_v0.1.md`
- `docs/Sprints/Flora-Sprint-1/Flora_Sprint_1_Governed_Blueprint_Import_and_Enterprise_Canvas_Delivery_Plan_v0.1.md`

## 3. Repository and runtime overview

Flora is a Python application using standard-library HTTP serving rather than a web framework. The main route table is `cios/applications/flora/web/app.py`, and product pages are mostly string-rendered HTML in `workspace`, `live`, `digital_twins`, `memory`, and `observatory` view modules.

Persistent pilot state is file-backed under `FLORA_DATA_DIR` or `/var/data/flora` via `cios/applications/flora/storage.py`. Current durable memory uses JSON/JSONL rather than SQL migrations. There is no Alembic, Django migration, or SQL migration tree in the repository.

Canonical-ish runtime memory currently lives in `cios/applications/flora/memory/`:

- `models.py` defines Flora-specific `Observation`, `EnterpriseModel`, `EnterpriseModelAttribute`, `EnterpriseUnknown`, and deterministic Observation identifiers.
- `repository.py` implements JSONL Evidence and Observation repositories and atomic Enterprise Model snapshots.
- `service.py` owns decomposition of accepted Evidence into factual claims, Observation validation, and Enterprise Model updates.

Generic SDK primitives also exist in `cios/core/models.py`, `cios/graph/models.py`, and `cios/memory/models.py`, but they are deliberately passive or thin model packages and should not be treated as the current Flora import runtime.

## 4. Current upload and immutable-storage capability

### Existing capability

- `cios/applications/flora/storage.py` provides safe path resolution, writable directory checks, atomic text/JSON writes, and startup directory provisioning.
- `REQUIRED_DIRS` already includes `ai_financial_reports/uploads`, `ai_financial_reports/runs`, `documents`, `live_evidence`, `collection_manifests`, `memory`, and `memory/enterprise_models`.
- `cios/applications/flora/document_review.py:create_upload_run` computes a SHA-256 checksum for uploaded PDFs and stores them under `ai_financial_reports/uploads/{checksum-prefix}.pdf`.
- Rapid financial acquisition receipts preserve SHA-256, URL, content type, byte count, validation result, and failure state in `cios/applications/flora/financial_intelligence/rapid_sources.py` and downstream candidates.

### Binding implication

Blueprint package receipt should reuse `storage.data_path`, `ensure_writable_dir`, `atomic_write_json`, and checksum patterns. It should not reuse `create_upload_run` because that flow is PDF/Financial-Intelligence-specific, calls a provider, creates review claims, and uses `air-*` IDs.

### Gap

There is no generic package archive abstraction, no content-addressed directory for package ZIPs or unpacked files, no manifest-level checksum verifier, no immutable Package Registry, and no package adapter registry.

## 5. Current canonical services and owned validation

### Existing owners

- `ObservationMemoryService` is the current owner for turning accepted Evidence-like rows into validated Observations and Enterprise Model updates.
- `Observation` enforces evidence-backed support, human provenance, non-speculative atomic statements, non-recommendation language, and deterministic IDs.
- `validate_factual_claim` and `CLAIM_VOCABULARY` are the narrow current canonical validation surface for factual claim types.
- `EvidenceRepository` saves Evidence rows but currently accepts dictionaries with only `evidence_id` required.
- `EnterpriseModelRepository` persists derived Enterprise Model snapshots by enterprise ID.

### Binding implication

Canonical promotion from Blueprint import should call owning services or introduce missing owners. It must not write directly into `memory/observations.jsonl`, `memory/evidence.jsonl`, or `memory/enterprise_models/*.json` outside repository/service APIs.

### Gaps

- Source has no canonical owning repository/service comparable to Evidence/Observation.
- Enterprise entities, relationships, Unknowns, Contradictions, and human-knowledge records do not yet have complete Flora-owned canonical services.
- Existing claim vocabulary is BT/financial-first and too narrow for Blueprint import.
- `ObservationMemoryService.observation_from_evidence` sets `lifecycle_state` to `Validated` for financial metrics, which is terminology drift against state-semantics separation because Observation lifecycle and measurement state should remain separate.

## 6. Data models and migration inventory relevant to import

### Current models

- Flora durable memory dataclasses: `cios/applications/flora/memory/models.py`.
- Flora memory repositories: `cios/applications/flora/memory/repository.py`.
- Passive SDK memory: `cios/memory/models.py`.
- Generic core Evidence/Observation/Entity/Relationship: `cios/core/models.py`.
- Generic graph models: `cios/graph/models.py`.
- Observatory local DTOs and graph edges: `cios/applications/flora/observatory/models.py`.
- Financial candidate DTOs: `cios/applications/flora/financial_intelligence/adapters.py` and `rapid_candidates.py`.

### Migration inventory

No SQL, Django, or Alembic migrations were found. Current persistence evolution is file-schema/version driven. Blueprint import PRs should therefore add JSON/JSONL schemas and migration-safe readers before considering database migration work.

## 7. Existing object IDs and external-ID support

### Reusable capability

- `stable_observation_fingerprint` and `stable_observation_id` provide deterministic Observation IDs from enterprise, type, statement, attribute, and effective date.
- Financial candidates derive deterministic IDs from source hash, source locator, metric identity, period, scope, basis, state, and value.
- Evidence rows can store arbitrary `source_id`, `source_url`, `source_locator`, `package_sha256`, page ranges, and raw source metadata.
- Enterprise model file paths are safe-slugged and hash-suffixed by enterprise ID.

### Gap

There is no generic `external_id`, `package_id`, `package_version`, `original_stable_id`, `source_file`, worksheet/section locator, import-run ID, or canonical-ID mapping table. These should be first-class import staging fields, not hidden in free-form metadata.

## 8. Existing lineage and provenance support

### Reusable capability

- Observation records preserve `supporting_evidence_ids`, provenance type, freshness, dates, contradiction state, and supersession fields.
- Evidence rows can preserve source URLs, source locators, page ranges, document hashes, package hashes, collection timestamps, adapter names, and extraction versions.
- Financial candidate extraction preserves source SHA-256 and page/table/row/column locator context.
- Observatory graph edges model evidence-to-signal-to-insight-to-thesis-to-argument-to-recommendation lineage for a read-only reasoning view.

### Gaps

- No end-to-end import ledger connects received package → adapter parse → candidate record → mapping decision → canonical object → analytical projection → Canvas tile.
- No durable graph persistence for imported entities/relationships.
- No reversal ledger or idempotency ledger.
- Human-supplied knowledge has validation support on Observations but no dedicated import category/service.

## 9. Existing UI architecture and navigation

### Existing surface

- `cios/applications/flora/web/app.py` owns routes and dispatch.
- `cios/applications/flora/workspace/views.py` owns common page rendering and legacy landing/radar/scoring/case views.
- `cios/applications/flora/digital_twins.py` implements the current BT Digital Twin product page over Enterprise Model and Financial Intelligence runs.
- `cios/applications/flora/memory/views.py` renders factual digital twin memory panels.
- `cios/applications/flora/observatory/views.py` renders an Observatory experience with cards, detail routes, unknowns, contradictions, and lineage details.

### Binding implication

Enterprise Canvas should extend the `digital_twins` product surface or be placed in a new bounded `cios/applications/flora/enterprise_canvas/` module. It should remain a read-model presenter, not a persistence owner.

### Gaps

- No Canvas read-model module, no generic Twin route, no lens switcher, no tile DTO, no detail panel route, no lineage journey route, and no governed feedback staging for Canvas corrections.
- Current Digital Twin is BT-specific and Financial-Intelligence-specific.

## 10. Existing auth and permission boundaries

### Existing capability

- `cios/applications/flora/access.py` supports product-session-style checks using `X-Flora-User`, `flora_user`, `X-Flora-Enterprises`, and `flora_enterprises`.
- Financial Intelligence support diagnostics are protected by `FLORA_SUPPORT_TOKEN` or `FLORA_ADMIN_TOKEN` in `web/app.py`.
- Run IDs for Financial Intelligence are regex-bounded.

### Gaps

- There is no role model for package receipt, package review, canonical promotion, reversal, Canvas viewing, or feedback submission.
- Current access checks are not centralized middleware and cover only selected financial routes.
- Blueprint import needs explicit permissions: `package.upload`, `package.review`, `candidate.promote`, `candidate.reject`, `import.reverse`, `canvas.view`, and `feedback.stage` or equivalent.

## 11. Current tests and fixtures

The repository has extensive pytest coverage under `tests/`, including storage runtime, web routing, financial intelligence, rapid extraction/acquisition, memory repositories, Enterprise Memory, graph models, core models, Observatory, and runtime alignment. Test fixtures include rapid financial data and opportunity assistant JSON fixtures. No Blueprint package fixtures or Canvas fixtures currently exist.

Recommended test additions are listed in each binding below.

## 12. Exact proposed bindings for Import Runtime Specification components

| Runtime component | Existing component/file | Current responsibility | Proposed extension | Why this location | Tests required | Architecture risk | Alternative considered |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Package Registry | New `cios/applications/flora/blueprint_import/registry.py`; storage via `cios/applications/flora/storage.py` | Safe file persistence exists, no registry | JSON registry records under `data_path('blueprint_import','packages')`; package ID/version/checksum/file inventory/state | Package registry is import workflow state, not canonical memory | Unit tests for register/get/list/idempotent duplicate receipt/checksum mismatch | Treating package acceptance as canonical acceptance | Reusing Financial Intelligence run records rejected: wrong lifecycle and semantics |
| Immutable Package Archive | New `blueprint_import/archive.py`; reuse `storage.py` | Uploads store PDFs by checksum prefix | Store exact package bytes by full checksum; unpack read-only copy; write normalized manifest alongside, never inside original | Keeps ADR-012 immutable package boundary | Tests for path traversal, duplicate archive, checksum, ZIP slip prevention | Editing original package | Using `documents/` rejected: too generic/no package semantics |
| Import Run | New `blueprint_import/runs.py` | Financial runs use JSON files and progress states | `import_run_id`, package ref, actor, timestamps, runtime state only | Keeps import-run state separate from EI object state | State transition tests | Conflating with Observation lifecycle | Extending `ai_financial_reports/runs` rejected |
| Package Adapter Boundary | New `blueprint_import/adapters/` | Financial adapters parse PDFs/tables | Adapter interface for profile-native and MOD legacy packages; emits Candidate Import Records only | Isolates package syntax from canonical services | Adapter contract tests with fixtures | Adapter accidentally writes canonical memory | Embedding adapters in `document_review.py` rejected |
| Manifest Validator | New `blueprint_import/manifest.py` | Financial source manifests are config-specific | Validate Blueprint profile manifest, file checksums, record sets, governing architecture | Profile-owned package boundary | Valid/invalid manifest fixture tests | Silent inference/repair | Reusing collection profile loader rejected |
| Candidate Import Record | New `blueprint_import/candidates.py` | Financial candidates exist but are financial facts only | Durable staged candidate records with record class, truth class, external ID, locator, proposed effect | Staging is import-specific | Serialization, idempotency, unresolved mapping tests | Promoting candidate data too early | Reusing financial candidate DTOs rejected |
| Import Mapping | New `blueprint_import/mapping.py` | Claim vocabulary maps limited evidence to attributes | Map candidate classes to owning canonical service or documented gap; persist decisions | Central place to expose unresolved mappings | Mapping table tests | Hidden canonical writes | Direct model mutation rejected |
| Canonical Promotion Orchestrator | New `blueprint_import/promotion.py`; call `ObservationMemoryService`, `EvidenceRepository`, future Source/Graph services | Existing service validates Evidence→Observation→Enterprise Model | Object-level promotion with dry-run effect, review decision, service call, ledger entry | Explicit acceptance boundary | Dry-run and promote tests; no direct file writes | Bypassing owners | Bulk import into JSON files rejected |
| Import Ledger | New `blueprint_import/ledger.py` | Observation JSONL ledger exists for observations only | Append-only import events: received, parsed, staged, reviewed, promoted, rejected, reversed | Audit trail separate from canonical object ledgers | Append/replay tests | Ledger used as canonical truth | Stuffing into package registry rejected |
| Idempotency Store | New `blueprint_import/idempotency.py` | Deterministic Observation/candidate IDs exist | Keys for package checksum, candidate original ID, proposed canonical target, adapter version | Prevent duplicate re-import effects | Re-import tests | Duplicate canonical objects | Relying only on Observation fingerprints rejected |
| Reversal Support | New `blueprint_import/reversal.py`; call owning services where reversal is supported | Observation model has supersession/retirement fields, no import reversal | Persist compensating action plan and supported reversal outcomes; defer unsupported owner reversal | ADR-012 requires reversibility without unsafe deletes | Reversal-plan tests | Deleting historical evidence | Physical delete rejected |
| Analytical Projection | New `blueprint_import/projections.py` or `enterprise_canvas/projections.py` | Observatory and digital twins compute views in memory | Versioned projection records, linked to package and canonical IDs, never canonical facts | Keeps reports/tiles as views | Projection serialization/freshness tests | Projection mistaken for Enterprise Model | Storing in EnterpriseModel attributes rejected |
| Lineage Router | New `blueprint_import/lineage.py`; UI in Canvas detail | Evidence IDs and graph edges exist | Resolve package → candidate → canonical object → evidence/source locator → tile | Supports inspectable user journey | Route/read-model tests | Broken trust path | Hiding lineage in metadata rejected |
| Package Review UI | New routes in `web/app.py`, views in `blueprint_import/views.py` | Existing routes dispatch manually | Minimal review screens for package state, candidates, mappings, ledgers | Keeps UI bounded | Route tests, permission tests | UI implies canonical acceptance | Reusing AI report review rejected |

## 13. Exact proposed bindings for Enterprise Canvas read model and components

| Canvas component | Existing component/file | Current responsibility | Proposed extension | Why this location | Tests required | Architecture risk | Alternative considered |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Canvas Read Model | New `cios/applications/flora/enterprise_canvas/read_model.py` | `digital_twins.py` reads BT Enterprise Model directly | Compose enterprise header, lenses, tiles, detail summaries from Enterprise Model, projections, Unknowns, Contradictions, lineage | Canvas is a view/read model | Read-model fixture tests | Tile becoming canonical object | Persisting tile objects rejected |
| Enterprise Header | `digital_twins.py` pattern; new `enterprise_canvas/views.py` | BT summary header | Generic header with enterprise, Twin version, effective date, source cut-off, import state, limitation | Matches ADR-013 and Canvas pattern | HTML route tests | One synthetic health score | Dashboard score rejected |
| Organisation Lens | New `enterprise_canvas/lenses.py` | Observatory cards group organisations; no imported org lens | Generate six to ten traceable organisation/domain tiles from entities/projections | Default Sprint 1 lens | Deterministic tile-set tests | Inventing tiles for visual balance | Hard-coded MOD tile list rejected except as fixture expectation |
| Intelligence Tile DTO | New `enterprise_canvas/models.py` | No tile model | Non-canonical DTO with name, role, state, pain/pressure text, material change, markers, lineage refs | Makes view semantics explicit | Model validation tests | Treating Pain Point as canonical object | Reusing `Entity` rejected |
| Detail Panel | New `enterprise_canvas/views.py` | Observatory org detail pages demonstrate progressive disclosure | Detail route/panel with purpose, facts, change, pains, responses, unresolved items, stakeholders, lineage | Bounded product UI | Route and content tests | Commercial overclaim | Report page rejected |
| Lineage Inspection | New `enterprise_canvas/lineage_views.py`, backed by `blueprint_import/lineage.py` | Observatory `details` expose traces | Navigate from tile to candidate/evidence/source/package location | Implements ADR-005/ADR-013 | Lineage fixture tests | Missing imported source locator | Metadata-only lineage rejected |
| Governed Feedback | Existing `workspace/feedback.py`, `live/alignment.py` | Writes feedback/logbook/live alignment records | Stage Canvas feedback as human-supplied candidate knowledge with provenance; no overwrite | Reuses feedback intent but needs new object semantics | Feedback staging tests | Silent canonical overwrite | Direct EnterpriseModel edit rejected |
| Canvas Routes | `web/app.py` | Manual route dispatch | Add `/digital-twins/{enterprise_id}/canvas`, lens and tile detail routes | Current app route owner | HEAD/GET/404/access tests | Generic route conflicts with BT routes | New server framework rejected |

## 14. Files likely to change in PRs 1-7

### PR1 — Import package receipt and registry

- Add `cios/applications/flora/blueprint_import/__init__.py`
- Add `archive.py`, `registry.py`, `manifest.py`, `models.py`
- Add `tests/test_flora_blueprint_import_registry.py`
- Possibly update `cios/applications/flora/storage.py` `REQUIRED_DIRS` for `blueprint_import/...`

### PR2 — Adapter boundary and candidate staging

- Add `blueprint_import/adapters/`
- Add `candidates.py`, `runs.py`, `ledger.py`
- Add Blueprint package fixtures under `tests/fixtures/blueprint_import/`
- Add tests for native and MOD legacy adapter outputs

### PR3 — Mapping and dry-run canonical effects

- Add `mapping.py`, `promotion.py`, `idempotency.py`
- Extend only through service APIs in `cios/applications/flora/memory/service.py` if an owner method is missing
- Tests for proposed effects: create/update/unchanged/conflict/contradiction/reject/quarantine/unresolved

### PR4 — Source, Unknown, Contradiction, human-knowledge owner gaps

- Add or extend bounded owner services, likely under `cios/applications/flora/memory/` or dedicated submodules
- Add repositories for Source registry, Unknown/Contradiction records if approved by architecture
- Tests for human provenance and conflict preservation

### PR5 — Analytical projections and lineage route

- Add `blueprint_import/projections.py`, `lineage.py`, `reversal.py`
- Add projection fixtures and replay tests
- Add reversal-plan tests without unsafe deletes

### PR6 — Enterprise Canvas read model

- Add `cios/applications/flora/enterprise_canvas/`
- Add `models.py`, `read_model.py`, `lenses.py`, `views.py`, `lineage_views.py`
- Add tests for read model, tile traceability, progressive disclosure, Unknowns/Contradictions visibility

### PR7 — Route integration, access checks, documentation hardening

- Update `cios/applications/flora/web/app.py`
- Extend `cios/applications/flora/access.py` with package/canvas permissions
- Add route tests and access tests
- Add or update user-facing docs after runtime behavior exists

## 15. Main architecture gaps

1. No Package Registry or immutable package archive.
2. No Blueprint manifest/profile validator.
3. No candidate staging persistence or review workflow.
4. No import mapping table or unresolved-mapping model.
5. No import ledger, idempotency ledger, or reversal ledger.
6. No generic Source owner/service.
7. No complete Unknown, Contradiction, human-knowledge import services.
8. No durable Knowledge Graph persistence or imported relationship owner.
9. Existing claim vocabulary is too narrow for Blueprint semantics.
10. Existing access control is limited and route-local.
11. No Enterprise Canvas read model, tile DTO, lens model, or lineage journey.
12. No Blueprint package fixtures.
13. No database/migration framework; all persistence changes must be schema-versioned file additions unless architecture chooses otherwise.

## 16. Conflicts, duplicated concepts, and terminology drift

- `ObservationMemoryService.observation_from_evidence` currently uses `lifecycle_state="Validated"` for financial metrics. This conflicts with the required separation between Observation lifecycle state and financial measurement state.
- Generic `cios/core/models.py:Observation` describes a detected commercial signal, while Flora memory `Observation` is closer to EI-012 durable memory. Import implementation must use the Flora durable memory owner, not the thin SDK model, for canonical promotion.
- `Relationship` exists in `cios/core/models.py` and graph primitives exist in `cios/graph/models.py`, but there is no persistent Flora Knowledge Graph owner. Imported relationships should not be force-fit into core Relationship without an owner decision.
- Observatory uses `KnowledgeGraphEdge` as a local reasoning view, not as durable graph persistence.
- Existing “Digital Twins” UI is BT/Financial-Intelligence-specific and should not be renamed into Enterprise Canvas without creating a generic read-model boundary.
- “Pain” appears in UI/reasoning text; it must remain a view/projection/description, not a canonical Pain Point object.

## 17. Recommended implementation sequence and dependencies

1. **PR1: Package receipt, immutable archive, registry, manifest validation.** Dependency-free and creates the governed package boundary.
2. **PR2: Adapter boundary and candidate staging.** Depends on PR1 registry/archive. Produces candidates only; no canonical writes.
3. **PR3: Mapping review, proposed effects, idempotency ledger.** Depends on staged candidates. Dry-run first.
4. **PR4: Canonical owner gap closure.** Add or formalize services for Source, Unknown, Contradiction, human knowledge, and relationship/graph promotion before broad promotion.
5. **PR5: Promotion ledger, reversal plans, analytical projections, lineage resolver.** Depends on object-level owners and mapping decisions.
6. **PR6: Enterprise Canvas read model and bounded Organisation Lens.** Depends on accepted projections and lineage resolver.
7. **PR7: Route/access integration and final Sprint 1 UI hardening.** Depends on stable read model and import lifecycle.

## 18. Risks, deferrals, and review triggers

### Risks

- Accidentally treating package acceptance as canonical acceptance.
- Writing directly to Enterprise Model snapshots without Observation/Evidence ownership.
- Importing analytical language as canonical facts.
- Losing package source location and original stable IDs.
- Creating Canvas tiles as canonical intelligence objects.
- Overclaiming Provider Fit, opportunity, or commercial action from imported Blueprint content.

### Deferrals

- Database migration framework selection.
- Full graph database/runtime persistence.
- Multi-enterprise role model beyond header/cookie pilot access controls.
- Non-Organisation Canvas lenses after Sprint 1.
- Automated reversal execution where canonical owners do not yet support safe compensation.

### Review triggers

- Any new canonical object, field, enum, lifecycle, or Enterprise Model path not owned by an approved architecture document.
- Any candidate promotion path that bypasses owning services.
- Any UI that hides Unknowns, Contradictions, human knowledge, effective dates, freshness, or lineage.
- Any import adapter that mutates canonical state.
- Any proposal to make Pain Point, Tile, or Report a canonical object.

## 19. Validation performed

- Repository-wide search for relevant runtime types, services, upload paths, storage helpers, auth checks, graph models, memory models, Unknown/Contradiction terminology, and route ownership.
- Migration inventory search for SQL/Alembic/Django migration files.
- Test inventory through repository file listing and targeted search.
- Current route and component map from `cios/applications/flora/web/app.py` and product view modules.
- Current persistence and file-storage map from `storage.py`, `document_review.py`, and memory repositories.
- Terminology conflict review against ADR-012, ADR-013, EI state-semantics separation, and CIOS AI context.

No runtime tests were required or run for this documentation-only audit.

## 20. Confirmation of read-only runtime boundary

This audit creates documentation only. It does not modify runtime Python modules, configuration, migrations, tests, fixtures, or executable assets. The proposed implementation sequence intentionally keeps all runtime changes for later PRs.
