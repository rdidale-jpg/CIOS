"""Versioned operational offers, extending Commercial Context, never Twin truth.

All state uses the existing verified service envelope/protected journal. Matching
is a pure APPA-aligned projection; neither matches nor Studio import Pipeline.
"""
from copy import deepcopy
from dataclasses import asdict
from datetime import date, datetime, timezone
import json
from uuid import uuid4

from . import offer_library as library
from .access import require_capability, is_cios_owner
from .commercial_mission import resolve_commercial_mission, resolve_employer_context, save_employer_context, save_commercial_mission
from .security import verified_service_read, verified_service_write, require_active_service_write
from .security_store import SecurityStore, canonical, digest
from .storage import data_path, atomic_write_json

POLICY = 'offers-pilot-v1'
PATTERNS = {
    'structural-review': ('Structural review', ()),
    'service-dependencies': ('Changing service dependencies', ('LBG-AR25-MIGRATION', 'AV-ICC')),
    'change-value': ('Transformation value', ('LBG-AR25-MIGRATION', 'AV-DIGITAL')),
    'ai-change': ('AI and data change', ('LBG-A2030-DATA',)),
}
BASE = '/flora/offers'
READ_PATHS = frozenset(BASE + s for s in ('', '/company', '/edit', '/review', '/discover', '/studio', '/start'))
WRITE_PATHS = frozenset(BASE + s for s in ('/profile', '/bind', '/select', '/save', '/transition', '/studio-toggle', '/compose', '/revoke', '/onboard-company', '/onboard-preferences', '/onboard-adopt'))
FIELDS = ('name', 'outcome', 'icp', 'buyers', 'trigger', 'entry_play', 'next_test',
          'capabilities', 'partners', 'constraints', 'evidence', 'exclusions', 'trigger_pattern')
VARIATION_FIELDS = frozenset({'name', 'icp', 'buyers', 'entry_play', 'next_test'})
TEMPLATES = {
    'service': {'name': 'Service resilience diagnostic', 'outcome': 'Identify critical-service dependencies and recovery priorities.',
        'icp': 'Technology, Banking, Aviation', 'buyers': 'Service operations / resilience owner',
        'trigger': 'Structural: a change in service dependencies; validate materiality with the owner.',
        'entry_play': 'Offer a permission-based critical-service mapping conversation; start with one service.',
        'next_test': 'Which dependency has measurable customer impact and an accountable owner?',
        'capabilities': 'Illustrative service mapping; seller must establish delivery ability.', 'partners': '',
        'constraints': 'No operational access or delivery rights established; no availability guarantee.',
        'evidence': '', 'exclusions': 'Safety-critical operational control; regulated assurance certification'},
    'consulting': {'name': 'Transformation value diagnostic', 'outcome': 'Test whether an existing change programme has a measurable value case.',
        'icp': 'Technology, Banking, Aviation', 'buyers': 'Transformation sponsor / finance business partner',
        'trigger': 'Structural: announced transformation or investment; budget is not inferred.',
        'entry_play': 'Propose a short value-baseline discussion using customer-approved measures.',
        'next_test': 'What existing programme would benefit from a baseline, and what would disprove the case?',
        'capabilities': 'Illustrative transformation consulting; credentials not established.', 'partners': '',
        'constraints': 'No customer sponsorship, baseline, funding or commercial terms established.',
        'evidence': '', 'exclusions': 'Guaranteed savings; unsupported outsourcing claims'},
    'ai': {'name': 'AI innovation experiment', 'outcome': 'Test one bounded AI use case against a simpler non-AI alternative.',
        'icp': 'Technology, Banking, Aviation', 'buyers': 'Data / AI product owner and risk partner',
        'trigger': 'Structural: reported AI or digital change; residual need requires validation.',
        'entry_play': 'Ask for a use-case comparison workshop with agreed data protections and a stop criterion.',
        'next_test': 'Does AI improve an agreed measure over the current process without unacceptable risk?',
        'capabilities': 'Illustrative AI experimentation; no delivery or vendor accreditation asserted.', 'partners': '',
        'constraints': 'No access to private data, model budget, partner rights or production deployment.',
        'evidence': '', 'exclusions': 'Autonomous decisions; guaranteed ROI; invented vendor partnerships'},
}
for _name, _pattern in (('service', 'service-dependencies'), ('consulting', 'change-value'), ('ai', 'ai-change')):
    TEMPLATES[_name]['trigger_pattern'] = _pattern


def _path():
    return data_path('commercial_context', 'offers-v1', 'context.json')


