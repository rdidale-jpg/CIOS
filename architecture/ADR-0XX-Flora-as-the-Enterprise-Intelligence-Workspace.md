# ADR-0XX — Flora as the Enterprise Intelligence Workspace

**Status:** Proposed  
**Decision owner:** Rob / CIOS  
**Architecture owner:** CIOS Chief Architect  
**Date:** 2026-07-19  
**Decision type:** Product and runtime architecture  
**Supersedes:** None  
**Related documents:**

- `CIOS/architecture/FP-0XX-Flora-Enterprise-Intelligence-Workspace-Product-Architecture.md`
- `CIOS/architecture/Flora-Workspace-Architecture-Reconciliation-Report.md`
- `CIOS/architecture/CIOS-Reference-Architecture-v1.0.md`
- `CIOS/architecture/CIOS-AI.md`
- `CIOS/architecture/EI-001-Enterprise-Model-Specification.md`
- `CIOS/architecture/EI-002-Enterprise-Knowledge-Graph.md`
- `CIOS/architecture/EI-003-Enterprise-Behaviour-Model.md`
- `CIOS/architecture/EI-012-Enterprise-Observation-Model.md`
- `CIOS/architecture/FP-009-Hypothesis-Validation-Standard.md`

> Repository paths must be verified before this ADR is accepted. Where an Accepted ADR or owning architecture paper conflicts with this document, the authoritative decision prevails and this ADR must be reconciled.

## 1. Decision

Flora shall be the contextual Enterprise Intelligence workspace for CIOS.

Flora shall provide the primary user environment through which authorised users explore, understand, explain, anticipate and act on governed Enterprise Intelligence.

Flora shall not establish a separate source of truth. It shall consume, render and interact with governed Enterprise Intelligence objects, relationships, reasoning state and lineage owned by the CIOS architecture.

Flora shall therefore be designed as:

```text
A contextual reasoning and action workspace
over governed Enterprise Intelligence
```

and not as:

```text
A standalone chatbot
A report repository
A dashboard collection
A CRM replacement
A second enterprise knowledge store
A UI-specific ontology
```

## 2. Context

CIOS exists to help elite strategic commercial professionals understand enterprise change, form commercially valuable judgement and take better action.

Its differentiator is Enterprise Reinvention Intelligence supported by Living Commercial Digital Twins.

The governing doctrine is:

> Evidence proves change.  
> Observations remember change.  
> Enterprise Models accumulate change.  
> Reports are views.

Previous Flora concepts risked organising the product around application modules, pages or separate “research” and “sales” domains. That approach could create:

- duplicate truth models;
- disconnected exploration and commercial workflows;
- report-centric memory;
- UI-local semantics;
- opaque opportunity scores;
- weak reasoning lineage;
- premature sales conclusions from incomplete enterprise evidence.

The Product Architecture Blueprint instead proposes an object-first workspace with four user-facing reasoning modes:

- Explore;
- Explain;
- Anticipate;
- Act.

This ADR establishes the durable architectural boundary needed before detailed UX design or implementation begins.

## 3. Architectural intent

Flora must enable a user to move through the following chain without losing context or lineage:

```text
Curiosity
→ Exploration
→ Explanation
→ Question
→ Evidence Demand
→ Understanding
→ Commercial Insight
→ Opportunity
→ Judgement
→ Action
→ Outcome
→ Learning
```

The user experience may provide direct entry to Opportunities or Actions, but those views must remain connected to the governed enterprise understanding from which they derive.

Flora must amplify human judgement. It must not conceal uncertainty or simulate certainty that the underlying intelligence does not support.

## 4. Scope

This decision governs:

- Flora’s role in the CIOS architecture;
- the boundary between Flora and governed Enterprise Intelligence;
- the relationship between user experience and canonical objects;
- the relationship between presentation state and durable enterprise memory;
- the minimum explainability expected of material insights and Recommendations;
- the architectural relationship between exploration and commercial action;
- constraints inherited by all Flora UX specifications and Codex missions.

This decision applies to:

- Flora Home;
- Search;
- Enterprise Intelligence Workspace;
- Watchlist;
- Opportunity views;
- Action views;
- Memory views;
- contextual Flora Ask experiences;
- future Flora surfaces that consume Enterprise Intelligence.

## 5. Out of scope

This ADR does not decide:

- the detailed page or component design;
- the persistence model for Exploration Trails;
- the canonical schema for Enterprise Questions;
- the implementation of the Enterprise Curiosity Engine;
- the model-delta contract behind “What changed?”;
- the full representation of future states and scenarios;
- detailed API contracts;
- database technologies;
- frontend frameworks;
- deployment architecture;
- authentication or authorisation implementation;
- CRM integration;
- the detailed opportunity or provider ontology.

Those matters require owning architecture papers, separate ADRs or implementation specifications.

## 6. Governing constraints

### 6.1 No second source of truth

Flora must not create UI-specific canonical versions of:

- Enterprises;
- Industries;
- Participants;
- Evidence;
- Observations;
- Signals;
- Hypotheses;
- Theses;
- Unknowns;
- Contradictions;
- Questions;
- Opportunities;
- Provider Capabilities;
- Provider Offers;
- Recommendations;
- Mechanisms.

Where a product projection is required, it must retain the identifier and lineage of the governed source object.

### 6.2 Observation-led intelligence

Flora must preserve the core intelligence chain:

```text
Evidence
→ Observation
→ Strategic Signal
→ Hypothesis
→ Commercial Thesis
→ Recommendation
```

Flora must not reason directly from ungoverned document fragments when governed Observations or equivalent accepted intelligence objects are available.

### 6.3 Reports and screens are views

Rendered pages, cards, summaries, exports and reports must not become canonical enterprise memory.

Material learning must be recorded through the owning governed models.

### 6.4 Unknowns and Contradictions remain visible

Flora must not hide unresolved uncertainty to make the interface appear more decisive.

Material views must expose, where relevant:

- Unknowns;
- Contradictions;
- assumptions;
- alternative hypotheses;
- evidence gaps;
- confidence;
- freshness;
- review conditions.

### 6.5 Human knowledge remains labelled

Human-supplied facts, interpretations, assumptions and judgements must remain distinguishable from machine-derived or externally evidenced knowledge.

### 6.6 Strong Recommendations require inspectable lineage

A material Recommendation must expose a reasoning path sufficient for an authorised user to inspect:

```text
Source
→ Evidence
→ Observation
→ Pattern or Signal
→ Hypothesis
→ Thesis
→ Commercial Conviction
→ Recommendation
```

The precise chain may vary by accepted model, but lineage must not be replaced by an unexplained score.

### 6.7 Exploration and commercial action share one governed model

Exploration and sales are not separate architecture domains.

The same governed enterprise understanding must support:

- research;
- explanation;
- anticipation;
- opportunity discovery;
- provider assessment;
- commercial action;
- learning.

Commercial views may optimise for speed and executive specificity, but must not duplicate or detach from Enterprise Intelligence.

### 6.8 Commercial judgement dimensions remain separate

Flora must preserve distinct judgements for:

- Enterprise Need;
- Commercial Domain Relevance;
- Commercial Intervention Boundary;
- Addressable Value;
- Provider Fit;
- Commercial Accessibility;
- route to market;
- timing;
- evidence strength;
- Commercial Conviction.

A composite score may be used as a secondary aid only if its inputs, weights and limitations are inspectable. It must not replace the underlying dimensions.

### 6.9 Future states preserve uncertainty

Flora may render anticipated future states, scenarios and transformation trajectories.

It must not present an inferred future as a known fact.

Future-oriented views must preserve:

- hypothesis or scenario status;
- assumptions;
- confidence;
- signposts;
- inhibitors;
- alternatives;
- evidence that would strengthen or weaken the view.

### 6.10 Domain neutrality

The first reference implementation may use UK Banking and Lloyds.

No Banking-specific rule, label, mechanism or workflow may become a core architectural assumption unless separately justified as domain-neutral.

### 6.11 Learning before selling

Where evidence or conviction is incomplete, Flora should recommend actions such as:

```text
Learn
Monitor
Validate
Shape
Position
Partner
Pursue
Do Not Pursue
```

It must not force every investigation toward pursuit.

## 7. Product interaction model

Flora shall provide four user-facing reasoning modes over the same governed intelligence:

### Explore

What is happening, and what is connected?

### Explain

Why do we believe this?

### Anticipate

What may happen next?

### Act

What should we do?

These are product perspectives. They are not separate canonical data models or independent pipelines.

Flora should favour an object-first interaction model in which a user can focus on a governed object and perform consistent contextual actions such as:

- What changed?
- Why do we believe this?
- What contradicts it?
- What remains Unknown?
- What is connected?
- Compare.
- Ask this object.
- Watch.
- Show evidence.
- Show opportunities.
- Next best exploration.

The definitive runtime interaction contract requires a subordinate ADR or specification.

## 8. Runtime authority boundary

Flora may own:

- presentation state;
- navigation state;
- user preferences;
- temporary filters;
- workspace layout;
- draft prompts;
- local interaction state;
- user-specific watch configuration, subject to its owning model;
- non-canonical display projections.

Flora may not silently own:

- canonical enterprise identity;
- canonical Observation state;
- evidence authority;
- hypothesis lifecycle;
- Question semantics;
- commercial conviction semantics;
- Recommendation authority;
- canonical mechanism identity;
- enterprise model history.

Where a user action produces durable intelligence, Flora must invoke the owning model’s governed creation or update process.

## 9. Consequences

### 9.1 Positive consequences

This decision:

- creates one coherent user environment;
- connects enterprise exploration to commercial action;
- prevents duplicated research and sales truth;
- strengthens explainability;
- supports durable Enterprise Memory;
- preserves Unknowns and Contradictions;
- enables domain-neutral product evolution;
- provides a stable boundary for UX and Codex implementation;
- makes reports and dashboards replaceable views rather than architectural assets;
- supports incremental delivery through complete reasoning slices.

