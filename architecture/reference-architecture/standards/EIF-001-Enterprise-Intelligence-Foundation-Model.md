# EIF-001 — Enterprise Intelligence Foundation Model

**Document class:** Reference architecture standard  
**Status:** Review  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-14  
**Production behaviour:** Documentation-only architecture. Does not change runtime behaviour, production Researcher packs, production Assurance packs, EI-001, EI-002, EI-003, EI-012, EOD-001, OT-001, AP-001, AP-002 or RP-001.  
**Relationship:** EIF-001 precedes EOD-001 and produces the initial Enterprise Twin.

## 1. Purpose

EIF-001 defines the canonical method for constructing the initial Enterprise Twin from public-domain evidence before Opportunity Discovery, Opportunity Twin creation or any Research Sprint begins.

It exists because the CSM sprint proved that beginning with a known procurement is not a general methodology. Where no opportunity is already known, CIOS must first understand the enterprise itself: why it exists, how value flows, how it operates, how it behaves, what is changing and what evidence is still missing.

## 2. Core principle

Every Commercial Digital Twin begins by understanding the enterprise before reasoning about opportunities.

Enterprise understanding is durable. Opportunity reasoning is derived. Reports are transient views.

EIF-001 therefore creates durable Enterprise Twin state and structured Unknowns. EOD-001 then derives the opportunity portfolio from that Twin. OT-001 then defines a selected opportunity in more detail. Research Sprints then deepen evidence for a validated research object.

## 3. Canonical lifecycle position

The canonical Enterprise Intelligence lifecycle is:

```text
Enterprise
  ↓
EIF-001 — Enterprise Intelligence Foundation
  ↓
Enterprise Twin
  ↓
EOD-001 — Enterprise Opportunity Discovery
  ↓
Opportunity Portfolio
  ↓
Opportunity Prioritisation
  ↓
OT-001 — Opportunity Twin
  ↓
Research Sprint
  ↓
RTP-001
  ↓
OPI-001
  ↓
Provider Fit
  ↓
Executive Pursuit
  ↓
Learning
  ↓
Enterprise Twin evolves
```

This order matters because:

1. Enterprise identity, purpose, value model, operating model, behaviour, technology, ecosystem, risk and change are stable inputs to repeated opportunity reasoning.
2. Opportunity Discovery must not repeatedly reconstruct foundational enterprise context.
3. Procurements are evidence of change, not the definition of the enterprise or the opportunity.
4. Provider Fit requires account-relative provider knowledge and must remain downstream of public-domain foundation and opportunity reasoning.
5. Learning from pursuit and outcomes improves the Enterprise Twin, so the lifecycle is cumulative rather than report-led.

## 4. Relationship to existing architecture

EIF-001 extends existing architecture. It does not duplicate or supersede it.

| Existing authority | EIF-001 relationship |
| --- | --- |
| CIOS Design Doctrine | Applies evidence-first, observation-led, model-centred reasoning before commercial action. |
| Reference Architecture | Inserts the Foundation step into the Enterprise Intelligence lifecycle before EOD-001. |
| EI-001 Enterprise Model Specification | Populates initial Enterprise Twin state within the durable Enterprise Model boundary. EIF-001 does not redefine the Enterprise Model. |
| EI-002 Enterprise Knowledge Graph | Identifies entities and relationships that may become graph state after acceptance. EIF-001 does not redefine graph semantics. |
| EI-003 Enterprise Behaviour Model | Uses EI-003 behaviour categories and confidence handling to assess enterprise behaviour. EIF-001 does not invent a parallel behaviour model. |
| EI-012 Enterprise Observation Model | Requires public-domain evidence and atomic Observations for material claims. EIF-001 does not change Observation lifecycle semantics. |
| EOD-001 | Provides the Enterprise Twin input from which Opportunity Discovery starts. EOD must not duplicate Foundation work. |
| OT-001 | Keeps Opportunity Twin creation downstream of Enterprise Twin and Opportunity Prioritisation. |
| AP-001 and AP-002 | Remains Review material excluded from production packs unless separately accepted through registry-backed architecture governance. |
| RP-001 | Does not change the production Researcher profile or pack. |
| Accepted ADRs | Preserves durable memory, Observation atomics, CIRM/EI separation, labelled human knowledge, inspectable lineage, progressive assurance, structured-source-first evidence acquisition, canonical acceptance boundaries and exchange-not-promotion rules. |

