# Flora Architecture Compliance Checklist

**Purpose:** Provide a concise architecture review checklist for every pull request affecting Flora.

## Authority and Cross References

This governance document introduces review workflow only. It does not duplicate or supersede architectural guidance. Interpret every checklist item through the current authoritative documents:

- [FA-001 — Flora Enterprise Intelligence Workspace Reference Architecture](../reference-architectures/FA-001-Flora-Enterprise-Intelligence-Workspace-Reference-Architecture.md)
- [Flora ADR index](../decisions/README.md), especially Flora-related ADRs and accepted ADRs governing evidence, observations, lineage, labelled human knowledge and Enterprise Intelligence boundaries
- [Flora Product Blueprint — Flora Enterprise Intelligence Workspace Product Architecture](../FP-0XX-Flora-Enterprise-Intelligence-Workspace-Product-Architecture.md)
- [UX Journey — UX-001 Flora UK Banking Lloyds Reference Journey](../UX-001-Flora-UK-Banking-Lloyds-Reference-Journey.md)
- [CIOS Reference Architecture v1.0](../reference-architecture/CIOS-Reference-Architecture-v1.0.md)

## Object-Centric Design

□ Does the feature keep a governed Focus Object at the centre?

□ Is navigation object-first?

## Perspectives

□ Is this a Perspective rather than a new page?

□ Does it reuse existing Perspectives where appropriate?

## Reasoning

□ Can users inspect:

- Evidence
- Observations
- Unknowns
- Contradictions
- Recommendations

## Commercial Context

□ Need remains independent.

□ Provider Fit remains independent.

□ Accessibility remains independent.

□ Commercial Conviction remains independent.

## Governance

□ No second source of truth.

□ Enterprise Intelligence remains governed.

□ Human knowledge labelled.

□ Evidence lineage preserved.

## Explainability

□ Recommendation explainable.

□ Supporting evidence visible.

□ Contradictions visible.

## FA-001

□ Which architectural region is implemented?

□ Does the implementation strengthen FA-001?