def _load():
    if not _path().exists():
        return {'schema_version': 1, 'employers': {}, 'users': {}, 'offers': {}}
    value = json.loads(_path().read_text())
    if value.get('schema_version') != 1 or any(not isinstance(value.get(k), dict) for k in ('employers', 'users', 'offers')):
        raise ValueError('Offer context format unavailable')
    return value


def _text(value, maximum=2400):
    if not isinstance(value, str) or len(value) > maximum or any(ord(c) < 32 and c not in '\n\t' for c in value):
        raise ValueError('Use bounded plain text')
    return value.strip()


def _key(context):
    return canonical([context.workspace, context.user_id])


def _actor(headers, edit=False):
    return require_capability(headers, 'commercial_context.edit' if edit else 'commercial_context.view')


def _employer(envelope, context, employer_id):
    employer = envelope['employers'].get(employer_id)
    if (not employer or employer['workspace_id'] != context.workspace or not employer['active']
            or context.user_id not in employer['sellers']):
        raise PermissionError('Employer context unavailable')
    return employer


def _selected(envelope, context):
    employer_id = envelope['users'].get(_key(context), {}).get('employer_id', '')
    return _employer(envelope, context, employer_id)


def _persist(envelope, headers, action, resource):
    context = require_active_service_write(headers, 'commercial_context.edit')
    _path().parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    _path().parent.chmod(0o700)
    atomic_write_json(_path(), envelope)
    _path().chmod(0o600)
    # Only digests and scoped IDs enter the authority audit, not private content.
    with SecurityStore().transaction() as db:
        SecurityStore().audit(db, 'commercial_offer_mutation', action=action,
            resource_id=resource, record_digest=digest(canonical(envelope)),
            user_id=context.user_id, workspace_id=context.workspace,
            membership_id=context.membership.membership_id, membership_version=context.membership.version,
            session_ref=context.session.session_ref)


@verified_service_write('commercial_context.edit', recent=True)
def declare_employer(organisation, expected_version=0, *, headers=None):
    """Edit the existing owner profile without requiring an imported Twin."""
    if not is_cios_owner(headers):
        raise PermissionError('Owner-reviewed pilot setup required')
    current = resolve_employer_context(headers)
    version = current.version if current else 0
    if version != expected_version:
        raise ValueError('Employer profile changed; reload before saving')
    organisation = _text(organisation, 256)
    value = asdict(current) if current and current.organisation == organisation else {}
    if current:
        value['context_id'] = current.context_id
    value.update(organisation=organisation, version=version + 1)
    value.setdefault('field_statuses', {})['organisation'] = 'human-supplied'
    # Existing profile owner supplies storage, workspace guard and audited persistence.
    return save_employer_context(headers, value)


@verified_service_write('commercial_context.edit', recent=True)
def bind_employer(sellers, approvers, approval_reference, *, headers=None):
    """Owner explicitly binds their declared EmployerContext; never grants IAM."""
    context = _actor(headers, True)
    if not is_cios_owner(headers):
        raise PermissionError('Explicit CIOS owner binding required')
    profile = resolve_employer_context(headers)
    if not profile or not profile.organisation or not _text(approval_reference, 300):
        raise ValueError('Configure My Company and supply the binding approval reference')
    sellers = sorted(set(_text(s, 128) for s in sellers))
    approvers = sorted(set(_text(s, 128) for s in approvers))
    if not sellers or not approvers or not set(approvers) <= set(sellers):
        raise ValueError('Named sellers and approvers are required; approvers must be bound sellers')
    with SecurityStore().transaction() as db:
        members = {r[0] for r in db.execute('SELECT user_id FROM memberships WHERE workspace_id=? AND active=1', (context.workspace,))}
    if not set(sellers + approvers) <= members:
        raise PermissionError('Delegates must be active members of this workspace')
    envelope = _load()
    employer_id = 'employer-' + digest(canonical([context.workspace, profile.context_id, profile.organisation]))[:24]
    prior = envelope['employers'].get(employer_id)
    # Repeat binding is an explicit ACL revision; prior versions cannot silently survive it.
    employer = {'id': employer_id, 'workspace_id': context.workspace, 'organisation': profile.organisation,
        'profile_context_id': profile.context_id, 'profile_version': profile.version,
        'participant_twin_id': None, 'sellers': sellers, 'approvers': approvers, 'active': True,
        'approval_reference': _text(approval_reference, 300), 'bound_by': context.user_id,
        'version': prior['version'] + 1 if prior else 1}
    envelope['employers'][employer_id] = employer
    _persist(envelope, headers, 'employer_binding', employer_id)
    return deepcopy(employer)


