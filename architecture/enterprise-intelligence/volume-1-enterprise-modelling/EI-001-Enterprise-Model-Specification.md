# EI-001 — Enterprise Model Specification

**Purpose:** Define the canonical enterprise object that CIOS builds and maintains for each monitored organisation.  
**Status:** Draft  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-03

## Architectural position

Enterprise Intelligence defines what CIOS knows about an enterprise. CIRM defines how CIOS reasons over evidence and signals. Flora is the first runtime implementation that combines both into operational intelligence.

The Enterprise Model is the durable memory of CIOS. Evidence updates the model. Reports, briefs, hypotheses, recommendations and opportunity predictions are generated from the model.

## Purpose

Define the canonical Commercial Digital Twin for each monitored enterprise. The Enterprise Model records evidence-backed attributes, inferred attributes, human-supplied attributes, confidence, freshness, decay state, contradictions, Transformation Pressure, Transformation Inevitability and Opportunity Outlook. This paper is documentation-only and avoids runtime implementation detail.

## Why enterprise models exist

CIOS is not merely collecting evidence about enterprises; it is building, updating and reasoning over living enterprise models. Enterprise Models exist so every report, brief and recommendation is grounded in persistent knowledge rather than a one-off search result. A model must answer: what is the enterprise, how does it operate, who controls change, what pressures it faces, what behaviours it repeatedly demonstrates and which commercial opportunities may become actionable.

A useful Enterprise Model must be:

- **Evidence-linked:** every material attribute carries source lineage or is explicitly marked as inferred or human-supplied.
- **Freshness-aware:** volatile facts such as executives, procurements and contracts decay faster than durable facts such as sector or ownership history.
- **Contradiction-aware:** conflicting evidence is represented and exposed rather than overwritten.
- **Commercially purposeful:** attributes are captured because they improve timing, targeting, qualification, shaping or executive engagement.
- **Updatable:** new evidence can create, update, weaken, retire or calibrate model attributes.

## Enterprise as Commercial Digital Twin

The Commercial Digital Twin is the commercially relevant model of a monitored enterprise. It combines enterprise facts, operating context, relationships, behaviour, pressures, hypotheses and opportunity signals into a durable architecture for decision support.

The twin should support five questions:

1. **What is this enterprise?** Identity, profile, structure, governance and monitored scope.
2. **How does it make, spend and lose money?** Financial performance, economics, cost base and pressure points.
3. **How does it operate and change?** Operating model, technology estate, transformation portfolio and supplier ecosystem.
4. **How does it behave?** Appetite for transformation, risk, innovation, procurement, suppliers, outsourcing, platforms, security, cloud, data and AI.
5. **Where might commercial opportunity emerge?** Transformation Pressure, Transformation Inevitability, Commercial Conviction and Opportunity Outlook.

### Attribute governance

- **Evidence-backed attribute:** a model attribute directly supported by evidence such as an annual report, procurement notice, regulator publication, executive statement or contract award.
- **Inferred attribute:** a reasoned conclusion from multiple evidence-backed attributes; it must carry an explanation and lower confidence than direct evidence.
- **Human-supplied attribute:** a correction, relationship insight or expert judgement added by Rob or another authorised user; it must be labelled, dated and calibratable.
- **Confidence:** the assessed reliability of the attribute, considering source quality, corroboration, recency and contradiction.
- **Freshness:** the time since the attribute was observed or confirmed, relative to the volatility of that attribute type.
- **Decay:** the reduction in confidence or actionability when an attribute has not been refreshed within the expected window.
- **Contradiction:** competing evidence or interpretations that cannot yet be reconciled.

## Enterprise identity

**Captures:** the stable identity and monitored perimeter of the organisation.

**Example attributes:** legal name, trading names, parent and subsidiary structure, sector, geography, ownership type, public/private/listed status, regulated status and monitored scope.

**Evidence sources:** company registries, annual reports, investor relations pages, regulator registers, stock exchange filings, public-sector organisation pages, group structure disclosures and authoritative enterprise websites.

