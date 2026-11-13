"""Read-only commercial view projection over the existing Technology foundation.

Supplementary reviewed passages reuse SourceSegment/CandidateClaim/EvidencePackageItem;
none is an accepted import, identity binding, rights grant or Pipeline record.
"""
from dataclasses import asdict
from hashlib import sha256
import json
import math
from pathlib import Path
from urllib.parse import urlsplit

from . import technology
from ..enterprise_intelligence.semantic import SourceSegment, CandidateClaim
from ..enterprise_intelligence.models import EvidencePackageItem

DATA = technology.ROOT / 'docs/flora-runtime/ux-refinement-573/Commercial-Views.json'
DATA_SHA256 = '75a80994f78251bc092e858788a23538685812034add59ad76ac6aeb8dc9db7d'
SORT_KEYS = ('name', 'uk_revenue', 'uk_workforce', 'role', 'specialty', 'signal')
CLOUD_FACILITIES = ('equinix', 'telehouse', 'pulsant', 'digital-realty', 'virtus')


def validate_metric(value, sources, *, uk=False):
    if value is None:
        return
    if not isinstance(value, dict) or value.get('kind') not in ('reported', 'estimate'):
        raise ValueError('Metric classification required')
    number = value.get('value')
    if type(number) not in (int, float) or not math.isfinite(number) or number < 0:
        raise ValueError('Metric must be finite and non-negative')
    if value.get('unit') not in ('GBP', 'USD', 'people', 'percent') or not value.get('period') or not value.get('scope'):
        raise ValueError('Metric unit, period and scope required')
    if uk and value['scope'] not in ('UK', 'UK segment', 'UK entity'):
        raise ValueError('UK column cannot inherit group or UK-and-Ireland data')
    if not value.get('source_ids') or set(value['source_ids']) - set(sources) or value.get('canonical_accepted') is not False:
        raise ValueError('Metric provenance or acceptance mismatch')
    if value['kind'] == 'estimate':
        bounds = value.get('range')
        if (not value.get('basis') or not isinstance(bounds, list) or len(bounds) != 2
                or any(type(n) not in (int, float) or not math.isfinite(n) for n in bounds)
                or not 0 <= bounds[0] <= number <= bounds[1]):
            raise ValueError('Estimate needs a sourced basis and uncertainty range')


def validate(data):
    if (data.get('authority') != 'candidate_intelligence' or data.get('canonical_accepted_count') != 0
            or data.get('pipeline_mutation') is not False):
        raise ValueError('Commercial view authority mismatch')
    foundation, blocks = technology.load()
    keys = {r['key'] for r in foundation['providers']}
    if set(data['participants']) - keys or set(data['profiles']) - keys:
        raise ValueError('View cannot create a new canonical enterprise')
    for key, source in data['sources'].items():
        parsed = urlsplit(source['url'])
        if (source['id'] != key or parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password
                or source.get('accepted') is not False or source.get('rights') != 'unestablished'
                or not source.get('excerpt') or not source.get('locator') or not source.get('reviewed_at')):
            raise ValueError('Reviewed public passage provenance required')
    for row in data['participants'].values():
        for key in ('uk_revenue', 'uk_workforce'):
            validate_metric(row.get(key), data['sources'], uk=True)
            if row.get(key) and row[key]['unit'] != ('GBP' if key == 'uk_revenue' else 'people'):
                raise ValueError('Comparison columns require consistent currency and units')
        signal = row.get('signal')
        if signal and (signal.get('kind') not in ('observation', 'hypothesis') or not signal.get('source_ids') or set(signal['source_ids']) - set(data['sources'])):
            raise ValueError('Commercial signal requires classification and sources')
        if set(row.get('foundation_blocks', [])) - set(blocks):
            raise ValueError('Unknown retained research passage')
    for profile in data['profiles'].values():
        for value in profile['metrics'].values():
            validate_metric(value, data['sources'])
        for key in ('strategy', 'pressures', 'relationships', 'programmes', 'opportunities'):
            for row in profile[key]:
                expected = 'hypothesis' if key == 'opportunities' else 'observation'
                if row.get('kind') != expected or not row.get('source_ids') or set(row['source_ids']) - set(data['sources']):
                    raise ValueError('Observation/hypothesis boundary or provenance mismatch')
                if expected == 'hypothesis' and not all(row.get(k) for k in ('buyer', 'basis', 'qualification', 'countercase')):
                    raise ValueError('Hypothesis requires buyer scope, basis and qualification')


