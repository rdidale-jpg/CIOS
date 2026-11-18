# EXPERIENCE-ALIGN-ALL · FLORA’s shared presentation design

Owner review draft for [#680](https://github.com/rdidale-jpg/CIOS/issues/680), under [#679](https://github.com/rdidale-jpg/CIOS/issues/679). Baseline `df475865cc367a28f355c38bc4c23054abe88502`, including accepted #671, #673, #675 and #677. The [Experience Contract](../FLORA-Experience-Contract-v1.0.md) and [owner handoff](../Acceptance-and-Implementation.md) govern this proposal. Approving this design leaves implementation and release for separate owner decisions.

## Decision

Use one shared interaction grammar and different compositions for the questions at each level. Top chooses perspective. Left chooses a subject within it. Main begins with **Facts | FLORA Insight** and keeps the selected scope, subject and reporting period when reading mode changes. Use the existing finite routes, semantic presentation and policy checks. Existing specialist lenses remain deep links or contextual views until each has a verified replacement.

| Perspective | UK | Industry | Enterprise |
| --- | --- | --- | --- |
| **Landscape** | National economic structure, industries and geography, institutional or infrastructure links. | Industry economics, customers, business models, value system and roles. | Entity identity, business lines, markets, customer propositions, economics and disclosed strategy. |
| **Inside** | — | — | Value streams show how work flows. Capabilities show what the enterprise can do, with activities, roles, process, information, systems and dependencies within scope. |
| **Forces** | Six navigable PESTLE dimensions and connections that matter to the economy. | Five Forces as structural mechanisms, with industry PESTLE as a contextual lens. | Conditions on the exact entity, its response and execution dependencies. Market context is linked with explicit applicability. |
| **What's changing?** | Dated national events and materially eligible UK impacts. | Dated industry developments and mechanism or cohort applicability. | Dated entity-specific programmes, milestones, changes and dependencies. |

Landscape is the default for every level. Facts is the default for ordinary arrival, a new subject or a new level. Preserve selections on perspective changes only when the subject is valid in the destination. If a reset is required, the destination title and current selector explain the new scope. Explicit shared Insight links can restore that mode after scope and access validation. Native links retain reload, Back/Forward, no-JavaScript and assistive-technology behavior. The disclosed illustrated scene replaces persistent Left on narrower screens, with the selected label visible while collapsed.

## Top, Left and Main composition

| View | Left selection | Main Facts | Main FLORA Insight |
| --- | --- | --- | --- |
| UK Landscape | Illustrated national map with sector, infrastructure and institution subjects. | Sector composition, basis, year and scope. Separate industry GVA from regional or overlapping measures. | Sector link or comparison, how it works and what the aggregate leaves unresolved. |
| UK Forces | Connected six-dimension PESTLE index. A dimension with gaps remains selectable if it has a meaningful bounded composition. | Dated national conditions, measure or instrument paired with scope. | Mechanism → affected sectors → qualification or alternate explanation. |
| Industry Landscape | Stages or roles on a sector-specific illustration. Banking money flows, Aviation rotations and Technology provisioning use different visual structure. | Value system, participants and exact role definitions. Add selective eligible measures and mark generic pathways Conceptual. | Value capture, differences in economics and constraints for the same selected stage or cohort. |
| Industry Forces | Rivalry, entrants, substitutes, buyers and suppliers connect to the same industry value system. PESTLE appears as a secondary lens. | One force map with chosen condition, evidence and scope. Add evidence coverage where forces differ. | Mechanism, variation across strategic groups and what would alter the interpretation. |
| Enterprise Landscape | Business lines and exchanges laid out by operating economics. | Identity and perimeter, how value is created and captured, selected business and financial facts and disclosed strategy. | Specific margin, funding, utilisation or capacity mechanisms. Distinguish business-line and consolidated evidence. |
| Enterprise Inside | Illustrated business value stream with selectable durable capabilities. The active capability can appear in multiple activities without duplicate ownership. | Value-stream overview at root. Selected capability: activity sequence, roles and systems as supported, dependencies and measured performance where available. | Operating constraint → consequence → uncertainty for the same capability. Where facts are thin, explain the evidence needed to discriminate between plausible mechanisms. |
| Enterprise Forces | Exposure subjects such as funding, input costs, demand, regulation or suppliers, based on entity eligibility. | Force and evidenced entity exposure or disclosed response, scoped by period. | Consequence for the business or capability, alternative explanation and unresolved dependency. |
| Eligible change perspective | Dated selection sorted within a labelled period. Filters for observed/completed, announced/proposed and upcoming. | Event or programme, event/publication/effective dates, status and jurisdiction or reporting entity. | Same event and period, implications and limitations. An announcement is a disclosure of intent until there is eligible evidence of execution. |

**Wireframe.** Wide: subject breadcrumb and perspective navigation across Top, labelled artwork and subject list in Left, then mode control → headline and scope → explanatory visual → selected fact or bounded mechanism → material gap and related subject in Main. Narrow: same Top in a wrapping row, disclosed scene with selected subject, then Main in the same order. Keep the scope statement near the headline, one short caveat beside its item, and required licence attribution in the established location. Pair visual edges with accessible text that identifies their meaning and provenance.

### Sparse evidence and conditional change

For a partially supported view, show a first-line summary of what is supported and the material limitation, then eligible content in its normal composition. Example for an enterprise operations root: “Three fleet activities are described. We cannot yet verify the performance of the recovery process.” On Insight, retain that subject and period and show a concise explanation of the missing link if no interpretation passes. One eligible partial subject may be offered as a nearby link that clearly changes selection. If there is no eligible content, give a plain unavailability state with a route back to the closest supported scope. This wording applies only if it does not disclose a private record's existence. Public unavailability and denied requests retain existing access behavior.

Propose activating a change perspective only where the source owner can return a meaningful, deduplicated, dated subject selection and an explicit historical or current period label. A dated pulse in Landscape or Forces is enough for a sparse example. A time window is a presentation choice for eligible supply without an implied data refresh. Support distinctions among publication, occurrence, effective date, reporting period, retrieval and assessment. Empty or ineligible selections after lifecycle changes return to a supported scope or explain unavailability without publishing stale detail. Agree the threshold per view during review with #681.

## Evidence and operating boundaries

- Facts may present reported, reproducibly calculated or clearly conceptual material through the existing presentation owner. Statements from management remain attributed. FLORA Insight uses eligible dependencies, comparison context and caveats. The existing six statement types remain owned by `intelligence_presentation`.
- `visual_streams` and `visual_panels` own finite scene state and the shared unit of presentation. `reading_views` owns reading-mode composition. `public_routes` and access/security owners retain the exact read path checks. Existing UK macro, Industry, Financial, Enterprise Model, Research and Source adapters own their content, permissions and interpretation limits.
- Keep a single durable Enterprise Model owner under [ADR-002](../../../../architecture/decisions/ADR-002-Enterprise-Model-as-Durable-Memory.md). Release by bounded depth under ADR-009 and preserve package-versus-canonical acceptance under ADR-012. ADR-026 gates enterprise Material Pressure. No insight auto-qualifies or becomes an opportunity. IT-001, EIF-001, EI-001, EGM-001 and INT-MAP-1 retain documented Draft or Review status.
- Links among UK, Industry and Enterprise remain contextual until a source supports applicability at the receiving level. Cross-industry comparisons need a compatible denominator, period and perimeter. Supplier brand, contracting legal entity, workload and company disclosure are distinct assertions.
- Reuse approved illustrations and exact asset bytes. Conceptual visual relationships carry a label and accessible text. Supporting views retain their deep-link and access semantics. Keep proprietary source expression, private workspace data and unapproved evidence out of public HTML, labels, metadata, URLs, exports and caches.

## Review pack

- [Portfolio and owner-feedback audit](scope.md) and [guest route/query sweep](route-audit.csv)
- [Observed and proposed preview index](previews.md)
- [Research handoff and acceptance](handoff.md) for [RESEARCH-ENRICH-ALL #681](https://github.com/rdidale-jpg/CIOS/issues/681)

## Owner-review refinements

- [Enterprise Inside root and linked Forces specifications](operating-model-and-forces.md) define the activity/capability distinction, evidence-qualified visual links and responsive treatment.
- [Perspective readiness and fallback](content-readiness.md) reconciles all 16 existing design requirements against #681's pinned research handoff and defines the threshold for every primary view.
