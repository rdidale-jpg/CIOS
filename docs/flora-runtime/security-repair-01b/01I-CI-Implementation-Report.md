# FLORA 01I — CI Implementation and Independent Review Preparation

**Implemented and locally validated; GitHub-hosted CI acceptance remains pending.** No peer approval, merge or deployment approval is implied. The CI-only change is on isolated local branch `codex/flora-security-ci-01i`, based on `8046f31b7a8f9acc630be54e37042e97d1c6965f`. Original published branches, all accepted application/test/evidence files and their relationships remain intact. Nothing was pushed and neither PR was modified.

## Exact CI change set

- `.github/workflows/flora-validation.yml` — one read-only GitHub Actions job.
- `tools/ci/flora_ci.py` — portable selection, execution, comparison, integrity/audit verification and sanitized evidence output; Python standard library only.
- `tools/ci/flora-baseline-v1.json` — explicit version-1 profiles, exact selected identities, inherited failure fingerprints and skip reasons.
- `tests/ci/test_flora_ci.py` — 25 CI-policy tests including actual subprocess pytest regressions, collection/skip/signature errors and corrupted integrity/audit observations.
- `docs/flora-runtime/security-repair-01b/01I-CI-Implementation-Report.md` — this report and reviewer/integration checklist.

There are no application/security implementation changes, production dependency changes, new permissive authority fixtures, workflow publication steps or repository-setting changes. The isolated commit is intended to contain only these five files. Its resulting SHA and post-commit status are reported in the task response; a commit cannot embed its own SHA in its contents.

## Workflow and trust boundary

The workflow covers PRs to `main` or `codex/flora-security-repair-01a` affecting FLORA application, tests, CI tools, requirements, pyproject, security evidence and regression-runner paths. It handles opened/synchronize/reopened/ready-for-review/edited events, including drafts and base retargets. It also covers relevant main pushes and manual dispatch. There is one job, **FLORA security and regression gate**, on Ubuntu with Python 3.12 and a 30-minute timeout.

Permissions are `contents: read`; checkout does not persist credentials. No production environment, secrets expression, OIDC/write permission, self-hosted runner, deployment, release action or `pull_request_target` is used. Runtime roots use per-selection temporary directories through **FLORA_DATA_DIR** and **FLORA_PILOT_DIR**, never production storage. The job supplies no production/provider credentials; common runtime/provider token variables are also removed from subprocess environments. This is runner/credential separation, not a claim that Python test code itself is an OS sandbox. Repository administrators must continue to keep production secrets out of PR jobs.

Security module discovery must match the explicit profile, and all security cases must pass without skips. The 01A profile has 104 cases; the 01B–01E profile has 388 including the original seven adversarial assertions and 23 closure checks. The explicit historical service fixture is used only for the already-approved 39 supplemental cases, never globally or for production-boundary tests. All 26 domain modules run in separate subprocesses and roots. Missing retained packages remain the ten explicitly named/reasoned baseline skips; no private package or local `work/` file is needed for CI execution.

The runner and baseline travel together and support either source boundary. The 01A profile is selected only when the 01E marker is absent and its three security modules exactly match; the 01B profile requires all 15 modules. Forcing the wrong profile or omitting a module fails closed. The CI commit is based on 01B for local validation but can be ported as a **CI-only five-file delta** to 01A under separate publication approval; it does not bring the 01B application into 01A. Do not publish this whole descendant branch directly against main as a purported CI-only PR.

## Versioned failure baseline

Version 1 derives its identity/status ledger from committed 01A review-closure and 01E acceptance records, with failure fingerprints reconstructed from retained accepted raw JUnit and verified by fresh runs. It adds no inherited exception identity: 22 domain, 24 legacy, and 12 separately selected 01B financial diagnostics remain the known failures. The runner has no baseline-writing/update mode. Baseline changes are source changes requiring independent review; a new version must explain each changed obligation or exception.

A signature contains the first failing test source frame/expression and SHA256 of the complete first exception-message line. It normalizes only machine-specific repository roots, object addresses, and one documented volatile checkout-SHA operand in the existing legacy `test_deployment_endpoint_identifies_canonical_import_runtime`. That operand is normalized **only when it matches the known checkout SHA**, including pytest's matching abbreviated representation; its expected `abc123deployed` operand and source assertion remain intact. A different observed SHA, a different test's SHA, source assertion, exception headline or exception class remains a changed signature and fails. Full volatile tracebacks are not treated as portable fingerprints; later assertions after an inherited failure are not inferred to pass.

Exact identity sets, normalized failure signatures, skips and reasons are compared. Missing/extra/duplicate cases, new failures, changed signatures, unexpected skips, collection/setup errors and process/XML inconsistencies fail the gate. Security never inherits a failure exception. Fixed inherited failures are explicitly reported for review. Suite exit code 1 is inspected through this exact ledger; no `continue-on-error`, unconditional success, xfail conversion or silent deselection is used. Infrastructure exit codes are rejected.