**Confidence / freshness rules:** legal names and listed status require high-quality primary sources; regulated status should be refreshed when regulator registers or licences change; monitored scope is a human-supplied attribute and should be reviewed when subsidiaries, business units or geographies change.

**Commercial relevance:** identity prevents duplicate accounts, ensures the right buying entity is targeted and clarifies whether opportunity sits at group, subsidiary, business unit or public-body level.

**Example signals generated from change:** new subsidiary added may signal acquisition integration; regulated status change may create compliance opportunity; monitored scope expansion may justify building a richer twin.

## Enterprise profile

**Captures:** how the enterprise creates value and competes.

**Example attributes:** business model, customer groups, operating footprint, major products/services, strategic priorities and market position.

**Evidence sources:** annual reports, strategy presentations, investor days, corporate websites, analyst reports, government strategy papers, speeches and market commentary.

**Confidence / freshness rules:** published strategy should be refreshed after annual results, investor days or leadership changes; market position should decay if only supported by old analyst commentary; inferred priorities must cite the underlying statements or investments.

**Commercial relevance:** profile determines relevant propositions, executive narrative and whether cost, growth, resilience, customer experience or compliance is the dominant route in.

**Example signals generated from change:** a new strategic priority around digital channels may generate customer operations and CRM signals; a shift to asset resilience may generate field operations, network intelligence and cyber resilience signals.

## Executive leadership

**Captures:** the people who own enterprise change and commercial decisions.

**Example attributes:** CEO, CFO, COO, CIO, CTO, CDO, CISO, Chief People Officer, Chief Commercial Officer, transformation leaders, digital/data/AI/cyber leaders, procurement/commercial leaders, recent appointments/departures, public statements and evidence of ownership of change.

**Evidence sources:** leadership pages, announcements, Companies House or equivalent filings, LinkedIn/public biographies where permissible, conference agendas, earnings calls, press releases, procurement documents and public statements.

**Confidence / freshness rules:** appointments and departures are volatile and should be refreshed frequently for priority enterprises; unconfirmed role ownership should be inferred only from multiple sources; public statements should retain date, venue and theme.

**Commercial relevance:** leadership determines sponsor mapping, executive engagement, buying committee hypotheses and whether a change window exists after a new appointment.

**Example signals generated from change:** new CFO plus margin pressure may signal cost transformation; new CIO plus legacy estate evidence may signal technology modernisation; CISO public comments after an incident may signal cyber resilience demand.

## Board and governance

**Captures:** governance structures that shape risk, transformation and accountability.

**Example attributes:** chair, non-executive directors, committees, audit/risk/technology/sustainability committees, governance changes and board-level transformation or risk indicators.

**Evidence sources:** annual reports, governance statements, committee terms of reference, board announcements, regulator correspondence, parliamentary records and investor presentations.

**Confidence / freshness rules:** board membership should be refreshed after annual reports and announcements; committee ownership must be source-linked; board-level risk indicators should be treated as hypotheses unless repeatedly evidenced.

**Commercial relevance:** board attention can make transformation unavoidable, especially where risk, audit, cyber, sustainability or technology committees explicitly sponsor remediation.

**Example signals generated from change:** new technology committee may signal board-level digital oversight; audit findings may elevate compliance or control transformation; chair change may precede strategic review.

## Financial performance

**Captures:** financial condition, trajectory and pressure.

**Example attributes:** revenue, revenue growth, EBITDA, operating profit, margins, cash flow, debt, capex, opex, segment performance, cost reduction targets and guidance changes.

**Evidence sources:** annual and interim reports, trading updates, investor presentations, regulatory filings, budget statements, government accounts, credit rating notes and audited financial statements.

**Confidence / freshness rules:** reported figures should be tied to period and accounting basis; guidance changes supersede prior guidance but prior guidance remains historically relevant; segment metrics should not be mixed with group metrics without labelling.

**Commercial relevance:** financial pressure shapes budget availability, sponsor urgency, savings narratives and whether opportunity is defensive, growth-led or compliance-led.