### 9.2 Costs and trade-offs

This decision:

- requires integration with governed object and lineage services;
- makes superficial UI delivery slower than building disconnected screens;
- requires clearer ownership of Question, Curiosity, model-delta and future-state semantics;
- limits the use of convenient but opaque aggregate scores;
- requires explicit promotion rules from workspace activity into durable knowledge;
- demands more disciplined testing of lineage and uncertainty;
- may expose architectural gaps before user-facing features can be completed.

These costs are accepted because they protect the differentiating asset: governed Enterprise Reinvention Intelligence.

## 10. Rejected alternatives

### 10.1 Flora as a collection of application modules

Rejected because it encourages separate Research, Sales, Reporting and Opportunity truth models.

### 10.2 Flora as a generic conversational interface

Rejected because conversation alone does not provide durable memory, governed identity, inspectable lineage or reliable change detection.

### 10.3 Flora as a dashboard and report portal

Rejected because reports are transient views and do not constitute the Enterprise Model.

### 10.4 Flora as a CRM replacement

Rejected because CRM records commercial process; Flora’s primary role is enterprise understanding, reasoning and commercially valuable action.

CRM integration may be appropriate, but CRM semantics must not define Enterprise Intelligence.

### 10.5 Flora as an independent knowledge graph

Rejected because the Enterprise Knowledge Graph and owning Enterprise Intelligence models already govern canonical knowledge.

### 10.6 Separate Exploration and Sales architectures

Rejected because the separation would break reasoning continuity and duplicate enterprise understanding.

## 11. Required subordinate decisions

The following must be resolved through separate ADRs or owning specifications:

1. Object-first runtime interaction and projection contract.
2. Exploration Trail persistence and promotion rules.
3. Canonical model-delta semantics for “What changed?”.
4. Runtime integration with EI-015 Enterprise Question Model.
5. Runtime integration with EI-016 Enterprise Curiosity Engine.
6. Commercial judgement separation and any permitted aggregate scoring.
7. Minimum explainability contract for material claims and Recommendations.
8. Future-state and scenario persistence.
9. Boundary between governed knowledge, user workspace state and event history.

## 12. Implementation constraints

Every Flora Codex mission must:

- cite this ADR and its authoritative inputs;
- identify the governed objects and services it consumes;
- state what Flora owns and does not own;
- prevent duplicate canonical schemas;
- preserve lineage for material outputs;
- preserve Unknowns and Contradictions;
- label human-supplied knowledge;
- maintain separate commercial judgement dimensions;
- state whether generated state is transient, user-owned or governed;
- include tests for the relevant architectural constraints;
- report any conflict with an Accepted ADR or owning paper;
- avoid Banking-specific core implementation.

## 13. Acceptance criteria

This ADR may be accepted when reviewers agree that:

1. Flora is the primary contextual workspace over governed Enterprise Intelligence.
2. Flora is not a separate source of truth.
3. Exploration and commercial action share one governed intelligence model.
4. Observation doctrine remains intact.
5. Reports and screens remain views.
6. Unknowns and Contradictions remain visible.
7. Human knowledge remains labelled.
8. material Recommendations require inspectable lineage.
9. Need, Provider Fit, Accessibility and Commercial Conviction remain distinct.
10. future-state views preserve uncertainty.
11. the UK Banking reference journey does not define domain-specific core architecture.
12. subordinate decisions are explicitly deferred rather than silently embedded in implementation.

## 14. Validation

Validation shall include:

### Architecture review

Confirm consistency with:

- the CIOS Reference Architecture;
- CIOS-AI;
- EI-001 Enterprise Model Specification;
- EI-002 Enterprise Knowledge Graph;
- EI-003 Enterprise Behaviour Model;
- EI-012 Enterprise Observation Model;
- FP-009 Hypothesis Validation Standard;
- Accepted ADRs.

### Product review

Demonstrate that the proposed UK Banking → Lloyds → APP Fraud → Opportunity → Validation journey can operate through one governed intelligence context.

### Negative validation

Confirm that the design does not require:

- a parallel Flora ontology;
- duplicated enterprise records;
- a separate sales truth store;
- report files as canonical memory;
- an opaque opportunity score;
- unsupported future certainty;
- direct promotion of every workspace interaction into Enterprise Knowledge.

## 15. Decision outcome

When accepted, this ADR becomes the parent architectural decision for Flora vNext.

All subsequent Flora UX specifications, ADRs and Codex missions must conform to it.

The delivery sequence shall be:

```text
Accepted parent ADR
→ subordinate architecture decisions
→ UX Journey Specification
→ bounded Codex mission
→ implementation
→ architectural validation
→ learning
```

## 16. Completion record

**Accepted by:** Pending  
**Acceptance date:** Pending  
**Repository path:** `CIOS/architecture/ADR-0XX-Flora-as-the-Enterprise-Intelligence-Workspace.md`  
**Implementation status:** Not started  
**Editorial reconciliation required:** Pending authoritative review  