## Actual local verification

The final 01B–01E run used a fresh Python **3.12.14** virtual environment installed solely from the unchanged `requirements.txt`; `pip check` passed. Resolved packages included pytest 9.2.0, pydantic 2.14.3, OpenAI 2.54.0, Argon2-cffi 25.1.0 and PyMuPDF 2.1. Repository dependency ranges remain unchanged; future dependency drift can make CI fail and requires diagnosis, not automatic baseline expansion.

| Check | Actual result |
| --- | --- |
| actionlint 1.7.7, workflow schema/expressions | Passed (`-shellcheck=`; external shellcheck integration disabled) |
| CI-policy unit tests, clean environment | **25 passed** |
| 01A complete profile / final-rule replay | **104 security passed**; domain **404 passed / 22 inherited failures / 10 original skips**; legacy **3 passed / 24 accounted failures**; gate PASS |
| Final clean 01B–01E complete profile | **388 security passed**, **404 domain passed / 22 inherited failures / 10 original skips**, **39 supplemental passed**, legacy **3 passed / 24 failures**, financial **35 passed / 12 unchanged failures**; gate PASS |
| Factory / Experience / Governance, included in domain | **88 passed / 8 skips**; **56 passed / 2 skips**; **157 passed** |
| Integrity / audit, independently recomputed by CI helper | **146 unchanged** comparisons; **17 committed record digests matching**, **15 selected valid chains**, **1 cleanup resource audit** |
| Application identity accounting | 01A **567** identities: 511 passed / 46 inherited failures / 10 skips. 01B–01E **937** disjoint identities: 869 passed / 58 inherited/historical failures / 10 skips. Profiles overlap and are not summed. |

The initial full 01B gate correctly failed on the deployment-metadata test's changing checkout-SHA fingerprint while retaining the same test outcomes. The narrowly scoped normalization above corrected that portability issue; no exception ID or test assertion was weakened. The 01A full run was replayed read-only under that final rule and passed. The final clean 01B run executed the complete runner again and passed under the final baseline/rule. Earlier diagnostic runs remain local; their results were not silently overwritten. No new active security/domain failure or unexpected skip was accepted.

Commands executed (paths abbreviated here for portability; output folders were new and separate):

```sh
python3.12 -m venv <clean-venv>
<clean-python> -m pip install -r requirements.txt
<clean-python> -m pip check
actionlint -shellcheck= .github/workflows/flora-validation.yml
<clean-python> -m unittest discover -s tests/ci -v
python tools/ci/flora_ci.py --repo <isolated-01A-checkout> --profile 01a --output <new-01A-output>
<clean-python> tools/ci/flora_ci.py --output <new-01B-output>
```

No runtime command refers to the task's private scratch, old executables or uncommitted prior reports. The local 01A checkout is the pinned original head; the workflow uses its own checkout by default. Tests are selected from the versioned baseline, not by copying private overlays into hosted execution.

### Demonstrated failure behavior

The 25 CI-policy tests include real subprocess pytest runs with deliberately introduced security failure, unapproved skip, malformed collection and changed domain failure signature. Each returns a failing gate with sanitized evidence. Additional tests reject changed source/headline signatures, missing/extra/duplicate identities, changed skip reasons, absent integrity records, changed protected hashes, corrupted audit-chain digests and retained-journal filtering that would hide data changes. Known inherited outcomes pass comparison and remain reported; fixed outcomes remain visible. Tests verify that a wrong profile and missing security discovery cannot pass, output cannot overwrite evidence, and unrelated/wrong SHA changes are not normalized away.

### Retained evidence and limitations

Only `artifacts/summary.json`, sanitized `results.xml` and `summary.md` are uploaded, on success or failure, with seven-day retention. They contain exact identities, counts, inherited/fixed/new classification and normalized signature hashes; JUnit still records failing historical cases truthfully even when the comparison gate passes. The private subtree holds raw logs/JUnit, synthetic stores and backups and is **not** included in artifact paths. Existing corruption tests retain their private recovery evidence; the exported result distinguishes that evidence from protected application files and verifies full observed maps without uploading them.

A preflight failure can result in no generated artifacts; the workflow and upload step then fail, rather than inventing a successful report. Hosted artifact permissions/availability, actual GitHub event/path filtering, merge-candidate checkout, installed action versions, timing, cancellation and job token enforcement have **not** been verified by a GitHub-hosted run. Local actionlint and subprocess execution do not constitute hosted CI acceptance. The current published PRs still lack this new workflow until separately approved publication.

## Dependency, publication and integration sequence

