# FP-0XX — Flora Enterprise Intelligence Workspace Product Architecture

**Status:** Proposed  
**Document class:** Product Architecture Blueprint  
**Owner:** Rob / CIOS  
**Architecture owner:** CIOS Chief Architect  
**Date:** 2026-07-19  
**Authority:** Subordinate to Accepted ADRs, the CIOS Reference Architecture, FA-001 and owning Enterprise Intelligence papers.

**Related reference architecture:** `CIOS/architecture/reference-architectures/FA-001-Flora-Enterprise-Intelligence-Workspace-Reference-Architecture.md`

## 1. Purpose

This document defines how users should experience CIOS Enterprise Intelligence through Flora.

It is not a runtime implementation specification, database schema, UX wireframe or Codex instruction. It bridges authoritative architecture and implementation by defining the product interaction architecture Flora must preserve.

## 2. Mission

Flora enables an elite strategic commercial professional to explore, understand, explain and act on enterprise change.

Flora must help the user:

- explore industries, enterprises, participants, mechanisms and transformations;
- discover what changed and why it matters;
- inspect evidence, Observations, Unknowns and Contradictions;
- understand plausible future states without presenting unsupported certainty;
- reveal commercially valuable opportunities;
- distinguish enterprise need, Provider Fit, accessibility and conviction;
- identify offers to use, adapt or develop;
- leave every meaningful investigation with a justified action or learning objective.

> Flora is the interactive operating environment for Enterprise Reinvention Intelligence.

## 3. Product thesis

Flora is not primarily a chatbot, dashboard, CRM or report library.

Flora is a contextual reasoning workspace over governed Enterprise Intelligence.

Its differentiator is allowing a user to move from curiosity to commercially useful judgement while retaining durable enterprise memory, inspectable lineage, uncertainty, contradiction, temporal change, human judgement and learning.

## 4. Governing doctrine

Flora must preserve:

> Evidence proves change.  
> Observations remember change.  
> Enterprise Models accumulate change.  
> Reports are views.

Consequently:

1. Flora consumes governed semantics rather than treating rendered reports as canonical truth.
2. Material claims remain distinguishable as fact, inference, Signal, Hypothesis, forecast or Recommendation.
3. Unknowns and Contradictions remain visible.
4. Human-supplied knowledge is labelled.
5. Strong Recommendations require inspectable lineage.
6. Where conviction is incomplete, Flora prefers learning, validation or monitoring before pursuit.
7. UI convenience must not introduce duplicate canonical objects or collapse distinct reasoning states.

## 5. Primary user outcome

```text
Curiosity
→ Exploration
→ Explanation
→ Question
→ Evidence Demand
→ Deeper Understanding
→ Commercial Insight
→ Opportunity
→ Judgement
→ Action
→ Outcome
→ Learning
```

Flora must support direct commercial entry points, but commercial action remains traceable to enterprise understanding.

## 6. Reasoning modes

Flora exposes four user-facing reasoning modes over the same governed object and model state.

### Explore
**Question:** What is happening and what is connected?

Supports industry and enterprise exploration, participant comparison, mechanisms, pressures, transformations, relationships, evidence, Unknowns and Contradictions.

### Explain
**Question:** Why do we believe this?

Supports evidence lineage, Observation history, supporting and contradictory reasoning, confidence, freshness, alternative hypotheses and causal mechanism explanation.

### Anticipate
**Question:** What may happen next?

Supports time-bound hypotheses, transformation inevitability, behaviour-informed expectations, future-state possibilities, leading indicators and signposts that strengthen or weaken the view.

### Act
**Question:** What should I do?

Supports Opportunity Outlook, Commercial Opportunity, Provider Fit, accessibility, Commercial Conviction, relevant Provider Offers, offer gaps, validation, executive conversation and pursuit action.

These modes are product perspectives, not separate data models.

## 7. Object-first interaction

Flora allows users to focus on governed objects and inspect them through contextual views.

Candidate focus objects include Enterprise, Industry, Market Participant, Executive, Supplier, Technology Platform, Regulation, Pressure, Transformation, Mechanism, Evidence, Observation, Signal, Hypothesis, Thesis, Unknown, Contradiction, Question, Commercial Opportunity, Provider Capability, Provider Offer and Recommendation.

The definitive canonical status of each object remains owned by the relevant architecture paper or Accepted ADR.

## 8. Universal object actions

Where applicable, every focused object should expose:

- What changed?
- Why do we believe this?
- What contradicts it?
- What remains Unknown?
- What is connected?
- Compare
- Ask this object
- Watch
- Show evidence
- Show opportunities
- Next best exploration

The product should favour consistent actions over bespoke pages.

