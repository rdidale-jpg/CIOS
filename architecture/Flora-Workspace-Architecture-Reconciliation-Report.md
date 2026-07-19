# Flora Enterprise Intelligence Workspace — Architecture Reconciliation Report

**Status:** Proposed review  
**Date:** 2026-07-19  
**Scope:** Reconcile `FP-0XX — Flora Enterprise Intelligence Workspace Product Architecture` against current CIOS architecture and identify decisions required before implementation.

## 1. Executive conclusion

The proposed Flora direction is strongly aligned with CIOS doctrine provided it remains:

- a presentation and interaction architecture over governed Enterprise Intelligence;
- object-first without inventing duplicate canonical objects;
- Observation-led;
- model-delta aware;
- explicit about Unknowns, Contradictions and human knowledge;
- separate in its treatment of enterprise need, Provider Fit, accessibility and conviction;
- domain-neutral despite using UK Banking and Lloyds as the first reference implementation.

The design should proceed.

Implementation should not begin from the blueprint alone. Exploration Trail persistence, model-delta semantics, future-state representation and the boundary between workspace state and canonical Enterprise Knowledge require decisions.

## 2. Authority order used

1. Explicit owner direction.
2. Accepted ADRs.
3. CIOS Reference Architecture and owning architecture papers.
4. CIOS Design Doctrine and Architecture Principles.
5. CIOS Chief Architect Handbook.
6. Derived product and implementation documents.

## 3. Reconciliation register

| Proposed concept | Finding | Decision |
|---|---|---|
| Flora as Enterprise Intelligence Workspace | Aligned with Flora consuming governed intelligence and presentation semantics | Proceed; ADR recommended |
| One governed model, many views | Strongly aligned with Reports are views | Preserve as mandatory |
| Object-first interaction | Aligned with governed nodes, relationships and stable identifiers | ADR required for runtime contract |
| Explore / Explain / Anticipate / Act | Compatible with Observation-to-Recommendation chain | Treat as UI perspectives |
| What changed? | Strongly aligned with Observation lifecycle and model updates | Define canonical model-delta contract |
| Question object | EI-012 already anticipates EI-015 Enterprise Question Model | Do not create competing model |
| Curiosity / next exploration | EI-012 anticipates EI-016 Curiosity Engine and Observation Demand | EI-016 owns reasoning semantics |
| Exploration Trail | No clear owner identified | ADR required |
| Mechanism explorer | Aligned, but recent Banking work proves identifier drift risk | Use canonical IDs and preserve variants |
| Future Blueprint | Too static as a term | Use anticipated future state or scenario |
| Opportunity Radar | Aligned with Opportunity Outlook and Commercial Conviction | Keep as view over governed reasoning |
| Need / Fit / Accessibility / Conviction | Strongly aligned and explicitly required | Mandatory separation |
| Provider Offer matching | Aligned subject to owning Provider model | Do not infer Fit from public need |
| Explain why | Strongly aligned with graph and hypothesis lineage | Mandatory runtime contract |
| Banking / Lloyds first slice | Aligned if domain-neutral | Proceed |
| Home attention feed | Compatible with Observation Demand and change | Drive from model change, not document recency |
| Memory view | Aligned with lifecycle and supersession | Render durable state history |
| Market Participant | Aligned with role-based graph semantics | Avoid assuming every participant is competitor |
| Contextual chat | Conditional | Ground in focused object and lineage |
| Opportunity horizons | Conditional | Timing/maturity only, not value score |

## 4. Key corrections

### 4.1 Question is not a new invention
EI-012 already anticipates EI-015 Enterprise Question Model, EI-016 Enterprise Curiosity Engine, Observation Demand and Observation Question Generation. The Product Blueprint defines the experience but not a competing schema.

### 4.2 Exploration and Sales are perspectives
The Researcher’s Exploration UI and Sales Opportunity UI remain useful outcomes, but they must read from the same governed objects and reasoning state.

### 4.3 Future Blueprint is not a fact
Future-state content must preserve hypothesis status, confidence, inhibitors, alternatives, evidence demands and strengthening/weakening signposts.

### 4.4 What changed? must represent model change
The runtime must distinguish external change, new knowledge, reasoning change, commercial change and model correction.

