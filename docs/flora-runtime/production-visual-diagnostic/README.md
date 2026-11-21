# FLORA production visual reality check

Inspected on 19 November 2026. Approved Banking release, fetched GitHub main and the SHA independently reported by the public Render deployment endpoint all agree on `2757e459f90fc4e1156180acf5f7ed9a40c292d9`. Public health returned HTTP 200. The deployment identity is application-reported. Render control-plane metadata and the owner's authenticated browser session were unavailable for this review. [Release issue #678](https://github.com/rdidale-jpg/CIOS/issues/678) · [Live deployment metadata](https://flora-current.onrender.com/deployment) · [Exact-main validation](https://github.com/rdidale-jpg/CIOS/actions/runs/44407873433)

## Screen-by-screen gap

| Screen | Implemented and visible in the public experience | Design gap and evidence boundary |
| --- | --- | --- |
| UK Landscape | Illustrated subject navigation and a selected national context | Artwork establishes place. Main needs to show how national conditions reach economic actors and industries. Keep jurisdiction and dated measures visible. |
| UK Forces | Six selectable PESTLE dimensions. Political and social coverage is partial. | Explain condition → transmission → affected population. Shared policy material cannot supply a second independent evidential link. |
| Banking Landscape | Painterly industry landscape with customers, funding, payments and technology stages. Main changes composition by stage. | The selected stage rarely connects visibly to adjacent stages. Keep Nationwide financial scope intact and distinguish payments principal, settlement and service economics. |
| Banking Forces | Five selectable Porter forces with mechanism-oriented prose and scoped context | A force needs a competitive mechanism and observable evidence, with the strength or direction withheld where evidence is partial. Monetary policy does not establish switching. |
| Lloyds Landscape | Group-level funding and performance context with a financial visual | Give the executive a coherent economic system linking deposits, lending, income, cost and impairment. Public Group totals do not allocate economics to business lines. |
| Lloyds Inside | Receive / Resolve / Review customer-service example alongside capability context and separate Envoy disclosure | A conceptual task sequence occupies the place of the enterprise operating model. The disclosure does not establish workflow, accountable role, workload or supplier contract. |
| Lloyds Forces | Enterprise pressure and response framing | Generic labels and prose obscure the mechanism and scope. Draw conditional consequences explicitly and avoid joining disclosures as if they prove a strategic response. |
| NatWest | Legal-bank complaint/service evidence, accompanied by a conceptual banking model | A useful service signal with narrow scope. No verified group operating model, service workflow, or group-wide financial inference follows. |
| HSBC | Legal-bank complaint/service evidence, accompanied by a conceptual banking model | Use the legal bank perimeter. International Group economics or an actual operating chain require separate evidence. |
| Nationwide | Mutual model framing and signed financial bridges with Group/Society boundaries | Strongest quantified comparison in the cohort. Give the mutual economics and signed bridges room to carry the explanation. Avoid interpreting Group measures as Society-only. |
| Starling | Challenger framing and legal-bank service context | Distinguish bank operating economics from platform economics. An association with Engine does not establish a legal bank contract or product economics. |
| Bank of England | Central-bank institutional roles and system context | Monetary and settlement functions need a separate institutional grammar. Retail-bank journeys and commercial unit economics do not transfer. |

