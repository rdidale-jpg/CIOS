# CIOS Progressive Assurance Architecture Pack v1.0

**Date:** 10 July 2026  
**Owner:** Rob / CIOS  
**Decision:** Implement ADR-009 and return to Flora testing.

## Canonical repository documents

- `architecture/decisions/ADR-009-Progressive-Assurance-for-Commercial-Digital-Twins.md`
- `architecture/decisions/README.md`
- `CIOS-AI.md`
- `architecture/founding-papers/FP-003-Flora-Intelligence-Architecture.md`
- `architecture/reference-architecture/CIOS-Reference-Architecture-v1.0.md`
- `architecture/handbook/CIOS-Chief-Architect-Handbook.md`
- `architecture/reference-architecture/Glossary.md`
- `architecture/reference-architecture/Document-Map.md`
- `docs/decisions/MOD-CDT-05-Owner-Acceptance-Decision-v1.3.md`
- `docs/testing/FLORA-TP-001-Progressive-Assurance-Test-Plan-v0.1.md`

## Deliberately unchanged

- EI-001 Enterprise Model Specification
- EI-002 Enterprise Knowledge Graph
- EI-003 Enterprise Behaviour Model
- EI-012 Enterprise Observation Model
- FP-009 Hypothesis Validation Standard

Their core object, lineage, uncertainty and hypothesis requirements remain authoritative.

## Review copies

The `review-copies` folder contains DOCX renderings of each changed or new document. Markdown files remain the canonical repository form.

## Banking three-horizon opportunity pipeline

Focus Banking now renders a transient, derived-runtime Banking Opportunity Pipeline for Strategic Sales Directors. The pipeline reuses the governed Banking Enterprise Intelligence runtime, semantic Banking interpretation layer, Banking Enterprise Twins, observations, mechanisms, Reinvention Hypotheses and Strategic Sales Navigation assets. It does not mutate authoritative Enterprise Knowledge and it does not create CRM-style scores.

The runtime output contract is implemented by `generate_banking_opportunity_pipeline()` and returns:

- `pipeline_id`, `industry`, `generated_at`, `knowledge_snapshot` and `reasoning_mode`;
- typed `commercial_opportunity` objects with hypothesis, observation, mechanism and asset lineage;
- portfolio counts for Horizon 1, Horizon 2, Horizon 3 and Not currently actionable;
- global Unknowns, Contradictions and validation state.

Focus Banking supports portfolio filters for horizon, enterprise, participant type, executive role, hypothesis, confidence, evidence strength, Recommendation Eligibility, Unknowns and Contradictions. Opportunity detail views show the thesis, target scope, why now, why this enterprise, executive role relevance, evidence, hypotheses, Unknowns, Contradictions, horizon rationale, movement criteria, next action, prohibited stronger actions and full lineage. Shape brief links preserve the selected opportunity context instead of treating Shape as a fresh blank run.

### Manual acceptance test for Rob

1. Open Flora.
2. Select Explore.
3. Open Banking.
4. Select `View Banking Opportunity Pipeline`.
5. Confirm Focus shows Horizon 1, Horizon 2, Horizon 3 and Not currently actionable.
6. Confirm every opportunity shows title, enterprise or participant type, why now, executive roles, confidence, next action and movement criterion.
7. Open one Horizon 1 opportunity if justified by the current generated set.
8. Confirm it explains why it is Horizon 1.
9. Open one Horizon 2 opportunity and confirm it explains missing evidence.
10. Open one Horizon 3 opportunity and confirm it explains the longer-term rationale.
11. Filter by enterprise.
12. Filter by executive role.
13. Open an opportunity detail and confirm Unknowns and Contradictions are visible.
14. Confirm no named executive is invented.
15. Select `Shape brief`.
16. Confirm Shape preserves the selected opportunity.
17. Confirm no proposal-level action is shown unless permitted.
18. Check Render logs for no startup or request failures.
