# FP-009 — Hypothesis Validation Standard

**Purpose:** Define how Flora creates, strengthens, weakens and retires commercial hypotheses.
**Status:** Draft
**Owner:** Rob / CIOS
**Last updated:** 2026-07-02

## Relationship to the CIOS Intelligence Reference Model

The CIOS Intelligence Reference Model (CIRM) defines how CIOS converts observable enterprise reality into strategic commercial judgement. Its canonical pipeline is:

```text
Observable Enterprise Reality
→ Governed Source Collection
→ Raw Evidence
→ Evidence Quality Assessment
→ Strategic Signals
→ Commercial Insights
→ Transformation Themes
→ Transformation Theses
→ Hypothesis Validation
→ Commercial Conviction
→ Executive Recommendations
→ Commercial Outcomes
→ Continuous Learning
```

FP-009 governs Hypothesis Validation: the testing discipline between Transformation Theses and Commercial Conviction.

## Transformation Pressure and Transformation Inevitability

**Transformation Pressure** is the internal and external forces that make change more likely or necessary. Internal pressure may include legacy technology, operating cost, service quality, cyber exposure, workforce constraints, fragmented data, delivery failure and technical debt. External pressure may include regulation, political direction, customer expectations, market disruption, competitive moves, supplier change, economic pressure and technology shifts.

**Transformation Inevitability** is the degree to which an enterprise appears structurally compelled to transform, regardless of whether procurement, budget or sponsor evidence is visible. Transformation inevitability is not the same as commercial opportunity: an enterprise may need to transform but still be inaccessible, already committed to another provider, internally constrained or commercially unattractive.

## Commercial Reasoning Loop

```text
Observe
→ Interpret
→ Challenge
→ Hypothesise
→ Test
→ Convict
→ Recommend
→ Learn
→ Observe
```

This loop describes Newton's desired behaviour. Flora should not only collect evidence and generate outputs; it should continually challenge, validate and improve its commercial judgement.

## Inspectable Reasoning Lineage

No recommendation may exist unless its reasoning chain can be inspected:

```text
Executive Recommendation
→ Commercial Conviction
→ Hypothesis / Transformation Thesis
→ Commercial Insight
→ Strategic Signal
→ Raw Evidence
→ Source
```

If any link is missing, the recommendation should be downgraded to a learning action or evidence demand.

## 1. Purpose

This paper defines the Hypothesis Validation Standard for CIOS. Flora should treat commercial hypotheses as scientific reasoning objects: created to be tested, challenged, strengthened, weakened, rejected or retired.

Hypotheses are not conclusions waiting for evidence. They are structured propositions about enterprise transformation that organise evidence demand and guide learning.

```text
Strategic Signals
→ Hypothesis
→ Validation Questions
→ Evidence Demand
→ Strengthen / Weaken / Reject / Retire
```

A hypothesis should never exist merely to confirm a preferred commercial narrative. It should make clear what would support it, what would contradict it and what remains unknown.

## 2. Why Hypotheses Exist

Strategic Signals identify why observed facts may matter. Hypotheses connect multiple signals into a testable proposition about what may be happening inside an enterprise and why it may be commercially relevant.

Hypotheses help Flora:

- organise signals into coherent transformation reasoning;
- identify the evidence needed next;
- avoid premature recommendations;
- compare competing explanations;
- expose uncertainty before executive action;
- preserve scientific discipline in commercial judgement.

A good hypothesis is useful even when it is rejected, because rejection improves CIOS by removing weak narratives and refining evidence demand.

## 3. Hypothesis Anatomy

Every commercial hypothesis should include the following elements.

### Statement

A clear, testable proposition about the enterprise transformation pattern that may be forming.

### Supporting Signals

The Strategic Signals that make the hypothesis plausible.

### Supporting Evidence

The evidence records that support the underlying signals and hypothesis.

### Contradictory Evidence

Evidence that challenges, complicates or weakens the hypothesis.

### Unknowns

Material questions that must be answered before the hypothesis can support stronger commercial action.

### Commercial Relevance

Why the hypothesis matters commercially if it is true.

### Executive Audience

The executive stakeholders who may care about the hypothesis, such as CIO, COO, CFO, Chief Digital Officer, Chief Customer Officer, Chief Risk Officer or sector-specific leaders.

### Transformation Theme

The broader transformation theme represented by the hypothesis, such as AI-enabled service redesign, cloud modernisation, operating-model change, data governance, resilience, cost transformation or regulatory response.

### Confidence

The quality and reliability of evidence supporting the hypothesis.

### Conviction

The judgement about whether the hypothesis is sufficiently supported to justify commercial action or executive engagement.

### Validation Questions

