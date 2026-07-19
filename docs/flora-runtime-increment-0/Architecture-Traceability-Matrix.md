# Architecture Traceability Matrix

| Increment 1 capability | Governing document/decision | Section or decision | Owning component | Acceptance criterion | Validation method |
| --- | --- | --- | --- | --- | --- |
| Read governed UK Banking corpus | ADR-024, ADR-016, Banking manifest/register | Repository is authoritative; Knowledge Pack acceptance boundary | Governed Asset Connector | Reads named files without mutation | Static path validation and read-only test. |
| Show Focus Object identity | FA-001, ADR-025 proposed, FEIR-001 | Focus Object and runtime object classes | Runtime Object Registry | Object header includes ID, type, status, owner, source path | Contract fixture validation. |
| Project relationships | EI-002, FEIR-001 | Relationship resolution/runtime graph projection | Relationship resolver | Relationships are source-linked and read-only | Fixture test with source/target resolution and collision report. |
| Evidence/Observation availability | ADR-001, EI-012, ADR-014 | Observations atomic; evidence package construction | Retrieval adapter | Availability shown; missing evidence returns Unknown/safe-unavailable | Validation fixtures for present/missing refs. |
| Preserve Unknowns | FEIR-001, EI-012, FA-001 | Unknown preservation | Projection composer | Unknowns visible and not converted into claims | Checklist review and fixture assertions. |
| Preserve Contradictions | FEIR-001, EI-012, ADR-001 | Contradiction preservation | Projection composer | Contradictory sources/claims displayed side by side | Fixture assertions. |
| Inspect one-hop lineage | ADR-005, ADR-014, FA-001 | Inspectable lineage | Lineage resolver | User can see source asset and evidence/observation refs where present | Lineage response fixture. |
| Persist workspace state only | FA-001, ADR-024, runtime plan | Runtime state not canonical memory | Workspace State Service | Focus/perspective/trail saved without knowledge writes | Code review and state fixture. |
| Enforce access boundary | FEIR-001, ADR-014, existing access code | Security/access considerations | Access policy adapter | Denied enterprise/object returns safe unavailable | Access tests with allow/deny fixtures. |
| Record audit baseline | FEIR-001, ADR-024, ADR-014 | Provenance and audit | Audit ledger stub | Every read/projection emits required fields | Schema validation over audit fixture. |
| Safe unavailable response | ADR-014, FEIR-001 | Failure behaviour | Presentation composer | Failure never fabricates intelligence | Negative tests for missing asset/denied access. |
| Exclude recommendations | ADR-005, FP-009 | No recommendation without lineage | Scope guard | No strong Recommendation in Increment 1 | Static route/component review. |
