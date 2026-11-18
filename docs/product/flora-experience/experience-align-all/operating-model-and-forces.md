# Enterprise Inside and Forces visual specification

This refines the [shared contract](README.md) after the [owner review](https://github.com/rdidale-jpg/CIOS/pull/682#issuecomment-6986511433). The examples define visual behavior; sampled statements and conceptual relationships do not establish durable model records.

## Enterprise Inside root

The executive question is **how does this enterprise deliver a customer outcome, and what must it be able to do repeatedly?** Top preserves identity, exact perimeter and perspective. Left preserves the illustrated company context and lets readers select a value stream or a capability. Main opens in Facts at the root rather than selecting a capability on the reader’s behalf.

| Main element | Meaning and selection behavior |
| --- | --- |
| Value stream | A named stakeholder outcome with a trigger, ordered activities and a result. Show hand-offs, optional branches and known organisation or accountable roles at the activity where they matter. |
| Capability hierarchy | A separate ability map, grouped into reusable domains. List parent and child abilities without making their order imply temporal sequence. Use the existing Enterprise Model owner’s IDs where assigned. If no approved mapping exists, label examples Conceptual and keep them in presentation. |
| Activity-to-capability links | Selecting an activity reveals the abilities that enable it; selecting an ability highlights every supported use in the selected stream. Many-to-many links retain their owner, evidence or conceptual status. Shared abilities retain one identity across streams. Provide a native list of linked activity and capability names so the map works without colour, hover or JS. |
| Context and accountability | Show who owns the outcome and who performs or controls the activity when documented. Distinguish accountable roles, teams, named incumbents and partner roles. If unknown, say “Accountable role not disclosed” only if safe to reveal the gap. |
| Capability detail | Show people/skills, process/controls, information/data, systems/technology and evidenced supplier dependencies as distinct concerns. An evidenced supplier link needs exact parties, service/perimeter, dates and an eligible source. Missing links become precise demands. Keep brand collaboration distinct from a contract or workload. |
| Operating and economic measures | Attach each measure to its evidenced scope: activity, capability, business line or Group. Include period and basis, actual versus target, currency/units, and denominator where required. Group deposits, profit or fleet scale can supply context without becoming a performance measure of a capability. |
| Insight at the same selection | Explain a hand-off, constraint, trade-off or dependency using eligible premises. Show the plausible alternative and what would distinguish it. Keep the same map, selection and date. In sparse views, retain a scoped eligible anchor and the missing link. |

**Responsive composition.** On wide screens pair a horizontal stream with a compact capability hierarchy below it; use ordinary links between them. Follow with the selected accountability, enablers and measures. Tablet and mobile stack stream, abilities and detail with selected state and reciprocal text links. No duplication of ability cards across activities. Screen-reader reading order is outcome → activity → linked abilities → detail. Do not encode the link status in line treatment alone.

**Archetypes.** Bank: lead with the customer-service outcome and hand-offs between request handling, servicing and controls; show service management and technology governance as reusable abilities. Lloyds Group’s Envoy disclosure is scoped supporting material; it does not identify an actual bank workflow, contract, performance result or accountable team. Airline: lead with delivering scheduled flying, with allocation, dispatch and recovery; enduring fleet management, operations control and service recovery can span more than one activity. Published fleet scale, where eligible, stays at its reported perimeter. Provider: lead with provisioning capacity and connectivity, with platform operations and interconnection abilities; Equinix is a partial provider profile and site roles, UK contracting entities and actual service performance remain unresolved. Each conceptual example is explicitly marked.

## Forces through mechanisms

Each relationship view has a compact reading order: starting condition → affected economic channel → implementation or exposure, where supported → material gap. Selection controls the anchor, date and links in both modes. Each relationship in the chain has a short verb, scope, period and one of these visible treatments, backed by a text equivalent:

- **Evidenced applicability**: the eligible source supports the stated relationship within the scoped parties and date; causal language requires causal support.
- **Conceptual or conditional mechanism**: labelled separately; the visual may show what could happen under a stated condition.
- **Related context**: use an ordinary link and a short question; no connecting arrow implying proven applicability.
- **Unknown / conflicting**: stop the proven path at the last supported step; show the decisive missing link or competing account beside it. Never display protected detail in the stop label.

| Level | Main composition | Facts → Insight |
| --- | --- | --- |
| UK | Select PESTLE condition; draw a national condition-to-sector channel, then offer a contextual Industry link. Surface the key date and jurisdiction at the condition. | HMT July 2026 designations → UK financial-system oversight is evidenced. Link to Banking's technology stage as relevant context. Shared-service disruption is conditional on reliance and substitute capacity. No enterprise exposure follows from designation. |
| Industry | Put Five Forces around the selected industry value stage. Compare effect by economics of participant/cohort and add a contextual PESTLE lens where pertinent. | Banking buyer power → customer distribution and servicing. Contrast a single-product household with an integrated business bundle as conceptual cases; evidence demands are cohort switching rates, multi-banking and service migration costs. Enterprise links carry no claim of exposure. |
| Enterprise | Use three distinct parts: observed condition, enterprise response, conditional consequence. If no response or exposure is eligible, show the gap at the corresponding position. Link to Inside only for a compatible verified capability or an explicit contextual question. | Lloyds Group → disclosed below-45% cost-to-income ambition for 2030 → effect could depend on cost and income movements. Treat the target as disclosed intent. A funding scale or efficiency target alone does not prove realised savings, supplier dependence or unmet demand. |

**Acceptance.** A reader can identify exactly which part of each chain is sourced, what is conceptual and where a legal-entity link would require more evidence. Remove an eligible premise and verify that the exact dependent relation, annotation and inference disappear while unrelated context remains. Test market, entity, period and jurisdiction mismatches; retained cross-level navigation must never turn them into an enterprise claim. Switching modes preserves the same relation selection, and Back/Forward, keyboard, text zoom and narrow layouts preserve the same meaning.