## 5. Scope and boundaries

EIF-001 is Foundation-only.

EIF-001 must:

- construct the initial public-domain Enterprise Twin;
- preserve Unknowns and Contradictions;
- separate evidence, interpretation and decision support;
- keep reports transient;
- prepare stable input for EOD-001;
- identify evidence demands that would most improve understanding.

EIF-001 must not:

- perform Opportunity Discovery;
- perform Positioning;
- perform Provider Fit;
- perform a Research Sprint;
- duplicate EI-001, EI-002, EI-003 or EI-012;
- change runtime behaviour;
- change canonical models;
- promote Review material into production packs.

## 6. Evidence rules

Foundation work uses public-domain evidence only unless explicitly labelled as human-supplied knowledge under the applicable ADR boundary.

Material claims require:

- source reference;
- claim type;
- date or freshness indicator;
- confidence;
- Unknowns;
- Contradictions where present;
- whether the claim is supported, inferred from supported evidence, or unsupported.

Unsupported claims may be recorded as Unknowns or evidence demands. They must not be projected into accepted Foundation objects.

## 7. Required Foundation domains

Every Enterprise Twin Foundation must establish the following ten domains. The goal is sufficient enterprise understanding, not unnecessary organisational exhaustiveness.

### 7.1 Enterprise Identity

Capture:

- legal identity;
- ownership;
- operating entities;
- geography;
- markets;
- business units;
- brands;
- customers;
- regulatory context;
- public mission or purpose.

Unknowns must be preserved rather than filled by assumption.

### 7.2 Enterprise Purpose

Explain why the organisation exists and how it creates value.

Classify the enterprise purpose where supported:

- Commercial;
- Public;
- National Infrastructure;
- Regulated Utility;
- Defence;
- Healthcare;
- Education;
- Other.

A single enterprise may have multiple classifications. The classification is evidence-backed interpretation, not a replacement for the enterprise's own stated purpose.

### 7.3 Enterprise Value Model

Describe how value flows through the enterprise, including as applicable:

- revenue;
- services;
- assets;
- products;
- platforms;
- operations;
- customers;
- funding;
- economic drivers.

The value model should explain what must work for the enterprise to remain viable, trusted and investable.

### 7.4 Enterprise Operating Model

Describe how work flows through capabilities rather than attempting unnecessary organisational detail.

Common capability areas include:

- Operations;
- Technology;
- Finance;
- HR;
- Commercial;
- Supply Chain;
- Customer;
- Field Operations;
- Shared Services;
- Manufacturing;
- Networks;
- Corporate Services.

Model capability and dependency. Do not overfit to current reporting lines unless those reporting lines are material evidence.

### 7.5 Enterprise Strategy

Capture and reason about:

- strategic objectives;
- transformation ambitions;
- public commitments;
- investment themes;
- growth themes;
- efficiency themes;
- risk themes.

Do not reproduce annual reports. Summarise the strategic logic and evidence-backed implications for the Enterprise Twin.

### 7.6 Enterprise Behaviour

Use EI-003 to assess how the enterprise typically responds to:

- risk;
- investment;
- technology;
- suppliers;
- regulation;
- transformation;
- public scrutiny;
- failure;
- change.

Preserve confidence. Behaviour claims should remain bounded by evidence and should not become personality-style assertions.

### 7.7 Enterprise Technology

Capture technology capability, not product inventory.

Examples include:

- ERP;
- CRM;
- Networks;
- Cloud;
- Cyber;
- AI;
- Data;
- Digital Workplace;
- Analytics;
- Customer Platforms;
- Operational Technology.

Explain why each capability matters to the enterprise's value model, operating model, risk landscape or change landscape.

### 7.8 Enterprise Ecosystem

Model relationships with:

