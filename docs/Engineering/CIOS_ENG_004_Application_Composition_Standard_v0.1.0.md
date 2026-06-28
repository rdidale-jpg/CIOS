# CIOS-ENG-004 – Application Composition Standard

**Version:** 0.1.0  
**Status:** Draft Engineering Standard  
**Repository target:** `docs/Engineering/`  
**Reference implementation:** `cios/applications/opportunity_assistant/`

## 1. Purpose

This standard defines the reusable application composition pattern established by the Opportunity Assistant. A CIOS application is a thin, deterministic composition layer that assembles platform primitives into a complete workflow without redefining those primitives.

Applications may own workflow-specific mapping, orchestration, policy configuration, reporting, and tests. Platform modules remain the source of truth for shared concepts such as evidence, ontology records, graph records, reasoning traces, scores, decisions, recommendations, and memory records.

## 2. Application Package Structure

Each application should live under `cios/applications/<application_name>/` and use a package name that describes the workflow domain. The Opportunity Assistant uses this structure:

```text
cios/applications/opportunity_assistant/
├── __init__.py
├── input.py
├── ontology_mapping.py
├── graph_mapping.py
├── rules.py
├── observation_mapping.py
├── reasoning_mapping.py
├── scoring_policy.py
├── decision_policy.py
├── explainability.py
├── memory_mapping.py
├── reporting.py
├── pipeline.py
├── main.py
└── sample_opportunity.json
```

Applications may add domain fixtures, sample data, or additional mapping modules when needed, but the package must remain recognisably compositional: modules should map, orchestrate, configure policy, render output, or persist passive snapshots.

## 3. Required Modules

A production application package should provide the following modules unless a documented exception explains why a module is not needed:

| Module | Responsibility |
|---|---|
| `__init__.py` | Expose only the stable public application entry points. |
| `input.py` | Load or normalise structured inputs and create `cios.core.Evidence` records. |
| `ontology_mapping.py` | Map source data into `cios.ontology` models. |
| `graph_mapping.py` | Map ontology and evidence artefacts into `cios.graph` records. |
| `rules.py` | Detect deterministic domain conditions without external services. |
| `observation_mapping.py` | Convert detections or source facts into `cios.core.Observation` records. |
| `reasoning_mapping.py` | Create reasoning signals, hypotheses, inferences, explanations, traces, and results using `cios.reasoning`. |
| `scoring_policy.py` | Hold inspectable deterministic scoring policy and create `cios.scoring` outputs. |
| `decision_policy.py` | Hold inspectable deterministic decision policy and create `cios.decision_engine` outputs. |
| `explainability.py` | Link recommendations back to evidence, rules, observations, reasoning, and scores. |
| `memory_mapping.py` | Persist passive memory snapshots when a repository is supplied. |
| `reporting.py` | Render application-specific human-readable reports without changing canonical artefacts. |
| `pipeline.py` | Orchestrate the application lifecycle and return a typed result object. |
| `main.py` | Optional console entry point for deterministic local execution. |

## 4. Composition Boundary Rules

1. Applications compose platform modules; they do not become platform modules.
2. Applications may call `cios.core`, `cios.ontology`, `cios.graph`, `cios.reasoning`, `cios.scoring`, `cios.decision_engine`, and `cios.memory` through their public model and repository interfaces.
3. Applications must preserve platform artefact identifiers across the lifecycle so downstream scores, decisions, recommendations, explanations, and memory records can trace back to evidence.
4. Applications may define application-specific result wrappers, mappings, rule detections, policy models, and report models when those wrappers describe workflow composition rather than new platform primitives.
5. Applications must keep orchestration in the application package. Platform modules must not import application packages.
6. Applications must not introduce global side effects during import. Pipeline execution should occur only through explicit entry points such as `run_pipeline()` or `main()`.
7. Applications should accept explicit policy instances and dependency arguments where practical so policy and persistence can be inspected or tested independently.

