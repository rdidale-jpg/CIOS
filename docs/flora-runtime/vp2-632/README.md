# FLORA VP-2 — accepted three-panel runtime

Implementation of [Issue #632](https://github.com/rdidale-jpg/CIOS/issues/632), starting from validated main `8a53777d1dec359f56b66e533d512c0a86881939`. The owner accepted the design in [PR #631](https://github.com/rdidale-jpg/CIOS/pull/631) at `f4059a34a55277adbd2a2337239827cab96d962e`; that design branch is not merged or used as the implementation base.

The running routes now compose the existing intelligence into **Top / Left / Main**. Top contains the constant UK skyline, real product/account navigation, scope and stream controls. Left contains the exact accepted portrait artwork and existing exploration destinations. Main prioritises readable intelligence, financial context and the existing Leadership Agenda, with optional sources and caveats.

This is a draft implementation for owner review, not authority to merge, accept research, change production or deploy. The exact tested implementation SHA and completed hosted run links are recorded in the draft PR validation comment; a document cannot contain its own commit hash.

## Review pack

- [Preflight, boundaries and architecture](Architecture-and-Preflight.md)
- [Before/after gallery and owner walkthrough](Acceptance-Walkthrough.md)
- [Retained destination inventory](Retained-Destinations.json): 51 labels and all 32 original active destinations
- [Exact selective asset provenance](Accepted-Asset-Import.json): 23 approved delivery files; seven historical originals and 21 existing variants remain unchanged
- [Validation, assertion reconciliation, limitations and rollback](Validation-and-Rollback.md)
- [Independent architecture and commercial critique](Independent-Critique.md)
- [777 browser checks](previews/Browser-Checks.json), [measured image delivery](previews/Performance.json), and [runtime preflight record](Runtime-Context.json)

## Start the application locally

Use the repository's established runtime/start instructions and isolated development storage. Open `/`, select **Banking**, then **Lloyds**. Direct routes remain `/industries/banking` and `/enterprises/lloyds`; stream/query links retain the existing server resolver. No new route, data migration, external service, dependency or deployment configuration is required.

The preview tool runs a temporary TLS loopback application and an exact-main comparison server. It creates only isolated authentication fixtures, removes them on exit and verifies no Offers/Pipeline state was written. Committed previews are real application screenshots, not the VP-1 static HTML prototype. GitHub renders screenshots but does not execute the application; downloadable hosted browser artifacts contain the same review outputs, not a deployed site.
