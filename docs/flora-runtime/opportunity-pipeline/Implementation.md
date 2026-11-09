# Banking opportunity discovery and commercial pipeline

Isolated branch: `codex/flora-opportunity-discovery-pipeline`, based on Banking Explorer `b2ca3d75c0387f9bacc0ae698861311e7bf1f295` (application `abb87dba2d1e2300f1679833f0b8bad36fbacbd7`). The existing Explorer branch, PR #543 and integrated main are preserved. No push, merge, deployment or production provisioning is included.

## Working journey

Banking Explorer → select Lloyds or Barclays → **Opportunity landscape** → select a business/technology lens or opportunity node → inspect the commercial hypothesis and source context → **Add to pipeline & qualify** → document qualification → explicitly select and confirm a stage → open the pipeline list or stage board → update the next action and record activity.

The public opportunity landscape is available for every existing bank fixture. The disposable demonstration seeds four hypotheses across Lloyds and Barclays. Public context remains readable without sign-in; captured commercial records require an existing verified identity and selected authorised workspace.

## Screens and reuse

- `/flora/banking/explorer/{bank}/opportunities`: six-node interactive SVG landscape, business/technology/supplier lenses, evidence-labelled opportunity cards, and links to manual creation and pipeline. Hypothesis nodes are peach; private maturity badges use green for qualified and violet for active pursuit. Supplier links describe research dependencies, not established contracts.
- `/flora/banking/explorer/{bank}/opportunities/{hypothesis}`: observation, interpretation, commercial implication, potential proposition, evidence/confidence and next action, plus capture into a private workspace. Existing opportunity assumptions, values and evidence views are linked rather than duplicated.
- `/flora/sales/{id}`: editable commercial brief; value basis and assumptions; ten MEDDICC-informed criteria with supporting references; evidence assessment; stage confirmation; activity capture; versioned change history. Validation restores the unsaved form. A stale version shows a recoverable draft alongside the current record instead of overwriting it.
- `/flora/sales/pipeline`: list and stage-board views, filters for industry, enterprise, owner, stage, evidence assessment, value basis, currency and minimum stated amount. Shows priority, next action, last update and completeness. Known and estimated amounts are separate per currency; unknown values are counted. Won/Lost are excluded from open totals. No probability weighting or currency conversion is invented; minimum-amount filtering requires an explicit currency.
- `/flora/sales/new`: manual demonstration hypothesis creation, using an existing bank and starting at Discovered with unknown amount/confidence.

Reuses `banking_portfolio.BANKS`, existing opportunity objects and source labels, Banking Explorer shell/breadcrumbs/SVG patterns, evidence/financial/hypothesis routes, existing sign-in and CSRF forms, capability/resource evaluator, service write/read envelopes, protected file journal and authority audit chain. No new authentication or permission engine. Existing governed Canvas discovery remains available; public bank fixture IDs are not assumed to establish private Canvas ownership.

## Persistent data model

The versioned envelope at `<FLORA_DATA_DIR>/sales_pipeline/opportunities.json` contains records with:

- Immutable ID, industry, enterprise identity/slug, authoritative selected workspace, demonstration flag, origin hypothesis and source provenance.
- Editable business problem, proposed solution, commercial owner display label, priority, next action, procurement timing and evidence-assessment rationale.
- Decimal amount, currency, value basis and assumptions/customer supporting reference. Initial amounts and timing are Unknown; scenario estimates are never imported automatically as budgets.
- Ten qualification notes and references: measurable problem, strategic priority, economic buyer/stakeholders, funding, decision process/criteria, competition, differentiation, procurement timing, relationship/champion and mutually supported next action.
- User-reviewed evidence flag, workflow stage, created/updated timestamps, integer version and actor-attributed before/after change/activity history.

The schema has industry and enterprise fields so additional industry adapters can be added later; creation is deliberately bounded to the existing Banking set now. Commercial owner assignment is a display/work-allocation field and grants no access.

Capture is idempotent per workspace/enterprise/source hypothesis. Updates use optimistic version checks. Writes and audit digests share the existing verified transaction/protected-journal envelope; audit failure restores the prior file and history. Reads and writes intersect active membership, effective capability, persisted workspace/enterprise and any existing enterprise ACL. No ACL or workspace ownership is fabricated for public fixtures: these are separate commercial records, not a new governed Canvas.

## Qualification and truth labels

Market/source context, opportunity hypotheses, evidence-backed potential, user-qualified sales opportunities and active pursuits are shown separately. All records in this increment remain demonstration records, even if qualified or marked Won.

A criterion is complete only when both a note and supporting reference are supplied; Unknown/TBC and equivalent placeholders remain missing. Percentage = completed criteria / ten; it is **input completeness**, not AI confidence, probability of winning or independent verification of source quality. Evidence-backed potential requires the problem/priority references and explicit user evidence review. Qualified/Pursuit/Proposal/Negotiation/Won require all ten inputs and evidence review; advancing into these stages additionally requires explicit confirmation. Saving complete inputs does not promote the stage automatically. Won/Lost require an outcome reference and confirmation. Closed records cannot be reopened in this increment.

Human reference entry and review do not magically verify a customer requirement. Actual source quality, sponsor authority and customer commitments still require commercial judgement. A customer-confirmed amount is explicitly a user-recorded statement with a reference, not an independent FLORA finding.

## Browser compatibility correction

