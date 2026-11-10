# FLORA v3.1 — commercial usability and evidence maturity

Implements [Issue #554](https://github.com/rdidale-jpg/CIOS/issues/554) as a v3.1-only stacked change above [draft #553](https://github.com/rdidale-jpg/CIOS/pull/553). Verified source: `f8b0dcb422f9ba51c5c54b800ec344bb3b2f36e6`. The upstream [draft #551](https://github.com/rdidale-jpg/CIOS/pull/551) remains intact at `e03b2fff29a0236d69fad4e522654d3a2a557990`.

## Product walkthrough

1. Open `/industries/banking?lens=commercial`. The illustrated system stays the default view. Expand **Find a hypothesis** for a compact, optional list in existing research order, with enterprise, source-context maturity, mapped activities and an actual next commercial action. Counts remain non-additive research hypotheses.
2. Select **Core platforms** in the list. The map highlights and pans to the activity. Desktop/tablet selection focuses the visible SVG activity. The existing v2 layout intentionally replaces the illustrated map with text navigation below 600px; list selection on narrow mobile therefore focuses the matching native activity inspector. A labelled HTML map region is a fallback when a visible SVG link cannot take focus. The live selection message names the activity. The native inspector remains available below.
3. Follow **Lloyds commercial intelligence** → the existing `RCO-LBG-001`. Or use the list's direct inspection action. The executive decision brief states problem, why now, potential service, evidence state, buyer access and next action. Unknown buyer/budget/timing remain explicit.
4. Inspect **counterevidence**. Conflicting findings are called out in the brief, and the full counterevidence panel is outside collapsed investigative detail. Source periods, entity scope and platform-claim disagreements remain separate. Expand the two investigative disclosures for all ten dimensions, complete supporting statements, gaps and separate ratings. The original dossier remains available.
5. With an authorised session/workspace, deliberately **Create or link record → qualification**. It starts at Discovered; repeat capture returns the original record and immutable provenance.
6. The private record shows **saved evidence maturity separately from Pipeline stage**. Complete/review inputs and explicitly confirm a stage change using the existing gates. A rejected submission does not alter storage or the saved maturity display. Return to **Pipeline**, where the register appears earlier; filters and value discipline are available in a disclosure. Records show stage, internal maturity, owner, stated value/Unknown, next action, last recorded activity and update time. Demonstration labels remain.
7. Repeat from `/industries/aviation?lens=commercial` → easyJet → an existing hypothesis. All six easyJet and nine Lloyds candidate identities remain; no hypotheses or customer records are automatically created.

## Evidence maturity: deliberately bounded semantics

The ten existing note/reference gates reject empty and Unknown/TBC-style placeholders; they do not verify the truth, authority or existence of a reference. Existing `evidence_reviewed` is an internal applicability attestation. Existing advanced stages require all ten inputs, review and explicit confirmation; closing additionally needs outcome evidence. Capture is idempotent and starts at Discovered. These rules, permission checks, CSRF, version checks, audit and transactions are unchanged.

`evidence_maturity(record)` is a pure, read-only view of the saved authorised record:

| Dimension | Meaning in this increment |
| --- | --- |
| Research hypothesis | Inputs incomplete or not internally reviewed |
| Research-qualified · internal review only | All ten note/reference pairs supplied and boolean review saved; input completeness, not factual verification |
| Customer-validated · not established | Free text, reference labels, confidence and Pipeline stage cannot establish verified buyer authority, budget or customer demand |
| Pursuit-qualified · not established | An advanced Pipeline stage alone cannot establish a customer-validated, accessible pursuit |

There is **no new persisted maturity field or schema version**, hence no migration, backfill or provenance rewrite. Old records render using their existing fields; a pre-existing Qualified record with missing inputs remains evidence-incomplete. Forged maturity fields are rejected by the unchanged service/form allowlists. Unsaved restored forms do not drive saved maturity. This increment does not add an attestation or independent verification workflow; durable customer validation will require an explicitly scoped future change reusing canonical Evidence/Observation and recorded authority. No claim that customer demand has been independently verified is made.

## Architecture reused

- `commercial_intelligence`: unchanged public projection, candidate identities, exact source resolver, source quality and reviewed counterevidence.
- `commercial_views`: executive summary and native progressive disclosure over the same projection. No public private-store lookup or write.
- `living_map`: optional native list and finite map-selection interaction. Original v2 illustration assets, nodes, conceptual flows and lenses retained. No permanent overlay, new graph or competing research representation.
- `sales_pipeline`: only a derived evidence-maturity function added. Capture/update/store/stage machine and all authority enforcement unchanged.
- `sales_views`: smaller Pipeline header, collapsible filters, existing verified fields and explicit saved evidence status. Existing list/board and qualification forms remain.
- CI: adds only the exact stacked PR base `codex/flora-commercial-visual-intelligence-v3` to branch eligibility. All execution, permissions, strict comparison and artifacts preserved. Baseline adds 22 passing test identities; every prior profile, identity, failure signature and skip reason is unchanged.

## Visual evidence

Matched viewports are desktop **1440×1080**, tablet **1180×820**, mobile **390×844**. Before uses unchanged v3 code; after uses this implementation. Private comparison instances contain the same single deliberately captured synthetic hypothesis at Qualified, with explicitly synthetic/unverified inputs. Dates/record IDs are disposable; no production identity or customer evidence is shown.

| Experience | Desktop before / after | Tablet before / after | Mobile before / after |
| --- | --- | --- | --- |
| Banking map | [Before](previews/banking-before-desktop.png) / [After](previews/banking-after-desktop.png) | [Before](previews/banking-before-tablet.png) / [After](previews/banking-after-tablet.png) | [Before](previews/banking-before-mobile.png) / [After](previews/banking-after-mobile.png) |
| Aviation map | [Before](previews/aviation-before-desktop.png) / [After](previews/aviation-after-desktop.png) | [Before](previews/aviation-before-tablet.png) / [After](previews/aviation-after-tablet.png) | [Before](previews/aviation-before-mobile.png) / [After](previews/aviation-after-mobile.png) |
| Lloyds inspection | [Before](previews/lloyds-before-desktop.png) / [After](previews/lloyds-after-desktop.png) | [Before](previews/lloyds-before-tablet.png) / [After](previews/lloyds-after-tablet.png) | [Before](previews/lloyds-before-mobile.png) / [After](previews/lloyds-after-mobile.png) |
| Pipeline | [Before](previews/pipeline-before-desktop.png) / [After](previews/pipeline-after-desktop.png) | [Before](previews/pipeline-before-tablet.png) / [After](previews/pipeline-after-tablet.png) | [Before](previews/pipeline-before-mobile.png) / [After](previews/pipeline-after-mobile.png) |

Additional previews: [Banking list](previews/banking-list-desktop.png), [tablet list](previews/banking-list-tablet.png), [mobile list](previews/banking-list-mobile.png), [Aviation list](previews/aviation-list-tablet.png), [Lloyds decision brief](previews/lloyds-summary-desktop.png), [mobile brief](previews/lloyds-summary-mobile.png), [saved evidence maturity](previews/evidence-maturity-tablet.png), [mobile maturity](previews/evidence-maturity-mobile.png), [synthetic zero-evidence state](previews/zero-evidence-mobile.png).

Print: [map](previews/map-print.pdf), [hypothesis](previews/hypothesis-print.pdf), [synthetic qualification](previews/qualification-print.pdf). Print expands disclosures and restores their exact prior states. Files contain synthetic qualification inputs and public repository research, not customer records.

## Product trade-offs and limitations

- The compact list expands in document flow and can be long, particularly on mobile. It is optional and closed initially; it never permanently obscures the illustrated map or traps scrolling. Research order is not a new ranking.
- The decision brief abbreviates long text; full dimensions, exact source passages, conflicting findings and the original dossier remain inspectable. Source support is not verified external supplier demand.
- The smaller Pipeline header makes the register substantially earlier. Filters are collapsed until requested, or automatically opened when filters/errors apply. Value-basis cautions remain beside filters.
- Customer/pursuit verification intentionally remains unestablished. Stronger maturity is not manufactured from reference presence, high confidence or a user-selected stage. Existing Pipeline demonstration status and historical research limitations remain.
- Chromium keyboard/touch emulation, reduced motion, native no-JS disclosures and PDF output are engineering checks. Physical iPad/Safari, screen-reader user testing, sales-director comprehension and commercial outcomes remain unmeasured.
- No source enrichment, customer buyer/budget/tender claims, Pipeline seeding, production changes, merge or deployment is included.

## Integration boundary

This draft targets **`codex/flora-commercial-visual-intelligence-v3`**, not main. Keep #553 → #551 dependency intact. After upstream integration, reconcile effective diffs and rerun actual-candidate hosted validation before any separately authorised merge. See [validation evidence](Validation.md) and [browser measurements](Browser-Checks.json).
