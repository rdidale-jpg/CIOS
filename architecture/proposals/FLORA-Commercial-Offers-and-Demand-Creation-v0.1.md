# FLORA Commercial Offers & Demand Creation — Architecture Proposal v0.1

**Status:** Draft for owner and architecture review — not an accepted canonical standard  
**Date:** 13 November 2026  
**Scope:** Seller-selected offers, buying triggers, proactive entry plays and governed transition to Pipeline  
**Implementation status:** Design only. No runtime, schema, permission, Pipeline or agent changes are authorised by this proposal.

## 1. Decision and thesis

FLORA must answer: **For this seller, selling this offer, which customers should be approached, why would they change, how might a relationship begin, and what justified action comes next?**

Current industry and enterprise intelligence identifies pressures and possible change. Offers add the missing seller-relative interpretation: not only which customers might buy, but how to **create preference and demand before a formal purchasing process**.

The intended path is:

```text
Authenticated seller / workspace Commercial Mission
    → represented employer / Market Participant Twin
    → selected existing Offers and/or seller-approved composite propositions
    → governed Trigger Patterns + Entry Plays
    ↔ Industry / Enterprise Intelligence (Evidence → Observation → Signal → Hypothesis)
    → Offer–Enterprise Fit Assessment (account-relative)
    → recommended commercial posture and next action
    → seller-reviewed qualification → existing Pipeline write boundary
    → learning from validated engagement/outcomes
```

**Design decision proposed:** No standalone Offer Twin in v1. Introduce versioned seller-side commercial entities/projections while reusing canonical capability/offer objects, Market Participant Twin, Enterprise Twin, Account-Participant Position Assessment, Commercial Mission, existing Evidence/Observation and opportunity/pipeline owners. A separate Offer Twin may be reconsidered only if independent lifecycle, multi-enterprise reuse or network propagation establishes a real requirement.

## 2. Existing architecture to reuse

- `cios/applications/flora/commercial_mission.py`: authenticated-user `CommercialMission` already includes `employer`, `offer_portfolio`, sectors, named accounts, partners, competitors and target objectives. `EmployerContext` is a separate operational-context projection. **Mission declarations are not verified Enterprise Intelligence.**
- `docs/flora-executive-twin-canonical-owners.md`: existing canonical `capability_offer` objects; declared seller portfolio is not the same as accepted supplier capability evidence.
- `architecture/specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md`: participant capabilities, offerings, alliances, references, routes to market, strengths and weaknesses.
- `architecture/specifications/market-participants/Account-Participant-Position-Assessment-Specification-v1.0.md`: account-specific need, capability fit, access, incumbency, alternatives, constraints, posture and lineage.
- `architecture/founding-papers/FP-003-Flora-Intelligence-Architecture.md`: Evidence → Observation → Signal → Hypothesis → validation → recommendation, with transformation pressure explicitly distinct from commercial opportunity.
- Existing Pipeline owner exclusively controls qualified opportunity creation, versioning, permissions, duplicate detection and audit.

Architecture review must settle canonical ownership before implementation, avoiding duplicate opportunity state and new truth stores.

## 3. Proposed conceptual entities and relationships

| Object | Responsibility | Canonical placement / ownership proposal |
|---|---|---|
| **Seller context** | Which employer, seller, territory, constraints and account access apply | Existing user/workspace-scoped Commercial Mission + Employer Context, linked to resolved Market Participant identity; no guessed linkage |
| **Commercial Offer** | Outcome, propositions, target conditions, capabilities, credentials, terms and delivery constraints | Versioned supplier-side offer projection linked to canonical `capability_offer` and Market Participant; private additions scoped to seller workspace |
| **Trigger Pattern** | Generalised structural pressure or discrete event and its observable indicators, alternatives, temporal relevance and conditions | Reusable pattern catalogue; source-backed observation at an account remains separately owned by Evidence/Enterprise Intelligence |
| **Entry Play** | Ethical/credible customer-first commercial intervention, buyer role, insight, discovery questions, proof, objections and progression steps | Versioned seller-authored reusable play associated with offer(s) and trigger(s) |
| **Offer–Enterprise Fit Assessment** | Account-relative judgement about need, trigger, offer fit, economic materiality, access and competition | Governed interpretation/recommendation layered on existing APPA; no new canonical fact |
| **Sales Play Recommendation** | The next concrete seller action, with rationale, evidence and testable hypothesis | Derived recommendation with timestamp, reason chain, version and user disposition; *not* a Pipeline opportunity |
| **Composite Offer Draft** | Proposed bundle of seller capabilities, partners and services; requires commercial/rights approval | Private candidate until seller accepts; do not assert its availability or delivery ability |
| **Learning Event** | Result of engagement/test and impact on hypotheses, effectiveness and next action | Audited seller feedback; do not treat a positive reply as proof of eventual purchase |