The comparator is the owner-accepted illustration and composition direction in VP-1 and the subsequent experience and operating-model contracts. VP-1 showed scene-specific composition and a working-space hierarchy around a meaningful comparative chart. Its static preview predated the accepted reading-mode interaction. The release sequence delivered the shared Facts-first interaction, Banking art, differentiated stage compositions and a partial enterprise cohort. It did not deliver full economic and operating models for each enterprise. [VP-1 #631](https://github.com/rdidale-jpg/CIOS/pull/631) · [Facts-first #671](https://github.com/rdidale-jpg/CIOS/pull/671) · [Banking illustration #675](https://github.com/rdidale-jpg/CIOS/pull/675) · [Banking depth #677](https://github.com/rdidale-jpg/CIOS/pull/677) · [Global design #682](https://github.com/rdidale-jpg/CIOS/pull/682) · [Banking cohort #692](https://github.com/rdidale-jpg/CIOS/pull/692)

## Root causes

1. **Composition.** The shared shell and navigation work, but the Main view often promotes prose, short lists and stacked panels to carry analysis that the contract assigns to visual structure. The same plate can look sparse on a wide viewport because its internal composition contains too little spatial information. Lloyds Inside's three-step sequence originates in the source composition.
2. **Responsive and print suppression.** The shared stylesheet switches Left to a collapsed native disclosure at widths up to 999 CSS pixels. iPad portrait and phone therefore start with a much less illustrated experience than the wide view. Print CSS hides Left and skyline explicitly. This is independent of whether the artwork is shipped. Owner PDF tooling and native Safari were outside the observed browser run.
3. **Reading-mode depth.** Accessible selection and mode preservation are in place. Several Main views change copy without changing the explanatory task or visual emphasis. Facts should locate a scoped measure or relationship. Insight should make its transmission, trade-off or uncertainty easier to reason about for the same selection.
4. **Evidence and coverage.** Group and regulated-entity facts establish specific anchors. They leave major commercial questions open at line-of-business, value-stream, accountable-role and dependency level. A presentation defect cannot establish the missing facts. The cohort can demonstrate distinct institutional models without suggesting these are complete enterprise twins.

[Capture and validation inventory](validation.md) · [Lloyds reconstruction proposal](lloyds-recovery.md)

## Trace to code and ownership

| Concern | Source at inspected main | What it explains |
| --- | --- | --- |
| Illustration and responsive behaviour | [Visual shell](../../../cios/applications/flora/visual_panels.py) · [Panel CSS](../../../cios/applications/flora/visual_stream_assets/panels.css) | Wide and compact variants use the same scene family. Breakpoint and print omission are presentation decisions. |
| Inside and Forces | [Experience compositions](../../../cios/applications/flora/experience_composition.py) | Source composition supplies Receive / Resolve / Review and the evidence separation. UK and Banking forces use numbered explanatory content. |
| Facts and Insight | [Reading views](../../../cios/applications/flora/reading_views.py) · [View routing](../../../cios/applications/flora/visual_streams.py) | Shared mode control and route state are reusable. Explanation within a perspective can evolve independently. |
| Banking and cohort | [Banking ecosystem](../../../cios/applications/flora/banking_ecosystem.py) · [Banking cohort](../../../cios/applications/flora/banking_cohort.py) | Use source-governed quantitative and conceptual components already in Banking. The five new selections address different perimeters and institution types at uneven depth. |
| Evidence and models | [Enterprise ownership](../../../architecture/decisions/ADR-002-Enterprise-Model-as-Durable-Memory.md) · [Progressive assurance](../../../architecture/decisions/ADR-009-Progressive-Assurance-for-Commercial-Digital-Twins.md) · [Canonical acceptance](../../../architecture/decisions/ADR-012-Governed-Blueprint-Package-Import-and-Canonical-Acceptance-Boundary.md) · [Material pressure](../../../architecture/decisions/ADR-026-Material-Pressure-Qualification-and-Ownership.md) | Preserve the canonical owner, evidence maturity and controlled promotion. Keep illustrated causal mechanisms distinct from qualified commercial pressure. |

[Experience Contract v1.0](../../product/flora-experience/FLORA-Experience-Contract-v1.0.md) · [Operating model and Forces specification](../../product/flora-experience/experience-align-all/operating-model-and-forces.md)

### Representative differences

- The accepted Lloyds prototype puts the comparative deposit chart in the editorial workspace. The live Landscape retains the two bars and adds headline measures. The unresolved design gap is the absence of a visual explanation tying customer funding to earning assets, costs and profitability.
- The live Lloyds Inside pair retains the same service sequence, capabilities and context headings in both reading modes. Insight adds a conceptual mechanism section. This improves interpretation without giving the mechanism its own visual emphasis.
- The live UK Forces pair exposes the PESTLE chooser and the contextual chain, with an additional sector-mechanism section in Insight. The same vertical list grammar also appears in Lloyds Forces, despite the change from national transmission to enterprise pressure and response.
- The narrow-screen disclosure is consistent with VP-1. Accepting that navigation pattern leaves the current Main visuals responsible for carrying meaning when Left is closed.
- Opening Lloyds Inside on mobile reveals the illustrated room with broad labels for Financial performance, Technology & data and Leadership Agenda. Those links support discovery, while the Main customer-request example answers a narrower question. The demonstrator should visually connect an Inside selection to a relevant activity or capability and keep cross-perspective navigation explicit.
