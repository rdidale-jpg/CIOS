# Evidence Semantic Reconciliation & Canonical Deduplication

## Governed boundary finding

ADR-012 keeps the imported candidate as the acceptance boundary and ADR-014
requires inspectable evidence lineage. The import-scoped `SemanticObject` is
therefore the Evidence owner. Key Reports is only a read projection and must
consume the meaning retained on that object. It must not create a competing
report record or infer from an Enterprise-specific identifier.

TEL-001 supplies these exact source records (fields not listed are absent):

| ID | title | publisher | publication date | URL | supported claim | evidence quality | confidence | source reference |
|---|---|---|---|---|---|---|---|---|
| `EV-BT-FY26` | BT Group FY26 results release | BT Group | 2026-05-21 | supplied BT PDF URL | FY26 release provides revenue, adjusted EBITDA, capex and transformation/cash-flow anchors. | Primary source | High | `turn540619search0` |
| `EV-BT-Q1FY27` | BT Group Q1 FY27 trading update | BT Group | 2026-07-23 | supplied BT PDF URL | Q1 FY27 update provides current fibre build/take-up and operational momentum evidence. | Primary source | High | `turn540619search4` |
| `EV-BT-AR26` | BT Group Annual Report 2026 | BT Group | 2026 | supplied BT PDF URL | FY26 revenue £19.654bn, EBITDA £8.2bn, capex £5.127bn, net debt £19.966bn, net financial debt £15.782bn and CFU operating model. | Primary company filing | High | `turn983748view3` |

The source rows supply no separate evidence type, category, source type,
document reference, extract, metadata object, relationship, alias, or lineage
field. The adapter retains the supplied columns in candidate payload and
Evidence attributes and adds import lineage (`record_id`, source file and source
location); it does not lose the title, publisher, dates, URL, claim, quality,
confidence, or source reference. Financial Position reaches these IDs through
the Enterprise dossier's supplied Evidence references. The previous Key Reports
selector used a local conjunction of title terms and a limited quality check.
That parallel recognition logic, rather than TEL-001 or the adapter, caused the
semantic risk. The shared Evidence classifier now recognises annual reports,
results releases, quarterly reports, and trading updates only when supplied
company-primary provenance also agrees. Deterministic date, richness, and
canonical-identity ordering remains in Key Reports.

## Programme identity finding

TEL-001 supplies one Programme, `PROG-BT-TRANSFORMATION`, with programme name
“BT FY30 cost and operating-model transformation” and the summary/strategic
objective “Multi-year cost, simplification, AI/data and cash-generation
programme.” It supplies one owning edge, `REL-W2-001`, from `ENT-BT` to that
Programme. The duplication was not a duplicate source Programme, canonical
Programme, or relationship. It arose when presentation traversals could retain
the same canonical Programme through more than one valid path and when the
Programme statement was also available through factual aggregation.

The relationship projection keys presentation associations by governed
business-object identity, retaining a stable relationship row for explanation.
Major Programmes and Executive Intelligence consume that association. They do
not use displayed text as identity, so genuinely distinct Programme IDs with
the same label remain distinct. Source Programme, Relationship, Evidence and
Opportunity counts are unchanged (13, 308 and 17 respectively).

## Presentation and acceptance contract

The existing factual source value remains inspectable. A shared presentation
translator is used by both Executive Intelligence and the detailed Reinvention
Timing projection, preserving “evidenced or hypothesised” and the unknown budget
while removing the `Ai Pressure:` schema label. Regression acceptance fails when
canonical Evidence identifies company financial reporting but Key Reports is
empty. The same test renders all six governed Enterprise dossiers, verifies
identity-unique Programme output, preserves the external-research empty state,
and protects TEL-001 counts and the unchanged fixture checksum.
