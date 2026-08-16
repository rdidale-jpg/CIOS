# Evidence Utilisation & Key Reports

## Architecture-first finding

**Architectural intent.** Evidence and its provenance remain governed import objects; Canonical Factual Projection owns Enterprise facts, Financial Intelligence owns financial extraction, owner assessments own completeness, and Research Requirements consume those owner states. Unknowns and Contradictions remain separate canonical object families.

**Implemented runtime capability.** The candidate Semantic Twin already retains Evidence title, publisher, publication date, governed URL, supported claim/extract, source-file lineage, and Enterprise association. The Enterprise dossier already consumes Canonical Factual Projection and links to Advanced Inspection. This change adds only a read-only report-selection and navigation projection over those owners.

**Current programme state.** TEL-001 remains candidate state and requires no fresh import. Its Evidence register supplies company financial reporting for several Enterprises. For BT, it supplies EV-BT-AR26, EV-BT-FY26, EV-BT-Q1FY27 and the richer duplicate-date EV-BT-Q1FY27-W4. It supplies no BT evidence explicitly typed or described as analyst, broker, equity research, market research, or market analysis.

## TEL-001 BT report metadata audit

| Evidence | Title | Publisher | Publication / period | Type / quality | Governed URL | Extract / summary | Lineage |
|---|---|---|---|---|---|---|---|
| EV-BT-AR26 | BT Group Annual Report 2026 | BT Group | 2026 | Primary company filing | supplied | supported claim with revenue, EBITDA, capex, debt and CFU operating model | Evidence register record and source reference supplied |
| EV-BT-FY26 | BT Group FY26 results release | BT Group | 21 May 2026 | Primary source | supplied | supported claim describing financial and transformation anchors | Evidence register record and source reference supplied |
| EV-BT-Q1FY27 | BT Group Q1 FY27 trading update | BT Group | 23 July 2026 | Primary source | supplied | supported claim describing fibre and operational momentum | Evidence register record and source reference supplied |
| EV-BT-Q1FY27-W4 | BT Group Q1 FY27 trading update | BT Group | 23 July 2026 / Q1 FY27 | Primary financial report / Investor results PDF | supplied | supported claim plus extracted summary | Evidence register record and source reference supplied |

The supplied records do not contain an author/analyst, source filename for an embedded report, document access restriction, or an internally embedded original document. Their lineage points to the Evidence register row; their URL points to the externally governed source. The fixture itself is unchanged.

## Behavioural boundary

Latest selection orders supplied publication metadata, then prefers the richer governed duplicate-date record and finally uses immutable Evidence identity as a deterministic tie-break. Only explicit HTTP(S) URLs from Evidence are rendered. Company reporting and external views are independently classified from existing Evidence type/quality/title semantics; neither can become the other. A missing report, an extract-only report, a referenced report without source/extract, and a directly linked report render as different states.

An unresolved Organisation Overview requirement remains unresolved. Where linked governed Evidence exists, the dossier now says that further canonical extraction is possible rather than treating an empty presentation field as proof that Evidence is absent. It does not mine or promote the report at runtime.
