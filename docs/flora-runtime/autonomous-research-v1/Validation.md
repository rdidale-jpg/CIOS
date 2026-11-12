# Validation evidence

Actual main `c3b818cbae7a2f88930d26bcd65b2dab7263e19f` was checked out in a separate worktree and the full established gate executed, rather than assuming earlier totals. Result: **PASS, 1,302 passed / 57 matched inherited failures / 10 original skips / 1,369 unique identities**. The exact failed identities/signatures and original skip reasons are retained in [Actual-Base-Comparison.json](Actual-Base-Comparison.json). Domain: 405 passed/21 inherited failed/10 skipped; financial: 35 passed/12 inherited failed; legacy: 3 passed/24 inherited failed. These failures remain product/diagnostic limitations, not newly passing tests.

Final focused foundation run: **76 passed**. Coverage includes scope/rights/schema/date enforcement, wrong-subsidiary identity separation, stale/conflicting passages, copied-source family counting, separate verifier acquisition, injection/sensitive/private rejection, request/byte/retry caps, pause/resume, idempotency, cancellation, all three unsupported future-mode runners, withdrawal/supersession, derived-state rebuild, immutable prior releases, archive tampering, public snapshot integrity and HTTP read-only/private-store isolation. Fixture acquisition is explicitly labelled and never substituted for the actual web demonstration.

The CI baseline adds exactly these 76 **passing** identities as a new suite; every previous suite definition, inherited failure fingerprint, skip reason and 388-test security selection remains structurally identical to the actual base. The exact source-inventory assertion is updated explicitly for five approved additions, while all previous 160 files remain byte-identical. Unknown files, changed historical bytes and changed new-source hashes continue to fail.

Other completed checks:

- 25 CI policy/comparator tests passed, including deliberately introduced failure, skip and identity-change rejection. Their expected negative-gate output is not a real product-suite failure.
- `actionlint .github/workflows/flora-validation.yml` passed. Workflow change adds only `enterprise-knowledge/technology/**` to existing PR/main path filters; commands, permissions, baseline policy and production boundaries are unchanged.
- Python compilation and `git diff --check` passed.
- Actual Chromium validation: desktop 1440×1050, tablet 1024×1366, mobile 390×844; navigation, category/provider/evidence/gap panels and no overflow/JavaScript exceptions. Desktop SVG link keyboard activation tested. [Browser-Validation.json](Browser-Validation.json) records results; screenshots are in [previews](previews).
- Evidence print generated as a local A4 PDF; extracted text includes source checksums, named provider and distinct acquisition receipts. No formal tagged-PDF/accessibility certification is claimed.
- [Correction-Drill.json](Correction-Drill.json): synthetic fixture claim withdrawal invalidates six objects spanning the claim, relationship, hypothesis, index and two visual projections; new release has zero claims, prior release is unchanged. This is not a real catalogue correction or live production write.

The complete candidate gate and GitHub-hosted gate must report their own actual conclusions. Publication will attach the tested commit, run URL, per-suite comparison and sanitized artifact evidence to the draft PR; local focused passes are not represented as hosted acceptance.

Reproduce:

```sh
python -m pytest tests/test_flora_autonomous_research_v1.py -q
python -m unittest discover -s tests/ci -q
python tools/ci/flora_ci.py --output /tmp/flora-foundation-ci-UNUSED
# With separately launched isolated HTTPS main/candidate servers:
python tools/research/validate_flora_foundation_ui.py \
  --base-url https://localhost:8874 --baseline-url https://localhost:8873 \
  --output /tmp/flora-foundation-browser-UNUSED
```

The browser runner requires Playwright and Chromium; it does not start a service, provision identities, seed data or contact production. Raw test stores, SQLite ledgers, source-tool responses with contact fields, local logs and the unused initial operational directory are not part of the PR. No production changes, canonical promotions, Pipeline qualifications, unattended monitoring, merge or deployment occur.

A targeted post-gate checkpoint replay found that returning an existing release left the job's status as `assessed`. The follow-up correction restores `released` in the same transaction; the existing resume test now asserts that state as well as unchanged release, acquisition count and retained bytes. No test identity or inherited baseline entry changes. The initial full candidate gate passed; final hosted/local evidence must identify the subsequent corrected commit explicitly.
