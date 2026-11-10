"""Read-only research-cycle presentation on the existing diagnostic page."""
from html import escape
from .cycle import research_plan, connected_context, reference_submission, run_cycle


def render(data, as_of):
    plan = research_plan(data, as_of)
    esc = lambda value: escape(str(value), quote=True)
    root = data.get('route_root', '/flora/banking/research')
    tasks = ''
    for task in plan['tasks']:
        selected = task['id'] in plan['selected_task_ids']
        routes = ''.join(f"<li><a href='{esc(url)}' rel='noreferrer'>{esc(url)}</a></li>" for url in task['source_routes'])
        tasks += (f"<details class='ux-claim' {'open' if selected else ''}><summary>{esc(task['title'])} · priority {task['priority_score']}"
            f"{' · Next wave' if selected else ''}</summary><p>{esc(task['question'])}</p>"
            f"<p>{esc(task['rationale'])}</p><p><strong>Source families:</strong> {esc('; '.join(plan['source_families'][f] for f in task['source_families']))}</p>"
            f"<p><strong>Search prompts:</strong> {esc('; '.join(task['search_queries']))}</p><ul>{routes}</ul><p><strong>Acceptance evidence:</strong> {esc(task['closure_test'])}</p>"
            "<p>Actively search for contrary evidence. A blocked URL does not establish evidence exhaustion.</p></details>")
    dossier = ''.join(f"<details class='ux-claim'><summary>{esc(row['label'])} · {len(row['supported_claim_ids'])}/{len(row['claim_ids'])} passage-supported mapped claims</summary>"
        f"<p>{esc('; '.join(row['deficiencies']))}</p><ul>" + ''.join(
            f"<li><a href='{root}/evidence/{esc(cid)}'>{esc(cid)} — inspect passage</a></li>" for cid in row['claim_ids']) + '</ul></details>' for row in plan['coverage']['dossier'])
    context = connected_context(data)
    edges = ''.join(f"<details class='ux-claim'><summary>{esc(e['subject'])} → {esc(e['predicate'])} → {esc(e['object'])}</summary>"
        f"<p>{esc(e['qualification'])}. {esc(e.get('temporal_scope', 'Effective period not recorded'))}</p><ul>" + ''.join(
            f"<li><a href='{root}/evidence/{esc(cid)}'>{esc(cid)} — relationship evidence</a></li>" for cid in e['claim_ids']) + '</ul></details>' for e in context['edges'])
    reference = reference_submission(data)
    reviewed = run_cycle(data, as_of, [reference])['waves'][0]['proposals'][0]
    recent = ("<details class='ux-claim'><summary>Latest retained primary-source review — proposed observations</summary>"
        + f"<p>{esc(reviewed['rationale'])}</p><p><a href='{esc(reference['source']['url'])}' rel='noreferrer'>{esc(reference['source']['title'])}</a> · Retrieved {esc(reference['source']['retrieved_at'])}. Publication: {esc(reference['source'].get('publication_date') or 'Unknown')}; period: {esc(reference['source']['reporting_period'])}. Original page bytes not archived.</p>"
        + ''.join(f"<blockquote>{esc(c['segment']['content'])}</blockquote><p>{esc(c['segment']['section_heading'])}. Candidate only; no finding automatically changed.</p>" for c in reviewed['candidates'])
        + "<p>Existing findings and the evidence gap remain retained. Company-reported metrics are not independent verification or sales qualification.</p></details>")
    sources = ''.join(f"<li>{esc(s['source_id'])}: {esc(s['date_status'])}. {esc(s['extent'])}. {esc(s['limitation'])}</li>" for s in plan['coverage']['source_review'])
    return ("<section aria-label='Research Intelligence v2'><h2>Deepen enterprise understanding</h2>"
        f"<p>Reproducible cut-off: {esc(as_of)}. Candidate baseline: <code>{esc(plan['coverage']['baseline_digest'][:16])}</code>.</p>"
        "<p class='ux-disclosure'>This is a deficiency screen, not IT-001 maturity or Research-ready certification. No new external evidence has been acquired by viewing this page. Missing topics stay Unknown; hypotheses stay unqualified.</p>"
        + recent + "<h3>Next evidence wave</h3>" + f"<p>{esc(plan['selection_rule'])}</p>" + tasks +
        "<h3>Dossier coverage — fourteen existing contract dimensions</h3>" + dossier +
        "<details><summary>Source freshness and retrieval limitations</summary><ul>" + sources + '</ul></details>' +
        "<details><summary>Connected enterprise understanding — inspect evidence</summary>" + edges +
        f"<p>Unmodelled relationship classes: {esc('; '.join(context['unmodelled_relationship_classes']))}. {esc(context['limitation'])}</p></details>"
        "<h3>Evidence → candidate observations → proposed finding changes</h3>"
        "<p>The bounded offline cycle accepts reviewed HTML, PDF or text, or confined approved-tool excerpts, with provenance, checksums and located quotations. It preserves original findings, Unknowns and proposed supersession. Each strengthen, weaken or invalidate judgement requires an explicit target and rationale; none automatically changes an accepted fact.</p>"
        "<p>Research operators can export the source plan and canonical Researcher commission with <code>python tools/research/flora_cycle.py --enterprise lloyds --as-of YYYY-MM-DD --output NEW_LOCAL_DIRECTORY</code> (use easyjet for Aviation). Supplied files and resumed checkpoints remain local; this public page never reads private research packages.</p></section>")
