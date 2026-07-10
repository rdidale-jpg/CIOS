# FLORA-TP-001 — Progressive Assurance Test Plan

**Version:** v0.1  
**Status:** Working Draft  
**Owner:** Rob / CIOS  
**Date:** 10 July 2026  
**Authority:** ADR-009  
**Architecture owner:** FP-003 Flora Intelligence Architecture  
**Baseline:** Accepted MOD-CDT v1.3

## Mission

Validate that Flora can preserve CIOS research quality while reducing time, owner interaction and unnecessary publication work.

## Scope

### In scope

- accepted MOD v1.3 state ingestion or reconstruction;
- incremental refresh;
- autonomous Initial Decision Twin creation;
- explicit promotion to Assured Release;
- output, timing, lineage and uncertainty measurements.

### Out of scope

- weakening EI-001 or EI-012 semantics;
- provider-specific MOD pursuit;
- sponsor outreach;
- classified or operationally sensitive research;
- production-scale performance engineering.

## Test 1 — Accepted baseline ingestion

### Objective

Represent the accepted MOD v1.3 intelligence state as durable Twin memory.

### Required behaviour

Flora must preserve:

- 24 governed pain, pressure, symptom, driver, mechanism, constraint and Evidence-gap items;
- material Unknowns and Contradictions;
- distinction between enterprise need, public accessibility and Provider Fit;
- zero accepted provider-specific Pursue recommendations;
- accepted limitations and pending account decisions;
- stable identifiers where available.

### Acceptance criteria

- the Twin is queryable without treating the report as canonical memory;
- material claims retain source or release lineage;
- Provider Fit remains Not assessed;
- no deferred state is promoted;
- an executive view can be rendered from maintained state.

## Test 2 — Incremental MOD refresh

### Objective

Prove that new evidence updates affected state without rebuilding the complete release.

### Method

Provide a small controlled evidence set containing:

- one change that strengthens an existing pressure;
- one change that weakens or contradicts an existing Hypothesis;
- one irrelevant or duplicate item;
- one unresolved item that should become an Evidence Demand.

### Acceptance criteria

- affected Observations and Twin attributes update;
- unaffected state remains stable;
- duplicate evidence strengthens rather than duplicates memory;
- the Contradiction is preserved;
- the output is a concise change view plus updated ledger;
- no full manifest, completion report, validation JSON, duplicate PDF set or release ZIP is created;
- no owner interruption occurs unless an escalation rule is triggered.

## Test 3 — Fresh Initial Decision Twin

### Objective

Create a new enterprise Twin through one autonomous run.

### Operating constraints

- target elapsed time: 60–90 minutes;
- no intermediate approval;
- three outputs only:
  1. governed Twin state;
  2. executive decision view;
  3. source, uncertainty and lineage ledger.

### Acceptance criteria

The output clearly answers:

- Who and what is the enterprise?
- What are the 5–8 most consequential pressures?
- Why now?
- What mechanisms are causing or sustaining them?
- Which 2–4 reinvention seams deserve attention?
- Who may own them?
- What Evidence supports the judgement?
- What remains Unknown or contradictory?
- What is the next justified learning or commercial action?

No strong Recommendation may exist without inspectable lineage.

## Test 4 — Promotion to Assured Release

### Objective

Prove that added assurance can be applied without reconstructing the Twin.

### Promotion trigger

Simulate external executive circulation or a provider-specific shaping decision.

### Required behaviour

- preserve lineage to the Initial Decision Twin;
- identify new Evidence and reviews added during promotion;
- run formal reconciliation and release validation;
- record owner acceptance;
- produce only the additional artifacts required by the promotion;
- show any judgement changed by the added assurance.

## Measures

Capture for each test:

| Measure | Definition |
| --- | --- |
| Elapsed time | Start to decision-ready completion |
| Owner interruptions | Questions requiring Rob to administer the workflow |
| Source yield | Accepted useful Evidence relative to sources examined |
| Observation yield | New or materially updated reusable Observations |
| Unsupported claims | Material claims without adequate lineage |
| Unknown preservation | Material gaps retained explicitly |
| Contradiction preservation | Conflicting evidence retained without silent overwrite |
| Output count | Artifacts produced |
| Decision usefulness | Rob's assessment of specificity and next-action value |
| Rework | Corrections required before use |

## Success thresholds

The initial test cycle succeeds when:

- Test 2 completes without full release regeneration;
- Test 3 completes in one autonomous run within 90 minutes, excluding source outages;
- owner interruptions are zero or limited to a genuine escalation;
- no material unsupported claim is accepted;
- Unknowns and Contradictions remain visible;
- Rob can identify a clear next learning or commercial action;
- promotion in Test 4 adds assurance rather than recreating the intelligence.

## Failure and downgrade behaviour

Where evidence is insufficient:

- Pursue becomes Shape;
- Shape becomes Validate;
- Validate becomes Evidence Demand or Monitor;
- the Twin remains usable with a visible limitation.

A failed quality threshold must not be concealed by producing more documents.

## Completion report

For each test return:

1. summary;
2. elapsed time;
3. owner interruptions;
4. state changed;
5. outputs produced;
6. lineage and uncertainty result;
7. unsupported claims found;
8. decision usefulness;
9. failures and architecture debt;
10. recommended runtime change.

## Recommended sequence

1. Accept and freeze MOD v1.3 baseline.
2. Run Test 1.
3. Run Test 2.
4. Correct only material runtime defects.
5. Run Test 3 on a different enterprise.
6. Run Test 4.
7. Review ADR-009 against measured evidence.
