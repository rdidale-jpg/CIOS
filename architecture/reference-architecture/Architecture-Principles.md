# CIOS Architecture Principles

**Identifier:** PR-001
**Version:** 1.0
**Document Type:** Architecture Principles
**Authority Classification:** Canonical architecture principles
**Status:** Draft
**Owner:** Rob / CIOS
**Last updated:** 2026-07-11

## First Principles of CIOS

1. CIOS detects meaningful enterprise change.
2. Evidence is proof, not intelligence.
3. Observations are the atomic unit of Enterprise Intelligence.
4. Enterprise Models are durable memory.
5. Every material claim must be traceable.
6. Unknowns and contradictions are first-class objects.
7. Commercial reasoning must distinguish fact, inference, hypothesis and recommendation.
8. Recommendations should maximise learning before selling.
9. Human expertise calibrates the model but must be labelled.
10. The platform should become more valuable as enterprise memory deepens.

## Detailed operating principles

- **Evidence before judgement.** CIOS should establish what is known before interpreting what it means.
- **Observations before signals.** Evidence should become reusable Observations before being promoted into Strategic Signals where possible.
- **Signals before hypotheses.** Hypotheses should be grounded in observed Signals rather than unsupported intuition.
- **Hypotheses before recommendations.** Recommendations should be justified by validated or explicitly uncertain hypotheses.
- **Unknowns are valuable.** Unknowns show where the model needs collection, learning or human calibration.
- **Contradictions must be preserved.** Contradictory claims should remain visible until resolved by better evidence or explicit judgement.
- **Human insight must be labelled.** Human-supplied knowledge can be valuable but must not masquerade as evidence-backed fact.
- **Reports are views, not memory.** Briefings, dashboards and PDFs should render model state; they should not become the canonical memory.
- **The Enterprise Model is memory.** Durable enterprise knowledge belongs in the Enterprise Model and Commercial Digital Twin.
- **The Knowledge Graph is structure.** Relationships, dependencies, influence and temporal edges belong in the graph.
- **The Observation is the atom.** Observations are the smallest reusable units of Enterprise Intelligence.
- **The Conversation is the commercial action interface.** Commercial action happens through explainable conversation, account planning and executive engagement.
- **Every capability must improve detection, explanation, prediction or action.** Features that do not improve one of these should be challenged.

## Compliance implications

Significant runtime changes should explain which principles they implement, which they defer and whether they improve traceability, evidence lineage and commercial judgement.


## Architecture v2.0 principles

- **Separate intelligence creation from governance.** Creation processes may identify, infer, draft or package intelligence, but governance decides truth status, acceptance, release and promotion.
- **Knowledge Packs are the standard exchange mechanism.** CIOS exchanges governed portable knowledge through Knowledge Packs rather than ad hoc files, untracked summaries or presentation-only artefacts.
- **Exchange is not canonical promotion.** Knowledge Pack acceptance validates package handling; canonical acceptance remains with the owning Enterprise Twin, Industry Twin, Market Participant Twin, Opportunity Twin, Relational Twin or EI model process.
- **Presentation Models are governed interpretations.** Twin Presentation Models render, navigate and explain governed knowledge for a defined audience and purpose; they are not themselves Evidence, Observations or durable model memory.
- **Accepted interpretation is not canonical fact.** A rendered or accepted interpretation may be approved for use while its claims remain labelled as interpretation unless the owning model process separately promotes them.
- **Industry maintenance is event-driven and risk-based.** Industry Twins should refresh when monitoring events, impact thresholds, assurance tier or market risk justify action, not only on fixed calendar cadence.
- **Cross-Twin intelligence is a primary Flora differentiator.** Flora should compound value by comparing Enterprise, Industry, Market Participant, Opportunity and Relational Twins while preserving their authority boundaries.
- **Cross-Twin impacts are proposed, not silently applied.** Intelligence discovered in one Twin may create Cross-Twin Impact Proposals for another Twin, but it must not overwrite target Twin state without acceptance by the target owner.
- **Truth status and lineage must survive exchange.** Fact, inference, hypothesis, recommendation, contradiction, unknown, provenance, authorship, validation and supersession metadata must remain inspectable after packaging, repository storage and rendering.
- **Repository handling preserves lineage.** Knowledge Repository validation must retain source, Evidence, Observation, Unknown, Contradiction, authorship and recommendation lineage.
- **Runtime follows authority.** Flora implementation contracts must follow Accepted ADRs, FP-010, FP-011, EI-013 and the normative specifications; documentation reconciliation must not imply runtime functionality has been built.
