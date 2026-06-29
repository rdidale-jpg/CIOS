# Enterprise Domain Initial Concept Catalogue

## Document Metadata

| Field | Value |
|---|---|
| Related Standard | CIOS-CBOK-STD-001A |
| Version | 0.1.0 |
| Status | Candidate Catalogue |
| Owner | CIOS Knowledge Governance |
| Last Reviewed | 2026-06-29 |

## Purpose

This catalogue records candidate Enterprise Domain concepts for future CBOK specification. Entries are not complete concept definitions.

## Enterprise Structure

| Candidate Identifier | Name | Object Family | Short Description | Proposed Maturity | Notes |
|---|---|---|---|---|---|
| cios.ontology.enterprise.enterprise | Enterprise | Enterprise Structure | Coordinated commercial entity or system pursuing strategic outcomes. | Candidate | Top-level structural concept. |
| cios.ontology.enterprise.organisation | Organisation | Enterprise Structure | Social and operational grouping arranged to achieve objectives. | Candidate | May be legal or non-legal. |
| cios.ontology.enterprise.legal_entity | Legal Entity | Enterprise Structure | Organisation recognised as having legal standing. | Candidate | Requires jurisdiction attributes later. |
| cios.ontology.enterprise.business_unit | Business Unit | Enterprise Structure | Managed organisational unit accountable for business outcomes. | Candidate | May own capabilities and budgets. |
| cios.ontology.enterprise.division | Division | Enterprise Structure | Major structural grouping within an enterprise. | Candidate | Often contains business units or functions. |
| cios.ontology.enterprise.function | Function | Enterprise Structure | Organisational grouping responsible for a specialised type of work. | Candidate | Examples include finance or operations. |
| cios.ontology.enterprise.department | Department | Enterprise Structure | Operational subdivision within a function or unit. | Candidate | Boundary varies by organisation. |
| cios.ontology.enterprise.team | Team | Enterprise Structure | Group of people collaborating on defined work. | Candidate | May be persistent or temporary. |

## Enterprise Governance

| Candidate Identifier | Name | Object Family | Short Description | Proposed Maturity | Notes |
|---|---|---|---|---|---|
| cios.ontology.enterprise.board | Board | Enterprise Governance | Senior governing body with oversight authority. | Candidate | Authority model to be defined. |
| cios.ontology.enterprise.executive_committee | Executive Committee | Enterprise Governance | Executive decision body coordinating enterprise leadership. | Candidate | May govern portfolios or strategy. |
| cios.ontology.enterprise.steering_committee | Steering Committee | Enterprise Governance | Governance body guiding a programme, initiative or domain. | Candidate | Commonly sponsors decisions. |
| cios.ontology.enterprise.sponsor | Sponsor | Enterprise Governance | Accountable party providing mandate, support or resources. | Candidate | Can be person or role. |
| cios.ontology.enterprise.decision_authority | Decision Authority | Enterprise Governance | Role or body authorised to make specified decisions. | Candidate | Needs scope and delegation attributes. |
| cios.ontology.enterprise.policy | Policy | Enterprise Governance | Governed rule or intent constraining enterprise action. | Candidate | Links to constraints and evidence. |
| cios.ontology.enterprise.governance_model | Governance Model | Enterprise Governance | Defined arrangement of roles, forums, authorities and controls. | Candidate | May govern domains or portfolios. |

## Enterprise Capability

| Candidate Identifier | Name | Object Family | Short Description | Proposed Maturity | Notes |
|---|---|---|---|---|---|
| cios.ontology.enterprise.capability | Capability | Enterprise Capability | Ability of an enterprise to achieve an outcome. | Candidate | Existing SDK concept may require alignment. |
| cios.ontology.enterprise.process | Process | Enterprise Capability | Repeatable sequence of activities producing an output. | Candidate | May realise a capability. |
| cios.ontology.enterprise.service | Service | Enterprise Capability | Defined offering or operational function delivered to consumers. | Candidate | Internal or external. |
| cios.ontology.enterprise.product | Product | Enterprise Capability | Packaged value proposition provided to users or customers. | Candidate | May be commercial or internal. |
| cios.ontology.enterprise.technology | Technology | Enterprise Capability | Tool, method or technical component enabling work. | Candidate | Distinguish from platform. |
| cios.ontology.enterprise.platform | Platform | Enterprise Capability | Shared foundation enabling products, services or capabilities. | Candidate | May be technical or business platform. |
| cios.ontology.enterprise.data_asset | Data Asset | Enterprise Capability | Governed data resource with enterprise value. | Candidate | Requires ownership and quality attributes. |
| cios.ontology.enterprise.supplier | Supplier | Enterprise Capability | External party providing goods, services or capabilities. | Candidate | Existing SDK concept may require alignment. |

## Enterprise Resources

