FLORA — Lloyds Enterprise Intelligence Coverage & Root-Cause Audit

1. Context and owner decision

PR #733 has been merged and the owner has reviewed the updated Lloyds screens.

Technical progress is recognised, particularly evidence discipline, information architecture and navigation. However, final visual and commercial acceptance has been withheld.

The screens do not sufficiently align with Flora’s Beautiful Simplicity design principle and expose potentially significant gaps in underlying enterprise intelligence.

The owner has approved a change in sprint sequencing: research coverage and root-cause investigation before further substantive UI development.

2. Baseline

Approved technical baseline:

3a4c7e0f6ad81af7ef32ed477a1a584ac2efae87

Verify the current repository and deployment state independently. Identify any subsequent changes before commencing.

Preserve all existing security, Source, Financial, contract, Pipeline and historical compatibility controls.

3. Sprint objective

Establish precisely what Flora knows about Lloyds Banking Group, what it presents, what it fails to connect, what it is authorised to present and what remains genuinely unknown.

This is a diagnostic sprint, not another UI implementation sprint.

Flora’s fundamental purpose remains identifying, qualifying and developing real commercial sales opportunities.

4. Comprehensive research inventory

Inspect existing research, historical records, canonical enterprise data, source records, structured facts, relationships, intelligence outputs and presentation mappings.

Assess coverage across:

* Group structure, subsidiaries, legal entities and brands.
* Business divisions, products and customer segments.
* Market share and competitive positioning.
* Group and divisional financial performance.
* Revenue, costs, profitability, capital and management targets.
* Executive leadership, responsibilities and decision-makers.
* Business processes and operating models.
* Business capabilities and organisational ownership.
* Applications, platforms and data architecture.
* Technology infrastructure and cloud services.
* Strategic suppliers and technology partners.
* Contracts, commercial relationships, values and renewal dates.
* Transformation programmes and investment priorities.
* AI adoption, use cases and measurable benefits.
* Regulatory obligations and enterprise-specific exposure.
* Acquisitions, integration activity and strategic implications.
* Commercial intelligence, investigation themes and opportunities.

For each domain, identify the existing evidence, its date, granularity, provenance, authority and relationship to the enterprise.

Do not equate the number of research documents with intelligence completeness.

5. Root-cause classification

Classify each material information gap using one or more of the following:

A. Research not undertaken.

B. Research undertaken but relevant facts not extracted.

C. Facts extracted but not connected to the correct enterprise, division, capability, programme or supplier.

D. Facts exist but are restricted by legitimate source or publication controls.

E. Information genuinely unavailable from accessible sources.

F. Information exists and is eligible but is not surfaced by the presentation layer.

G. Information exists but is stale, contradictory or insufficiently verified.

H. Root cause remains undetermined.

Provide concrete evidence for each classification.

Distinguish research availability, evidence quality, publication eligibility and presentation coverage. Do not conflate them.

6. Screen-by-screen diagnostic

Inspect the current Lloyds experience across Landscape, Inside and Forces, including:

* Group overview.
* Group economics.
* Retail Banking.
* Commercial Banking.
* Insurance, Pensions & Investments.
* Operating model.
* Lending and credit journey.
* Capabilities.
* Strategy and change.
* Markets and earnings.
* Regulation and resilience.
* Competition and technology.
* Associated drill-downs.

For each screen, establish:

1. What commercial question should this screen answer?
2. What information does it currently present?
3. What relevant intelligence already exists elsewhere in Flora?
4. What is missing, and why?
5. What could be recovered without additional external research?
6. What targeted research would materially improve it?
7. How could the intelligence support a salesperson’s next action?

Investigate text wrapping, overlapping icons, clipped values and excessive card sizes separately. Determine whether these defects affect live desktop, iPad portrait, iPad landscape, PDF output or multiple environments.

Do not implement fixes during this sprint.

7. Research recovery and enrichment plan

Prioritise recovering existing intelligence before commissioning additional research.

Produce a prioritised backlog separating:

* Existing facts that can be surfaced.
* Existing evidence requiring extraction.
* Missing relationships and entity mappings.
* Evidence requiring verification or refreshing.
* Genuinely new research.
* Source authority dependencies.
* Information unlikely to be publicly obtainable.

