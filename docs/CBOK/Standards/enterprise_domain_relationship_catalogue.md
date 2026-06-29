# Enterprise Domain Relationship Catalogue

## Document Metadata

| Field | Value |
|---|---|
| Related Standard | CIOS-CBOK-STD-001A |
| Version | 0.1.0 |
| Status | Candidate Catalogue |
| Owner | CIOS Knowledge Governance |
| Last Reviewed | 2026-06-29 |

## Purpose

This catalogue records initial governed relationship identifiers for the Enterprise Domain. Relationships are candidates until promoted through CBOK review.

| Relationship Identifier | Name | Definition | Allowed Source Types | Allowed Target Types | Multiplicity | Example | Notes |
|---|---|---|---|---|---|---|---|
| owns | Owns | Indicates accountability or control over an artefact, resource or outcome. | Enterprise, Organisation, Business Unit, Function, Sponsor | Capability, Product, Data Asset, Asset, Outcome | Many-to-many | Business Unit owns Product. | Ownership semantics require context. |
| contains | Contains | Indicates structural inclusion of one entity inside another. | Enterprise, Organisation, Division, Function, Department, Portfolio, Programme | Business Unit, Division, Function, Department, Team, Project, Asset | One-to-many | Division contains Department. | Prefer for whole-part structure. |
| belongs_to | Belongs To | Indicates membership or assignment to a larger structure. | Business Unit, Department, Team, Project, Asset | Enterprise, Organisation, Division, Function, Portfolio | Many-to-one | Team belongs_to Department. | Inverse of contains where appropriate. |
| employs | Employs | Indicates an organisation engages people for work. | Enterprise, Organisation, Legal Entity, Business Unit | People | One-to-many | Legal Entity employs People. | Detailed employment model deferred. |
| funds | Funds | Indicates provision of budget or investment to an artefact. | Budget, Investment, Sponsor, Portfolio | Initiative, Programme, Project, Capability, Product | Many-to-many | Portfolio funds Programme. | Requires amount and period attributes later. |
| governs | Governs | Indicates authority or control over decisions, policies or artefacts. | Board, Executive Committee, Steering Committee, Governance Model, Policy | Enterprise, Portfolio, Programme, Project, Capability, Risk | Many-to-many | Steering Committee governs Programme. | Must preserve authority source. |
| sponsors | Sponsors | Indicates mandate, support or accountable sponsorship. | Sponsor, Executive Committee, Business Unit | Initiative, Programme, Project, Product, Capability | Many-to-many | Sponsor sponsors Project. | May include sponsorship role attributes. |
| depends_on | Depends On | Indicates reliance on another artefact, condition or resource. | Capability, Process, Service, Product, Project, Initiative | Capability, Process, Supplier, Data Asset, Technology, Assumption | Many-to-many | Project depends_on Supplier. | Direction points from dependent to dependency. |
| enables | Enables | Indicates that one artefact makes another possible or more effective. | Capability, Technology, Platform, Data Asset, Skill | Process, Service, Product, Outcome, Capability | Many-to-many | Platform enables Service. | Avoid using for vague association. |
| constrains | Constrains | Indicates a limit or rule restricting another artefact. | Policy, Constraint, Contract, Risk | Process, Project, Capability, Decision Authority, Product | Many-to-many | Policy constrains Process. | Constraint evidence should be recorded. |
| measures | Measures | Indicates that a metric evaluates an artefact or outcome. | KPI, Performance Measure | Objective, Outcome, Process, Service, Product, Benefit | Many-to-many | KPI measures Outcome. | Measurement method deferred. |
| delivers | Delivers | Indicates production or provision of an output, service, product or outcome. | Team, Project, Programme, Process, Capability, Supplier | Product, Service, Outcome, Benefit | Many-to-many | Project delivers Outcome. | Distinguish from enables. |
| transforms | Transforms | Indicates material change from one state, input or structure to another. | Process, Initiative, Programme, Project, Capability | Organisation, Process, Data Asset, Outcome, Capability | Many-to-many | Initiative transforms Capability. | State transition modelling deferred. |
| participates_in | Participates In | Indicates involvement in a forum, process, initiative or activity. | People, Team, Sponsor, Supplier, Business Unit | Steering Committee, Process, Project, Programme, Initiative | Many-to-many | Team participates_in Initiative. | Role details may be attributes or separate concepts. |
| competes_with | Competes With | Indicates market or resource competition between parties or offerings. | Enterprise, Organisation, Product, Service | Enterprise, Organisation, Product, Service | Many-to-many | Product competes_with Product. | Symmetric relationship. |
| partners_with | Partners With | Indicates cooperative relationship between parties. | Enterprise, Organisation, Supplier, Business Unit | Enterprise, Organisation, Supplier, Business Unit | Many-to-many | Organisation partners_with Supplier. | Symmetric relationship. |
| supplies | Supplies | Indicates provision of goods, services, resources or capabilities. | Supplier, Business Unit, Service, Platform | Enterprise, Organisation, Process, Product, Capability | Many-to-many | Supplier supplies Capability. | May link to contract. |
| serves | Serves | Indicates that an artefact supports or provides value to a consumer or objective. | Service, Product, Capability, Team, Function | Customer, Business Unit, Objective, Outcome, Organisation | Many-to-many | Service serves Business Unit. | Customer concept may be defined in another domain. |
