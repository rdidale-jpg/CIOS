# Architecture and preflight

## Verified starting point

| Check | Result |
|---|---|
| Current main at branch creation | `8a53777d1dec359f56b66e533d512c0a86881939` |
| Exact full main post-merge CI | [43709888042](https://github.com/rdidale-jpg/CIOS/actions/runs/43709888042), success |
| Accepted design | #631, `f4059a34a55277adbd2a2337239827cab96d962e` |
| Owner decision | [comment 6896760263](https://github.com/rdidale-jpg/CIOS/pull/631#issuecomment-6896760263), separate implementation only |
| Branch origin | New `codex/flora-vp2-632` from validated main, not from a design/research branch |
| Running production version | **Unverified**: public deployment/health reads failed; no authenticated Render read service is available. Main and CI are not evidence of the deployed SHA. |
| Production operations | None; no Render configuration, deployment, production data or canonical record changes |

The current route handlers, source adapters, asset catalogues, accepted ADRs and existing main application were inspected before implementation. ADR-002/005/009/010/012–016/024/026 ownership and admission boundaries remain. No architectural exception or source-admission decision is introduced.

## Integration inventory

| Work | Current integration position | VP-2 treatment |
|---|---|---|
| #613 VEX-1 | Merged; scope, stream, geometry, assets and URL contracts in main | Reused; all historical assets and active addresses preserved |
| #627 INT-1 | Merged into main at `8a53777…`; permitted read-only semantics/agenda | Reused, with conservative negative metadata guards |
| #616 SI-1 | Draft; selected Option A functionality already live through #627 | Existing owner only; no wholesale design merge |
| #624 ISP-1 | Draft; selected presentation policy already live through #627 | Existing six-type policy only |
| #618 / #620 / #622 | Draft research / consolidation | No merge, import, new claims or acceptance |
| #628 / #630 EAI-1 | Separate issue and draft; #630 head `678412a4320b5d13d88ffe66592e7a225cc4817c` | No code, source decision, evidence package or research copied |
| #631 VP-1 | Accepted design, still draft/unmerged | Only the exact approved 23 delivery assets selectively copied; no static facts, clock override or prototype HTML |
| #603 Owner Assurance | Draft `fc565bda6004c8ba5cd832a837ab7c116a85fc61`, not fully merged | Current main's verified-owner/account inspection preserved; do not claim the whole draft Command Centre is live |
| #609 / #610 | Draft historical visual designs | Untouched |
| #614 News / #626 Banking research | Separate future work / candidate research | No runtime News/Tools/Topic Cards controls or research integration |

Other open strategy/research/design branches (#559, #563, #568, #569, #589, #590, #596) are unchanged. This sprint does not close, merge, retarget or delete any existing PR or branch.

## Runtime composition

`web.app → existing public_routes → visual_streams.resolve(Context) → visual_panels.render`

The new module is a pure HTML presentation adapter. Existing `Context`, query whitelist, `url`, subject geometry, identity, permitted source adapters, claim/force views and Leadership Agenda remain owners. It neither persists data nor loads private enterprise models. The existing header supplies real navigation, workspace/account controls and CSRF-protected actions; role identity is derived from verified authority, never a prototype label or caller-supplied role header.

Top is the single header; the existing compact header can render an embedded inner container. Left is a single aside with mutually exclusive wide/compact scene subtrees. Main is a single main landmark. A conditional existing pilot notice is inserted within Top. The product menu expands Top rather than creating a fourth floating application region. Other application journeys keep their default header behaviour.

Desktop and iPad landscape expose all three panels. iPad portrait/mobile use native, initially closed Left disclosure; Main has reading priority. Supplementary labels remain under native **Explore deeper** / **All 20 industries**. The 20 industry section names remain original, with exactly three researched exits (Banking, Technology, Aviation), not an implication that whole sections have complete research.

## Interaction and feature preservation

| Scene | Existing labels | Active destinations |
|---|---:|---:|
| UK Landscape | 20 | 3 |
| UK Forces | 4 | 4 |
| Banking Landscape | 9 | 9 |
| Banking Forces | 4 | 4 |
| Lloyds Inside | 5 | 5 |
| Lloyds Landscape | 5 | 3 |
| Lloyds Forces | 4 | 4 |
| **Total** | **51** | **32** |

[Retained-Destinations.json](Retained-Destinations.json) is the per-label baseline map, including inert subjects. Banking's five bank exits, BoE/PRA/FCA/payments, six existing agenda keys, all three context layers, parent returns, selected detail close/Escape and canonical routes remain. Technology/Aviation retain their existing experiences; VP-2 does not pretend they have Banking's seven new views.

Native anchors retain history and deep links without JavaScript. Switching streams keeps country, subject, layer, selected company and agenda. A compatible topic maps to the equivalent existing subject (for example technology ↔ platform/control pressures). An incompatible detail clears rather than presenting a different claim with the same incidental ID. Regulatory/supplier context retains the original owner rules and gains visible border emphasis and an accessible explanation; supplementary matching subjects open their disclosure.

## Intelligence and source semantics

The six existing types remain **Reported / Calculated / Estimated / Working assumption / FLORA Insight / Hypothesis**. Type, evidence quality and canonical acceptance are separate. Calculating does not upgrade an assumption into a fact. The runtime displays only values supplied by the already permitted owner, without forcing an example of each type onto every page.

The UK national measures retain year, basic-price scope and separate real-growth period. Finance & insurance share explicitly includes more than Banking; it is not a Banking TAM. Lloyds deposits and profit retain entity, unit, accounting definition and different reporting periods. The deposit change is not organic net flow; the 2030 efficiency ambition is a target. Original material caveats, counter-evidence and understandable source access remain.

The design's illustrative £212bn estimate, conditional range, AI hypothesis, static `SourceData` and snapshot-date override are **not imported**. No SEC/H1 financial bridge, new ONS admission rule, EAI candidate, invented demand or new source is introduced. Public UK economy output must match the existing pinned owner basis. Supplier statements retain the existing verified-relationship gate. Explicit owner-only, withdrawn/retracted, denied/revoked/unknown rights, stale/superseded or core-contradictory source metadata is rejected before claim projection; that negative guard grants no positive source permission. Whole explicitly private research releases are withheld. Source reporting periods use actual source periods/publication context, not the research review date.

There are no new intelligence stores, matchers, agendas, Pipeline services, approvals, paid calls or autonomous research. Leadership Agenda remains the existing read-only owner with the real clock and expiry policy. Existing public content can therefore disappear when stale, revoked or unsupported; VP-2 does not freeze acceptance screenshots as perpetual facts.

## Artwork and delivery

Seven historical originals and all 21 original runtime variants remain exact. The accepted design contributes fourteen portrait WebPs (384/768 widths), two skyline WebPs and seven decorative SVG watermarks. The 23 files total **3,743,905 bytes**; 384 portraits are 88,324–125,396 bytes and 768 portraits 321,434–440,682 bytes. No art generation or image-edit call occurred in VP-2.

[Accepted-Asset-Import.json](Accepted-Asset-Import.json) records exact design paths, byte sizes and SHA-256s. Public assets use the existing finite route catalogue, content-addressed URLs, symlink/path validation and digest checks. No arbitrary SVG/file route is exposed. Existing originals remain addressable. PNG master duplicates and prototype/generated pages are excluded. WebP responses retain immutable ETags; HTML/account pages remain no-store. Responsive srcset, native lazy loading, async decoding, and deferred collapsed Left avoid forcing portrait loads before mobile reading. Illustrations are decorative to the accessible labelled navigation; they do not assert premises, systems topology, legal boundaries or quantified pressure.
