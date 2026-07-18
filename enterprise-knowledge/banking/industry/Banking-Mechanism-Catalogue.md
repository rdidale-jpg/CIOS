---
asset_id: "BK-MEC-001"
title: "Banking Mechanism Catalogue and Executive Tension Model"
asset_type: "Mechanism Catalogue"
domain: "Banking"
status: "Validated"
version: "1.0"
owner: TBD
repository: "Enterprise Knowledge"
created_from: "Industry Foundation synthesis"
confidence: "High"
---

# Banking Mechanism Catalogue and Executive Tension Model — New Build Synthesis

This commission converts the completed UK Retail and Commercial Banking Industry Foundation into reusable causal intelligence: mechanisms, executive tensions, Decision Envelopes and Reinvention Signals. It follows the supplied synthesis brief and does not use the Banking Reinvention Blueprint, Founder Design Knowledge, Provider Fit, private account knowledge or future-bank design. 

## 0. Evidence anchor register

The mechanism catalogue uses these public evidence anchors:

| Evidence ID | Anchor                                                                                                                                             |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| E1          | FCA retail-banking business-model review: current accounts, mortgages, savings and challenger-bank competition. ([FCA][1])                         |
| E2          | CMA retail-banking investigation and Open Banking remedy covering personal current accounts and SME banking. ([GOV.UK][2])                         |
| E3          | FCA Financial Lives 2024: 17,950 respondents, financial resilience, vulnerability and consumer circumstances. ([FCA][3])                           |
| E4          | Bank of England July 2026 Financial Stability Report and payment-system statistics. ([Bank of England][4])                                         |
| E5          | HM Treasury designation of Microsoft, Google Cloud, AWS and Oracle as UK financial-services critical third parties. ([GOV.UK][5])                  |
| E6          | UK Finance H1 2025 fraud data and PSR APP reimbursement rules. ([UK Finance][6])                                                                   |
| E7          | Commons Library and FCA evidence on branch closures, banking hubs and access-to-cash rules. ([House of Commons Library][7])                        |
| E8          | Treasury Committee evidence of 158 banking IT failure incidents between January 2023 and February 2025. ([UK Parliament Committees][8])            |
| E9          | FCA Consumer Duty focus areas and operational-resilience expectations. ([FCA][9])                                                                  |
| E10         | Financial Ombudsman Service complaints data: current accounts, fraud/scams and service complaints. ([Financial Ombudsman][10])                     |
| E11         | Monzo and Starling evidence on digital-native scale, deposits, primary-bank usage, AI service and fraud controls. ([Monzo][11])                    |
| E12         | British Business Bank and market evidence that SME lending is shifting toward challenger, specialist and non-bank lenders. ([Financial Times][12]) |
| E13         | PRA Basel 3.1 implementation and capital-rule evidence. ([Bank of England][13])                                                                    |
| E14         | Pay.UK role in UK payment networks. ([Pay.UK][14])                                                                                                 |

---

# 1. Executive Mechanism Brief

## The seven most important banking mechanisms

**1. Current-account primacy flywheel.**
Personal and business current accounts remain the control point for salary flows, business receipts, direct debits, transaction data, payments, overdrafts, switching inertia, fraud exposure and product adjacency. This mechanism explains incumbent-bank advantage, but it is being weakened at the margin by multi-banking, digital challengers and open banking. Evidence strength: high. Mechanism change: active but not fully structural yet. E1, E2, E11.

**2. Deposit-to-investment capacity mechanism.**
Deposits support funding economics, net interest income, liquidity, structural hedge benefit and balance-sheet capacity. Stronger funding economics can finance technology, resilience, AI, simplification and regulatory change. This mechanism explains why large incumbents can absorb investment and regulatory burden better than smaller participants. Evidence strength: high for system-level economics; medium for bank-specific internal allocation. E4, E13.

**3. Digital-efficiency versus inclusion mechanism.**
Digital migration reduces marginal servicing cost and expands engagement, but branch closures, cash access, vulnerability, outages and complaint pathways create balancing pressure. Shared banking hubs and Post Office access are not simply distribution channels; they are compensating controls for physical-access withdrawal. Evidence strength: high. E3, E7, E8, E10.

**4. Faster-payments and APP-fraud control loop.**
Real-time payments create customer value and economic efficiency, but faster irreversible movement of money amplifies scam risk, reimbursement cost, friction, fraud controls and ecosystem accountability across banks, payment providers, telecoms and online platforms. Evidence strength: high. E6, E14.

**5. Legacy complexity and resilience mechanism.**
Legacy platforms, application sprawl, fragmented data, high-change risk and supplier interdependence create cost, outage, cyber, resilience and migration pressure. This is one of the most important mechanisms for later Opportunity Discovery because it connects cost-to-income, customer harm, supplier dependency and transformation capacity. Evidence strength: high for industry pressure; medium for bank-by-bank architecture. E5, E8, E9.

**6. AI-control trade-off mechanism.**
AI can assist service, fraud detection, colleague productivity, coding, knowledge search and decision support, but regulated banking converts AI into a control problem: explainability, model risk, fairness, Consumer Duty, operational resilience, data quality, human accountability and third-party dependency. Evidence strength: medium. E5, E9, E11.

**7. SME relationship-to-data lending mechanism.**
SME banking historically depends on current accounts, relationship managers and credit judgement. Challenger, specialist and embedded-finance participants are shifting some economics toward workflow data, transaction data, faster onboarding and targeted lending. Evidence strength: medium-high for market shift; lower for operating baselines and credit outcomes. E2, E12.

## Mechanisms most important for future Opportunity Discovery

The strongest later Opportunity Discovery candidates sit where mechanisms collide: legacy complexity with operational resilience; AI augmentation with control burden; APP fraud with Faster Payments; SME automation with relationship value; cloud migration with critical-third-party oversight; open banking with current-account primacy; and physical-channel rationalisation with vulnerable-customer access.

---

# 2. Banking Mechanism Catalogue

Confidence uses public evidence only.

