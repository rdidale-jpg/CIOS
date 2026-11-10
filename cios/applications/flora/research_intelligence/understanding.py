"""Read-only evidence and relationship assessments over existing semantic contracts.

All findings remain candidate intelligence. Exact-support and independence reviews
are inspectable judgments, never a numeric scoring authority or canonical acceptance.
"""
from collections import Counter
from copy import deepcopy
from dataclasses import replace
from datetime import date
import json
from urllib.parse import urlsplit, urlunsplit

from ..blueprint_import.semantic_twin import SemanticObject, SemanticTwin, resolve_relationships
from .cycle import digest, coverage, research_plan, semantic_projection
from .model import validate, primary_text, REPO
from .registry import assessment_path
from .source_import import secondary_excerpt

STATES = ('Verified factual relationship', 'Supported analytical inference',
          'Plausible unverified hypothesis', 'Contradicted relationship',
          'Superseded relationship', 'Unknown / missing relationship')


def load_review(domain):
    return json.loads((assessment_path(domain).parent / 'Understanding-Review.json').read_text())


def document_key(source):
    """Presentation variants and fragments cannot create independent documents."""
    p = urlsplit(source['url'])
    return urlunsplit((p.scheme.lower(), (p.hostname or '').lower(), p.path.rstrip('/'), '', ''))


def publisher_group(source):
    host = (urlsplit(source['url']).hostname or '').lower()
    if host in ('www.lloydsbankinggroup.com', 'www.lloydsbank.com'): return 'Lloyds'
    if host in ('www.easyjet.com', 'corporate.easyjet.com', 's203.q4cdn.com'): return 'easyJet'
    if host == 'www.theguardian.com': return 'Guardian'
    if host in ('www.bankofengland.co.uk', 'www.fca.org.uk', 'www.gov.uk'): return host
    return None  # Unknown ownership is not evidence of independence.


def source_quality(source, as_of):
    text = None
    if source.get('verification') == 'primary_retrieved':
        text = primary_text(source)
        kind = ('Search-index-only excerpt' if 'index' in source.get('retrieval_extent', '').lower()
                else 'Original primary document' if source.get('content_kind', 'verified_download') == 'verified_download'
                else 'Reviewed primary excerpt')
    elif source.get('verification') == 'secondary_reviewed':
        text = secondary_excerpt(source, REPO)
        kind = 'Independent-publisher secondary excerpt'
    else:
        kind = 'Unverified source reference'
    publication = source.get('publication_date')
    age = (date.fromisoformat(as_of) - date.fromisoformat(publication)).days if publication else None
    retrieval = source.get('retrieved_at')
    eligible = (not publication or publication <= as_of) and (not retrieval or retrieval[:10] <= as_of)
    return {'id': source['id'], 'kind': kind, 'publisher_group': publisher_group(source),
            'document_key': document_key(source), 'publication_date': publication,
            'reporting_period': source['reporting_period'], 'retrieved_at': retrieval,
            'age_days': age, 'currentness': 'Not established' if age is None else 'Review due' if age > 90 else 'Within review window',
            'eligible_at_cutoff': eligible, 'primary_content_sha256': source.get('primary_content_sha256'),
            'excerpt_sha256': source.get('text_sha256'), 'limitation': source.get('limitation', ''),
            'url': source['url'], 'text': text}


def _claims(data, review):
    claims = {c['id']: {'id': c['id'], 'statement': c['statement'], 'subject': c['asset_id'],
                       'period': c['reporting_period'], 'kind': c['kind'], 'source_ids': c['source_ids'], 'previous_verification': c.get('verification'),
                       'supersedes': c.get('supersedes'), 'updates': c.get('updates')}
              for c in data['claims']}
    for row in review.get('observations', []):
        c = row['candidate']; segment = row['segment']
        if (c['claim_id'] in claims or c['subject'] not in (data['enterprise_twin_id'], data['industry_twin_id'])
                or c['authority'] != 'candidate_intelligence' or row.get('accepted_observation') is not False
                or segment['content'] != c['statement'] or digest(c['statement']) != digest(segment['content'])):
            raise ValueError('Candidate identity/scope/authority conflict')
        import hashlib
        if segment['content_hash'] != hashlib.sha256(segment['content'].encode()).hexdigest():
            raise ValueError('Candidate passage digest mismatch')
        claims[c['claim_id']] = {'id': c['claim_id'], 'statement': c['statement'], 'subject': c['subject'],
            'period': c['time_scope'], 'kind': 'candidate_observation', 'source_ids': [row['source_id']],
            'segment_id': segment['segment_id']}
    return claims


