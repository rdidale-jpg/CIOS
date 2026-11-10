# FLORA Visual Intelligence v3 — Commercial Opportunity Discovery

Implements [Issue #552](https://github.com/rdidale-jpg/CIOS/issues/552) over the verified, **unmerged** v2 PR #551 implementation. Exact base: `e03b2fff29a0236d69fad4e522654d3a2a557990`. Main at start: `650b92c377b7295a01cb59deec7195fae21e8a93`. See [architecture/reuse and material trade-offs](Architecture-and-Reuse.md).

## Working flagship journey

1. Open `/industries/banking?lens=commercial` and select **Core platforms**.
2. Open **Lloyds Banking Group commercial intelligence**, preserving the activity fragment.
3. Inspect **Legacy decommissioning and migration benefit assurance** (`RCO-LBG-001`). The hypothesis retains current source context and the competing platform/estate assertions; neither is proof of an unmet buying requirement.
4. Inspect evidence, scope, publication/retrieval dates, counterevidence, inferred stakeholders, supplier/competitive context, unknowns, separate authored assessments and the next customer-validation action.
5. A verified permitted user deliberately chooses **Create or link record → qualification**. Anonymous users get sign-in/workspace guidance; public pages never enumerate private Pipeline records.
6. Existing duplicate handling returns the same workspace record if already captured. A new record starts **Discovered**, with no qualification, unknown amount and no reviewed evidence flag. Complete all ten note/reference inputs, review applicability and explicitly confirm Qualified or a later stage through the existing private form.
7. Open Pipeline, then follow the originating hypothesis/industry links. New captures freeze review/counterevidence references; existing linked records remain untouched.

The inherited Pipeline remains **demonstration-marked**. The increment does not independently validate customer references, certify a revenue forecast or convert public research to accepted Enterprise Evidence. It preserves the existing order: capture/link first, then private qualification. No competing pre-Pipeline draft store was added.

## Visual review

| Experience | Desktop | Tablet/mobile |
| --- | --- | --- |
| Banking commercial overlay | [Map](previews/banking-commercial-desktop.png) | [Tablet](previews/banking-commercial-tablet.png) · [Mobile](previews/banking-commercial-mobile.png) |
| Core Platforms inspection | [Activity](previews/core-platforms-desktop.png) | [Tablet](previews/core-platforms-tablet.png) |
| Lloyds enterprise drill-down | [Enterprise](previews/lloyds-commercial-desktop.png) | [Tablet](previews/lloyds-commercial-tablet.png) |
| Lloyds opportunity hypothesis | [Inspection](previews/lloyds-hypothesis-desktop.png) | [Tablet](previews/lloyds-hypothesis-tablet.png) · [Mobile](previews/lloyds-hypothesis-mobile.png) |
| Counterevidence | [Scope/period conflict](previews/lloyds-counterevidence-desktop.png) | [Tablet](previews/lloyds-counterevidence-tablet.png) |
| Qualification — synthetic only | [Private form](previews/qualification-desktop.png) | [Mobile](previews/qualification-mobile.png) |
| Qualified Pipeline — synthetic only | [Pipeline](previews/pipeline-desktop.png) | [Tablet](previews/pipeline-tablet.png) · [Mobile](previews/pipeline-mobile.png) |
| Aviation compatibility | [easyJet map](previews/aviation-commercial-desktop.png) | [Tablet](previews/aviation-commercial-tablet.png) · [Mobile](previews/aviation-commercial-mobile.png) |

[Before](previews/banking-before.png) / [after](previews/banking-after.png) use matched desktop viewports and public context. Commercial markers count existing hypotheses, not market attractiveness, demand, value or unique additive deals. One hypothesis can appear under several activities; idempotency uses its original identity. Zero context/zero hypotheses is valid, with an explicit research-gap state.

The v2 illustration identity, AI/regulatory lenses and six diagram contracts are preserved. Labels are slightly larger; flow labels have a legibility halo, selected flows identify their conceptual endpoints, and secondary count markers avoid neighbouring participant labels. Coarse-pointer devices automatically expose equivalent 44px text targets. Finite URL fragments restore the selected activity and its inspection panel; they never select a workspace or construct authority. Supporting statements use progressive disclosure while counterevidence remains inspectable. The header offers direct evidence, counterevidence and capture-review links.

## Architecture, evidence and qualification boundaries

`commercial_intelligence` is a read-only presentation projection of existing `commercial_candidates`, capability/programme references, living-map specs and exact source metadata resolved by the v1 projection. Existing `source_quality` additionally excludes index-only, unverified or future-at-cutoff material from source-backed counts. No canonical graph, source store, opportunity model, scoring engine or dependency was introduced.

All nine Lloyds and six easyJet hypotheses retain their IDs, source claims, research history and original ordinal assessments. Research coverage associations are **not confirmed enterprise dependencies**. Current support is shown separately from dated authored ratings; withdrawing support does not silently rewrite the historic score or claim a verified need. Relevance, accessibility, evidence maturity and seller fit (where already assessed) remain separate, with rationale/anchors and no combined win probability.

The inspection answers ten commercial questions using existing problem/outcome, programme signal, proposed service, inferred buying functions, supplier/competitive context, gaps, route-to-market and next-action fields. Unknown budget, verified buyer authority, contract value, tender/procurement date and customer demand stay Unknown. Source retrieval is a provenance-review timestamp, not independent verification of current enterprise operations. Historical supplier evidence does not establish a current contract or incumbent scope. The Lloyds platform statements retain competing periods/denominators and their treatment.

The existing capture producer, workspace/resource evaluator, CSRF envelope, write journal, audit, version checks and qualification state machine remain authoritative. New captures add immutable `provenance.commercial_review` metadata (review/inspection digests, support/counterevidence IDs and activity IDs); no existing record is migrated or backfilled. An older assessment without a matching pinned review retains only its own original capture provenance; a newer review is never attached to it. Source fields cannot be edited through save/capture payloads. The private record view shows the captured boundary and maps back to the public origin. Public views never read workspace Pipeline records or Commercial Mission/employer profiles.

## Validation and review evidence

- **27 new acceptance identities** cover reproducibility, existing identities, Core Platforms/Lloyds mapping, zero/unsupported context, ten questions, provenance/counterevidence, historic suppliers, all lenses/six contracts, no GET mutation or private record enumeration, complete HTTP capture/qualification/link, Aviation capture, unchanged hashes on CSRF/anonymous/scope/role/membership/session/ACL denials, immutable review provenance, safe finite return fragments and unchanged research files.
- **120 existing focused tests passed** across v2 maps, v1 visuals, commercial assessments, sales/Pipeline, multi-industry integration and research contracts.
- [Browser checks](Browser-Checks.json): Chromium desktop 1440 × 1080, tablet 1180 × 820 and mobile 390 × 844; both industries/all four lenses (24 combinations), real source navigation, desktop keyboard and tablet/mobile touch journey, return-to-origin, flow endpoint selection, reduced motion, no-JS fallback, no page overflow and no console errors.
- A disposable HTTPS fixture begins with **zero commercial records**. Only deliberate browser actions create the synthetic `RCO-LBG-001` record, reject incomplete qualification, fill ten explicitly SYNTHETIC references, confirm Qualified and link back to the same ID. No production data/accounts or automatic demo seeding tool is used.
- Print: [commercial map](previews/banking-commercial-print.pdf), [Lloyds inspection](previews/lloyds-hypothesis-print.pdf), [synthetic qualification](previews/qualification-synthetic-print.pdf); source/counterevidence and qualification details are expanded for print and original disclosure state restored. Print/PDF checked separately from browser panning.
- CI policy **25 passed** and actionlint passed. The final local strict gate **passed: 1,140 passed, 57 matched inherited failures and 10 original skips (1,207 identities)**, including **388 security** and **27 new v3** passes. See [test results and the corrected historical-capture regression](Test-Results.md). Only the new 27 expected passing identities are added; every prior identity, inherited signature and skip reason remains unchanged. There is no blanket continue-on-error.

## Stacked CI and integration

PR #551 remains the dependency. The workflow’s existing `pull_request.branches` did not include the v2 branch, so add only **`codex/flora-living-industry-maps-v2`** to trigger this stacked candidate. Path filters, permissions, checkout, test commands, artifact retention and strict comparator are unchanged. No repository rules/settings are modified.

V3 targets the v2 branch initially, giving a v3-only review diff. After a separately authorised #551 merge, retarget v3 to main, verify the effective diff and rerun actual-candidate CI. Neither PR is merged or deployed here.

## Limitations and next step

No new customer research was invented. Buyer authority, budget, access, contract scope and procurement timing remain the customer-validation priorities. The Pipeline’s demonstration designation and completeness-only qualification checks are preserved; a user-entered reference is not independently verified. Exact historical review digests/IDs are frozen, but this increment does not introduce a new archival evidence-store interface.

Physical iPad/Safari and assistive-technology usability remain untested. Human comprehension and commercial outcomes remain **unmeasured**; see the [short comparison protocol](Comprehension-Evaluation.md). Review the owner journey and obtain actual customer evidence before treating any hypothesis as a real pursuit. No merge, deployment, production change or automatic intelligence promotion.
