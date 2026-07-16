# EI-015 — Enterprise Intelligence Pattern Model

**Document class:** Enterprise Intelligence model
**Status:** Review
**Authority:** Proposed Enterprise Intelligence Model
**Owner:** Rob / CIOS
**Last updated:** 2026-07-16
**Production behaviour:** Documentation-only architecture. It does not introduce runtime behaviour, alter canonical model semantics, change production Researcher packs or Assurance packs, or promote any architecture.
**Release-profile membership:** none — excluded from production Researcher, Assurance and Reviewer profiles

## 1. Mission and purpose

EI-015 documents the emerging concept of **Enterprise Intelligence Patterns** as a candidate architectural capability derived from validation across multiple Enterprise Twins. It records the current evidence, governance model, lifecycle and open questions so that the concept can be tested through further Enterprise Twins.

This is a Review model. It does **not** promote Enterprise Intelligence Patterns to Accepted architecture, make patterns production authority, or change the responsibilities of existing Enterprise Intelligence papers.

The model emerged from comparative work across **MOD**, **VodafoneThree** and **National Grid**. That evidence is useful but not universal proof; the model remains subject to validation through additional enterprises.

## 2. Architectural position

The proposed hierarchy is:

```text
Evidence
  ↓
Observation
  ↓
Enterprise Mechanism
  ↓
Enterprise Intelligence Pattern
  ↓
Enterprise Twin
  ↓
Opportunity Twin
  ↓
Industry Twin
```

| Object | Meaning and boundary |
| --- | --- |
| **Evidence** | Attributable source material that supports, challenges or contextualises a claim. Evidence is not itself intelligence or a Pattern. |
| **Observation** | An evidence-backed, governed intelligence atom that records an interpretable change, condition or relationship. EI-012 continues to own Observation semantics and lifecycle. |
| **Enterprise Mechanism** | A causal structure explaining how change propagates within one enterprise. A mechanism belongs to one Enterprise Twin and remains accountable to that Twin's evidence, confidence, freshness, Unknowns and Contradictions. |
| **Enterprise Intelligence Pattern** | A reusable, evidence-governed reasoning asset observed by comparing analogous mechanisms across multiple Enterprise Twins. It describes a recurring causal configuration, its conditions and its limits; it is not a universal law. |
| **Enterprise Twin** | The governed, enterprise-specific durable memory in which evidence, Observations, mechanisms, state and uncertainty remain attributable to that enterprise. Patterns may inform reasoning, but do not overwrite enterprise-specific evidence. |
| **Opportunity Twin** | The governed model of a selected commercial opportunity. It consumes enterprise-specific context and may use a Pattern as a testable reasoning input; it is not a Pattern and does not validate one by itself. |
| **Industry Twin** | The governed industry-level Twin. It may later compare and contextualise Pattern candidates across an industry, subject to its own lifecycle and target-owner acceptance; this model does not make direct Pattern consumption a requirement. |

The arrows describe a proposed reasoning relationship, not automatic promotion, inheritance or data mutation. Each downstream object retains its own owner, acceptance boundary and evidence lineage.

## 3. Mechanisms and Patterns

### 3.1 Enterprise Mechanism

An **Enterprise Mechanism** is a causal structure explaining how change propagates within a single enterprise. It connects evidence-backed conditions, actors, constraints, dependencies and effects in the context of that enterprise.

Examples include:

- **Connections Queue Governance**;
- **Regulated Investability Corridor**;
- **Enterprise Integration Control**.

Mechanisms belong to one Enterprise Twin. They must retain their originating evidence and Observations, enterprise context, confidence, freshness, Unknowns, Contradictions and falsification conditions. A mechanism can be useful and strongly evidenced without becoming a Pattern.

### 3.2 Enterprise Intelligence Pattern

An **Enterprise Intelligence Pattern** is a reusable reasoning asset that has been observed across multiple Enterprise Twins. It emerges from structured comparison of mechanisms, including the similarities, contextual differences, contradictions and counterexamples found in that comparison.

