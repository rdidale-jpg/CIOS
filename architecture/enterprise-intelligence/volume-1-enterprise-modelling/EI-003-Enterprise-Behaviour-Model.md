# EI-003 — Enterprise Behaviour Model

**Purpose:** Define how CIOS models how an enterprise behaves.  
**Status:** Draft  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-03

## Architectural position

Enterprise Intelligence defines what CIOS knows about an enterprise. CIRM defines how CIOS reasons over evidence and signals. Flora is the first runtime implementation that combines both into operational intelligence.

## Purpose

Define enterprise behaviour as the predictive layer of the Commercial Digital Twin. Behaviour scores describe how an enterprise tends to act when facing cost pressure, regulatory scrutiny, technology change, supplier decisions and executive turnover. This paper is documentation-only and avoids runtime implementation detail.

## Why enterprise behaviour matters

Two enterprises can have the same financial pressure and technology need but respond differently. One may move quickly through a framework with a trusted incumbent; another may run a long open competition; a third may delay until regulation forces action. The Enterprise Behaviour Model helps CIOS interpret evidence, qualify opportunities and shape executive engagement.

Behaviour is not a substitute for evidence. It is a weighted pattern derived from evidence-backed attributes, inferred attributes and human-supplied attributes in the Enterprise Model and Enterprise Knowledge Graph. Behaviour influences recommendations but must not override direct contradictory evidence.

## Behaviour dimensions

Each dimension is scored from 0 to 100, carries Confidence and Freshness, links to evidence and records contradiction state.

### Transformation appetite

- **Meaning:** willingness to commit to material operating, technology or business change.
- **Observable evidence:** named programmes, leadership language, capex, repeated transformation commitments, consultant/supplier activity and delivery milestones.
- **Scoring indicators:** higher scores when programmes are funded, sponsored and repeated across reporting periods; lower scores when transformation language is generic or unfunded.
- **Commercial implication:** high appetite supports proactive shaping; low appetite requires pressure-based or compliance-led narrative.
- **Example:** a new multi-year digital programme with a named COO sponsor and procurement activity scores higher than a single annual-report ambition.

### Risk appetite

- **Meaning:** tolerance for operational, regulatory, commercial and delivery risk.
- **Observable evidence:** regulated posture, cyber incidents, audit findings, innovation speed, procurement conservatism and public risk statements.
- **Scoring indicators:** higher scores when pilots and rapid adoption continue despite uncertainty; lower scores when governance, regulation or incident history drives conservative change.
- **Commercial implication:** low risk appetite favours proven, compliant, incremental propositions; high risk appetite can support innovation-led pursuits.
- **Example:** a critical infrastructure operator with strict regulator commitments is likely to show moderate/low risk appetite even when Transformation Pressure is high.

### Innovation appetite

- **Meaning:** willingness to explore novel technologies, business models and partnerships.
- **Observable evidence:** pilots, AI labs, partnerships, venture investments, accelerator participation and tech hiring.
- **Scoring indicators:** higher scores when experimentation is funded and public; moderate when pilots exist without scale; low when innovation appears absent or purely rhetorical.
- **Commercial implication:** high scores support early ideation and co-creation; weak governance alongside high innovation creates AI governance and secure-by-design opportunities.
- **Example:** AI lab announcements plus data science hiring and partner pilots suggest moderate/high innovation appetite.

### Buying behaviour

- **Meaning:** how the enterprise converts need into supplier selection.
- **Observable evidence:** procurement route, framework preference, incumbency, direct awards, competitive tenders and long evaluation cycles.
- **Scoring indicators:** framework and repeat-award patterns indicate predictable route; frequent open competitions indicate competitive buying; direct awards may indicate urgency or incumbency.
- **Commercial implication:** buying behaviour determines route-to-market, partner choice, qualification and lead time.
- **Example:** a public body repeatedly using a cloud framework requires framework positioning before solution shaping.

### Procurement style

