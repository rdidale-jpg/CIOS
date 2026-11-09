# Unified experience and visual Twins

Feature branch: `codex/flora-unified-visual-experience`, from verified main `ac2861e855257f3f70322bf4c1568434e565945a`. This is a local UX increment; nothing is pushed, merged or deployed. No research facts, governed assets, accounts, workspace settings, opportunity records or activity history are migrated or deleted.

## Owner walkthrough

Open Home → **Industries** → **Banking** → **Explore Lloyds** → **Opportunity landscape** → select a hypothesis → inspect its evidence. On an authorised running instance, the existing candidate brief can capture a hypothesis into Pipeline and invoke the unchanged qualification workflow. Reading a diagram cannot create or qualify a record.

| Previous primary menu | New primary menu |
| --- | --- |
| Home · Intelligence · Opportunities · Research · Governance | **Home · Industries · Enterprises · Opportunities · Pipeline** |

Research, advanced intelligence, Canvas, financial intelligence, Import History, governance and settings are contextual tools. Destination handlers retain their existing authorisation. A visible link does not grant authority. The primary menu is shared by the product shell and legacy workspace shell.

## One Banking and Lloyds entry point

| Canonical page | Purpose |
| --- | --- |
| `/industries` | Industry catalogue; Banking is the integrated reference. |
| `/industries/banking` | Supported disclosures, PESTLE, Five Forces, value chain, enterprise landscape and commercial implications. |
| `/enterprises` | Existing bank profiles, with enriched versus historical coverage labelled. |
| `/enterprises/lloyds` | Capability landscape, supplier evidence, important disclosures, programmes and commercial priorities. |
| `/opportunities` | Existing ranked research shortlist, candidate briefs and a full expandable opportunity landscape. |
| `/flora/sales/pipeline` | Existing authenticated workspace Pipeline, qualification and activity history. |

Legacy `/flora/banking`, `/flora/banking/lloyds`, `/flora/banking/explorer`, its enterprise pages, `/flora/banking/research` and its Lloyds dossier remain HTTP 200 compatibility routes. They lead to the unified entry points and retain supporting content under expandable sections. This preserves old links, anchors and source access without making the historical pages competing primary destinations. Existing specialist, source, evidence, insights, import and Canvas routes remain available.

The Home dashboard's older intelligence summaries and the Opportunities page's historical Horizon scenarios remain expandable supporting views. Explicit historical Horizon queries still open their contextual section. Illustrative legacy sizing is not promoted into the current research shortlist or Pipeline.

Canonical pages favour supported disclosures with explicit observation periods. Detailed quotations, source dates, provenance, historical observations, supersession, inferred relationships and unanswered questions remain available through drill-down. Other banks are labelled as historical profiles with incomplete deep research; no current capabilities or supplier contracts are invented for them.

## Six visual templates from research

| Template | Research input | Visual form |
| --- | --- | --- |
| PESTLE | Six `frameworks` with `lens=pestle` | Six-segment radial infographic; segments open affected capabilities and evidence. |
| Five Forces | Five `frameworks` with `lens=porter` | Competitive cross with distinct rivalry, buyer, supplier, entry and substitute positions, plus assessment excerpts. |
| Value chain | Ordered `frameworks` with `lens=value-chain` | Horizontal chevrons, keyboard links and equivalent compact destinations. |
| Enterprise operating model | `capabilities`, their evidence and candidate mappings | Capability map; conceptual coverage and linked research hypotheses, not an asserted organisation chart. |
| Supplier / technology ecosystem | `suppliers` and exact enterprise relationship edges | Enterprise-to-provider diagram; source-supported links solid, reported or unknown links dashed. Current contract scope remains unverified. |
| Opportunity landscape | Existing `commercial_candidates` output | Ranked rows and separate relevance/access/evidence ratings; seller fit is rendered when supplied by the provider. No combined probability, budget or automatic qualification. |

