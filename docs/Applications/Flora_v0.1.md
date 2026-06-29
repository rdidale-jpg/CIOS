# Flora v0.1 — AI Reinvention Intelligence

## Purpose

Flora is a CIOS application for AI Reinvention Intelligence. It helps a commercial team identify target organisations where AI-enabled reinvention may be timely, valuable and commercially actionable.

## What v0.1 does

Flora v0.1 is a deterministic command-line application that:

- Defines Commercial DNA for an employer, business unit, target sectors, offerings, competitors, differentiators, reference clients and target geographies.
- Defines a target account watchlist with organisations, sectors, priorities, notes, incumbents and competitors.
- Defines seeded intelligence signals with source metadata, evidence text, confidence, strength, freshness and related capabilities.
- Calculates simple deterministic indices:
  - Commercial Pressure Index
  - AI Suitability Index
  - Organisational Readiness Index
  - Commercial Attractiveness Index
  - Influence Potential Index
  - AI Reinvention Opportunity Score
- Generates a Daily Intelligence Brief containing the top five organisations, reasons they are interesting, strongest signals, likely capability areas, competitors to watch and recommended next actions.

## What is mocked or seeded

Flora v0.1 does not call live news, CRM, market intelligence, LLM, database or web APIs. All Commercial DNA, watchlist accounts and signals are seeded in code for repeatable local execution. The sample data focuses on communications-sector adjacencies: utilities, energy, telecommunications, media and sport.

Seeded organisations include Thames Water, BT, National Grid, Sky, BBC, Vodafone, SSE and United Utilities. Seeded competitors include IBM, Accenture, Capgemini, Deloitte, KPMG, CGI, TCS, Infosys, Cognizant, Wipro and Sopra Steria.

## How to run

Human-readable briefing:

```bash
python -m cios.applications.flora.main
```

Structured JSON briefing:

```bash
python -m cios.applications.flora.main --json
```

Run tests:

```bash
pytest -q
```

## Future roadmap

Potential future increments:

1. Load Commercial DNA and watchlists from reviewed JSON or YAML files.
2. Add evidence traceability to platform evidence and reasoning artefacts.
3. Add configurable scoring weights and sector-specific scoring profiles.
4. Add approved internal data connectors once CIOS integration standards permit them.
5. Add persistent memory snapshots through the passive CIOS memory layer.
6. Add UI/API surfaces after the deterministic CLI workflow is stable.
7. Introduce carefully governed LLM summarisation only if a future standard approves it.

## Future roadmap note — Commercial Intelligence Playbooks

Future Flora versions will consume the Commercial Intelligence Playbook Library in `docs/CBOK/Playbooks/` to make recommendations more specific, evidence-backed and role-aware. Flora should use playbooks to connect signals, commercial pressure, AI reinvention potential, competitor hypotheses, stakeholder influence and Commercial DNA to context-specific next actions while preserving confidence and traceability.
