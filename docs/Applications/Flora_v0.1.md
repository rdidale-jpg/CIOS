# Flora v0.2 — Flora Intelligence Engine

## Purpose

Flora is a deterministic CIOS Commercial Intelligence application for identifying organisations where AI-enabled reinvention may be timely, valuable and commercially actionable. Sprint 2 upgrades Flora from a signal-scoring prototype into an explainable assessment engine while preserving the existing SDK-style application architecture.

Flora v0.2 does **not** use LLMs, external APIs or databases. All intelligence remains seeded and repeatable for local validation.

## Assessment model

Each ranked organisation now carries an `IntelligenceAssessment` with:

- `assessment_id`
- `organisation`
- `assessment_date`
- `commercial_summary`
- `why_now`
- `why_this_capability`
- `why_this_proposition`
- `why_this_executive`
- `competitive_context`
- `confidence`
- `missing_evidence`
- `supporting_patterns`
- `supporting_playbooks`
- `supporting_propositions`
- `evidence`
- `recommended_actions`

The assessment connects deterministic scores, seeded signals, commercial patterns, sector/capability/executive playbooks and propositions into a single explainable object.

## Evidence model

Each assessment includes seeded `EvidenceItem` objects with:

- `source_name`
- `source_type`
- `publication_date`
- `evidence_summary`
- `related_signal`
- `confidence`

Evidence is generated from the seeded Flora signals. The `related_signal` field preserves traceability back to the signal that contributed to the assessment.

## Explainability

Every recommended action answers:

- Why this organisation?
- Why now?
- Why this capability?
- Why this executive?
- Why this proposition?
- Why this action?

The same recommendation also names the Commercial Pattern, Sector Playbook, Capability Playbook, Executive Playbook and Proposition used to shape the action.

## Missing evidence

Flora v0.2 explicitly exposes evidence gaps so users do not confuse seeded hypotheses with confirmed pursuit intelligence. Initial gaps include:

- Funding not confirmed
- Executive sponsor unknown
- Procurement timing unknown
- Competitor engagement unknown

## Weekly Intelligence Brief

In addition to the daily assessment brief, Flora supports a Weekly Intelligence Brief containing:

- biggest movers
- score changes
- new evidence
- organisations to watch
- organisations to deprioritise

Weekly score movement is deterministic and seeded; it is intended to validate report shape before live connectors are introduced.

## How to run

Human-readable assessment brief:

```bash
python -m cios.applications.flora.main
```

Weekly brief:

```bash
python -m cios.applications.flora.main --weekly
```

Structured JSON briefing:

```bash
python -m cios.applications.flora.main --json
```

Run tests:

```bash
pytest -q
```

## Future live evidence connectors

Future versions may add governed connectors for approved internal CRM, market intelligence, procurement, account-planning or public-source feeds. Those connectors should populate the same evidence model, retain source and publication metadata, preserve confidence scoring and keep missing-evidence gaps visible. No connector should bypass deterministic validation or introduce opaque recommendation logic.

## Governed Blueprint Import product workflow

Normal authorised users import Commercial Digital Twin Blueprint packages through Flora, not through PowerShell, shell scripts, repository checkout, or manual `FLORA_DATA_DIR` configuration.

1. Open Flora.
2. Choose **Import Blueprint** at `/blueprint-import`.
3. Select the Blueprint ZIP from the local computer with the file chooser.
4. Review the validation result, checksum, discovered files, workbook/worksheet summary, warnings, errors, and accepted/quarantined/rejected/unsupported counts.
5. Review proposed canonical effects in plain language, including create/update/mapped/duplicate/conflict/unresolved/projection totals and important exceptions.
6. Explicitly approve with **Approve and update governed Twin**, including a rationale, or decline promotion.
7. Open the resulting Enterprise Canvas from the completion screen.

Flora preserves the original ZIP in governed runtime storage outside source control. Upload and validation do not create canonical intelligence; canonical promotion remains an explicit governed approval and execution step. Technical command-line operation remains an administrative fallback only.
