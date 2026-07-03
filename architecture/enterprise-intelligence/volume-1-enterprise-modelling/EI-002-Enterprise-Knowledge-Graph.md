# EI-002 — Enterprise Knowledge Graph

**Purpose:** Define entities, relationships and evidence-backed links that connect the enterprise model.  
**Status:** Draft  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-03

## Architectural position

Enterprise Intelligence defines what CIOS knows about an enterprise. CIRM defines how CIOS reasons over evidence and signals. Flora is the first runtime implementation that combines both into operational intelligence.

## Purpose

Define the Enterprise Knowledge Graph used to connect the Commercial Digital Twin. The graph represents enterprises, executives, financials, suppliers, contracts, programmes, technologies, pressures, hypotheses and recommendations as dated, confidence-scored relationships with evidence lineage. This paper is documentation-only and avoids runtime implementation detail.

## Why a graph is needed

A Commercial Digital Twin cannot be expressed as a flat profile. Opportunity intelligence depends on relationships: a CFO owns a savings theme, a supplier holds an expiring contract, a regulator pressures a business unit, a technology platform is being modernised by a programme and a hypothesis is supported by several signals but weakened by an unknown. The Enterprise Knowledge Graph makes those relationships explicit, queryable, temporal and explainable.

The graph must support:

- evidence-backed discovery of entities and relationships;
- inferred relationships with explanations and lower confidence;
- human-supplied relationships labelled by contributor and date;
- contradiction handling without silent overwrite;
- relationship decay and temporal state;
- query patterns that identify opportunity timing, blockers, access routes and pressure.

## Core entities

### Enterprise

Attributes include id, name, sector, geography, ownership type, priority tier, model maturity, regulated status, monitored scope, last refreshed, Confidence and Freshness.

### Business Unit

Attributes include name, parent enterprise, segment type, geography, revenue or scale where known, performance trend, operating role, customer group and source links.

### Executive

Attributes include name, role, tenure start, tenure end where applicable, prior roles, public statements, owns themes, source links, Confidence, Freshness and whether the attribute is evidence-backed, inferred or human-supplied.

### Board Member

Attributes include name, role, committee memberships, independence status, prior roles, risk/technology/sustainability relevance, appointment date and source links.

### Committee

Attributes include name, remit, members, risk domain, reporting cadence where known and source links.

### Programme

Attributes include name, theme, status, start date, target date, investment amount, sponsor, delivery partners, milestones, delays, source links and Confidence.

### Transformation Theme

Attributes include theme name, pressure driver, linked programmes, executive owners, related technologies, supporting signals and Opportunity Outlook relevance.

### Technology Platform

Attributes include platform name, category, vendor, cloud/ERP/CRM/data/AI/cyber/network/mainframe classification, deployment status, known partners, evidence links and last confirmed date.

### Supplier

Attributes include name, supplier type, capabilities, frameworks, strategic partner status, public-sector identifiers where relevant, incumbent positions and source links.

### Contract

Attributes include supplier, buyer, value, start date, end date, extension options, framework, procurement route, status, capability, source, Confidence and last confirmed date.

### Procurement

Attributes include title, buyer, category, procurement route, framework, notice type, publication date, deadline, estimated value, status, linked contract and source.

### Framework

Attributes include name, owner, lots, suppliers, start date, end date, buying route, eligible buyers and source.

### Regulator

Attributes include name, jurisdiction, regulated domain, licence conditions, enforcement powers, current consultations and source links.

### Competitor

Attributes include name, sector, geography, relevant business units, relative performance, disruptive capability, AI-first status where evidenced and source links.

### Market Force

Attributes include name, type, affected sector, direction, severity, evidence links and last observed date.

### Risk

Attributes include risk type, severity, affected entity, owner, mitigation status, source and relationship to Transformation Pressure.

### Financial Metric

Attributes include metric type, value, period, segment, trend, source, Confidence, accounting basis and last refreshed date.

### Cost Category

Attributes include labour, technology, capex, opex, outsourcing, customer operations, network/asset operations, finance/HR/procurement, pressure level, trend and evidence links.

### Evidence

Attributes include id, source, publication date, observed date, collection date, evidence type, extracted claim, affected attributes, source reliability and source URL/path.

