# CIOS Architecture

## Architectural Intent

CIOS is a platform, not a single application.

The first application is the Commercial Opportunity Intelligence Assistant, but the underlying platform should remain reusable for future commercial intelligence use cases.

## Layered Architecture

```text
Applications
    ↓
Agent Society
    ↓
Commercial Decision Engine
    ↓
Commercial Reasoning Language
    ↓
Commercial Knowledge Graph
    ↓
Commercial Ontology
    ↓
Enterprise Data
```

## Core Modules

| Module | Purpose |
|---|---|
| `ontology/` | Defines core commercial entities and concepts. |
| `graph/` | Stores and retrieves commercial relationships. |
| `reasoning/` | Implements Commercial Reasoning Language structures. |
| `decision_engine/` | Executes reasoning and produces recommendations. |
| `agents/` | Contains specialist agent behaviours. |
| `scoring/` | Implements scoring models such as Transformation Pressure. |
| `memory/` | Stores decisions, evidence and learning history. |
| `app/` | Hosts user-facing application logic. |
| `tests/` | Contains validation tests. |
| `data/` | Stores sample data and fixtures. |

## MVP-001 Architecture

```text
Opportunity Input
      ↓
Input Parser
      ↓
Scoring Engine
      ↓
Reasoning Engine
      ↓
Decision Engine
      ↓
Recommendation Output
      ↓
Evidence Trail
```

## First Engineering Goal

Create a command-line prototype that can read a structured opportunity file and produce:

- opportunity summary
- Transformation Pressure score
- key risks
- win themes
- recommended next actions
- evidence trail
