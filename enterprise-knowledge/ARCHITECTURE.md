# Enterprise Knowledge Repository Architecture

**Status:** Draft governing architecture  
**Owner:** CIOS Architecture  
**Scope:** All Enterprise Knowledge domains  
**Architecture alignment:** CIOS Chief Architect Doctrine, CIOS Reference Architecture, Enterprise Intelligence, Observation Model, Enterprise Model Specification and Enterprise Knowledge Graph

## 1 Purpose

Enterprise Knowledge exists to provide the durable knowledge substrate for Enterprise Intelligence and Flora. It organises governed knowledge assets so CIOS can remember, compare, validate and evolve understanding across industries, enterprises, infrastructure, mechanisms, relationships and evidence lineage without becoming dependent on one report, one file, one research sprint or one implementation.

Enterprise Knowledge is not a document library. It is the governed architecture for how reusable knowledge is identified, related, validated, refreshed and superseded. It preserves the CIOS doctrine:

```text
Evidence proves change.
Observations remember change.
Enterprise Models accumulate change.
Reports are views.
```

Enterprise Knowledge distinguishes the following concepts:

- **Research** is inquiry. It collects sources, asks questions, explores unknowns and produces candidate findings. Research may be incomplete, contradictory or provisional.
- **Evidence** is proof that something was published, stated, filed, observed or supplied. Evidence is immutable once accepted and must retain provenance, date and confidence.
- **Knowledge** is governed, reusable understanding derived from evidence, observations, models, validated reasoning or accepted human expertise. Knowledge is durable, versioned and lineage-aware.
- **Models** are structured representations of accumulated understanding. Enterprise, Industry, Infrastructure, Reference and Mechanism models organise knowledge into reusable memory rather than narrative output.
- **Observations** are atomic, evidence-backed intelligence units that remember meaningful change, condition, relationship, absence, contradiction, trend or anomaly.
- **Reports** are generated views over governed knowledge, observations, models, relationships and reasoning. A report communicates intelligence for a purpose; it is not canonical memory.
- **Enterprise Intelligence** is the governed discipline that turns evidence-backed observations into durable models, graph relationships, hypotheses, recommendations, learning and action.

## 2 Architectural Principles

1. **Knowledge is durable.** Governed knowledge must remain reusable across reports, domains, releases, products and reasoning contexts.
2. **Evidence is immutable.** Accepted evidence records must not be rewritten to fit later interpretation. Later correction creates new evidence, new observations or supersession lineage.
3. **Observations are atomic.** Each observation records one meaningful fact, change, condition, absence, relationship or contradiction.
4. **Models accumulate understanding.** Models absorb accepted observations and governed knowledge over time; they are durable memory, not one-off analysis.
5. **Reports are generated views.** Reports, briefings, dashboards and presentations render selected knowledge for an audience and decision.
6. **Identifiers are permanent.** Governed asset identity must survive renames, moves, reclassification and presentation changes.
7. **Lineage is inspectable.** Every material claim, relationship, model attribute and recommendation should be traceable to evidence, observation, source, inference or labelled human contribution.
8. **Unknowns are preserved.** Missing knowledge is a first-class state that drives future research and validation.
9. **Contradictions are retained.** Conflicting evidence or interpretations must remain visible until resolved or explicitly accepted as unresolved.
10. **Governance before scale.** Repository growth must not outrun identifier control, metadata quality, relationship integrity, validation and stewardship.
11. **Truth status is explicit.** Fact, inference, hypothesis, recommendation, view, contradiction and unknown must not be collapsed into a single narrative.
12. **Domain neutrality is mandatory.** The architecture applies to Banking, Insurance, Energy, Telecommunications and future industries without modification.
13. **Exchange is not canonical promotion.** Moving or packaging knowledge does not silently promote it into an owning model.
14. **Human knowledge is labelled.** Human-supplied expertise may calibrate knowledge but must remain distinguishable from evidence-backed fact.

## 3 Repository Architecture

The Enterprise Knowledge repository is organised by architectural responsibility, not by implementation technology or reporting format.

```text
enterprise-knowledge/
  ARCHITECTURE.md
  README.md
  industry/
  enterprise/
  infrastructure/
  mechanism/
  comparison/
  observation/
  reference-models/
  flora/
  governance/
  manifests/
  registers/
  archive/
```