- suppliers;
- partners;
- regulators;
- customers;
- government;
- industry bodies;
- strategic alliances;
- outsourcing providers;
- joint ventures.

Relationships must distinguish evidenced relationships from inferred dependencies.

### 7.9 Enterprise Risk Landscape

Capture only supported risks, including as applicable:

- strategic risks;
- operational risks;
- financial risks;
- technology risks;
- people risks;
- regulatory risks;
- environmental risks;
- transformation risks.

Risk statements must be tied to evidence or carried as evidence demands.

### 7.10 Enterprise Change Landscape

Summarise everything materially changing, including as applicable:

- merger;
- restructure;
- ERP;
- Cloud;
- AI;
- Cyber;
- Customer;
- Asset Management;
- Operating Model;
- Finance;
- HR;
- Supply Chain;
- Digital Transformation;
- Sustainability.

This landscape is the direct input to EOD-001. It describes change themes and programmes without selecting opportunities.

## 8. Foundation outputs

EIF-001 produces the following outputs:

| Output | Purpose | Durability |
| --- | --- | --- |
| Enterprise Foundation Summary | Concise explanation of what the enterprise is, why it exists, how it creates value and what is changing. | Durable Twin view. |
| Enterprise Behaviour Assessment | EI-003-aligned behaviour assessment with confidence, evidence and caveats. | Durable but revisable. |
| Capability Map | Capability-level operating model without unnecessary org-chart detail. | Durable map. |
| Technology Capability Map | Technology capability view connected to value, operations, risk and change. | Durable map. |
| Enterprise Ecosystem Map | Evidence-backed relationship map of suppliers, partners, regulators, customers and alliances. | Durable map. |
| Enterprise Change Landscape | Material change themes and programmes that become EOD input. | Durable input, refreshed as evidence changes. |
| Enterprise Twin v1 | Initial governed Enterprise Twin state assembled from accepted Foundation objects. | Canonical target object after acceptance. |
| Decision Envelope | Boundary of what the Foundation supports, supports with caveats or does not support. | Decision-support artefact. |
| Evidence Demand Register | Prioritised missing evidence that would most improve enterprise understanding. | Active backlog. |
| Flora Import Manifest | List of accepted Foundation objects eligible for Flora import. | Import-control artefact. |

## 9. Decision Envelope

The Foundation Decision Envelope states what the Foundation is sufficient to support.

Use three decisions:

- **Supported** — Foundation evidence is sufficient for the stated downstream use.
- **Supported with Caveats** — Foundation evidence is usable but material Unknowns, Contradictions, freshness issues or low-confidence interpretations must be carried forward.
- **Not Supported** — Foundation evidence is insufficient and downstream use would require unsupported inference.

The Decision Envelope must explain:

- what the Foundation can support now;
- what still requires further research;
- which Unknowns block EOD-001;
- which Unknowns can be carried as caveats;
- which claims must not enter Flora.

## 10. Evidence Demand Register

Prioritise evidence that would most improve enterprise understanding.

For each evidence demand capture:

- question;
- Foundation domain affected;
- why it matters;
- likely source class;
- priority;
- impact if unresolved;
- whether unresolved evidence blocks Enterprise Twin v1 acceptance, blocks EOD-001, or can be carried as a caveat.

## 11. Flora relationship

Only accepted Foundation objects may enter Flora.

Examples of import-eligible Foundation objects include:

- Enterprise;
- Business Units;
- Capabilities;
- Technology Domains;
- Partners;
- Programmes;
- Enterprise Behaviour;
- Strategic Objectives;
- Change Themes;
- Relationships.

Reports remain transient. A report may present Foundation findings, but the report itself is not canonical memory. Flora import must therefore reference accepted objects, evidence lineage and acceptance state rather than importing narrative text as fact.

## 12. Relationship to EOD-001

EIF-001 ends by providing the Enterprise Twin.

EOD-001 begins from that Enterprise Twin and derives an Opportunity Portfolio from the Enterprise Change Landscape, capability map, technology capability map, risk landscape, ecosystem map and evidence demands.

