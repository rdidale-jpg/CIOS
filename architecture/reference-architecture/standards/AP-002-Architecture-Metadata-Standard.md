# AP-002 — Architecture Metadata Standard

**Identifier:** AP-002
**Version:** 1.0
**Document Type:** Architecture Process Standard
**Authority Classification:** Canonical architecture standard
**Document class:** Architecture process standard
**Status:** Accepted
**Owner:** Rob / CIOS
**Last updated:** 2026-07-11
**Production behaviour:** Documentation-only governance standard; does not change runtime behaviour, export code, production pack membership or canonical Twin state.

## Purpose

AP-002 defines the canonical metadata semantics that CIOS architecture documents use to declare identity, authority, ownership, dependency, profile-membership and lifecycle information in a machine-readable way.

The standard is intentionally implementation-neutral. YAML front matter is an acceptable initial representation, but AP-002 governs the meaning of metadata fields, not a particular syntax, parser, storage format or runtime implementation.

## Scope

AP-002 applies to canonical architecture documents governed by the [CIOS Architecture Authority Registry](../Architecture-Authority-Registry.md), including architecture process standards, ADRs, reference-architecture papers, founding papers, Enterprise Intelligence papers, specifications and review materials.

Out of scope:

- changing production Researcher or Reviewer pack contents;
- changing Flora, Newton, Observatory, Publisher or Commercial Digital Twin runtime behaviour;
- mutating canonical Enterprise Model, Observation, Evidence or Twin state;
- replacing the Authority Registry as the control plane for authority and profile membership;
- requiring a specific metadata serialisation format.

## Foundation rule

The Authority Registry remains the control plane for architecture authority and release-profile membership.

Document metadata must be backward compatible with the existing Authority Registry columns and meanings. A compiler may read metadata from documents, the registry or both, but if document metadata conflicts with the Authority Registry, the registry wins until amended by an accepted governance change.

## Canonical metadata object

Each canonical document may declare one metadata object with these top-level semantic groups:

| Group | Required for canonical documents | Purpose |
| --- | --- | --- |
| `identity` | Yes | Stable document identity and locator. |
| `type` | Yes | Document class and architecture family. |
| `status` | Yes | Governance status using the Authority Registry status taxonomy. |
| `authority` | Yes | Authority classification and authoritative scope. |
| `owner` | Yes | Accountable owner and review responsibility. |
| `dependencies` | Yes | Upstream authority, related documents and validation dependencies. |
| `profiles` | Yes | Explicit release-profile membership. |
| `lifecycle` | Yes | Creation, review, supersession and promotion state. |

A document may include additional implementation-specific fields, but additional fields must not redefine these semantics.

## Field semantics

### `identity`

`identity` identifies the canonical document independently of file location.

| Field | Semantics |
| --- | --- |
| `id` | Stable governed identifier, such as `AP-002`, `ADR-010`, `EI-012` or `FP-010`. |
| `title` | Human-readable title used in registries and compilations. |
| `canonical_path` | Repository-relative canonical path to the document. |
| `version` | Document version or version-like label when applicable. |
| `aliases` | Optional previous IDs, short names or migration aliases. |

### `type`

`type` classifies the document without determining authority.

| Field | Semantics |
| --- | --- |
| `document_class` | Controlled class such as architecture process standard, ADR, founding paper, Enterprise Intelligence paper, specification, review material or implementation note. |
| `architecture_domain` | Broad domain such as reference architecture, enterprise intelligence, founding papers, knowledge packs, runtime architecture or review. |
| `canonical_document` | Boolean marker that the document participates in canonical architecture governance. |

### `status`

`status` declares the document governance state using the Authority Registry status taxonomy.

Permitted values are `Accepted`, `Draft`, `Proposed`, `Review`, `Superseded` and `Rejected`. These values are backward compatible with the current Authority Registry status taxonomy.

### `authority`

`authority` explains how the document may be used as architecture authority.

| Field | Semantics |
| --- | --- |
| `classification` | Authority classification compatible with the Authority Registry `Authority classification` column. |
| `scope` | Bounded subject matter over which the document is authoritative or proposed to be authoritative. |
| `normative` | Boolean indicating whether the document contains normative governance or architecture requirements inside its accepted scope. |
| `registry_entry_required` | Boolean indicating whether a registry row is required before production-profile compilation. |
| `conflict_rule` | Required statement that the Authority Registry wins over conflicting local metadata. |

### `owner`

`owner` records accountability rather than authorship alone.

