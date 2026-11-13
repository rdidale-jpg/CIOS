# Seller-controlled opportunity development — Sprint C

Issue #598. Base: `b5003f81481fb8d7a039972255da8a8b58a8b814`, directly from validated origin/main. Full main [CI run 43511484185](https://github.com/rdidale-jpg/CIOS/actions/runs/43511484185) and its artifact were verified before branch creation: 1,432 tests, 388 strict security passes, 36 unchanged inherited failures, 10 skips, zero comparator issues. Main artifact SHA-256: `4154bbf16c512ee7bfc9370657f6426892885cb8c8c24ce44797a079b6d0d797`.

## Product and ownership contract

Discover → Investigate → Validate → Create Preference → Qualify → Pipeline is a deliberate seller workflow. The four development tasks are private working statuses, never a second authoritative sales-stage engine or a claim that a customer has agreed. Users can revisit tasks, pause, retire and resume. There is no automated outreach, research, notification, qualified opportunity creation or canonical promotion.

| Owner | Existing responsibility / Sprint C use |
|---|---|
| CommercialMission | Current employer-linked seller mission, exclusions, target context and preferences; snapshot dependency, never authority granted by free text |
| EmployerContext / Offers | Owner-bound employer, authorised sellers, separate approver, versioned eligible Offer and shared matcher |
| Buying Trigger Intelligence | Original source IDs, dated candidate facts, negative evidence, identity/rights limitations and differentiated entry plays; copied as an immutable research snapshot |
| Sprint B reviewed shortlist | Required intentional source for private development creation; own user, employer, workspace, source revision and assessment identity revalidated |
| `seller_development.py` | Private versioned working notes inside the existing Offers user's envelope; no new evidence, matcher, canonical Opportunity Twin or Pipeline store |
| Canonical imported Opportunity Twins / assessments | Existing blueprint import/semantic Twin and runtime CommercialAssessment/HypothesisAssessment ownership is unchanged; private seller conclusions never enter these stores |
| `sales_pipeline.py` | Sole authorised opportunity-record owner, existing ten qualification criteria, explicit review/confirmation, existing state machine, journal and audit |
| Security services | Existing verified read/write transactions, IAM/entity/workspace intersection, protected file journal and revocable sessions |

Persistence is additive: `offers-v1/context.json → users[workspace,user] → development[stable_id] → versions[]`. Stable identity includes private actor, workspace, employer, Offer and enterprise. Repeated create returns the existing record and never overwrites notes. Limits: 50 histories per user and 100 versions per candidate. The entire write uses the existing atomic protected envelope; no migrations or new background processes.

Allowed fields: customer challenge, seller commercial insight, first conversation, proposed diagnostic/proof artifact, seller delivery proof/rights/constraints, competing/no-change alternatives, next action, optional due date, engagement notes, unvalued economics, role-based buying group, typed qualification evidence, explicit customer-evidence attestation and seller review. Scope, author, employer, enterprise, snapshot, development owner and Pipeline link are server-controlled. Owner is the creating private seller; arbitrary reassignment is not permitted.

Every revision retains the full assessment/Offer identity, original shortlist/version, Offer/version/state, research and play-content digests, source IDs/publication/verification/effective dates and rights/identity limitations. Private notes remain separate from immutable research. Buying-group roles begin as hypotheses; the product generates no individuals, access or relationships. Seller-supplied role details must have a permitted reference before being labelled customer-reported.

## Distinctions and gates

- Public evidence: original retained source context, never customer validation.
- Seller hypothesis: privately authored interpretation, insight, diagnostic and role assumptions.
- Customer statement / document: evidence the seller says they actually received, with an actual date, note, permitted reference and explicit rights/receipt attestation. This is **seller-reported customer evidence**, not independent customer verification by FLORA.
- Seller review: evidence for delivery rights, differentiation, competition and internal commercial judgement. Self-declared capability does not acquire customer verification status.
- Qualification decision: an explicit seller-reviewed internal completeness decision, followed by a separate explicit Pipeline hand-off.

Validate needs an actual customer-evidence problem row and attestation; internal tasks and public releases cannot supply it. Create Preference also needs a meaningful challenge, insight, diagnostic, seller proof, alternatives and next action. Unknown placeholders do not satisfy those fields. Qualify additionally requires all ten existing Pipeline criteria with supported notes/references, appropriate evidence distinctions, current employer-approved Offer, owner/next action, active candidate, current supported research and a supported enterprise reference. Eight customer-facing criteria need customer statements/documents; competition and differentiation can use a seller review. Unsupported or future-dated customer evidence is rejected. An exact public trigger source ID/URL cannot be relabelled as customer confirmation.

