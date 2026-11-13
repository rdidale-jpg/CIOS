# PR #586 — production release preparation

**Production decision: NO-GO until every required Render check below is established. No merge or deployment has been performed.** A passing code gate is separate from proof that the existing service, data, identity and recovery arrangements are ready.

The final validated **candidate SHA** is pinned in PR #586's current handoff and exact-head Actions results. This document is committed before that final run; it does not invent a future green result or a production deployment SHA. The owner must use the complete 40-character SHA, never a moving branch name. If a later merge produces another SHA, that SHA must receive complete local and hosted validation before it becomes a release candidate.

## Changes and integration

- Preview records now say **Example offer**, **Example private offer variation** and **Example opportunity**, with example proof and example-company context. They remain illustrations, not customer demand or approved corporate capabilities. No preview fixture is imported into production, and no stored customer offer/name, audit receipt or research record is renamed.
- The Observatory's exact internal `SEEDED / SYNTHETIC / FALLBACK` marker is translated at the escaped presentation boundary to **Example data / fallback (not live)**, including derived text. Internal evidence classes, IDs, sources, scores, confidence and live/non-live flags are unchanged. Actual terms such as “synthetic biology” in business descriptions are not rewritten.
- The existing Pipeline create-action foreground is corrected within its existing scope. No destination, form field, stage, evidence or permission rule changes. Browser checks verify contrast at all five viewports.
- All 108 before/after captures are regenerated with the same example dataset in each UI version. **732 browser checks pass**; authenticated browsing preserves Offers/Pipeline bytes. Internal fixture IDs/operator receipts/passwords remain technical test artifacts outside the user experience.

The observed remote refs are already ancestors of the candidate; no additional merge was needed to reconcile their source. Existing draft heads and main are preserved:

| Integration source | Observed SHA | Included |
|---|---|---|
| Current main | `854a783b3c5f83d6ee3604f49a76772529b7339a` | Yes |
| Technology UX #574 | `867e11809dd13058648b891387038948ccd978a1` | Yes |
| Offers architecture #575 | `667ce1b3d1f77d4c7d66b20e21c595e7b4882cbb` | Yes, proposal status retained |
| Offers v1 #577 | `ad0b3d4c781178e6fb02271f3f8373fd3b23c339` | Yes |
| Integration/banner/release controls #580 | `34e34570c52847e16eb5f0d00579ca923983af7c` | Yes |
| Approved visual #584 | `19ab36d241dbca2099ffb9b5d519c68c493a914a` | Yes |
| Individual 21-case reconciliation | `6a6add2422e37ddd97bcc4c818f0b72606434fef` | Yes |
| Rejected Home #582 | `9aaaa692e5200681bfa69d55a6d13aa483cc1837` | **No** |

The PR remains stacked on approved #584, itself stacked on #580/main. Source inclusion does not merge or approve those drafts. The 20-sector UK landscape, six PESTLE factors, original artwork/economic extract, private employer/seller scopes, independent offer approvals, default-off Studio, research boundaries and explicit Pipeline controls remain in place.

## Exact-head code acceptance

Final acceptance requires the complete canonical FLORA workflow, not an older component result: all **1,432 identities**, **1,386 passing tests / 36 retained inherited failures / ten unchanged skips**, **388/388 strict security tests**, exactly the 21 individually reconciled cases reported fixed, zero comparator issues, all Technology/Offers/visual-system steps successful. The baseline and comparator remain byte-identical. [Individual findings](Reconciliation-586.md) and [machine-readable per-case evidence](Reconciliation-586.json) remain available.

The final local focused selection includes the original 238 cases plus five business-wording/provenance/escaping cases. The 39 CI-policy/release-helper tests and applicable startup/runtime-proof tests are also run. Hosted ownership validation includes the new terminology tests. Any pending, failed, skipped required step, changed source/base or branch drift is **NO-GO**.

## What was observed about production