@verified_service_write('commercial_context.edit', recent=True)
def revoke_employer(employer_id, *, headers=None):
    context = _actor(headers, True)
    envelope = _load()
    employer = envelope['employers'].get(employer_id)
    if not is_cios_owner(headers) or not employer or employer['workspace_id'] != context.workspace:
        raise PermissionError('Binding unavailable')
    employer['active'] = False
    employer['version'] += 1
    _persist(envelope, headers, 'employer_revoked', employer_id)


@verified_service_write('commercial_context.edit')
def select_employer(employer_id, *, headers=None):
    context = _actor(headers, True)
    envelope = _load()
    _employer(envelope, context, employer_id)
    settings = envelope['users'].setdefault(_key(context), {})
    settings['employer_id'] = employer_id
    _persist(envelope, headers, 'employer_selected', employer_id)



@verified_service_write('commercial_context.edit')
def configure_library(selected, employer_id, employer_version, mission_version, *, headers=None):
    """Private supplier categories, separate from target customer sectors and IAM."""
    context = _actor(headers, True)
    employer = _selected(_load(), context)
    if employer['id'] != employer_id or employer['version'] != employer_version:
        raise ValueError('Employer authorisation changed; reload setup')
    selected = library.categories(selected)
    mission = resolve_commercial_mission(headers)
    if (mission.version if mission else 0) != mission_version:
        raise ValueError('Commercial preferences changed; reload setup')
    value = asdict(mission) if mission else {
        'executive_role': 'Seller', 'commercial_objective': 'Explore declared technology offers'}
    value.update(technology_subindustries=selected, offer_library_employer_id=employer_id,
                 version=mission_version + 1)
    return save_commercial_mission(headers, value)


@verified_service_write('commercial_context.edit')
def adopt_library(references, employer_id, employer_version, mission_version, confirmed=False, *, headers=None):
    """Atomic, explicitly selected private drafts in the existing offer journal.

    Validate the whole selection first. No capability assertion, approval, matching
    write or Pipeline capture is implied. Repeated selection is idempotent.
    """
    context = _actor(headers, True)
    envelope = _load()
    employer = _selected(envelope, context)
    mission = resolve_commercial_mission(headers)
    if (employer['id'] != employer_id or employer['version'] != employer_version or not mission
            or mission.offer_library_employer_id != employer_id or mission.version != mission_version):
        raise ValueError('Company or preferences changed; reload setup')
    selected = library.categories(mission.technology_subindustries)
    if confirmed is not True:
        raise ValueError('Confirm these are private examples requiring seller proof and independent review')
    if not isinstance(references, (list, tuple)) or not 1 <= len(references) <= 12:
        raise ValueError('Select between one and twelve developed offers')
    rows = []
    for ref in references:
        if not isinstance(ref, dict) or set(ref) != {'id', 'version', 'digest'}:
            raise ValueError('Invalid library reference')
        row = library.template(ref['id'], ref['version'])
        if library.fingerprint(row) != ref['digest'] or not set(row['subindustries']) & set(selected):
            raise ValueError('Library selection changed or does not match your business categories')
        rows.append(row)
    if len({r['id'] for r in rows}) != len(rows):
        raise ValueError('Select each offer only once')
    result = []
    for row in rows:
        source = library.source_ref(row)
        existing = next((versions[-1] for versions in envelope['offers'].values()
            if versions[-1]['author'] == context.user_id and versions[-1]['employer_id'] == employer_id
            and versions[-1]['workspace_id'] == context.workspace and versions[-1]['state'] != 'retired'
            and versions[-1].get('template_source') == source), None)
        if existing:
            result.append(deepcopy(existing))
            continue
        record = save_offer(library.offer_content(row), headers=headers)
        envelope = _load()
        stored = envelope['offers'][record['id']][-1]
        stored['template_source'] = source
        stored['library_playbook'] = deepcopy(row)
        stored['classification'] = 'private example offer; seller capability and customer demand unverified'
        _persist(envelope, headers, 'library_example_adopted', record['id'])
        result.append(deepcopy(stored))
    return result

def _visible(record, context, employer):
    return (record['workspace_id'] == context.workspace and record['employer_id'] == employer['id']
        and (record['author'] == context.user_id or record['state'] == 'employer_approved'
             or (record['state'] == 'submitted_for_review' and context.user_id in employer['approvers'])))


def _record(envelope, context, employer, offer_id, version=None):
    versions = envelope['offers'].get(offer_id, [])
    record = next((r for r in versions if r['version'] == version), None) if version is not None else (versions[-1] if versions else None)
    if not record or not _visible(record, context, employer):
        raise PermissionError('Offer unavailable')
    return record


