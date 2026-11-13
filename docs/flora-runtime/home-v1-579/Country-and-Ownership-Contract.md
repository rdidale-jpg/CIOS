# Country and ownership contract / readiness audit

## Three separate geographical concepts

| Concept | Source/owner | Home treatment | Must not imply |
|---|---|---|---|
| Active market | Explicit allowlisted `market=GB` or `market=FR` in the preview URL; default UK is presentation configuration | Controls artwork, eligible regions, briefing and local plays. Preserved in Home/global links and country form. | Physical location, residency, legal entity, employer, permission or accepted research coverage |
| Seller geography | Existing authorised `CommercialMission.geography` | Displayed as declared **Seller territory**; may contain multiple countries. Existing selected employer is resolved through Offers' authorised binding. | Verified employer footprint, automatic active-market selection or country access grant |
| Macro context | Existing `macro_intelligence` context, source segments, jurisdictions and country-specific references | Global PESTLE definitions → cross-market theme or local policy → country evidence/exposure → existing industry/enterprise context. | A measured country impact from a global theme, legal applicability to an enterprise, procurement or demand |

Existing CommercialMission does not own an explicit active-market preference field. Home deliberately does not infer that preference from a possibly multi-country territory, and does not write a parallel profile/cookie/localStorage store. IP/GPS, proxy-country headers and browser geolocation are not used. A later persistent active-market field needs an explicit existing-owner contract and migration/review, not a guess from user location.

## Presentation integration contract

`HomeMarketPresentation` is a finite source-code view configuration: `country_code`, `name`, `coverage`, `lang`, `art asset key`, native `width/height`, descriptive conceptual `alt`, and zero or more regions with canonical `href` and image-relative `x/y` percentages. It is **not** a new country/industry/enterprise intelligence model. Files are served only through the exact `/home/assets/styles`, `/home/assets/uk-artwork` and `/home/assets/fr-artwork` routes; no caller-selected filesystem path or private-record lookup.

The UK registry links only the existing Technology, Banking and Aviation routes. France has distinct art and an empty regions tuple. Artwork can be replaced and coordinates reviewed without rewriting research/matching logic. At desktop/iPad, anchors are positioned against the same natural image coordinate system; mobile places those same native links below the image. The image is decorative/conceptual context, not Evidence or a claim that industries occupy those locations.

## Ownership and permissions

- Canonical `/`, `/flora`, `/flora/` and the existing `_flora_home_page` implementation remain unchanged. The new routes are explicitly finite public preview/PESTLE routes with bounded selectors. Duplicate/unknown market/lens/private selectors fail closed.
- Public composition never enumerates private Offers or mission files. Signed-in private composition holds the existing verified service-read/revocation envelope across the full render. Existing session, membership, workspace, capability and account access are authoritative; query strings/headers provide no identity.
- Employer comes from the existing authorised Offers selection, not a free-text company name. Private focus comes from the authenticated user's existing mission. Only current accessible **employer-approved** Offers with proof references and qualifying existing source-linked assessments can enter recommended plays. Private draft counts are not approval badges or recommendations.
- One existing `offers.discover` / `assess_fit` service powers the recommendation. Home changes retrieval/grouping only, retaining stable assessment IDs, source cutoff, policy, limitations and next test. The minimal Offers-view change adds `id=assessment_id` to an existing row so a native link reaches it. No persistence owner, approval, matching rule or private selector changed.
- Research publication dates are taken from existing source metadata only. Existing SourceSegment validation, candidate authority, source-rights/identity limitations, counter-evidence and dates remain inspectable. No intake, promotion, autonomous agent, paid runtime call, outreach, opportunity store or Pipeline writer is added.
- Country selection changes no employer binding, mission, permissions, offers, opportunities or Pipeline records. Existing session refresh on GET remains the authentication owner's behaviour; it is not a market preference or permission change.

## Cross-country readiness audit

| Area | UK preview | France layout / gap |
|---|---|---|
| Routes / regions | Three existing industry routes; source-backed enterprise/insight routes | No invented French industry/enterprise region or local briefing. Links to UK libraries are labelled UK. Header remains global canonical navigation. |
| Country data | Existing UK-associated/group disclosures and covered UK policies, with source scope | No national metrics or claimed local opportunity. Limited existing French macro sources may be inspected through the existing owner. |
| Identity / permission | Existing account IDs and authorisation, no new synthetic canonical IDs | No French entity identity or seller rights inferred from country selection. Country options are not role grants. |
| Global vs local | Cross-market resilience is distinguished from UK evidence; local UK policy stays local | EU enactment, French transposition and enterprise applicability stay distinct; no global prevalence or national economic estimate inferred. |
| Currency / estimates | No new financial metric or currency conversion. Available-offer counts are scoped operational counts. | No invented EUR figures, FX conversion or revenue/local headcount. Future defensible estimates need EST, basis, source/date and range. |
| Date / timezone | Publisher ISO date retained; English day-month-year display; no freshness from retrieval | Country is not timezone/locale. English presentation retained; French copy, date preferences and timezone strategy need review. |
| Locale / art | Generated conceptual British panorama; readable native labels | Separate Paris-inspired conceptual art demonstrates layout only, not researched national coverage. |
| Source rights / coverage | Existing validation and limitations retained; no accepted-research promotion | No blanket claim that all PESTLE lenses or countries have sourced coverage; empty lenses remain empty. |
| User context | Seller-level employer, territory, horizon and private priority declarations remain | Same seller context persists without implying those targets operate in France. Local recommendations withheld. |
| Persistence / security | Existing read guards and no-store responses; real sign-out/CSRF path | No new active-market store, country cookie, GPS/IP inference, cross-tenant cache or permission shortcut. |

## Sequencing

Base dependency: integration #580/#578 at `34e34570c52847e16eb5f0d00579ca923983af7c`. This Home branch is separate and must be reconciled with the **final** integration/main SHA after owner acceptance; do not silently change or retarget the release branch. All existing security, country source/license and live production readiness gates still apply. No merge/deployment until #578 completes and the owner approves Home's visual direction and later implementation scope.
