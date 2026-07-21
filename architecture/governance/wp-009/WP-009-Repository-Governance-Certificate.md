# WP-009 Repository Governance Certificate

**Work Package:** WP-009 — Architecture Governance Certification
**Status:** Completed with governance findings
**Document Type:** Architecture Governance Certificate
**Owner:** Chief Architect
**Date:** 2026-07-21
**Authority Classification:** Governance evidence; documentation-only; does not create, rename, merge or supersede architecture

## Executive Summary

The architecture repository was inspected for identifier integrity, authority integrity, metadata integrity, repository integrity, terminology integrity, reference integrity and release readiness. No architectural redesign was performed. No semantic ambiguity was resolved by assumption. No Document Map or Authority Registry corrections were applied because the outstanding non-report issues require approval or future architectural decision rather than deterministic automatic correction.

**Overall governance status:** Not Ready for Architecture Version 1.0.

Primary evidence:
- 519 governed candidate files were scanned across Markdown, JSON and YAML assets.
- 139 architecture-root or CIOS governance Markdown/metadata candidates were inspected.
- 8 duplicate canonical filename identifier groups were found and require approval or explicit historical classification.
- 217 Markdown governance candidates have missing AP-002-style metadata fields.
- 0 broken relative Markdown links were found by deterministic link scan.

## Repository Health

The repository is substantially documented and already contains a central Document Map and Authority Registry. Governance health is constrained by historical parallel locations, duplicate identifier-like filenames, incomplete metadata across candidate governed documents, and mixed canonical/review/report artefacts sharing identifier prefixes. These are governance issues, not architecture design defects.

## 1. Repository Governance Report

| Workstream | Result | Classification |
| --- | --- | --- |
| Canonical identifiers | Filename-level duplicate identifier groups detected; identifier references are widely reused in citations, so duplicate textual references are observation evidence rather than duplicate definitions. | Approval Required / Observation Only |
| Authority | Authority Registry exists and distinguishes accepted authority from review material; conflicts remain where duplicate identifiers exist in historical or alternate paths. | Approval Required |
| Metadata | Metadata is partially normalised in architecture-core documents but incomplete across many governed candidates and knowledge assets. | Required Before Release |
| Repository structure | ADRs appear in `architecture/decisions/`, `architecture/adr/` and `docs/adr/`; standards appear in architecture standards and docs standards locations. | Approval Required |
| Cross references | Deterministic relative Markdown link scan found no broken relative Markdown links. | Accepted Limitation: non-Markdown and external links not exhaustively dereferenced |
| Terminology | Glossary and doctrine exist; terminology consistency requires semantic review, especially across Review specifications. | Observation Only |
| Governance validation | AP-001/AP-002 profile model and registry-backed authority are present; packaging must continue to avoid creating authority. | Observation Only |
| Release readiness | Not Ready due to identifier, metadata and canonical-location approval items. | Blocker / Required Before Release |

## 2. Canonical Identifier Register

### Duplicate canonical filename identifier groups

| Identifier | Files | Classification | Release impact |
| --- | --- | --- | --- |
| ADR-003 | `architecture/decisions/ADR-003-CIRM-and-EI-Separation.md`<br>`architecture/decisions/ADR-003-uk-banking-theme-taxonomy.md` | Approval Required | Blocker until canonical ownership or historical/report classification is approved |
| ADR-004 | `architecture/decisions/ADR-004-Human-Supplied-Knowledge-Must-Be-Labelled.md`<br>`docs/adr/ADR-004-commercial-intelligence-recommendations-ranking-valuation.md` | Approval Required | Blocker until canonical ownership or historical/report classification is approved |
| ADR-015 | `architecture/decisions/ADR-015-Observation-Identity-and-Minimal-Model-Projection.md`<br>`architecture/adr/ADR-015-Runtime-Mission-Context.md` | Approval Required | Blocker until canonical ownership or historical/report classification is approved |
| AP-001 | `architecture/reference-architecture/standards/AP-001-Architecture-Compilation-Standard-v1.1.md`<br>`architecture/reference-architecture/standards/AP-001-Architecture-Compilation-Standard.md` | Approval Required | Blocker until canonical ownership or historical/report classification is approved |
| EIRP-001 | `architecture/specifications/flora/EIRP-001-Enterprise-Intelligence-Reasoning-Pipeline-Specification.md`<br>`architecture/specifications/flora/EIRP-001-Completion-Report.md` | Approval Required | Blocker until canonical ownership or historical/report classification is approved |
| EU-001 | `architecture/reviews/EU-001-Review-and-Acceptance-Checklist.md`<br>`architecture/enterprise-intelligence/contracts/EU-001-Enterprise-Understanding-Contract.md` | Approval Required | Blocker until canonical ownership or historical/report classification is approved |
| FEIR-001 | `architecture/specifications/flora/FEIR-001-Completion-Report.md`<br>`architecture/specifications/flora/FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md` | Approval Required | Blocker until canonical ownership or historical/report classification is approved |
| RP-001 | `architecture/programmes/researcher-profile/RP-001-Completion-Report.md`<br>`architecture/reference-architecture/profiles/RP-001-Enterprise-Blueprint-Researcher-Profile.md` | Approval Required | Blocker until canonical ownership or historical/report classification is approved |