- **Meaning:** the procedural style and transparency of procurement.
- **Observable evidence:** framework usage, open tendering, PINs, supplier days, procurement pipeline quality and award behaviour.
- **Scoring indicators:** high openness when PINs, supplier days and pipelines are frequent; low openness when awards appear late or through narrow routes.
- **Commercial implication:** open style enables early market engagement; opaque style demands relationship-led validation and careful qualification.
- **Example:** a detailed commercial pipeline and early PINs indicate time to shape requirements before tender.

### Supplier loyalty

- **Meaning:** tendency to retain incumbents or strategic partners.
- **Observable evidence:** repeat awards, contract extensions, strategic partnerships and concentration of spend.
- **Scoring indicators:** high scores when incumbents repeatedly win extensions or adjacent work; low scores when supplier churn or competitive replacement is common.
- **Commercial implication:** high loyalty may block displacement and require partnership or executive-level reframing.
- **Example:** repeated extensions to a managed service provider indicate relationship-led shaping is required before replacement pursuit.

### Executive stability

- **Meaning:** continuity of leadership and change ownership.
- **Observable evidence:** leadership churn, new CEO/CFO/CIO, board changes and transformation leader turnover.
- **Scoring indicators:** high stability when leadership remains consistent; lower stability when multiple executive roles change in short windows.
- **Commercial implication:** new executives create timing windows but may delay decisions while strategies are reset.
- **Example:** a new CIO and new CFO within six months should trigger hypothesis review for cloud, cost and operating-model change.

### Decision velocity

- **Meaning:** how quickly the enterprise moves from recognition of need to decision and award.
- **Observable evidence:** speed from PIN to award, strategy-to-procurement lag, approval cycles and procurement delays.
- **Scoring indicators:** higher scores when similar procurements progress quickly; lower scores when procurements are delayed, cancelled or repeatedly extended.
- **Commercial implication:** low decision velocity plus high Transformation Pressure suggests early executive education rather than immediate pursuit.
- **Example:** a two-year gap between strategy commitment and tender suggests slow decision velocity.

### Cost discipline

- **Meaning:** intensity of focus on savings, margin, productivity and spending control.
- **Observable evidence:** savings targets, margin pressure, restructuring, headcount controls and capex discipline.
- **Scoring indicators:** high scores when public savings targets, restructuring and margin pressure align; moderate when cost language exists without hard targets.
- **Commercial implication:** high cost discipline favours automation, operating-model redesign and self-funding transformation narratives.
- **Example:** a CFO-led cost reduction programme plus declining margins signals strong cost discipline.

### Outsourcing tendency

- **Meaning:** preference for external delivery, managed services or insourcing.
- **Observable evidence:** outsourced operations, managed service awards, insourcing announcements and shared service models.
- **Scoring indicators:** high outsourcing tendency when core operations are repeatedly contracted out; lower when insourcing or internal capability build is explicit.
- **Commercial implication:** determines whether proposition should be managed service, advisory, platform, augmentation or internal enablement.
- **Example:** an organisation insourcing IT after a major contract expiry may still buy specialist support but resist broad outsourcing.

### Platform standardisation

- **Meaning:** tendency to consolidate onto common enterprise platforms.
- **Observable evidence:** ERP consolidation, cloud strategy, common data platform and enterprise architecture statements.
- **Scoring indicators:** higher scores when standardisation is a funded programme; lower when business units run fragmented platforms without consolidation evidence.
- **Commercial implication:** high standardisation supports enterprise platform plays; low standardisation may require business-unit-led entry.
- **Example:** a single ERP consolidation programme across finance, HR and procurement indicates high platform standardisation.

### Security maturity

- **Meaning:** demonstrated cyber governance, resilience and security investment maturity.
- **Observable evidence:** zero trust, CISO profile, cyber incidents, NCSC/regulated guidance and security investment.
- **Scoring indicators:** high maturity when strategy, investment, leadership and controls are visible; low maturity when incidents, audit failures or absent leadership dominate.
- **Commercial implication:** low maturity with high scrutiny creates urgent remediation; high maturity may favour advanced resilience or assurance work.
- **Example:** a public CISO, zero-trust programme and resilience reporting suggest higher security maturity than ad hoc incident response.