Read-only GitHub inspection reconfirmed #539 open/draft/unmerged at `83aee1aaf5a49b36d8c5e397d75b99624422fac3`, targeting main `dc9203e6880f8722e821d39cf53b689732edb0e7`; #540 remains draft on 01A at `8046f31b7a8f9acc630be54e37042e97d1c6965f`, with its approved 61-file delta. No retarget occurred.

1. Obtain separate approval to publish the CI-only delta on an appropriate 01A-based branch/change, inspect the resulting scope and update the stack deliberately without force-pushing. CI placement necessarily changes SHAs; refresh dependency references under authorization and preserve historical acceptance records.
2. Review and validate #539's actual main integration candidate using the 01A profile. Obtain independent approval and explicit permission to merge #539. Verify main integration cannot inadvertently trigger an unauthorized deployment; actual Render autodeploy settings remain unverified.
3. Only after its separately authorized merge, inspect #540's base, ancestry, effective diff and overlapping paths. Do not assume retargeting happened automatically, and do not retarget it now. Any future retarget/base update needs authorization.
4. Run required CI on #540's updated-base candidate, confirm intended scope and re-obtain any stale independent approvals. Obtain separate independent approval for #540.
5. Consider either merge only through a separately authorized action. Neither is currently declared merge-ready, and successful code integration would still not approve production activation/deployment.

Preserving normal merge ancestry for #539 simplifies the stack. If squash/rebase policy is required, explicitly plan descendant/base reconciliation and rerun checks; do not rewrite or force-push by default. Code rollback would be a reviewed reverse-order revert (#540 before #539), not a reset. Reverting to pre-01A trust behavior can restore insecure access and is not an automatic safe fallback. Any later deployed rollback must separately coordinate authority/schema/audit/data, retained journals, verified backups and session revocation. Unsealed journals require inspected recovery; never fabricate ownership or discard recovery artifacts to unblock a downgrade.

## Independent reviewers and concise checklist

No reviewer identities were available; none were invented or contacted, and no self-approval was supplied.

- **Authentication/workspace/ACL reviewer:** verify Bootstrap v1.0 and verified-context compatibility, no legacy/caller-made authority, revocation/expiry and recent authentication, exact persisted selected workspace/capability/ACL intersections, canonical financial destinations, CSRF and public-route boundaries. Review positive owner journeys as well as denials.
- **Transaction/audit/recovery reviewer:** trace mutation envelope, writer-lock ordering, promotion/deletion/revocation races, independently committed-data survival, mandatory resource audit/rollback, complete snapshot/backup validation, retained corrupt artifacts and retry. Review actual CI integrity verification rather than just green pytest counts.
- **Application/regression reviewer:** confirm legitimate financial apply/model updates and candidate lifecycle behavior, Factory/Experience/governance compatibility, exact 22/24/12 failure registers and ten retained-input skips, without conflating explicit historical fixtures with authentication proof.
- **All reviewers:** inspect the five-file CI delta, baseline/version changes and narrow metadata normalization; ensure no security exception, new skip, raw sensitive artifact or private work dependency is hidden. Record decisions against exact tested head/base SHAs and resolve material comments.

The inherited product/harness failures remain visible quality obligations and need owned triage before production acceptance; they are not new demonstrated vulnerabilities or an automatic waiver. New security failures, changed failure signatures, infrastructure errors, unexpected skips, scope drift or missing independent approval are genuine CI/integration blockers.

## Protection-policy limitations and next controlled action

The 01H read-only branch summaries reported protection disabled and required contexts empty for main and both stack branches; the visible rulesets list was empty. Detailed protection reads returned 403 to the integration, so administrator policy verification remains required. No protection/ruleset changes are included here. Because this workflow has path filters, do not globally require its check for unrelated path-only PRs without an approved always-on scope gate or filter-policy adjustment; otherwise a skipped required check may remain pending. After a real hosted run, confirm the exact check context and separately approve any desired enforcement/review settings.

**Next action:** review this isolated CI commit and, only after separate approval, publish the CI-only change and controlled stack reconciliation; then verify hosted runs, safe artifacts and the independent review decisions. CI implementation is not CI acceptance, peer approval, merge authorization or deployment approval.

## Exact Git status

Captured in the isolated checkout immediately before staging the five-file CI commit (original published branches and their excluded historical files were preserved in their original checkout):

```
?? .github/workflows/flora-validation.yml
?? docs/flora-runtime/security-repair-01b/01I-CI-Implementation-Report.md
?? tests/ci/test_flora_ci.py
?? tools/ci/flora-baseline-v1.json
?? tools/ci/flora_ci.py
```

Only the five listed files are authorized for this local commit. No source/evidence files from the accepted stack were edited. Final commit SHA, verified committed inventory, clean isolated checkout/index and unchanged published refs are reported after commit in the task response. No push, PR modification, approval, merge, deployment, repository setting or production change was performed.
