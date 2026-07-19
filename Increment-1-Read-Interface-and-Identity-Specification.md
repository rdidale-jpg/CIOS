# Increment 1 Read Interface and Identity Specification

**Status:** Proposed Specification for Increment 1  
**Version:** 0.1.0  
**Scope:** Flora Runtime Increment 1: Read-Only Object Workspace Slice for governed UK Banking Enterprise Intelligence.

## Purpose

This specification freezes the minimum contracts Flora needs to read, project, and present governed UK Banking Enterprise Intelligence without creating canonical knowledge, generated reasoning, scoring, Recommendations, write-back, lifecycle transitions, or provider-specific runtime behaviour.

## Authority

Authority order used by this specification:

1. Accepted ADRs: ADR-001, ADR-005, ADR-014, ADR-016, ADR-024.
2. Owning Enterprise Intelligence and founding papers.
3. CIOS Reference Architecture.
4. Accepted specifications.
5. Proposed references: ADR-025, FEIR-001, and FA-001.
6. Product and UX guidance.
7. Runtime implementation roadmap.
8. Governance templates and handbooks.

Proposed documents are used only as reference standards. Where proposed runtime material describes generated reasoning, scoring, or Recommendations, Increment 1 excludes it and preserves the accepted read-only, evidence-first, lineage-inspectable posture.

## Scope

Included: focus-object identity and display projection, governed relationships, Evidence and Observation availability, Unknowns, Contradictions, lineage, non-canonical workspace state, audit events, ingestion outcomes, and safe-unavailable behaviour.

Excluded: APIs, UI components, graph persistence selection, GPT workers, reasoning orchestration, hypotheses generation, Recommendations, scoring, lifecycle transitions, human approval workflows, write-back, model-provider selection, and canonical mutation.

## Design Constraints

- Every runtime response is a projection, report, audit event, workspace state, or safe-unavailable response; none is canonical Enterprise Knowledge.
- Evidence, Observations, Unknowns, and Contradictions remain separate object classes.
- Runtime contracts fail closed when identity, authority, access, lineage, or schema validity is unsafe.
- Missing governed metadata is explicit and never filled with fabricated defaults.
- Human-supplied knowledge remains labelled and is not promoted by display.
- Proposed authority may inform implementation shape but not override accepted ADRs or owning architecture.

## Identity Principles

1. IDs are opaque identifiers, not display labels.
2. Display names must not be used as identifiers.
3. Object identity and object version must be distinguishable.
4. Runtime projection identity must not replace canonical identity.
5. Source asset identity must remain inspectable.
6. Cross-enterprise relationships require explicit enterprise boundaries.
7. Unresolved identity must not be silently inferred.
8. Identifier collisions must fail safely.
9. Candidate intelligence identifiers are outside Increment 1 display semantics unless already governed source identifiers.
10. Runtime workspace state identifiers are non-canonical.

### Temporary Identity Resolution Envelope

Use this envelope for heterogeneous corpus IDs; do not rewrite source assets:

| Field | Meaning | Required |
|---|---|---|
| `original_identifier` | Identifier as found in the governed source. | Yes |
| `original_identifier_type` | Source-declared or observed identifier family. | Yes |
| `owning_asset` | Source asset where the identifier occurs. | Yes |
| `resolved_runtime_identifier` | Runtime identifier when safely resolvable. | No |
| `resolution_status` | `resolved`, `unresolved`, `collision`, `not_applicable`. | Yes |
| `collision_status` | `none`, `suspected`, `confirmed`. | Yes |
| `resolution_rationale` | Human-readable reason, with source reference. | Yes |

## Authority and Persistence Classifications

`authority_status`: `accepted`, `validated`, `candidate`, `proposed`, `unclassified`, `missing`, `unknown`.

`lifecycle_status`: source lifecycle label when provided; otherwise `null` or omitted when not applicable.

`persistence_class`: `canonical_reference`, `read_projection`, `workspace_state`, `audit_record`, `ingestion_report`, `safe_unavailable`, `transient`.