Key relationships: Seller REPRESENTS Participant; Participant HAS_CAPABILITY / OFFERS; Offer ADDRESSES Need/Outcome; TriggerPattern INDICATES PotentialNeed; Enterprise EXHIBITS Evidence-anchored Signal; EntryPlay VALIDATES Hypothesis and opens BuyerConversation; FitAssessment COMPARES seller+offer to enterprise; SalesPlay MAY_BECOME Existing Opportunity only after qualification.

**Offer is not a customer need. Trigger is not intent. Entry Play is not an opportunity. Opportunity is not a Pipeline write until explicitly authorised.**

## 4. Commercial Offer contract (candidate)

Minimum fields: stable ID and version; name; seller/owner; employer identity and geography; products/services and capability links; customer outcome; economic value mechanism (cost, revenue, risk, speed or resilience); ICP/target enterprise attributes; applicability and exclusions; buyer roles and plausible buying centres; differentiated credentials and evidenced references; required partners, licences and delivery constraints; pricing/engagement shape if approved; approved proposal assets; visibility scope; source/owner, reviewed date, lifecycle (draft/approved/retired).

The catalogue can contain:
1. **Existing approved offers:** seller/organisation-approved current propositions; still do not claim delivery proof without evidence.
2. **Seller-defined plays:** approved packaging of existing capabilities for a target situation.
3. **Composite offer candidates:** FLORA-suggested combinations; clearly provisional internally, never presented externally as seller commitments prior to approval.

A single Offer may have many Entry Plays. An Entry Play can serve several Offers. A multi-stage commercial journey may chain a diagnostic, implementation and longer-term service, with explicit customer value at each stage.

## 5. Trigger model and entry logic

**Event trigger:** a dated or anticipated catalyst (renewal, regulatory deadline, acquisition, leadership change, announced technology retirement, major investment, service incident). Evidence must support *that event*; do not infer automatic budget or procurement.

**Structural trigger:** underlying pressure (rising run cost, fragmented workflows, constrained capacity, weak service economics, competitive disadvantage) without a discrete buyer event. May justify proactive exploration rather than asserted buying urgency.

Each pattern stores applicability, indicators, positive and negative evidence, materiality, temporal horizon and decay/review policy, normal alternative explanations, affected roles and suggested validation questions.

**Entry Play** must contain:
- Buyer/influencer starting point and permission-based route to access.
- Insight-led proposition: customer business consequence, not vendor features.
- Discovery question(s) which could disconfirm the hypothesis.
- Low-friction first step (benchmark, workshop, assessment, proof-of-value).
- Expected value, customer cost/time burden and transparent limitations.
- How a successful first step might lead to next phases.
- What to do if timing, fit or access does not materialise.
- Evidence needed before financial or technical claims.

Example: AI-enabled operations transformation. Structural pressure may be large repeatable contact volumes or ageing workflows; catalyst could be a cost programme or renewal; entry play might offer a targeted process-cost diagnostic. Never assume a diagnosed problem, ROI percentage or approved buying process merely from sector membership.

## 6. Decision logic: no opaque single score

