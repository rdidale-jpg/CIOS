"""Offline FIG-1 research/design QA; no new admission or financial engine."""
from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.research.fig1_demo import demonstration
from cios.applications.flora.research_intelligence.source_import import official_url

PACK = ROOT / 'docs/flora-runtime/fig1'
BANKS = ('natwest-group', 'hsbc-uk', 'santander-tsb', 'nationwide', 'starling')


def load():
    return {name: json.loads((PACK / (name + '.json')).read_text())
            for name in ('Source-Ledger', 'Banking-Exemplars', 'Analysis-Specification', 'Gate-Audit')}


def require(value, reason):
    if not value:
        raise ValueError(reason)


def validate(pack=None):
    pack = load() if pack is None else deepcopy(pack)
    sources = {s['id']: s for s in pack['Source-Ledger']}
    cases = pack['Banking-Exemplars']
    require(tuple(c['id'] for c in cases) == BANKS, 'Five differentiated exemplars required')
    expected_subjects = {
        'natwest-group': 'NatWest Group plc and subsidiaries',
        'hsbc-uk': 'HSBC UK Bank plc, UK ring-fenced bank; not Holdings/HSBC Bank plc/UK geography',
        'santander-tsb': 'Santander UK Group Holdings plc; TSB acquired-period contributions separately labelled',
        'nationwide': 'Nationwide Building Society consolidated Group including Virgin Money',
        'starling': 'Starling Group; Bank and Engine platform/customer measures remain distinct',
    }
    source_refs = dict(zip(BANKS, ('NW', 'HS', 'SA', 'NB', 'ST')))
    old_sources = json.loads((ROOT / 'docs/flora-runtime/bie3/Source-Review.json').read_text())
    old_bie2 = {s['id']: s for s in json.loads((ROOT / 'docs/flora-runtime/bie2/Source-Ledger.json').read_text())}
    expected_urls = {'NW': next(s['url'] for s in old_sources if s['id'] == 'BIE3-NW-Q3'),
                     'HS': next(s['url'] for s in old_sources if '3q-2026-data-pack-pdf-file' in s['url']),
                     'SA': next(s['url'] for s in old_sources if 'Q3-26%20QMS.pdf' in s['url']),
                     'NB': old_bie2['NBS-FY']['url'], 'ST': old_bie2['STAR-FY']['url']}
    expected_units = {'NW': {'GBP million', 'GBP billion'}, 'HS': {'USD million'},
                      'SA': {'GBP million'}, 'NB': {'GBP million', 'GBP billion'},
                      'ST': {'GBP million', 'GBP billion', 'million accounts', 'GBP million annual recurring revenue'}}
    denials = []
    for case in cases:
        sid = case['source_id']; src = sources[sid]
        require(source_refs[case['id']] == sid and case['subject'] == expected_subjects[case['id']],
                'Reporting Group/legal-bank/source binding changed')
        require(src['url'] == expected_urls[sid] and src['source_use_permission'].startswith('UNRESOLVED'),
                'Original source identity or unresolved use changed')
        require(case['rights_status'] == 'UNRESOLVED' and case['real_canonical_ids'] is None
                and not case['new_canonical_acceptance'] and not case['public_runtime_integration'],
                'Research/design is not source permission, canonical acceptance or live integration')
        require(src['original_bytes_sha256'] is None and not src['retained_original_bytes']
                and src['canonical_acceptance'].startswith('UNVERIFIED')
                and not src['runtime_admitted_by_this_sprint'], 'No fabricated source archive or authority')
        try:
            official_url(src['url'])
        except ValueError:
            denials.append(sid)
        else:
            raise ValueError('Current source policy changed; review this frozen design baseline')
        require(all(m['unit'] in expected_units[sid] and m['source_locator']
                    and m['basis'] and m['temporal_scope']
                    and m['authority'] == 'research_candidate_not_accepted'
                    and m['semantic_type'] == 'reported' and m['measurement_state'] == 'actual'
                    for m in case['metrics']),
                'Measurement unit, basis, period, lineage or authority missing')
    by = {c['id']: {m['key']: m for m in c['metrics']} for c in cases}
    for c in cases:
        require(len(by[c['id']]) == len(c['metrics']), 'Duplicate metric key')
        for m in c['metrics']:
            if c['id'] == 'hsbc-uk':
                require(m['temporal_scope'] == '9M to2026-09-30', 'HSBC YTD cannot become a quarter')
            elif c['id'] == 'santander-tsb' and not m['key'].startswith('tsb-'):
                require(m['temporal_scope'] == '9M to2026-09-30', 'Santander Group period mismatch')
            elif c['id'] == 'nationwide' and m['key'] != 'deposits':
                require(m['temporal_scope'] == 'FY2025-04-01/2026-03-31', 'Nationwide duration mismatch')
            if c['id'] == 'natwest-group':
                require(m['unit'] == ('GBP million' if m['key'] == 'pbt' else 'GBP billion')
                        and m['temporal_scope'] == ('9M to2026-09-30' if m['key'] == 'pbt' else 'instant2026-09-30'),
                        'NatWest stock/flow scale/date mismatch')
    amount = lambda bank, key: Decimal(by[bank][key]['reported_value'])
    require(amount('natwest-group', 'pbt') == 6543
            and amount('natwest-group', 'deposits') == Decimal('454.3')
            and amount('natwest-group', 'deposits-ex-central') == Decimal('453.4'), 'NatWest definitions/cells changed')
    h = by['hsbc-uk']; require(len({m['temporal_scope'] for m in h.values()}) == 1
                             and len({m['basis'] for m in h.values()}) == 1, 'HSBC bridge incompatible')
    require(sum(amount('hsbc-uk', k) for k in ('revenue', 'ecl', 'costs', 'associates'))
            == amount('hsbc-uk', 'pbt') == 6084, 'HSBC signed USD bridge failed')
    require(sum(amount('santander-tsb', k) for k in ('income', 'costs', 'credit', 'restructuring'))
            == amount('santander-tsb', 'pbt') == 1158, 'Santander signed Group bridge failed')
    require(by['santander-tsb']['tsb-pbt']['temporal_scope'] == 'duration2026-05-01/2026-09-30'
            and by['santander-tsb']['tsb-cost']['temporal_scope'] == 'duration2026-05-01/2026-09-30',
            'TSB acquired contribution cannot become nine-month/annual performance')
    require(sum(amount('nationwide', k) for k in ('income', 'costs', 'credit'))
            == amount('nationwide', 'underlying-pbt') == 2026, 'Nationwide underlying bridge failed')
    require(sum(amount('nationwide', k) for k in ('underlying-pbt', 'income-adjustment', 'cost-adjustment', 'member-reward'))
            == amount('nationwide', 'statutory-pbt') == 1490, 'Nationwide statutory/member bridge failed')
    require(amount('nationwide', 'integration') == 127, 'Integration expense cannot replace statutory bridge')
    require(amount('starling', 'revenue') - amount('starling', 'revenue-prior') == Decimal('-52.6')
            and amount('starling', 'pbt') - amount('starling', 'pbt-prior') == Decimal('-6.3'),
            'Starling within-Group trend failed')
    require('not a verified active UK-bank customer denominator' in by['starling']['platform']['basis']
            and 'composition unverified' in by['starling']['platform']['basis']
            and 'not recognised' in by['starling']['engine-arr']['basis']
            and 'not external' in by['starling']['engine-investment']['basis'],
            'Platform/ARR/intragroup economics cannot become customer count/revenue/supplier budget')
    spec = pack['Analysis-Specification']
    require([d['id'] for d in spec['dimensions']] == list('ABCDEFGHIJ'), 'A–J analyst specification required')
    require({c['exemplar'] for c in spec['coverage']} == set(BANKS), 'Five-bank dimension assessment required')
    permitted = {'selected_verified', 'partial', 'located_not_reconciled',
                 'not_in_selected_material', 'not_comparable_without_bridge'}
    for coverage in spec['coverage']:
        require(set(coverage['dimensions']) == set('ABCDEFGHIJ'), 'All ten dimensions must be assessed')
        require(all(r['status'] in permitted and r['finding'] for r in coverage['dimensions'].values()),
                'No fabricated complete research or unqualified empty slot')
    gates = pack['Gate-Audit']
    require(len(gates) == len({g['id'] for g in gates}) == 17, 'Seventeen actual ownership/risk gates required')
    for gate in gates:
        source = (ROOT / gate['path']).read_text()
        require(gate['symbol'] in source and gate['risk'] and gate['required_for']
                and gate['proposed_simplification'] and not gate['authority_change_executed'],
                'Audit must reference actual code/risks without executing authority')
    proof = demonstration()
    require(proof == json.loads((PACK / 'Demo-Output.json').read_text()), 'Committed fixture output not reproducible')
    return {'design_qa_passed': True, 'bank_exemplars': 5, 'dimension_assessments': 50,
            'actual_gate_owners_assessed': 17, 'current_issuer_policy_denials': denials,
            'new_rights_grants': 0, 'canonical_promotions': 0, 'runtime_changes': 0,
            'research_completeness_claim': False, 'proof_scope': 'fixed synthetic examples, not a live financial analyst'}


if __name__ == '__main__':
    print(json.dumps(validate(), indent=2))
