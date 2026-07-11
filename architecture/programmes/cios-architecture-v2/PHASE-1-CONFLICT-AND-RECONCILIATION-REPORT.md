# Phase 1 Conflict and Reconciliation Report

**Status:** Phase 1 Report  
**Date:** 2026-07-11  
**Owner:** Rob / CIOS

## Summary

The Architecture v2.0 foundation documents introduce Knowledge Pack, Knowledge Asset, Knowledge Exchange Architecture, Knowledge Repository, Twin Presentation Model, Industry Twin, Market Participant Twin, Opportunity Twin, Relational Twin, Cross-Twin Intelligence and Knowledge Supply Chain terminology. No immediate core-document rewrite is made in Phase 1 except index, map and ADR reconciliation.

| Source document | Section | Tension | Authoritative decision | Proposed Phase 2 amendment | Immediate reconciliation required |
| --- | --- | --- | --- | --- | --- |
| CIOS Reference Architecture v1.0 | Architecture overview | Current reference architecture predates Knowledge Pack exchange language. | ADR-016 establishes Knowledge Packs as standard exchange mechanism once accepted. | Add Architecture v2.0 exchange layer and authority chain. | No |
| FP-003 | Flora Intelligence Architecture | Flora runtime reasoning remains account-level and may appear broader than presentation-model handling. | ADR-014 as amended permits account-level runtime reasoning but does not require it when accepted Twin Presentation Model exists. | Add explicit Presentation Model rendering boundary. | ADR amendment added now |
| CIOS-AI.md | AI working rules | Does not define specialist GPT authorship of Twin Presentation Models. | ADR-016 and Twin Presentation Model Specification define labelled GPT-authored interpretation. | Add authoring guidance and labelling rules. | No |
| EI-001 | Enterprise Model | Enterprise Model canonical memory may be confused with accepted Knowledge Pack contents. | ADR-016 states package acceptance is not canonical fact acceptance. | Add Knowledge Pack import boundary. | No |
| EI-002 | Enterprise Knowledge Graph | Graph relationships may be proposed by Knowledge Assets before canonical acceptance. | EI-013 requires semantic labels and promotion through target owner. | Add candidate relationship handling. | No |
| EI-003 | Enterprise Behaviour Model | Behaviour interpretations may be exchanged before validation. | EI-013 labels interpretation and confidence. | Add exchanged behaviour hypothesis state. | No |
| EI-012 | Enterprise Observation Model | Observations are atomic intelligence; Knowledge Assets are exchange units. | EI-012 remains owner of Observation lifecycle; EI-013 owns exchanged Knowledge Asset semantics. | Cross-reference Knowledge Asset to Observation conversion. | No |
| FP-009 | Hypothesis Validation Standard | Hypotheses and recommendations in packs need lineage. | ADR-005 and FP-009 continue to govern inspectable lineage and validation. | Add Knowledge Pack hypothesis payload examples. | No |
| Chief Architect Handbook | Stewardship practice | Handbook predates Architecture v2.0 authority chain. | Supersession note defines the chain for Phase 1. | Add governance workflow for accepting ADR to specs. | No |
| Design Doctrine | Evidence-first doctrine | AI-authored presentation models could be mistaken for evidence. | ADR-004, ADR-005, ADR-014 and ADR-016 require labels, lineage and no silent canonical upgrade. | Add explicit presentation-as-interpretation doctrine. | No |
| Architecture Principles | Principles | Knowledge Supply Chain terminology is absent. | FP-011 owns Knowledge Exchange Architecture. | Add principle for exchange without canonical promotion. | No |
| Accepted ADRs | ADR-014 | Runtime reasoning could be read as always required for Executive Intelligence Briefs. | Amendment clarifies it is permitted but not required when accepted Twin Presentation Model is supplied. | Consider superseding ADR if runtime scope changes materially in Phase 2. | Yes, amendment added |
