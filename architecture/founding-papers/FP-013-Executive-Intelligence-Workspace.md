# FP-013 — Executive Intelligence Workspace

**Identifier:** FP-013
**Version:** 0.1
**Document Type:** Founding Paper
**Authority Classification:** Proposed founding architecture
**Document class:** Founding Paper
**Status:** Proposed
**Owner:** Rob / CIOS
**Architecture owner:** CIOS Chief Architect
**Last updated:** 2026-07-27
**Production behaviour:** Documentation-only product-experience intent; introduces no runtime behaviour, canonical data model, canonical write path or Twin type.
**Release-profile membership:** none — excluded from `architecture-authority`, `researcher-pack`, `assurance-pack` and `reviewer-pack`

## 1. Purpose

This paper proposes the **Executive Intelligence Workspace** as the primary product experience for consuming governed Enterprise Intelligence. Its purpose is to make complex Twin intelligence useful to an executive first, while keeping the underlying reasoning, uncertainty and lineage inspectable for every audience that needs greater depth.

This is a founding product-experience intent, not a new runtime, canonical data model, presentation payload specification or implementation plan. Until accepted, it is not architecture authority. If accepted, it will govern the composition and consumption experience only; existing accepted ADRs and owning papers continue to govern canonical intelligence, import, reasoning, presentation semantics and runtime behaviour.

## 2. Mission

The Executive Intelligence Workspace enables a decision-maker to understand what is happening in and around an enterprise, why it matters, what may happen next and what proportionate action or learning should follow.

Its mission is to turn governed Enterprise Intelligence into an executive-ready, commercially useful and inspectable experience without turning summaries into a second source of truth. It begins with meaning and decision context, then provides purposeful access to the governed depth behind each material judgement.

The Workspace is therefore:

- **executive-first**, because the opening experience communicates the enterprise situation, consequence and decision relevance in business language;
- **governed**, because every material claim retains its truth class, effective time, uncertainty and owning lineage;
- **inspectable**, because simplification never removes access to the supporting intelligence;
- **common**, because different accepted Twin types enter one inspection experience through owner-approved adapters rather than bespoke shells; and
- **read-first**, because inspection does not silently mutate canonical memory or bypass an owning governance workflow.

## 3. The five questions

Every inspectable Twin must help the user answer the established CIOS Five Questions:

1. **What changed?**
2. **Why did it change?**
3. **Why does it matter?**
4. **What will probably happen next?**
5. **What should we do?**

These questions are an experience test, not five new fields, scores or canonical objects. An answer may be unavailable, contested or not applicable. The Workspace must state that condition rather than manufacture completeness or certainty. "What should we do?" includes proportionate outcomes such as learn, validate, monitor or defer; it does not imply that every Twin supports a pursuit Recommendation.

The [CIOS Chief Architect Handbook](../handbook/CIOS-Chief-Architect-Handbook.md) remains the canonical home of the Five Questions and their relationship to the CIOS intelligence chain. This paper applies them to Twin consumption; it does not redefine that doctrine.

## 4. Executive-first progressive disclosure

The Workspace uses one continuous inspection journey with four levels:

1. **Executive** — the concise situation, material change, business consequence, likely direction, decision posture and principal uncertainty.
2. **Analyst** — the facts, comparisons, trends, assumptions, confidence, competing interpretations and evidence coverage needed to challenge the executive view.
3. **Architect** — the enterprise structures, mechanisms, relationships, dependencies, model boundaries and transformation implications that explain how the view fits together.
4. **Technical** — the object identity, truth class, version, effective date, Observation and Evidence lineage, source location, validation state, Unknowns, Contradictions and relevant audit history.

These are levels of disclosure over the same governed intelligence, not separate products or stores. A user may enter at or move directly to an appropriate level. The Executive level must stand on its own for comprehension; the Technical level must remain reachable for material claims. Audience preference may alter initial emphasis, not truth, authority or access to qualification.

This application preserves [ADR-013](../decisions/ADR-013-Enterprise-Canvas-as-Primary-Living-Twin-Navigation.md), which owns the accepted Enterprise Canvas decision and its four-level disclosure principle. It also aligns with the [CIOS Enterprise Intelligence Experience Standard](../../docs/Architecture/CIOS_Enterprise_Intelligence_Experience_Standard_v0.1.md), which owns the current cross-product working presentation guidance.

## 5. One common Twin inspection experience

An inspectable Twin should open in one common **Twin Inspection Shell** within the Executive Intelligence Workspace. The shell composes owner-provided read projections and provides consistent navigation, state labels and lineage access. It does not normalize those projections into another knowledge store.

Adapters allow an existing, governed Twin type to supply the sections it can support. An adapter may:

- resolve a governed Twin identity and authorised route;
- map owned read projections to common presentation sections;
- declare section availability and appropriate audience level;
- expose existing effective-date, freshness, confidence and lineage references; and
- resolve governed relationships to other inspectable Twins.