**Example signals generated from change:** margin decline plus cost reduction target may trigger automation signals; capex increase in technology may signal platform opportunity; debt pressure may weaken appetite for discretionary transformation.

## Enterprise economics

**Captures:** the economic mechanics behind performance and pressure.

**Example attributes:** cost base structure, labour intensity, cost-to-serve indicators, technology spend, outsourcing spend, supplier concentration, transformation savings, capital allocation and economic pressure points.

**Evidence sources:** annual reports, cost programme disclosures, procurement spend files, contract registers, workforce data, investor Q&A, public accounts and operating reviews.

**Confidence / freshness rules:** direct cost disclosures carry higher confidence than inferred cost base estimates; supplier spend should be refreshed when transparency data or contract registers update; savings claims require dated programme lineage.

**Commercial relevance:** economics identify where commercial interventions can create measurable value and which executive budget owner is likely to care.

**Example signals generated from change:** rising labour cost-to-serve may signal AI-enabled operations; high supplier concentration may create renegotiation or replacement opportunity; capex reallocation to digital may strengthen timing.

## Operating model

**Captures:** how work is organised and delivered.

**Example attributes:** business units, shared services, centralised vs decentralised functions, customer operations, field operations, asset operations, contact centres, technology delivery model and outsourcing/insourcing model.

**Evidence sources:** annual reports, operating model announcements, job adverts, procurement documents, organisational charts, transformation updates, union communications and service performance reports.

**Confidence / freshness rules:** operating models change through programmes and restructures, so attributes should be refreshed after restructuring announcements; inferred centralisation should cite shared-services evidence; operational pain points decay unless re-confirmed.

**Commercial relevance:** operating model determines where change lands, which functions sponsor it and whether propositions should target process efficiency, service resilience, field productivity or shared-service optimisation.

**Example signals generated from change:** shared-service consolidation may signal ERP/workflow opportunity; contact-centre pressure may signal automation and experience opportunity; insourcing announcement may weaken managed-service pursuit.

## Technology estate

**Captures:** known and inferred technology platforms, constraints and partners.

**Example attributes:** cloud platforms, ERP, CRM, data platforms, AI platforms, cyber/security stack, legacy estate, networks, mainframe, digital workplace, automation platforms and known technology partners.

**Evidence sources:** case studies, procurement notices, job adverts, architecture statements, technology partner announcements, annual reports, cyber disclosures and supplier references.

**Confidence / freshness rules:** supplier case studies can become stale and should decay unless refreshed by current evidence; job adverts indicate skills demand but not confirmed production use; technology estate inferences require explanation.

**Commercial relevance:** technology estate shapes fit, competitive displacement, integration risk, partner route and credible transformation themes.

**Example signals generated from change:** data platform hiring may signal AI readiness; cloud migration award may signal adjacent security opportunity; legacy platform risk may support modernisation thesis.

## Transformation portfolio

**Captures:** active and planned change initiatives.

**Example attributes:** named programmes, announced initiatives, strategy commitments, cost programmes, digital programmes, AI/cloud/cyber/data programmes, delivery milestones, delays, investment amounts and executive sponsors.

**Evidence sources:** annual reports, strategy updates, procurement pipelines, programme pages, budget papers, regulator commitments, supplier announcements and executive statements.

**Confidence / freshness rules:** programme status must distinguish announced, funded, procured, in-flight, delayed and completed; delays must be evidenced; investment amounts must retain currency, period and scope.

**Commercial relevance:** portfolio visibility identifies current spend, white space, sequencing and opportunities to shape before formal procurement.

**Example signals generated from change:** milestone delay may signal delivery support; new AI programme may signal governance/security need; cost programme expansion may signal automation budget.

## Supplier ecosystem

**Captures:** the suppliers and partners delivering technology, operations and change.

**Example attributes:** incumbent suppliers, strategic partners, framework suppliers, cloud partners, systems integrators, software vendors, outsourcing providers, recent wins/losses and supplier concentration.

**Evidence sources:** contract registers, award notices, spend transparency data, supplier press releases, case studies, framework records, annual reports and procurement portals.

