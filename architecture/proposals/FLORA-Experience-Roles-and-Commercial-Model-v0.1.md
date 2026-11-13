# FLORA — Experience Roles, Professional Lenses and Long-Term Monetisation

**Strategic product and architecture proposal — version 0.1**  
**Date:** 13 November 2026  
**Status:** Proposed / discussion paper, not accepted architecture or a live subscription product  
**Owner:** FLORA / CIOS  
**Sequencing:** Preserve the current Offer-to-Sales v2 Sprint A (Issue #587). Defer implementing this proposal until that work is reviewed and a separate role-architecture pilot is authorised.

## Executive summary

FLORA can serve substantially more users than a technology-sector salesperson by separating its **shared industry and enterprise intelligence** from **role-specific experiences**, **commercial entitlements**, and **security authority**.

A user chooses a purpose — for example Educator, Researcher, Business Development & Sales, Technologist, Clean Energy, or Social Value — through a minimal “My FLORA” account control. The selected experience changes which questions FLORA foregrounds, which visual lenses are relevant, what navigation appears and which next actions are offered. It does not alter underlying facts or grant access to private data. Users may hold several interests and select one active experience at a time.

This makes possible a broad free discovery and education experience, paid specialist individual subscriptions, premium Sales & Business Development tools, and enterprise/team agreements. The same continually improved Industry and Enterprise intelligence becomes valuable to multiple user segments.

**Proposed principle:** One intelligence foundation; many purposeful experiences; an explicit permission and payment boundary.

## 1. Why this matters

Today's FLORA emphasises commercial opportunity discovery and an Offers/Pipeline workflow. That is a compelling premium use case, but a narrower addressable audience than the total population who need to understand industries, enterprises and economic change.

Role-aware experiences could:
- make onboarding understandable (“What do you want to achieve?” rather than a catalogue of technical modules);
- reduce interface clutter by foregrounding the two or three things that matter to a given user;
- improve retention: an educator returns for teaching material, a researcher for comparisons, a salesperson for buying triggers;
- grow distribution through free public and educational access without subsidising unlimited expensive compute;
- enable modular pricing based on professional value, usage and collaboration rather than arbitrary access to a page;
- support international growth by composing the same country/industry/enterprise intelligence differently for local audiences.

**Important caution:** Additional role names do not equal products. Each paid role must offer meaningful differentiation, supported data and outcomes users would pay for. The strategy is a hypothesis requiring market validation.

## 2. The distinct architectural concepts

| Concept | Question answered | Example | Authority |
|---|---|---|---|
| Experience role / lens | What is the user trying to achieve? | Educator; Sales | User preference, not security role |
| Active mission and preferences | What specifically matters to them? | UK banking, cloud, named accounts | Personal or authorised workspace context |
| Subscription plan / entitlement | Which purchased or granted features, quotas and seats are available? | Free education, Sales Pro | Billing/entitlement authority (future) |
| Security permissions | Which records or actions may this user legally/operationally access? | View own offers; approve employer catalogue | Existing verified sessions, workspace membership and capability checks |
| Intelligence truth | What evidence, observation and interpretation exist? | easyJet financials and programme signals | Existing canonical industry, enterprise, evidence and source owners |

The distinction is non-negotiable. **Choosing “Sales” must not grant commercial_context.view, access to another seller's Offers, a Pipeline write or an employer approval right.** Likewise buying a Sales subscription never bypasses authenticated workspace/enterprise permissions. Changing experience lenses must not change evidence, claim status or canonical Twin state.

An experience role is not an employment title, an IAM role, a qualified professional licence or a claim of subject-matter competency. The name **Experience** or **Focus** may be friendlier in the consumer UI than “Role”.

## 3. Candidate experience-role portfolio

The following portfolio is deliberately broad. **Do not launch every experience at once.** The role groupings are candidate product-market segments, not a claim that all underlying features exist.

| Experience | Core user and jobs-to-be-done | FLORA lens: priority questions and tools | Potential monetisation |
|---|---|---|---|
| **Explorer / Curious Learner** | Anyone seeking a clear view of economies and industries | Beautiful country scenes, industry fundamentals, accessible enterprise summaries and visual PESTLE | Free discovery; capped expensive operations |
| **Educator / Student** | Teachers, lecturers, students, training providers | Guided sector lessons, comparative business case studies, learning pathways, classroom-safe exercises, downloadable teaching packs | Free individual educational tier; institution licensing for class/administration features |
| **Researcher / Analyst** | Independent researchers, market researchers, think tanks | Deeper evidence, methods, source provenance, comparative dashboards, export and reproducible analysis | Free limited research; paid professional depth and exports |
| **Business Development & Sales** | Sales executives, capture leaders, account managers, consultancies | My Company, Offer Library, customer signals, trigger/entry-play matching, target accounts, opportunity shaping and Pipeline | Premium individual and team subscription |
| **Technologist / Architect** | CTO/CIO advisers, solution architects, product technologists | Capability landscapes, suppliers, technology dependencies, architecture trade-offs, adoption barriers and futures | Specialist professional subscription; team tier |
| **Founder / Product Strategist** | Founders, product leaders, innovators | Market structure, underserved needs, adjacent capabilities, product-market hypotheses and partner discovery | Founder/Pro tier, with bounded early-stage access |
| **Investor / Corporate Development** | Public/private investors, strategy and M&A professionals | Industry scale, financial comparisons, competitive dynamics, scenarios, acquisition/partnership intelligence | Higher-value specialist subscription, depending on data licence |
| **Clean Energy & Sustainability** | Transition researchers, energy strategists, sustainability advisers and advocates | Energy systems, emissions and environmental pressures, transition pathways, regulatory developments, technology choices | Free public-interest lens plus professional impact/analysis tier |
| **Social Value & Inclusion** | Social-value practitioners, public-benefit analysts, community/ESG teams | Skills, labour markets, jobs, community outcomes, procurement social value, inclusive supply chains | Free public-interest lens plus organisation/reporting tier |
| **Public Policy / Regulation** | Civil servants, policy analysts, policy advisers, regulators | National vs global PESTLE, regulations and proposals, policy effects, affected industries and alternatives | Public-sector/institution agreements; some open-access content |
| **Procurement / Commercial Buyer** | Enterprise procurement leaders and commissioning teams | Supplier-market maps, capability comparisons, dependency and delivery risks, sourcing options | Enterprise-team tier |
| **Operations / Transformation Leader** | COO, CIO, transformation directors and advisers | Enterprise performance, cost pressures, operating models, reinvention pathways and implementation economics | Executive / Enterprise Pro |
| **Academic / Scientific Innovator** | Universities, research partnerships, frontier specialists | Research ecosystems, collaborations, technical adoption, funding/programme mapping | Education/research grants; professional partnership tier |
| **Workforce / Skills Leader** | HR, learning providers, workforce planners | Skills transitions, employment, industry workforce demand, training opportunities | Professional/institution licences |
| **Journalist / Industry Communicator** | Specialist journalists and professional communicators | Fast explainers, sourced chronology, comparisons and visual storytelling | Free limited access; paid publishing tools where licensed |
| **Ecosystem / Partner Development** | Alliances, channels, vendors and market development teams | Partner/supplier maps, adjacent offers, channel access, account compatibility | Professional or enterprise tier |
| **Economic Development / Local Growth** | Local authorities, chambers, development agencies | Regional sector scale, jobs, investment, enterprise clusters and transition opportunities | Institution/public-impact tier; only when geographic data are credible |

### Role-family consolidation

To avoid a bewildering first-run picker, initially group the experiences under six human-readable motivations:
1. **Learn** — Explorer, Educator & Student.
2. **Research** — Researcher/Analyst, Journalist, Academic.
3. **Sell & Grow** — Sales, Founder/Product, Partnerships.
4. **Build & Transform** — Technologist, Operations/Transformation, Procurement.
5. **Invest & Advise** — Investor, Corporate Development, Professional Adviser.
6. **Improve Society** — Clean Energy, Social Value, Public Policy, Skills, Economic Development.

A user chooses a high-level purpose first; optional specialisms appear later. No one should be asked to complete a sixteen-question onboarding form. Start with a small selectable set of most relevant experiences and a “More interests” option.

### Difference between professions and thematic interests

Researcher, Educator and Sales are largely *workflow roles*. Clean Energy, Social Value and AI may also be *thematic lenses* usable by a researcher or salesperson. Architecturally, prefer two orthogonal dimensions:
- **Purpose / workflow:** Learn, Research, Sell, Build, Invest, Influence/Improve.
- **Topics / causes:** Clean Energy, Social Value, AI, Cybersecurity, Health, Finance, etc.

A clean-energy researcher should not have to choose between being a Researcher and an Advocate. The combined view can be composed without proliferating product-specific logic. Neutrality matters: an advocate lens may foreground a legitimate goal, but cannot suppress counter-evidence or misrepresent unsettled policy or impacts.

## 4. What the interface would do

The approved FLORA visual design remains the product foundation: one compact header alongside the FLORA brand and image-native country, industry, enterprise and PESTLE views.

At the far-right account control, **My FLORA** offers:
- Switch experience (one active at a time), with remembered favourites.
- My interests and markets, including active country vs seller territory.
- My plan and usage (when billing is implemented).
- Workspace and organisation switch (existing verified authority only).
- Account settings and help.

Switching changes navigation prominence, allowed presentation lenses, default discovery route, saved personal filters, suggested next actions and tailored onboarding — **not** stored research facts or permissions.

### Illustrative navigation

| Active experience | Foregrounded destinations |
|---|---|
| Educator | Home · Industries · Enterprises · Learn |
| Researcher | Home · Industries · Enterprises · Research · Compare |
| Sales | Home · Industries · Enterprises · Offers · Opportunities · Pipeline |
| Technologist | Home · Industries · Enterprises · Technology Models |
| Clean Energy | Home · Industries · Enterprises · Energy & Transition |
| Social Value | Home · Industries · Enterprises · People & Social Impact |

Only show destinations the user both **has a plan entitlement to use** and **is authorised to access**. Hiding a route is UI convenience, not the security boundary. Direct URL access remains checked server-side.

### One enterprise, six interpretations: easyJet (conceptual)

- **Educator:** airline economics, operating model, how competition and regulation affect decisions; an interactive case study.
- **Researcher:** independently sourced financial measures, supplier relationships, timelines, alternative interpretations.
- **Sales:** match the seller's approved Offers to supported easyJet signals, potential entry plays and an optional authorised Pipeline journey.
- **Technologist:** fleet/operations data dependencies, major technology choices, integration and resilience.
- **Clean Energy:** aviation energy transition, emissions sources, credible options and dependencies; no unverified decarbonisation claims.
- **Social Value:** workforce, skills, community and supplier outcomes where sourced; no invented impact figures.

All of these views point to the same governed enterprise/industry state. Where a specialised evidence basis has not yet been researched, the UI should simply omit unsupported claims or show an honest, low-clutter invitation to explore existing content, not fabricate a role-specific analysis.

## 5. Commercial and monetisation design

A freemium ecosystem is promising, but should be validated commercially, not adopted as an ideological commitment.

### Candidate offer architecture (no actual price commitments)

| Tier / packaging hypothesis | Who it serves | Experience features | Commercial mechanism |
|---|---|---|---|
| **FLORA Discover (Free)** | Explorers, students, interested public | Country/industry visuals, selected public enterprise content, basic PESTLE | Free, fair-use limits, restricted expensive exports/research |
| **FLORA Education** | Teachers, eligible students/institutions | Guided learning, case studies, classroom packs, education workflow | Free verified individual usage where sustainable; paid institution management where useful |
| **FLORA Research Pro** | Researchers, analysts, journalists | Advanced comparisons, citations, saved collections, controlled exports and research depth | Individual monthly/annual |
| **FLORA Sales Pro** | Sales and business-development professionals | Offer Library, triggers, entry plays, targeted discovery, private workspace/Pipeline | Premium per seat or annual plan |
| **FLORA Specialist Pro** | Technologists, clean-energy, social-value, procurement and policy professionals | Domain-specific models, depth and specialist workflows | Modular vertical add-ons or one profession tier |
| **FLORA Enterprise / Institution** | Corporate teams, universities, public-sector bodies | SSO, seats, permissions, shared workspaces, governance, approved collaboration, admin and usage controls | Organisational contracts |
| **Optional high-compute add-on** | Heavy researchers and power users | Bounded intensive collection, AI research/analysis and volume export | Metered credits/quotas with explicit costs and limits |

**Role selection is free; specialist feature use may require a plan.** Avoid charging people just for choosing “Sales” or for switching roles. A subscription may enable several experiences; enterprise seats may grant more than one.

Potential routes to monetisation also include approved professional datasets, API/embedding licensing, institutional curricula, carefully governed expert workflows and industry-specific analytical products — all subject to data rights, compute cost and partner terms. Do not assume reselling source data is permitted.

### Illustrative commercial mechanics

Consider modelling the contribution margin of each tier as:
**net subscription revenue − research/AI inference − data licences − hosting/operations − support/payment costs − attributable acquisition cost**.

Key hypotheses to validate:
- conversion from a free useful industry experience into paid role-specific workflows;
- why a salesperson pays more than a casual learner (business-critical decision support and private workflow);
- whether Education creates meaningful distribution without disproportionate cost;
- specialist Pro willingness-to-pay and retention;
- enterprise seat expansion, team collaboration and lower churn;
- usage cost exposure and abuse risk of free or heavily automated research.

Do not set firm market prices, free quotas, sales conversion percentages or projected revenue without evidence from pricing research and real user testing.

## 6. Product and security architecture

### Proposed capability boundaries

1. **Experience Profile (new user preference projection):** selected purpose, optional thematic interests, country preference, presentation depth and favourite experiences. Scoped to authenticated user; anonymous preference, if offered, must not cross security boundary. Versioned and minimal.
2. **Experience Registry:** versioned manifest specifying user-friendly role names, relevant modules, navigation slots, default lenses and onboarding instructions. No hardcoded bypasses.
3. **Entitlement Service (future):** plan, trial, quotas, add-ons, organisation seats and expiry, with fail-closed server-side feature checks; independent of verified IAM permissions.
4. **Experience Composer:** read-only renderer over existing authorised intelligence, Commercial Mission, Market Participant/Enterprise/Industry twins and available feature projections. It composes views, not new truth.
5. **Existing Security Authority:** verified sessions, workspace membership, enterprise scope, capability checks, employer approval separation, audit, CSRF and protected journals remain the sole authority for private data/writes.
6. **Usage/Cost Meter:** privacy-aware event counts, per-capability compute/data cost, limits and spend alerts. No conversation or personal research content should be unnecessarily logged.
7. **Billing Adapter (future):** provider-agnostic interface for plans, purchase verification, cancellation, refunds, tax/VAT, trials and enterprise invoicing, without storing payment-card data in FLORA.
8. **Learning and Feedback:** optional, consent-aware experience feedback; distinguish product analytics from canonical evidence and never use individual activity to assert commercial facts about an enterprise.

### Access decision

A request may proceed only if all conditions relevant to it are met:

**authenticated identity (where required) AND verified workspace/enterprise permission AND valid plan entitlement/limit AND domain-specific policy (e.g., approved offer, evidence, review, Pipeline stage).**

This is additive to the existing access model, not a replacement. If a user switches away from Sales, their private Offers/Pipeline remain intact and protected; switching back restores the view if entitlement and authority remain valid. Purchased access never grants workspace membership. Billing outages must not silently permit protected writes.

### Compatibility with existing architecture

This concept extends:
- **FP-014** Mission-Aware Executive Intelligence Composition (currently proposed): mission affects relevance and presentation, not evidence truth;
- **FP-003** FLORA Intelligence Architecture: canonical source → evidence → observation → hypothesis chain;
- **CommercialMission / EmployerContext:** seller-specific commercial purpose and authorised employer context;
- **navigation.py and the unified visual shell:** one top navigation, progressive disclosure and image-native interaction;
- **offers.py / Offers v1 and Pipeline:** Sales-specific catalogue, matching, authorisation, version and qualification boundaries;
- existing Market Participant, Enterprise, Industry, Knowledge Pack and assessment ownership.

Avoid inventing a new canonical Role Twin, parallel evidence repository or a second Pipeline permission service. The primary implementation gap is a *presentation and entitlement* layer, not a new enterprise truth layer.

### Multitenancy and licensing constraints

Public/educational views must never embed private commercial context in HTML, caches, search results, exports or logs. Account and employer data stay isolated even if a user moves among roles. Role-specific cache keys must include authorised viewer, market, scope, entitlement and source-version factors where relevant. Respect copyright, data-source publication permissions, contract terms and public-sector accessibility obligations.

If school-age students may be served, age-appropriate privacy, child-safety, institutional administration and education-specific legal requirements need separate assessment before launch; do not rely on unverified student status.

International expansion requires regional payments/taxes, market access policy, language, time zone, country-specific educational and regulatory content and clear separation between global PESTLE and local applicability. Professional roles alone do not prove qualifications or legal authority to give regulated advice.

## 7. Governance and editorial neutrality

The same research must remain truthful across roles. In particular:
- advocacy experiences may emphasise clean energy or social value, but preserve material counter-evidence, competing interventions and uncertainty;
- investor and finance experiences must not silently claim to provide regulated investment advice;
- educational content must distinguish confirmed facts, scenarios, debated policy and exercises;
- Sales must not turn a signal into a fabricated procurement or buyer intent;
- sources and methodology are available on demand without repeated “inspect evidence” prompts;
- estimated numeric outputs carry **EST** and a defensible basis/range; unsupported data are omitted rather than filled with false precision;
- a role's prominence/ranking decisions should be explainable and configurable, not manipulate facts for conversion.

Pricing and feature gating should be transparent and respectful: no deceptive paywalls, artificial urgency or surprise compute costs.

## 8. Pilot recommendation and phased roadmap

**Phase 0 — market discovery (parallel to future roadmap planning, no runtime):** 12–20 qualitative interviews across educators, researchers, sellers and technologists; define specific jobs, willingness-to-pay, alternatives, data cost and regulatory requirements. Test whether Clean Energy/Social Value behave more like thematic interests than distinct paid profession roles.

**Phase 1 — minimal Experience Profile:** prototype **Educator** and **Business Development & Sales** using the same UK visual industry and easyJet enterprise example. Put role choice in My FLORA; show different primary navigation and one or two meaningful work experiences. No billing yet. Use existing auth and permission checks unchanged. Add Researcher as a useful third comparison if economically feasible.

**Phase 2 — entitlement proof:** introduce a bounded test entitlement/feature manifest that gates premium **functions** server-side, with plan/source/admin approval and no billing integration or recurring charge. Prove direct URLs cannot bypass gates and role switching cannot leak restricted data.

**Phase 3 — commercial experiments:** instrument privacy-conscious cost/activation/retention, test Education eligibility and fair-use; research actual pricing and run consented user pilots. Only then select paid plans and a compliant payments provider.

**Phase 4 — expanding specialist lenses:** Technologist, Researcher Pro, Clean Energy/Social Value thematic overlays, Investor/Founder and Institution tiers according to validated demand and suitable evidence coverage. Extend internationalisation progressively.

**Phase 5 — team and ecosystem monetisation:** organisation subscriptions, shared experiences, licensing or API offerings where rights and demand justify them.

## 9. Acceptance criteria for later implementation

- A first-time user can choose “Learn” or “Sell” in a simple first-run interaction; their Home and nav adapt accordingly.
- Switching role never creates a new security principal, grants an entitlement, joins an employer, changes canonical research or creates Pipeline records.
- Educator lacks distracting Offers/Pipeline links by default and cannot access paid/restricted routes via URL without both entitlement and permissions.
- A Sales-enabled user sees Offers, triggers, entry plays and Pipeline only if their plan AND existing authority allow them.
- Both roles display the same sourced easyJet financial facts with consistent geography/period; differences are solely in relevant interpretation and permitted actions.
- Public/anonymous/education sessions cannot access private seller/employer information through HTML, cache, APIs or exports.
- A denied paid feature produces a clear upgrade explanation, not a security role grant or destructive account mutation.
- The one-header/image-first design is preserved across desktop, iPad and mobile.
- Security, audit, existing ownership, evidence status and Pipeline approvals remain unchanged.
- Usage and cost are measurable, with consent/privacy and limits, and trials do not permit unchecked paid-model spend.

## 10. Open architectural decisions

1. **Role taxonomy:** Are Clean Energy/Social Value best implemented as topical overlays? **Recommendation: yes, initially**, alongside professional workflow roles.
2. **Multi-role:** One active experience plus saved other interests, or a merged interface? **Recommendation: one active experience**, with multiple saved interests to avoid UI clutter.
3. **Organisation versus personal experience:** An individual may be a researcher while working for a Sales organisation. **Recommendation: personal display preference; organisation-managed licences and data permissions remain independent**.
4. **Education:** Is Free Education open self-declared, verified, or institution-sponsored? **Recommendation: pilot limited free individual research, then validate eligibility/administration before material free compute allocation**.
5. **Payment packaging:** Profession tiers versus modular add-ons? **Recommendation: research buyer needs and unit economics before selecting prices or hard rules**.
6. **Advocacy neutrality:** How to avoid role-specific selection bias? **Recommendation: shared evidentiary corpus, alternative viewpoints and visible methodology on demand**.
7. **Country scope:** Whether role preferences travel across markets or apply per country. **Recommendation: global purpose preference with country-specific contextual filters and entitlements**.
8. **Entitlement failure policy:** What happens after expiry, billing outage or abuse? **Recommendation: preserve user records, limit premium functionality and never silently elevate access**.

## 11. Decision requested later, not now

Approve the strategic distinction between **Experience Role**, **Theme**, **Entitlement** and **Security Permission**. Then authorise a narrowly scoped role-personalisation design pilot with Educator and Sales before building pricing/billing infrastructure.

**No immediate implementation is proposed while Offer-to-Sales v2 Sprint A is running.** This document is a durable option for the next architecture discussion, not a directive to modify the live platform.

## 12. References within FLORA

- [FP-014 — Mission-Aware Executive Intelligence Composition](../founding-papers/FP-014-Mission-Aware-Executive-Intelligence-Composition.md) — proposed mission-aware rendering, with stable governed evidence.
- [FP-003 — FLORA Intelligence Architecture](../founding-papers/FP-003-Flora-Intelligence-Architecture.md) — observation, signals and commercial hypothesis chain.
- [Market Participant Twin specification](../specifications/market-participants/Market-Participant-Twin-Specification-v1.0.md) — offerings, account-relative strength and source lineage.
- [Account-Participant Position Assessment](../specifications/market-participants/Account-Participant-Position-Assessment-Specification-v1.0.md) — fit, access and competition.
- [Current primary navigation](../../cios/applications/flora/navigation.py) and [Commercial Mission](../../cios/applications/flora/commercial_mission.py).
- [Existing Offers v1](../../cios/applications/flora/offers.py) — private employer/seller offers and shared matching.
- [FLORA Offers v2 Sprint A](https://github.com/rdidale-jpg/CIOS/issues/587) — in-progress separate work.