`freshness_status`: `current`, `stale`, `incomplete`, `unknown`, `not_applicable`.

Unavailable value semantics:

- **Absent:** field not applicable to this contract instance.
- **Null:** field applicable, but source provides no truthful value.
- **Unknown:** source says value is unknown or runtime cannot determine it safely.
- **Not applicable:** field does not apply to the object or response class.
- **Safe unavailable:** response cannot be presented without violating identity, authority, access, lineage, freshness, or schema constraints.

## Common Metadata Envelope

All Increment 1 projections that present governed object identity use `IdentityEnvelopeV0_1` with: `object_id`, `object_type`, `schema_version`, `source_asset_id`, `source_asset_version`, `canonical_owner`, `authority_status`, `lifecycle_status`, `persistence_class`, `enterprise_id`, `created_at`, `updated_at`, `valid_from`, `valid_to`, `freshness_status`, `human_supplied`, `provenance_reference`, and `access_classification`. Required fields are limited to values the governed source or runtime contract can truthfully provide.

## Contract Definitions

### FocusObjectProjectionV0_1

Purpose: place an Enterprise Intelligence object in focus.

Fields: `identity`, `display_name`, `object_type`, `short_description`, `enterprise_context`, `authority_status`, `lifecycle_status`, `freshness_status`, `provenance_summary`, `available_perspectives`, `available_universal_actions`, relationship/Evidence/Observation/Unknown/Contradiction/lineage availability, and `safe_unavailable_notices`.

Rules: projection only; no generated reasoning; no Recommendation; actions must reflect authorised capability; unsupported actions are not advertised; missing metadata remains explicit.

### RelationshipProjectionV0_1

Fields: `relationship_id`, `source_object_id`, `target_object_id`, `target_original_identifier`, `relationship_type`, `direction`, source/target enterprise IDs, authority/lifecycle status, effective dates, provenance, confidence when governed, human-supplied flag, contradiction status, and resolution status.

Rules: never infer relationships from labels; never convert generated associations into governed relationships; unresolved targets remain unresolved; cross-enterprise relationships expose both enterprise contexts; relationship type must use an owned vocabulary or be `unclassified`.

### EvidenceObservationAvailabilityV0_1

Fields: `focus_object_id`, Evidence/Observation/accepted Observation/candidate counts, freshness summary, authority summary, lineage coverage, inaccessible/unavailable counts, paging information, and notices.

Rules: Evidence and Observations remain distinct; counts do not imply inaccessible content is absent; raw Evidence is not elevated to Observation; availability is not quality or sufficiency; no opaque intelligence score.

### UnknownResponseV0_1

Fields: Unknown ID, Focus Object ID, statement, category, origin, authority/lifecycle status, dates, owner, evidence demand, linked objects, linked Observations, impact, provenance, human-supplied flag, and distinction class.

Rules: Unknowns are not errors; do not infer missing answers; missing data is not automatically a governed Unknown; distinguish governed Unknown, unavailable, inaccessible, unresolved identity, and not applicable.

### ContradictionResponseV0_1

Fields: Contradiction ID, Focus Object ID, conflicting references, statement, status, materiality, authority/lifecycle status, evidence and Observation references, provenance, human review status, and resolution history.

Rules: both sides remain inspectable; the interface selects no winner; missing authority is visible; resolved contradictions preserve history; do not collapse conflict into confidence score.

### LineageResponseV0_1

Minimum path where available: Source → Evidence → Observation → governed object or relationship → presentation projection.

Fields: requested object ID, lineage nodes, lineage edges, node type, source asset ID, authority/lifecycle status, version, temporal validity, provenance reference, unavailable segments, access-redacted segments, and completeness status.

Rules: partial lineage is labelled partial; inaccessible lineage is not absent; missing lineage produces incomplete or safe-unavailable outcome; presentation never implies stronger lineage.

### WorkspaceStateV0_1

Fields: workspace state ID, user ID, tenant context, Focus Object ID, active perspective, navigation trail, watch state, filters, optional comparison state, dates, retention class, and schema version.

