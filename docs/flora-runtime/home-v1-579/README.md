# FLORA Home v1 — Hybrid Home design review

**Separate design sprint for Issue #579. Draft only; no merge or deployment.** This branch depends on the validated integration candidate `34e34570c52847e16eb5f0d00579ca923983af7c` from #580/#578. The draft PR targets that integration branch so its diff contains Home work only. The integration/release branch was not changed.

The owner's [issue direction](https://github.com/rdidale-jpg/CIOS/issues/579#issuecomment-6849338295) requires visual acceptance before a full Home implementation. Accordingly, this is a **functional, read-only design preview at `/home`**, with Global PESTLE at `/home/global-forces`. The current canonical `/`, `/flora` and `/flora/` remain unchanged. No live preview was deployed and no working production URL is claimed.

## Start with desktop and iPad

| View | Desktop 1440×1000 | iPad landscape 1194×834 | iPad portrait 834×1194 | Mobile 390×844 |
|---|---|---|---|---|
| Before: current Home | [Before](previews/desktop-before-home.png) | [Before](previews/ipad-landscape-before-home.png) | [Before](previews/ipad-portrait-before-home.png) | [Before](previews/mobile-before-home.png) |
| UK: public discovery | [Preview](previews/desktop-uk-public.png) | [Preview](previews/ipad-landscape-uk-public.png) | [Preview](previews/ipad-portrait-uk-public.png) | [Preview](previews/mobile-uk-public.png) |
| UK: seller perspective | [Preview](previews/desktop-uk-seller.png) | [Preview](previews/ipad-landscape-uk-seller.png) | [Preview](previews/ipad-portrait-uk-seller.png) | [Preview](previews/mobile-uk-seller.png) |
| France: alternate layout | [Preview](previews/desktop-fr-public.png) | [Preview](previews/ipad-landscape-fr-public.png) | [Preview](previews/ipad-portrait-fr-public.png) | [Preview](previews/mobile-fr-public.png) |
| France: same seller | [Preview](previews/desktop-fr-seller.png) | [Preview](previews/ipad-landscape-fr-seller.png) | [Preview](previews/ipad-portrait-fr-seller.png) | [Preview](previews/mobile-fr-seller.png) |
| Global PESTLE overview | [Preview](previews/desktop-global-forces.png) | [Preview](previews/ipad-landscape-global-forces.png) | [Preview](previews/ipad-portrait-global-forces.png) | [Preview](previews/mobile-global-forces.png) |
| France: legal context | [Preview](previews/desktop-fr-legal.png) | [Preview](previews/ipad-landscape-fr-legal.png) | [Preview](previews/ipad-portrait-fr-legal.png) | [Preview](previews/mobile-fr-legal.png) |

[Print example](previews/home-seller-print.pdf) · [Browser checks](previews/Browser-Checks.json) · [Design assessment](Design-Assessment.md) · [Country/ownership audit](Country-and-Ownership-Contract.md) · [Validation](Validation.md)

The commercial identities, employer binding, approvals and priority-account selections in signed-in pictures are **disposable synthetic fixtures**. They demonstrate real session/permission paths, not actual seller relationships, corporate proof, customer demand or approved live propositions. Enterprise/news statements come from the existing repository's source contracts, with their original status and scope.

## Annotated composition

Read these annotations alongside the screenshots rather than adding explanation boxes to the product:

1. **Country + global window.** A small explicit market selector sits above the scene; Global forces is one native link away. No national flag wall, IP/GPS inference or automatic employer change.
2. **One editorial heading.** A short headline leaves space for the illustrated world and brings the commercial focus closer to the first viewport. Body text uses a restrained serif/sans hierarchy rather than KPI widgets.
3. **The living commercial world.** One seamless, feathered panorama. Three visible native labels address existing Technology, Banking and Aviation routes. The image is conceptual scenery, not a literal map or enterprise relationship graph. Desktop/iPad labels use image-relative positions; mobile exposes the same links as a readable strip under the artwork.
4. **My Commercial Focus.** A quiet horizontal briefing from the selected authorised employer and existing private mission. Empty fields disappear. Territory is explicitly seller context, separate from the active market. Public visitors receive a sign-in/discovery invitation; users without commercial permission receive a workspace availability message.
5. **What's Changing.** Four concise developments from existing dated sources; each explains why it matters and has one insight action. Dates are original publisher dates, never retrieval/update times. Source detail stays optional and secondary.
6. **Recommended Sales Plays.** At most three existing authorised, evidence-linked assessments of approved offers with proof references. Presentation grouping favours different accounts before repeating one. No new matching engine, scores, opportunity store, inferred intent, budget, sponsorship or Pipeline writes. A native fragment links to the existing assessment row; the only Offers view change adds that HTML anchor.
7. **Explore.** A small text navigation strip rather than another card wall. Existing header destinations and destination permissions remain. The canonical header Home/brand still point to the current Home; the preview's own Back to your world link preserves the country.

## Owner acceptance walkthrough

1. Compare the old Home with UK public desktop, then the two iPad views. Assess whether the panorama feels embedded and recognisable, labels are legible, and the composition feels distinct from a dashboard.
2. Activate each labelled region with keyboard/Enter and touch. It should reach the existing industry page in one step. At mobile/320px, read the three native labels under the image; no hover-only controls or hidden hit zones.
3. Open Global forces once. All six PESTLE lenses are visible. Inspect Technological: the cross-market theme is separated from country evidence and qualitative exposure. Inspect Economic: no unsupported statistic or invented signal appears. Follow the existing industry/enterprise context if desired.
4. Select France. Its artwork and layout change, while local industry regions, the UK briefing and account plays do not appear as French coverage. Global context remains available; existing French legal/source limitations remain inspectable. Switch country within a lens and confirm the explicit lens is preserved.
5. With an authorised synthetic seller, compare UK and France focus: company, seller territory, priority-account declarations and horizon remain unchanged. France selection grants no access or authority. Another seller's private context must not appear.
6. In UK seller mode, inspect up to three plays and follow one to its exact existing assessment. Compare the assessment ID/cutoff/next test with the Offers owner. Unapproved private drafts may contribute to an available-offers count but are not recommended Home plays. When no eligible pair exists, show a useful invitation, not invented examples.
7. Check the public page's HTML for absence of private employer/mission/offer data. Sign out through the existing CSRF-protected path and confirm the preview becomes public. Revoked or missing commercial permissions must not reveal private focus.
8. Inspect optional sources/limitations after reading the briefing. No acceptance status or research task is upgraded by Home. Check country changes and normal browsing leave domain/profile/Pipeline state untouched; normal session touches remain the existing authentication owner's responsibility.
9. Inspect print, reduced motion and mobile. Physical iPad/Safari and screen-reader acceptance remain manual; automated Chromium emulation is not a claim of those checks.

## Decision sought

Owner approval of this **visual direction and country/seller/macro separation**, with particular attention to desktop/iPad balance, labels, typography, briefing density and the empty alternate-country state. Canonical Home replacement, persistence of market preferences, wider national coverage and production release are **not** included. Any later promotion must follow completion/approval of integration #578, reconcile the final base, rerun current-head CI and receive explicit owner approval. No Render/release helper or production configuration is changed here.
