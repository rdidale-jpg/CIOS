# Bounded zero-touch research assurance

Baseline `ec6380a72369db99d1e7198271fff28d286dae37` has the same tree as the approved #719 head. Its [post-merge CI](https://github.com/rdidale-jpg/CIOS/actions/runs/45146804101) passed. The [evaluation criteria](criteria.md) were committed before execution.

## Assurance and authority

1. Existing discovery and acquisition read the bounded original HTML. The body extractor supplies a specific source digest, paragraph and sentence for each candidate. The new screen checks that digest against the acquired bytes, the dated review window and atomicity. A usable issuer excerpt receives attributed-only status.
2. The deterministic core evaluates one resolved field at a time. The caller must supply trusted, separately bound entity, event, definition, period and original document evidence. Matching sources need exact active revisions and a dated observation within the current 90-day proof window. Values and units must agree. Scope excludes different entities, periods and definitions from the comparison. Different units in the same field remain a conflict until resolved. Unsupported or ambiguous inputs remain outside verified output.
3. Two direct records can support verification if their bound publishers and origins are both distinct. Syndicated copies or repeated reports cannot supply a second origin. An official register or publisher notice can establish the narrower fact it directly records. It gives no independent proof of the broader issuer claim. A later same-origin direct record replaces the older one only through an explicit, trusted replacement link with valid chronology. The audit retains competing or superseded evidence.
4. Factual decisions cannot grant Source reuse, publication, workspace access, execution or Pipeline authority. The handoff preview independently requires an exact isolated workspace, audience and statement binding with Source, workspace and execution gates. The test harness then uses the existing Blueprint staging, reviewer decisions, dry-run plan, approval and execution service. The test fixture allows exactly the Microsoft announcement. Its audit rationale includes the deterministic decision ID. No production policy is created.
5. Native views continue to load only accepted Evidence under existing access and Source lifecycle rules. Verified commercial readings can supply an investigation question. The module does not infer buyer intent, an opportunity, budget or expected deal value. An issuer-only or held decision supplies no confirmed commercial conclusion.

The normalized assurance core is not yet a verifier for arbitrary prose. Its trusted binding input is a boundary: body extraction cannot create that binding simply by naming a company or using a confident verb. New eligible evidence can be re-evaluated by the same function and can change attribution to verified. Loss of a required revision immediately removes eligibility on re-evaluation. The feature adds no autonomous fetching to resolve a conflict, no scheduler, no standing Source grant, and no live approval path. In the existing workflow, source comparison and atomicity are quality gates. Source use, audience and scope, Blueprint approval/execution and Pipeline actions remain genuine authority decisions.

## Reproduce

```sh
printf '%s\n' '["lloyds-banking-group-plc","bt-group-plc","arm-holdings-plc","easyjet-plc"]' >/tmp/flora-assurance-commission.json
python -m tools.research.initial_factory /tmp/flora-assurance-commission.json --discover --extract-body /tmp/flora-assurance-new
python -m tools.research.factory_assurance_proof
CIOS_VERIFIED_ROUTE_OUTPUT=/tmp/flora-assurance-routes python -m pytest -q \
  tests/test_flora_assurance.py tests/test_flora_verified_factory.py
PYTHONPATH=. python docs/research/initial-factory/verified/browser.py /tmp/flora-assurance-routes --output /tmp/flora-assurance-previews
```

The [decision trail](decision-trail.json) records the controlled outcomes and the four existing fixture assessments. The [body screen manifest](body-screen.json) retains IDs, precise source references and decisions while omitting publisher prose. The [register proof](register-proof.json) records the two added official sources and the six expected and observed values.

## Measured results and limits

| Check | Observed result | Reference scope |
| --- | ---: | --- |
| Structured extraction precision | 6/6 reported fields | Tesco and National Grid company number, legal name and status |
| Structured extraction recall | 6/6 expected fields | Same two independently selected registry records and their labels |
| Controlled scoped decision correctness | 15/15 | Predetermined outcomes in the test corpus, including 3 deliberately verified controls |
| Unsupported verified outcome rate | 0/17 | 12 non-verified controlled decisions plus 5 invalid date, entity, unit or inference controls |
| Material conflict detection | 2/2 | Contradictory same-scope sources and ambiguous assertions in one revision |
| Explicit supersession outcomes | 2/2 | Accepted chronological replacement and rejected same-day replacement |
| Isolated publication gate | 8/8 | One allowed exact scope and seven deny cases |
| Live newsroom screening | 6 attributed, 4 withheld, 0 verified out of 10 | Four issuers. A screen result does not measure whether the publisher assertion is true |

