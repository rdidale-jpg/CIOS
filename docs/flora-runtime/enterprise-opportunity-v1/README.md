# Enterprise-to-Opportunity Integration v1 — working UI iteration

**Draft:** [PR #561](https://github.com/rdidale-jpg/CIOS/pull/561) · **Issue:** [#560](https://github.com/rdidale-jpg/CIOS/issues/560) · **Design work:** [#558](https://github.com/rdidale-jpg/CIOS/issues/558)

## What is wired in application routes
- `/enterprises/lloyds` (existing operating model) keeps the original Enterprise Twin illustrated story and adds a selectable capability-to-commercial-hypothesis overlay immediately following it.
- `/enterprises/lloyds?lens=opportunities` presents the overlay as its principal visual inspection.
- Three public hypothesis pages (`RCO-LBG-001`, `RCO-LBG-002`, `RCO-LBG-009`) present a visual four-stage commercial story, eight pursuit-development modules, and **one top-level Full research & evidence disclosure** containing all original dimension cards, supporting and counter-evidence and source limitations. The existing deliberate, authorised Pipeline capture is **outside** the folded research area and remains unchanged.
- All visual links use source-owned commercial projection IDs. Each node is labelled as **research capability association, not a verified reporting line**. Business owner, buying authority, funding and procurement remain unknown.

## Explicit boundaries
- **No new database, schema or private Pipeline mutations.** Read-only public templates; no automated opportunity record creation.
- Source claims retain their original URLs/locators, historical support, counterevidence and print controls. Research visibility is changed, not underlying evidence or status.
- This is an incremental interaction upgrade, **not a completed high-fidelity redesign**. Canonical capability groups do not prove organisational unit ownership. Physical testing and user timing are pending.
- Current work is stacked on unmerged draft PR #557. Separate design-only PR #559 is reference material and is not secretly merged into this implementation.

## Test plan
- Run `pytest -q tests/test_flora_enterprise_opportunity_integration.py` and existing strict inherited-gate suite; report results, do not infer success from added test code.
- Browser inspect page for each of three hypotheses and Lloyds operating model/opportunities, with no-JS, keyboard/touch, Safari/tablet/mobile, print executive and appendix.
- Verify all nine Lloyds hypotheses remain discoverable through the enterprise and original opportunities routes, whether or not a canonical capability association exists.
- Verify the legacy dossier starts collapsed but remains complete and that capture/qualification controls are visible and authorised.
- Verify that no private store enumeration occurs on public research routes; all immutable capture provenance stays unchanged.

## Remaining design work
- Richer capability map artwork, contextual overlays directly on illustration nodes, enterprise-specific organisation ownership with proof status, accessible visual selection, detailed evidence panel, comprehensive stakeholder/competitor visual modules.
- Full de-duplication of repeated content within the deliberately accessible long research appendix.
- Real read/write opportunity development **only after** the existing Pipeline schema, access, audit and progression gates are reviewed. Do not fabricate an independent commercial store.

## Unverified at publication
This document does **not** claim passing CI, 20-second user comprehension, screen-reader audit, physical iPad/Safari or exact print equivalence. These remain outstanding pending recorded evidence.
