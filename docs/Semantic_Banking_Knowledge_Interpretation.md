# Semantic Banking Knowledge Interpretation

Flora now extends the governed Banking Enterprise Intelligence runtime with a semantic interpretation layer. The layer loads meaning-bearing governed content, segments source text, extracts derived runtime claims, packages a bounded semantic context and exposes semantic reasoning mode in diagnostics.

## Runtime behaviour

- Governed Markdown, JSON and YAML assets are loaded through the Banking manifest.
- Markdown is segmented deterministically by headings; JSON/YAML are converted into stable content sections.
- Candidate claims are derived runtime claims only; they are not promoted to governed Observations or Enterprise Knowledge.
- Explore and Shape share the same Banking pipeline output and semantic context.
- Unknowns and Contradictions remain visible and constrain recommendations.

## Provider configuration

Model-backed semantic reasoning is enabled only when production configuration is present:

- `FLORA_REASONING_PROVIDER=openai`
- `OPENAI_API_KEY` configured as a secret
- Optional `FLORA_REASONING_MODEL` (default `gpt-4.1-mini`)
- Optional `FLORA_REASONING_TIMEOUT_SECONDS` (default `20`)
- Optional `FLORA_REASONING_RETRY_LIMIT` (default `1`)

When configuration is absent, Flora uses deterministic fallback and labels diagnostics as `Semantic reasoning mode: Deterministic fallback`. Provider objects and hidden chain-of-thought are not persisted in runtime models. Generated material claims must cite permitted source IDs; unsupported IDs fail deterministic validation.

## Cost and logging policy

The semantic context is bounded to the selected Banking assets and a maximum token budget recorded in the context. Secrets are never logged. The runtime records provider/model name and instruction version in telemetry, not the full private prompt or hidden reasoning.

## Manual acceptance

1. Open Flora.
2. Open Explore.
3. Open Banking.
4. Confirm the top of the page explains what is changing, why it matters and why now.
5. Confirm mechanisms have names and explanations.
6. Confirm observations have distinct statements and relevance.
7. Confirm evidence has human-readable labels.
8. Confirm Unknowns have matched evidence demands.
9. Confirm Alternative Interpretations are shown.
10. Confirm the page does not primarily read like asset IDs.
11. Open Shape.
12. Confirm the Strategic Sales Brief contains substantive interpretation, executive consequence, commercial implication and proportionate next action.
13. Expand `How Flora reasoned`.
14. Confirm semantic reasoning mode is visible.
15. Confirm no named executive or unsupported bank-specific claim is invented.
16. Check Render logs for no startup or request failures.
