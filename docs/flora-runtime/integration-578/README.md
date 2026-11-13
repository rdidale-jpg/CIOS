# FLORA integrated Technology UX + Offers — Issue #578

**Integration is prepared for review. Production release remains NO-GO until the manual gates in the [owner deployment guide](Render-Owner-Deployment.md) are verified and the owner explicitly approves the exact release. No main merge or Render deployment was performed.**

## Included reviewed heads

- #574 Technology UX: `867e11809dd13058648b891387038948ccd978a1`.
- #575 Offers architecture proposal: `667ce1b3d1f77d4c7d66b20e21c595e7b4882cbb`.
- #577 Offers v1: `ad0b3d4c781178e6fb02271f3f8373fd3b23c339`.
- Main/base at assembly: `854a783b3c5f83d6ee3604f49a76772529b7339a`.

All three heads are ancestors of the integration candidate. Their reviewed contents were combined locally without changing the original PR branches. Only the CI workflow conflicted: the resolution retains both feature tests and documentation triggers, strict security and the inherited-failure comparator. The architecture document remains a proposal; the bounded Offers implementation does not claim complete canonical APPA or accepted capability truth.

The narrow visual follow-up adds a thin native link to UK Technology above district/all-participant comparison, using a crop of the original approved artwork. No new illustration, metric, research promotion, evidence path or interaction model is introduced. Sort/search/table and enterprise profiles remain. Height is 88px desktop, 72px iPad and 64px mobile; the banner is keyboard-accessible without JavaScript and its decorative image does not duplicate accessible text.

| Comparison | Desktop | iPad | Mobile |
|---|---|---|---|
| Cloud district | [Preview](previews/desktop-cloud-banner.png) | [Preview](previews/ipad-cloud-banner.png) | [Preview](previews/mobile-cloud-banner.png) |
| All participants | [Preview](previews/desktop-all-banner.png) | [Preview](previews/ipad-all-banner.png) | [Preview](previews/mobile-all-banner.png) |

Integrated Offers previews use isolated synthetic identities and real local HTTPS/sign-in; they are not a hosted deployment or real employer approval:

| Offers | Desktop | iPad | Mobile |
|---|---|---|---|
| Catalogue | [Preview](offers-previews/desktop-catalogue.png) | [Preview](offers-previews/ipad-catalogue.png) | [Preview](offers-previews/mobile-catalogue.png) |
| Owner setup | [Preview](offers-previews/desktop-owner-setup.png) | [Preview](offers-previews/ipad-owner-setup.png) | [Preview](offers-previews/mobile-owner-setup.png) |
| Matching | [Preview](offers-previews/desktop-account-led.png) | [Preview](offers-previews/ipad-account-led.png) | [Preview](offers-previews/mobile-account-led.png) |
| Studio off | [Preview](offers-previews/desktop-studio-off.png) | [Preview](offers-previews/ipad-studio-off.png) | [Preview](offers-previews/mobile-studio-off.png) |

Original full [Technology walkthrough](../ux-refinement-573/README.md) and [Offers walkthrough](../offers-v1-576/Acceptance-Walkthrough.md) remain historical acceptance records for their own source SHAs; do not treat their source manifests as the integration commit. Current integrated source fingerprints are in `Source-Manifest.json`; current exact SHA and hosted result belong to the draft PR/Checks.

## Acceptance and validation

1. Inspect the thin banner at all three sizes; activate it by keyboard and sort/search natively with JavaScript off. Confirm original landscape and table remain intact.
2. Use the full Technology journey and NVIDIA profile; inspect actual source/estimate limits. All 80 participant views, 34 programme relationships, six unqualified themes and three lenses retain existing acceptance status.
3. Use the Offers owner/seller/distinct reviewer walkthrough. Check private scope, version lineage, protected/stale parents/components, default-off Studio, symmetrical assessment IDs, source-cutoff seals and unchanged Pipeline. No real identities or production data were used in automated previews.
4. Review [Validation](Validation.md), canonical owner fingerprints, complete current-head local/hosted security/regression results and release-helper refusal tests. No merged candidate may rely on an older head's green check.
5. Complete the production release ticket and explicit human approval separately; follow exact-SHA deployment and data-preserving rollback instructions. The preflight helper cannot deploy and cannot replace Render/IAM/backup checks.

Intended URL after verified deployment: **https://flora-current.onrender.com/flora/offers**. The owner confirmed the origin; live Offers availability, service identity and deployed SHA were not observed because no Render connection is available and network policy blocked the earlier live probe. No further bypass/retry was attempted.