def load():
    if DATA.is_symlink() or not DATA.is_file() or not DATA.resolve().is_relative_to(technology.ROOT):
        raise ValueError('Commercial view asset unavailable')
    raw = DATA.read_bytes()
    if sha256(raw).hexdigest() != DATA_SHA256:
        raise ValueError('Commercial research changed; reconcile before presentation')
    data = json.loads(raw)
    validate(data)
    return data


def participants(district='', sort='name', direction='asc'):
    if district not in ('', *technology.SEGMENTS) or sort not in SORT_KEYS or direction not in ('asc', 'desc'):
        raise ValueError('Unknown participant comparison selection')
    foundation, _ = technology.load()
    data = load()
    rows = []
    for provider in foundation['providers']:
        if district and district not in provider['memberships'] and not (district == 'cloud' and provider['key'] in CLOUD_FACILITIES):
            continue
        supplement = data['participants'].get(provider['key'], {})
        rows.append({'key': provider['key'], 'name': provider['label'], 'memberships': provider['memberships'],
                     'role': supplement.get('role', provider['primary_group']), 'specialty': supplement.get('specialty', ''),
                     'uk_revenue': supplement.get('uk_revenue'), 'uk_workforce': supplement.get('uk_workforce'),
                     'signal': supplement.get('signal'), 'foundation_blocks': supplement.get('foundation_blocks') or
                     [p['block'] for p in provider['profile']], 'identity_status': provider['identity_status'],
                     'canonical_enterprise_id': provider['canonical_enterprise_id']})
    def key(row):
        value = row.get(sort)
        if sort in ('uk_revenue', 'uk_workforce'):
            return value['value'] if value else None
        if sort == 'signal':
            return value['title'].casefold() if value else None
        return value.casefold() if value else None
    present = [r for r in rows if key(r) is not None]
    empty = [r for r in rows if key(r) is None]
    # Blanks stay last in either direction; numeric values remain numeric.
    return sorted(present, key=lambda r: (key(r), r['name'].casefold()), reverse=direction == 'desc') + sorted(empty, key=lambda r: r['name'].casefold())


def source_projection(source_id):
    """Reuse existing contracts, without an importer or acceptance side effect."""
    source = load()['sources'][source_id]
    content = source['excerpt']
    digest = sha256(content.encode()).hexdigest()
    identifier = 'tech-commercial:' + source_id
    segment = SourceSegment(identifier + ':segment', source_id, source['locator'], content, digest,
                            str(DATA.relative_to(technology.ROOT)) + '#' + source_id,
                            'candidate_intelligence', 'reviewed_web_excerpt_not_accepted')
    claim = CandidateClaim(identifier, 'public_presentation_passage', content, source_id, segment.segment_id,
                           source['reporting_period'], source_id, 'reports', content, source['reporting_period'],
                           'source passage only', '', 'Source-supported presentation; acceptance withheld',
                           'candidate_intelligence', 'withheld', [], [])
    item = EvidencePackageItem(identifier, 'research_claim_candidate', content, 'reviewed_web_excerpt_not_accepted',
                               'Source-supported presentation', source['reporting_period'], (segment.segment_id,), (), source['url'], '')
    return {'source_segment': asdict(segment), 'candidate_claim': asdict(claim), 'evidence_package_item': item.to_dict(),
            'canonical_enterprise_id': None, 'canonical_evidence_id': None, 'eligible_for_import': False,
            'rights': source['rights'], 'publisher_original_sha256': None}
