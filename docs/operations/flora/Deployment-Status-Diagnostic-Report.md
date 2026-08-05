# Flora Deployment Status Diagnostic Report

## Diagnosis

The previous Import Twin panel treated deployment verification as an exact SHA comparison between the running build SHA and the Codex implementation SHA. That is only valid for a direct deployment of the same commit. It is not valid after a GitHub merge commit, squash merge, rebase merge, direct commit to `main`, or later commits on `main` that contain the approved implementation.

## Corrected decision logic

Flora now proves an approved change is live using this evidence order:

1. A deployed release/change marker matching the stable `change_id`.
2. Runtime build metadata for the final deployed commit.
3. Git ancestry/containment where repository history is available.
4. Merge or squash mapping through the stable change marker.
5. Exact SHA equality only as a narrow fallback.

If proof is unavailable, Flora reports **Metadata incomplete** rather than **Wrong deployed commit**. **Deployment problem** is reserved for authoritative wrong branch/service/repository evidence, failed deployments, or elapsed deployment windows with complete evidence that the approved change is absent.

## Merge-mode handling

| Merge mode | How inclusion is proved |
| --- | --- |
| Merge commit | `git merge-base --is-ancestor <source_commit_sha> <deployed_sha>` proves the implementation commit is in deployed history. |
| Squash merge | The deployed application exposes the stable `change_id` / release marker because ancestry will not contain the original branch SHA. |
| Rebase merge | Git ancestry proves the source change when the source SHA survives, otherwise the stable release marker proves inclusion. |
| Direct commit to main | Exact SHA equality or ancestry proves inclusion. |
| Later commits on main | Git ancestry proves the approved source commit is contained by the later deployed SHA. |

## Render configuration audit

| Field | Finding |
| --- | --- |
| Render service name | `flora` in pilot metadata; runtime value is unknown unless Render exposes `RENDER_SERVICE_NAME` or `FLORA_RENDER_SERVICE`. |
| Repository | Unknown from checked-in metadata; runtime can expose `RENDER_GIT_REPO_SLUG`, `RENDER_REPOSITORY`, or `GITHUB_REPOSITORY`. |
| Deployed branch | Expected `main`; runtime branch is read from `RENDER_GIT_BRANCH` or repository fallback. |
| Build command | Unknown unless exposed via `RENDER_BUILD_COMMAND` or `FLORA_BUILD_COMMAND`. |
| Start command | Unknown unless exposed via `RENDER_START_COMMAND` or `FLORA_START_COMMAND`. |
| Auto-deploy setting | Unknown unless exposed via `RENDER_AUTO_DEPLOY` or `FLORA_AUTO_DEPLOY`. |
| Latest known deployment SHA | Runtime reads `RENDER_GIT_COMMIT` or equivalent revision variables, falling back to local Git. |
| Latest known deployment status | Unknown unless exposed via `RENDER_DEPLOY_STATUS` or `FLORA_DEPLOYMENT_STATUS`. |
| Deploys from `main` | Expected by metadata; authoritative runtime proof depends on branch metadata. |
| Other service/branch serving Flora URL | Cannot be proven from repository-only evidence; wrong branch metadata is treated as deployment problem when authoritative. |
| Deployment metadata exposed to app | Partially. Commit, branch and build timestamp may be exposed; service, repository, marker, commands and status require environment variables. |

## Most likely current cause

The mismatch is most likely an invalid exact-SHA assumption after a GitHub merge or squash workflow, compounded by missing deployment timestamp and candidate runtime fingerprint metadata.

## Known limitations

Render API state is not available to the running application unless passed through environment metadata. When metadata is missing, the panel safely reports **Metadata incomplete** and does not require the Chief Architect to inspect Render manually.
