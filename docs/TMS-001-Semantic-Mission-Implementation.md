# TMS-001 semantic and Commercial Mission implementation

## Authorities consulted

This increment applies FP-012's evidence-bounded Enterprise Intelligence, FP-013's progressive Executive Inspection, FP-014's declared mission/truth boundary, WP2-003's deterministic composition contract, ADR-014 and EIRP-001's existing reasoning stages, and EI-001/EI-002 identity and relationship rules. It retains the accepted package import, candidate review and explicit promotion boundary described by WP1-005/WP1-006; canonical in-package placement does not mean governed acceptance.

## Root cause and correction

The TMS adapter previously staged only HFT upgrade inventories. Its generic `objects` collection forced all 56 inventory entries to `entity`, so capabilities, offers and other concepts became enterprise-like identities. The semantic workspace then inferred dossiers from names and subjects. It also did not stage the root evidence register or executive-intelligence object, so canonical references could not resolve.

The adapter now loads each explicitly typed root artefact before enrichment and preserves its source path, ID, candidate lineage and type. Upgrade objects retain their declared `object_type`; they cannot override the canonical enterprise collection. Enterprise dossiers are seeded only by canonical `enterprise_twin` objects (or an explicit generic enterprise identifier for non-TMS packages), then resolve typed reference arrays through an ID index. Broken references remain visible.

## Commercial Mission and composition

The existing authenticated-user JSON profile owner is reused. The Sales Director / Sopra Steria mission is persisted as human-supplied operational context and now includes the requested interests and optional named-account/campaign fields. The inspect/edit route writes atomically to that same profile store. No Sopra Steria offer portfolio was present, so offer alignment remains explicitly incomplete; no offer is invented.

Candidate executive reasoning from `11_executive_intelligence.json` is split into traceable presentation conclusions while retaining common evidence, confidence, freshness, unknowns, source and candidate status. The deterministic workspace uses supplied `why_now` content and exposes a categorical evidence-sufficiency/permitted-use assessment rather than a score.

## Reconciliation and validation

Before correction, the workspace derived 56 mixed enterprise identities from the HFT object inventory. After correction, it reports 14 canonical priority enterprises, separately from 10 canonical Market Participants, 16 upgrade capabilities/offers and nine canonical Opportunity Hypotheses. The validation panel also reports evidence, unknowns, contradictions, evidence coverage, unsupported claims, unused evidence, missing dates and unresolved references.

Canonical root records form a read-only semantic projection alongside the preserved 315 staged upgrade candidates; they do not expand promotion scope. Nothing is silently promoted: staged candidates still pass through existing quarantine, review, reconciliation and explicit promotion services.

## Remaining gaps

There is no governed Sopra Steria offer portfolio in the fixture or current stores. Offer alignment therefore remains incomplete until a human supplies operational offer context or the existing import/review workflow accepts governed corporate knowledge. Source-quality detail is inspected through linked evidence records rather than collapsed into a new score. Some upgrade-only references intentionally remain unresolved when their endpoint is not present in a canonical root collection; these are reported rather than inferred.
