# CIOS-ENG-003 – Commercial Intelligence Pipeline Specification

**Version:** 1.0.0  
**Status:** Engineering Baseline  
**Repository target:** `docs/Engineering/`

## 1. Executive Summary

This specification defines the **Commercial Intelligence Pipeline**: the canonical processing lifecycle that transforms raw evidence into explainable recommendations and organisational learning.

The pipeline connects the CIOS core, ontology, graph, reasoning, scoring, decision engine, memory, agents and applications into a single operating model.

## 2. Canonical Lifecycle

```text
Evidence -> Observation -> Signal -> Hypothesis -> Commercial Law -> Reasoning -> Score -> Decision -> Recommendation -> Action -> Outcome -> Learning
```

## 3. Stage Responsibilities

| Stage | Responsibility | Owner |
|---|---|---|
| Evidence | Raw source material, fact, document, note or structured input. | `core.Evidence` |
| Observation | Detected fact or condition extracted from evidence. | `core.Observation` |
| Signal | Interpreted commercial indicator that may change judgement. | `reasoning.Signal` |
| Hypothesis | Possible explanation or commercial interpretation. | `reasoning.Hypothesis` |
| Commercial Law | Commercial Physics principle used to evaluate the hypothesis. | Constitution / future physics module |
| Reasoning | Traceable inference chain linking evidence to conclusion. | `reasoning.ReasoningTrace` |
| Score | Quantified assessment of pressure, risk, maturity or confidence. | `scoring.ScoringResult` |
| Decision | Structured assessment of options against criteria. | `decision_engine.DecisionOutput` |
| Recommendation | Actionable guidance produced for a human decision maker. | `core.Recommendation` |
| Action | Human or system action taken as a result. | applications / future workflows |
| Outcome | Observed result after action. | memory future record |
| Learning | Reusable improvement captured for future decisions. | memory / learning future module |

## 4. Module Interaction Model

```text
core + ontology + graph
        ↓
reasoning
        ↓
scoring
        ↓
decision_engine
        ↓
applications
        ↓
memory / learning feedback
```

## 5. Traceability Rules

- Every recommendation must link to at least one decision or rationale.
- Every decision must link to scores, reasoning or evidence.
- Every score should identify components and optional reasoning trace.
- Every reasoning trace should contain explicit steps and confidence where available.
- Pipeline stages must preserve upstream identifiers.

## 6. Orchestration Boundaries

- The pipeline coordinates modules but does not erase module ownership.
- Memory remains passive; it stores pipeline artefacts but does not decide.
- Agents may assist each stage but must not bypass the decision engine for formal recommendations.
- Applications own end-to-end user workflows.
- Commercial laws are defined in the Constitution before being implemented as code.

## 7. State Model

| State | Meaning |
|---|---|
| Draft | Input has been captured but not interpreted. |
| Observed | Evidence has produced observations. |
| Interpreted | Signals and hypotheses exist. |
| Assessed | Reasoning and scoring have been produced. |
| Decided | Options and rationale have been created. |
| Recommended | Human-readable guidance exists. |
| Actioned | An action has been taken. |
| Learned | Outcome feedback has been persisted. |

## 8. Sprint Implications

- Sprint 7A should harden architecture before memory.
- Sprint 7B should implement passive memory records.
- Sprint 8 should define storage adapter interfaces.
- Sprint 9 should implement a pipeline package or application composition boundary.
- Sprint 10 should implement the first Opportunity Intelligence flow.

## 9. Future Codex Implementation Guardrail

```text
Implement CIOS pipeline only after Sprint 7 memory is complete. Do not implement pipeline orchestration before dependency hardening and passive memory records exist. When implementation begins, create cios/pipeline with typed stage inputs/outputs, no LLM calls, no external services, and tests proving evidence-to-decision traceability.
```

## 10. Decisions

| Decision | Rationale | Status |
|---|---|---|
| Introduce Commercial Intelligence Pipeline | CIOS requires a canonical lifecycle from evidence to learning. | Accepted |
| Do not implement pipeline before memory | Pipeline needs passive persistence contracts before orchestration. | Accepted |
| Keep applications responsible for workflows | Prevents decision engine and memory from becoming monolithic. | Accepted |