### AI readiness

- **Meaning:** ability to adopt AI safely and productively.
- **Observable evidence:** AI strategy, AI governance, AI hiring, AI use cases, data platform maturity and agentic AI partnerships.
- **Scoring indicators:** high readiness requires governance, use cases, data foundations and executive ownership; hiring alone is a weak signal.
- **Commercial implication:** high readiness supports AI deployment; low readiness supports data, governance and secure-by-design propositions.
- **Example:** AI hiring plus no governance statement may indicate interest but weak readiness.

### Cloud readiness

- **Meaning:** preparedness to move workloads to cloud or operate modern hybrid/cloud environments.
- **Observable evidence:** cloud partnerships, cloud migration, hybrid cloud, private cloud, sovereign cloud and data centre exit.
- **Scoring indicators:** high readiness when migration, operating model and partners are evidenced; moderate when strategy exists; low when legacy or data-centre dependency dominates.
- **Commercial implication:** new CIO plus low cloud readiness suggests technology strategy or cloud modernisation opportunity.
- **Example:** data centre exit commitment plus cloud partner award indicates rising readiness.

### Data maturity

- **Meaning:** ability to govern, integrate and exploit data for analytics, operations and AI.
- **Observable evidence:** data leadership, data platform, governance, analytics, AI readiness and data quality issues.
- **Scoring indicators:** high maturity when data ownership, platform and governance are evidenced; low maturity when public failures cite data quality or fragmented systems.
- **Commercial implication:** weak data maturity constrains AI opportunity and strengthens data foundation propositions.
- **Example:** repeated audit criticism of data quality weakens AI readiness until remediation is evidenced.

### Public scrutiny sensitivity

- **Meaning:** exposure and responsiveness to media, parliamentary, customer or public-service scrutiny.
- **Observable evidence:** parliamentary scrutiny, regulator/media attention, customer complaints and public service criticality.
- **Scoring indicators:** high scores when failures attract public hearings, regulator action or media coverage; low scores when scrutiny is limited or private.
- **Commercial implication:** high sensitivity requires careful, evidence-led narratives aligned to public value, resilience and assurance.
- **Example:** NAO/PAC attention on a public service programme indicates high scrutiny sensitivity.

### Regulatory responsiveness

- **Meaning:** speed and seriousness of response to regulator, policy or licence obligations.
- **Observable evidence:** speed of compliance actions, regulator commitments, enforcement history and consultation responses.
- **Scoring indicators:** high scores when commitments are quickly funded and acted on; low scores when enforcement repeats or deadlines slip.
- **Commercial implication:** high responsiveness plus audit pressure supports compliance transformation opportunity.
- **Example:** rapid publication of a remediation plan after enforcement indicates high responsiveness, even if underlying maturity remains weak.

## Observable signals

Observable signals are evidence-backed events or patterns that influence behaviour scores. Examples include procurements, awards, extensions, executive appointments, financial guidance, savings programmes, incidents, regulatory findings, hiring patterns, public statements, board changes, strategy launches and supplier announcements.

Signals must link to evidence, affected behaviour dimension, direction of impact, strength, Freshness and Confidence. Signals can support, weaken or contradict a behaviour assessment.

## Behaviour scoring

Behaviour scoring bands:

- **0–20 — Unknown / no evidence:** insufficient evidence for reliable assessment.
- **21–40 — Low:** weak or contrary evidence; behaviour rarely observed.
- **41–60 — Moderate:** mixed or partial evidence; behaviour appears situational.
- **61–80 — High:** repeated evidence across relevant contexts.
- **81–100 — Very High:** strong, repeated, independent evidence over time.

Scores should include explanation, source family, last reviewed date and contradiction state. A precise number is less important than the evidence trail and the band.

### Behaviour confidence

- **Low confidence:** single weak evidence point.
- **Medium confidence:** multiple evidence points from one source family.
- **High confidence:** multiple independent source families.
- **Very high confidence:** independent corroboration plus observed behaviour over time.