Patterns are **never inferred from a single enterprise alone**. Repeated language, a familiar procurement category or an analyst's intuition is not sufficient. A candidate Pattern must preserve links back to the enterprise-specific mechanisms and evidence from which it emerged.

### 3.3 What Patterns are not

Patterns are not:

- opportunities, procurements, sales plays, recommendations or commercial outcomes;
- a replacement for enterprise-specific evidence, Observations, mechanisms, Unknowns or Contradictions;
- a substitute for an Opportunity Twin or a claim that an opportunity exists;
- **Solution Patterns**, reusable solution, delivery, product or capability designs. Solution Patterns answer how a provider might respond; Enterprise Intelligence Patterns explain a recurring enterprise causal configuration and remain provider-neutral;
- universal laws, accepted architecture, runtime rules, scoring rules or automatic classification; or
- authority to mutate an Enterprise Twin, Opportunity Twin or Industry Twin without that target object's own governed acceptance.

## 4. Pattern emergence and use

A Pattern emerges only through a controlled comparison:

1. build or update each Enterprise Twin with attributable Evidence and governed Observations;
2. identify an enterprise-specific Mechanism and record its causal structure, boundary conditions and uncertainty;
3. compare mechanisms from materially distinct Enterprise Twins;
4. formulate a Pattern candidate that states the common causal configuration, its reuse scope, confidence and falsification conditions;
5. actively seek contradictory evidence and counterexamples; and
6. retain the lineage to every contributing enterprise rather than collapsing it into a generic claim.

A Pattern can support Opportunity Discovery by suggesting **questions, hypotheses and evidence demands** when an Enterprise Twin exhibits analogous conditions. It must not create, rank or recommend an opportunity without enterprise-specific EOD-001 reasoning and evidence. EOD-001 continues to own opportunity discovery; EI-015 contributes only a bounded, testable reasoning input.

A Pattern can support Industry Intelligence by providing a candidate comparative lens for industry structure, regulation, investment or operating change. Industry Twin lifecycle, monitoring, release and target-owner acceptance remain owned elsewhere. No direct Pattern-to-Industry-Twin runtime consumption is introduced by this paper.

## 5. Proposed lifecycle

```text
Candidate
  ↓
Observed
  ↓
Strengthening
  ↓
Cross-enterprise Validated
  ↓
Accepted
  ↓
Deprecated
  ↓
Retired
```

| Transition | Evidence required |
| --- | --- |
| **Candidate → Observed** | A documented Mechanism in one Enterprise Twin, full evidence lineage, explicit confidence/freshness, proposed reuse scope and falsification conditions. The state records an observation of possible recurrence; it does not validate a Pattern. |
| **Observed → Strengthening** | Comparable mechanisms in at least one additional, materially distinct Enterprise Twin; a documented comparison; and an explicit account of similarities, differences, Unknowns and contradictory evidence. |
| **Strengthening → Cross-enterprise Validated** | Repeated corroboration across multiple Enterprise Twins, including cross-sector or otherwise materially different contexts where applicable; stable or explicitly bounded causal logic; reviewed counterexamples; and evidence that the Pattern improves bounded reasoning without displacing enterprise-specific evidence. |
| **Cross-enterprise Validated → Accepted** | A separate architecture-governance decision after the validation threshold is met. Review status does not self-promote, and this document makes no such decision. |
| **Accepted → Deprecated** | A governance decision that a still-useful Pattern has been superseded, narrowed or replaced, with its successor and retained lineage recorded. |
| **Deprecated → Retired** | Recorded evidence that the Pattern is no longer reliable or useful within its stated scope, or is conclusively superseded. Its history, counterexamples and rejection learning remain available. |

Contradiction is not a failure to hide. It may narrow a Pattern's scope, reduce confidence, return it to an earlier lifecycle state or justify deprecation/retirement. Rejected Pattern candidates remain part of organisational learning.

## 6. Pattern governance

Every Pattern record must include:

