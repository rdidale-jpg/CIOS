# ADR-026: Material Pressure Qualification and Ownership

**Identifier:** ADR-026  
**Version:** 1.0  
**Document Type:** Architecture Decision Record  
**Authority Classification:** Accepted canonical ADR  
**Status:** Accepted  
**Owner:** Rob / CIOS  
**Date:** 2026-08-16  
**Durable-model owner:** EI-001 — Enterprise Model Specification (Draft document; ownership boundary only)  
**Runtime implementation:** Authorised for a subsequent sprint; not implemented by this decision

## Status

Accepted.

Repository ADR conventions permit an architecture commission to record an Accepted decision. Human acceptance is not an additional gate for this decision. EI-001 remains Draft: this ADR, rather than EI-001's document status, is the accepted authority for the qualification semantics below.

## Architectural question

What authorises CIOS to transform governed Enterprise Intelligence into a qualified Material Pressure?

## Context and authority

ADR-002 accepts the Enterprise Model as durable memory. ADR-014 accepts evidence-governed, Enterprise-bounded interpretation and safe failure. ADR-024 accepts a hybrid runtime in which generated outputs remain candidates until deterministic validation. They constrain qualification but did not define it. EI-001 describes the intended durable Enterprise Model and is Draft; EI-003, EI-004 and EI-012 are Draft; EIF-001 is Review; FEIR-001 and EIRP-001 are Proposed. CURRENT-PROGRAMME-STATE and WP-011 are programme/runtime baselines, not domain-object acceptance decisions.

Before this decision there was therefore no Accepted Material Pressure qualification authority. This ADR is that authority. It establishes EI-001 as the single durable-model owner without accepting EI-001 wholesale or creating a subsystem. ADR-024 remains the runtime reasoning owner and EI-004 remains the intended Commercial Reasoning owner, subordinate to accepted ADR boundaries while EI-004 is Draft.

## Decision

The proposed six-gate contract is **AMENDED and ACCEPTED**. Its core gates are retained, but:

1. identity/singularity is made an explicit deterministic acceptance rule;
2. commercial significance is removed from the durable qualification gate;
3. Unknown, Contradiction and rejection outcomes are made deterministic; and
4. lifecycle is kept evidence/timing-based rather than introducing a new fixed enumeration.

A runtime may create or update a qualified Material Pressure only when every core gate below passes. `UNKNOWN` is permitted only for non-core detail explicitly listed below. A failed gate yields `NOT QUALIFIED`; a core contradiction yields `UNRESOLVED`. Both outcomes preserve the governed source facts and assurance records.

## Canonical object and reasoning boundary

A durable Material Pressure contains only:

- stable pressure identity and the affected Enterprise;
- an evidence-grounded condition acting on that Enterprise;
- an explainable material Enterprise consequence;
- source Observation/factual-object and Evidence lineage;
- explicit Unknowns and Contradictions; and
- effective, observed and resolution/supersession timing where established.

EI-001 owns this durable object. ADR-026 owns qualification. ADR-024's governed hybrid runtime may assess candidates and enforce this contract. It must not silently amend canonical source facts or infer from public model knowledge.

Commercial Reasoning may derive why the pressure matters to a seller, possible Opportunity or pursuit relevance, monitoring significance and validation needs. Those derived statements retain their own lineage and status and are not fields of durable Material Pressure truth. For example, evidence may establish that debt and capex intensity constrain investment flexibility; it does not establish that cash-benefit propositions are preferable. The latter is derived commercial reasoning.

## Qualification contract

### Gate 1 — eligible governed input

The candidate must be one or more governed Enterprise Observations or canonical factual objects owned by an authorised source, with inspectable supporting Evidence. The candidate records its source object type and stable identifier, Evidence identifiers, observed/effective dates, truth/status labels, confidence and freshness where supplied. Narrative resemblance, a model prior, a keyword, a renderer field or an ungoverned assertion does not pass.

### Gate 2 — Enterprise applicability

Evidence must support that the condition acts on the identified canonical Enterprise and relevant monitored scope. Group/subsidiary applicability follows governed identity and relationship semantics; it is not assumed. Industry evidence or another Enterprise's condition is context only unless governed evidence establishes applicability to the target Enterprise.

### Gate 3 — pressure semantics

The candidate must express a condition, constraint, demand or forcing mechanism acting upon the Enterprise. A fact, metric, negative adjective, Programme, Opportunity, Procurement, strategic priority or market observation alone does not pass. The qualifying explanation must state the condition and how it acts; it may constrain, accelerate, redirect, increase urgency, change investment, or affect operations, strategy or regulatory response.

### Gate 4 — identity and singularity

The minimum identity basis is:

`canonical Enterprise + pressure condition/concept + affected domain/context + applicable time/lifecycle context (where supported)`.