### Status distribution in Markdown candidates

| Status value | Count |
| --- | ---: |
| Missing | 273 |
| Draft | 28 |
| Review | 21 |
| draft | 17 |
| Accepted | 17 |
| Proposed | 12 |
| Complete | 11 |
| Proposed operational artefact | 9 |
| Audit artefact | 6 |
| Draft Normative Specification | 5 |
| Proposed Foundation | 3 |
| Working Draft | 2 |
| Proposed implementation report for Increment 1. | 1 |
| Proposed traceability matrix. | 1 |
| Proposed Specification for Increment 1 | 1 |
| Living document | 1 |
| Accepted Architecture Baseline | 1 |
| Approved for Codex implementation | 1 |
| Engineering Baseline | 1 |
| Proposed review | 1 |
| Draft governing architecture | 1 |
| Canonical v1.0 model, with Unknowns and candidate mechanisms preserved. | 1 |
| Completed; candidate knowledge asset pending owner acceptance. | 1 |
| Produced / Candidate | 1 |
| First release candidate; owner acceptance required for canonical accepted state. | 1 |
| Candidate specification | 1 |
| Mission instructions only | 1 |
| Operational readiness artefact | 1 |
| Operational research guide | 1 |
| Operational checklist | 1 |
| Canonical pack instruction | 1 |
| Operational configuration guide | 1 |
| Living briefing | 1 |
| Living doctrine | 1 |
| Proposed implementation roadmap | 1 |
| Canonical Markdown guidance | 1 |
| Living handbook | 1 |
| Proposed / Accepted / Superseded / Deprecated | 1 |
| Living index | 1 |
| Active Reconciliation Note | 1 |
| Phase 1 Report | 1 |
| Phase 2 Complete; Phase 3 Runtime Contracting Identified | 1 |
| Completed | 1 |
| Governance audit | 1 |
| Accepted architecture index | 1 |
| Accepted specification index | 1 |
| Complete — reconciled 2026-07-18 | 1 |
| Approved cross-product working standard | 1 |
| Analysis complete | 1 |
| Approved design baseline for Flora Sprint 1 | 1 |
| Approved exchange profile for Flora Sprint 1 | 1 |
| Approved implementation baseline for Flora Sprint 1 | 1 |
| current sprint review | 1 |
| Read-only audit for Flora Sprint 1 PR0 | 1 |
| Audit complete | 1 |
| Draft Engineering Standard | 1 |
| Ready for Codex planning after architecture merge | 1 |

### Identifier observations

- Textual duplicate identifier references are expected in maps, registries and citations and were not treated as duplicate ownership by themselves.
- Filename-derived duplicate identifiers are treated as approval-required because choosing a canonical owner would change governance semantics.
- `FP-0XX` is intentionally unresolved-looking and remains approval-required before release if it is to become governed architecture.

## 3. Authority Validation Report

| Finding | Evidence | Classification |
| --- | --- | --- |
| Authority Registry is present and includes accepted, review and profile-membership concepts. | `architecture/reference-architecture/Architecture-Authority-Registry.md` | Observation Only |
| Document Map is present and points readers to owning documents. | `architecture/reference-architecture/Document-Map.md` | Observation Only |
| Review documents are generally labelled as non-authoritative in the registry, but duplicate identifier groups can still confuse tooling. | Duplicate groups listed above | Approval Required |
| Accepted ADRs are listed as constraints in authority/profile material. | Authority Registry ADR rows | Observation Only |

## 4. Metadata Consistency Report

217 Markdown governance candidates are missing at least one of: Identifier/Title, Status, Version, Owner, Date, Document Type or Authority Classification. Metadata was not automatically filled because ownership, status, date and authority classification are governance assertions.

Top metadata gaps:

