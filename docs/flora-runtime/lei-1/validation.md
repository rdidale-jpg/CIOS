# Validation and rollback

Run from the repository root.

```sh
python docs/flora-runtime/lei-1/validate.py
git diff 434129b100f556c6e82acfaa162f6db3a322b017 --check
```

The research validation checks signed arithmetic, required scope/basis/period and source locators, reproduces the two unchanged Wave 3 bridges via their existing validator, checks local references and rejects changes outside this research directory. It cannot prove publisher permission or independently audit the issuer. The four source documents were inspected directly against the selected inputs, with version identifiers in the source register. The historical Wave 3 whole-branch validator is pinned to its own pre-Wave-3 base and change allowlist. LEI reuses only its reconciliation validator rather than changing or bypassing its historical publication boundary.

Review the signed Group profit delta and the H1 underlying-to-statutory boundary before using any results. Review the direct issuer notes on banking NIM, revised wholesale funding and capital ratios before comparing scope or periods. Owner review of exact intended source use precedes any later integration.

Rollback is to close the research draft or revert the research commit. There is no runtime or data migration. Existing source permissions, Pipeline, PR #696 implementation, canon and deployments retain their current state.
