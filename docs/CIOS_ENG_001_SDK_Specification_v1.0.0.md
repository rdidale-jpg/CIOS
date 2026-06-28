# CIOS-ENG-001 – Software Development Kit (SDK) Specification

**Version:** 1.0.0  
**Phase:** Genesis Sprint 1  
**Status:** Approved for Codex implementation  

## 1. Executive Summary

This specification defines the first software development kit for the Commercial Intelligence Operating System (CIOS). The SDK is the reusable Python foundation from which the first CIOS application, the Commercial Opportunity Intelligence Assistant, will be built.

CIOS is a platform, not a single application. The Opportunity Intelligence Assistant is the first application built on that platform.

## 2. SDK Purpose and Scope

The SDK provides reusable software primitives for representing commercial knowledge, reasoning, decisions, evidence, memory and agents.

In scope for Sprint 1:

- Core models
- Basic ontology primitives
- Basic graph primitives
- Reasoning structures
- Decision engine interface
- Test foundation

## 3. Target Repository Structure

```text
CIOS/
├── cios/
│   ├── core/
│   ├── ontology/
│   ├── graph/
│   ├── reasoning/
│   ├── decision_engine/
│   ├── memory/
│   ├── agents/
│   ├── applications/
│   └── utils/
├── tests/
├── data/
├── docs/
├── README.md
├── ARCHITECTURE.md
├── ROADMAP.md
├── pyproject.toml
└── requirements.txt
```

## 4. Module Responsibilities

| Module | Responsibility | May Depend On |
|---|---|---|
| `cios.core` | Foundational data models, identifiers, timestamps, validation and common types | None |
| `cios.ontology` | Commercial entity and capability definitions | core |
| `cios.graph` | Relationships, evidence links and graph store interfaces | core, ontology |
| `cios.reasoning` | Commercial Reasoning Language structures | core |
| `cios.decision_engine` | Orchestrates reasoning, scoring and recommendations | core, reasoning, graph, scoring |
| `cios.memory` | Stores decisions, assessments and learning history | core, graph |
| `cios.agents` | Specialist agent interfaces and behaviours | core, reasoning, decision_engine |
| `cios.applications` | Application-specific logic | all platform modules |

## 5. Dependency Rules

- `core` must not import from any other CIOS module.
- `ontology` may import from `core` only.
- `graph` may import from `core` and `ontology`.
- `reasoning` may import from `core` only during early implementation.
- `decision_engine` may import from `core`, `graph`, `reasoning` and `scoring`.
- `agents` may import from `core`, `reasoning` and `decision_engine`.
- `applications` may import from all platform modules.
- `tests` may import any module.
- No module should perform hidden network calls during MVP-001.

Allowed dependency direction:

```text
applications → agents → decision_engine → reasoning/scoring/graph → ontology → core
```

## 6. Core Data Model Strategy

The first implementation should use Pydantic models.

| Model | Purpose |
|---|---|
| Entity | Generic object in the CIOS universe |
| Relationship | Connection between two entities |
| Evidence | Source material supporting a claim |
| Observation | A detected commercial signal |
| Recommendation | A proposed action |
| Decision | A decision object with rationale |
| Opportunity | Commercial opportunity being assessed |
| Capability | Reusable organisational capability |

## 7. Testing Strategy

- Use pytest.
- Keep tests small and readable.
- Test object construction and validation.
- Add behavioural tests only once services are created.
- Tests should run without external services.

## 8. Codex Working Instructions

Codex should behave like a cautious software engineer.

- Read `README.md`, `ARCHITECTURE.md` and `ROADMAP.md` before coding.
- Make one conceptual change per task.
- Show files changed, git status, diff summary and test results.
- Do not invent large frameworks without approval.
- Prefer package structure under `cios/`.

## 9. Sprint 1 Implementation Plan

| Step | Task | Output | Success Criteria |
|---|---|---|---|
| 1 | Create cios package | `cios/__init__.py`, `cios/core/` | Package imports successfully |
| 2 | Create core models | `cios/core/models.py` | Pydantic models instantiate |
| 3 | Create model tests | `tests/test_core_models.py` | pytest passes |
| 4 | Update docs if needed | architecture docs | docs match structure |
| 5 | Create pull request | PR into main | reviewable changes |

## 10. Acceptance Criteria

- Repository contains a `cios` Python package.
- Core module contains foundational Pydantic models.
- Tests verify every foundational model can be instantiated.
- Test suite runs successfully with pytest.
- Implementation is committed via pull request.
- No application logic is introduced before core models are stable.

## 11. Next Codex Prompt

```text
Create CIOS Core v0.1.

First, ensure your workspace is based on the latest GitHub main branch.

Create a Python package named cios with this structure:

cios/
  __init__.py
  core/
    __init__.py
    models.py

In cios/core/models.py, define foundational Pydantic models for:
- Entity
- Relationship
- Evidence
- Observation
- Recommendation
- Decision
- Opportunity
- Capability

Use Python 3.11+ typing and Pydantic v2.

Also create:
tests/test_core_models.py

The tests should verify that each model can be instantiated with sensible sample data.

Do not build the full Opportunity Intelligence Assistant yet.
Do not add external services.
Do not change README.md unless necessary.

After making the changes:
1. show the files created,
2. show git status,
3. show the diff summary,
4. run pytest if possible,
5. commit the changes with message: Add CIOS Core data models,
6. create a pull request into main.
```
