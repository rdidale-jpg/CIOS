# TEL-001 semantic import reconciliation

## Finding and recommendation

**MERGE.** The immutable archive is unchanged. The failure was at the reusable
Researcher-profile mapping boundary: bare governed rows were correctly assigned
an object class, but their nested producer vocabulary was passed through without
the stable aliases consumed by `SemanticObject` and the executive views. There
was no persistence truncation. Seven reinvention rows were additionally mapped
to the projection-only `transformation_pressure_view` class and quarantined.

The correction adds aliases while retaining the complete original row in
`source_payload`, and emits `mapping_diagnostics` containing source, mapped and
unmapped field names. It neither assesses completeness nor authorises promotion.

## End-to-end representative trace and field matrix

| Family / source class | Source fields and nesting | Canonical owner and transformation | Validation | Executive projection | Result |
|---|---|---|---|---|---|
| Industry Overview / `industry_overview` | `executive_summary`, `definition`, `economics`, `technology_landscape`, `value_chain`, nested evidence | `industry_twin`; summary → `description`, whole document → `industry_profile`, evidence → `evidence_refs` | Declared collection and ID required; owner assessment unchanged | Industry Overview / advanced canonical attributes | Populated supported source content; no inferred completeness |
| Enterprise Dossier / `enterprise_dossiers` | `executive_overview.what/pressures`, `corporate_strategy`, `operating_model`, `financial_intelligence`, `technology_landscape`, ecosystem arrays, portfolio and embedded reinvention | `enterprise_twin`; mapped to `description`, `strategy`, `operating_structure`, `financial_context`, `technology`, `ecosystem`, `pressures`, `programmes`, `transformation_posture` | Existing candidate validation and promotion authority | Enterprise dossier canonical identity and profile attributes | Six substantive, lossless dossiers |
| Market Participant / `market_participant_profiles` | `name`, `role`, `classification`, `commercial_significance`, capabilities, relationships, evidence | `market_participant_twin`; name → `organisation_name`, classification → `domain`, significance alias; other owner fields retained | Existing validation | Participant inspection/profile | 17 profiles retain role, domain, capability, links and evidence |
| Programme / `programme_objects` | `programme_name`, owners, `strategic_objective`, phase, timeline, budget, procurement, milestones/evidence | `transformation_programme`; stable aliases `title`, `owner`, `business_unit`, `objective`, `timing`, `investment` | Existing validation | Programme canonical attributes | 13 useful programme hypotheses; no completion inference |
| Opportunity / `opportunity_objects` | `opportunity_title`, nested `client_problem`, customer IDs, buyer, nested timing/value, Wave 5 commercial/value types, evidence/unknowns/contradictions | `opportunity_hypothesis`; nested values copied to stable owner aliases | Existing eligibility and owner assessment remain authoritative | Opportunities reads canonical owner only | Exactly 17; no derived register, evidence, relationship, or nested row becomes an opportunity |
| Reinvention / `reinvention_assessments` | operating model, mechanisms/functions, timing/tipping point, implications, evidence and uncertainty | existing `ai_reinvention_assessment`; stable summary/title/function/timing/consequence aliases | Supported canonical candidate, not projection-only quarantine | Reinvention inventory and canonical inspection | Seven canonical records; zero automatic promotion |
| Evidence / `evidence_register` | supported claim/object, publisher, URL, dates, confidence | `evidence`; claim → `statement`, object → `subject`, publication → `freshness` | Existing evidence validation | Evidence Sources and owner references | 92 linked records |
| Unknown / `unknown_register` | question, object, field, reason, impact, searched sources | `unknown`; question → `statement`, object → `subject`, impact → `consequence`, searched sources → evidence refs | Existing uncertainty governance | Unknowns and owner references | 30 linked records |
| Contradiction / `contradiction_register` | issue, competing claims, sources, impact and resolution | `contradiction`; issue → `statement`, sources → evidence refs, impact → consequence | Existing contradiction governance | Contradictions and owner references | 11 linked records |
| Relationship / `relationship_register` | source, target, type, rationale, evidence | `relationship`; endpoints retained and added as canonical references | Existing validation | Relationship collection / dossier association | 308 linked edges |
| Membership / `membership_register` | parent twin, child identity/type, role, rationale, period, evidence | `membership`; endpoints retained and added as canonical references | Existing validation | Membership collection | 50 linked memberships |

All other fields remain under their canonical owner's attributes and are named
in diagnostics; none is silently allow-listed away. Required executive meaning
still fails the existing presentation/completeness contract when the mapped
value is absent, and owner-produced assessment/promotion decisions are not
replaced by field-presence checks.

## Opportunity reconciliation

The 17 rows in `opportunity_objects_wave5.ndjson` are the canonical opportunity
owners. The reported 272 were repeated opportunity-shaped rows in derived Wave
5 registers (qualified, residual, procurement, horizon, buyer, identity and
estimate outputs) and/or nested support lines reconstructed by a local view.
Those record sets have no canonical semantic role and remain lineage-only. The
business collection selects only `opportunity_hypothesis`, so evidence and
relationships cannot inflate the count.

## Counts and snapshots

| Measure | Before | After |
|---|---:|---:|
| Accepted canonical candidates | 641 | 648 |
| Quarantined reinvention projections | 7 | 0 |
| Industry / enterprise / participant / programme / opportunity | 1 / 6 / 17 / 13 / 17 | 1 / 6 / 17 / 13 / 17 |
| Reinvention assessments | 0 | 7 |
| Evidence / Unknown / Contradiction | 92 / 30 / 11 | 92 / 30 / 11 |
| Relationships / Memberships | 308 / 50 | 308 / 50 |
| Lineage-only rows | 412 | 412 |

The before snapshot is the prior staging regression. The after snapshot is
asserted directly against the unchanged SHA-256-pinned package. No research
content, archive member, checksum, owner assessment, or promotion state changed.
