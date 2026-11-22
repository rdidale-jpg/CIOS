# Record-level review and acceptance batches

All rows are candidates. The research asset ID BK-ENT-001 is carried through the package for traceability. Runtime normalisation to bk-ent-001 is distinct from the Group name’s normalised value lloyds-banking-group-plc. Canonical owner and exact workspace are unresolved. The owner must confirm a scoped binding before receipt or planning.

| Record | Batch and disposition | Subject and dated meaning | Source references |
| --- | --- | --- | --- |
| F01 | A · eligible for consideration | Lloyds Bank plc · 2026-11-22 · register-observed | ch-bank, ch-psc |
| F02 | A · eligible for consideration | HBOS plc · 2026-11-22 · register-observed | ch-hbos |
| F03A | B · corrected eligible for consideration | Scottish Widows Limited · 2026-11-22 · register-observed | ch-widows |
| F03B | B · corrected eligible for consideration | Scottish Widows Limited · 1996-05-02 to 2015-12-31 · registered-name-history | ch-widows |
| F04 | A · eligible for consideration | Scottish Widows Master Trust · 2026-11-22 · regulator-observed | tpr, tpr-transfer |
| F05A | D · source decision | Lloyds Banking Group plc, Business & Commercial Banking · 2026-02 · reported-role-start | lbg-exco |
| F05B | D · source decision | Lloyds Banking Group plc, SME banking · 2026-08-12 · reported-appointment-announcement | lbg-morton |
| F06A | D · source decision | Lloyds Banking Group plc, Corporate & Institutional Banking · 2026-03 · reported-role-start | lbg-exco |
| F06B | D · source decision | Lloyds Banking Group plc, CIB Transaction Banking · 2026-11-18 · reported-appointment-announcement | lbg-condon |
| F07 | D · source decision | Lloyds Banking Group plc, Connected Finance · 2026-10 · issuer-reported | lbg-exco |
| F08A | D · source decision | Lloyds Banking Group plc, IP&I · 2026-11-22 · role-roster-observation | lbg-exco |
| F08B | D · source decision | Lloyds Banking Group plc, investment management remit · 2025-12-10 · reported-appointment-announcement | lbg-fit |
| F08C | D · source decision | Scottish Widows, issuer role label · 2026-11-22 · role-roster-observation | lbg-exco |
| F09 | D · source decision | Lloyds Banking Group plc · 2026-09 · issuer-reported | lbg-exco |
| F10A | D · source decision | Lloyds Banking Group plc · 2026 · issuer-plan | lbg-skills |
| F10B | D · source decision | Lloyds Banking Group plc · 2026-06-22 · issuer-plan | lbg-skills |
| F11A | D · source decision | Lloyds Banking Group plc, colleague productivity estate · 2026-06-04 · reported-rollout-scope | lbg-ms, ms-e7 |
| F11B | D · source decision | Lloyds Banking Group plc, GitHub Copilot · 2026-06-04 · supplier-reported-agreement | ms-e7 |
| F12 | D · source decision | Lloyds Banking Group plc, sourcing process · 2026-11-22 · issuer-reported | lbg-ariba |
| F13 | D · source decision | Scottish Widows protection claims and underwriting · 2025-06-05 · historical-trial | lbg-sprout |
| F14A | B · corrected eligible for consideration | Scottish Widows, FCA participant label · 2026-04-21 · retrospective-citation | fca-ai |
| F14B | B · corrected eligible for consideration | Lloyds Banking Group (Scottish Widows), FCA participant label · 2026-04-21 · selection-announcement | fca-ai |
| F15 | A · eligible for consideration | Scottish Widows, FCA participant name · 2026-07-22 · regulator-reported | fca-sandbox |
| F16 | A · eligible for consideration | Lloyds Bank plc as supplier · 2026-11-22 · buyer-channel-observed | gca |
| F17 | D · further evidence | Lloyds Bank as supplier to Gloucestershire County Council · 2021-10 · historical-award | glos |
| F18 | A · eligible for consideration | Great Britain SME business current account survey, Lloyds Monzo and Starling brands · 2025-07 to 2026-06 · independent-survey | ipsos, starling |
| F19 | C · external owner and identity review | UK motor finance regime, external context · 2026-10-26 · external-scheduled | fca-motor-firms |
| F20 | C · external owner and identity review | UK financial services AI, external context · 2026-10-20 · external-observed | fca-aaa |
| F21A | C · external owner and identity review | GoCardless, external UK fintech context · 2026-04-21 · external-selection-announcement | fca-ai |
| F21B | C · external owner and identity review | TrueLayer, external UK fintech context · 2026-07-22 · external-selection-announcement | fca-sandbox |
| F22 | A · eligible for consideration | Lloyds Banking Group plc, colleague software · 2026-06-04 · supplier-reported | ms-e7 |
| F23A | C · external owner and identity review | UK monetary policy, external context · 2026-09-17 · external-policy-decision | boe-sep |
| F23B | C · external owner and identity review | UK monetary policy, external context · 2026-11-04 · external-policy-decision | boe-nov |
| F24 | C · external owner and identity review | PRA-supervised firms; external context · 2025-12 · external-observed | pra-climate |
| F25 | D · source decision | Lloyds Banking Group plc · 2026-08-20 · issuer-plan | lbg-invest |
| F26A | D · source decision | Lloyds Banking Group plc, CEO role · 2026-11-22 · role-roster-observation | lbg-exco |
| F26B | D · source decision | Lloyds Banking Group plc, CFO role · 2026-11-22 · role-roster-observation | lbg-exco |
| F26C | D · source decision | Lloyds Banking Group plc, COO role · 2026-11-22 · role-roster-observation | lbg-exco |
| F26D | D · source decision | Lloyds Banking Group plc, committee-level reporting · 2026-11-22 · reporting-line-observation | lbg-exco |
| F27 | D · source decision | Lloyds Banking Group plc third-party sourcing · 2026-11-22 · issuer-reported | lbg-sourcing |

