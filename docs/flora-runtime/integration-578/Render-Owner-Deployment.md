# Owner-controlled Render deployment — exact commit

**Current decision: NO-GO for merge/deployment.** This guide is executable by the authorised owner/operator after the missing production checks below are completed. It does not report a deployment, create Render credentials, change a service, or authorise release merely because CI is green.

Owner-confirmed production origin: **https://flora-current.onrender.com**. Intended Offers URL: **https://flora-current.onrender.com/flora/offers**. The origin was supplied by the owner; neither live endpoint nor deployed code was independently observed in this session. An earlier network-policy denial was not retried through another route. No Render connector, service ID or credential is available here.

## 1. Complete the production record before merging

In the authenticated Render dashboard, open the **existing** FLORA service. Do not create a replacement service or attach an empty disk to make a check pass. Record the following in the owner's private release ticket; record secret presence/verification only, never secret values.

| Check | Expected / action | Current evidence | Responsible owner |
|---|---|---|---|
| Service | Actual service ID, display name and external origin belong to FLORA | ID/name not observed. Repository blueprint says `flora`; URL alone does not prove the actual service ID. | Render service owner |
| Repository and branch | Connected to `rdidale-jpg/CIOS`; record actual configured deployment branch | Not observed; do not assume main | Render owner |
| Release policy | Inspect auto-deploy, CI gating, deploy hooks, root directory and competing automation | Not observed; pause uncontrolled auto-deploy before any integration merge | Render owner / repository maintainer |
| Commands | Build `pip install -r requirements.txt`; start `python -m cios.applications.flora.web.app`; repository root | Blueprint only; inspect actual dashboard overrides | Render owner |
| Deployed code | Record current deployment ID, Git commit and known-good rollback commit from authenticated deployment details; correlate `/deployment` | Unverified | Render owner |
| Storage | Existing persistent disk retained, mount `/var/data/flora`, `FLORA_DATA_DIR` matches; one service instance/process writer; no external writers | Blueprint names `flora-pilot-memory`, 1 GB; actual mount/topology/capacity unverified | Operations/data custodian |
| Capacity / recovery | Enough disk/inodes for protected undo and reserve; no unresolved/corrupt journal; storage health ready | Unverified; do not delete journals to recover availability | Data custodian |
| Origin / TLS | HTTPS, exact `FLORA_PUBLIC_ORIGIN=https://flora-current.onrender.com` with no trailing slash; request Origin must match | Not declared in blueprint; may already be set in Render, not verified | Render owner / security owner |
| Authority | Existing private `security/authority.sqlite3`, legitimate enrolled humans, revocable memberships and capabilities; security directory/file ownership and modes correct | Unverified; never initialise over an existing store | Security owner |
| Trust boundary | `FLORA_TRUST_PROXY_HEADERS=0`; no retired pilot auto-sign-in/import bypass or forged-header authority | Blueprint/code support this; actual service settings unverified | Security owner |
| Backups | Consistent full protected-root backup/snapshot and private restore verification, including authority/audit, profiles, research/evidence, Pipeline and any journals | No production backup inspected | Data custodian |
| Human approval | Owner accepts integrated previews/architecture, validates release ticket and explicitly authorises exact commit | Required; not inferred from this document | Product/release owner |

**Stop if any check fails or remains unknown.** Existing general `docs/Deployment/Render_Flora_Deployment.md` contains historical free-tier/pilot-bypass instructions; those are not the current security contract. Do not restore legacy bypasses, substitute header identity, weaken permissions, reset authority or point to ephemeral storage.

The existing protected journal assumes participating writers on a single persistent filesystem. Quiesce writes through the operator's approved procedure before taking a consistent backup of the whole protected root and SQLite state (including any required WAL/SHM state). Verify restoration in an isolated private location without exposing enrollment tokens or customer data. A filesystem copy taken during concurrent mutation is not automatically a valid recovery backup. Do not claim an existing Render snapshot is usable without inspecting its timestamp, scope and recovery procedure.

## 2. Select the exact release SHA

Take the **full 40-character candidate SHA from the draft integration PR's current head and successful CI**. Source SHA and GitHub's tested synthetic merge SHA are distinct: inspect both; if different, compare their file trees and base. A changed branch head or base invalidates a prior release decision.

