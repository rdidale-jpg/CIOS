---
source: FA-001-Flora-Enterprise-Intelligence-Workspace-Reference-Architecture-v2.docx
conversion_note: Markdown transcription for repository navigation; architectural wording preserved from uploaded source document.
---


# FA-001

# Flora Enterprise IntelligenceWorkspace Reference Architecture

The architectural north star for an object-centric, evidence-grounded and commercially actionable Enterprise Intelligence Workspace.

| Status | Proposed |

| --- | --- |

| Version | 2.0 |

| Document class | Reference Architecture |

| Owner | Chief Architect |

| Authority | Applies accepted CIOS architecture and ADR decisions to the Flora workspace interaction model |

> Core proposition Flora is the Enterprise Intelligence Workspace over governed Enterprise Intelligence. Users navigate objects, change perspectives, inspect reasoning and move toward commercially valuable action without losing evidence, uncertainty or lineage.

Evidence proves change.Observations remember change.Enterprise Models accumulate change.Reports are views.

# Executive Summary

Flora is the operating workspace through which trusted advisers explore, understand, reason about and act on governed Enterprise Intelligence. It is not a report portal, CRM, dashboard suite or second knowledge store.

| What is Flora? | A contextual Enterprise Intelligence Workspace centred on governed objects. |

| --- | --- |

| Why does it exist? | To turn evidence and enterprise understanding into explainable, commercially valuable action. |

| What makes it different? | It organises work around objects, perspectives, reasoning and actions rather than pages and applications. |

## Architectural outcome

A user should be able to search for an enterprise or commercial object, focus it, change perspective, inspect evidence and reasoning, compare alternatives, validate uncertainty and shape a next action without leaving the workspace or losing context.

## The architectural shift

| From | To |

| --- | --- |

| Page navigationExplore → Focus → Shape | Object-centric workspaceSearch → Focus Object → Change View → Reason → Act |

## Design promise

> Five-minute comprehension test A first-time user should understand what Flora is, what object is in focus, why a conclusion is believed, what remains unknown and what action is possible within five minutes.

# 1. Purpose, Scope and Authority

## 1.1 Purpose

FA-001 defines the conceptual operating architecture of the Flora Enterprise Intelligence Workspace. It establishes the workspace model, universal interaction contract, architectural boundaries and design review standard.

## 1.2 In scope

Object-centric workspace interaction.

Universal views and actions.

Navigation and workspace behaviour.

How evidence, reasoning and commercial context are exposed.

Separation between Flora workspace state and governed Enterprise Intelligence.

Architectural acceptance and review criteria.

## 1.3 Out of scope

Canonical semantics of Evidence, Observation, Enterprise Model or Enterprise Knowledge Graph.

Persistence, API, security, identity or deployment implementation.

Detailed visual design, component library or page-level UX specification.

Runtime ownership already governed by the Reference Architecture, Accepted ADRs and owning Enterprise Intelligence papers.

## 1.4 Authority order

This document applies authoritative CIOS decisions to the Flora workspace. Where it conflicts with an Accepted ADR or an owning architecture paper, the Accepted ADR or owning paper prevails and FA-001 must be reconciled.

> Authority principle FA-001 governs how Flora presents and enables interaction with Enterprise Intelligence. It does not redefine the governed intelligence model.

# 2. Architectural Position

FA-001 is the bridge between authoritative Enterprise Intelligence architecture and implementation-facing product and UX work.

| Layer | Role |

| --- | --- |

| CIOS doctrine | Mission, principles and non-negotiable operating beliefs. |

| Reference Architecture | Platform boundaries, runtime structure and system responsibilities. |

| Enterprise Intelligence papers | Canonical models for enterprise, knowledge, observations, evidence and reasoning. |

| Accepted ADRs | Enduring decisions that constrain implementation. |

| FA-001 | Workspace reference architecture and interaction model. |

| Product Architecture Blueprint | Product-level application of the workspace architecture. |

