# FP-013 — Executive Intelligence Workspace

**Identifier:** FP-013  
**Version:** 0.1  
**Document Type:** Founding Paper  
**Authority Classification:** Proposed founding paper; documentation-only and non-runtime  
**Status:** Proposed  
**Date:** 2026-07-27  
**Owner:** Rob / CIOS  
**Release-profile membership:** None — review context only

## 1. Purpose and mission

The Executive Intelligence Workspace is the primary product experience through which governed Enterprise Intelligence is understood, explored and acted upon. Its mission is to enable executives, analysts, architects and researchers to inspect Digital Twins through a consistent, explainable and commercially useful experience.

Flora is evolving from a workflow-centred governance application into an operational Enterprise Intelligence workspace. Governance remains essential supporting infrastructure: the workspace does not replace governance, canonical memory or promotion boundaries, and introduces neither a new runtime nor a canonical knowledge model.

This paper owns the **executive-first product-experience doctrine** for inspecting governed intelligence. It does not own the underlying intelligence, presentation payload, runtime or governance semantics.

[FP-014 — Mission-Aware Executive Intelligence Composition](FP-014-Mission-Aware-Executive-Intelligence-Composition.md) extends this doctrine with the proposed composition that occurs before and around inspection; it does not replace FP-013 or change FP-013's authority over the common inspection experience and trust through inspection.

## 2. The CIOS Five Questions for Twin inspection

Every inspectable Twin should help its user answer:

1. What is this?
2. What do we currently know?
3. How complete and trustworthy is that understanding?
4. Why does it matter commercially?
5. Where should I explore next?

These inspection questions apply the wider [CIOS Design Doctrine](../reference-architecture/CIOS-Design-Doctrine.md); they do not replace its system-level five questions.

## 3. Progressive disclosure

The default experience begins at the **Executive** level. Users may disclose further depth without losing context:

| Experience level | Content |
| --- | --- |
| Executive | Summary; strategic and commercial implications; confidence; completeness; recent change. |
| Analyst | Intelligence domains; relationships; evidence; gaps and uncertainty. |
| Architect | Governance; provenance; lineage; contradictions; canonical ownership. |
| Technical | Identifiers; processing diagnostics; payloads; runtime metadata. |

Evidence must remain purposefully reachable from material conclusions, but implementation detail must not dominate initial understanding.

## 4. One common Twin inspection experience

Governed Digital Twins use one shared inspection model:

- the existing **Twin Inspection Shell** is the presentation and orchestration boundary;
- adapters or presentation metadata compose Twin-specific sections within that shell;
- existing runtimes and read models provide intelligence without transferring ownership to the shell; and
- canonical sources continue to own data, identity and governance semantics.

Twin-specific behaviour must not create separate inspection products, duplicate runtimes, a second knowledge store or a UI-local relationship model. The shell renders owned projections and links to owned workflows; it does not promote, persist or reinterpret canonical state. This direction extends the accepted [Enterprise Canvas navigation model](../decisions/ADR-013-Enterprise-Canvas-as-Primary-Living-Twin-Navigation.md) and preserves the [governed import boundary](../decisions/ADR-012-Governed-Blueprint-Package-Import-and-Canonical-Acceptance-Boundary.md) and [reasoning-runtime boundary](../decisions/ADR-014-Evidence-Governed-Enterprise-Intelligence-Reasoning-Runtime.md).

## 5. Common information hierarchy

### Layer 1 — Executive Intelligence

Identity and purpose; executive summary; commercial significance; completeness; confidence; freshness; recent change.

### Layer 2 — Business Intelligence Domains

Contextual domains may include enterprises, suppliers, market participants, capabilities, products and services, technologies, regulations, opportunities, risks and evidence. These examples are navigation and presentation groupings only. They establish no canonical Twin type, schema, data structure or taxonomy.

### Layer 3 — Connected Digital Twins

Navigation uses governed identities and governed relationships. The workspace must not fabricate a hierarchy, relationship or inspectable Twin where its canonical owner provides none.

### Layer 4 — Evidence and Governance