| ID    | Mechanism                                                       | Outcome explained                                                               | Causal structure                                                                                                                                                         | Evidence         | Contradictions / Unknowns                                                                                                                         | Participant variants                                                                                                                              | Horizons                     | Falsification                                                                                            |
| ----- | --------------------------------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- | -------------------------------------------------------------------------------------------------------- |
| BM-01 | **Current-account primacy flywheel**                            | Customer retention, deposit stability, product adjacency, data advantage        | Salary/business inflows + direct debits + transaction history + identity + switching friction → relationship primacy → lending, savings, cards and service opportunities | E1, E2, E11      | Contradiction: challengers gain active users while many customers retain incumbent primary accounts. Unknown: true primary-account share by bank. | Strongest for incumbents; rising for Monzo/Starling; weaker for specialist lenders; infrastructure/fintechs attack moments not full primacy.      | Operate, Transform, Reinvent | Evidence that most customers move salary/business flows away from incumbents at scale.                   |
| BM-02 | **Customer trust and conduct feedback loop**                    | Retention, complaints, regulatory scrutiny, brand permission                    | Customer outcome + service quality + fraud handling + complaint resolution → trust or distrust → switching, complaints, regulatory intervention                          | E3, E9, E10      | Strong profitability can coexist with poor trust; complaints data may reflect claims-company activity or awareness, not only failure.             | Incumbents have legacy trust and legacy complaint exposure; challengers have UX trust but weaker long-cycle control evidence.                     | Operate, Transform           | Sustained high satisfaction and low complaints despite service/fraud failures.                           |
| BM-03 | **Digital engagement to multi-banking mechanism**               | Challenger growth and incumbent engagement pressure                             | App quality + notifications + budgeting tools + fast onboarding + card controls → frequent engagement → secondary use → possible primary-bank migration                  | E1, E11          | Digital engagement may remain secondary-account usage. Unknown: durable primary migration by cohort.                                              | Core challenger mechanism; incumbents imitate through app investment; fintechs capture tasks rather than accounts.                                | Transform, Reinvent          | Challenger growth stalls without salary/deposit migration.                                               |
| BM-04 | **Assisted-access substitution mechanism**                      | Physical access, inclusion and branch-cost pressure                             | Branch closure + cash need + vulnerable/SME needs → Post Office, hubs, community bankers, call centres → partial substitution and residual access risk                   | E3, E7           | Hubs may not replace relationship depth or full cash/business services. Unknown: customer outcomes by segment.                                    | Incumbents reduce branches; building societies may use branches as differentiation; challengers depend on digital and shared cash infrastructure. | Operate, Transform           | Evidence that hubs fully substitute branches across vulnerable and SME segments.                         |
| BM-05 | **SME relationship-data credit bridge**                         | SME lending access, commercial-banking differentiation                          | BCA flows + accounting/payment data + relationship knowledge + KYB + risk appetite → credit decision and working-capital support                                         | E2, E12          | Automation may improve speed but lose contextual judgement. Unknown: approval rates and service outcomes by lender type.                          | Incumbents retain relationships; challengers/specialists use speed and focus; accounting/embedded platforms may own workflow context.             | Transform, Reinvent          | SME customers return decisively to incumbent relationship lending and challenger share falls materially. |
| BM-06 | **Deposit acquisition and pricing mechanism**                   | Funding cost, retention and customer value                                      | Savings rates + trust + FSCS confidence + app friction + brand + rate sensitivity → deposit inflow/outflow → funding economics                                           | E1, E4, E11      | Rate-sensitive deposits can undermine low-cost funding advantage. Unknown: elasticity by segment.                                                 | Incumbents benefit from inertia; challengers use rate/app acquisition; building societies use member trust.                                       | Operate, Transform           | Deposits become fully commoditised and primary relationship no longer affects funding cost.              |
| BM-07 | **Structural hedge and NII investment-capacity mechanism**      | Profitability and transformation capacity                                       | Stable deposits + interest-rate environment + hedge policy + loan pricing → NII and RoTE → capacity for technology, resilience and change                                | E4               | Public evidence rarely reveals internal capital-allocation logic.                                                                                 | Strongest in large deposit banks/building societies; less relevant to fintechs and non-bank providers.                                            | Operate, Transform           | NII no longer funds discretionary transformation or loses relevance to bank returns.                     |
| BM-08 | **Mortgage economics cyclicality mechanism**                    | Margin, volume, customer stress and balance-sheet mix                           | Rates + house prices + affordability + refinancing + capital weights + broker distribution → mortgage volumes, pricing and risk                                          | E1, E4, E13      | Mortgage competition can compress margins despite deposit strength. Unknown: bank-specific book repricing.                                        | Core for Lloyds, Nationwide, Santander; less central for Monzo/Starling.                                                                          | Operate                      | Mortgage economics cease to be material for UK retail-banking returns.                                   |
| BM-09 | **Credit decisioning and impairment loop**                      | Lending growth, credit losses, fairness and capital consumption                 | Customer data + affordability + scorecards/models + macro conditions + risk appetite → approval/pricing/limit decisions → impairments and customer outcomes              | E3, E4, E13      | Better models can expand access or create exclusion. Unknown: model fairness and overrides.                                                       | Incumbents have deep data; specialists target niches; challengers need credit-cycle proof.                                                        | Operate, Transform           | Credit outcomes become independent of decisioning, macro and affordability controls.                     |
| BM-10 | **Capital and liquidity constraint mechanism**                  | Growth capacity, resilience and risk appetite                                   | Prudential rules + CET1/liquidity buffers + risk-weighted assets + stress testing → lending appetite, pricing, dividends and investment                                  | E4, E13          | Political growth agenda may pressure regulators to ease constraints.                                                                              | Systemic banks most constrained; smaller firms face proportional regimes; fintechs depend on bank partners.                                       | Operate                      | Capital/liquidity no longer constrains lending, pricing or investment.                                   |
| BM-11 | **APP fraud reimbursement and friction mechanism**              | Fraud loss, customer harm, payment friction, PSP economics                      | Faster Payments + social engineering + mule accounts + scam origination channels + reimbursement rules → fraud controls, payment delays, customer challenge, losses      | E6               | More friction reduces fraud but harms legitimate payments. Unknown: bank-level reimbursement rates and false positives.                           | All PSPs affected; digital challengers face onboarding/mule risk; infrastructure sets rules and standards.                                        | Operate, Transform, Reinvent | APP fraud falls materially without added friction or control investment.                                 |
| BM-12 | **AML/KYC/KYB friction-control mechanism**                      | Onboarding speed, financial-crime risk, account freezes, SME friction           | Identity/business verification + sanctions/AML screening + monitoring alerts + risk appetite → onboarding, account restrictions, SARs, remediation                       | E6, E9, E10      | Strong controls may create customer harm through false positives and account closures. Unknown: false-positive rates.                             | Hardest for fast-growth challengers and SME-heavy banks; incumbents have mature but costly controls.                                              | Operate, Transform           | Faster onboarding occurs without increased financial-crime or remediation risk.                          |
| BM-13 | **Operational-resilience service-continuity mechanism**         | Availability of money, payments, trust and regulatory confidence                | Important business services + platform mapping + impact tolerances + testing + supplier controls → outage prevention and recovery                                        | E5, E8, E9       | Digital concentration can increase both resilience capability and systemic fragility. Unknown: root causes and supplier role in outages.          | Critical for all banks; infrastructure operators and hyperscalers become systemic actors.                                                         | Operate, Transform           | Outages stop affecting customer access despite no platform/supplier change.                              |
| BM-14 | **Consumer Duty outcome-evidence mechanism**                    | Product design, servicing, vulnerability treatment and regulatory defensibility | Customer outcomes + monitoring + MI + remediation + governance → evidence that products and support deliver fair value and good outcomes                                 | E3, E9, E10      | Outcomes are harder to prove than process compliance. Unknown: bank-level outcome metrics.                                                        | Strong across all regulated firms; especially important for credit, overdrafts, vulnerability and digital journeys.                               | Operate, Transform           | FCA deprioritises outcome evidence or firms prove outcomes with process attestations only.               |
| BM-15 | **Legacy complexity cost-to-income mechanism**                  | Cost base, slow change, outage risk and transformation backlog                  | Duplicated platforms + old cores + manual controls + product variants + data fragmentation → high run cost and change friction                                           | E8, E9           | Legacy may be stable and understood; migration can be riskier than retention. Unknown: bank-specific complexity maps.                             | Incumbents most exposed; challengers have cleaner stacks but growing complexity.                                                                  | Transform                    | Legacy banks achieve challenger-level cost agility without simplification.                               |
| BM-16 | **Core/cloud migration risk-return mechanism**                  | Modernisation speed versus execution risk                                       | Cloud/core migration + API redesign + data migration + testing + supplier dependence → scalability and resilience, but migration risk                                    | E5, E8, E9       | Cloud can improve resilience while increasing concentration. Unknown: workload and dependency exposure.                                           | Incumbents face migration risk; challengers start cloud-native; building societies may partner selectively.                                       | Transform, Reinvent          | Major migrations complete with no outage, no cost overrun and no supplier lock-in.                       |
| BM-17 | **Data-quality to AI-decision utility mechanism**               | AI value, decision quality, personalisation and control                         | Clean data + lineage + consent + model governance + monitoring → useful AI assistance or decisioning; poor data → unsafe automation                                      | E5, E9, E11      | AI benefits are mostly company-reported; harms may lag deployment. Unknown: independent value evidence.                                           | All banks affected; digital-native firms may move faster; incumbents have richer but messier data.                                                | Transform, Reinvent          | AI delivers durable benefit without data remediation or model governance.                                |
| BM-18 | **Open-banking and embedded-distribution mechanism**            | Competition, account visibility, payment initiation and journey ownership       | CMA remedy + APIs + consent + TPPs + Faster Payments → external parties access data/initiate payments → bank visibility and primacy pressure                             | E2, E14          | Banks retain regulated accounts and reimbursement burden. Unknown: economics of premium APIs and bank revenue capture.                            | Fintechs/platforms gain customer moments; banks remain account providers; infrastructure standardises access.                                     | Transform, Reinvent          | Open banking usage grows but has no effect on acquisition, pricing, data or payments.                    |
| BM-19 | **Hyperscaler critical-dependency mechanism**                   | Technology resilience, concentration risk and regulatory perimeter              | Bank cloud/AI adoption + hyperscaler concentration + CTP designation → direct supervisory oversight and supplier-risk governance                                         | E5               | Oversight may improve resilience but not reduce concentration. Unknown: bank-specific critical services.                                          | Hyperscalers become quasi-infrastructure; banks become dependent consumers; SIs orchestrate migration.                                            | Transform, Reinvent          | Banks reduce systemic cloud concentration or regulators withdraw CTP oversight.                          |
| BM-20 | **AI workforce augmentation and retained-capability mechanism** | Productivity, role change, control quality and organisation design              | AI tools + workflow redesign + skills + human oversight + adoption → service productivity and decision support; weak retained capability → unmanaged automation          | E9, E11          | AI may save time but create review, compliance and exception workload. Unknown: net role and cost effect.                                         | Digital banks can embed faster; incumbents must reskill large workforces; BPO providers may redesign service models.                              | Transform, Reinvent          | AI adoption produces no measurable workflow change or only superficial assistance.                       |
| BM-21 | **Outsourcing efficiency versus control mechanism**             | Cost flexibility, operational capacity and supplier risk                        | BPO/managed services + SLAs + retained oversight + regulatory accountability → lower cost or scale, but dependency and control risk                                      | E5, E9           | Public evidence on bank-specific BPO workshare is weak.                                                                                           | Incumbents most likely to use large BPO/SI estates; challengers use software/cloud and selective outsourcing.                                     | Operate, Transform           | Banks insource material operations without cost or capability penalty.                                   |
| BM-22 | **Participant convergence mechanism**                           | Competitive reshaping and business-model blur                                   | Incumbents digitalise + challengers add lending/deposits + fintechs embed finance + technology firms become regulated dependencies → role convergence                    | E1, E5, E11, E12 | Convergence may stop at interface layer; balance-sheet banking remains distinct.                                                                  | Most visible across challengers, fintechs, hyperscalers and incumbents.                                                                           | Reinvent                     | Regulatory and capital boundaries prevent any meaningful role convergence.                               |

