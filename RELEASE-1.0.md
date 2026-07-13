# CIOS Runtime Architecture Baseline 1.0

## 1. Release identity

| Field | Value |
| --- | --- |
| Release | CIOS Runtime Architecture Baseline 1.0 |
| Status | Baseline recorded for MOD validation; not a full production-readiness claim |
| Effective date | 2026-07-13 |
| Repository branch and commit | `work` at `b5d22a2` baseline source commit |
| Owner | Rob / CIOS |
| Purpose | Record the implemented CIOS Runtime Architecture baseline before MOD validation begins, including proven outcomes, deliberate exclusions, experimental material and the next validation phase. |

## 2. Executive summary

CIOS can now govern architecture through the Architecture Authority Registry, compile accepted architecture into role-specific profiles, produce a Researcher runtime package and produce an independent Assurance runtime package.

The implementation preserves source authority and traceability, respects runtime upload limits through governed compilation and generates deterministic runtime package outputs. This is an engineering baseline only: it records what has been implemented and tested, not that CIOS or the Enterprise Understanding discipline is fully validated.

## 3. Included capabilities

- Architecture Authority Registry as the control plane for status, authority and release-profile membership.
- AP-001 Architecture Compilation Standard.
- AP-002 Architecture Metadata Standard.
- Architecture Profile Compiler.
- RP-001 Enterprise Blueprint Researcher Profile.
- RP-002 Enterprise Intelligence Assurance Profile.
- Researcher runtime package.
- Assurance runtime package.
- Source-preserving ADR compilation into generated runtime ADR packs.
- Profile validation tests for Researcher and Assurance compilation.
- Deterministic compilation and deterministic runtime ZIP generation.
- Review-material exclusion for EU-001 and ADR-023.
- Provenance and traceability from compiled artefacts back to canonical source paths and registry rows.

## 4. What has been proven

The evidence supports these claims only:

- Accepted registry membership drives production profile compilation.
- Researcher and Assurance profiles compile successfully and are non-empty.
- Generated Researcher and Assurance packages fit the current runtime file constraint of 17 upload files each.
- Runtime ZIP outputs are reproducible apart from expected profile compilation timestamps.
- Proposed and review material remains excluded from production Researcher and Assurance profiles.
- Canonical architecture source documents are read during compilation and are not changed by compilation.
- Targeted architecture tests pass for registry parsing, profile inclusion, review exclusion, ADR traceability and deterministic ZIP output.

## 5. What has not yet been proven

This baseline does not prove:

- Whether the Researcher produces superior Enterprise Understanding.
- Whether Assurance identifies material weaknesses missed by the Researcher.
- Whether Decision Envelopes improve executive judgement.
- Whether the method transfers beyond MOD.
- Whether EU-001 should be promoted.
- Whether the architecture generalises across multiple enterprises.
- Whether wider repository test failures affect the runtime architecture.

No claim is made that the platform, the runtime packages or the Enterprise Understanding discipline are fully validated.

## 6. Known limitations

- Runtime packages are currently designed around the Custom GPT file constraint.
- EU-001 and ADR-023 remain Review or Proposed material and are excluded from production profiles.
- Repository-wide tests currently include unrelated failures outside the targeted architecture scope.
- Runtime deployment still requires manual GPT configuration.
- MOD validation has not yet been completed.

## 7. Governance statement

GitHub remains canonical. Compiled packages are generated artefacts and do not replace source architecture documents. Profiles do not promote document authority. Research and Assurance remain separate roles. Future architectural changes should be driven by validation evidence, not by packaging convenience.

## 8. Next validation phase

The next milestone is **Reference Enterprise 001 — MOD Assurance Review**.

The review will test:

- EU-001 compliance.
- Enterprise Understanding depth.
- Enterprise Coherence.
- Evidence lineage.
- Opportunity completeness.
- CSM and Oracle Fusion treatment.
- Commercial relevance.
- Decision Envelope quality.
- Executive utility.
- Prioritised Evidence Demands.

## 9. Release acceptance criteria

- RP-001 compiles.
- RP-002 compiles.
- Both packages fit the runtime upload limit.
- Packages are deterministic.
- Source ADRs remain unchanged.
- EU-001 and ADR-023 remain excluded from production profiles.
- Targeted architecture tests pass.
- No runtime or canonical Twin state changed.

## 10. Completion record

| Item | Record |
| --- | --- |
| Files created or changed | `RELEASE-1.0.md` created. |
| Validation performed | Source documents inspected; targeted architecture tests run; `git diff --check` run. |
| Tests passed | `python -m pytest tests/architecture/test_architecture_profile_compiler.py tests/architecture/test_rp001_researcher_profile.py tests/architecture/test_rp002_assurance_profile.py` |
| Known unrelated test failures | Repository-wide tests are not part of this baseline and are known to include unrelated failures outside the architecture scope. |
| Commit | `b5d22a2` is the baseline source commit; this release note is committed separately with message `docs: record CIOS runtime architecture baseline 1.0`. |
| Pull request | `Record CIOS Runtime Architecture Baseline 1.0`. |
| Recommended next action | Begin Reference Enterprise 001 — MOD Assurance Review and record validation evidence before promoting EU-001 or ADR-023. |
