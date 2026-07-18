# Flora Banking Enterprise Intelligence Prototype

Purpose: run one governed Banking Enterprise Intelligence vertical slice for the canonical Strategic Sales Director question.

Architecture ownership: ADR-024, FEIR-001, EIRP-001, EI-012, FP-009 and the Banking Strategic Sales Navigation Specification govern the prototype boundaries.

Run:

```bash
python -m cios.applications.flora.enterprise_intelligence banking
```

Outputs are written to `.flora_enterprise_intelligence/banking/`: `pipeline-run.json`, `execution-trace.txt`, and `strategic-sales-brief.md`.

The default mode is deterministic development mode using replaceable `ReasoningAdapter` semantics. No model configuration is required. A future model-backed adapter must still return structured schema-valid outputs and pass deterministic validation.

Validation checks ID resolution, BRH-003 lineage, authority boundaries, Unknown/Contradiction propagation, named-executive controls, enterprise-specificity downgrade, recommendation downgrade, lineage in the final brief, and schema validity.

The brief is labelled `Derived runtime view — not authoritative Enterprise Knowledge`. It is a transient presentation of governed Banking assets, not a repository mutation or accepted Enterprise Knowledge.

Known limitations: only Banking, one role, one question, BRH-003, one challenge pass, no production UI, no durable session, no repository write-back, and observation source evidence remains inherited where the current Banking assets expose lineage only in prose.

Next increment: introduce a durable session decision if repeated runs need comparative memory, add a machine-readable Observation Register when governed, and add model-backed reasoning behind the adapter without leaking provider-specific types into runtime contracts.