`research_intelligence.visual_specs.build_visual_specs(data, routes, priorities=None)` adds a visual output to the existing overlay; it does not replace the research schema, evidence spine or ranking engine. An optional `priorities` argument accepts another sector provider's existing ranked output, preserving its scoring policy. Presentation destinations are server-supplied local paths, including an optional sector-specific `opportunities` destination.

Each specification includes schema version, diagram type, title/summary, nodes/categories, exact relationships, justified priority or null, evidence references and periods, verification status, research assessment date, enterprise links and candidate links. Node status distinguishes source-supported disclosures, historical or superseded observations, management expectations, interpretations and unverified research. Assessment date is not substituted for source publication date.

The validator rejects unknown or omitted nodes, unsupported summaries, changed dates, invented priorities, changed ratings, invented or upgraded relationships and altered evidence lineage. Rendering is deterministic SVG/HTML; labels and excerpts come from research, not an image model. No external image-generation service, paid API or new dependency is introduced. Public structured output is inspectable at `/industries/banking/visual-specs`.

## Cross-industry compatibility

No Aviation implementation, research file or route is imported into this feature. The parallel Aviation branch remains unchanged. A read-only interface check supplied its committed overlay and its own ranking output from `cfa9016e6b76e9b30b7e889d16501ccfa06881ef` to this visual API: all six templates rendered, with six opportunities and four distinct ratings. That local experiment is evidence of interface compatibility, not a CI dependency on an unpublished branch or a claim that Aviation is integrated into this branch.

The automated generic-configuration test changes presentation routes without changing facts or duplicating Banking rendering code. Integrating another sector requires its approved data provider and route registration; the six templates accept the same structured interface.

## Visual assessment

Previews are actual Chromium screenshots from a disposable, empty local runtime. No production credentials, customer data or identities were used. Desktop is 1440×1000; iPad-size layout is 1024×1366. These are browser viewport checks, not a claim of physical Safari/iPad testing.

| View | Desktop | iPad-size |
| --- | --- | --- |
| New Home and navigation | [Home](previews/desktop-home.png) | [Home](previews/ipad-home.png) |
| Banking landing | [Banking](previews/desktop-banking.png) | [Banking](previews/ipad-banking.png) |
| PESTLE | [Radial infographic](previews/desktop-pestle.png) | [Radial infographic](previews/ipad-pestle.png) |
| Five Forces | [Competitive diagram](previews/desktop-porter.png) | [Competitive diagram](previews/ipad-porter.png) |
| Value chain | [Horizontal chain](previews/desktop-value-chain.png) | [Horizontal chain](previews/ipad-value-chain.png) |
| Lloyds landing | [Lloyds](previews/desktop-lloyds.png) | [Lloyds](previews/ipad-lloyds.png) |
| Operating landscape | [Capability map](previews/desktop-operating-model.png) | [Capability map](previews/ipad-operating-model.png) |
| Supplier ecosystem | [Relationships](previews/desktop-ecosystem.png) | [Relationships](previews/ipad-ecosystem.png) |
| Opportunity landscape | [Ranked hypotheses](previews/desktop-opportunity-landscape.png) | [Ranked hypotheses](previews/ipad-opportunity-landscape.png) |
| Evidence drill-down | [Evidence](previews/desktop-evidence.png) | [Evidence](previews/ipad-evidence.png) |

[Additional read-only easyJet renderer example](previews/generic-easyjet-renderer.png): generated from the supplied parallel research through the same capability-map template. This is a static compatibility illustration, not a separate Aviation application or published environment.

Both viewport walkthroughs checked the exact five primary destinations, Industry → Enterprise navigation, keyboard Enter on SVG nodes, opportunity/evidence drill-down and six core pages without horizontal page overflow. Wide value chains scroll within their figure; all diagrams provide equivalent text navigation. Small screens use compact link layouts. Source confidence and temporal context remain textual, not colour-only.

## Validation and inherited comparison

