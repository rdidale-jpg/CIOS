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

## Pilot-only Flora owner authentication

Flora includes a reversible **pilot-only authentication mechanism** so the configured CIOS owner can use protected functions such as Blueprint import before the enterprise identity architecture exists. Secret sign-in remains available by default. An explicit auto-sign-in mode can instead issue the same signed `flora_pilot_session` cookie and derive the owner identifier, workspace and role from the same server-side environment configuration. It does not bypass downstream authorisation.

Required Render environment variables:

| Key | Value | Notes |
| --- | --- | --- |
| `FLORA_PILOT_AUTH_ENABLED` | `1` | Enables the pilot sign-in route and signed pilot session resolver. |
| `FLORA_ENVIRONMENT` | `pilot` | Required explicit non-production environment guard for auto-sign-in. Never use `production`. |
| `FLORA_PILOT_AUTO_SIGN_IN` | `false` (default) | Set to `true` only for the controlled single-user pilot. Invalid, absent and false values do not activate it. |
| `FLORA_PILOT_SESSION_SIGNING_KEY` | Create in Render dashboard | Required independent signing key for auto-sign-in. Do not commit or log it. |
| `FLORA_PILOT_ACCESS_SECRET` | Create in Render dashboard, or leave absent in auto mode | Retained for secret sign-in when auto-sign-in is disabled. Never place it in URLs. |
| `FLORA_PILOT_OWNER_ID` | Non-sensitive owner identifier | Example: an email-style or stable internal owner ID. |
| `FLORA_PILOT_WORKSPACE` | `CIOS` | Workspace resolved from the signed pilot session. |
| `FLORA_PILOT_ROLE` | `cios_owner` | Owner role; existing Flora policy expands this to Blueprint capabilities including `package.upload`. |
| `FLORA_TRUST_PROXY_HEADERS` | `0` | Public `X-Flora-*` headers are ignored by default. |

Cookie security: the pilot session cookie is HttpOnly, SameSite=Lax, Path=/, bounded by Max-Age, tamper-evident with HMAC, and marked Secure in Render/HTTPS deployments. Sign-out uses `POST /pilot-sign-out` and clears the same cookie.

Auto-sign-in fails closed unless pilot authentication and the explicit auto flag are enabled, `FLORA_ENVIRONMENT` identifies a non-production pilot-like environment, the canonical owner and workspace are non-empty, an effective membership role is configured, and the independent signing key exists. The issued cookie is immediately resolved through the normal session and workspace policy before it is returned. A configuration failure produces a diagnostic page and audit/log event without credentials. In auto mode the former access secret is not read for authentication or signing and may be absent.

**Exposure warning:** Pilot auto-sign-in grants the configured pilot identity to anyone able to reach this service. Flora reports whether trusted proxy headers are enabled, but this repository does not configure a service-level allow-list or trusted network boundary. Restrict the Render service externally where appropriate. The compact in-product banner remains visible while this mode is active.

Header-trust boundary: keep `FLORA_TRUST_PROXY_HEADERS=0` unless a real upstream identity proxy exists. If a future deployment sets it to `1`, the edge must strip all public client-supplied `X-Flora-*` headers before injecting trusted identity, workspace and role values.

Blueprint import: anonymous users and synthetic browser-supplied `X-Flora-*` headers remain denied. When auto-sign-in is off, the denied Blueprint page offers the existing pilot sign-in action. Signed-in pilot owners resolve as the configured owner in the configured CIOS workspace with `cios_owner`, and Blueprint GET/POST use the same signed session and existing role/capability policy, including `package.upload`, inspection, governance, promotion and administration checks.

Future migration path: replace this pilot-only mechanism with enterprise SSO, identity-provider integration, database-backed memberships, durable workspace ownership, and centrally managed roles/capabilities. The pilot cookie should then be removed rather than expanded into an enterprise identity platform.

## Temporary pilot-only Twin import bypass

The package-import bypass is disabled by default and activates only for the
case-insensitive explicit value `true`. In the Render service, add this
environment variable:

```text
FLORA_PILOT_IMPORT_BYPASS=true
```

Then trigger a new deployment. No former pilot access-secret variable is
required for `GET /blueprint-import` or `POST /blueprint-import/upload` while
the flag is active. Remove the variable (or set it to `false`) and redeploy to
restore the normal account, workspace, membership, role and capability policy.
The bypass remains scoped to package import and does not confer review,
promotion, canonical mutation, administration or workspace-management access.
