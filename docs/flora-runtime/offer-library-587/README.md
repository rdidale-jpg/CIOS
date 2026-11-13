# FLORA Offer-to-Sales v2 — Sprint A owner review

Issue [#587](https://github.com/rdidale-jpg/CIOS/issues/587), based directly on validated main `3b8bd2c5e5177c012826658f820eeeb4ea2705f5`. **Draft review only; no merge or deployment.**

**89 distinct commercial offer types across 12 families; 29 developed playbooks.** The original 84 types / 24 methods are retained, with five owner-priority enterprise programmes added. Each developed offer has two structural patterns, two event patterns and two entry plays, including observable signals, alternatives, proof, disconfirming questions, stops and delivery/rights constraints. The other 60 types have distinct outcomes and honest catalogue-only labels, and cannot yet be adopted.

The existing Offers workspace now supports authorised company → multiple business categories → ranked/searchable examples → private versioned portfolio → existing discovery and independent employer review. Examples establish neither company capability nor customer demand. Original library bibliography is separate from private seller proof. Existing custom offers, retirement and protected variations remain available.

[Complete coverage and per-playbook assessment](Coverage.md) · [Primary-source bibliography](Sources.md) · [Architecture, controls and rollback](Architecture.md) · [Validation and reproduction](Validation.md)

[**Updated five-priority coverage, complete playbooks, matches and desktop/iPad/mobile gallery**](strategic-priorities/README.md)

The current category is **Digital Transformation & Consulting**, with separately selectable **Systems Integration** delivery specialism. Original Offer IDs and existing approved snapshots remain valid.

## Original Sprint A before / after gallery

Before images use an isolated checkout of the exact validated main release. After images use example-only employers, sellers, proof and independent reviewers. No actual company proposition, customer lead or production data is depicted.

| View | Desktop 1440 | iPad landscape | iPad portrait | Phone 390 | Phone 320 |
|---|---|---|---|---|---|
| Private portfolio | [Before](previews/desktop-portfolio-before.jpg) · [After](previews/desktop-portfolio-after.jpg) | [Before](previews/ipad-landscape-portfolio-before.jpg) · [After](previews/ipad-landscape-portfolio-after.jpg) | [Before](previews/ipad-portrait-portfolio-before.jpg) · [After](previews/ipad-portrait-portfolio-after.jpg) | [Before](previews/mobile-portfolio-before.jpg) · [After](previews/mobile-portfolio-after.jpg) | [Before](previews/mobile-320-portfolio-before.jpg) · [After](previews/mobile-320-portfolio-after.jpg) |
| Account-led discovery | [Before](previews/desktop-discovery-before.jpg) · [After](previews/desktop-discovery-after.jpg) | [Before](previews/ipad-landscape-discovery-before.jpg) · [After](previews/ipad-landscape-discovery-after.jpg) | [Before](previews/ipad-portrait-discovery-before.jpg) · [After](previews/ipad-portrait-discovery-after.jpg) | [Before](previews/mobile-discovery-before.jpg) · [After](previews/mobile-discovery-after.jpg) | [Before](previews/mobile-320-discovery-before.jpg) · [After](previews/mobile-320-discovery-after.jpg) |
| Multiple categories | [View](previews/desktop-categories-after.jpg) | [View](previews/ipad-landscape-categories-after.jpg) | [View](previews/ipad-portrait-categories-after.jpg) | [View](previews/mobile-categories-after.jpg) | [View](previews/mobile-320-categories-after.jpg) |
| Suggested examples | [View](previews/desktop-selection-after.jpg) | [View](previews/ipad-landscape-selection-after.jpg) | [View](previews/ipad-portrait-selection-after.jpg) | [View](previews/mobile-selection-after.jpg) | [View](previews/mobile-320-selection-after.jpg) |
| Private offer / retained playbook | [View](previews/desktop-playbook-after.jpg) | [View](previews/ipad-landscape-playbook-after.jpg) | [View](previews/ipad-portrait-playbook-after.jpg) | [View](previews/mobile-playbook-after.jpg) | [View](previews/mobile-320-playbook-after.jpg) |

## Three illustrative pilots

| Seller type | Three examples | Preview |
|---|---|---|
| Systems integrator | Technology operating model; legacy modernisation; cloud landing zone | [Desktop](previews/desktop-si-portfolio.jpg) · [iPad](previews/ipad-portrait-si-portfolio.jpg) · [Phone](previews/mobile-si-portfolio.jpg) |
| Software / SaaS supplier | Service workflow subscription; customer-service adoption; data quality product | [Desktop](previews/desktop-saas-portfolio.jpg) · [iPad](previews/ipad-portrait-saas-portfolio.jpg) · [Phone](previews/mobile-saas-portfolio.jpg) |
| Managed security provider | Managed detection/response; privileged identity; managed service operations | [Desktop](previews/desktop-mssp-portfolio.jpg) · [iPad](previews/ipad-portrait-mssp-portfolio.jpg) · [Phone](previews/mobile-mssp-portfolio.jpg) |

Each fixture explicitly selects three different templates from multiple categories, then edits one with example delivery/rights proof and obtains a **separate reviewer's** approval. The other two remain private. Tests exercise the full transition, rejection, retirement, source history and stale-parent behaviour. These approvals exist only inside disposable test workspaces.

## Acceptance walkthrough

1. Sign into a local candidate workspace using existing authority. Open `/flora/offers`, then **Set up my offers**. Choose a previously authorised company. No employer grant is created by selecting a name or category. Without a binding, the owner must authorise it in existing My company first.
2. Select a primary business category and optionally others. Categories describe the supplier's business, separately from target-customer industries. No category is silently selected for a first-time seller. Existing mission exclusions and private fields survive.
3. Search or browse the relevant developed examples. Each library ID appears once despite category overlap. Open **See the sales playbook** only when useful. Structural conditions and possible future events are questions to test, not detected buyer events. The full 84-type catalogue is an optional disclosure.
4. Select offers and explicitly confirm they require validation against company capabilities and rights. Save to private drafts. Repeating the same selection returns the existing drafts without adding duplicates or auto-approving them. Open an offer to customise it, add permitted seller proof, retire it or request independent employer review.
5. Review the portfolio's outcomes, buyer roles, trigger and first move, then **Continue to discovery**. Compare offer-led and account-led discovery; both use the same assessment service. For Lloyds, compare legacy modernisation with the bounded AI experiment: distinct reported context, distinct play and validation test; no urgency, budget, procurement invitation or customer demand is inferred.
6. With a separately authorised reviewer, approve one submitted example after checking delivery evidence, rights and scope. Self-approval, missing proof, stale templates, stale parents and foreign employer access must fail. Updating library content must retain historic snapshots and require explicit re-adoption/review.
7. Inspect original account lineage and library bibliography through the one optional header **Sources & method**. Matching stays an interpretation. Creative Studio stays off; Pipeline requires its original separate deliberate action. No data is copied into Pipeline by discovering or following a qualification link.
8. Compare all five widths and both iPad orientations, native keyboard focus, required confirmation, zoom and the optional disclosures. Physical-device and human timing acceptance remain owner checks.

## Design assessment and product metrics

The approved FLORA header, restrained green/cream typography and optional source location are reused. Offers have a practical outcome-led layout; full methods stay in native disclosures. No new general redesign, repeated evidence CTAs, admin panels, autonomous research or runtime enrichment was added.

Automatic browser checks cover real local HTTPS sign-in, one header, a single source location, keyboard focus, no overflow, unchecked capability selections, three separate pilot portfolios, independent approval, selected-employer privacy, idempotent CSRF-protected selection and both discovery routes. [Machine-readable browser evidence](previews/browser-checks.json) includes dimensions and timings. GET walkthroughs preserve existing offer/mission bytes; repeat adoption is deliberately idempotent. Pipeline remains absent.

The one-minute target is a **human usability target**, not a certified result. Automated repeat-selection timing starts from existing category preferences and is not an onboarding benchmark. Owner testing should time company selection through a three-offer portfolio and record confusing vocabulary, selection changes, proof completion and discovery relevance. Do not count catalogue-only names as usable offers or hypothesised matches as leads.

Candidate routes are review routes, **not live changes at flora-current.onrender.com**. This PR does not merge, deploy, alter Render settings or modify production data.
