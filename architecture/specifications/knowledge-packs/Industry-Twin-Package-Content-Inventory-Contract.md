# Industry Twin Package Content Inventory and Deficiency Contract

**Status:** Draft Normative controlled schedule to IT-001; implementation-profile layer active
**Governance role:** IT-001 governs Industry Twin content semantics through this schedule. The Knowledge Pack Specification governs envelope, packaging and exchange mechanics. Neither document silently takes ownership of the other's semantics.
**Physical-layout rule:** logical content only; no new mandatory directory structure or runtime schema.

## 1. Self-description and inventories

An Industry Twin `.zip` declares release ID/version, scope/boundaries, target decisions, research period/effective date, producer/reviewer, provenance, checksums, compatibility, validation/completeness/promotion state, freshness and supersession. Every entry has stable ID, object type, tier/rationale where applicable, owner, lifecycle/effective dates, provenance, package locator and relevant relationships.

| Inventory | Required logical content |
|---|---|
| Objects | Industry/subsectors, Enterprises, Market Participants/suppliers, executives/buying centres, products/services/capabilities/offers, transformations/opportunities and their tier/state |
| Facts | atomic governed assertion preserving, where applicable: assertion ID; subject; predicate; value and unit; fact classification (current/historical/forecast/target/expectation/inference/superseded); valid-from and valid-to; observation/publication date; source and evidence IDs; extraction/transformation provenance; confidence; freshness/review state; scope/geography; and supersession lineage |
| Sources/evidence | source/document identity/type/organisation/authority, citation/locator, source/publication/retrieval/effective dates, lawful extract or governed paraphrase, licence/access, freshness, provenance and integrity metadata |
| Documents/references | packaged document only when lawful; otherwise metadata/citation/access constraint and linked extracted facts |
| News | governed event fields from completeness contract, affected objects and observation/contradiction effects |
| Analyst | attributable observation fields, comparative assessment, licence constraints and affected objects |
| Capabilities/offers | detailed first-class records; provider, scope, deployment/delivery/integration, buyer, proof, commercial signals, lifecycle, constraints and opportunity links |
| Transformations/opportunities | detailed state, ownership, timing, economics, ecosystem, evidence, uncertainty and reasoning |
| Observations/reasoning | observations, Signals/Insights/Themes where used, hypotheses, commercial theses and recommendations with transformation lineage |
| Relationships | typed/directed endpoints, provenance, confidence, effective interval and lifecycle state |
| Historical states | version/state snapshots or changes, effective dates, supersession reason and successor/predecessor |
| Uncertainty | separate Unknown and Contradiction inventories with affected objects/decisions, materiality, status, owner and next review |
| Assurance | dimension assessments, deficiencies/warnings, evidence-exhaustion records, independent review and promotion-gate results |

Inventories may be represented in compatible existing assets. A summary, source dump or links-only pack fails even when the envelope validates. Non-redistributable material uses lawful metadata, citation, extracted governed facts, compliant paraphrase, observation/reasoning and access restrictions.

Enterprise content uses the containment modes governed by IT-001: embedded governed release, embedded immutable snapshot, decision-scoped materialised projection, or declared external dependency. Embedded modes preserve source Twin identity/version, provenance, checksums, effective date and supersession lineage and never transfer semantic ownership. Tier 1 content needed for normal offline investigation cannot be links-only; omitted external dependencies are completeness and portability deficiencies with promotion impact.

## 2. Machine-readable deficiency record

Each record contains `code`, `title`, `dimension`, `object_type`, `object_id`, `description`, `detection_basis`, `evidence_ids`, `severity` (`warning|material|critical`), `blocking`, `remediation`, `evidence_exhaustion_applicability`, `owner`, `promotion_impact`, `status`, and review dates. Codes are stable; implementations may add fields/codes but not weaken meanings.

