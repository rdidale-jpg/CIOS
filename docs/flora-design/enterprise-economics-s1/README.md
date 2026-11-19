# Enterprise Economics — Sprint 1 design for owner acceptance

**Status:** Proposed UX/architecture design. **Design only; no runtime, Source permission, canonical or production change.**

Verified main/base: **03719d7573f087c65d9622719273aa4b89caf7d3**. Its full main CI [44548522149](https://github.com/rdidale-jpg/CIOS/actions/runs/44548522149) succeeded before branching. PR #631 remains an unmerged, visually accepted design reference at **f4059a34a55277adbd2a2337239827cab96d962e**; its Top/Left/Main assets are already implemented in main through VP-2. PR #698's accepted policy is merged as **56965a381caf7adbb9e81b90e121051735c303b9**. PR #699 is merged into this base; the Lloyds §2 hold and §5 link deferral are still active.

## Recommendation

**Choose A: Economics as a Landscape component.** Extend the existing Funding / Lending & income / Profit & costs composition into a single, selectable economic story. Use the same Source-owned eligible inputs, Financial calculation recipes and Facts/FLORA Insight modes. Economics is a subject in Landscape, not another global destination or primary perspective. Inside and Forces provide contextual continuations, not duplicate financial dashboards.

The static prototype is [prototype/index.html](prototype/index.html). GitHub displays HTML source; it does not host this as an application. Download the design artifact, unzip it and open `prototype/index.html` with its assets alongside. Or serve the repository locally:

```bash
python -m http.server 8765 --bind 127.0.0.1
# Open http://127.0.0.1:8765/docs/flora-design/enterprise-economics-s1/prototype/index.html
```

No server-side FLORA runtime, identity provider, Financial run, private store or network research is used by the prototype. Offers/Pipeline labels are contextual references, not private controls. The separate review index is a design artifact; product views retain exactly Top, Left and Main.

## Three differentiated options

| Option | Where / interaction | Commercial usefulness | Simplicity | Visual impact | Architectural fit | Subsequent effort |
|---|---|---|---|---|---|---|
| **A — the economic story** | Select the existing economic component in Landscape; click an economic stage to update Main detail | High: quickly distinguishes money in, delivery and retained return | **Highest**: no new mode or lens state | High: memorable three-stage mechanism with restrained measured context | **Direct**: existing Landscape, Source, Financial and reading-mode owners | Lowest: one read-only composition and source adapters; eligibility remains necessary |
| **B — economics in the work** | Inside; a capability remains selected while economic mechanisms sit along the activity spine | High for operational investigation; less direct for an executive financial overview | Medium: activities, capability and Group context must remain distinct | Medium/high: clear connection between work and economics | Reuses Inside/capability ownership, but needs genuine capability-to-outcome relationships for greater depth | Medium: relationship evidence, semantic selection and no invented allocation |
| **C — contextual economic overlay** | Main-only lens on the current business context; one local show/hide action | Useful for contextual exploration; less obvious as the default economic story | Lowest of the three: extra overlay state and visibility decisions | Highest initial impact; greatest risk of visual crowding | Possible as a view over existing owners under ADR-013; no new intelligence object | Highest: context/lens state, touch targets, overlap, history and accessibility |

These are design judgements, not measured user-research scores. All options keep the accepted shell, same enterprise and reporting perimeter, Facts by default, explicit Insight, optional inspection and no automatic commercial promotion. The option chooser exists only on the review index; it is not a proposed FLORA global toggle.

## Walkthrough

1. Open the review index; compare A, B and C for Lloyds and easyJet. No additional country or industry journey is claimed by this bounded study.
2. In **A**, select a stage in the economic mechanism. Facts explains the selected subject; FLORA Insight gives conditional interpretation of that same subject. Back/Forward and reload preserve enterprise, option, subject, view and mode.
3. In **B**, the selected capability is Risk assessment or Network Planning. The activity spine is explicitly illustrative, not a verified organisation chart. easyJet's Group figures remain separate from capability economics.
4. In **C**, hide/show the economic drivers inside Main. The global perspective, subject and country stay unchanged. The orbit is a conceptual layout, not a measured flow or supplier graph.
5. Open **Source & basis**, inspect source/period/perimeter/APM/calculation limits, then close with Escape. Focus returns to the invoking control. Lloyds inspection contains no financial figures or PDF link.
6. Follow **Related forces** and **Leadership context**; return to economics. These are navigable design views. They are not actual qualified Material Pressures, named buying groups or a second Leadership Agenda engine.
7. Repeat at desktop 1440×1000, iPad landscape 1194×834 and portrait 834×1194. Portrait collapses Left; reopening it retains context. Browser checks also cover mobile and 200% text.

## Reading the financial example

easyJet is an existing Aviation Enterprise candidate (`AV-ENT-001`), not a new canonical identity. Its original FY2025 annual report was rechecked on 19 November 2026. Only three bare financial values are retained for this design: Group revenue £10,106m in FY2025, the £9,309m FY2024 comparator and FY2025 headline pretax profit £665m. [Original issuer report, printed p32](https://s203.q4cdn.com/522538739/files/doc_financials/2025/ar/easyJetARA25_DIGITAL_sm.pdf).

Revenue growth is **Calculated**, `(10,106−9,309)/9,309×100 = 8.56%`, retaining input rounding. The prototype uses a zero-based revenue comparison; headline PBT stays separate. It is not a statutory profit, operating margin, cash-flow reconciliation, cost residual or capability return. No Headline-PBT/revenue ratio is introduced: the existing bounded Financial engine supports difference/percent-change and signed bridges, not a generic ratio recipe. The validator reproduces growth using that existing owner rather than proposing another financial engine.

**Lloyds has no financial values in this design.** Its banking mechanism is explicitly illustrative. The §2-restricted three-measure slice is not called, copied, activated or used to derive an inference. §5 PDF links stay deferred; only the homepage is linked. No bank-specific funding mix, margin sensitivity, allocation or buying intent is invented. See [Content and lineage](Content-and-Lineage.md).

## Previews and validation

[Preview index](Previews.md) contains the desktop/iPad Facts and Insight renders for all six option/enterprise combinations, comparison boards and inspection/related-view examples. Source artwork is copied byte-for-byte; [Artwork-Provenance.json](Artwork-Provenance.json) records originals and hashes. No accepted illustration is replaced or edited.

Reproduce from the repository root:

```bash
python docs/flora-design/enterprise-economics-s1/validate.py
python docs/flora-design/enterprise-economics-s1/preview.py --output /tmp/flora-economics-design
```

The design assurance workflow validates exact-head scope/content/contracts and browser interactions, then publishes a downloadable prototype, fresh screenshots and sanitized proof. Actual counts and final SHA belong to the PR's final validation record. Full production regression is not claimed merely because static design checks pass; the verified baseline's security/regression remains unchanged. See [Architecture and next sprint](Architecture-and-Next-Sprint.md) and [Self-critique](Self-Critique.md).

## Owner acceptance checklist

- [ ] Select A, B or C based on the actual desktop/iPad previews, not just the written assessment.
- [ ] Accept the industry-specific financial story and restrained visual language.
- [ ] Confirm Facts/Insight, optional inspection and related-view navigation are understandable.
- [ ] Confirm illustrative banking mechanics and Group-versus-capability boundaries are unmistakable.
- [ ] Accept A's incorporation of Lending & income and the single Financial-owner presentation path.
- [ ] Review source-use/financial availability requirements for a subsequent implementation.
- [ ] Keep Lloyds §2/§5 restrictions and existing canonical/Material Pressure/Opportunity gates intact.

**Stop before implementation, merge or deployment.** No new ADR acceptance, approval registry, permission, canonical record or production action is performed. Rollback is removal of this additive design directory and its design-only assurance workflow; no data migration or authority-store operation exists.
