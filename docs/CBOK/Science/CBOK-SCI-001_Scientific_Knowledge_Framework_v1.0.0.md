# CBOK-SCI-001 Scientific Knowledge Framework

## Document Metadata

| Field | Value |
|---|---|
| Document ID | CIOS-CBOK-SCI-001 |
| Title | Scientific Knowledge Framework |
| Version | 1.0.0 |
| Status | Approved |
| Owner | CIOS Knowledge Governance |
| Last Reviewed | 2026-06-29 |
| Scope | Classification, evaluation, validation, promotion, traceability and engineering consumption of CBOK scientific knowledge |

## Executive Summary

CBOK-SCI-001 governs how knowledge is created, evaluated, validated, promoted and consumed by engineering within the Commercial Body of Knowledge (CBOK). It establishes a common taxonomy, evidence hierarchy, confidence model, lifecycle, promotion path, review criteria and traceability chain so commercial knowledge can move from early observation to approved engineering use without losing provenance or overstating certainty.

## Purpose

The purpose of this standard is to ensure that CBOK scientific artefacts are explicit, reviewable, evidence-based and traceable. It shall be used whenever a CBOK artefact classifies knowledge, evaluates evidence, assigns confidence, promotes research into standards or maps validated knowledge into engineering, SDK, platform or application work.

## Scope

This standard applies to CBOK observations, claims, definitions, principles, patterns, hypotheses, models, laws, frameworks, standards, reference models and recommendations. It covers knowledge governance from initial recording through archival. It does not define runtime behaviour, SDK implementation, product features or application logic.

## Normative References

- [CBOK Authoring System](../README.md)
- [CBOK Authoring Guide](../AUTHORING_GUIDE.md)
- [CBOK Identifier Standard](../IDENTIFIER_STANDARD.md)
- [CBOK Document Lifecycle](../DOCUMENT_LIFECYCLE.md)
- [CBOK Scientific Confidence](../SCIENTIFIC_CONFIDENCE.md)
- [CBOK Operational Confidence](../OPERATIONAL_CONFIDENCE.md)
- [CBOK Traceability Standard](../TRACEABILITY_STANDARD.md)
- [CBOK Review Process](../REVIEW_PROCESS.md)
- [Science Governance](../../Science/SCIENCE_GOVERNANCE.md)
- [CIOS Traceability Model](../../TRACEABILITY.md)

## Definitions

| Term | Definition |
|---|---|
| Knowledge artefact | A controlled CBOK record that captures an observation, claim, hypothesis, model, law, standard or related knowledge unit. |
| Evidence | Reviewed information used to support, challenge or qualify a knowledge artefact. |
| Scientific confidence | The assessed strength of scientific support for a claim or artefact. |
| Operational confidence | The assessed readiness of an artefact for governed operational or engineering use. |
| Promotion | A governed lifecycle transition that increases the authority or downstream usability of an artefact. |
| Traceability | The maintained relationship from evidence through knowledge artefacts to engineering and operational evidence. |

## Knowledge Taxonomy

CBOK scientific knowledge shall be classified using the formal classes in [Knowledge Classification](KNOWLEDGE_CLASSIFICATION.md). Authors must not treat all knowledge statements as equivalent. At minimum, each material knowledge statement should be labelled as an observation, claim, definition, principle, pattern, hypothesis, model, law, framework, standard, reference model or recommendation.

Knowledge classification determines evidence expectations, review criteria, permissible confidence levels and downstream engineering use. A recommendation, for example, may be useful operationally while remaining less scientifically durable than a law.

## Evidence Hierarchy

CBOK uses evidence levels E0 through E6 as defined in [Evidence Hierarchy](EVIDENCE_HIERARCHY.md). Evidence shall be proportionate to claim strength, risk and downstream impact. E0 and E1 evidence may support exploration but must not be the sole basis for an approved standard that affects engineering behaviour. Claims that affect automation, user recommendations, prioritisation or customer-facing outcomes should normally require E4 or higher evidence, or an explicit governance exception.

## Scientific Confidence

Scientific confidence shall be assigned using the CBOK Scientific Confidence Standard. Authors shall document evidence type, scope, limitations, counterevidence and rationale for the selected confidence level. Scientific confidence must not be inferred from operational convenience or implementation success alone.

## Operational Confidence

Operational confidence shall be assigned separately from scientific confidence using the CBOK Operational Confidence Standard. A knowledge artefact may be scientifically supported but not operationally ready, or operationally useful in a bounded context while requiring further validation. Engineering consumers must use operational confidence to determine pilot, controlled-use or production readiness.

