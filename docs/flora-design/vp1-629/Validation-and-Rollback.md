# Validation and rollback

Exact final SHA and hosted run/job URLs are recorded in the draft PR’s validation comment. This avoids a self-referential validation commit. Baseline main8a passed full post-merge CI43709888042 before branching. All application/security/owner/source files remain byte-identical to baseline; only this new design directory and its dedicated assurance workflow are added.

## Reproduction

From repository root with project Python dependencies and Playwright/Chromium:

```
PYTHONPATH=. python docs/flora-design/vp1-629/build.py
PYTHONPATH=. python docs/flora-design/vp1-629/checks.py
PYTHONPATH=. python docs/flora-design/vp1-629/preview.py --output /tmp/flora-vp1-previews
python -m pytest tests/test_flora_security*.py -q
```

The standard-library static checks cover three-region ownership, native link/fragment closure, scoped selection, inert concepts, original/derivative hashes, unchanged owners, source pins, semantics/financial definitions/rights attribution and byte-reproducible HTML export. The generated reference/crop sheet is separately labelled a review artifact, not a product composition.

The browser harness serves the static prototype locally and starts the unchanged public application renderer with isolated temporary storage for baseline captures. It does not authenticate as a production owner or read/write private data. Source activation is intercepted locally to verify the exact public link; it is not a publisher availability or rights check. Browser source paths and no-JS links require no external service or paid model. No Offers/Pipeline domain file may be created by captures.

Local security checks retain all388 strict tests and original assertions; no failure/skip baseline or comparator changes. The dedicated hosted workflow checks exact PR head, runs the same static/browser tests and original security modules, and publishes previews plus a portable prototype artifact. It does not merge or deploy. Full main27-suite CI is the baseline evidence; design-only changes do not require re-running an unchanged application’s full inherited-failure comparator, nor claim all inherited failures are fixed.

Local frozen proof:16 static checks,935 browser checks,388 strict security cases;118 JPG previews. Final exact-head hosted results are recorded in the PR. Local tooling:Python3.12,Playwright1.62.1,Chromium154.0.8037.57; hosted uses the pinned Playwright Chromium build. Cross-platform pixel identity is not claimed.

## Browser scope

1440×900 desktop;1280×720 laptop;1194×834 iPad landscape;834×1194 iPad portrait;390×844 and320×740 phones. Additional effective200% reflow, all-element200% text enlargement, long scope/detail names,844×390 phone landscape, iPad DPR2, forced colours/reduced motion, missing-image navigation, keyboard/touch/collapse focus, active states, source disclosure/activation, chart comparison, Back/Forward/deep links and native no-JS journey. Default compact Left is closed, with separate expanded previews.

The all-element stress test records computed sizes before doubling each element, preventing compounded inheritance, then verifies every resulting size. Effective zoom is emulated viewport reflow, not a claim of operating a physical browser zoom control. Long-text stress repeats existing text only inside an ephemeral test page; no fabricated research is committed.

Cold performance observations are single-run loopback emulation at1.6Mbps/150msRTT. FCP is text/initial paint, not full art readiness. On compact screens the portrait is not requested until expanded. Source artwork delivery is responsive WebP with unchanged PNG masters retained. There is no production latency/SLA, physical Safari/iPad, screen-reader or formal WCAG certification claim.

## QA corrections

The initial FCP collector raced the first paint entry. An explicit paint/resource completion wait corrected the harness; no threshold or assertion was removed. A uniqueness check found two identical Main landscape watermarks; subject-specific line geometry corrected the assets. Source-master captions, source/event dating, focus targets, all-text enlargement and on-demand OGL attribution were corrected during review. Final exact-head results supersede preliminary reports.

## Stop and rollback

Owner visual and architectural acceptance must precede a separate implementation issue/sprint. No code here changes production routes, permissions, source admission, accepted research, Offers or Pipeline. Static “Owner” identity is illustrative and grants no authority. Existing research/Owner Command Centre access remains protected.

Rollback is simply discarding this design branch or reverting the new design-directory/workflow commit. Do not revert merged INT’s security/semantics or delete original imagery/research branches. There is no migration, canonical import, production-data compensation, feature flag or Render rollback to perform. Any later application implementation needs its own route/IAM/source/performance/regression and owner-release gates.
