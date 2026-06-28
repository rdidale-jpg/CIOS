# CBOK Identifier Standard

## Document Metadata

| Field | Value |
|---|---|
| Document ID | CIOS-CBOK-STD-ID |
| Title | CBOK Identifier Standard |
| Version | 0.1.0 |
| Status | Draft |
| Owner | CIOS Knowledge Governance |
| Last Reviewed | 2026-06-28 |

## Purpose

This standard defines stable identifiers for CBOK documents, claims, evidence records, review decisions and traceability links.

## Document Identifier Format

CBOK documents use:

```text
CIOS-CBOK-<TYPE>-<NUMBER>
```

Recommended type codes are:

| Type | Use |
|---|---|
| CON | Constitution or foundational doctrine |
| SCI | Scientific framework |
| STD | Normative standard |
| REF | Reference model |
| LAW | Commercial law |
| INF | Influence model |
| PAT | Enterprise pattern |
| WP | Working paper |
| LIT | Literature review |
| EXP | Experiment |
| VAL | Validation report |
| ARC | Architecture document |

## Internal Identifier Format

Internal claims and records use:

```text
<document-id>#<record-type>-<number>
```

Examples include `CIOS-CBOK-SCI-001#CLAIM-001`, `CIOS-CBOK-EXP-001#EVIDENCE-003` and `CIOS-CBOK-VAL-001#FINDING-002`.

## Identifier Rules

- Identifiers are permanent once published.
- Retired identifiers must not be reused.
- Draft identifiers may be reserved but must not collide with controlled records.
- Renamed documents retain their original identifier unless scope changes so substantially that a new document is required.
