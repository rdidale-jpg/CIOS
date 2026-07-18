---
asset_id: "BK-CMP-002"
title: "Four-Bank Mechanism Differential Matrix"
asset_type: "Differential Matrix"
domain: "Banking"
status: "Validated"
version: "2.1"
owner: TBD
repository: "Enterprise Knowledge"
created_from: "Correction / reconciliation"
confidence: "High"
---

# Four-Bank Mechanism Differential Matrix v2.1 — Correction

Run mode: correction / reconciliation, not rebuild.
Authority: the original Banking Mechanism Catalogue is the sole authority for BM-01 through BM-22.
Correction target: Four-Bank Mechanism Differential Matrix v2.
Correction reason: mechanism identifier drift occurred where enterprise-local labels were treated as canonical BM identifiers. The most material issues are Monzo’s local use of BM-03, NatWest’s local use of BM-06, and Nationwide’s local use of BM-10.

## 1. Executive Correction Summary

The v2 comparison is not invalidated, but several rows require correction.

The main issue is semantic drift:

1. Monzo local “BM-03” was labelled “Deposit-funded banking economics mechanism.” That is not canonical BM-03. Canonical BM-03 is Digital engagement to multi-banking mechanism. Monzo’s local BM-03 should be treated as a compound challenger mechanism involving BM-03, BM-06, BM-09 and BM-10, with product-adjacency elements.

2. NatWest local “BM-06” was labelled “Digital-primary relationship mechanism.” That is not canonical BM-06. Canonical BM-06 is Deposit acquisition and pricing mechanism. NatWest’s local BM-06 should map mainly to BM-03, with links to BM-01 and BM-05. NatWest’s actual deposit-pricing and deposit-franchise evidence remains canonical BM-06.

3. Nationwide local “BM-10” was used in different ways. Where it means capital strength, liquidity, retained surplus and investment allocation, it maps to canonical BM-10 Capital and liquidity constraint mechanism as a mutual variant. Where it means trust/customer retention, it maps to canonical BM-02 Customer trust and conduct feedback loop, not BM-10. Nationwide explicitly states that mutual ownership changes BM-07/BM-10 because surplus allocation becomes a three-way decision between capital strength, member value and transformation investment.

The corrected v2.1 position is:
- BM-03 is demoted from Strong to Supported because the multi-banking / primary-conversion mechanism is strongly visible in Monzo but not yet validated across multiple challenger cases.
- BM-06 remains Strong, but NatWest’s local “BM-06” label no longer contributes to BM-06 confidence unless it concerns deposits/pricing.
- BM-10 remains Strong, but Nationwide’s “trust/customer retention” usage is remapped to BM-02.
- BM-21 remains Candidate; commercial opportunity material from the Twins must not influence mechanism confidence.
- No mechanism is retired.
- No mechanism reaches Established status.

## 2. Canonical BM Assurance Register

Every final row must retain these canonical definitions.

| BM ID | Canonical mechanism name | Optional comparison label allowed? | Assurance |
|---|---|---|---|
| BM-01 | Current-account primacy flywheel | Current-account primacy | Preserved |
| BM-02 | Customer trust and conduct feedback loop | Trust/conduct feedback | Preserved |
| BM-03 | Digital engagement to multi-banking mechanism | Digital engagement / primary-conversion pressure | Preserved; corrected from local misuse |
| BM-04 | Assisted-access substitution mechanism | Branch/access substitution | Preserved |
| BM-05 | SME relationship-data credit bridge | SME/commercial relationship data | Preserved |
| BM-06 | Deposit acquisition and pricing mechanism | Deposit franchise / deposit pricing | Preserved; corrected from local misuse |
| BM-07 | Structural hedge and NII investment-capacity mechanism | Hedge/NII investment capacity | Preserved |
| BM-08 | Mortgage economics cyclicality mechanism | Mortgage-cycle economics | Preserved |
| BM-09 | Credit decisioning and impairment loop | Credit/impairment loop | Preserved |
| BM-10 | Capital and liquidity constraint mechanism | Capital/liquidity discipline | Preserved; corrected from local misuse |
| BM-11 | APP fraud reimbursement and friction mechanism | APP fraud/friction | Preserved |
| BM-12 | AML/KYC/KYB friction-control mechanism | Financial-crime onboarding/control friction | Preserved |
| BM-13 | Operational-resilience service-continuity mechanism | Resilience continuity | Preserved |
| BM-14 | Consumer Duty outcome-evidence mechanism | Outcome-evidence mechanism | Preserved |
| BM-15 | Legacy complexity cost-to-income mechanism | Legacy simplification/cost-to-income | Preserved |
| BM-16 | Core/cloud migration risk-return mechanism | Core/cloud migration | Preserved |
| BM-17 | Data-quality to AI-decision utility mechanism | Data/AI decision utility | Preserved |
| BM-18 | Open-banking and embedded-distribution mechanism | Open banking / embedded distribution | Preserved |
| BM-19 | Hyperscaler critical-dependency mechanism | Hyperscaler dependency | Preserved |
| BM-20 | AI workforce augmentation and retained-capability mechanism | AI workforce augmentation | Preserved |
| BM-21 | Outsourcing efficiency versus control mechanism | BPO / outsourcing control | Preserved |
| BM-22 | Participant convergence mechanism | Participant convergence | Preserved |

