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


## Appendix A — Tools and repeat-value engines by experience (proposed 13 November 2026)

**Product design test:** For every experience ask: *What durable object does a user maintain, what changes between visits, what meaningful action can they take, and why might they pay?* Avoid generic newsfeeds and artificial check-in incentives. These are concepts to validate, not features delivered in current FLORA.

### A1. Sell & Grow

| Role | Signature tool and persistent object | Repeat-value trigger | Potential premium value |
|---|---|---|---|
| Business development / strategic sales | **Opportunity Factory:** seller-selected Offers → target-account signals → buyer hypotheses → entry plays → qualification → governed Pipeline | New evidence, changed prospect fit, introduction, pursuit stage or milestone | Ranked, explainable opportunity pipeline and account plans |
| Account / client director | **Account Growth Map:** relationships, business units, installed services, whitespace, renewal horizon and expansion hypotheses | Account event, service performance, stakeholder change, renewal milestone | Expansion and retention planning |
| Founder / product strategist | **Market Opportunity Studio:** problem clusters, underserved segments, competitors and product-market hypotheses | Change in demand/competitor offerings, customer experiment result | Product decisions and experiment prioritisation |
| Alliance/channel development | **Partner Opportunity Map:** complementary offers, partner strengths, account access, channel conflicts and joint plays | Partner announcement, joint opportunity, alliance renewal | Co-sell planning and partnership pipelines |

**Sales north-star:** qualified, seller-reviewed pipeline created or progressed from FLORA-recommended commercial plays, with attributable evidence and user confirmation. Do not count unvalidated hypotheses as real pipeline.

### A2. Learn

| Role | Signature tool and persistent object | Repeat-value trigger | Potential premium value |
|---|---|---|---|
| Educator | **Living Case Study Builder:** industry/enterprise cases, learning objectives, exercises, teacher notes and presentation-ready visual journeys | Next class, case update, assignment or curriculum cycle | School/institution lesson packs, class management, educator collaboration |
| Student | **Industry Learning Path:** industry maps, enterprise case missions, quizzes, feedback and personal mastery record | Next module, examination topic, project milestone | Free basic learning; optional advanced guided study under transparent limits |
| Explorer | **My World Atlas:** saved markets, comparative journeys, clear economic explainers | Material world change or personal curiosity | Free acquisition funnel, not forced daily use |
| Workforce/skills leader | **Skills Transition Mapper:** role changes, industry workforce trends, learning and redeployment pathways | Industry skills shift, workforce planning review | Organisational planning and reporting |

**Learning north-star:** meaningful learning outcome (teacher-ready lesson deployed, assessment completed or improved demonstrated understanding), not clicks or time on site. Exercises must not invent business facts.

### A3. Research

| Role | Signature tool and persistent object | Repeat-value trigger | Potential premium value |
|---|---|---|---|
| Researcher / analyst | **Living Research Notebook:** question, tracked industry/enterprises, evidence, comparison, hypotheses, counter-evidence and reproducible report | Source update, contradiction, report deadline, new comparable data | Deep source access, exports, larger monitored research universe |
| Academic / scientific innovator | **Research Ecosystem Explorer:** research programmes, institutions, collaborators, technologies and funding/publication evidence | New grant, paper, programme or collaborator | Specialist collaboration intelligence, institutional access |
| Journalist / communicator | **Change & Claims Desk:** sourced chronology, cross-check, comparisons, factual explainer and exportable visual | Verifiable material development and publishing deadline | Professional source trails, citations and publishing assets |
| Policy researcher | **Policy Impact Tracker:** proposal vs effective law, affected markets, alternative scenarios and impact hypotheses | Consultation, law commencement, amendment or review | Policy dossiers and jurisdiction-specific comparison |

**Research north-star:** source-backed decisions or reusable completed research products, with stronger quality and less analyst time; reject volume-only metrics and fabricated certainty.

### A4. Build & Transform

| Role | Signature tool and persistent object | Repeat-value trigger | Potential premium value |
|---|---|---|---|
| Technologist / enterprise architect | **Technology Landscape & Decision Studio:** reference architecture, dependency map, product choices, trade-offs, technical debt and option decision log | New architecture constraint, vendor release, programme design gate | Technology decision support and team collaboration |
| CIO / transformation director | **Transformation Portfolio Navigator:** operating-model baseline, capability maturity, initiative dependencies, measurable benefits and delivery risks | Programme milestone, revised financial or technology pressure | Portfolio decision support and benefit tracking |
| Procurement / commercial buyer | **Supplier Market & Sourcing Mapper:** supplier capability/relationship evidence, route-to-market and sourcing scenario | Contract renewal, category review or supplier event | Shortlisting and supplier-market analysis |
| Operations leader | **Operational Opportunity Mapper:** process economics, dependencies, improvement hypotheses and validation plan | Cost-performance change, bottleneck or service change | Evidence-led productivity and operational transformation planning |

**Build north-star:** a decision made or initiative advanced with documented alternatives and usable evidence, not a generated diagram.

### A5. Invest & Advise

| Role | Signature tool and persistent object | Repeat-value trigger | Potential premium value |
|---|---|---|---|
| Investor / portfolio manager | **Living Investment Thesis:** watchlists, industry and company fundamentals, catalysts, thesis, challenge evidence and scenario valuation | Earnings, disclosure, sector change, thesis threshold | Comparison, valuation/scenario tools, saved monitoring and transparent risk analysis |
| Corporate development / M&A | **Strategic Target & Synergy Explorer:** market map, target fit, business economics, overlap and integration hypotheses | Acquisition/disposal, target development, market shifts | Deal-screening and corporate-development workflow |
| Professional adviser | **Client Strategy Workbench:** governed business-context comparison and recommendation drafts | Client review, regulatory or enterprise change | Repeatable client advice workflows under appropriate professional boundaries |

