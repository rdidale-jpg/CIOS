# Macro-to-Enterprise Intelligence v2

Implements [#565](https://github.com/rdidale-jpg/CIOS/issues/565), stacked on draft [#564](https://github.com/rdidale-jpg/CIOS/pull/564) at `4c374ac2d326639245b60967aa64e934e0c1d7a3`. Verified main is `adf205993cc0857183d77766ce4882bf48326fb4`. No other PR is modified, merged, rebased or retargeted.

**Product result:** one more precise UK investigation and an intentionally bounded France industry trace. Neither is a compliance verdict or confirmed sales opportunity. The approved six-force atlas and shared PESTLE/operating visuals remain. A single concise enterprise inspector distinguishes identity, applicability, consequence and next action; exact sources and six separate decision edges are available in the dossier.

Open `/macro?market=GB&view=enterprise&offering=ai-delivery` for Lloyds Bank plc. Its public register identity is supported; formal binding-rule applicability remains Unknown. SS1/21 supports investigating ongoing critical-service dependency and recovery/exit assurance, not alleging a Lloyds weakness or a new deadline. The existing `RCO-LBG-005` remains an unqualified hypothesis. Ask which service, legal entity and evidenced test gap cannot be addressed by internal teams/current suppliers before proposing work.

Open `/macro?market=FR&category=sustainability&force=eu-csrd&view=enterprise` for the French reporting-perimeter investigation. The national code and consolidation exemption can be inspected directly. Exact French entity, size, phase-in and current amended thresholds remain unresolved. No French Lloyds subsidiary, obligation or opportunity is invented. This is the issue's explicit industry-only fallback, not completion of French entity verification.

## Architecture and authority

- Append-only `Entity-Traces-v2.json` is a versioned **candidate presentation specification** over the existing research spine. It pins the v1 context digest. All old knowledge bytes, 9 Lloyds and 6 easyJet opportunity identities remain unchanged.
- Four new located primary excerpts reuse `primary_text`, `SourceSegment`, `CandidateClaim`, `EvidencePackageItem` and `SemanticTwin`. No accepted Observation, canonical promotion, new truth database, permission engine or qualification engine.
- `macro_trace` validates provenance, exact identity passage, canonical capabilities, market/force scope, unresolved French identity and separately typed decisions. Global never silently selects a UK entity. Parent/group identity cannot prove subsidiary duty.
- MacroContextReference v1 is a deterministic **adapter design only**: force/instrument, jurisdiction/country, entity-scope state, edge/claim IDs, Macro and original research assessment/review digests, dates, limitations and contradictions. Caller changes are rejected against server-derived reconstruction. Seller offering is omitted from research truth and stays reversible relevance only.
- Current capture accepts commercial fields only. The #557/#561 capture owner has not introduced a compatible Macro append hook; modifying persistence now would interfere with the outstanding stack. No reference is saved. Duplicate capture, immutable original provenance, access/CSRF and qualification rejection are exercised through the existing service. No public page enumerates private records.
- No routes, public query selectors, private-store permissions or Pipeline production files change. Two exact official publisher hosts are added, without wildcard expansion.

[Source audit](Source-Audit.md) · [Architecture integration assessment](Integration-Assessment.md) · [Actual gallery / owner checklist](Gallery.md)

## Verification

Commands:

```sh
python -m compileall -q cios/applications/flora tools/preview_flora_macro_trace.py
actionlint .github/workflows/flora-validation.yml
python -m unittest discover -s tests/ci -q
python -m pytest -q tests/test_flora_macro_enterprise_v2.py tests/test_flora_global_macro.py tests/test_flora_commercial_visual_v3.py
python tools/ci/flora_ci.py --output <new-empty-directory>
python tools/preview_flora_macro_trace.py --url https://localhost:PORT --before-url https://localhost:BEFORE_PORT --output <gallery-directory>
```

Focused run: **115 passed**, comprising 33 new scoped-trace tests plus all 55 Macro and 27 v3 tests. CI-policy tests: **25 passed**; dependencies consistent; changed validation workflow passes actionlint. Repository-wide actionlint additionally reports an existing unsupported `overwrite_files` input in unrelated `export-flora-architecture.yml`; this sprint does not change that workflow.

Export inspection also caught and corrected an executive-footer citation bug: entity traces now print their own register/instrument sources instead of only the broader force sources. Both new export modes were regenerated and checked.

The strict baseline adds only the 33 observed passing identities and one suite selection. Every old suite, status, failure signature and skip reason is structurally unchanged. Required final comparison is 1,250 passed / 57 inherited failures / 10 original skips = 1,317 unique identities, including all 388 security tests. **Actual committed-candidate and hosted conclusions are recorded in PR checks and final publication evidence, not inferred from the focused pass.** Inherited failures remain 21 domain, 12 financial diagnostic and 24 historical legacy; skips remain ten unavailable retained-artifact tests.

The historical-corpus test retains its identity, all 142 historical files and all nine v1 additions byte-for-byte, permitting only five named v2 additions. Unknown additions/modifications/deletions remain forbidden. Isolated negative probes confirmed that modifying a v1 source or adding an unlisted file fails; restored approved corpus passes. See History-Guard-Probes.json. No failure exception or test exclusion is introduced.

Browser checks use temporary localhost storage, no synthetic demo seeding, production credentials, accounts or data. Chromium desktop/tablet/mobile and no-JS/keyboard paths are automated; physical Safari/iPad, screen-reader evaluation and human comprehension/commercial usefulness remain unperformed. This is suitable for draft owner evaluation, not legal certification, integration approval or deployment approval.