The integration PR includes the reviewed heads of #574, #575 and #577 as ancestors, the narrow banner and release controls. None of those PRs is automatically approved or merged by this integration branch. The architecture file remains a proposal, not a new accepted normative standard.

Before any actual integration merge, complete section 1 and confirm that auto-deploy cannot release an unvalidated new main commit. If repository policy creates a new merge/squash/rebase SHA, **that new SHA must pass full local and hosted FLORA validation before deployment**. Do not substitute tree similarity for the requested exact-commit validation. If a fast-forward preserves the validated SHA, verify that fact rather than assuming it. Do not bypass branch protections to preserve a SHA.

On the owner's authenticated workstation:

```sh
# Paste the actual complete validated release SHA; these variables are not secrets.
FLORA_RELEASE_SHA='<full-40-character-validated-sha>'
FLORA_DEPLOY_BRANCH='<actual-configured-render-branch>'

git fetch origin "$FLORA_DEPLOY_BRANCH"
git rev-parse FETCH_HEAD
git show --no-patch --format=fuller "$FLORA_RELEASE_SHA"
gh api "repos/rdidale-jpg/CIOS/commits/$FLORA_DEPLOY_BRANCH" --jq .sha
gh run list --repo rdidale-jpg/CIOS --workflow flora-validation.yml --commit "$FLORA_RELEASE_SHA"
```

All observed branch/commit values must match the intended release record. Inspect the latest run, not an older green result. Full gate requirements: all 388 security tests pass without skips; all 1,432 baseline identities preserve 57 inherited failures and 10 skips with approved signatures/reasons; Technology owner/UX/integration and Offers checks pass; CI-policy/release-helper tests pass. No exception or comparator changes are introduced in this sprint.

Freeze competing pushes/merges for the release window. Recheck the configured branch immediately before initiating deployment. A local variable, a successful earlier check, a deploy hook or clicking **Deploy latest commit** does not pin an arbitrary historical SHA.

## 3. Optional GitHub approval/preflight helper — no deployment

The added **FLORA owner release preflight (no deployment)** workflow is `flora-release-preflight.yml`. It is manual-only, uses read-only GitHub permissions, serialises release checks, runs trusted workflow-source code rather than checking out/executing the candidate, and refuses non-main dispatch. It cannot contact Render or write production data. It is not available for normal dashboard dispatch until the workflow is present on the repository's default branch after an authorised integration.

Before using it, the repository administrator must create/review the `flora-production` GitHub environment, add required human reviewers and enable prevention of self-review. Restrict environment/workflow usage to trusted main and prevent bypass as repository policy allows. Missing environment, unavailable policy-read access or absent reviewer protection causes refusal **before** the approval job can create/use an unprotected environment. No Render secret or service ID is added or invented. The user triggering the run needs a different authorised environment reviewer for approval.

After an authorised merge and exact-main validation, dispatch from **main**, entering the full SHA and actual Render branch:

```sh
gh workflow run flora-release-preflight.yml --repo rdidale-jpg/CIOS --ref main \
  -f commit_sha="$FLORA_RELEASE_SHA" -f configured_branch="$FLORA_DEPLOY_BRANCH"
```

Review the pending environment job in Actions and approve only after checking the production release ticket. The helper verifies branch HEAD twice, current-main ancestry, the latest exact-SHA canonical FLORA workflow run, and successful security/baseline/Technology/Offers steps. It repeats checks after approval, so waiting for approval cannot silently bless a moved branch. A failed, pending, cancelled or partially skipped validation cannot fall back to an older green run.

**A successful helper says only that read-only release eligibility passed.** It does not inspect Render settings, lock a branch, validate backups, prove real IAM, authorise external release on its own, or deploy. The GitHub environment may display a deployment/approval record; that is not a Render deployment. No authenticated Render API action is implemented because no supported connection/credential/service identity was available to verify one.

## 4. Owner-executed Render deployment

Proceed only after all preconditions, exact-SHA CI and explicit owner approval have cleared.

**Preferred — specific commit:** On the verified existing Render service, use the dashboard's manual **Deploy a specific commit** facility if offered for that connected Git service. Select the exact validated full commit. Confirm repository and branch eligibility, inspect the release summary/commit, then start deployment. Record the resulting deployment ID and its exact Git commit. If the selected commit differs, stop.

