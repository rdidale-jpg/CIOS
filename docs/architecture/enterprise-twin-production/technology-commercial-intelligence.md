# Technology estate, contracts and leadership

**Proposed information and review requirements.** Apply the [factual envelope](factual-contract.md) to selected records. Distinguish a vendor product from an enterprise installation and a named person from an enduring role. Record effective intervals and assertion status per edge, exact source revision and locator, direction and endpoints, scope, contradictions and counterevidence. Keep inferred links in investigation with their basis and validation trigger. Suppress a dependent output when its qualifying support is withdrawn.

## Relationship and ownership map

These are semantic requirements over existing relationships and references. [EI‑002](../../../architecture/enterprise-intelligence/volume-1-enterprise-modelling/EI-002-Enterprise-Knowledge-Graph.md) remains Draft. Use a compatible existing contract only where its predicate and scope fit. Otherwise retain a traceable evidence reference in the owning review material and raise any storage gap separately. This proposal authorises no new graph predicates, objects, grants or EI‑002 edits.

| Required relationship | Owner and qualifying evidence |
| --- | --- |
| Enterprise → operates → Application | Estate identifies a verified installation and legal operating perimeter. A parent, licence holder or vendor logo establishes no operation. |
| Application → supports → Business Capability | Estate references operating model capability/process and evidenced scope. Map conceptual flows separately. |
| Application → depends on → Platform | Estate references the host/infrastructure record and evidence of actual functional dependency. An endorsed platform alone supplies no dependency. |
| Supplier → provides → Contracted Service | Supplier records the evidenced operating role, with a link to the contract or procurement award. Distinguish primary, subcontracted and announced roles. |
| Contract → covers → Application/Capability | Contract records actual legal scope, with an explicit link to the relevant estate/capability record. |
| Contract → expires/renews on → Date | Contract retains original and amended terms, notice dates and option status. Only exercised renewals enter as confirmed renewals. Estimated dates remain hypotheses. |
| Executive Role → accountable for → Function | Leadership retains scoped mandate, effective dates, delegation and evidenced decision rights. Workforce retains aggregate reporting structure. |
| Programme → changes → Application/Capability | Programme records change scope, target and milestones, linked to estate evidence for actual deployment or retirement. |
| Procurement → seeks → Goods/Services | Procurement records buyer, scoped notice, stage and actual route. Contract retains award obligations, while general chronology references the originating event. |
| Material Pressure → affects → Enterprise/Capability | ADR‑026 qualification supplies the Enterprise and supported scope; EI‑001 retains the durable ownership boundary. Capability is a scope reference where supported. |

## Inputs to ADR‑026

The [accepted ADR‑026](../../../architecture/decisions/ADR-026-Material-Pressure-Qualification-and-Ownership.md) governs every candidate. Record stable identifiers for governed Observations or canonical facts, supporting Evidence, observed/effective dates, status, freshness and counterevidence. Verify (1) eligible governed input, (2) exact Enterprise applicability, (3) a forcing condition and how it acts, (4) identity and singularity against existing conditions, (5) materiality in an accepted domain, and (6) a traceable supported Enterprise consequence. Duplicate conditions update the existing assessment or are rejected. Missing core input means NOT QUALIFIED; a core contradiction means UNRESOLVED. Non-core uncertainty stays visible under the ADR.

