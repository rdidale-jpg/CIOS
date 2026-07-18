# Validation Report

| Check | Result | Evidence |
|---|---|---|
| No documents lost | Passed | Governed inventory reconciled in `MANIFEST.yaml` and `REGISTER.md`. |
| No content removed | Passed | Governance changes added metadata/navigation and removed one byte-identical duplicate copy only. |
| No duplicate assets | Passed | Duplicate Four-Bank Matrix copy removed after byte-identical comparison. |
| All links valid | Passed | `python /tmp/validate_governance.py`. |
| Every governed asset has metadata | Passed | `python /tmp/validate_governance.py`. |
| Every directory has README | Passed | `python /tmp/validate_governance.py`. |
| Banking repository consistent | Passed | `python /tmp/validate_governance.py`. |

| Banking mechanisms-and-tensions classification corrected | Passed | `Banking-Mechanism-Catalogue.md` renamed to `Banking-Mechanisms-and-Tensions-Model.md`; asset ID changed from `BK-MEC-001` to `BK-REF-001`; `BK-MEC-001` reserved only for future planned Banking Mechanism Catalogue. |
| No canonical Banking Mechanism Catalogue content file exists | Passed | No governed file remains at `banking/industry/Banking-Mechanism-Catalogue.md`; Flora records the future catalogue as planned/pending only. |
