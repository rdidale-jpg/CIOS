# FP-005 — Enterprise Intelligence Collection Framework

**Purpose:** Define reusable evidence blueprints by enterprise type and sector so Flora can collect evidence without organisation-specific logic.
**Status:** draft
**Owner:** Rob / CIOS
**Last updated:** 2026-07-02

## Relationship to the CIOS Intelligence Reference Model

The CIOS Intelligence Reference Model (CIRM) defines how CIOS converts observable enterprise reality into strategic commercial judgement. Its canonical pipeline is:

```text
Observable Enterprise Reality
→ Governed Source Collection
→ Raw Evidence
→ Evidence Quality Assessment
→ Strategic Signals
→ Commercial Insights
→ Transformation Themes
→ Transformation Theses
→ Hypothesis Validation
→ Commercial Conviction
→ Executive Recommendations
→ Commercial Outcomes
→ Continuous Learning
```

FP-005 governs the collection framework that determines which source families and evidence categories Flora should pursue for different enterprise types.

## Inspectable Reasoning Lineage

No recommendation may exist unless its reasoning chain can be inspected:

```text
Executive Recommendation
→ Commercial Conviction
→ Hypothesis / Transformation Thesis
→ Commercial Insight
→ Strategic Signal
→ Raw Evidence
→ Source
```

If any link is missing, the recommendation should be downgraded to a learning action or evidence demand.

## 1. Purpose

This paper defines an enterprise-generic collection framework for Flora. It describes reusable evidence blueprints that help Flora decide what to collect for different types of organisations and sectors without hard-coding organisation-specific collection logic.

The framework should help Flora pursue evidence that improves commercial judgement, supports transformation theses and exposes gaps before downstream reasoning begins.

## 2. Enterprise-generic collection model

Flora should collect through reusable enterprise patterns. An organisation may be a government department, regulator, utility, telecommunications provider, supplier, media organisation or sports organisation, but the collection model should remain consistent:

1. identify enterprise type and sector;
2. select the relevant evidence blueprint;
3. map universal evidence categories to expected source families;
4. collect authoritative and specific evidence first;
5. score coverage and gaps;
6. adapt collection based on active transformation theses.

This model prevents bespoke logic for individual organisations while still allowing sector-aware evidence pursuit.

## 3. Enterprise evidence blueprint

An enterprise evidence blueprint defines the expected evidence categories, source families and minimum coverage for an organisation type. It does not prescribe implementation mechanics. It describes what Flora should seek and why.

A blueprint should include:

- enterprise type;
- relevant universal evidence categories;
- expected Tier 1 and Tier 2 source families;
- optional sector-specific sources;
- minimum viable coverage requirements;
- priority account extensions;
- common evidence gaps;
- source replacement options.

Blueprints should be reusable and composable. A public utility, for example, may combine utility, regulator-facing, procurement and critical infrastructure evidence patterns.

## 4. Universal evidence categories

### Strategy

Evidence of stated priorities, transformation programmes, market position, operating model change, service reform or long-term ambition.

### Finance

Evidence of revenue, cost pressure, budget allocations, capital expenditure, financial performance, efficiency targets or investment capacity.

### Technology

Evidence of platforms, cloud, AI, data, cyber, automation, legacy modernisation, network infrastructure or technology partnerships.

### Procurement

Evidence of tenders, contract awards, supplier frameworks, procurement pipelines, spending data and buying patterns.

### Leadership

Evidence of executive appointments, accountable owners, board priorities, role changes and public statements by named leaders.

### Operations

Evidence of delivery constraints, service performance, operating footprint, workforce change, resilience issues or process redesign.

### Regulation

Evidence of obligations, enforcement, policy pressure, audit findings, compliance requirements and sector oversight.

### Delivery

Evidence of programmes, milestones, implementation progress, delays, benefits realisation or transformation execution.

### Suppliers