| Candidate | Minimum evidence package before assessment |
| --- | --- |
| Technology obsolescence | Verified live estate and critical workload, evidenced incompatibility or loss of viable maintenance, and consequence for the service or required investment. Check replacements and existing mitigation. |
| Support-end deadline | Authoritative notice for exact deployed version, tier and date, local coverage/extensions and affected capability. Show how remaining options and lead times affect continuity or controls. |
| Migration or transformation pressure | Programme scope and timed gates, estate cutover dependencies and Workforce capacity or scarce skills where relevant. Show the forcing dependency and evidenced delivery, continuity or investment consequence. |
| Supplier concentration or exit risk | Verified supplier and contract exposures across material services, evidence of actual substitutability, rights and transition dependencies, and measurable or otherwise evidenced consequence of disruption. |
| Contract renewal or recompetition | Confirmed term, notice and option status, affected scope and constraint on continuation or transition. Keep extension, actual procurement notice and inferred date separate. |
| Operating cost or productivity | Comparable Financial/operating baselines, cost definition and Workforce/technology perimeter, evidenced driver and effect on decisions or service. Retain management targets separately. |
| Cyber or resilience exposure | Scoped controls/incident/test evidence, affected assets and service tolerances, mitigation and residual operational or regulatory consequence. |
| Regulatory deadline | Final instrument and dated obligation, exact legal-entity applicability, remaining implementation/control gap and evidenced consequence. Keep proposal and final rule distinct. |
| Delivery failure or programme risk | Dated plan and actual variance, evidenced dependency and accountable role, recovery or fallback status and impact on service, obligation or committed change. |

A time-critical “burning platform” is an optional editorial interpretation after qualification. Require a credible decision window or binding date, adverse consequence of delay, evidence the current response or feasible alternatives cannot remove the time constraint, and a dated review trigger. Consider support exceptions, alternative suppliers, extensions and fallback plans. If timing or mitigation is Unknown, report qualified pressure at its supported scope and withhold the urgency label. Authority, budget, buying access, Opportunity and Watchpoint follow their existing separate owners.

## Analytical input traceability and visual destinations

Each row extends the [catalogue](analytical-models.md) minimum for the scoped question. An unsupported join stays Unknown and limits the model verdict. No row produces a procurement or opportunity by inference.

| Model | Traceable inputs and required distinction | Destination |
| --- | --- | --- |
| Operating and Capability | Role mandate and Workforce function → capability → application → platform; qualify responsibility and dependencies individually. | Inside operating processes and organisation with role drill-through. |
| Technology and Supplier Ecosystem | Verified installation and host → supplier delivery → contract scope, including incumbent/transition status. Keep partnership and subcontract service distinct. | Inside application and supplier views, linked to Landscape divisions. |
| Value Chain | Capability/process hand-off → supported application → contracted service where evidenced. Test alternate channels. | Inside service lane and Landscape strategic exposure. |
| Enterprise Economics | Join scoped estate and contract costs to eligible Financial period, entity, unit and measurement basis. Separate contract ceiling, recognised cost and modelled change. | Landscape Economics with scoped cost inspection. |
| SWOT/TOWS and VRIO | Use lifecycle, control, evidenced capability/outcomes and real alternatives. Rights and adoption do not show rarity, value capture or competitive advantage alone. | Landscape strengths and alternatives with supporting or opposing evidence. |
| Risk and Material Pressure | Dated lifecycle and regulation, resilience, workforce readiness, costs, programme and accountable role as applicable. Apply all ADR‑026 gates. | Forces with evidenced scope, deadline status and uncertainty. |
| Transformation Timeline | Programme milestones, role changes, version changes, amendments or actual handover. Keep announcement and occurrence distinct. | Inside timeline and verified Forces events. |
| Strategic Options | Evidence of actual alternatives, option/notice constraints, service baseline, mandate and eligible costs. Separate trade-offs from buying intent. | Landscape decision context and relevant Inside evidence. |
| AI and Technology Disruption | Tie verified adoption/readiness to named capability, dependencies and observed effects. Verify competitor offering and overlap separately. | Forces disruption and competitive signals. |

Use the existing depth and Facts/Insight contract. An optional commercial event timeline distinguishes contractual dates, options, planned events and observed procurement. Drill-through reveals scoped contract and role evidence, verified milestones and decision rights at the relevant depth. Keep workflow, permissions and administrative metadata in existing inspection. Collapse distracting chronology by default and preserve specific unknowns that could change the decision.
