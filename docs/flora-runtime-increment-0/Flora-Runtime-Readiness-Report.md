# Flora Runtime Readiness Report

**Readiness outcome:** Ready with conditions.

## Executive summary

The repository is architecturally ready to estimate Increment 1, the Read-Only Object Workspace Slice, but not ready to implement a broad runtime foundation without conditions. Accepted ADR-024 governs the hybrid runtime. ADR-001, ADR-005, ADR-014 and ADR-016 are accepted and provide sufficient authority for a read-only, evidence/Observation-aware workspace. FEIR-001, FA-001, ADR-025, the Flora Product Architecture Blueprint and the runtime implementation plan are Proposed, so they guide but do not override accepted ADRs or owning Enterprise Intelligence papers.

Increment 1 can proceed if it is bounded to read-only projection over the UK Banking governed corpus and if it implements no generated recommendations, write-back, runtime graph product selection or canonical mutation. The principal blockers for broader scope are incomplete accepted status for FA-001/ADR-025/FEIR-001, uneven asset identity conventions, missing formal read contracts, and unresolved audit retention/access detail.

## Governing authority findings

| ID | Title | Status | Owner | Path | Increment 1 finding |
| --- | --- | --- | --- | --- | --- |
| ADR-001 | Observations as Atomic Intelligence Unit | Accepted | Rob / CIOS | `architecture/decisions/ADR-001-Observations-as-Atomic-Intelligence-Unit.md` | Governs Observation primacy and evidence lineage. |
| ADR-005 | No Recommendation Without Inspectable Lineage | Accepted | Rob / CIOS | `architecture/decisions/ADR-005-No-Recommendation-Without-Inspectable-Lineage.md` | Blocks strong Recommendation behaviour in Increment 1. |
| ADR-014 | Evidence-Governed Enterprise Intelligence Reasoning Runtime | Accepted | Not explicitly line-formatted; CIOS ownership implied | `architecture/decisions/ADR-014-Evidence-Governed-Enterprise-Intelligence-Reasoning-Runtime.md` | Authorises bounded retrieval, structured packages, safe unavailable state; reasoning remains out of scope for Increment 1. |
| ADR-016 | Knowledge Packs as Standard Exchange Mechanism | Accepted | Rob / CIOS | `architecture/decisions/ADR-016-Knowledge-Packs-as-Standard-Exchange-Mechanism.md` | Governs Knowledge Pack handling; acceptance is not canonical fact promotion. |
| ADR-024 | Hybrid Enterprise Intelligence Runtime | Accepted | Rob / CIOS | `architecture/decisions/ADR-024-Hybrid-Enterprise-Intelligence-Runtime.md` | Primary accepted runtime decision. Flora owns orchestration/provenance/runtime state/presentation, not governed knowledge. |
| ADR-025 | Flora as Enterprise Intelligence Workspace | Proposed | Rob / CIOS | `architecture/decisions/ADR-025-Flora-as-the-Enterprise-Intelligence-Workspace.md` | Useful product/runtime intent but not accepted; runtime plan must not treat it as binding ADR. |
| FEIR-001 | Flora Enterprise Intelligence Runtime Architecture v1.0 | Proposed | Rob / CIOS | `architecture/specifications/flora/FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md` | Owns proposed runtime object classes, audit and security expectations; needs acceptance or explicit Increment 1 specification baseline. |
| FA-001 | Flora Enterprise Intelligence Workspace Reference Architecture | Proposed | Not in metadata; CIOS Chief Architect implied | `architecture/reference-architectures/FA-001-Flora-Enterprise-Intelligence-Workspace-Reference-Architecture.md` | Reference standard for Focus Object and workspace regions; subordinate where conflicts exist. |
| CIOS-RA-v1.0 | CIOS Reference Architecture v1.0 | Existing architecture source; status not captured in header | Rob / CIOS implied | `architecture/reference-architecture/CIOS-Reference-Architecture-v1.0.md` | Governs no-second-source-of-truth layering. |
| EI-001 | Enterprise Model Specification | Draft | Rob / CIOS | `architecture/enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md` | Draft durable memory model; read only in Increment 1. |
| EI-002 | Enterprise Knowledge Graph | Draft | Rob / CIOS | `architecture/enterprise-intelligence/volume-1-enterprise-modelling/EI-002-Enterprise-Knowledge-Graph.md` | Draft relationship semantics; do not implement durable graph changes. |
| EI-012 | Enterprise Observation Model | Draft | Rob / CIOS | `architecture/enterprise-intelligence/volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md` | Draft Observation doctrine; supported by accepted ADR-001. |
| FP-009 | Hypothesis Validation Standard | Founding paper; status not machine-readable in header | Rob / CIOS implied | `architecture/founding-papers/FP-009-Hypothesis-Validation-Standard.md` | Governs hypothesis validation; Increment 1 may display but not validate/promote hypotheses. |
| Flora governance | DoD, compliance checklist, review workflow | Active governance docs; statuses vary | CIOS Chief Architect | `architecture/governance/` | Provide validation gate; not runtime interfaces. |

### Conflicts and ambiguities

