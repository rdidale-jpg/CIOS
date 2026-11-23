# Validation, exact scope and rollback

Baseline: `97d316c640c96d99c2301819f8aac00b3b9c1398`. Design: `da1a6c7b5e4b95e85ef2de3697bc8c506368192c`. The draft PR identifies the final implementation SHA and hosted checks; this document does not imply merge or deployment.

## Reproduce

```sh
python -m pytest tests/test_flora_living_enterprise_preview.py tests/test_flora_accepted_ux_recovery.py tests/test_flora_eei2b.py tests/test_flora_eei3.py -q
python tools/ci/flora_ci.py --output /tmp/flora-living-preview-ci
python docs/flora-runtime/living-enterprise-preview/validate.py --check
```

For real before/after browser comparisons, run the **same** `browser.py OUTPUT before` from a detached baseline checkout, then `browser.py OUTPUT after` from the candidate. The existing `flora-enterprise-economics-a1.yml` workflow performs both, includes the new unit/security-boundary tests, retains all existing tests and publishes sanitized JSON/JPEG proof. Install only the existing project dependencies/Playwright Chromium; no paid service or new runtime dependency is involved.

## Required checks

- All three preview layers and 12 region states, exactly four image regions per layer, original rich artwork and selected highlight.
- Ordinary Home/Industries/Banking/Lloyds arrival, optional entry, obvious experimental label and return, current Lloyds unchanged except the entry link, eight SWOT themes and easyJet preserved.
- Exact finite route/asset catalogue, malformed/duplicate/private/foreign selectors denied, no export/snapshot/Financial-run route, valid HEAD state and `no-store`, writes rejected through existing authority.
- Correct Group entity, date, stock/flow, unit and semantic kind. Existing restricted Lloyds three-measure projection stays inactive; no PDF links exposed.
- Source withdrawn/revoked/owner-only/contradictory/stale/superseded removes dependent financials, Curve marker/accessibility label, affected SWOT and diagrams. Independent intelligence remains.
- Guest/forged/authorised/expired/revoked-membership Main content equivalence; private Financial services are forbidden in those tests, not mocked to grant access. Existing security storage is isolated and synthetic only.
- Browser keyboard/Enter, touch, direct reload, subject context, Back/Forward, compact/open portraits, source withdrawal through history/reload/print, no-JavaScript native fallback, no horizontal overflow or page errors.
- Existing full strict security/regression comparator, inherited failures/skips and signature integrity unchanged. Exact-current frame cut includes only `_frame`; every historical compatibility cut and the security baseline remain pinned. New mutation-negative tests protect this extension.
- All 51 original application image hashes unchanged. Source/research/rights/authentication/Financial/canonical/Pipeline/schema records untouched. Existing web authentication/mutation/response methods unchanged; only GET/HEAD dispatch and content typing gain the finite public preview.

Actual results, device/capture hashes and unchanged-default renderer hashes are in [Browser-after.json](previews/Browser-after.json), compared with [Browser-before.json](previews/Browser-before.json). [Integrity-Proof.json](Integrity-Proof.json) records exact file inventory, protected code checks, documentation links and full binary reverse-patch restoration of baseline tree `6c72c645777372e196cbc3c4248f5ec7321cd84e`. These checks do not perform a live deployment or rollback.

## Limits

Browser captures are real local application renders on desktop 1440 × 1000, iPad landscape 1194 × 834, iPad portrait 834 × 1194 and mobile 390 × 844. They do not certify physical iPad/Safari or assistive technology. Render metadata confirms the current deployed code; live page browsing is blocked by the execution environment's network policy. No live smoke result is claimed. No independent review was commissioned by this task; [Implementation.md](Implementation.md) includes the self-critique and known trade-offs.

## Completion boundary

Return the draft implementation for technical and visual acceptance. Recheck the exact head and resulting release CI before any later authorised integration/deployment. See [Deployment.md](Deployment.md) for existing-service-only steps and code/data rollback limits. No new environment, registry, authentication or source-admission setup is required for the preview.
