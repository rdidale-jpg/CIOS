# TEL-001 Executive Experience root-cause matrix

## Investigation boundary

The immutable package, candidate staging repository, semantic Twin, Canonical
Factual Projection, relationship fields, executive view model and final HTML
were traced in that order.  Flora's existing Blueprint Import lifecycle remains
the lifecycle owner; the semantic Twin and Canonical Factual Projection remain
the read owners.  Presentation does not persist facts or relationships.

| Defect | Expected truth | Source truth | Runtime truth | Rendered truth | First divergence | Canonical owner | Root cause | Required correction |
|---|---|---|---|---|---|---|---|---|
| Import instruction | A live current change with passing acceptance is testable even without optional telemetry | Package and change marker are present | Optional deployment fields may be absent | Previously answered “No” | Status logic | Deployment status | Optional telemetry was treated as a gate | Treat it as incomplete verification, not a test blocker |
| Human review | Chief Architect review is distinct from promotion | Import is staged and unpromoted | Existing Review stage and append-only human review record are available | Fictional governance-pending language appeared | Presentation/status logic | Blueprint Import lifecycle | Candidate state was used as review state | Display import, review, assessment, promotion and recommendation separately |
| Twin Map grammar | 1 industry, 6 enterprises, 17 participants, 13 programmes, 17 opportunities | Those families are supplied | Counts reconcile in candidate staging | Technical nouns and mechanical plurals appeared | Presentation | Candidate staging | Generic type labels leaked into executive copy | Use family-specific plain-language nouns and plural forms |
| Industry hierarchy | Structured overview, metrics, structure, economics, landscape, implications and uncertainty | Nested industry fields are supplied | CFP retains nested fields | Generic formatted source blocks dominated | View model/presentation | Canonical Factual Projection | A general record inspector was used as the information hierarchy | Compose named executive sections from the existing projection |
| Enterprise dossier facts | Each assessment section repeats the relevant known facts and residual deficiency | Enterprise facts are supplied but incomplete | CFP retains those facts | Sections redirected readers to facts “above” | Presentation | Canonical Factual Projection | Gap helper emitted a location, not factual content | Render concise CFP values in each assessed section |
| Enterprise associations | Only owner or explicitly related Programmes/Opportunities | Explicit subject, affected-organisation and canonical references exist | Semantic objects retain these fields | Earlier broad record references leaked unrelated objects; later output could omit explicit links | Relationship query | Source relationship/candidate semantic read model | Page and diagnostics used different or overly broad association predicates | Share the strict canonical association predicate and its explanation with diagnostics |
| Enterprise labels | The same dossier pattern works for all six enterprises | Six distinct enterprises exist | Shared dossier renderer is used | BT-specific headings and pills appeared on every dossier | Presentation | Enterprise factual projection | Regression copy was hard-coded to the exemplar | Use neutral owned/explicit-relationship copy and the rendered enterprise identity |
| Participants | Human name is primary; ID is disclosed | Names and IDs are supplied | Both survive import | IDs/internal read-model labels dominated | View model/presentation | Candidate factual object | Generic technical card identity was primary | Prefer display name and collapse lineage |
| Programmes | Thirteen readable business records | 13 supplied | 13 staged and projected | Hypothesis/technical wording obscured facts | Presentation | Candidate programme object | Assessment vocabulary replaced factual identity | Present programme facts and separate assessment status |
| Opportunities | Preserve H1/H2/H3/Award/Framework and nested facts | 17 opportunities with supplied categories and structures | Fields survive in semantic payload | Categories collapsed; mappings printed like dictionaries | View model/presentation | Candidate opportunity object | Generic scalar formatter and default type | Structured value renderer and source-backed category grouping |
| Reinvention | Candidate facts and canonical assessments have explicit dispositions | Seven relevant assessment/pressure records are supplied | Seven records survive candidate projection | A bare zero implied no intelligence | Status logic/presentation | Candidate objects and assessment owner | Canonical-assessment count was substituted for factual inventory | Show supplied, retained, requires-review, assessed and rejected dispositions separately |
| Research Gaps | Residual deficiencies only | Facts, Unknowns and Contradictions coexist | CFP and owner assessments distinguish them | Whole profiles were recommissioned or facts called absent | Research-gap view model | Research requirements owner + CFP | Presence and owner assessment were collapsed | Render coverage, residual deficiency, reason, action and exact state from shared owners |
| Explore | Business collections precede technical/supporting records | Business and lineage families are distinct | Collection classifier distinguishes them | Generic runtime families dominated | Presentation | Semantic Twin collection classifier | Runtime genericity was mistaken for business priority | Order business collections first and collapse support records |
| Advanced Inspection | Reconciliation and page anomalies precede traces | Counts, references and projection state are queryable | Diagnostics can consume shared association rule | Trace detail preceded the outcome | Presentation/diagnostics | Pilot diagnostics | Object-inspector hierarchy | Lead with reconciliation, anomaly filters and collapsed traces |

## Route trace

All routes originate in the package registry and candidate staging summary.
`assemble_semantic_twin` creates the read-only semantic view;
`CanonicalFactualProjection` and the semantic executive record view model supply
facts; `executive_workspace_page` selects the route and shared presentation
helpers; `_page` supplies the existing Flora shell. Review remains rendered by
the Blueprint Import Review route rather than a new workflow.

## BT Group relationship reconciliation

The strict query found two of thirteen Programmes and three of seventeen
Opportunities related to BT Group. The remaining twenty-five records were
omitted. Every displayed association is supplied through subject,
affected-organisation or direct canonical reference data; no narrative or
title matching is used.

| Object | Object type | Expected BT relationship | Runtime relationship | Displayed on BT | Correct? | Reason |
|---|---|---|---|---|---|---|
| PROG-BT-VERIZON-JV | Programme | Explicit BT association | Retained and queryable | Yes | Yes | Supplied canonical association |
| PROG-BT-TRANSFORMATION | Programme | Explicit BT association | Retained and queryable | Yes | Yes | Supplied canonical association |
| OPP-BT-AI-ENGINEERING | Opportunity | Explicit BT association | Retained and queryable | Yes | Yes | Supplied canonical association |
| OPP-BT-AIOPS | Opportunity | Explicit BT association | Retained and queryable | Yes | Yes | Supplied canonical association |
| OPP-BT-VERIZON-JV-INTEGRATION | Opportunity | Explicit BT association | Retained and queryable | Yes | Yes | Supplied canonical association |
| Other 11 Programmes | Programme | None | No permitted BT association | No | Yes | Belongs to another enterprise |
| Other 14 Opportunities | Opportunity | None | No permitted BT association | No | Yes | Belongs to another enterprise |

## Expected-truth reconciliation

The test-only oracle is `tests/fixtures/tel001_expected_truth.json`. Direct
package staging reconciled 648 accepted candidate objects: one Industry, six
Enterprises, 17 Market Participants, 13 Programmes, 17 Opportunities, 92
Evidence records, 30 Unknowns, 11 Contradictions, 308 Relationships, 50
Memberships, 95 Refresh Triggers, one Release Manifest and seven AI
reinvention-assessment records. The six enterprise identities are BT Group,
CityFibre, Openreach, TalkTalk, Virgin Media O2 and VodafoneThree.

All seven reinvention records were retained. They are presented as seven
candidate pressure/reinvention facts requiring owner review/classification;
no record was rejected, silently discarded or represented as a completed
canonical timing assessment.
