# Flora Runtime Increment 1 UK Banking Fixtures

Fixtures are contract-test inputs for the proposed Increment 1 read-only contracts. They use governed UK Banking asset identifiers where available. Runtime IDs, user IDs, correlation IDs, audit IDs, and some Unknown/Contradiction IDs are synthetic and labelled with `synthetic` or `BK-UNK/BK-CON` fixture ranges.

## Source Labels

- Governed corpus: `enterprise-knowledge/banking/MANIFEST.yaml`, `enterprise-knowledge/banking/flora/Banking-Knowledge-Manifest.json`, and `enterprise-knowledge/banking/canonical/banking-research-canonical-objects.json`.
- Supporting docs: `docs/Semantic_Banking_Completion_Report.md` and related Banking runtime completion reports.
- Synthetic values: workspace, audit, ingestion run, correlation, and fixture-only Unknown/Contradiction IDs.

## Expected Validation Outcomes

| Fixture | Schema | Expected outcome | Notes |
|---|---|---|---|
| `valid/focus-object-lloyds.json` | `focus-object-projection-v0.1.schema.json` | pass | Governed asset BK-ENT-001; owner remains `TBD`. |
| `partial/focus-object-incomplete-freshness.json` | `focus-object-projection-v0.1.schema.json` | pass | Incomplete freshness is explicit. |
| `valid/relationship-governed.json` | `relationship-projection-v0.1.schema.json` | pass | Manifest relationship to EGM-001. |
| `partial/relationship-unresolved-target.json` | `relationship-projection-v0.1.schema.json` | pass | Target remains unresolved. |
| `valid/evidence-observation-availability.json` | `evidence-observation-availability-v0.1.schema.json` | pass | Availability counts only, not quality/scoring. |
| `valid/unknown.json` | `unknown-response-v0.1.schema.json` | pass | Governed Unknown fixture. |
| `valid/contradiction.json` | `contradiction-response-v0.1.schema.json` | pass | Preserves both sides. |
| `valid/lineage-complete.json` | `lineage-response-v0.1.schema.json` | pass | Complete Source→Evidence→Observation→Object→Projection path. |
| `partial/lineage-partial.json` | `lineage-response-v0.1.schema.json` | pass | Partial lineage labelled partial. |
| `partial/lineage-access-redacted.json` | `lineage-response-v0.1.schema.json` | pass | Redaction differs from absence. |
| `valid/workspace-state.json` | `workspace-state-v0.1.schema.json` | pass | Non-canonical workspace state. |
| `valid/ingestion-success.json` | `ingestion-report-v0.1.schema.json` | pass | Successful projection ingestion report; not claim acceptance. |
| `invalid/ingestion-identifier-collision.json` | `ingestion-report-v0.1.schema.json` | pass schema, fail expected semantic outcome | Collision report is structurally valid and semantically an ingestion failure. |
| `safe-unavailable/missing-authority-metadata.json` | `safe-unavailable-response-v0.1.schema.json` | pass | Safe unavailable due to missing authority metadata. |
| `safe-unavailable/unresolved-identity.json` | `safe-unavailable-response-v0.1.schema.json` | pass | Safe unavailable due to unresolved identity. |
| `invalid/focus-object-missing-authority.json` | `focus-object-projection-v0.1.schema.json` | fail schema | Required `identity.authority_status` omitted. |

## Contract-Test Notes

Invalid examples are intentionally retained. Implementations should assert their documented failure modes rather than treating all fixtures as valid payloads.