An adapter must not:

- invent or promote a Twin type;
- copy Evidence, Observations or domain records into UI-owned canonical state;
- create a UI-local relationship ontology;
- calculate an unowned completeness, confidence or commercial score;
- infer absent facts merely to fill a common section; or
- bypass type-specific acceptance, authorisation, review or canonical-write controls.

Sections that are unsupported are omitted unless their absence is itself governance-critical. `Unavailable`, `not supplied`, `unknown` and `not applicable` remain distinct.

## 6. Business-first presentation

The opening language must describe the enterprise, situation and consequence before exposing architecture machinery. Material content should normally present:

1. the business judgement in plain English;
2. why it matters and to whom;
3. what changed or is expected to change;
4. the proportionate decision, question or next action;
5. the material uncertainty or contrary view; and
6. access to supporting detail and lineage.

Internal identifiers, object classes, package paths, confidence mechanics and source registers belong in deeper disclosure unless needed to qualify the opening judgement. Canonical CIOS terms must remain available and accurate, but users should not have to translate repository or runtime terminology to understand the business meaning.

Business-first language must not disguise interpretation as fact, convert possibility into prediction, or collapse need, fit, accessibility and conviction into one unexplained result.

## 7. Evidence accessibility without evidence clutter

Evidence must be near every material judgement without dominating the executive surface. The Workspace should use concise qualification and clear inspection affordances rather than rendering a source register by default.

A user must be able to travel purposefully from a material judgement to, where available:

`judgement → reasoning or projection → Observation → Evidence → Source and exact location`

The journey must also expose material contrary Evidence, Unknowns, Contradictions, human-supplied knowledge, freshness, effective time and interpretation status. Evidence counts or badges are navigation aids, not substitutes for lineage quality. A clean surface must never imply stronger support than the governed state provides.

This paper applies, and does not duplicate, [ADR-005](../decisions/ADR-005-No-Recommendation-Without-Inspectable-Lineage.md), [EI-012](../enterprise-intelligence/volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md) and the evidence acquisition and quality doctrine owned by [FP-004](FP-004-Evidence-Acquisition-Standard.md) and [FP-006](FP-006-Source-Quality-Standard.md).

## 8. Relationship to existing presentation architecture

### 8.1 Twin Inspection Shell

The Twin Inspection Shell identified by the [WP1-007 Twin Intelligence Inspection Runtime Assessment](../reviews/WP1-007-Twin-Intelligence-Inspection-Runtime-Assessment.md) is the intended common composition boundary. The existing Enterprise Canvas, Model Explorer and Executive Intelligence Brief are foundations to converge, not a reason to create a parallel runtime. This paper establishes the product mission for that convergence; it does not specify the shell contract or claim that every Twin adapter is implemented.

### 8.2 Enterprise Canvas

The Enterprise Canvas remains the accepted primary navigation model for a Living Commercial Digital Twin under ADR-013. The Executive Intelligence Workspace contains and extends that experience through common inspection composition; it does not replace the Canvas, make the Canvas canonical memory or weaken its model-before-view boundary.

For currently supported Enterprise Twins, the Canvas is the preferred foundation and deterministic fallback. Other Twin types may join the common experience only through their existing canonical owners and an adapter that can satisfy the inspection contract.

### 8.3 Twin Presentation Models

The [Twin Presentation Model Specification v1.0](../specifications/presentation-models/Twin-Presentation-Model-Specification-v1.0.md) continues to own presentation payload semantics. An accepted Twin Presentation Model may provide an executive-ready interpretation for rendering, but its acceptance does not promote its claims to canonical fact. The Workspace may render or navigate such a payload through an adapter; it does not redefine its schema, exchange location, acceptance semantics or authorship.

The preferred opening order is: an existing accepted presentation where valid; a bounded, validated generated interpretation where explicitly supported; otherwise a deterministic governed overview. Inspection must never require fresh generation merely to open a Twin.

## 9. Canonical memory and governance boundaries

The Workspace is a view and orchestration boundary over governed Enterprise Intelligence. It preserves:

- [ADR-012](../decisions/ADR-012-Governed-Blueprint-Package-Import-and-Canonical-Acceptance-Boundary.md): receipt, staging or package acceptance is not canonical fact acceptance, and promotion remains explicit;
- ADR-013: Enterprise Canvas is a view over Living Twin state and progressive disclosure governs its navigation;
- [ADR-014](../decisions/ADR-014-Evidence-Governed-Enterprise-Intelligence-Reasoning-Runtime.md): governed fact remains distinct from runtime interpretation and generated output does not silently become canonical memory;
- [EI-001](../enterprise-intelligence/volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md): the Enterprise Model remains durable memory;
- EI-012: Observations and their lifecycle remain owned by the Enterprise Observation Model;
- [FP-009](FP-009-Hypothesis-Validation-Standard.md): Hypothesis state and validation remain governed; and
- [ADR-016](../decisions/ADR-016-Knowledge-Packs-as-Standard-Exchange-Mechanism.md), [FP-010](FP-010-Knowledge-Pack-Architecture.md), [FP-011](FP-011-Knowledge-Exchange-Architecture.md) and [EI-013](../enterprise-intelligence/EI-013-Knowledge-Asset-Exchange-Model.md): exchange and repository handling do not silently confer canonical authority.

