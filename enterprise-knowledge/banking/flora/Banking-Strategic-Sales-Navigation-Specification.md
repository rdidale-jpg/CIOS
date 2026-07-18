# Banking Strategic Sales Navigation Specification

**Asset ID:** `BK-FLR-SSN-SPEC-001`  
**Document class:** Flora navigation specification  
**Domain:** Banking  
**Strategic user:** Strategic Sales Director  
**Status:** Candidate specification  
**Effective date:** 2026-07-18  
**Scope:** Experience and information requirements only; this specification does not prescribe frontend technology.

## 1. Strategic user and intended outcomes

Flora must support a commercially experienced, non-technical Strategic Sales Director who is shaping enterprise reinvention opportunities before formal procurement. The user must not need to understand repository paths, manifest schemas or asset taxonomy.

The intended outcome is a governed navigation journey from industry change to a proportionate commercial action:

```text
Industry change
→ transformation pressure
→ mechanism of change
→ affected participant types
→ priority enterprises
→ enterprise-specific observations
→ reinvention hypothesis
→ evidence and contradictions
→ relevant executive audience
→ next best commercial action
```

Every answer must preserve the difference between external evidence, governed observations, mechanisms, hypotheses, Unknowns, Contradictions, human-supplied knowledge and recommendations.

## 2. Explore, Focus and Shape modes

### Explore — understand the industry

Explore answers:

- What is changing in Banking?
- Which structural pressures and mechanisms matter?
- Which participant types are affected?
- Which hypotheses are strengthening or weakening?
- What remains Unknown or Contradictory?

Explore must use the Banking Industry Foundation, Industry Twin, Mechanisms and Tensions Model, Infrastructure Twin, mechanism matrices and Reinvention Hypotheses as governed sources.

### Focus — select enterprises and opportunity zones

Focus answers:

- Which enterprises are exposed to the pressure?
- Where is urgency increasing?
- Where is credible ownership visible?
- Where is evidence weak?
- Which enterprises require more learning before selling?

Focus must compare enterprises by explainable factors, not by an invented opportunity score unless a governed scoring method exists.

### Shape — prepare executive engagement

Shape answers:

- What is the strongest current hypothesis?
- What contradicts it?
- Who should care?
- What would be a useful executive conversation?
- What evidence is required next?
- What should not yet be proposed?

Shape must treat hypotheses as testable reasoning objects, not conclusions.

## 3. Required navigation views

| View | Purpose | Support expectation |
|---|---|---|
| Banking Industry Overview | Summarise structural pressures, mechanisms, participant variants, Unknowns and Contradictions. | Must be generated from governed industry assets and hypothesis register. |
| Why Now / Change Signals | Show observations, evidence dates, freshness, timing pressure and confidence. | Must expose missing timing data where evidence is not recent or not dated at observation level. |
| Pressure and Mechanism Explorer | Let a user move from pressure to mechanism, tension, participant type and hypothesis. | Must use stable mechanism IDs and show mechanism confidence separately from enterprise applicability. |
| Participant-Type Comparison | Compare incumbents, challengers, mutuals, universal banks, infrastructure participants and ecosystem actors. | Must preserve variants and avoid averaging the industry into one bank model. |
| Enterprise Comparison | Compare enterprise exposure, ambition, programmes, dependency and confidence. | Must distinguish commercially interesting, requires more learning, inaccessible, weakly evidenced and not priority. |
| Enterprise Canvas | Answer “Why this enterprise?” using pressures, mechanisms, programmes, hypotheses, evidence, contradictions and Unknowns. | Must be enterprise-specific and cite source twin evidence. |
| Hypothesis Workspace | Inspect statement, lifecycle, confidence, supporting observations, mechanisms, enterprise models, evidence, contradictions and validation questions. | Must show governing methodology and rejection/weakening conditions. |
| Evidence and Contradiction View | Trace source evidence to observations, mechanisms and hypotheses. | Must preserve external evidence, human-supplied knowledge labels and contradictions. |
| Executive Stakeholder View | Identify roles, owners, sponsors, influencers, blockers and ecosystem participants. | Must show whether roles are governed, inferred or missing. |
| Next Best Commercial Action | Recommend learning, evidence seeking, executive provocation, discovery, workshop, defer or reject. | Must be proportional to evidence strength and state what should not yet be proposed. |

## 4. Required questions each view must answer

Each Flora view must answer the Strategic Sales Director’s core questions:

- **Who?** Named executive role, decision owner, likely sponsor, influencer, blocker or ecosystem participant.
- **Why now?** Triggering observation, evidence date, timing pressure, external deadline, programme movement, leadership or market change.
- **Why them?** Enterprise-specific exposure, ambition, capability gap, operating-model dependency or transformation appetite.
- **What evidence?** Supporting sources, observations, freshness, confidence, contradictions and human-supplied labels.
- **What next?** Learning action, executive engagement, validation question, commercial asset, defer or reject decision.

A view does not pass if this answer exists only as unstructured prose in a document. It must be available through explicit relationships or a clearly identified derived view.

## 5. Required asset and relationship types

Flora should support the following asset types:

- Industry Foundation
- Industry Twin
- Infrastructure Twin
- Mechanism Catalogue or mechanism authority
- Observation Register
- Enterprise Twin
- Participant comparison matrix
- Reinvention Hypothesis Register
- Evidence source
- Methodology or standard
- Discovery register / manifest
- Navigation specification
- Validation report