---

# 3. Mechanism Interaction Map

## Principal reinforcing loops

```text
BM-01 Current-account primacy
→ transaction data
→ BM-09 credit decisioning
→ product adjacency and pricing
→ customer retention
→ BM-06 deposit stability
→ BM-07 NII and investment capacity
→ BM-15 simplification / BM-17 AI / BM-13 resilience investment
→ improved service and trust
→ stronger primacy
```

```text
BM-03 digital engagement
→ frequent app use
→ more behavioural data
→ personalisation and alerts
→ customer convenience
→ secondary-account usage
→ possible primary-account migration
→ challenger deposit growth
→ lending and product expansion
```

```text
BM-18 open banking
→ external access to bank data and payment initiation
→ fintech and embedded journey ownership
→ multi-banking and comparison
→ pressure on incumbent primacy
→ incumbent app, data and pricing response
```

```text
BM-19 hyperscaler dependency
→ faster cloud and AI deployment
→ richer data/AI capabilities
→ higher concentration risk
→ CTP oversight
→ resilience and supplier-governance investment
→ slower but safer transformation
```

## Balancing and negative loops

```text
Digital migration
→ branch closure and cost reduction
→ reduced assisted access
→ vulnerability, cash and SME friction
→ complaints / conduct / political pressure
→ banking hubs, Post Office and service obligations
→ cost savings diluted
```