## 3. Mechanism Identifier Reconciliation Register

### 3.1 Lloyds

| Enterprise | Local identifier or label | Local meaning | Canonical BM identifier | Mapping type | Confidence | Conflict / ambiguity | Resolution |
|---|---|---|---|---|---:|---|---|
| Lloyds | BM-01 Current-account primacy | Current accounts, deposits, hedge-eligible balances | BM-01 | Exact canonical match | High | None | Retain |
| Lloyds | BM-03 Digital engagement | App usage, mobile current-account opening, digital sales | BM-03 | Participant-type variant | Medium | Digital usage may not prove multi-banking or primacy | Retain as Lloyds incumbent digital-engagement variant, not proof of primary strengthening |
| Lloyds | BM-06 Deposit acquisition/pricing | Deposit franchise and price sensitivity | BM-06 | Exact canonical match | High | Deposit elasticity unknown | Retain |
| Lloyds | BM-07 Structural hedge/NII | Hedge income and NII investment capacity | BM-07 | Exact canonical match | High | Internal allocation unknown | Retain |
| Lloyds | BM-10 Capital/liquidity discipline | Capital generation and CET1 discipline | BM-10 | Exact canonical match | High | None material | Retain |
| Lloyds | BM-15 Legacy complexity cost-to-income | App decommissioning, cloud migration, cost savings | BM-15 | Exact canonical match | Medium-high | Causality not fully isolated | Retain |
| Lloyds | BM-16 Cloud/core migration | Cloud migration and migration risk | BM-16 | Exact canonical match | Medium | Core exposure unknown | Retain |
| Lloyds | BM-17 Data/AI utility | Vertex AI, model migration, AI platform | BM-17 | Exact canonical match | Medium | Benefit validation weak | Retain |
| Lloyds | BM-20 AI workforce augmentation | Copilot, AI Academy, GenAI use cases | BM-20 | Exact canonical match | Medium | Net productivity unknown | Retain |
| Lloyds | BM-04 assisted access / channel substitution | Branch and Halifax/Lloyds migration effects | BM-04 | Enterprise-specific variant | Medium | Brand migration and physical access overlap | Retain as branch/brand channel variant |
| Lloyds | Brand simplification mechanism | Halifax-to-Lloyds brand/app/branch simplification | None | New Mechanism Candidate | Medium | Related to BM-02, BM-03, BM-04, BM-15 but not equivalent | Keep as LBG-CAND-001 |
| Lloyds | Fintech acquisition for customer-moment control | Curve acquisition / payment flexibility | BM-18 / BM-22 | Related but not equivalent | Medium-low | Not enough evidence of economic effect | Keep as related evidence, not canonical mechanism |
| Lloyds | Compound incumbent loop | Deposit/current account -> hedge/NII -> capital -> investment -> simplification | BM-01 + BM-06 + BM-07 + BM-10 + BM-15 | Compound mechanism | High | Final primacy renewal unproven | Preserve as LBG-COMP-001 |

### 3.2 NatWest

NatWest’s Twin explicitly says Lloyds BM-01, BM-05 and BM-06 were human-supplied comparison mechanisms, not NatWest evidence; this makes local mapping control especially important.

