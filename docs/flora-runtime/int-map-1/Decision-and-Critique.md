# Decision options, staged roadmap and critical challenge

**Independent review status:** This is a multi-perspective critical assessment by the author, **not** a completed independent Chief Architect or separate executive/designer review. The decision remains provisional until owner review, and any separate specialist review required by the commission is **outstanding**. Do not claim approvals from simulations or agents that were not actually run.

## Alternative architectures

| Question | A — Existing-owner recomposition (recommended) | B — Generalised persistent change graph (defer) |
| --- | --- | --- |
| Primary design | Reuse Source/Research events, Financial records, industry and enterprise overlays, existing relationship semantics, finite editorial adapter | New cross-domain event/impact lifecycle with persistent graph-like relationships |
| Writing | **None for first proof**; read-only calculated change views over permitted existing facts | Requires new ownership/schema/migration and evidence-to-event transactional persistence |
| Ripple semantics | Supported association vs contextual reassessment, source-key invalidation; canonical pressure stays separate | General graph propagation, risk of automatic/inaccurate inherited enterprise applicability |
| UX | Small Change pulse or third toggle in existing Top/Left/Main | Broad dashboard/cross-vertical change cockpit |
| Advantages | Lower risk, fast visible benefit, fewer approval paths | Potential large-scale reuse after event/data volume justifies it |
| Principal risks | Over-specialising to three Banking stories; hard-coded map; no ongoing refresh | Duplicated stores, incorrect causality, heavier operational/support burden |
| Release requirement | Real permissible sources, source revision suppression, exact entity/date mapping and clean responsive previews | New domain contract, security/canonical reconciliation, migrations, sustained usage evidence |
| Decision | Choose and test Option A first | Revisit only after measuring A's real limitations |

## Proposed incremental roadmap (not authorised yet)

**INT-1 — Model-connected editorial proof (small implementation).** Demonstrate 2–3 current, permitted change stories in a bounded non-production `What's changing` design preview. Use real source IDs and one source→event→industry association→optional enterprise consequence; respect legal/entity applicability. Compare Change pulse versus third toggle with iPad/desktop/mobile and user experience. Test source retraction, time correction and isolation. No fresh autonomous agent or canonical write.

**INT-2 — Reusable researched event registration.** Only if INT-1 proves visual value, let existing Source/Research ownership expose a tested, reusable *read-only* news/event selector and change classification; existing BIE2 event candidates must be revalidated for use and dates. Show the current period with dated boundaries. Retain no public third-party article text. **Do not** build a scraper or schedule under this sprint.

**INT-3 — Bidirectional synthesis.** Derive enterprise→industry candidates from independent peer evidence and downward contextual applicability from UK forces to appropriate industry/enterprise capabilities. Tie into existing PESTLE/Porter/value chain/operating mechanisms; qualified pressure/opportunities stay separately controlled. Introduce only necessary index/refresh support shown by real latency/freshness measurements.

**INT-4 — Research operations / living refresh.** Explicitly authorise periodic monitoring/refresh only after reliable source/use/time semantics, host/network cost, roles, alert thresholds and historical versioning are demonstrated. Factual research default for views, governance for real exceptions/canonical writes.

## Architecture critique

- **Challenge 1: A third toggle could be cosmetic.** Four current Forces stories are mostly a dated editorial list. Renaming it “What’s changing” would not create ripple-through. Require an actual change delta, resolved subjects, directional association and invalidation proof before declaring capability.
- **Challenge 2: Do not turn data layers into independent truth stores.** `Assessment-Overlay.json`, BIE-2 news, public Financial Source bundles and Enterprise Models can contain overlapping statements. A new writeable industry event database duplicates owner revisions. Reuse existing stable identities and only compose projections.
- **Challenge 3: What is an industry pattern?** Multiple banks discussing AI is insufficient unless comparison is meaningful, independently supported and temporally aligned. Mechanisms and business models matter, not a count of headlines.
- **Challenge 4: What is actually “new”?** An article published today may discuss an old change; a prospective legal effective date differs from an announced plan. Changing source vintage should cause revision, not silent overwrite.
- **Challenge 5: Prevent UK force overreach.** CTP designation of technology providers is not universal bank-provider contracting. Industry context is useful before an enterprise applicability test, but cannot be a qualified enterprise pressure.
- **Challenge 6: Preserve commercial specificity.** When an enterprise is truly exposed, explain relevant capability, accountable role (if evidenced), consequence, current internal response and an investigable next step. Do not invent procurement/funding/urgency.
- **Challenge 7: Don't let permissions dictate the public view.** Working, lawfully usable research can appear without individual canonical promotion, while protected/private records stay protected. Separate marketing polish from robust provenance underneath.

## Commercial executive challenge

A salesperson should get an answer to: *which enterprise is changing, what's materially different, why now, which operational or economic mechanism, what existing response, and where could an informed conversation help?* Today's data is strongest at specific reported events, financial bridges and sector regulation. It is weaker at enterprise-level operational consequences, named decision owners, supplier workshare, opportunities and actual dates. Avoid a beautifully illustrated but empty “pulse”. The UI must give one or two authentic insights before inviting more exploration.

## Visual design challenge

- Current two-tone editorial lists improved simplicity, but Forces and selected-bank pages often have limited visual differentiation. A third view must offer a **distinctive time/change visual**, not another heading and list.
- Proposed visual metaphor: a restrained timeline with 2–3 rings/connection arcs (UK→industry→enterprise where **supported**). Sparse evidence should appear sparsely; do not draw extra arrows to fill space.
- No source links, evidence tables, nested research expanders or scientific caveat essays in normal Main. Context-specific dates and one material qualifier are enough.
- Original Top/Left/Main illustrations and accessible active states remain; never mutate original artwork as a shortcut.

## Owner decisions needed before implementation

1. Accept Option A as the minimum-read-only integration strategy or require an architectural change.
2. Confirm the product question **“What's changing?”** should be tested as a third toggle, not automatically added to navigation.
3. Choose which 2–3 source-eligible stories to pilot and decide any remaining rights/term exceptions.
4. Accept source withdrawal and temporal revision invalidating **derived presentation and assessment**, never automatic canonical knowledge mutation.
5. Require actual independent Chief Architect/executive/design review of the proposed implementation before merge.
6. Keep authentication rollout, four additional bank earnings admissions, source crawler/agent funding and Pipeline automation out of scope until separately commissioned.

## Validation and completion

- Verified GitHub `main` head before drafting: `fbac4c37910ed07b2baa516e1a5c8d7f329086de`.
- Reviewed exact code/doc owners through GitHub read-only file operations, including current `SCOPES`, Financial/Source/public rendering, `unified_views`, `visual_templates`, canonical external-change service, ADR-026 and BIE-2 research/event packs.
- Changes are **new documentation only** under `docs/flora-runtime/int-map-1/`. No tests executed locally, no application code altered, no CI claim. Docs-only PR must still pass any applicable hosted repository checks; report their actual status on PR before owner acceptance.
- Three scenarios are **repository-grounded existing research interpretations**, not freshly verified 17 November news.