Evidence of incumbent suppliers, new partnerships, major awards, delivery ecosystems and supplier-led announcements.

### Customers / citizens

Evidence of user demand, service quality, customer outcomes, citizen impact, complaints, satisfaction, adoption or market behaviour.

### Risk / security

Evidence of cyber risk, operational resilience, safety, continuity, fraud, data protection, national security or critical infrastructure exposure.

## 5. Enterprise type blueprints

Each enterprise type blueprint should describe minimum viable evidence, high-value evidence, weak or noisy evidence, likely hidden gaps and next-best source options. These blueprints should guide deliberate collection without hard-coding organisation-specific logic.

### Government department

Minimum viable evidence:

- annual report and accounts;
- spending data;
- procurement pipeline or contracts;
- strategy, outcome plan or departmental plan;
- leadership structure.

High-value evidence:

- NAO / PAC findings;
- major programme reports;
- digital, data or technology strategy;
- named senior responsible owners;
- large contract awards or tender notices;
- select committee evidence tied to delivery pressure.

Weak or commonly noisy evidence:

- GOV.UK organisation landing page;
- publication scheme text;
- jobs and contracts footer text;
- generic policy collection pages;
- accessibility, complaints or modern slavery boilerplate.

Likely hidden evidence gaps:

- supplier incumbency behind framework lots;
- programme delivery milestones;
- internal ownership below permanent secretary level;
- spend linked to a named transformation thesis;
- negative evidence from audit follow-up or delayed programmes.

Example next-best sources:

- NAO report pages;
- PAC hearings and transcripts;
- Contracts Finder and Find a Tender;
- departmental annual report annexes;
- spend over threshold files;
- supplier case studies only where contract or programme detail is specific.

Commercial use: identify policy priorities, delivery pressure, budget constraints, procurement timing, transformation ownership and supplier movement.

### Regulator

Minimum viable evidence:

- annual report and corporate plan;
- strategy and enforcement priorities;
- consultations and decision documents;
- leadership structure;
- procurement or technology operating evidence.

High-value evidence:

- enforcement action or market study findings;
- speeches by named executives;
- supervision, data or digital strategy;
- regulated entity performance publications;
- budget or capability-build evidence.

Weak or commonly noisy evidence:

- consultation index pages;
- generic “how we regulate” pages;
- careers landing pages;
- standing guidance without current enforcement or policy movement.

Likely hidden evidence gaps:

- internal analytics and supervisory technology demand;
- procurement for data platforms;
- enforcement capacity constraints;
- cross-regulator collaboration.

Example next-best sources:

- consultation outcome pages;
- board papers where public;
- speeches and event transcripts;
- procurement portals;
- parliamentary committee evidence.

Commercial use: identify regulatory pressure, market change, digital supervision needs, data capability requirements and sectors under scrutiny.

### Utility

Minimum viable evidence:

- annual report;
- regulatory business plan;
- price control determination or submission;
- operational performance report;
- resilience, safety or security evidence.

High-value evidence:

- capital programme plans;
- regulator performance penalties or improvement notices;
- named infrastructure programmes;
- customer service metrics tied to obligations;
- supplier awards for field, asset, data or customer platforms.

Weak or commonly noisy evidence:

- generic customer help pages;
- service area menus;
- sustainability landing pages without targets or delivery plans;
- careers overview pages.

Likely hidden evidence gaps:

- asset management platform replacement;
- field-force transformation;
- cyber resilience investments;
- incumbent delivery ecosystems;
- delayed benefits realisation.

Example next-best sources:

- regulator determinations;
- performance commitments and outcome delivery reports;
- capital delivery updates;
- supplier award announcements;
- local planning or infrastructure programme material.

Commercial use: identify infrastructure investment, resilience obligations, customer pressure, capital programme risk and technology-enabled operating change.

### Telecommunications provider

Minimum viable evidence:

- annual report;
- investor results;
- regulator publications;
- network investment evidence;
- technology partnerships.