| Code | Title / dimension / object | Detection basis and evidence | Default severity / block | Remediation / exhaustion / owner / promotion impact |
|---|---|---|---|---|
| HFT-IND-001 | Shallow Industry coverage / Industry Fidelity / Industry | applicable material domains absent or summary-only; inventory/claim sample | critical / yes | populate evidence-linked detail; exhaustion only for discrete unavailable facts; IT-001; blocks |
| HFT-ENT-001 | Shallow Enterprise coverage / Enterprise Density / Enterprise | Tier 1 dossier lacks applicable breadth/depth | critical / yes | research/structure dossier; bounded exhaustion cannot cure material shallowness; EI-001/EIF-001; blocks |
| HFT-MPT-001 | Shallow Market Participant coverage / Participant Density / Participant | material participant is name/node or sparse dossier | critical / yes | complete dossier; discrete exhaustion only; participant owner/IT-001; blocks |
| HFT-CAP-001 | Missing capability detail / Capability & Offer / Capability | supplier invoked without scoped capability record/proof | critical / yes | create governed capability; exhaustion rarely cures decision-critical fit; participant/EI-002; blocks |
| HFT-OFR-001 | Missing offer detail / Capability & Offer / Offer | proposition/components/commercial/delivery detail absent | material / if material | create offer or mark not offered; exhaustion applicable; participant owner; blocks affected decision |
| HFT-FIN-001 | Missing financial periods / Financial / Enterprise | required comparable periods or metrics absent | critical / yes for material Enterprise | acquire primary periods or exhaustive gap; EI-001; blocks/conditions per effect |
| HFT-EVD-001 | Missing primary evidence / Primary Coverage / any | material claim uses secondary evidence despite available primary family | critical / yes | acquire/link primary; exhaustion if genuinely unavailable; ADR-010; blocks |
| HFT-EVD-002 | Missing annual-report evidence / Financial / Enterprise | applicable reporting Enterprise lacks report/filing coverage | material / yes for Tier 1 financial claim | inspect reports or record access absence; ADR-010/EI-001; blocks affected claim |
| HFT-NEW-001 | Missing news coverage / News / Tier 1 object | declared period has unexplained material coverage gap | material / yes | search explicit news families/periods; exhaustion applicable; IT-001/lifecycle; blocks if material |
| HFT-ANA-001 | Missing analyst coverage / Analyst / material object | applicable lawful perspective absent/unassessed | material / conditional | acquire lawful metadata/paraphrase or exhaustion/licence record; ADR-010/IT-001; blocks when decision-material |
| HFT-SRC-001 | Weak source diversity / Source Diversity / any | claims rely on one family, organisation or syndicated cluster | material / yes for material conclusion | independent corroboration; exhaustion applicable; ADR-010; blocks/conditions |
| HFT-TMP-001 | Stale evidence / Temporal / any | freshness threshold breached without reassessment | material / yes if current decision | refresh/supersede; exhaustion applicable; lifecycle; blocks affected decision |
| HFT-EVD-003 | Unsupported fact / Evidence Maturity / Fact | no adequate evidence edge | critical / yes if material | evidence, downgrade to inference/Unknown or remove claim; no exhaustion cure; ADR-010/EI-012; blocks |
| HFT-OBS-001 | Unsupported observation / Observation Maturity / Observation | missing evidence or opaque inference | critical / yes if material | link evidence/explain transformation; no cure; EI-012; blocks |
| HFT-REC-001 | Unsupported recommendation / Reasoning / Recommendation | cannot traverse to thesis/facts/evidence | critical / yes | rebuild or withdraw recommendation; no cure; EI-004; blocks |
| HFT-RSN-001 | Broken reasoning lineage / Reasoning / reasoning object | missing/unresolvable stage or rationale | critical / yes | restore typed lineage; no cure; EI-004; blocks |
| HFT-GPH-001 | Missing relationship / Graph / any | expected material typed relationship absent | material / if decision-relevant | research/link or explicit deficiency; exhaustion applies; EI-002; may block |
| HFT-GPH-002 | Dangling relationship / Graph / relationship | endpoint unresolved | critical / yes | repair/quarantine edge; no exhaustion; EI-002; blocks |
| HFT-IDN-001 | Duplicate identity / Graph / entity | collision/unreconciled aliases | critical / yes if material | resolve identity while preserving lineage; EI-002; blocks |
| HFT-TMP-002 | Temporal inconsistency / Temporal / any | impossible/conflicting state intervals/types | critical / yes | correct or represent Contradiction; lifecycle/object owner; blocks |
| HFT-TMP-003 | Missing historical state / Temporal / Tier 1 object | current-only view where material changes occurred | material / yes | reconstruct history or exhaustion; lifecycle; blocks if decision-material |
| HFT-UNC-001 | Hidden Unknown / Unknown Quality / any | known evidence gap omitted from governed inventory | critical / yes | restore/link/materiality-rate; no exhaustion cure; EI-012; blocks |
| HFT-CON-001 | Suppressed Contradiction / Contradiction Quality / any | conflicting evidence/conclusion omitted or flattened | critical / yes | restore both sides and decision treatment; no cure; EI-012; blocks |
| HFT-PRC-001 | Incomplete procurement intelligence / Enterprise Density / Buying Centre | decision route/cycle/incumbent/access materially absent | material / yes for commercial decision | research portals/contracts; exhaustion applies; EI-001; blocks affected use |
| HFT-TRN-001 | Incomplete transformation intelligence / Enterprise Density / Transformation | owner/scope/status/timing/ecosystem/evidence gap | material / yes if opportunity basis | complete/history or exhaustion; EI-001; blocks affected use |
| HFT-SUP-001 | Incomplete supplier intelligence / Participant Density / Supplier | fit/ecosystem/commercial/incumbent proof absent | critical / yes for recommendation | complete participant/capability dossiers; exhaustion limited; participant owner; blocks |
| HFT-OPP-001 | Incomplete opportunity detail / Opportunity / Opportunity | required buyer/problem/value/route/fit/risk/lineage absent | critical / yes if promoted | complete or withdraw maturity claim; EI-006/OT-001; blocks |
| HFT-EXH-001 | Unproven evidence exhaustion / Exhaustion / any | record omits mandatory strategy/search/effect fields | critical / yes where relied upon | repeat/document research and independent review; Production Protocol/ADR-010; blocks |
| HFT-FLO-001 | Non-addressable Flora content / Flora / any | packaged required content has no resolvable locator/traversal | critical / yes | add addressability metadata/projection mapping later; FEIR/presentation; blocks |
| HFT-PKG-001 | Package valid but content shallow / Package / release | syntax passes while material density requirements fail | critical / yes | remediate content, never validator-only; IT-001; blocks |
| HFT-PRO-001 | Promotion not ready / Promotion / release | one or more promotion gates fail | critical / yes | resolve gate and re-review; IT-001/lifecycle; blocks |