def claim_quality(claim, sources, quality, review, as_of):
    links = []
    if review:
        if (review['assertion_digest'] != digest(claim['statement']) or review['entity_id'] != claim['subject']
                or review['period'] != claim['period']):
            raise ValueError('Support review belongs to another assertion, entity or period')
        for link in review['links']:
            if link['source_id'] not in claim['source_ids'] or link['source_id'] not in sources:
                raise ValueError('Support review invents claim/source lineage')
            s = sources[link['source_id']]; q = quality[s['id']]
            if (link.get('assertion_digest') != digest(claim['statement']) or not link.get('reason')
                    or not link.get('reviewed_by') or not link.get('reviewed_at') or link['reviewed_at'] > as_of):
                raise ValueError('Unbound or undated semantic support review')
            if claim['subject'] not in s.get('entity_ids', []):
                raise ValueError('Industry or another enterprise source cannot establish entity-specific support')
            if link['support'] not in ('direct', 'context', 'contradicts'):
                raise ValueError('Unsupported semantic review class')
            located = (s.get('content_kind') != 'reviewed_web_excerpt' or any(e['quote'] == link['quote'] and e['locator'] == link['locator'] for e in s.get('excerpts', [])))
            present = bool(located and q['text'] and link['quote'] in q['text'] and link.get('locator'))
            exact = (present and link['support'] == 'direct' and q['eligible_at_cutoff']
                     and q['kind'] not in ('Search-index-only excerpt', 'Unverified source reference'))
            links.append({**deepcopy(link), 'passage_present': present, 'exact_support_reviewed': exact,
                          'source_kind': q['kind'], 'eligible_at_cutoff': q['eligible_at_cutoff'], 'publisher_group': q['publisher_group'],
                          'assertion_origin': s.get('assertion_origin'), 'content_digest': s.get('text_sha256') or s.get('primary_content_sha256'), 'document_key': q['document_key']})
    direct = [l for l in links if l['exact_support_reviewed'] and not quality[l['source_id']].get('superseded_by')]
    historical = any(l['exact_support_reviewed'] and quality[l['source_id']].get('superseded_by') for l in links)
    # A different publisher reporting the SAME management assertion is not an
    # independent measurement. Unknown origins and duplicate documents never count.
    independent_pairs = []
    for i, a in enumerate(direct):
        for b in direct[i+1:]:
            if (a['publisher_group'] and b['publisher_group'] and a['publisher_group'] != b['publisher_group']
                    and a['assertion_origin'] and b['assertion_origin'] and a['assertion_origin'] != b['assertion_origin']
                    and a['document_key'] != b['document_key'] and a['content_digest'] != b['content_digest']
                    and a.get('independence_basis') and b.get('independence_basis')):
                independent_pairs.append([a['source_id'], b['source_id']])
    contradictory = [l for l in links if l['support'] == 'contradicts' and l['passage_present'] and l['eligible_at_cutoff']]
    state = ('Interpretation / unsupported assertion' if claim['kind'] in ('interpretation', 'unknown')
             else 'Contradictory evidence requires treatment' if contradictory
             else 'Exact passage support reviewed; candidate only' if direct
             else 'Historical support retained; source superseded' if historical
             else 'Exact assertion support not established')
    return {**claim, 'quality_state': state, 'links': links, 'direct_support_reviewed': bool(direct),
            'independent_corroboration': bool(independent_pairs), 'independent_pairs': independent_pairs,
            'contradictory_source_ids': [l['source_id'] for l in contradictory],
            'limitation': 'Review binds scope/period to a passage; it is not proof of causal truth or accepted canonical Evidence.'}


