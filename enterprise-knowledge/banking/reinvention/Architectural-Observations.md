# Banking Reinvention Hypotheses — Architectural Observations

**Parent asset:** `EK-BANK-RHYP-001`  
**Document class:** Architectural observations companion  
**Effective date:** 2026-07-18

| ID | Architectural observation | Why it matters |
|---|---|---|
| `ARCH-OBS-001` | Hypotheses require an explicit intermediate Observation layer. | The commission confirms that future reinvention reasoning should not jump from source documents or mechanisms directly to future statements. The Observation Register is the required stabilising layer. |
| `ARCH-OBS-002` | Mechanism confidence is not the same as hypothesis confidence. | A Strong mechanism can support only Medium reinvention confidence where future movement depends on unobserved elasticity, adoption, regulation or execution evidence. |
| `ARCH-OBS-003` | Contradictions generate better hypotheses than they generate conclusions. | Branch cost-versus-trust, cloud speed-versus-concentration, AI productivity-versus-assurance and convergence-versus-variant contradictions produced high-value falsifiable hypotheses without forcing premature conclusions. |
| `ARCH-OBS-004` | Participant-type variants should remain first-class model objects. | The register repeatedly requires incumbent, challenger, mutual, universal-bank and global-platform subsidiary variants. Future Industry Reinvention Models should not flatten those variants into one banking model. |
| `ARCH-OBS-005` | Infrastructure-owned mechanisms need separate ownership modelling. | Payments, Confirmation of Payee, Open Banking and cloud critical-dependency hypotheses show that important Banking futures are partly controlled by shared infrastructure and third parties, not by bank strategy alone. |
| `ARCH-OBS-006` | Falsification evidence should become a standard field for Flora hypothesis objects. | Every hypothesis benefits from monitoring indicators and evidence required. Flora should preserve not only supporting evidence, but also the evidence that would weaken, split, supersede or retire the hypothesis. |
| `ARCH-OBS-007` | Methodology assets and evidence assets must remain separated. | EGM-001 guides how hypotheses are formed. Banking assets determine what hypotheses are admissible. Method concepts should not be treated as evidence that a Banking future will occur. |

## Architecture Debt

| Debt ID | Description | Suggested future handling |
|---|---|---|
| `ARCH-DEBT-001` | Hypothesis objects do not yet have a canonical Flora schema with lifecycle states such as Candidate, Strengthened, Weakened, Contradicted, Superseded and Retired. | Define a Hypothesis Register schema or extend the existing Evidence / Observation / Signal / Hypothesis lineage model. |
| `ARCH-DEBT-002` | Banking observation lineage is inherited from the Observation Register, but individual hypothesis entries would benefit from machine-readable reverse lineage to each Evidence ID. | Add a structured reverse-lineage table in the next release. |
| `ARCH-DEBT-003` | Universal-bank candidate mechanisms create scope tension between Retail/Commercial Banking and broader Universal Banking. | Resolve through an ADR or a separate Universal Banking / Capital Markets mechanism catalogue boundary. |
| `ARCH-DEBT-004` | Monitoring indicators are human-readable rather than executable. | In a later Flora implementation, convert indicators into typed watch conditions linked to refresh triggers. |