### Source

Attributes include publisher, source family, authority level, publication cadence, access constraints and reliability rating.

### Signal

Attributes include name, generated from, severity, freshness, supported hypotheses and explanation.

### Hypothesis

Attributes include statement, supporting evidence, contradicting evidence, unknowns, Confidence, owner, status and last reviewed date.

### Thesis

Attributes include strategic claim, linked hypotheses, commercial implication, confidence, contradiction state and recommended next validation.

### Recommendation

Attributes include action, audience, rationale, linked thesis, Confidence, expiry date, dependencies and blockers.

### Commercial Outcome

Attributes include opportunity theme, owner, budget owner, route-to-market, timing window, estimated value, status and evidence lineage.

### Unknown

Attributes include question, affected conviction, priority, evidence needed, owner and expiry/review date.

## Core relationships

### Structural relationships

- `Enterprise HAS_BUSINESS_UNIT Business Unit`
- `Enterprise HAS_EXECUTIVE Executive`
- `Enterprise HAS_BOARD_MEMBER Board Member`
- `Board Member SITS_ON Committee`
- `Business Unit PART_OF Enterprise`

### Commercial relationships

- `Enterprise CONTRACTS_WITH Supplier`
- `Contract AWARDED_TO Supplier`
- `Procurement MAY_REPLACE Contract`
- `Supplier INCUMBENT_FOR Capability`
- `Procurement SIGNALS Opportunity`
- `Enterprise USES Framework`

### Financial relationships

- `Financial Metric INDICATES Pressure`
- `Cost Category DRIVES Transformation Pressure`
- `Segment UNDERPERFORMS Enterprise`
- `Financial Metric RELATES_TO Business Unit`

### Technology relationships

- `Enterprise USES Technology Platform`
- `Programme MODERNISES Technology Platform`
- `Supplier IMPLEMENTS Technology Platform`
- `Technology Platform SUPPORTS Capability`

### People relationships

- `Executive OWNS Programme`
- `Executive PREVIOUSLY_WORKED_AT Organisation`
- `Executive PUBLICLY_STATED Statement`
- `Executive INFLUENCES Theme`
- `Executive REPORTS_TO Executive` where public and relevant.

### Reasoning relationships

- `Evidence SUPPORTS Signal`
- `Signal SUPPORTS Hypothesis`
- `Hypothesis SUPPORTS Thesis`
- `Thesis SUPPORTS Recommendation`
- `Evidence CONTRADICTS Hypothesis`
- `Unknown WEAKENS Conviction`
- `Recommendation TARGETS Executive`

### Competitive relationships

- `Competitor THREATENS Business Unit`
- `Competitor OUTPERFORMS Enterprise`
- `Market Force PRESSURES Enterprise`
- `Regulator PRESSURES Enterprise`

## Evidence-backed edges

An evidence-backed edge is a relationship directly supported by source evidence. It must carry source id, observed date, evidence extract, confidence, last confirmed date and affected model attributes. Example: an award notice creates `Contract AWARDED_TO Supplier` and `Enterprise CONTRACTS_WITH Supplier` edges.

Evidence-backed edges should be preferred for facts such as appointments, contracts, procurements, financial metrics, regulator actions and named programmes.

## Inferred edges

An inferred edge is derived from multiple evidence-backed nodes and must carry lower confidence, explanation and the supporting evidence set. Example: `Cost Category DRIVES Transformation Pressure` may be inferred from rising opex, savings targets and executive cost statements.

Inferred edges must not be displayed as direct facts. They should remain revisable when evidence changes.

## Confidence and uncertainty

Every edge carries Confidence. Confidence reflects source quality, corroboration, freshness, specificity and contradiction. Uncertainty should be explicit through unknown nodes, weakened conviction edges and competing edges.

Edge governance states:

- **Evidence-backed edge:** directly supported by source evidence.
- **Inferred edge:** derived from multiple evidence-backed nodes and explained.
- **Human-supplied edge:** added by Rob or another expert; labelled with contributor, date and rationale.
- **Rejected edge:** proposed but rejected due to weak, noisy or contradictory evidence; retained for audit and to prevent repeated false positives.

