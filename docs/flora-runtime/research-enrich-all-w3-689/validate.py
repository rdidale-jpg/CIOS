"""Offline research QA only. No Source grants, runtime owner, writes, or network calls."""
from collections import Counter
from decimal import Decimal
import csv
from hashlib import sha256
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = 'ecb91591e5abe854a6227ae4ebd21b4aa566cb69'
ALLOWED = ('docs/flora-runtime/research-enrich-all-w3-689/',
           'tests/test_flora_research_enrich_all_w3_689.py',
           '.github/workflows/flora-research-w3-689.yml')
GAPS = {'eligible_already_presented', 'eligible_not_presented',
        'researched_pending_rights_identity', 'missing_requires_enrichment', 'stale_or_conflicted'}


def read(name):
    return json.loads((HERE / name).read_text())


def index(rows):
    result = {r['id']: r for r in rows}
    assert len(result) == len(rows), 'duplicate research identity'
    return result


def source_check(s):
    assert s['url'].startswith('https://') and s['locator'] and s['issuer_scope']
    assert s['acquisition_extent'] and s['verification'] in {
        'original_primary_passage_review', 'normalised_original_text_partial'}
    assert s['original_bytes_acquired'] is False and s['original_bytes_sha256'] is None
    assert s['public_use'] == 'pending_existing_Source_owner'
    assert s['canonical_acceptance'] is False
    assert len(s['retained_quote'].split()) <= 25
    assert s['retrieved_on'] == '2026-11-18'
    if s['publication_date'] is None:
        assert s['publication_date_precision'] == 'not_verified'


def claim_check(c, sources, claims):
    assert c['source_ids'] or c['input_claim_ids'], 'unsupported proposition'
    assert set(c['source_ids']) <= sources.keys()
    assert set(c['input_claim_ids']) <= claims.keys()
    assert c['id'] not in c['input_claim_ids']
    assert c['subject_key'] and c['reporting_period'] and c['material_caveat']
    assert c['counter_evidence_or_alternative'] and c['next_material_demand']
    assert c['semantic_type'] in {'reported', 'calculated', 'estimated', 'assumed', 'insight', 'hypothesis'}
    if c['semantic_type'] in {'insight', 'calculated'}:
        assert c['input_claim_ids']
    assert c['public_eligible'] is False and c['canonical_acceptance'] is False


def survivors(rows, denied_sources=()):
    """Declared documentary lineage only; not runtime access or source admission."""
    claims = index(rows)
    visiting = set()
    cache = {}

    def visit(key):
        assert key not in visiting, 'cyclic documentary input'
        if key in cache:
            return cache[key]
        visiting.add(key)
        c = claims[key]
        parents = [visit(p) for p in c['input_claim_ids']]
        result = not (set(c['source_ids']) & set(denied_sources)) and all(parents)
        visiting.remove(key)
        cache[key] = result
        return result

    for key in claims:
        visit(key)
    return {key for key, alive in cache.items() if alive}


def check_bridge(recipe, measurements):
    """Validate transcribed context then sum declared signed terms. No dynamic code."""
    total = Decimal(0)
    for term in recipe['input_terms']:
        m = measurements[term['measurement_id']]
        for field in ('subject_key', 'reporting_period', 'currency', 'unit', 'basis'):
            assert m[field] == recipe[field], 'incompatible ' + field
        assert m['stock_flow'] == 'flow', 'stock/rate/count cannot enter financial flow bridge'
        assert m['measurement_state'] == 'actual', 'target cannot become actual'
        assert m['semantic_type'] == 'reported', 'estimate/assumption cannot silently become actual'
        assert term['sign'] in {-1, 1}
        value = Decimal(m['value'])
        assert value.is_finite()
        total += term['sign'] * value
    assert total == Decimal(recipe['expected']), 'financial transcription/reconciliation mismatch'
    assert recipe['canonical_acceptance'] is False
    return total


def same_owner_identity(left, right):
    """Diagnostic negative-join proof; no alias resolution or production identity service."""
    assert isinstance(left, tuple) and len(left) == 2
    assert isinstance(right, tuple) and len(right) == 2
    assert all(left) and all(right)
    return left == right


