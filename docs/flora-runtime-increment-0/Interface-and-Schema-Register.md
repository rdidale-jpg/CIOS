# Interface and Schema Register

**Register version:** 0.1  
**Scope:** Increment 1 estimation contracts only. These are documentation stubs, not production interfaces.

| Contract | Status | Owner/source | Version | Producer | Consumer | Authority | Persistence | Minimum validation | Open questions |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GovernedAssetRead | Required stub | ADR-024, FEIR-001, ADR-016 | 0.1 | Governed Asset Connector | Workspace projection | Read projection | None except cache metadata | Path exists; status captured; owner captured; access allowed | Formal source status taxonomy. |
| ManifestRead | Existing partial | Banking manifest, runtime plan | 0.1 | Manifest adapter | Ingestion report | Source index | None | JSON parse; asset paths resolve; IDs unique within manifest | Accepted schema needed before broader use. |
| KnowledgePackRead | Required stub | ADR-016 | 0.1 | Knowledge Pack adapter | Workspace projection | Exchange package | None | Pack ID, status, owner, lineage, Unknowns/Contradictions retained | Pack spec location/status to normalize. |
| FocusObjectProjection | Required stub | FA-001, ADR-025, FEIR-001 | 0.1 | Runtime Object Registry | Workspace view | Runtime projection | Cache allowed | Identity envelope complete; source authority linked | Supported object types for v1. |
| RelationshipProjection | Required stub | EI-002, FEIR-001 | 0.1 | Relationship resolver | Focus view/lineage | Runtime projection | Cache allowed | Source/target resolve; relationship type known; source asset lineage | Canonical relationship ID absent. |
| EvidenceObservationAvailability | Required stub | ADR-001, EI-012, ADR-014 | 0.1 | Retrieval adapter | Evidence/Observation panel | Availability response | Audit only | Return available/unavailable/safe-unavailable with reason | Canonical store boundaries vary. |
| UnknownResponse | Required stub | FEIR-001, EI-012 | 0.1 | Runtime projection | Workspace reasoning panel | Projection | Cache allowed | Unknown text/ID, parent object, evidence demand, source | ID convention incomplete. |
| ContradictionResponse | Required stub | FEIR-001, EI-012 | 0.1 | Runtime projection | Workspace reasoning panel | Projection | Cache allowed | Competing claims/sources preserved; no collapse | Conflict status taxonomy. |
| LineageResponse | Required stub | ADR-005, ADR-014, FA-001 | 0.1 | Lineage resolver | User inspection | Runtime projection | Audit refs | At least source asset path/version and evidence/observation refs when present | Depth beyond one hop later. |
| WorkspaceState | Existing partial | FA-001, workspace code | 0.1 | Workspace State Service | Flora UI | Runtime state | Allowed | User/workspace/focus/perspective captured; no canonical fields | Persistence duration. |
| AuditEvent | Required stub | FEIR-001, ADR-014, ADR-024 | 0.1 | All Increment 1 services | Audit ledger | Operational audit | Required | User/trigger, timestamp, focus object, assets, operation, outcome, validation, access, failure, component version | Retention/privacy ADR later. |
| IngestionReport | Required stub | FEIR-001 runtime ingestion | 0.1 | Ingestion/normalisation | Runtime operator, reviewer | Runtime diagnostic | Required | Assets read, skipped, invalid, unknown status, collisions, safe failures | Whether report is committed or runtime-only. |
| SafeUnavailableResponse | Required stub | ADR-014, FEIR-001 | 0.1 | Any adapter/service | Workspace UI | Runtime response | Audit only | No fabricated content; failure reason; next safe action | UX wording standard. |

## Minimal documentation-only stubs

```yaml
FocusObjectProjectionV0_1:
  object_id: string
  object_type: string
  display_name: string
  authority_class: governed|derived|candidate|runtime|transient
  lifecycle_status: string
  version: string|null
  owner: string
  source_path: string
  source_asset_id: string|null
  evidence_cutoff: string|null
  provenance_refs: [string]
  unknown_refs: [string]
  contradiction_refs: [string]
```

```yaml
AuditEventV0_1:
  event_id: string
  occurred_at: iso8601
  actor_id: string
  actor_type: user|system
  workspace_id: string
  focus_object_ref: string
  operation: read_asset|project_object|resolve_relationship|inspect_lineage|safe_unavailable
  source_asset_ids: [string]
  source_asset_versions: [string]
  outcome: success|denied|unavailable|validation_failed
  validation_result: string
  access_decision: allow|deny|not_applicable
  failure_reason: string|null
  component_version: string|null
```