- ADR-025 is Proposed while the runtime plan lists it in governing authority. Treat ADR-025 as non-binding until accepted.
- FEIR-001 is Proposed but ADR-024 names it as owning architecture paper. Increment 1 should either accept FEIR-001 or create a narrow Increment 1 runtime read specification before implementation.
- EI-001, EI-002 and EI-012 are Draft but are owning semantics. Accepted ADRs reinforce them; Flora must not redefine them.
- CIOS Reference Architecture status is not captured in the first header block. Add status metadata in a later documentation hygiene mission.

## Asset inventory summary

The governed corpus for the first slice should be UK Banking because it has a manifest/register, industry assets, reinvention observations/hypotheses, governance reports and Flora navigation specification. Existing asset formats are Markdown, JSON, JSONL-like runtime stores and Python dataclasses. Identity conventions exist but are heterogeneous (`BK-*`, `EK-*`, `FEIR-001`, `ADR-*`, file paths, dataclass IDs). Increment 1 ingestion is possible as repository read/projection, not as canonical import.

## Identity findings

Stable document identifiers exist for architecture sources and many banking assets. Stable object identity is only partially ready: Evidence and Observation classes in code expose IDs, banking registers carry asset IDs, and architecture documents carry formal IDs, but there is no single minimal Focus Object identity envelope across document, asset, Observation, Unknown, Contradiction and candidate classes. Increment 1 needs a read-only identity envelope, not a semantic redesign.

Minimum identity contract:

```text
object_id, object_type, authority_class, lifecycle_status, version, source_path,
source_asset_id, evidence_cutoff, owner, provenance_refs, supersedes, replaces
```

Relationship projection should use deterministic runtime relationship IDs derived from source object ID, relationship type, target object ID and source asset version; this is a projection key, not canonical graph identity.

## Schema findings

Most Increment 1 contracts are missing as versioned interface specifications. Existing code/dataclasses and manifests are usable evidence for estimability. Interface stubs should be documentation-only in Increment 1 planning: AssetRead, ManifestRead, FocusObjectProjection, RelationshipProjection, EvidenceObservationAvailability, UnknownResponse, ContradictionResponse, LineageResponse, WorkspaceState, AuditEvent, IngestionReport and SafeUnavailableResponse.

## Existing Flora implementation findings

Current Flora is a collection of pilot/runtime modules, including web views, workspace state, access checks, blueprint import, live evidence collection, enterprise intelligence retrieval/persistence and enterprise canvas read models. The implementation contains reusable read-model patterns, access helpers and lineage display concepts, but also contains pilot authentication, seeded data, generated HTML views, live collection/write paths and scoring/pipeline code that must be isolated from Increment 1.

Mapping to FA-001:

- Focus Object: present in concept across web/workspace pages, not unified as a governed object contract.
- Perspectives: present as page routes/views; not yet a governed perspective interface.
- Reasoning: present in multiple pilot components; Increment 1 should not activate reasoning orchestration.
- Unknowns/Contradictions: visible in web pages and banking assets; response contracts missing.
- Explainability/lineage: implemented in enterprise canvas completion history and some views; formal lineage response missing.
- No second source of truth: existing import and live paths include write behaviour; Increment 1 must use read-only adapters and exclude collection/promotion routes.

## Access findings

Existing pilot access supports owner recognition, user enterprise access and enterprise allow-list checks, but it is not enterprise SSO and should be treated as a pilot mechanism only. Increment 1 requires authenticated identity, enterprise/workspace boundary, asset-level and object-level access checks, cross-enterprise retrieval denial, restricted audit access and fail-closed safe-unavailable responses.

## Audit findings

Audit baseline is ready at specification level but not as a formal contract. Increment 1 must separate operational telemetry, reasoning provenance, human decision history and canonical knowledge history. Only operational audit for read/projection is required in Increment 1.

## Risks, Unknowns and blockers

### Key risks

- Proposed governance documents may be mistaken for accepted decisions.
- Runtime projection could accidentally duplicate canonical Evidence/Observation/Enterprise Model truth.
- Existing pilot code includes write/collection behaviours unsuitable for read-only Increment 1.
- Asset metadata and freshness are inconsistent across banking files.

### Unknowns

- Final runtime graph persistence approach.
- Formal context package schema.
- Audit retention/privacy periods.
- Accepted human role taxonomy.
- Write-back proposal contract.
- Complete object-level access policy.

### Blockers for Increment 1

No absolute architectural blocker exists if Increment 1 is narrowed to read-only projection and documentation contracts are accepted before coding. Blocking conditions for broader scope: accepted FEIR/FA/ADR-025 status, formal identity/read contracts, and access/audit retention decisions.

## Recommendations

1. Proceed to Increment 1 only as a read-only UK Banking Focus Object slice.
2. Create a narrow Increment 1 interface specification before implementation; do not create broad ADRs for implementation details.
3. Treat FEIR-001 and FA-001 as proposed guidance until accepted or explicitly baselined.
4. Isolate existing collection, promotion, scoring and reasoning routes from the read-only slice.
5. Validate every view against no-second-source-of-truth, Unknown/Contradiction preservation and inspectable lineage.