| Enterprise | Local identifier or label | Local meaning | Canonical BM identifier | Mapping type | Confidence | Conflict / ambiguity | Resolution |
|---|---|---|---|---|---:|---|---|
| NatWest | BM-01 Current-account and deposit franchise | Current accounts/savings -> stable deposits -> NIM/hedge -> investment | BM-01 + BM-06 + BM-07 | Compound mechanism | High | Local label blends three BMs | Split in canonical matrix |
| NatWest | BM-06 Digital-primary relationship mechanism | Digital engagement, Cora, app, APIs, digitally-first C&I | BM-03, plus BM-01/BM-05 links | Related but not equivalent | High | Conflict: canonical BM-06 is deposit acquisition/pricing | Corrected: do not use local BM-06 to validate canonical BM-06 |
| NatWest | BM-05 Commercial-banking relationship flywheel | RM + sector + payments/FX/lending + APIs -> deeper relationship | BM-05 | Participant-type variant | High | Commercial/corporate scope broader than SME | Retain as commercial-incumbent variant |
| NatWest | Simplification-to-investment-capacity | Simplification -> savings -> investment capacity -> tech/AI/cloud | BM-15 + BM-16 + BM-20 | Compound mechanism | High | App retirement attribution incomplete | Preserve as NTW-COMP-001 |
| NatWest | AI colleague augmentation | Cora, OpenAI, coders, RMs, contact-centre AI | BM-20, linked to BM-17 | Exact / participant-type variant | High | Benefit/control validation incomplete | Retain as scale-AI variant |
| NatWest | Cloud critical dependency | AWS/Accenture/OpenAI dependency and CTP relevance | BM-19, linked to BM-16 | Exact / participant-type variant | Medium-high | Critical workloads unknown | Retain |
| NatWest | Trust recovery/history mechanism | Post-bailout/private ownership trust recovery | BM-02 | Enterprise-specific variant | Medium | NatWest-specific historical driver | Keep as NTW-CAND-001 |
| NatWest | NTW-BM-01 | Deposit/current-account franchise economics | BM-01 + BM-06 + BM-07 | Compound mechanism | High | Blends current-account, deposit pricing and hedge/NIM | Split |
| NatWest | NTW-BM-05 | Commercial-banking relationship flywheel | BM-05 | Participant-type variant | High | C&I wider than SME | Retain variant |
| NatWest | NTW-BM-06 | Digital primary-relationship reinforcement | BM-03 | Participant-type variant | Medium-high | Local ID conflicts with canonical BM-06 | Rename as NTW-VAR-DIG-001 |
| NatWest | NTW-SIMP-01 | Simplification-to-investment-capacity | BM-15 + BM-16 + BM-20 | Compound mechanism | Medium-high | Not a single BM | Preserve as compound |
| NatWest | NTW-AI-01 | AI-enabled relationship bank | BM-17 + BM-20 + BM-05 | Compound / participant variant | Medium-high | Not equivalent to BM-17 alone | Preserve as compound |
| NatWest | NTW-CLOUD-01 | Cloud partnership dependency | BM-19 + BM-16 | Compound mechanism | Medium-high | Workload criticality unknown | Preserve |
| NatWest | NTW-TRUST-01 | Public-trust recovery | BM-02 | Enterprise-specific variant | Medium | NatWest-specific | Preserve as candidate |

### 3.3 Nationwide / Virgin Money

Nationwide’s Twin states that mutual ownership changes BM-07/BM-10, and that BM-04 behaves differently because branches are a brand, trust, inclusion and acquisition mechanism rather than simply a cost frontier.

| Enterprise | Local identifier or label | Local meaning | Canonical BM identifier | Mapping type | Confidence | Conflict / ambiguity | Resolution |
|---|---|---|---|---|---:|---|---|
| Nationwide | MECH-NW-001 Mutual value allocation | Profit -> capital -> member value -> retention/trust -> deposits/mortgages | BM-02 + BM-06 + BM-10 | Compound mechanism | High | Not equivalent to BM-10 alone | Preserve as NW-COMP-001 |
| Nationwide | MECH-NW-002 Mortgage-savings mutual flywheel | Member savings -> mortgage capacity -> member relationship -> funding resilience | BM-06 + BM-08 + BM-10 | Compound mechanism | High | Mutual savings and mortgage economics intertwined | Preserve as NW-COMP-002 |
| Nationwide | MECH-NW-003 Branch network as strategic differentiation | Branch promise -> trust/acquisition/product openings | BM-04 + BM-02 | Participant-type variant | High | BM-04 behaves opposite to cost-removal variant | Retain as mutual branch variant |
| Nationwide | MECH-NW-004 Virgin Money integration as reinvention catalyst | Acquisition -> diversification -> duplicated platforms -> migration risk -> member value | BM-15 + BM-16 + BM-10 + BM-02 | Compound / enterprise-specific candidate | Medium-high | Not an existing BM | Preserve as NW-CAND-001 and NW-COMP-003 |
| Nationwide | MECH-NW-005 Platform/payments modernisation under trust constraint | Payments/cloud/core modernisation -> resilience -> supplier risk | BM-16 + BM-13 + BM-19 | Compound mechanism | Medium | Supplier and end-state architecture unknown | Preserve |
| Nationwide | Local BM-04 | Physical access / branch mechanism | BM-04 | Participant-type variant | High | None; meaning differs by participant | Retain as mutual branch-trust variant |
| Nationwide | Local BM-07/BM-10 mutual economics | Surplus allocation, structural hedge, capital and member value | BM-07 + BM-10 + BM-02 | Compound mechanism | High | BM-10 alone insufficient | Split into BM-10 capital/liquidity and BM-02 member trust |
| Nationwide | Mutual Variant Matrix “BM-10 Trust/customer retention” | Trust, satisfaction, Fairer Share, member retention | BM-02 | Rejected mapping to BM-10 | High | Conflict: canonical BM-10 is capital/liquidity, not trust | Correct row to BM-02 |
| Nationwide | Branch-enabled omnichannel opportunity material | Branch service, vulnerable-customer service, tooling | BM-04 / BM-14 only where mechanism evidence | Commercial leakage risk | Medium | Opportunity classification may bias mechanism | Quarantine commercial material |

### 3.4 Monzo

Monzo’s Twin explicitly labelled local BM-03 as “Deposit-funded banking economics mechanism,” with deposits, revenue, balances, borrowing, payments, wealth, subscriptions and fees. That local label is not canonical BM-03.