Severity may increase with materiality but cannot be lowered merely by passing package validation. Exhaustion remains evidence about absence, not remediation. Every blocking finding appears in release and Flora-addressable deficiency inventories.

## 3. Canonical ownership and implementation-profile boundary

This controlled schedule is the canonical implementation-profile owner because IT-001 already owns Industry Twin content and composition, while this schedule already owns the logical, structured, Flora-addressable package inventory. A new profile document would split that ownership and is prohibited. The profiles below bind existing subject owners to research, package, import and projection; they do not create a Twin taxonomy or redefine completeness, reasoning, evidence, eligibility or promotion.

Repository authority prevails where the reconciliation evidence proposed a broader type. In particular, a Programme remains an EI-001 Enterprise-owned governed object represented in the EI-002 graph, not a Programme Twin. Reinvention is an owner assessment using FP-012 method, not a new score. Unknowns and Contradictions remain EI-012 records. Relationships and membership records remain EI-002 edges.

This activation extends only this schedule, the versioned release-manifest exchange schema, and the subordinate Researcher Knowledge Pack instructions. It does **not** modify EI-001, EI-002, EIF-001, IT-001 core semantics, FP-009, FP-012, FP-013, FP-014, FEIR-001, EIRP-001, the completeness schedules, or Flora runtime. Those owners are referenced, not copied.

### 3.1 Common profile rules