Evidence; research lineage; unknowns; contradictions; provenance; change history; technical diagnostics.

## 6. Business-first presentation

Business-first language is a presentation concern, not a model migration. Context may render **organisations** for generic entities, **intelligence** for generic facts, **connected intelligence** for generic relationships, or **research lineage** for implementation-oriented lineage terminology. Such labels are mappings over canonical concepts; they do not rename, modify or weaken those concepts. The [Twin Presentation Model Specification](../specifications/presentation-models/Twin-Presentation-Model-Specification-v1.0.md) remains the owner of presentation-payload semantics.

## 7. Evidence and explainability

- Material conclusions remain traceable to evidence under [FP-004](FP-004-Evidence-Acquisition-Standard.md), [FP-006](FP-006-Source-Quality-Standard.md), [EI-012](../enterprise-intelligence/volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md) and [FP-009](FP-009-Hypothesis-Validation-Standard.md).
- Uncertainty, contradictions and missing evidence must be preserved and visible at the appropriate disclosure level.
- Evidence must be accessible without dominating the Executive level.
- Confidence and completeness communicate bounded assessment, never certainty. They must retain their owner-defined scope, basis and freshness rather than being combined into an invented universal score.

## 8. Ownership and architectural boundaries

FP-013 owns only the executive-first inspection experience doctrine. It does **not** own or redefine:

- canonical memory or Digital Twin schemas, which remain with [EI-001](../enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md) and applicable canonical Twin owners;
- Evidence or Observation semantics;
- Twin identity or governed relationships;
- promotion governance;
- recommendation governance;
- research acquisition;
- runtime persistence;
- existing accepted ADRs; or
- existing Enterprise Intelligence doctrine.

In particular, [FP-004](FP-004-Evidence-Acquisition-Standard.md), [FP-006](FP-006-Source-Quality-Standard.md) and [FP-009](FP-009-Hypothesis-Validation-Standard.md) retain their acquisition, source-quality and hypothesis-governance scopes. The existing [Flora workspace reference architecture](../reference-architectures/FA-001-Flora-Enterprise-Intelligence-Workspace-Reference-Architecture.md) composes the broader workspace; FP-013 supplies its executive-first founding product position rather than duplicating that composition.

## 9. Intent, implemented capability and programme state

These states must not be conflated:

- **Architectural intent:** this paper describes the governed target experience: a common, executive-first inspection model with progressive access to governed depth.
- **Implemented runtime capability:** the repository currently contains the Twin Inspection Shell, Enterprise Canvas reuse, and only the adapters and inspection surfaces actually implemented. Their existence does not imply universal Twin coverage or full conformance with this target.
- **Programme state:** later work packages must close evidenced experience and adapter gaps, validate Twin-type coverage and pass normal architecture and runtime governance. Proposed WP2 capability is future work, not current runtime state.

No merge of this Proposed paper constitutes architectural acceptance. Acceptance and any implementation commitment require the repository's separate governed decision and promotion processes.

## 10. Commercial outcome

The expected outcome is faster executive understanding, improved confidence in decisions, greater reuse of governed intelligence, easier discovery of related commercial intelligence, reduced dependence on technical users to interpret the platform, and clearer differentiation from storage, workflow and dashboard products.

## 11. Success measures

The experience succeeds when:

- an executive can understand a Twin's purpose and material state in approximately 30 seconds;
- users can identify confidence, completeness and freshness without opening technical diagnostics;
- supporting evidence is reachable through progressive disclosure;
- users can navigate to related governed Twins when governed relationships and routable identities exist; and
- the same inspection model supports multiple Twin types through adapters or metadata, without separate runtimes.

## 12. Governance status

FP-013 is **Proposed**, documentation-only, non-runtime and non-promotional. It is registered for architectural review and navigation only. It has no membership in `architecture-authority`, `researcher-pack`, `assurance-pack` or `reviewer-pack`, and must not enter or invalidate the production Chief Architect Knowledge Pack merely because it is registered. A separate governed acceptance decision is required before its status or production-profile membership changes.
