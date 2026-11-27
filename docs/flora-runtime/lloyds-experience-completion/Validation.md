# Validation and rollback

Baseline: `3d9bdb84e64908a3a99dea1f857fecb57b835b88`, with successful full main CI [46018605703](https://github.com/rdidale-jpg/CIOS/actions/runs/46018605703).

The final PR checks and their immutable head identify release validation. Checked-in browser manifests identify their actual capture commit and runtime hashes; subsequent evidence-only changes must not be mistaken for a new render. Hosted CI regenerates the complete after capture set against its checked-out PR head.

## Reproduce

```sh
python -m pytest tests/test_flora_lloyds_gold.py tests/test_flora_lloyds_ceo.py tests/test_flora_main_canvas.py tests/test_flora_lloyds_gold_v2.py tests/test_flora_gold_reconciliation.py tests/test_flora_lloyds_experience_completion.py -q
python -m pytest tests/test_flora_security*.py -q
python tools/ci/flora_ci.py --output /tmp/experience-ci-new-empty-directory
python docs/flora-runtime/lloyds-experience-completion/browser.py /tmp/experience-browser after
python docs/flora-runtime/lloyds-experience-completion/validate.py
```

The existing Enterprise Economics workflow additionally executes its compatibility tests, historical immutable cuts and all existing product browser drivers. No approved failure, skip, baseline or comparator is changed.

The affected test run passed 455 cases during implementation. The final integrated browser run passed 48 captures across four sizes, physical region hits, keyboard/touch, history/reload/deep links, no-JavaScript navigation, 200% zoom, withdrawal through history/print/accessibility and preserved Banking/easyJet/legacy routes. The strengthened geometry check includes node content and the surrounding composition boundary. Main Canvas's existing browser driver also passed 37 captures across four sizes after its removed-layout selectors were individually reconciled.

Final exact-head local and hosted results are linked in the PR. Do not infer deployment from any test or merge.

## Issues resolved by checks

- A surviving FY25 deposit source was initially omitted from the new funding selection. Each eligible stock now renders independently; withdrawal of Q3 also removes its difference calculation.
- Secondary wording could otherwise outlive a withdrawn source. Factual examples are conditional; economic mechanisms are explicitly conceptual.
- The older EAI-2 browser expected a funding-agenda marker directly on the Group root. It now follows the actual whole-region Customer funding link, verifies the primary comparison and retains the exact-one and numerical-content checks.
- Two hosted suites exposed the same remaining EAI-2 assertion requiring the stock difference on the Group root. It now verifies root discoverability and all three values exactly once in the dedicated funding view while retaining denied-service omission in both views.
- Narrow Main/200% zoom initially overflowed fixed diagram regions. Container-width reflow and readable native targets correct that failure.
- The SWOT foundation extended beyond its diagram and legacy timeline margins affected contextual controls. Bounds and spacing are corrected; browser assertions cover the geometry.
- An exploratory regression run spanned changing checkout SHAs, so its deployment-identity signature was not valid exact-head evidence. The comparator remains unchanged; the final run uses a fixed committed head.

## Rollback

`validate.py` reverses the complete binary commit delta in an isolated temporary index and requires the resulting tree to equal the baseline tree exactly. It prints the exact file inventory, candidate SHA and both tree IDs. No working checkout, database or production record is changed by this proof.

After merge, a controlled `git revert -m 1 <integration-merge-SHA>` reverses this one increment. Run existing checks before integrating the revert. There is no schema/data/authentication migration. Render is not deployed or reconfigured by this sprint; its currently deployed version is not inferred.

## Genuine limits

The §2 three-measure hold and §5 deferred PDF links are unchanged. No new financial figures, segment allocations, current capital ratio/RWA bridge, complete installed-system topology, contract schedules or buying authority are admitted. The original source/artwork/security/Financial/Pipeline implementations remain unchanged. Physical iPad/Safari and owner commercial/visual acceptance remain separate from Chromium emulation.
