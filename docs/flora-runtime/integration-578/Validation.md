# Integrated validation and acceptance limits

The draft integration PR identifies the exact committed candidate; its current-head hosted Checks are authoritative. Full local and hosted validation run **after the source is committed and frozen**. Exact source/checkout SHAs, per-suite counts and comparator issues are recorded in the existing sanitized CI artifacts. Do not infer a passing current-head gate from the earlier component PRs.

## Observed focused / browser results

- **161 focused tests passed:** Offers v1 (58), retained Technology owner journey, Technology UX #573, existing Pipeline and four narrow banner route/accessibility scenarios.
- **39 CI-policy tests passed:** existing 25 plus 14 release-preflight tests. Refusal cases include abbreviated/injected SHA, invalid branch, foreign repository/environment, moved head, changed main ancestry, absent independent protection, missing/wrong/foreign/pending/failed/cancelled CI, newer failure over old success, skipped feature/security gates, network-read failure, fixed-origin GET-only transport and refused redirects. These are synthetic GitHub-response fixtures, not proof that a production environment or connection exists.
- **Six banner browser scenarios passed** across desktop/iPad/mobile and district/all-participant screens: 44–88px native link, unchanged artwork endpoint, placement above the table, single heading, keyboard activation, native no-JS sorting and no horizontal overflow. [Checks](previews/Banner-Checks.json), [screenshots](README.md).
- **63 retained Technology responsive checks, 32 keyboard district activations and 15 unchanged Banking/Aviation/enterprise/Macro parity captures passed** against clean main. Zero external requests or network writes. [Sanitized results](Technology-Browser-Checks.json).
- **217 integrated Offers owner/browser checks passed** with isolated synthetic identities, real local HTTPS/authentication/CSRF, private version creation/review, explicit Studio opt-in and private combination drafts; zero Pipeline files created. [Sanitized checks](offers-previews/Browser-Checks.json). These omit the earlier standalone #577 comparison-to-main captures because Technology's intended integrated changes make those captures different.

The banner harness initially read a URL before keyboard navigation completed; waiting for the actual native navigation fixed the harness without changing application behavior. No security/test exception was relaxed.

## Required full gate

The unchanged 01b comparator enforces **1,432 baseline identities**: normally 1,365 passing cases, exactly 57 inherited failures (21 domain, 12 financial, 24 legacy) and ten inherited skips with their approved signatures/reasons. **Strict security must pass all 388 without skips.** Baseline, normalization and exception records are unchanged. New integration/Technology/Offers tests and release-policy tests are retained as separate current workflow gates.

The final local result is reported in the PR handoff and exact-SHA sanitized artifacts; the hosted workflow must complete successfully for that source head and tested merge tree. If any final merge/squash/rebase creates a different SHA, validate it again before release. No source edit after a passing run can inherit that run's status.

## Data and authority preservation

`Protected-Owners.json` records byte identity against main for the existing Pipeline writer, security/capability/authority stores, CommercialMission/EmployerContext owner, import/promotion owner, research registry/foundation and Render manifest. No authority schema, canonical research acceptance, existing records, user memberships, production files or Pipeline controls were migrated or overwritten. Source data and source-rights/identity/Unknown limitations are preserved. The original illustration bytes and commercial source JSON remain unchanged. The architecture proposal is integrated as a proposal, not promoted into a new normative standard.

The integration does not invoke a model, autonomous agent, outreach or live Pipeline writer. Studio remains disabled by default. Synthetic preview scripts and test authority are never production seed data.

## Distinct production gate: NO-GO until verified

No Render service ID, configured branch/deploy policy, current deployment SHA, live health/authentication/origin, real IAM, existing disk/capacity or recoverable backup was authenticated in this session. The owner confirmed the origin only; an earlier host network-policy denial was not bypassed/retried. No credentials, service IDs, readiness attestations or deployment were invented. The release helper uses read-only GitHub checks and explicit environment approval and **cannot deploy or establish Render production readiness**.

See [owner-executable exact-SHA deployment and rollback](Render-Owner-Deployment.md) for responsible owners and missing checks. Physical iPad/Safari and assistive-technology owner acceptance remain manual. No merge or production deployment occurs while production readiness is unverified or owner approval absent.

## Reproduction

Use an isolated development environment with the repository requirements; keep test data/logs outside production and never publish private fixture databases, tokens, raw tool logs or environment secrets.

```sh
python -m unittest discover -s tests/ci -v
python -m pytest tests/test_flora_offers_v1.py tests/test_flora_technology_owner_journey.py tests/test_flora_ux_refinement_573.py tests/test_flora_sales_pipeline.py tests/test_flora_integration_578.py -q
python tools/ci/flora_ci.py --output /tmp/flora-integration-final-ci
PYTHONPATH=. python tools/ci/flora_offers_preview.py --output /tmp/flora-integration-offers-previews
```

The full gate requires a new output directory and exports only sanitized artifacts. Browser harnesses require local Playwright/Chromium; `tools/research/check_flora_integration_578.cjs <local-base> <output>` works only against a loopback test server. No dependency or production configuration was added to run the app.