## Temporal behaviour

Edges have observed date, effective date and last confirmed date. Temporal state is required because the Commercial Digital Twin is a living model, not a static map.

Rules:

- appointments supersede previous roles but historical role edges remain time-bounded;
- contracts expire unless renewed or extended;
- procurement edges move through planned, live, awarded, cancelled and expired states;
- supplier relationships weaken after expiry unless renewed by contract, spend or public relationship evidence;
- hypotheses strengthen or decline through evidence updates;
- source publication date, observed date and collection date must remain distinct.

## Contradictions

Contradictory evidence creates competing edges. The graph must never silently overwrite a relationship. Conflicts should be exposed in analyst views and reduce Confidence until resolved.

Examples:

- One source says a programme is complete while a procurement notice implies replacement work is still live.
- A supplier case study claims platform use, while a new tender indicates migration away.
- An executive biography differs from a company leadership page.

Contradiction edges should record the evidence pair, affected claim, severity and recommended validation action.

## Relationship decay

Relationship decay reduces the weight of stale edges without deleting history. Decay speed depends on relationship type:

- **Fast decay:** live procurements, job adverts, incident responses, executive statements and unconfirmed rumours.
- **Medium decay:** contracts, supplier relationships, transformation programmes and technology estate.
- **Slow decay:** historical employment, long-term sector, ownership history and durable regulatory obligations.

Decay can weaken recommendations, lower Commercial Conviction or create validation tasks.

## Graph updates

Graph updates are triggered when evidence creates, updates, weakens, contradicts or retires a node or edge. Updates should propagate to downstream signals, hypotheses, theses, recommendations, Transformation Pressure, Transformation Inevitability and Opportunity Outlook.

Human feedback can correct or calibrate the graph. Human-supplied edges must be labelled and dated. Rejected edges should remain visible to explain why a proposed relationship did not enter the Enterprise Model.

## Example graph fragments

### BT example

- `BT HAS_EXECUTIVE CFO`
- `BT HAS_BUSINESS_UNIT Openreach`
- `BT CONTRACTS_WITH Supplier X`
- `BT USES Technology Platform Y`
- `BT PRESSURED_BY Ofcom`
- `BT HAS_SIGNAL Network Resilience`
- `Network Resilience SUPPORTS Hypothesis AI-enabled Network Operations`

Commercial interpretation: network resilience, regulation and technology estate evidence can support a hypothesis around AI-enabled network operations, but supplier and platform details determine fit and blockers.

### DWP example

- `DWP HAS_EXECUTIVE CDIO`
- `DWP HAS_PROGRAMME Digital Modernisation`
- `DWP HAS_PROCUREMENT Debt / Casework Platform`
- `DWP CONTRACTS_WITH Supplier`
- `NAO Report PRESSURES DWP`

Commercial interpretation: public scrutiny, digital modernisation and live or planned procurement evidence can strengthen a policy-aligned transformation thesis, while procurement route and incumbent contracts shape pursuit timing.

## Query patterns

The graph must support queries such as:

- Which enterprises have rising cost pressure and a new CFO?
- Which contracts expire in the next 18 months?
- Which suppliers are gaining share in public sector spend?
- Which enterprises have AI hiring signals but no published AI strategy?
- Which executives own transformation themes?
- Which organisations show high Transformation Pressure but low procurement evidence?
- Which opportunities are blocked by incumbent contracts?
- Which regulated enterprises have audit pressure and active technology programmes?
- Which suppliers are linked to both cloud migration and cyber resilience programmes?
- Which human-supplied relationship routes are stale and require validation?

## Open questions

- Which graph storage pattern should best preserve evidence lineage, temporal edges and contradiction state?
- Which edge confidence thresholds should be required before a relationship can influence Opportunity Outlook?
- How should rejected edges be presented without cluttering analyst workflows?

## Relationship to other EI Volume 1 papers

EI-002 implements the connected structure required by EI-001's Enterprise Model and Commercial Digital Twin. EI-001 defines the domains and attribute governance that become graph nodes and properties. EI-003 supplies behaviour dimensions and scores that the graph stores, connects to evidence and uses in opportunity reasoning.
