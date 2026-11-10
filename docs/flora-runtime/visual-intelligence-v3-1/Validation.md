# Issue #554 — validation and product acceptance

## Local results

- Complete strict command: `python tools/ci/flora_ci.py --output /workspace/flora-commercial-v31-ci` — **PASS**. After the final display-only Pipeline stage/value labels, the full refresh in `/workspace/flora-commercial-v31-ci-final` was started; its completed conclusion is reported with actual-candidate hosted CI in the delivery response.
- **1,162 passed / 57 exact signature-matched inherited failures / 10 original skips = 1,229 identities**. The prior 1,140 passes remain, with **22 additional v3.1 passes**.
- Includes **388 strict security**, **27 existing v3**, **22 new v3.1**, **25 sales Pipeline**, **29 living maps**, **32 visual intelligence**, **36 enterprise understanding**, **25 research cycle**, **4 research diagnostic**, **15 unified experience**, **39 supplemental**, **18 primary enrichment**, **18 research intelligence**, **8 multi-industry**, **8 commercial assessment**, **12 Banking Explorer**, **13 Aviation**, domain **405 passed / 21 inherited failures / 10 original skips**, financial **35 passed / 12 inherited diagnostic failures**, legacy **3 passed / 24 inherited contract failures**.
- `python -m unittest discover -s tests/ci -v` — **25 passed**, including deliberate synthetic baseline violations. `actionlint .github/workflows/flora-validation.yml` and `git diff --check` passed.
- Final-revision focused run: existing v3 + Pipeline + new v3.1, **74 passed**. The earlier split runs were 52 and 22 passed. These overlap the strict totals; they are not added again.
- Comparator preservation checked structurally against `f8b0dcb`: remove only the new `commercial_usability_v31` suite and the complete baseline is identical. No failures, skip reasons, identities or prior selections were relaxed.

New identities are explicitly listed as passing under `profiles.01b.suites.commercial_usability_v31` in `tools/ci/flora-baseline-v1.json`, selected by `tests/test_flora_commercial_usability_v31.py`. Coverage includes both industries, empty/unsupported lists, concise summary plus visible contradictions, every sales stage independent of customer/pursuit validation, missing/forged references, boolean review, immutable provenance and idempotence, rejected direct-service and HTTP maturity fields with unchanged storage hash, saved-versus-restored-draft status, compact register/filter/board/empty states and public exploration with private lookups forbidden. Existing authority/ACL/CSRF/session/revocation/transaction tests remain intact.

## Browser and visual results

[Browser-Checks.json](Browser-Checks.json) records Chromium/Playwright checks at 1440×1080, 1180×820 and 390×844 with reduced motion. Both industry lists and Core Platforms keyboard/touch selection passed. Desktop/tablet focus the selected SVG activity; below 600px the preserved v2 text alternative focuses the corresponding native inspector. The public enterprise → candidate → support/counterevidence path, deliberate synthetic capture → rejected incomplete qualification → ten explicitly synthetic references + review/confirmation → Qualified → private Pipeline → idempotent link passed. The same stored record is reused for later viewports. No script errors or page-wide horizontal overflow occurred. No-JavaScript list/hypothesis/investigative disclosure passed.

The first record's vertical position, measured from page top with the same one-record state:

| Viewport | v3 before | v3.1 after | Reduction |
| --- | ---: | ---: | ---: |
| Desktop | 1,484px | 709px | 52% |
| Tablet | 1,455px | 705px | 52% |
| Mobile | 1,870px | 1,013px | 46% |

Desktop/tablet show the record in the first viewport. Mobile still needs approximately 169px of scrolling beyond an 844px viewport, largely because the existing global navigation and notices remain; no claim of zero-scroll mobile operation is made. [Full mobile before](previews/pipeline-before-mobile-full.png), [full mobile after](previews/pipeline-after-mobile-full.png), [mobile record detail](previews/pipeline-register-mobile.png).

Map, hypothesis and private qualification PDFs were captured. Before/after print restores the exact original disclosure-open state. Synthetic zero-evidence desktop/tablet/mobile previews are presentation fixtures, explicitly labelled, and do not alter research or create Pipeline records. Private preview instances began empty and used disposable synthetic identities, sessions and manually entered demonstration inputs; no demo seeding tool or production account was used.

## Product acceptance assessment

**Engineering acceptance supports draft product review.** A user can find hypotheses through the optional map list, focus a mapped activity, reach Lloyds/easyJet, read a six-part source-scoped decision brief, inspect visible counterevidence and deliberately continue into the existing authorised qualification/Pipeline. The register appears substantially earlier. Input completeness and sales stage no longer imply verified customer demand.

This is not verified customer demand or production acceptance. No real sales-director study, comprehension improvement, win rate or customer adoption has been measured. Customer/pursuit validation remains explicitly not established; physical iPad/Safari and screen-reader user testing remain outstanding. Historical source limitations, the 57 inherited failures and ten retained-artifact skips remain visible and unchanged.

## Hosted validation boundary

The published draft must target `codex/flora-commercial-visual-intelligence-v3`, depending on #553 and #551. The workflow adds that exact branch to PR eligibility without changing permissions, commands or strict policy. Actual immutable-candidate GitHub run/result and artifact links are supplied in the delivery response; local results alone do not establish hosted acceptance. No merge, retargeting of parents, deployment or production modification is authorised or performed.
