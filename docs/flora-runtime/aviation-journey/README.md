# Aviation Journey Continuity

Baseline `088275e75365f1f251537d21e2601f10aa8e861a` includes #701. The route decisions follow [the #703 audit](https://github.com/rdidale-jpg/CIOS/blob/187aec220a87a6a8c9618f989794bf1df9a38a13/docs/flora-audits/cross-industry-2026-11-20/Next-Decisions.md).

## Route coverage

| Entry or deep link | Result |
| --- | --- |
| UK Landscape Aviation selection, Industry catalogue and sector catalogue | Existing Aviation Industry destination. |
| Aviation overview and other living-map lenses | Visible header link to the ordinary easyJet path, using the current Industry header. |
| Aviation PESTLE, Five Forces and value chain, and Enterprise catalogue | Existing links to the ordinary easyJet path. |
| `/enterprises/easyjet` | Existing visual renderer opens `AV-ENT-001`, Landscape and Facts, with integrated Economics. HTTP 200 on the established enterprise entry. |
| `/enterprises/easyjet/preview` and its `stream`, `detail`, `reading` selectors | Original server-native links and validation. This is the existing canonical presentation address and all generated stateful URLs continue to use it. |
| `/enterprises/easyjet?lens=operating-model` | Prior default screen, now the detailed operating model linked from Aviation. |
| `?lens=timeline`, `?lens=ecosystem`, `?lens=opportunities`, `?lens=commercial` on the enterprise path | Same specialist dispatcher and access boundaries. |
| `/enterprises/easyjet/understanding`, `/enterprises/easyjet/research-diagnostic`, `/industries/aviation/visual-specs` | Existing dedicated handlers. Landscape links directly to Understanding through Research and evidence. |
| `/flora/aviation/research` and its easyJet, opportunity, source, gap, evidence and candidate destinations | Existing read-only research family. Canonical/Financial-run/Pipeline permissions stay with their current owners. |

## Architecture review

Direct dispatch keeps the ordinary path at HTTP 200, preserves native Back to the discovery page, and shares one identity, renderer and canonical state URL family. It also keeps authorization and storage checks ahead of render. The historical `/preview` spelling remains visible when users select a mode or stage. Renaming it would require a separate alias and query migration with little benefit to this journey.

Aviation retains its current Industry composition. The added CTA prevents a user having to discover the enterprise card inside a disclosure. The fuller operating model is one step back via the Aviation breadcrumb and supporting material. That adds a step for specialist users coming from the modern view, while they can also bookmark their existing exact lens URL.

The Source checker, licensed art, Finance and identity owners are inherited from the merged baseline. No source admissions or legal decisions were made. Lloyds §2 affected output stays inactive and §5 PDF deep links deferred. easyJet research-only revenue and profit remain excluded. The Economics workflow checks its historical exact-cut rollback on the merged A1 snapshot and still runs current-head runtime, security and browser steps on this PR.

## Browser review

| Entry after following Aviation navigation | Desktop | iPad landscape | iPad portrait |
| --- | --- | --- | --- |
| Before | [Desktop](previews/before-desktop.jpg) | [Landscape](previews/before-ipad-landscape.jpg) | [Portrait](previews/before-ipad-portrait.jpg) |
| After | [Desktop](previews/after-desktop.jpg) | [Landscape](previews/after-ipad-landscape.jpg) | [Portrait](previews/after-ipad-portrait.jpg) |
| After, selected Economics stage in Insight | [Desktop](previews/after-economics-insight-desktop.jpg) | [Landscape](previews/after-economics-insight-ipad-landscape.jpg) | [Portrait](previews/after-economics-insight-ipad-portrait.jpg) |

The baseline exposes a visible easyJet link through its PESTLE lens. The candidate exposes one directly in Overview. Chromium iPad dimensions are simulated. Physical hardware, Safari and assistive-technology acceptance remain owner checks. The browser is loopback-only against isolated research and storage fixtures.

## Rollback

Apply the complete reverse binary patch against the candidate in a temporary Git index and compare the resulting tree with the pinned main tree. Reversing this PR requires no migration or data rollback. A future release would need its normal separate approval.

## Reproduce verification

With the repository requirements and Python Playwright installed and Chromium on PATH, run from the candidate checkout:

```sh
python docs/flora-runtime/aviation-journey/browser.py /tmp/aviation-after after
python -m pytest tests/test_flora_multi_industry_integration.py tests/test_flora_aviation_twin.py tests/test_flora_enterprise_economics_a1.py tests/test_flora_experience_684.py -q
python -m pytest tests/test_flora_security*.py -q
python tools/ci/flora_ci.py --output /tmp/aviation-full
```

To reproduce Before, run the same browser script by absolute path from a checkout of the baseline and pass `/tmp/aviation-before before`. The [before report](previews/before-browser.json) and [after report](previews/after-browser.json) bind observations to the captured checkout and runtime file hashes. The PR body records the final head, inventory and validation outcomes.