```text
Faster payments
→ customer convenience and lower payment friction
→ APP scam exposure
→ reimbursement and fraud losses
→ stronger controls and payment friction
→ customer frustration and complaint risk
→ trust pressure
```

```text
AI automation
→ productivity ambition
→ model, data, fairness and resilience burden
→ governance and human oversight
→ slower deployment
→ lower realised benefit than headline use-case value
```

```text
Legacy replacement
→ simplification ambition
→ migration and outage risk
→ executive caution and parallel-run cost
→ partial modernisation
→ residual complexity
```

---

# 4. Executive Tension Register

| ID    | Executive tension                             | Pressure origin                   | Mechanisms                 | Likely owners                               | Evidence        | Consequence of inaction                                  | Why hard                                                     | Unknowns                                           | Horizon             |
| ----- | --------------------------------------------- | --------------------------------- | -------------------------- | ------------------------------------------- | --------------- | -------------------------------------------------------- | ------------------------------------------------------------ | -------------------------------------------------- | ------------------- |
| ET-01 | Profitability vs customer trust               | Economic, Customer, Regulatory    | BM-02, BM-07, BM-14        | CEO, CFO, Chief Customer Officer, CRO       | E3, E4, E9, E10 | Higher complaints, regulatory pressure, weaker retention | Good returns can look like extraction during customer stress | Link between trust and deposit/switching behaviour | Operate             |
| ET-02 | Digital efficiency vs inclusion               | Customer, Cost, Regulatory        | BM-03, BM-04, BM-13        | COO, Retail CEO, Customer Director          | E3, E7, E8      | Exclusion, cash access gaps, political scrutiny          | Branches are expensive but digital is not universal          | Hub usage and outcomes                             | Operate, Transform  |
| ET-03 | Faster payments vs fraud exposure             | Customer, Technology, Regulatory  | BM-11, BM-18               | COO, Payments Director, Fraud Director, CRO | E6, E14         | Fraud losses, reimbursement cost, customer harm          | Friction prevents fraud but weakens convenience              | False-positive rates                               | Operate, Transform  |
| ET-04 | AI productivity vs control burden             | Technology, Workforce, Regulatory | BM-17, BM-20, BM-14        | CIO, COO, Chief Data/AI Officer, CRO        | E5, E9, E11     | Shadow AI, unsafe automation, missed productivity        | Regulated decisioning needs evidence and accountability      | Net benefit and adoption quality                   | Transform           |
| ET-05 | Cloud adoption vs systemic dependency         | Technology, Regulatory            | BM-16, BM-19, BM-13        | CIO, CTO, CRO, Supplier Risk                | E5, E8, E9      | Concentration risk, resilience exposure                  | Cloud enables modernisation but creates lock-in              | Service-level criticality by bank                  | Transform, Reinvent |
| ET-06 | Simplification vs migration risk              | Technology, Cost, Customer        | BM-15, BM-16, BM-13        | CIO, COO, CFO                               | E8, E9          | Run cost, outages, slow change                           | Migration can damage live banking services                   | Actual legacy maps                                 | Transform           |
| ET-07 | Personalisation vs fairness and privacy       | Customer, Regulatory, Technology  | BM-02, BM-14, BM-17        | CMO, Data/AI Officer, Compliance            | E3, E9          | Mis-selling, exclusion, privacy harm                     | Better targeting can become unfair treatment                 | Model features and consent quality                 | Transform           |
| ET-08 | Incumbent scale vs challenger agility         | Competitive, Economic             | BM-01, BM-03, BM-06, BM-22 | CEO, Strategy, Retail/Commercial CEOs       | E1, E11, E12    | Loss of high-engagement customers and SME flows          | Scale supports resilience but slows change                   | True primacy migration                             | Transform           |
| ET-09 | SME automation vs relationship value          | Customer, Competitive, Cost       | BM-05, BM-12, BM-17        | Commercial Banking CEO, CRO, COO            | E2, E12         | SME churn, poor credit outcomes, slower lending          | Automation speeds simple cases but may miss context          | Approval/service baselines                         | Transform           |
| ET-10 | Outsourcing efficiency vs retained capability | Cost, Workforce, Regulatory       | BM-21, BM-13, BM-19        | COO, CIO, Procurement, CRO                  | E5, E9          | Supplier dependency, weak control, poor recovery         | Outsourcing saves cost but accountability remains internal   | BPO workshare and controls                         | Operate, Transform  |
| ET-11 | Growth vs capital discipline                  | Economic, Regulatory              | BM-09, BM-10, BM-08        | CFO, CRO, Treasurer, Business CEOs          | E4, E13         | Overextension, impairments or under-lending              | Growth, capital and resilience cannot all be maximised       | Risk appetite by segment                           | Operate             |
| ET-12 | Innovation vs resilience                      | Technology, Customer, Regulatory  | BM-13, BM-16, BM-17, BM-18 | CIO, COO, CRO, Product                      | E5, E8, E9      | Outages, control gaps, delayed innovation                | Banking services cannot fail safely like ordinary apps       | Test evidence and incident root causes             | Transform           |