Opportunity Discovery must not duplicate Foundation work. If EOD finds a material identity, purpose, value-model, behaviour, technology, ecosystem, risk or change gap, it should raise a Foundation evidence demand or Twin update proposal rather than silently rebuilding the Foundation inside EOD.

## 13. VodafoneThree worked example — Foundation only

This example demonstrates sequence, not a complete Enterprise Twin release. It intentionally performs no Opportunity Discovery, no procurement research, no positioning and no Provider Fit.

### 13.1 Foundation scope

Enterprise: VodafoneThree, the UK mobile network joint venture formed from Vodafone UK and Three UK.

Public-domain evidence used for the example includes Vodafone's CMA approval announcement, UK competition-regulator material describing approval conditions and public reporting that the combination created a UK mobile-market leader. This is sufficient to demonstrate the Foundation method but not sufficient for a complete assured Enterprise Twin.

### 13.2 Enterprise Identity

- Legal / operating identity: VodafoneThree is the combined UK mobile-network enterprise created from Vodafone UK and Three UK.
- Ownership: public material describes Vodafone Group and CK Hutchison as joint-venture owners at formation, with Vodafone holding majority control and CK Hutchison retaining a minority interest.
- Geography: United Kingdom.
- Markets: UK mobile telecommunications, including consumer, business and wholesale mobile services.
- Brands: Vodafone and Three remain material customer-facing brand evidence at Foundation stage unless later evidence shows brand consolidation.
- Regulatory context: Competition and Markets Authority approval with conditions; Ofcom involvement in UK telecoms oversight.
- Customers: UK consumers, business customers and wholesale/MVNO customers.
- Unknowns: detailed post-merger legal-entity structure, current internal business-unit design and full operating-entity map require further evidence before Flora import beyond high-level identity.

### 13.3 Enterprise Purpose

VodafoneThree exists to provide UK mobile connectivity and to create value by combining scale, spectrum, network assets, customers and investment capacity. Its public purpose is partly Commercial and partly National Infrastructure because UK mobile connectivity supports consumers, businesses, emergency resilience, productivity and digital inclusion. It is also a regulated utility-like telecoms operator because competition, consumer protection, wholesale access and network commitments are externally supervised.

### 13.4 Enterprise Value Model

Value flows through:

- consumer mobile services;
- business connectivity;
- wholesale/MVNO services;
- network assets and spectrum;
- customer platforms and distribution;
- long-term network investment intended to improve coverage, quality and 5G capability;
- merger synergies and operating efficiency.

Foundation interpretation: the enterprise's value model depends on integrating networks and operations while maintaining customer protections, wholesale obligations and regulatory trust.

### 13.5 Enterprise Operating Model

Capability-level operating model:

- Network operations and engineering;
- Spectrum and radio access planning;
- Core network and service platforms;
- Retail commercial operations;
- Business and wholesale operations;
- Customer service and digital channels;
- Cyber, fraud and resilience operations;
- Finance, HR, procurement and corporate services;
- Regulatory compliance and public affairs;
- Transformation and integration management.

Unknown: detailed organisational design after merger is not required for Foundation v1 unless it materially affects change reasoning.

### 13.6 Enterprise Strategy

Supported strategic themes:

- build a larger UK mobile network with substantial 5G investment;
- improve coverage, speed and network quality;
- compete more effectively in the UK mobile market;
- integrate two operators while satisfying competition remedies;
- protect selected customer and wholesale outcomes during the remedy period;
- realise merger synergies and fund network transformation.

Foundation does not infer specific supplier opportunities from these themes.

### 13.7 Enterprise Behaviour

EI-003-aligned behaviour assessment:

- Regulation: high sensitivity; merger approval and conditions indicate regulatory dependence and external scrutiny.
- Investment: public commitments indicate willingness to make large, multi-year network investment when scale and regulatory permission support it.
- Transformation: high transformation intensity because the enterprise must integrate networks, systems, people, brands, customer operations and governance.
- Suppliers: supplier posture is unknown at Foundation stage; do not infer procurement routes or preferred vendors.
- Public scrutiny: high, because mobile prices, coverage, wholesale access and market concentration are public-interest issues.
- Failure response: unknown; preserve as evidence demand until operational incidents, service records or formal reports are reviewed.