## 9. Workspace architecture

The central product surface is the **Enterprise Intelligence Workspace**.

### Focus header
Shows the current object, type, status, confidence, freshness and watch state.

### Intelligence canvas
Renders the selected view: executive thesis, operating-system map, mechanism map, transformation landscape, timeline, comparison, relationship network, evidence, opportunity landscape or anticipated future state.

### Context panel
Shows material recent change, related objects, Unknowns, Contradictions, open Questions, evidence demands, lineage, confidence and candidate next explorations.

### Flora reasoning panel
Supports prompts such as:

- Ask this enterprise.
- Explain this mechanism.
- Challenge this hypothesis.
- Compare these participants.
- Find missing evidence.
- Show opportunities.
- What would change this Recommendation?

A material answer should expose:

```text
Answer
Why it matters
Reasoning path
Evidence
Contradictory evidence
Unknowns
What changed
Next exploration
Recommended action
```

## 10. Navigation

Permanent navigation should remain small:

```text
Home
Search
Workspace
Watchlist
Opportunities
Actions
Memory
```

Industry, Enterprise and Participant are object types, not mandatory fixed navigation silos.

### Home
Prioritises continue exploring, what changed, what deserves attention, opportunity movement, open Questions and validation actions.

### Search
Supports governed object discovery and contextual questions.

### Watchlist
May contain any object with a refresh or attention need.

### Opportunities
Provides a direct commercial view over governed Enterprise Intelligence.

### Actions
Includes validation, evidence collection, executive conversation, positioning, partnering, pursuit, monitoring and learning.

### Memory
Shows how Enterprise Models, Observations, hypotheses, conviction and Recommendations changed through time.

## 11. “What changed?” capability

“What changed?” is a canonical user experience over temporal model state.

It must distinguish:

1. External change — something changed in the enterprise or environment.
2. Knowledge change — CIOS learned something new.
3. Reasoning change — a Signal, Hypothesis, Thesis or Recommendation strengthened, weakened, split or retired.
4. Commercial change — timing, accessibility, Provider Fit, intervention boundary or conviction changed.
5. Model correction — previous understanding was contradicted, superseded or corrected.

It must not degrade into a recent-document feed.

## 12. Exploration Trails

An Exploration Trail is a product-level representation of a purposeful path through governed intelligence.

Example:

```text
UK Banking
→ APP Fraud
→ Reimbursement Pressure
→ Fraud Operations Transformation
→ Lloyds
→ Incumbent Supplier
→ Accessibility Unknown
→ Commercial Opportunity
```

A trail should preserve starting intent, visited objects, comparisons, filters, evidence inspected, Unknowns and Contradictions discovered, hypotheses affected, opportunities revealed, conclusions, actions and learning.

**Architectural boundary:** this document does not decide whether an Exploration Trail is canonical Enterprise Knowledge, durable user workspace state or reconstructable event history. That requires an ADR.

## 13. Questions and curiosity

Flora should surface and manage durable enterprise Questions.

Questions should connect to a target object, Unknown, Observation Demand, Hypothesis, Commercial Opportunity, required evidence, owner, priority, status and answer lineage.

**Architectural boundary:** EI-012 already anticipates EI-015 Enterprise Question Model and EI-016 Enterprise Curiosity Engine. Flora must not create a competing Question model.

## 14. Industry and enterprise exploration

### Industry
Supports industry thesis and boundary, facts and figures, mechanisms, forces and pressures, participants, infrastructure, regulation, transformations, comparative behaviour, anticipated future states, Unknowns, Contradictions and opportunity themes.

### Enterprise
Supports identity and boundary, enterprise thesis, governance, economics, operating model, business units, executives, technology, suppliers, behaviour, transformation portfolio, future-state hypotheses, Opportunity Outlook and evidence demands.

### Market Participant
Supports industry role, business model, strengths, weaknesses, mechanisms demonstrated, trajectory, dependencies, control points and commercial relevance.

## 15. Mechanism experience

A Mechanism view should show canonical identity, causal sequence, scope, supporting Observations, enterprise applicability, participant variants, confidence, contradictions, expected consequences, commercial implications and evidence demands.

This blueprint consumes the owning Mechanism architecture and governed repository semantics.

## 16. Future-state experience

The former “Future Blueprint” concept should be presented as one or more **anticipated future states** or **scenario views**.

Each view must show current state, mechanism and pressure, inferred transition, expected consequence, signposts, inhibitors, confidence, alternatives and evidence that would strengthen or weaken the view.

A future-state view is reasoning, not an unqualified fact.

## 17. Opportunity experience

### Opportunity Radar
Answers: **Where may commercially valuable action be forming?**