User corrections, context and feedback enter existing governed candidate and review paths. Inspection remains read-first; commands that collect, review, promote, refresh or write remain explicit, authorised and auditable.

## 10. Architectural intent, runtime capability and programme evidence

Three kinds of statement must remain visibly distinct:

- **Architectural intent:** this Proposed paper describes the desired primary consumption experience.
- **Implemented runtime capability:** only reachable, tested behaviour in the repository or a verified deployment may be described as implemented; support may differ by Twin type and projection.
- **Current programme state:** work-package completion, validation and acceptance are evidence about delivery, not architecture authority.

In particular, WP1-008 verification may demonstrate implementation conformance and contribute acceptance evidence. It cannot accept this paper, override an owning document, create a canonical model or prove capability beyond its tested scope. The Authority Registry and the normal architecture acceptance process remain decisive.

## 11. Success measures

Success must be assessed without inventing a universal Twin quality score. Measures should be segmented by Twin type, user role and availability of governed source intelligence.

### Executive usefulness

- an executive can answer the Five Questions, or identify the governed reason an answer is unavailable;
- time to a defensible first understanding and next decision is reduced;
- users can distinguish fact, interpretation, uncertainty and recommendation posture; and
- the opening experience is understood without prior knowledge of CIOS object taxonomy.

### Inspectability and trust

- every material judgement offers a successful path to its available lineage;
- Unknowns, Contradictions, stale intelligence and human-supplied knowledge remain visible where decision-relevant;
- users can challenge or request validation through existing governed workflows; and
- executive summaries do not produce unsupported certainty or untraceable recommendations.

### Experience convergence

- supported Twin types use the common shell and shared vocabulary rather than parallel inspection products;
- domain entry points deep-link to one governed Twin identity and inspection route;
- adapters reuse owning projections without duplicated canonical records; and
- accessibility and task completion meet the applicable product standard.

### Governance integrity

- no presentation action silently mutates canonical memory;
- import, reasoning, presentation and Twin-type ownership remain with their canonical documents and services;
- runtime and programme claims are accurately scoped; and
- architecture and profile validation continue to pass without promoting this Proposed paper.

## 12. Expected commercial outcome

The expected outcome is faster, more confident executive consumption of Enterprise Intelligence: less time assembling and translating specialist artefacts, more time understanding enterprise change, challenging the evidence and choosing a proportionate commercial action.

Commercially, the Workspace should improve the quality and timing of strategic conversations, increase reuse of governed intelligence across roles, shorten the path from Twin acceptance to executive value, and differentiate CIOS through inspectable judgement rather than opaque summaries. These are expected outcomes to validate, not guaranteed benefits or authority to overstate Provider Fit, accessibility, conviction or revenue impact.

## 13. Acceptance and implementation boundary

Acceptance of this paper would approve the founding product-experience intent only. It would not by itself:

- implement or accept a Twin Inspection Shell contract;
- change a route, service, database, schema or canonical write path;
- create or approve an adapter for a particular Twin type;
- accept a Twin Presentation Model;
- add this paper to a governed release profile; or
- accept any WP1 implementation or verification result.

Any material runtime decision not already covered by ADR-012, ADR-013 or ADR-014 must follow the existing architecture decision workflow. A subordinate presentation-contract specification may define adapter and section mechanics without reopening accepted decisions, provided it preserves the boundaries in this paper.

## 14. Ownership and overlap summary

**Proposed owner:** FP-013 owns the founding product-experience intent for executive-first consumption and common inspection composition of governed Enterprise Intelligence.

It deliberately references rather than takes ownership from:

- ADR-013 and the Enterprise Intelligence Experience Standard for Enterprise Canvas and progressive-disclosure presentation doctrine;
- the Twin Presentation Model Specification for presentation payload semantics;
- EI-001, EI-002 and EI-012 for durable memory, governed relationships and Observation lineage;
- ADR-012 for import and promotion boundaries;
- ADR-014 for runtime interpretation boundaries;
- FP-004, FP-006 and ADR-005 for evidence quality and inspectable lineage; and
- the accepted owners of each existing Twin type.

No ADR or runtime change is required to propose this paper because it formalises product-experience intent and explicitly composes existing accepted boundaries. Acceptance of a future implementation contract or a decision that changes those boundaries may require a separate specification or ADR through normal governance.