| Enterprise | Local identifier or label | Local meaning | Canonical BM identifier | Mapping type | Confidence | Conflict / ambiguity | Resolution |
|---|---|---|---|---|---:|---|---|
| Monzo | BM-01 Current-account primacy mechanism | Main bank / primary-bank conversion | BM-01 + BM-03 | Participant-type variant | Medium-high | Active-user primacy ≠ total customer primacy | Retain challenger-primary variant |
| Monzo | BM-03 Deposit-funded banking economics mechanism | Engagement/current-account activity -> deposits, lending, fees, profitability | BM-06 + BM-09 + BM-10 + BM-22, linked to BM-03 | Compound mechanism | High | Conflict: canonical BM-03 is digital engagement to multi-banking | Rename as MONZO-COMP-001 |
| Monzo | App engagement to primary-bank conversion | MAU -> primary use -> deposits/product depth | BM-03 + BM-01 | Participant-type variant | High | Salary/direct-debit data missing | Retain as challenger variant |
| Monzo | Notification and control loop | App controls, alerts, engagement and trust | BM-03 + BM-02 | New Mechanism Candidate | Medium | Not enough causal proof | Preserve as MONZO-CAND-001 |
| Monzo | Subscription-to-relationship-depth | Subscriptions deepen product relationship | BM-22 / BM-03 related | New Mechanism Candidate | Medium | Not equivalent to canonical mechanism | Preserve as MONZO-CAND-002 |
| Monzo | Cloud-native agility versus concentration | AWS/Kubernetes/microservices + Stand-in | BM-16 + BM-19 + BM-13 | Participant-type variant / compound | Medium-high | Supplier exit feasibility unknown | Preserve as MONZO-COMP-002 |
| Monzo | Rapid growth versus control maturity | Growth creates AML/APP/control stress | BM-12 + BM-11 + BM-10 | Compound mechanism | High | Not one canonical BM | Preserve as MONZO-COMP-003 |
| Monzo | Community and brand advocacy | Word-of-mouth, NPS, advocacy | BM-02 + BM-03 | Related but not equivalent | Medium | Correlation not causation | Preserve as candidate evidence |
| Monzo | Digital primacy to deposit-funded lending | Engagement -> primacy -> deposits -> lending/profitability | BM-01 + BM-03 + BM-06 + BM-09 + BM-10 | Compound mechanism | Medium-high | Through-cycle credit and capital unknown | Preserve as MONZO-COMP-004 |

## 4. Corrected Affected Rows from v2

Only affected rows are revised. Unaffected rows retain v2 status.

| BM ID | Canonical definition preserved | v2 issue | v2.1 correction | Applicability correction | Confidence correction | Material change |
|---|---|---|---|---|---|---|
| BM-01 | Current-account primacy flywheel | Monzo primacy and incumbent primacy were blended too tightly | Split display into incumbent primacy and challenger primary-conversion variant | Lloyds Dominant; NatWest Dominant; Nationwide Significant; Monzo Significant | Strong retained | Variant clarification |
| BM-02 | Customer trust and conduct feedback loop | Nationwide local “BM-10 Trust/customer retention” should have mapped here | Add Nationwide mutual trust/member-value evidence to BM-02, not BM-10 | Nationwide remains Dominant | Strong retained | Applicability lineage corrected |
| BM-03 | Digital engagement to multi-banking mechanism | Monzo local BM-03 was not canonical BM-03; NatWest local BM-06 also not canonical BM-06 | Canonical BM-03 covers app/digital engagement, multi-banking and primary-conversion pressure only | Lloyds Moderate; NatWest Moderate; Nationwide Moderate; Monzo Dominant | Strong -> Supported | Confidence change |
| BM-04 | Assisted-access substitution mechanism | Branch cost-burden and branch trust-differentiator risked being treated as same expression | Preserve canonical row; add participant variants | Lloyds Moderate; NatWest Moderate; Nationwide Dominant; Monzo Weak | Strong retained | Variant clarification |
| BM-05 | SME relationship-data credit bridge | NatWest C&I wider than SME but causally aligned | Keep as commercial relationship-data variant, not replacement definition | NatWest Dominant retained | Strong retained | Variant clarification |
| BM-06 | Deposit acquisition and pricing mechanism | NatWest local BM-06 wrongly labelled digital-primary relationship | Exclude NatWest local BM-06 from BM-06 validation unless deposit/pricing evidence is used | Lloyds Dominant; NatWest Dominant; Nationwide Dominant; Monzo Significant | Strong retained | Mapping correction, no confidence change |
| BM-07 | Structural hedge and NII investment-capacity mechanism | Nationwide mutual economics blended member value with hedge/NII | Keep hedge/NII distinct; mutual value goes to compound NW-COMP-001 | Nationwide Significant retained | Strong retained | Semantic boundary clarified |
| BM-10 | Capital and liquidity constraint mechanism | Nationwide “trust/customer retention” incorrectly mapped to BM-10 in local material | Correct: trust component maps BM-02; capital/liquidity/member surplus allocation maps BM-10 variant | Nationwide Dominant retained for capital/liquidity, not trust | Strong retained | Mapping correction |
| BM-15 | Legacy complexity cost-to-income mechanism | Virgin Money integration and Monzo cloud-native were treated as same row pressure | Preserve canonical legacy complexity; create integration variant and cloud-native contrast | Lloyds Dominant; NatWest Dominant; Nationwide Significant; Monzo Weak | Strong retained | Variant clarification |
| BM-16 | Core/cloud migration risk-return mechanism | Some platform/payment modernisation material is compound with BM-13/BM-19 | Keep canonical row and place Form3/AWS/Stand-in evidence as variants/compound | No change | Strong retained | Semantic clarification |
| BM-17 | Data-quality to AI-decision utility mechanism | AI value evidence risked being mixed with workforce augmentation and commercial demand | Keep BM-17 to data/model/decision utility; workforce tooling remains BM-20 | NatWest Significant, not Dominant for BM-17 alone | Supported retained | Applicability adjustment |
| BM-20 | AI workforce augmentation and retained-capability mechanism | Some BM-17 evidence belonged here | Move colleague, coder, contact-centre and self-service AI evidence here | NatWest Dominant; Lloyds Significant; Monzo Significant; Nationwide Moderate | Supported retained | Applicability clarification |
| BM-21 | Outsourcing efficiency versus control mechanism | Opportunity/BPO candidate material risked overstating validation | Exclude commercial opportunity material from validation | All remain weak/not observable | Candidate retained | Commercial leakage quarantined |
| BM-22 | Participant convergence mechanism | Product adjacency/fintech acquisition sometimes over-mapped | Keep as supported pattern-level mechanism, not economic proof | No material change | Supported retained | No promotion |

