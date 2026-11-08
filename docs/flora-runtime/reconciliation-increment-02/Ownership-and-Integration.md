# Increment 02 — ownership and pre-implementation contract assessment

Baseline: `6f76511a5708e5e5820119c611af5b1d71258a63` (main; merged PR #530).

## Existing canonical path

1. `BlueprintPackageRegistry.receive`: immutable ZIP, checksum, identity, registry and import receipt; no canonical intelligence writes.
2. `BlueprintPackageValidator.validate_and_stage`: candidate records and validation diagnostics, not canonical acceptance.
3. `CandidateReviewService`, `ImportMappingService`, `DryRunPlanningService`: object-level decisions, target IDs and proposed effects; no canonical writes.
4. `CanonicalPromotionService.approve_plan`: actor permissions, nonempty rationale, constructor checks and package/plan/review/mapping fingerprints; approval is not execution.
5. `CanonicalPromotionService.execute_approved_plan` / `_promote`: supported approved create/update effects reach EvidenceRepository, ObservationRepository, ContradictionRepository and existing generic repositories. This is canonical acceptance.
6. `ObservationMemoryService.apply_observation`: existing model-update owner; consumes an already validated Observation, uses the existing ledger for conflict links, and writes EnterpriseModelRepository snapshots. It does not need a second extraction pass.
7. BoundedTwinRetrievalService and EnterpriseCanvasService consume existing models and canonical records. Presentation and reasoning are not canonical owners.

ADR-002, ADR-009, ADR-012, ADR-014, ADR-024 and ADR-026 retain authority. No accepted ADR is changed.

## Contract mismatches found before implementation

- Promotion saves Observations but does not call the model-update owner.
- `apply_observation` is a low-level owner API: accepting a generic imported type/attribute as input does not establish a supported mapping. Only typed inputs already described by the service's factual vocabulary/domain prefixes will be projected. Generic facts, wrappers, relationships and analytical objects must not acquire invented mappings.
- Evidence alone is not an Enterprise Model update. Supporting Evidence must exist within the Observation's enterprise before projection.
- Canonical import ID overrides, external fingerprints and package-only permission checks need target-owner checks to prevent cross-enterprise ID collisions and writes.
- Import date fallback can prefer collection time over an explicitly supplied Observation date; supplied effective period/scope are not carried into the existing provenance mapping.
- ObservationRepository corroborates identity but does not persist explicitly approved lifecycle corrections. The model service ignores retirement rather than marking existing model state inactive. These need narrow extensions in their existing owners; no new ledger or schema.
- Promotion's file backups cover canonical ledgers but not affected model snapshots. Success receipt/audit publication occurs outside the compensated block. Fixed backup names also have no crash-recovery guarantee.

## Minimum intended boundary

Save approved canonical effects first, then project only the affected, safely mapped canonical Observations through ObservationMemoryService in the same compensated promotion attempt. Extend the existing promotion receipt with projection diagnostics, not a new intelligence object. Unsupported mappings remain canonical where already authorised and are explicitly reported as partial projection.

Single-writer file compensation is not an ACID transaction. Include affected model snapshots and success receipts in compensation, serialize importer execution, refuse unrecovered backup artifacts, and expose failed/uncertain recovery rather than returning success. Other writers/processes and power-loss recovery remain explicit operating limits; no production backfill is performed.

## Implemented reconciliation boundary

`execute_approved_plan` now persists all approved canonical effects, resolves the
actual saved Observation IDs, and invokes `ObservationMemoryService.apply_observation`
for supported, enterprise-scoped canonical inputs before publishing success.
It does not call evidence decomposition or manufacture another Observation.
`CLAIM_VOCABULARY` and its owned attribute prefixes bound the mapping. Evidence
alone and other canonical record classes do not acquire invented model mappings.
The existing receipt adds optional `model_projection_status` and
`model_projection_results` diagnostics; no canonical object schema changes.

Lifecycle updates use an explicitly authorised update effect and the existing
Observation repository. Prior lifecycle state and both original and correction
approval lineage remain in existing provenance metadata. The model service marks
an affected current value inactive instead of erasing its value/history or
inventing a replacement. Canvas omits inactive current support; canonical records
remain inspectable. Scoped explicit successors prevent older facts from becoming
current merely because of package order or re-import.