**Invest north-star:** validated thesis updates and decision-quality research. No claims of investment returns or regulated advice without proper authority, licensing and safeguards.

### A6. Improve Society

Clean Energy, Social Value, Inclusion and Economic Development should be selectable **themes** that can combine with different professional workflows, not necessarily mutually exclusive roles.

| Role/theme | Signature tool and persistent object | Repeat-value trigger | Potential premium value |
|---|---|---|---|
| Clean Energy / sustainability | **Transition Pathway Studio:** sector emissions/energy baseline, intervention choices, costs, timing, barriers and measured outcomes | New energy statistics, policy change, project milestone | Scenario models, reporting and stakeholder planning |
| Social Value / inclusion | **Social Impact & Outcomes Planner:** employment, skills, community benefits, interventions, KPIs and evidence of results | Procurement review, community programme update, reporting deadline | Impact tracking, reporting and multi-team collaboration |
| Public policy / regulation | **Policy Consequence Navigator:** policy change, affected industry groups, jurisdiction, competing consequences and uncertainties | Consultation deadline, draft/operative change | Comparative policy analysis and briefings |
| Regional economic development | **Regional Growth Atlas:** industries, jobs, firms, skills, investment, clusters, projects and progress | Local investment, employment release, funding call | Regional intelligence, programme monitoring and evidence-based reports |

**Public-impact north-star:** outcomes or programme decisions supported by sourced evidence. Advocacy lenses must show material counter-evidence and should not masquerade as causal impact measurement.

### A7. Cross-role reusable engines

Rather than build twenty separate applications, reuse a small set of governed product engines:
1. **Living Watchlist / Change Engine** — authorised, bounded updates on saved industries, enterprises, technologies or policies; source dates and materiality matter more than notification frequency.
2. **Model & Scenario Studio** — reusable financial, operating, technical, environmental and market scenarios with assumptions, alternatives and uncertainty.
3. **Visual Knowledge Explorer** — country → industry → enterprise → relationships with image-native insights and clean financial scale.
4. **Personal Project Workspace** — saved questions, models, decisions, next steps and a history of what changed; individual and team plans differ in sharing rights.
5. **Guided Playbooks / Journeys** — user-purpose-specific steps: teach a case, research an issue, shape a deal, design a solution, evaluate a policy.
6. **Source and Method Service** — single discreet access to evidence, provenance, dates and limitations with consistent authorization.
7. **Outcome & Feedback Recorder** — user-confirmed learning, decisions, completed reports, opportunity actions, impact metrics; never make feedback canonical enterprise truth automatically.
8. **Permissioned Alerts & Briefing** — user-controlled material-change notifications; digest by explicit cadence, respect consent, costs, privacy and legal boundaries.
9. **Export & Collaboration** — role-specific reports, slides, worksheets, case packs and approved cross-team projects, subject to source/data licences.
10. **Entitlement + Quota Layer** — independently gates costly/proprietary functions; no security permission escalation and no hidden usage charges.

### A8. Candidate cadence and retention loops

| Experience | Useful cadence | Trigger/action loop | Worth paying for when… |
|---|---|---|---|
| Sales | Daily/weekly around target accounts | New signal → entry-play review → contact/qualification → pipeline progress | It improves qualified pipeline, conversion or time-to-insight |
| Educator | Weekly/termly | Plan lesson → deliver → assess → update class material | It saves preparation time and improves learning outcomes |
| Student | Self-paced/course cycle | Study → interact → practice → feedback → next concept | Learning support is measurably useful |
| Researcher | Project-driven/weekly | Research question → new evidence → thesis update → publish/decide | It saves research time without sacrificing source quality |
| Technologist | Project milestones/events | Architecture signal → option comparison → decision/implementation | It reduces decision risk or work required |
| Investor | Earnings/events | Thesis catalyst → challenge → scenario adjustment → portfolio research action | Intelligence is timely, defensible and materially differentiated |
| Clean Energy | Policy/reporting/project intervals | New evidence → pathway revision → impact comparison → project decision | It supports a real, trusted transition decision |
| Social Value | Contract/reporting intervals | Commitments → evidence → outcomes → report/adjust | It improves credible outcome tracking and reporting |

**Do not manufacture daily activity where the authentic workflow is weekly, termly, project-driven or event-led.** Value and trust beat forced engagement.

### A9. Product-priority matrix (hypotheses to test)

Prioritise by (a) urgency and willingness-to-pay, (b) fit to existing FLORA intelligence, (c) build/research cost and source rights, (d) user retention/return value, (e) differentiated user outcome, and (f) security/compliance burden.