## 5. Corrected Four-Bank Mechanism Differential Matrix v2.1

| BM ID | Canonical name | Lloyds | NatWest | Nationwide / VM | Monzo | v2.1 confidence | Variant required | Key correction |
|---|---|---:|---:|---:|---:|---|---|---|
| BM-01 | Current-account primacy flywheel | Dominant | Dominant | Significant | Significant | Strong | Yes | Challenger primary conversion separated from incumbent primacy |
| BM-02 | Customer trust and conduct feedback loop | Significant | Significant | Dominant | Significant | Strong | Yes | Nationwide trust/customer retention remapped here from local BM-10 |
| BM-03 | Digital engagement to multi-banking mechanism | Moderate | Moderate | Moderate | Dominant | Supported | Yes | Demoted because local Monzo BM-03 and NatWest BM-06 were not canonical |
| BM-04 | Assisted-access substitution mechanism | Moderate | Moderate | Dominant | Weak | Strong | Yes | Branch cost and branch trust variants retained |
| BM-05 | SME relationship-data credit bridge | Moderate | Dominant | Moderate | Moderate | Strong | Yes | NatWest commercial variant retained |
| BM-06 | Deposit acquisition and pricing mechanism | Dominant | Dominant | Dominant | Significant | Strong | Yes | NatWest local BM-06 excluded unless deposit/pricing evidence |
| BM-07 | Structural hedge and NII investment-capacity mechanism | Dominant | Dominant | Significant | Weak | Strong | Yes | Mutual value separated from hedge/NII |
| BM-08 | Mortgage economics cyclicality mechanism | Dominant | Significant | Dominant | Weak | Strong | Yes | No change |
| BM-09 | Credit decisioning and impairment loop | Significant | Significant | Significant | Significant | Strong | Light variant | No change |
| BM-10 | Capital and liquidity constraint mechanism | Dominant | Dominant | Dominant | Significant | Strong | Yes | Nationwide trust component remapped to BM-02 |
| BM-11 | APP fraud reimbursement and friction mechanism | Not Observable | Significant | Significant | Dominant | Strong | Yes | No change |
| BM-12 | AML/KYC/KYB friction-control mechanism | Moderate | Moderate | Significant | Dominant | Strong | Yes | No change |
| BM-13 | Operational-resilience service-continuity mechanism | Significant | Significant | Significant | Significant | Strong | Yes | No change |
| BM-14 | Consumer Duty outcome-evidence mechanism | Significant | Significant | Dominant | Moderate | Strong | Yes | No change |
| BM-15 | Legacy complexity cost-to-income mechanism | Dominant | Dominant | Significant | Weak | Strong | Yes | Integration variant separated from pure legacy mechanism |
| BM-16 | Core/cloud migration risk-return mechanism | Significant | Significant | Significant | Significant | Strong | Yes | Platform/payment compounds separated |
| BM-17 | Data-quality to AI-decision utility mechanism | Significant | Significant | Moderate | Significant | Supported | Yes | NatWest reduced from Dominant for BM-17 alone |
| BM-18 | Open-banking and embedded-distribution mechanism | Moderate | Moderate | Weak | Moderate | Supported | Yes | No change |
| BM-19 | Hyperscaler critical-dependency mechanism | Significant | Significant | Significant | Dominant | Strong | Yes | No change |
| BM-20 | AI workforce augmentation and retained-capability mechanism | Significant | Dominant | Moderate | Significant | Supported | Yes | NatWest AI adoption belongs here, not BM-17 alone |
| BM-21 | Outsourcing efficiency versus control mechanism | Not Observable | Weak | Weak | Weak | Candidate | Yes | Commercial opportunity evidence quarantined |
| BM-22 | Participant convergence mechanism | Moderate | Moderate | Moderate | Significant | Supported | Yes | No promotion |

