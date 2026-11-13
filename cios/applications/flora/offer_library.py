"""Read-only commercial archetypes. Never company capability or customer demand."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ASSET = Path(__file__).with_name('offer_library_assets') / 'technology-v1.json'


def catalogue():
    return json.loads(ASSET.read_text(encoding='utf-8'))


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def categories(values):
    if not isinstance(values, (list, tuple)) or not 1 <= len(values) <= 12 or any(type(v) is not str for v in values):
        raise ValueError('Choose a primary business category and optional additional categories')
    allowed = {r['id'] for r in catalogue()['subindustries']}
    if len(set(values)) != len(values) or not set(values) <= allowed:
        raise ValueError('Choose distinct supported business categories')
    return list(values)


def template(identifier, version=None):
    if not isinstance(identifier, str) or len(identifier) > 100:
        raise ValueError('Library offer unavailable')
    row = next((r for r in catalogue()['offers'] if r['id'] == identifier), None)
    if version is not None and (type(version) is not int or version < 1):
        raise ValueError('Invalid library version')
    if not row or row['stage'] != 'deep' or row['status'] != 'active' or (version is not None and version != row['version']):
        raise ValueError('Library offer changed, withdrawn or not yet developed; review the current library')
    return deepcopy(row)


def source_ref(row):
    return {'id': row['id'], 'version': row['version'], 'digest': fingerprint(row),
            'taxonomy_version': row['taxonomy_version'], 'classification': 'seller-declared adoption of a general commercial method'}


def current(ref):
    try:
        return source_ref(template(ref['id'], ref['version'])) == ref
    except (ValueError, KeyError, TypeError):
        return False


def specialisms(values):
    if not isinstance(values, (list, tuple)) or any(type(v) is not str for v in values):
        raise ValueError('Choose supported delivery specialisms')
    allowed = {r['id'] for r in catalogue().get('delivery_specialisms', [])}
    if len(values) > len(allowed) or len(set(values)) != len(values) or not set(values) <= allowed:
        raise ValueError('Choose distinct supported delivery specialisms')
    return list(values)


def suggestions(selected, search='', delivery_specialisms=()):
    selected = categories(selected)
    delivery_specialisms = specialisms(delivery_specialisms)
    if not isinstance(search, str) or len(search) > 120:
        raise ValueError('Use a short offer search')
    q = search.casefold().strip()
    data = catalogue()
    crosswalk = data.get('offer_delivery_specialisms', {})
    labels = {r['id']: r['label'] for r in data.get('delivery_specialisms', [])}
    def searchable(row):
        return ' '.join([row['name'], row['outcome'], *row['synonyms'], *row['capability_tags'],
                         *(labels[s] for s in crosswalk.get(row['id'], []))]).casefold()
    rows = [r for r in data['offers'] if r['stage'] == 'deep' and r['status'] == 'active'
            and set(selected) & set(r['subindustries']) and (not q or q in searchable(r))]
    return sorted(rows, key=lambda r: (r.get('strategic_priority', 100),
        selected[0] not in r['subindustries'],
        not bool(set(delivery_specialisms) & set(crosswalk.get(r['id'], []))),
        -len(set(selected) & set(r['subindustries'])), r['family'], r['name']))


def offer_content(row):
    """Projection onto existing operational fields; bibliography is not seller proof."""
    return {'name': row['name'], 'outcome': row['outcome'], 'icp': ', '.join(row['target_sectors']),
            'buyers': '; '.join(row['buyer_roles']),
            'trigger': '; '.join(p['condition'] for p in row['structural_triggers']),
            'entry_play': row['entry_plays'][0]['point_of_view'] + ' ' + row['entry_plays'][0]['conversation'],
            'next_test': row['entry_plays'][0]['disconfirming_question'],
            'capabilities': 'Seller declaration to validate: ' + '; '.join(row['required_capabilities']),
            'partners': '', 'constraints': '; '.join(row['constraints']), 'evidence': '',
            'exclusions': '; '.join(row['exclusions']), 'trigger_pattern': row['legacy_pattern']}