| Candidate | Existing-platform leverage | Likely implementation complexity | Suggested order |
|---|---|---|---|
| **Sales Opportunity Factory** | Very high: Offers, Enterprise Twins and Pipeline exist | Medium for quality; high for scalable research | 1 — continue existing Offers sprints |
| **Research Notebook + Watchlist** | High: evidence, enterprise comparisons and macro signals | Medium; monitoring cost must be bounded | 2 — reusable across roles |
| **Educator Case Study Builder** | High: visual industries and enterprise operating models | Medium; pedagogy/content QA required | 3 — contrasting free/education pilot |
| **Technology Decision Studio** | High: technology landscape and supplier ecosystem | Medium/high; technical depth and validation | 4 |
| **Investor Thesis Studio** | Medium: finance and industry context | High: data licences, timeliness and regulated-advice issues | Research before delivery |
| **Transition/Impact Studio** | Medium: PESTLE and some sector data | High: environmental/social measurement rigor | Targeted proof only |
| **Enterprise collaboration/subscriptions** | High once valuable role tools exist | High IAM, tenancy, billing, support effort | After individual value proven |

The order is a **product hypothesis**, not verified market demand or financial forecast. Interview and pilot users before committing revenue targets or pricing.

### A10. First future proof: two contrasting experiences

After Offers Sprint A and the associated sales development milestones, build a **design pilot** for:
- **Educator:** open the same UK economy and easyJet pages; create and save a short interactive business case/teaching sequence; choose an assessment and export a source-aware lesson plan.
- **Sales:** open those same pages; select an authorised Offer; review a supported customer trigger and entry play; save a commercial action and, only after qualification, progress via the existing Pipeline.
- **Researcher (optional third):** watchlist easyJet and compare its latest source-backed changes to a saved hypothesis.

Demonstrate **shared facts, different tools**. Instrument meaningful completions, retention at natural cadence and compute cost, but preserve access, evidence and data-rights boundaries. No billing implementation or new permissions until reviewed.

### A11. Long-run success measures

Avoid optimising primarily for daily-active-user counts. Prefer:
- activation: users complete their first **role-relevant valuable artifact**;
- effectiveness: opportunity progressed, case lesson delivered, thesis updated, decision made or measured impact assessed;
- retention: return on meaningful event/cadence, not nudges alone;
- conversion: free-to-paid upgrades **after** users experience a real premium need;
- economics: gross margin by tier, cost per successful artifact/active paying user, data licence burden and support cost;
- quality: evidence traceability, material error rate, user correction, abandoned work and trust metrics.

**Architecture rule:** every profession-specific tool must identify the shared FLORA intelligence objects it reuses, new durable user work artifacts it owns, who may access them and a clear outcome metric. If it cannot specify these, it is a navigation lens rather than a separate product.


## Appendix B — Integration ecosystem and API commercialisation strategy (research dated 13 November 2026)

### B1. Strategic thesis

FLORA should **orchestrate authorised external intelligence and work tools**, rather than replicate them. Its differentiated asset is the joint interpretation of `country → industry → enterprise → people/technology/financial signal → role-specific decision or action`.

Each integration must have a clearly articulated recurring job, permission/licence model, data scope, operating cost, update frequency and paying audience. An available API is not automatically a right to resell or redistribute its data.

Three separate acquisition patterns:
1. **Open/public-data connectors:** authoritative statistical, research, corporate-registry, procurement and energy data; verify source licence, attribution, limits and historical revisions.
2. **Licensed commercial intelligence feeds:** stock fundamentals, forecasts, financial prices and specialist vendor insights; negotiate redistribution, caching, display, end-user entitlements and geographic coverage explicitly.
3. **User-/organisation-authorised app connections:** CRM, Microsoft 365, teaching platforms, calendar and personal contacts; OAuth, narrow delegated scopes, workspace segregation, revocation, audit and no unauthorised cross-user inference.

### B2. Provider availability assessment — official sources

