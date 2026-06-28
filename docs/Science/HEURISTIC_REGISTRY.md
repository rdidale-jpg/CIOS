# Heuristic Registry

This registry records practical decision rules used when complete modelling is impractical, unnecessary, or too slow for the commercial context.

| Identifier | Name | Version | Status | Confidence | Owner | Related Artefacts | Related Engineering Standards | Applications | Validation Status | Last Review |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HEU-COM-001 | Preserve Segment Context During Interpretation | 0.1.0 | Proposed | Medium | Science Governance Board | Principles: PRI-COM-002; Models: MOD-COM-002 | CIOS_ENG_002 | Segmentation, messaging, recommendation review | Requires reviewer sampling | 2026-06-28 |
| HEU-COM-002 | Prefer Reversible Commercial Interventions First | 0.1.0 | Proposed | Medium | Science Governance Board | Experiments: EXP-COM-002; Evidence: EVD-COM-004 | CIOS_ENG_004 | Experiment design, rollout planning, risk reduction | Requires intervention log review | 2026-06-28 |
| HEU-COM-003 | Escalate Low-Confidence High-Impact Decisions | 0.1.0 | Proposed | High | Science Governance Board | Principles: PRI-COM-001; Evidence: EVD-COM-001 | CIOS_ENG_001 | Human review, governance gates, operational assurance | Requires adoption audit | 2026-06-28 |

## Entry Requirements

A heuristic entry must define its trigger conditions, expected benefit, failure modes, and override criteria. Heuristics must be reviewed after operational use to detect drift, bias, or misuse.
