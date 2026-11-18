"""Read-only QA for this documentary research pack; no runtime intelligence engine."""
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
from hashlib import sha256
import csv
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = 'c56bd74f130c4d855baf522ba8ba99fe87317fb1'


def read(name):
    return json.loads((HERE / name).read_text())


def index(rows):
    result = {r['id']: r for r in rows}
    assert len(result) == len(rows), 'Duplicate research identity'
    return result


def source_check(row):
    assert row['url'].startswith('https://') and row['locator'] and row['scope']
    assert len(row['excerpt'].split()) <= 25, 'Retained quotation exceeds bounded extent'
    assert sha256(row['excerpt'].encode()).hexdigest() == row['excerpt_sha256']
    assert row['original_bytes_acquired'] is False and row['original_bytes_sha256'] is None
    assert row['verification'] == 'original_primary_passage_review'
    assert row['canonical_acceptance'] is False
    assert row['public_use_decision'] == 'pending_existing_Source_owner'
    assert row['retrieved_on'] == '2026-11-18'


def claim_check(row, sources, claims):
    assert row['source_ids'] or row['input_claim_ids'], 'Unsupported assertion'
    assert set(row['source_ids']) <= sources.keys()
    assert set(row['input_claim_ids']) <= claims.keys()
    assert row['id'] not in row['input_claim_ids']
    assert row['semantic_type'] in {'reported', 'calculated', 'estimated', 'assumed', 'insight', 'hypothesis'}
    assert row['subject_key'] and row['reporting_period'] and row['material_caveat']
    assert row['counter_evidence'] and row['outstanding_demand']
    assert row['public_eligible'] is False and row['canonical_acceptance'] is False
    if row['semantic_type'] in {'insight', 'calculated'}:
        assert row['input_claim_ids'], 'Derived output has no identifiable premise'
    for measurement in row['measurements']:
        assert measurement['stock_flow'] in {'stock', 'flow', 'rate', 'ratio', 'change', 'count'}
        assert measurement['measurement_state'] and measurement['semantic_type']
        assert measurement['unit'] and measurement['basis'] and measurement['precision']
        assert Decimal(str(measurement['value'])).is_finite()
        if 'estimate' in measurement['measurement_state']:
            assert measurement['semantic_type'] == 'estimated'


def documentary_survivors(claims, denied_sources=()):
    """Audit declared lineage only; never grants research or public-use permission."""
    rows = index(claims)
    visiting = set()
    result = {}

    def visit(key):
        if key in result:
            return result[key]
        assert key not in visiting, 'Cyclic documentary dependency'
        visiting.add(key)
        row = rows[key]
        alive = not bool(set(row['source_ids']) & set(denied_sources))
        # Visit all inputs even where a denied direct source already invalidates a row.
        parents = [visit(parent) for parent in row['input_claim_ids']]
        result[key] = alive and all(parents)
        visiting.remove(key)
        return result[key]

    for key in rows:
        visit(key)
    return {key for key, alive in result.items() if alive}


