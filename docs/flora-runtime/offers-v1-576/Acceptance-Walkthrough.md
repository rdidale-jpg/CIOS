# Offers v1 — owner acceptance walkthrough

**Draft pilot, no merge or deployment.** Entry after a separately authorised deployment: `/opportunities` → **Open My offers**, or `/flora/offers`. This PR does not create a hosted preview or change Flora's deployment.

## Before and after / responsive previews

All pictured employers, sellers, approvals and capability proof are **isolated synthetic fixtures**. Enterprise research retains its original source status. No live leads, customer relationships or company-approved propositions are demonstrated.

| Screen | Desktop 1440×1000 | iPad 1024×1366 | Mobile 390×844 |
|---|---|---|---|
| Existing Technology starting point | [Before](previews/desktop-before-technology.png) | [Before](previews/ipad-before-technology.png) | [Before](previews/mobile-before-technology.png) |
| Opportunities entry | [Before](previews/desktop-before-opportunities.png) / [After](previews/desktop-after-opportunities.png) | [Before](previews/ipad-before-opportunities.png) / [After](previews/ipad-after-opportunities.png) | [Before](previews/mobile-before-opportunities.png) / [After](previews/mobile-after-opportunities.png) |
| My offers | [Preview](previews/desktop-catalogue.png) | [Preview](previews/ipad-catalogue.png) | [Preview](previews/mobile-catalogue.png) |
| Employer selection | [Preview](previews/desktop-company.png) | [Preview](previews/ipad-company.png) | [Preview](previews/mobile-company.png) |
| Owner company setup | [Preview](previews/desktop-owner-setup.png) | [Preview](previews/ipad-owner-setup.png) | [Preview](previews/mobile-owner-setup.png) |
| Private variation | [Preview](previews/desktop-variation.png) | [Preview](previews/ipad-variation.png) | [Preview](previews/mobile-variation.png) |
| Offer-led discovery | [Preview](previews/desktop-offer-led.png) | [Preview](previews/ipad-offer-led.png) | [Preview](previews/mobile-offer-led.png) |
| Account-led discovery | [Preview](previews/desktop-account-led.png) | [Preview](previews/ipad-account-led.png) | [Preview](previews/mobile-account-led.png) |
| Separate employer review | [Preview](previews/desktop-review.png) | [Preview](previews/ipad-review.png) | [Preview](previews/mobile-review.png) |
| Studio disabled | [Preview](previews/desktop-studio-off.png) | [Preview](previews/ipad-studio-off.png) | [Preview](previews/mobile-studio-off.png) |
| Private combination | [Preview](previews/desktop-composite.png) | [Preview](previews/ipad-composite.png) | [Preview](previews/mobile-composite.png) |

## Acceptance steps

