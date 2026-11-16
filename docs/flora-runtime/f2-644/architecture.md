# Existing owners and bounded adapter

| Responsibility | Existing owner / F2 change |
|---|---|
| Financial persistence | `document_review` Financial runs under workspace-bound records in the shared `ai_financial_reports/runs` directory; no new repository/schema/database |
| Typed measurements and recipes | `financial_intelligence.candidate_analytics`; existing stock/duration, entity, basis, state, precision and Decimal arithmetic retained |
| Current source validity | Existing reviewed source owner and F1 content pin, revalidated on every external read; no registry or permission expansion |
| Six presentation types | Existing `intelligence_presentation`; unsupported empty/question/action content omitted |
| Main composition | New finite `financial_intelligence.analyst` presentation adapter; shared existing `visual_panels._frame` |
| Identity / capability / resource | Verified SecurityStore session and `package.inspect`, selected workspace, EnterpriseCanvas ACL; no browser-supplied owner identity |
| Navigation | Existing Banking/Lloyds routes and stream grammar; one narrow private query guard, no public catalogue change |

## Discovery and read lifecycle

The contextual link uses the Financial owner's finite permitted selection keys, current eligible source bundle and deterministic F1 run identity. It checks the exact workspace/resource/run path and performs a fresh authorised read. It never scans global/latest runs or creates on GET. Missing file, missing capability, foreign workspace, missing resource ACL or withdrawn source contributes no title, link, count or source identity. A missing-run file check precedes a nested guarded read so an expected absence cannot poison the outer authority transaction.

The private selector enters through existing `private_read` after verified identity, then `authorise_request`. Duplicate/extra query parameters, wrong country, incompatible stream/detail/agenda, wrong subject and invalid run identifiers fail closed. `render_selected` is itself guarded throughout composition and obtains a fresh sanitised `document_review.read_run`. All HTML, chart/table, title, ARIA and sources come from that fresh projection; no persisted derived values are trusted. No export or public cache is added. Existing no-store/private response policy remains authoritative.

The actual reported subject is distinct from the ACL resource: BoE UK MFI data belongs in the Banking resource and cannot be relabelled as Lloyds financials. The existing detail route retains its current source-withdrawal sanitisation. Current source changes remove dependent output, preserve immutable run history and permit restoration only when the same eligible reviewed source revision is restored.

## Finite reusable composition

One signed linear bar family groups exact subject/name, perimeter, currency, scale, unit, accounting basis, actual/target state and period kind. Instant series also require identical metric/definition; duration comparisons require identical explicit dates and issuer fiscal calendar. Multi-perimeter charts retain their precise perimeter labels. Definitions and conflicting same-period reported values are checked. Zero is always included; negative values retain sign. Display conversion never changes stored inputs or arithmetic precision. No chart framework, executable expression, automatic annualisation, peer ranking or FX conversion is added.

Result cards accept the existing finite difference/relative difference recipes and one bounded `signed_bridge` contract. The bridge validates exact source revision, subject, period, state, unit, explicit basis changes, signed adjustments and separately reported endpoint. It invents no residual and provides no rounding plug. Only synthetic contract tests use this bridge; no new real source or recipe admission is implied. Assumed/estimated dependencies keep an Estimated result and inspectable owner/version. A separately reported endpoint is not independent corroboration.

## Concrete F3 extension contract

A future separately reviewed source adapter would return the existing `InputBundle(resource_id, title, measurements, source)` and typed `Measurement` / `SourceReference` records. It must supply a permitted document-specific source-use decision, immutable source/measurement revisions, precise legal issuer/consolidation, accounting basis, period/instant date, currency, scale, unit, precision and published/retrieved/vintage limits. It must bind the real canonical resource identity and existing workspace ACL. A finite owner selection key and pinned finite recipe are then registered inside the existing Financial owner, not supplied by browser code. Existing guarded creation stores the same Financial run contract; generic Main composition needs no per-bank renderer.

F2 permits exactly the F1 BoE key. This interface does not approve future bank sources. Any new source, financial definition, nonmonetary unit, recipe or canonical identity needs its own source/semantic/security review. Unknown source identity, rights or authority remains blocked. No new intelligence owner, Evidence registry, SourceRecord, canonical promotion or Pipeline path is created.
