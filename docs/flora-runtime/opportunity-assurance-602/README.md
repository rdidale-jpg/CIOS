# OA-1 — Owner Opportunity Assurance

Issue #602; broader #600/#599 assurance/research and #597 Ripple programmes remain future scope. Base: `0cb07c2e78ccb16240c799b31cd62736e2135529`. [Full main CI](https://github.com/rdidale-jpg/CIOS/actions/runs/43522807793) and its exact-head artifact were verified before branching: 1,432 identities, 388 strict security passes, 36 unchanged inherited failures, 10 skips, zero comparator issues. Main artifact SHA-256: `b1541647b17904d43e17ee983b25016b9077f6ad37babddf10d63d91fe77da05`.

## Entry and permission contract

Open `/flora/command-centre` → Opportunity Assurance (`/flora/command-centre/opportunity-assurance`). A server-verified active workspace owner under the existing `is_cios_owner` IAM contract **and** `commercial_context.view` are required. Selected roles, URL selectors and free-text identity cannot grant authority. Existing private-read admission and no-store responses are reused; the renderer and every assurance service repeat owner/capability checks. There is no POST/write capability for these routes.

Ownership of the software grants no tenant/private-record bypass. Assessments use the current authorised employer/Offer portfolio and existing per-enterprise discovery checks. Private shortlists/development are read only through their existing actor-private services. An employer owner cannot inspect another seller's private work, even in the same workspace. No cross-user consent grant is invented in OA-1; future delegated private review requires a separately approved permission/consent workflow. Pipeline uses its existing workspace/entity read services. A Pipeline activity reference never unlocks private development notes. Linked Pipeline details require the permitted private record and the existing Pipeline resource check.

An owner in another workspace can see its own empty/non-disclosing dashboard, not another workspace's counts, IDs or notes. No global tenant aggregation is performed. Zero means zero **within the authorised scope**, not that other customers have no records. Forbidden IDs, unknown selectors, duplicate selectors and foreign pair/source references fail closed. Session/enterprise revocation is rechecked on subsequent reads. No private data, hashes or session material is emitted on a public route.

## Control and criterion ownership map

| Control | Actual owner | OA-1 treatment |
|---|---|---|
| IAM, active workspace, enterprise access | Verified security/access services | Existing owner check intersects current capabilities; no new role, grant or bypass |
| CommercialMission / EmployerContext | Existing commercial context and owner-bound employer | Current mission/exclusions and employer versions are retained; no free-text authority |
| Source/Evidence/Observation | Existing candidate adapter, SourceRecord/SourceSegment/CandidateClaim/CandidateObservation/EvidencePackage contracts | Original IDs, passages, dates, locators, rights and candidate/accepted distinctions displayed; no research import/promotion |
| Enterprise/Industry/Market Participant/Twin/APPA | Existing registry, blueprint/Twin, runtime assessment owners | Identity and authority gaps reported; no new canonical store or inferred accepted identity |
| Offer matching / ranking | **`offers.assess_fit`** | Instrument its actual admission conditions, boolean checks and selected sets; same matcher for real and hypothetical inputs |
| Entry-play policy | `buying_entry_plays.resolve` | Original required facts, commercial question/diagnostic/stop condition and content revision retained |
| Private development and eligibility | `seller_development` | Existing authority wrapper calls the extracted pure `qualification_checks`; real hand-off and read-only challenges share that one gate evaluator |
| Pipeline criteria and stages | **unchanged `sales_pipeline.py`** | Existing `CRITERIA`, `qualification`, evidence maturity and authorised read services; no second Pipeline or stage engine |
| Explicit hand-off | Existing seller-development hand-off and Pipeline journal/audit | History/link shown only under scope; no hand-off or reviewer write is available here |

The matcher admission list now records the exact booleans used to select positive facts, rather than recomputing a plausible explanation afterwards. Public temporal/scope rejection, closed programmes, current programmes/catalysts, linked scope, employer approval, mission exclusions and tailored-play availability are inspectable. Business decisions, ordering and eligibility are unchanged; a 50-pair parity test executes the original main matcher and compares its full result with the enriched result after removing only the new trace field. All historical protected files, comparator and failure baseline remain intact; only the already explicit Offers content hash is revised.

Development qualification is factored into a pure function within its existing service, not cloned into assurance. The bound service still resolves current Offer authority and eligibility before the same checks. The hand-off still owns real writes and cannot accept challenge inputs. Pipeline's completeness calculation stays byte-unchanged. Per-criterion UI states project that existing calculation and the actual typed-development trace, rather than defining new qualification rules.

