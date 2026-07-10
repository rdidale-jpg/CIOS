# ADR-009 — Progressive Assurance for Commercial Digital Twins

**Status:** Accepted  
**Decision date:** 10 July 2026  
**Owner:** Rob / CIOS  
**Decision class:** Reasoning, governance and cross-cutting runtime obligation  
**Scope:** Flora research, Commercial Digital Twin creation and refresh, Publisher release production  
**Supersedes:** No existing ADR  
**Related:** ADR-001, ADR-002, ADR-004, ADR-005, ADR-010; FP-003; EI-001; EI-012

## Context

CIOS must preserve research vigour, inspectable lineage and durable enterprise memory while enabling a strategic sales director to obtain a useful Commercial Digital Twin quickly and with minimal administration.

The MOD Commercial Digital Twin v1.3 demonstrated improved enterprise specificity and disciplined separation of enterprise need, accessibility, Provider Fit and commercial action. It also demonstrated that applying full publication, reconciliation and release controls to routine research can create excessive elapsed time, owner interruption and document production.

The architecture therefore needs to distinguish the assurance required to create useful governed Twin state from the additional assurance required to publish, circulate or act on high-consequence conclusions.

## Decision

CIOS adopts **Progressive Assurance**.

Commercial Digital Twin work has two explicit operating modes:

### Initial Decision Twin

The default mode for creating or refreshing governed enterprise understanding.

It optimises for:

- rapid autonomous research;
- durable Observation-backed Twin state;
- executive decision usefulness;
- explicit Unknowns and Contradictions;
- inspectable lineage proportionate to the action proposed;
- the shortest practical time to a useful first Twin.

The minimum output set is:

1. governed Commercial Digital Twin state;
2. an executive decision view;
3. a source, uncertainty and lineage ledger.

A separate manifest, completion report, validation narrative, duplicate publication formats, release JSON or packaged release is not mandatory.

### Assured Release

An explicit promotion mode used when intelligence will support external publication, executive outreach, provider-specific Pursue decisions, material investment or procurement decisions, or another high-consequence use.

It may add:

- deeper reconciliation and independent challenge;
- formal release validation;
- publication controls;
- owner acceptance;
- machine-readable release evidence;
- packaged and duplicated publication formats.

Assured Release is not the default path for routine Twin creation or refresh.

## Researcher authority

Within an Initial Decision Twin, the Researcher has standing authority to:

- select and prioritise permissible sources;
- create and update Evidence, Observations, Unknowns and Contradictions;
- form and challenge outside-in Hypotheses;
- rank pressures and identify candidate reinvention seams;
- stop collection when decision sufficiency and Evidence Saturation are reached;
- produce the minimum output set without intermediate owner approval.

The Researcher must escalate when:

- provider-specific Pursue, Redirect, Reject or external outreach is proposed;
- confidential relationship knowledge or provider capability materially changes the judgement;
- evidence conflict prevents a useful bounded conclusion;
- the enterprise boundary, legal boundary or security boundary is unclear;
- a requested conclusion would require unsupported inference;
- the owner explicitly requests Assured Release.

## Invariants

Progressive Assurance does not weaken:

- Observations as atomic reusable intelligence;
- the Enterprise Model as durable memory;
- source permissibility and material-claim attribution;
- separation of Evidence, inference, Hypothesis and Recommendation;
- preservation of Unknowns and Contradictions;
- labelling of human-supplied knowledge;
- inspectable lineage for strong Recommendations;
- learning-before-selling where conviction is incomplete.

## Completion rule

An Initial Decision Twin is complete when:

- the monitored enterprise boundary is clear;
- the most consequential pressures and causal mechanisms are adequately supported;
- material counter-evidence, Unknowns and Contradictions are visible;
- the leading commercial or learning seams are explicit;
- the next justified actions are clear;
- additional research is unlikely to change the immediate decision materially.

Completeness is decision-relative. Exhaustive field population and publication packaging are not completion requirements.

## Promotion triggers

Promote an Initial Decision Twin to Assured Release when one or more of the following applies:

- external circulation as an authoritative CIOS publication;
- provider-specific fit or Pursue judgement;
- named sponsor outreach;
- material financial, procurement or investment reliance;
- high reputational, legal, safety or security consequence;
- owner request.

## Alternatives considered

### Uniform full governance

Rejected as the default because it creates disproportionate delay and administrative overhead for reversible learning decisions.

### Ungoverned fast research

Rejected because speed without durable memory, lineage and uncertainty controls would weaken the CIOS differentiator.

### One fixed reduced process

Rejected because assurance must vary with action strength, audience and consequence.

## Consequences

### Positive

- faster time to an initial useful Twin;
- greater Researcher autonomy;
- fewer owner interruptions;
- less publication theatre;
- clearer distinction between model creation and formal release;
- retained ability to increase assurance before consequential action.

### Trade-offs

- Initial Decision Twins may contain more visible Unknowns;
- not every field or publication view will be complete;
- users must understand the operating mode and decision boundary;
- runtime must support explicit promotion rather than silently treating all outputs as equivalent.

## Runtime implications

Flora must:

- default to Initial Decision Twin mode;
- maintain mode, maturity and decision boundary as explicit state;
- update affected Twin state incrementally;
- run mandatory integrity checks once near completion rather than as repeated conversational gates;
- prevent Publisher packaging from becoming a prerequisite for model completion;
- support explicit promotion to Assured Release;
- record elapsed time, owner interruptions and output count for evaluation.

Publisher must render views from governed Twin state. It must not become the canonical memory or force full release production during ordinary research.

## Required validation

The operating model must be tested through:

1. ingestion of the accepted MOD v1.3 governed state;
2. an incremental MOD refresh;
3. creation of a fresh Initial Decision Twin with no intermediate approval;
4. promotion of one Initial Decision Twin to Assured Release.

Success measures include elapsed time, owner interruptions, unsupported claims, Observation quality, preserved uncertainty, decision usefulness and unnecessary artifacts.

## Affected documents

- `CIOS-AI.md`
- `architecture/founding-papers/FP-003-Flora-Intelligence-Architecture.md`
- `architecture/reference-architecture/CIOS-Reference-Architecture-v1.0.md`
- `architecture/handbook/CIOS-Chief-Architect-Handbook.md`
- `architecture/reference-architecture/Glossary.md`
- `architecture/reference-architecture/Document-Map.md`
- `architecture/decisions/README.md`

EI-001, EI-002, EI-003, EI-012 and FP-009 are not changed by this decision.

## Review and supersession conditions

Review this ADR after the first two Flora test cycles or when:

- Initial Decision Twins repeatedly fail quality thresholds;
- full release controls are still being invoked by default;
- users cannot distinguish operating mode or decision boundary;
- a new runtime model replaces Flora/Publisher responsibilities;
- evidence shows a materially better assurance design.