| Provider/source | Data/capability of interest | Public access assessment | FLORA potential | Constraints / official source |
|---|---|---|---|---|
| **LinkedIn** | User identity, LinkedIn career/profile context, connections, Sales Navigator-related workflow | Self-service developer scopes generally sign-in/profile/email and approved sharing; connections/Contacts and many Sales/Talent APIs **restricted** | Job seeker: known contacts around a target employer; Sales: relationship access | Ordinary Premium membership does not grant developer connection access. Partner approval, user consent and data restrictions required. https://learn.microsoft.com/en-us/linkedin/shared/authentication/getting-access and https://learn.microsoft.com/en-us/linkedin/shared/integrations/people/connections-api |
| **LinkedIn member data export** | User-supplied connections and messages for personal analysis | Data import workflow rather than live authorised LinkedIn API | Near-term user-controlled relationship graph, links back to LinkedIn profiles, update on re-import | Validate privacy, export terms, retention and identity matching; **do not** scrape, automate private LinkedIn pages or infer other members' permission. No promise of live updates |
| **Microsoft Graph** | Outlook contacts, email, events, shared contacts with delegated permissions | Documented delegated APIs | Sales relationship continuity, calendar/meeting context, job-seeker network, follow-up | Explicit OAuth consent; application vs delegated permissions differ; narrow scopes; tenant admin can restrict. https://learn.microsoft.com/en-us/graph/api/user-list-contacts?view=graph-rest-1.0 |
| **HubSpot** | Company, contact, deal, activity and relationship context | Official APIs and generally available hosted MCP interface (2026) | Bidirectional, permissioned CRM-connected Pipeline intelligence | Per-account approval and permissions; no unauthorised writeback. https://developers.hubspot.com/changelog/remote-hubspot-mcp-server-is-now-generally-available |
| **Salesforce** | CRM account/contact/opportunity objects | Established enterprise API offering; separately validate exact product scope and licence | Sales account plans, contacts, pipeline sync | Tenant permissions, API quota, data residency, CRM ownership, duplicate handling. Confirm latest official docs at https://developer.salesforce.com |
| **Investing.com / InvestingPro** | Equity prices, forecasts, fundamentals and other market information | **No public API** as explicitly stated by Investing.com; official embeds/widgets and commercial contact path | Investor visual reference or negotiated licensed access | Widgets are not unrestricted data APIs; check display and redistribution rights. https://www.investing-support.com/hc/en-us/articles/115005473825-Do-You-Offer-API-Access-at-Investing-com |
| **Armstrong Economics — Socrates Platform / Ask-Socrates** | Proprietary cyclical, capital-flow and market commentary/forecasts | **Public API unverified** despite published platform/member documentation | Distinctive investor research overlays; high differentiation if licensed | Contact provider about official feed, user-level entitlement, forecasting rights, derivative display and licensing. Do **not** confuse with Answer Socrates search-keyword API. https://www.ask-socrates.com/mkc/Content/MembersGuide.pdf |
| **Answer Socrates (separate provider)** | Keyword research, rising topics, trend indicators | Published API/MCP | Product-strategy and marketing demand research, not Armstrong market analysis | Commercial tiers and quotas. https://answersocrates.com/docs/api |
| **Alpha Vantage** | Time series, company fundamentals, earnings, analyst estimates, macro and commodities | Documented API, free key and premium endpoints | Investor and enterprise finance snapshots, earnings expectation overlays | Pricing/freshness/asset coverage and redistribution differ by endpoint. https://www.alphavantage.co/documentation/ |
| **Financial Modeling Prep (FMP)** | Public company financial statements, analyst revenue/EPS estimates | Documented paid/limited-access APIs | Comparable company financials, forecast-vs-actual analysis | Licence global/UK coverage, currency, analyst consensus methodology and display rights. https://site.financialmodelingprep.com/developer/docs |
| **Massive (formerly Polygon.io)** | Market ticks, quotes, bars, reference/fundamentals, streamed prices | Documented REST, WebSocket and bulk APIs | Investor market charts and catalyst awareness | Feed/exchange redistribution and real-time entitlements; may be too costly for free tier. https://www.massive.com/stocks |
| **UK Companies House** | Legal company identity, filings, registered details | Official live REST API with developer registration | Enterprise entity resolution and UK corporate facts | Company registered identity ≠ operating scale. Source filing periods and ownership must be reconciled. https://developer.company-information.service.gov.uk/ |
| **ONS** | UK economic sector, labour, regional and other official statistics | Open, unrestricted **v1 beta API** for supported datasets; no API key for core access | Country/industry GVA, labour and sector scale | Versioning, statistical definitions, breaking beta changes and historic category compatibility. https://developer.ons.gov.uk/ |
| **World Bank Indicators** | International economy, employment, development and macro time series | Public Indicators v2 API without API key | Global/country macro comparisons and policy views | Coverage, methodology and lag differ by country/indicator. https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api |
| **Eurostat** | EU economic, labour, social and environmental statistics | Public REST Statistics, SDMX and catalogue APIs | European market and country comparisons, including France | Units, revisions, geography and comparable source periods. https://ec.europa.eu/eurostat/en/web/user-guides/data-browser/api-data-access/api-getting-started |
| **OpenAlex** | Scholarly works, authors, institutions, research topics and networks | Documented API, limited free use; free key recommended for larger-scale queries | Researcher, technologist, educator, scientific collaboration ecosystems | Coverage and identity quality; pay-as-you-go for heavier use, check budget. https://help.openalex.org/api/ |
| **Crossref** | Scholarly publication/DOI metadata, funding, updates | Open public REST API without signup | Research papers, dated source trails and bibliographies | Metadata does not equal a licence to reproduce full papers; rate/attribution norms. https://www.crossref.org/documentation/retrieve-metadata/rest-api/ |
| **UK Find a Tender** | Procurement notices and structured release/record data | Official OCDS JSON APIs and OGL data | Sales bid triggers, buyer renewal/award context and public-policy analysis | Tender notice ≠ evidence of seller fit or award outcome; record notice dates, stage and licensing. https://www.find-tender.service.gov.uk/Developer/Documentation |
| **Adzuna** | Job adverts, salary/vacancy trends and sector skills demand | Published developer REST API with keys | Job seeker role matching, enterprise hiring indicators and workforce analysis | Job ads do not prove committed headcount or actual employer demand; check licensing and quotas. https://developer.adzuna.com/overview |
| **Jooble** | Job vacancies by country | Documented REST API; regional keys and published free daily request limit | Job seeker discovery and company/hiring signals | Separate keys for countries; validate dedup, freshness and source display rights. https://jooblehelpcenter.freshdesk.com/en/support/solutions/articles/60001448238-rest-api-documentation |
| **Google Classroom** | Teacher coursework, materials, assignments, submissions | Official Classroom API with OAuth and institutional authorisation | Educator case-study delivery, assignment workflows | Student privacy, school admin, learning-data retention and age requirements. https://developers.google.com/workspace/classroom/guides/coursework-integration |
| **GB Carbon Intensity API (NESO)** | Grid carbon intensity, generation mix and regional forecasts | Official public API; CC BY 4.0 published | Clean energy, environmental and educational visual analytics | Grid intensity is not an enterprise's carbon footprint; forecast uncertainty/timezone must be shown. https://api.carbonintensity.org.uk/ |

**Commercial terms and status are time-sensitive.** The above confirms documentation/API availability only, not approval to use, the pricing for production, redistribution rights, supplier partnership or full endpoint suitability. Re-check each before procurement or implementation.