def _eligible(envelope, record):
    versions = envelope['offers'][record['id']]
    if record is not versions[-1] or record['state'] not in {'private_draft', 'employer_approved'}:
        return False
    if record.get('template_source') and not library.current(record['template_source']):
        return False
    if record.get('parent'):
        parent = record['parent']
        latest = envelope['offers'].get(parent['id'], [])
        if (not latest or latest[-1]['version'] != parent['version']
                or latest[-1]['state'] != 'employer_approved' or not _eligible(envelope, latest[-1])):
            return False
    for component in record.get('components', []):
        latest = envelope['offers'].get(component['id'], [])
        if (not latest or latest[-1]['version'] != component['version']
                or latest[-1]['state'] != 'employer_approved' or not _eligible(envelope, latest[-1])):
            return False
    return True


@verified_service_read('commercial_context.view')
def snapshot(*, headers=None):
    context = _actor(headers)
    envelope = _load()
    employers = [deepcopy(e) for e in envelope['employers'].values()
                 if e['workspace_id'] == context.workspace and e['active'] and context.user_id in e['sellers']]
    user = envelope['users'].get(_key(context), {})
    selected = next((e for e in employers if e['id'] == user.get('employer_id')), None)
    records = []
    if selected:
        for versions in envelope['offers'].values():
            for record in versions:
                if _visible(record, context, selected):
                    records.append({**deepcopy(record), 'current': record is versions[-1], 'eligible': _eligible(envelope, record)})
    return {'employers': employers, 'selected': selected, 'offers': records,
        'studio_enabled': bool(user.get('studio_enabled', False)), 'user_id': context.user_id,
        'owner': is_cios_owner(headers)}


@verified_service_write('commercial_context.edit')
def save_offer(values, offer_id='', expected_version=0, parent_id='', parent_version=0, *, headers=None):
    context = _actor(headers, True)
    envelope = _load()
    employer = _selected(envelope, context)
    if set(values) - set(FIELDS):
        raise ValueError('Unsupported offer fields')
    prior = _record(envelope, context, employer, offer_id) if offer_id else None
    if prior:
        can_revise_master = prior['state'] == 'employer_approved' and context.user_id in employer['approvers']
        can_edit_private = prior['author'] == context.user_id and prior['state'] in {'private_draft', 'changes_requested', 'rejected'}
        if not (can_revise_master or can_edit_private):
            raise PermissionError('Create a private variation; employer master revisions require a delegated approver')
    if expected_version != (prior['version'] if prior else 0):
        raise ValueError('Offer changed; reload before saving')
    parent = prior.get('parent') if prior else None
    if parent_id:
        if prior:
            raise ValueError('Parent lineage is immutable')
        master = _record(envelope, context, employer, parent_id, parent_version)
        if master['state'] != 'employer_approved' or not _eligible(envelope, master):
            raise ValueError('Choose a current approved parent')
        parent = {'id': parent_id, 'version': parent_version}
    content = deepcopy(prior['content']) if prior else {k: '' for k in FIELDS}
    if parent:
        master = _record(envelope, context, employer, parent['id'], parent['version'])
        if not _eligible(envelope, master):
            raise ValueError('Parent changed; create a new variation against the current version')
        if any(k not in VARIATION_FIELDS and _text(v) != master['content'][k] for k, v in values.items()):
            raise ValueError('Protected parent claims cannot be overridden')
        content = deepcopy(master['content']) | ({k: v for k, v in content.items() if k in VARIATION_FIELDS} if prior else {})
    content.update({k: _text(v) for k, v in values.items()})
    content['trigger_pattern'] = content.get('trigger_pattern') or 'structural-review'
    if content['trigger_pattern'] not in PATTERNS:
        raise ValueError('Choose a supported trigger pattern')
    if any(not content[k] for k in ('name', 'outcome', 'icp', 'buyers', 'trigger', 'entry_play', 'next_test', 'capabilities', 'constraints')):
        raise ValueError('Complete the outcome, customer, trigger, play, capability and constraint fields')
    identifier = offer_id or 'offer-' + uuid4().hex
    record = {'id': identifier, 'version': expected_version + 1, 'workspace_id': context.workspace,
        'employer_id': employer['id'], 'author': context.user_id, 'state': 'private_draft', 'content': content,
        'parent': parent, 'components': deepcopy(prior.get('components', [])) if prior else [],
        'kind': prior['kind'] if prior else ('variation' if parent else 'seller'),
        'created_at': datetime.now(timezone.utc).isoformat(), 'canonical_offer_ref': None,
        'classification': prior['classification'] if prior else 'human-supplied operational context', 'review': None}
    lineage_owner = prior or (master if parent else {})
    for key in ('target_context', 'composition_review', 'template_source', 'library_playbook'):
        if key in lineage_owner:
            record[key] = deepcopy(lineage_owner[key])
    envelope['offers'].setdefault(identifier, []).append(record)
    _persist(envelope, headers, 'offer_version_saved', identifier)
    return deepcopy(record)


