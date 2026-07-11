# Account-Participant Position Assessment Specification v1.0

**Status:** Draft Normative Specification  
**Date:** 2026-07-11  
**Owner:** Rob / CIOS  
**Owning ADR:** [ADR-016 — Knowledge Packs as the Standard Exchange Mechanism](../../decisions/ADR-016-Knowledge-Packs-as-Standard-Exchange-Mechanism.md)  
**Owning papers:** [FP-010 — Knowledge Pack Architecture](../../founding-papers/FP-010-Knowledge-Pack-Architecture.md), [FP-011 — Knowledge Exchange Architecture](../../founding-papers/FP-011-Knowledge-Exchange-Architecture.md), [FP-009 — Hypothesis Validation Standard](../../founding-papers/FP-009-Hypothesis-Validation-Standard.md)  
**Semantic authorities:** [EI-013 — Knowledge Asset Exchange Model](../../enterprise-intelligence/EI-013-Knowledge-Asset-Exchange-Model.md), [EI-002 — Enterprise Knowledge Graph](../../enterprise-intelligence/volume-1-enterprise-modelling/EI-002-Enterprise-Knowledge-Graph.md)  
**Related specification:** [Market Participant Twin Specification v1.0](Market-Participant-Twin-Specification-v1.0.md)

## Purpose

An Account-Participant Position Assessment is a governed, account-relative interpretation of a Market Participant Twin against a specific account, opportunity or enterprise pressure. It answers whether, why, how and with what confidence a participant is commercially relevant in that account context.

The assessment is not a general ranking of the participant. It is a contextual judgement constrained by account need, pressure, decision ownership, access, procurement route, incumbent context, delivery requirement, alternatives, Unknowns and Contradictions.

## Account-relative rule

Every assessment MUST state the account, participant, opportunity or pressure, source cut-off and decision context. A recommendation is invalid unless its Evidence lineage, Observation lineage and Hypothesis lineage are inspectable.

Participant strength is not absolute. The assessment MUST interpret participant strengths and weaknesses relative to:

- the specific account;
- the material enterprise pressure;
- decision ownership;
- relationship and stakeholder access;
- procurement route and commercial frameworks;
- incumbent advantage or disadvantage;
- delivery requirement;
- partner dependencies;
- competitive alternatives.

## Required assessment structure

An Account-Participant Position Assessment MUST include:

| Field | Requirement |
| --- | --- |
| `assessment_id` | Stable assessment identifier. |
| `account_twin_id` | Account or Enterprise Twin identifier. |
| `participant_twin_id` | Market Participant Twin identifier. |
| `opportunity_or_pressure_id` | Opportunity, pressure, need or hypothesis being assessed. |
| `assessment_date` | Date of assessment. |
| `source_cut_off` | Latest source date included. |
| `account_need` | Account need being addressed. |
| `material_pressure` | Enterprise pressure or timing driver. |
| `participant_strengths` | Account-relevant strengths with classification and lineage. |
| `participant_weaknesses` | Account-relevant weaknesses with classification and lineage. |
| `capability_fit` | Fit against required capability and delivery context. |
| `credibility` | Evidence-backed credibility in this account, sector or requirement. |
| `relationship_access` | Existing relationships, channel access or partner routes. |
| `stakeholder_access` | Known or plausible access to decision owners and influencers. |
| `incumbent_advantage` | Whether incumbency helps, blocks, weakens or is irrelevant. |
| `route_to_market` | Direct, partner, framework, procurement or advisory route. |
| `commercial_frameworks` | Applicable frameworks, lots, panels, contracts or buying vehicles. |
| `delivery_confidence` | Confidence in delivery ability for the account requirement. |
| `partner_dependencies` | Required partners and dependency risk. |
| `competitive_alternatives` | Alternatives and why they may be stronger or weaker. |
| `delivery_risk` | Delivery, capacity, reputation, technical or execution risks. |
| `commercial_conflict` | Conflicts of interest, channel conflict or account constraints. |
| `addressability` | Whether the opportunity can practically be reached and pursued. |
| `unknowns` | First-class Unknowns affecting judgement. |
| `contradictions` | First-class Contradictions affecting judgement. |
| `confidence` | Overall confidence and confidence by material dimension. |
| `recommended_posture` | One or more supported postures. |
| `what_not_to_claim` | Claims prohibited by evidence limits. |
| `next_validation_action` | Next action needed to validate or revise the assessment. |
| `evidence_lineage` | Evidence references supporting the assessment. |
| `observation_lineage` | Observation references and lifecycle states. |
| `hypothesis_lineage` | Hypotheses tested, strengthened, weakened, rejected or still open. |

## Supported postures

The assessment MUST use one or more of the following postures:

- `learn` — gather more evidence before shaping or engaging;
- `validate` — test a defined hypothesis, access route or fit claim;
- `shape` — influence the account or market around a supported need;
- `engage` — proceed to direct account engagement with bounded claims;
- `partner` — pursue through or with the participant;
- `compete` — treat the participant as a competitive alternative or threat;
- `avoid claiming` — do not assert fit, strength, access or differentiation;
- `deprioritise` — reduce priority because fit, access, timing or risk is weak.