### 13.8 Enterprise Technology

Technology capability map:

- Mobile network / RAN: central to coverage, capacity, 5G rollout and merger remedy delivery.
- Core network: material to service quality, resilience, integration and future services.
- OSS/BSS and customer platforms: material to integration, customer experience, billing, product management and wholesale service delivery.
- Cyber and fraud controls: material because telecom networks are critical infrastructure and customer channels are fraud targets.
- Data and analytics: material to network planning, customer insight, operations and regulatory reporting.
- Cloud and digital workplace: likely material to integration and productivity, but specific capability maturity remains an evidence demand.

### 13.9 Enterprise Ecosystem

Foundation ecosystem objects:

- Regulators: CMA and Ofcom.
- Owners: Vodafone Group and CK Hutchison at formation.
- Customers: consumers, business customers and MVNO/wholesale customers.
- Government / public-policy context: UK digital infrastructure and mobile coverage policy.
- Industry bodies and partners: to be evidenced before import.
- Suppliers: not Foundation-accepted without specific public evidence.

### 13.10 Enterprise Risk Landscape

Supported risk themes:

- regulatory compliance with merger remedies;
- network integration execution risk;
- customer protection and price scrutiny;
- wholesale-market access scrutiny;
- service resilience and cyber risk;
- synergy-delivery and investment-funding risk;
- people and operating-model integration risk.

### 13.11 Enterprise Change Landscape

Material changes:

- merger integration;
- network integration and 5G investment programme;
- customer and wholesale remedy compliance;
- operating-model integration;
- brand, channel and customer-experience evolution;
- technology-platform rationalisation where supported by later evidence;
- cyber, fraud and resilience enhancement where supported by later evidence.

This Change Landscape becomes input to EOD-001. EIF-001 stops here and does not identify, prioritise or research opportunities.

### 13.12 Foundation outputs demonstrated

- Enterprise Foundation Summary: VodafoneThree is a UK mobile network enterprise created by merger, with commercial and national-infrastructure purpose, high regulatory scrutiny and material network-transformation commitments.
- Enterprise Behaviour Assessment: high regulatory sensitivity, high transformation intensity, high public scrutiny, unknown supplier posture.
- Capability Map: network, customer, wholesale, regulatory, cyber, corporate and transformation capabilities.
- Technology Capability Map: mobile network, core, OSS/BSS, cyber, data, cloud/digital workplace as capability domains.
- Enterprise Ecosystem Map: owners, regulators, customers, wholesale customers and public-policy context.
- Enterprise Change Landscape: merger integration and network investment, with remedy compliance.
- Enterprise Twin v1: supportable at high-level Foundation confidence, subject to evidence demands.
- Decision Envelope: Supported with Caveats for starting EOD-001; Not Supported for procurement research, provider fit or supplier positioning.
- Evidence Demand Register: entity structure, leadership and operating model, integration roadmap, technology estate, supplier relationships, current regulatory remedy status.
- Flora Import Manifest: high-level Enterprise, owners, regulators, markets, capabilities, technology domains, strategic objectives and change themes only after acceptance; no narrative report import.

## 14. Acceptance criteria for EIF-001

EIF-001 is complete when:

- every Enterprise Twin starts consistently;
- enterprise understanding is separated from Opportunity Discovery;
- Foundation outputs are durable;
- reports remain transient;
- EOD-001 has a stable input;
- public-domain boundaries are preserved;
- the methodology works across industries;
- VodafoneThree validates that an Enterprise Twin is created before Opportunity Discovery.

## 15. Completion report

EIF-001 has been added as Review, documentation-only architecture. It inserts the Enterprise Intelligence Foundation before EOD-001, defines ten required Foundation domains, specifies durable Foundation outputs, preserves the Flora acceptance boundary and demonstrates the method with VodafoneThree without performing Opportunity Discovery.

No runtime behaviour, canonical model, production Researcher pack or production Assurance pack is changed.
