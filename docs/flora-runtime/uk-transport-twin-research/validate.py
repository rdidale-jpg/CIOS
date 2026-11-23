"""Offline research-package QA. No runtime stores, network, imports or promotion."""
import json
import hashlib
import subprocess
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse

PACK = Path(__file__).resolve().parent
ROOT = PACK.parents[2]
CONTEXT = ('entity_id', 'period', 'basis', 'currency', 'unit',
           'measurement_state', 'stock_flow', 'semantic_type')


def read(name):
    return json.loads((PACK / name).read_text())


def index(rows):
    result = {r['id']: r for r in rows}
    assert len(result) == len(rows), 'duplicate identity'
    return result


def source_check(s):
    u = urlparse(s['url'])
    assert u.scheme == 'https' and u.hostname and not u.username
    assert not u.query, 'temporary/signed URLs are not stable source identities'
    assert s['original_bytes_sha256'] is None, 'no original bytes acquired'
    assert s['canonical_acceptance'] is False
    assert s['public_source_admission'] is False
    assert s['acquisition_extent'] and s['locator'] and s['rights']
    assert s['retrieved_on'] == '2026-11-18'
    if s['published_on']:
        assert s['published_on'] <= s['retrieved_on'], 'future publication'


def claim_check(c, sources, entities, claims):
    assert c['entity_id'] in entities, 'unknown subject'
    assert c['status'] == 'research_candidate' and not c['canonical_promotion']
    assert c['period'] and c['caveat']
    assert c['semantic_type'] in {'reported', 'insight', 'hypothesis'}
    assert set(c['source_ids']) <= sources.keys(), 'missing source'
    assert set(c['input_claim_ids']) <= claims.keys(), 'missing dependency'
    if c['semantic_type'] == 'reported':
        assert c['source_ids'], 'unsupported factual proposition'
    else:
        assert c['input_claim_ids'], 'unfounded interpretation'


def documentary_survivors(claims, withdrawn=()):
    """Inspect this document's dependency graph; no runtime lifecycle semantics."""
    records = index(claims)
    active, visiting = {}, set()

    def alive(key):
        if key in active:
            return active[key]
        assert key not in visiting, 'cyclic documentary dependency'
        visiting.add(key)
        row = records[key]
        dependencies = [alive(i) for i in row['input_claim_ids']]
        value = not set(row['source_ids']).intersection(withdrawn) and all(dependencies)
        visiting.remove(key)
        active[key] = value
        return value

    for key in records:
        alive(key)
    return {key for key, value in active.items() if value}


def check_calculation(recipe, measurements, withdrawn=()):
    total = Decimal('0')
    assert recipe['context']['stock_flow'] == 'flow'
    assert recipe['context']['measurement_state'] == 'actual'
    assert recipe['output_type'] == 'calculated' and not recipe['canonical_promotion']
    for term in recipe['terms']:
        m = measurements[term['measurement_id']]
        assert m['source_id'] not in withdrawn, 'withdrawn documentary input'
        assert all(m[k] == recipe['context'][k] for k in CONTEXT), 'incompatible financial context'
        value, coefficient = Decimal(m['value']), Decimal(term['coefficient'])
        assert value.is_finite() and coefficient.is_finite(), 'nonfinite number'
        total += value * coefficient
    tolerance = Decimal(recipe['tolerance'])
    assert tolerance == (Decimal('1') if recipe['id'] == 'TFL-rounded' else Decimal('0')), 'undeclared tolerance'
    assert abs(total - Decimal(recipe['expected'])) <= tolerance, 'unreconciled financial assertion'
    return total


