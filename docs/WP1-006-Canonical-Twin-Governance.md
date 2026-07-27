# WP1-006 — Canonical Twin Identity and Cross-Twin Governance

## Architecture and runtime capability assessment

The accepted baseline separates package exchange from canonical acceptance (ADR-012 and ADR-016), makes the Enterprise Model durable enterprise memory (ADR-002 and EI-001), and requires inspectable lineage. IT-001 owns Industry Twin semantics: an Industry Twin synthesises enterprise intelligence while each Enterprise Twin remains the canonical semantic owner of enterprise-specific state. Package containment may be an embedded release, immutable snapshot, decision-scoped materialised projection or declared dependency; none transfers semantic ownership.

Before this increment Flora had one governed importer with archive inspection, contract adapters, candidate staging, reconciliation planning, approval, atomic canonical promotion, audit lineage, Unknown and Contradiction handling, repeat-import protection and rollback. It had no common runtime Twin-identity projection, stable-ID cross-package dependency discovery, cross-Twin impact record or downstream reconciliation work record. The executive category defect was a **derived-view defect**: the view searched technical class names, source paths and display-like text. The governed TMS object inventory already declares `object_type` values for enterprises, market participants and capability/offers; its separate governed collections declare opportunities.

## Taxonomy and canonical owners

| Twin type | Baseline status | Primary subject and owner | Import behaviour / relationship |
|---|---|---|---|
| Industry Twin | Defined by IT-001; implemented package route | An explicitly identified industry scope; the Industry Twin owns industry synthesis | Governed Industry package adapter; contained enterprise material remains an owned release, snapshot, projection or dependency |
| Enterprise Twin | Defined by EI-001; implemented by the Blueprint route | One monitored enterprise; its Enterprise Twin owns enterprise-specific durable state | Existing Blueprint inspection, staging, review and promotion |
| Market Participant Twin | Defined by the accepted Market Participant Twin Specification and EI-001 extension; candidate collection support exists | One market actor; its Market Participant Twin owns participant state | May be imported only through an explicit governed contract; account-relative claims remain governed interpretations |
| Opportunity Twin | Defined by OT-001 and existing candidate support | One governed opportunity | Existing candidate/package support; not an Enterprise identity |
| Supplier Twin | **Not independently defined** | Not applicable | Must not be invented. Supplier is a commercial role of an Enterprise or Market Participant |

Supplier, buyer, regulator, operator, intermediary, partner and competitor are commercial roles, not independent Twin types. Package role and projection role are also independent of canonical identity type.

## Package identity projection contract

`TwinIdentityProjection` exposes Twin ID/type, primary-subject ID/name/class, governed scope, canonical owner, version, research state, decision maturity and source-package identity. Recognition requires explicit governed metadata. An incomplete projection is `ambiguous`; it does not use filenames, names, collection size or containment to fill gaps, and disables dependency propagation. TMS-001's single governed industry release document explicitly supplies `IND-TMS-001`, its name and scope; IT-001 makes that Industry Twin the owner of industry synthesis.

## Dependency, impact and reconciliation model

Dependency discovery searches only previously promoted package candidates and matches the incoming primary-subject stable ID in governed identity/relationship fields. It never compares names. Each result retains dependent Twin identity, reason, affected object, candidate/package lineage, confidence and review requirement. The impact projection counts changed governed classes, Unknowns and Contradictions and classifies a confirmed match as `reconciliation required`; ambiguous identity is unsupported rather than speculative.

After successful source promotion, the existing lifecycle creates an idempotent pending downstream reconciliation record containing source/version, dependent Twin, projections, proposed counts, evidence/lineage, uncertainty, supersession pointer, approval state and audit history. It records `dependent_twin_mutated: false`; it performs no dependent canonical write.

## Remaining gaps and unsupported cases

* There is no independently governed Supplier Twin contract; the smallest canonical-source change would be an accepted specification and package contract, not a runtime label rule.
* A Market Participant Twin is architecturally defined, but a dedicated top-level package contract is not implemented by this increment. Explicit Blueprint metadata can project it; ambiguous packages remain under review.
* Dependency discovery covers stable IDs present in Flora's promoted import lineage. External Twins without imported governed identifiers require a future canonical registry/index.
* Impact counts are deliberately conservative class-level proposals. Semantic field diffs and stale-projection resolution remain work for explicit downstream review.
* Downstream approval and mutation continue through governed reconciliation; this increment records pending work and does not implement automatic synchronisation.

## Acceptance answer

**Will any dependent Twin be changed automatically?** No. Dependent Twins change only through explicit governed reconciliation and approval.

## Recommendation

**Merge.** This is the smallest evidence-based runtime increment: it reuses the importer, staging, promotion and lifecycle boundaries; adds explicit identity and affected-Twin projections; creates pending reconciliation work; and never transfers ownership or mutates dependent Twins.