def graph_projection(data, review, claims):
    """Translate the existing overlay vocabulary into the owning semantic resolver."""
    original = semantic_projection(data)
    objects = [replace(o, kind='observation') for o in original.objects if o.kind == 'Observation']
    known = {o.record_id for o in objects}
    for key in ('assets', 'frameworks', 'capabilities', 'programmes', 'suppliers', 'candidates', 'gaps'):
        rows = [{'id': k, 'title': k} for k in data[key]] if key == 'assets' else data[key]
        for row in rows:
            if row['id'] in known: continue
            objects.append(SemanticObject(row['id'], key, row.get('title', row['id']), data['enterprise_twin_id'],
                tuple(row.get('claim_ids', [])), 'Period unspecified', 'Unassessed', 'candidate_intelligence',
                data['assessment_id'], '', False, 'Read-only public research projection', original_id=row['id'], validation_status='candidate'))
            known.add(row['id'])
    for c in claims.values():
        if c['id'] not in known:
            objects.append(SemanticObject(c['id'], 'observation', c['statement'], c['subject'], tuple(c['source_ids']),
                c['period'], 'Candidate', 'candidate_intelligence', data['assessment_id'], '', False,
                'Not accepted Evidence', original_id=c['id'], validation_status='candidate'))
            known.add(c['id'])
    edges = deepcopy(data['relationships']) + deepcopy(review.get('relationships', []))
    if len({e['id'] for e in edges}) != len(edges): raise ValueError('Relationship ID reuse')
    for edge in edges:
        objects.append(SemanticObject(edge['id'], 'relationship', edge['predicate'], edge['subject'],
            tuple(edge['claim_ids']), edge.get('temporal_scope', 'Unknown'), 'Candidate', 'candidate_intelligence',
            data['assessment_id'], '', False, 'Not a canonical promotion', original_id=edge['id'], validation_status='candidate',
            attributes={**edge, 'source': edge['subject'], 'target': edge['object'], 'relationship_type': edge['predicate']}))
    return SemanticTwin(tuple(objects), ())


def relationship_quality(resolved, claims, known_edges):
    edge = resolved.relationship.attributes
    refs = edge['claim_ids']
    if set(refs) - set(claims): raise ValueError('Relationship has unresolved evidence/Observation refs')
    assessed = edge.get('assessment', {})
    status = assessed.get('status', 'factual' if edge.get('verified') else 'hypothesis')
    if status not in ('factual', 'inference', 'hypothesis', 'contradicted', 'superseded', 'unknown'):
        raise ValueError('Unknown relationship assessment')
    bound = bool(assessed.get('reason') and assessed.get('edge_digest') == digest({k:edge[k] for k in ('id','subject','predicate','object','claim_ids','temporal_scope')})) if assessed else False
    if assessed and not bound: raise ValueError('Relationship review no longer matches its endpoints/evidence/period')
    direct = bool(refs) and all(claims[r]['direct_support_reviewed'] for r in refs)
    factual_binding = bool(assessed.get('explicit_relationship') == {'subject': edge['subject'], 'predicate': edge['predicate'], 'object': edge['object']})
    # Joining two evidenced endpoints or a contextual regulatory fact cannot prove
    # their causal edge. A causal mechanism requires its own governed validation.
    causal = assessed.get('causal') is True or edge['predicate'] in ('causes', 'delivers', 'caused_by')
    if assessed and status == 'factual' and any(claims[r]['subject'] != assessed.get('entity_id') for r in refs):
        raise ValueError('Context from another entity/industry cannot prove an enterprise edge')
    if status == 'factual' and causal:
        raise ValueError('Candidate context/correlation cannot establish proven causation')
    state = STATES[5]
    if resolved.resolved and status != 'unknown':
        if status == 'superseded':
            if not assessed.get('superseded_by') or assessed['superseded_by'] not in known_edges:
                raise ValueError('Supersession must retain and identify an actual successor')
            state = STATES[4]
        elif status == 'contradicted':
            if not assessed.get('contradicting_claim_ids') or set(assessed['contradicting_claim_ids']) - set(claims):
                raise ValueError('Contradiction needs retained counterevidence')
            if not all(claims[c]['direct_support_reviewed'] for c in assessed['contradicting_claim_ids']):
                raise ValueError('Contradicted state needs supported counterevidence, not unverified context')
            state = STATES[3]
        elif status == 'factual' and bound and direct and factual_binding:
            state = STATES[0]
        elif status == 'inference' and bound and refs and all(any(l['passage_present'] and l['eligible_at_cutoff'] and l['source_kind'] not in ('Search-index-only excerpt', 'Unverified source reference') for l in claims[r]['links']) for r in refs):
            state = STATES[1]
        else:
            state = STATES[2]
    return {'id': edge['id'], 'subject': edge['subject'], 'object': edge['object'], 'predicate': edge['predicate'],
            'state': state, 'scope': assessed.get('entity_id', 'Scope not reviewed'), 'period': edge.get('temporal_scope', 'Not recorded'),
            'claim_ids': refs, 'evidence_ids': sorted({s for r in refs for s in claims[r]['source_ids']}),
            'reason': assessed.get('reason', 'Legacy verification flag alone does not establish an exact, current causal relationship'),
            'causation_proven': False, 'legacy_verified_flag': bool(edge.get('verified')), 'resolution': resolved.status,
            'missing_evidence': assessed.get('missing_evidence', ['Endpoint/period/semantic review outstanding']),
            'superseded_by': assessed.get('superseded_by'), 'contradicting_claim_ids': assessed.get('contradicting_claim_ids', [])}