Every object declares `profile_id`, `profile_version`, `object_id`, `object_type`, `canonical_owner`, `object_version`, `lifecycle_state`, `effective_from`, optional `effective_to`, `evidence_cut_off`, `section_status`, `evidence_refs`, `unknown_refs`, `contradiction_refs`, and `relationship_refs`. `section_status` has one entry for every mandatory or applicable conditional section and is exactly `populated`, `unknown`, or `not_applicable`. `unknown` resolves an EI-012 Unknown affecting the section. `not_applicable` records rationale, assessor, assessment date and basis/evidence. Blank, omitted, placeholder, summary-only and narrative-only values satisfy none of these states.

All evidence, confidence, freshness, Observation, reasoning, completeness, eligibility and promotion rules are evaluated by their existing owners. A profile states the references that must resolve; it never substitutes a local rule or score. A Contradiction is retained as an EI-012 reference with both sides and impact and never flattened into a preferred narrative.

Import applies, in order: envelope/checksum validation; known profile and version; mandatory section and field validation; conditional applicability; stable identity and version continuity; EI-002 endpoint and membership resolution; evidence/EI-012 reference resolution; canonical-owner assessment output presence; and release-pin integrity. Failure rejects or quarantines the candidate and must identify the profile, object, field/section and rule. Import success is not canonical promotion.

For every profile, acceptance requires all applicable mandatory fields and sections to be populated or explicitly Unknown, every inapplicable section to carry a valid Not Applicable record, all references to resolve, no suppressed Contradiction, and all profile-specific assertions below to pass. Flora may select, order, label and format conformant values. It must display governed unavailable states and must not infer absent structure.

## 4. Deterministic Twin Object Profiles

The field paths below are logical paths and may be serialised in any package layout allowed by the Knowledge Pack Specification. The registered profile version for this activation is `1.0.0`.

### 4.1 `industry-overview` — Industry Overview profile

- **Purpose:** provide the governed industry context from which executives inspect the composite.
- **Executive experience:** Industry Overview; source projection for Twin Map.
- **Mandatory sections:** identity-and-boundary; information; economics; pressures; structure; reinvention; assurance.
- **Mandatory fields:** common fields; `industry.name`; `industry.definition`; `industry.geographies[]`; `industry.in_scope[]`; `industry.out_of_scope[]`; `information.outcomes[]`; `economics.value_pools[]`; `economics.cost_and_funding_dynamics[]`; `pressures[]`; `structure.segments[]`; `structure.control_bodies[]`; `structure.material_populations[]`; `reinvention.assessment_ref`; `assurance.completeness_projection_ref`.
- **Conditional sections:** `regulation` when a control body or regulation is material; `subsectors` when the declared boundary contains separately analysed segments.
- **Relationships:** resolve EI-002 industry, pressure, Enterprise, Participant and control-body edges; membership uses `industry-membership`.
- **Evidence expectations:** each material assertion resolves evidence/Observation lineage under existing evidence and EI-012 owners.
- **Unknown handling:** common EI-012 rule; an unknown population or economic measure is explicit and remains visible.
- **Contradiction handling:** common EI-012 rule; competing boundary, value or pressure claims remain inspectable.
- **Import validation:** common validation plus unique Industry identity, coherent effective intervals and resolvable assessment/completeness projections.
- **Acceptance criteria:** each mandatory section has governed structured content/state and the overview can be rendered without extracting headings or facts from narrative.

### 4.2 `enterprise-dossier` — Enterprise Dossier profile

- **Purpose:** project one EI-001 Enterprise Twin as decision-grade, inspectable state.
- **Executive experience:** Enterprise Directory and Enterprise Dossier.
- **Mandatory sections:** identity; purpose-and-outcomes; financial; operating-model; leadership-and-governance; workforce; technology-and-data; ecosystem-and-procurement; performance-risk-and-behaviour; transformation; assurance.
- **Mandatory fields:** common fields; `enterprise.twin_id`; `enterprise.name`; `enterprise.aliases[]`; `enterprise.type`; `enterprise.geographies[]`; `purpose.mandate`; `purpose.outcomes[]`; `financial.periods[]`; `operating_model.summary`; `leadership.accountabilities[]`; `workforce.state`; `technology.platforms[]`; `data.state`; `ecosystem.participant_refs[]`; `procurement.object_refs[]`; `performance.measures[]`; `risk.items[]`; `behaviour.assessment_refs[]`; `transformation.programme_refs[]`; `assurance.owner_assessment_ref`.
- **Conditional sections:** `regulation` for regulated Enterprises; `business_units` where units are independently material; `procurement` where external buying is material.
- **Relationships:** Industry membership and EI-002 Enterprise links to Participants, Programmes, Opportunities, executives, contracts and platforms.
- **Evidence expectations:** EI-001 state resolves governed evidence/Observations; periods and effective dates remain explicit.
- **Unknown handling:** common EI-012 rule at section or field scope; missing financial periods are not narrative caveats.
- **Contradiction handling:** common EI-012 rule; conflicting Enterprise state is not silently selected.
- **Import validation:** common validation plus EI-001 identity/version continuity, typed related-object resolution and period/unit checks.
- **Acceptance criteria:** directory identity and all dossier sections project directly from one canonical Enterprise version; no generic attribute-to-section inference is required.

