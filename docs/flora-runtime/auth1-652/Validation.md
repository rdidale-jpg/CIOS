# AUTH-1 validation

The final PR comment identifies the frozen SHA and local/hosted results. Committed screenshots are real pre-commit worktree renders; the AUTH-1 workflow reproduces the same journeys at the exact PR head. The full existing validation workflow still runs all27 comparator suites, including388 strict security cases. No failure/skip baseline or comparator changes.

## New fault and positive tests

`tests/test_flora_auth1_652.py` contains45 cases. It uses real disposable SecurityStore/offline authority/ACL services, not production data. Coverage includes:

- Missing root, security directory and database; mode/owner/symlink/hardlink failure; unchanged missing state rather than replacement files.
- Actual exclusive SQLite locking, corrupt/empty bytes, unrecognised schema/extra columns/views/tables, missing/wrong schema metadata, invalid membership JSON and filesystem read-only state.
- Pending SQLite sidecars/WAL headers refused before SQLite open. Explicit operator quiescence required before SQL. Unexpected backend/configuration errors produce no paths/secret text/tracebacks.
- Malformed protected JSON/UTF-8/non-object manifests fail as generic503. A real subprocess interruption leaves a sealed pending journal and changed fixture payload; inspection retains both rather than attempting undo/cleanup.
- No invocation of transaction/preauth/bootstrap/audit/recovery/startup probes by the diagnostic; bytes/ownership/modes remain unchanged under the controlled quiesced fixtures.
- HTTP failure pages disclose no cause/path/token and issue no cookies; public Banking remains readable and private routes remain denied.
- PRAGMA setup failure closes its connection and does not leave active authority.

These45 cases combine direct service/metadata assertions and selected actual HTTP probes; they are not all browser tests or production proof.

## Browser proof

`tools/research/auth1_proof.py` uses an isolated existing authority provisioned through the established offline test fixture route, actual Argon2 enrollment/login, current memberships/resource ACL and actual permitted Financial data. No production accounts or credentials are involved. It preserves the same fixture database through the missing-file failure; no replacement is created.

The actual loopback HTTPS110-check harness covers unavailable store before/after, controlled schema-row503 versus the baseline transport failure, sign-in, secure preauth/session cookies, workspace selection, direct authorised Nationwide earnings, protected absent-run preparation, Guest/forged/foreign/no-resource/revoked denials, CSRF/origin and logout. Screens cover1440/1280 desktop, both iPad orientations and390/320 mobile. They emulate Chromium, not physical Safari or assistive-technology certification. Existing UX-R1/Financial/VP-2 browser workflows remain enabled and unchanged.

Diagnostic `read_only_checks_passed` does not itself prove writable authentication, correct specific bindings or live Render. The browser proof establishes the isolated journey separately. Live source/mount/configuration remains UNKNOWN.

## Reproduce safely

```sh
python -m pytest tests/test_flora_auth1_652.py -q
python tools/research/auth1_quality.py
python tools/ci/flora_ci.py --output /tmp/auth1-exact-ci

git worktree add --detach /tmp/auth1-before 836a4c29015c59117b873e6324c9618f7eb41930
python tools/research/auth1_proof.py --output /tmp/auth1-proof --preview --baseline-root /tmp/auth1-before
```

Install repository requirements and Playwright1.62.1/Chromium. Never point test fixtures at production storage. Diagnostic commands for actual operator observation are in [Operator-Recovery.md](Operator-Recovery.md), with explicit backup/quiescence and authority limits.

## Scope and artifact safety

`auth1_quality.py` verifies only the reviewed existing transaction/recover/operator-entry functions changed; other definitions and schema remain AST-identical. Auth resolver, web authentication, roles/permissions, legacy pilot refusal, root/storage owner, web dispatcher, Financial calculation owner, Render blueprint, baseline/comparator are byte-identical. All51 visual files and178 retained research files remain unchanged through existing QA.

Workflow upload allowlists contain sanitized JSON/check labels and screenshots only. Temporary browser config/password, DB, cookies, certificates, private rows and raw logs are excluded. The proof reports exact **commit** SHA and aggregate/check results, not password/token/audit hashes. No secret material or production evidence is published.

## Owner acceptance

- [ ] Review the exact final SHA, independent critique, full security/comparator and browser evidence.
- [ ] Accept the bounded connection/schema/journal error handling without interpreting it as a database recovery.
- [ ] Verify the actual Render service/SHA/runtime, existing disk/root and independently protected backup.
- [ ] Obtain only the authorised read-only operator observations needed to identify the actual blocker.
- [ ] Approve any later recovery/configuration action separately; no initialization, replacement Owner or credential reset through this repair.
- [ ] Independently verify live existing-account sign-in → workspace → Banking → Nationwide after an approved recovery. Until then, do not mark Render repaired.