def scope_boundary():
    changed = subprocess.check_output(['git', 'diff', '--name-only', BASE], cwd=ROOT, text=True).splitlines()
    new = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], cwd=ROOT, text=True).splitlines()
    assert all(p.startswith(ALLOWED) for p in changed + new), 'research-only boundary changed'
    stamps = read('Preserved-Inputs.json')
    for path, stamp in stamps['source_artifacts'].items():
        assert sha256((ROOT/path).read_bytes()).hexdigest() == stamp, 'preserved source/baseline changed'
    manifest = subprocess.check_output(['git', 'ls-tree', '-r', '--format=%(path) %(objectname)', BASE], cwd=ROOT, text=True).splitlines()
    protected = [p for p in manifest if p.split(' ')[0].startswith(('cios/', 'enterprise-knowledge/', 'docs/Architecture/', 'docs/product/flora-experience/'))]
    assert len(protected) == stamps['protected_tracked_paths']
    assert sha256(('\n'.join(protected)+'\n').encode()).hexdigest() == stamps['path_blob_manifest_sha256']
    assert not any(p.startswith(('cios/', 'enterprise-knowledge/', 'docs/product/')) for p in changed)


def validate():
    sources, claims = index(read('Sources.json')), index(read('Claims.json'))
    for source in sources.values():
        source_check(source)
    for c in claims.values():
        claim_check(c, sources, claims)
    assert len(survivors(list(claims.values()))) == len(claims)
    measurements = index(read('Financial-Measurements.json'))
    for recipe in read('Financial-Reconciliations.json'):
        check_bridge(recipe, measurements)
        assert recipe['source_id'] in sources
    for m in measurements.values():
        assert m['source_id'] in sources
        assert Decimal(m['value']).is_finite()
        assert m['precision'] and m['reporting_period'] and m['subject_key']
        assert m['canonical_acceptance'] is False and m['public_eligible'] is False
    dossiers = index(read('Enterprise-Dossiers.json'))
    assert len(dossiers) == 25
    provider_questions = []
    for d in dossiers.values():
        assert set(d['claim_ids']) <= claims.keys()
        assert d['canonical_id'] is None and d['canonical_acceptance'] is False
        assert d['new_public_eligible'] is False
        assert d['unresolved_demands'] and d['forces']['alternative_or_counter_evidence']
        assert 'conceptual' in d['value_stream']['model_type']
        assert d['value_stream']['stakeholder_journey_demand']
        assert d['capabilities'] and all('unverified' in c['assurance'] for c in d['capabilities'])
        assert (HERE/'dossiers'/f"{d['id']}.md").is_file()
        if d['archetype'] == 'provider':
            provider_questions.append(d['commercial_investigation'])
    assert len(provider_questions) == len(set(provider_questions)) == 7
    cross = read('Banking-Portfolio-Crosswalk.json')
    original = json.loads((ROOT/'docs/flora-runtime/bie2/Actor-Register.json').read_text())['actors']
    occurrence = {x['original_actor_id']: x for x in cross['occurrence_rows']}
    assert len(occurrence) == len(original) == 76
    for a in original:
        x = occurrence[a['id']]
        assert x['original_name'] == a['name'] and x['original_kind'] == a['kind']
        assert x['canonical_id'] is None and x['qualitative_rationale'] and x['next_material_demand']
        if not x['exact_new_research_subject']:
            assert x['candidate_research_readiness'] == 'Unavailable'
            assert x['related_research_claims'] == []
        for binding in x['exact_element_bindings']:
            assert binding['candidate_Facts'] == 'Partial'
            assert binding['financial_metric_binding'] is False
            assert set(binding['claim_ids']) <= claims.keys()
        assert x['facts_readiness_for_new_W3_supply'] == 'Unavailable'
    req = read('Information-Requirements-and-Readiness.json')
    assert set(x['gap_state'] for x in req) == GAPS
    counts = Counter(x['actor_id'] for x in req if x.get('actor_id'))
    assert set(counts) == set(occurrence) and set(counts.values()) == {13}
    for actor, row in occurrence.items():
        for binding in row['exact_element_bindings']:
            cell = next(q for q in req if q.get('actor_id') == actor
                        and q['perspective'] == binding['perspective']
                        and q['information_element'] == binding['information_element'])
            assert cell['candidate_readiness']['Facts'] == 'Partial'
            assert cell['gap_state'] == 'researched_pending_rights_identity'
            assert cell['exact_element_claim_ids'] == binding['claim_ids']
    for q in req:
        assert q['subject_key'] and q['perspective'] and q['information_element'] and q['reporting_period']
        if q['gap_state'] in {'researched_pending_rights_identity', 'missing_requires_enrichment', 'stale_or_conflicted'}:
            assert q['public_readiness'] == {'Facts': 'Unavailable', 'FLORA Insight': 'Unavailable'}
    design = ROOT/'docs/product/flora-experience/experience-align-all/requirements.csv'
    expected = {x['requirement'] for x in csv.DictReader(design.open())}
    handoff = read('Experience-Readiness-Handoff.json')
    assert {x['requirement'] for x in handoff['rows']} == expected and len(expected) == 16
    assert sha256(design.read_bytes()).hexdigest() == handoff['design_sha256']
    previous = read('../research-enrich-all-w2-685/Experience-Readiness-Handoff.json')
    before = {x['requirement']: x['current_owner_permitted_readiness'] for x in previous['rows']}
    for row in handoff['rows']:
        assert row['current_owner_permitted_readiness'] == before[row['requirement']]
        assert set(row['new_candidate_claims']) <= claims.keys()
        assert row['new_public_readiness'] == {'Facts': 'Unavailable', 'FLORA Insight': 'Unavailable'}
    edges = read('Typed-Relationships.json')
    index(edges)
    assert Counter(x['status'] for x in edges) == {'verified_candidate': 18, 'rejected_join': 12}
    assert all(x['contract_value'] is None and x['buying_intent'] is None and x['public_eligible'] is False for x in edges)
    assert all(set(x['claim_ids']) <= claims.keys() for x in edges)
    historical = read('Inherited-Relationship-Review.json')
    original_edges = json.loads((ROOT/'docs/flora-runtime/bie2/Relationship-Candidates.json').read_text())['edges']
    assert [x['original'] for x in historical['rows']] == original_edges and len(original_edges) == 31
    cohort = read('Existing-Cohort-Reconciliation.json')
    assert cohort['counts'] == {'finite_bank_reference': 5, 'historical_narrative': 7, 'financial_candidate_dossier': 6}
    assert all(r['related_dossier'] in dossiers for r in cohort['rows'])
    assert cross['raw_id_join_allowed'] is False
    assert same_owner_identity(('LegacyManifest', 'BK-ENT-003'), ('BankingPortfolio', 'BK-ENT-003')) is False
    exceptions = index(read('Source-Exceptions-and-Decisions.json'))
    assert exceptions['PAYUK-LISTS']['state'] == 'use_restricted_pending_decision'
    assert exceptions['PAYUK-GD4']['state'] == 'document_specific_rights_conflict'
    assert sources['SAN-Q3']['verification'] == 'normalised_original_text_partial'
    assert 'interim CEO' in claims['NVDA-2']['statement']
    assert 'July' in exceptions['SEC-ONS']['observed'] or 'ADR027' in exceptions['SEC-ONS']['observed']
    waves = read('Continuing-Waves.json')
    assert waves['wave4']['population'] == 80 and waves['wave5']['population'] == 103
    assert len(waves['wave5']['configured_targets']) == 103
    scope_boundary()
    return dict(sources=len(sources), propositions=len(claims), dossiers=len(dossiers), actor_occurrences=len(occurrence), information_cells=len(req), reconciliations=len(read('Financial-Reconciliations.json')), measurements=len(measurements), design_keys=len(expected), positive_edges=18, rejected_joins=12)


if __name__ == '__main__':
    print(json.dumps(validate(), sort_keys=True))