def edge_check(e, entities, sources):
    assert e['from_entity'] in entities and e['to_entity'] in entities, 'invalid endpoint'
    assert e['from_entity'] != e['to_entity'], 'self-join'
    assert e['source_ids'] and set(e['source_ids']) <= sources.keys()
    assert e['period'] and e['scope']
    assert e['status'] in {'supported_candidate', 'rejected_join'}
    assert not e['canonical_promotion'] and not e['legal_contract_binding']
    assert e['contract_value'] is None and e['expiry'] is None
    prohibited = {
        ('NR', 'NRIL', 'same_financial_entity'),
        ('GBR', 'NRIL', 'completed_acquisition'),
        ('ABP', 'DPW-UK', 'owns_or_has_contract_with'),
        ('DHL-GLOBAL', 'DHL-UK', 'same_financial_entity'),
        ('IDS', 'RM', 'same_financial_entity'),
        ('HEATHROW', 'HSP', 'automatic_legal_metric_binding'),
        ('IAG', 'OPENAIR', 'open_unallocated_procurement'),
        ('GBR', 'SCOTRAIL', 'owns'),
    }
    if (e['from_entity'], e['to_entity'], e['predicate']) in prohibited:
        assert e['status'] == 'rejected_join', 'unsupported identity/contract join'


def preservation_check():
    for item in read('Preserved-Inputs.json'):
        assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256'], 'inherited artifact changed'
    a = ROOT / 'knowledge-packs/researcher/contracts/researcher_v1.json'
    b = ROOT / 'cios/contracts/twin_object_profiles/researcher_v1.json'
    assert a.read_bytes() == b.read_bytes()
    assert 'industry_twin' in json.loads(a.read_text())['profiles']
    base = read('MissionState.json')['base_sha']
    changed = subprocess.check_output(['git', 'diff', '--name-only', base], cwd=ROOT, text=True).splitlines()
    permitted = {'tests/test_flora_transport_research.py', '.github/workflows/flora-transport-research.yml'}
    for name in changed:
        assert name.startswith('docs/flora-runtime/uk-transport-twin-research/') or name in permitted, 'unrelated file changed: ' + name
    modified = subprocess.check_output(['git', 'diff', '--name-only', '--diff-filter=MDRT', base], cwd=ROOT, text=True).splitlines()
    assert not modified, 'existing implementation/research/baseline modified'


def validate():
    s, e, c = index(read('Sources.json')), index(read('Entities.json')), index(read('Claims.json'))
    for row in s.values():
        source_check(row)
    for row in e.values():
        assert row['source_ids'] and set(row['source_ids']) <= s.keys()
        assert row['status'] == 'research_reference_only'
        assert row['canonical_identity'] is None or row['id'] == 'EASYJET'
    for row in c.values():
        claim_check(row, s, e, c)
    assert len(documentary_survivors(list(c.values()))) == len(c)
    m = index(read('Measurements.json'))
    for row in m.values():
        assert row['source_id'] in s and row['entity_id'] in e
        assert row['semantic_type'] == 'reported' and Decimal(row['value']).is_finite()
    for row in read('Calculations.json'):
        check_calculation(row, m)
    for row in read('Relationships.json'):
        edge_check(row, e, s)
    for row in read('Taxonomy.json'):
        assert row['open_demand'] and set(row['source_ids']) <= s.keys()
    for row in read('Dossier-Index.json'):
        assert (PACK / row['path']).is_file()
        assert set(row['entity_ids']) <= e.keys() and set(row['claim_ids']) <= c.keys()
    for row in read('Programme-Pressure-Procurement.json'):
        assert row['entity_id'] in e and set(row['source_ids']) <= s.keys()
        assert not row['opportunity'] and not row['qualified_material_pressure']
        assert row['procurement_value'] is None and row['renewal_date'] is None and row['blocker']
    state = read('MissionState.json')
    assert state['overall_outcome'] == 'CONTINUE' and not state['runtime_changes']
    assert not state['canonical_writes'] and not state['source_permissions_changed']
    assert not list(PACK.rglob('*.zip')) and not list(PACK.rglob('blueprint_manifest.json'))
    preservation_check()
    return dict(sources=len(s), entities=len(e), claims=len(c), measurements=len(m),
                calculations=len(read('Calculations.json')), relationships=len(read('Relationships.json')),
                dossiers=len(read('Dossier-Index.json')), subindustries=len(read('Taxonomy.json')))


if __name__ == '__main__':
    print(json.dumps(validate(), sort_keys=True))