**Fallback — latest-head-only dashboard:** Do not click latest while the configured branch points elsewhere. With the owner/maintainer and branch protections, pin the actual configured deployment branch's HEAD to the exact *validated* release SHA. Use a reviewed branch selection/update only if the service owner explicitly approves it and confirms this preserves the same service and persistent disk. Do not force-push main or silently change Render's branch. If branch protection/merge policy produces another SHA, validate that new SHA first. Freeze competing writers, read the branch's remote HEAD again immediately before clicking latest, and verify it equals `FLORA_RELEASE_SHA`. Verify the created Render deployment actually captured that SHA; abort or treat it as unvalidated if it captured another commit. If branch drift cannot be prevented or the captured SHA cannot be established, **NO-GO**.

Use the dashboard's authenticated status view to follow queued → build → deploy → live. A webhook invocation or accepted job is not proof of success. Do not report deployment complete until both Render and application checks below identify the selected release. No credentials should be pasted into chat, committed, placed in a command-line URL, or printed in CI output.

## 5. Post-deployment acceptance

From a network authorised to reach the owner-confirmed origin:

```sh
curl --fail --show-error https://flora-current.onrender.com/health
curl --fail --show-error https://flora-current.onrender.com/deployment
```

Health must be ready; `/deployment` must identify the repository-resolved released commit and expected application module. Do not treat an arbitrary environment label as verified code identity. If the fingerprint is unavailable/mismatched, investigate; do not label the feature live from URL accessibility alone. Confirm the authenticated Render deployment commit independently.

Then use real browser sessions (including an owner iPad check):

1. An anonymous request to `/flora/offers` must remain denied. A 403 by itself cannot prove Offers was deployed.
2. Sign in with an existing authorised human, choose the correct workspace and open `/flora/offers`. Confirm the expected integrated UI and matching employer scope.
3. Verify owner declaration and separate employer binding; private seller offers remain private even to unrelated owners; only a distinct delegated reviewer can publish approved employer offers. Re-authenticate when required. Never seed the synthetic preview accounts/approvals into production.
4. Confirm Studio is off by default; enabling it explicitly saves only private, version-pinned drafts and invokes no paid model, outreach or Pipeline writer.
5. Open Technology → district/participants: thin native industry banner, original approved illustration, sortable table, blank unsupported UK metrics, NVIDIA profile, evidence/source limitations and keyboard navigation. Check Banking/Aviation/Macro and existing Pipeline journeys.
6. Compare protected research/Pipeline inventories through approved read-only operator checks. Record existing-data survival and no unintended Pipeline/canonical writes. Do not create fictitious live customer records to test deployment. Actual employer setup writes need explicit owner authorisation after release, not an automatic smoke script.

**Owner employer setup:** existing enrolled owner/seller/reviewer memberships and capabilities must already be valid. Under My offers → My company, owner saves the declared EmployerContext and then separately records the binding review reference and named authorised sellers/reviewers. Seller selects the employer, drafts offers with genuine delivery/source/partner-rights references, and submits to a different delegated reviewer. Saving a company name grants no IAM or publication authority. All offers/variations remain versioned; canonical participant/offer bindings remain unbound unless accepted by their existing owners. Pipeline capture stays in the existing separately authorised Banking/Aviation flow.

## 6. Code rollback while preserving data

Before release, record an authenticated, known-good deployment ID and full commit SHA, its availability in Render and compatibility with current persistent state. This sprint introduces no authority schema migration or new Pipeline writer; Offers state is additive under `commercial_context/offers-v1`, and profile edits retain the existing owner. Additive file compatibility is not permission to restore older authority or erase user changes.

If post-release checks fail, stop new commercial writes through the approved operator procedure, keep the existing persistent disk attached, and redeploy the **recorded known-good commit** using the same exact-commit dashboard controls. Recheck branch drift if only latest-head deployment is offered. Do not force-reset repository history. Preserve current authority, audit, evidence, profiles, offers and Pipeline files; a code rollback is not a data rollback. A later code revert PR should receive its own tests and review.

Do not automatically restore stale SQLite/profile/Pipeline backups, initialise a new authority store, discard protected undo journals or downgrade to retired header/pilot bypasses. If current data is corrupt or incompatible, retain recovery artifacts and use the security/data custodian's reviewed consistent recovery procedure. The preflight helper intentionally rejects older commits behind current main; rollback is a separate explicit owner operation, not an unchecked use of that helper.
