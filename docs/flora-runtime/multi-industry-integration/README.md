# Banking and Aviation: one FLORA experience

Consolidates Unified Experience `a8515b91ea4e177bdb9700e05813c1d448ba189f` and Aviation/easyJet `cfa9016e6b76e9b30b7e889d16501ccfa06881ef` on verified main `ac2861e855257f3f70322bf4c1568434e565945a`. Both feature heads have that main commit as their direct parent. The original branches are preserved. Earlier feature reports/screenshots are historical snapshots; this page describes the consolidated experience.

The two textual conflicts were the shared page wrapper and research navigation. The combined wrapper preserves both optional `active` and `notice` arguments. The shared navigation remains **Home · Industries · Enterprises · Opportunities · Pipeline**. Aviation's former renderer is now a thin compatibility adapter to the Unified presentation; it has no separate SVG templates or menus.

## Walkthroughs

- **Banking:** Home → Industries → Banking → Lloyds → Operating landscape / Supplier ecosystem / Opportunity landscape → select a hypothesis → Evidence → capture into the authorised Pipeline → complete qualification and explicitly confirm.
- **Aviation:** Home → Industries → Aviation → easyJet → the same visual tabs → select a hypothesis → Evidence → the same authorised Pipeline and qualification workflow.

Canonical routes: `/industries/banking`, `/industries/aviation`, `/enterprises/lloyds`, `/enterprises/easyjet`. The Enterprises catalogue also retains Barclays, NatWest, HSBC UK and Santander UK supporting profiles. Existing governed Canvas and specialist functions retain their own access controls and contextual links. Legacy Banking and Aviation research URLs remain compatible.

Both sectors use the same six SVG templates and visual-specification contract. The global Opportunities view separates within-enterprise priorities; it does not create a cross-industry score. Banking's three existing dimensions and easyJet's four dimensions (including seller fit) are preserved. Supplier plans remain labelled as plans, not live incumbency. Two official search-index-only sources and unresolved source verification remain prominently disclosed for easyJet.

Banking research and the Aviation overlay are byte-identical to their feature commits. All six easyJet hypotheses, nine Lloyds hypotheses, dates, evidence references, source limitations and unknown commercial facts are retained. No research is automatically qualified, no Pipeline record is seeded and no account, membership, production data or configuration is changed.

## Representative current previews

| View | Desktop | Tablet-sized Chromium |
| --- | --- | --- |
| Industries catalogue | [Both industries](previews/desktop-industries.png) | [Both industries](previews/tablet-industries.png) |
| Banking industry | [Banking](previews/desktop-banking.png) | [Banking](previews/tablet-banking.png) |
| Aviation industry | [Aviation](previews/desktop-aviation.png) | [Aviation](previews/tablet-aviation.png) |
| Lloyds capabilities | [Lloyds](previews/desktop-lloyds-operating-model.png) | [Lloyds](previews/tablet-lloyds-operating-model.png) |
| easyJet capabilities | [easyJet](previews/desktop-easyjet-operating-model.png) | [easyJet](previews/tablet-easyjet-operating-model.png) |
| Lloyds opportunities | [Lloyds](previews/desktop-lloyds-opportunities.png) | [Lloyds](previews/tablet-lloyds-opportunities.png) |
| easyJet opportunities | [easyJet](previews/desktop-easyjet-opportunities.png) | [easyJet](previews/tablet-easyjet-opportunities.png) |

Desktop 1440×1000 and tablet 1024×1366 Chromium walkthroughs cover both complete public journeys, all six templates, SVG keyboard navigation, evidence and sector-specific opportunity anchors. Authenticated HTTP tests cover capture, rejected premature qualification without mutation, explicit supported qualification and Pipeline continuity for both sectors. These are not physical Safari/iPad device tests. No external preview infrastructure was created.

## Exact inherited-failure reconciliation

The original 58 are **22 domain + 12 financial diagnostics + 24 historical legacy**. Unified fixes exactly:

`tests/test_flora_enterprise_canvas.py::test_home_page_does_not_expose_synthetic_canvas_route`

The contextual Import History link is restored while the synthetic Canvas route remains absent. It is now required to pass. Thus **21 domain + 12 financial + 24 legacy = 57**. No other failure identity is removed or introduced. Three inherited HTML fingerprints changed only with the Unified menu/footer; the unchanged assertions were reproduced on original main. The existing [exact comparison](../unified-experience/Inherited-UI-Comparison.json) remains unchanged. An integration test verifies the exact old/new failure sets, those three approved signatures and all original skip reasons. The CI comparator is not weakened.

Local established gate: **PASS — 987 passed, 57 matched inherited failures, ten original skips; 1,054 unique identities.** All 388 strict security tests, 13 Aviation tests, 15 Unified tests and eight integration cases pass. Integrity: 146 unchanged storage comparisons, 15 audit chains, 17 record digests and one cleanup audit. All 25 CI-policy tests and actionlint pass. No new failure, changed unapproved signature or unexpected skip. Raw stores/logs remain outside Git under `/workspace/flora-integration-ci-local/`; sanitized results are in its `artifacts/` directory. Hosted results are verified and reported on the consolidated PR, not inferred from this local pass.

## Integration controls and remaining limits

GitHub's main-branch metadata reports `protected: false`, protection disabled and status-check enforcement off; repository rulesets are empty. The connection has repository push permission. No protection is changed or bypassed, and no independent human approval is fabricated. A successful actual-candidate hosted FLORA gate is still required by this task before a normal merge.

Owner-verified Render Auto-Deploy is disabled and no repository webhooks exist. The targeted check found four GitHub workflows: FLORA validation, architecture artifact export, tag/manual-only Researcher pack publication and Chief Architect pack validation. None deploys application code to production. A main merge can publish the existing architecture export artifact; it does not deploy FLORA. No deployment settings are changed.

Remaining limitations are source maturity, unverified buying demand/eligibility, current supplier scope, the known inherited diagnostics and unavailable retained-artifact skips. No new UX defect is known from the completed focused tests. Live-service acceptance still requires a separately approved manual deployment; none is performed here.