| File | Missing fields | Classification |
| --- | --- | --- |
| `CIOS-AI.md` | Version, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `architecture/Flora-Workspace-Architecture-Reconciliation-Report.md` | Owner, Version, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `architecture/FP-0XX-Flora-Enterprise-Intelligence-Workspace-Product-Architecture.md` | Version, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `architecture/UX-001-Flora-UK-Banking-Lloyds-Reference-Journey.md` | Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `architecture/README.md` | Version, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/ARCHITECTURE.md` | Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/REGISTER.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/README.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/insurance/README.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/telecommunications/README.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/utilities/README.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/README.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/infrastructure/UK-Banking-Payments-Infrastructure-Twin.md` | Title, Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/infrastructure/README.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/comparisons/Four-Bank-Mechanism-Differential-Matrix.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/comparisons/Banking-Mechanism-Differential-Matrix.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/comparisons/README.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/industry/Banking-Industry-Twin.md` | Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/industry/Banking-Mechanisms-and-Tensions-Model.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/industry/Banking-Industry-Foundation.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/industry/README.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/enterprises/README.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/governance-reports/Banking-Reinvention-Hypotheses-Governance-Report.md` | Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/governance-reports/Banking-Strategic-Sales-Navigation-Validation-Report.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/governance-reports/Filename-Mapping-Report.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/governance-reports/Banking-Strategic-Sales-Navigation-Completion-Report.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/governance-reports/File-Conversion-Report.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/governance-reports/Validation-Report.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/governance-reports/README.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/reinvention/Hypothesis-Statistics.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/reinvention/Completion-Report.md` | Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/reinvention/Delivery-Manifest.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/reinvention/Architectural-Observations.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/reinvention/Banking-Reinvention-Hypotheses-v0.1.md` | Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/reinvention/Validation-Report.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/reinvention/README.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/provider-offer-twin/Provider-Offer-Twin-Implementation-Report.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/research-migration/Banking-Research-Package-Migration-Report.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/flora/Banking-Strategic-Sales-Navigation-Specification.md` | Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |
| `enterprise-knowledge/banking/flora/Banking-Knowledge-Register.md` | Status, Owner, Version, Date, Document Type, Authority Classification | Approval Required unless field value is explicitly derivable from an owning registry row |

## 5. Repository Structure Report

| Area | Observed locations | Certification result |
| --- | --- | --- |
| ADRs | `architecture/decisions/`, `architecture/adr/`, `docs/adr/` | Canonical ADR location requires Chief Architect approval; do not restructure automatically. |
| Standards | `architecture/reference-architecture/standards/`, `docs/CBOK/Standards/`, `docs/Engineering/` | Architecture standards location appears canonical for architecture authority; broader standards locations require explicit scope boundaries. |
| Specifications | `architecture/specifications/`, `docs/Architecture/`, `enterprise-knowledge/` | Architecture specifications appear canonical under `architecture/specifications/`; runtime/product specs in docs need scope classification. |
| Knowledge Packs | `knowledge-packs/`, `enterprise-knowledge/` | Packaging and source-map assets are present; they must package authority rather than create it. |

## 6. Cross Reference Report

| Check | Result | Classification |
| --- | --- | --- |
| Relative Markdown links | 0 broken relative Markdown links detected | Automatic scan passed |
| External links | Not dereferenced during this repository-local certification | Accepted Limitation |
| JSON/YAML internal references | Inspected as files for identifier occurrence; schema-level semantic resolution deferred | Deferred Enhancement |

## 7. Orphan Document Report

Potential orphan status cannot be certified solely by text search because reports, fixtures and knowledge assets may be valid historical evidence without inbound links. Filename identifiers with no cross-file reference should be reviewed before release but were not automatically removed or relabelled.

## 8. Terminology Consistency Report

| Term area | Observation | Classification |
| --- | --- | --- |
| Enterprise Intelligence / Enterprise Knowledge / Knowledge Packs | Boundaries are repeatedly documented, but packaging versus authority must remain explicit in profiles and manifests. | Observation Only |
| Flora Workspace / Runtime / Product Architecture | Multiple proposed/review artefacts exist; semantic promotion requires explicit approval. | Approval Required for status changes |
| Observation / Evidence / Enterprise Model | Accepted ADR and EI documents appear to protect these semantics. | Observation Only |

## 9. Governance Validation Report

- Authority Registry is the intended authority driver; no correction was made to it in WP-009.
- Knowledge Packs contain manifests and source maps; no Knowledge Pack content was changed.
- AP-001/AP-002 tests exist under `tests/architecture/` and should remain release gates.
- GitHub workflow inspection is recorded as deferred because no workflow files were present in the scanned file list at the repository root depth; absence should be confirmed before release.

## 10. Architecture Release Readiness Report

| Integrity domain | Readiness | Outstanding issue classification |
| --- | --- | --- |
| Identifier integrity | Not Ready | Blocker: duplicate filename identifier groups require approval |
| Authority integrity | Not Ready | Required Before Release: canonical owner/path decisions required for duplicate groups |
| Metadata integrity | Not Ready | Required Before Release: incomplete metadata across governed candidates |
| Repository integrity | Not Ready | Required Before Release: canonical ADR/standards/specification locations require approval |
| Terminology integrity | Ready with limitations | Accepted Limitation / Observation Only pending semantic governance review |
| Reference integrity | Ready with limitations | Accepted Limitation: relative Markdown links pass; external/schema references deferred |

**Release decision:** Not Ready.

## Mandatory Change Register

| Change ID | Classification | Description | Reason | Evidence | Before | After | Impact Assessment | Approval Required | Approval Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WP009-CHG-001 | Automatic | Added WP-009 governance certificate and reports. | Required deliverable; documentation-only certification record. | Repository audit outputs and this file. | No WP-009 certification artefact. | `architecture/governance/wp-009/WP-009-Repository-Governance-Certificate.md` exists. | Preserves architecture; records findings without implementing semantic decisions. | No | Completed |

## Mandatory Decision Register

| Decision ID | Issue | Repository Evidence | Possible Options | Consequences | Recommended Option | Approval Required |
| --- | --- | --- | --- | --- | --- | --- |
| WP009-DEC-001 | Duplicate canonical filename identifiers. | Duplicate table in Canonical Identifier Register. | (A) Approve one canonical owner and reclassify others as reports/historical; (B) assign new identifiers; (C) preserve duplicates with explicit exception. | A preserves IDs but needs metadata; B changes identifiers; C weakens deterministic tooling. | A, where evidence shows one document is a completion/report artefact; otherwise none. | Chief Architect |
| WP009-DEC-002 | Canonical ADR location. | ADR files appear under `architecture/decisions/`, `architecture/adr/`, and `docs/adr/`. | (A) standardise on `architecture/decisions/`; (B) keep split with explicit scopes; (C) migrate legacy docs. | A improves determinism; B preserves history; C requires redirects/maps. | A for architecture ADRs if approved. | Chief Architect |
| WP009-DEC-003 | Metadata completion for governed candidates. | Metadata gaps table. | (A) registry-derived batch normalisation; (B) owner-by-owner review; (C) narrow governed scope. | A is efficient but requires trusted registry completeness; B is slower; C limits certification scope. | None without scope approval. | Chief Architect |
| WP009-DEC-004 | Architecture v1.0 release readiness. | Readiness table. | (A) block v1.0 until issues resolved; (B) release with accepted limitations; (C) narrow v1.0 scope. | A maximises governance trust; B requires explicit risk acceptance; C requires scope definition. | A based on current blocker findings. | Chief Architect |

## Governance Issues Found

### Blockers
- Duplicate canonical filename identifier groups require approved ownership/classification.
- Canonical ADR, standards and specification locations require approved scope rules before deterministic release tooling can rely on paths.

### Required Before Release
- Complete or explicitly scope metadata requirements for governed documents.
- Decide treatment for historical reports whose filenames start with governed identifiers.

### Accepted Limitations
- Repository-local Markdown relative links were checked; external hyperlinks were not dereferenced.
- JSON/YAML semantic references were inventoried but not semantically interpreted.

### Deferred Enhancements
- Generate a machine-readable identifier registry from the Authority Registry after approval decisions.
- Add a CI test for duplicate filename identifier ownership exceptions.

## Governance Issues Corrected

- WP009-CHG-001 added this governance certification artefact. No architecture semantics, registry ownership, Document Map entries, Knowledge Pack content or runtime behaviour were changed.

## Governance Issues Requiring Approval

- WP009-DEC-001 through WP009-DEC-004 require Chief Architect approval before implementation.

## Governance Observations

- The current repository contains extensive review and completion evidence that should be preserved, not removed.
- Several duplicate identifier findings likely represent reports or legacy locations rather than true competing architecture, but that classification is itself a governance decision.
- The Authority Registry and Document Map are already the right control points for deterministic compilation once duplicate/path/metadata decisions are resolved.

## Repository Governance Certificate

WP-009 certifies that the repository has been inspected and that all discovered governance issues in this certificate are classified. The repository is **not certified as ready for Architecture Version 1.0** until blocker and required-before-release items are resolved or formally accepted by the Chief Architect. This certificate does not create new architecture, rename concepts, merge concepts, alter Accepted ADR intent, modify Enterprise Intelligence semantics, change runtime behaviour, or change Knowledge Pack content.