def assess(data, review, as_of):
    validate(data)
    if (review.get('version') != 1 or review.get('authority') != 'candidate_intelligence' or review.get('enterprise_id') != data['enterprise_twin_id']
            or review.get('baseline_digest') != digest(data) or review['as_of'] > as_of or as_of > date.today().isoformat()):
        raise ValueError('Understanding review baseline/scope/cut-off mismatch')
    sources = {s['id']: s for s in data['sources']}
    for s in review.get('sources', []):
        if s.get('research_domain') != data.get('research_domain', 'banking'): raise ValueError('Cross-domain source review')
        if s['id'] in sources: raise ValueError('Existing source identity must not be overwritten')
        sources[s['id']] = s
    quality = {sid: source_quality(s, as_of) for sid, s in sources.items()}
    for sid, source in sources.items():
        prior = source.get('supersedes_source_id')
        if prior:
            if (prior not in sources or prior == sid or sources[prior]['reporting_period'] != source['reporting_period']
                    or not publisher_group(source) or publisher_group(sources[prior]) != publisher_group(source)
                    or not source.get('entity_ids') or set(sources[prior].get('entity_ids', [])) != set(source['entity_ids'])
                    or not source.get('supersession_reason')):
                raise ValueError('Source supersession requires a retained same-period predecessor and reason')
            quality[prior]['superseded_by'] = sid
            quality[sid]['supersedes_source_id'] = prior
    for sid in sources:
        seen = set(); cur = sid
        while quality[cur].get('superseded_by'):
            if cur in seen: raise ValueError('Cyclic source supersession')
            seen.add(cur); cur = quality[cur]['superseded_by']
    raw = _claims(data, review)
    for o in review.get('observations', []):
        c = o['candidate']; segment = o['segment']; source = sources[o['source_id']]
        if (c['source_segment_id'] != segment['segment_id'] or c['source_asset_id'] != segment['asset_id']
                or not segment['source_location'].startswith(source['url'] + ' [')):
            raise ValueError('Candidate segment/source lineage mismatch')
    annotations = {r['claim_id']: r for r in review.get('claim_reviews', [])}
    if len(annotations) != len(review.get('claim_reviews', [])) or set(annotations) - set(raw):
        raise ValueError('Duplicate or unresolved assertion review')
    for cid, annotation in annotations.items():
        extra = annotation.get('additional_source_ids', [])
        if extra:
            if (not annotation.get('source_link_reason') or annotation['assertion_digest'] != digest(raw[cid]['statement'])
                    or set(extra) - set(sources)):
                raise ValueError('Additional candidate provenance needs a bound reason and known sources')
            raw[cid]['original_source_ids'] = list(raw[cid]['source_ids'])
            raw[cid]['candidate_additional_source_ids'] = sorted(set(extra))
            raw[cid]['source_ids'] = sorted(set(raw[cid]['source_ids']) | set(extra))
    claims = {cid: claim_quality(c, sources, quality, annotations.get(cid), as_of) for cid, c in raw.items()}
    twin = graph_projection(data, review, claims)
    all_edges = {r.relationship.record_id for r in resolve_relationships(twin)}
    edges = [relationship_quality(r, claims, all_edges) for r in resolve_relationships(twin)]
    for edge in edges:
        if edge['scope'] not in (data['enterprise_twin_id'], data['industry_twin_id'], 'Scope not reviewed'):
            raise ValueError('Relationship review crosses enterprise boundary')
    conclusions = []
    by_edge = {e['id']: e for e in edges}
    for e in edges:
        if e['superseded_by']:
            successor = by_edge[e['superseded_by']]
            if any(e[k] != successor[k] for k in ('subject','object','predicate')):
                raise ValueError('Supersession cannot silently change relationship scope')
    successors = {e['id']: e['superseded_by'] for e in edges if e['superseded_by']}
    for eid in successors:
        visited = set(); current = eid
        while current in successors:
            if current in visited: raise ValueError('Cyclic/self supersession')
            visited.add(current); current = successors[current]
    for c in review.get('conclusions', []):
        if not c['claim_ids'] or set(c['claim_ids']) - set(claims) or set(c.get('relationship_ids', [])) - all_edges:
            raise ValueError('Conclusion breaks evidence lineage')
        if not c.get('missing_evidence') or c.get('entity_id') != data['enterprise_twin_id']:
            raise ValueError('Conclusion must preserve scope and material missing evidence')
        if c.get('kind') not in ('factual', 'inference', 'hypothesis', 'unknown'):
            raise ValueError('Conclusion must disclose its reasoning class')
        if c['kind'] == 'factual' and (len(c['claim_ids']) != 1 or c['statement'] != claims[c['claim_ids'][0]]['statement']
                or not claims[c['claim_ids'][0]]['direct_support_reviewed'] or claims[c['claim_ids'][0]]['subject'] != c['entity_id']):
            raise ValueError('Factual conclusion must preserve one exact supported assertion, not invent entailment')
        conclusions.append({**deepcopy(c), 'support': [claims[r] for r in c['claim_ids']], 'authority': 'candidate_intelligence'})
    for conflict in review.get('contradictions', []):
        if len(conflict['claim_ids']) < 2 or set(conflict['claim_ids']) - set(claims) or not conflict.get('treatment'):
            raise ValueError('Conflict requires explicit retained claims and treatment')
    dossier = coverage(data, as_of)['dossier']
    for row in dossier:
        row['reviewed_candidate_ids'] = sorted(cid for cid, cr in annotations.items() if row['id'] in cr.get('domains', [])
            and claims[cid]['direct_support_reviewed'] and claims[cid]['subject'] == data['enterprise_twin_id'])
        row['completion'] = 'Not certified; candidate passages do not establish full dossier depth'
    stats = {'candidate_claims': len(claims), 'exact_support_reviewed': sum(c['direct_support_reviewed'] for c in claims.values()),
        'independent_corroborated_claims': sum(c['independent_corroboration'] for c in claims.values()),
        'relationship_states': dict(Counter(e['state'] for e in edges)),
        'unresolved_conflicts': len(review.get('contradictions', [])), 'evidence_supported_causal_outcomes': 0,
        'reviewed_company_outcome_observations': sum(bool(cr.get('outcome_class')) and claims[cid]['direct_support_reviewed'] for cid, cr in annotations.items()),
        'dossier_dimensions_with_new_scoped_passages': sum(bool(row['reviewed_candidate_ids']) for row in dossier)}
    next_tasks = deepcopy(research_plan(data, as_of)['tasks'])
    task_index = {t['id']: t for t in next_tasks}
    for follow in review.get('follow_up_tasks', []):
        if follow['task_id'] not in task_index or not follow['claim_ids'] or set(follow['claim_ids']) - set(claims):
            raise ValueError('Follow-up must retain an existing task ID and resolved evidence')
        task = task_index[follow['task_id']]
        task.update(prior_question=task['question'], question=follow['question'], rationale=follow['reason'],
                    refinement_claim_ids=follow['claim_ids'])
    return {'enterprise_id': data['enterprise_twin_id'], 'as_of': as_of, 'baseline_digest': digest(data),
        'authority': 'candidate_intelligence', 'stats': stats,
        'sources': [{k:v for k,v in q.items() if k != 'text'} for q in quality.values()],
        'claims': list(claims.values()), 'relationships': edges, 'conclusions': conclusions,
        'contradictions': deepcopy(review.get('contradictions', [])), 'retained_unknowns': deepcopy(data['gaps']),
        'dossier': dossier, 'next_research': next_tasks,
        'maturity': 'IT-001 maturity not certified; full criteria and required human validation remain outstanding',
        'automatic_acceptance': False, 'pipeline_mutation': False}