The specific questions Flora should answer to strengthen, weaken or reject the hypothesis.

Examples include:

- Is there named executive ownership?
- Is there budget, investment or cost pressure?
- Is there procurement movement or route-to-market evidence?
- Are suppliers already appointed?
- Are there delivery milestones or failures?
- Has contradictory evidence appeared?

## 4. Hypothesis Lifecycle

Commercial hypotheses should move through explicit lifecycle states.

### Created

The hypothesis has been formed from one or more signals and requires validation.

### Emerging

Early evidence supports the hypothesis, but coverage and corroboration are incomplete.

### Strengthening

New evidence, stronger corroboration, reduced contradiction or executive confirmation increases confidence and conviction.

### Validated

The hypothesis is sufficiently supported for the intended decision context. Validation is not proof; it means the hypothesis has enough evidence to guide action with visible assumptions and unknowns.

### Weakening

Contradictions appear, evidence ages, expected corroboration fails to emerge or enterprise conditions change.

### Rejected

Evidence materially disproves the hypothesis or makes the explanation commercially unreliable.

### Retired

The hypothesis is no longer active because it has been superseded, completed, rejected, made irrelevant or absorbed into a broader thesis.

## 5. Validation Rules

Hypotheses strengthen when:

- independent evidence increases;
- coverage improves;
- contradictions reduce;
- executive confirmation is obtained;
- budget evidence appears;
- procurement evidence appears.

Hypotheses weaken when:

- contradictions emerge;
- expected evidence fails to appear;
- leadership changes;
- strategy changes;
- evidence ages.

Validation should be proportional to the decision being supported. A hypothesis used to guide research may require less evidence than a hypothesis used to justify executive engagement or investment.

## 6. Falsification

Flora should actively search for evidence that disproves a hypothesis.

Falsification is essential because commercial narratives are easy to construct after the fact. If Flora only searches for confirming evidence, it will produce confident stories rather than reliable judgement.

Failure to falsify is not proof. It only increases confidence when the search for disconfirming evidence was credible, targeted and current.

A hypothesis should therefore include explicit falsification prompts, such as:

- What evidence would show that the transformation is not a priority?
- What evidence would show that budget is unavailable?
- What evidence would show that another supplier already owns the route?
- What evidence would show that leadership has changed direction?
- What evidence would show that the problem has already been solved?

## 7. Hypothesis Competition

Multiple competing hypotheses may exist simultaneously. Flora should compare them rather than prematurely selecting one.

For example, the same evidence could support different interpretations:

- an enterprise is investing because of growth ambition;
- an enterprise is investing because of cost pressure;
- an enterprise is investing because of regulatory obligation;
- an enterprise is investing because legacy technology is constraining delivery.

Competing hypotheses should be assessed against the same evidence base, unknowns and contradictions. Flora should prefer the explanation with stronger coverage and fewer unresolved contradictions, but should keep alternatives visible while evidence remains incomplete.

## 8. Recommendation Relationship

Recommendations should reference hypotheses, not raw evidence.

Raw evidence is too granular to justify action by itself. Recommendations should be grounded in validated or sufficiently strong hypotheses that preserve their supporting signals, evidence, contradictions and unknowns.

```text
Raw Evidence
→ Strategic Signals
→ Hypotheses
→ Commercial Conviction
→ Executive Recommendations
```

This relationship keeps recommendations explainable. A senior user should be able to inspect the hypothesis behind a recommendation and see why Flora believes the action is justified.

## 9. Future Learning

Future versions of Flora should learn from:

- won pursuits;
- lost pursuits;
- executive feedback;
- commercial outcomes.

Learning should improve hypothesis formation and validation without erasing provenance. CIOS should learn which evidence patterns were predictive, which contradictions mattered, which unknowns caused failure and which hypotheses led to valuable action.

Learning should also preserve humility. A won pursuit does not prove every supporting hypothesis was correct. A lost pursuit does not prove the hypothesis was wrong. Outcomes should calibrate judgement, not overwrite the scientific record.

## 10. Open Questions

- What evidence threshold should move a hypothesis from Strengthening to Validated?
- How should Flora represent hypotheses that are commercially important but ethically unsuitable?
- How should competing hypotheses be visualised for executive users?
- When should a rejected hypothesis remain visible for institutional learning?
- How should commercial outcomes recalibrate hypothesis validation rules?
- What human review should be required before a hypothesis supports a recommendation?

## Relationship to CIRM

This paper governs the hypothesis validation stage of CIRM. It defines how Flora creates, tests, strengthens, weakens, rejects and retires hypotheses using signals from [FP-007](FP-007-Strategic-Signal-Standard.md) and feeding conviction decisions in [FP-008](FP-008-Commercial-Conviction-Model.md).
