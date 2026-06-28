# Science Governance

## Purpose of Commercial Cognitive Science

Commercial cognitive science is the disciplined study of how commercial actors perceive, decide, coordinate, trust, buy, sell, adopt, retain, and create value within market systems. In CIOS, it provides the scientific foundation for commercial intelligence, ensuring that recommendations, models, workflows, and standards are grounded in explicit reasoning and reviewable evidence.

The purpose of the Commercial Science Registry is to:

- Preserve institutional knowledge about commercial behaviour and commercial intelligence.
- Separate validated knowledge from assumptions, early research, and operating convenience.
- Provide traceability from scientific artefacts to engineering standards and applications.
- Support safe adoption of models, automation, heuristics, and decision-support mechanisms.
- Create a durable review process for amending or retiring scientific claims.

## Artefact Types

| Artefact Type | Definition | Governance Role | Typical Output |
| --- | --- | --- | --- |
| Principle | A normative rule or design commitment derived from scientific reasoning and evidence. | Guides decisions, reviews, and standards. | Design principle, review criterion, operating doctrine. |
| Law | A durable relationship repeatedly observed across commercial contexts. | Constrains modelling, interpretation, and system design. | Boundary condition, expected relationship, invariant. |
| Model | A structured representation of entities, relationships, behaviours, decisions, or causal mechanisms. | Enables analysis, prediction, simulation, explanation, or implementation. | Conceptual model, computational model, data model, causal model. |
| Heuristic | A practical rule for decisions under uncertainty, time pressure, or incomplete evidence. | Provides bounded operational guidance where full modelling is not feasible. | Decision rule, escalation rule, review shortcut. |
| Hypothesis | A falsifiable proposition that has not yet accumulated sufficient evidence for adoption. | Directs research and experimentation. | Testable claim, expected effect, research question. |
| Experiment | A structured validation activity designed to test an artefact or proposition. | Produces evidence for promotion, amendment, rejection, or deprecation. | Protocol, trial, observational study, retrospective analysis. |
| Evidence | Reviewed information that supports, challenges, or qualifies an artefact. | Provides the factual basis for governance decisions. | Measurement, analysis, literature review, audit finding, operational result. |

## Lifecycle

| Status | Meaning | Entry Criteria | Exit Criteria |
| --- | --- | --- | --- |
| Proposed | The artefact has been identified and recorded for consideration. | Clear description, owner, intended use, and initial rationale. | Accepted into research, rejected, or deferred by governance review. |
| Research | The artefact is being investigated through literature, analysis, stakeholder review, or data exploration. | Research question, scope, and evidence plan. | Sufficient basis for experiment, candidate drafting, or rejection. |
| Experimental | The artefact is under active validation through defined tests or structured operational observation. | Approved experiment or validation plan with measurable criteria. | Results reviewed and converted into evidence records. |
| Candidate | The artefact has promising evidence and is suitable for limited adoption or formal review. | Evidence summary, limitations, risk assessment, and proposed applications. | Approved as Validated, returned for more work, or rejected. |
| Validated | The artefact has sufficient evidence for governed use in defined contexts. | Evidence meets quality requirements and review confirms scope. | Adopted as Standard, amended, or deprecated after monitoring. |
| Standard | The artefact is approved as a durable governance reference for CIOS. | Approval authority accepts evidence, traceability, operational value, and controls. | Periodic review confirms continued validity or initiates amendment/deprecation. |
| Deprecated | The artefact is retired from active governance use. | Evidence of invalidity, supersession, unacceptable risk, or lack of use. | Archived with rationale and replacement guidance where applicable. |

## Review Process

1. **Submission**: The proposer records the artefact in the appropriate registry with identifier, name, version, owner, confidence, status, related artefacts, related engineering standards, applications, validation status, and last review date.
2. **Scope Review**: The Science Governance Board verifies that the artefact is correctly typed, non-duplicative, bounded, and relevant to CIOS.
3. **Evidence Review**: Reviewers assess evidence quality, provenance, reproducibility, limitations, and applicability to the proposed use.
4. **Engineering Impact Review**: If the artefact affects CIOS architecture, data structures, automation, interfaces, or operational controls, reviewers identify related engineering standards and required implementation controls.
5. **Decision Review**: The approval authority records one of the following decisions: accept, accept with constraints, request amendment, request further evidence, reject, or deprecate.
6. **Publication**: Approved registry changes are versioned, dated, and linked to supporting evidence, experiments, and engineering standards.
7. **Periodic Review**: Standard artefacts are reviewed at least annually, and higher-risk artefacts are reviewed when new evidence, operational incidents, or major product changes occur.

## Evidence Requirements

Evidence must be proportionate to risk, operational impact, and claimed confidence. At minimum, evidence records must include:

- Source or provenance.
- Collection or analysis method.
- Date range and context.
- Quality assessment.
- Known limitations and threats to validity.
- Artefacts supported or challenged.
- Implications for engineering standards or applications.

Higher-confidence artefacts require stronger evidence. Promotion to Validated or Standard normally requires more than one evidence source, evidence from a relevant operational context, and review of contrary findings. Artefacts that influence automation, prioritisation, user recommendations, or customer-facing decisions require explicit evaluation for bias, reliability, explainability, and failure modes.

## Amendment Process

Amendments are required when definitions, assumptions, scope, evidence, applications, owners, or related engineering standards change. The amendment process is:

1. Create a proposed version increment and describe the reason for change.
2. Identify affected artefacts, applications, and engineering standards.
3. Review new evidence and compare it against the current approved version.
4. Record the governance decision and update the registry entry.
5. Preserve the prior version history where the artefact materially influenced decisions.
6. Communicate changes to engineering, research, operations, and product owners affected by the artefact.

Versioning should use semantic intent: major versions for meaning or scope changes, minor versions for new evidence or applications, and patch versions for clerical corrections that do not alter governance meaning.

## Approval Authority

The Science Governance Board is the approval authority for lifecycle promotion, deprecation, and material amendments. The board is accountable for scientific integrity, evidence sufficiency, traceability, and alignment with CIOS engineering standards.

Engineering owners must approve implementation changes caused by scientific artefacts. Product or operational owners must approve changes that affect user workflows, customer-facing behaviour, or business process commitments. Where an artefact creates material risk, the board may require additional review before adoption.

## Review Cadence

| Artefact Status | Minimum Review Cadence | Triggered Review Events |
| --- | --- | --- |
| Proposed | Within 90 days of submission. | Duplicate discovery, scope challenge, sponsor withdrawal. |
| Research | At research milestone or every 180 days. | New literature, data access change, revised research question. |
| Experimental | At experiment checkpoint and completion. | Metric anomaly, ethical concern, implementation issue. |
| Candidate | Before adoption and within 180 days if not promoted. | Conflicting evidence, operational incident, expanded use case. |
| Validated | At least annually. | New evidence, material system change, performance drift. |
| Standard | At least annually. | Major engineering change, governance incident, contrary evidence. |
| Deprecated | When referenced by active work. | Replacement artefact, audit request, historical review. |
