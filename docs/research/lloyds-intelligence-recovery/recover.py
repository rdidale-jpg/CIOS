"""Reconstruct a bounded research handoff from immutable retained Git objects.

No network, Source admission, credentials, canonical services or runtime writers.
SHA256 below always identifies repository records/files, NEVER publisher bytes.
"""
from collections import Counter
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BASE = '0a6423fe3a32d0a0d5d11fe9d7027859e94c6df7'
PACKS = {
    'RIE1': ('c57ed9728473563b5535db36d5bfbe5e96a8c572', 'docs/flora-runtime/rie1-617'),
    'RIE2': ('71d34bb50cff4a7e99cf49f53a0ee5c8724c3df5', 'docs/flora-runtime/rie2-619'),
    'RIC1': ('9db8253b23deefac00022716c53311472203aec7', 'docs/flora-runtime/ric1'),
    'BNK': ('412c086391194ec4e9d2f1b76841b0bb1df8917d', 'docs/flora-runtime/bnk-ent-1'),
    'TIER': (BASE, 'docs/research/lloyds-tier1-sprint1'),
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def read(package, filename):
    ref, folder = PACKS[package]
    raw = subprocess.check_output(['git', 'show', ref + ':' + folder + '/' + filename], cwd=ROOT)
    return ([json.loads(line) for line in raw.decode().splitlines()] if filename.endswith('.ndjson')
            else json.loads(raw))


def build():
    r1 = read('RIE1', 'Facts.json')
    r2 = read('RIE2', 'Claims.json')
    if isinstance(r2, dict):
        r2 = r2['claims']
    originals = {pack + ':' + row['id']: row for pack, rows in [('RIE1', r1), ('RIE2', r2)] for row in rows}
    ric = read('RIC1', 'Claim-Ledger.json')
    assert len(ric) == len(originals) == 362
    for row in ric:
        assert row['record'] == originals[row['id']], row['id']
    index = [{'id': key, 'package': key.split(':')[0], 'original_id': row['id'],
              'record_sha256': digest(row), 'ric_alias': key,
              'ric_relationship': 'exact original record, NOT another finding',
              'entity': row.get('subject_scope', row.get('subject')),
              'period': row.get('reporting_period'), 'source_refs': row.get('source_refs', []),
              'canonical_acceptance': False}
             for key, row in originals.items()]
    tier = read('TIER', 'evidence.ndjson')
    recovered = []
    for row in tier:
        recovered.append({'id': 'REC-TIER-' + row['id'], 'original_refs': ['TIER:' + row['id']],
            'entity': row['supported_object'], 'period': row['period'],
            'semantic_type': 'Reported candidate', 'statement': row['supported_claim'],
            'source_refs': ['TIER:' + key for key in row['evidence']],
            'source_locator': row['source_location'], 'retained_verification': row['verification_status'],
            'new_original_source_verification': False, 'canonical_acceptance': False,
            'public_admission_in_this_sprint': False,
            'source_use': 'Existing candidate review status retained; not a public-use grant',
            'disposition': row['review_disposition'], 'caveat': row['limitations'],
            'record_sha256': digest(row)})
    wanted = ['RETAIL-PRICE', 'RETAIL-LEASE', 'CREDIT-EXPLAIN', 'IP-DIVIDEND',
              'PRIMARY-SUBS', 'MS-ADOPTION', 'ENVOY-DATE', 'AI-VALUE', 'INVESTMENT']
    for suffix in wanted:
        row = next(r for r in r2 if r['id'] == 'R2-OBS-' + suffix)
        recovered.append({'id': 'REC-' + row['id'], 'original_refs': ['RIE2:' + row['id']],
            'entity': row['subject'], 'period': row['reporting_period'],
            'semantic_type': 'Reported candidate; retained compound note, NOT atomic Observation',
            'statement': row['statement'], 'source_refs': ['RIE2:' + s for s in row['source_refs']],
            'source_locator': row['source_locator'], 'retained_verification': 'Original package research assertion',
            'new_original_source_verification': False, 'canonical_acceptance': False,
            'public_admission_in_this_sprint': False, 'source_use': row['rights_status'],
            'disposition': 'Financial-source dependency' if suffix in {
                'RETAIL-PRICE', 'RETAIL-LEASE', 'CREDIT-EXPLAIN', 'IP-DIVIDEND', 'PRIMARY-SUBS', 'INVESTMENT'
                } else 'Research-only; source applicability and factual assurance retained',
            'caveat': row['uncertainty'], 'record_sha256': digest(row)})
    clarifications = {
        'R2-OBS-MS-ADOPTION': 'Do not reuse this compound note as one issuer-verified population. Tier F11A/F11B/F22 distinguish issuer rollout scope from the interested supplier engineering-deployment claim. Licence count, active licensed colleagues and engineers are different denominators.',
        'R2-OBS-AI-VALUE': 'Prior-year contribution is company-reported; the following-year amount is expectation. Gross/net accounting, full costs and causal attribution are not established. Neither figure is a supplier budget.',
        'R2-OBS-RETAIL-PRICE': 'Retain H1 Retail pricing explanation. This is not the Group deposit-stock comparison or evidence of organic Group outflow.',
        'R2-OBS-RETAIL-LEASE': 'Fleet growth, mix, residual prices and disclosed mitigation coexist. Other-income movements less depreciation movements do not calculate leasing margin or profit.',
        'R2-OBS-IP-DIVIDEND': 'An upstream distribution, deferred-profit stock including risk adjustment and release flow are different measures; no addition into customer revenue.',
        'R2-OBS-PRIMARY-SUBS': 'Historical reported interests do not settle the current intermediate ownership hierarchy or override later registry observations.',
        'R2-OBS-ENVOY-DATE': 'Publisher versions refer to one platform announcement. Designed controls are not independently proven effectiveness or live use-case outcomes.',
    }
    for row in recovered:
        row['recovery_reconciliation'] = clarifications.get(row['original_refs'][0].split(':', 1)[1],
            'Retain the original scope, date, assurance and limitations; do not strengthen the claim on recovery.')
    groups = [
        ('GROUP-REPORTING', ['RIE1:LBG-AR25-WEB-F1', 'RIE2:R2-OBS-PRIMARY-SUBS'], 'Reporting divisions and legal holdings are different axes.'),
        ('ENVOY', ['RIE1:LBG-ENVOY26-F1', 'RIE2:R2-OBS-ENVOY-DATE'], '28 April PDF and 1 May HTML are publication versions, not two deployments.'),
        ('AI-BENEFITS', ['RIE1:LBG-AI26-F1', 'RIE2:R2-OBS-AI-VALUE'], 'Prior-year reported contribution and next-year expectation are not net realised savings.'),
        ('MICROSOFT', ['RIE1:LBG-MS26-F1', 'RIE2:R2-OBS-MS-ADOPTION'], 'Agreement, licences, active users and engineering population must remain distinct.'),
    ]
    for _, refs, _ in groups:
        assert all(ref in originals for ref in refs)
    operations = read('RIE2', 'Operating-Model.json')
    bundle = json.loads(subprocess.check_output(['git', 'show', BASE + ':docs/research/initial-factory/register-replay.json'], cwd=ROOT))
    commission = next(row['commission'] for row in bundle
                      if row['commission']['enterprise_id'] == 'lloyds-banking-group-plc')
    group = [{'kind': 'group_legal_identity', 'name': commission['legal_name'],
              'registration_number': commission['registration_number'], 'as_at': commission['as_of'],
              'canonical_id': None, 'source_ref': 'Initial Factory retained register replay commission',
              'restriction': 'Group identity from retained replay, not a fresh register verification or production binding'}]
    legal = [{'kind': 'legal_entity', **row, 'canonical_id': None,
              'source_ref': 'RIE2:' + row['source_ref'],
              'restriction': 'Historical holdings from retained SEC source; not current register authority'}
             for row in operations['principal_legal_interests']]
    reporting = [{'kind': 'reporting_segment', 'name': name,
                  'period': operations['reporting']['period'], 'source_ref': 'RIE2:' + operations['reporting']['source_ref'],
                  'canonical_id': None, 'restriction': 'Not a legal entity or automatic mapping to November management units'}
                 for name in operations['reporting']['divisions']]
    roles = [{'kind': 'professional_role', **row, 'source_ref': 'RIE2:' + row['source_ref'],
              'canonical_id': None, 'restriction': 'Dated roster, not delegation, current mandate or buying authority'}
             for row in operations['current_roles']]
    # Retain corrected/current dated Tier records alongside earlier role snapshots.
    # Do not manufacture equivalence between Group, legal bank and research alias.
    management = [{'kind': 'dated_management_or_brand_context', 'record_ref': row['id'],
                   'statement': row['statement'], 'period': row['period'], 'entity': row['entity'],
                   'canonical_id': None, 'restriction': row['caveat']}
                  for row in recovered if row['original_refs'][0] in {
                      'TIER:F05A', 'TIER:F05B', 'TIER:F06A', 'TIER:F06B', 'TIER:F07',
                      'TIER:F08A', 'TIER:F08B', 'TIER:F08C', 'TIER:F09', 'TIER:F26A',
                      'TIER:F26B', 'TIER:F26C', 'TIER:F26D'}]
    brands = [{'kind': 'brand_context', 'name': 'Halifax', 'source_ref': 'RIE1:LBG-RING-F1',
               'period': 'Retained RIE1 November 2026 research cut', 'canonical_id': None,
               'restriction': operations['brand_warning']},
              {'kind': 'brand_context', 'name': 'Scottish Widows', 'source_ref': 'TIER:F08C',
               'period': '2026-11-22', 'canonical_id': None,
               'restriction': 'Brand, roster label, legal company and authorised Master Trust are not interchangeable.'}]
    tier_sources = read('TIER', 'sources.json')
    sources = [{'id': 'TIER:' + key, 'origin_package': 'TIER', **value,
                'new_permission': False, 'publisher_bytes_reacquired': False}
               for key, value in tier_sources.items()]
    for pack in ['RIE1', 'RIE2']:
        rows = read(pack, 'Source-Ledger.json')
        if isinstance(rows, dict):
            rows = rows['sources']
        sources += [{'id': pack + ':' + row['id'], 'origin_package': pack,
                     'retained_metadata': row, 'new_permission': False, 'publisher_bytes_reacquired': False}
                    for row in rows]
    proposals = read('RIC1', 'Observation-Proposals.json')
    checks = json.loads(subprocess.check_output(['git', 'show', BASE + ':docs/flora-runtime/lei-1/reconciliations.json'], cwd=ROOT))['checks']
    reconciliation = [{'id': row['id'], 'entity': row['subject'], 'period': row['period'],
                       'basis': row['basis'], 'arithmetic_reproduces': sum(Decimal(str(n)) for n in row['inputs']) == Decimal(str(row['expected'])),
                       'eligibility': 'Research arithmetic only; no Financial run or output activated'} for row in checks]
    return {
        'Recovery.json': {'baseline': BASE, 'authority': 'Research recovery only; no new verified facts or admissions',
                          'records': recovered,
                          'concept_groups': [{'id': key, 'original_refs': refs, 'reconciliation': note,
                            'rule': 'Co-reference, not sum or identity merge'} for key, refs, note in groups],
                          'reconciliations': reconciliation},
        'Deduplication.json': {'baseline': BASE, 'packages': PACKS,
            'package_record_counts': {'RIE1': len(r1), 'RIE2': len(r2), 'RIC1': len(ric)},
            'ric_exact_references_not_additional_findings': len(ric),
            'original_record_identities': len(originals),
            'limit': 'Record-identity denominator across the full RIE packages, NOT 362 unique Lloyds facts or semantic completeness',
            'records': index},
        'Entity-Crosswalk.json': {'baseline': BASE,
            'authority': 'Dated research crosswalk, not accepted Enterprise Model hierarchy',
            'identity_rules': ['Group SC095000 != Lloyds Bank 00002065',
                'BK-ENT-001 retained research alias is not a new canonical identity decision',
                'BK-ENT-003 collision remains unresolved; never repaired by name similarity',
                'PSC statements do not establish every intermediate owner or an entire Group tree',
                'November BCB/CIB/Connected Finance labels do not restate H1 reporting segments'],
            'entries': [*group, *legal, *reporting, *roles, *management, *brands],
            'candidate_relationships': read('TIER', 'relationship.ndjson'),
            'historical_legal_relationships': read('RIE2', 'Relationships.json')['new_edges']},
        'Source-Register.json': {'baseline': BASE,
            'authority': 'Existing research source metadata only; not a new Source registry',
            'sources': sources,
            'unchanged_owner_proposals': [{'id': row['id'], 'claim_ref': row['claim_ref'],
                'original_record_sha256': digest(row), 'source_refs': row['source_refs'],
                'owner_evidence_acceptance': False, 'canonical_acceptance': False,
                'origin': 'RIC1:Observation-Proposals.json'} for row in proposals]},
    }


def main():
    for name, content in build().items():
        (HERE / name).write_text(json.dumps(content, ensure_ascii=False, indent=2) + '\n')
    print('Reconstructed research handoff; no service calls or permissions changed.')


if __name__ == '__main__':
    main()
