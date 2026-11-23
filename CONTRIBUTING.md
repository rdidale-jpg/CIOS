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

For FLORA, use the [Product Delivery Doctrine](docs/product/flora-delivery-acceleration/README.md): agree the user outcome and bounded scope, reuse existing capability, deliver the complete journey, validate proportionately, then return or update one draft PR with a concise acceptance walkthrough. Reuse evidence for unchanged decisions; retain all required checks. Routine implementation within an accepted contract does not require a fresh architecture decision. A material conflict still goes to its existing owner.

Visual acceptance uses the running candidate in a browser, not screenshots alone. Merge and deployment require the authority specified in the commission; neither is implied by passing tests or visual acceptance.

## AI Agent Guidance

AI coding agents must:

- Read `README.md`, `ARCHITECTURE.md` and `ROADMAP.md` before making changes.
- Ask for clarification when architectural intent is unclear.
- Avoid deleting files unless explicitly instructed.
- Prefer small, reviewable commits.
- Explain what changed and why.
