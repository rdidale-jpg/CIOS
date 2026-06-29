# Flora Pilot Workspace v0.3

## Purpose

Flora Pilot Workspace v0.3 is a lightweight local browser interface for the Flora Commercial Intelligence pilot. It turns the deterministic Flora daily brief, weekly movement logic and Living Commercial Case Files into a morning workspace Rob can use without leaving the local machine.

The workspace is designed for daily habit formation: fewer screens, clearer recommendations, visible evidence and fast feedback capture.

## How to run

From the repository root:

```bash
python -m cios.applications.flora.workspace.app
```

The server prints a local URL, by default:

```text
http://127.0.0.1:8000
```

Open that URL in a browser. Stop the server with `Ctrl+C`.

## Pilot workflow

1. Open the Morning Edition.
2. Review what changed, why it matters and the recommended priority action.
3. Scan the watchlist for movement and priority.
4. Open the relevant case file.
5. Review the explainability panel before taking action.
6. Capture recommendation feedback or a Pilot Logbook entry in seconds.

## Morning Edition

The landing page is an executive briefing headed **Good Morning Rob**. It shows the date, estimated reading time, top AI reinvention opportunities, biggest movers, new evidence count, organisations requiring attention, one recommended priority action and links into case files.

It answers three questions:

- What changed?
- Why does it matter?
- What should I do?

## Watchlist

The watchlist pane shows the seeded pilot organisations:

- Thames Water
- National Grid
- BT
- Vodafone
- Sky
- BBC
- SSE
- United Utilities

Each row shows organisation, sector, AI Reinvention Opportunity Score, movement and priority. Selecting an organisation opens its case-file page.

## Case Files

Case-file routes use slugs such as:

- `/case/ThamesWater`
- `/case/BT`

Each page uses the existing deterministic case-file generation logic and renders:

- Executive Summary
- Commercial DNA View
- Commercial Timeline
- Evidence Ledger
- Commercial Insights
- Pressure Profile
- AI Reinvention Assessment
- Capability Heatmap
- Competitive Context
- Open Intelligence Questions
- Recommended Actions

## Teach Flora feedback

Each recommended action includes lightweight feedback buttons:

- Useful
- Not useful
- I acted
- Needs correction

Feedback is appended locally as JSON Lines. No database is used.

## Pilot Logbook

The **Teach Flora / Pilot Logbook** page lets Rob record:

- biggest insight
- biggest miss
- action taken
- what Flora should learn
- Flora Value Score from 0 to 5

Entries are appended locally as JSON Lines.

## Local storage

Runtime pilot data is stored in the ignored local directory:

```text
.flora_pilot/
```

Files created by the workspace:

- `.flora_pilot/feedback.jsonl`
- `.flora_pilot/logbook.jsonl`

The storage location can be overridden for tests or local experiments with `FLORA_PILOT_DIR`.

## Limitations

- Flora v0.3 remains deterministic and seeded.
- It does not call LLMs.
- It does not call external APIs.
- It does not use a database.
- Commercial DNA settings are read-only in this release.
- Case-file evidence remains pilot sample evidence, not live market intelligence.

## Future roadmap

- Editable local Commercial DNA JSON.
- Feedback review and export screen.
- Improved case-file navigation and filtering.
- Configurable watchlists.
- Richer evidence gap tracking.
- Optional authenticated deployment pattern if the pilot moves beyond local use.

## Flora Product Principles

- One screen, one decision.
- Evidence before opinion.
- Explain before recommendation.
- Capture learning in seconds.
- Fewer, better insights.
- Daily habit over feature count.
- Flora should always reduce uncertainty, never merely increase information.