Rules: not Enterprise Knowledge; no authoritative copies of governed objects; store references and interaction state only; deletion does not affect governed knowledge; comparison can be omitted in V0_1.

### AuditEventV0_1

Fields: audit event ID, event type, timestamp, actor, tenant context, Focus Object ID, source asset IDs/versions, operation, access decision, validation result, outcome, failure reason, component/version, correlation ID, and safe-unavailable status.

Rules: keep operational telemetry, access audit, reasoning provenance, human decision history, and canonical knowledge history distinct. Increment 1 covers read activity, ingestion, access decisions, validation, and safe failure only.

### IngestionReportV0_1

Fields: ingestion run ID, source asset/version, timestamps, schema version, object/relationship/Evidence/Observation/Unknown/Contradiction counts, accepted/rejected/unresolved/collision/warning counts, validation failures, safe-unavailable causes, and resulting projection version.

Rules: ingestion success does not imply claim acceptance; package validity does not promote claims to truth; rejected and unresolved records remain reportable; reports do not mutate owning assets.

### SafeUnavailableResponseV0_1

Reason classes: `object_not_found`, `identifier_unresolved`, `identifier_collision`, `access_denied`, `source_unavailable`, `source_stale_beyond_policy`, `unsupported_object_type`, `missing_authority_metadata`, `missing_lineage`, `invalid_source_schema`, `ingestion_incomplete`, `relationship_target_unresolved`, `dependency_unavailable`.

Fields: status, reason code, user-safe explanation, technical reference, affected object/asset IDs, correlation ID, retryable, recommended next action, and audit event reference.

Rules: fabricate no substitute content; no generated fallback interpretation; sensitive details are not exposed to unauthorised users; retry guidance reflects actual retryability; responses are auditable.

## Validation Rules and Error Behaviour

- Validate schemas with JSON Schema Draft 2020-12.
- Validate fixture outcome manifests before implementation.
- Treat schema failures, missing authority metadata, unresolved IDs, collisions, access denial, and missing lineage as safe-unavailable candidates.
- Invalid fixtures must fail for the documented reason.
- Link checks should cover repository-local references in this spec, fixtures, reports, and schema `$id` references.

## Fixture Examples

Fixtures are under `fixtures/flora-runtime/increment-1/uk-banking/` and include valid, partial, invalid, and safe-unavailable examples. Values are drawn from `enterprise-knowledge/banking/MANIFEST.yaml`, `enterprise-knowledge/banking/flora/Banking-Knowledge-Manifest.json`, `enterprise-knowledge/banking/canonical/banking-research-canonical-objects.json`, and banking completion reports. Synthetic fixture values are labelled in fixture names or values.

## Compatibility Policy

V0_1 is pre-1.0. Consumers must ignore undocumented fields because schemas set `additionalProperties: false`. Additive optional fields can be introduced in V0_1 patch releases only when absent/null/unknown semantics remain unchanged.

Breaking changes include changing required fields, changing reason-code meaning, collapsing object classes, weakening safe-unavailable behaviour, or changing identity semantics.

## Versioning Policy

Schema IDs follow `https://cios.local/schemas/flora-runtime/v{major}.{minor}/{contract}.schema.json`. Fixture packages follow `fixtures/flora-runtime/increment-1/<domain>/` and declare expected outcomes in README. Deprecation requires a replacement schema, migration notes, and fixture coverage.

## Explicit Exclusions

Increment 1 excludes canonical mutation, generated reasoning, hypothesis generation, Recommendations, numeric opportunity scoring, graph product choice, model-provider choice, worker execution lineage, human approval workflow, write-back, UI/API implementation, and source-ID rewriting.

## Acceptance Criteria

All ten contracts and schema stubs exist; identity envelope is defined; fixtures cover valid, invalid, partial, and unavailable states; identity collisions/unresolved relationships are documented; authority and persistence classes are explicit; inaccessible and absent information are distinguishable; safe unavailable fails closed; traceability is complete; schema validation passes; implementation can proceed without inventing semantics.
