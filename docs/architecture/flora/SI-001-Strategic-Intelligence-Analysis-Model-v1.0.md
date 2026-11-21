# SI-001 — CIOS Strategic Intelligence Analysis Model v1.0

**Status: Review proposal — architecture and design only.** Owner acceptance pending. No canonical contract, ADR, production profile or runtime behaviour is changed. Prepared under Issue #615 and its two owner amendments on 14 November 2026, against main `fe66516c15726dc45de147ede2674c9172f8cac6`.

## Decision recommendation

Adopt **Option A: a derived, read-only strategic synthesis** over existing authorised source/Observation/Twin/relationship and interpretation owners. Leadership Agenda is a scoped executive projection. Strategic Issue is a concern-and-decision view, not a new durable intelligence object. Pain is a classification of a demonstrated adverse consequence or an explicit hypothesis; it is not an intelligence stream. No new pressure, matcher, qualification or autonomous opportunity engine is required.

Complete analytical coverage is the **design obligation**. It does not certify complete current evidence. Zero findings, fewer than three issues and an unanswered analytical dimension are valid. The proof has two UK, two Banking and three Lloyds agenda issues, rather than filling a target count. None establishes customer-confirmed need, external spend or a deal valuation.

The commercial domain includes potentially £100m+ reinvention. That is a product ambition, not an estimate for these examples. A bank's deposit stock, Group profit, investment plan or savings target cannot supply an external contract value.

## Authority and existing model boundaries

Accepted ADR-001/002/003/004/005 govern Observation memory, durable Enterprise Models, reasoning/model separation, human knowledge and lineage. ADR-009/010/011 govern proportionate assurance and source-first/candidate financial work. ADR-012/013 preserve canonical acceptance and model-backed views. ADR-014/024 permit evidence-governed reasoning with deterministic validation; ADR-015 governs mission/research-policy/capability context; ADR-016 governs exchange. ADR-026 alone owns Material Pressure qualification semantics.

The ADR index and bodies identify ADR-014/024 as Accepted despite stale Draft headers. EI-001 is marked Draft in its header and ADR-026, while the Authority Registry lists Accepted; that registry explicitly complements rather than supersedes owning papers. Record this unresolved metadata inconsistency and rely on accepted ADR-002/026 ownership and invariants; do not silently accept additional fields. The Reference Architecture/Design Doctrine also have legacy header/registry discrepancies. ADR-023/025, EU-001, IT-001 and relevant workspace/industry/completeness specifications remain Proposed/Review unless their explicit authority states otherwise. They inform compatibility, not new runtime permission.

No existing authority is edited by SI-1. A directory or file named `canonical` and a Validated prose frontmatter are not, by themselves, proof that every included claim is a currently accepted canonical Observation.

## The analytical composition