### B3. The two exemplar integrations

**Career and relationships — “Who do I know at this company?”**

1. User opens an enterprise (e.g. target employer) and opts into a **Career/Networking** lens.
2. FLORA resolves the company's validated identity and group/subsidiary scope.
3. If user-approved LinkedIn export is present, it matches known first-degree connections conservatively to the selected company; exposes last-known employment date, confidence and one-click opening of the person's LinkedIn profile, not an invented current role.
4. If permitted, complement with Microsoft Graph contacts and user-authorised CRM records, tracking source, consent and recency separately.
5. Adzuna/Jooble provides available vacancies and hiring-context metrics where licensed; no profile scraping.
6. User saves an interview/research dossier, personal networking action and optional reminder. Do not send contact messages automatically.
7. LinkedIn's restricted APIs are a **partnership opportunity**, not the initial technical assumption.

**Investor — “What is changing, and what do forecasts imply?”**

1. User opens an enterprise; FLORA verifies its legal entity, exchange ticker, listing/currency and financial period.
2. Public reported financials are separated from forward analyst consensus (FMP/Alpha Vantage) and market prices (Massive/other licensed feed).
3. An investment-thesis view shows revenue/EPS history, consensus growth estimates, earnings revisions, sourced catalysts, bull/base/bear assumptions and forecast-vs-actual history where licences permit.
4. Proprietary Socrates cyclical indicators, if licensed, appear as **a named external model perspective**, never FLORA's accepted prediction and never conflated with analyst consensus. Distinguish forecasts, technical targets, observed market levels and user assumptions.
5. Users save/watch theses and are notified only on material changes with authorised, bounded monitoring.
6. No guaranteed returns, opaque win probabilities, trade execution or regulated investment advice.

### B4. High-leverage cross-role integration ideas

- **Sales:** CRM + Contacts/Calendar + public tender notices + Companies House + enterprise change → qualified account growth plans. Highest willingness-to-pay hypothesis; strongest dependence on permissions.
- **Job seeker:** saved employer + vacancies + opt-in LinkedIn exports/Graph contacts + company financial research → job matching and personalised introductions.
- **Researcher:** OpenAlex/Crossref + official economic data + company disclosures → living notebooks and documented comparisons.
- **Educator:** industry/enterprise visuals + ONS/World Bank + Classroom → living lessons with assignments and source-updated case studies.
- **Technologist:** enterprise technology ecosystems + authorised GitHub organisation/project metadata + technical research → decision records, architecture alternatives and lifecycle alerts.
- **Investor:** licensed fundamentals/estimates/price feed + official macro + earnings calendar → living valuation/thesis, explicit estimate boundaries.
- **Clean Energy:** NESO/Eurostat + sector energy/impact sources → modelled transition options, never substituting grid carbon intensity for company-level measured emissions.
- **Social Value/Public Policy:** ONS/World Bank + tender policy/procurement events → opportunity and impact planning, with direct source support and outcome tracking.

### B5. Integration architecture — proposal, not an implementation

```text
FLORA User (role, mission, country, tenant)
           |
   Experience / Entitlement / IAM checks
           |
 External Connections Catalogue (approval, OAuth, revocation)
           |
 Provider Adapters (public API | paid API | user-authorised personal API | user-supplied export)
           |
 Scope/Identity Resolver (legal entity; person consent; ticker; country)
           |
 Rights & Data Quality Envelope (provider, licence, source URL, retrieved/published/effective dates,
                usage constraints, geography, confidence, schema version, cache/expiry)
           |
 Governed Candidate Data / Existing Evidence+Observation Owners
           |
 Shared Industry/Enterprise Intelligence + Role-Specific Read-Only Views
           |
 Durable User Work Product (Pipeline | Research Notebook | Learning Case | Investment Thesis)
```

Strict boundaries:
1. **No integration may create an authorised employer, workspace membership, offer approval or Pipeline write.** Existing human and domain gates apply.
2. **OAuth consent and API entitlement are not data redistribution rights.** Per-provider licence matrix distinguishes personal, internal use, paid redistribution, caching, persistence, AI training, exports and onward sharing.
3. **No external raw member/contact data in public HTML, previews, logs or other tenants.** Separate public intelligence from private user and company accounts; expire/revoke on disconnect where required.
4. **Do not assume cross-service identity equality.** LinkedIn employer name, Companies House legal entity, stock ticker and CRM account require explicit grounded matching/version.
5. **Keep forecasts and derived estimations visible as such**, with model, period, source, update and range where applicable. No buying trigger inferred from a job ad or analyst estimate alone.
6. **Bound cost and rate:** quota, caching, retry/backoff, licensing, tenant-level budget, source availability and disconnected fallback before scheduled monitoring.
7. **Do not scrape protected services or bypass partner limits**. If an API is unavailable (LinkedIn network, Investing.com, Armstrong Socrates), pursue legal data export, provider contact or an alternative licensed source.
8. **Start read-only:** no outbound contact, auto-CRM write, automatic investment action or third-party changes without separate authorisation and approval.
9. **Data deletion/portability:** handle user revocation, account deletion, GDPR/UK GDPR and provider retention obligations as first-class connector lifecycle events.

### B6. Business development and monetisation