No rigid external sales methodology is imposed. Customer outcome, buyer/decision context, funding, timing, relationships and next steps map to the current Pipeline contract; MEDDICC/Blue Sheet/capture artifacts can be referenced without claiming completion. Pipeline's current ten-input rule is intentionally stricter than the private research workspace. Unknown economics remain acceptable where that existing contract permits; no amount is generated or transferred from free-text commercial assumptions. Pipeline receives blank amount / Unknown value basis.

Research-only candidates can retain private Investigate notes, but cannot progress beyond that task or enter qualified Pipeline. The UI gives Continue research instead of Develop opportunity for Research-only/stale shortlist entries. Unbound Technology presentation identities can retain private work and customer-reported investigation; they cannot qualify/convert. A presentation reference is not an accepted enterprise identity, and this sprint grants no source licence or canonical binding. Existing reference compatibility is sufficient only where the authorised Pipeline service already supports it.

## Pipeline hand-off and transaction boundary

An eligible seller must first explicitly save Qualify after reviewing all inputs, then separately confirm Create reviewed Pipeline entry. The development service calls **existing** `create_opportunity`, then **existing** `update_opportunity` with the ten notes/references, evidence review, Qualified and confirmation. The original Pipeline service validates all existing criteria and state rules. Existing demonstration/evidence-maturity labels remain conservative: Qualified is seller-reviewed completeness, not independent customer verification or accepted Twin truth.

The outer verified transaction journals both the Offers development revision and Pipeline file. A failure in creation, qualification, audit or linking rolls back both. Candidate-to-Pipeline ID is written only after success. Repeated authorised hand-off returns the same Pipeline record; it never creates a duplicate or overwrites subsequent Pipeline progression. Activity history links the private development ID/version; the private record retains full source/evidence lineage. No existing opportunity is selected or overwritten. Only the explicitly selected qualification notes/references are deliberately shared into the existing workspace Pipeline; other private development notes remain private.

## Staleness and future Ripple

Reads compare Offer content/version/state, employer binding revision, CommercialMission, research digest, entry-play content revision, tier/stage and individual fact-reference/freshness dependencies against the current matcher output. Changed keys are shown exactly as **Stale — Reassess**. Withdrawn/completed/cancelled/superseded/expired facts and revoked Offer eligibility disable progression. No customer note, old snapshot or Pipeline stage is silently rewritten. Explicit reassessment appends a new snapshot, retains private notes and history, resets internal review and returns to Investigate. Parent shortlist drift does not erase development history.

The stored dependencies, private owner/workspace/entity IDs and hand-off link are sufficient for later Ripple #597 to address impact checks under existing permissions. No Ripple collector, schedule or notifications are implemented. Counterfactual tests simulate cancellation/withdrawal: fact dependencies and tier change, customer notes persist, reassessment records a Research-only snapshot, and no Pipeline write occurs. An already handed-off record can show drift while the Pipeline record remains untouched.

## Pilot walkthroughs

1. **Santander Digital:** reviewed conditional migration context → private service-continuity hypothesis → seller reports a permitted example customer journey decision → proposes a one-journey ownership/acceptance artifact → explicitly reviews all ten criteria → separate example-only Qualified hand-off. Court/transfer conditions and separate Santander/TSB identities remain explicit.
2. **Santander Legacy:** same dated source, distinct retained estate-treatment/rights/reconciliation/rollback diagnostic. It remains private; no transfer, rewrite, cloud move or supplier vacancy is assumed.
3. **Lloyds AI-first:** AI use-case expansion remains distinct from process/role transformation. Without customer-confirmed process redesign, validation/qualification fails. A non-AI baseline and human control/adoption questions are retained.
4. **Computacenter Cyber:** existing framework investment can remove the need for outside assurance. The candidate asks whether a specific independent assurance question remains. No missing control or external budget is asserted. Unbound identity prevents qualified Pipeline.
5. **ESG Research-only:** no evidenced buying programme; private research notes can persist but task changes and hand-off fail. No positive is invented.

All previews and positive customer-evidence examples use explicitly labelled local **example fixtures**. They are not real customer statements, capability evidence, budgets, buyer names or demand. The demonstrated qualification uses ten dated example references (`Private example meeting/reference <criterion>`); customer-facing rows are Customer statement, competition/differentiation are Seller review, receipt/rights and internal review are manually checked. No numeric value is supplied. Real deployment users must provide their actual permitted evidence; an independent sales-practitioner acceptance review remains owner work.