### 4.3 `market-participant` — Market Participant profile

- **Purpose:** project independently governed participant state while keeping parent-relative role on membership/relationship records.
- **Executive experience:** Market Participants.
- **Mandatory sections:** identity; strategy; financial-and-growth-pressure; capabilities; offerings; footprint; delivery-evidence; incumbent-positions; alliances; procurement-routes; strengths-and-vulnerabilities; delivery-risks; likely-moves; assurance.
- **Mandatory fields:** common fields; `participant.twin_id`; `participant.name`; `participant.type`; `strategy.summary`; `financial.pressures[]`; `capability_refs[]`; `offering_refs[]`; `footprint.industry_refs[]`; `footprint.enterprise_refs[]`; `delivery_evidence_refs[]`; `incumbent_positions[]`; `alliance_relationship_refs[]`; `procurement_routes[]`; `assessment.strengths[]`; `assessment.vulnerabilities[]`; `delivery_risks[]`; `likely_moves[]`; `assurance.owner_assessment_ref`.
- **Conditional sections:** `account_presence` only for a declared account context; `regulated_status` when applicable.
- **Relationships:** EI-002 Participant edges and `industry-membership`; contextual role/fit never becomes participant-global state.
- **Evidence expectations:** Market Participant owner and EI-012 rules apply, including proof for capabilities, offerings and delivery claims.
- **Unknown handling:** common EI-012 rule.
- **Contradiction handling:** common EI-012 rule, especially for participant-supplied versus independent claims.
- **Import validation:** common validation plus canonical participant identity, controlled participant type and resolvable capability/offering/evidence objects.
- **Acceptance criteria:** a participant page is fully owner-supplied; membership role and account assessment remain separately governed.

### 4.4 `programme` — Programme object profile

- **Purpose:** project an Enterprise-owned transformation Programme without creating a Programme Twin.
- **Executive experience:** Major Programmes and relevant Enterprise Dossier sections.
- **Mandatory sections:** identity; goal-and-pressure; accountability; funding; scope-and-operating-change; technology-and-data; delivery-ecosystem; procurement; dependencies; risks-and-contradictions; status-and-timing; outcomes; assurance.
- **Mandatory fields:** common fields; `programme.programme_id`; `programme.name`; `programme.enterprise_twin_id`; `goal`; `pressure_refs[]`; `accountable_party_refs[]`; `funding.context`; `scope`; `operating_model_changes[]`; `technology_refs[]`; `data_dependencies[]`; `delivery_participant_refs[]`; `procurement_refs[]`; `dependency_refs[]`; `risk_refs[]`; `status`; `start_date`; `target_end_date`; `horizon`; `expected_outcomes[]`; `assurance.enterprise_assessment_ref`.
- **Conditional sections:** `funding` may be Not Applicable only where no funded delivery exists; `procurement` when external delivery or acquisition is material.
- **Relationships:** resolvable EI-002 links to owning Enterprise, accountable actors, Participants, technologies, contracts and Opportunities; only approved EI-002 vocabulary is permitted.
- **Evidence expectations:** EI-001/EI-002/EI-012 owners apply; status, timing and outcome claims carry current lineage.
- **Unknown handling:** common EI-012 rule.
- **Contradiction handling:** common EI-012 rule; disputed status/timing remains explicit.
- **Import validation:** common validation plus exactly one owning Enterprise, valid dates/horizon and resolvable dependencies.
- **Acceptance criteria:** Major Programmes projects structured programme objects; no Programme Twin identity or lifecycle is asserted.