The initial complete gate correctly rejected the obsolete navigation expectation and four changed inherited HTML fingerprints. The old navigation test now enforces the requested five destinations exactly, with specialist functions outside the primary menu. No security assertion or comparator rule was relaxed.

Four historical failures were reproduced on unchanged main in an isolated worktree and on the candidate with separate disposable stores. The missing Import History link is fixed and its original test is now required to pass. Three failures remain at the exact same assertions in byte-identical test files; only the rendered-HTML exception suffix changed with the shared navigation/footer. Their exact expected fingerprints were refreshed after that comparison. [Comparison evidence](Inherited-UI-Comparison.json) retains the prior and new signatures, unchanged assertion predicates and test-file digests. No failure was excluded or added to the inherited allowlist; the comparator still rejects every new failure, changed signature and unexpected skip.

Final established local gate: **PASS**, profile 01b, **1,033 unique test identities**.

| Selection | Passed | Matched inherited failures | Original skips |
| --- | ---: | ---: | ---: |
| Banking Explorer | 12 | 0 | 0 |
| Commercial assessment | 8 | 0 | 0 |
| Domain / Factory / Experience / Governance | 405 | 21 | 10 |
| Financial diagnostics | 35 | 12 | 0 |
| Historical legacy | 3 | 24 | 0 |
| Primary enrichment | 18 | 0 | 0 |
| Research intelligence | 18 | 0 | 0 |
| Sales Pipeline | 25 | 0 | 0 |
| Strict security | 388 | 0 | 0 |
| Supplemental | 39 | 0 | 0 |
| New unified UX and visual contracts | 15 | 0 | 0 |
| **Total** | **966** | **57** | **10** |

No new failure, changed unreviewed signature, missing/duplicate identity or unexpected skip. One original domain failure is fixed; the remaining 57 include the three explicitly re-proven presentation fingerprints described above. Ten original unavailable-retained-artifact skips remain unchanged.

Integrity checks: **146 unchanged protected-storage comparisons**, 15 verified audit chains, 17 verified record digests and one verified cleanup audit. All **25 CI-policy tests** passed, including deliberate regression/skip rejection; workflow actionlint passed. The existing 81 focused Banking/research/Pipeline tests and the 21 new-UX/information-architecture selection passed. These overlap the full gate; they are not additional unique gate identities. The existing PDF-import test emits a PyMuPDF API deprecation warning.

Commands used (the prepared Python environment and actionlint binary were reused):

```sh
actionlint .github/workflows/flora-validation.yml
python -m unittest discover -s tests/ci -q
python -m pytest -q tests/test_flora_banking_explorer.py tests/test_flora_research_intelligence.py tests/test_flora_primary_enrichment.py tests/test_flora_commercial_assessment.py tests/test_flora_sales_pipeline.py
python -m pytest -q tests/test_flora_unified_experience.py tests/test_flora_v2_information_architecture.py
python tools/ci/flora_ci.py --output /workspace/flora-unified-ci-verified
git diff --check
```

Sanitized full-gate artifacts remain in `/workspace/flora-unified-ci-verified/artifacts/`; private stores and raw diagnostics remain outside the repository and are not committed. Separate baseline/candidate proof results remain under `/workspace/flora-unified-main-proof-complete/` and `/workspace/flora-unified-candidate-proof-complete/`; the committed comparison JSON contains the bounded relevant evidence, not runtime stores or full HTML diagnostics.

Desktop/iPad-size browser journeys passed with no runtime errors. Additional SVG bounding-box checks verified labels inside rectangular diagram nodes at iPad size, and the contextual Import History link was verified against the final running source. No application or test changes followed completion of the final gate. GitHub-hosted validation is not asserted because this branch is not published.

Remaining qualification limits: existing inherited product/financial/legacy defects remain separate from this UX work; public disclosures do not establish customer demand, buyer authority, procurement timing or contract value. Actual Safari and production acceptance remain outside the local preview. No production deployment is performed.