| UX specifications | Reference journeys and behavioural detail. |

| Codex missions | Implementation instructions with acceptance and validation. |

| Implementation | Code, tests, documentation and operational evidence. |

## 2.1 Architectural dependency

Flora depends on governed Enterprise Intelligence. It may cache or hold transient workspace state, but it must not silently promote presentation state, user inference or generated text into canonical enterprise knowledge.

# 3. Guiding Principles

Object first

Users navigate governed Enterprise Intelligence objects, not applications.

Perspective before page

A view is an interpretation of the focused object, not a disconnected destination.

Reasoning before recommendation

Recommendations must be traceable to evidence, observations, questions, uncertainty and rationale.

Enterprise Intelligence before CRM

Commercial activity follows understanding; it does not replace it.

Unknowns and Contradictions are assets

Uncertainty and conflicting evidence remain visible and actionable.

Human knowledge is labelled

Human-supplied context is distinguishable from sourced evidence and machine-generated inference.

Workspace never owns knowledge

Flora renders and interacts with governed intelligence; it does not become a second source of truth.

Learning before selling

When conviction is incomplete, Flora should recommend validation and learning rather than premature selling.

# 4. Reference Architecture Diagram

Figure 1 is the primary architectural representation of FA-001. The following sections define how it must be read and applied.

Figure 1 - Flora Enterprise Intelligence Workspace Reference Architecture

# 5. Reading the Architecture

## 5.1 Focus Object

The Focus Object is the centre of the workspace. It may be an Industry, Enterprise, Mechanism, Executive, Observation, Evidence item, Question, Opportunity, Provider or Offer. Every view, action and reasoning panel is contextual to it.

## 5.2 Navigation

Navigation helps the user find, return to and follow objects through Search, Recent, Watchlist, History and Exploration Trails. Navigation does not imply separate application modules.

## 5.3 Workspace - Understand

Workspace perspectives support interpretation of the focused object: Overview, What Changed, Timeline, Behaviour, Relationships, Mechanisms and Transformations.

## 5.4 Reasoning - Evidence

The reasoning region exposes Evidence, Observations, Questions, Unknowns, Contradictions, Hypotheses and Recommendations. Its purpose is inspectability rather than decorative explanation.

## 5.5 Commercial Context - Connect and Act

Commercial Context links enterprise understanding to Need, Provider Fit, Accessibility, Commercial Conviction, Offers, Validation and Actions. These dimensions remain separate and should not be collapsed into an opaque score.

## 5.6 Actions - Act

Universal actions include Validate, Watch, Compare, Ask, Explain, Shape and Share. Actions operate on the focused object and preserve its context.

## 5.7 Universal Views

Common views create a consistent mental model across object types. Availability may vary by object, but naming and meaning must remain stable.

# 6. Architectural Layers

| Layer | Contents | Responsibility |

| --- | --- | --- |

| Experience | Enterprise Intelligence Workspace | Object-centric environment used by advisers, executives and teams. |

| Interaction | Views, actions, navigation and collaboration | Defines how users move, inspect, compare, validate and act. |

| Reasoning | Synthesis, explanation and recommendations | Produces inspectable interpretation without concealing uncertainty. |

| Knowledge | Enterprise Models and Knowledge Graph | Holds durable enterprise understanding and relationships. |

| Observation | Curated observations with provenance and context | Records what has been seen, inferred or asserted over time. |

| Evidence | Governed sources and signals | Provides the immutable or controlled basis for claims and change. |

## 6.1 Separation of concerns

Higher layers may interpret and present lower-layer intelligence, but they must not overwrite lower-layer authority. For example, a workspace explanation may summarise observations, but the observation objects and their evidence lineage remain governed outside the presentation layer.

# 7. Universal Object Contract

Every governed object presented in Flora should expose the following contract where applicable.

| Contract element | Expectation |

| --- | --- |

| Identity | Stable identifier, name, type, status and provenance. |

| Relationships | Inspectable links to other governed objects. |