| Analysis | Question and scope | Required inputs / output | Critical boundary |
|---|---|---|---|
| **PESTLE** | Political, Economic, Social, Technological, Legal, Environmental at country → industry → enterprise | Dated geography/legal scope; external development; transmission mechanism; applicability support; consequence hypothesis; counter-case | Six named dimensions, each allowed zero material findings. A national force is not an enterprise duty, pain or buying trigger. |
| **Porter's Five Forces** | Rivalry, entrants, substitutes, supplier power, buyer power at a defined market/segment | Market boundary; structure; alternatives; barriers/capital; bargaining; profitability mechanism; historical/trend evidence and missingness | No national all-economy Porter score, no arbitrary numeric severity, no industry inference from one company's supplier announcement. |
| **Industry economics** | Where value and returns accumulate | Sourced market/segment size and matched-period growth; revenues/profit pools; costs/margins; capital requirements; investment and value distribution | Finance & insurance GVA is not Banking sales. Size does not prove profitability. EST needs declared method, scope, range and source basis. Current missing profit/capital series remains missing. |
| **Industry value chain** | Create, deliver and capture value | Activities; customer segments; participant roles; upstream/downstream dependencies; infrastructure; suppliers/platforms; economic flows | Conceptual functions are not actual contracts, named customers or current bank participation. Each typed relationship needs its own support. |
| **Competitive positioning** | How comparable firms differ | Defined strategic groups; evidenced shares/relative performance; comparable periods/entity scopes; business-model/capability alternatives | No unsupported rankings, inferred market-share gains or false peer benchmarks. An illustrative district is not an economic map. |
| **Enterprise economics** | Make, spend, earn, invest and generate cash | Reported income/revenue, cost, profit, margins, matched-period growth, capital/investment, appropriate cash/productivity data; reconciliation | Preserve Group/segment/legal entity, currency, stock/flow, reporting basis and actual/target. For banks use relevant banking definitions; do not force industrial EBITDA/FCF. Never annualise nine-month profit silently. |
| **Operating model** | How the enterprise serves customers and changes | Business divisions/brands/subsidiaries; products/journeys; processes, people, governance, accountability, operations, data/technology and delivery partners | Actual hierarchy/ownership differs from a conceptual illustration. Roles, brands and regulated legal entities are not interchangeable. |
| **Capabilities and technology** | Which capabilities support or constrain choices | Evidenced estate/legacy, data foundations, AI, cyber/resilience, programmes, suppliers/dependencies, delivery constraints and outcomes | A programme is not a demonstrated capability gap; an AI announcement is not effective deployment; no arbitrary maturity rating. |
| **Leadership and decisions** | What is stated, inferred, decided and still uncertain | Attributable dated leader statement or authorised corporate report; role-at-time; actual decision rights; commitments; alternatives; ownership and open-choice evidence | Never infer a named leader's belief or buying authority. Role hypotheses remain hypotheses. Announced strategy may already have allocated delivery. |
| **Relational SWOT synthesis** | Which internal conditions and external developments interact? | Scope-specific strengths/weaknesses and opportunities/threats, links to prior analyses, tensions, alternative explanations, possible choices | Research gaps are not enterprise weaknesses. SWOT Opportunity is a strategic possibility, not a sales Opportunity. Empty quadrants are valid. |
| **Leadership Agenda** | Which issues deserve executive attention and investigation? | Evidence-backed issue, consequence, roles, decision, known/unknown choices, counter-evidence, next learning action and source dates | A shared synthesis of the same scope/cutoff across streams; no issue per headline, no padded agenda or weighted score. |
| **Conditional techniques** | Which further analysis would change the decision? | Benchmarking; journey/gap/dependency/concentration analysis; scenarios/sensitivity; options/trade-offs; stakeholder/influence; transformation portfolios | Invoke only when needed and inputs are eligible. Do not introduce a tab or engine per technique. Scenario/formula implementation belongs to #611, influence to #604. |

PESTLE explains external conditions. Five Forces explains competitive economics. Value chain explains operating/economic transmission. Enterprise analyses explain actual subject exposure and response. SWOT relates them into strategic tensions. Leadership Agenda communicates issues and choices. These layers complement rather than replace one another.

## Scope and transmission

A proposed analytical link must retain **from-scope, to-scope, source period, effective/publication/observation/review time, evidence references, relationship type, claim class, inference rationale, counter-evidence and an applicability test**. Source-backed endpoints do not establish the edge between them.

A typical inspectable path is:

```mermaid
flowchart LR
 S[Source / existing Evidence] --> O[Existing Observation or labelled public candidate]
 O --> P[PESTLE development]
 P -. conditional exposure .-> F[Defined industry Five Forces / economics]
 F -. mechanism to test .-> V[Value-chain activity]
 V -. exact entity dependency required .-> E[Enterprise exposure]
 E -. labelled interpretation .-> W[Relational SWOT]
 O --> I[Strategic Issue view]
 W --> I
 I --> A[Shared Leadership Agenda]
 A --> Q[Specific commercial investigation]
 Q --> G[Existing Offer approval / shared matcher / customer validation]
 G --> H[Existing human-reviewed Pipeline service]
```

