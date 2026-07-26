# Industry Twin Package Content Inventory and Deficiency Contract

**Status:** Draft Normative controlled schedule to IT-001; WP1-002 proposal
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
