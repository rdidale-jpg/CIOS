# Repair 02 — producer/consumer assessment before implementation

Baseline: main `327fb506d46fda1ba981ed0aa1ff85a4c56486e5`, merged #530–#534.
Accepted ADR-002/009/012/014/024/026 retain authority and are unchanged.

Retained TEL W5/W6 each contain six Enterprise Dossiers; BNK W1 contains eleven.
The existing Researcher adapter preserves their scalar/nested fields and Evidence
links in source_payload, but wrappers remain support metadata, not Observations.
No canonical Enterprise Model is created by accepting a wrapper. PR #531 already
provides safe typed Observation -> model projection; PR #534 supplies scoped
Evidence mapping and release continuity. Neither should be rebuilt.

| Source class | Available contract | Disposition |
| --- | --- | --- |
| Explicit Evidence.supported_claim linked from a dossier's evidence list | Producer-written assertion, source location, confidence, publication/collection dates | Offer for an explicit owner-selected atomic handoff; existing atomicity/Observation constructor and current Evidence checks must pass. No sentence splitting or semantic extraction. |
| Dossier leadership scalar, e.g. NatWest group_ceo | Name and Evidence links, but retained executive-page summary does not explicitly assert that name | Candidate requiring additional source support; not automatically converted into a fact. |
| TEL financial_intelligence revenue/profitability | Mixed figures, periods, comparisons and commentary within a string | Compound or insufficiently typed; defer, without extracting arbitrary numeric facts. |
| Identity/legal entity | Some explicit roles; numerous Unknown/revalidation statements | Not proof of legal identity or canonical Enterprise ownership. Owner must explicitly map source dossier to target enterprise. |
| Pressures, opportunity/procurement, recommendations, supplier narratives | Mixed hypotheses, recommendations and source context | Remain research context; no automatic commercial or Material Pressure promotion. |
| Relationships to ENT/PROG/OPP/PROC/MP identifiers | Candidate endpoints, not necessarily existing governed objects | Resolve only owned canonical endpoints or approved planned objects; defer unresolved edges and retain source endpoints. |

Minimum handoff uses the existing staging/review/mapping records, existing
Observation fields, EvidenceRepository, and PR #531 promotion/projection. An owner
explicitly selects a dossier and its linked Evidence.supported_claim, confirms
enterprise identity and a permitted event/leadership Observation attribute and
rationale. The source assertion is copied verbatim, never rewritten. Publication
and collection dates must be complete ISO dates; publication is labelled as the
observed/source date, not invented event-effective timing. Explicit source
effective/supersession/uncertainty fields are preserved when present.

For a fresh, unpromoted package only, selected Evidence can receive an explicit
enterprise ownership decision in its existing staged canonical fields, with raw
source_payload unchanged and the decision recorded in existing mapping/review
lineage. No canonical write happens at handoff. Already accepted Evidence under a
different owner cannot be silently moved or copied. Owner-authorised selected
subset mode explicitly defers other candidates; their payloads remain inspectable.
This is partial package acceptance, not a complete Industry Twin.

The derived Observation requires a separate review decision. Handoff candidates
must not inherit the normal automatic review approval. Generated identities use
the existing stable Observation identity, so package version alone cannot duplicate
facts/confidence history. The runtime rechecks the approved handoff before writing.
Existing strict reasoning and pressure qualification remain unchanged.

Canonical graph completeness is reported as counts of resolved/deferred edges,
never inferred from candidate graph resolution. No wrapper is promoted to close
an edge. Existing model-backed views and bounded retrieval consume only the
accepted Observation/model/Evidence path, separate from candidate dossier views.