For proposed new research, identify candidate sources, expected commercial value, likely accessibility and dependencies.

Do not execute new paid research or model/API experiments.

8. Commercial intelligence assessment

Evaluate Flora’s ability to connect:

Management ambition → business pressure → transformation priority → affected capability → applications and infrastructure → suppliers → decision-makers → commercial investigation → qualified opportunity.

Use Lloyds examples, including where supported:

* Core-platform renewal and application retirement.
* Cloud migration.
* AI industrialisation.
* Payments transformation and Curve integration.
* Branch transformation.
* Regulatory reporting and operational resilience.
* Efficiency and cost reduction.

Clearly distinguish established facts, management ambitions, original analysis, commercial hypotheses and qualified opportunities.

Do not create artificial opportunities or promote unqualified intelligence into Pipeline.

9. Beautiful Simplicity assessment

Document the current design shortcomings and their root causes.

Our design principle is:

Make complex information easy to understand, not simplistic.

Future designs should prioritise:

* Differentiated and memorable visual storytelling.
* Enterprise-specific intelligence.
* High information value relative to screen space.
* Meaningful diagrams, charts, timelines and relationships.
* Minimal repetitive text.
* Plain commercial language.
* Progressive disclosure of evidence and methodology.
* Material qualifications retained alongside relevant claims.
* Responsive desktop and iPad experiences.
* Preservation of established Flora artwork and visual identity.

Assess how the current presentation architecture supports or inhibits these principles.

Do not undertake the visual redesign yet.

10. Required deliverables

Produce a comprehensive, owner-readable audit pack containing:

A. Executive assessment

Summarise the most important findings, root causes and commercial implications.

B. Research coverage matrix

For every research domain, show:

* Existing intelligence.
* Evidence quality and freshness.
* Publication eligibility.
* Presentation coverage.
* Material gaps.
* Root-cause classification.
* Commercial importance.
* Recommended action.

C. Research-to-screen traceability matrix

Map relevant existing intelligence to the screens where it is presented or should be presented.

D. Recoverable intelligence inventory

Identify material intelligence already held by Flora that is not currently being used effectively.

E. Prioritised research backlog

Separate recovery, extraction, mapping, verification and genuinely new research.

F. Commercial intelligence examples

Demonstrate how existing and proposed intelligence could improve commercial investigation, without manufacturing opportunities.

G. Visual diagnostic

Provide annotated desktop and iPad screenshots demonstrating representative design and rendering problems.

H. Proposed sprint roadmap

Recommend the sequencing, dependencies and acceptance criteria for:

1. Research recovery and enrichment.
2. Beautiful Simplicity visual prototypes.
3. Runtime implementation.
4. Commercial intelligence integration.
5. Validation against easyJet and subsequent enterprises.

11. Measurement

Provide transparent, evidence-backed measures of:

* Research coverage by domain.
* Evidence quality and freshness.
* Extraction completeness.
* Relationship and mapping completeness.
* Eligible intelligence surfaced in the UI.
* Commercial intelligence readiness.

Define denominators and scoring methods.

Where reliable percentages cannot be established, report the limitation rather than inventing precision.

12. Constraints and authority

This is a read-only diagnostic with respect to application runtime, canonical data and production.

Documentation and diagnostic artefacts may be created in an isolated branch and submitted in a draft PR.

* No runtime implementation.
* No canonical research mutations.
* No production deployment.
* No merge.
* No new paid expenditure.
* No authority or permissions changes.
* No activation of restricted §2 output.
* No implementation of deferred §5 PDF links.
* No changes to Pipeline qualification.
* No protected source reproduction outside existing authority.
* No destruction or replacement of historical research.

Preserve existing controls and prior work.

13. Completion and handoff

Submit a draft PR containing the audit documentation and reproducible diagnostic evidence.

Report:

* Exact commit SHA.
* File inventory.
* Principal findings.
* Most significant root causes.
* Research coverage assessment.
* Highest-value recoverable intelligence.
* Recommended next sprint.
* Validation results.
* Incremental expenditure.
* Outstanding blockers and owner decisions.

Stop at owner review.

The success of this sprint will be measured by how clearly it explains the gap between Flora’s existing knowledge and its current commercial usefulness, not by the number of files changed.