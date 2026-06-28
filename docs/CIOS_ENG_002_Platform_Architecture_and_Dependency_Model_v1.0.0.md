# CIOS-ENG-002 – Platform Architecture & Dependency Model

**Version:** 1.0.0  
**Status:** Accepted Architecture Baseline  
**Phase:** Genesis  
**Primary Use:** GitHub/Codex engineering guidance and implementation control

## 1. Purpose

This document converts the Codex SDK architecture review into an accepted CIOS engineering baseline. It defines the authoritative package layout, dependency model, module ownership rules, and implementation guardrails for the first build phase of the Commercial Intelligence Operating System.

The purpose is practical: Codex should use this document before writing code. It prevents the first implementation from drifting into a one-off Opportunity Assistant and keeps CIOS on a reusable platform path.

## 2. Accepted Decisions

| ID | Decision | Status |
|---|---|---|
| CIOS-ENG-002-DEC-001 | Use `cios/` as the authoritative Python package root. | Accepted |
| CIOS-ENG-002-DEC-002 | Add `cios.scoring` as a first-class module. | Accepted |
| CIOS-ENG-002-DEC-003 | Represent dependencies as a DAG, not a single chain. | Accepted |
| CIOS-ENG-002-DEC-004 | Keep memory passive; it persists records but does not orchestrate decisions. | Accepted |
| CIOS-ENG-002-DEC-005 | Remove or tightly constrain `utils`; do not allow it to become a dumping ground. | Accepted |
| CIOS-ENG-002-DEC-006 | Keep Opportunity, Capability and Relationship provisional if initially placed in core. | Accepted with guardrail |

## 3. Authoritative Package Layout

The CIOS SDK shall use a package-root layout under `cios/`. Existing top-level folders created during bootstrap are retained temporarily as repository scaffolding but are not the long-term implementation package boundary.

```text
cios/
  __init__.py

  core/
    __init__.py
    models.py
    identifiers.py        # later
    types.py              # later
    validation.py         # later
    time.py               # later

  ontology/
    __init__.py

  graph/
    __init__.py

  reasoning/
    __init__.py

  scoring/
    __init__.py

  decision_engine/
    __init__.py

  memory/
    __init__.py

  agents/
    __init__.py

  applications/
    __init__.py
```

## 4. Dependency Model

CIOS shall use a directed acyclic dependency graph. Modules may depend downward or sideways only where explicitly permitted. Circular dependencies are prohibited.

```text
core
├── ontology
│   └── graph
├── reasoning
├── scoring
├── memory
└── decision_engine
    └── agents
        └── applications

Composition rule:
decision_engine may compose core + ontology + graph + reasoning + scoring.
applications may compose all platform modules.
memory remains passive and is called by applications or explicit persistence services.
```

## 5. Module Ownership Rules

| Module | Owns | May Depend On |
|---|---|---|
| `cios.core` | Universal primitives, IDs, evidence, observations, decisions, recommendations. | None from `cios.*` |
| `cios.ontology` | Commercial domain concepts: Opportunity, Capability, Customer, Competitor, Supplier, Contract. | core |
| `cios.graph` | Relationships, evidence links, graph edge primitives and graph access interfaces. | core, ontology |
| `cios.reasoning` | Commercial Reasoning Language primitives and reasoning traces. | core |
| `cios.scoring` | Score types, scoring interfaces, Transformation Pressure and future scoring models. | core; reasoning later if needed |
| `cios.decision_engine` | Decision orchestration and recommendation formation. | core, ontology, graph, reasoning, scoring |
| `cios.memory` | Persistence of decisions, assessments, evidence, outcomes and learning history. | core, graph; no orchestration |
| `cios.agents` | Agent interfaces, roles, inputs, outputs and behaviours. | core, reasoning, decision_engine |
| `cios.applications` | Specific user-facing applications such as Opportunity Intelligence Assistant. | all platform modules |

## 6. Core Model Ownership Guardrail

The first implementation may define the eight Sprint 1 models in `cios.core.models` to keep the change small and testable. This is a tactical compromise, not permanent ownership.