@verified_service_write('commercial_context.edit', recent=True)
def transition(offer_id, expected_version, action, approval_reference='', *, headers=None):
    context = _actor(headers, True)
    envelope = _load()
    employer = _selected(envelope, context)
    record = _record(envelope, context, employer, offer_id)
    if record['version'] != expected_version:
        raise ValueError('Offer changed; reload before review')
    if action in {'submit', 'approve'} and record.get('template_source') and not library.current(record['template_source']):
        raise ValueError('Library version changed or withdrawn; adopt and review the current playbook explicitly')
    if action == 'approve' and record.get('template_source') and not record['content']['evidence']:
        raise ValueError('Seller delivery proof and rights references are required; library sources are not seller evidence')
    author = record['author'] == context.user_id
    permitted = ((action == 'submit' and author and record['state'] in {'private_draft', 'changes_requested'})
        or (action in {'approve', 'reject', 'changes'} and record['state'] == 'submitted_for_review'
            and context.user_id in employer['approvers'] and not author)
        or (action == 'retire' and ((author and record['state'] != 'employer_approved') or context.user_id in employer['approvers'])
            and record['state'] != 'retired'))
    if not permitted:
        raise PermissionError('Separate authorised review required')
    reference = _text(approval_reference, 300)
    if action in {'approve', 'reject', 'changes'} and not reference:
        raise ValueError('Record the review/rights approval reference')
    if action == 'approve':
        if record.get('parent'):
            p = record['parent']; master = _record(envelope, context, employer, p['id'], p['version'])
            if not _eligible(envelope, master):
                raise ValueError('Parent is no longer current')
        for component in record.get('components', []):
            part = _record(envelope, context, employer, component['id'], component['version'])
            if part['state'] != 'employer_approved' or not _eligible(envelope, part):
                raise ValueError('Composite components require current organisational approval')
    updated = deepcopy(record)
    updated['version'] += 1
    updated['state'] = {'submit': 'submitted_for_review', 'approve': 'employer_approved',
        'reject': 'rejected', 'changes': 'changes_requested', 'retire': 'retired'}[action]
    updated['review'] = {'actor': context.user_id, 'reference': reference, 'action': action,
        'at': datetime.now(timezone.utc).isoformat(), 'from_version': record['version']}
    envelope['offers'][offer_id].append(updated)
    _persist(envelope, headers, 'offer_' + action, offer_id)
    return deepcopy(updated)


@verified_service_write('commercial_context.edit')
def studio_toggle(enabled, *, headers=None):
    if type(enabled) is not bool:
        raise ValueError('Explicit boolean activation required')
    context = _actor(headers, True)
    envelope = _load()
    _selected(envelope, context)
    envelope['users'].setdefault(_key(context), {})['studio_enabled'] = enabled
    _persist(envelope, headers, 'studio_enabled' if enabled else 'studio_disabled', context.user_id)


