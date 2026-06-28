# CIOS Applications

Applications are the composition layer for complete CIOS workflows. They assemble platform modules into runnable, testable flows while keeping platform primitives owned by the platform packages.

## Composition Role

Applications may orchestrate modules such as:

- `cios.core` for evidence, observations, recommendations, confidence, and shared base models;
- `cios.ontology` for domain entities;
- `cios.graph` for knowledge graph records and evidence links;
- `cios.reasoning` for signals, hypotheses, inferences, explanations, and traces;
- `cios.scoring` for scoring models, components, bands, and results;
- `cios.decision_engine` for formal decisions, criteria, assessments, rationales, and options;
- `cios.memory` for passive persistence of completed artefacts.

Applications may provide workflow-specific input loading, mapping, deterministic rules, policy configuration, reporting, and pipeline orchestration.

## Boundary Rule

Applications may orchestrate platform modules, but they must not redefine platform primitives. For example, an application can create and connect `Evidence`, `KnowledgeGraphRecord`, `ReasoningTrace`, `ScoringResult`, `DecisionOutput`, and memory records, but it must not create alternate application-local versions of those primitives.

Applications should preserve traceability identifiers across composed artefacts and should keep runtime side effects behind explicit entry points.

## Reference Implementation

`cios/applications/opportunity_assistant/` is the reference implementation for the application composition pattern. It demonstrates how an application package composes evidence, ontology, graph, reasoning, scoring, decision, explainability, reporting, and optional passive memory persistence without changing platform module ownership.

See `docs/Engineering/CIOS_ENG_004_Application_Composition_Standard_v0.1.0.md` for the formal standard.