## Metrics and actual semantics

- Research only / Investigate / Prioritise counts use **authorised Offer–enterprise pairs** as denominator at a visible cutoff. Prioritise means prioritise validation, never Qualified.
- Shortlist/development counts cover only the viewer's private records. Pipeline counts cover the existing authorised workspace/entity view, with Qualified shown separately from other stages.
- Current dated facts / retained relevant facts describes temporal admissibility only, not completeness of research. Admitted support / evaluated relevant facts describes the matcher's selection only, not probability or source sufficiency.
- **Qualification input completeness** uses the ten existing Pipeline notes/references, with an explicit `n/10` and percentage. It is not independently verified buyer need, opportunity authenticity, win probability or empirical accuracy.
- Development criteria additionally require the actual customer/seller evidence kind. Ten complete Seller hypothesis notes can produce **100% input completeness and ten failed development evidence checks**. Customer receipt/rights attestation, separate employer approval, identity, current research, owner/action, proof/alternatives and fresh seller review remain separate gates.
- Independently verified buyer need: **Not established**. Opportunity accuracy: **Unknown**, with no labelled outcome cohort. No aggregate accuracy gauge or benchmark is invented.
- Owner review is not recorded by simply opening a page. Read-only outcomes say More evidence needed or Input checks complete; no persistent QA approval or correction is added.

The queue shows ten rows per page, retaining full-cohort denominators. It is sortable by existing rank, enterprise, Offer, version or seller-review state; it filters tier, industry, freshness, applicability blockers, version, seller review and development staleness. Last private-record update is shown where authorised. Country is UK only; group/UK legal and workshare boundaries are retained. Unrecorded facts and independent reviews remain Unknown.

## Trace and reproducibility

A drill-down shows original entity scope, Offer version/approval, declared capabilities/proof/rights/ICP, the matched commercial dimension, primary source IDs/URLs/quoted locators, publication/effective/verification dates, source status, structural/catalyst/programme/completed/counter classifications, exact admitted/rejected conditions, tier, rank key, entry play and stop question. Existing Source rights and unbound identity restrictions remain explicit; original quote extents are unchanged.

The authorised discovery output is replayed through the same pure matcher with the same seller, Offer, account, cutoff and policy. **Full output equality** is required before the path is labelled reproduced; otherwise inspection fails with an unresolved reproduction error. Policy ID, evaluator-source revisions, source-register digest, play-content revision and private input-snapshot digest appear only in the protected view. No LLM or post-hoc rationale generator is used.

When an authorised private record is selected, original seller-reported customer evidence, role hypotheses, typed criteria, review booleans, snapshot cutoff, changed dependencies and any permitted Pipeline link are shown. Saved records are never rewritten to match a replay. Historical successful hand-off does not imply current readiness or independent verification, and current readiness is not permission to write.

## Deterministic copied-input challenges

The same matcher and development gates evaluate:

1. Withdraw one source belonging to this pair/cutoff.
2. Close a selected explicit programme.
3. Supply a **hypothetical** programme-scoped contradiction, not a newly observed source.
4. Remove separate Offer approval.
5. Lose customer-evidence attestation.
6. Unbind the identity boundary.
7. Expire source verification dates under the pinned cutoff.
8. Compare an **unapproved 60-day** review policy with the original 90-day window on the same pinned facts/cutoff.

Challenge records are clearly labelled hypothetical; fabricated contradiction/closure records never acquire canonical status or appear as authentic new research. Original real source passages remain in the original-source disclosure. The display reports actual changed tier/readiness, including valid **no change** outcomes. For example the 60-day policy can invalidate Computacenter's September support while leaving the recent Santander source unchanged. Conditional Santander migration remains conditional.

Existing dependency calculation reports whether private work would require reassessment and exactly which dependencies differ. No source, Offer, development revision, customer note, reviewer status or Pipeline record is changed. There is no autosave, background agent, monitoring, notification or persistent reviewer-decision workflow. OA-2 human decisions/accuracy sampling and Ripple impact notifications remain separate future work.

## Pilot owner walkthrough

All examples are isolated local fixtures, with explicit separate employer approval and clearly labelled **example**, not real customer, evidence.