@verified_service_write('commercial_context.edit')
def compose(components, enterprise_slug='', *, headers=None):
    context = _actor(headers, True)
    envelope = _load()
    employer = _selected(envelope, context)
    if not envelope['users'].get(_key(context), {}).get('studio_enabled', False):
        raise PermissionError('Creative Offers Studio is disabled')
    enterprise = accounts().get(enterprise_slug)
    if not enterprise:
        raise ValueError('Select an authorised account context for the value hypothesis')
    if not enterprise['id'].startswith('presentation:'):
        require_capability(headers, 'commercial_context.view', enterprise['id'], context.workspace)
    if len(components) != 2 or len({c[0] for c in components}) != 2:
        raise ValueError('Choose two different accessible approved offers')
    parts = [_record(envelope, context, employer, identifier, int(version)) for identifier, version in components]
    if any(p['state'] != 'employer_approved' or not _eligible(envelope, p) or not p['content']['evidence'] for p in parts):
        raise ValueError('Components need current approval and evidence references; verify delivery rights at review')
    content = {k: '\n'.join(dict.fromkeys(p['content'][k] for p in parts if p['content'][k])) for k in FIELDS}
    content['name'] = 'Explore: ' + ' + '.join(p['content']['name'] for p in parts)
    content['next_test'] += '\nCompare each existing offer alone; prefer the simpler option unless the bundle adds measurable value.'
    content['trigger_pattern'] = parts[0]['content']['trigger_pattern']
    # Do not invent capabilities/partners; preserve explicit component dependencies.
    record = save_offer(content, headers=headers)
    envelope = _load()
    stored = envelope['offers'][record['id']][-1]
    stored['kind'] = 'composite'
    stored['classification'] = 'derived_private_composite_candidate'
    stored['target_context'] = {'enterprise_id': enterprise['id'], 'research_digest': digest(canonical(enterprise)),
        'source_cut_off': '2026-11-13'}
    stored['composition_review'] = {
        'value_thesis': 'Test whether the combined outcomes matter to ' + enterprise['name'] + '; residual need is not established.',
        'simpler_alternative': 'Use either existing offer alone or retain the current solution.',
        'differentiation': 'Not established; validate against the simpler alternative.',
        'feasibility': 'Component declarations retain their original status; combined delivery and partner rights need separate review.',
        'next_test': content['next_test']}

    stored['components'] = [{'id': p['id'], 'version': p['version']} for p in parts]
    _persist(envelope, headers, 'private_composite_saved', record['id'])
    return deepcopy(stored)


# Public account adapters retain their owning research contracts and verification.
# These are adapter-input seals, not an Evidence store or acceptance decision.
# Reconcile the policy/cutoff before a changed upstream overlay can enter matching.
REVIEWED_ACCOUNT_DIGESTS = {
    'lloyds': '6687039517eba7b8aa531c74c25a7d8f81836d211c6bdcf61c130a17d946e1c5',
    'easyjet': '413774700cbd08e5f5eca14046a75fb4d70bd4c6e3b94a84715688e7030b40b1',
    'equinix': '6f40eaf24b9723272a987bb3718e5171ca3ab2df45f391832522a9656bdf6996',
}
ACCOUNT_CONFIG = {
    'lloyds': ('banking', ('LBG-AR25-MIGRATION', 'LBG-A2030-DATA', 'LBG-ENVOY-CONTROLS', 'LBG-SOURCING-ACCESS')),
    'easyjet': ('aviation', ('AV-DIGITAL', 'AV-ICC', 'AV-MRO', 'AV-PROCUREMENT')),
}


def accounts():
    from .research_intelligence.model import load_assessment, claim_segment
    result = {}
    for slug, (domain, ids) in ACCOUNT_CONFIG.items():
        data = load_assessment(domain)
        claims = {c['id']: c for c in data['claims']}
        selected = [claims[i] for i in ids]
        sources = {s['id']: s for s in data['sources']}
        lineage = []
        for claim in selected:
            segment = claim_segment(data, claim)
            lineage.append({'claim_id': claim['id'], 'statement': claim['statement'],
                'classification': claim['verification'], 'period': claim['reporting_period'],
                'segment_id': segment.segment_id, 'content_sha256': segment.content_hash,
                'source_refs': [deepcopy(sources[s]) for s in claim['source_ids']]})
        result[slug] = {'id': data['enterprise_twin_id'], 'slug': slug, 'name': data['enterprise_name'],
            'industry': data['industry_name'], 'knowledge_date': '2026-11-13',
            'authority': data['authority'], 'lineage': lineage,
            'observation_lineage': [], 'limitations': ['Existing research status preserved; no new acceptance.',
                'No access, budget, current procurement or unmet need established.'],
            'counter_indicators': [c['statement'] for c in selected[2:]],
            'url': '/enterprises/' + slug}
    # Technology source remains the existing read-only presentation; no canonical entity is invented.
    from .research_intelligence.technology_experience import REPORT_URL, SOURCE_NOTE
    result['equinix'] = {'id': 'presentation:equinix', 'slug': 'equinix', 'name': 'Equinix', 'industry': 'Technology',
        'knowledge_date': '2026-11-12', 'authority': 'public_presentation_research_not_canonical',
        'lineage': [{'claim_id': 'presentation:equinix-annual-report',
            'statement': 'Existing Technology presentation cites Equinix FY2025 annual reporting for the cloud/data-centre account context.',
            'classification': 'presentation_citation_only', 'period': 'FY2025',
            'segment_id': None, 'content_sha256': digest(SOURCE_NOTE),
            'source_refs': [{'id': 'existing-technology-report', 'title': 'Equinix FY2025 annual report',
                'url': REPORT_URL, 'verification': 'presentation_citation_only', 'limitation': SOURCE_NOTE}]}],
        'observation_lineage': [], 'limitations': ['Canonical identity unbound; presentation citation is not accepted evidence.',
            'No account-specific buying event, access, budget or procurement established.'],
        'counter_indicators': ['Existing infrastructure and in-house capability may remove the need for an external diagnostic.'],
        'url': '/industries/technology/experience/enterprise?enterprise=equinix'}
    if any(digest(canonical(account)) != REVIEWED_ACCOUNT_DIGESTS[slug] for slug, account in result.items()):
        raise ValueError('Offers source snapshot changed; reconcile policy and evidence cutoff before matching')
    return result