High-value evidence:

- Capital Markets Day material;
- Ofcom resilience/security publications;
- RNS announcements;
- major network programme updates;
- supplier ecosystem announcements;
- named executive statements on capex, automation, AI, cloud or security.

Weak or commonly noisy evidence:

- generic newsroom index;
- consumer product pages;
- careers overview;
- service menu pages;
- broadband availability or sales pages.

Likely hidden evidence gaps:

- supplier incumbency by network domain;
- security remediation activity;
- automation programme delivery evidence;
- enterprise technology estate modernisation;
- operational resilience incidents not visible in marketing.

Example next-best sources:

- annual report strategic and risk sections;
- investor presentations and results transcripts;
- Ofcom publications;
- RNS feeds;
- vendor ecosystem announcements;
- specialist network programme updates.

Commercial use: identify network investment, automation priorities, cyber and resilience pressure, regulatory obligations, supplier shifts and transformation timing.

### Energy provider

Minimum viable evidence:

- annual report and investor results;
- transition strategy;
- regulatory publications;
- infrastructure or grid investment plan;
- customer service or vulnerability evidence.

High-value evidence:

- named decarbonisation programmes;
- Ofgem decisions, penalties or resilience findings;
- smart grid, customer platform or field operations awards;
- safety and operational incident evidence;
- executive commitments on net zero delivery.

Weak or commonly noisy evidence:

- tariff and consumer product pages;
- generic net zero landing pages;
- broad sustainability claims without investment detail;
- careers overview pages.

Likely hidden evidence gaps:

- technology architecture behind transition programmes;
- contractor and supplier ecosystem;
- grid constraint remediation;
- customer affordability operating pressure;
- cyber and operational technology security.

Example next-best sources:

- Ofgem publications;
- investor presentations;
- grid and infrastructure programme pages;
- contract award notices;
- supplier and technology partner announcements.

Commercial use: identify decarbonisation investment, grid pressure, customer service obligations, resilience risk and digital operations change.

### Media organisation

Minimum viable evidence:

- annual report or public service remit documents;
- audience or market strategy;
- technology and distribution evidence;
- executive leadership evidence;
- revenue, advertising or subscription performance.

High-value evidence:

- platform migration or distribution strategy;
- AI, data, rights-management or content workflow programmes;
- regulator or public accountability findings;
- major supplier/platform partnerships;
- named executive statements on audience or operating model change.

Weak or commonly noisy evidence:

- programme or content landing pages;
- generic newsroom indexes;
- consumer subscription pages;
- broad brand marketing pages.

Likely hidden evidence gaps:

- content supply-chain transformation;
- data and identity platform investment;
- AI governance and rights-management controls;
- operational efficiency programmes;
- supplier dependency on cloud or platform providers.

Example next-best sources:

- annual report strategy/risk sections;
- regulator publications;
- platform partnership announcements;
- executive speeches;
- technology job adverts for corroboration.

Commercial use: identify platform transition, content economics, audience change, AI disruption, data capability and operational efficiency pressure.

### Sports organisation

Minimum viable evidence:

- annual report or governance report;
- commercial strategy;
- broadcast, sponsorship or fan engagement evidence;
- venue and event operations evidence;
- executive leadership evidence.

High-value evidence:

- digital product or fan data platform announcements;
- venue infrastructure programmes;
- integrity, safeguarding or regulatory findings;
- major sponsorship, broadcast or ticketing technology deals;
- named supplier partnerships.

Weak or commonly noisy evidence:

- fixture pages;
- merchandise pages;
- fan content indexes;
- generic venue information pages;
- careers overview pages.

Likely hidden evidence gaps:

- fan identity and CRM architecture;
- event operations suppliers;
- safeguarding workflow systems;
- data commercialisation plans;
- cyber and venue resilience.

Example next-best sources:

- league or federation governance materials;
- venue planning documents;
- supplier announcements;
- sponsorship and broadcast deal releases;
- annual or impact reports.

