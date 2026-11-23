# Lloyds vertical demonstrator

Use the existing Lloyds subject, perspective and mode owners. Keep the original portrait and accepted Top, Left and Main shell. Top holds the existing perspectives. Left anchors the scene and exposes selectable topics, with direct access to the topic selector on narrow screens. Main places the explanatory graphic immediately after the reading mode and puts citations, definitions and optional detail below it. Give each perspective a distinct visual grammar.

| Perspective | Facts default | FLORA Insight on the same selection | Admission boundary |
| --- | --- | --- | --- |
| Landscape | Build a balance-sheet and economic flow. Put deposits and other funding on one side, conceptual lending and deployment on the other, and the scoped reported Group performance below (£6.6bn statutory pretax profit for the nine months to 30 September 2026). Use existing 30 September 2026 (£502.8bn) and 31 December 2025 (£496.5bn) Group deposit points and label them as stocks. Show income, operating costs, impairment and capital as separate concepts with scoped approved figures only. | Highlight how funding cost and asset pricing affect spread, why deposit growth cannot establish funding cost, and how impairment and capital headroom can constrain lending. Explain the competing paths without attributing them to a specific reported outcome. | Do not reconcile a flow from two deposit stocks, allocate Group profit to business lines, or turn a Group efficiency target into an attained ratio. Place Lloyds Bank plc service evidence in a separately labelled perimeter. |
| Inside | Give the operating system two axes. Horizontal value streams show selected conceptual credit origination/servicing and customer support journeys. Vertical durable capabilities show risk assessment, servicing, customer support and control as a conceptual map. Put organisation, people, process, information and technology in a selectable detail layer. Place the evidenced Group Envoy platform-controls disclosure in a separate context block. | Focus on the selected activity-to-capability relationship. Explain alternative hand-offs, control checks, operational resilience or service/cost trade-offs as conditional mechanisms. The operating-system view should explain how capabilities can support more than one journey. | Leave operating ownership and real sequences unverified unless directly supported. No connector from Envoy to the journey and no inferred bank contract, workload or supplier assignment. Publish named accountability only from eligible exact-scope evidence. |
| Forces | Build a pressure → transmission → response canvas. Anchor in scoped published measures and commitments. Keep industry policy and company facts visibly distinct. Show risks and unobserved links with a distinct line style and a short explanatory label. | Trace a selected force through its transmission path to a conditional implication. Examples include rate changes reaching net interest income through asymmetric repricing, and SRE/control design shaping potential disruption exposure. Draw alternatives and show the evidence required to compare them. | Rate policy cannot establish Lloyds exposure or response. The Group efficiency target cannot establish realised performance. A disclosed control does not establish reduced outages or exclusive dependence. |

Use text labels and line styles alongside colour for reported facts, conceptual paths, supported contextual links and unknowns. Show the decision-relevant graphic and two to three anchors before drill-through. Use stacked, readable relationships on phones. Ensure users can reach Main and reselect its topic without opening a large image. Print Main's scope, relationships and source labels legibly using the existing print surface.

## Reuse and remaining evidence

- `visual_panels.py` and `visual_stream_assets/panels.css` own the shell, layout, artwork and existing financial chart. Use their native links and responsive components.
- `reading_views.py` and `experience_composition.py` own reading and contextual presentation. Reuse the same current subject and period through mode switches. Use Banking's stage layouts as a pattern for different compositions, not a common data model.
- Reuse eligible Lloyds Group deposit and performance facts and separately scoped legal-bank service facts. Keep the Group performance reporting period and measurement basis visible. Use the existing financial and source resolution owners.
- The Wave 3 Lloyds dossier is candidate material. Quantified business-line economics, leadership/accountability links, real customer hand-offs, capital allocation by business line, effective supplier relationships and quantified resilience outcomes need exact-scope eligibility and evidence. Continue to withhold ineligible inputs.
- Keep canonical identity and evidence rights in existing owners. A new graph, registry, source permission, inferred identity or reasoning pipeline would expand the recovery without solving the visual issue.

## Smallest next implementation

One presentation-only Lloyds vertical slice on the existing route. Reuse approved anchors to deliver one linked economic visual, a two-journey conceptual Inside matrix with an independent evidenced disclosure, and one traversable Forces mechanism. Scope new styling to Lloyds and preserve the existing shell, artwork, deep links, reading controls and all neighbouring routes. An evidence owner can review the scope labels in parallel with design. Deeper operating and commercial claims can follow as evidence becomes eligible.

| Acceptance area | Pass and negative cases |
| --- | --- |
| Commercial comprehension | An executive can explain how deposit stocks differ from profit flows, which operating links Lloyds disclosed, and what missing evidence prevents a force being attributed to Lloyds. Quick review in both modes. |
| Same subject | Facts defaults. Enter Insight and return with perspective, subject, period and entity preserved. Reload and Back/Forward restore selection. |
| Sources and identity | Withdraw a source and verify dependent figures and assertions disappear. Prove separation of Group and Lloyds Bank plc, period and stock/flow units, conceptual sequence and actual operation, and Envoy context and supplier linkage. |
| Visual and interaction | Compare actual wide desktop, iPad landscape/portrait and 390/320px mobile captures. Exercise keyboard, touch, native focus, 200% text, no JavaScript and printable Main. Check legibility without relying on colour or a hover state. |
| Regression | Run full security and regression for the implementation head. Verify existing routes and output for Banking, Nationwide, easyJet, UK and Technology. Review read-only behaviour and rights under guest and authorised test contexts. |

Keep the slice reversible as a single presentation commit or bounded PR. Before release, revert or drop the slice and rerun the existing gate. After any future authorised release, reverting that presentation commit restores the previous composition without a data migration. Production rollback requires separate owner authorisation.

## Main composition at a glance

```text
Landscape                     Inside                          Forces
Funding stocks │ Deployment   Value streams across the top    Pressure → Transmission
       ↓        │ (conceptual)       ↓ selected activity               ↓
Income → Costs / Impairment    Capability lanes and hand-offs   Observed response or unknown
       ↓                       Context: Group controls          ↓ conditional consequence
Scoped reported performance    (separate disclosure)           Assess with named evidence gap
```

Pair each selected graphic with its evidence panel. In Facts, foreground measurement and the stated relationship. In Insight, retain the selected anchor and highlight the mechanism and the reason it could move in either direction.