### 4.5 `opportunity` — Opportunity profile

- **Purpose:** project a governed EI-006/OT-001 Opportunity separately from Industry themes and recommendations.
- **Executive experience:** Opportunities.
- **Mandatory sections:** identity; customer-and-problem; buying-context; value; timing-and-stage; competition; partners; route; risks; lineage-and-uncertainty; assurance.
- **Mandatory fields:** common fields; `opportunity.twin_id`; `opportunity.name`; `customer.enterprise_ref`; `problem`; `buying_context`; `value.case`; `timing.window`; `stage`; `competition.participant_refs[]`; `partner_refs[]`; `route_to_decision`; `risk_refs[]`; `reasoning_lineage_refs[]`; `assurance.owner_assessment_ref`.
- **Conditional sections:** `programme_origin` when a Programme creates or shapes the opportunity; `provider_fit` only when its separate canonical owner has produced it.
- **Relationships:** EI-002/EI-006 approved target, participant and Programme relationships; renderers must not invent missing aliases.
- **Evidence expectations:** EI-006/OT-001 and existing reasoning/evidence owners apply; an Industry theme alone is insufficient.
- **Unknown handling:** common EI-012 rule.
- **Contradiction handling:** common EI-012 rule.
- **Import validation:** common validation plus canonical opportunity identity, customer resolution, allowed stage and complete reasoning lineage where claimed.
- **Acceptance criteria:** each card field is an owned value/state, and no opportunity or recommendation is created by projection.

### 4.6 `reinvention-assessment` — Reinvention Assessment profile

- **Purpose:** project an owner-produced, versioned assessment without redefining FP-012 method or completeness.
- **Executive experience:** Reinvention Timing.
- **Mandatory sections:** identity; assessed-subject; method; inputs; findings; timing; implications; limitations; assurance.
- **Mandatory fields:** common fields; `assessment.assessment_id`; `assessment.subject_ref`; `assessment.subject_version`; `assessment.owner`; `method.ref`; `method.version`; `input_refs[]`; `findings[]`; `timing.current_horizon`; `timing.trigger_refs[]`; `implications[]`; `limitations[]`; `assurance.review_ref`.
- **Conditional sections:** `recommendations` only when an existing recommendation owner and FP-009 reasoning chain authorise them.
- **Relationships:** assessment resolves its Industry/Enterprise subject, inputs, evidence and affected Programme/Opportunity objects through approved relationships.
- **Evidence expectations:** FP-012 is method reference only; underlying subject, evidence and reasoning owners retain authority.
- **Unknown handling:** common EI-012 rule; insufficient timing evidence is Unknown, never a default horizon.
- **Contradiction handling:** common EI-012 rule.
- **Import validation:** common validation plus known method/version, exact subject version and no unowned calculated score.
- **Acceptance criteria:** Flora displays the supplied assessment and limitations without keyword classification or rescoring.

### 4.7 `industry-membership` — Industry Membership profile

- **Purpose:** record why and when a canonical object participates in an Industry Twin composition without copying member state.
- **Executive experience:** Twin Map, Enterprise Directory, Market Participants, Major Programmes, Opportunities and Advanced Inspection.
- **Mandatory sections:** identity; endpoints; inclusion; effective-period; evidence-and-uncertainty; resolution.
- **Mandatory fields:** common fields; `membership.relationship_id`; `membership.industry_twin_id`; `membership.member_id`; `membership.member_type`; `membership.role`; `membership.why_included`; `membership.effective_from`; `membership.effective_to` (nullable); `membership.evidence_refs[]`; `membership.resolution_policy`; `membership.resolved_version`.
- **Conditional sections:** `domain` for a subsector/domain-scoped role; `ended_membership` when `effective_to` is set, including disposition/successor.
- **Relationships:** this is an EI-002 typed, directed Industry-to-member relationship profile. Use only vocabulary accepted by EI-002; this schedule does not introduce a new edge term.
- **Evidence expectations:** the Industry inclusion decision resolves evidence under EI-002/EI-012 rules.
- **Unknown handling:** role or rationale cannot be Unknown for active membership; uncertain inclusion remains candidate and cannot enter a release.
- **Contradiction handling:** conflicting inclusion evidence is linked and prevents active release membership until owner disposition permits it.
- **Import validation:** unique edge ID; canonical endpoints; permitted member type (`enterprise`, `market_participant`, `programme`, `opportunity`, `relationship`); coherent interval; evidence; exact `resolved_version` for a package release.
- **Acceptance criteria:** every directory/map member is selected through one effective membership edge containing member identity, role, inclusion rationale, effective period, evidence and resolved version. Many-to-many membership is permitted; child state remains with its owner.

