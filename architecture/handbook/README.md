# CIOS Chief Architect Handbook

## Stewarding the Enterprise Intelligence Platform

This directory contains the canonical handbook governing Chief Architect judgement and working practice for CIOS.

## Canonical source

`CIOS-Chief-Architect-Handbook.md`

The Markdown manuscript is the editable source of truth.

PDF, DOCX, HTML and other published forms should be generated views and should not be edited independently.

## Purpose

The handbook teaches human and AI Chief Architects how to:

- steward the CIOS mission;
- preserve Enterprise Intelligence doctrine;
- design living Commercial Digital Twins;
- challenge assumptions;
- maintain evidence and reasoning lineage;
- make architecture and commercial decisions;
- turn doctrine into bounded implementation;
- review, mentor and learn.

## Authority

The handbook governs judgement and working practice.

Detailed architecture remains governed by:

1. explicit owner direction;
2. Accepted Architecture Decision Records;
3. the CIOS Reference Architecture and owning architecture papers;
4. the CIOS Design Doctrine and Architecture Principles.

Where a conflict is found, record and resolve it rather than allowing silent divergence.

## Proposed repository location

```text
architecture/
└── handbook/
    ├── README.md
    └── CIOS-Chief-Architect-Handbook.md
```

## Maintenance rules

- Use CIOS Glossary terminology.
- Preserve the distinction between Evidence, Observation, Signal, Hypothesis, Commercial Thesis and Recommendation.
- Keep reports and published formats as views over the canonical Markdown.
- Use ADRs for enduring architecture decisions.
- Update cross-references when concepts or source-of-truth documents change.
- Review the handbook after material doctrine, architecture or operating-method changes.
- Record significant revisions in the handbook’s Document History.

## Suggested review workflow

1. Create a documentation branch.
2. Add the handbook and this README.
3. Update the Document Map and Reference Architecture navigation.
4. Add the handbook to the `CIOS-AI.md` reading order.
5. Review terminology, links and authority.
6. Merge through pull request.
7. Upload the merged Markdown as GPT Knowledge.
8. Run configuration acceptance tests.

## Suggested commit

```text
docs(architecture): add CIOS Chief Architect Handbook
```

## Suggested pull request title

```text
Add the CIOS Chief Architect Handbook
```