Commercial use: identify fan experience investment, data and digital opportunities, venue operations, integrity risk and commercial growth priorities.

### Systems integrator / supplier

Minimum viable evidence:

- annual report and investor results;
- strategy and capability announcements;
- major contract wins;
- partner ecosystem evidence;
- sector-specific offerings.

High-value evidence:

- named client awards with value, scope or timeline;
- delivery case studies tied to measurable outcomes;
- cloud, AI, cyber or platform partnership status;
- hiring patterns in priority domains;
- executive statements on target sectors.

Weak or commonly noisy evidence:

- generic service catalogue pages;
- undated capability pages;
- broad thought leadership without client, programme or platform detail;
- duplicate press release indexes.

Likely hidden evidence gaps:

- actual delivery capability versus marketed capability;
- incumbent relationships not publicly disclosed;
- partner certification depth;
- delivery risk or failed programme history;
- sector concentration and whitespace.

Example next-best sources:

- procurement award databases;
- client annual reports naming suppliers;
- partner marketplaces;
- investor presentations;
- specialist case studies with named outcomes.

Commercial use: identify competitive positioning, partnership opportunities, delivery capability, target sectors and supplier momentum.

### Cross-blueprint evidence examples

- Bad evidence: “Jobs and contracts Procurement at DWP Working for DWP Publication scheme”. Classification: reject / diagnostics only.
- Context evidence: a regulator homepage stating its remit. Classification: context unless tied to current enforcement, strategy or investment.
- Secondary evidence: a supplier case study naming a platform implementation but omitting value and contract source. Classification: useful but biased; corroborate.
- Primary evidence: “£15 billion investment to transform Armed Forces and keep the UK safe”. Classification: primary evidence, investment pressure, high specificity.
- High-value evidence cluster: regulator finding plus investment announcement plus contract award plus named accountable executive. Classification: strong collection coverage for the relevant thesis.

## 6. Sector-specific source families

Sector-specific source families extend enterprise blueprints. Examples include:

- government: GOV.UK, NAO, PAC, select committees, departmental spending data;
- telecommunications: Ofcom, RNS, network resilience publications, infrastructure updates;
- energy and utilities: Ofgem, Ofwat, price control materials, resilience plans;
- media: Ofcom, audience measurement, public service remit reporting;
- sport: league governance, federation publications, venue and event operations reports;
- suppliers: partner marketplaces, framework awards, customer case studies and analyst coverage.

Sector-specific sources should increase relevance without creating one-off collection rules for individual organisations.

## 7. Evidence coverage map

An evidence coverage map shows which categories have sufficient evidence, weak evidence or gaps for an organisation. It should separate source presence from evidence usefulness.

A coverage map should include:

- category;
- expected source family;
- evidence found;
- evidence tier;
- freshness;
- corroboration status;
- gap status;
- collection priority.

## 8. Minimum viable coverage

Minimum viable coverage is the evidence floor required before Flora should produce meaningful downstream judgement. It should vary by enterprise type, but should normally include current strategy, recent performance or financial posture, procurement or supplier movement where relevant, leadership accountability and any known regulatory or operating pressure.

If minimum viable coverage is not met, Flora should state that intelligence confidence is constrained by evidence gaps.

## 9. Priority account coverage

Priority accounts require deeper collection. Flora should pursue additional evidence for accounts with high commercial importance, active transformation hypotheses or strategic relationship relevance.

Priority coverage may include historical trend analysis, richer supplier mapping, leadership biographies, procurement timelines, committee evidence, job advert analysis, incident history and more extensive corroboration.

## 10. Evidence gap scoring

Evidence gaps should be scored because missing evidence affects confidence. Gap scoring should consider:

- expected importance of the category;
- whether the gap blocks a transformation thesis;
- availability of replacement sources;
- freshness of last known evidence;
- account priority;
- whether absence itself is commercially meaningful.