Flora should support the following relationship types:

- `governed_by_methodology`
- `supports_hypothesis`
- `contradicts_hypothesis`
- `uses_observation`
- `uses_mechanism`
- `affects_enterprise_model`
- `evidenced_by`
- `derived_from`
- `requires_evidence`
- `has_unknown`
- `has_contradiction`
- `has_executive_audience`
- `enables_commercial_action`
- `human_supplied_comparison`

Relationships must carry source asset ID, target asset ID or path, relationship type, resolution status, confidence and whether the relationship is directly asserted or derived.

## 6. Evidence, confidence and contradiction display requirements

Flora must display:

- evidence source type: external evidence, governed observation, inferred relationship, hypothesis, human-supplied knowledge, recommendation, Unknown or Contradiction;
- source freshness and evidence cut-off;
- confidence at both mechanism and enterprise-applicability level;
- contradictions with the same prominence as supporting evidence;
- Unknowns as required learning tasks, not as hidden metadata;
- evidence lineage from source evidence to observation to mechanism to hypothesis to action;
- warnings when observation-level source evidence is inherited rather than directly linked in the current asset.

## 7. Hypothesis lifecycle display requirements

Each hypothesis must show:

- hypothesis ID and statement;
- lifecycle state and owner acceptance state;
- confidence or conviction;
- supporting observations;
- supporting mechanisms;
- affected enterprise models or twins;
- supporting evidence;
- contradicting evidence;
- Unknowns;
- evidence required;
- monitoring indicators;
- governing methodology;
- conditions that would weaken or reject it;
- commercial-action boundary: learn, validate, provoke, workshop, defer or reject.

## 8. Executive specificity requirements

Executive specificity must be explicit. Flora must not imply named ownership merely because a related role appears in a generic tension table.

Required fields:

- governed executive role;
- enterprise-specific decision owner;
- likely sponsor;
- influencer;
- blocker;
- ecosystem participant;
- source basis;
- confidence;
- missing specificity.

Where the repository only provides generic roles, Flora must label the answer as generic role-level evidence and require enterprise validation.

## 9. Next-best-action constraints

Recommendations must not appear stronger than their evidence lineage permits. Flora must:

- prefer learning before selling when conviction is incomplete;
- state intended executive audience;
- state commercial purpose;
- state evidence supporting the action;
- state evidence still required;
- state current confidence;
- state what should not yet be proposed;
- reject automatic sales recommendations without inspectable lineage;
- label human-supplied knowledge;
- preserve Unknowns and Contradictions in the action view.

## 10. Example Banking journeys

### Journey A — AI as governed decision infrastructure

Start: “What is changing in Banking?”  
Path: AI and outcome evidence pressure → BM-17/BM-20/BM-14 → enterprise twins with AI use cases → `BRH-007` and `BRH-014` → evidence gaps on maturity and benefit → generic executive audience CIO, COO, Chief Data/AI Officer, CRO → next action: discovery conversation to validate use-case maturity and assurance evidence, not a product proposal.

### Journey B — Physical access as shared trust infrastructure

Start: “Why does this matter now?”  
Path: app-first but not app-only distribution and access pressure → BM-04/BM-02/BM-14/BM-15 → Nationwide and Lloyds variants → `BRH-003` → contradiction that branches are both cost burdens and trust assets → next action: executive provocation or learning session for Retail CEO / COO / Customer Director where enterprise branch, hub and vulnerable-customer evidence is missing.

### Journey C — Cloud and core migration as optionality

Start: “Which enterprises are most exposed?”  
Path: cloud/core and operational-resilience pressure → BM-16/BM-19/BM-13/BM-15/BM-17 → incumbent and challenger twins → `BRH-008` and `BRH-009` → Unknowns on workload concentration and exit plans → next action: shape a workshop only if enterprise-specific migration or critical third-party exposure is visible; otherwise seek named evidence.

## 11. Acceptance criteria for a future Flora interface

A future Flora interface passes when:

1. a Strategic Sales Director can answer Who, Why now, Why them, What evidence and What next without opening repository files;
2. Explore, Focus and Shape modes are visible and navigable;
3. at least three Banking hypotheses can be inspected as testable reasoning objects;
4. every commercial action has inspectable evidence lineage;
5. contradictions and Unknowns remain visible in all relevant views;
6. human-supplied knowledge is labelled distinctly from external evidence and governed observations;
7. repository discovery readiness, ingestion readiness and runtime UX validation are displayed separately;
8. no unsupported Banking research is introduced by the interface;
9. generic executive role evidence is not presented as enterprise-specific ownership;
10. weak evidence leads to learn, seek evidence, defer or reject rather than automatic selling.

## 12. Runtime validation boundary

Flora must display three separate readiness states and must not collapse them:

- Repository discovery readiness: whether manifests and governed relationships can support navigation.
- Runtime ingestion validation: whether an operational loader or service has ingested the assets.
- Runtime UX validation: whether a working Flora interface or test harness has supported the user journey.

If no runtime or harness is available, the interface and reports must state `Runtime ingestion validation: NOT EXECUTED` and `Runtime UX validation: NOT EXECUTED`.