## 6. Commercial Leakage Quarantine

The following material is excluded from mechanism confidence and applicability scoring:
- Opportunity Candidate Universe.
- Rob-relevant commercial portfolio classifications.
- Commercial Intervention Boundary.
- Commercial demand.
- Commercial accessibility.
- Provider or supplier positioning.
- Opportunity readiness.
- Watch / Shape / Partner / Pursue actions.

This affects especially the Nationwide file, where commercial opportunity sections follow the mechanism analysis and include Rob-relevant portfolios and opportunity candidates. Those opportunity sections may contain useful Deferred Opportunity Discovery Inputs, but they do not validate mechanisms or alter BM confidence.

### Deferred Opportunity Discovery Inputs

| Source | Material preserved | Why preserved | Why excluded from mechanism validation |
|---|---|---|---|
| Nationwide | Virgin Money integration, payments/core modernisation, financial-crime controls, AWS/contact-centre/branch operating model | Useful later for Opportunity Discovery | Portfolio/Tier/action labels are commercial, not mechanism evidence |
| NatWest | AWS/Accenture, OpenAI, application decommissioning, Bankline/API | Useful later for Opportunity Discovery | Supplier/route/action content does not validate mechanism confidence |
| Monzo | Cloud-native resilience, AI self-service, AML/APP remediation | Useful later for Opportunity Discovery | Commercial potential not equal to validated causal mechanism |
| Lloyds | Curve acquisition, AI/cloud, Halifax migration | Useful later for Opportunity Discovery | Acquisition/technology activity does not prove business-model outcome |

## 7. Participant-Type Variant Register

| Variant ID | Parent BM | Participant type | Causal difference | Evidence | Applicability boundary | Confidence | Falsification |
|---|---|---|---|---|---|---|---|
| V-INC-01 | BM-01 | Scale incumbents | Embedded current accounts create deposits, data and product adjacency | Lloyds/NatWest deposit/current-account evidence | Lloyds, NatWest-like banks | Strong | Salary/direct-debit flows materially migrate away |
| V-CHAL-01 | BM-01/BM-03 | Digital challengers | App engagement converts some active users into primary-bank users | Monzo 49% MAU primary evidence | Monzo-like challengers | Supported | Primary MAU share fails to translate into salary/bill/deposit depth |
| V-MUT-01 | BM-02/BM-06/BM-10 | Mutuals | Member value and savings relationship reinforce trust and funding | Nationwide mutual/member value evidence | Building societies/mutuals | Strong | Member value fails to affect retention or funding |
| V-COM-01 | BM-05 | Commercial incumbents | RM + sector expertise + payments/API/FX/lending deepen relationship | NatWest C&I / Bankline / API evidence | Commercial banks | Strong | Digital/API usage does not deepen deposits, fees or retention |
| V-BR-01 | BM-04 | Shareholder incumbents | Branch network is primarily cost/access trade-off | Lloyds/NatWest | Branch incumbents | Supported | Branches become proven acquisition/trust growth asset |
| V-BR-02 | BM-04 | Mutuals | Branch promise becomes trust, acquisition and inclusion asset | Nationwide branch promise evidence | Mutual/community models | Strong | Branch usage/product-opening evidence weakens materially |
| V-LEG-01 | BM-15 | Incumbents | Legacy complexity creates cost, resilience and speed constraint | Lloyds/NatWest app decommissioning/simplification | Legacy banks | Strong | Decommissioning has no cost/risk/service effect |
| V-INT-01 | BM-15/BM-16 | Acquisition integration | Integration creates duplicated platforms, migration risk and eventual simplification | Nationwide/Virgin Money integration | Acquirers/integrators | Supported | Integration completes without platform/customer harm or cost complexity |
| V-CLOUD-01 | BM-16/BM-19 | Cloud-native challengers | Low legacy drag but high cloud concentration | Monzo AWS/Kubernetes/Stand-in | Cloud-native banks | Supported | Cloud concentration is immaterial to resilience or exit |
| V-AI-01 | BM-20 | Scale incumbents | AI augments colleagues, coders, RMs, contact centres | NatWest/Lloyds AI adoption | Large workforce banks | Supported | AI shows no durable time/quality/cost benefit |
| V-AI-02 | BM-20 | Digital challengers | AI self-service protects cost-to-serve but raises quality/control risk | Monzo AI self-service evidence | App-first challengers | Supported | Automation degrades trust or requires equivalent human workload |
| V-CAP-01 | BM-10 | Listed banks | Capital generation allocated between growth, buffers, dividends/buybacks and transformation | Lloyds/NatWest | Listed banks | Strong | Capital allocation ceases to constrain strategy |
| V-CAP-02 | BM-10 | Mutuals | Capital strength competes with member value and transformation spend | Nationwide | Mutuals | Strong | Mutual surplus behaves like shareholder distribution |
| V-CTP-01 | BM-19 | All participant types | Cloud/AI providers become regulated dependency layer | All four evidence cloud/platform dependency | Banking-wide | Strong | Banks materially reduce critical third-party concentration |