A high gap score should create new evidence demand.

## 11. Adaptive collection strategy

Collection should adapt as evidence is found. If procurement evidence reveals a cloud migration, Flora should seek leadership, supplier, skills and delivery evidence related to that migration. If regulatory evidence reveals resilience pressure, Flora should seek investment, incident, supplier and accountable-owner evidence.

Adaptive collection should be governed by the blueprint and active theses, not by arbitrary page discovery.

## 12. Evidence Coverage Score

The Evidence Coverage Score should summarise whether Flora has enough useful evidence to reason about an enterprise and its active transformation theses. It should consider:

- category coverage;
- source diversity;
- primary evidence presence;
- freshness;
- corroboration;
- relevance to active thesis;
- missing critical categories.

Suggested coverage states:

| State | Meaning | Guidance |
| --- | --- | --- |
| Coverage sufficient | Required categories are covered by fresh, specific, diverse evidence | Proceed with normal downstream reasoning and continue monitoring |
| Coverage partial | Some required categories are useful, but gaps or weak corroboration remain | Generate caveats and next collection objectives |
| Coverage insufficient | Critical categories are missing or stale | Limit confidence and collect before strong recommendations |
| Coverage misleading / noisy | Available material is dominated by generic, duplicated or biased evidence | Replace sources, split parent pages and avoid high-confidence claims |

The score should not reward volume. Ten noisy pages are weaker than one authoritative source plus one independent corroborating source.

## 13. Collection Priority Matrix

Collection effort should be allocated by commercial priority and evidence strength:

| Commercial priority | Evidence strength | Collection action |
| --- | --- | --- |
| High | Weak | Collect urgently |
| High | Strong | Monitor and corroborate |
| Low | Weak | Defer |
| Low | Strong | Monitor |

This matrix should guide which organisations Flora spends collection effort on. High-priority accounts with weak evidence should receive targeted evidence acquisition plans, while low-priority accounts with weak evidence should not consume disproportionate collection capacity unless a new thesis or user signal raises priority.

## 14. Human feedback loop

Future UI should allow users to mark:

- useful evidence;
- weak evidence;
- wrong classification;
- noisy source;
- important source;
- missing source.

This feedback should change evidence coverage, source yield and future blueprint behaviour. For example, repeated “missing source” feedback for regulator board papers should make that source family a next-best source for similar regulators. Repeated “weak evidence” feedback for landing pages should lower their value in coverage scoring.

## 15. Example coverage map

Example for a telecommunications provider:

| Category | Expected source family | Evidence status | Gap / action |
| --- | --- | --- | --- |
| Strategy | Annual report, Capital Markets Day | Found current strategic priorities | Seek programme-level delivery evidence |
| Finance | Investor results | Found capex and cost pressure | Track next results cycle |
| Technology | Partnerships, network updates, job adverts | Partial evidence of automation | Seek supplier corroboration |
| Regulation | Ofcom publications | Found resilience and service obligations | Link to investment evidence |
| Procurement | Contract notices and supplier announcements | Weak public evidence | Search replacement sources |
| Leadership | Executive appointments and speeches | Found named technology leader | Seek direct statements |
| Risk / security | Security and resilience publications | Partial evidence | Corroborate with regulatory material |

## 16. Open questions

- How many enterprise blueprints are needed for Phase 1 without overfitting?
- Which coverage categories should be mandatory by enterprise type?
- How should Flora represent hybrid organisations that span multiple enterprise types?
- What gap score should block a high-confidence recommendation?
- How should sector blueprints evolve from user feedback and won/lost outcomes?

## Relationship to CIRM

This paper governs the enterprise collection planning layer of CIRM. It defines how collection varies by enterprise type, sector and priority so that [FP-004](FP-004-Evidence-Acquisition-Standard.md) acquisition and [FP-006](FP-006-Source-Quality-Standard.md) source quality controls produce sufficient coverage for downstream reasoning.
