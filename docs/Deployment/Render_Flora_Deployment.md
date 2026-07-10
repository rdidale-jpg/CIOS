# Flora Render Deployment

This guide deploys Flora as a Render Web Service that Rob can open from an iPad browser.

## Scope

The deployment wrapper is intentionally minimal:

- no LLM dependency
- no database dependency
- no broad crawler
- no change to the existing CLI, publisher, workspace, live evidence, or tests

## Create the Render service

1. In Render, choose **New +** → **Web Service**.
2. Connect the Git repository that contains this project.
3. Select the `main` branch.
4. If Render detects `render.yaml`, review the generated service and create it.
5. If Render does not detect `render.yaml`, enter the manual settings below.

## Manual settings if `render.yaml` is not detected

| Setting | Value |
| --- | --- |
| Language / Runtime | Python 3 / `python` |
| Branch | `main` |
| Root Directory | leave blank |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python -m cios.applications.flora.web.app` |
| Instance Type | Free tier |

## Environment variables

Set these values in Render:

| Key | Value | Notes |
| --- | --- | --- |
| `FLORA_HOST` | `0.0.0.0` | Ensures the service binds to Render's public interface. |
| `PORT` | Render managed | Render injects this automatically for Web Services. Do not hard-code it. |

The web app prefers `PORT`, then `FLORA_PORT`, and defaults to `8000` for local smoke tests. It prefers `HOST`, then `FLORA_HOST`, and defaults to `0.0.0.0` for production.

## Render build command

```bash
pip install -r requirements.txt
```

## Render start command

```bash
python -m cios.applications.flora.web.app
```

## Routes

The production web service exposes:

- `/`
- `/health`
- `/case/ThamesWater`
- `/case/NationalGrid`
- `/case/BT`
- `/case/Vodafone`
- `/settings`
- `/logbook`

## Health check

After deploy, open:

```text
https://<your-render-service>.onrender.com/health
```

Expected response:

```json
{"status":"healthy","service":"flora"}
```

You can also test locally:

```bash
PORT=8000 python -m cios.applications.flora.web.app
curl -i http://127.0.0.1:8000/health
```

## Free-tier limitations

Render free-tier services can spin down when idle. The first iPad request after inactivity may be slow while the service wakes. Free-tier CPU and memory are limited, so the service should remain dependency-light and avoid adding heavy frameworks or background jobs unless the hosting plan changes.

## Live evidence limitations

Flora's live evidence remains governed by the source-specific access policies already implemented in the project. Some source pages may block, throttle, change HTML structure, or otherwise limit access. When live evidence is unavailable, Flora may continue to use seeded pilot evidence and local JSONL evidence receipts rather than broad crawling.

## BT FY26 structured financial ingestion persistence

The BT FY26 structured route uses the existing Flora storage-root mechanism. For hosted proof, configure a single Render Web Service instance with one persistent disk mounted at `/var/data/flora` and set `FLORA_DATA_DIR=/var/data/flora`.

| Setting | Value |
| --- | --- |
| Service type | Render Web Service |
| Instance constraint | Single instance / single writer only |
| Persistent disk name | `flora-pilot-memory` |
| Persistent disk mount | `/var/data/flora` |
| Application storage key | `FLORA_DATA_DIR` |
| Source configuration | `config/flora/structured_sources/bt-group-plc-fy26.json` |
| Structured route | `structured_standard_financials` |

The route retrieves the issuer-hosted ESEF ZIP over public HTTPS, validates archive limits, writes canonical Evidence / Observation / Enterprise Model JSONL/JSON memory beneath `FLORA_DATA_DIR`, and removes temporary ZIP storage after processing. The ZIP itself is not canonical memory and must not be placed in the repository or in an environment variable.

ADR-009 limitations still apply: this is accepted file-backed pilot memory for one service instance and one writer. It does not claim production-grade database concurrency.

## Flora runtime data directory and Blueprint audit resilience

Flora runtime persistence is rooted at `FLORA_DATA_DIR` (falling back to the legacy `FLORA_PILOT_DIR`, then `/var/data/flora`). Render deployments must set `FLORA_DATA_DIR` to a writable location. If durable file-backed runtime state is required, attach a Render persistent disk and mount it at the same path configured in `FLORA_DATA_DIR` (for example `/var/data/flora`). Do not assume `/var/data` exists on a Render service unless a disk is explicitly provisioned and mounted there.

Blueprint import audit records are append-only JSONL diagnostics under `${FLORA_DATA_DIR}/blueprint_import/audit/events.jsonl`. These records are important for operator support, but they are optional for rendering the denied Blueprint import page: if the audit directory is unavailable or unwritable, Flora keeps the authorisation decision intact, renders the normal failure screen, shows the diagnostic reference, and writes a structured `blueprint_audit_persistence_failed` warning to application logs. The warning includes the diagnostic reference, event type, storage path, exception type, safe exception summary, deployment version and storage mode; it must not include secrets, raw package contents or tokens.

At startup, Flora validates the configured storage root and expected subdirectories. Unavailable storage is reported as `flora_storage_unavailable` in process logs so operators can fix `FLORA_DATA_DIR` or the Render disk mount without turning optional Blueprint diagnostics into a blank page.

To correlate a user report with Render logs, copy the `bpi-diag-...` reference shown on the Blueprint import page and search Render logs for the same diagnostic reference or the `blueprint_audit_persistence_failed` event.