- **Santander Digital:** 10/10 example customer/seller inputs, explicit Sprint C hand-off. Inspect the current original conditions and separate actual Pipeline stage. Withdraw `BTI-TSB-TRANSFER`: Prioritise weakens to Research only, private work would need reassessment, existing Qualified Pipeline is unchanged.
- **Santander Legacy:** same conditional event, different estate treatment/reconciliation/rollback conversation; missing customer inputs prevent qualification.
- **Lloyds AI-first:** use-case expansion does not establish process/role redesign, buyer demand or customer verification. Inspect missing customer checks and the non-AI alternative question.
- **Computacenter Cyber:** existing framework investment does not establish an assurance gap or outside scope; unbound identity prevents qualification. Compare 90 versus 60 review days.
- **ESG:** Research only; no current programme diagnostic is promoted and no positive is invented.
- **Privacy negative:** a permitted owner sees only its own scope; another owner's workspace stays empty and private seller records cannot be opened through guessed IDs.
- **Metric negative:** ten supported notes/references of Seller hypothesis kind show 100% input completeness while typed evidence and hand-off checks remain failed.

Inspect optional sources, actual machine conditions, ten criteria and current versus hypothetical readiness. Native GET forms provide repeatable read-only challenges. No seller-facing navigation or forensic controls are added; normal business-language explanations and optional sources remain unchanged. Owner entry is a discrete management URL.

## Security, acceptance and rollback

Focused tests cover role spoofing, ordinary-user denial, direct URLs, no-store caching, entity/workspace and private-user IDOR, source/pair/query tampering, session revocation, prompt/script injection as inert text, read-only POST denial, deterministic replay, all bounded challenges, typed criterion states, percentages, source/Offer/identity staleness, Pipeline non-mutation and full original-matcher parity. The original 388 strict security cases, 36 inherited failures and 10 skips stay unchanged.

Required exact-head checks: full `tools/ci/flora_ci.py` gate, all supplemental workflow pytest steps including assurance, and 39 CI failure-policy tests. Responsive previews cover desktop, both iPad orientations, 390/320px mobile and desktop 200% zoom, native keyboard/focus and semantic heading/progress/form checks. Manual real-device Safari, screen-reader and independent commercial-review acceptance remain owner work; automation is not claimed as a human accessibility audit.

Owner acceptance: verify permitted scope; compare the five actual traces; confirm unknown independent verification; challenge sources/approval/attestation/identity; verify no Pipeline mutation; inspect privacy negatives and responsive previews; approve only this bounded read-only increment.

Draft PR only. No merge, Render deployment/restart/configuration, production-data mutation, paid calls, research collection or outreach. To abandon, retain branch/evidence and leave main/production unchanged. If later integrated, revert through a protected PR and rerun exact-head CI. There is no assurance datastore or business-data migration to roll back; retain all existing source, Offer, development and Pipeline records. Never delete or automatically reverse user-qualified opportunities.

## Responsive review pack

231 browser checks: five viewport sizes, JavaScript disabled, native focus and labelled controls, one header, no horizontal overflow, desktop 200% zoom, exact 10/10 input-completeness labelling, deterministic source withdrawal and no seller forensic navigation. All business-domain, Pipeline and mission bytes remain unchanged during the browser challenge session.

| View | Overview | Logic explorer |
|---|---|---|
| Desktop | [Dashboard](previews/desktop-overview-after.jpg) | [Santander Digital](previews/desktop-digital-after.jpg), [withdrawal](previews/desktop-withdrawal-challenge.jpg) |
| iPad landscape | [Dashboard](previews/ipad-landscape-overview-after.jpg) | [Legacy](previews/ipad-landscape-legacy-after.jpg) |
| iPad portrait | [Dashboard](previews/ipad-portrait-overview-after.jpg) | [Computacenter Cyber](previews/ipad-portrait-cyber-after.jpg) |
| Mobile | [Dashboard](previews/mobile-overview-after.jpg) | [Lloyds AI-first](previews/mobile-ai-after.jpg), [ESG](previews/mobile-esg-after.jpg) |
| 320px / zoom | [320px dashboard](previews/mobile-320-overview-after.jpg) | [320px Digital](previews/mobile-320-digital-after.jpg), [200% zoom](previews/zoom-200-digital.jpg) |

[Machine-produced pilot traces/challenges](previews/Assurance-Pilots.json), [browser checks](previews/Browser-Checks.json), [byte-integrity assertions](previews/Read-Only-Integrity.json). Before snapshots show the accepted Sprint C development workspace; the new Command Centre is a separate management view. Source, identity and independent-verification limits remain visible in every applicable drill-down.