### Opportunity Portfolio
Answers: **Where should attention be allocated?**

It must preserve separate judgements for Enterprise Need, Commercial Domain Relevance, Commercial Intervention Boundary, Addressable Value, Provider Fit, Commercial Accessibility, route-to-market, timing, evidence strength, Commercial Conviction, main Unknown and next action.

No opaque combined opportunity percentage should replace these dimensions.

### Opportunity Workspace
Answers: **How should this opportunity be understood and progressed?**

It should include opportunity thesis, enterprise need, why now, intervention boundary, economics, buyers, stakeholders, suppliers, incumbents, Provider Fit, accessibility, offers, offer gaps, Unknowns, Contradictions, lineage, validation plan and next action.

## 18. Horizons and action vocabulary

- Horizon 1 — Operate: current or near-term actionable needs.
- Horizon 2 — Transform: material enterprise change requiring positioning, shaping or offer alignment.
- Horizon 3 — Reinvent: emerging future models and strategic offer creation.

Horizon expresses timing and maturity, not value.

Recommended action vocabulary:

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

## 19. Provider and offer insight

Flora must keep separate:

- Provider Capability — what the provider can do.
- Provider Offer — how capabilities are packaged.
- Provider Fit — whether the offer fits this need and context.
- Commercial Accessibility — whether there is a credible route to participate.
- Commercial Conviction — whether the opportunity is worth progressing.

Repeated need patterns should reveal relevant capabilities, existing offers, partial fits, offer gaps, proof needs, partner dependencies, target enterprises, maturity and recommended offer action.

## 20. Explainability contract

Every material insight, opportunity and Recommendation should provide an **Explain why** control.

```text
Source
→ Evidence
→ Observation
→ Pattern / Signal
→ Hypothesis
→ Thesis
→ Commercial Conviction
→ Recommendation
```

The view must also expose contradictory evidence, Unknowns, human-supplied knowledge, confidence, freshness, assumptions, alternatives and review conditions.

## 21. First reference journey

```text
Flora Home
→ What changed in UK Banking?
→ Explore APP Fraud
→ Inspect the reimbursement and friction mechanism
→ Show enterprises materially affected
→ Open Lloyds
→ Explain the operating-model implications
→ Inspect open Questions and evidence demands
→ Reveal candidate commercial opportunities
→ Open AI-Controlled Financial Crime Operations
→ Inspect Need, Fit, Accessibility and Conviction
→ Create a validation action
```

UK Banking and Lloyds are reference content only; the architecture remains domain-neutral.

## 22. First implementation slice

1. Flora Home attention view.
2. Enterprise Intelligence Workspace shell.
3. Universal object actions.
4. Enterprise Canvas for Lloyds.
5. “What changed?” view.
6. Evidence, Unknown and Contradiction panel.
7. Opportunity Radar.
8. Opportunity Workspace.
9. Question / Evidence Demand interaction using the accepted owning model.
10. Creation of one governed validation action.

## 23. Explicit non-goals

The first iteration must not attempt to build a generic graph visualiser, replacement CRM, large dashboard catalogue, unrestricted report generator, automated opportunity score, ontology editor, duplicate exploration/sales stores, unsupported prediction, Banking-specific core architecture or dozens of bespoke object screens.

## 24. Acceptance criteria

The first implementation allows Rob to:

1. open UK Banking and understand material pressures and mechanisms;
2. move into Lloyds without losing context;
3. see what changed since the previous view;
4. inspect evidence behind a material claim;
5. see Unknowns and Contradictions beside the claim;
6. ask a contextual enterprise Question;
7. follow a recommended next exploration;
8. discover a candidate opportunity from the reasoning;
9. understand why Flora believes the opportunity exists;
10. distinguish Need, Fit, Accessibility and Conviction;
11. identify an existing offer, partial fit or offer gap;
12. create a specific validation or executive action;
13. return later and resume the investigation with memory intact.

## 25. Required architectural decisions

1. Flora as a contextual Enterprise Intelligence Workspace.
2. Object-first interaction and universal object actions.
3. Storage and governance boundary for Exploration Trails.
4. Runtime consumption of EI-015 Question Model and EI-016 Curiosity Engine.
5. Canonical model-delta semantics behind “What changed?”
6. Separation of Need, Provider Fit, Accessibility and Commercial Conviction.
7. Explainability contract for material Recommendations.
8. Status of anticipated future states and scenario views.
9. Boundary between governed intelligence, workspace state and presentation state.

## 26. Completion

This blueprint is complete when architecture reconciliation is accepted, conflicts and open decisions are registered, required ADRs are accepted, the first UX journey is specified and a Codex mission is derived without redefining canonical architecture.
