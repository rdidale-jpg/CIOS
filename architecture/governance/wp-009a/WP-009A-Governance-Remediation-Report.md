# WP-009A Governance Remediation Report

**Identifier:** WP-009A
**Title:** Architecture Governance Remediation
**Status:** Accepted
**Version:** 1.0
**Owner:** Chief Architect
**Date:** 2026-07-21
**Document Type:** Governance Remediation Report
**Authority Classification:** Release governance evidence; not a canonical architecture authority document

## Executive summary

WP-009A implements the approved governance decisions from WP-009 without changing architecture semantics or runtime behaviour. The canonical ADR location is now `architecture/decisions/`; duplicate identifier groups have one governed owner or an explicitly non-authoritative artefact; governed architecture scope is defined in a testable YAML rule; and governance validation tests cover identifier uniqueness, metadata, ADR location and registry/map path validity.

## Duplicate Identifier Resolution Matrix

| Identifier | Canonical document | Canonical location | Authority evidence | Other artefact | Other artefact classification | Action taken | References updated | Semantic change |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ADR-003 | CIRM and EI Separation | `architecture/decisions/ADR-003-CIRM-and-EI-Separation.md` | Accepted ADR registry row | UK Banking theme taxonomy decision | Product/implementation decision | Renamed to `architecture/decisions/UK-Banking-Theme-Taxonomy-Decision.md`; added non-canonical classification | WP-008 references | None |
| ADR-004 | Human-Supplied Knowledge Must Be Labelled | `architecture/decisions/ADR-004-Human-Supplied-Knowledge-Must-Be-Labelled.md` | Accepted ADR registry row | Commercial intelligence recommendations/ranking/valuation decision | Product decision outside architecture authority | Renamed to `docs/adr/commercial-intelligence-recommendations-ranking-valuation-decision.md`; added non-canonical classification | Path references | None |
| ADR-015 | Runtime Mission Context Architecture | `architecture/decisions/ADR-015-Runtime-Mission-Context.md` | Accepted status and ADR index/Document Map usage | Observation Identity and Minimal Model Projection draft | Historical proposed ADR draft | Moved accepted ADR into canonical decisions folder; renamed draft to descriptive historical filename and removed canonical identifier claim | ADR index, Document Map, Glossary, WP-008 references | None |
| AP-001 | Architecture Compilation Standard | `architecture/reference-architecture/standards/AP-001-Architecture-Compilation-Standard.md` | Authority Registry accepted AP-001 row | AP-001 v1.1 copy | Historical copy | Renamed to `architecture/reference-architecture/standards/AP-001-Architecture-Compilation-Standard-v1.1-Historical-Copy.md`; added non-canonical classification | WP-008 references | None |
| EIRP-001 | Enterprise Intelligence Reasoning Pipeline Specification | `architecture/specifications/flora/EIRP-001-Enterprise-Intelligence-Reasoning-Pipeline-Specification.md` | Specification metadata and Document Map runtime section | EIRP completion report | Completion report | Renamed to `architecture/specifications/flora/Enterprise-Intelligence-Reasoning-Pipeline-Completion-Report.md`; added related-document metadata | Flora spec README and self-reference | None |
| EU-001 | Enterprise Understanding Contract | `architecture/enterprise-intelligence/contracts/EU-001-Enterprise-Understanding-Contract.md` | Contract metadata and review status | EU-001 review checklist | Review checklist | Retained path; added non-canonical classification and related-document metadata | Test path retained | None |
| FEIR-001 | Flora Enterprise Intelligence Runtime Architecture v1.0 | `architecture/specifications/flora/FEIR-001-Flora-Enterprise-Intelligence-Runtime-Architecture-v1.0.md` | Specification metadata and Document Map runtime section | FEIR completion report | Completion report | Renamed to `architecture/specifications/flora/Flora-Enterprise-Intelligence-Runtime-Architecture-Completion-Report.md`; added related-document metadata | Flora spec README and self-reference | None |
| RP-001 | Enterprise Blueprint Researcher Profile | `architecture/reference-architecture/profiles/RP-001-Enterprise-Blueprint-Researcher-Profile.md` | Authority Registry accepted RP-001 row | RP-001 completion report | Completion report | Renamed to `architecture/programmes/researcher-profile/Enterprise-Blueprint-Researcher-Profile-Completion-Report.md`; added related-document metadata | Path references | None |

