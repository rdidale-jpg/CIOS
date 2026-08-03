# Migration to Researcher Knowledge Pack v2.8.0

Replace Researcher Knowledge Pack v2.7.0 bundles with `CIOS-Researcher-Knowledge-Pack-v2.8.0.zip`. Regenerate every commission from a schema 1.1 manifest; 1.0 manifests and generated briefs remain historical evidence but are not compatible active inputs. Retain canonical repository source documents in their owning paths.

## Behavioural changes from v2.7.0

- Research commissions name governed Twin Object profile IDs and versions; topic reports are no longer valid primary deliverables.
- Researchers populate, validate and package deterministic Industry, Enterprise, Participant, Programme, Opportunity, assessment and membership objects.
- Packages use the composite release manifest v2 for reproducible exact-version composition; existing v1 releases remain unchanged.
- Unknown and Not Applicable are explicit section states. Narrative-only completion and runtime reconstruction are prohibited.