### 4.5 Mechanism identity must remain canonical
Flora must display canonical mechanism identity, preserve local variants, distinguish applicability from confidence and prevent UI labels from redefining architecture.

## 5. Conflicts to prevent

1. UI-local truth becoming canonical knowledge.
2. Generated reports becoming durable memory.
3. Flora creating a Question schema before EI-015.
4. Need, Provider Fit, accessibility and conviction becoming one score.
5. Future hypotheses being presented as facts.
6. Banking assumptions leaking into core architecture.
7. Mechanism labels drifting from canonical meaning.
8. Public enterprise need being treated as proof of accessibility or Provider Fit.

No direct doctrinal conflict was identified.

## 6. Architectural decision register

### ADR A — Flora as Enterprise Intelligence Workspace
Confirm Flora as contextual reasoning and presentation over governed Enterprise Intelligence, not a separate knowledge store or CRM.  
**Recommendation:** Accept.

### ADR B — Object-first runtime interaction
Confirm runtime focus, navigation and interaction operate on governed object identity and relationships rather than page-specific models.  
**Recommendation:** Accept.

### ADR C — Exploration Trail persistence
Choose between governed knowledge, user workspace state, reconstructable event history or a combination with promotion rules.  
**Recommendation:** User-owned workspace state backed by append-only event history; promote conclusions, Questions and actions explicitly.

### ADR D — Model-delta contract
Define how CIOS records and exposes changes to Observations, Enterprise Model attributes, hypotheses, conviction and Recommendations.  
**Recommendation:** Required before full What changed? implementation.

### ADR E — Question and Curiosity integration
Confirm Flora consumes EI-015 and EI-016 rather than owning parallel models.  
**Recommendation:** Accept.

### ADR F — Commercial judgement separation
Confirm Need, intervention boundary, Provider Fit, accessibility, timing, evidence strength and Commercial Conviction remain separately visible.  
**Recommendation:** Accept as mandatory.

### ADR G — Explainability contract
Define minimum lineage exposed for material claims, opportunities and Recommendations.  
**Recommendation:** Accept.

### ADR H — Future-state representation
Decide whether anticipated future states are persisted hypotheses/scenarios, derived projections or both.  
**Recommendation:** Persist governed hypotheses and scenarios; render future-state views as projections.

## 7. Product / architecture boundary

### Product Architecture Blueprint owns
User outcomes, interaction modes, workspace behaviour, navigation principles, universal object actions, product acceptance criteria and reference journey.

### Owning architecture / ADRs own
Canonical object identity, lifecycle semantics, relationships, evidence and Observation rules, hypothesis validation, model-delta contract, persistence boundary, runtime authority and promotion into governed knowledge.

### UX specifications own
Layouts, controls, responsive behaviour, hierarchy, interaction states, empty states and error states.

### Codex missions own
Implementation scope, repositories, components, APIs, migrations, tests, validation, commit, PR and completion report.

## 8. First implementation decision envelope

### Supported now
Workspace shell, object focus, UK Banking/Lloyds journey, evidence and uncertainty visibility, separate commercial judgement panels, contextual Flora Ask, Watchlist and validation action creation.

### Supported with temporary boundaries
Questions through an EI-015-compatible interface, Curiosity through transparent heuristics, What changed? limited to reliably reconstructable history, and Exploration Trails as user workspace state.

### Not supported before decisions
Autonomous promotion into canonical knowledge, opaque prediction, full persistent future-state model, one-score opportunity ranking, Provider Fit inferred from public evidence, CRM replacement and uncontrolled cross-domain mechanism creation.

## 9. Required next outputs

1. Accept or amend the Product Architecture Blueprint.
2. Draft and accept the minimum ADR set.
3. Draft EI-015 and EI-016 ownership stubs or confirm their sequence.
4. Produce the first UX Journey Specification.
5. Produce one implementation-ready Codex mission.

## 10. Chief Architect recommendation

Proceed with Flora vNext.

Do not send the blueprint directly to Codex.

The completion path is:

```text
Product Architecture Blueprint
→ Architecture Reconciliation
→ Accepted ADRs
→ UX Journey Specification
→ Codex Mission
→ Implementation
→ Validation
→ Learning
```