def calculation(row, expected):
    # These eight reproducibility examples are fixed audit recipes, not a second Financial service.
    for field in ('id', 'input_claim_id', 'entity', 'period', 'basis', 'unit', 'operation', 'inputs'):
        assert row[field] == expected[field], 'Incompatible calculation perimeter: ' + field
    parent = index(read('Claims.json'))[row['input_claim_id']]
    assert row['entity'] == parent['subject_key'] and row['period'] == parent['reporting_period']
    # Independent original-source cuts prevent a self-consistent but substituted denominator.
    cuts = {
        'RR-UNDERLYING-MARGIN': ('MFG-RR','underlying','GBP million',['2534','11279']),
        'RR-STATUTORY-MARGIN': ('MFG-RR','IFRS','GBP million',['2418','11448']),
        'HOTEL-ROUNDED-BRIDGE': ('HOTEL-BRIDGE','adjusted-to-statutory bridge','GBP million',['287','-178']),
        'CC-GII-DIFFERENCE': ('TECH-CHANNEL','APM vsIFRS recognition','GBP million',['8927.5','6845.2']),
        'CC-GROSS-MARGIN': ('TECH-CHANNEL','IFRS grossprofit/revenue','GBP million',['657.9','6845.2']),
        'MORTGAGE-COHORT-GAP': ('BNK-RATES','newdrawn vsoutstandingstock effective rates','percent',['4.63','4.03']),
        'HUB-REVENUE-MIX': ('AIR-HUB','reported streamsum','GBP million',['1620','592','472']),
        'HUB-EBITDA': ('AIR-HUB','revenue lessadjustedoperatingcost','GBP million',['2684','1243']),
    }
    assert (row['input_claim_id'],row['basis'],row['unit'],row['inputs']) == cuts[row['id']]
    values = [Decimal(v) for v in row['inputs']]
    assert all(v.is_finite() for v in values)
    op = row['operation']
    if op in {'sum', 'sum_three'}:
        value = sum(values)
    elif op == 'difference':
        value = values[0] - values[1]
    else:
        assert op == 'ratio_percent' and values[1] > 0
        value = values[0] / values[1] * 100
    rounded = value.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
    assert rounded == Decimal(row['expected_rounded'])
    assert row['not_meaning'] and row['display_precision']
    return str(rounded)


