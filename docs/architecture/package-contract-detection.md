# Flora package contract detection

## Audit and interception point

The upload controller performs authentication, workspace resolution and membership/permission checks before registry receipt. Registry receipt previously read `blueprint_manifest.json` before building the ZIP inventory. The earliest safe generic interception is **after** `inspect_zip_inventory` has accepted every archive member and **before** Blueprint identity parsing and validation. The inventory function remains the sole archive path-safety and ZIP enumeration boundary.

The existing flow remains: `BlueprintPackageRegistry.receive` preserves the immutable receipt; `BlueprintPackageValidator.validate_and_stage` begins validation and candidate staging; review planning and `CanonicalPromotionService` provide the only path to promotion. The detector and adapters must never call those promotion services directly.

## Governed routing

1. `PackageContractDetector` consumes the original bytes plus the already-safe immutable inventory and returns a frozen `PackageInspection`.
2. Exact, case-sensitive root names govern detection. `blueprint_manifest.json` routes unchanged to the Blueprint validator. A root `mission_state.json` or `deterministic_restart_state.json` denotes a Research Workspace. A standalone root `industry_twin_delta_for_Flora.json` denotes an Industry Twin Delta. Similar or nested names do not count.
3. Workspace extraction inventories assets only. Research queues, restart state, checkpoint metadata, notes and diagnostics remain lineage and are never eligible for promotion.
4. `IndustryTwinDeltaAdapter` maps delta records to the existing `CandidateImportRecord` contract. The existing candidate repository, constructor validation, review plan, approval and canonical promotion service remain the single governed pipeline.
5. Unknown packages return a blocking inspection result and stop before validation and staging: “Unknown package contract. Package inspected. No canonical changes performed.”

Import-history projections should append the serialized inspection fields (`contract_type`, outcome, `promotion_eligible`, and ultimately promoted artefacts) to existing history records; they must not create a second registry or ledger.
