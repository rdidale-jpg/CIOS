# Contributing to CIOS

CIOS is being developed iteratively using ChatGPT, Codex and GitHub.

## Contribution Principles

Every contribution should:

- Align with the CIOS Constitution.
- Preserve explainability.
- Improve modularity.
- Include appropriate documentation.
- Avoid unnecessary complexity.
- Be traceable to a clear requirement, issue or architectural decision.

## Working Method

1. Define the objective.
2. Confirm the relevant CIOS artefacts.
3. Make the smallest useful change.
4. Add or update tests where appropriate.
5. Document the decision or implementation.
6. Commit with a clear message.

For FLORA, **default to progress; escalate exceptions**. Use the [Product Delivery Doctrine](docs/product/flora-delivery-acceleration/README.md): **Build → Test → Merge → Review**. Reuse existing capability and accepted decisions, complete one useful increment in one PR, run existing applicable checks, then merge routine reversible work without separate owner integration approval. Reuse valid evidence for unchanged scope; preserve required security, financial/evidence and regression checks. Routine implementation within an accepted contract does not require a fresh architecture decision.

Owner review tests usefulness in the running candidate; visual work needs browser interaction, not screenshots alone. Flora-Current is a development/evaluation runtime; a merge does not deploy it. Retain explicit owner authority for the doctrine's [protected exceptions](docs/product/flora-delivery-acceleration/README.md#exceptions-requiring-explicit-owner-authority), task-specific stops and actual deployment. Do not bypass an approval-system rejection. Report what changed, what can be tested, tests/material failures, genuine blockers, and merge SHA/rollback in the same PR.

## AI Agent Guidance

AI coding agents must:

- Read `README.md`, `ARCHITECTURE.md` and `ROADMAP.md` before making changes.
- Ask for clarification when architectural intent is unclear.
- Avoid deleting files unless explicitly instructed.
- Prefer small, reviewable commits.
- Explain what changed and why.