## 8. Enterprise-Specific Mechanism Candidate Register

| Candidate ID | Enterprise | Candidate mechanism | Why it is not an existing BM | Evidence | Confidence | Next validation |
|---|---|---|---|---|---|---|
| LBG-CAND-001 | Lloyds | Brand simplification mechanism | Blends trust, access, digital migration and operating simplification; no single BM covers it | Halifax-to-Lloyds migration evidence | Medium | Attrition, complaints, app migration and branch outcomes |
| LBG-CAND-002 | Lloyds | Fintech acquisition for customer-moment control | Related to BM-18/BM-22 but not equivalent | Curve acquisition | Medium-low | Integration economics and customer adoption |
| NTW-CAND-001 | NatWest | Public-trust recovery mechanism | NatWest-specific crisis/government-ownership history | Full private ownership / trust narrative | Medium | Longitudinal trust and complaints outcomes |
| NW-CAND-001 | Nationwide | Virgin Money integration as reinvention catalyst | Acquisition/integration mechanism spans multiple BMs | Legal transfer, integration cost, migration risk | Medium-high | Customer migration and platform convergence outcomes |
| MONZO-CAND-001 | Monzo | Notification and control loop | Related to digital engagement/trust but not yet causal | App/engagement/control claims | Medium | Engagement-to-retention and trust evidence |
| MONZO-CAND-002 | Monzo | Subscription-to-relationship-depth | Product-specific relationship mechanism, not canonical | Subscription customer evidence | Medium | Retention, product depth and unit economics |
| MONZO-CAND-003 | Monzo | Community and brand advocacy | Related to trust/digital but not causal enough | NPS/word-of-mouth evidence | Medium | Conversion, retention and complaint resilience |

## 9. Compound Mechanism Register

| Compound ID | Component mechanisms | Enterprise / participant type | Causal sequence | Evidence | Confidence |
|---|---|---|---|---|---|
| LBG-COMP-001 | BM-01 + BM-06 + BM-07 + BM-10 + BM-15 | Lloyds / scale incumbent | Current-account/deposits -> hedge/NII -> capital -> investment -> simplification | Lloyds deepening | High |
| NTW-COMP-001 | BM-15 + BM-16 + BM-20 | NatWest / commercial incumbent | Simplification -> savings -> investment capacity -> AI/cloud/platform | NatWest simplification evidence | Medium-high |
| NTW-COMP-002 | BM-05 + BM-17 + BM-20 | NatWest / commercial relationship bank | Relationship -> data/API/AI -> RM/customer productivity -> deeper relationship | NatWest C&I, Bankline, AI evidence | Medium-high |
| NW-COMP-001 | BM-02 + BM-06 + BM-10 | Nationwide / mutual | Profit/capital -> member value -> trust/retention -> deposits | Nationwide mutual value evidence | High |
| NW-COMP-002 | BM-06 + BM-08 + BM-10 | Nationwide / mutual mortgage-savings | Member savings -> mortgage capacity -> retention/funding | Nationwide mortgage/savings evidence | High |
| NW-COMP-003 | BM-15 + BM-16 + BM-10 + BM-02 | Nationwide / integration | Virgin acquisition -> duplicated platforms -> integration risk -> member value | Nationwide integration evidence | Medium-high |
| NW-COMP-004 | BM-16 + BM-13 + BM-19 | Nationwide / platform trust | Payments/cloud modernisation -> resilience -> supplier risk under trust constraint | Nationwide Form3/AWS evidence | Medium |
| MONZO-COMP-001 | BM-03 + BM-06 + BM-09 + BM-10 | Monzo / challenger | Engagement/current-account use -> deposits/revenue/lending -> capital/control maturity | Monzo local BM-03 evidence | Medium-high |
| MONZO-COMP-002 | BM-16 + BM-19 + BM-13 | Monzo / cloud-native | AWS/microservices -> agility + Stand-in resilience -> concentration risk | Monzo platform evidence | Medium-high |
| MONZO-COMP-003 | BM-12 + BM-11 + BM-10 | Monzo / rapid-growth challenger | Rapid growth -> AML/APP/control load -> capital and trust constraints | FCA/PSR control evidence in Twin | High |
| MONZO-COMP-004 | BM-01 + BM-03 + BM-06 + BM-09 + BM-10 | Monzo / challenger bank maturity | Digital primacy -> deposits -> lending/product depth -> regulated maturity | Monzo Twin | Medium-high |

## 10. Change Report

