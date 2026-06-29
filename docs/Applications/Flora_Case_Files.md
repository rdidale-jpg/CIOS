# Flora Case Files — Commercial Evidence Engine and Living Commercial Case Files

## Purpose

Flora Case Files turn seeded scoring signals into governed Commercial Intelligence artefacts. A case file gives Sales Directors a deterministic view of organisational memory: evidence, timeline, insights, pressure profile, AI reinvention themes, competitive context, open validation questions and recommended actions.

Flora Case Files do **not** use LLMs, external APIs, live web collection or databases. Sprint 3 uses only seeded local Python resources and Markdown documentation.

## Architecture

The Sprint 3 package is `cios/applications/flora/intelligence/`:

- `evidence_engine.py` defines the first-class `CommercialEvidence` model, approved categories, seeded evidence and future connector protocols.
- `insight_engine.py` defines `CommercialInsight` and deterministic combination rules.
- `timeline.py` orders evidence and insight events chronologically.
- `case_file.py` builds `CommercialCaseFile` objects from seeded evidence, existing Flora assessments and Commercial DNA.
- `case_reporting.py` renders human-readable case files.

## Evidence model

`CommercialEvidence` records source metadata, publication date, title, summary, extracted observation, confidence, freshness and traceability to signals, patterns, playbooks, propositions, capability tags, executive tags and sector tags. Supported categories include annual reports, investor presentations, results announcements, regulatory publications, executive appointments, strategy updates, company news, industry news, hiring signals, technology investments and customer signals.

## Insight model

`CommercialInsight` combines multiple evidence items into one human-readable insight with supporting evidence IDs, patterns, assessments, confidence and a recommended next step. Insight generation is deterministic and rule-based.

## Commercial timeline

The timeline places every evidence item in publication-date order and then appends generated insights at the latest relevant evidence date. It provides a compact chronology for reviewing how commercial pressure and AI-reinvention hypotheses developed.

## Commercial narrative

Each case file includes a concise deterministic executive summary of no more than 400 words. It describes the current commercial situation, key capability themes and validation needs for a Sales Director.

## Future live evidence connectors

Sprint 3 designs dependency-injection-friendly connector contracts only. Future implementations may provide annual report, investor presentation, regulator, company news and hiring signal connectors. Any future connector must populate `CommercialEvidence`, preserve source metadata, expose confidence and freshness, avoid opaque reasoning and remain optional to the seeded local engine.