**Confidence / freshness rules:** live contracts require start/end date lineage; relationships weaken after expiry unless renewed; supplier concentration should be based on spend or contract count and labelled if inferred.

**Commercial relevance:** supplier ecosystem determines competitive landscape, relationship routes, incumbent blockers and partner opportunities.

**Example signals generated from change:** incumbent loss may signal dissatisfaction; strategic partnership renewal may block displacement; new SI award may create subcontract or alliance route.

## Procurement and commercial activity

**Captures:** buying activity, routes and commercial timing.

**Example attributes:** live procurements, planned procurements, contract awards, framework call-offs, contract extensions, contract expiries, spend transparency, procurement route, buying authority, commercial pipeline and supplier spend.

**Evidence sources:** Find a Tender, Contracts Finder, public procurement portals, commercial pipelines, contract registers, award notices, framework catalogues, transparency spend and tender documents.

**Confidence / freshness rules:** live opportunities are highly volatile and must be refreshed frequently; expiry dates must be tied to original and extension terms; planned procurements are lower confidence until notice publication.

**Commercial relevance:** procurement evidence converts broad interest into actionable timing, route-to-market, qualification and competitive strategy.

**Example signals generated from change:** PIN publication may trigger early shaping; contract extension may delay opportunity; new framework call-off may identify preferred route.

## Competitive position

**Captures:** relative market, peer and disruption context.

**Example attributes:** direct competitors, peer performance, market share, customer churn, competitor investment, disruptive entrants, AI-first entrants, relative cost position and regulatory comparison.

**Evidence sources:** market reports, annual reports, regulator data, customer metrics, competitor announcements, analyst commentary, public performance tables and industry benchmarks.

**Confidence / freshness rules:** competitor and market-share data must retain period and source; inferred relative cost position requires multiple indicators; disruption claims require clear evidence of customer, product or economics impact.

**Commercial relevance:** competitive pressure supports transformation inevitability and executive urgency.

**Example signals generated from change:** competitor AI investment may signal defensive AI strategy; customer churn rise may signal experience transformation; weaker regulatory performance may signal compliance remediation.

## Regulatory and political environment

**Captures:** external scrutiny and obligations.

**Example attributes:** regulators, consultations, fines/enforcement, parliamentary scrutiny, NAO/PAC reports, political priorities, licence conditions and compliance pressure.

**Evidence sources:** regulator publications, enforcement notices, consultation documents, parliamentary records, NAO/PAC reports, ministerial statements, licence documents and public audit reports.

**Confidence / freshness rules:** enforcement and licence conditions are high-confidence primary evidence; consultations should be time-bound; political priorities decay after policy or ministerial change unless reaffirmed.

**Commercial relevance:** regulatory pressure can create non-discretionary demand and improve board access when risk, resilience or compliance is material.

**Example signals generated from change:** enforcement action may signal urgent remediation; consultation response may reveal investment direction; NAO report may signal public-sector transformation pressure.

## People and workforce signals

**Captures:** workforce demand, constraints and sentiment visible in permissible public sources.

**Example attributes:** hiring spikes, hiring freezes, redundancy programmes, key skills demand, AI/cloud/cyber/data job adverts, workforce sentiment where publicly available, union activity, executive LinkedIn/public posts where permissible and conference appearances.

**Evidence sources:** job boards, corporate career pages, public LinkedIn posts where permissible, union statements, redundancy announcements, conference agendas, workforce reports and employee consultation notices.

**Confidence / freshness rules:** job adverts are signals not proof of implemented capability; workforce sentiment must be source-qualified; hiring data decays quickly once adverts close.

**Commercial relevance:** workforce signals reveal capability gaps, delivery capacity, transformation readiness and likely demand for partners or automation.

**Example signals generated from change:** AI hiring spike may signal AI readiness; cyber recruitment after an incident may signal security programme; hiring freeze may weaken discretionary transformation but strengthen automation thesis.

## Relationship graph

**Captures:** relationships that influence access, trust and decision pathways.

**Example attributes:** executive relationships, prior employers, board networks, supplier relationships, adviser relationships, partner ecosystem and known relationship access routes.