| Mechanism ID | v2 conclusion | v2.1 conclusion | Changed? | Reason | Materiality |
|---|---|---|---|---|---|
| BM-01 | Strong; variants | Strong; variants clarified | Yes | Challenger conversion separated from incumbent primacy | Variant change |
| BM-02 | Strong | Strong; Nationwide trust remapped here | Yes | Local Nationwide BM-10 trust usage corrected | Applicability change |
| BM-03 | Strong | Supported | Yes | Monzo local BM-03 and NatWest local BM-06 were not canonical BM-03 | Confidence change |
| BM-04 | Strong | Strong; branch variants clarified | Yes | Cost burden vs trust differentiator made explicit | Variant change |
| BM-05 | Strong | Strong | No material | NatWest C&I variant retained | Editorial |
| BM-06 | Strong | Strong; NatWest local BM-06 excluded from BM-06 validation | Yes | Canonical BM-06 is deposit acquisition/pricing | Applicability lineage change |
| BM-07 | Strong | Strong | Yes | Nationwide mutual value separated from hedge/NII | Editorial / variant clarification |
| BM-08 | Strong | Strong | No | No identifier conflict | Editorial |
| BM-09 | Strong | Strong | No | No identifier conflict | Editorial |
| BM-10 | Strong | Strong; Nationwide trust component remapped to BM-02 | Yes | Canonical BM-10 is capital/liquidity | Applicability change |
| BM-11 | Strong | Strong | No | No identifier conflict | Editorial |
| BM-12 | Strong | Strong | No | No identifier conflict | Editorial |
| BM-13 | Strong | Strong | No | No identifier conflict | Editorial |
| BM-14 | Strong | Strong | No | No identifier conflict | Editorial |
| BM-15 | Strong | Strong; integration variant separated | Yes | Virgin Money integration is compound, not pure legacy | Variant change |
| BM-16 | Strong | Strong; platform/payment compounds separated | Yes | BM-16 should not absorb BM-13/BM-19 | Variant change |
| BM-17 | Supported | Supported; NatWest applicability lowered for BM-17 alone | Yes | Some NatWest AI evidence belongs to BM-20 | Applicability change |
| BM-18 | Supported | Supported | No material | Keep provisional | Editorial |
| BM-19 | Strong | Strong | No | Cloud dependency correctly mapped | Editorial |
| BM-20 | Supported | Supported; NatWest remains Dominant here | Yes | Colleague/coder/RM/contact-centre AI belongs here | Applicability change |
| BM-21 | Candidate | Candidate; commercial leakage quarantined | Yes | Opportunity/BPO material excluded from validation | Promotion/reversal prevented |
| BM-22 | Supported | Supported | No material | Convergence remains causal-light | Editorial |

## 11. Corrected Promotion and Retirement Table

| Mechanism ID | v2 state | v2.1 state | Decision |
|---|---|---|---|
| BM-01 | Strong | Strong | Retain; split variants |
| BM-02 | Strong | Strong | Retain; add Nationwide trust mapping |
| BM-03 | Strong | Supported | Reverse promotion pending more challenger evidence |
| BM-04 | Strong | Strong | Retain; explicit variants |
| BM-05 | Strong | Strong | Retain |
| BM-06 | Strong | Strong | Retain; correct NatWest local mapping |
| BM-07 | Strong | Strong | Retain |
| BM-08 | Strong | Strong | Retain |
| BM-09 | Strong | Strong | Retain |
| BM-10 | Strong | Strong | Retain; correct Nationwide trust mapping |
| BM-11 | Strong | Strong | Retain |
| BM-12 | Strong | Strong | Retain |
| BM-13 | Strong | Strong | Retain |
| BM-14 | Strong | Strong | Retain |
| BM-15 | Strong | Strong | Retain; split integration variant |
| BM-16 | Strong | Strong | Retain; split cloud-native / migration variants |
| BM-17 | Supported | Supported | Hold |
| BM-18 | Supported | Supported | Hold |
| BM-19 | Strong | Strong | Retain |
| BM-20 | Supported | Supported | Hold; correct AI evidence allocation |
| BM-21 | Candidate | Candidate | Hold; exclude commercial leakage |
| BM-22 | Supported | Supported | Hold |

## 12. Assurance Findings

| Acceptance criterion | v2.1 result |
|---|---|
| Every local mechanism has inspectable mapping | Met |
| No local identifier treated automatically as canonical | Met |
| Rejected mappings visible | Met: Monzo local BM-03 to canonical BM-03 rejected; NatWest local BM-06 to canonical BM-06 rejected; Nationwide trust/local BM-10 to canonical BM-10 rejected |
| Canonical BM meanings preserved | Met |
| Enterprise applicability remains separate from mechanism confidence | Met |
| Variants remain separate from canonical mechanisms | Met |
| New candidates not silently assigned BM identifiers | Met |
| Commercial-analysis sections do not influence validation | Met |
| Material changes to v2 reported | Met |

The Four-Bank Mechanism Differential Matrix v2.1 correction is complete. Canonical Banking Mechanism identifiers have been reconciled against all enterprise-local labels, semantic conflicts and variants are explicit, and the revised confidence and applicability judgements retain inspectable lineage to the original Banking Mechanism Catalogue.