Integration models to test:
- **Bring your own account:** user connects an existing service; FLORA charges for orchestration, interpretation and work-product tools, subject to provider terms.
- **FLORA-provided licensed data:** bundle a permitted subset of market/company/industry feeds into paid Professional or Enterprise tiers.
- **Premium connector packs:** Sales CRM/networking; Investor data/consensus; Educator institution; Energy impact data.
- **Team/workspace subscriptions:** cross-user sharing where data owner/tenant permissions and supplier licences permit.
- **Partner or distribution agreements:** potential co-sell/referral and negotiated source API access; treat as future business development, not built-in rights.

Do not assume all users pay for the same feed. A sector research user may need only public-data access, while a live market-data user may create expensive per-seat/exchange obligations. Track **contribution margin by connected provider and role**, not simply aggregate subscription revenue.

### B7. Delivery priority and due diligence

| Phase | Candidate integrations | Why |
|---|---|---|
| **0 — catalogue and rights audit** | API/entitlement registry, object mapping, restricted-source contract, cost/licence checks | Avoid vendor lock-in and unlicensed redistribution |
| **1 — low-friction public sources** | Companies House, ONS, World Bank, Eurostat, OpenAlex, Crossref, Find a Tender, NESO | Documented APIs; boost economic and industry context quickly |
| **2 — role-specific pilot** | Microsoft Graph or HubSpot (authorised), Adzuna, one financial data API such as FMP/Alpha Vantage | Test sales/career/investor value, consent and unit economics |
| **3 — negotiated sources** | LinkedIn connections/Sales Navigator, Investing.com specialist arrangement, Armstrong Socrates | May be valuable but access is uncertain, partner approval/licence costs matter |
| **4 — packaged recurring products** | Integration-powered Opportunity Factory, Career Network Map, Investor Thesis, Educator Case Studio | Monetise outcomes, not connector count |

Proposed commercial diligence per provider: legal entity/contract; geographic coverage; exact endpoints; onboarding time; schema documentation; limits; availability/SLA; commercial and free quotas; retention/caching/export/redistribution/derived-work/AI clauses; consent/privacy and right to erase; costs at 100/1,000/10,000 active users; attribution; cancellation/rollback; independence of core FLORA.

**Recommendation:** Do not delay Offer-to-Sales Sprint A. In parallel, preserve this option in the Roles strategy paper; later select one public-source connector and one user-authorised connector as pilot before building a broad marketplace.


## Appendix C — Ask FLORA: context-aware intelligence, user overlays and actions (proposed 13 November 2026)

### C1. Thesis: images first, answers on demand

Ask FLORA is proposed as the universal conversational interaction between beautiful, minimal, image-led FLORA views and the complex intelligence underneath. Default pages foreground **one coherent scene, relevant economic scale and a few meaningful interactions**. Users request richer explanations, evidence, comparisons, personalised analyses and controlled actions rather than enduring permanently visible research panels.

**Product principle:** *Show the world. Let users ask for detail. Help them act.*

Do not add an always-open chat pane that consumes the image. A single accessible Ask FLORA control in the top header (and optionally a compact contextual affordance on a selected visual element) opens an unobtrusive overlay/drawer/voice or keyboard input; dismissal returns the user to the same underlying view/selection. A result can appear anchored within the illustration, as an ephemeral overlay, or as an expressly requested saved view. No duplicate navigation, universal prompt-wall or permanently expanding chatbot transcript beneath each page.

### C2. Four functions, different trust and price/cost boundaries

| Mode | User intent | Behaviour | Safe default |
|---|---|---|---|
| **Explain** | “Tell me more about this company / factor.” | Short contextual answer anchored to current market, industry, enterprise, selection, role and source cutoff | Read-only sourced answer; uncertainty not invented |
| **Investigate** | “Show me evidence / challenge this / what changed?” | Read-only citations, methods, dates, counter-evidence, source comparison and provenance via canonical owners | Evidence only on demand; source rights/ACL intact |
| **Visualise / Analyse** | “Overlay UK revenue”, “Compare these three”, “Show suppliers and dependencies.” | Scoped client-side visual transformation or permissioned read-model; comparisons label units, geography, year and EST | Reversible, temporary layer; never mutate accepted data |
| **Act / Save** | “Save this view”, “Watch this company”, “Add to target accounts”, “Prepare an entry play.” | Explicit action plan with permission/policy checks, human confirmation and audited domain-owner write | No write on question interpretation alone; protected approval and Pipeline qualification retained |

A fifth **Research** mode may be offered to entitled users: bounded and cost-controlled search for new evidence, producing candidate findings subject to the existing research acceptance process. It is **not** an automatic promotion of new facts.

### C3. Context contract

Each invocation receives a **server-resolved minimal context envelope** (not user-controlled authority):
- authenticated actor, active workspace and authorised entities;
- active experience purpose and thematic interests;
- viewed route, selected country, industry, enterprise, programme or opportunity ID and current illustrated element;
- source snapshot/evidence cutoff, data version and applicable market/statistical unit;
- permitted tool/function scopes and paid/free usage quota (future), using the actual entitlement service;
- optional user-selected, authorised private overlay layers and the overlay's consent/revision.

The model must not acquire permissions from request text, an HTML route, a query string, a user's self-declared role or a third-party document. Revalidate server-side before **every** read of private records and every write. Different workspaces, markets and user overlays never mingle through caches or prompted conversation memory.

The default query should be contextual: “Which companies matter here?” on a UK banking industry view refers to the selected sector and scope, whereas the same question on the user's approved Offers view includes the seller's authorised Offer portfolio. A user can visibly switch scope where appropriate.

### C4. Ask FLORA by professional experience