## ADR Classification and Location Register

Canonical architecture ADRs are governed through `architecture/decisions/`. The former `architecture/adr/ADR-015-Runtime-Mission-Context.md` was migrated to `architecture/decisions/ADR-015-Runtime-Mission-Context.md`. The historical observation identity draft and product decisions are retained with explicit classification and no canonical architecture identifier claim.

## Governed Architecture Scope Definition

The governed architecture set is defined in `architecture/governance/governed-architecture-scope.yaml`. It uses explicit paths, recognised document types and registered authority; it does not classify all Markdown files as governed architecture.

## Governed Metadata Compliance Report

- Total governed architecture documents: 32.
- Compliant governed documents after remediation: 32.
- Non-compliant governed documents after remediation: 0.
- Excluded evidence and operational artefacts: completion reports, implementation reports, audit reports, review checklists, fixtures, test assets, programme notes, operational guides, enterprise knowledge content, generated manifests/source maps and historical evidence unless explicitly registered.
- Exclusion rationale: these artefacts preserve traceability but do not own architecture authority.

## Authority Registry and Document Map alignment

The Authority Registry remains the source of release-profile and authority control for accepted architecture authority. The Document Map now points ADR-015 to `architecture/decisions/` and reports the canonical folder accurately.

## Release readiness reassessment

| Issue | Classification | Result |
| --- | --- | --- |
| Duplicate canonical identifiers | Blocker before WP-009A | Resolved |
| Canonical ADR scope/location | Blocker before WP-009A | Resolved |
| Governed metadata standard | Required before release | Resolved for explicit WP-009A governed scope |
| Authority Registry path validity | Required before release | Passing |
| Document Map path validity | Required before release | Passing |
| Semantic unknowns unrelated to governance | Accepted Limitation | Retained where already labelled |
| Broader metadata expansion outside approved scope | Deferred Enhancement | Not part of v1.0 blocker set |

Architecture v1.0 governance is ready when the WP-009A validation tests pass.

## Change Register

| Change ID | File | Change type | Before | After | Evidence | Governance rationale | Semantic impact | Validation result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WP009A-CHG-001 | `architecture/governance/governed-architecture-scope.yaml` | Add | No testable scope rule | Explicit governed scope and metadata/status rules | WP-009 Decision 3 | Prevent Markdown-wide governance inference | None | Covered by tests |
| WP009A-CHG-002 | `architecture/decisions/ADR-015-Runtime-Mission-Context.md` | Move/metadata | Canonical ADR outside decisions folder | Canonical ADR in decisions folder with AP-style metadata | Accepted status and index evidence | Enforce canonical ADR location | None | Covered by tests |
| WP009A-CHG-003 | Duplicate non-canonical artefacts | Rename/reclassify | Reports/drafts shared canonical IDs | Descriptive filenames or classification metadata | Report/checklist titles and existing canonical owners | Unique canonical identifiers | None | Covered by tests |
| WP009A-CHG-004 | `architecture/reference-architecture/Document-Map.md` | Update | ADR-015 path/folder referenced `architecture/adr/` | ADR-015 path/folder references `architecture/decisions/` | Canonical ADR decision | Registry/map path consistency | None | Covered by tests |
| WP009A-CHG-005 | `tests/architecture/test_wp009a_governance.py` | Add | No WP-009A gate | Automated governance checks | WP-009A Workstream 6 | Release gate automation | None | Passing |

## Completion Report

Resolved duplicate identifiers: ADR-003, ADR-004, ADR-015, AP-001, EIRP-001, EU-001, FEIR-001 and RP-001. No duplicate group was returned for approval because repository evidence established canonical ownership in each case. Governed architecture documents are the explicit paths listed in the scope YAML. Governed metadata compliance is 32/32. ADR location compliance is achieved for canonical architecture ADRs. Authority Registry and Document Map paths resolve under the governance test. Remaining blockers: none after tests pass. Architecture v1.0 readiness: ready from a WP-009A governance perspective.