**Evidence sources:** public biographies, board histories, supplier announcements, event participation, adviser disclosures, public LinkedIn profiles where permissible and human-supplied relationship intelligence.

**Confidence / freshness rules:** public relationships should be distinguished from human-supplied attributes; access routes must be dated and owner-labelled; inferred influence should carry low confidence until corroborated.

**Commercial relevance:** relationship intelligence helps choose warm routes, partner strategies and stakeholder sequencing.

**Example signals generated from change:** executive joins from a supplier may create relationship route; adviser appointment may signal strategy review; board network may enable senior introduction.

## Enterprise behaviour

**Captures:** repeatable behavioural tendencies used as a predictive layer.

**Example attributes:** transformation appetite, risk appetite, procurement style, supplier loyalty, decision speed, innovation appetite, outsourcing tendency and cost discipline.

**Evidence sources:** historic procurements, contract behaviour, executive statements, programme delivery history, regulatory responses, crisis responses, technology adoption and EI-003 scoring.

**Confidence / freshness rules:** behaviour changes slowly and should be based on patterns over time; sudden changes after leadership, crisis or transaction should begin as hypotheses; behaviour should not override direct evidence.

**Commercial relevance:** behaviour informs pursuit strategy, timing, proposition style and how strongly to weight Opportunity Outlook.

**Example signals generated from change:** new leadership plus faster procurement may signal decision-velocity change; repeated incumbent renewals may signal high supplier loyalty; pilot-heavy activity may signal innovation appetite.

## Transformation pressure

**Captures:** force accumulating on the enterprise to change.

**Example attributes:** internal pressure, external pressure, accumulated pressure, pressure release, pressure severity and pressure evidence.

**Evidence sources:** financial deterioration, operational failures, customer complaints, regulatory findings, cyber incidents, competitor movement, workforce constraints, public scrutiny and executive commitments.

**Confidence / freshness rules:** pressure requires evidence lineage and should separate event severity from persistence; pressure release occurs when remediation, funding or programme completion reduces pressure; stale pressure decays unless refreshed.

**Commercial relevance:** pressure helps identify timing windows, urgency and whether change is discretionary or becoming unavoidable.

**Example signals generated from change:** audit failure plus public scrutiny may raise compliance pressure; margin decline plus savings target may raise cost pressure; incident resolution may lower immediate pressure.

## Transformation inevitability

**Captures:** the reason transformation may become unavoidable and when.

**Example attributes:** inevitability rationale, timing window, inhibitors, evidence required to strengthen/weaken and dependency on regulation, economics, technology obsolescence or market disruption.

**Evidence sources:** pressure evidence, financial trends, regulatory deadlines, contract expiries, technology end-of-life, board commitments, competitor disruption and procurement pipelines.

**Confidence / freshness rules:** inevitability is an inferred attribute and must remain explainable; it strengthens through independent evidence families and weakens when pressure is released or inhibitors dominate.

**Commercial relevance:** inevitability frames executive narratives around strategic risk, resilience and timing rather than generic solution selling.

**Example signals generated from change:** regulator-mandated deadline may strengthen inevitability; contract extension may delay it; capital constraint may inhibit otherwise necessary transformation.

## Commercial conviction

**Captures:** whether an opportunity thesis is worth pursuing.

**Example attributes:** evidence confidence, commercial attractiveness, provider fit, relationship access, unknowns, blockers and Rob score / expert calibration.

**Evidence sources:** all Enterprise Model domains, human feedback, opportunity history, provider capability mapping, relationship intelligence and expert review.

**Confidence / freshness rules:** conviction must expose unknowns and blockers; human-supplied calibration must be dated; contradictory evidence reduces confidence or splits the thesis.

**Commercial relevance:** conviction prevents over-pursuit of noisy signals and focuses shaping effort on opportunities with evidence, fit and access.

**Example signals generated from change:** new warm relationship may improve access; incumbent renewal may reduce attractiveness; Rob score adjustment may calibrate model weighting.

## Opportunity outlook

