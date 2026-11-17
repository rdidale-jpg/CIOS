# Current model ownership, update semantics and gaps

**Repository reference point:** `fbac4c37910ed07b2baa516e1a5c8d7f329086de`. These are observed code/document relationships; an item labelled **candidate** is not accepted canonical knowledge.

| Model / lens | Existing owner and source | Inputs → stored knowledge/view | Update trigger actually supported | Status and principal gap |
| --- | --- | --- | --- | --- |
| External / UK context | `visual_streams` + `visual_panels` UK scene; `enterprise-knowledge/macro/research-model/Macro-Context-v1.json`; historical global macro runtime/docs | selected public policy/economic claims → UK editorial view | source/code/research revision + next deployment; no continuous recomputation shown | **View exists;** force identity to bank dependency not generally updated |
| Banking PESTLE | `research_intelligence.model.load_assessment`, `unified_views.industry_page`, `visual_templates.pestle` | `Assessment-Overlay.json.frameworks` → radial diagram / clauses | author revises overlay and renderer reads version | **Candidate research**; primary Banking Landscape does not automatically recompose PESTLE |
| Five Forces | `unified_views.industry_page(lens='porter')`, `visual_templates.forces`, BIE-2 Industry-Analysis | competition/actors/mechanisms → competitive graphic | overlay pack revision | **Parallel view**; currently branded Banking Forces is *four editorial drivers*, not the five Porter forces |
| Value chain and relational ecosystem | `visual_templates.chain/ecosystem`, industry overlay, BIE-2 actor/relationship candidate packs | roles, typed reported/unknown edges → diagram | overlay/candidate update | **Mixed status**; do not infer financial flows or contracts from conceptual arrows |
| Financial reported/calc/estimated | Financial `candidate_analytics`, `analyst`, public nationwide projection | typed source value + date/entity/basis → stored run or public current projection → calculations | explicit prepared run; public facts change on new source bundle/code; per-read rights/lifecycle validation | **Real Nationwide and BoE pilot**, uneven broader bank coverage and no auto schedule |
| Enterprise capability / tech / supplier maps | `unified_views.enterprise_page`, `visual_streams` Lloyds, overlay `capabilities`, `suppliers`, programmes | source/claim associations → conceptual maps | overlay/source revisions | **Mostly curated or candidate**; limited validated causal operation/relationship evidence |
| Leadership and events | `leadership_agenda.Issue`, `agenda(scope,...)`, existing `banking_portfolio` timeline, BIE2 News | claim/issue or dated event → headline/timeline | new pinned claim/event snapshot; not automatic rolling news update | **Partial**; source date and material change not always integrated |
| Canonical Evidence/Observation/Model | `memory.repository`, Blueprint import; `EI-001` Draft, accepted ADR-002 and related | accepted Evidence→Observation→Model durable state | only authorised canonical transactions | **Proper stronger boundary**; do not require for ordinary analytical charts |
| External change interpretation | `ExternalChangeInterpretationService.assess` | governed external Evidence descriptor + canonical related entity & annotated Observations → read-only eligible/assessed consequences and evidence demands | explicitly invoked; must have accepted Evidence and relationship assertions | **Narrowly implemented**, no general noncanonical working-ripple acceptance |
| Material Pressure | `blueprint_import.material_pressure.qualify_candidates`, ADR-026 | canonical enterprise condition/evidence/impact → qualified or rejected pressure | explicitly assessed on canonical sources, not public news by itself | **Essential boundary**; industry evidence alone insufficient |
| Commercial hypothesis & Pipeline | `research_intelligence` candidate opportunity views, `banking_portfolio` pilot routes, protected Pipeline services | evidence-backed possible issue → user-confirmed qualification/actions | separate candidate research and authorised capture | **Not automatic**; clear transition from intelligence to sales action still requires evidence/owner |

## Minimal existing-owner data contract needed for a working ripple

Do **not** introduce a second graph database. For each **current working** change association, derive a small materialised *view* or temporary index over existing immutable source/event/subject keys:

`{event_or_claim_id, source_revision, event_date, publication_date, effective_date, reporting_period, subject_entity_id, legal_scope, geography, industry_id, typed_relation, target_capability_or_force_id, association_kind, support_ids, interpretation_type, exception_or_counterevidence, computed_at}`

This is a **proposal**, not a schema admitted to production. It may live in an existing overlay/Financial/presentation record only after owning contracts and tests are approved. Never invent canonical IDs, assert source-candidate status is Evidence acceptance, store duplicated independently editable truth or make a 'ripple score'. Distinguish:
- `reported_direct`: source explicitly says the subject changed.
- `contextual_relevance`: independently documented mechanism makes the event worth reassessing.
- `supported_exposure`: target enterprise relationship/capability and actual application supported.
- `hypothesised_impact`: reasoned but unverified and never automatic buying need.
- `not_applicable` only if actual evidence shows exemption; Unknown is not that evidence.

### Invalidation, not rewriting
A change in source revision, rights/use state, relevant observed/effective dates, identity/perimeter, association support or contradiction must trigger **reassessment/omission** of the affected derived view and downstream materialisations. It must **not** silently erase historical events or mutate canonical Enterprise Models. Public private-workspace checks and source suppression remain in existing owners. Effective/upcoming changes must not be rendered as already happened.

### What to measure
- Real current visible change stories with supported sources and honest dates.
- Correct association/denial and retraction scenarios; exact affected scenes invalidated, unrelated stories preserved.
- Whether one enterprise update produces a justified cross-enterprise synthesis when several independent cases exist.
- Zero source IDs or internal provenance hyperlinks in normal seller Main; protected inspection retains proof.
- No auto new Material Pressure, Opportunity, Pipeline action or unapproved canonical mutation.

### Source anchors
- `cios/applications/flora/visual_streams.py`: `SCOPES`, `resolve`, `current_data`, `render` and finite selectors.
- `cios/applications/flora/visual_panels.py`: `_editorial_banking`, `_frame`, `_bank_picker`.
- `cios/applications/flora/research_intelligence/unified_views.py`: `industry_page`, `enterprise_page`.
- `cios/applications/flora/research_intelligence/visual_templates.py`: `pestle`, `forces`, `chain`, `ecosystem`.
- `cios/applications/flora/enterprise_intelligence/change_interpretation.py`: `ExternalChangeInterpretationService.assess`.
- `cios/applications/flora/blueprint_import/material_pressure.py`: `qualify_candidates`.
- `cios/applications/flora/intelligence_presentation.py`: six semantic types and output omission.
- `docs/flora-runtime/bie2/News-Candidates.json`: dated candidate events, production flags.
- `docs/flora-runtime/bie2/Industry-Analysis.json`: financial/competitor/framework working hypotheses.
- `architecture/decisions/ADR-026-Material-Pressure-Qualification-and-Ownership.md`: accepted pressure qualification.
- `architecture/specifications/industry-twins/IT-001-Industry-Twin-Specification.md`: **Review**, not accepted.