| Perspectives | Consistent views such as Overview, Evidence, Timeline and What Changed. |

| Actions | Ask, Explain, Compare, Watch, Validate, Shape and Share. |

| Evidence | Sources and lineage supporting claims about the object. |

| Observations | What CIOS has seen or inferred about the object. |

| Questions | Answerable, open or unresolved enterprise questions. |

| Unknowns | Known gaps that constrain confidence or action. |

| Contradictions | Conflicts in evidence, observations or reasoning. |

| Commercial context | Need, Provider Fit, Accessibility, Conviction, Offers and Validation. |

| Explainability | Rationale and lineage for material conclusions or recommendations. |

| History | Meaningful change in the object, model and reasoning over time. |

## 7.1 Applicability

The contract is universal in meaning, not necessarily universal in availability. A view or action may be unavailable when the focused object lacks the required governed data. Flora should expose the absence honestly rather than manufacture content.

# 8. Navigation Model

Flora navigation is a grammar for moving through Enterprise Intelligence:

Search  →  Focus Object  →  Choose Perspective  →  Investigate  →  Reason  →  Validate  →  Act

## 8.1 Exploration Trails

An Exploration Trail records the meaningful path through objects and perspectives so that inquiry can be resumed, shared and learned from without treating the trail itself as canonical enterprise knowledge.

## 8.2 Compare

Comparison is a workspace operation across two or more governed objects. It must preserve each object's evidence, unknowns and context rather than flattening them into a superficial side-by-side summary.

## 8.3 What Changed

What Changed should distinguish external change, knowledge change, reasoning change, commercial change and model correction. This prevents users from confusing new evidence with a change in the enterprise itself.

# 9. Workspace Behaviour

### Change focus

Replace the current Focus Object while retaining relevant workspace context.

### Change perspective

Interpret the same object through another governed or approved view.

### Follow relationship

Move to a connected object while retaining the exploration trail.

### Inspect reasoning

Open the evidence, observations, questions, unknowns and contradictions behind a conclusion.

### Validate

Create or perform a learning action that tests a hypothesis, need, fit, accessibility or conviction.

### Shape

Develop an opportunity or brief without severing it from enterprise understanding and evidence.

# 10. Architectural Boundaries

| Flora owns | Governed Enterprise Intelligence owns |

| --- | --- |

| Presentation and composition | Evidence and source lineage |

| Navigation and focus state | Observations and their lifecycle |

| Workspace and user context | Enterprise Models |

| Interaction patterns | Enterprise Knowledge Graph |

| Perspective rendering | Questions, hypotheses and recommendations |

| Transient comparison state | Commercial reasoning and governed assessments |

## 10.1 Prohibited boundary violations

Creating a second knowledge store inside the UI.

Persisting generated explanation as fact without governed promotion and lineage.

Hiding Unknowns or Contradictions to make a recommendation appear stronger.

Collapsing Need, Provider Fit, Accessibility and Commercial Conviction into one opaque score.

Treating reports or workspace layouts as canonical enterprise models.

Allowing user-entered knowledge to lose its human-supplied label.

# 11. Relationship to Existing Architecture

| Document | Relationship to FA-001 |

| --- | --- |

| CIOS Chief Architect Handbook | Primary guide for Chief Architect judgement and working practice. |

| CIOS-AI | Authoritative detailed AI architecture and runtime decisions. |

| CIOS Reference Architecture v1.0 | Governs platform structure, ownership and runtime boundaries. |

| EI-001 Enterprise Model Specification | Defines the durable Enterprise Model that Flora presents. |

| EI-002 Enterprise Knowledge Graph | Defines governed enterprise relationships and graph semantics. |

| EI-003 Enterprise Behaviour Model | Defines behaviour representation used by workspace perspectives. |

| EI-012 Enterprise Observation Model | Defines Observation doctrine, lifecycle, provenance and uncertainty. |

| FP-009 Hypothesis Validation Standard | Governs validation of hypotheses and recommendations. |