---

# 5. Decision Envelope Register

## DE-01: Digital efficiency vs inclusion

**Available decisions:** slow branch closures; expand hubs; redesign assisted digital journeys; invest in call-centre capacity; partner with Post Office; segment vulnerable customers; improve outage backup journeys.
**Not currently available:** full digital-only migration for all UK customers without access-risk consequences.
**Constraints:** FCA access-to-cash rules, Consumer Duty, reputational risk, cash dependence, local politics.
**Reversible choices:** service hours, staffing models, community-banker schedules.
**Irreversible or hard-to-reverse choices:** branch sale, lease exit, local relationship-manager removal.
**Evidence required:** hub usage, vulnerable-customer outcomes, cash-deposit/withdrawal volumes, complaints, SME impacts.

## DE-02: Faster payments vs fraud exposure

**Available decisions:** payment holds, risk-based warnings, confirmation enhancements, behavioural analytics, mule detection, scam education, receiving-bank controls, telecom/platform collaboration.
**Not currently available:** zero-friction instant payments with near-zero fraud.
**Constraints:** PSR reimbursement rules, customer expectations, Faster Payments scheme standards, fraud typology changes.
**Reversible choices:** threshold tuning, warnings, review queues.
**Irreversible choices:** major fraud-platform architecture, customer-liability policy stance.
**Evidence required:** false positives, scam origin, reimbursement rates, receiving-bank recovery, customer drop-off.

## DE-03: AI productivity vs control burden

**Available decisions:** deploy AI for summarisation, knowledge search, coding support, case triage, fraud investigation support, servicing assistance; restrict automated decisions; build model governance.
**Not currently available:** full unsupervised AI decision execution in high-impact regulated banking without governance, auditability and human accountability.
**Constraints:** Consumer Duty, model risk, data privacy, explainability, operational resilience, third-party dependency.
**Reversible choices:** assistant scope, user groups, prompt libraries, review thresholds.
**Irreversible choices:** deep workflow redesign, AI platform standardisation, workforce restructuring.
**Evidence required:** productivity baseline, quality impact, control failures, adoption, bias testing, customer harm.

## DE-04: Cloud adoption vs systemic dependency

**Available decisions:** multi-cloud strategy, exit plans, resilience testing, critical-service mapping, private connectivity, concentration limits, stronger supplier governance.
**Not currently available:** large-scale modern AI/cloud capability without material dependency on major cloud providers, unless banks accept slower or costlier alternatives.
**Constraints:** CTP oversight, operational-resilience rules, data/security requirements, legacy integration.
**Reversible choices:** workload placement for non-critical services.
**Irreversible choices:** core-platform migration, data-platform lock-in, enterprise AI tooling standard.
**Evidence required:** service criticality, exit feasibility, outage test results, supplier substitutability.

## DE-05: Simplification vs migration risk

**Available decisions:** decommission peripheral apps, refactor APIs, create strangler architectures, migrate product lines sequentially, increase testing and parallel run.
**Not currently available:** rapid replacement of critical banking cores without customer, data, payments and control risk.
**Constraints:** live-service continuity, regulatory tolerance, data quality, dependent applications, supplier capacity.
**Reversible choices:** migration sequencing and release windows.
**Irreversible choices:** core replacement path, platform vendor selection, data-model redesign.
**Evidence required:** application dependency map, incident history, product complexity, run-cost baseline.

## DE-06: SME automation vs relationship value

**Available decisions:** automate low-risk onboarding and lending, retain relationship escalation, use transaction/accounting data, create hybrid human-digital service, specialise by SME segment.
**Not currently available:** fully automated SME credit at scale without KYB, fraud, affordability, conduct and sector-context constraints.
**Constraints:** KYB/AML, credit risk, sector variation, relationship expectations, data availability.
**Reversible choices:** thresholds, escalation rules, channel mix.
**Irreversible choices:** relationship-manager restructuring, SME platform architecture.
**Evidence required:** approval times, manual-touch rates, decline reasons, customer satisfaction, credit performance.

---

# 6. Reinvention Signal Register

| ID    | Signal                                                   | Observed evidence                                                                  | Strength   | Affected mechanisms | Plausible consequence                                                   | Alternative explanation                               | Monitoring trigger                                         | Falsification                                      |
| ----- | -------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------- | ------------------- | ----------------------------------------------------------------------- | ----------------------------------------------------- | ---------------------------------------------------------- | -------------------------------------------------- |
| RS-01 | Weakening of current-account primacy                     | Challenger scale, digital engagement, open-banking remedy                          | Medium     | BM-01, BM-03, BM-18 | Primacy shifts from account ownership to journey ownership              | Secondary-account growth, not true primacy            | Salary-flow and direct-debit migration                     | Incumbent primary share remains stable             |
| RS-02 | Challengers becoming primary banks                       | Monzo reports 49% of monthly active users use it as primary bank                   | Medium     | BM-01, BM-03, BM-06 | Digital-native banks gain funding and product adjacency                 | Self-reported definition may differ from full primacy | Independent CASS/salary-flow data                          | Challenger deposits grow but primary use stagnates |
| RS-03 | Deposits becoming more price sensitive                   | Digital savings competition and challenger deposit growth                          | Medium     | BM-06, BM-07        | Lower incumbent deposit franchise value                                 | Rate cycle effect only                                | Outflows when rate gaps widen                              | Customer inertia persists despite rate gaps        |
| RS-04 | AI moving from assistance to execution                   | Starling and Monzo/Lloyds/NatWest-style AI activity; CTP concerns                  | Medium     | BM-17, BM-20        | AI becomes embedded operating control, not just productivity tool       | Company-reported pilots and PR                        | AI decisions in credit/fraud/service with audited outcomes | AI remains limited to summaries and search         |
| RS-05 | Hyperscalers becoming regulated financial infrastructure | CTP designation of Microsoft, Google Cloud, AWS and Oracle                         | High       | BM-19, BM-16, BM-13 | Tech providers become part of banking supervisory perimeter             | Oversight may remain narrow and resilience-only       | CTP incident reports or further designations               | Banks materially diversify critical services       |
| RS-06 | Open banking shifts from access to payment initiation    | CMA remedy and payment-network role                                                | Medium     | BM-18, BM-11        | Account-to-account payments challenge card economics and bank journeys  | Adoption remains niche                                | Merchant adoption and payment volumes                      | Open-banking payments plateau                      |
| RS-07 | Branch networks become shared infrastructure             | Banking hubs and FCA access-to-cash regime                                         | High       | BM-04, BM-02        | Physical access becomes industry utility, not bank-owned differentiator | Hubs remain small mitigation layer                    | Hub coverage and usage growth                              | Banks reopen proprietary networks at scale         |
| RS-08 | Fraud controls move beyond banks                         | UK Finance data shows many APP cases start online or via telecoms                  | High       | BM-11               | Cross-sector fraud operating model emerges                              | Banks still carry most liability                      | Formal platform/telecom reimbursement duties               | Fraud liability stays bank/PSP-centred             |
| RS-09 | Commercial banking becomes embedded in SME workflows     | SME lending shift to challengers/specialists and fintech/accounting platform logic | Medium     | BM-05, BM-12, BM-18 | Lending moves into cashflow/accounting journeys                         | Specialist credit appetite, not workflow shift        | Workflow-originated lending growth                         | Relationship banks regain share                    |
| RS-10 | BPO moves from labour arbitrage to AI-enabled operations | AI service evidence and outsourcing/control pressure                               | Low-medium | BM-20, BM-21        | Managed services redesign around AI, analytics and controls             | Internal bank AI absorbs benefit                      | BPO contracts explicitly priced around AI outcomes         | BPO remains headcount-based                        |