| Candidate Identifier | Name | Object Family | Short Description | Proposed Maturity | Notes |
|---|---|---|---|---|---|
| cios.ontology.enterprise.people | People | Enterprise Resources | Human participants available to the enterprise. | Candidate | May decompose into person, role or workforce later. |
| cios.ontology.enterprise.skill | Skill | Enterprise Resources | Human capability or competency relevant to enterprise work. | Candidate | Supports resource and capability analysis. |
| cios.ontology.enterprise.budget | Budget | Enterprise Resources | Allocated financial resource for a purpose or period. | Candidate | Links to funding and governance. |
| cios.ontology.enterprise.asset | Asset | Enterprise Resources | Resource controlled by the enterprise with expected value. | Candidate | Broad parent concept. |
| cios.ontology.enterprise.facility | Facility | Enterprise Resources | Physical location or site supporting enterprise activity. | Candidate | May contain assets and teams. |
| cios.ontology.enterprise.intellectual_property | Intellectual Property | Enterprise Resources | Protected or proprietary intangible asset. | Candidate | Legal evidence may be required. |
| cios.ontology.enterprise.contract | Contract | Enterprise Resources | Agreement creating obligations, rights or commitments. | Candidate | Existing SDK concept may require alignment. |

## Enterprise Strategy

| Candidate Identifier | Name | Object Family | Short Description | Proposed Maturity | Notes |
|---|---|---|---|---|---|
| cios.ontology.enterprise.vision | Vision | Enterprise Strategy | Desired future state or aspiration. | Candidate | Strategic intent concept. |
| cios.ontology.enterprise.mission | Mission | Enterprise Strategy | Enduring purpose and reason for enterprise action. | Candidate | Often constrains objectives. |
| cios.ontology.enterprise.objective | Objective | Enterprise Strategy | Specific intended result. | Candidate | Should link to outcomes and measures. |
| cios.ontology.enterprise.outcome | Outcome | Enterprise Strategy | Realised or intended change in state or value. | Candidate | May be measured by KPIs. |
| cios.ontology.enterprise.initiative | Initiative | Enterprise Strategy | Coordinated effort to produce strategic change. | Candidate | Parent for programme or project may vary. |
| cios.ontology.enterprise.programme | Programme | Enterprise Strategy | Coordinated set of related initiatives or projects. | Candidate | UK spelling retained per user request. |
| cios.ontology.enterprise.project | Project | Enterprise Strategy | Temporary endeavour delivering defined outputs or outcomes. | Candidate | Needs lifecycle states. |
| cios.ontology.enterprise.portfolio | Portfolio | Enterprise Strategy | Managed collection of investments, programmes, projects or assets. | Candidate | Links to governance and performance. |

## Enterprise Risk

| Candidate Identifier | Name | Object Family | Short Description | Proposed Maturity | Notes |
|---|---|---|---|---|---|
| cios.ontology.enterprise.risk | Risk | Enterprise Risk | Uncertain event or condition affecting objectives. | Candidate | Requires probability and impact model later. |
| cios.ontology.enterprise.issue | Issue | Enterprise Risk | Current condition requiring attention or resolution. | Candidate | Distinguish from risk. |
| cios.ontology.enterprise.dependency | Dependency | Enterprise Risk | Reliance of one artefact or activity on another. | Candidate | Relationship and object forms may both be needed. |
| cios.ontology.enterprise.assumption | Assumption | Enterprise Risk | Statement accepted as true for planning or reasoning. | Candidate | Must link to evidence and review. |
| cios.ontology.enterprise.constraint | Constraint | Enterprise Risk | Limitation restricting options or behaviour. | Candidate | Also appears as modelling rule; context needed. |
| cios.ontology.enterprise.opportunity | Opportunity | Enterprise Risk | Favourable uncertain condition or potential value path. | Candidate | Existing SDK concept may require alignment. |

## Enterprise Performance

| Candidate Identifier | Name | Object Family | Short Description | Proposed Maturity | Notes |
|---|---|---|---|---|---|
| cios.ontology.enterprise.kpi | KPI | Enterprise Performance | Key performance indicator used to assess progress or performance. | Candidate | Acronym retained as canonical candidate. |
| cios.ontology.enterprise.benefit | Benefit | Enterprise Performance | Positive value or advantage expected or realised. | Candidate | Links to outcomes and initiatives. |
| cios.ontology.enterprise.cost | Cost | Enterprise Performance | Resource consumption or financial burden. | Candidate | May link to budget and investment. |
| cios.ontology.enterprise.value | Value | Enterprise Performance | Assessed worth or utility to stakeholders. | Candidate | Requires valuation context. |
| cios.ontology.enterprise.investment | Investment | Enterprise Performance | Committed resource expected to produce future value. | Candidate | Links to portfolio and return. |
| cios.ontology.enterprise.return | Return | Enterprise Performance | Value or gain produced by investment or action. | Candidate | May be financial or non-financial. |
| cios.ontology.enterprise.performance_measure | Performance Measure | Enterprise Performance | Metric used to evaluate activity, output or outcome. | Candidate | KPI may be specialised measure. |
