# CIRM Runtime Compliance Report

**Sprint:** Runtime Alignment Sprint — CIRM Version 1 Compliance and Information Architecture  
**Scope:** Flora runtime, Executive Brief, Observatory, Portfolio and Organisation pages  
**Update rule:** Every future runtime sprint should update this document before implementation closes.

## Canonical runtime information architecture

Flora runtime now uses one governing UI rule: **every piece of information has one canonical home; everything else references it.**

```text
Evidence → Strategic Signals → Commercial Insights → Transformation Thesis → Commercial Argument → Executive Recommendation
```

- **Evidence** contains facts only.
- **Strategic Signals** explain why evidence matters and identify unknowns and evidence needed.
- **Commercial Insights** combine signals.
- **Transformation Thesis** explains enterprise change.
- **Commercial Argument** explains why the thesis matters commercially.
- **Executive Recommendation** explains what to do and references the argument or hypothesis, not raw evidence.

## Compliance assessment

| Founding Paper | Runtime status | Estimated compliance | What currently aligns | What does not | Intentionally deferred |
|---|---:|---:|---|---|---|
| FP-003 — Flora Intelligence Architecture | Partially implemented | 76% | Observable evidence, quality assessment, signals, insights, theses, commercial arguments and recommendations are visible as an inspectable chain. Organisation pages follow executive-first presentation and retain diagnostics for analysts. | Runtime still has seeded fallback data and limited closed-loop learning. Some portfolio scoring remains legacy-compatible for existing tests and pages. | Full continuous learning loop, richer challenge/rebuttal workflow and outcome feedback automation. |
| FP-004 — Evidence Acquisition Standard | Partially implemented | 72% | Live collection routes, acquisition plans, evidence quality bands, source URLs and evidence drill-down support governed source collection. Evidence appears once in diagnostics and is referenced upstream by IDs. | Acquisition is deterministic and lightweight; it does not yet run sector-specific evidence hunts at depth for every enterprise. | Deeper acquisition orchestration, richer source refresh scheduling and automated evidence demand fulfilment. |
| FP-005 — Enterprise Intelligence Collection Framework | Partially implemented | 68% | Source registry and coverage maps support reusable collection patterns across sectors. Organisation pages expose gaps and evidence needed. | Blueprints are not yet formalised as first-class runtime objects for every enterprise type. | Fully versioned enterprise blueprints, sector minimum coverage policies and configurable collection playbooks. |
| FP-006 — Source Quality Standard | Partially implemented | 78% | Source tiers, evidence quality bands, diagnostics-only treatment and rejected-context handling prevent weak evidence from supporting signals. | Source lifecycle actions are visible but still basic; bias/freshness modelling is not yet comprehensive. | Advanced source retirement automation, freshness SLAs by source family and bias scoring. |
| FP-007 — Strategic Signal Standard | Partially implemented | 82% | Signals are treated as the primary reasoning object and show evidence references, unknowns, evidence needed, quality and confidence. Signals do not render as recommendations. | Some generated signal language can still resemble commercial interpretation rather than strictly bounded signal wording. | Stronger signal linting and automatic downgrade when signal text overclaims beyond evidence. |
| FP-008 — Commercial Conviction Model | Partially implemented | 74% | Runtime displays separate dimensions: Evidence Confidence, Commercial Attractiveness, Commercial Conviction, Transformation Pressure, Transformation Inevitability and Momentum. Recommendation and portfolio pages no longer rely only on one opaque score. | Some legacy score explainability still exposes final score for backward compatibility. | Retiring final-score-led UX once downstream consumers migrate to multidimensional conviction. |
| FP-009 — Hypothesis Validation Standard | Partially implemented | 70% | Organisation pages expose primary thesis, competing hypotheses, supporting and contradictory signals, unknowns, evidence needed, validation questions and next learning conversation. | Hypotheses are mostly rendered from current theses/insights rather than managed through a complete validation lifecycle. | Dedicated hypothesis state machine for strengthen, weaken, reject and retire decisions. |

## Overall runtime alignment

**Estimated Overall CIRM Alignment:** 74%

Flora is substantially closer to CIRM Version 1 because the runtime now favours an executive reading path, canonical information homes, references over repetition, multidimensional conviction and inspectable drill-down. The remaining gap is not presentation; it is the depth of runtime lifecycle management for collection blueprints, source retirement, hypothesis validation and continuous learning.
