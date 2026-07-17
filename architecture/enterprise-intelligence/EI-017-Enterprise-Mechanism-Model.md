# EI-017 — Enterprise Mechanism Model

**Document class:** Enterprise Intelligence model
**Status:** Review
**Authority:** Proposed Enterprise Intelligence Model
**Owner:** Rob / CIOS
**Last updated:** 2026-07-17
**Production behaviour:** Documentation only. This model introduces no runtime behaviour, implementation schema, automation, inference rule, or change to canonical model semantics.
**Production profile membership:** None — excluded from `architecture-authority`, `researcher-pack`, `assurance-pack`, and `reviewer-pack`.

## 1. Purpose and architectural position

EI-017 defines an **Enterprise Mechanism** as the governed representation of a reusable causal explanation of how enterprise inputs, actors, decisions, dependencies, and constraints combine to produce, protect, or inhibit an enterprise outcome.

A Mechanism explains causation. It is not a Pattern, Theme, Trend, report section, or Recommendation. It does not replace the Enterprise Twin, nor does it make a recommendation or assert that an opportunity exists.

This Review model preserves the existing doctrine:

> Evidence proves change.
> Observations remember change.
> Enterprise Models accumulate change.
> Reports are views.

In particular, **Observation remains the atomic commercial intelligence object**. A Mechanism consumes governed evidence-backed Observations and preserves their lineage; it must not collapse evidence, observations, patterns, signals, hypotheses, mechanisms, and recommendations into one opaque reasoning object.

## 2. Required distinctions

| Object | Purpose | Boundary |
| --- | --- | --- |
| **Evidence** | Source material. | Attributable material that supports, challenges, or contextualises a claim; it is not itself an intelligence conclusion. |
| **Observation** | Atomic evidence-backed statement. | EI-012 owns its semantics, lifecycle, evidence lineage, Unknowns, and Contradictions. |
| **Pattern** | Recurring configuration of Observations. | It describes recurrence across a bounded context; it does not by itself explain why the configuration produces an outcome. EI-015 owns cross-enterprise Pattern governance. |
| **Mechanism** | Causal explanation. | It explains how specified conditions and interactions produce, protect, or inhibit an outcome within a stated scope. |
| **Signal** | Commercial meaning. | It expresses why an evidence-backed condition may matter commercially; it is not a causal proof. |
| **Hypothesis** | Falsifiable interpretation. | It proposes an interpretation to test and remains governed by FP-009; it is not a validated Mechanism. |
| **Recommendation** | Proposed action. | It proposes a course of action and requires inspectable lineage under ADR-005; it is not evidence or causal proof. |

**Patterns describe recurrence. Mechanisms explain causation. Signals express meaning. Hypotheses propose interpretation.** These boundaries are mandatory even where one output references another.

## 3. Canonical intelligence hierarchy

The preferred conceptual lineage model is:

```text
Evidence
    ↓
Observation
    ↓
Observation Network
    ↓
Pattern
    ↓
Mechanism Candidate
    ↓
Validated Mechanism
    ↓
Signal
    ↓
Executive Tension
    ↓
Decision Envelope
    ↓
Opportunity
    ↓
Recommendation
```

This hierarchy is a conceptual lineage model, **not a mandatory runtime pipeline**. It does not require a particular execution order, persistence model, automation, or data schema. A downstream object must retain references to the distinct upstream objects that justify it. Unknowns and Contradictions can arise at every stage and must remain first-class rather than being hidden by a Mechanism conclusion.

## 4. Canonical conceptual object

An Enterprise Mechanism record is a conceptual governance object, not an implementation-specific schema. At minimum it identifies:

