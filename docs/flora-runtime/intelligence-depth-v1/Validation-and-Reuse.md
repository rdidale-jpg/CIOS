# Architecture reuse, validation and product assessment

## Reused ownership

- `Assessment-Overlay.json` is unchanged: original 45 assessment claims, programmes, capabilities, suppliers, nine Lloyds candidates and authored commercial dimensions retain their identities and values. Aviation/easyJet data is unchanged.
- `Understanding-Review.json` owns the four new unaccepted CandidateClaim/SourceSegment observations, exact-support reviews, four excerpt snapshots and one period-bound analytical relationship. Existing fields/records are retained exactly. `understanding.assess`, `primary_text`, canonical graph projection and relationship resolution perform the validation; no parallel graph, source authority or opportunity store is added.
- `commercial_intelligence.commercial_projection` resolves explicit source-owned `hypothesis_ids` only when their `assessment_digest` matches the assessed data. It uses the existing exact evidence catalogue and quality rules. The existing immutable capture mechanism freezes new support references in new captures; duplicate capture and historical snapshots retain prior provenance. Additive source metadata does not change Pipeline schema or require data migration.
- `intelligence_depth.py` is a read-only presentation/inspection module. It reuses the dossier/coverage assessment, the source-owned commercial projection, existing capability IDs and the existing visual glyphs. Its specific investigation questions and arrows are labelled interpretation, not asserted enterprise topology.
- `unified_views` and `commercial_views` provide the context-specific entry points. Original diagrams, public route classification, canonical identities, source limitations, supersession and counterevidence remain.
- The print controller creates a temporary clone of the executive summary only for printing, removes scripts/buttons from that clone, and cleans it up afterwards. Full appendix mode expands native disclosures explicitly. Initial disclosure states are captured before legacy print handlers and restored after those handlers finish. Existing private qualification, CSRF, authorisation, audit and protected transactions are unchanged.

## Local verification

Complete strict gate: `python tools/ci/flora_ci.py --output /workspace/flora-depth-ci-final` — **PASS: 1,182 passed / 57 matched inherited failures / 10 original skips = 1,249 exact identities**. Includes **388 security**, **27 v3**, **22 v3.1**, **29 living maps**, **32 visual intelligence**, **36 enterprise understanding**, **25 Pipeline**, and **20 added Intelligence Depth** passes. **25 CI-policy tests** and actionlint also passed. Focused runs overlap these totals; they are not added again.

The final client-side print-restoration adjustment was additionally checked with the 20-test focused suite and actual Chromium print events/PDF captures for both modes on enterprise and hypothesis pages. All original disclosure states were restored; citations were verified in extracted PDF text. Current-candidate hosted validation is required after publication and is reported in the delivery response with its run/artifact links; local results are not substituted for hosted acceptance.

The inherited failures remain **21 domain +12 financial diagnostics +24 legacy**. Ten retained-artifact skips and every pre-existing baseline identity/signature/reason remain structurally unchanged. The only baseline addition selects the 20 new passing identities in `tests/test_flora_intelligence_depth.py`; no `continue-on-error`, skip or exception expansion is introduced.

New tests cover reproducible/read-only assessments, exact primary passage/date/scope/locator/hash and unaccepted state, the three hypothesis questions/options/unknowns, retained cloud conflict and gaps, framework direction and questions, all 9/6 identities, historical snapshot binding, escaped text, separate cited print modes, forbidden private enumeration from public exploration, immutable fresh-support capture and duplicate prevention with Discovered status.

## Reconciled historical fixture assumptions

The first full run detected two *new test failures* after adding review records. These were diagnosed and corrected without changing production metric validation or weakening negative assertions:

1. `test_unreviewed_or_missing_measurement_does_not_become_zero_or_verified` had selected `observations[-1]`, previously the Bank of England metric. It now resolves the precise `review_source` declared by the metric. It still corrupts that source's locator and strictly requires `value is None` and absence of `3118` from output.
2. `test_history_is_append_only_and_existing_enterprise_visual_profiles_unchanged` had hard-coded exactly one new source and forbidden additional relationships. It now preserves every prior review-list prefix and scalar against integrated main, permits **exactly the four named new sources/four observations/four assertion reviews/one named relationship**, and keeps both original visual profiles byte-identical to the earlier baseline.
3. `test_no_existing_research_history_or_source_identity_is_changed` previously used blanket `git diff --quiet`, which also forbade legitimate new research. It now checks **every prior enterprise-knowledge file**, requiring byte identity for historical snapshots/assets and structural identity for every prior review record/scalar; only appended review-list entries are permitted. No historical source or identity can be overwritten.

The test IDs remain reported and passing in the final gate. None was excluded, retired or added to inherited failures. The original unsafe metric behaviour remains denied. The print defect found by PDF testing was an actual UI issue: full appendix provenance expansion and final disclosure restoration are now verified by browser events, not inferred solely from Python tests.

## Browser, print and safety evidence

Matched baseline/current pages use Chromium at desktop 1440×1080, tablet 1180×820 and mobile 390×844. Enterprise, industry framework, opportunity register and hypothesis screenshots are paired. The three purpose-specific framework investigations have separate previews. Keyboard/touch, reduced-motion, no page-wide overflow, no-JavaScript navigation and Banking/Aviation compatibility passed. Physical iPad/Safari and screen-reader user evaluation remain unperformed.

Four directly opened primary documents produced only short located excerpts. Two publication dates remain unknown; source retrieval is not publication. Company statements are not independent outcome verification. The existing 50%/60% estate/cloud tension is unchanged; no averaging, recency selection or invented supplier currentness occurs.

Disposable HTTPS test instances began empty. Only deliberate authenticated/CSRF-protected user actions captured the three existing hypotheses and linked duplicates. All three remained **Discovered**; no automatic qualification or customer validation occurred. Test identity/workspace and records are explicitly synthetic. No production identities, data, Pipeline records, environment settings, infrastructure, outreach or deployment were changed. No demo seeding tool was run. Session/CSRF values are excluded from committed text and PDF evidence; private screenshot values are synthetic.

## Product assessment and next increment

**Suitable for draft owner evaluation of a bounded Lloyds decision slice.** It is more specific about dated platform context, internal/partner alternatives, acquisition versus integration milestones, missing programme/application evidence and customer-validation questions. The one-page cited export makes executive review practical while retaining the expanded audit appendix.

This is not a complete enterprise inventory, independent supplier/benefit verification, customer-qualified Pipeline or production acceptance. Human comprehension/decision quality and the issue's 2–3 minute goal remain unmeasured. Navigation instrumentation verifies direct entry paths but does not demonstrate reduced total task clicks. Four added source records increase distinct document URLs only **26→27**, not four independent corroborating documents.

Next bounded work: obtain dated application/retirement inventory and dependency ownership; verify Curve closing/product milestones and current delivery boundaries; establish net-benefit baselines and controls for one AI workflow; then seek authorised customer evidence of unmet external delivery need, accountable buyer and procurement route. Preserve unqualified research status until the existing controls and explicit user confirmation permit progression. No external outreach or deployment is authorised by this PR.