## Knowledge Lifecycle

Knowledge shall mature through the lifecycle defined in [Knowledge Lifecycle](KNOWLEDGE_LIFECYCLE.md): Idea, Observation, Claim, Working Paper, Literature Review, Hypothesis, Experiment, Validation Report, Candidate Artefact, Approved Artefact, Standard, Superseded and Archived. Each transition shall have entry criteria, exit criteria, an owner and traceability to evidence or review decisions.

## Knowledge Promotion Rules

Promotion shall follow the rules in [Knowledge Promotion](KNOWLEDGE_PROMOTION.md). The preferred promotion path is:

```text
Observation
→ Claim
→ Working Paper
→ Literature Review
→ Hypothesis
→ Experiment
→ Validation Report
→ Commercial Law / Model / Reference Model
→ Standard
→ Engineering Standard
→ SDK / Platform / Application
```

Promotion must not erase uncertainty. Earlier artefacts should remain linked to later artefacts so reviewers can reconstruct why knowledge was accepted, limited, amended or rejected.

## Review Criteria

Reviews shall use the [Knowledge Review Checklist](KNOWLEDGE_REVIEW_CHECKLIST.md). Reviewers should evaluate terminology consistency, evidence quality, confidence rating, falsifiability, contradictory evidence, ethical considerations, engineering impact, traceability, duplication, ownership and next review date.

## Traceability Requirements

Each controlled CBOK scientific artefact shall identify:

- Upstream evidence, observations, literature reviews, experiments or validation reports.
- Internal claims, assumptions, definitions and decisions.
- Scientific and operational confidence ratings.
- Known limitations, contradictory evidence and unresolved questions.
- Downstream standards, engineering specifications, SDK packages, platform components, applications or operational practices affected.
- Review owner, review date and next review trigger.

Traceability records should preserve stable identifiers from the CBOK Identifier Standard.

## Conformance Requirements

A document conforms to CBOK-SCI-001 when it:

1. Uses a valid CBOK identifier and document metadata.
2. Classifies all material knowledge statements.
3. Assigns evidence levels and confidence ratings where claims are made.
4. States lifecycle status and promotion rationale.
5. Records upstream and downstream traceability.
6. Includes review history and next review expectations.
7. Avoids unsupported certainty and separates scientific conclusions from operational decisions.

## Governance Requirements

CIOS Knowledge Governance owns this standard. The Science Governance Board shall apply it when reviewing scientific artefacts and shall require amendments when artefacts lack evidence, traceability, confidence rationale or engineering impact analysis. Material changes to this standard require versioning, review history updates and Master Index updates.

## Engineering Integration

Engineering may consume CBOK knowledge only according to its approved lifecycle state, confidence ratings and documented constraints. Approved standards may inform engineering standards, SDK design, platform architecture and application behaviour. Candidate or experimental artefacts may inform prototypes or pilots only when downstream documentation clearly marks them as non-baseline and identifies monitoring requirements.

Engineering standards should map each implemented scientific requirement back to the supporting CBOK artefact and should return operational evidence, incidents or performance findings to the relevant scientific artefact for review.

## Future Extensions

Future CBOK scientific standards may define detailed evidence record schemas, experiment protocols, validation report templates, meta-analysis criteria, ethical review methods, contradiction handling and machine-readable traceability records.

## Version History

| Version | Date | Change | Author |
|---|---|---|---|
| 1.0.0 | 2026-06-29 | Initial approved framework for CBOK scientific knowledge governance. | CIOS Knowledge Governance |

## Review History

| Date | Reviewer | Role | Decision | Notes |
|---|---|---|---|---|
| 2026-06-29 | CIOS Knowledge Governance | Governance Reviewer | Approved | Establishes Newton Sprint 1 scientific knowledge framework. |

## Appendices

### Appendix A: Supporting Standards

- [Knowledge Classification](KNOWLEDGE_CLASSIFICATION.md)
- [Evidence Hierarchy](EVIDENCE_HIERARCHY.md)
- [Knowledge Lifecycle](KNOWLEDGE_LIFECYCLE.md)
- [Knowledge Promotion](KNOWLEDGE_PROMOTION.md)
- [Knowledge Review Checklist](KNOWLEDGE_REVIEW_CHECKLIST.md)
- [Scientific Glossary](SCIENTIFIC_GLOSSARY.md)

### Appendix B: Minimum Engineering Consumption Gate

Before engineering consumes a CBOK artefact, the artefact should have an approved owner, documented constraints, traceability to evidence, scientific confidence, operational confidence and an explicit downstream mapping.
