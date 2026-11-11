# FLORA Visual-First v2 — owner design checkpoint

Issue: [#558](https://github.com/rdidale-jpg/CIOS/issues/558). Design prototype: [design-prototype.html](design-prototype.html).

## Status
Standalone HTML/CSS/JS **design exploration only**, intentionally **not wired into FLORA routes or production records**. This branch was created from the exact head of **draft PR #557** (`6988ba50d29c1f238293fc7fe110d6182f055e68`). Design-only PR should target that branch, not main, while #557 is unmerged. Do not merge it until the underlying implementation branch is integrated/rebased appropriately.

## Two screen archetypes
1. **Opportunity atlas:** nine existing Lloyds commercial hypotheses in a visual 3×3 decision atlas, each selectable. Clicking changes one contextual inspector; three separately-authored scores stay uncombined. View full evidence remains a deliberate choice.
2. **AI intelligence journey:** five selectable stages (Strategy → Platforms → Workflow → Outcome → Buying gap), representing analytical sequencing, **not proven causal or contractual links**. One contextual inspector holds the explanation and key validation question.

## Design commitments for implementation
- Reuse canonical source-owned evidence, status/scope/period, counterevidence, incumbent/supplier constraints, commercial projection, and authorised Pipeline.
- Design story first, contextual inspection second, full dossier on demand.
- Replace repeating accordion/card content rather than hiding duplicate content without removing duplication.
- Enterprise landscape should ultimately be **data-driven by canonical capability/programme links** and may not invent relationships. Current 3×3 arrangement is a **design device**, not a verified topology.
- AI diagram is intentionally a design schematic. Source/relationship inspection must be made verifiably accurate and truly linked to evidence in the implementation.
- On tablet/mobile the inspector stacks beneath the visual; implementation should make active selection obvious and avoid excessive scrolling.
- Provide accessible alternative summary/list, keyboard interactions, focus labels, touch targets and reduced motion; production no-JS fallback.
- Preserve one-page executive vs full appendix print semantics. The prototype itself is not print/PDF validated.
- Include **dedicated prototype versions for legacy and wallet**, matching evidence and contextual map semantics, in the actual implementation.

## How to review
Download the HTML from GitHub, open locally in a browser, choose **Opportunity landscape** / **AI opportunity**, and click the visual nodes. Note typography, map shape, whitespace, information balance and whether opening a node gives the right decision-making content. GitHub's source preview may not execute scripts.

## Known design-phase limits
- Intentional static sample strings from #557 and owner screenshots, *not live query-driven data*. Formal test results, provenance checks, full accessibility audit, iPad/Safari, actual comprehension and interaction timings **not performed**.
- Ranked atlas arrangement does not yet have rich illustrated iconography or verified programme-to-capability connectors.
- The prototype links to app-relative dossier routes; links only work when deployed under the FLORA application path. Local file review supports the on-page interactions only.
- The nine candidates' identifiers and labels should be rechecked against the canonical projection during implementation; the pilot depiction is not an authoritative entity store.
- No application code, production data, source records, pipeline state or permissions touched.

## Decision checkpoint
Approve/refine two visual metaphors, especially whether the **spatial portfolio atlas** is sufficiently beautiful and useful, versus capability-cluster alternative, before committing to full UI refactor. The final visual standard should match the polished Industry/Enterprise hero treatment and not degrade into merely prettier cards.