## Behaviour change over time

Behaviour changes slowly unless leadership, crisis, regulatory intervention or a major transaction occurs. Behaviour evidence should decay slowly compared with event evidence because repeated patterns remain useful after individual events age.

Rules:

- sudden changes should be treated as hypotheses first;
- leadership changes can open behaviour reassessment windows;
- crisis and regulatory intervention can temporarily alter risk appetite, decision velocity and cost discipline;
- behaviour should influence recommendations but not override evidence-backed attributes;
- contradictory behaviour evidence should reduce Confidence or split the behaviour by business unit or context.

## Behaviour and opportunity shaping

Behaviour-to-opportunity mapping:

- **High cost discipline + margin pressure →** automation / operating-model opportunity.
- **New CIO + low cloud readiness →** technology strategy / cloud modernisation opportunity.
- **High supplier loyalty + long incumbent contract →** relationship-led shaping required.
- **High regulatory responsiveness + audit pressure →** compliance transformation opportunity.
- **Low decision velocity + high Transformation Pressure →** early executive education, not immediate pursuit.
- **High innovation appetite + weak governance →** AI governance / secure-by-design opportunity.
- **Low data maturity + AI ambition →** data foundation and AI readiness opportunity.
- **High public scrutiny sensitivity + service failures →** resilient service transformation narrative.

Behaviour should adjust pursuit strategy. It should not invent opportunity without supporting Enterprise Model evidence.

## Behaviour and executive engagement

Behaviour-to-executive-engagement mapping:

- **CFO:** cost discipline, capex/opex pressure, savings and economic pressure points.
- **COO:** operating resilience, process efficiency, service performance and field/customer operations.
- **CIO/CTO:** cloud, legacy, platforms, technology debt and platform standardisation.
- **CISO:** cyber exposure, resilience, zero trust and security maturity.
- **CHRO:** workforce, skills, productivity and operating model.
- **Chief Commercial/Procurement Officer:** supplier ecosystem, frameworks, procurement route and supplier loyalty.
- **CEO/Board:** Transformation Inevitability, strategic risk, market disruption, public scrutiny and board-level accountability.

Engagement recommendations should cite the behaviour dimension, evidence, confidence and why the executive is the likely owner or influencer.

## Behaviour examples

### BT behaviour example

- Cost discipline: high.
- Innovation appetite: moderate/high.
- Regulatory responsiveness: high.
- Supplier loyalty: unknown until contract and award history are assessed.
- Decision velocity: unknown until procurement history is assessed.
- Commercial implication: validate network operations / cyber resilience opportunity with CFO, COO and CIO evidence before asserting a firm Opportunity Outlook.

### DWP behaviour example

- Public scrutiny sensitivity: high.
- Regulatory/political responsiveness: high.
- Decision velocity: low/moderate.
- Transformation appetite: evidence-dependent.
- Commercial implication: pursue early evidence validation and policy-aligned transformation narrative; avoid assuming fast procurement without route and sponsorship evidence.

### National Grid behaviour example

- Regulatory responsiveness: high.
- Asset intensity: high.
- Transformation Pressure: high where resilience, asset performance or energy transition obligations converge.
- Risk appetite: moderate/low.
- Commercial implication: resilience, asset intelligence and secure-by-design propositions are likely more credible than broad AI transformation claims.

## Open questions

- Which behaviour dimensions should be weighted differently by sector or enterprise priority tier?
- What minimum evidence should be required before behaviour scores influence Opportunity Outlook?
- How should Rob score / expert calibration adjust behaviour scoring without masking evidence?

## Relationship to other EI Volume 1 papers

EI-003 supplies the predictive behaviour layer for EI-001's Enterprise Model and Commercial Digital Twin. EI-001 defines where behaviour, Confidence, Freshness, Decay, Contradiction and Opportunity Outlook sit in the canonical model. EI-002 defines how behaviour evidence, scores and relationships are stored in the Enterprise Knowledge Graph and connected to signals, hypotheses, theses and recommendations.
