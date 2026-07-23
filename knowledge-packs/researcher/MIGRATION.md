# Migration to Researcher Knowledge Pack v2.3.0

Replace Researcher Knowledge Pack v2.1.0 bundles with `CIOS-Researcher-Knowledge-Pack-v2.3.0.zip`. Retain canonical repository source documents in their owning paths.

## Behavioural changes from v2.1.0

- Industry Twin research is now explicitly participant-aware and cannot reasonably be interpreted as buyer-only research where participant, contract, procurement or opportunity context is commercially material.
- Configure the Researcher with `Researcher-GPT-Instructions.md`, upload the ZIP, and use the UK Central Government mission brief as connected commercial intelligence scope rather than an organisation-description scope.
- Use the new Market Participant Twin, Account-Participant Position Assessment and Opportunity Hypothesis templates for relevant output objects.
- Preserve the Research-ready boundary: the Researcher must not declare Architecture-ready, Implementation-ready, Pilot-ready or Accepted.

## Authority and source handling

Review-status sources packaged in v2.3.0 remain labelled as Review material and are included only because they are required to operationalise participant-aware research outputs. Missing required owning sources must be recorded as validation failures or unresolved-source warnings rather than silently paraphrased.
