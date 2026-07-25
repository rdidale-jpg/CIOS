# Flora governed Twin import: repository audit and smallest increment

## Executive decision

**Recommendation: Revise before production merge.** The repository does contain the reported importer; rebuilding it would violate its canonical boundary. This increment therefore adds only guided expectation metadata, deterministic maturity assessment and read-only portfolio/opportunity projection primitives. It deliberately does not claim that every requested Twin is canonically promotable: current promotion supports evidence, observations, contradictions, unknowns, entities, relationships and human knowledge, but not dedicated Industry, Market Participant, Opportunity or Control Body canonical constructors.

## Evidence-based lifecycle and architecture-to-runtime map

| Lifecycle/component | Implementation and persistence | State and tests | Limitation |
|---|---|---|---|
| HTTP entry/upload | `blueprint_import/views.py`; routes in `web/app.py` | Existing interface tests | ZIP/multipart web flow; historically Enterprise-oriented |
| Receipt/archive/checksum | `registry.py`, `archive.py`, `models.py` | Immutable archive plus registry/import-run JSON; registry/validation tests | 50 MB UI limit; ZIP only |
| Manifest | `manifest.py`, `validator.py` | Root `blueprint_manifest.json`; validation tests | Identity requires package/version, enterprise and profile; no general Twin-package schema discriminator |
| Validation/staging | `validator.py`, `candidates.py`, `cios_twin_adapter.py` | Candidate JSON and summary JSON; validation tests | NDJSON and CIOS workbook adapter; narrative is non-canonical |
| Mapping/review | `mapping.py`, `review.py`, `review_plan.py` | Immutable decision/mapping records; review-planning tests | UI creates safe defaults only for accepted records |
| Restaging/dry run | `restage.py`, `planning.py` | Versioned staging history and persisted plan; restage/planning tests | Mapping-version invalidation is deliberate |
| Promotion | `promotion.py`, `atomicity.py` | Approval and execution JSON, canonical repositories, rollback; promotion tests | Constructor allow-list is narrower than requested Twin portfolio |
| Ledger/audit | `ledger.py`, promotion/review repositories | Append-only JSONL/JSON records | File-backed runtime, not a transactional multi-node database |
| Post-import view | `views.py`, Enterprise Canvas access/views | Import record/completion/Canvas tests | Consistent generic Twin overview was absent |

Authority remains at the established review/approval boundary. Guidance is package metadata, maturity is a derived assessment, and portfolio/opportunity records are read projections; none is a second importer or canonical store.

## Supported package-format matrix

| Item | Actual support |
|---|---|
| Archive | ZIP only; safe member paths, immutable original bytes and SHA-256 |
| Manifest | One JSON manifest at archive root; duplicate/nested/missing manifests fail |
| Identity/version | safe identifiers for `package_id`, `package_version`, `enterprise_id`, `profile_version`; registry identity must equal manifest |
| Payload | Declared NDJSON `record_sets`; CIOS Commercial Twin OOXML workbook where adapter contract matches |
| Checksums | Whole archive always; workbook/member hashes where declared by adapter contract |
| Compatibility | Exact current mapping version controls cached staging and stale review; no broad manifest upgrade adapter |
| Dependencies | `missing:` references are quarantined by existing validation; new scope helper closes explicit payload references and reports unresolved ones |

## Supported asset matrix

| Asset | Classification and evidence |
|---|---|
| Enterprise/twin/source | Partially implemented: recognised candidates; promotion constructor coverage is not general Twin promotion |
| Evidence, Observation | Fully implemented for validation, review, promotion and lineage |
| Entity, relationship, Unknown, Contradiction, human knowledge | Promoted by existing generic/contradiction repositories with package lineage |
| Industry, Market Participant, Opportunity, Control Body Twins | Partially implemented through a generic `twin` candidate declaration; dedicated canonical constructors and complete product views are missing |
| Pressures, responses, burning platforms, solution patterns, executive publications | Projection-only; retained outside canonical intelligence |
| Facts/figures, risks, transformations, recommendations, AI outputs | Package-dependent payload semantics; no general canonical importer class, so support is partial or unclear |
| Completeness/maturity/freshness/confidence | Package validation counts existed; governed Twin-type maturity was missing. This increment supplies deterministic read assessment, not canonical persistence |