| Required field | Governance purpose |
| --- | --- |
| Pattern ID | Stable identity for comparison, review and lineage. |
| Definition | Bounded statement of the recurring causal configuration. |
| Originating Enterprise | The Enterprise Twin in which the first contributing Mechanism was documented. |
| Validated Enterprises | Enterprises that contribute comparable mechanism evidence; this must never be a one-enterprise list for validation. |
| Evidence Lineage | Links to contributing Evidence, Observations, mechanisms, comparison records and review decisions. |
| Confidence | Current confidence with rationale, not an unsupported label. |
| Freshness | Currency of supporting evidence and next review date. |
| Reuse Scope | Conditions, enterprise types and decision contexts in which the Pattern may be used as a reasoning aid. |
| Falsification Conditions | Observable conditions that would challenge, narrow or invalidate the Pattern. |
| Counterexamples | Known non-conforming enterprises, mechanisms or outcomes, including why they differ where known. |
| Lifecycle State | Candidate, Observed, Strengthening, Cross-enterprise Validated, Accepted, Deprecated or Retired. |
| Review Trigger | Events, evidence age, counterexamples, commercial outcomes or cadence that require reassessment. |

Validation rules are therefore explicit:

- one enterprise cannot validate a Pattern;
- comparison must preserve enterprise-specific evidence rather than generalising away context;
- contradiction strengthens governance by making scope and limits inspectable;
- rejected patterns remain part of organisational learning; and
- Patterns remain evidence-governed assets throughout their lifecycle.

## 7. Relationship to existing architecture

EI-015 cross-references existing authorities and does not duplicate their responsibilities.

| Authority | EI-015 relationship |
| --- | --- |
| EIF-001 | EIF-001 builds the initial Enterprise Twin and may surface enterprise-specific mechanisms. EI-015 does not perform Foundation work or alter its method. |
| EOD-001 | EOD-001 owns Enterprise Opportunity Discovery. Patterns may supply bounded hypotheses and evidence demands, never opportunity assertions or prioritisation. |
| OT-001 | OT-001 owns the Review Opportunity Twin interface. A Pattern can be a traceable reasoning input, not an Opportunity Twin, opportunity claim or substitute for opportunity evidence. |
| EI-014 | EI-014 owns Review solution positioning intelligence after an Opportunity Twin. EI-015 does not create positioning intelligence, Provider Fit, proposals or Solution Patterns. |
| FP-009 | FP-009 continues to own hypothesis validation and learning discipline. Pattern hypotheses, counterexamples and falsification remain subject to FP-009. |

EI-001, EI-002, EI-003 and EI-012 retain ownership of Enterprise Model, graph, behaviour and Observation semantics respectively. This model neither redefines those papers nor changes canonical acceptance boundaries.

## 8. Known Unknowns

The following questions remain open and must remain visible during Review:

1. Should Enterprise Mechanisms become a first-class architectural object?
2. When should Pattern Validation become part of IC-001?
3. Should Industry Twins consume Patterns directly?
4. How should Pattern confidence evolve over time?
5. How should Commercial Outcomes feed Pattern refinement?
6. What constitutes sufficient material difference between enterprises and sectors for cross-enterprise validation?
7. Which governance forum should approve a transition from Cross-enterprise Validated to Accepted?

## 9. Validation roadmap and constraints

Promotion depends on successful validation across:

- **United Utilities**;
- **another commercial enterprise**; and
- **additional cross-sector evidence**.

Validation must test whether the same Pattern definition remains useful only within an explicit scope, whether counterexamples and negative cases are preserved, whether it improves Opportunity Discovery without manufacturing opportunities, and whether it can inform Industry Intelligence without bypassing Industry Twin governance.

This Review document must not:

- promote Patterns to Accepted architecture;
- change runtime behaviour;
- modify Researcher or Assurance packs; or
- redefine existing Enterprise Intelligence papers.

## 10. Review confirmation

EI-015 is documentation-only. It introduces no runtime changes, architecture promotion, production profile membership or changes to Researcher and Assurance packs. Its status remains evidence-based **Review** pending the validation roadmap above.