def assess_fit(seller, offer, enterprise, evidence_cutoff, policy=POLICY):
    """The ONLY matcher: no IO, writes, clock, random ID, journey or paid calls."""
    cutoff = date.fromisoformat(evidence_cutoff)
    if policy != POLICY:
        raise ValueError('Unsupported assessment policy')
    available = date.fromisoformat(enterprise['knowledge_date']) <= cutoff
    lineage = deepcopy(enterprise['lineage']) if available else []
    excluded = any(s.casefold() in {enterprise['slug'].casefold(), enterprise['id'].casefold(), enterprise['name'].casefold()} for s in seller.get('excluded_accounts', ()))
    sector_fit = any(s.strip().casefold() in enterprise['industry'].casefold() for s in offer['content']['icp'].split(','))
    if offer.get('target_context') and offer['target_context']['enterprise_id'] != enterprise['id']:
        sector_fit = False
    approved = offer['state'] == 'employer_approved'
    pattern = offer['content'].get('trigger_pattern', 'structural-review')
    playbook = offer.get('library_playbook')
    context_ids = playbook['research_context_claim_ids'] if playbook else PATTERNS[pattern][1]
    indicators = [r for r in lineage if r['claim_id'] in context_ids]
    posture = 'deprioritise' if excluded or not sector_fit else ('validate' if indicators else 'research')
    if indicators and not excluded and sector_fit and offer['content']['partners']:
        posture = 'partner'
    identity = {'seller': seller, 'offer': [offer['id'], offer['version'], digest(canonical(offer))],
        'enterprise': enterprise['id'], 'cutoff': evidence_cutoff, 'policy': policy,
        'research_digest': digest(canonical(enterprise)), 'available_lineage': lineage}
    assessment_id = 'fit-' + digest(canonical(identity))[:32]
    hypotheses = [{'id': assessment_id + ':hypothesis', 'status': 'proposed',
        'statement': 'Test whether ' + offer['content']['outcome'].rstrip('.') + ' is relevant to ' + enterprise['name'] + '.',
        'supporting_evidence': [r['claim_id'] for r in lineage], 'contradictory_evidence': enterprise['counter_indicators'] if available else [],
        'validation_question': offer['content']['next_test']}]
    result = {'assessment_id': assessment_id, 'offer_id': offer['id'], 'offer_version': offer['version'],
        'enterprise_id': enterprise['id'], 'enterprise_name': enterprise['name'], 'enterprise_slug': enterprise['slug'],
        'source_cut_off': evidence_cutoff, 'policy_version': policy, 'status': 'pilot_interpretation_not_accepted_APPA',
        'account_twin_id': None if enterprise['id'].startswith('presentation:') else enterprise['id'],
        'participant_twin_id': seller.get('participant_twin_id'), 'opportunity_or_pressure_id': hypotheses[0]['id'],
        'account_need': 'Hypothesis to validate: ' + offer['content']['outcome'],
        'material_pressure': offer['content']['trigger'], 'trigger_evaluation': PATTERNS[pattern][0] + ': ' + ('relevant reported change; residual need is a hypothesis.' if indicators else 'no matching account-specific indicator.') + ' No buying event or urgency established.',
        'capability_fit': 'Sector applicability only; delivery fit requires validation.' if sector_fit else 'Outside declared target sectors.',
        'credibility': 'Employer-approved proposition; delivery proof still requires review.' if approved else 'Private seller declaration; no employer approval.',
        'participant_strengths': [{'classification': 'human-supplied', 'statement': offer['content']['capabilities']}],
        'participant_weaknesses': [offer['content']['constraints']],
        'relationship_access': 'Unknown; ask permission to reach the accountable buyer.',
        'stakeholder_access': offer['content']['buyers'] + ' (proposed roles, not named contacts)',
        'incumbent_advantage': 'Unknown; existing solutions may already address the need.',
        'route_to_market': 'Validate authorised access first.', 'commercial_frameworks': [],
        'delivery_confidence': 'Unverified', 'partner_dependencies': offer['content']['partners'],
        'competitive_alternatives': ['Retain existing solution', 'Customer in-house delivery', 'Use an existing offer alone'],
        'delivery_risk': offer['content']['constraints'], 'commercial_conflict': 'Not assessed',
        'addressability': 'Excluded by mission' if excluded else 'Not qualified',
        'economics': None, 'confidence': {'need': 'Hypothesis', 'access': 'Unknown', 'delivery': 'Unverified'},
        'unknowns': ['Residual need and material impact', 'Buyer, access and funding', 'Delivery proof and partner rights', 'Current competitive position'],
        'contradictions': deepcopy(enterprise['counter_indicators']) if available else [],
        'recommended_posture': posture, 'appa_posture': 'learn' if posture == 'research' else posture,
        'what_not_to_claim': ['Buying intent', 'Approved procurement', 'Customer relationship', 'Guaranteed ROI', 'Verified delivery'],
        'entry_play': offer['content']['entry_play'], 'next_validation_action': offer['content']['next_test'],
        'why_account': indicators[0]['statement'] if indicators else 'No account-specific indicator for this pattern at the selected cutoff; research the fit first.',
        'why_offer': offer['content']['outcome'], 'why_now': 'Explore timing with the owner; no urgency inferred.',
        'evidence_lineage': lineage, 'observation_lineage': deepcopy(enterprise['observation_lineage']),
        'hypothesis_lineage': hypotheses, 'offer_evidence': offer['content']['evidence'],
        'limitations': deepcopy(enterprise['limitations']), 'pipeline_eligible': False}
    if playbook:
        result['trigger_evaluation'] = ('Authored example patterns; existing account context may inform validation. '
            'Structural and event patterns are not observed buying triggers. No buying event or urgency established.')
        result['material_pressure'] = 'Pattern to validate: ' + result['material_pressure']
        result['entry_plays'] = deepcopy(playbook['entry_plays'])
        result['library_context'] = {
            'pattern_policy': 'technology-archetype-context-v1',
            'template_source': deepcopy(offer['template_source']),
            'structural_patterns': deepcopy(playbook['structural_triggers']),
            'event_patterns': deepcopy(playbook['event_triggers']),
            'status': 'Authored patterns only; account context is not an observed buying trigger',
            'seller_proof': 'Required; taxonomy bibliography does not validate seller capability',
            'source_ids': list(playbook['source_ids'])}
    return result


