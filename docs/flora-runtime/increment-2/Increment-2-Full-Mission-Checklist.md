# Increment 2 Full Mission Checklist

Baseline: Flora Runtime Increment 2 — Bounded Evidence-Governed Explain. Stable IDs are authoritative for reconciliation and traceability.

## 1. baseline declaration
| ID | Requirement |
|---|---|
| I2-01-001 | Preserve semantic evaluation baseline commit `e7dca8e`. |
| I2-01-002 | Preserve the original Lloyds semantic evaluation dataset. |
| I2-01-003 | Preserve Increment 1 accepted contracts, behaviours, audit evidence and validation evidence. |
| I2-01-004 | Do not rewrite historical evaluation results; corrective runs must be separately versioned. |

## 2. Definition of Done
| ID | Requirement |
|---|---|
| I2-02-001 | Provide a bounded Lloyds Explain runtime for one fixed supported question. |
| I2-02-002 | Demonstrate package-only reasoning from governed Context Package input. |
| I2-02-003 | Validate context, output, repeatability, user experience, audit and prohibited boundaries. |

## 3. Context Package specification
| ID | Requirement |
|---|---|
| I2-03-001 | Define ContextPackageV0_1 as the sole Explain Worker input. |
| I2-03-002 | Include package identity, Focus Object identity and approved question identity. |
| I2-03-003 | Include substantive source passages, Evidence, Observations, Unknowns, contradictions or competing interpretations. |
| I2-03-004 | Include lineage, exclusions, limitations, authority, freshness and access state. |
| I2-03-005 | Include retrieval policy version, corpus baseline, evaluation baseline and package hash where practical. |

## 4. Context Package JSON Schema
| ID | Requirement |
|---|---|
| I2-04-001 | Provide machine validation for ContextPackageV0_1 shape. |
| I2-04-002 | Forbid undeclared fields and require declared package fields. |

## 5. semantic validation
| ID | Requirement |
|---|---|
| I2-05-001 | Validate reference integrity across passages, Evidence, Observations, Unknowns and tensions. |
| I2-05-002 | Validate Lloyds specificity and sector-general exclusion discipline. |
| I2-05-003 | Validate Unknown and contradiction preservation. |

## 6. deterministic Question Validator
| ID | Requirement |
|---|---|
| I2-06-001 | Accept only the approved question. |
| I2-06-002 | Reject unsupported questions safely. |

## 7. deterministic Context Planner
| ID | Requirement |
|---|---|
| I2-07-001 | Build a deterministic plan from Focus Object and approved question. |
| I2-07-002 | Use deterministic ordering and fixed governed retrieval policy version. |

## 8. governed content retrieval
| ID | Requirement |
|---|---|
| I2-08-001 | Retrieve only governed Lloyds evaluation corpus content. |
| I2-08-002 | Preserve authority, freshness and access state. |
| I2-08-003 | Record explicit exclusion reasons for non-usable or sector-only material. |

## 9. Context Package Builder
| ID | Requirement |
|---|---|
| I2-09-001 | Assemble source passages, Evidence, Observations, Unknowns and tensions into one package. |
| I2-09-002 | Compute a deterministic package identity and package hash. |
| I2-09-003 | Avoid canonical writes while building the package. |

## 10. package immutability
| ID | Requirement |
|---|---|
| I2-10-001 | Make validated Context Packages immutable runtime objects. |
| I2-10-002 | Ensure repeated executions against a frozen package use the same package hash. |

## 11. bounded Explain Worker
| ID | Requirement |
|---|---|
| I2-11-001 | Worker receives only the Context Package. |
| I2-11-002 | Worker cannot query canonical stores directly or arbitrary repository content. |
| I2-11-003 | Worker emits runtime views only. |

## 12. claim classification
| ID | Requirement |
|---|---|
| I2-12-001 | Classify material statements as source-supported fact, governed Observation, bounded interpretation, Unknown, competing interpretation, confidence limitation or next Evidence demand. |
| I2-12-002 | Facts trace to passages; Observations trace to Evidence; interpretations disclose the inferential step. |
| I2-12-003 | Reject unsupported causality and unsupported change claims without temporal basis. |

## 13. strategic coherence boundary
| ID | Requirement |
|---|---|
| I2-13-001 | Do not construct comprehensive Lloyds strategy or enterprise-wide causality. |
| I2-13-002 | Do not infer executive intent, extrapolate limited Evidence, identify sales opportunities, recommend pursuit, generate scores or name target executives without governed Evidence. |
| I2-13-003 | State when available Evidence does not support wider enterprise conclusions. |

