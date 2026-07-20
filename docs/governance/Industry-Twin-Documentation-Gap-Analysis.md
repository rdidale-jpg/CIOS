# Industry Twin Documentation Gap Analysis

**Status:** Audit artefact  
**Owner:** Rob / CIOS  
**Last updated:** 2026-07-20

| Gap ID | Missing capability/guidance | Why it matters | Role affected | Risk | Closest owner | Recommended remediation | Existing or new? | Priority | Dependencies | Acceptance criterion |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P0-G01 | Accepted Researcher-visible Industry Twin operating route | Researcher cannot know where to start/stop or hand over | Researcher | Public Sector starts from chat memory | RP-001 + Research Guide | Register a revised Researcher guidance appendix/guide | Existing | P0 | Registry | Researcher pack includes Industry Twin operating checklist. |
| P0-G02 | Minimum viable Industry Twin completeness/readiness gate | Cannot decide enough research | Researcher/Architect | Premature or endless research | ADR-009/EKPP/IT-001 | Add research-ready and architecture-ready criteria | Existing | P0 | IT-001 | Gate covers enterprise count, source coverage, Unknowns, evidence ledger. |
| P0-G03 | Supplier, contract and procurement timing fields | Public Sector requires commercial timing | Researcher | Weak opportunity intelligence | Research Guide | Add mandatory fields and source families | Existing | P0 | ADR-010 | Checklist requires programme/supplier/contract/procurement trigger/buyer/timing. |
| P0-G04 | Banking lessons checklist | Known v1 lessons may repeat | Researcher | Repeat weak historical/supplier/valuation coverage | Research Guide/EKPP | Add lessons as non-doctrinal checklist | Existing | P0 | Banking closure | Each lesson has pass/fail/not-applicable entry. |
| P0-G05 | FP-010 identifier collision | Authority confusion | All | Wrong FP-010 used as owner | Authority Registry/FP files | Rename or explicitly reconcile Review FP-010 | Existing | P0 | ADR-016 | Only one FP-010 remains or collision caveat is explicit everywhere. |
| P1-G06 | Generic Industry Twin acceptance/closure template | Banking closure is not reusable enough | Architect/Codex | Handover and closure inconsistent | EKPP/ADR-009 | Add acceptance/closure section | Existing | P1 | P0-G02 | Template includes readiness, limitations, backlog, tests. |
| P1-G07 | Pressure-to-procurement graph semantics | Commercial chain not fully inspectable | Researcher/Architect | Opportunities lack timing lineage | EI-002/Research Guide | Add examples/edge guidance | Existing | P1 | P0-G03 | Chain fields map to KG relationships. |
| P1-G08 | Commercial valuation comparables guidance | Value estimates weak/inconsistent | Commercial reviewer | Over/understated value | FP-008 | Add comparables and confidence treatment | Existing | P1 | ADR-005 | Valuation states evidence basis and limitations. |
| P1-G09 | Human commercial validation checklist | Human input may be unlabeled or late | Owner/Reviewer | Unsupported conviction | ADR-004/Research Guide | Add validation section | Existing | P1 | P0 guide | Human-supplied knowledge is labelled and separated. |
| P2-G10 | Freshness/decay cadence by source class | Refresh hard to operate | Researcher | Stale Twin | IT-LC/EKPP | Expand refresh cadence | Existing | P2 | P0/P1 | Source classes have decay and review triggers. |
| P3-G11 | Document Map discoverability gaps | Readers miss audit-relevant docs | All | Hard to find docs | Document Map | Add governance audit entries | Existing | P3 | This audit | New audit docs listed. |

## New document decision

No new document is required now. If the Authority Registry cannot responsibly include a revised Research Agent Guide, a narrowly bounded **Researcher Handbook** may be justified later; ownership would be operational Researcher procedure only, not architecture doctrine.
