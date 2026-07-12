# RP-001 — Enterprise Blueprint Researcher Profile

**Document class:** Architecture role profile  
**Status:** Accepted  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-11  
**Production behaviour:** Documentation-only role profile; does not change runtime behaviour, existing architecture, document authority, export code or canonical Twin state.

## Purpose

RP-001 defines the official CIOS Researcher role for Enterprise Blueprint work so that the Architecture Profile Compiler can generate a complete, registry-traceable `researcher-pack` profile.

The Researcher exists to acquire, inspect and organise enterprise evidence under accepted architecture controls. The role supports Enterprise Blueprint preparation by using only architecture material explicitly approved for research-agent use in the Architecture Authority Registry.

## Scope

RP-001 governs Researcher profile composition, Researcher responsibilities and acceptance criteria for compiled Researcher profiles.

It does not:

- change Flora, Newton, Observatory, Publisher or Commercial Digital Twin runtime behaviour;
- modify existing architecture authority or promote documents by prose;
- add unregistered documents to production packs;
- override AP-001, AP-002 or the Architecture Authority Registry;
- change the authority status of review, proposed, draft, superseded or rejected material.

## Role responsibilities

The Researcher is responsible for:

1. collecting enterprise evidence from governed sources;
2. preserving provenance, source identity and acquisition context;
3. separating candidate evidence from accepted architecture and accepted Twin state;
4. preparing observations and research findings for downstream review without making approval decisions;
5. using only registry-approved architecture material when operating from a production Researcher profile;
6. reporting gaps, contradictions and validation needs rather than resolving them by assumption;
7. respecting document authority boundaries recorded in the Architecture Authority Registry.

The Researcher must not:

- approve architecture;
- promote review or proposed material into production use;
- change canonical Twin state without the relevant accepted process;
- infer pack membership from folder location, file name, topic relevance or prose;
- use documents with `none` profile membership as production Researcher-pack authority.

## Researcher profile membership

The official Researcher profile is the compiled `researcher-pack` profile defined by AP-001 and controlled by the Architecture Authority Registry.

The Researcher profile includes only accepted, authoritative registry rows whose release-profile membership explicitly contains `researcher-pack`.

At acceptance of RP-001, the approved Researcher-pack members are:

| ID | Document | Reason for inclusion |
| --- | --- | --- |
| AP-001 | Architecture Compilation Standard | Defines registry-backed profile compilation, inclusion/exclusion rules and non-promotion safeguards. |
| AP-002 | Architecture Metadata Standard | Defines metadata semantics needed for compiler-readable profile membership and authority traceability. |
| RP-001 | Enterprise Blueprint Researcher Profile | Defines the official Researcher role, allowed profile contents and acceptance criteria. |

## Documents never included

The compiled Researcher profile must never include:

- unregistered architecture documents;
- documents whose registry release-profile membership is `none`;
- documents that lack explicit `researcher-pack` membership;
- documents with `Draft`, `Proposed`, `Review`, `Superseded` or `Rejected` status;
- documents whose authority classification states that they are not authoritative;
- documents explicitly excluded from `researcher-pack` by the Architecture Authority Registry;
- bounded `review-context` material unless and until a separate accepted registry update grants explicit `researcher-pack` membership.

The current EU-001 and ADR-023 review-material rows remain excluded from the Researcher profile because the registry marks them as `none` and excluded from production profiles.

## Dependencies

The Researcher profile depends on:

- AP-001 for compilation rules, production-profile inclusion rules and non-promotion semantics;
- AP-002 for document metadata semantics and registry-compatible profile membership;
- the Architecture Authority Registry as the control plane for authority, status, dependencies, validation triggers and release-profile membership;
- the Document Map as navigational context, without allowing the map to override the registry.

## Acceptance criteria for a compiled Researcher profile

A compiled Researcher profile is acceptable only when:

1. the compiler is invoked for `researcher-pack`;
2. the included document list is non-empty;
3. every included document is traceable to an Architecture Authority Registry row;
4. every included document has `Accepted` status;
5. every included document is authoritative within its registry classification;
6. every included document has explicit `researcher-pack` release-profile membership;
7. no `none`, `Draft`, `Proposed`, `Review`, `Superseded` or `Rejected` row is included;
8. AP-001, AP-002 and RP-001 are present in the compiled profile;
9. dependencies and validation triggers in the compilation record come from included registry rows;
10. the compilation record states that compilation does not promote document status.