Dashed edges can be **unknown** and cannot be used as eligible support for a strong conclusion. A company-stated strategic priority may independently support an agenda question while a broader macro-to-company mechanism remains unresolved. Do not force every issue through every framework; the worked traces include explicit blocked edges and shorter direct-source paths.

Scope is not inferred from names. A public Banking reference is not a private imported Enterprise Model. Country/industry/enterprise rights and verified access are checked by the existing owning services before composition, counting, caching, export or rendering. No cross-tenant agenda cache. Sharing the public view across streams never authorises private seller notes.

## Truth and pain

Preserve the original owner authority and status, alongside a presentation classification:

1. **Fact:** eligible evidence of a statement/event/measure with its exact verification scope. A company disclosure is not independently verified effectiveness. Pilot `source_supported` is still public candidate intelligence, not an accepted canonical Observation.
2. **Interpretation:** an explicit argument from eligible inputs, with assumptions, scope and alternatives.
3. **Hypothesis:** a falsifiable condition/consequence/need requiring further evidence or customer proof.
4. **Recommendation:** a proportionate next action. Incomplete lineage permits investigation/learning, not provider pursuit or a strong sales claim.

A demonstrated pain point requires suitable direct evidence of an adverse business consequence in the correct entity/period. Otherwise it is an unvalidated hypothesis, or no pain claim is admitted. A cost target, generic threat, missing research, big programme or announcement is insufficient. The Lloyds examples contain **no demonstrated current cost-to-serve pain**.

Existing qualified Material Pressures may contribute when authorised and current, with ADR-026 gate outcomes, evidence, identity, Unknowns and Contradictions preserved. SI-1 neither runs nor recreates qualification. In particular, `offers.assess_fit`'s `material_pressure` field contains authored Offer trigger text; it is not a qualified pressure reference.

## Strategic Issue / Leadership Agenda view contracts

These are **proposed presentation contracts**, not accepted canonical schemas, object paths or state enums. They refine a future read-only adapter/Presentation Model under existing validation and owner review.

| Concern | Required view contract |
|---|---|
| Context | Existing identity owner/reference; country, industry, enterprise/legal perimeter; audience/verified scope; source cutoff and dependency release/digests; editorial policy/version. |
| Identity | A reproducible *view reference* for scope + concern + relevant decision/horizon; never a new durable Issue ID. Source IDs alone do not define issue identity. Group duplicates through reviewed concern/decision semantics, not keywords. |
| Issue | Clear business title; why it matters; specific consequence and materiality argument; fact/interpretation/hypothesis/recommendation classes; original authority/status. |
| Leadership | Stated priority versus FLORA-derived issue; attributable corporate report or named speaker/role-at-time evidence; proposed role hypotheses separately; no invented named buyer. |
| Analysis | Relevant PESTLE factors, market forces, value-chain activities, strengths/weaknesses and opportunities/threats; each statement/edge independently supported or explicitly inferred/unknown. |
| Pain | Demonstrated adverse consequence + eligible refs, unvalidated hypothesis, or no claim; no automatic strategic-issue-to-pain conversion. |
| Decisions | What is known committed; unresolved choices; owner/alternatives/internal/incumbent coverage; influence evidence or Unknown; no guessed sourcing dates. |
| Challenge | Counter-evidence, contradictions, unknowns, stale/superseded input indicators, what would falsify/change this view. |
| Action | One specific next investigation, required source/customer proof and role to validate. Seller-specific Offer fit/access/qualification stays in existing private owners. |
| Agenda | Ordered eligible issue views for the same scope/cutoff, normally 3–5 only if support warrants; zero/fewer valid; qualitative rationale and exclusions inspectable; no arithmetic score. |
| Lineage | Original Evidence/Observation/candidate/source IDs and immutable versions/locators, temporal axes, rights/verification extent, trace edge rationales and challenge. |

Ordering is editorial and qualitative: evidenced strategic consequence and decision relevance, currentness, relevance of unresolved choices and material uncertainty. These are separate reasons, not weights. A large number, recent headline, seller preference or unknowns count cannot force admission or ranking. Explicit owner pinning/reordering, if later implemented, is labelled human input under ADR-004.

