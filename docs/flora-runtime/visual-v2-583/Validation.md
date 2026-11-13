# Visual v2 validation and reproduction

## Observed focused and browser validation

**34 dedicated scenarios passed**; the combined retained feature run passed **195 tests** and the CI-policy suite passed **39 tests**. The dedicated test file covers statistical partition/rounding/year/units, official weights, non-researched inertness, broader-section versus researched-subsector meaning, real GDP versus nominal GVA, all six UK-only source lineages, retained cutoffs/counter-evidence, finite query/asset paths, forged authority, real revoked sessions, private offer/employer non-disclosure, no commercial/network calls or writes, real HTTP/no-store/CSRF and protected-owner fingerprints. The candidate reruns it together with retained Technology, Offers, Pipeline and integration tests. No existing selection/assertion/baseline is weakened.

**525 browser checks passed**. Browser evidence: [actual check list](previews/Browser-Checks.json). Desktop 1440×1000, iPad landscape 1194×834, portrait 834×1194, mobile 390×844 and 320×780. Checks cover both screens, all six selected factor states at each size, no-JS keyboard/close, actual research-route navigation, 44px targets, no overlaps/overflow, selected note entirely over the artwork, all six controls unobscured, optional full statistical table, viewport-bounded sources, native iPad touch, Chromium accessibility-tree names/headings, Escape/focus/skip, real HTTPS sign-in/workspace/CSRF sign-out, reduced motion and print. All screenshots are public scenes; authentication fixtures are disposable synthetic authority, not production users.

Five pixel comparisons verify the current canonical Home remains unchanged relative to the #582 comparison checkout (whose canonical Home itself matches #580). Source-level checks also preserve its exact function. The preview helper refuses Offers/Pipeline files and cleans up temporary enrollment/authentication/certificate material. Raw logs and private fixture stores are not committed.

## Full exact-candidate gate

Final source is committed/frozen before the full local and hosted run. The handoff and current-head Checks report exact source SHA and results without committing a new post-test head. GitHub's synthetic merge SHA must contain the intended integrated base and have the same source tree as the candidate when base is unchanged.

The retained 01b comparator enforces **1,432 identities**, normally 1,365 passing, with **57 inherited failures and 10 inherited skips** retaining their approved signatures/reasons. **All 388 security tests must pass without skips.** All 39 CI-policy/release-helper tests, Technology owner/UX/integration and Offers gates remain; the Visual v2 gate is additive. This draft adds the integration branch to PR triggers without modifying that branch. No inherited failure is hidden, promoted to a pass or accepted anew.

Public source extracts, generated conceptual assets and all rendering/test/tool/workflow fingerprints are in Source-Manifest.json and Artwork-Manifest.json. Protected-Owners.json fingerprints unchanged canonical/domain/research/security/release owners. Null original publisher hashes are not filled with local extract/artifact hashes. Statistical data provenance remains separate from artwork provenance.

## Reproduce

```sh
python -m pytest tests/test_flora_visual_v2_583.py -q
python -m pytest tests/test_flora_visual_v2_583.py tests/test_flora_offers_v1.py tests/test_flora_technology_owner_journey.py tests/test_flora_ux_refinement_573.py tests/test_flora_sales_pipeline.py tests/test_flora_integration_578.py -q
python -m unittest discover -s tests/ci -v
python tools/ci/flora_ci.py --output /tmp/flora-visual-v2-final-ci
PYTHONPATH=. python tools/ci/flora_visual_v2_preview.py --baseline-root /path/to/clean-home-v1-9aaaa692-checkout --output /tmp/flora-visual-v2-previews
```

Use an isolated local workspace/new output directory, the repository Python dependencies and local Playwright/Chromium. No runtime dependency is added. Physical device/Safari/assistive-technology/high-zoom acceptance remains manual; Chromium emulation is not certification. **No merge, Render inspection/deployment, production data change, paid runtime research or autonomous agent was performed.** Visual owner acceptance and a revalidated final integrated base are required before any later promotion.