## Commercial questions

Each assessment MUST answer:

| Question | Required answer basis |
| --- | --- |
| Why this participant? | Account-relevant capability, credibility, access, incumbent position or differentiation. |
| Why this account? | Account need, material pressure, timing and commercial relevance. |
| Why now? | Fresh evidence, pressure, procurement timing, leadership change or validation trigger. |
| What evidence supports the fit? | Evidence and Observation lineage. |
| What access exists? | Relationship access, stakeholder access, procurement route and partner route. |
| What blocks access? | Incumbency, procurement barriers, stakeholder gaps, conflicts or missing frameworks. |
| Where are they genuinely differentiated? | Evidence-backed or clearly inferred differentiation, not marketing claims alone. |
| Where are they weak? | Evidence-backed or clearly inferred limitations. |
| What does the incumbent position mean? | Whether incumbency creates advantage, complacency, lock-in, conflict, risk or vulnerability. |
| What is unknown? | Explicit Unknowns with validation questions. |
| What contradicts the assessment? | Active or potential Contradictions and confidence impact. |
| What should be tested next? | Next validation action and related hypothesis. |
| What should not be claimed? | Prohibited overstatements and unsupported assertions. |

## Strength and weakness handling

Participant strengths and weaknesses used in an assessment MUST retain their Market Participant Twin classification:

- evidence-backed;
- inferred;
- human-supplied;
- unknown;
- contradictory.

The assessment MAY reinterpret the commercial relevance of a strength or weakness for the account, but it MUST NOT upgrade the underlying classification. A general strength may become irrelevant in an account; a general weakness may be mitigated by a partner, framework or account context.

## Hypothesis governance

The assessment MUST record Hypothesis lineage when it supports a posture or recommendation. Hypothesis lineage MUST identify:

- hypothesis statement;
- status: proposed, testing, strengthened, weakened, contradicted, rejected or retired;
- supporting Evidence and Observations;
- contradictory Evidence and Observations;
- Unknowns;
- validation questions;
- next validation action.

Recommendations MUST NOT be detached from their hypothesis and evidence lineage.

## Unknowns and Contradictions

Unknowns and Contradictions are first-class assessment outputs. They MUST be displayed alongside recommendation and confidence. They MUST affect posture, what-not-to-claim and next validation action.

A high-confidence recommendation is invalid if material Unknowns or Contradictions are hidden, downgraded to footnotes or omitted from the lineage.

## Account-Participant Assessment Knowledge Pack

An Account-Participant Assessment Knowledge Pack is the governed exchange container for an assessment. It MUST conform to the common Knowledge Pack structure:

```text
manifest.json
metadata.json
validation.json
lineage.json
checksums.sha256
payload/account-participant-assessment/
payload/presentation-model/
attachments/
```

Required content:

| Component | Requirement |
| --- | --- |
| Manifest | Pack identifier, version, issuer, account, participant, opportunity or pressure, source cut-off and payload inventory. |
| Metadata | Intended audience, use, assessment status, producer, rights and handling constraints. |
| Validation | Schema checks, posture checks, lineage checks, Unknown/Contradiction checks, strength/weakness classification checks and quarantine reasons. |
| Lineage | Evidence, Observation and Hypothesis lineage, inference explanations and human-supplied labels. |
| Checksums | Checksums for payload and attachments. |
| Payload | Structured assessment and optional Presentation Model. |
| Presentation Model | Audience-specific rendering where relevant, governed as interpretation. |

Pack acceptance means the package is valid for governed repository handling. Acceptance MUST NOT upgrade interpretation into fact, convert inferred relationships into evidence-backed relationships, or promote recommendations without owning-model review.

## Enterprise Knowledge Graph projection

The assessment MAY propose EI-002 graph relationships such as:

- `Participant SUPPLIES Enterprise`;
- `Participant COMPETES_FOR Opportunity`;
- `Participant PARTNERS_WITH Participant`;
- `Participant INCUMBENT_FOR Capability`;
- `Participant HAS_STRENGTH Capability`;
- `Participant HAS_WEAKNESS Capability`;
- `Participant HAS_ACCESS_TO Stakeholder`;
- `Participant ALIGNS_WITH Account Need`;
- `Participant CONFLICTS_WITH Account Constraint`;
- `Participant VULNERABLE_IN Account Context`.

All inferred graph relationships MUST preserve explanation and lineage. Assessment acceptance does not automatically accept graph projection into canonical Enterprise Knowledge Graph state.

## Minimum validation checklist

An Account-Participant Position Assessment is valid only when:

1. account, participant, opportunity or pressure and source cut-off are declared;
2. account-relative context is explicit;
3. strengths and weaknesses retain evidence governance;
4. Unknowns and Contradictions remain first-class;
5. recommended posture is one of the supported values;
6. recommendations retain Evidence, Observation and Hypothesis lineage;
7. what-not-to-claim is explicit;
8. next validation action is defined;
9. Knowledge Pack acceptance does not promote interpretation into fact.
