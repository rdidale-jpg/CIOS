# Increment 04 — Phase A conformance and ownership review

Baseline verified before implementation: `ec0bd875ab2a780ff1551dcb2a239aa8a76eb402`.
PRs #530, #531 and #532 are merged. This assessment precedes runtime changes.

## Decision gate

The bounded capability can reuse existing owners without a new accepted ADR:
external developments remain Evidence, enterprise applicability/consequence remain
governed enterprise intelligence, and change interpretations/reassessment requests
are transient ADR-014/024 assessments. No external-event canonical object, new
Industry Twin lifecycle, durable inference or automatic write-back is introduced.
The proposed broader operating direction remains a proposal. A durable event
model, automatic cross-Twin promotion or new orchestration authority would require
separate architectural review and is outside this implementation.

ADR-002/009/012/026 have Accepted metadata. ADR-014/024 contain conflicting Draft header
metadata and explicit Accepted Status sections; ADR-024's concluding reconciliation
and ADR-026 explicitly recognize their accepted runtime boundaries. Those sources
are recorded as-is, not silently edited. EI-001/EI-002/EI-004/EI-012 are Draft.
IT-001 is Review and expressly documentation-only; it cannot prove a live generic
Industry Twin maintenance engine. The Presentation Model specification is design
material, not a claim of autonomous runtime refresh.

## Canonical boundary map and existing implementation

Paths below are relative to `cios/applications/flora/` unless stated otherwise.

| Concern | Canonical owner / existing runtime | Increment 04 use and preserved boundary |
| --- | --- | --- |
| Industry Twin | IT-001 (Review); `blueprint_import/industry_delta_adapter.py`, semantic import projections; `twin_inspection/industry.py` has Banking-specific presentation | Read existing promoted entities/Evidence only. Do not create a new Industry lifecycle or treat staged dossiers as accepted facts. |
| External developments | Existing `memory/repository.py::EvidenceRepository`; generic import `CanonicalPromotionService` | Explicitly annotated industry/external Evidence is the input; no event store, ingestion service or external-to-enterprise Observation promotion. |
| Identity and relationships | Canonical entity/relationship JSONL owned by existing import promotion; `semantic_twin.py::resolve_relationships` and `canonical_enterprise_id` | Resolve canonical endpoints through the existing semantic resolver. Direct governed links identify candidates only; membership never proves exposure or consequence. No fuzzy/name/keyword association. |
| Enterprise support | `ObservationMemoryService`, `ObservationRepository`, Evidence and Contradiction repositories | Read accepted enterprise-scoped Observations and resolved Evidence. A governed annotation explicitly links an interpretation to external Evidence and time context. No new Observation type or independent fact store. |
| Model/pressure truth | Existing `EnterpriseModelRepository`, ADR-026 `qualify_candidates` and `assess_material_pressure` | Identify existing attribute/pressure dependencies. Read-only qualification previews reuse ADR-026; no write from external development or transient interpretation. Actual future writes must use existing accepted owner path. |
| Comparison | `observatory/engine.py::observatory_snapshot`, `compare_observatory_snapshots` | Existing comparison explains changes in Observatory-derived organisations/hypotheses, not governed propagation. Do not use seed/sector scores as applicability evidence or invoke its commercial generation. |
| Economic/commercial reasoning | `enterprise_intelligence/runtime.py`, bounded retrieval/validator; development Banking pipeline and `opportunity_pipeline.py` | Keep differentiated exposure/mitigation as sourced explanations. No calculation, funded demand, buying intent or commercial engine invocation. |
| Import | ADR-012; `CanonicalPromotionService` approval, source mapping, compensation and lineage | Consume accepted records only. Staging/package acceptance does not prove canonical acceptance. Existing import can carry opt-in metadata without new canonical classes. |
| Research execution | `live/collect.py`, fetcher/documents/extractor/worker, source registry and progress files | Existing explicit collection runs remain separate from canonical acceptance. Evidence demands are returned as transient learning needs; no research dispatch or scheduler. |
| Presentation | Existing Canvas, Enterprise Memory panel, `enterprise_intelligence/retrieval.py::EvidencePackageV1.enterprise_context`, imported presentation contracts | Add read-only diagnostics to existing boundaries with qualifications and lineage. No new dashboard, presentation store or Navigator. |

## Minimum runtime contract

An accepted Evidence record can opt in with an `external_change` descriptor in
its existing `human_provenance`: canonical `scope_id`, `statement`, `time_context`.
Its scope is explicitly `industry` or `external`; the statement must have direct
source-clause support. Entity/relationship IDs are canonical endpoint vocabulary,
not presentation slugs or raw import candidates.

An accepted enterprise Observation can carry an `external_change_interpretation`
descriptor in its existing provenance: `evidence_id` (external development),
`time_context`, `applicability`, `applicability_basis`, optional `mechanism`,
`mitigation`, `consequence`, `unknown_refs`, and `contradiction_refs`. Enterprise
Evidence must separately support its basis and supplied assertions. This is
opt-in governed interpretation, not a deterministic domain/economic rules engine.
The external source remains context; it is never borrowed as enterprise proof.

Transient results distinguish NOT_APPLICABLE, POTENTIALLY_APPLICABLE,
APPLICABLE_WITH_EVIDENCED_CONSEQUENCE and UNRESOLVED. Missing or contradictory
support yields explicit evidence demands and preserves current state. Candidate
search is a bounded one-hop governed graph, not industry propagation. Exact
source event/time linkage prevents unrelated exposure facts implying consequence.
Only authorized target enterprise IDs may be returned. Results have stable IDs
and are computed without writes, so replay cannot append assessments or change
models. Bounded retrieval consumes only the requested enterprise's diagnostics.

## Assurance and maintenance limits

Core applicability/consequence Unknowns produce POTENTIALLY_APPLICABLE with an
explicit evidence demand; conflicting assertions produce UNRESOLVED. Non-core
Unknowns such as severity remain visible without inventing magnitude or blocking
an otherwise sourced consequence. Resolved conflicts remain inspectable lineage.
Canonical conflict records linked through supporting Evidence are inspected even
without redundant annotation links.

The implementation performs no canonical write, including when an ADR-026 preview
passes. The next action is review/research or the existing explicitly accepted
owner reassessment path. Current Model state is not overwritten by these results.
Read-model output is capped at 20 events per enterprise; a batch assessment caps
candidate enterprises at 50 and declares truncation. Current file-backed owners
are scanned; no cache, index or durable event ledger is introduced.