@verified_service_read('commercial_context.view')
def discover(mode='offer', selected='', evidence_cutoff='2026-11-13', *, headers=None):
    if mode not in {'offer', 'account'}:
        raise ValueError('Choose offer-led or account-led discovery')
    if date.fromisoformat(evidence_cutoff) > date.today():
        raise ValueError('Evidence cutoff cannot be in the future')
    context = _actor(headers)
    envelope = _load()
    employer = _selected(envelope, context)
    mission = resolve_commercial_mission(headers)
    seller = {'user_id': context.user_id, 'workspace_id': context.workspace,
        'employer_id': employer['id'], 'employer_version': employer['version'],
        'participant_twin_id': employer['participant_twin_id'],
        'mission_id': mission.context_id if mission else None, 'mission_version': mission.version if mission else None,
        'excluded_accounts': list(mission.excluded_accounts) if mission else []}
    eligible = [versions[-1] for versions in envelope['offers'].values()
                if _visible(versions[-1], context, employer) and _eligible(envelope, versions[-1])]
    targets = accounts()
    if selected and mode == 'offer':
        chosen = _record(envelope, context, employer, selected)
        if not _eligible(envelope, chosen):
            raise ValueError('Offer needs current review')
        eligible = [chosen]
    if selected and mode == 'account':
        if selected not in targets:
            raise ValueError('Account unavailable')
        targets = {selected: targets[selected]}
    results = []
    for enterprise in targets.values():
        # Public presentation context stays public; bound account Twin IDs retain enterprise permission checks.
        if not enterprise['id'].startswith('presentation:'):
            try:
                require_capability(headers, 'commercial_context.view', enterprise['id'], context.workspace)
            except PermissionError:
                continue
        results.extend(assess_fit(seller, offer, enterprise, evidence_cutoff) for offer in eligible)
    return sorted(results, key=lambda r: ({'validate': 0, 'partner': 1, 'research': 2, 'deprioritise': 3}[r['recommended_posture']], r['enterprise_name'], r['offer_id']))
