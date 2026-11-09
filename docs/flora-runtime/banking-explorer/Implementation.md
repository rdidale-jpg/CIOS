# Banking Industry Explorer

Reference vertical slice based on integrated main `fda5864e60be159683662ad66098b7abfddeba66`.
Feature branch: `codex/flora-banking-industry-explorer`. Local development only; no publication, merge or deployment.

## Working journey

Open FLORA home → **Banking Explorer** → select **Lloyds Banking Group** → **Explore operating landscape** → select **Customer & service** → inspect **Strategic insights** → expand validation assumptions or open existing source/evidence and detailed hypothesis views. All five existing public bank profiles are selectable; Lloyds is the browser-tested reference journey.

New screens:

- `/flora/banking/explorer`: industry overview, five enterprise cards, conceptual ecosystem, market forces and links to existing financial/technology signals, outlook and opportunities.
- `/flora/banking/explorer/{bank}`: enterprise overview, dated financial reference points, strategic priorities, conceptual operating landscape, business divisions, technology context, explicit supplier/partnership gaps, competitive navigation and change hypotheses.
- `/flora/banking/explorer/{bank}/insights`: observation → interpretation → implication → opportunity → evidence/confidence, with assumptions, next validation action and disconfirming signals.

FLORA home and the existing Banking landing page now provide prominent Explorer entry links. Existing detailed views remain available.

## Reuse and new components

Reused: `banking_portfolio.BANKS`, existing opportunities and `analyst_sources` labels; the FLORA product shell and verified account presentation; existing evidence, financial, comparison, supplier scenario, research/industry inspection and hypothesis routes. Existing protected Canvas discovery is linked through `/digital-twins`; no public fixture ID is assumed to identify a private Enterprise Model.

New: a read-only presentation module, scoped responsive styling, linked SVG ecosystem/operating diagrams and equivalent compact mobile links, structured insight cards, finite public-route catalogue entries for the existing fixture slugs, HTTP journey tests and an optional local browser preview command. No new persistence, external data retrieval or authentication mechanism.

The public route entries have no query parameters. Unknown slugs, extra path segments and workspace-selection parameters do not gain public access. Protected Canvas and accepted canonical Evidence retain their existing controls.

## Experience details

Breadcrumbs and enterprise navigation preserve context. Diagrams link to underlying sections, insights and existing evidence/context views. Native details disclosures expose assumptions without JavaScript. Server-rendered content has no asynchronous loading dependency. Unknown enterprise and empty insight states are explicit. Mobile uses equivalent labelled node links instead of shrinking a desktop diagram; desktop and mobile share the same destinations. Keyboard focus, a skip link and reduced-motion handling are included.

Source labels are context, not claim-level verification. The old fixture's `sources` field contains limitations for some banks; the Explorer uses the existing `analyst_sources` context labels and does not reinterpret those limitations as source documents. Historical financial periods and group-versus-UK scope are visible. Editorial conviction is distinguished from calibrated evidence confidence.

## Visual evidence

Chromium previews captured at 1440×1000 desktop and 390×844 mobile. Selected previews are committed:

- [Industry desktop](previews/industry-desktop.png)
- [Enterprise desktop](previews/enterprise-desktop.png)
- [Insights mobile](previews/insights-mobile.png)

Optional reproducible local browser check (requires Playwright and Chromium): run a local FLORA server, then `python tools/preview_flora_banking.py --url http://127.0.0.1:8765 --output /tmp/banking-previews`. It verifies the home-to-insight journey, SVG/mobile navigation, expanded validation details, keyboard skip navigation, horizontal overflow and JavaScript errors; it captures all six previews. The tool refuses non-local targets. Browser dependencies are development-only and are not added to production requirements.

## Validation

- `python -m pytest -q tests/test_flora_banking_explorer.py`: **12 passed**. Covers all five banks, insight/evidence/hypothesis destinations, anchor resolution, attribution, empty/unknown states, escaping, finite route classification, protected Canvas rejection and unchanged local protected storage.
- `python -m unittest discover -s tests/ci -q`: **25 passed**, including deliberate failure/skip detection probes (their printed FAIL outcomes are expected assertions).
- Local Chromium browser acceptance: **PASS**, desktop and mobile, including keyboard navigation.
- `python tools/ci/flora_ci.py --output /workspace/flora-banking-ci-1`: **PASS**, established 01B profile. **949 distinct identities: 881 passed, 58 inherited failures, 10 original skips**; zero comparison issues. Security **388 passed**; domain **404 passed / 22 inherited failures / 10 original skips**; financial **35 passed / 12 inherited failures**; legacy **3 passed / 24 inherited failures**; supplemental **39 passed**; Explorer **12 passed**. Integrity: **146 unchanged protected-data comparisons**, **15 audit chains**, **17 audit-record digests**, **1 cleanup audit**. Private temporary stores/logs remain outside the feature worktree. No new or changed failures and no unexpected skips. The new feature suite was rerun after final attribution/formatting edits: **12 passed**; browser previews were captured from the corrected presentation.

The existing workflow is reused unchanged. Twelve expected-pass identities are added as the `banking_explorer` suite in the 01B baseline; every existing identity, inherited failure signature and skip remains unchanged. New failures, changed failures, missing cases and unexpected skips remain gate failures. Hosted validation requires separately authorised publication; local results do not claim a new GitHub-hosted pass.

## Data gaps and next enrichment priorities

1. Attach current, dated primary reports and claim-level source locations to Lloyds observations, with financial scope and reporting-period reconciliation.
2. Acquire accepted capability ownership, application/platform inventories and dependency relationships before rendering them as verified architecture.
3. Validate bank-specific supplier/partner contracts, renewal windows, programme owners, budgets and delivery status; industry market presence alone does not establish incumbency.
4. Link an authorised, accepted bank Enterprise Model to its Canvas through existing discovery and ACL evaluation when one is available.
5. Refresh historical financial/context fixtures and distinguish customer-confirmed programmes from strategic hypotheses. No new factual population is fabricated in this increment.

Existing detailed product/diagnostic failures are tracked by the established CI baseline. This increment creates a coherent new presentation path; it does not claim to repair every historical Banking report or establish production acceptance.