### 4.8 `industry-release-manifest` — Release Manifest profile

- **Purpose:** make an immutable Industry Twin release reproducible as an exact assembly of governed objects, memberships and relationships.
- **Executive experience:** Twin Map, Research Commission and Advanced Inspection; release context for every screen.
- **Mandatory sections:** release-identity; industry-root; profiles; objects; memberships; relationships; evidence-and-uncertainty-snapshots; validation; supersession-and-rollback.
- **Mandatory fields:** common release identity fields plus every required field in `twin-release-manifest-v2.schema.json`: `release`; `industry_twin`; `profile_versions`; `objects`; `memberships`; `relationships`; `snapshots`; `validation`; `supersession`; `checksums`.
- **Conditional sections:** `rollback_reference` when an approved recovery release exists; embedded/snapshot locator and checksum according to each object's declared content mode.
- **Relationships:** pins exact membership and relationship IDs/versions; it does not duplicate their semantics.
- **Evidence expectations:** pins immutable evidence, Unknown and Contradiction selections; existing owners govern their meaning.
- **Unknown handling:** unresolved required pins fail validation; release limitations may reference governed Unknowns but cannot replace pins.
- **Contradiction handling:** relevant Contradictions are pinned and visible; suppression fails validation.
- **Import validation:** JSON Schema v2, checksums, known profiles, unique IDs, exact object/edge versions, effective membership at release time, snapshot resolution, supersession and rollback target resolution.
- **Acceptance criteria:** the same package resolves the same composition without network reconstruction; import remains staged until separate owner assessment/promotion.

## 5. Executive Workspace projection bindings

Every listed screen is projection only. Where a screen composes profiles, the release manifest supplies the selection; it does not become a new screen-owned model.

| Executive screen | Twin Object Profile | Canonical owner | Projection only |
|---|---|---|---|
| Twin Map | `industry-overview`, `industry-membership`, `industry-release-manifest` | IT-001 composition/inclusion; EI-002 edges; member owners | Yes—render resolved nodes/edges and governed unavailable states. |
| Industry Overview | `industry-overview` | IT-001 | Yes—format owner fields; never synthesize sections. |
| Enterprise Directory | `industry-membership`, `enterprise-dossier` identity | IT-001 inclusion; EI-001 Enterprise | Yes—filter effective Enterprise members. |
| Enterprise Dossier | `enterprise-dossier` | EI-001/EIF-001; EI-002/EI-012 references | Yes—project the resolved Enterprise version. |
| Market Participants | `industry-membership`, `market-participant` | participant specification; IT-001 inclusion; EI-002 | Yes—role comes from membership, state from participant. |
| Major Programmes | `industry-membership`, `programme` | EI-001 Enterprise object; EI-002 links | Yes—no Programme Twin is inferred. |
| Opportunities | `industry-membership`, `opportunity` | EI-006/OT-001; EI-002 | Yes—no card fields or opportunities are invented. |
| Reinvention Timing | `reinvention-assessment` | assessed subject owner; FP-012 method | Yes—no runtime rescoring or keyword classification. |
| Research Gaps | all applicable profiles' validation output | applicable completeness owner; EI-012 | Yes—display deficiencies/Unknowns; do not calculate a replacement completeness model. |
| Research Commission | `industry-release-manifest` plus the profiles commissioned | applicable subject owners; Researcher profile governs production | Yes—emit profile IDs, versions and failed assertions as the work order. |
| Advanced Inspection | `industry-release-manifest` and every referenced object profile | each canonical subject/edge/evidence owner | Yes—show unmodified IDs, versions, lineage and payloads. |