```text
1. Resolve authenticated seller + employer + selected offer(s).
2. Select eligible target industries/enterprises and exclude disallowed accounts.
3. Collect bounded, authorised, dated enterprise and market signals.
4. Match trigger indicators; examine counter-evidence and alternative explanations.
5. Assess customer problem importance separately from explicit buying intent.
6. Test Offer capability/outcome fit and delivery/partner constraints.
7. Assess access, incumbent/competition, timing and procurement possibility.
8. Build a reasoned commercial value thesis, with EST if defensible and a range.
9. Choose appropriate posture and most proportionate entry play.
10. Explain the top reason(s), counter-signals, one next action and validation test.
11. Await seller feedback; only existing opportunity capture can write Pipeline.
```

Separate assessment dimensions: **need**, **trigger/urgency**, **solution fit**, **customer value**, **seller credibility**, **access**, **competitive position**, **commercial attractiveness**, **evidence quality**. Store evidence and independent dimension state. Do not allow a high need score to conceal no access, lack of delivery rights or an incumbent constraint. Hard constraints and disqualifiers override an aggregate ranking.

Suggested postures:
- Monitor / research: weak or ambiguous signal.
- Validate: credible pressure and a testable question.
- Create demand: structural need and plausible fit, no explicit buyer programme.
- Shape: emergence of sponsored change, scope influence still possible.
- Pursue / capture: evidence of buying process, access and seller suitability.
- Partner: relevant need but seller access/capability constrained.
- Deprioritise: weak commercial/economic/ethical case or explicit exclusion.

An enterprise can appear for several Offers with **separate fit assessments**; the UI should group related hypotheses to avoid multiplying duplicate opportunities.

## 7. Example commercial journey (hypothetical)

Seller: a UK technology-services company, identity and offer portfolio explicitly configured. Offer: AI-enabled service operations transformation.

- **Enterprise signal:** a public announcement of a cost-efficiency programme (if actually sourced).
- **Structural hypothesis:** service operations may contain automation potential; *not stated as a company weakness*.
- **Trigger interpretation:** cost programme could create an executive window, but intent/budget are not assumed.
- **Proposed entry:** show an externally shareable industry-level operating economics perspective; offer a scoped service baseline workshop with mutually agreed data protections.
- **Qualify:** contact decision owner, establish operational baseline, sponsorship, success measures, funding route, seller fit and competition.
- **Expansion:** only if supported, assess transformation implementation and managed-service phases.
- **Pipeline:** seller explicitly promotes a validated, authorised opportunity through existing service boundary.

## 8. UI principles

- Under **My Company**, select represented organisation via explicit identity resolution; show offers and access-authorised seller-specific context.
- **My Offers:** three or four concise offer tiles, selectable portfolio; each shows outcome, buyers, trigger examples and entry plays.
- **Target opportunities:** an evidence-based ranked list grouped by enterprise with two short answers: **Why this customer?** and **What should I do?** Include recommended entry play and potential commercial shape.
- Business-facing presentation uses verified clean values; defensible estimates carry visible **EST** and an available basis/range; unavailable fields are blank/omitted rather than repetitive labels such as “unknown”, “missing”, “ungoverned”. Specialist detail retains full evidence, contradictions and security/operational alerts where required.
- User can approve/reject/edit an offer or play and record customer feedback. Data boundary must be obvious: a personal employer selection must not redefine shared enterprise truth.

## 9. Security, assurance and operating limits

- Seller workspace and organisational profiles are private; public Market Participant facts do not reveal private account plans, relationships, commissions, access maps or commercial strategies.
- Multi-tenant/role constraints, explicit offer ownership, edit permission, encryption/storage constraints, CSRF for any write and audit remain in force.
- Sources, time, source rights, provenance, citations, strengths, delivery claims and supplier relationships remain checked as in existing architecture.
- No autonomous outreach, external account mutation, paid agent, full scraping, auto-publication or automatic Pipeline entries.
- Human review required for externally asserted seller capabilities, composite Offers and qualified opportunity promotion.
- Match explainability and disconfirming evidence are mandatory; outcome feedback must not self-authorise new canonical knowledge.

## 10. Proposed phased validation

**Phase A — semantic and architectural contract:** architecture review; owner mapping, entity relationships, no duplicate stores, versioning, confidentiality and migration plan; define acceptance datasets.

