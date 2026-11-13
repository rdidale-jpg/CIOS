# Home v1 design-preview validation

## Actual focused/design results

- **43 Home scenarios passed** using real revocable authority where private context is exercised. Coverage includes public/private separation, forged-header rejection, country/lens selector validation, existing canonical Home retention, native labelled regions, global/local source distinction, empty Economic lens, original publication dates, no freshness from retrieval, approved/proof-referenced offer eligibility, stable assessment links, private focus isolation, revoked membership/account scope, escaped private declarations, visible read failure, no commercial role access, no unsupported French recommendations, and no domain/Pipeline or outgoing network/model activity.
- The combined retained feature run passed **202 tests** before the final explicit no-commercial-role and no-proof-reference Home cases were added. The final committed candidate reruns Home and all retained Technology/Offers/Pipeline/integration scenarios together. No assertion, exception, baseline or security selection was weakened.
- **39 CI-policy tests passed**; the integration's exact-SHA read-only release helper and all its refusal tests remain unchanged.
- **172 responsive/authenticated browser checks passed**, with desktop 1440×1000, iPad landscape 1194×834, iPad portrait 834×1194 and mobile 390×844. Additional 320px overflow/touch checks, native skip focus, no-JS country/lens/industry navigation, 44px+ region targets, source/empty-state rendering, real local HTTPS/sign-in, authenticated focus/plays, reduced motion and print were exercised.
- Four before/after pixel comparisons verify the **canonical Home remains unchanged** against the validated #578 integration base, even while private fixture data exists in the candidate's runtime. The design prototype is separate at `/home`.
- The preview script fails if it creates a Pipeline file. It uses disposable synthetic employer/seller/reviewer approval fixtures and removes their private authority, passwords, enrollment deliveries and self-signed certificate. Only pictures, print output and sanitized check descriptions are committed. No production data or real business approval is represented by those fixtures.

[Browser evidence](previews/Browser-Checks.json) · [Review gallery](README.md) · [Ownership audit](Country-and-Ownership-Contract.md) · [Design assessment](Design-Assessment.md)

## Full exact-candidate gate

The source is committed/frozen before the final full local and hosted validation. The draft PR and sanitized hosted artifacts identify the exact source head, synthetic checkout SHA and result. A component PR's earlier green run is not a Home result. PR target is the separate integration branch; its test merge must retain the intended integrated base. If the base changes, reconcile and revalidate before promotion.

The unchanged 01b comparator enforces **1,432 identities**, with 1,365 normally passing cases, exactly **57 inherited failures and 10 inherited skips** retaining approved signatures/reasons. All **388 security tests** must pass without skips. Current workflow retains the full gate, existing 39 CI-policy tests, Technology owner/UX/integration tests, Offers tests, and adds the Home-specific test step. It includes the integration target in PR triggers but does not edit that branch or run a deployment helper.

The actual final full local/hosted results are reported in the PR handoff/current Checks, without committing a new post-test source head. Source and protected-owner fingerprints are in `Source-Manifest.json` and `Protected-Owners.json`.

## Preserved contracts and limits

Canonical Home and its original function body, navigation owner, Offers matcher/state owner, employer profile owner, permissions, authority/CSRF/origin, Pipeline writer, existing research JSON/contracts and release configuration remain unchanged. The only Offers-view change is an HTML ID on an existing assessment row, enabling a native Home link; it changes no source, recommendation, permission or mutation path.

Personal rendering reuses the existing verified read transaction/revocation lock. Every private read is subject to current server authority; user/country headers and query strings cannot confer access. Existing no-store response handling is retained. Normal session refreshes remain the authentication owner's existing behaviour, not a new domain mutation or geography store.

Existing source/status/identity/rights limitations remain; no canonical acceptance, private-public promotion, synthetic live records, paid runtime calls, agents, outreach or Pipeline writes are introduced. What's Changing is a bounded selection of source-dated records, not a live news service. France is a layout extension with limited existing macro inspection, not industry research expansion. Unsupported lenses/data remain unfilled; no estimates or currency conversion are fabricated.

Physical iPad/Safari, screen readers, high zoom and real production performance remain owner/manual checks. No merge or deployment is authorised. Visual owner acceptance precedes canonical Home implementation and any release after integration #578 completes.

## Reproduce in an isolated development workspace

```sh
python -m pytest tests/test_flora_home_v1_579.py -q
python -m pytest tests/test_flora_home_v1_579.py tests/test_flora_offers_v1.py tests/test_flora_technology_owner_journey.py tests/test_flora_ux_refinement_573.py tests/test_flora_sales_pipeline.py tests/test_flora_integration_578.py -q
python -m unittest discover -s tests/ci -v
python tools/ci/flora_ci.py --output /tmp/flora-home-final-ci
PYTHONPATH=. python tools/ci/flora_home_preview.py --baseline-root /path/to/clean-integration-base --output /tmp/flora-home-previews
```

Use a new full-gate output directory. Browser reproduction needs local Chromium/Playwright and the existing repository Python dependencies; no runtime dependency was added. Never point fixture tools at deployed data or publish their raw logs/databases/configuration. The temporary local HTTPS certificate and synthetic authentication exist only to exercise existing production boundaries, not to weaken them.