The same scope/cutoff agenda must be identical in Inside, Landscape and Forces. A seller/employer-specific next play is a separately authorised projection over that agenda and an approved private Offer, not a rewritten public issue. No public projection contains customer attestations or seller qualification data.

## Temporal, contradiction and update contract

Keep event/effective time, reporting period, publication time, original retrieval/review time, source cutoff and rendering time distinct. Unknown dates stay unknown. Repeated sources and syndication do not create independent corroboration. Source rights and original excerpt extent travel with each reference; no full article archive or new redistribution right is implied.

Proposed read-only recomputation uses the authorised dependency snapshot and policy version; records why the view changed and can display stale/contradicted/missing-input explanations without mutating source owners. Reproduction requires source release/digest, scope, cutoff and policy. No SI-1 runtime recomputation is implemented.

A contradiction about applicability/consequence prevents a strong issue or pain claim. Unresolved sources may remain as a question with the conflict visible. Unknowns are not silently filled. Superseded facts remain historical; old Curve proposed-acquisition references cannot overrule the later completed-acquisition statement.

Future News (#614) contributes dated, rights-eligible evidence/Observation candidates through existing intake and scope review. It may strengthen, challenge or suggest a research candidate for an existing issue; it does not create a new truth owner or a new pain point per headline. Ripple (#597) can later flag affected public views and private records through existing dependencies. It must not rewrite seller notes, customer attestations, historical tiers, approval, decisions or Pipeline stage.

## Conditional techniques and decision use

- **Benchmarking:** only comparable entity/segment, accounting definition, currency and period. Missing competitor metrics prevent rankings.
- **Customer journeys:** use actual journey/outcome evidence; conceptual maps remain explanatory. Do not invent customer friction.
- **Capability gaps:** distinguish stated capability, observed effectiveness and evidenced shortfall. Existing strengths can defeat an Offer thesis.
- **Dependencies/concentration:** named relationship and scope first; no contract, criticality, spend or lock-in inferred from logos.
- **Scenarios/sensitivity:** future #611 owns formulas/private assumptions. No default invented bank income/cost decomposition or benefit calculation in SI-1.
- **Strategic options:** show internal, incumbent, process-only, defer/monitor and external alternatives; state evidence needed to distinguish them.
- **Stakeholder/influence:** role hypotheses and exact remaining decision, not guessed named beliefs or an automatic early window. #604 owns further influence policy.
- **Transformation portfolios:** separate programme importance, phase, decision commitment and external need; no duplicated deal values.

## Commercial boundary

Investigation → existing employer/Offer approval → existing shared matching (`offers.assess_fit`) / buying-trigger interpretation → reviewed private shortlist and seller development → real customer evidence → existing qualification → explicit authorised Pipeline hand-off. Source and Offer staleness remain visible throughout. Ten Pipeline criteria and origin/CSRF/ACL/idempotency/audit controls stay with their current services.

A shared issue does not prove seller capability, access, customer need, funding or an influence window. Customer-attested qualification-input completeness is distinct from independently verified buyer need and opportunity accuracy. Owner forensic logic belongs to #600 / existing assurance work, not default seller copy.

## Architecture alternatives and acceptance boundary

A is sufficient for v1's cross-stream synthesis, inspectable reasoning and no-write experience proof. A later durable representation is justified only if governed issue-specific history, accountability or collaboration cannot be carried by existing Observation/Twin/Presentation or private seller-record owners. Then a narrow proposal must define ownership, identity/singularity, temporal/contradiction lifecycle, ACL, retention, reconciliation and migration, and obtain Chief Architect review **before** canonical contract/runtime implementation. No durable Strategic Issue contract is approved here.

SI-1 ends with this model, a capability/evidence ledger, sourced/conditional proof traces, an isolated prototype, independent critique and tests. Owner architectural and visual acceptance is required before NEWS-1 implementation or any lasting model/runtime change. The seven accepted illustrations, current application navigation, research and Pipeline owners remain unchanged.