Real HTTPS browser testing reproduced an inherited sign-in failure: `Referrer-Policy: no-referrer` caused Chromium's form POST to carry `Origin: null`; the existing strict origin check correctly rejected it. Changing only the document policy to `same-origin` produced the expected HTTPS origin and enabled ordinary sign-in and commercial forms. Cross-origin referrers remain withheld. Origin validation, session verification, CSRF tokens, membership and capabilities are unchanged. No origin-check bypass or test-only browser header injection is used by the successful journey.

## Reproducible interactive demonstration

Install normal repository requirements in a development virtual environment, then run:

```sh
python tools/demo_flora_sales.py
```

The runner creates a **new disposable temporary root**, one explicitly synthetic identity through the existing offline operator/enrollment flow and four clearly labelled bank hypotheses. No API keys, production stores or inherited runtime configuration are used. It prints a local HTTPS URL and the path to a private `demo-access.json` file with randomly generated development credentials. Read that local file, sign in normally, select `demo-sales-workspace`, then open the printed Explorer or pipeline URL.

The local server binds only to loopback, uses a temporary self-signed localhost certificate and stops with Ctrl-C. A developer must trust/accept that local certificate in their local browser for the demo; no live service certificate/configuration is changed. The application reloads persisted records from its configured root across processes/restarts. The demo runner intentionally creates a fresh temporary root on each launch; its data is disposable rather than a production durability guarantee. No external preview hosting is configured or created.

Optional development-only Chromium acceptance (Playwright required):

```sh
python tools/preview_flora_sales.py --access-file /tmp/flora-sales-demo-.../demo-access.json --output /tmp/flora-sales-previews
```

This runner only accepts the disposable localhost demo identity/workspace. It performs ordinary browser sign-in, enterprise navigation, capture, rejection/recovery of incomplete qualification, explicit Qualified/Pursuit changes, activity/next-action edits, manual creation, board/filter navigation and desktop/iPad layout checks. Certificate-error tolerance is confined to that local test context. It does not fabricate an Origin header or bypass application authentication.

## Validation and evidence

Focused coverage: `python -m pytest -q tests/test_flora_sales_pipeline.py tests/test_flora_banking_explorer.py` — **37 passed** (25 commercial, 12 Explorer), including an independent-process persistence read, edit history, Won/Lost outcomes, empty/Unknown reference rejection, amount/currency separation, optimistic conflicts, read-only UI, workspace/enterprise/ACL restrictions, rejected-write rollback and authenticated HTTP/CSRF workflow. `python -m unittest discover -s tests/ci -q` — **25 passed**, including deliberate failure/skip probes.

The final ordinary-browser walkthrough passed with real sign-in and no injected Origin headers: capture, error/draft recovery, explicit Qualified and Pursuit transitions, activity, next-action editing, manual creation, filtering and stage board. Chromium viewports: **1440×1000**, **1024×768** and **768×1024**; no horizontal overflow or JavaScript errors. These are iPad-sized viewport checks, not native Safari/device certification.

The established full gate is run with `python tools/ci/flora_ci.py --output /workspace/flora-sales-ci-final`. **Final result: PASS. 974 distinct identities: 906 passed, 58 inherited failures, 10 original skips; zero comparison issues.**

| Suite | Actual result |
| --- | --- |
| Commercial pipeline | 25 passed |
| Banking Explorer | 12 passed |
| Security | 388 passed |
| Domain, including Factory/Experience/Governance | 404 passed, 22 inherited failures, 10 original skips |
| Financial diagnostics | 35 passed, 12 inherited failures |
| Historical legacy | 3 passed, 24 inherited failures |
| Supplemental application | 39 passed |

Existing integrity/audit gate: 146 unchanged comparisons, 15 audit chains, 17 audit-record digests and one cleanup audit. New commercial tests additionally verify persisted record/history digests and rollback when audit persistence fails. No new failures, changed failure signatures or unexpected skips. Browser acceptance and focused tests passed on the final presentation. No skipped new commercial tests. Existing baseline identities, inherited failure signatures and skips are unchanged; only 25 expected-pass commercial tests are added to the 01B profile. Workflow configuration is unchanged.

Committed visual previews (all synthetic; no passwords or tokens):

- [Opportunity diagram](previews/opportunity-diagram.png)
- [Lloyds opportunity landscape](previews/lloyds-opportunity-landscape.png)
- [Qualification workspace](previews/qualification-workspace.png)
- [Pipeline on iPad-sized viewport](previews/pipeline-ipad.png)

No static export is presented as an editable backend preview. The local HTTPS demonstration exercises the actual services and persistence. External preview publication requires separate authorisation.

## Remaining limitations and enrichment

- Initial bank/source data is historical curated context. Add current primary documents and claim-level source locations, accepted observations, freshness and confidence rationale before claiming current customer demand.
- Acquire customer-validated business impact, buyer/champion authority, funding, procurement process and dates. Supplier presence is not verified bank incumbency.
- Qualification is a transparent, human-confirmed capture framework; reference contents and commercial quality are not independently verified automatically.
- Demonstration-only records, single local protected JSON store, no distributed CRM synchronisation, task notifications, currency conversion, forecast weighting or closed-record reopening. No production sales records are claimed.
- The next industry requires a reviewed source adapter, not cloning the Banking fixture into another sector. Future real-world opportunity enablement should explicitly define demonstration-versus-real record policy and integrate accepted Enterprise/Evidence mappings.
- Existing sign-in/workspace selection still hands off to the import-history page. Sign in first, then open Banking Explorer (as in the verified demo walkthrough); a new authentication return-target mechanism is not introduced here. Legacy evidence views may require browser Back to return to the originating opportunity.
- Hosted CI has not run for this isolated branch because pushing is not authorised. Local/browser results do not imply deployment approval.
