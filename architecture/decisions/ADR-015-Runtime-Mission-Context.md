# ADR-015: Runtime Mission Context Architecture

**Identifier:** ADR-015
**Version:** 1.0
**Document Type:** Architecture Decision Record
**Authority Classification:** Accepted canonical ADR
**Status:** Accepted
**Date:** 2026-07-21
**Owner:** Rob / CIOS
**Supersedes:** None
**Superseded by:** None

## Context

CIOS AI agents operate across discovery, research, decision support and assurance work. Before this decision, runtime prompts, task descriptions, available tools and research depth could be treated as part of the same bundle as durable Enterprise Intelligence doctrine. That creates two risks: runtime behaviour can accidentally modify architecture doctrine, and durable knowledge objects can be overloaded with mission-specific instructions.

CIOS already has universal doctrines for Evidence, Observation and Enterprise Model memory. ADR-001, ADR-002, ADR-005, ADR-010, ADR-014, ADR-016, ADR-024 and the Founding Papers establish that Evidence proves, Observations remember, Enterprise Models accumulate durable memory, recommendations require lineage and provider output is candidate until validated. ADR-015 adds the missing runtime execution model without changing those doctrines.

## Decision

CIOS shall treat **Mission**, **Research Policy** and **Capability Profile** as independent runtime inputs that are assembled into a **Runtime Context** for a specific AI-agent execution.

Runtime Context is transient execution configuration. It guides what the agent is trying to achieve, how much research and assurance are expected, and which tools or capabilities may be used. It does not modify Evidence, Observation, Enterprise Model, Enterprise Knowledge Graph, CIRM, Knowledge Pack or Founding Paper doctrine.

The Runtime Context Architecture is mandatory for CIOS AI-agent missions, including Codex missions, Researcher missions, Assurance missions and future Flora-native AI missions.

## Core runtime inputs

### Mission

A **Mission** is the bounded objective for one runtime execution. It states the intended outcome, scope, acceptance criteria, deliverables, constraints and completion report expectations.

A Mission must not redefine canonical architecture terms. If the Mission requires a new concept, the agent must either use an existing CIOS term, identify the owning document to update or propose an ADR.

### Research Policy

A **Research Policy** is the declared behavioural mode governing research depth, source-seeking posture, assurance burden, stop rule and escalation threshold for the Mission.

Canonical Research Policies are:

| Policy | Behavioural intent |
| --- | --- |
| Discovery | Rapidly understand the problem, surface candidate concepts, identify uncertainties and avoid premature architectural commitment. |
| Research | Build a sufficiently evidenced view, create or update Observations where appropriate and preserve Unknowns and Contradictions. |
| Decision | Support an explicit architectural, commercial or product decision with traceable rationale, alternatives, consequences and boundaries. |
| Assurance | Validate conformance, conflicts, lineage, terminology, authority and release readiness without weakening existing doctrine. |

Research Policy does not redefine Evidence. Evidence remains attributable proof from permissible sources under the Evidence Acquisition Standard and related source-quality doctrine.

### Capability Profile

A **Capability Profile** is the declared set of runtime abilities, tools, permissions, model affordances, environment constraints and output channels available to the agent for the Mission.

Capability Profile is descriptive and operational. It does not grant architecture authority. A capable runtime may still be prohibited from making canonical changes without the relevant reviewed and merged repository artefact.

## Runtime Context

A **Runtime Context** is the assembled, execution-time configuration composed of:

1. Mission;
2. Research Policy;
3. Capability Profile;
4. applicable repository instructions and authority documents;
5. current workspace state;
6. explicit human constraints for the run.

Runtime Context is not durable knowledge. It may affect what an agent does during a run, but it must not silently write new doctrine, promote candidate intelligence into canonical fact or alter the meaning of Evidence, Observation, Enterprise Model or Enterprise Knowledge Graph objects.

## Runtime Pipeline

The canonical runtime pipeline is:

```text
Mission
+ Research Policy
+ Capability Profile
+ Repository and authority context
→ Runtime Context
→ Planning
→ Evidence and knowledge acquisition within policy
→ Observation or model update where authorised
→ Reasoning and synthesis
→ Validation against doctrine and acceptance criteria
→ Reviewed repository artefact or completion output
```

The pipeline is layered above the Enterprise Intelligence Runtime. It configures agent execution; it does not replace the Source, Evidence, Observation, Knowledge, Reasoning, Presentation, Knowledge Pack or Flora runtime architectures.

## Relationship to Existing Doctrine

- **Evidence remains universal.** Runtime Policy can determine how aggressively an agent seeks evidence, but it cannot change what counts as Evidence.
- **Observation remains universal.** Runtime configuration can decide whether Observation creation is in scope, but it cannot change Observation semantics or lifecycle doctrine.
- **Knowledge Graph remains universal.** Runtime configuration can scope graph queries or proposed graph updates, but it cannot change graph ownership, relationship semantics or canonical-memory rules.
- **Enterprise Model remains durable memory.** Runtime outputs are not Enterprise Model state unless accepted through the owning model process.
- **Runtime configuration does not modify doctrine.** Doctrine changes require reviewed and merged repository artefacts governed by Accepted ADRs and owning architecture papers.
- **Provider output remains candidate.** Capability Profile may include provider tools, but provider output is not canonical intelligence by default.

## Architectural Consequences

- Every AI mission has an explicit runtime contract before execution.
- Mission-specific instructions are separated from durable CIOS knowledge architecture.
- Research depth and assurance burden become governable without duplicating Evidence or Observation doctrine.
- Tool availability and model capability are visible as runtime facts rather than hidden assumptions.
- Runtime reasoning can be audited against the policy under which it was produced.
- Architecture evolution remains repository-mediated: no architectural decision becomes authoritative until represented by a reviewed and merged repository artefact.

## Alternatives Considered

### Encode mission rules in durable knowledge objects

Rejected. It would pollute Enterprise Models, Observations or Knowledge Graph state with run-specific instructions and make durable memory dependent on temporary execution context.

### Treat Research Policy as Evidence doctrine

Rejected. Research Policy controls behaviour during a mission; Evidence doctrine defines proof. Combining them would weaken the universality of Evidence.

### Infer capability from the agent implementation

Rejected. Hidden tool and model assumptions make audits difficult and can cause two agents with the same Mission to produce incomparable outputs.

### Leave runtime context implicit in prompts

Rejected. CIOS requires inspectable governance. Important mission, policy and capability choices must be explicit enough to review.

## Compliance

A compliant CIOS AI-agent Mission must:

1. declare or inherit a Mission;
2. declare or inherit a Research Policy;
3. declare or inherit a Capability Profile;
4. preserve Evidence, Observation, Enterprise Model and Knowledge Graph doctrine;
5. label Unknowns, Contradictions, human-supplied knowledge, inference and recommendation lineage;
6. validate terminology against the Glossary;
7. record material architecture changes as reviewed and merged repository artefacts before treating them as authoritative.

## Implementation Notes

- `CIOS-AI.md` is the default repository-level AI runtime guidance.
- The Document Map should list ADR-015 as the owning decision for Runtime Context, Mission, Research Policy and Capability Profile.
- Runtime templates may specialise policy defaults, but they must reference this ADR rather than duplicate doctrine.
- Future runtime implementations may persist runtime execution metadata for audit, but persistence of metadata does not make runtime configuration part of canonical Enterprise Intelligence memory.