| Element | Required meaning |
| --- | --- |
| Identifier and name | Stable identity and a concise, non-marketing name. |
| Description | Bounded causal explanation in plain language. |
| Outcome explained and scope | The outcome, enterprise context, time horizon, and limits of applicability. |
| Inputs, actors, and decisions | Required conditions, participating actors, and relevant choices or governance decisions. |
| Dependencies and constraints | Prerequisites, external/internal dependencies, regulatory, technical, economic, operating, or organisational constraints. |
| Causal sequence | Inspectable account of how the stated elements combine to produce, protect, or inhibit the outcome. |
| Reinforcing and balancing effects | Feedback that amplifies, stabilises, or counteracts the causal sequence. |
| Supporting Observations and supporting Patterns | Distinct references to atomic Observations and, where relevant, bounded recurrence descriptions. |
| Evidence lineage | Traceable evidence supporting or challenging the contributing Observations and causal claims. |
| Contradictions and Unknowns | Contrary evidence, absent information, unresolved assumptions, and their effect on scope or confidence. |
| Confidence, freshness, and maturity | Calibrated confidence with rationale; currency and review need; and lifecycle state. Confidence does not equal truth. |
| Enterprise variants | The enterprise-specific, participant-type, or cross-enterprise form, including what varies and what remains comparable. |
| Executive ownership | Accountable executives, decision owners, or explicitly unknown ownership; this is not an asserted buying contact. |
| Pressure, Executive Tension, and Signal relationships | Explicit, distinct relationships to pressures, tensions, and commercial meaning; none is silently inferred as causation. |
| Falsification conditions | Observable conditions that would challenge, narrow, weaken, or invalidate the explanation. |
| Review history | Review dates, reviewers, decisions, changes in evidence, and retained rejection learning. |

## 5. Causal discipline and assurance

Every Mechanism must identify its outcome explained, required inputs, participating actors, relevant decisions, dependencies, constraints, supporting evidence, competing explanations, falsification conditions, and known limits of applicability.

The following are prohibited:

- presenting correlation as causation;
- presenting supplier marketing as architecture or causal proof;
- asserting unsupported economic claims;
- hiding inference inside a narrative, diagram, score, or label; and
- using human knowledge without the explicit label required by ADR-004.

A Mechanism can be incomplete, disputed, or useful as a candidate. It must say so. Recurrence does not prove causation, and confidence does not equal truth. A causal explanation remains evidence-governed throughout its life.

## 6. Review-stage lifecycle

```text
Candidate → Supported → Validated → Established → Weakened → Contradicted → Retired
```

| State or transition | Evidence and governance requirement |
| --- | --- |
| **Candidate** | States a causal proposition, scope, competing explanations, Unknowns, and falsification conditions; it may be based on limited evidence but cannot be presented as established. |
| **Candidate → Supported** | Evidence-backed Observations, inspectable lineage, a stated causal sequence, and review of plausible competing explanations support the explanation. |
| **Supported → Validated** | Multiple relevant evidence items and Observations, active consideration of contradictory evidence, and testing against stated falsification conditions support the causal account within its scope. |
| **Validated → Established** | Repeated, current corroboration in the stated scope; bounded variants; documented counterexamples; and review confirming that the explanation remains useful without displacing direct enterprise evidence. |
| **Established → Weakened** | Stale evidence, changed conditions, contrary outcomes, or a materially stronger competing explanation reduces confidence or narrows scope. |
| **Weakened → Contradicted** | Credible evidence or outcomes materially conflict with the explanation or satisfy a falsification condition. The contradictory record remains visible. |
| **Contradicted → Retired** | Review concludes the explanation is no longer usable in its stated scope or has been superseded; preserve lineage, history, and learning. |

Transitions are Review-stage governance, not runtime state transitions. Contradiction is valuable evidence: it may narrow a Mechanism, create a variant, return it to Candidate, or retire it.

## 7. Variants and reuse boundaries

- **Enterprise Mechanism:** an enterprise-specific explanation accountable to one Enterprise Twin and its direct evidence.
- **Participant-Type Mechanism:** a bounded explanation concerning a class of market participant; it must retain the participant evidence and conditions from which it was derived.
- **Cross-Enterprise Mechanism:** a comparative explanation tested across multiple materially distinct Enterprise Twins; it must preserve contributing variants, differences, counterexamples, and evidence lineage.

Industry Twins may synthesise Mechanisms for comparative intelligence, but do not replace enterprise-specific evidence, Observation acceptance, or Mechanism governance. Industry synthesis is not universal acceptance, and a single industry catalogue cannot validate a Cross-Enterprise Mechanism.

## 8. Relationship to existing architecture

EI-017 is deliberately narrow and does not duplicate authority already owned elsewhere.

