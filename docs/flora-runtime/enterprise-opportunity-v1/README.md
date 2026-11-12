# Enterprise-to-Opportunity Integration v1 — validation and owner walkthrough

[Draft PR #561](https://github.com/rdidale-jpg/CIOS/pull/561) builds on unmerged [#557](https://github.com/rdidale-jpg/CIOS/pull/557), pinned at `6988ba50d29c1f238293fc7fe110d6182f055e68`. Implementation scope: [#560](https://github.com/rdidale-jpg/CIOS/issues/560); visual-first contract: [#558](https://github.com/rdidale-jpg/CIOS/issues/558). Neither dependency nor main is modified. The separate design-only #559 is not imported.

## Working journey

1. Open `/enterprises/lloyds`. The illustrated Enterprise Twin remains; the capability overlay follows it. Repeated findings and priority cards now sit inside the enterprise research disclosure.
2. Select **Opportunity landscape**. Eight canonical capability anchors surround FLORA’s reused banking illustration. Gold indicators count associated hypotheses, not sales probability; counts overlap.
3. Select a capability, then a hypothesis in the single inspector. All nine original hypotheses remain available, with separate authored scores, source-period drill-down and next commercial action. The comparison disclosure retains the shared opportunity diagram and a nine-row accessible table.
4. Follow **Develop hypothesis & inspect dossier**. AI (`002`), legacy (`001`) and wallet/Curve (`009`) use four selectable investigation stages, one contextual panel, a clear next validation action and eight read-only development lenses.
5. Open **Full research & evidence** for the original dossier, source scope, supporting/counterevidence, prior assessments and snapshot. Technical disclosures are nested here rather than repeated in the default view. Existing deliberate Pipeline capture stays outside the dossier.

No association proves business ownership, a reporting line, implementation dependency or supplier mandate. Programme-only and unmapped hypotheses stay discoverable without creating a capability.

## Eight development modules

| Module | Displayed boundary |
| --- | --- |
| Financial opportunity | TCV, ACV, allocated budget, benefit, price and margin remain Unknown; corporate investment is not supplier spend. |
| Business ownership | Business unit, accountable owner and economic buyer unverified; procurement is distinct from business ownership. |
| Stakeholder network | Opportunity-specific inferred decision functions; no invented named buyer, sponsor or access. |
| Hot buttons & outcomes | Opportunity-specific problem/outcome context, explicitly not validated personal motivations. |
| Competitors & alternatives | Existing scoped supplier context plus internal delivery/no-purchase alternatives; no invented competitive procurement. |
| Proposed solution | Existing service hypothesis; no approved customer requirement. |
| Capture & win strategy | No customer-confirmed process or approved win strategy. |
| Pursuit execution | Canonical next research/customer-validation action; no fabricated authorised milestones. |

These are public, read-only research lenses. They do not create a new CRM, private editing schema or permission engine. Existing authorised Pipeline inputs remain the place for customer evidence.

## Validation performed

- Python compilation, actionlint and dependency consistency (`pip check`) pass; CI policy tests: **25 passed**.
- Integration tests: **17 passed**, including all three public routes, unique inspector controls, separate ratings, missing-context behaviour, idempotent existing capture, immutable records and rejected premature qualification.
- Integration plus multi-industry compatibility: **25 passed**. Wider focused intelligence/commercial run: **64 passed**.
- Initial strict comparison exposed one new shared-template regression; the original slice had removed the Lloyds shared opportunities diagram. It is restored inside the comparison disclosure; the unchanged compatibility suite passes. The initial unmapped-with-programme focused failure is also corrected.
- **388 security tests passed** in the complete local run. Existing **57 inherited failures** (21 domain, 12 financial diagnostics, 24 historical legacy) and **10 original skips** retain exact identities/signatures/reasons. Only 17 passing integration identities are added to the gate; no old test or baseline entry is removed or weakened.
- Final committed-candidate full strict rerun and hosted status are reported in [PR checks](https://github.com/rdidale-jpg/CIOS/pull/561/checks) and the delivery response. This document does not predict a hosted pass.
- Actual Chromium: five routes × three viewport sizes × before/after = **30 page checks**, no horizontal overflow or JavaScript errors. All eight modules and four investigation stages exercised for each priority opportunity; keyboard Enter, touch-emulated selection, reduced motion and no-JavaScript access checked.
- Separate signed-in synthetic localhost journey: research inspection creates nothing; deliberate capture creates **Discovered**; unsupported **Qualified** is rejected. Existing 10 qualification inputs, evidence review, explicit confirmation, CSRF, workspace ACLs and immutable provenance are unchanged.
- Six real PDFs generated: AI/legacy/wallet executive briefs **one page each**, full appendices **22/22/20 pages**. Unknowns and source URLs remain present; disclosure state restores after printing. Executive and sampled full-evidence pages visually inspected. Full appendix retains specialist detail and some inefficient pagination.

No production store, account, environment or deployment setting is accessed or changed. Local fixture identities/stores are disposable and excluded; the synthetic demo seeding tool is not run.

## Previews and comparisons

Captures are real browser viewports, generally scrolled to the relevant visual rather than full-page thumbnails. Desktop **1440×1080**, tablet **1024×768**, mobile **390×844**. “Before” is original #561 head `f281e554be72c1955b7813a3975db865159a1ad5`; source hashes in [manifest](previews/source-manifest.json) identify the final rendered implementation.

| View | Before | After |
| --- | --- | --- |
| Overlay desktop | [Original](previews/before-overlay-desktop.png) | [Capability map](previews/after-overlay-desktop.png) |
| Overlay tablet | [Original](previews/before-overlay-tablet.png) | [Updated](previews/after-overlay-tablet.png) |
| Overlay mobile | [Original](previews/before-overlay-mobile.png) | [Updated](previews/after-overlay-mobile.png) |
| AI desktop | [Original](previews/before-ai-desktop.png) | [Updated story](previews/after-ai-desktop.png) |
| AI tablet | [Original](previews/before-ai-tablet.png) | [Updated](previews/after-ai-tablet.png) |
| AI mobile | [Original](previews/before-ai-mobile.png) | [Updated](previews/after-ai-mobile.png) |

Also: [Enterprise Twin](previews/after-enterprise-desktop.png), [selected hypothesis](previews/after-selected-hypothesis-desktop.png), [eight modules](previews/after-modules-desktop.png), [first viewport](previews/after-ai-first-viewport-desktop.png), [legacy](previews/after-legacy-desktop.png), [wallet](previews/after-wallet-desktop.png). Tablet/mobile versions of all five routes are in this directory.

PDFs: [AI executive](previews/ai-executive.pdf) / [full evidence](previews/ai-appendix.pdf); [legacy executive](previews/legacy-executive.pdf) / [full](previews/legacy-appendix.pdf); [wallet executive](previews/wallet-executive.pdf) / [full](previews/wallet-appendix.pdf). [PDF checks](previews/pdf-checks.json), [browser results](previews/browser-results.json), [measured comparison](previews/comparison-metrics.json).

Measured desktop default disclosures fall **4 → 2** on each priority page: one primary research disclosure plus the global specialist-tools control. The decision area itself falls **3 → 1**. Page height grows approximately **5–6%** because the interactive story adds context; no claim of reduced scrolling or measured comprehension speed is made.

Reproduce public browser/print checks against an isolated localhost FLORA instance:

```sh
python tools/preview_flora_enterprise_opportunity.py --url https://localhost:PORT --output /tmp/flora-eo-browser
# Optional matched comparison: --before-url https://localhost:BEFORE_PORT
```

Requires development Playwright/Chromium, not a production dependency. Run strict validation with `python tools/ci/flora_ci.py --output <new-empty-directory>`. The only workflow change adds the exact #557 base to eligible PR branches; permissions, commands, paths and inherited-failure handling are preserved.

## Product assessment and owner acceptance

The experience is more coherent: reusable illustration, capability-positioned indicators, contextual inspection and less default disclosure clutter. It remains a **research-association map**, not a verified Lloyds organisational model or an editable pursuit cockpit. No new intelligence was invented to fill customer gaps.

Owner checklist (not yet performed by a human):

- [ ] From Lloyds, locate a priority hypothesis through a relevant capability and understand why the association exists.
- [ ] Compare AI, legacy and wallet stories; distinguish evidence, interpretation and customer-validation gaps.
- [ ] Inspect all eight development modules and assess whether the next commercial action is useful.
- [ ] Open exact evidence/counterevidence and both PDF modes without losing context.
- [ ] In an authorised evaluation workspace, confirm deliberate capture and qualification behaviour.
- [ ] Assess desktop/tablet/mobile visual quality and acceptable navigation/reading effort.

Physical iPad/Safari, screen-reader audit, 20-second comprehension testing and owner acceptance are **not performed**. Chromium touch emulation is not physical-device validation. The 57 inherited failures, ten unavailable retained-artifact skips, historical source limitations and unverified buyer/budget/procurement remain outstanding. No merge, deployment or production acceptance is implied.
