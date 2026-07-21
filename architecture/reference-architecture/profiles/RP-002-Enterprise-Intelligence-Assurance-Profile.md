# RP-002 — Enterprise Intelligence Assurance Profile

**Identifier:** RP-002
**Version:** 1.0
**Document Type:** Architecture Role Profile
**Authority Classification:** Canonical architecture profile
**Document class:** Architecture role profile
**Status:** Accepted
**Owner:** Rob / CIOS
**Last updated:** 2026-07-13
**Production behaviour:** Documentation-only role profile; does not change runtime behaviour, existing architecture, document authority, export code or canonical Twin state.

## Purpose

RP-002 defines the official CIOS Enterprise Intelligence Assurance role so that the Architecture Profile Compiler can generate a complete, registry-traceable `assurance-pack` profile.

The Assurance role exists to inspect Enterprise Intelligence outputs, lineage and governed package boundaries before those outputs are relied on by downstream users, runtimes or governance forums. The role evaluates whether candidate intelligence is proportionate to evidence, consistent with accepted architecture and clear about uncertainty without making canonical promotion decisions by itself.

## Scope

RP-002 governs Assurance profile composition, Assurance responsibilities and acceptance criteria for compiled Enterprise Intelligence Assurance profiles.

It does not:

- change Flora, Newton, Observatory, Publisher or Commercial Digital Twin runtime behaviour;
- modify existing architecture authority or promote documents by prose;
- add unregistered documents to production packs;
- override AP-001, AP-002, RP-001 or the Architecture Authority Registry;
- change the authority status of review, proposed, draft, superseded or rejected material;
- approve canonical Twin promotion, architecture acceptance or release decisions without the relevant accepted governance process.

## Role responsibilities

The Enterprise Intelligence Assurance role is responsible for:

1. checking that Enterprise Intelligence outputs preserve source identity, evidence lineage and acquisition context;
2. verifying that observations, hypotheses, recommendations, Knowledge Packs and presentation views remain separated from canonical Twin acceptance;
3. testing candidate outputs against accepted Enterprise Model, Observation, Knowledge Graph, behaviour and hypothesis-governance boundaries;
4. identifying unsupported claims, missing citations, over-strong recommendations, hidden assumptions and unresolved contradictions;
5. confirming that human-supplied knowledge is labelled and dated before it affects assurance judgement;
6. reporting gaps, risks, validation triggers and governance questions without silently resolving them by assumption;
7. using only registry-approved architecture material when operating from a production Assurance profile;
8. respecting document authority boundaries recorded in the Architecture Authority Registry.

The Enterprise Intelligence Assurance role must not:

- approve architecture;
- promote review or proposed material into production use;
- change canonical Twin state without the relevant accepted process;
- infer pack membership from folder location, file name, topic relevance or prose;
- treat Knowledge Packs, Presentation Models, research packages or assurance findings as canonical Twin state unless separately accepted by the owning governance process;
- use documents with `none` profile membership as production Assurance-pack authority.

## Assurance profile membership

The official Enterprise Intelligence Assurance profile is the compiled `assurance-pack` profile defined by AP-001 and controlled by the Architecture Authority Registry.

The Assurance profile includes only accepted, authoritative registry rows whose release-profile membership explicitly contains `assurance-pack`.

At acceptance of RP-002, the approved Assurance-pack members are:

| ID | Document | Reason for inclusion |
| --- | --- | --- |
| AP-001 | Architecture Compilation Standard | Defines registry-backed profile compilation, inclusion/exclusion rules and non-promotion safeguards. |
| AP-002 | Architecture Metadata Standard | Defines metadata semantics needed for compiler-readable profile membership and authority traceability. |
| RP-002 | Enterprise Intelligence Assurance Profile | Defines the official Assurance role, allowed profile contents and acceptance criteria. |
| DD-001 | CIOS Design Doctrine | Establishes evidence-first, observation-led and model-centred assurance expectations. |
| RA-001 | CIOS Reference Architecture v1.0 | Provides the accepted authority-chain entry point for assurance review. |
| EI-001 | Enterprise Model Specification | Defines the durable Enterprise Model and canonical Twin memory boundary being assured. |
| EI-012 | Enterprise Observation Model | Defines Observation lifecycle and evidence lineage rules used in assurance checks. |
| EI-002 | Enterprise Knowledge Graph | Defines relationship provenance and graph-governance checks. |
| EI-003 | Enterprise Behaviour Model | Defines bounded behavioural interpretation for assurance of inferred enterprise behaviour. |
| FP-009 | Hypothesis Validation Standard | Defines hypothesis strengthening, weakening, rejection and retirement checks. |
| GL-001 | CIOS Reference Architecture Glossary | Provides canonical vocabulary for assurance findings. |
| ADR-001; ADR-002; ADR-003; ADR-004; ADR-005; ADR-009; ADR-010; ADR-011; ADR-012; ADR-013; ADR-014; ADR-016 | Relevant accepted ADRs | Provide accepted decisions governing observations, durable memory, CIRM/EI separation, human knowledge labels, lineage, progressive assurance, acquisition, financial intelligence, blueprint import, canvas navigation, evidence-governed reasoning and Knowledge Pack exchange. |

## Documents never included

The compiled Assurance profile must never include:

- unregistered architecture documents;
- documents whose registry release-profile membership is `none`;
- documents that lack explicit `assurance-pack` membership;
- documents with `Draft`, `Proposed`, `Review`, `Superseded` or `Rejected` status;
- documents whose authority classification states that they are not authoritative;
- documents explicitly excluded from `assurance-pack` by the Architecture Authority Registry;
- bounded `review-context` material unless and until a separate accepted registry update grants explicit `assurance-pack` membership.

The current EU-001 and ADR-023 review-material rows remain excluded from the Assurance profile because the registry marks them as `none` and excluded from production profiles.

## Dependencies

The Assurance profile depends on:

- AP-001 for compilation rules, production-profile inclusion rules and non-promotion semantics;
- AP-002 for document metadata semantics and registry-compatible profile membership;
- RP-001 for the upstream Researcher boundary whose outputs Assurance may inspect without converting research into approval;
- the Architecture Authority Registry as the control plane for authority, status, dependencies, validation triggers and release-profile membership;
- the Document Map as navigational context, without allowing the map to override the registry.

## Acceptance criteria for a compiled Assurance profile

A compiled Assurance profile is acceptable only when:

1. the compiler is invoked for `assurance-pack`;
2. the included document list is non-empty;
3. every included document is traceable to an Architecture Authority Registry row;
4. every included document has `Accepted` status;
5. every included document is authoritative within its registry classification;
6. every included document has explicit `assurance-pack` release-profile membership;
7. no `none`, `Draft`, `Proposed`, `Review`, `Superseded` or `Rejected` row is included;
8. AP-001, AP-002 and RP-002 are present in the compiled profile;
9. dependencies and validation triggers in the compilation record come from included registry rows;
10. the compilation record states that compilation does not promote document status;
11. the runtime upload package preserves source paths, document status and verbatim ADR traceability.