## 14. deterministic Output Validator
| ID | Requirement |
|---|---|
| I2-14-001 | Reject unsupported claims, unknown IDs, absent lineage and sources outside the Context Package. |
| I2-14-002 | Reject sector-to-Lloyds attribution errors, invented causality, invented dates, fabricated authority or freshness. |
| I2-14-003 | Reject omitted material Unknowns, omitted competing interpretations, Recommendation language, scoring, pursuit language, unsupported executive attribution and strategic overreach. |
| I2-14-004 | Failed output becomes safe unavailable rather than misleading partial prose. |

## 15. user experience
| ID | Requirement |
|---|---|
| I2-15-001 | Accepted Lloyds workspace exposes “Explain what has changed”. |
| I2-15-002 | No unrestricted chat box; fixed supported question. |
| I2-15-003 | Show inspectable Context Package summary, source passages, Evidence, Observations, interpretations, Unknowns, competing interpretations, confidence limits and claim-level lineage. |
| I2-15-004 | Show safe-unavailable states in understandable user language. |

## 16. runtime audit
| ID | Requirement |
|---|---|
| I2-16-001 | Audit correlation ID, Focus Object ID, question ID, package ID, version and hash. |
| I2-16-002 | Audit retrieval policy version, model identifier, prompt version, timestamp, validator outcome and failure reason. |
| I2-16-003 | Audit records remain non-canonical. |

## 17. repeatability
| ID | Requirement |
|---|---|
| I2-17-001 | Run at least three executions against the same frozen Context Package. |
| I2-17-002 | Compare material claims, Evidence references, Lloyds attribution, interpretations, Unknowns, competing interpretations and confidence limits. |

## 18. validation fixtures
| ID | Requirement |
|---|---|
| I2-18-001 | Fixture set covers complete package, partial freshness, missing temporal baseline, insufficient Lloyds-specific Evidence, sector-general exclusion, competitor-specific content, competing interpretations, contradiction, scope difference and time difference. |
| I2-18-002 | Fixture set covers material Unknown, inaccessible Evidence, invalid references, unsupported claim, unsupported causality, fabricated date, Recommendation language, scoring, unsupported executive attribution, strategic overreach and safe-unavailable failure. |
| I2-18-003 | Each fixture defines schema, semantic, output-validation and operational outcomes plus user-visible result. |

## 19. semantic evaluation replay
| ID | Requirement |
|---|---|
| I2-19-001 | Create a new separately versioned evaluation run without overwriting `e7dca8e`. |
| I2-19-002 | Evaluate substantive content understanding, Lloyds specificity, change detection, semantic equivalence, contradiction understanding, materiality, evidence sufficiency, explanation without paraphrase, strategic coherence boundary, Unknown preservation and unsupported causality rejection. |

## 20. two-reviewer acceptance
| ID | Requirement |
|---|---|
| I2-20-001 | Maintain two independent reviewer scorecards. |

## 21. architecture constraints
| ID | Requirement |
|---|---|
| I2-21-001 | Preserve Focus Object → Approved Question → Validation → Plan → Retrieval → Immutable Package → Explain → Output Validation → Inspectable Explanation. |
| I2-21-002 | Treat Context Package bypass as material architecture defect. |

## 22. prohibited capabilities
| ID | Requirement |
|---|---|
| I2-22-001 | No canonical mutation, Observation promotion, unrestricted prompting, Recommendation capability, scoring capability or unsupported Focus Object/question handling. |

## 23. required deliverables
| ID | Requirement |
|---|---|
| I2-23-001 | Deliver checklist, gap analysis and reconciliation report. |
| I2-23-002 | Update tests, schemas, runtime, fixtures, UI, audit behaviour, semantic replay, reviewer evidence or completion report only where required. |

## 24. testing
| ID | Requirement |
|---|---|
| I2-24-001 | Run Increment 1 regressions and Increment 2 contract tests. |
| I2-24-002 | Run JSON Schema, semantic, output-validator, immutability, package-only boundary, unsupported object/question, repeatability, runtime route, rendered UI, prohibited scan and semantic replay checks where applicable. |

## 25. acceptance criteria
| ID | Requirement |
|---|---|
| I2-25-001 | Completion requires architecture boundary, content understanding, claim discipline, output validation, UX, audit, repeatability and evidence artefacts to pass. |

## 26. completion decision
| ID | Requirement |
|---|---|
| I2-26-001 | Use exactly one formal decision: confirmed complete, complete after reconciliation, accepted with conditions or materially incomplete. |

## 27. completion report
| ID | Requirement |
|---|---|
| I2-27-001 | Report original merge state, truncation impact, gaps, corrections, validation, architecture judgement, final decision and Increment 3 readiness. |
