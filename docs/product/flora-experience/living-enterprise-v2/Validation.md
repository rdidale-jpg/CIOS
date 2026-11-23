# Validation and rollback

**Scope:** Phase A contract, design composition and browser prototype only. Current main/Render code is `97d316c640c96d99c2301819f8aac00b3b9c1398`; the final design commit is reported in the draft PR. No application, Source, security, research, Financial, canonical, dependency or workflow files are changed.

## Reproduce

From repository root using the existing Python dependencies and Playwright Chromium:

```sh
python -m pytest -q docs/product/flora-experience/living-enterprise-v2/checks.py
python docs/product/flora-experience/living-enterprise-v2/export.py
python docs/product/flora-experience/living-enterprise-v2/browser.py /tmp/flora-living-browser
python docs/product/flora-experience/living-enterprise-v2/validate.py
```

`browser.py` currently selects system `/usr/bin/chromium`. The validation environment used existing `/workspace/cios-venv` dependencies and Playwright 1.62, with no paid API or infrastructure. The renderer uses a temporary data directory; the test server closes on completion. The self-contained export uses the same 12 already rendered design states, not a separate intelligence owner.

## Evidence and applicable assurance

- **15 design/content checks:** three perspectives × four visual regions; one selected region; no reading selector, PDF links or Main evidence accordions; eight existing SWOT themes; invalid/duplicate/private state rejection; temporary frame seams restored; subject context retained; withdrawn Source removes dependent figures, Curve marker and affected SWOT while independent material remains; wrong financial definition is omitted; restricted factual projection stays inactive.
- **Actual Chromium journeys:** desktop 1440 × 1000, iPad landscape 1194 × 834, iPad portrait 834 × 1194 and mobile 390 × 844. Each layer's four illustrated selections updates Main. Keyboard/Enter or simulated touch, selected highlight, minimum 44px region targets, all eight SWOT themes, reload, Back/Forward and retained subject context are exercised. Captures wait for visible images and fonts and reject horizontal overflow. Main contains no accordions. Banking's original ecosystem image remains visually distinct. No-JavaScript server fallback exposes all eight themes.
- **Self-contained preview:** embedded images/styles, no asset subrequests, selections, perspective changes, reload and history tested over loopback HTTP. The managed browser blocks `file://` by administrator policy; that policy was not overridden. Download/open is offered for ordinary owner browsers but file-protocol execution has **not** been certified in this environment. Without JavaScript, use the serial server's native-link fallback or the committed screenshots.
- **Protected scope:** [Integrity-Proof.json](Integrity-Proof.json) records the exact changed-file inventory, 51 byte-identical original runtime images, local-link checks, unchanged historical v1 body and exact base-tree restoration using a reverse binary patch in a disposable Git index.
- **Browser provenance:** [Browser-Proof.json](previews/Browser-Proof.json) records capture hashes, tested prototype file hashes and device checks. Screenshots are from actual local baseline/design renderers, not a claim of direct live Render browsing or physical iPad/Safari testing.
- **Hosted status:** the baseline full security/regression run [45255984476](https://github.com/rdidale-jpg/CIOS/actions/runs/45255984476) succeeded at exact main `97d316c`. The existing PR workflows path-filter application/runtime/research changes and do not select this design-only documentation path. No workflow is added just for this phase. Do not describe baseline CI as a new implementation CI run or imply 388 strict security tests were rerun for this documentation-only change. Full implementation security/regression remains mandatory in Phase B.

The original November 23 PDFs and direct live page access were unavailable; the before captures are actual baseline-code renders. These limitations are explicit in the [audit](Audit-and-Lineage.md). Passing checks is not owner visual acceptance.

## Exact rollback

This branch only adds a proposed contract/design folder and a short reconciliation note to the existing v1 contract. The validator constructs its candidate tree in a temporary index and reverses its entire binary diff back to baseline tree **`6c72c645777372e196cbc3c4248f5ec7321cd84e`**. It does not mutate the real index or worktree. Discarding this unmerged design PR leaves application/runtime unchanged; after any separately authorised documentation integration, reverting its documentation commit removes the proposal and previews without data or schema rollback. No Render rollback is needed or authorised for this phase.

## Completion boundary

Phase A delivers the proposed responsibilities, existing-work audit, source-to-view allocation, navigable design, responsive previews, self-critique and owner checklist. **Phase B application implementation, legacy-route adaptation and full operational release validation are not performed.** Owner visual acceptance comes next; no merge or deployment.
