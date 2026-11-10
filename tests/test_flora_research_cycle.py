"""Bounded research without canonical or commercial authority."""
from copy import deepcopy
import hashlib
import json
import subprocess
import sys

import pytest
from cios.applications.flora.research_intelligence import cycle
from cios.applications.flora.research_intelligence.model import load_assessment, REPO
from cios.applications.flora.research_intelligence.mission_adapter import manifest, mission_owner
from cios.applications.flora.research_intelligence.cycle_views import render
from tests.test_flora_primary_enrichment import download
from tests.test_flora_research_intelligence import web

AS_OF = '2026-11-10'


def submission(data, tmp_path, effect='strengthen'):
    path, meta = download(tmp_path, text='Synthetic test disclosure: the operating programme was discontinued.')
    meta['reviewed_quotes'] = [{'quote': 'the operating programme was discontinued.', 'locator': 'Synthetic paragraph 1'}]
    meta['retrieved_at'] = AS_OF + 'T00:00:00+00:00'
    task = cycle.research_plan(data, AS_OF)['selected_task_ids'][0]
    target = next(c['id'] for c in data['claims'] if c['asset_id'] == data['enterprise_twin_id'])
    meta['reporting_period'] = next(c['reporting_period'] for c in data['claims'] if c['id'] == target)
    return {'task_id': task, 'path': str(path), 'metadata': meta, 'effect': effect,
            'target_claim_id': None if effect == 'new' else target,
            'rationale': 'Synthetic reviewer judgement only; test provenance and retention, not real company research.'}


@pytest.mark.parametrize('domain', ['banking', 'aviation'])
def test_reproducible_coverage_and_material_deficiency_plan(domain):
    data = load_assessment(domain); before = deepcopy(data)
    plan = cycle.research_plan(data, AS_OF)
    assert plan == cycle.research_plan(data, AS_OF)
    assert len(plan['coverage']['dossier']) == 14
    assert len(plan['selected_task_ids']) == 3
    assert plan['tasks'] == sorted(plan['tasks'], key=lambda t: (-t['priority_score'], t['id']))
    assert all(t['question'] and t['source_families'] and t['closure_test'] for t in plan['tasks'])
    assert all('customer' not in t['source_families'] for t in plan['tasks'][:3])
    assert data == before
    assert cycle.coverage(data, AS_OF)['baseline_digest'] == cycle.digest(before)


def test_industry_evidence_and_index_only_sources_do_not_fill_enterprise_dossier():
    data = load_assessment('aviation'); report = cycle.coverage(data, AS_OF)
    industry = {c['id'] for c in data['claims'] if c['asset_id'] != data['enterprise_twin_id']}
    for row in report['dossier']:
        assert not industry.intersection(row['claim_ids'])
        assert all('SRC-AV-Q326' not in c['source_ids'] and 'SRC-AV-HOL26' not in c['source_ids']
                   for c in data['claims'] if c['id'] in row['supported_claim_ids'])
    assert any(s['date_status'] == 'Publication date unknown' for s in report['source_review'])


def test_semantic_reuse_preserves_identities_and_excludes_canonical_authority():
    data = load_assessment('aviation'); twin = cycle.semantic_projection(data)
    assert {o.original_id for o in twin.objects} == {r['id'] for key in ('claims', 'relationships') for r in data[key]}
    assert all(not o.eligible_conclusion and o.governance == 'candidate_intelligence' for o in twin.objects)
    assert all(o.validation_status == 'candidate' for o in twin.objects)
    assert twin.enterprises == ()  # Never invent an accepted imported Enterprise identity.
    observation = twin.of_kind('Observation')[0]
    assert observation.attributes['candidate_claim']['source_segment_id'] == observation.attributes['segment']['segment_id']


def test_connected_context_keeps_verified_and_interpretive_edges_distinct():
    data = load_assessment('aviation'); context = cycle.connected_context(data)
    assert len(context['edges']) == len(data['relationships'])
    assert any(e['verified'] for e in context['edges']) and any(not e['verified'] for e in context['edges'])
    assert all(e['evidence_locations'] or not e['claim_ids'] for e in context['edges'])
    assert context['unmodelled_relationship_classes']
    assert {e['id'] for e in context['edges']} == {e['id'] for e in data['relationships']}