Unknowns and Contradictions are first-class supported candidate classes. Promotion lineage records package/version/checksum, run, candidate, review, mapping, plan, approval, source location/fingerprint and actors. Updates retain the prior canonical version inside lineage; re-execution is deterministic and returns no change.

## Banking ingestion-path analysis

Banking is a combination rather than a proof of generic package ingestion. `banking_portfolio.py` owns substantial in-code Banking presentation data, while Enterprise Intelligence reads its established runtime/knowledge sources. The global portfolio was a static Banking-plus-placeholder presentation. No evidence demonstrates that those Banking cards were produced by the blueprint importer. This increment leaves Banking routes and state untouched; future shared portfolio wiring should adapt Banking as a read projection rather than migrate it.

## Maturity analysis and rules

Existing scoring modules concern other product scores and package staging counts, not a uniform Twin-type governed maturity result. The new profiles are weighted by material dimensions for Industry, Enterprise, Market Participant, Opportunity and Control Body Twins. Missing dimensions score zero rather than being inferred. Unknowns, Contradictions and stale evidence apply bounded penalties. Missing critical opportunity buyer, pressure, outcome, addressability or evidence lineage caps maturity at 49. Output separates package completeness, Twin maturity and decision completeness and exposes dimensions, weights, caps, penalties, gaps and next evidence. It is deliberately read-time and deterministic; historical assessment persistence and freshness-threshold scheduling remain gaps.

## Capability classification (1–32)

1–4 **reusable**; 5 **partial, extended by detection**; 6 **implemented in guided UI**; 7 **reusable**; 8–9 **partial (dependency-safe selection primitive, full UI/persistence not wired)**; 10 **reusable**; 11–15 **missing dedicated canonical promotion**; 16–20 **reusable**; 21–24 **partial/missing generic overview**; 25–26 **partial and payload-specific**; 27–29 **partially implemented by the new read assessment**; 30–31 **partially implemented by read-projection primitives, not full routes**; 32 **projection/import logic is industry-neutral, but canonical constructor gaps remain**.

## Smallest increment, impact and acceptance evidence

Changed runtime code adds: (a) six expected-type choices saved beside import-run metadata; (b) independent candidate detection and hard mismatch gates on review and approval; (c) transitive selection/dependency inspection; (d) five materiality-weighted maturity profiles; and (e) non-persistent industry/opportunity projections with safe-unavailable output and inspectable ranking. Tests prove mixed detection, mismatch, dependency closure, unresolved evidence, maturity determinism/caps/penalties, safe unavailable values, deterministic ranking and addition of an arbitrary second industry without industry-specific code.

No schema migration occurs. Guidance adds one JSON document per run below existing blueprint-import runtime data. IAM is unchanged and existing inspection/review/promotion checks remain authoritative. Operationally, file-backed durability and multi-process coordination retain their existing constraints. Banking behaviour is unchanged.

## Known gaps, contradictions and future-package conditions

* The stated baseline is correct about the lifecycle, but broader product claims exceed constructor reality. Do not advertise full Industry/Participant/Opportunity/Control Body promotion until accepted canonical owners expose constructors.
* Selective scope has a tested dependency closure primitive but needs an authorised persisted scope form integrated before review-plan creation.
* Generic Twin overview and portfolio/opportunity HTTP routes remain to be wired after canonical Twin reads exist; persisting projections would be an architectural error.
* Maturity recalculation events and immutable assessment history need an accepted owner before implementation.
* Market Participant evidence is insufficient for supplier-relative fit or win probability; those claims remain prohibited.
* Future Central Government and Utilities packages must use the root manifest/ZIP contract, stable safe IDs, supported schema/profile and mapping version, declared/checksummed payloads, explicit Twin types and references, atomic evidence-backed observations, retained Unknowns/Contradictions, and no unresolved critical opportunity buyer/evidence dependencies.