The owner-confirmed origin is **https://flora-current.onrender.com**. Repository `render.yaml` declares a Python service named `flora`, a standard plan, build `pip install -r requirements.txt`, start `python -m cios.applications.flora.web.app`, `FLORA_DATA_DIR=/var/data/flora`, `FLORA_TRUST_PROXY_HEADERS=0` and a 1 GB disk named `flora-pilot-memory` mounted at `/var/data/flora`.

Those are repository declarations, not authenticated Render settings. No Render connector, service ID or credential is available in this session. Read-only `/health` and `/deployment` probes were unavailable through the current network (`URLError`); they do not establish either service failure or readiness. No proxy/alternate route was used to bypass the unavailable connection. No Render setting, deployment or production data was modified.

| Required production check | Observed evidence | State / responsible owner |
|---|---|---|
| Actual service ID, name and origin | Owner supplied origin; blueprint says `flora` | **UNVERIFIED** — Render service owner |
| GitHub repository, configured branch, root directory | Repository declaration only; actual Render connection unknown | **UNVERIFIED** — Render service owner |
| Automatic deployments, deploy hooks, previews and competing release automation | No authenticated settings | **UNVERIFIED** — service owner/maintainer; prevent uncontrolled release before any merge |
| Current deployment ID/SHA and secure rollback deployment/SHA | Not observed | **UNVERIFIED** — service owner; do not select current main or a previous PR merely because it exists |
| Existing persistent disk ID/attachment/mount, capacity/inodes and one-writer topology | Blueprint only | **UNVERIFIED** — operations/data custodian |
| Effective data-root and all profile/storage path overrides | Expected `/var/data/flora`; actual overrides unknown | **UNVERIFIED** — data custodian; all writable stores must be durable and backed up |
| HTTPS origin/CSRF and trusted-header boundary | Code requires exact HTTPS `FLORA_PUBLIC_ORIGIN`; absent from blueprint. Trust flag declared `0` | **UNVERIFIED** — security/service owner |
| Existing authority store, real humans/memberships/workspace grants and sign-in | No production identity/state inspected | **UNVERIFIED** — security owner; never bootstrap over an existing store |
| Consistent full backup, retention, access and tested restoration | No backup/recovery evidence | **UNVERIFIED** — data custodian |
| Rollback compatibility with current authority, audit, Offers and Pipeline | No actual previous release/state verification | **UNVERIFIED** — security/data/release owners |
| Application health and owner visual/access acceptance | Live probes unavailable; real browser acceptance not performed here | **UNVERIFIED** — release owner |

**Any required unknown is a stop condition.** The non-secret readiness summary requested from the owner may supply authenticated dashboard observations; credentials, environment dumps, private records and backup contents must not be posted to the PR/chat. Record sensitive operational evidence in the owner's private release ticket.

## Owner procedure — first verify, then select a commit

