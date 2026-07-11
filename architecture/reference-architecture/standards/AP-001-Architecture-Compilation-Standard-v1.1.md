# AP-001 — Architecture Compilation Standard

**Document class:** Architecture process standard  
**Status:** Accepted  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-11  
**Production behaviour:** Documentation-only governance standard; does not change runtime behaviour, export code, production pack membership or canonical Twin state.

## Purpose

AP-001 defines how CIOS compiles architecture material into named, reviewable architecture sets without allowing draft, proposed or review material to be mistaken for accepted authority.

The standard uses the [CIOS Architecture Authority Registry](../Architecture-Authority-Registry.md) as the foundation for compilation decisions. A compilation must therefore start from registered document authority, status, release-profile membership and validation triggers rather than from folder scans, filename conventions or convenience manifests.

## Architectural Intent

CIOS distinguishes between **canonical architecture** and **deployable runtime artefacts**.

AP-001 defines the governance rules that allow canonical architecture to be compiled into role-specific architecture packages while preserving **authority**, **provenance** and **architectural integrity**.

The standard ensures that compilation is **deterministic**, **inspectable** and **repeatable** without changing the authority or lifecycle of the source architecture.

## Scope

AP-001 applies to architecture documentation compilation, release preparation, reviewer packs, researcher packs and architecture-authority bundles. It does not alter Flora, Newton, Observatory, Publisher or Commercial Digital Twin runtime behaviour.

Out of scope:

- changing production Researcher or Reviewer pack contents;
- promoting proposed or review material to accepted architecture;
- mutating canonical Enterprise Model, Observation, Evidence or Twin state;
- changing the Flora architecture export implementation or default export profile.

## Foundation rule

The Authority Registry is the control plane for architecture compilation.

Compilation lifecycle:

```text
Authority Registry
        │
        ▼
Profile Selection
        │
        ▼
Dependency Resolution
        │
        ▼
Compilation
        │
        ▼
Validation
        │
        ▼
Compiled Profile
```

A compilation process must use the registry to determine:

1. whether a document is accepted, draft, proposed, review, superseded or rejected;
2. whether the document belongs to `architecture-authority`, `researcher-pack`, `reviewer-pack` or `none`;
3. whether dependencies and validation triggers are known before release;
4. whether a document must be excluded from production-facing packs.

If a manifest, checklist or manual file list conflicts with the Authority Registry, the registry wins until the registry itself is amended by an accepted governance change.

## Compilation profiles

| Profile | Purpose | Inclusion rule | Exclusion rule |
| --- | --- | --- | --- |
| `architecture-authority` | Accepted architecture authority set. | Include only documents with registry membership in `architecture-authority` or an explicit owner-designated authoritative classification. | Exclude proposed, review, rejected and unregistered material unless the registry marks it authoritative. |
| `researcher-pack` | Material approved for production research-agent use. | Include only documents with registry membership in `researcher-pack`. | Exclude all `none` profile material and all material marked not accepted or not authoritative. |
| `reviewer-pack` | Material approved for production reviewer use. | Include only documents with registry membership in `reviewer-pack`. | Exclude all `none` profile material and all material marked not accepted or not authoritative. |
| `review-context` | Bounded context for architecture review. | May include proposed or review material if every such document is clearly labelled with its registry status. | Must not be represented as production authority or production agent pack material. |

## Required compilation metadata

Every architecture compilation record or release note must identify:

- compilation profile;
- source registry path and registry last-updated date;
- included document IDs and paths;
- excluded proposed or review documents relevant to the topic;
- dependencies used to justify inclusion;
- validation triggers still outstanding;
- statement that compilation does not promote document status;
- architecture version;
- registry version;
- compiler version (when implemented);
- compilation timestamp.

## Non-promotion rule

Compilation is packaging, not acceptance. Adding a document to a review-context compilation does not make it accepted, authoritative or production-pack eligible.

A proposed or review document may only move into an authority or production profile after the Authority Registry records the accepted decision, approved status and explicit profile membership.

## Extensibility

Future compiler implementations may optimise compilation through document merging, digest generation, runtime-specific packaging or other implementation techniques.

Such optimisation must never alter document authority, lifecycle status, dependency relationships or canonical architectural meaning.

## Production behaviour guardrail

Implementing AP-001 must be documentation-only unless a separate accepted implementation task explicitly authorises runtime changes. This standard does not require code changes, workflow changes, new export profiles or changes to `FLORA_ARCHITECTURE_DOWNLOAD_MANIFEST.json`.

## Relationship to Other Standards

AP-001 governs **architecture compilation**.

It does not define metadata formats, compiler implementation or runtime behaviour.

Those responsibilities are intended to be defined by subsequent Architecture Standards.

This separation preserves a stable architectural principle while allowing implementation to evolve independently.

## Initial application

The current review material entries for EU-001 and ADR-023 remain excluded from `architecture-authority`, `researcher-pack` and `reviewer-pack`. They may be used only in bounded review-context compilations that preserve their registry status and validation trigger.
