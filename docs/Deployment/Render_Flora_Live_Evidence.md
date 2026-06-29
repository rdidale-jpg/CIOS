# Render Flora Live Evidence v0.2

Flora live evidence v0.2 lets the production Render web app collect deterministic evidence from the governed pilot source registry and display the results without adding LLMs, databases, broad crawling, PDF ingestion, browser automation, or scraping frameworks.

## Deploy

Deploy the existing Flora web service on Render with the current start command for:

```bash
python -m cios.applications.flora.web.app
```

The service binds to Render's `PORT` environment variable automatically.

## Browser routes

- `/` — Morning Edition homepage with a live evidence banner.
- `/health` — health JSON.
- `/live` — live evidence dashboard.
- `/live/collect` — triggers governed collection for all enabled pilot sources.
- `/live/status` — JSON status and latest source diagnostics.
- `/live/evidence` — readable HTML evidence table or an empty state.

## Trigger collection

Open this route in the deployed Render app:

```text
/live/collect
```

Collection is source-specific and limited to the configured pilot source allow-list. After completion Flora renders a result table showing each source, success or failure, HTTP status or error, evidence count, and attempt timestamp.

## Check status

Open:

```text
/live/status
```

The response includes last collection time, attempted sources, succeeded sources, failed sources, collected evidence object count, and latest diagnostics.

## Inspect evidence

Open:

```text
/live/evidence
```

Each evidence object shows organisation, source name, source URL, source type, extracted snippet, condition mapping, capability mapping, confidence, and extraction timestamp.

## Manual command

Run locally or in a Render shell:

```bash
python -m cios.applications.flora.live.collect --all
```

The command prints source diagnostics and writes JSONL files under `.flora_pilot/live_evidence/`.

## Diagnostics

Every source attempt is appended to:

```text
.flora_pilot/live_evidence/source_diagnostics.jsonl
```

Each row captures `source_id`, `organisation`, `source_name`, `url`, `success`, `http_status`, `error`, `evidence_count`, and `attempted_at`.

If sources fail:

1. Open `/live/status` to identify whether the failure is HTTP status based or network based.
2. Re-run `/live/collect` once to rule out transient source/network issues.
3. If a source consistently blocks automated HTML access, replace it in the governed source registry with a stable public HTML page for the same organisation and evidence tier.
4. Do not add broad crawling, browser automation, scraping frameworks, PDF ingestion, LLM fallback, or database persistence for v0.2.

## Render free-tier storage limitation

Live evidence and diagnostics are stored as local JSONL files:

- `.flora_pilot/live_evidence/live_evidence.jsonl`
- `.flora_pilot/live_evidence/source_diagnostics.jsonl`

Render free-tier filesystems may be ephemeral. Evidence may reset on redeploy, restart, or instance replacement. This is acceptable for pilot v0.2 because the goal is to prove governed live collection and transparent diagnostics. Persistent storage or a database is a later product decision.

## Why no LLMs or databases

Flora v0.2 uses deterministic keyword extraction and local JSONL receipts only. This keeps the pilot explainable, cheap to operate, auditable, and aligned with the current constraint to avoid LLMs, databases, broad crawling, and unrelated product expansion.
