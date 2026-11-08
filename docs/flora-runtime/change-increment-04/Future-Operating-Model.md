# Future continuous intelligence operating model — proposal

This is a proposal, not an accepted ADR or an implemented orchestration plan.
Increment 04 implements bounded, explicitly invoked, read-only interpretation.
The following distinctions prevent existing code from being mistaken for a live
continuous intelligence system.

| Future activity | Implemented building blocks | Not implemented by Increment 04 / next review boundary |
| --- | --- | --- |
| Continuous monitoring | Configured sources, explicit live collection and diagnostics; canonical Evidence lifecycle | No always-on monitoring, event bus, subscription registry or generic change-event ledger. Establish source coverage and assurance needs before authorizing a trigger. |
| Scheduled research | `live/worker.py`, `collect.py`, source profiles, run/progress state | Existing explicit execution is not a new generic recurring scheduler. Any future scheduling must reuse an authorized execution boundary; no scheduling was added. |
| Event-driven reassessment | Observatory snapshot comparison; new Evidence-derived interpretation and explicit model/pressure target IDs | No queue dispatch, automatic model mutation, bulk reassessment or new trigger authority. A future coordinator could call the bounded assessment with authorized target scope, then request evidence or existing owner assessment. |
| Evidence-demand-driven research | New transient evidence demands; existing acquisition plans/source registry and live collection | No autonomous translation of demands into source expansion or research execution. A human or bounded worker could investigate a demand, return candidate Evidence and use normal acceptance. |
| Industry Twin refresh | Existing package registry, Industry Delta adapter, candidate validation/review/promotion and read projections | IT-001 remains Review. No new generic Industry Twin canonical lifecycle, cross-enterprise inference owner or automatic promotion. Scope any future maintenance decision explicitly. |
| Enterprise Twin refresh | Accepted Observation application, Enterprise Model history, governed import compensation | External context does not create enterprise facts. Future research must supply accepted enterprise-specific Observations, timing, uncertainty and consequence through the existing owner. |
| Material Pressure reassessment | ADR-026 qualification, existing model-owned lifecycle, new dependency targets and read-only qualification previews | Preview is not an update. Actual changes must pass the existing owner gates. No new pressure authority or automatic external-to-pressure write was added. |
| Commercial hypothesis reassessment | Existing EI runtime/provider/validator; separate commercial/hypothesis paths and audit | Not invoked here. An enterprise consequence does not establish funded demand, budget, contract value, buying intent or procurement. Future commercial reassessment needs its own bounded question, evidence and approval posture. |
| Navigator view updates | Existing Canvas, Enterprise Memory and Evidence-package diagnostics; accepted imported presentation paths | No Navigator generation, four-slide implementation or new presentation store. Any later view should consume current owner-backed read models and preserve qualification labels. |
| Human review and feedback | Existing import approvals, explicit Unknown/Contradiction owners, Canvas feedback and runtime audit paths | Evidence demands are learning needs, not automatic tasks or accepted facts. Review should resolve support, scope and conflicting claims before owner reassessment. No new feedback store or approval system was introduced. |

A future bounded execution sequence could be: collect candidate external Evidence;
accept it under its existing owner; resolve authorized candidate enterprises;
interpret only governed enterprise support; retain unresolved demands; investigate
those demands through bounded research; accept new enterprise Observations; call
existing model/pressure maintenance; separately reassess commercial hypotheses;
refresh existing views. Each arrow is a governance boundary, not implied automatic
write permission. Persistent orchestration/trigger policy and material commercial
actions require separate authorization and any architectural decisions they need.

The current interpreter consumes explicitly governed semantic annotations. A future
specialist worker may propose these annotations, but generated interpretations
remain candidates until accepted under ADR-014/024 and the relevant source owner.
This increment supplies deterministic scope, lineage and assurance controls; it
does not encode industry economics or replace bounded semantic reasoning with
sector-specific rules.