| Authority | Preserved ownership and EI-017 relationship |
| --- | --- |
| [EI-001](volume-1-enterprise-modelling/EI-001-Enterprise-Model-Specification.md) | Owns the durable Enterprise Model / Commercial Digital Twin. Mechanisms are evidence-governed explanatory assets within, or referenced by, that memory; they do not replace it. |
| [EI-002](volume-1-enterprise-modelling/EI-002-Enterprise-Knowledge-Graph.md) | Owns graph entities and relationships. EI-017 defines no graph schema. |
| [EI-003](volume-1-enterprise-modelling/EI-003-Enterprise-Behaviour-Model.md) | Owns Enterprise Behaviour. Mechanisms may explain bounded behavioural outcomes but do not redefine Enterprise Behaviour. |
| [EI-004](volume-2-commercial-intelligence/EI-004-Commercial-Reasoning-Framework.md) | Owns commercial reasoning. A Mechanism is an inspectable causal input, not a replacement reasoning framework. |
| [EI-012](volume-5-intelligence-foundations/EI-012-Enterprise-Observation-Model.md) | Owns Observation semantics and lifecycle. Observation primacy, evidence lineage, Unknowns, and Contradictions are unchanged. |
| [EI-015](EI-015-Enterprise-Intelligence-Pattern-Model.md) | Owns candidate cross-enterprise Pattern governance. Patterns can support a Mechanism but cannot substitute for its causal explanation. |
| [IT-001](../specifications/industry-twins/IT-001-Industry-Twin-Specification.md) | Owns Industry Twin governance. Industry Twins may synthesise, never erase, enterprise-specific Mechanism evidence. |
| [OT-001](../specifications/opportunity-twins/OT-001-Opportunity-Twin-Specification.md) | Owns Opportunity Twin governance. A Mechanism does not create an Opportunity or bypass opportunity evidence. |
| [FP-009](../founding-papers/FP-009-Hypothesis-Validation-Standard.md) | Owns hypothesis validation and learning. Mechanism Candidates remain distinct from, and may be tested by, hypotheses. |
| Accepted ADRs | ADR-001, ADR-002, ADR-003, ADR-004, ADR-005, ADR-009, ADR-010, ADR-011, ADR-012, ADR-013, ADR-014, and ADR-016 remain controlling accepted decisions. In particular, ADR-005 requires strong recommendations to retain inspectable lineage. |

## 9. Banking validation provenance (non-normative)

The Banking Mechanism Catalogue is **validation evidence only**. It is not this architecture, a normative catalogue, or sufficient proof of universal mechanisms. It demonstrated candidate mechanisms concerning:

- current-account primacy;
- deposit-funded investment capacity;
- APP fraud reimbursement;
- operational resilience;
- legacy complexity;
- AI-assisted decisioning; and
- hyperscaler dependency.

These candidates are useful validation inputs because they expose causal claims, dependencies, competing explanations, and falsification needs. Banking is one validation input. Banking is not sufficient for universal acceptance; cross-industry validation remains outstanding.

## 10. Researcher implications (non-runtime only)

Future Researcher outputs could emit, for review and governed acceptance: **Observations**, **Pattern references**, **Mechanism Candidates**, **Executive Tensions**, **Reinvention Signals**, and **Evidence Demands**. This statement introduces no output contract, runtime behaviour, pack change, automation requirement, or production profile membership. Any future implementation must separately comply with EI-012, FP-009, and the Accepted ADRs.

## 11. Known Unknowns

The following remain open during Review and must remain visible in any validation work:

1. minimum Observation evidence required for a Candidate, Supported, or Validated Mechanism;
2. minimum diversity of evidence sources and evidence types;
3. confidence thresholds and their calibration;
4. relationship to Enterprise Behaviour ownership under EI-003;
5. relationship to Executive Tension ownership and governance;
6. how competing Mechanisms should be compared or ranked without hiding uncertainty;
7. freshness, decay, and review cadence;
8. variant identity, inheritance, and separation criteria;
9. cross-industry validation threshold;
10. human approval requirements for each lifecycle transition; and
11. runtime representation, if any, after a separate architecture decision.

## 12. Validation roadmap and non-promotion confirmation

Acceptance requires evidence from multiple UK Banking Enterprise Twins, Telecommunications, Utilities, cross-enterprise comparison, executive usefulness, and failure analysis. Validation must test whether the model preserves lineage, exposes contradictions and Unknowns, remains useful to executive review, and avoids manufacturing causal confidence from recurrence.

EI-017 remains **Review**, documentation only, with no production profiles and no runtime effect. Promotion, implementation, schemas, production-pack inclusion, or a universal mechanism catalogue require separate evidence and architecture governance.