## 6. Composite Industry Twin and package assembly

The Industry Twin owns industry information, economics, pressures, structure, membership decisions and release composition. It does not own Enterprise, Market Participant, Programme or Opportunity state. Enterprise and Participant Twins and Opportunity Twins remain independently governable and versioned by their owners; Programme remains an Enterprise-owned governed object; relationships remain EI-002 governed objects. An Industry release pins resolved versions without transferring ownership. A live view may resolve the latest permitted child version, but a reproducible package always pins exact versions.

A valid Industry Twin package is an assembly of profile-conformant governed Twin Objects, Programme objects, EI-002 relationships/memberships and evidence/EI-012 records selected by an `industry-release-manifest`. Documents, notes, summaries and insights may accompany that assembly as presentation or evidence assets but cannot replace it. Narrative-only completion fails profile validation even if the package envelope is valid.

## 7. Deterministic research production contract

Research commissions name `profile_id`, `profile_version`, object identity/scope, applicability expectations and acceptance assertions. Researchers populate every mandatory section and field with structured governed values, explicit Unknown, or justified Not Applicable; attach approved relationships and evidence/uncertainty references; validate; and package. Researchers do not choose headings, object types, required fields, completeness rules or output shape.

The production loop for every profile is: **select governed profile → populate all mandatory and applicable conditional structure → record Unknown/Not Applicable/Contradictions → resolve evidence and relationships → validate → assemble package → import to candidate state → project**. Topic-led exploration may discover evidence, but its deliverable is the commissioned Twin Objects, not a topic report.

Import rejects a free-form-only deliverable, an unknown profile/version, missing section state, missing applicable field, invalid Not Applicable record, unresolved EI-012/evidence reference, duplicate identity, dangling endpoint, unpinned release member or failed checksum. It reports a deterministic validation failure; neither importer nor Flora repairs the structure.

## 8. Activation traceability

| Profile | Canonical owner | Existing authority reused | Extension in this schedule | Runtime consumer | Research consumer |
|---|---|---|---|---|---|
| Industry Overview | IT-001 | Industry content, boundary and completeness schedules | Deterministic overview binding | Twin Map; Industry Overview | Industry object producer |
| Enterprise Dossier | EI-001/EIF-001 | Enterprise identity/state and foundation | Dossier projection contract | Directory; Dossier | Enterprise object producer |
| Market Participant | Market Participant specification/EI-002 | Participant state and graph identity | Package/projection binding | Market Participants | Participant object producer |
| Programme | EI-001/EI-002 | Enterprise transformation state and graph object | Deterministic object profile; no Twin type | Major Programmes; Dossier | Programme object producer |
| Opportunity | EI-006/OT-001 | Opportunity state/interface | Package/projection binding | Opportunities | Opportunity object producer |
| Reinvention Assessment | subject owner/FP-012 | Subject state and assessment method | Versioned projection binding; no score | Reinvention Timing | Assessment producer |
| Industry Membership | IT-001 inclusion/EI-002 edge | Composite inclusion and relationship semantics | Parent-scoped membership record | Map; directories; inspection | Membership producer |
| Release Manifest | Knowledge Pack/IT-001 | Exchange envelope and Industry release composition | Exact composite pins in schema v2 | All screens/import | Package assembler |

## 9. TEL-001 readiness proof

TEL-001 is neither created nor required by this activation. A Telecommunications researcher receives the eight registered profiles and can immediately: populate Industry boundary/information/economics/pressures/structure; construct Enterprise and Participant Twins under their owners; construct Enterprise-owned Programme objects and governed Opportunities; produce owner assessments; link evidence-backed EI-002 relationships and memberships; pin exact versions in a release; validate; and hand the same structures to import and Flora. Telecommunications terminology and facts populate governed fields but do not alter the profiles. The researcher therefore chooses evidence and supported values, not architecture or output structure, and no further Telecommunications-specific architectural decision is needed before research begins.