**Phase B — seller setup and offer playbooks:** authenticated employer selection and small offer portfolio, with one approved existing Offer and trigger/entry templates; preserve old missions.

**Phase C — offer–account matching pilot:** test one service, one consulting and one AI-innovation offer across a small, diverse Banking/Aviation/Technology set. Measure top-N relevance and reason clarity; false positives; timeliness; appropriateness of entry plays and customer actionability. Use sourced and human-validated data, not assumed current contracts.

**Phase D — controlled Sales Play workflow:** seller review, recording outcomes and explicit existing Pipeline capture; no parallel writer.

**Phase E — composite-offer generation:** opt-in experiments based on validated capability/partner coverage; require approval before an offer is treated as sellable.

## 11. Owner decisions before coding

1. **Identity:** Is a user able to represent one employer at a time, or multiple seller organisations/roles (advisor, channel partner, portfolio career)? Recommend many authorised identities but one active Commercial Mission at a time.
2. **Offer creation:** Should a seller be able to create personal Offers immediately, with a separate approval state for organisation-wide publication? Recommend yes.
3. **Targeting mode — OWNER DECISION CONFIRMED (13 Nov 2026):** Support both offer-led discovery and account-led discovery with **one shared Offer–Enterprise matching engine**. This is a required product/architecture contract, not a future option.
4. **Composite proposals:** Opt-in exploratory mode only, with no external or contractual claims until seller approval.
5. **Scoring:** Show explainable prioritisation, not pseudo-exact win probabilities.
6. **Pipeline threshold:** Require account problem, relevant buyer/access route, explicit seller fit, qualified commercial action and user approval before promotion.

## 11A. Confirmed decision: symmetric discovery, one matching engine

**Owner confirmation: 13 November 2026.** FLORA must support both:

- **Offer-led:** seller selects one or more authorised Offers → shared engine evaluates eligible enterprises against each offer → ranks commercially useful enterprise/offer matches and proposes trigger interpretation, entry play and next action.
- **Account-led:** seller selects an enterprise → the same engine evaluates the seller's authorised Offer portfolio against it → ranks relevant offers, with trigger evidence, recommended entry play and next action.

The two journeys MUST call the same assessment contract `assess_fit(seller_context, offer_id, enterprise_id, evidence_cutoff, policy_context)` or a functionally equivalent service. Selection only changes candidate retrieval and result grouping, **not assessment dimensions, evidence standards, status, confidence, access control or pipeline eligibility**.

**Invariance rule:** For a given seller context, Offer, enterprise, source cutoff and assessment/policy version, offer-led and account-led exploration yield the same underlying fit assessment and recommendation identity, independent of the journey path. Stable IDs and deduplication prevent duplicated opportunities. Both journeys allow a concise explanation of *why this customer / why this offer / why now / recommended first move*.

**Pilot acceptance:** Test the same Offer–Enterprise pairs through both journeys, assert identical reasoning inputs and assessment outcomes, check ranking remains context-sensitive, inspect source/EST presentation, and verify neither route writes Pipeline or bypasses existing authorisation.

## 12. Acceptance criteria

- User can select represented enterprise and a small, versioned set of offers without modifying public canonical organisation facts.
- Each Offer expresses outcome, ideal customers, Trigger Patterns, Entry Plays, differentiated credentials, delivery constraints and sources.
- Two different offers produce meaningfully different, explainable target enterprise recommendations.
- Signal-to-hypothesis-to-play-to-next-action lineage survives and disconfirming evidence is visible in specialist inspection.
- Product can recommend creating demand *without* asserting buyer intent, budget, procurement or an enterprise weakness.
- A candidate may not become Pipeline without existing authorised capture/qualification and deduplication.
- Financial/people estimates explicitly show **EST**, basis and date; no filler “unknown” text in primary views.
- Regression/security suite, access isolation, desktop/iPad/mobile UX and clear rollback criteria pass before merge.

**Next decision:** Review the six owner choices above and settle the minimal v1 contract before implementation. This proposal itself is not a normative architecture release.