| Model | Initial Location | Long-Term Ownership |
|---|---|---|
| Entity | core | core |
| Evidence | core | core |
| Observation | core | core or reasoning |
| Recommendation | core | core or decision_engine |
| Decision | core | core or decision_engine |
| Relationship | core, provisional | graph |
| Opportunity | core, provisional | ontology |
| Capability | core, provisional | ontology |

## 7. Memory Rule

Memory is passive persistence. It stores and retrieves CIOS records. It must not call agents, invoke workflows, perform scoring, or make decisions. In early releases, applications decide whether to persist outputs. This avoids circular dependencies between memory, agents and the decision engine.

## 8. Utils Rule

A generic `cios.utils` package shall not be created during Sprint 1. Common reusable functions should live in specific core modules such as `identifiers.py`, `types.py`, `validation.py` or `time.py`. If `utils` is later introduced, it may depend only on the Python standard library and approved third-party packages. It must not import from `cios.*`.

## 9. Documentation Alignment Rule

The first implementation PR that creates the `cios/` package should update `README.md` and `ARCHITECTURE.md` only where necessary to align them with the `cios/` package-root architecture. Documentation updates should be small and directly related to the implementation change.

## 10. Sprint 1 Implementation Scope

Sprint 1 may:

- Create the `cios/` package root.
- Create `cios/core/models.py`.
- Define minimal Pydantic models for the eight foundational Sprint 1 models.
- Create `tests/test_core_models.py`.
- Add lightweight construction, serialization and required-field validation tests.

Sprint 1 must not:

- Build Opportunity Assistant application logic.
- Introduce graph databases.
- Introduce service containers.
- Introduce plugin systems.
- Introduce web frameworks.
- Introduce agent frameworks.

## 11. Next Codex Implementation Prompt

Use the following prompt as the next instruction to Codex.

```text
Create CIOS Core v0.1 using the accepted architecture baseline in docs/Engineering/CIOS_ENG_002_Platform_Architecture_and_Dependency_Model_v1.0.0.md.

First, make sure your working branch is up to date with main.

Create a new Python package root:
cios/

Inside it create:
cios/__init__.py
cios/core/__init__.py
cios/core/models.py

In cios/core/models.py, define minimal Pydantic v2 models for:
- Entity
- Relationship
- Evidence
- Observation
- Recommendation
- Decision
- Opportunity
- Capability

Important architectural guardrail:
Opportunity, Capability and Relationship are provisional core models for Sprint 1 only. Add code comments noting that Opportunity and Capability may later migrate to cios.ontology and Relationship may later migrate to cios.graph.

Use Python 3.11+ typing.
Use Field(default_factory=...) for mutable defaults.
Use timezone-aware datetime defaults where timestamps are needed.
Keep models thin and serializable.
Do not build application logic.
Do not create a web UI.
Do not introduce databases or external services.

Create:
tests/test_core_models.py

Tests should verify:
1. each model can be instantiated with sample data;
2. models can be serialized to dictionaries;
3. at least one simple required-field validation failure is tested.

If needed, make only minimal README.md or ARCHITECTURE.md updates to align the repo with the cios/ package-root layout.

After changes:
1. show files created;
2. show git status;
3. show diff summary;
4. run pytest if possible;
5. commit with message: Add CIOS Core data models;
6. create a pull request.
```

## 12. Acceptance Criteria

- The repository contains a `cios/` Python package root.
- The `cios.core` module contains minimal reusable Pydantic models.
- No application-specific logic is implemented in Sprint 1.
- Tests pass locally or Codex reports clearly why they could not be run.
- `README.md` and `ARCHITECTURE.md` are not materially rewritten, only aligned where necessary.
- The pull request is small, reviewable and traceable to CIOS-ENG-002.

## 13. Summary

CIOS-ENG-002 establishes the accepted platform architecture before implementation begins. The immediate next step is to build CIOS Core v0.1 as a small, testable SDK foundation. This keeps the project moving from architecture to software while avoiding early structural debt.