@pytest.mark.parametrize('effect', ['strengthen', 'weaken', 'invalidate', 'new'])
def test_new_evidence_proposes_effects_with_exact_passage_and_retained_history(tmp_path, effect):
    data = load_assessment(); before = deepcopy(data)
    item = submission(data, tmp_path, effect)
    result = cycle.run_cycle(data, AS_OF, [item])
    proposal = result['waves'][0]['proposals'][0]
    assert proposal['proposed_effect'] == effect
    assert result['change_proposals'][effect] == [proposal['id']]
    assert result['pending_review_task_ids'] == [item['task_id']]
    assert proposal['target_claim_id'] == item['target_claim_id']
    assert result['retained_history'] == before == data
    assert not result['canonical_mutation'] and not result['automatic_qualification']
    assert result['outcome'] == 'CONTINUE'
    candidate = proposal['candidates'][0]
    assert candidate['candidate']['statement'] == candidate['segment']['content'] == item['metadata']['reviewed_quotes'][0]['quote']
    assert candidate['segment']['content_hash'] == hashlib.sha256(candidate['segment']['content'].encode()).hexdigest()
    assert not candidate['accepted_observation']
    assert candidate['candidate']['source_asset_id'] == candidate['segment']['asset_id'] == proposal['source_id']
    assert candidate['candidate']['subject'] == data['enterprise_twin_id']
    assert candidate['candidate']['contradicting_ids'] == ([item['target_claim_id']] if effect in ('weaken', 'invalidate') else [])
    assert proposal['supersession']['state'] == 'Proposed; predecessor retained'
    assert result == cycle.run_cycle(data, AS_OF, [item])


def test_invalid_source_provenance_and_unlocated_passages_are_rejected(tmp_path):
    data = load_assessment(); item = submission(data, tmp_path)
    for change in ({'expected_sha256': '0'*64}, {'provenance_verified': False},
                   {'reviewed_quotes': [{'quote': 'A fabricated passage absent from the source', 'locator': 'p1'}]},
                   {'url': 'https://private.invalid/source'}, {'retrieved_at': '2026-11-11T00:00:00Z'}):
        broken = deepcopy(item); broken['metadata'].update(change)
        with pytest.raises(ValueError): cycle.run_cycle(data, AS_OF, [broken])


def test_claim_scope_effect_and_budget_validation(tmp_path):
    data = load_assessment(); item = submission(data, tmp_path)
    industry_claim = next(c['id'] for c in data['claims'] if c['asset_id'] != data['enterprise_twin_id'])
    for change in ({'task_id': 'not-selected'}, {'target_claim_id': 'AV-ICC'},
                   {'target_claim_id': industry_claim}, {'target_claim_id': None},
                   {'effect': 'accept'}, {'effect': 'new'}, {'rationale': ''}):
        with pytest.raises(ValueError): cycle.run_cycle(data, AS_OF, [{**item, **change}])
    with pytest.raises(ValueError): cycle.run_cycle(data, AS_OF, [item, item])
    with pytest.raises(ValueError): cycle.run_cycle(data, AS_OF, [item]*4)
    oversized = deepcopy(item); oversized['metadata']['reviewed_quotes'] *= 9
    with pytest.raises(ValueError, match='eight'): cycle.run_cycle(data, AS_OF, [oversized])
    mismatched = deepcopy(item); mismatched['effect'] = 'invalidate'; mismatched['metadata']['reporting_period'] = 'Different historical period'
    with pytest.raises(ValueError, match='periods'): cycle.run_cycle(data, AS_OF, [mismatched])
    for limit in (0, 11, True):
        with pytest.raises(ValueError): cycle.research_plan(data, AS_OF, limit)