---

# 7. Participant Variants

| Participant type                               | Mechanism behaviour                                                                                                                                                                                                |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Major incumbents**                           | Strongest in BM-01, BM-06, BM-07, BM-10 and BM-15. They own deposit scale, current-account flows and regulatory maturity, but carry legacy complexity, branch-access tension and higher transformation risk.       |
| **Building societies**                         | Strong in savings, mortgages, trust and community access. They may use branches/member service as differentiation, but are constrained by mortgage cyclicality, capital, technology capacity and mutual economics. |
| **Digital-native challengers**                 | Strong in BM-03, BM-17 and app-led service. Growth increasingly depends on turning engagement into primary banking, deposits, lending discipline, fraud control and regulatory maturity.                           |
| **Specialist lenders**                         | Strong in focused credit niches and intermediary distribution. Less exposed to current-account primacy, more exposed to funding cost, credit-cycle discipline and broker/platform relationships.                   |
| **Infrastructure operators**                   | Own rails and standards rather than customer relationships. Their mechanisms centre on resilience, interoperability, payment risk, settlement and industry change coordination.                                    |
| **Fintechs and embedded-finance participants** | Capture customer moments, workflow data, payment initiation, merchant journeys and SME context. They often depend on partner banks, APIs, payment schemes and regulatory permissions.                              |
| **Technology providers**                       | Increasingly embedded in platform, data, AI, cloud and resilience mechanisms. Hyperscalers are now regulated critical dependencies; software providers create lock-in and migration constraints.                   |
| **Systems integrators**                        | Shape transformation capacity, migration delivery, architecture integration and programme execution. Their influence is high, but supplier benefit claims need independent validation.                             |
| **BPO and managed-service providers**          | Operate service, remediation, complaints, operations and technology processes where banks externalise workload. Their future role may shift toward AI-enabled operations, but public evidence is weak.             |

---

# 8. Opportunity Discovery Inputs

These are not Opportunity Twins.

| Candidate | Mechanism + tension                                  | Enterprise types affected                  | Evidence strength | Value domain                            | Dependency complexity | Unknowns                              | Why later discovery may be justified                                                 |
| --------- | ---------------------------------------------------- | ------------------------------------------ | ----------------- | --------------------------------------- | --------------------- | ------------------------------------- | ------------------------------------------------------------------------------------ |
| ODI-01    | BM-15/BM-16 + ET-06 simplification vs migration risk | Incumbents, building societies             | High              | Cost, resilience, change speed          | Very high             | App maps, core dependencies, run cost | Mechanism sits at the centre of cost-to-income, outages and transformation capacity. |
| ODI-02    | BM-11 + ET-03 faster payments vs fraud               | Banks, PSPs, infrastructure, fintechs      | High              | Fraud loss, trust, operations           | High                  | False positives, reimbursement rates  | Strong regulatory and customer-harm pressure.                                        |
| ODI-03    | BM-17/BM-20 + ET-04 AI productivity vs control       | All banks, BPO, SIs, cloud                 | Medium            | Productivity, service, risk             | High                  | Net benefit, model risk, adoption     | High activity but weak independent benefits.                                         |
| ODI-04    | BM-19 + ET-05 cloud vs systemic dependency           | Banks, hyperscalers, regulators            | High              | Resilience, architecture, supplier risk | Very high             | Critical-service exposure             | CTP designation makes dependency visible and regulated.                              |
| ODI-05    | BM-05 + ET-09 SME automation vs relationship value   | Commercial banks, challengers, specialists | Medium-high       | Revenue, credit, customer growth        | Medium-high           | Approval outcomes, KYB friction       | SME banking is structurally contested.                                               |
| ODI-06    | BM-04 + ET-02 digital efficiency vs inclusion        | Incumbents, building societies, hubs       | High              | Cost, access, trust                     | Medium                | Hub outcomes, cash demand             | Branch-to-shared-access model is live and unresolved.                                |
| ODI-07    | BM-18 + RS-06 open-banking payments                  | Banks, fintechs, merchants, PSPs           | Medium            | Revenue, distribution, data             | Medium-high           | Adoption economics                    | Could change payment economics and account primacy.                                  |
| ODI-08    | BM-21 + ET-10 outsourcing vs retained capability     | Incumbents, BPO, SIs                       | Low-medium        | Cost, capacity, control                 | High                  | Workshare, contract terms             | Public evidence is weak but mechanism may be material.                               |

---

# 9. Research Gaps — Mechanism-Specific Evidence Demand

