# Industry Twin Lifecycle Documentation Map

**Status:** Audit artefact  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-20

| Stage | Owning document | Supporting documents | Required inputs | Required outputs | Quality / acceptance criteria | Responsible role | Gaps / ambiguity / contradictions |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1. Industry selection | IT-001 (Review); EKPP-001 process | CIOS-AI, ADR-009 | Business need, candidate industry rationale | Industry selection rationale | Must not be a market report; must support decision/learning | Chief Architect + Researcher | No accepted Researcher-visible selection gate. |
| 2. Industry scope definition | IT-001 | EK-ARCH, BK-FOUND precedent | Boundary, inclusions/exclusions, value chain, regulation | Industry identity and scope | Explicit boundary and rationale | Researcher | IT-001 Review only; minimum scope unresolved. |
| 3. Source mapping | ADR-010 | FP-004, FP-006, CIOS-AI | Industry source families, evidence demand | Source map and acquisition plan | Structured-source-first, authority tiered | Researcher | FP-004/FP-006 draft and not researcher-pack. |
| 4. Industry research | EKPP-001 | IT-001, RA-Guide | Source map | Industry evidence, observations, foundation | Evidence-backed, explainable, cross-referenced | Researcher | Operating checklist missing from accepted pack. |
| 5. Enterprise selection | IT-001 | EI-001, Banking precedent | Industry scope, candidate enterprises | Enterprise population | Multiple materially different enterprises | Researcher + Chief Architect | Minimum number unresolved in IT-001. |
| 6. Enterprise research | EI-001 | EI-012, EI-002, RP-001 | Enterprise evidence | Enterprise Twin candidates | Durable memory, Unknowns/Contradictions | Researcher | Supplier/contract/procurement depth not explicit. |
| 7. Evidence governance | ADR-010 | FP-004, FP-006, EI-012 | Evidence | Classified evidence records | Authority, specificity, freshness, corroboration | Researcher | Draft source standards need accepted profile route. |
| 8. Observation creation | EI-012 | ADR-001, FP-004 | Accepted evidence | Atomic Observations | One meaningful fact/change/relationship/absence/contradiction | Researcher | Strong coverage. |
| 9. Enterprise Model population | EI-001 | ADR-002, EI-012 | Observations, evidence | Enterprise Model state | Reports not memory; durable model accumulates change | Researcher/Architect | Strong coverage. |
| 10. Knowledge Graph population | EI-002 | ADR-005, EI-012 | Entities, observations, relationships | KG relationships | Provenance, direction, confidence | Researcher/Architect | Pressure-to-procurement chain incomplete. |
| 11. Behaviour assessment | EI-003 | IT-001, EI-017 Review | Enterprise state | Behaviour interpretations | Separate observed recurrence from unsupported inference | Researcher/Architect | Mechanism model Review only. |
| 12. Industry-force synthesis | IT-001 | BK-IT precedent | Enterprise comparisons, observations | Industry pressures/forces | Affected scope, confidence, freshness, counterevidence | Researcher | IT-001 non-production. |
| 13. Reinvention model creation | FP-010-ERI Review; EGM-001 external | FP-009, BK reinvention reports | Pressures, behaviours, hypotheses | Reinvention themes/journey | Preserve methodology vs architecture boundary | Chief Architect | FP-010-ERI not accepted; EGM-001 external/absent. |
| 14. Hypothesis generation | FP-009 | ADR-005, EI-012 | Observations, signals, gaps | Hypotheses | Truth status and evidence required | Researcher | Strong coverage. |
| 15. Hypothesis validation | FP-009 | BK-RHYP-GOV | Hypotheses, evidence/counterevidence | Strengthened/weakened/rejected hypotheses | Lifecycle states, falsification | Researcher/Reviewer | Strong coverage, but Industry-specific thresholds missing. |
| 16. Opportunity formation | OT-001 Review | ADR-005, EI-014 Review | Themes, enterprise context | Opportunity hypotheses/themes | Must not assert supplier/procurement without evidence | Researcher/Architect | Review-only owner. |
| 17. Commercial valuation | ADR-004 docs/adr; FP-008 | Banking pipeline precedent | Opportunity hypotheses, comparables | Value/timing estimates | Inspectable, transient, non-canonical | Commercial reviewer | Comparables guidance weak. |
| 18. Human validation | ADR-004 | ADR-009, CIOS-AI | Human input, findings | Labelled validation notes | Human-supplied knowledge labelled/date | Human owner/Reviewer | Commercial validation checklist missing. |
| 19. Research quality review | EKPP-001 | RP-002, RA-Guide | Research package | Review findings | Evidence-backed, explainable, independently understandable | Assurance/Architect | EKPP not researcher-pack; checklist not specific. |
| 20. Architecture review | Handbook | EKPP-001, ADRs | Research outputs, gaps | Architecture decision/conditions | Authority hierarchy preserved | Chief Architect | Strong, but Industry Twin specifics should be added. |
| 21. Codex implementation handover | ADR-012 | FP-010-KP, KPS-001, CIOS-AI | Accepted candidate package | Codex task/handover | Package validity not canonical acceptance | Codex/Architect | Handover template not generic for Industry Twins. |
| 22. Runtime implementation | FEIR-001 Review | Engineering standards, Banking closure | Architecture handover | Runtime routes/views | No silent runtime authority | Codex | Out of scope; runtime specs Review/Proposed. |
| 23. Product acceptance | ADR-009 | BK-CLOSURE, FL-BANK-EVAL | Runtime + intelligence baseline | Acceptance decision | Initial Decision Twin vs Assured Release clear | Owner/Reviewers | Generic Industry Twin acceptance missing. |
| 24. Baseline and closure | EKPP-001 | BK-CLOSURE, BK-COMP | Accepted product | Baseline, limitations, backlog | Known limitations visible | Chief Architect/Product | Closure template not generalized. |
| 25. Refresh and continuous learning | IT-LC-001 Draft | CIOS-AI, EKPP-001 | Monitoring triggers, evidence demands | Refresh plan/backlog | Materiality, volatility, contradiction review | Researcher/Architect | Lifecycle spec too thin and Draft. |
