# Sprint A ownership and integration contract

Base: validated main `3b8bd2c5e5177c012826658f820eeeb4ea2705f5`. Issue [#587](https://github.com/rdidale-jpg/CIOS/issues/587). Separate draft branch; no merge, deployment, runtime configuration or production data change.

## Actual owners

| Concern | Reused owner and boundary |
|---|---|
| Employer authority | Existing `EmployerContext` plus owner-reviewed, workspace-scoped `offers.py` binding. A profile name, category, template or CIOS-owner role alone does not authorise representing an employer. No new membership or identity resolver. |
| Supplier preferences | Two additive `CommercialMission` fields: `technology_subindustries` (primary first, up to 12 distinct categories), `offer_library_employer_id`. Existing target-customer `industries`, account exclusions, geography, mission and employer fields retain their meaning. Preferences apply to the currently configured employer; switching company requires confirmation of its categories. |
| Library | Versioned, read-only repository asset `offer_library_assets/technology-v1.json`. 12 parent families, 84 unique IDs, 24 adoptable deep examples, 60 catalogue-only types. Multi-category membership never creates duplicate template IDs. |
| Private adoption | Existing `offers-v1/context.json`; original envelope schema remains v1. `adopt_library` uses existing `save_offer`, verified service envelope, protected journal, audit and persistence. No new operational store. |
| Version semantics | Each new draft retains immutable `template_source` (ID, offer version, taxonomy version, full playbook digest) and `library_playbook` snapshot including original source bibliography. Seller edits, independent review and variations retain lineage. No implicit upgrade or bulk revision of old offers. |
| Canonical intelligence | Existing canonical `capability_offer`, Market Participant Twin and Account Participant Position Assessment remain their owning models. No library row becomes a canonical Offer Twin, capability claim, accepted APPA, participant identity, observation or customer need. `canonical_offer_ref` stays null. |
| Matching | Existing pure `offers.assess_fit`, called by unchanged `discover` in both modes. Library patterns enrich its interpretation; no second scorer, lead engine or evidence store. Existing non-library offers retain their original response shape and pattern policy. |
| Evidence | Existing reviewed Lloyds/easyJet/Technology account adapters and sealed inputs are unchanged. Public category references support vocabulary only. Private seller delivery/rights references remain in existing offer content, entered by a person and reviewed independently. |
| Pipeline and Studio | Original manual qualification routes remain separate GET links. Library/adoption/matching never imports or calls Pipeline writes. Studio remains default-off; no activation, composition, paid model calls or runtime enrichment from onboarding. |

Reconciled against `architecture/specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md`, `Account-Participant-Position-Assessment-Specification-v1.0.md` and canonical `blueprint_import/semantic_twin.py`. Account-relative discovery is an interpretation, not accepted research or global vendor strength.

## Read and write contract

| Route | Behaviour |
|---|---|
| GET `/flora/offers` | Existing portfolio with library-example buyer, trigger and first-play highlights; one continuation to discovery. Custom offers and current variations remain available. |
| GET `/flora/offers/start` | Authorised employer, primary/optional categories, then searchable multi-category examples; no domain mutation. |
| POST `/flora/offers/onboard-company` | Reuses existing employer selection. No free-text lookup or new employer grant. |
| POST `/flora/offers/onboard-preferences` | Selected-employer ID/binding-version and mission-version compare-and-set; bounded distinct category list, save through existing mission owner. |
| POST `/flora/offers/onboard-adopt` | Explicit unchecked selections and seller confirmation; 1–12 unique, current, developed templates, matching selected categories and pinned versions/digests. Validate the whole batch before writing. |
| Existing `/edit`, `/review`, `/transition`, `/discover` | Private editing, separate employer approval and shared offer/account discovery remain the only corresponding owners. Retirement removes a draft from matching; approved parents support protected private variations. |

New routes join existing finite `READ_PATHS` / `WRITE_PATHS`; authentication, capability, revocation/recovery, CSRF, same-origin and cache controls are unchanged. Browser field validation conveys no service authority. Unknown fields, duplicate scalar fields, malformed/stale references, foreign employers and IDOR fail closed. Category HTML, seller fields, source and template fragments are escaped.

All adoption writes run under one consequential verified service transaction. An injected second-item persistence failure is tested to restore the entire batch and remove its committed mutation audit records. Repeated adoption of the same current template by the same user/employer returns the existing non-retired offer, including its existing state; it never silently revises or approves it.

For adopted library offers, submission/approval refuses stale or withdrawn template source; matching eligibility also refuses it. Historic source snapshots stay readable. Retiring remains possible. A current version must be deliberately adopted and separately reviewed. Independent approval additionally requires nonempty seller proof/rights references; human review remains responsible for their validity. A public vendor catalogue is not automatically copied into seller evidence.

The existing profile serializer omitted several existing declared fields. It now preserves `employer`, `offer_portfolio`, `competitors`, `partners`, `strategic_propositions` and `delivery_constraints` when onboarding saves an existing mission. Older profile forms also preserve the two additive preferences when they omit them. Tests cover both compatibility paths; no existing data is rewritten merely by loading a view.

## Matching, timing and countries

Library `research_context_claim_ids` select **existing account context**, not observed triggers. For the same Lloyds context, legacy modernisation refers to the reported application-retirement priority while the bounded AI experiment refers to the reported data-enablement strategy. They yield different entry plays and disconfirming tests through the same engine. Existing controls and rival explanations remain available, including incumbent capability. Dated events, residual need, buyer access, budgets and procurement are unestablished. No event half-life, ranking score, ROI, contract value or urgency is invented.

Every structural/event pattern carries observables, rival explanations, qualitative importance and revalidation/decay semantics. They remain explicitly **not observed**. Sprint A does not monitor or detect live events. Account facts obey the existing evidence cutoff, permission checks, identity/rights limits and adapter seals.

Methods are country-neutral with an explicit GB overlay for initial discovery. Other country overlays require reviewed local rights, residency, regulatory and procurement context plus existing governed account research. There is no hardcoded country-specific matching implementation or invented international research. The commercial taxonomy is not SIC/NAICS; it does not alter the UK landscape's existing SIC2007/2024 GVA series. SIC2026 is cited as a newer statistical classification, not silently mixed into that series.

## Protected owner reconciliation

The historical #585 `Protected-Owners.json` stays byte-identical. #585 was presentation-only; #587 explicitly authorises additive changes in `offers.py` and `commercial_mission.py`. The #583/#585 presentation-only tests now check their old hashes against that historical record, their exact new hashes against [Owner-Compatibility.json](Owner-Compatibility.json), and all remaining **196 protected files** against the original bytes. New tests independently pin the AST of 16 existing authority/storage/Studio/account/discovery functions to the validated base. The security selection, failure comparator, 1,432 baseline identities, approved failures and skips are unchanged. This is a scoped functional contract revision, not a refreshed failure baseline.

## Rollback and limits

No migration command runs. Existing offers/profiles lacking new fields load normally; older private drafts are untouched. Atomic adoption rollback is exercised by fault injection. Keep application and persistent-store backups before any future owner-authorised integration.

A post-integration rollback must preserve newly authored private work: stop writes, take a consistent backup, and prefer a forward fix disabling library entry points and excluding library-derived candidates while retaining their history. Do not blindly restore an old data snapshot or run an old matcher against new lineage that it cannot enforce. A binary rollback to the validated base requires a reviewed retention/compatibility plan for new records; no such production operation is performed by this PR.

Remaining owner checks: physical iPad/Safari, screen-reader/zoom behaviour, real seller vocabulary and delivery-proof review, one-minute human usability timing, and production setup through the existing owner-authorisation procedure. Browser automation uses isolated local HTTPS fixtures only.

## Owner-priority continuation (PR #588)

The current catalogue is 89 types / 29 developed, with five enterprise programmes and explicit qualitative economic, disconfirming and follow-on hypotheses. The original 84 rows, IDs and snapshots are unchanged. Top-level catalogue v2 does not invalidate original row-v1 references: `source_ref` now reads each row's pinned `taxonomy_version`. Actual row edits/withdrawals continue to block eligibility. [Original-84 pins](strategic-priorities/Original-84.json) and tests enforce this migration contract.

`consulting` retains its ID and now displays Digital Transformation & Consulting. Optional Systems Integration is stored in additive private `technology_delivery_specialisms`; omitted legacy-client fields preserve it, explicit empty selections clear it. A separate static delivery crosswalk supports existing Offer IDs without mutating their archetypes. No company capability, identity or permission is inferred.

Only strategic-programme results gain `economic_value_hypothesis` and contextual disconfirmation/follow-on data; `economics` remains null and no Pipeline eligibility, score or second matcher is added. Existing non-priority response shapes remain. The same sixteen authority/Studio/account/discovery functions stay AST-identical, all other 196 protected owners stay byte-identical, and the two explicitly authorised functional owners have updated reviewed candidate pins. [Detailed contract, sources and walkthrough](strategic-priorities/README.md).