| Gap ID | Evidence needed                                                                             | Mechanisms affected | Priority  |
| ------ | ------------------------------------------------------------------------------------------- | ------------------- | --------- |
| RG-01  | Bank-by-bank primary-account, salary-flow and direct-debit share                            | BM-01, BM-03        | Very high |
| RG-02  | Deposit elasticity by bank, rate tier and customer segment                                  | BM-06, BM-07        | High      |
| RG-03  | Bank-specific application/core/platform dependency maps                                     | BM-13, BM-15, BM-16 | Very high |
| RG-04  | Supplier contracts, renewal dates, cloud workload criticality and exit plans                | BM-16, BM-19, BM-21 | Very high |
| RG-05  | Independent AI benefit evidence: baseline, adoption, quality, control failures              | BM-17, BM-20        | Very high |
| RG-06  | APP fraud loss, reimbursement, false-positive and friction metrics by bank                  | BM-11               | Very high |
| RG-07  | SME approval rates, KYB cycle times, relationship-manager coverage and customer outcomes    | BM-05, BM-12        | High      |
| RG-08  | Branch/hub/Post Office usage and outcomes for vulnerable customers and SMEs                 | BM-04, BM-14        | High      |
| RG-09  | Complaint root-cause data by product, channel and customer segment                          | BM-02, BM-14        | High      |
| RG-10  | BPO and managed-service workshare across servicing, remediation, operations and collections | BM-21               | High      |
| RG-11  | Credit decisioning model governance, override rates and fairness outcomes                   | BM-09, BM-17        | High      |
| RG-12  | Operational-resilience test results, impact tolerances and incident root causes             | BM-13, BM-19        | Very high |

---

# 10. Required Additional Questions

## 1. Which three mechanisms most strongly explain incumbent-bank advantage?

1. **BM-01 Current-account primacy flywheel** — control of payment flows, deposits, data and product adjacency.
2. **BM-06 Deposit acquisition and pricing** — funding advantage from trusted, sticky deposit relationships.
3. **BM-10 Capital and liquidity constraint mechanism** — scale, capital depth and regulatory maturity support resilience and lending capacity.

## 2. Which three mechanisms most strongly explain challenger growth?

1. **BM-03 Digital engagement to multi-banking** — superior app experience can create daily usage and eventual primacy.
2. **BM-05 SME relationship-data credit bridge** — challengers/specialists use focused underwriting and faster journeys in SME niches.
3. **BM-22 Participant convergence** — challengers add lending, savings, business banking and platform services, narrowing the incumbent proposition gap.

## 3. Which mechanisms are most likely to change due to AI?

BM-17 data-quality to AI-decision utility, BM-20 AI workforce augmentation, BM-11 fraud controls, BM-12 AML/KYB friction, BM-09 credit decisioning, BM-14 Consumer Duty outcome monitoring and BM-21 BPO operating model.

## 4. Which mechanisms are most constrained by regulation?

BM-10 capital/liquidity, BM-11 APP reimbursement, BM-12 AML/KYC/KYB, BM-13 operational resilience, BM-14 Consumer Duty, BM-19 critical-third-party dependency and BM-09 credit/affordability decisioning.

## 5. Which mechanisms create greatest customer harm when they fail?

BM-11 APP fraud, BM-13 operational resilience, BM-09 credit decisioning, BM-12 AML/KYC/KYB false positives, BM-04 assisted access and BM-14 Consumer Duty outcome monitoring.

## 6. Which mechanisms determine investment capacity?

BM-06 deposit acquisition/pricing, BM-07 structural hedge and NII, BM-10 capital/liquidity, BM-08 mortgage economics, BM-09 impairments and BM-15 cost-to-income improvement.

## 7. Which mechanisms create supplier or platform dependency?

BM-16 core/cloud migration, BM-19 hyperscaler dependency, BM-15 legacy complexity, BM-18 open-banking/API dependency, BM-21 outsourcing/BPO and BM-13 operational resilience.

## 8. Which mechanisms are weakly understood from public evidence?

BM-21 BPO dependence, BM-17 AI benefit and model control, BM-16 bank-specific migration risk, BM-12 KYB/AML false positives, BM-05 SME relationship value and BM-06 deposit elasticity.

## 9. Which tensions are likely to become board-level priorities during 2026–2028?

ET-04 AI productivity vs control burden, ET-05 cloud adoption vs systemic dependency, ET-06 simplification vs migration risk, ET-03 faster payments vs fraud exposure, ET-02 digital efficiency vs inclusion and ET-11 growth vs capital discipline.

## 10. Which mechanism changes could create entirely new banking business models?

Open-banking payment initiation replacing card-like journeys; SME banking embedded in accounting/workflow platforms; banks offering software/platform services; AI-assisted regulated operations; shared physical banking infrastructure; regulated cloud/AI infrastructure becoming part of banking’s formal operating model.

---

# 11. Recommended Validation Priorities

## First five mechanisms to validate through Enterprise Twins

1. **BM-01 Current-account primacy flywheel** — validates the basic economic control point of UK banking.
2. **BM-07 Structural hedge and NII investment capacity** — explains why some banks can fund reinvention and others cannot.
3. **BM-11 APP fraud reimbursement and friction** — high customer harm, high regulatory pressure, high operating change.
4. **BM-15 Legacy complexity cost-to-income** — likely explains transformation drag across incumbents.
5. **BM-17 Data-quality to AI-decision utility** — essential before any future-state AI design.

## First four banks for contrasting mechanism behaviour

1. **Lloyds Banking Group** — scale incumbent, mortgage/deposit/current-account economics, technology transformation.
2. **NatWest Group** — UK-focused incumbent with retail/commercial banking, simplification and AI/cloud activity.
3. **Monzo Bank** — digital-native challenger testing primacy, deposits, app engagement and growth economics.
4. **Nationwide including Virgin Money** — mutual/building-society model, branch commitment, mortgage/savings economics and integration complexity.

These four maximise contrast across incumbent scale, commercial banking, challenger primacy, mutual economics, physical access and platform maturity.

## First three executive tensions for deeper research

