# Flora Architectural Decision Workflow

**Purpose:** Define the mandatory architecture workflow for Flora ideas, missions and implementation changes. No implementation should bypass this workflow.

## Authority and Cross References

This governance document introduces review workflow only. It does not duplicate or supersede architectural guidance. Interpret every checklist item through the current authoritative documents:

- [FA-001 — Flora Enterprise Intelligence Workspace Reference Architecture](../reference-architectures/FA-001-Flora-Enterprise-Intelligence-Workspace-Reference-Architecture.md)
- [Flora ADR index](../decisions/README.md), especially Flora-related ADRs and accepted ADRs governing evidence, observations, lineage, labelled human knowledge and Enterprise Intelligence boundaries
- [Flora Product Blueprint — Flora Enterprise Intelligence Workspace Product Architecture](../FP-0XX-Flora-Enterprise-Intelligence-Workspace-Product-Architecture.md)
- [UX Journey — UX-001 Flora UK Banking Lloyds Reference Journey](../UX-001-Flora-UK-Banking-Lloyds-Reference-Journey.md)
- [CIOS Reference Architecture v1.0](../reference-architecture/CIOS-Reference-Architecture-v1.0.md)

## Workflow

```text
Idea
↓
Architecture Review
↓
ADR required?
↓
Update FA?
↓
Update UX?
↓
Codex Mission
↓
Implementation
↓
Validation
↓
Architecture Review
↓
Merge
```

## Workflow Rules

- Every Flora idea starts with architecture review against FA-001, the Flora ADR record, the Product Blueprint, the UX Journey and the Reference Architecture.
- If the idea changes architectural intent, ownership, terminology, boundaries, lineage, explainability or commercial reasoning, determine whether an ADR is required before implementation.
- If the idea changes the Flora workspace composition or architectural regions, update the relevant FA document before or alongside implementation.
- If the idea changes user journey, navigation, Perspective behaviour or inspectability, update the relevant UX Journey before or alongside implementation.
- Codex missions should cite the relevant architecture sources and state the architectural region being strengthened.
- Implementation must preserve governed Enterprise Intelligence and must not create a second source of truth.
- Validation must include the Flora Architecture Compliance Checklist and the Flora Implementation Review template.
- Merge is allowed only after final architecture review confirms that no duplicate architectural guidance has been introduced.
