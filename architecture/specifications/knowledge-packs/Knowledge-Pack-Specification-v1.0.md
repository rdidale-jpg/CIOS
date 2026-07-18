# Knowledge Pack Specification v1.0

**Status:** Draft Normative Specification
**Date:** 2026-07-18
**Owner:** Rob / CIOS
**Owning paper:** [FP-010 — Knowledge Pack Architecture](../../founding-papers/FP-010-Knowledge-Pack-Architecture.md) and [FP-011 — Knowledge Exchange Architecture](../../founding-papers/FP-011-Knowledge-Exchange-Architecture.md)
**Semantic owner:** [EI-013 — Knowledge Asset Exchange Model](../../enterprise-intelligence/EI-013-Knowledge-Asset-Exchange-Model.md)
**Owning ADR:** [ADR-016 — Knowledge Packs as the Standard Exchange Mechanism](../../decisions/ADR-016-Knowledge-Packs-as-Standard-Exchange-Mechanism.md)
**Reference architecture:** [CIOS Reference Architecture v1.0](../../reference-architecture/CIOS-Reference-Architecture-v1.0.md)
**Related protocol:** [Enterprise Knowledge Production Protocol v1.0](../enterprise-knowledge/Enterprise-Knowledge-Production-Protocol-v1.0.md)

## 1. Purpose

A Knowledge Pack is a governed, portable collection of Enterprise Knowledge assets assembled for a declared purpose. Knowledge Packs exist to move, review, compare, brief, render or exchange governed knowledge without changing the authoritative memory of CIOS.

Knowledge Packs are transport. They are not memory.

The Enterprise Knowledge Repository remains the system of record. A Knowledge Pack is a reproducible release generated from governed knowledge held in the repository or in other accepted canonical architecture stores. A pack may make knowledge easier to consume, inspect or deliver, but it must never become the master copy of that knowledge.

Knowledge Packs support situations where selected governed knowledge must be assembled for a specific audience, question, engagement, review or workflow. Enterprise Knowledge production before pack release is governed by the [Enterprise Knowledge Production Protocol v1.0](../enterprise-knowledge/Enterprise-Knowledge-Production-Protocol-v1.0.md). Examples include a researcher context pack, a cross-industry comparison pack, an executive briefing pack, a client opportunity pack, a review-board evidence pack or a Presentation Intelligence input pack.

### 1.1 Relationship to other knowledge forms

| Knowledge form | Role | Authoritative status | Primary use |
| --- | --- | --- | --- |
| Enterprise Knowledge Repository | Governed system of record for Enterprise Knowledge assets, lineage, metadata and accepted model state. | Authoritative within its governed scope. | Durable memory, reuse, assurance, lineage and release generation. |
| Knowledge Pack | Governed, portable, reproducible release of selected Knowledge Assets and metadata. | Not authoritative; valid as a release container only. | Transport, exchange, review, briefing, rendering, comparison and workflow input. |
| Report | Narrative or analytical view created for a moment, audience or decision. | Not authoritative unless separately governed as an asset. | Communication, explanation and decision support. |
| Presentation | Audience-specific rendering of selected knowledge and interpretation. | Not authoritative unless separately accepted by the owning model process. | Executive communication, board review, client engagement and storytelling. |
| Research | Discovery activity, evidence gathering, analysis or draft interpretation. | Candidate until governed and accepted. | Learning, enrichment and hypothesis development. |

A Knowledge Pack may contain reports, presentations, research outputs or presentation payloads when those assets are governed and in scope. Carrying such material does not make the carried material canonical fact.

## 2. Principles

Knowledge Packs must follow these architectural principles:

1. **Portable** — a pack can be moved between consumers, environments, review processes or future workflows without depending on a single runtime implementation.
2. **Immutable** — a released pack is not edited in place. Corrections or changes require a new version or replacement release.
3. **Reproducible** — a pack can be regenerated from the same governed source selection, version constraints and inclusion rules.
4. **Governed** — only governed assets are eligible for inclusion. Candidate material must be clearly labelled and must not be presented as accepted knowledge.
5. **Versioned** — the pack, manifest, included assets and validation outcome must identify their relevant versions.
6. **Manifest-driven** — every pack is described by a manifest that declares identity, purpose, scope, contents, exclusions, lineage and validation state.
7. **Traceable** — every included asset preserves lineage to its originating repository asset, source evidence, observation, model object or accepted governing document.
8. **Technology-neutral** — the specification defines architecture and governance semantics, not a programming language, automation platform or storage technology.
9. **Domain-neutral** — a pack can represent any domain, including banking, insurance, utilities, telecommunications, cross-industry analysis, client opportunity work or executive briefing.
10. **Non-authoritative** — pack acceptance means the package is valid for handling, not that its contents become canonical memory.

## 3. Consumers

Knowledge Packs are designed for governed consumption by humans, AI-assisted workflows and future CIOS services. Intended consumers include:

- **Researcher GPT** — receives scoped, lineage-preserving context for a specific research task without treating the pack as durable memory.
- **Chief Architect** — reviews architecture evidence, relationships, decisions, principles and proposed changes using a bounded, reproducible release.
- **Review Boards** — inspect the assets, lineage, Unknowns, Contradictions, recommendations and validation state relevant to a decision or assurance checkpoint.
- **Client Engagement** — receives client-specific or opportunity-specific knowledge assembled for preparation, pursuit, validation or briefing.
- **Presentation Intelligence** — renders governed knowledge into audience-specific narrative, visual, executive or board-facing views while preserving source lineage.
- **Future Flora workflows** — may validate, compare, render, route, archive, sign or regenerate packs as part of the target Knowledge Exchange Architecture.
- **Architecture and governance functions** — evaluate whether assets are complete, consistent, traceable and aligned with reference architecture.

Consumers must treat a pack as a release of selected knowledge, not as a replacement for the repository or as proof that every included claim is canonical fact.

## 4. Pack Structure

A Knowledge Pack has a logical structure. This specification does not mandate a physical packaging technology, file system layout, archive format or runtime storage mechanism.

A typical pack may use the following logical structure:

```text
README.md
MANIFEST.yaml
industry/
enterprise/
infrastructure/
comparison/
mechanism/
observation/
governance/
```

The logical areas are optional and should be selected according to pack purpose:

- **README.md** — human-readable purpose, scope, intended consumers, handling notes and summary of contents.
- **MANIFEST.yaml** — canonical pack declaration, identity, contents, exclusions, lineage and validation state.
- **industry/** — industry-level assets, sector context, change summaries or industry twin extracts.
- **enterprise/** — enterprise-level assets, enterprise model extracts, executive context, operating model, technology, financial or relationship assets.
- **infrastructure/** — reusable infrastructure, architecture, capability, data, platform or mechanism knowledge relevant to the pack purpose.
- **comparison/** — cross-entity, cross-industry, account-participant, option, pattern or benchmark comparison assets.
- **mechanism/** — explanatory mechanisms, reasoning chains, reusable models, operating patterns or architectural mechanisms.
- **observation/** — selected observations, observation summaries, evidence-backed change records, Unknowns and Contradictions.
- **governance/** — validation outputs, release notes, lineage summaries, rights or handling constraints and review records.

The structure must remain domain neutral. A banking pack may contain banking material; the Knowledge Pack architecture must not require banking-specific paths, terminology or assumptions.

## 5. Manifest

Every Knowledge Pack must include a manifest named `MANIFEST.yaml` unless a future governing standard explicitly defines an equivalent manifest form. The manifest is the primary declaration of pack identity, purpose, scope, contents, exclusions, lineage and validation status.

The manifest must include at least:

```yaml
pack_id: "knowledge-pack.example.v1"
version: "1.0.0"
creation_date: "YYYY-MM-DD"
source_repository: "Enterprise Knowledge Repository identifier or governed source reference"
knowledge_domains:
  - "domain-neutral-name"
included_assets:
  - asset_id: "asset.identifier"
    asset_type: "observation | knowledge_asset | presentation_model | report | governance_record | other"
    version: "asset-version"
    source_path_or_reference: "repository-relative-path-or-stable-reference"
    lineage_reference: "lineage-identifier"
excluded_assets:
  - asset_id: "asset.identifier-or-pattern"
    reason: "out of scope | superseded | restricted | candidate | duplicate | other"
validation_status: "draft | passed | passed_with_warnings | failed | not_validated"
owner: "named accountable owner or owning function"
```

The manifest should also declare, where relevant:

- pack title and description;
- intended consumers;
- declared purpose;
- scope boundaries;
- source selection criteria;
- repository snapshot or release basis;
- handling constraints;
- rights or usage constraints;
- dependency packs;
- related Knowledge Packs;
- release state;
- validation date;
- validator identity or governance function;
- checksum, signature or integrity reference where available;
- Unknowns and Contradictions included or intentionally excluded;
- recommendation lineage where recommendations are included.

Manifest validity means the pack can be understood, inspected and governed. It does not mean the contained knowledge has become authoritative.

## 6. Asset Selection

Knowledge Packs include only governed assets. A governed asset is an asset with an identifiable owner, type, version or date, lineage, source reference and acceptance or governance status appropriate to the pack purpose.

Selection rules:

1. The pack must declare its purpose and selection criteria.
2. Included assets must be relevant to the declared purpose.
3. Included assets must preserve their originating identifiers and lineage.
4. Candidate, draft, inferred or human-supplied assets may be included only when clearly labelled according to their governance status.
5. Assets known to be superseded, restricted, duplicate, contradicted or out of scope should be excluded or explicitly explained.
6. Partial packs are permitted when the manifest declares scope boundaries and exclusions.
7. Recommendations may be included only with inspectable rationale and lineage.
8. Unknowns and Contradictions must remain visible when they materially qualify included claims.

Supported pack scopes include:

- single-industry packs;
- multiple-industry packs;
- cross-industry packs;
- single-enterprise packs;
- multiple-enterprise packs;
- client opportunity packs;
- research packs;
- presentation packs;
- executive briefing packs;
- review-board packs;
- architecture assurance packs;
- future Flora workflow packs.

## 7. Metadata

Knowledge Pack governance requires three distinct metadata layers.

### 7.1 Pack metadata

Pack metadata describes the release container. Required pack metadata includes:

- pack identifier;
- pack title;
- version;
- creation date;
- owner;
- purpose;
- intended consumers;
- scope;
- source repository or governed source reference;
- knowledge domains;
- release state;
- validation status;
- handling constraints where applicable;
- manifest version or schema reference where applicable.

### 7.2 Asset metadata

Asset metadata describes each included Knowledge Asset. Required asset metadata includes:

- asset identifier;
- asset type;
- asset title or subject;
- asset version or date;
- provenance;
- authoring mode where relevant;
- confidence where applicable;
- temporal scope where applicable;
- lineage reference;
- governance status;
- human-supplied label where applicable;
- fact, interpretation, hypothesis, recommendation, Unknown or Contradiction classification where applicable.

### 7.3 Repository metadata

Repository metadata describes the authoritative source context from which the pack was generated. Repository metadata should include:

- repository identifier;
- repository snapshot, release, baseline or selection basis;
- source path or stable reference for each asset;
- repository owner or governing function;
- canonical status of the source asset;
- source model, graph, observation, evidence or decision relationship where applicable.

Pack metadata governs the container. Asset metadata governs the included assets. Repository metadata preserves the link back to the system of record.

## 8. Validation

A Knowledge Pack must be validated before release. Validation is an architectural governance activity and does not prescribe a specific tool, script, workflow or automation platform.

Validation must check:

- **Manifest completeness** — required manifest fields are present and understandable.
- **Duplicate detection** — duplicate assets, identifiers or conflicting copies are detected and resolved or explained.
- **Asset existence** — every included asset exists in the declared source repository or governed source reference.
- **Version consistency** — pack version, asset versions and manifest version are internally consistent.
- **Identifier consistency** — pack identifiers, asset identifiers and lineage identifiers are stable and non-conflicting.
- **Link integrity** — referenced assets, lineage records, evidence, observations and governance documents resolve or are explicitly marked unavailable.
- **Metadata completeness** — required pack, asset and repository metadata is present.
- **Lineage completeness** — included claims and assets preserve source lineage sufficient for inspection.
- **Scope conformance** — included and excluded assets match the declared purpose and selection rules.
- **Canonical-boundary protection** — validation confirms that release handling does not promote pack contents into authoritative memory.
- **Unknown and Contradiction visibility** — material Unknowns and Contradictions are included or their exclusion is justified.

Validation outcomes are:

- **not_validated** — validation has not yet been performed.
- **failed** — one or more release-blocking checks failed.
- **passed_with_warnings** — validation passed with non-blocking issues or declared limitations.
- **passed** — required checks passed.

A failed pack must not be released. A pack with warnings may be released only when the owner accepts the warnings and records them in the manifest or validation record.

## 9. Lineage

Knowledge Packs preserve lineage. They do not create authority.

Lineage remains attached to originating assets in the Enterprise Knowledge Repository or other governed source. A pack must carry enough lineage to let a consumer inspect where an asset came from, what evidence or observation supports it, what version was selected, what governance state applied at release time and what Unknowns or Contradictions qualify it.

Lineage may reference:

- source documents;
- evidence records;
- observations;
- Enterprise Knowledge Graph entities and relationships;
- Enterprise, Industry, Market Participant, Opportunity or Relational Twin state;
- architecture decisions;
- founding papers;
- reference architecture documents;
- human-supplied contributions;
- recommendations and rationale chains.

If a pack is copied, rendered, imported, archived or used by a consumer, lineage must remain inspectable. If an asset is later corrected or superseded in the repository, the released pack remains an immutable historical release and a new pack version should be generated when updated transport is required.

## 10. Release

Knowledge Packs follow a governed release lifecycle:

1. **Draft** — pack purpose, scope and candidate asset selection are being assembled. It is not valid for release consumption.
2. **Validated** — required validation has passed or passed with accepted warnings. The pack is ready for owner approval or release handling.
3. **Released** — the pack is immutable, versioned, reproducible and approved for declared consumers and purpose.
4. **Deprecated** — the pack remains historically inspectable but should no longer be used for new decisions because it has been superseded, expired or materially qualified.
5. **Archived** — the pack is retained for audit, lineage, historical reconstruction or governance record, not active use.

Release records should identify release owner, release date, validation outcome, source selection basis, intended consumers, handling constraints and known limitations.

Released packs must not be edited in place. Material correction requires a new release, deprecation notice or replacement pack.

## 11. Repository Relationship

The repository is authoritative. The Knowledge Pack is generated.

Knowledge Packs should never become the master copy of Enterprise Knowledge. They are release containers assembled from governed assets held in the Enterprise Knowledge Repository or another accepted source of canonical architecture state.

A Knowledge Pack may be stored in a repository for retrieval, audit or distribution, but repository storage of the pack does not make the pack the source of truth for the assets it carries. The source asset remains authoritative in its owning repository, model, graph, observation store or governing architecture document.

Knowledge Pack acceptance means the package is valid for repository handling. It does not silently promote contained claims into Enterprise Models, Enterprise Knowledge Graph state, Observations, Commercial Digital Twins or reference architecture.

## 12. Future Evolution

Future Knowledge Pack capabilities may include:

- automatic pack generation from governed repository selections;
- pack signing and integrity verification;
- semantic packs generated from graph, relationship or model queries;
- relationship filtering across enterprises, industries, participants, opportunities and mechanisms;
- observation filtering by type, date, confidence, relevance, contradiction, absence or evidence family;
- industry filtering for single-sector, multi-sector and cross-sector releases;
- client opportunity filtering for pursuit, discovery and account-participant assessment;
- executive briefing and board-pack profiles;
- pack comparison and delta analysis;
- pack dependency management;
- pack expiry and freshness signalling;
- Flora integration for validation, rendering, comparison, routing, lineage inspection, archive and regeneration workflows.

Future evolution must preserve the core boundary: Knowledge Packs transport governed knowledge; they do not become authoritative memory.