1. **ET-04 AI productivity vs control burden** — most likely to create misunderstood transformation claims.
2. **ET-03 Faster payments vs fraud exposure** — clearest customer-harm and regulatory-economic tension.
3. **ET-06 Simplification vs migration risk** — central to cost, resilience, investment capacity and supplier dependency.

## Evidence needed before future-state design

Future-state design should not start until the programme has: bank-specific platform maps; AI baseline and benefit evidence; primary-account/deposit behaviour; fraud economics; BPO workshare; supplier dependency maps; operational-resilience incident root causes; Consumer Duty outcome data; SME onboarding and lending cycle data; and branch/hub customer-outcome evidence.

## Appropriate next Researcher commission

**Commission:** Build four contrasting Enterprise Twins — Lloyds, NatWest, Monzo and Nationwide/Virgin Money — using BM-01, BM-07, BM-11, BM-15 and BM-17 as the first structured mechanism-validation spine. The output should preserve mechanism-specific Observations and test whether the industry mechanisms behave differently by enterprise type.

---

# 12. What Flora Learned

## Mechanisms Flora should remember permanently

Banking works through controlled money movement, regulated risk-taking, deposit funding, trust, payments, data, operational resilience and capital constraints. The most reusable mechanisms are current-account primacy, deposit-funded investment capacity, credit decisioning, fraud-control friction, operational resilience, legacy complexity and third-party dependency.

## Mechanisms that remain industry hypotheses

AI decision execution, BPO-to-AI operations, open-banking payment displacement, branch-hub full substitution, SME workflow banking and challenger primary-bank migration remain hypotheses until validated inside Enterprise Twins.

## Patterns strengthened

* Scale creates resilience and investment capacity, but also legacy drag.
* Digital migration creates new inclusion and resilience obligations.
* Supplier concentration becomes an enterprise-governance problem.
* AI value depends on data, controls and adoption, not model capability alone.
* Customer harm often appears where speed, automation and weak controls intersect.

## Patterns weakened

* “Better digital UX wins banking” is too weak; primacy, trust, deposits, risk and regulation matter.
* “Branch closure equals pure cost saving” is weakened by access obligations and outage risk.
* “Cloud migration is just IT modernisation” is weakened by CTP designation and systemic-dependency evidence.
* “AI productivity is self-evident” is weakened by the lack of independent, bank-specific benefit evidence.

## New Pattern candidates

* Regulated third-party infrastructure pattern.
* Shared physical-access utility pattern.
* Real-time payment fraud-friction pattern.
* Primary-account-to-investment-capacity pattern.
* SME workflow-credit convergence pattern.
* AI-assisted retained-organisation pattern.

## Cross-industry comparison opportunities

Banking mechanisms should later be compared with telecoms, utilities, healthcare and government service delivery where customer-critical infrastructure, regulated resilience, legacy complexity, inclusion and supplier concentration interact.

## Mechanisms that should become structured Industry Twin objects

BM-01, BM-07, BM-11, BM-13, BM-15, BM-17, BM-19 and BM-22 should become structured Industry Twin objects with stable IDs, observation ledgers, evidence lineage, participant variants and refresh triggers.

## What must remain Unknown

Exact bank-specific supplier workshare, platform architecture, primary-account migration, AI benefit, BPO exposure, operational root causes, credit model fairness, Consumer Duty outcome evidence, fraud false positives and executive ownership remain Unknown from public evidence alone.

**The Banking Mechanism Catalogue is complete. It converts the Industry Foundation into reusable causal intelligence, executive tensions, Decision Envelopes and Reinvention Signals suitable for Enterprise Twin validation and later Opportunity Discovery.**

[1]: https://www.fca.org.uk/publications/multi-firm-reviews/strategic-review-retail-banking-business-models?utm_source=chatgpt.com "Strategic review of retail banking business models"
[2]: https://www.gov.uk/cma-cases/review-of-banking-for-small-and-medium-sized-businesses-smes-in-the-uk?utm_source=chatgpt.com "Retail banking market investigation"
[3]: https://www.fca.org.uk/financial-lives/financial-lives-2024?utm_source=chatgpt.com "Financial Lives 2024 survey"
[4]: https://www.bankofengland.co.uk/financial-stability-report/2026/july-2026?utm_source=chatgpt.com "Financial Stability Report - July 2026 (to be published at ..."
[5]: https://www.gov.uk/government/news/uk-financial-system-strengthened-with-new-safeguards-for-major-technology-providers?utm_source=chatgpt.com "UK financial system strengthened with new safeguards for major technology providers"
[6]: https://www.ukfinance.org.uk/news-and-insight/press-release/over-ps600-million-stolen-fraudsters-in-first-half-2025?utm_source=chatgpt.com "Over £600 million stolen by fraudsters in first half of 2025"
[7]: https://commonslibrary.parliament.uk/research-briefings/cbp-9453/?utm_source=chatgpt.com "Access to cash and banking services - Commons Library"
[8]: https://committees.parliament.uk/committee/158/treasury-committee/news/205611/more-than-one-months-worth-of-it-failures-at-major-banks-and-building-societies-in-the-last-two-years/?utm_source=chatgpt.com "More than one month's worth of IT failures at major banks ..."
[9]: https://www.fca.org.uk/publications/corporate-documents/consumer-duty-focus-areas?utm_source=chatgpt.com "Our Consumer Duty focus areas"
[10]: https://www.financial-ombudsman.org.uk/businesses/resolving-complaint/our-insight/annual-complaints-data-and-insight-2025-26?utm_source=chatgpt.com "Annual complaints data and insight 2025/26"
[11]: https://monzo.com/annual-report?utm_source=chatgpt.com "Monzo 2026 Annual Report | Our Numbers"
[12]: https://www.ft.com/content/de4b95e7-d500-4012-940d-d7d4f364be3c?utm_source=chatgpt.com "Rachel Reeves makes last-minute pitch for senior job under Andy Burnham"
[13]: https://www.bankofengland.co.uk/news/2026/june/pra-adjustments-market-risk-internal-model-approach-under-basel31?utm_source=chatgpt.com "PRA sets out adjustments to its market risk internal model ..."
[14]: https://www.wearepay.uk/?utm_source=chatgpt.com "Home - Pay.UK - The recognised operator and standards ..."
