# Rapid AI Twin Snapshot

Flora now supports an AI-first rapid Financial Intelligence lane for the BT Commercial Digital Twin. The lane uses the existing governed BT source acquisition and the existing OpenAI direct-PDF document-understanding configuration to build a source-backed, verification-pending snapshot inside the standard Financial Intelligence run record.

The snapshot is explicitly separate from trusted Commercial Digital Twin knowledge. It is candidate intelligence only: the rapid stages do not write Evidence, Observations, Enterprise Model attributes, or automatic accepted claims.

## Stage 1 schema

Stage 1 returns `rapid-ai-twin-extraction-v1` with:

- `document_identity`
- `financial_tables`
- `reported_facts`
- `management_commitments`
- `strategic_priorities`
- `transformation_programmes`
- `risks_and_pressures`
- `technology_digital_ai`
- `leadership_and_governance`
- `customer_market_and_regulation`
- `unknowns`
- `extraction_coverage`
- `citation_index`

Each financial table row retains the displayed current and comparator values, page lineage, supporting excerpt, measurement state, accounting basis, ambiguity, confidence, and optional canonical metric mapping. Rows that cannot be mapped remain as reported rows rather than being discarded.

## Stage 2 schema

Stage 2 returns `rapid-ai-twin-synthesis-v1` with:

- `executive_summary`
- `what_changed`
- `why_it_matters`
- `financial_trajectory`
- `enterprise_pressures`
- `transformation_direction`
- `management_execution_assessment`
- `strategic_signals`
- `hypotheses`
- `commercial_themes`
- `likely_executive_stakeholders`
- `contradictions`
- `unknowns`
- `questions_to_investigate`
- `what_not_to_claim`
- `recommended_learning_actions`

Stage 2 receives only the structured Stage 1 extraction and citation index. Signals and Hypotheses must reference valid Stage 1 fact or table-row IDs.

## Product behaviour

After successful BT research, the BT Digital Twin page renders the Rapid AI Twin Snapshot before trusted knowledge, labels it `AI-built snapshot — verification pending`, and explains that structured verification and canonical acceptance have not completed. Financial tables can be downloaded as CSV from persisted Stage 1 rows without rerunning AI.

Partial results remain useful: if synthesis fails, extracted tables are still displayed; invalid rows are removed or marked ambiguous without failing the whole snapshot.