Identity uses governed Enterprise identity and evidence-grounded semantic reasoning. It must not rely solely on string equality, fuzzy matching, keywords, Evidence IDs or source-object IDs. Multiple Evidence records or differently worded Observations about one underlying condition strengthen or contradict one Material Pressure; they do not automatically create several objects. A candidate matching an extant identity updates that object and lineage or is rejected as a duplicate. Compound candidates are separated only when evidence supports distinct underlying conditions.

### Gate 5 — materiality

Evidence must establish at least one explainable, non-trivial Enterprise consequence in an accepted domain: strategic, financial/economic, operational, regulatory/obligation, investment, or programme/change. No numeric score is required. A negative condition, large-looking number, priority label or generic importance assertion alone is insufficient. The qualification record identifies the consequence domain and supporting evidence.

### Gate 6 — Enterprise consequence and assurance

The record must state an Enterprise consequence supported by governed intelligence and preserve the qualification path from source objects through Evidence to condition, materiality and consequence. Unsupported consequence inference is prohibited. Supporting and counter-evidence, Unknowns, Contradictions, confidence/freshness labels and timing are retained. Commercial consequence is not required and must not be manufactured here.

## Unknown

A qualified Pressure may retain `Unknown` for severity, financial magnitude, precise timing, duration, owner, response or resolution path when existence, Enterprise applicability, pressure semantics, materiality and an Enterprise consequence have passed. Unknown core existence, applicability, pressure semantics, materiality or consequence does not pass qualification: the candidate remains unqualified or unresolved. Unknown is never filled from general knowledge for convenience.

## Contradiction

Contradiction is always visible and linked to supporting and counter-evidence.

- If conflict concerns severity, magnitude, precise timing, duration, owner, response or resolution while existence and at least one material consequence remain supported, the object may be **qualified with contradiction**.
- If conflict leaves existence, direction as a pressure, Enterprise applicability, materiality or the existence of an Enterprise consequence unresolved, the outcome is **UNRESOLVED**, not qualified.
- If governed evidence resolves the core conflict sufficiently to pass every core gate, qualification may proceed while retaining the historical contradiction and resolution lineage.

No runtime may silently choose the more convenient source.

## Lifecycle

No mandatory `EMERGING / ACTIVE / REDUCING / RESOLVED / SUPERSEDED` enumeration is introduced. The minimum durable lifecycle is governed observed/effective timing, current qualification status, and resolution or supersession relationship when evidence establishes one. A runtime may present equivalent labels only as derived views. Resolution does not erase the object or its lineage, and new evidence may update, weaken, resolve, supersede or re-qualify it through the same gates.

## Deterministic rejection

Qualification is rejected when the candidate is only a keyword match; a generic industry assumption; another Enterprise's pressure without applicable evidence; a financial metric without pressure semantics; only a Programme, Opportunity, Procurement or strategic priority; unsupported by Evidence; without material Enterprise consequence; duplicative of an existing Pressure; or core-contradictory without sufficient resolution. Weak single evidence is not rejected merely for being singular, but it fails wherever its governance, confidence or content cannot support existence, applicability, materiality and consequence.

Rejection removes or changes no underlying governed fact. The qualification assessment records the failed gate and may preserve an Unknown, Contradiction or validation need outside the durable Pressure object.

## Domain boundaries

**Material Pressure is not Opportunity.** It may be an input to governed Opportunity reasoning but never automatically creates an Opportunity. Existing Opportunity governance remains authoritative.

**Material Pressure is not Procurement.** It may persist for years without procurement. Pressure alone never establishes budget, buyer, tender, procurement route or award timing.

A Material Pressure may explain why an existing Watchpoint matters. It does not automatically create a Watchpoint; existing Watchpoint governance controls that derivation.

Programme delivery, a strategic priority, an Opportunity and a Procurement may supply evidence of a condition, but none qualifies by object type alone. Dossier renderers and Key Reports are views, not owners.

## Conceptual validation against unchanged TEL-001

This validation uses governed TEL-001 dossier claims and Evidence IDs as candidates; it does not accept the dossier's existing `pressures` strings merely because they occupy that field.