def validate():
    sources = index(read('Sources.json'))
    claims = index(read('Claims.json'))
    for s in sources.values():
        source_check(s)
    for c in claims.values():
        claim_check(c, sources, claims)
    assert len(documentary_survivors(list(claims.values()))) == len(claims)
    for source in sources:
        alive = documentary_survivors(list(claims.values()), [source])
        assert not any(c['id'] in alive for c in claims.values() if source in c['source_ids'])

    sectors = read('Twenty-Sector-Foundations.json')
    assert [s['sic'] for s in sectors] == list('ABCDEFGHIJKLMNOPQRST')
    expected = [('0.63','0.60'),('0.47','0.50'),('0.67','0.66'),('0.71','0.76'),('0.49','0.50'),
                ('0.63','0.63'),('0.45','0.45'),('0.60','0.59'),('0.51','0.50'),('0.50','0.50'),
                ('0.47','0.47'),('0.17','0.17'),('0.42','0.42'),('0.47','0.46'),('0.44','0.43'),
                ('0.28','0.28'),('0.39','0.38'),('0.46','0.46'),('0.32','0.32')]
    for s, pair in zip(sectors, expected):
        row = s['economic_update']
        assert tuple(Decimal(str(row['value'+year])) for year in ('2023','2024')) == tuple(map(Decimal, pair))
        assert Decimal(str(row['gva_output_residual2024'])) == 1 - Decimal(pair[1])
        assert row['semantic_type'] == 'calculated' and row['input_claim_id'] in claims
        assert row['calculated_claim_id'] in claims and 'not profit margin' in row['meaning']
    assert sectors[-1]['economic_update'] is None, 'T exclusion is not a zero ratio'
    for s in sectors:
        assert s['material_remaining_demand'] and s['material_counter_evidence']
        assert s['public_admission'] is False and s['candidate_research_readiness'] == {'Facts':'Partial','FLORA Insight':'Partial'}
        assert set(s['claim_ids'] + [s['insight_id']]) <= claims.keys()
        assert s['existing_owner_eligible_baseline']['Facts'] == 'Partial'
    assert sectors[7]['currently_visible_composition']['Facts'] == 'Unavailable', 'Aviation navigation does not populate SIC H'

    uk = read('UK-PESTLE.json')
    assert {u['dimension'] for u in uk} == {'Political','Economic','Social','Technological','Legal','Environmental'}
    for u in uk:
        assert u['fact_claim_id'] in claims and u['insight_claim_id'] in claims
        assert u['not_automatic_enterprise_applicability'] is True
    assert claims['UK-LAW']['effective_date'] is None
    assert [(c['effective_date'], c['status']) for c in claims['UK-LAW']['clauses']] == [
        ('2026-10-30','guidance_reports_effective'),('2027-01-01','future_timetable_subject_to_parliamentary_process')]
    assert claims['UK-LABOUR']['semantic_type'] == claims['UK-PAYROLL']['semantic_type'] == claims['UK-CARBON']['semantic_type'] == 'estimated'

    industries = read('Priority-Industry-Analyses.json')
    for i in industries:
        assert len(i['forces']) == 5 and len(i['industry_pestle']) == 6
        for f in i['forces']:
            assert set(f['premise_claim_ids']) <= claims.keys()
            assert f['material_alternative'] and f['outstanding_evidence']
    assert len(industries[2]['value_system']) == 8
    for r in read('Typed-Relationships.json'):
        assert r['claim_id'] in claims and r['direction'] == 'subject_to_object'
        assert r['public_eligible'] is False and r['identity_status']
    assert 'top five divisions' in next(r for r in read('Typed-Relationships.json') if r['id']=='REL-6')['object']

    req = read('Experience-Readiness-Handoff.json')
    original = (ROOT / req['design_owner']).read_bytes()
    assert sha256(original).hexdigest() == req['design_sha256']
    keys = {r['requirement'] for r in csv.DictReader(original.decode().splitlines())}
    assert {r['requirement'] for r in req['rows']} == keys and len(req['rows']) == 16
    for r in req['rows']:
        assert set(r['new_withheld_candidate_ids']) <= claims.keys()
        assert set(r['current_owner_permitted_readiness']) == {'Facts','FLORA Insight'}
        assert r['new_public_permission'] is False and r['canonical_promotion'] is False
        assert r['precise_remaining_gap'] and r['minimum_composition']
        for scope in r['proposal_scope_assessments']:
            c = claims[scope['claim_id']]
            assert scope['subject_key'] == c['subject_key'] and scope['period'] == c['reporting_period']
            assert scope['Facts'] == scope['FLORA_Insight'] == 'Unavailable'

    calculations = read('Financial-and-Scope-QA.json')
    assert len(calculations) == 8
    for row in calculations:
        calculation(row,row)
        assert claims[row['output_claim_id']]['input_claim_ids'] == [row['input_claim_id']]

    foundation = json.loads((ROOT/'docs/flora-runtime/technology-visual-foundation/Foundation.json').read_text())
    work = read('Wave-4-Provider-Worklist.json')
    assert len(work) == 80 and {x['key'] for x in work} == {x['key'] for x in foundation['providers']}
    for x in work:
        assert x['existing_canonical_id'] is None and len(x['closure_demands']) == 6
    waves = read('Continuing-Waves.json')
    assert len(waves['wave5']['targets']) == 103
    assert all(isinstance(x['name'],str) and x['source_ids'] for x in waves['wave5']['targets'])
    assert len({x['name'] for x in waves['wave5']['targets']}) == 103
    assert sum(len(b['keys']) for b in waves['wave4']['batches']) == 80
    assert len(waves['wave3']['mandatory_named_cohorts']) >= 20

    # Existing files, all illustrations, IAM, Source, canonical and comparator bytes must stay unchanged.
    changed = subprocess.check_output(['git','diff','--name-status',BASE],cwd=ROOT,text=True).splitlines()
    for row in changed:
        status,path = row.split('\t',1)
        assert status == 'A' and (path.startswith('docs/flora-runtime/research-enrich-all-w2-685/') or path in {
            'tests/test_flora_research_enrich_all_w2_685.py','.github/workflows/flora-research-w2-685.yml'}), 'Unauthorised existing-file mutation: ' + row
    return dict(baseline=BASE, sources=len(sources),claims=len(claims),semantic_counts=dict(Counter(c['semantic_type'] for c in claims.values())),sectors=20,uk_dimensions=6,priority_industries=3,relationships=8,provider_followups=80,organisation_followups=103,design_keys=16,public_admissions=0,canonical_writes=0,runtime_edits=0)


if __name__ == '__main__':
    print(json.dumps(validate(),indent=2))