| Experience | Natural questions | New persistent object or outcome |
|---|---|---|
| **Business Development & Sales** | “Which three UK banks best fit my cloud offer?”, “Why would easyJet buy?”, “Show the underlying trigger”, “Prepare a sponsor-discovery play.” | Seller-confirmed account priority, saved entry-play draft, reviewed opportunity hypothesis → only authorised Pipeline capture |
| **Account / Client Director** | “Where might our footprint expand?”, “Show renewal timing and relationship risks.” | Account growth plan and verified renewal watch items |
| **Educator** | “Explain this value chain to a 16-year-old”, “Create a question using real financial data”, “Compare aviation and banking.” | Lesson plan, case study, class-safe quiz and source references |
| **Student** | “What is GVA?”, “Quiz me on the five forces of this industry.” | Progress and learning feedback, not inferred academic grades |
| **Researcher** | “Challenge this thesis”, “Show sources and contradictions since the last review.” | Research notebook, referenced evidence comparison and watchlist |
| **Technologist** | “Show the dependencies behind this architecture”, “Compare Azure and AWS for this stated requirement.” | Option assessment, decision log with assumptions and constraints |
| **Founder / Product strategist** | “What unsolved problems are appearing in this segment?”, “What would invalidate this market hypothesis?” | Saved market/customer validation experiment |
| **Investor** | “Compare revenue forecasts and realised performance”, “Which assumption drives the valuation?”, “Show Socrates versus consensus if licensed.” | Versioned investment thesis, watchlist and scenarios; no guaranteed forecasts or investment advice |
| **Clean Energy** | “Overlay electricity carbon intensity”, “How would this transition option alter the baseline?” | Transition scenario and impact assumptions, distinguishing measured vs forecast |
| **Social Value** | “Show workforce and skills impacts”, “Compare the evidence supporting this programme.” | Impact assessment and source-backed report |
| **Policy / Procurement** | “What is the operative regulation?”, “Which suppliers have evidence for this category?” | Policy analysis/sourcing dossier; proposal not treated as law |
| **Job Seeker / Career** | “Who do I know here?” when user has opted in to their contacts, “Show live vacancies and recent company results.” | Career dossier, personal relationship notes and job watchlist |
| **Regional Development** | “Which industries contribute most locally?”, “Show grants or jobs signals.” | Regional briefing or investment project watchlist |

Role changes the **question suggestions, default scope, tools and work-product**, never the evidence truth. Unimplemented capabilities must not appear as functional controls; mark future functions as planned in product design, not as live features.

### C5. Local Data: private generated overlays

**Recommendation: make “My Data” a first-class private overlay mechanism, not a replacement for canonical industry/enterprise intelligence.** “Local” should mean *owned or scoped to the user/workspace*, not necessarily stored only on the device. A separate offline-device storage mode is a future privacy/product decision, and should not be implied.

Potential overlay inputs:
1. **Personal inputs:** uploaded CSV/XLSX, notes, declared assumptions, private research, contact exports and watchlists.
2. **Connected accounts:** user-authorised CRM, contacts, licensed financial data, calendars and other provider feeds, with provenance and retention restrictions.
3. **FLORA-derived personal analysis:** user-requested models, estimates, annotations, scenario results and comparison layers based on cited or user-supplied inputs.
4. **Team/shared workspace layers:** explicitly promoted, permissioned overlays with owner approval and collaborative versioning; never automatically public.
5. **Temporary exploratory layers:** on-screen analyses not stored by default; user can deliberately save, rename, edit, export or delete.

Example overlays:
- UK economy: visualise user's selected targets by sector; show sourced sector GVA versus *their* potential account value without conflating units.
- Technology industry: overlay an authorised seller's selected Offers, match candidates and privately imported contact relationships.
- NVIDIA enterprise: overlay a personal financial thesis, market-data estimates (licensed), partner mapping and explicitly sourced customer references.
- PESTLE: overlay one user's jurisdiction/sector exposures or custom scenario assumptions, not claim they apply universally.
- Educator: overlay lesson annotations, key terms and class exercises.
- Investor: overlay bull/base/bear scenarios, forecast provider names, methodology and source cutoff.

**Visual handling:** clearly distinguish **FLORA baseline**, **External licensed source**, **My data**, **Team data**, and **My estimate (EST)** via discreet layer controls, subtle colour/line treatment and a compact legend available when overlays are active. The underlying image remains beautiful; toggling a layer must be reversible with one action. On-image insight reveals should have legible mobile/iPad/keyboard equivalents. No visually implied false numeric ranking from scene geometry.

### C6. Private overlay object contract (candidate)

Fields: stable `overlay_id`, owner principal and workspace/tenant, optional team sharing scope, attached entity/industry/market references, dataset source and legal rights, created/updated/snapshot timestamps, model/prompt version when generated, input references, geographic scope, currency/unit/period, data quality, uncertainty/EST basis, visibility level, content/data schema and format, version/history, retention/deletion/consent/revocation state, allowed exports and lineage to source records or user uploads.

**Persistence:** prefer a separate, encrypted/protected operational store or adapter under existing verified service boundary; do not write user overlays into canonical Source, Evidence, Observation, Twin or industry statistics. Promotion or cross-tenant sharing requires explicit owner review and existing canonical acceptance; a user private assumption can never become an independently verified market fact merely because an AI assistant summarised it.

### C7. Proposed implementation architecture

