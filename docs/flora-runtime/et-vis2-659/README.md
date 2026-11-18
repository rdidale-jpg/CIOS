# ET-VIS-2 · easyJet interactive Enterprise Twin preview

Owner review candidate for [Issue #659](https://github.com/rdidale-jpg/CIOS/issues/659). **Bounded interaction prototype, not a complete or current operational digital twin. No merge or deployment authorised.**

Base is verified main `fbac4c37910ed07b2baa516e1a5c8d7f329086de`. Main full validation [44174841384](https://github.com/rdidale-jpg/CIOS/actions/runs/44174841384) succeeded on that exact SHA. INT-MAP-1 #657 remains a separate draft; ET-VIS-1 #658 is design-only. Neither is an implementation dependency. No pending branch was merged or modified.

## Try the running prototype

Run the existing FLORA application locally with an **isolated development data directory**, then open:

`/enterprises/easyjet/preview?stream=landscape&capability=fleet-operations`

1. Fleet Operations explains aircraft readiness, utilisation mechanisms, crew/maintenance coordination and the dated fleet snapshot.
2. Select **Network Planning** in Left. Main changes to route/capacity choices, demand, seasonality and schedule economics. The operating picture stays in place.
3. Switch **Forces**, then **What's changing?**. Selection stays on Network Planning. Announcements are explicitly company or adjacent channel context, not proof of a planning change.
4. Browser Back/Forward, reload or paste the URL. Capability and mode restore together.
5. On mobile, open **Explore the operating system**, select a capability, and Main comes into view. Without JavaScript, the same links perform ordinary read-only GET navigation.
6. Customer Service provides an additional differentiated capability. Global Explore retains the existing product/account destinations.

The original `/enterprises/easyjet` remains unchanged. Preview is deliberately not a new default or a link silently inserted into the accepted seven scenes.

## Review pack

- [Actual before/after browser previews](Previews.md)
- [Architecture and UX assessment](Architecture-and-UX.md)
- [Machine-readable source-to-content lineage](Content-Lineage.json)
- [Source use, evidence boundaries and remaining gaps](Source-Review.md)
- [Validation, independent critiques and reproduction](Validation-and-Review.md)
- [Exact predecessor dispatcher evolution](Owner-Evolution.json)
- [Unchanged original/source/security inputs](Retained-Inputs.json)

## Owner acceptance

- [ ] Fleet → Network is commercially meaningful and easy to understand.
- [ ] Capability selection and modes feel coherent on desktop and both iPad orientations.
- [ ] Mobile scene selection reveals Main; keyboard and enlarged text remain usable.
- [ ] Historical counts are clearly dated, not presented as today's operating measures.
- [ ] Conceptual activities, capabilities and dependencies are distinguishable from company disclosures.
- [ ] Adjacent commercial announcements are not mistaken for a verified capability change.
- [ ] Accept or request refinement of the **new additive vector illustration**. Independent visual review found it flatter than the rich original FLORA scenes; equal artistic quality is **not claimed**.
- [ ] Accept the bounded prototype architecture; approve any later expansion separately.

## Rollback

Before merge, close this draft or abandon the branch: production is unchanged. If later integrated under separate approval, revert the ET-VIS-2 integration commit as a unit, including its finite route/assets, dispatcher additions, tests, workflow and predecessor compatibility adapter. Original easyJet/Aviation/Banking/Lloyds routes, all research records and original artwork are unchanged; there is no migration, data cleanup, authority reset or source rollback. Run the full gate after any future revert. No Render action is part of this sprint.
