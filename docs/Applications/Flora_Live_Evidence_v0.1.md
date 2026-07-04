# Flora Live Evidence v0.1

## Purpose

Flora Live Evidence v0.1 replaces a purely seeded Morning Edition view with a small governed public-evidence pilot for Thames Water, National Grid, BT and Vodafone. It is intended to help Rob judge whether source-specific live public evidence improves the usefulness of Flora recommendations.

## Source registry

Configured sources live in `cios/applications/flora/live/source_registry.py`. Each source record contains a source ID, organisation, source name, source type, URL, sector, evidence tier, expected signal types and enabled flag.

## Live fetch approach

The collector fetches only configured source URLs. It uses Python standard-library `urllib`, bounded response sizes, HTML content-type checks, a clear user agent and short timeouts. It does not follow links into a crawl queue.

## Evidence extraction and interpretation

Extraction is deterministic keyword and phrase matching only. Matching snippets are mapped to commercial conditions, likely capabilities, AI reinvention relevance, confidence, source URL, evidence tier and extraction timestamp. Every recommendation can show a live evidence receipt with source name, URL, snippet, extraction date/time, condition mapping and missing evidence.

## Evidence tiers

- `tier_1_company`: official company investor, annual report or newsroom pages.
- `tier_1_regulator`: official regulator pages from Ofwat, Ofgem or Ofcom.

## How to run

```bash
python -m cios.applications.flora.live.collect --organisation ThamesWater
python -m cios.applications.flora.live.collect --organisation NationalGrid
python -m cios.applications.flora.live.collect --all
python -m cios.applications.flora.publisher.morning_edition
```

Live evidence is stored locally as JSONL at `.flora_pilot/live_evidence/live_evidence.jsonl`. Morning Edition uses that local file if present; it does not require a live fetch every run.

## Privacy and safety

The pilot reads public company and regulator HTML pages only. It does not authenticate, submit forms, collect personal data, or retain cookies intentionally.

## Limitations

- No PDFs yet unless a configured endpoint returns trivial HTML.
- No aggressive retries.
- No broad web crawling.
- No freshness guarantee beyond the extraction timestamp.
- Keyword extraction may miss relevant evidence or over-weight generic page text.
- Missing evidence remains explicit: sponsor, funding, timing, incumbent position and quantified AI outcome are not inferred.

## No LLM use

No LLM calls, LLM SDKs or generated interpretations are used. Interpretation is deterministic mapping code.

## No database use

No database is added. Local JSONL is the only persistence format.

## No broad crawling

The collector attempts only enabled URLs in the governed source registry and does not discover or crawl additional pages.

## BT Group plc single-enterprise calibration

BT Digital Twin calibration uses the governed profile at `config/flora/collection_profiles/bt-group-plc.json` and the canonical enterprise ID `bt-group-plc`.

Run the baseline pass:

```bash
python -m cios.applications.flora.live.collect --profile bt-group-plc --mode live_authoritative --pass baseline
```

Run the change-event pass:

```bash
python -m cios.applications.flora.live.collect --profile bt-group-plc --mode live_authoritative --pass change_event
```

Run recollection to validate idempotency:

```bash
python -m cios.applications.flora.live.collect --profile bt-group-plc --mode live_authoritative --pass recollection
```

Each run writes a collection manifest under `.flora_pilot/collection_manifests/` and can be inspected through the calibration lineage view showing Evidence → Observation → affected Enterprise Model attribute.
