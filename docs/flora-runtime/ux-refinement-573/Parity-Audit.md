# Banking / Aviation / available-view UX parity audit

Baseline: `854a783b3c5f83d6ee3604f49a76772529b7339a`. This is an audit and preservation check, not an authorisation to redesign other sectors.

## Measured preservation

The automated browser check compares Banking, Aviation, Lloyds, easyJet and Macro at desktop 1440×1050, iPad landscape 1024×768 and phone 390×844. All 15 captures are byte-identical between baseline and candidate, with no document overflow. Exact hashes and observed UI inventory are retained in `previews/Browser-Results.json`.

| Area | Technology refinement | Banking | Aviation |
| --- | --- | --- | --- |
| Primary industry visual | Approved local artwork, eight persistent district labels | Existing two SVG visuals preserved | Existing two SVG visuals preserved |
| Phone navigation | Eight numbered image targets plus visible name key | Existing sector-specific text/visual fallback preserved | Existing sector-specific text/visual fallback preserved |
| Participant comparison | Compact table with scoped UK metrics, blanks and source detail | No equivalent comparison table in the audited industry entry | No equivalent comparison table in the audited industry entry |
| Enterprise depth | NVIDIA financials, priorities, pressures, ecosystem, programmes and hypotheses | Lloyds has substantive existing content and two tables; presentation remains diagram-led | easyJet retains existing findings and opportunities; no table in the audited enterprise entry |
| Default diagnostic prose | Removed from default Technology views; retained in specialist context | Automated visible-language scan flags diagnostic/qualification wording | Automated visible-language scan flags diagnostic/qualification wording |
| Pipeline | Explicitly labelled tab-local preview; existing protected live destination remains available | Existing `/flora/sales/pipeline` destination retained | Existing `/flora/sales/pipeline` destination retained |
| Security and provenance | Existing owners retained | Existing owners retained | Existing owners retained |

The diagnostic-language scan is a review aid, not an automatic judgement that every matched word is inappropriate. Source/qualification context can be important. The screenshots and actual flow should guide a later owner-reviewed refinement.

## Follow-up recommendations

1. Apply the same **display contract**, not Technology's eight-district taxonomy, to sector-specific data: clean sourced values, explicit EST only with a defensible basis, and empty unavailable fields.
2. Review each sector's illustration and its own constituent actors before changing navigation. Aviation's terminal, airline, cargo, maintenance and air-traffic roles differ from Banking's institutions and financial flows.
3. Reuse the small comparison/presentation patterns only after each sector's participant population, measurement scope and provenance are mapped. Do not repurpose UK group figures as entity/market figures.
4. Move routine diagnostic prose into the existing specialist views while preserving operational failures, access denials and qualification boundaries. Maintain source and temporal distinctions internally.
5. Preserve the existing authenticated live-Pipeline capture owner. Technology's illustrative tab state does not authorise an alternative sales database or automatic capture.

No Banking, Aviation, Lloyds, easyJet, Macro or live-Pipeline implementation is redesigned in this sprint. Uniform UX parity is **not** claimed. Physical-device and assistive-technology acceptance remain outstanding.