def before_after(data, review, as_of):
    baseline = {'version': 1, 'authority': 'candidate_intelligence', 'enterprise_id': data['enterprise_twin_id'],
                'baseline_digest': digest(data), 'as_of': as_of}
    before = assess(data, baseline, as_of); after = assess(data, review, as_of)
    return {'before': before['stats'], 'after': after['stats'],
            'unchanged_existing_claim_ids': sorted(c['id'] for c in data['claims']),
            'unchanged_existing_relationship_ids': sorted(r['id'] for r in data['relationships']),
            'gaps_automatically_closed': [], 'canonical_mutation': False,
            'limitation': 'Same stricter v3 review rules before/after; v2 source_supported counts are not exact-assertion review counts.'}


def replay_research(data, review):
    """Reproduce the retained acquisition waves through v2, without network/store writes."""
    from .cycle import run_cycle
    sources={s['id']:s for s in review['sources']};checkpoint=None
    for wave in review['acquisition_plan']:
        submissions=[]
        for sid in wave['source_ids']:
            source=sources[sid];task=review['source_task_ids'][sid]
            submissions.append({'task_id':task,'source':source,'subject_id':source['entity_ids'][0],
                'effect':'new','target_claim_id':None,
                'rationale':'Candidate passage for scoped evidence and relationship assessment; no automatic acceptance.',
                'revisit_reason':'Additional source/period to deepen or challenge an existing acquisition.'})
        checkpoint=run_cycle(data,review['as_of'],submissions,previous=checkpoint,
                             revisit_task_ids=wave['revisit_task_ids'])
    return checkpoint