| Flora Product Architecture Blueprint | Applies FA-001 to product structure and behaviour. |

| Accepted Flora ADR | Defines Flora as the Enterprise Intelligence Workspace and constrains implementation. |

| Flora reference UX journey | Demonstrates the architecture through a concrete end-to-end journey. |

# 12. Design Review Checklist

Which governed object is in focus?

Which perspective is being introduced or changed?

Which universal action is being enabled?

Which region of FA-001 does the change implement?

What evidence and observations support the displayed conclusion?

Are Unknowns and Contradictions visible?

Is human-supplied knowledge labelled?

Can a material recommendation be traced through inspectable lineage?

Does the proposal create a second source of truth?

Does it keep Need, Provider Fit, Accessibility and Commercial Conviction distinct?

Which Accepted ADR or owning architecture paper governs the decision?

What validation proves the change improves detection, understanding, prediction or action?

# 13. Acceptance Criteria

Users navigate governed objects rather than application pages.

Perspectives are contextual views over the focused object.

Universal actions behave consistently across applicable object types.

Commercial action emerges from enterprise understanding and inspectable reasoning.

Evidence, Observations, Unknowns and Contradictions remain visible where material.

Workspace state does not become canonical Enterprise Intelligence.

Need, Provider Fit, Accessibility and Commercial Conviction remain separately inspectable.

Every material new capability can be located within FA-001.

Implementation conforms to Accepted ADRs and owning architecture papers.

Validation evidence demonstrates the intended user and architectural outcome.

# 14. Future Evolution

FA-001 deliberately leaves room for evolution without asserting unimplemented capability as current fact.

Curiosity Engine and governed Enterprise Questions.

Multi-object workspaces and comparative reasoning.

Collaboration, shared trails and adviser workflows.

Scenario modelling and predictive Enterprise Intelligence.

Personalised but non-canonical workspace preferences.

Enterprise Perspective as a governed definition of how an object may be interpreted.

> Anticipated evolution Enterprise Perspective may become a governed architectural concept in a future owning paper or ADR. Until then, perspectives remain an approved workspace interaction construct and must not silently redefine canonical object semantics.

# Appendix A - Glossary

| Term | Definition |

| --- | --- |

| Focus Object | The governed object currently at the centre of the workspace. |

| Perspective | A consistent interpretation or view over a focused object. |

| Workspace State | Transient user and interaction context held by Flora. |

| Governed Enterprise Intelligence | Authoritative evidence, observations, models, relationships and reasoning managed by the CIOS platform. |

| Commercial Context | Need, Provider Fit, Accessibility, Commercial Conviction, Offers, Validation and Actions. |

| Observation | The atomic commercial object that records what CIOS has seen, inferred or been told, with provenance and context. |

| Mechanism | A causal or structural driver explaining enterprise behaviour or change. |

| Exploration Trail | A resumable path through objects and perspectives during inquiry. |

# Appendix B - Revision History

| Version | Date | Status | Change |

| --- | --- | --- | --- |

| 0.1 | July 2026 | Concept | Initial generated reference diagram used to validate the architecture. |

| 1.0 | July 2026 | Draft | First explanatory document around the diagram. |

| 2.0 | July 2026 | Proposed | Added authority, layers, universal object contract, navigation model, boundaries, review checklist and glossary. |

# Appendix C - Repository and Delivery Guidance

Recommended canonical repository path:

CIOS/architecture/reference-architectures/FA-001-Flora-Enterprise-Intelligence-Workspace-Reference-Architecture.md

The repository-managed package should contain:

The authoritative Markdown document.

A repository-native editable diagram source.

Canonical SVG export.

PNG and PDF exports for embedding and review.

Cross-references from the document map, Product Architecture Blueprint, Accepted Flora ADR and UX journey.

## Completion Standard

FA-001 is complete when the document and diagram are committed, cross-referenced, rendered cleanly, and used as the architectural review standard for Flora implementation missions.