The controlled cases include syndication, one publisher relaying several releases, duplicates, withdrawal, changed revisions, stale and future dates, subsidiaries, reporting periods and definitions. These hand-selected cases establish program behaviour. They do not estimate newsroom accuracy. The register labels are taken from the public statutory record, and the two sources were outside the development newsroom sample. They establish exact transcription only. No independently adjudicated body corpus exists here for newsroom precision, recall, party resolution, event matching or corroboration rates. There is no statistical confidence interval for the purposive 2-record sample or the designed controls. The main errors visible in the live screen were compound excerpts and qualified milestones, and the accepted source example narrows what its official notice can establish.

## Six-enterprise proof and native views

- **Lloyds, BT and easyJet**. The assurance engine retained their prior statements as issuer-only. The native comparisons for these enterprises use the previous manually accepted fixture records as the visual baseline. They do not demonstrate new automatic acceptance.
- **Arm**. Microsoft’s own Azure notice establishes that it announced Cobalt 200 availability. The Arm article traces to the same announcement. The test grants isolated eligibility for the exact Microsoft publication event only. Existing Blueprint permissions, execution and native ACLs still apply. Repeat execution is a no-op. Removing the Microsoft revision removes factual eligibility and the native card.
- **Tesco and National Grid**. The existing public register lane confirmed statutory identities and registered Active status. These are offline scope and transcription proofs. They add no native claims, live canonical rows or commercial relationships.

| Enterprise | Desktop | iPad portrait | iPad landscape |
| --- | --- | --- | --- |
| Lloyds | [Desktop](previews/lloyds-banking-group-plc-route-desktop.jpg) | [Portrait](previews/lloyds-banking-group-plc-route-ipad-portrait.jpg) | [Landscape](previews/lloyds-banking-group-plc-route-ipad-landscape.jpg) |
| BT | [Desktop](previews/bt-group-plc-route-desktop.jpg) | [Portrait](previews/bt-group-plc-route-ipad-portrait.jpg) | [Landscape](previews/bt-group-plc-route-ipad-landscape.jpg) |
| Arm | [Desktop](previews/arm-holdings-plc-route-desktop.jpg) | [Portrait](previews/arm-holdings-plc-route-ipad-portrait.jpg) | [Landscape](previews/arm-holdings-plc-route-ipad-landscape.jpg) |
| easyJet | [Desktop](previews/easyjet-plc-route-desktop.jpg) | [Portrait](previews/easyjet-plc-route-ipad-portrait.jpg) | [Landscape](previews/easyjet-plc-route-ipad-landscape.jpg) |

The compact cards preserve the same seller language and artwork. Evidence opens separately and the primary surface carries no research scores or approval terminology. The most useful test scenario is the distinction between a published launch announcement and actual adoption. It gives a seller a specific question about coverage and readiness. A collapsed summary earns the first screen space. The trade-off remains two actions to reach evidence and a longer wrap on some tablet layouts. The proof uses Chromium and simulated iPad sizes.

## Readiness and owner decisions

Factory v1.0 remains incomplete. The routine user can rely on conservative withholding for this bounded prototype. Generalised extraction, automatic entity resolution and independent corroboration have not been demonstrated with a representative accuracy corpus. Trusted evidence binding and material conflict decisions still need owner-governed preparation. The isolated fixture demonstrates a separate authority policy but grants no standing permission.

Before considering production, the owner must approve representative independent accuracy criteria, the exact Source use and lifecycle channel, intended audience, verified workspace and scoped approver/executor, and any standing policy and operating schedule. Lloyds §2, §5 and the existing BT, easyJet and Financial boundaries remain in place. No live publication, permission expansion, scheduler, production deployment or Pipeline action is included.