def report_markdown(data, review, as_of):
    x=assess(data,review,as_of);delta=before_after(data,review,as_of)
    lines=[f"# {data['enterprise_name']} — Enterprise Understanding before/after",'',
        f"Cut-off: {as_of}. Baseline overlay SHA-256: `{digest(data)}`.",
        'Candidate reasoning only. Existing canonical identities, research history and Pipeline remain unchanged.','',
        '| Same v3 assessment rule | Before | After |','| --- | ---: | ---: |']
    for k in ('candidate_claims','exact_support_reviewed','independent_corroborated_claims','reviewed_company_outcome_observations','evidence_supported_causal_outcomes','unresolved_conflicts','dossier_dimensions_with_new_scoped_passages'):
        lines.append(f"| {k} | {delta['before'][k]} | {delta['after'][k]} |")
    lines+=['','A zero before means no qualifying v3 semantic review, not an absence of prior facts. Record counts are not maturity. Exact support is attributable, scope-bounded support, not independent proof of the real-world outcome. No material gap is automatically closed.','',
        '## Material understanding changes']
    for c in x['conclusions']:
        lines += ['',f"### {c['title']}",f"Class: **{c['kind']}**. {c['statement']}",'',
            '**Change:** '+c['change_from_v2'],'','**Missing evidence:** '+ '; '.join(c['missing_evidence']),
            '**Supporting candidate Observation / claim IDs:** '+', '.join(c['claim_ids']),
            '**Relationship assessments:** '+', '.join(c['relationship_ids'])]
    lines+=['','## Relationships','| ID | State | Period | Missing evidence |','| --- | --- | --- | --- |']
    for e in x['relationships']:
        if e['id'].startswith('V3-'):lines.append(f"| {e['id']} | {e['state']} | {e['period']} | {'; '.join(e['missing_evidence'])} |")
    lines+=['','Causation is not proven for any edge. Legacy verified flags remain in the original overlay; the v3 exact scoped review does not overwrite them.','', '## Unresolved contradictions / scope tensions']
    for conflict in x['contradictions']:lines+=['',conflict['id']+': '+conflict['status'],conflict['treatment'],'Claims: '+', '.join(conflict['claim_ids'])]
    if not x['contradictions']:lines+=['No new explicit conflict recorded; this is not a claim that contradictions are absent.']
    lines+=['','## Source acquisition and limits']
    for source in review['sources']:
        lines += [f"- [{source['title']}]({source['url']}): published {source.get('publication_date') or 'Unknown'}, period {source['reporting_period']}, retrieved {source['retrieved_at']}. Excerpt hash `{source['text_sha256']}`; original bytes not archived. Assertion origin: {source['assertion_origin']}."]
    for limitation in review.get('source_limitations',[]):lines+=['- '+limitation['status']+' — '+limitation['url']]
    lines+=['','Independent secondary publishing is not independent measurement when the underlying assertion still originates in management. The Guardian excerpt is an independently published report of a plan, not corroborated achievement. No copied, syndicated or differently labelled company page increases independence.','',
        '## Dossier and next research']
    for row in x['dossier']:lines.append(f"- {row['label']}: {len(row['reviewed_candidate_ids'])} new scoped passages; {'; '.join(row['deficiencies'])}.")
    lines+=['','Next high-value tasks:']+[f"- {t['id']}: {t['question']} Why: {t['rationale']}" for t in x['next_research'][:3]]
    lines+=['','## Remaining qualification limits',x['maturity'],
        'No original-byte archive is claimed. Current contract terms, accountable buyers, budgets and procurement remain unknown. No new opportunity hypothesis, canonical promotion or Pipeline qualification was performed.']
    return '\n'.join(lines)+'\n'
