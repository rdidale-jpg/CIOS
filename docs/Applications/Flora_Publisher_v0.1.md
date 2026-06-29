# Flora Publisher v0.1

## Purpose

Flora Publisher v0.1 turns the existing deterministic Flora intelligence engine into an executive publishing workflow. It produces a professional Morning Edition briefing as PDF and matching local HTML for daily iPad consumption.

The publisher does **not** use external APIs, LLMs or databases. It reuses seeded Flora daily briefs, weekly movement logic and governed local commercial evidence.

## Morning Edition

Run from the repository root:

```bash
python -m cios.applications.flora.publisher.morning_edition
```

The command creates:

- `.flora_pilot/publications/Morning_Edition_YYYY-MM-DD.pdf`
- `.flora_pilot/publications/Morning_Edition_YYYY-MM-DD.html`
- `.flora_pilot/publications/VERSION.json`
- `.flora_pilot/publications/index.html`
- `.flora_pilot/publications/assets/flora_publisher.css`

The PDF contains nine executive pages:

1. Cover page with title, date, reading time, version and pilot confidentiality marker.
2. Executive Summary with no more than five bullets.
3. Today's Priority Opportunity.
4. Top Five Organisations.
5. Emerging Commercial Conditions.
6. Executive & Market Movements.
7. Competitive Intelligence for IBM, Accenture, Capgemini and Deloitte using only seeded deterministic observations.
8. Recommended Actions.
9. Teach Flora placeholders.

Every page includes the Flora Pilot footer, publisher version, generated timestamp and page number.

## Weekly Edition roadmap

`cios.applications.flora.publisher.weekly_edition` is currently a roadmap placeholder. A future weekly edition should reuse `generate_weekly_brief()` and publish week-on-week movement, new evidence, accounts to watch and deprioritisation guidance in the same PDF/HTML architecture.

## Publication architecture

The publisher package is located at `cios/applications/flora/publisher/`:

- `morning_edition.py` builds the deterministic publication context, writes the manifest and index, and coordinates output generation.
- `pdf_renderer.py` uses ReportLab to render the executive PDF.
- `html_renderer.py` renders matching local HTML and relative CSS.
- `weekly_edition.py` documents the future weekly command surface.
- `assets/` and `templates/` are reserved for publisher-owned static assets and templates.

## Output locations

By default, publications are written to:

```text
.flora_pilot/publications/
```

For tests or isolated pilot runs, set `FLORA_PILOT_DIR` to redirect the root pilot directory.

## Running commands

Generate the Morning Edition:

```bash
python -m cios.applications.flora.publisher.morning_edition
```

Run validation:

```bash
pytest -q
python -m cios.applications.flora.publisher.morning_edition
git diff --check
```

## Pilot workflow

1. Run the Morning Edition command each morning.
2. Open the generated PDF on an iPad or desktop PDF reader.
3. Open `index.html` to browse generated publications locally.
4. Use page 9, Teach Flora, to capture pilot learning manually.
5. Validate any recommended action against sponsor, funding, timing and competitor evidence before commercial escalation.

## Future cloud publishing

Future cloud publishing can add authenticated storage, scheduled generation and controlled distribution. Those capabilities should preserve deterministic provenance and the current separation between intelligence generation, rendering and publication indexing.