def test_checkpoint_resume_preserves_wave_and_selects_next_work(tmp_path):
    data = load_assessment(); item = submission(data, tmp_path)
    first = cycle.run_cycle(data, AS_OF, [item])
    second = cycle.run_cycle(data, AS_OF, previous=first)
    assert second['waves'][0] == first['waves'][0]
    assert item['task_id'] not in second['waves'][-1]['selected_task_ids']
    assert first['retained_history'] == second['retained_history']
    assert cycle.run_cycle(data, AS_OF, previous=second) == second
    broken = deepcopy(first); broken['waves'][0]['proposals'][0]['proposed_effect'] = 'new'
    with pytest.raises(ValueError, match='digest'): cycle.run_cycle(data, AS_OF, previous=broken)
    changed = deepcopy(data); changed['assessment_id'] += '-changed'
    with pytest.raises(ValueError, match='baseline'): cycle.run_cycle(changed, AS_OF, previous=first)
    with pytest.raises(ValueError): cycle.run_cycle(load_assessment('aviation'), AS_OF, previous=first)


@pytest.mark.parametrize('domain', ['banking', 'aviation'])
def test_unacquired_evidence_is_not_claimed_and_history_is_unchanged(domain):
    data = load_assessment(domain); before = cycle.digest(data)
    report = cycle.run_cycle(data, AS_OF)
    assert 'no new evidence acquired' in report['waves'][0]['acquisition_status']
    assert report['waves'][0]['proposals'] == []
    assert report['retained_history'] == data
    assert cycle.digest(data) == before
    assert report['waves'][0]['retained_unknowns'] == data['gaps']


@pytest.mark.parametrize('domain', ['banking', 'aviation'])
def test_mission_uses_existing_researcher_schema_profiles_and_generator(domain):
    data = load_assessment(domain); output = manifest(data, AS_OF)
    owner = mission_owner(); owner.validate_manifest(output)
    rendered = owner.render(output)
    assert data['enterprise_twin_id'] in rendered
    assert 'TEL-001' not in json.dumps(output)
    assert output['governance_state'] == 'DRAFT'
    assert output['scope']['geography'] == [data.get('geography', 'Source-specific geography; enterprise and industry boundaries require review')]
    assert output['estimation_policy']['permitted_estimate_types'] == []
    assert output['research_priorities']['named_closure_targets']


