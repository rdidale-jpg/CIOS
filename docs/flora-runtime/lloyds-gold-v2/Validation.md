# Validation and release status

Base: `1c8c8ae17bb2af3c95bf264d7df9befb60b0b576`, verified origin/main and successful post-merge main CI run `45996416290` before branching. Branch: `codex/flora-lloyds-gold-v2`. Runtime deployment is excluded.

## Reproducible checks

- `python -m pytest tests/test_flora_lloyds_gold_v2.py tests/test_flora_gold_reconciliation.py tests/test_flora_research_intelligence.py -q`: 105 passed after Source lifecycle, temporal composition and candidate-review reconciliation.
- `python docs/flora-runtime/lloyds-gold-v2/browser.py <output> after`: 32 actual Chromium captures across desktop, iPad landscape, iPad portrait and mobile; keyboard, touch, native whole-region hits, no-JavaScript, Back/Forward, reload, deep links, print/accessibility withdrawal and Banking/easyJet compatibility passed.
- Same driver on the #741 worktree with `before`: 24 equivalent captures. No comparison image is fabricated. Proof JSON records the exact runtime hashes and whether they match its checkout SHA; hosted CI reruns the driver on the final PR head.
- `python tools/ci/flora_ci.py --output <empty-directory>`: mandatory existing full regression/security gate, unchanged baseline, comparator and skip/failure policy.
- Existing Economics workflow runs Financial/source/access compatibility, all 388 strict security tests, older preview/CEO/Main Canvas journeys and this Gold v2 browser driver on the exact PR head.

Final new-functionality suite: **67 passed**, including strategic-role destination and optional evidence-inspection coverage. Final browser run: **32 captures, four device sizes**, clean runtime commit `93feb94fd2c9ee468485d50b8d24916e79cae007`. The final evidence commit only records these captures and validation text.

Additional completed local checks: 357 Gold/CEO/Main Canvas/current-source cases; 137 existing VP-2 presentation/access cases; 26 primary-enrichment/multi-industry cases; eight commercial-assessment cases; 130 BIE-2/BIE-3/history compatibility cases. Historical Gold (31 captures), CEO (42), Main Canvas (37), subject activation (12), service knowledge (8) and Gold reconciliation (16) browser runs passed; EAI-2 completed 843 browser assertions. Full strict security completed 388/388 in the exploratory gate.

The exploratory full gate exposed six previously passing count/immutable-overlay assertions; these were individually reconciled for the exact additive cut, without a baseline refresh. Older candidate-analysis cutoffs also require 27 November to include the new November 18 source. The corrected complete gate and hosted checks must finish before integration. Final exact-head results and links are recorded in the PR and completion report; this document does not predeclare a pending run successful.

## Historical fidelity

Every previous assessment Source/claim object remains equal; all historical source and research dossier files remain byte-for-byte unchanged. The candidate Understanding review changes only assessment/date references, including four existing sources' assessment-digest references; its statements, rights, claim reviews, observations and relationships are unchanged. Exact additive-cut checks verify the new overlay/review and short excerpts before the unchanged historical comparator runs. Unknown mutations/additions still fail. Original failure/skip corpus and comparator are not refreshed. Passed assertions that assumed a final claim/source count now include the exact 39/7 addition while retaining original-record comparisons. Candidate-analysis test cutoffs move from 10 to 27 November to cover the newer November 18 source; the future-retrieval negative fixture moves to November 28, preserving its denial. The older EAI browser now verifies a neutral whole-region Customer operations destination instead of the removed complaint attention marker.

The source-import, Financial, canonical import, security/ACL, Pipeline implementations and accepted ADRs are unchanged. New generic presentation checks withhold restricted/mismatched disclosure bindings; they cannot issue a Source permission or owner acceptance. The older Gov CEO record can be withdrawn without hiding an independently verified current issuer GEC record; both paths have their own lifecycle checks.

## Rollback

The complete increment is reversible against its first parent without data/schema migration. In an isolated temporary git index, reverse the base-to-candidate binary diff and compare the resulting tree to the base tree. The final validation records that equality. Operational rollback requires a separately authorised deployment of the previous successful release; this sprint neither queries nor changes Render.

## Owner acceptance

Review the three scopes, select a leader and actual programme, compare banking business models, inspect the seven goal chains and eight SWOT themes, and try both iPad orientations. Check the intelligence itself: named roles and programmes must be useful, the reported periods and targets distinct, and no assumed profit split, contract scope, buying intent or held financial figure implied. Significant remaining gaps are stated in the 18-question assessment rather than hidden by a completeness score.


## Final historical-design correction

The complete design-contract job additionally found three older tests that byte-pinned the Banking overlay. They now verify their original manifest digest against the preserved predecessor, then call the existing exact research-cut guard. Artwork, other owners and original assertion/relationship judgments remain pinned. All **101 tests** in those three modules pass locally. No runtime or research data changed in this correction; none of these three test modules is selected by the 1,432-case local regression gate. That gate's run at `9821c9217349bf37f49e36c717b95966ca43ede8` remains applicable to the identical runtime and selected test inputs. Hosted validation reruns all required jobs against the final head, including the corrected design/semantic jobs.