**Captures:** the likely future commercial opportunities implied by the twin.

**Example attributes:** likely opportunity themes, likely executive owner, likely budget owner, possible procurement route, timing window, estimated value where inferable and recommended shaping action.

**Evidence sources:** transformation portfolio, procurements, financial pressure, technology estate, leadership statements, supplier ecosystem, behaviour scores and relationship graph.

**Confidence / freshness rules:** Opportunity Outlook is always time-bound and hypothesis-led until procurement or budget evidence appears; estimated value must be labelled as reported, inferred or unknown; route-to-market confidence decays quickly.

**Commercial relevance:** Opportunity Outlook turns the Enterprise Model into actionable commercial intelligence.

**Example signals generated from change:** new CFO plus cost pressure may create operating-model opportunity; expiring cyber contract plus incident may create security opportunity; AI hiring without governance may create AI governance opportunity.

## Evidence linkage

Every material model attribute must link to one or more evidence records or be labelled as inferred or human-supplied. Evidence lineage should retain source, publication date, observed date, collection date, affected attributes and whether the evidence creates, updates, weakens, contradicts or retires an attribute.

Evidence should not be treated as the output. Evidence is the input that updates the Enterprise Model; the model is the durable memory used to generate outputs.

## Confidence and freshness

Confidence combines source authority, corroboration, recency, specificity and contradiction. Freshness is assessed by attribute volatility:

- **High volatility:** live procurements, appointments, contract status, incidents, job adverts and public statements.
- **Medium volatility:** transformation programmes, supplier relationships, technology estate, financial outlook and operating model.
- **Low volatility:** sector, ownership history, long-term business model and durable regulatory context.

Decay lowers confidence or actionability when attributes are not refreshed. Decay should not delete historical knowledge; it should mark it as stale, require confirmation or reduce its weighting in recommendations.

## Minimum Viable Commercial Digital Twin

- **Level 0 — Skeleton:** identity, sector and basic sources exist, but there is no reliable reasoning. The twin can prevent duplicates but cannot support recommendations.
- **Level 1 — Observable Enterprise:** identity, strategy, financials, leadership and minimum evidence coverage exist. The twin can produce basic enterprise briefs and simple signals.
- **Level 2 — Reasonable Enterprise Model:** financials, operating model, leadership, technology, procurement, supplier ecosystem and active hypotheses exist. The twin can support qualification and early opportunity shaping.
- **Level 3 — Strategic Commercial Twin:** full model includes behaviour, economics, relationships, Opportunity Outlook, Confidence and live updates. The twin can support executive narratives, account planning and pursuit prioritisation.
- **Level 4 — Predictive Enterprise Twin:** the model can support opportunity prediction, executive engagement and transformation window assessment with explicit confidence, contradiction handling and feedback calibration.

## Enterprise Model Update Rules

- Evidence can create, update, weaken or retire model attributes.
- Every material model attribute requires evidence lineage or an explicit inferred/human-supplied label.
- Inferred attributes must be labelled as inferred and retain reasoning explanation.
- Stale attributes must decay rather than remain silently current.
- Contradictions must be represented, not overwritten.
- User feedback can correct, override or calibrate the model when labelled as human-supplied and dated.
- Retired attributes remain available for history, trend analysis and explanation.
- High-impact updates should trigger downstream re-evaluation of Transformation Pressure, Transformation Inevitability, Commercial Conviction and Opportunity Outlook.

## Open questions

- What exact freshness thresholds should apply by enterprise priority tier and attribute volatility?
- Which human-supplied attributes require explicit approval before influencing recommendations?
- How should Rob score / expert calibration be weighted against evidence-backed model signals?

## Relationship to other EI Volume 1 papers

EI-001 defines the canonical Enterprise Model and Commercial Digital Twin. EI-002 defines the Enterprise Knowledge Graph that stores and connects model entities, attributes and evidence-backed relationships. EI-003 defines the Enterprise Behaviour Model that supplies behavioural scores and predictive tendencies used by Transformation Pressure, Transformation Inevitability and Opportunity Outlook.