def test_cli_exports_reproducible_local_bundle_and_refuses_overwrite(tmp_path):
    output = tmp_path / 'bundle'
    cmd = [sys.executable, 'tools/research/flora_cycle.py', '--enterprise', 'easyjet', '--as-of', AS_OF, '--output', str(output)]
    first = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    assert first.returncode == 0, first.stderr
    assert sorted(p.name for p in output.iterdir()) == ['checkpoint.json', 'commission.md', 'mission.json', 'plan.json']
    snapshot = {p.name: p.read_bytes() for p in output.iterdir()}
    assert subprocess.run(cmd, cwd=REPO, capture_output=True).returncode != 0
    assert snapshot == {p.name: p.read_bytes() for p in output.iterdir()}
    data = load_assessment(); item = submission(data, tmp_path)
    input_file = tmp_path / 'submissions.json'; input_file.write_text(json.dumps([item]))
    acquired = tmp_path / 'acquired'
    imported_cmd = [sys.executable, 'tools/research/flora_cycle.py', '--enterprise', 'lloyds', '--as-of', AS_OF,
                    '--submissions', str(input_file), '--output', str(acquired)]
    proc = subprocess.run(imported_cmd, cwd=REPO, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    raw = (tmp_path / 'source.txt').read_bytes()
    assert (acquired / 'sources' / hashlib.sha256(raw).hexdigest()).read_bytes() == raw
    checkpoint = json.loads((acquired / 'checkpoint.json').read_text())
    assert checkpoint['waves'][0]['proposals'][0]['raw_sha256'] == hashlib.sha256(raw).hexdigest()
    resumed = tmp_path / 'resumed'
    resumed_cmd = [sys.executable, 'tools/research/flora_cycle.py', '--enterprise', 'lloyds', '--as-of', AS_OF,
                   '--resume', str(acquired / 'checkpoint.json'), '--output', str(resumed)]
    proc = subprocess.run(resumed_cmd, cwd=REPO, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    mission = json.loads((resumed / 'mission.json').read_text())
    assert all(item['task_id'] not in t for t in mission['research_priorities']['named_closure_targets'])
    resumed_plan = json.loads((resumed / 'plan.json').read_text())
    assert item['task_id'] not in resumed_plan['selected_task_ids']
    assert mission['scope']['included_domains'] == [t['title'] for t in resumed_plan['tasks'] if t['id'] in resumed_plan['selected_task_ids']]


@pytest.mark.parametrize('slug', ['lloyds', 'easyjet'])
def test_existing_diagnostic_route_renders_research_cycle_and_evidence_links(web, slug):
    status, page = web('/enterprises/' + slug + '/research-diagnostic')
    assert status == 200
    assert 'Research Intelligence v2' in page and 'Next evidence wave' in page
    assert 'fourteen existing contract dimensions' in page
    assert 'Source freshness' in page and 'No new external evidence' in page
    assert 'Connected enterprise understanding' in page
    assert 'Home' in page and 'Pipeline' in page


def test_html_output_escapes_research_content():
    data = load_assessment(); data['gaps'][0]['title'] = '<script>evil</script>'
    assert '<script>evil' not in render(data, AS_OF)
    assert '&lt;script&gt;' in render(data, AS_OF)


def test_cutoff_validation_rejects_future_and_prebaseline_research():
    with pytest.raises(ValueError): cycle.coverage(load_assessment(), '2999-01-01')
    with pytest.raises(ValueError): cycle.coverage(load_assessment(), '2020-01-01')


@pytest.mark.parametrize('domain', ['banking', 'aviation'])
def test_real_reference_excerpt_produces_candidate_without_inventing_original_bytes(domain):
    data = load_assessment(domain); item = cycle.reference_submission(data)
    result = cycle.run_cycle(data, AS_OF, [item]); proposal = result['waves'][0]['proposals'][0]
    assert proposal['raw_sha256'] is None and not proposal['original_bytes_archived']
    assert proposal['source_metadata']['retrieval_method'] == 'approved_web_research_tool'
    assert proposal['source_metadata']['retrieval_reference']
    assert proposal['source_metadata']['primary_content_sha256'] is None
    assert proposal['source_metadata']['text_sha256'] == proposal['text_sha256']
    assert result['retained_history'] == data
    assert result['waves'][0]['retained_unknowns'] == data['gaps']
    assert 'Latest retained primary-source review' in render(data, AS_OF)
    if domain == 'banking': assert 'SRC-LBG-AI' in proposal['equivalent_existing_source_ids']


def test_excerpt_acquisition_rejects_cross_domain_changed_text_and_fake_original_hash():
    data = load_assessment(); item = cycle.reference_submission(data)
    for change in ({'research_domain': 'aviation'}, {'text_sha256': '0'*64},
                   {'primary_content_sha256': '0'*64}, {'text_path': '/etc/passwd'},
                   {'verification': 'citation_only'}):
        broken = deepcopy(item); broken['source'].update(change)
        with pytest.raises(ValueError): cycle.run_cycle(data, AS_OF, [broken])


def test_cli_archives_excerpt_as_excerpt_without_fabricated_original_hash(tmp_path):
    data = load_assessment(); item = cycle.reference_submission(data)
    submitted = tmp_path / 'submitted.json'; submitted.write_text(json.dumps([item]))
    output = tmp_path / 'web-excerpt-bundle'
    proc = subprocess.run([sys.executable, 'tools/research/flora_cycle.py', '--enterprise', 'lloyds',
        '--as-of', AS_OF, '--submissions', str(submitted), '--output', str(output)], cwd=REPO, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    expected = item['source']['text_sha256']
    assert [p.name for p in (output / 'sources').iterdir()] == [expected + '.excerpt.txt']
    assert hashlib.sha256((output / 'sources' / (expected + '.excerpt.txt')).read_bytes()).hexdigest() == expected
    proposal = json.loads((output / 'checkpoint.json').read_text())['waves'][0]['proposals'][0]
    assert proposal['raw_sha256'] is None