1. Open the existing service at `https://dashboard.render.com/` in the authorised account. Identify it by the verified origin and record its real service ID. Confirm `rdidale-jpg/CIOS`, actual branch/root, actual build/start commands and health-check path. Do not create a replacement service/disk. Inspect actual auto-deploy/hook/automation settings; prevent an uncontrolled deploy before a merge, branch change or environment save. No such setting change has been made here.
2. Inspect the existing persistent disk and match its ID/attachment to the release record. Confirm `/var/data/flora` is a real persistent mount retained on this same service, not just a directory name. Confirm `FLORA_DATA_DIR` and any mission/employer/legacy path overrides resolve to reviewed durable locations. Check capacity/inodes, protected-journal/reserve health and the single-writer layout. `/health` being 200 does not prove disk persistence or a valid backup.
3. Verify the real security store at `security/authority.sqlite3` under the effective root, its existing ownership/permissions and real operator-controlled enrollment/memberships. Verify `FLORA_PUBLIC_ORIGIN` is exactly `https://flora-current.onrender.com` without a trailing slash, `FLORA_TRUST_PROXY_HEADERS=0`, HTTPS secure cookies, exact-origin/CSRF enforcement and working real sign-in/workspace selection. A pilot label, header claim, retired bypass flag, environment presence or example account is not authority. If configuration needs repair, plan that change against a known validated commit; do not blindly save/redeploy unknown branch HEAD or initialise/replace authority.
4. Quiesce application writes through the approved operator procedure. Take/verify a consistent private backup of the **whole protected root**, all configured external store paths and required SQLite/WAL state: authority/audit/revocation, protected undo journals/reserves, research/evidence, imports/approvals, profiles, `commercial_context/offers-v1/context.json` and `sales_pipeline/opportunities.json`. Establish snapshot timestamp, scope, retention and protected access. Restore-test it in an isolated private environment with correct permissions. A live file copy or an uninspected Render snapshot is not sufficient recovery evidence. Do not discard journals or copy backups over live files to make a readiness check pass.
5. Record a real known-good deployment ID/full SHA and demonstrate compatibility with current persistent state. The rollback must preserve the repaired authentication, journal/audit, private offer and Pipeline boundaries. A previously green but never deployed candidate is not an observed production rollback. No automatic migration or data restore is part of this terminology correction.
6. Only after every production check is established, review/approve the complete integration. The existing stack is unmerged; if Render tracks main, the candidate is not on that branch yet. Use the repository's protected integration process. A merge/squash/rebase that creates a different commit creates a **new candidate**: run full local and hosted validation on that SHA before release. Do not force-push main, bypass protections or relabel a new SHA as the old tested SHA. If the reviewed process preserves the final validated SHA, verify that explicitly.

## Exact-commit preflight on the owner's workstation

Replace the first two literal placeholders with the final full validated SHA from this PR's handoff and the **actual authenticated Render branch**. These are not secrets.

```sh
FLORA_RELEASE_SHA='<full-40-character-validated-SHA-from-PR-586-handoff>'
FLORA_DEPLOY_BRANCH='<actual-Render-deployment-branch>'

git fetch origin "$FLORA_DEPLOY_BRANCH"
git cat-file -e "$FLORA_RELEASE_SHA^{commit}"
git show --no-patch --format=fuller "$FLORA_RELEASE_SHA"
git merge-base --is-ancestor origin/main "$FLORA_RELEASE_SHA"
gh run list --repo rdidale-jpg/CIOS --workflow flora-validation.yml --commit "$FLORA_RELEASE_SHA"
```

Inspect the **latest exact-SHA** run; all required steps must be completed successfully. GitHub's PR test-merge tree must match the candidate and contain its reviewed base. A moving branch or another component's CI is not proof for this SHA. Check current PR/main/component heads against the recorded graph; stop/reconcile/revalidate on drift.

For the latest-head-only fallback, additionally require:

```sh
FLORA_REMOTE_HEAD=$(gh api "repos/rdidale-jpg/CIOS/commits/$FLORA_DEPLOY_BRANCH" --jq .sha)
test "$FLORA_REMOTE_HEAD" = "$FLORA_RELEASE_SHA"
```

Freeze competing pushes/merges throughout the release window. An equality check detects drift; it does not lock a branch. If branch drift cannot be prevented, do not use latest-head deployment.