## Batch gates

- **A · Initial Evidence review.** Check exact scope, Source operation/audience/version and lifecycle. Resolve F04 to the scheme label and treat 6 May as the guidance event. Keep F15 at the regulator’s participant label and F16 in the bank-as-supplier listing scope. F18 is the GB SME survey wave, separate from complaint counts. F22 is Microsoft’s June GitHub Copilot statement, separate from the existing Microsoft 365 Copilot counts.
- **B · Corrected Evidence review.** Independently check the two registered-identity/history records and two FCA Live Testing assertions. Confirm the exact participant identity for any legal-entity attribution.
- **C · External context.** Route to the existing external Industry or regulatory context owner. No promotion into Lloyds-specific findings from sector facts alone.
- **D · Source or Evidence hold.** Preserve F07/F09/F12/F13/F25/F27. Split issuer records retain the need for operation-specific review. For F17 retain the original council decision reference and obtain accessible primary evidence through the existing owner. Do not rely on indexed or cached text, a mirror, or inferred renewal.
- **E · Relationships.** Review separately after Evidence and governed endpoint resolution. See [endpoint register](endpoints.md). R03 is withheld as a graph candidate. F04 preserves the authorisation observation.

## Existing ownership and duplication

For each eligible row the authorised reviewer must compare exact subject, statement, period and version against the scoped canonical store. Use map-existing or duplicate where equivalent, or resolve a versioned update or proposed create through existing review. Group/bank perimeter and known executive roles may already exist. F11A/F11B/F22 share announcement lineage and should reference one matching Source revision where they rely on the same Microsoft page. The repository overlap check is not a live canonical-store check.

Lloyds §2 remains held where applicable, §5 direct PDF links remain deferred, and ADR‑027 remains Proposed. Applicable Source holds continue through withdrawal or supersession. Each fact is conservatively held for reassessment when a linked source becomes unusable, and each dependent edge inherits that hold.

Any later approval and execution under ADR‑012 requires authenticated and correctly scoped existing candidate.promote authority and a verified Lloyds workspace, subject and plan. This package does not submit, approve or execute a plan.