- **industry/** contains industry-level foundations and Industry Twins. It describes market structure, regulation, participant roles, sector pressures, operating patterns and common transformation dynamics.
- **enterprise/** contains Enterprise Twins and enterprise-specific governed knowledge assets where a monitored organisation is the subject.
- **infrastructure/** contains Infrastructure Twins that model platforms, ecosystems, networks, operational assets, shared capabilities or enabling infrastructure relevant across enterprises or industries.
- **mechanism/** contains mechanism catalogues that explain reusable causal, commercial, operating, regulatory, economic or transformation mechanisms.
- **comparison/** contains governed comparison matrices and cross-domain analysis assets.
- **observation/** contains observation registers or observation-oriented knowledge assets that preserve atomic change memory.
- **reference-models/** contains reusable conceptual, domain, capability, operating, economic and relationship models.
- **flora/** contains architecture-level integration knowledge describing how Flora consumes governed knowledge without binding the repository to runtime implementation.
- **governance/** contains governance reports, validation records, stewardship guidance and architecture assurance assets.
- **manifests/** contains manifests that declare governed asset collections, releases, dependencies and lineage boundaries.
- **registers/** contains knowledge registers and controlled catalogues of assets, identifiers, domains, statuses and relationships.
- **archive/** contains superseded or retired assets retained for lineage, audit and historical interpretation.

The hierarchy may be extended for new knowledge domains, but extensions must preserve the governing taxonomy, metadata, identifier, lifecycle, lineage and validation rules in this architecture.

## 4 Asset Taxonomy

The following are governed Enterprise Knowledge asset types.

| Asset type | Purpose |
| --- | --- |
| **Industry Foundation** | Establishes stable baseline knowledge for an industry: structure, roles, regulation, economics, value chains, common pressures, participants, operating patterns and terminology. |
| **Industry Twin** | A living industry model that accumulates industry observations, change, pressures, participant movement, reference mechanisms and cross-enterprise patterns. |
| **Enterprise Twin** | A durable model of a monitored enterprise, including identity, leadership, economics, operating model, technology, suppliers, transformation, risks, behaviours, opportunities, unknowns and contradictions. |
| **Infrastructure Twin** | A durable model of shared or critical infrastructure, such as networks, platforms, ecosystems, operational assets, market utilities or enabling capabilities. |
| **Mechanism Catalogue** | A governed catalogue of reusable mechanisms explaining how change happens, such as regulatory pressure, margin compression, platform migration, supplier lock-in, operating-model centralisation or AI adoption dynamics. |
| **Comparison Matrix** | A structured comparison of assets, enterprises, industries, mechanisms, participants, capabilities or models, preserving criteria, lineage, confidence and interpretation boundaries. |
| **Observation Register** | A governed register of atomic observations or observation collections, including dates, evidence lineage, confidence, status, affected models and contradiction state. |
| **Reference Model** | A reusable model that defines concepts, structures, relationships, capabilities, stages, patterns or taxonomies applicable across one or more domains. |
| **Knowledge Register** | A controlled register of governed knowledge assets, identifiers, ownership, status, version, domain, relationships, supersession and refresh state. |
| **Manifest** | A declaration of an asset collection, release, package, dependency boundary, lineage boundary or governed knowledge set. |
| **Governance Report** | A review, validation, assurance or stewardship record documenting quality, gaps, risks, conflicts, decisions or acceptance status. |
| **Architecture** | A constitutional or structural specification defining enduring principles, taxonomy, boundaries, semantics or governance for Enterprise Knowledge. |
| **README** | A navigational and orientation asset that explains scope, entry points and usage expectations for a repository area without becoming the governing architecture. |

## 5 Asset Lifecycle

Enterprise Knowledge assets move through a governed lifecycle:

```text
Research
  ↓
Draft
  ↓
Validated
  ↓
Governed
  ↓
Living Knowledge
  ↓
Superseded
  ↓
Archived
```

- **Research** explores sources, unknowns, candidate claims and early structure. It is not governed knowledge.
- **Draft** expresses candidate knowledge in the expected asset form but remains incomplete or unaccepted.
- **Validated** has passed required checks for metadata, lineage, consistency, relationship integrity and review scope.
- **Governed** has an accountable owner, stable identifier, declared status, known lineage and accepted governance state.
- **Living Knowledge** remains active, refreshable and capable of accumulating observations, relationships, versions or supersession history.
- **Superseded** has been replaced or materially displaced by another asset but remains retained for lineage.
- **Archived** is no longer active but is preserved for audit, historical interpretation, evidence lineage or architectural continuity.

Lifecycle state changes must be explicit. Assets must not silently move from research to governed status because they are useful, well-written or frequently referenced.

## 6 Asset Metadata

Every governed asset must carry mandatory metadata. This architecture defines semantics, not prescribed values.

- **asset_id** identifies the asset permanently and uniquely across the Enterprise Knowledge repository.
- **title** is the human-readable name of the asset.
- **asset_type** declares the governed taxonomy type of the asset.
- **domain** identifies the knowledge domain, industry, enterprise, infrastructure area or cross-domain scope to which the asset belongs.
- **status** declares lifecycle and governance state.
- **version** identifies the asset version or revision state.
- **owner** identifies the accountable steward, role or governance authority.
- **confidence** expresses assessed reliability or maturity of the asset's claims, given evidence quality, corroboration, freshness, contradiction and review depth.
- **evidence_cutoff** identifies the latest evidence date intentionally considered by the asset.
- **related_assets** lists assets with meaningful non-hierarchical association.
- **derived_from** identifies source assets, models, research or evidence collections from which this asset is derived.
- **depends_on** identifies assets required to interpret, validate or maintain this asset.
- **supersedes** identifies assets replaced or materially displaced by this asset.
- **refresh_trigger** describes conditions that should cause review, refresh or revalidation.

Metadata must distinguish identity from location, truth status from presentation quality, and confidence in evidence from confidence in interpretation.

## 7 Asset Identifiers

Asset identifiers are architectural identity, not storage paths.

Identifier rules:

1. Asset IDs are permanent.
2. Asset IDs are never derived from filenames.
3. Asset IDs are never reused.
4. Asset IDs remain stable through renames, moves, restructuring or presentation changes.
5. Asset IDs identify governed knowledge assets, not temporary research notes.
6. Superseded or archived assets retain their identifiers.
7. New versions must preserve continuity while making version state inspectable.
8. Cross-references must use identifiers where architectural identity matters.
9. Filename, title and location may change without changing asset identity.
10. Identifier assignment is a governance responsibility.

## 8 Relationships

Relationships describe semantic dependency, lineage, authority and use. They are not implementation instructions.

- **implements** means an asset realises, applies or instantiates a higher-level architecture, standard, model or pattern.
- **extends** means an asset adds domain-specific or specialised knowledge while preserving the authority of the extended asset.
- **derived_from** means an asset was produced from another asset, evidence set, model, observation collection or research base.
- **related_to** means two assets have meaningful association but neither dependency nor derivation is being asserted.
- **supports** means one asset provides evidence, rationale, structure or reasoning support for another asset, claim, model or recommendation.
- **depends_on** means an asset requires another asset for interpretation, validation, completeness or governed use.
- **supersedes** means an asset replaces or materially displaces another asset while preserving historical lineage.
- **contradicts** means an asset, observation or evidence item conflicts with another claim or interpretation and the contradiction remains unresolved or intentionally retained.
- **refines** means an asset improves precision, confidence, scope or structure without necessarily replacing the earlier asset.
- **references** means an asset cites or points to another asset without asserting dependency, support or derivation.

Relationship semantics must preserve direction. If one asset depends on another, the inverse relationship is not automatically true.

## 9 Evidence Lineage

Every material recommendation should be traceable through reasoning, model state, observations and evidence. The repository must preserve the distinction between evidence, observation, model, interpretation, hypothesis and recommendation.

Evidence lineage requirements:

- Evidence remains immutable once accepted.
- Evidence confidence belongs to evidence and must not be confused with model confidence or recommendation confidence.
- Observations must retain links to supporting and contradicting evidence.
- Models must expose the observations, evidence or governed knowledge that caused material state.
- Recommendations must expose supporting observations, hypotheses, models, unknowns and contradictions.
- Lineage must be inspectable by humans.
- Unknowns remain explicit even when a recommendation is still useful.
- Contradictions remain explicit even when an asset is accepted.
- Human-supplied knowledge must be labelled and traceable to contributor, date and scope where available.
- Evidence cutoff dates must be visible so users know what was and was not considered.

## 10 Governance

Enterprise Knowledge governance ensures that repository growth creates durable intelligence rather than unmanaged documents.

Governance responsibilities include:

- **Repository stewardship:** maintaining structure, taxonomy, identifiers, registers, manifests and archive integrity.
- **Review:** assessing architectural alignment, domain neutrality, terminology consistency, lineage and completeness.
- **Validation:** applying repository-level checks before promotion or release.
- **Change control:** ensuring meaningful changes are visible, reviewed and connected to supersession or version history.
- **Versioning:** preserving evolution without overwriting lineage or erasing prior knowledge states.
- **Quality:** managing confidence, evidence quality, duplicate detection, unknowns, contradictions and asset maturity.
- **Authority boundaries:** ensuring acceptance of a report, manifest or package does not silently promote claims into an owning model.
- **Conflict handling:** flagging conflicts with accepted ADRs or governing architecture rather than silently changing architectural decisions.

Governance is accountable for truth status and stewardship; it does not prescribe implementation technology, workflow tooling or storage mechanism.

## 11 Validation

Repository validation must confirm that Enterprise Knowledge assets are identifiable, complete, connected, lineage-aware and coherent.

Validation includes:

- **Metadata completeness:** mandatory fields are present and semantically meaningful.
- **Identifier uniqueness:** each governed asset has one permanent unique asset ID.
- **Relationship integrity:** referenced assets exist or are explicitly external, directional semantics are valid and required relationships are present.
- **Link integrity:** internal references, citations and navigational links are resolvable or intentionally marked unresolved.
- **Manifest consistency:** manifests accurately declare included assets, versions, dependencies, lineage and status.
- **Register consistency:** knowledge registers agree with asset metadata and lifecycle state.
- **Duplicate detection:** likely duplicate assets, observations or identifiers are flagged for review.
- **Orphan detection:** assets with no owner, domain, register entry, relationship or navigational path are flagged.
- **Lineage inspection:** material claims have evidence, observation, model, inference or human-source lineage.
- **Supersession consistency:** superseded assets point to replacing assets and remain accessible for history.
- **Architecture alignment:** terms and decisions remain consistent with the CIOS Design Doctrine, Reference Architecture, Enterprise Model Specification, Observation Model and Enterprise Knowledge Graph.

Validation reports should identify pass, warning, failure and unresolved conflict states without dictating implementation tooling.

## 12 Flora Integration

Flora consumes Enterprise Knowledge as governed knowledge, not as filenames or ad hoc document text. Flora reasons over:

- observations;
- models;
- relationships;
- knowledge assets;
- evidence lineage;
- unknowns;
- contradictions;
- confidence and freshness;
- governance status;
- supersession and version state.

Flora should use asset identifiers, metadata, relationships and lineage to understand authority, scope and truth status. Repository location may help navigation, but it must not be treated as semantic authority. Flora may render reports, compare twins, propose cross-twin impacts, identify refresh demand and support Enterprise Intelligence reasoning, but it must preserve the boundary between evidence, observation, model, interpretation, hypothesis and recommendation.

## 13 Enterprise Knowledge Evolution

New industries inherit this architecture. Banking is Reference Implementation #1, not a special case and not a constraint on future domains. Insurance, Energy, Telecommunications and future industries reuse the same governing architecture:

- same lifecycle;
- same identifier rules;
- same metadata semantics;
- same evidence lineage doctrine;
- same relationship semantics;
- same validation responsibilities;
- same distinction between research, evidence, observations, models, knowledge and reports.

Domain-specific extensions may add asset subtypes, specialised models or industry terminology, but they must not weaken the governing doctrine or make the repository dependent on one industry.

## 14 Architectural Decisions

1. **Enterprise Knowledge is the durable substrate for Enterprise Intelligence.**  
   Rationale: Intelligence value compounds only when knowledge can be remembered, refreshed, related and reused.

2. **Evidence, Observations, Models and Reports remain separate architectural responsibilities.**  
   Rationale: Collapsing proof, memory, accumulated state and presentation weakens traceability and reasoning quality.

3. **The repository is domain-neutral.**  
   Rationale: Banking may demonstrate the pattern, but CIOS requires cross-industry applicability.

4. **Governed asset identifiers are independent of filenames and paths.**  
   Rationale: Repository structure must evolve without breaking architectural identity or lineage.

5. **Unknowns and contradictions are governed knowledge states.**  
   Rationale: Preserving uncertainty improves collection, validation, reasoning and commercial judgement.

6. **Reports are not source of truth.**  
   Rationale: Reports are views over durable knowledge and model state; treating them as memory recreates report-centric failure modes.

7. **Flora consumes governed semantics, not storage layout.**  
   Rationale: Runtime reasoning must follow identifiers, metadata, relationships and lineage rather than filenames.

8. **Validation precedes promotion.**  
   Rationale: Scale without validation creates unmanaged narrative rather than Enterprise Knowledge.

9. **Supersession preserves history.**  
   Rationale: Knowledge evolves; prior states remain necessary for audit, learning and interpretation of past decisions.

10. **Conflicts with accepted ADRs must be flagged.**  
    Rationale: Architectural decisions should change only through explicit governance, not silent documentation drift.

## 15 Future Work

Future Enterprise Knowledge evolution is expected to include:

- a governed knowledge graph connecting assets, observations, models, entities, evidence and recommendations;
- a relationship graph for dependency, lineage, support, contradiction, supersession and cross-domain reasoning;
- semantic search over governed knowledge with status, confidence, evidence cutoff and lineage awareness;
- enterprise reasoning that can compare twins, detect change, preserve unknowns and propose next-best validation;
- cross-industry intelligence that identifies reusable mechanisms, patterns, pressures and transformation trajectories;
- Commercial Digital Twins spanning enterprises, industries, market participants, opportunities, infrastructure and relationships;
- richer refresh governance using materiality, volatility, evidence cutoff, contradiction and risk;
- stronger validation of duplicate observations, orphaned assets, stale evidence and unresolved contradiction clusters;
- progressively governed exchange between Enterprise Knowledge, Knowledge Packs, Presentation Models and Flora.

Future work must remain architecture-first and technology-neutral unless a separate implementation specification is explicitly created.

## Cross-reference Suggestions

Existing repository documentation should consider referencing this architecture where it defines or consumes governed knowledge assets:

- `architecture/reference-architecture/CIOS-Reference-Architecture-v1.0.md` should reference Enterprise Knowledge as the repository-level governing architecture for durable knowledge assets.
- `architecture/reference-architecture/CIOS-Design-Doctrine.md` should reference this document as the repository expression of the doctrine that evidence proves change, observations remember change, Enterprise Models accumulate change and reports are views.
- `architecture/enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md` should reference Enterprise Knowledge where Enterprise Twins are treated as governed repository assets.
- `architecture/enterprise-intelligence/volume-1-enterprise-modelling/EI-002-Enterprise-Knowledge-Graph.md` should reference the relationship and identifier semantics defined here.
- `architecture/enterprise-intelligence/volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md` should reference the Observation Register asset type and repository validation expectations.
- `architecture/specifications/knowledge-packs/Knowledge-Pack-Specification-v1.0.md` should reference this architecture as a source of repository asset taxonomy, metadata and lineage expectations.
- `architecture/decisions/README.md` should note that future ADRs affecting Enterprise Knowledge should be checked against this architecture.

## Architectural Observations

- The existing CIOS doctrine is already strongly aligned with Enterprise Knowledge: evidence, observations, models and reports have distinct responsibilities.
- Enterprise Knowledge fills a repository-level gap between high-level doctrine and domain-specific assets by defining how governed knowledge is organised and evolved.
- The architecture should prevent Banking from becoming an implicit hardcoded domain model; Banking remains the first reference implementation only.
- The metadata and identifier rules are essential because filenames and folder structures will change as industries, twins and asset types scale.
- Validation should mature before large-scale asset creation, or the repository risks becoming a document collection rather than a knowledge substrate.
- No conflict with the reviewed accepted ADRs was identified. This architecture reinforces ADR-001 and ADR-002 by preserving observations as atomic intelligence units and Enterprise Models as durable memory.

## Validation Report

This architecture was reviewed against the requested CIOS architecture sources at a documentation level:

| Review source | Validation result |
| --- | --- |
| CIOS Chief Architect / Design Doctrine | Aligned. The document preserves evidence, observation, model and report separation and the change doctrine. |
| CIOS Reference Architecture | Aligned. The document supports Enterprise Intelligence, Commercial Digital Twins, Presentation Intelligence and Knowledge Exchange boundaries. |
| Enterprise Model Specification | Aligned. Enterprise Twins are treated as durable governed memory assets. |
| Observation Model | Aligned. Observations remain atomic, evidence-backed, non-speculative and separate from recommendations. |
| Enterprise Knowledge Graph | Aligned. Relationship semantics preserve direction, lineage, confidence, uncertainty and inspectability. |
| Existing ADRs reviewed | Aligned with ADR-001 and ADR-002. No conflicting architectural decision was identified. |

Validation findings:

- **Pass:** Domain neutrality is preserved; no Banking-specific rules are required.
- **Pass:** Required sections are present.
- **Pass:** Required asset types are defined.
- **Pass:** Mandatory metadata semantics are defined without prescribing implementation values.
- **Pass:** Identifier permanence and path independence are specified.
- **Pass:** Evidence lineage, unknowns and contradictions are first-class architectural concerns.
- **Pass:** Flora integration is described in semantic and architecture-neutral terms.
- **Warning:** Existing repository documents do not yet cross-reference this new architecture. Cross-reference updates are suggested above but not applied in this change.