1. Sign in with an existing enrolled user and select an authorised workspace. Anonymous requests to every Offers route must fail. Read-only membership cannot perform writes.
2. In **My offers → My company**, a CIOS owner saves the declared employer through the existing **Employer Context** service (no imported Twin required), then separately supplies the explicit employer-binding review reference, named active seller IDs and delegated reviewer IDs. Changing the declared employer clears employer-specific profile fields rather than transferring capabilities or partnerships; already authorised catalogues remain separate. This grants no IAM membership and creates no canonical participant identity. Select one authorised company. An unrelated seller with the same declared employer name must still be denied.
3. Use each illustrative template: service resilience, transformation consulting and AI innovation. Confirm outcome, ICP, buyer roles, trigger pattern, exclusions, first play and validation question. Supply actual delivery/rights proof before real company use. Save privately; change a play and verify a new immutable version. Another seller and even a workspace owner cannot inspect the private content.
4. Submit for employer review. A delegated **different** reviewer inspects capabilities, proof, rights and scope, records a reference, then requests changes, rejects or approves. Only approval makes that version available to bound employer sellers. Approval is publication permission, not evidence acceptance. Seller authors cannot change or withdraw approved employer masters. A delegated approver may draft a master revision, which needs independent approval again.
5. Create a private variation of a current approved offer. Sector emphasis, buyer roles, first play, question and name can change; parent capabilities, constraints, partner dependencies, evidence and trigger definition are protected. Parent ID/version survives. Retire or revise the parent through delegated authority and confirm the old variation becomes ineligible for discovery.
6. Explore the same pair through **Offer-led** and **Account-led**. Open assessment detail and compare the stable `fit-…` ID, source cutoff, reasoning, sources, counter-indicators and next test. They must be identical. The pilot includes Lloyds, easyJet and Equinix public presentation context. Existing account permissions still filter bound account assessments. Service and AI patterns give different recommendations where supporting change differs.
7. Move the cutoff before the reviewed snapshot: no later account indicator or counter-evidence may appear. Inspect the evidence limits: no accepted Observation IDs are invented, existing candidate/source status remains, and Equinix is explicitly unbound presentation research. Economics stay blank: no unsupported estimates, budgets, win probabilities or modelled financial values.
8. Confirm Studio starts **off** for each user/workspace. Enable explicitly; choose an authorised account and two current approved offer versions with evidence references. Save a private combination. Inspect the target reference, component versions, value thesis, buyer, trigger, play, partner/rights constraints, simpler alternatives and validation question. Edit or retire the draft privately. Organisational publication still requires a different delegated reviewer. Retired or changed components block reuse. Disable Studio and confirm composition is denied. There are no paid model calls or autonomous actions in either mode.
9. Follow **Open manual Pipeline qualification** for supported Banking/Aviation accounts only. The link writes nothing and transfers no match content. The existing manual demonstration capture, evidence review and qualification requirements remain authoritative. Equinix has no capture link. Inspect Pipeline before/after browsing, editing, reviewing and Studio: it must be unchanged.
10. Use Tab/Shift+Tab and native Enter/Space controls; expand source details and follow evidence links. Repeat on desktop, iPad and mobile. Verify the five primary destinations and existing Banking/Aviation/Technology journeys remain intact.

## Reproduce safely

Use an isolated local environment; never point the preview at deployed data. Install the repository's existing requirements plus local Playwright/Chromium as appropriate. From the repo:

```sh
python -m pytest tests/test_flora_offers_v1.py -q
python -m pytest tests/test_flora_technology_owner_journey.py tests/test_flora_sales_pipeline.py -q
python -m unittest discover -s tests/ci -v
python tools/ci/flora_ci.py --output /tmp/flora-offers-final-ci
PYTHONPATH=. python tools/ci/flora_offers_preview.py --output /tmp/flora-offers-previews --baseline-root /path/to/clean-main-checkout
```

The preview command provisions and destroys a temporary synthetic authority, uses local HTTPS with a throwaway certificate and real browser sign-in, and fails if any Pipeline file appears. It never changes production authentication or relaxes origin/CSRF checks. The existing offline bootstrap admits owners only; synthetic seller/reviewer fixture roles are narrowed **before enrollment**, inside that disposable database. Only screenshots and sanitized checks are retained. Do not publish its temporary database, enrollment deliveries, credentials or logs.

## Limits and acceptance gate

This is not a complete canonical APPA, canonical capability catalogue import, customer validation system or CRM integration. Participant/offer canonical bindings are deliberately absent. The three templates are illustrative; approval proof supplied by a user remains human-supplied until existing evidence owners accept it. Recommendations stay at research/validate/partner/deprioritise because the pilot inputs establish no sponsorship or purchase process; create-demand/shaping/pursuit require further customer validation. No outreach, autonomous learning or paid-model integration is included. Technology account research is especially limited; refresh and accept it through existing governance before making stronger claims.

The read-only enterprise source snapshot is conservatively available from **13 November 2026** for matching cutoffs; earlier cutoffs withhold it as a whole. This is a knowledge-availability boundary, not a claimed publication date. Adapter-input digests fail closed if upstream source context changes; reconcile the snapshot and cutoff before reuse. No latest-source re-verification occurred in this sprint. Source rights and private employer storage/retention remain owner responsibilities. Binding changes invalidate the context revision; Studio opt-in is persisted per user/workspace, not per browser tab. Root storage remains FLORA's existing single-writer protected filesystem; no new distributed deployment model is introduced.

Review architecture and all three viewport previews, then require a successful **current-head hosted FLORA validation** run before considering merge. Review this pilot separately from #574 and proposal #575. No merge or deploy is authorised by this walkthrough.

Rollback after any separately authorised integration: revoke the affected employer binding, disable Studio, revert the feature commit, and retain/delete the additive private operational directory only under the owner's retention policy. Existing profiles, authority audit, canonical evidence and Pipeline must not be overwritten or restored from older snapshots.
