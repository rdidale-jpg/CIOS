# Validation and compatibility

This is a documentation-only policy proposal. The cases below are acceptance specifications for a later authorised implementation, not claims that new runtime behaviour has been built or that a test grants legal permission. Ordinary cases should use the adopted reusable method without repeated discretionary sign-off. Existing runtime denials remain unchanged by this PR.

| Case | Expected result after authorised implementation |
| --- | --- |
| Two compatible measurements, then a new compatible issuer/document within the established method category | Deterministic source/version, lawful-method and meaning checks suffice. No new licence application merely because the issuer, document or figure changed; no per-measure or per-issuer approval queue. An actual changed legal/use premise is separately handled. |
| Same publisher but different path, applicant issuer, terms, version, retained format, use or audience | Validate each dimension. A different version must be independently verified; a changed decision premise or purpose must be reviewed. Reject lookalikes, credentialed access and redirects outside approved origin. |
| Allowed OGL numerical content and excluded third-party content in the same release | Format, rights, mandatory attribution and precise exclusions determine display. A source allowlist alone gives neither result. |
| Independently stated public fact or reproducible calculation; no express publisher factual-use licence | Absence of a licence is not itself a denial: facts and original analysis use their applicable lawful basis within the established category. Verify inputs, source and actual applicable restrictions. Copyright in the report is not automatically copyright in each number. |
| Minimal numerical facts/provenance without a stored full-text copy | The category's lawful retained form can render if integrity binds the actual fact, version and locator. No per-number retention approval or redundant report copy. Missing text in an unchanged legacy path that requires it still fails; archives/excerpts/embeddings are different operations. |
| Generic copyright notice without an identified restriction on the actual factual method | Do not invent a new approval gate. Preserve source attribution and check whether any concrete rights, contract, access or evidence exception actually applies. |
| Identified materially unresolved or binding term on a specific operation | Record clause, applicability, operation and uncertainty under the existing owner. Hold only the affected use as needed; preserve ordinary reading, unrelated eligible facts and permitted attribution. Independent wording cannot waive a binding contract; alternate hosting cannot evade it. |
| Lloyds S3 three-fact method vs protected report/table copying | Separately restating the three factual measures is not automatically licensed expression copying. Resolve the specific §2 contractual premise once if material; no per-number copyright licence is presumed. Protected copies require their own applicable lawful basis. Do not declare either unconditional clearance or a blanket issuer ban. |
| Lloyds home-page attribution vs a new direct PDF/deep link | Apply the §5 conditions to the compliant home-page route; preserve exact internal source locator and bibliographic attribution. Defer the deep-link operation pending scoped resolution without treating that alone as a restriction on the facts. |
| Lawful-user insubstantial database use vs cumulative/substantial extraction | Assess actual lawful-user/statutory position and cumulative extent; neither ignore statutory protections nor invent a fixed three-number safe harbour. Routine matching within scope needs no new discretionary approval; changed scale can require an exception. |
| Source withdrawn, superseded, contradicted or permission denied | Values, series counts, chart points, labels, HTML/ARIA, print/export and dependent calculations or Insight disappear or resolve to the explicitly verified successor. Unrelated eligible facts and historical owner records survive. |
| Wrong legal entity, fiscal period, comparison basis, units or incompatible accounting assumptions | Reject or show the properly labelled separate measure. No Group to legal-bank allocation. No annualising a nine-month result as actual or mixing Group and banking NII. |
| Identical public guest read with private run present, absent, inaccessible or store offline | Identical public data and no visibility or timing dependency on tenant records. Wrong workspace cannot read a run or discover its existence via the projection. |
| Existing F1 and F2 BoE working analysis and AUTH-2 Nationwide | Preserve existing selection and scope, hashes and lineage, access rules, public attribution, source withdrawal and signed bridges. F3 remains proposed and existing exceptions are not silently lifted by this documentation. |
| Public fact/minimal working data vs a new Lloyds Financial run | Public factual eligibility does not call private-run lookup or creation. Existing F1 exclusion, user/workspace/resource ACL, CSRF, audit, idempotency and run source-use boundaries remain. Separately authorise any extension; do not make every isolated fact inherit a private-run restriction. |
| Public display requested as canonical acceptance or used to trigger Pipeline | Display has no mutation capability. Existing authorised canonical review and Material Pressure lifecycle remain independent. |

Exact-head implementation validation should include existing F1/F2/F3, RUD1 and AUTH-2 source and financial tests, strict security and functional regression, plus the new public projection cases above. Keep the existing regression baseline and historical rights decisions unchanged. Roll back a future projection by withdrawing its eligibility under the existing owner and reverting its use in views as needed, retaining governed history. This draft itself can be withdrawn without a data or runtime migration.

## Documentation refinement validation and compatibility assessment

Reviewed starting head **90108618761cf86fe2ff2c3b0b1bb00b0713a3ed** and main **46ed59295abb0259ee09ffa79c778848f170a5eb** before editing. The update is confined to this folder's Markdown: policy wording, the six-operation [Lloyds disposition](lloyds-q3-disposition.md) and these acceptance cases. No code, source record, grant, security control, historical research decision, accepted ADR, comparator, test, workflow or Pipeline file changes.

Relevant existing checks, run in isolated test stores:

```bash
python -m pytest tests/test_flora_f1_642.py tests/test_flora_f2_644.py tests/test_flora_f3_646.py tests/test_flora_rud1_648.py tests/test_flora_auth2_655.py -q
python -m pytest tests/test_flora_security*.py -q
git diff --check
```

Final SHA and actual results are reported in PR #698. Existing tests assess current source/financial/ACL/withdrawal behaviour; they do not implement or legally approve the proposed category. Source/meaning review rechecked S3's three numbers, period and different Group/banking bases against the original. Link checks distinguish internal repository links from the specifically unresolved public deep link. No report/table archive, fabricated byte hash or source licence is produced. Official legal-page retrieval limits are recorded in the disposition.

The regression argument for this documentation update is exact unchanged executable/control/data bytes, plus the focused existing financial/source and strict security checks. A full application/browser regression is not claimed for prose changes. A later implementation must execute the broader cases above, including public/private equivalence, cache/ARIA/export withdrawal, source changes and negative legal/identity cases.

Owner acceptance is still required for the policy wording and the precise remaining exceptions. ADR-027 remains Proposed. No merge, runtime permission change, canonical acceptance or deployment occurs here. Rollback of this refinement is a revert of its documentation commit; it requires no data migration.
