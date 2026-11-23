# Controlled existing-service release — instructions only

**No merge or deployment is authorised by this draft PR.** Owner technical acceptance must identify the exact reviewed head. A later authorised integration must validate the exact resulting release SHA and CI before a separately approved manual Render deployment. Do not deploy an unreviewed branch or call the preview live merely because CI passes.

## Verified existing target

Read-only Render metadata, 23 November 2026, in the owner-confirmed **My Workspace**:

- **Flora - Current**, service `srv-d97unhbtqb8s739huf1g`: [existing dashboard](https://dashboard.render.com/web/srv-d97unhbtqb8s739huf1g), `https://flora-current.onrender.com`.
- Repository `rdidale-jpg/CIOS`, tracked branch **main**, Auto-Deploy **off**.
- Build: `pip install -r requirements.txt`. Start: `python -m cios.applications.flora.web.app`. Root directory unchanged.
- Existing **10 GB** persistent disk mounted at **`/var/data/flora`**. Preserve it and every existing environment, authentication/origin and data setting; no new variables, dependency install, schema/data migration or storage change is introduced by this preview.
- Configured HTTP health-check path is empty: Render's default TCP readiness does not prove the application journey. Perform the `/health` and browser smoke checks below. No health-check configuration change was made or is required by this PR.
- Live deployment `dep-dc2a6017lnhs73a5oi0g`, manual, commit **`97d316c640c96d99c2301819f8aac00b3b9c1398`**, finished 23 November 2026 20:34:56 UTC. This is the current rollback code target, subject to rechecking actual live state at release time.

Only service/deployment metadata was inspected. No secret environment values, database records or production data were requested. Do not target Flora-pilot or create a service, Blueprint, production environment, deploy hook or other infrastructure.

## Owner actions after explicit release approval

1. Confirm the approved implementation head, integration result and all required checks. Record the **full 40-character release SHA**; it must contain only the approved integration. Recheck that the current live deployment is still the intended rollback target and that its retained artifact offers Rollback. Use the existing storage/backup procedure; no new backup service or data migration is needed.
2. Open the existing dashboard above → **Manual Deploy → Deploy a specific commit**. Paste the exact validated **release SHA**, verify it, then **Deploy Commit**. Do not choose latest commit if main has moved; do not change the branch or settings. Leave Auto-Deploy off. Attached persistent disks can cause a deployment interruption.
3. Wait for that deployment to report **Live**. Confirm its commit ID matches the approved release. Check `/deployment` against the same SHA and `/health` for healthy application storage. If any check fails, do not call the release successful.
4. Open **Industries → Banking → Lloyds**. Current experience must still arrive first. Follow **Preview New Experience**, exercise Landscape/Inside/Forces, four regions, keyboard/touch and browser history; use **Return to current experience**.
5. Verify **Industries → Aviation → easyJet**, **Enterprises → Lloyds** and **Enterprises → easyJet**. Confirm existing owner/private functions retain their normal sign-in/workspace boundaries; use read-only inspection rather than creating financial runs or Pipeline records for smoke testing.

Planned preview URL after an authorised successful release: **`https://flora-current.onrender.com/enterprises/lloyds/preview`**. It is absent from the currently deployed baseline code. Do not assert successful live navigation until the deployed service has actually been checked.

## Rollback

If the approved release is unhealthy, use the existing service's **Deploys** page, select the retained successful baseline deployment at `97d316c640c96d99c2301819f8aac00b3b9c1398`, and use **Rollback → Rollback to this deploy**. Confirm the rollback itself reaches Live, its SHA, `/health`, current Lloyds and Aviation/easyJet. If that artifact has expired, manually deploy the same exact baseline SHA instead. Preserve Auto-Deploy off and every persistent disk/environment setting.

Rollback reverts code, not disk state. This preview introduces no canonical, Financial, Pipeline, database or schema writes, so there is no preview data migration to reverse. [Integrity-Proof.json](Integrity-Proof.json) demonstrates that reversing the complete source patch restores exact baseline tree `6c72c645777372e196cbc3c4248f5ec7321cd84e`. No operational rollback has been triggered as a test.

## Current platform references

The official Markdown references were retrieved and read on 23 November 2026: [specific-commit deployment](https://render.com/docs/deploys.md#deploying-a-specific-commit), [health checks](https://render.com/docs/health-checks.md), [rollback and artifact retention](https://render.com/docs/rollbacks.md). They support the manual commit selection, TCP-versus-application checks and code-versus-disk rollback distinctions above. Actual rollout identity and artifact availability must still be checked in this existing service at release time.