| Field | Semantics |
| --- | --- |
| `name` | Accountable owner or owning group. |
| `role` | Owner role, such as Chief Architect, CIOS Architecture, document steward or review owner. |
| `reviewers` | Optional people or groups expected to review changes. |

### `dependencies`

`dependencies` makes upstream and validation dependencies available without prose interpretation.

| Field | Semantics |
| --- | --- |
| `requires` | Documents that must be considered upstream authority for this document. |
| `related` | Non-blocking related documents. |
| `supersedes` | Earlier documents or versions replaced by this document. |
| `superseded_by` | Later authority that replaced this document, when applicable. |
| `validation_triggers` | Registry-compatible validation triggers needed before promotion or release. |

### `profiles`

`profiles` is the machine-readable declaration of release-profile membership. It is sufficient for a compiler to determine candidate profile membership without reading document prose.

| Field | Semantics |
| --- | --- |
| `membership` | List of profile identifiers from the Authority Registry release-profile taxonomy. |
| `exclusions` | Profiles from which the document is explicitly excluded. |
| `eligible_when` | Optional machine-readable promotion condition; absence means current membership is authoritative subject to registry confirmation. |

Permitted profile identifiers are `architecture-authority`, `researcher-pack`, `reviewer-pack`, `review-context` and `none`. `review-context` is a metadata/compiler profile from AP-001; production release-profile membership remains limited to the Authority Registry taxonomy unless the registry is updated. `none` means no production release-profile membership and must not be combined with production profiles.

A compiler can determine profile membership by reading `profiles.membership` and `profiles.exclusions`, then applying AP-001 and the Authority Registry conflict rule. The compiler must not infer production membership from document prose, folder location, title or status alone.

### `lifecycle`

`lifecycle` records governance movement over time.

| Field | Semantics |
| --- | --- |
| `created` | Date or known creation marker. |
| `last_updated` | Latest material update date. |
| `review_due` | Optional review date or cadence. |
| `promotion_state` | Current promotion state, such as not applicable, candidate, under review, accepted, blocked, superseded or rejected. |
| `change_control` | Governance mechanism required to change authority, status or profile membership. |

## Initial representation guidance

YAML front matter is the preferred initial representation because it is readable and easy to compile, but equivalent JSON, TOML, sidecar registry data or database records are valid if they preserve AP-002 semantics.

Example representation:

```yaml
architecture_metadata:
  identity:
    id: AP-002
    title: Architecture Metadata Standard
    canonical_path: architecture/reference-architecture/standards/AP-002-Architecture-Metadata-Standard.md
    version: "1.0"
  type:
    document_class: Architecture process standard
    architecture_domain: reference architecture
    canonical_document: true
  status: Accepted
  authority:
    classification: Architecture process standard governing canonical document metadata; documentation-only and non-runtime
    scope: Canonical architecture document metadata semantics
    normative: true
    registry_entry_required: true
    conflict_rule: Authority Registry wins over conflicting document metadata
  owner:
    name: Rob / CIOS
    role: Chief Architect
  dependencies:
    requires:
      - Architecture Authority Registry
      - AP-001
    related:
      - Document Map
    supersedes: []
    superseded_by: []
    validation_triggers:
      - Registry-backed metadata compatibility check before compiler enforcement
  profiles:
    membership:
      - architecture-authority
    exclusions: []
  lifecycle:
    created: 2026-07-11
    last_updated: 2026-07-11
    review_due: null
    promotion_state: accepted
    change_control: Accepted governance change recorded in the Authority Registry
```

## Backward compatibility with the Authority Registry

AP-002 deliberately mirrors existing Authority Registry concepts:

- `identity.id`, `identity.title` and `identity.canonical_path` map to the registry `ID`, `Title` and `Path` columns.
- `status` maps to the registry `Status` column and uses the same status taxonomy.
- `authority.classification` maps to `Authority classification`.
- `profiles.membership` maps to `Release-profile membership`.
- `dependencies.requires` and `dependencies.validation_triggers` map to `Dependencies` and `Validation trigger`.
- `owner` and `lifecycle` extend governance accountability without changing existing registry rows.

Therefore an existing registry row remains valid even before a document carries embedded metadata. AP-002 enables gradual adoption and compiler support without invalidating current registry practice.

## Production behaviour guardrail

Implementing AP-002 is documentation-only unless a separate accepted implementation task explicitly authorises compiler, export or runtime changes. This standard does not require code changes, workflow changes, new export profiles or changes to `FLORA_ARCHITECTURE_DOWNLOAD_MANIFEST.json`.