| Enterprise | Input fact / Observation | Evidence | Applicability | Pressure semantics | Materiality | Enterprise consequence | Lineage | Qualified | Reason |
|---|---|---|---|---|---|---|---|---|---|
| BT Group | FY26 revenue, EBITDA, capex and debt anchors together with continued fibre investment | EV-BT-AR26; EV-BT-FY26; EV-BT-Q1FY27 | PASS | PASS | PASS | PASS | PASS | YES | The combined evidence supports a BT-specific debt/capex condition constraining investment flexibility; the raw revenue or debt metric alone would not qualify. |
| CityFibre | £170m revenue, £29m adjusted EBITDA, £2.3bn financing and network build/take-up context | EV-CF-2025; EV-CITYFIBRE-FY25 | PASS | PASS | PASS | PASS | PASS | YES | Financing and monetisation conditions act on continued network investment; Project Gigabit entries alone remain Programme facts. |
| Openreach | FTTP build/take-up alongside regulated access and constrained local competitive response | EV-OR-FTTP26; EV-OF-TAR26; EV-BT-CMA-NEXFIBRE-RESPONSE26 | PASS | PASS | PASS | PASS | PASS | YES | Regulation and fibre economics constrain pricing/monetisation; the build target alone is a Programme/priority, not a Pressure. |
| TalkTalk | Refinancing facilities and reported revenue/customer pressure | EV-TT-REFINANCE; EV-TALKTALK-CH-2025; EV-TALKTALK-FT-FUNDING26 | PASS | PASS | UNKNOWN | UNKNOWN | PASS | UNRESOLVED | Lineage exists and the financing condition is plausible, but the available mixed primary/secondary dossier evidence does not yet establish an adequately supported material consequence. |
| Virgin Media O2 | FY25 operating/investment anchors plus secondary debt concerns | EV-VMO2-FY25; EV-VMO2-Q4FY25-PDF; EV-VMO2-FT-DEBT26 | PASS | PASS | UNKNOWN | UNKNOWN | PASS | UNRESOLVED | Secondary debt context cannot by itself establish the asserted material consequence; signed RAN spend is investment/Programme evidence, not automatic pressure. |
| VodafoneThree | Completed merger, binding remedies and £11bn network investment commitment | EV-VT-MERGER; EV-CMA-VT-CLOSE25; EV-VT-5GSA26 | PASS | PASS | PASS | PASS | PASS | YES | Binding integration, wholesale and investment obligations act on the Enterprise and have evidenced operational, regulatory and investment consequence; a supplier selection alone would not qualify. |

### BT discrimination examples

| Candidate | Outcome | Reason |
|---|---|---|
| Revenue pressure | NO | A revenue figure or decline label alone is a metric; qualify only with evidence of a condition and material consequence. |
| Debt/capex intensity | YES | The combined FY26/Q1 evidence establishes an Enterprise-specific investment-flexibility constraint. |
| Regulated pricing constraints | YES | Governed regulatory and BT/Openreach evidence establishes applicability and monetisation/competitive consequence. |
| Enterprise complexity | NO | Generic descriptor without a bounded condition and supported consequence. |
| PSTN/copper migration execution | UNRESOLVED | Programme existence is evidenced, but the candidate needs evidence of a material forcing condition/consequence rather than the Programme alone. |
| Cost base | NO | Metric/domain label only. |
| Legacy estate | NO | Asset/challenge label only; no supported material consequence in the candidate as stated. |
| Debt financing costs | UNRESOLVED | Debt is evidenced; the distinct financing-cost condition and consequence are not established by the cited anchors alone. |
| Competitive broadband/mobile pricing | NO | Generic market pressure unless evidence establishes BT applicability, mechanism and consequence. |

## Falsification and safe failure

| Attack candidate | Required result | Contract result |
|---|---|---|
| Financial metric only | reject | Gate 3/5 fail. |
| Generic telecom competitive pressure | reject | Gates 2, 3 and 5 fail. |
| Competitor's pressure applied to target | reject | Gate 2 fails. |
| Programme only | reject | Gate 3 fails. |
| Opportunity only | reject | Gate 3 and domain boundary fail. |
| Procurement only | reject | Gate 3 and domain boundary fail. |
| Strategic priority only | reject | Gate 3/5 fail. |
| Weak single Observation | reject when core support is insufficient | Gates 1, 5 or 6 fail; otherwise singularity alone is not disqualifying. |
| Unsupported consequence | reject | Gate 6 fails. |
| Duplicate Evidence/restatement | update existing or reject duplicate | Gate 4 prevents a second object. |
| Core contradiction | unresolved | Core contradiction rule prevents qualification. |

The contract therefore discriminates rather than populates and fails safely.

## Consequences

- One accepted qualification authority and one durable-model owner now exist.
- A subsequent runtime sprint is authorised to implement these semantics without making another architecture decision.
- The implementation owner is the Flora governed reasoning/validation runtime under ADR-024, writing accepted durable state to EI-001's Enterprise Model boundary.
- Implementation must expose pass/fail/unresolved gates, singularity handling and complete lineage; it must not alter Opportunity, Procurement or Watchpoint governance.
- No runtime, projection, dossier, Evidence or TEL-001 fixture behaviour changes in this ADR sprint. No fresh import is required.

## Supersession and reconciliation

This ADR does not supersede ADR-002, ADR-014 or ADR-024. It narrows their application to Material Pressure qualification. It normatively replaces the non-normative six-gate annex in `TEL-001-Material-Pressure-Governance-Assessment.md`. EI-001 remains Draft and is reconciled only to point to this accepted authority.