The existing manual `flora-release-preflight.yml` helper remains read-only and unchanged. It is usable only after its trusted workflow exists on main, the `flora-production` environment has required independent reviewers/prevent-self-review configured and inspectable, the exact deployment branch equals the typed SHA, and canonical exact-SHA CI passes. It repeats checks after approval. It does not contact Render, check backups, change the branch, deploy or replace owner operational approval. Do not invoke a PR copy as trusted main or create an unprotected environment to get around this gate. See [the original helper procedure](../integration-578/Render-Owner-Deployment.md#3-optional-github-approvalpreflight-helper--no-deployment).

## Deploy that exact commit through Render — only after GO

1. In the **verified existing service**, open **Manual Deploy → Deploy a specific commit**, if that facility is available for its Git connection. Select/enter the complete validated `FLORA_RELEASE_SHA`; verify the displayed full SHA, repository and branch eligibility. Do not choose a similar short SHA or “latest” accidentally. If the dashboard cannot select this unmerged/branch-ineligible commit, stop: complete the approved integration and exact-new-SHA validation or obtain a separately reviewed same-service branch configuration. No branch retarget is authorised by this document alone.
2. If only **Deploy latest commit** is available, use it only when the actual configured branch's remote HEAD equals `FLORA_RELEASE_SHA`, all earlier checks passed and concurrent writers are controlled. Recheck the equality immediately before clicking. If integration generated another SHA, the old candidate SHA is not deployable by this fallback.
3. Start the owner-approved deployment and record deployment ID, exact captured SHA and status. Keep the existing disk attached; use the verified configuration. Watch queued → build → deploy → live and inspect health. An accepted deployment job or webhook response is not success. A captured SHA mismatch is an unvalidated release, not a substitute for the requested commit.
4. Compare the authenticated Render deployment commit with the application fingerprint below. Stop/rollback on failed health, authentication, storage, access control or SHA mismatch. There is no Render API/deploy hook command in this handoff because no supported authenticated service connection was available to verify one.

## Post-release acceptance and owner URLs

```sh
curl --fail --show-error https://flora-current.onrender.com/health
curl --fail --show-error https://flora-current.onrender.com/deployment
```

Require `/health` to report healthy, and `/deployment.commit_sha` plus `application_module` to identify the exact release and `cios.applications.flora.web.app`. Correlate that SHA with authenticated Render deployment details; a display/environment label alone is not code proof. Never report a feature live from URL accessibility alone.

Owner walkthrough URLs, **intended until the exact release is independently observed**:

- Home: `https://flora-current.onrender.com/`
- PESTLE: `https://flora-current.onrender.com/pestle?market=GB`
- Technology: `https://flora-current.onrender.com/industries/technology/experience`
- Offers: `https://flora-current.onrender.com/flora/offers`
- Pipeline: `https://flora-current.onrender.com/flora/sales/pipeline`

Use a real owner session and an authorised seller session. Confirm Home's 20 UK sectors/three researched entry routes, six image-native PESTLE factors, Technology participants/NVIDIA and required source access. Check real sign-in/workspace selection, owner controls, sign-out/revocation, denied signed-out/private/wrong-workspace Offers/Pipeline access, employer versus private-offer scope and independent approval/version controls. GET discovery/qualification pages must not create Pipeline records. Existing records/counts and storage health remain intact after deployment/restart. Do not seed examples or create test opportunities in production merely to demonstrate the screen.

Required employer setup is owner-controlled: a real enrolled operator with appropriate workspace rights selects the workspace, records the real employer and capabilities through existing employer setup, binds only the actual sellers and independent reviewers, and sellers select that employer. Actual offers require real proof and the existing independent approval flow; private variations retain seller visibility and versions. Creative Offers Studio stays off until a deliberate opt-in. Existing employer bindings/profiles must be inspected and reused, not replaced. Example screenshots confer no production entitlement or business verification.

## Rollback

If any acceptance check fails, stop new commercial writes through the approved procedure. On the same service and **same persistent disk**, redeploy the recorded secure known-good deployment/SHA using the exact-commit control; if only latest is available, use a reviewed rollback process and verify the captured SHA. Do not force-reset main or assume an older codebase can safely read new Offers/authority state.

A code rollback preserves current authority, membership/revocation, audit, evidence, profiles, offer versions and Pipeline files. It is **not** a data restore. Never restore stale authority/sessions, discard protected journals, erase owner changes or attach an empty disk. Data corruption/incompatibility requires the data/security custodians' separately reviewed consistent recovery procedure; preserve recovery evidence and fail closed meanwhile. Recheck health, exact SHA, real sign-in, scopes, Offers and Pipeline after rollback. The forward-only GitHub preflight intentionally does not certify an old rollback SHA; rollback is an explicit owner operation.
