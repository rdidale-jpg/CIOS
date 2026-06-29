# Ontology Attribute Taxonomy

## Document Metadata

| Field | Value |
|---|---|
| Document ID | CIOS-CBOK-STD-000-ATTR |
| Title | Ontology Attribute Taxonomy |
| Version | 1.0.0 |
| Status | Approved |
| Owner | CIOS Knowledge Governance |
| Last Reviewed | 2026-06-29 |

## Modelling Rules

Attributes shall describe intrinsic or governed properties. Attributes must not encode relationships that require first-class relationship semantics.

| Category | Definition | Examples | Modelling Rules | YAML Representation Guidance |
|---|---|---|---|---|
| Identity attributes | Attributes used to identify an artefact. | `identifier`, `canonical_name`, `version` | Shall be stable and unique within scope. | Include `required: true` and controlled data type. |
| Descriptive attributes | Human-readable explanatory properties. | `definition`, `description`, `rationale` | Should be concise and implementation independent. | Use strings or markdown-safe text fields. |
| Classification attributes | Attributes that place artefacts in governed categories. | `domain`, `object_family`, `primitive_type` | Shall use controlled values where available. | Use `allowed_values` when category set is governed. |
| Quantitative attributes | Numeric or scored properties. | `risk_score`, `confidence_score`, `value` | Shall define scale, unit and interpretation. | Include `data_type`, `unit` and `scale`. |
| Temporal attributes | Time, date or validity properties. | `created_at`, `effective_from`, `review_due` | Should use ISO dates or datetimes. | Use date strings and document timezone expectations when needed. |
| Evidence attributes | Properties linking evidence or provenance. | `evidence_id`, `source`, `provenance` | Shall preserve traceability to evidence records. | Prefer identifiers or references over prose-only notes. |
| Confidence attributes | Properties recording certainty or readiness. | `scientific_confidence`, `operational_confidence` | Shall use governed confidence values. | Use controlled strings and cite confidence rationale. |
| Governance attributes | Ownership and review properties. | `owner`, `status`, `last_reviewed` | Shall identify accountable owner and lifecycle state. | Include in metadata blocks for all governed artefacts. |
| Implementation attributes | Explicit mapping metadata for SDK, graph or application use. | `sdk_model`, `graph_label`, `schema_version` | Must not redefine commercial meaning. | Place under `mapping` or equivalent implementation section. |
