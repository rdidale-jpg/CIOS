"""Bounded candidate research waves over the existing public assessment spine.

No network client, canonical store or write authority lives here. Generated objects
reuse existing semantic/evidence contracts; a checkpoint is operational evidence,
not an accepted Twin, RG-002 completion decision or publisher-authenticity proof.
"""
from copy import deepcopy
from datetime import date
import hashlib
import json

from ..blueprint_import.semantic_twin import SemanticObject, SemanticTwin
from ..enterprise_intelligence.semantic import CandidateClaim, SourceSegment
from ..memory.models import stable_observation_fingerprint
from .diagnostic import assess
from .model import (validate, primary_claim_supported, claim_segment, candidate_claim,
                    evidence_item)
from .source_import import import_proposal

# §5.2 of the existing High-Fidelity contract. These selectors detect deficiencies;
# they do not replace its dossier fields, IT-001 tiers or 22-dimension maturity gate.
DOSSIER = (
    ('corporate', 'Corporate identity and structure', ('corporate', 'ownership'), 3),
    ('leadership', 'Leadership and governance', ('leadership', 'governance'), 3),
    ('strategy', 'Strategy', ('strategy',), 3),
    ('financials', 'Financial intelligence', ('financials',), 4),
    ('products', 'Products, services and offers', ('products', 'services', 'offers'), 3),
    ('technology', 'Technology and digital estate', ('technology',), 3),
    ('operations', 'Operating model', ('operations', 'operating-model'), 4),
    ('customers', 'Customers and markets', ('customers', 'market'), 3),
    ('suppliers', 'Suppliers and ecosystem', ('suppliers',), 3),
    ('procurement', 'Procurement and buying', ('procurement',), 3),
    ('transformation', 'Transformation', ('programmes', 'transformation'), 4),
    ('events', 'Events and analyst intelligence', ('events', 'analyst'), 3),
    ('opportunities', 'Opportunity reasoning', ('opportunities',), 1),
    ('uncertainty', 'Evidence and uncertainty', ('uncertainty',), 3),
)
FAMILIES = {
    'filing': 'Official dated annual/interim results and strategy disclosures',
    'regulator': 'Applicable regulator / official statistical publications',
    'supplier': 'Named supplier disclosure corroborated by the enterprise or contract',
    'procurement': 'Official procurement, award and contract notices; otherwise retain Unknown',
    'independent': 'Lawfully accessible independent reporting / analyst challenge',
    'customer': 'Authorised customer validation; never infer buying intent from investment',
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def _day(as_of):
    value = date.fromisoformat(as_of)
    if value > date.today():
        raise ValueError('Research cut-off cannot be in the future')
    return value


def coverage(data, as_of):
    """Conservative, reproducible deficiency screen; not full maturity certification."""
    validate(data)
    today = _day(as_of)
    if date.fromisoformat(data['assessed_at']) > today:
        raise ValueError('Assessment follows research cut-off')
    inventory = assess(data)
    claims = {c['id']: c for c in data['claims']}
    sources = {s['id']: s for s in data['sources']}
    rows = []
    for key, label, domains, importance in DOSSIER:
        # Industry statements cannot satisfy enterprise dossier coverage.
        selected = [c for c in claims.values() if c['asset_id'] == data['enterprise_twin_id']
                    and c['domain'] in domains and c['kind'] not in ('unknown', 'interpretation')]
        supported = [c for c in selected if primary_claim_supported(data, c)
                     and all('index' not in sources[s].get('retrieval_extent', '').lower() for s in c['source_ids'])]
        refs = sorted({s for c in selected for s in c['source_ids']})
        publishers = sorted({sources[s]['publisher'] for s in refs})
        periods = sorted({c['reporting_period'] for c in selected})
        flags = []
        if not selected: flags.append('No mapped enterprise factual claim; inspect full dossier')
        elif not supported: flags.append('No passage-supported enterprise claim')
        if len(publishers) < 2: flags.append('Independent/source-family corroboration not established')
        if len(periods) < 2: flags.append('Comparable multi-period history not established')
        if key == 'opportunities': flags.append('Research hypotheses do not establish customer demand')
        if key == 'uncertainty': flags.append('Open Unknowns and Contradictions require explicit treatment')
        # Multiple publishers/period labels are only an inventory, never proof of
        # independence or comparability; causal understanding is still unassessed.
        flags.append('Causal depth and complete dossier fields not assessed automatically')
        rows.append({'id': key, 'label': label, 'importance': importance,
                     'claim_ids': sorted(c['id'] for c in selected),
                     'supported_claim_ids': sorted(c['id'] for c in supported),
                     'source_ids': refs, 'publishers': publishers, 'period_labels': periods,
                     'deficiencies': flags, 'maturity': 'Not certified'})
    source_review = []
    for s in data['sources']:
        published = s.get('publication_date')
        age = (today - date.fromisoformat(published)).days if published else None
        source_review.append({'source_id': s['id'], 'age_days': age,
            'date_status': 'Publication date unknown' if age is None else 'Review due (>90 days)' if age > 90 else 'Within 90-day review window',
            'extent': s.get('retrieval_extent', s.get('content_kind', 'Citation only')),
            'limitation': s.get('limitation', ''),
            'original_verified': bool(s.get('primary_content_sha256'))})
    return {'enterprise_id': data['enterprise_twin_id'], 'as_of': as_of,
            'baseline_digest': digest(data), 'diagnostic': inventory, 'dossier': rows,
            'source_review': source_review,
            'limitation': 'A domain/publisher/period count is not completeness, corroboration, freshness or IT-001 maturity.'}


def research_plan(data, as_of, limit=3):
    if type(limit) is not int or not 1 <= limit <= 10:
        raise ValueError('Select between one and ten tasks')
    report = coverage(data, as_of)
    tasks = []
    for row in report['dossier']:
        if row['id'] in ('opportunities', 'uncertainty'):
            continue  # Existing uncertainty register supplies question-specific work.
        missing = not row['claim_ids']
        score = row['importance'] * 10 + (9 if missing else 6 if not row['supported_claim_ids'] else 3)
        families = ['filing', 'independent']
        if row['id'] in ('suppliers', 'technology', 'transformation'): families += ['supplier', 'procurement']
        if row['id'] == 'procurement': families += ['procurement', 'customer']
        tasks.append({'id': 'R-' + data['enterprise_twin_id'] + '-' + row['id'],
            'topic': row['id'], 'title': row['label'], 'priority_score': score,
            'rationale': '; '.join(row['deficiencies']),
            'question': f"What dated, enterprise-specific evidence establishes {row['label'].lower()} for {data['enterprise_name']}, and what contradicts the current account?",
            'target_claim_ids': row['claim_ids'], 'source_families': families,
            'source_routes': [s['url'] for s in data['sources'] if s['id'] in row['source_ids']],
            'closure_test': 'Located primary passage, explicit scope/period, contrary evidence search and complete applicable dossier fields; separate governed review required.'})
    for gap in report['diagnostic']['active_gaps']:
        commercial = any(w in (gap['title'] + ' ' + gap.get('question', '')).lower()
                         for w in ('customer buying', 'customer demand', 'seller access'))
        score = (12 if commercial else {'High': 48, 'Medium': 28, 'Low': 18}.get(gap.get('priority'), 18))
        tasks.append({'id': gap['id'], 'topic': 'registered-gap', 'title': gap['title'],
            'priority_score': score, 'rationale': gap.get('decision_impact', gap['question']),
            'question': gap['question'], 'target_claim_ids': [],
            'source_families': ['customer'] if commercial else ['filing', 'regulator', 'independent'],
            'source_routes': [], 'closure_test': gap.get('required_evidence', gap['question'])})
    for task in tasks:
        task['search_queries'] = [data['enterprise_name'] + ' ' + task['title'] + ' official disclosure ' + as_of[:4],
                                  data['enterprise_name'] + ' ' + task['title'] + ' delay cancellation risk contrary evidence']
    tasks.sort(key=lambda t: (-t['priority_score'], t['id']))
    return {'coverage': report, 'tasks': tasks, 'selected_task_ids': [t['id'] for t in tasks[:limit]],
            'selection_rule': 'Materiality 1–4 ×10 + deficiency 3/6/9; registered High gaps 48. Customer qualification deferred (12). Stable ID tie-break.',
            'source_families': FAMILIES}


def semantic_projection(data):
    """Use the canonical semantic projection vocabulary, with candidate authority."""
    validate(data)
    records = []
    for c in data['claims']:
        item = candidate_claim(data, c)
        segment = claim_segment(data, c)
        evidence = evidence_item(data, c)
        records.append(SemanticObject(c['id'], 'Observation', c['statement'], item.subject,
            evidence.lineage,
            c['reporting_period'], item.confidence, 'candidate_intelligence', segment.asset_id,
            evidence.source_location, False, 'Not accepted canonical Evidence / Observation',
            original_id=c['id'], references=tuple(c['source_ids']), domains=(c['domain'],),
            validation_status='candidate', attributes={'candidate_claim': item.to_dict(), 'segment': segment.to_dict(), 'evidence_item': evidence.to_dict()}))
    for edge in data['relationships']:
        records.append(SemanticObject(edge['id'], 'Relationship', edge['predicate'], edge['subject'],
            tuple(edge['claim_ids']), edge.get('temporal_scope', 'Period not recorded'),
            'Source-supported edge' if edge.get('verified') else 'Interpretation',
            'candidate_intelligence', data['assessment_id'], '', False,
            'Candidate graph; endpoint evidence does not prove all connecting edges',
            original_id=edge['id'], references=(edge['subject'], edge['object']), attributes=deepcopy(edge), validation_status='candidate'))
    return SemanticTwin(tuple(records), ())


def connected_context(data):
    """Return evidenced and interpretive paths; never invent missing graph edges."""
    groups = {key: {r['id'] for r in data[key]} for key in
              ('frameworks', 'capabilities', 'suppliers', 'programmes', 'candidates')}
    edges = []
    for projected in semantic_projection(data).of_kind('Relationship'):
        edge = projected.attributes
        row = deepcopy(edge)
        row['evidence_locations'] = [claim_segment(data, next(c for c in data['claims'] if c['id'] == cid)).source_location for cid in edge['claim_ids']]
        row['qualification'] = 'Source-supported within recorded period' if edge.get('verified') else 'Interpretation; relationship unverified'
        edges.append(row)
    gaps = []
    for category in ('frameworks', 'capabilities', 'suppliers', 'programmes'):
        missing = sorted(groups[category] - {e[k] for e in edges for k in ('subject', 'object')})
        if missing: gaps.append({'category': category, 'unconnected_ids': missing})
    return {'edges': edges, 'unconnected_objects': gaps,
            'unmodelled_relationship_classes': ['Contract award / renewal / expiry', 'Measured programme-to-business outcome'],
            'limitation': 'These classes are not structured in the current overlays; missing is not evidence of absence. Industry context is not enterprise proof.'}


def _checkpoint(previous, data, as_of):
    if not previous: return []
    body = {k: v for k, v in previous.items() if k != 'checkpoint_digest'}
    if previous.get('version') != 1:
        raise ValueError('Unsupported checkpoint version')
    if digest(body) != previous.get('checkpoint_digest'):
        raise ValueError('Checkpoint digest mismatch')
    if previous['baseline_digest'] != digest(data) or previous['enterprise_id'] != data['enterprise_twin_id']:
        raise ValueError('Checkpoint baseline changed; explicit rebase review required')
    if previous['as_of'] > as_of:
        raise ValueError('Cannot resume before previous research cut-off')
    return deepcopy(previous['waves'])


def run_cycle(data, as_of, submissions=(), limit=3, previous=None):
    """Acquire supplied permitted source files, extract exact passages, propose review.

    Reviewer effects are proposed judgements, NOT automatic semantic entailment,
    rejection of history, closure of an Unknown or canonical acceptance.
    """
    plan = research_plan(data, as_of, limit)
    history = _checkpoint(previous, data, as_of)
    tasks = {t['id']: t for t in plan['tasks']}
    attempted = {p['task_id'] for w in history for p in w['proposals']}
    selected = [t['id'] for t in plan['tasks'] if t['id'] not in attempted][:limit]
    if len(submissions) > limit:
        raise ValueError('Wave exceeds selected task budget')
    proposals = []
    claims = {c['id']: c for c in data['claims']}
    seen_tasks = set()
    for submission in submissions:
        task_id = submission['task_id']
        if task_id not in selected or task_id in seen_tasks:
            raise ValueError('Evidence must address one selected task per submission')
        seen_tasks.add(task_id)
        imported = import_proposal(submission['path'], submission['metadata'])
        meta = imported['metadata']
        if date.fromisoformat(meta['retrieved_at'][:10]) > date.fromisoformat(as_of):
            raise ValueError('Acquisition follows research cut-off')
        target = submission.get('target_claim_id')
        effect = submission['effect']
        if effect not in ('strengthen', 'weaken', 'invalidate', 'new') or not submission.get('rationale'):
            raise ValueError('Explicit proposed effect and review rationale required')
        if target and (target not in claims or claims[target]['asset_id'] != data['enterprise_twin_id']):
            raise ValueError('Change target must be an existing same-enterprise claim')
        if (effect == 'new') != (target is None):
            raise ValueError('Existing-finding effects require explicit target lineage')
        if effect == 'invalidate' and meta['reporting_period'] != claims[target]['reporting_period']:
            raise ValueError('Incompatible periods cannot invalidate a historical finding')
        fingerprint = digest({'raw': imported['primary_content_sha256'], 'task': task_id,
                              'target': target, 'effect': effect, 'rationale': submission['rationale'], 'metadata': meta})
        if not 1 <= len(meta['reviewed_quotes']) <= 8:
            raise ValueError('Wave accepts at most eight reviewed passages per source')
        observations = []
        for quote in meta['reviewed_quotes']:
            text = quote['quote']
            if not 20 <= len(text.strip()) <= 4000:
                raise ValueError('Candidate passages need 20–4000 characters of context')
            sid = 'RS-' + digest({'url': meta['url'], 'hash': imported['primary_content_sha256']})[:20]
            segment = SourceSegment(sid + '::' + digest(quote)[:16], sid,
                quote['locator'], text, hashlib.sha256(text.encode()).hexdigest(),
                meta['url'] + ' [' + quote['locator'] + ']', 'candidate_intelligence', 'reviewed_supplied_file')
            obs = stable_observation_fingerprint(data['enterprise_twin_id'], 'research_excerpt', text,
                                                 tasks[task_id]['topic'], meta['reporting_period'])
            candidate = CandidateClaim('RC-' + obs.rsplit('-', 1)[-1][:20], 'research_excerpt', text,
                sid, segment.segment_id, 'enterprise', data['enterprise_twin_id'],
                tasks[task_id]['topic'], text, meta['reporting_period'], data['industry_name'],
                data['enterprise_twin_id'], 'Provenance reviewed; semantic scope and atomicity pending',
                'candidate_intelligence', 'needs_governed_observation_review', [sid],
                [target] if target and effect in ('weaken', 'invalidate') else [])
            observations.append({'candidate': candidate.to_dict(), 'segment': segment.to_dict(),
                'observation_fingerprint': obs, 'accepted_observation': False})
        proposals.append({'id': 'RP-' + fingerprint[:24], 'task_id': task_id,
            'target_claim_id': target, 'proposed_effect': effect, 'rationale': submission['rationale'],
            'source_id': sid, 'source_metadata': meta, 'raw_sha256': imported['primary_content_sha256'],
            'text_sha256': imported['text_sha256'], 'candidates': observations,
            'supersession': {'predecessor_claim_id': target, 'state': 'Proposed; predecessor retained',
                'target_reporting_period': claims[target]['reporting_period'] if target else None,
                'new_reporting_period': meta['reporting_period'],
                'period_match': bool(target and claims[target]['reporting_period'] == meta['reporting_period'])},
            'status': 'Review required; no automatic finding change',
            'remaining_checks': ['Enterprise/scope/period entailment', 'Atomic observation and contrary evidence',
                'Source authorship and independence', 'Governed Evidence acceptance before Observation persistence']})
    wave = {'as_of': as_of, 'selected_task_ids': selected, 'proposals': proposals,
            'acquisition_status': 'Supplied file(s) reviewed' if proposals else 'Awaiting permitted source imports; no new evidence acquired',
            'retained_unknowns': deepcopy(data['gaps']),
            'retained_contradictions': [deepcopy(c) for c in data['claims'] if c['kind'] == 'contradiction'],
            'retained_claim_ids': sorted(claims),
            'next_actions': [tasks[t]['question'] for t in selected if t not in seen_tasks] +
                ['Adjudicate candidate provenance, scope and counterevidence before any governed update'] * bool(proposals)}
    wave['id'] = 'RW-' + digest(wave)[:24]
    if not history or history[-1]['id'] != wave['id']: history.append(wave)
    checkpoint = {'version': 1, 'enterprise_id': data['enterprise_twin_id'],
        'baseline_digest': digest(data), 'as_of': as_of, 'waves': history,
        'outcome': 'CONTINUE', 'canonical_mutation': False, 'automatic_qualification': False,
        'retained_history': deepcopy(data), 'retained_relationships': connected_context(data),
        'coverage': plan['coverage'],
        'pending_review_task_ids': sorted(attempted | seen_tasks),
        'change_proposals': {effect: [p['id'] for w in history for p in w['proposals'] if p['proposed_effect'] == effect]
                             for effect in ('strengthen', 'weaken', 'invalidate', 'new')},
        'remaining_tasks': [t for t in plan['tasks'] if t['id'] not in attempted | seen_tasks]}
    checkpoint['checkpoint_digest'] = digest(checkpoint)
    return checkpoint
