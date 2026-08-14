# TEL-001 Relationship Truth Executive Summary

## Decision
**SAFE TO MERGE.** The unchanged governed package contains at least one explicit Enterprise → Programme and Enterprise → Opportunity Relationship object for each of the six Enterprises. Flora’s reported zero/zero Enterprise pages therefore lose valid source associations. The commercially obvious BT/Verizon Programme is a separate producer/package gap: it has no explicit Relationship endpoint at all. This audit changes only documentation and Import Twin operational-panel presentation.

## Plain-English answers

1. **Does TEL-001 contain Enterprise → Programme relationships?** Yes. Every required Enterprise has at least one direct, explicit typed Relationship to a Programme.
2. **Does TEL-001 contain Enterprise → Opportunity relationships?** Yes. Every required Enterprise has at least one direct, explicit typed Relationship to an Opportunity.
3. **Which Enterprises have them?** BT Group, CityFibre, Openreach, TalkTalk, Virgin Media O2, and VodafoneThree each have both kinds.
4. **Which Enterprises do not?** None of the six.
5. **Is Flora losing valid source relationships?** Yes. The current Enterprise pages show zero Programmes and zero Opportunities despite explicit source relationships. Candidate staging preserves the Relationship IDs, endpoint IDs, and types; many exact endpoints resolve, so the visible zero result diverges later in association consumption/presentation.
6. **Primary remaining defect?** **Both**, without collapsing the causes. Flora runtime loses valid direct associations that do exist. Separately, the producer/package omits any explicit Relationship involving the BT/Verizon Programme. Some unrelated endpoints also use non-object labels/pseudo-identities; the full report diagnoses them record by record.
7. **What should be fixed next?** Flora should first consume the already preserved, exact, resolved Relationship objects consistently on Enterprise pages. The Researcher/package-contract owner should separately decide whether to emit governed Relationship objects for the unlinked BT/Verizon Programme.
8. **Does the TEL-001 ZIP need to change?** Not for Flora to recover the valid associations already supplied. A future governed producer release—not a repair or repackaging of this ZIP—is needed only if BT/Verizon Programme linkage is intended to be canonical.
9. **Does Flora need a runtime correction?** Yes, in a separate implementation mission.
10. **Smallest next implementation step?** Add a focused failing acceptance test that stages this exact checksum, asserts each Enterprise’s source-derived Programme and Opportunity IDs, then correct the Enterprise association read/presentation path to use the shared candidate relationship resolution result. Do not alter importer semantics or the package.

## Enterprise conclusions

- **BT Group: FLORA DEFECT** — 1 source Programme(s), 3 source Opportunity/Opportunities; Flora reports 0 and 0.
- **Openreach: FLORA DEFECT** — 1 source Programme(s), 3 source Opportunity/Opportunities; Flora reports 0 and 0.
- **Virgin Media O2: FLORA DEFECT** — 2 source Programme(s), 3 source Opportunity/Opportunities; Flora reports 0 and 0.
- **VodafoneThree: FLORA DEFECT** — 2 source Programme(s), 3 source Opportunity/Opportunities; Flora reports 0 and 0.
- **CityFibre: FLORA DEFECT** — 1 source Programme(s), 2 source Opportunity/Opportunities; Flora reports 0 and 0.
- **TalkTalk: FLORA DEFECT** — 1 source Programme(s), 2 source Opportunity/Opportunities; Flora reports 0 and 0.

## Traces

- **BT/Verizon Programme:** `PROG-BT-VERIZON-JV` appears as a Programme object but no Relationship record has it as source or target. It is not explicitly linked to `ENT-BT`, directly or through an explicit mediated path. This is a producer/package gap, not evidence Flora lost that particular link.
- **BT-looking Opportunity:** `OPP-BT-VERIZON-JV-INTEGRATION` has a direct explicit Relationship to `ENT-BT`; this conclusion does not rely on its title or narrative.

## Evidence boundaries

- Fixture checksum: `bd3924d85125e308e36cc3f0b02af38e3eca7d163640d0d2c95aa7a861441d07`.
- Reconciled source inventory: 308 Relationship records and 50 Membership records.
- Membership establishes inclusion in `IND-UK-TELECOMS`; it is not required for Enterprise → Programme/Opportunity association.
- See [the complete Relationship Truth Report](TEL-001-Relationship-Truth-Report.md) for all rows, family totals, Enterprise matrices, traces, Membership classification, and candidate resolver comparison.