## 5. Policy Module Rules

Policy modules make deterministic scoring or decision behaviour inspectable and replaceable without changing the pipeline shape.

- Policy classes should be plain typed models or simple deterministic classes.
- Policy defaults may be exported as module constants for convenience.
- Policy modules may reference application rules and platform primitives.
- Scoring policy must remain separate from rule detection. A rule detection states whether a condition is present; a scoring policy assigns quantitative meaning to that condition.
- Decision policy must remain separate from scoring. A score informs an assessment, but formal recommendations must be emitted through the decision engine models.
- Policy methods must include evidence, reasoning, scoring, and graph identifiers in produced artefacts where those links are available.
- Policy modules must not call LLMs, agents, remote APIs, databases, background workers, or external services.

## 6. Memory Usage Rules

Memory is passive in application composition.

- Applications may persist memory records only after the relevant pipeline artefacts already exist.
- Memory mapping must store snapshots, references, and traceability metadata; it must not make decisions, change scores, invoke reasoning, or mutate the completed result.
- Pipeline execution must remain valid without a memory repository.
- Memory dependencies should be injected into the pipeline entry point, not created implicitly inside the application.
- Platform memory modules must not import application modules.

## 7. Explainability Requirements

Every application that produces recommendations must also provide machine-readable explainability links.

Explainability output should include, where applicable:

- recommendation identifiers and titles;
- supporting evidence identifiers;
- supporting observation identifiers and statements;
- triggered rule names and stable rule identifiers;
- reasoning trace identifiers and reasoning step identifiers;
- score identifiers and score values used by the recommendation;
- decision confidence or equivalent confidence metadata.

Explainability reports should be generated from existing pipeline artefacts. They must not perform hidden inference or introduce new evidence.

## 8. Testing Requirements

Application tests must prove the composition boundary, not only the final happy path.

Required test coverage includes:

1. end-to-end pipeline execution from input to recommendation;
2. typed result object creation;
3. evidence-to-observation-to-reasoning-to-score-to-decision traceability;
4. independent inspection of scoring and decision policy modules;
5. behaviour with and without an injected memory repository;
6. passive memory persistence contents when memory is provided;
7. explainability report creation for each recommendation;
8. negative or low-signal fixtures that prove absent rules do not fire;
9. forbidden dependency checks where a platform module is at risk of importing application code.

Tests must not require network access, external services, databases, LLM credentials, or UI automation for deterministic application composition.

## 9. Forbidden Imports and Behaviours

Applications and platform modules must preserve these dependency rules:

- `cios.memory` must not import `cios.reasoning`, `cios.scoring`, `cios.decision_engine`, `cios.agents`, or `cios.applications`.
- Platform modules such as `cios.core`, `cios.ontology`, `cios.graph`, `cios.reasoning`, `cios.scoring`, and `cios.decision_engine` must not import `cios.applications`.
- Application modules must not redefine platform primitives such as `Evidence`, `Observation`, `Recommendation`, ontology entities, graph records, reasoning traces, scores, decision outputs, or memory records.
- Application modules must not bypass `cios.decision_engine` when producing formal decisions or recommendations.
- Application modules must not write to memory as a substitute for returning typed pipeline results.
- Application imports must not execute pipelines, mutate repositories, open network connections, start background jobs, or read/write external state beyond module constants.
- Applications must not add Agents, LLMs, APIs, UI frameworks, databases, or external services unless a future approved standard explicitly changes this boundary.

## 10. Reference Implementation Notes

The Opportunity Assistant is the reference implementation for this standard. It demonstrates a deterministic composition pipeline that loads structured input, creates evidence, maps ontology and graph records, detects rules, maps observations and reasoning, applies inspectable scoring and decision policies, creates explainability links, optionally persists passive memory records, and returns a typed pipeline result.

Future applications should start from this pattern and diverge only where their workflow requires a documented module-level exception.