```text
FLORA image-native view + selected object / user experience
      ↓ single Ask FLORA entry
Server-authorised Context Resolver (scope, identity, source cutoff, role/entitlement, tenant)
      ↓
Intent Router (Explain | Investigate | Visualise | Save/Act | bounded Research)
      ↓
Tool Allowlist + Evidence Retrieval + Cost/Consent Policy
      ↓
Structured result (answer + citations + visualization specification + proposed action)
      ↓
Read-only on-image overlay / optional details / user-confirmed save
      ↓ only upon explicit confirmation
Existing authorised domain service / private overlay owner / reviewed Pipeline writer
```

Possible response types should be structured and bounded: `answer`, `source_refs`, `visual_overlay_spec`, `recommended_questions`, `action_proposal`, `permission_state`, `estimated_cost`, `error`. The renderer sanitises model outputs and cannot treat generated arbitrary HTML or URLs as authority. A prompt should not execute scripts, create links to private records or infer write permissions.

**Answer provenance:** show a concise answer first with one “Sources & method” control, but preserve full lineage to precise source claims and both positive/negative evidence. Distinguish external-feed forecasts, FLORA interpretations, user assumptions and measured numbers; attach visible **EST** to defensible numerical estimates, leave unsupported values blank.

**Security:** verified sessions/workspace, signed user scope, CSRF/origin on state writes, canonical privilege checks, source-licence policy, external connector consent, per-tool isolation, abuse/rate limits, revocation, data minimisation, injection resistance and auditing of consequential actions. The assistant cannot access or act outside its allowlist even if a retrieved source says it should. Do not send private documents to third-party models without appropriate user consent and provider contract.

### C8. Commercial implications

The core **Explain** mode can be broadly accessible, with rate/compute limits, and may be a powerful reason to try FLORA. Premium tiers monetise deep private connected context, more intensive research, saved overlays and scenarios, recurring monitoring, collaboration and professional **Act** workflows.

Candidate packaging:
- **Discover/Education Free:** basic contextual explanations, bounded evidence view and limited read-only visual interactions; clear usage limits.
- **Research Pro:** deep evidence comparisons, persistent notebooks, advanced saved overlays, exports and monitored research questions.
- **Sales Pro:** seller/private CRM and network overlays, offer-to-account assessments, entry-play generation and authorised Pipeline workflow.
- **Investor/Specialist Pro:** licensed external feeds, scenario/valuation/technology/impact overlays, saved decision history.
- **Enterprise:** multi-seat permissioned overlays, SSO/administration, collaborative work products, cost governance and vendor connections.
- **Usage-based add-on:** expensive AI model/research calls only by explicit user choice, quota and cost controls.

Avoid paywalling basic source transparency on any claim the user is permitted to see. Source inspection is a trust feature, not a premium-only privilege. No hidden paid calls in free role switching.

### C9. Pilot and metrics

**Pilot 1: explain and evidence, no AI autonomy.** Implement one lightweight contextual Ask FLORA for the **UK Technology or Banking industry**, one enterprise and image-native PESTLE. Use existing retrieved evidence and bounded model answers; test a deterministic alternative as baseline. User can ask “tell me more” and “show me evidence”; return concise sourced answer, on-image reveal and safe fallback. No user data uploads or writes initially.

**Pilot 2: one private overlay.** Authorised sales user adds a small private target-account list or a researcher adds a watchlist/notes; Ask FLORA overlays it on an existing industry scene and permits one deliberate Save/Remove action. Compare view before/after, accessibility, tenancy, data deletion and no canonical mutation.

**Pilot 3: role-specific work product.** Educator asks for a case-study lesson; Sales user asks for a trigger-led entry play; save only through their respective authorised user/project services. Demonstrate identical source facts but different permitted actions.

**Later:** licensed connector context, longitudinal monitoring, voice mode, multi-step actions, team shared overlays, internationalisation and multi-modal explanation, only when evidence licensing, costs and security are ready.

Measure: task completion, time-to-useful-answer, source accuracy, hallucination/material error rate, source inspection availability, privacy violations (target zero), repeated re-ask due to poor context, overlay usefulness, user-confirmed saved work, cost per successful interaction, role retention at natural cadence and willingness-to-pay.

### C10. Architectural decisions to settle later

1. **Assistant placement:** fixed header Ask FLORA control with contextual overlay vs optional image-selection entry. Recommend single header control, with selected visual elements pre-populating context.
2. **Default persistence:** ephemeral conversation with deliberate Save; opt-in history and explicit retention/deletion. Do not assume chat history is permanent canonical memory.
3. **Local semantics:** private FLORA-hosted workspace overlays first; encrypted device-local/offline mode only if users have a demonstrable need.
4. **Overlay authorisation:** private by default, explicit team sharing and permissioned institutional/corporate publication; no cross-user leak.
5. **Cost model:** basic explanation under quota; research/large model/connector calls separately authorised and metered.
6. **Navigation style:** answers in situ where possible; no new page/card wall for every follow-up, but open a specialist full-page view when analytical complexity genuinely warrants it.
7. **Generated insights:** structured, explainable candidate interpretation with version and source cutoff, not accepted facts; user may challenge and correct.
8. **Trigger actions:** reversible read-only effects first; deliberate user confirmation for any save/write, and independent approvals for employer catalogue/publication and formal Pipeline capture.

**Strategic position:** Ask FLORA is not a separate chatbot bolted onto an illustrated site; it is the shared **interaction and orchestration layer** for all role-specific experiences, their data integrations and user-owned work products. The visible product can remain beautifully minimal while functionality deepens.
