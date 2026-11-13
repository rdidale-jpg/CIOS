# Validation, exact candidate and reproduction

## Observed development checks

- **237 focused tests passed**, followed by the final explicit Aviation sales-context case and contrast check passing. The committed candidate repeats the expanded **238-case selection**: 26 unified-system cases, 34 approved-world cases, retained feature checks and the two adapted legacy navigation/Home accessibility cases. Base ink/muted/focus contrast is checked quantitatively; this is not a whole-product WCAG certification.
- **692 responsive browser checks passed** across desktop 1440×1000, iPad landscape 1194×834, portrait 834×1194, mobile 390×844 and 320×780. The gallery contains 108 actual before/after screenshots and two print exports.
- Browser coverage includes default eight industry names/44px targets/native focus; six-column company-only row navigation and native sorting; preserved NVIDIA financials/three buyer hypotheses/source access; every PESTLE factor at all sizes with the note inside the image and controls unobscured; no-JS conceptual model selection; real synthetic HTTPS sign-in/workspace/CSRF forms/sign-out; private route denial; manual Offers→new qualification GET; no page overflow; Escape/skip/accessibility tree; reduced motion and print.
- **39 CI-policy/release-helper tests passed**. The strict selection, comparator, baseline and release machinery are unchanged and fingerprinted.
- Both synthetic before/after workers verify **Offers and Pipeline bytes remain unchanged by browsing**. The helper explicitly seeds a local demonstration record before that check. It is not a claim that all test setup performs zero writes, and it never touches production.

Browser results and editorial counts are committed sanitized artifacts, not raw tool logs. Synthetic authority, enrollment deliveries, cookies, passwords, certificates and fixture stores are temporary and removed by the helper. Private fixture screenshots are explicitly labelled synthetic in the gallery/assessment.

## Full exact-head local and hosted gate

Source is committed/frozen before final full validation. The PR/current Checks and handoff identify the exact candidate SHA. No later documentation-only source commit is made after final checks. GitHub's synthetic merge must contain the approved base and match the candidate's source tree when that base is unchanged.

The unchanged 01b gate enforces **1,432 identities**: normally 1,365 pass, **57 inherited failures and 10 inherited skips** retain approved signatures/reasons. **All 388 strict security tests must pass without skips.** The additive UI tests do not alter that selection. Full local/current-head hosted checks are required; a component PR's earlier green status is not a #585 result. Results are reported in the handoff/current Checks, not fabricated in advance.

`Protected-Owners.json` fingerprints **198 unchanged files** including research/model data, security/permissions and their tests, employer context, Offers engine, Pipeline writer, CI comparator/baseline and release helpers. Five approved artwork/statistical assets are separately pinned. Three presentation-owner exceptions to the older #584 guard are explicit: Offers views, unified views and the navigation registry. All other protected owners remain byte-identical.

## Readiness blocker discovered by the full gate

The first frozen candidate exposed a real specialist route regression: the flagship-only enterprise registry did not include every legacy bank. The presentation parent now uses the explorer’s existing Banking/Aviation scope, preserving Barclays and other bank discovery without broadening access. Targeted specialist tests pass. Canonical Home assertions are adapted to the approved industry destinations.

Two strict security checks additionally caught missing established owner Controls/sign-out presentation and an obsolete declared Home handler. The shared header now uses the existing authorised account presenter; the finite public catalogue declares the actual read-only canonical Home handler. Both original, unchanged security tests pass. Responsive screenshots and all **692 browser checks** were regenerated after these corrections. The living-map assertion now checks its retained accessible contextual-inspection label instead of the removed decorative numbered heading; node IDs, protected-route denials and every layer assertion remain.

Visual inspection of the refreshed Home caught the shared anchor reset overriding the approved dark research-pill foreground. A scoped colour rule restores readable labels; five new computed browser contrast checks cover all three links at every viewport. All **692 checks pass** and the full preview pack is regenerated.

The full comparator also detects changed signatures for inherited failures whose rendered-HTML exception text changed with the shared shell. The original failing assertions remain; these are not automatically accepted as equivalent failures. The comparator, baseline and exception records remain unchanged. This is a **NO-GO for integration** until the exact-head gate passes or a separately reviewed baseline reconciliation establishes equivalence. Do not merge or deploy this draft. Final local and hosted outcomes are reported in the PR and handoff.

## Presentation-test adaptations

Existing UI assertions are updated for the approved design, not removed to hide failures: seven compact destinations instead of the old five-link bar; one scoped Technology demo link alongside the separate protected live Pipeline; readable image labels instead of a duplicate phone legend; three NVIDIA section names; approved world/skip/20-sector Home instead of a question form; and compatible presentation-owner changes. Original test identities are retained for the versioned comparator. The original Home function remains as a compatibility helper, while separate HTTP tests verify the intentional new canonical route. No security test, data validation, source scope assertion or baseline exception is weakened.

After consolidating the header onto the original navigation registry, four representative public views retained identical rendered HTML bytes; the captured composition did not change. The final candidate still receives the complete committed-source tests.

## Reproduce safely

```sh
python -m pytest tests/test_flora_design_system_585.py tests/test_flora_visual_v2_583.py tests/test_flora_technology_owner_journey.py tests/test_flora_ux_refinement_573.py tests/test_flora_offers_v1.py tests/test_flora_sales_pipeline.py tests/test_flora_unified_experience.py tests/test_flora_integration_578.py -q
python -m pytest tests/test_flora_v2_information_architecture.py::test_primary_navigation_uses_five_executive_destinations tests/test_flora_web.py::test_home_accessibility_basics -q
python -m unittest discover -s tests/ci -v
python tools/ci/flora_ci.py --output /tmp/flora-design-system-final-ci
PYTHONPATH=. python tools/ci/flora_design_system_preview.py --baseline-root /path/to/clean-19ab36d-checkout --output /tmp/flora-design-system-previews
```

Use a new isolated output/data directory, repository Python dependencies and local Playwright/Chromium. No runtime dependency is added. Preview servers bind loopback only and stop after capture. Physical device/assistive technology/high-zoom review remains manual. **No main/PR merge, Render call/deployment or production data change is performed.** #578 production-readiness checks remain a separate gate.