## Acceptance and UX

From an Offer/enterprise assessment, explicitly review a shortlist. A current supported reviewed entry offers one Develop opportunity action. Open My development through the compact header Explore menu. The private list foregrounds customer, Offer, task/activity and next action. Detail starts with customer challenge → commercial insight → first conversation → next action. Native form disclosures hold proof/competition, buying-group roles and customer qualification; original research stays in the single Sources & method.

Before: investigation ended at a private research shortlist. After: durable development work and an explicitly reviewed service-owned Pipeline hand-off. No additional top-level navigation forest or automated CRM is introduced. Review desktop, iPad landscape/portrait, phone/320px and 200% zoom previews. Automated native-label/focus/overflow checks complement manual real-device Safari and assistive-technology acceptance; do not claim a human screen-reader audit.

## Security, validation and rollback

Focused tests exercise private/foreign-workspace/foreign-user/entity denial, forged scope, wrong Origin, CSRF, escaping, stale replay, separate Offer approval, unknown commercial inputs, real customer-evidence distinctions, research-only/unbound identity gates, staleness, cancellation, pause/retire/resume, idempotent creation and hand-off, atomic two-store rollback, existing Pipeline preservation and Studio default-off. Existing source bytes, comparator, baseline, security selection and historical pins remain unchanged. The current Offers file hash is explicitly revised for additive route registration; its protected authority functions and shared matcher are unchanged.

Required final checks: `python tools/ci/flora_ci.py --output <fresh-external-directory>`, all supplemental workflow pytest selections including Sprint C, and `python -m unittest discover -s tests/ci -v`. Hosted CI checks the exact PR head. The gate must retain 1,432 test identities, 388 strict security passes, 36 inherited failures and 10 skips with zero comparator issues. Exact final outcomes are supplied by the PR checks and sanitized artifacts.

No merge, Render change/deployment or production-data action is authorised. Before any later integration, owner acceptance and deployment approval are required. Abandoning the draft leaves main/production unchanged and preserves this branch/evidence. If later rolled back, revert through a protected PR and rerun exact-head CI; retain the additive development histories and existing Pipeline records. Old code ignores the new private envelope field. Do not delete stores, wipe Pipeline or automatically reverse a qualified opportunity. Any store restoration needs separately authorised validated backups.

## Preview gallery and automated walkthrough

258 browser checks pass with JavaScript disabled across five viewport sizes, plus 200% zoom at a 1280px desktop viewport. The isolated example creates five development candidates, exercises three explicit development revisions and one separate hand-off, and verifies one qualified addition, an unchanged pre-existing Pipeline record, unchanged other candidates/Offers/users and default-off Studio.

| View | Before | Development | Reviewed hand-off |
|---|---|---|---|
| Desktop | [Discovery](previews/desktop-discovery-before.jpg) | [Santander Digital](previews/desktop-digital-after.jpg), [Legacy](previews/desktop-legacy-after.jpg), [list](previews/desktop-list-after.jpg) | [Review](previews/desktop-qualified-review.jpg), [Pipeline](previews/desktop-pipeline-handoff.jpg) |
| iPad landscape | [Discovery](previews/ipad-landscape-discovery-before.jpg) | [Lloyds AI-first](previews/ipad-landscape-ai-after.jpg) | [Review](previews/ipad-landscape-qualified-review.jpg) |
| iPad portrait | [Discovery](previews/ipad-portrait-discovery-before.jpg) | [Computacenter Cyber](previews/ipad-portrait-cyber-after.jpg) | [Pipeline](previews/ipad-portrait-pipeline-handoff.jpg) |
| Phone | [Discovery](previews/mobile-discovery-before.jpg) | [Digital](previews/mobile-digital-after.jpg), [ESG](previews/mobile-esg-after.jpg) | [Review](previews/mobile-qualified-review.jpg) |
| 320px / zoom | [320px discovery](previews/mobile-320-discovery-before.jpg) | [320px Digital](previews/mobile-320-digital-after.jpg), [200% zoom](previews/zoom-200-ai.jpg) | [320px Pipeline](previews/mobile-320-pipeline-handoff.jpg) |

See [pilot source/version snapshots](previews/Development-Pilots.json), [browser checks](previews/Browser-Checks.json) and [hand-off integrity](previews/Handoff-Validation.json). No real user or customer data is used.
