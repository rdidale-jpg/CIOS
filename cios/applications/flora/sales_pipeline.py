"""Workspace-scoped commercial records over existing public opportunity hypotheses.

Uses FLORA's existing evaluator, verified transaction and protected file journal.
Public context is never converted into a confirmed customer requirement.
"""
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import json
import re
from uuid import uuid4

from .access import require_capability, require_resource_scope
from .banking_portfolio import BANKS, GENERATED_DATE
from .security import verified_service_read, verified_service_write, require_active_service_write
from .security_store import SecurityStore, canonical, digest
from .storage import atomic_write_json, data_path

STAGES = ('Discovered', 'Researching', 'Validating', 'Qualified', 'Pursuit', 'Proposal', 'Negotiation', 'Won', 'Lost')
ADVANCED = frozenset({'Qualified', 'Pursuit', 'Proposal', 'Negotiation', 'Won'})
CRITERIA = {
    'problem': ('Business problem & measurable impact', 'Describe the customer problem and its measurable consequence.'),
    'priority': ('Customer strategic priority', 'Identify the customer-owned priority and its supporting material.'),
    'buyer': ('Economic buyer & stakeholders', 'Identify the accountable buyer, sponsor and decision stakeholders.'),
    'funding': ('Budget or funding evidence', 'Record funding evidence; an estimated deal value is not a budget.'),
    'decision': ('Decision criteria & process', 'Identify decision criteria, approval steps and who decides.'),
    'competition': ('Competitive landscape', 'Record alternatives, incumbents and evidence of the competitive position.'),
    'differentiation': ('Potential differentiation', 'Explain the proposition advantage and how it will be demonstrated.'),
    'timing': ('Procurement timing', 'Record the customer process/timing source, not a modelled date.'),
    'relationship': ('Relationship strength & champion', 'Describe access, customer engagement and the champion evidence.'),
    'next_action': ('Next action & mutual commitment', 'Record a concrete next step and supporting customer engagement.'),
}


class SalesValidationError(ValueError):
    pass


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def _text(value, limit=2000):
    if not isinstance(value, str) or len(value) > limit or any(ord(c) < 32 and c not in '\n\t' for c in value):
        raise SalesValidationError('Use bounded plain-text values.')
    return value.strip()


def hypothesis(slug, origin):
    bank = BANKS.get(slug)
    if bank is None:
        raise SalesValidationError('Choose a supported Banking enterprise.')
    opportunity = next((o for o in bank.opportunities if o.id == origin), None)
    if opportunity is None:
        raise SalesValidationError('Choose an existing enterprise hypothesis.')
    return bank, opportunity


def _path():
    return data_path('sales_pipeline', 'opportunities.json')


def _load():
    if not _path().exists():
        return {'schema_version': 1, 'records': {}}
    result = json.loads(_path().read_text())
    if result.get('schema_version') != 1 or not isinstance(result.get('records'), dict):
        raise SalesValidationError('Pipeline storage format is unavailable.')
    return result


def _supported(value):
    return (isinstance(value, str) and bool(value.strip())
            and value.strip().casefold() not in {'unknown', 'tbc', 'tbd', 'n/a', 'none', 'not known', 'not supplied', 'not available'})


def qualification(record):
    fields = record.get('qualification', {})
    complete = [key for key in CRITERIA if _supported(fields.get(key, {}).get('note')) and _supported(fields.get(key, {}).get('source'))]
    return {'complete': complete, 'missing': [k for k in CRITERIA if k not in complete],
            'percent': len(complete) * 100 // len(CRITERIA),
            'rationale': 'Completeness only: each criterion needs a note and supporting reference; Unknown/TBC placeholders remain missing. Not win probability, AI confidence or independent evidence verification.'}


def maturity(record):
    if record['stage'] == 'Won':
        return 'Won — user-confirmed demonstration outcome'
    if record['stage'] == 'Lost':
        return 'Closed / Lost'
    if record['stage'] in ADVANCED:
        return 'Active pursuit' if record['stage'] in {'Pursuit', 'Proposal', 'Negotiation', 'Won'} else 'Qualified sales opportunity'
    if record.get('evidence_reviewed') and {'problem', 'priority'} <= set(qualification(record)['complete']):
        return 'Evidence-backed potential opportunity'
    return 'Opportunity hypothesis'


def _scope(headers, record, capability):
    # The persisted workspace and enterprise are immutable, not payload overrides.
    return require_resource_scope(headers, capability, record.get('enterprise_id', ''), record.get('workspace_id', ''), require_acl=False)


def _persist(envelope, record, actor, action, changes):
    record['version'] = record.get('version', 0) + 1
    record['updated_at'] = now()
    event = {'at': record['updated_at'], 'actor': actor.user_id, 'workspace_id': actor.workspace,
             'action': action, 'version': record['version'], 'changes': changes}
    record.setdefault('history', []).append(event)
    envelope['records'][record['id']] = record
    atomic_write_json(_path(), envelope)
    with SecurityStore().transaction() as db:
        SecurityStore().audit(db, 'sales_opportunity_mutation', resource_id=record['id'],
            record_digest=digest(canonical(record)), user_id=actor.user_id, workspace_id=actor.workspace,
            membership_id=actor.membership.membership_id, membership_version=actor.membership.version,
            session_ref=actor.session.session_ref, version=record['version'], action=action)
    return deepcopy(record)


@verified_service_write('commercial_context.edit')
def create_opportunity(slug, origin='', values=None, headers=None):
    actor = require_active_service_write(headers, 'commercial_context.edit')
    from .research_intelligence.registry import enterprise_reference, landscape_url
    bank = enterprise_reference(slug)
    if bank is None:
        raise SalesValidationError('Choose a supported enterprise.')
    require_resource_scope(headers, 'commercial_context.edit', bank.id, actor.workspace, require_acl=False)
    values = values or {}
    if set(values) - {'title', 'problem', 'solution', 'next_action'}:
        raise SalesValidationError('Creation accepts commercial fields only; scope is server controlled.')
    envelope = _load()
    if origin:
        research_capture=None
        if origin.startswith('RCO-'):
            from .research_intelligence.model import commercial_capture
            try:
                research_capture=commercial_capture(slug,origin)
            except ValueError as exc:
                raise SalesValidationError(str(exc)) from exc
        else:
            bank, source = hypothesis(slug, origin)
        # Idempotent capture: do not create a second copy in the same workspace.
        existing = next((r for r in envelope['records'].values() if r['workspace_id'] == actor.workspace
                         and r['enterprise_id'] == bank.id and r['origin_id'] == origin), None)
        if existing:
            _scope(headers, existing, 'commercial_context.edit')
            return deepcopy(existing)
        if research_capture is not None:
            defaults=research_capture['fields']
            provenance=research_capture['provenance']
        else:
            defaults = {'title': source.title, 'problem': source.problem, 'solution': ', '.join(source.components), 'next_action': source.next_action}
            provenance = {'kind': 'public_fixture_hypothesis', 'source_labels': list(bank.analyst_sources),
                          'snapshot': GENERATED_DATE, 'signals': list(source.signals),
                          'evidence_url': f'/flora/banking/{slug}/evidence',
                          'origin_url': f'/flora/banking/{slug}/opportunity/{origin}',
                          'limitations': 'Public scenario context; no claim-level accepted Evidence or confirmed customer requirement.'}
    else:
        defaults = {'title': '', 'problem': '', 'solution': '', 'next_action': ''}
        provenance = {'kind': 'user_entered_demonstration', 'source_labels': [], 'signals': [],
                      'snapshot': now(), 'evidence_url': f'/flora/banking/{slug}/evidence' if slug in BANKS else landscape_url(slug),
                      'origin_url': getattr(bank,'origin_url',f'/flora/banking/explorer/{slug}'), 'limitations': 'User-entered demonstration hypothesis; not a verified customer requirement.'}
    fields = {key: _text(values.get(key, value)) for key, value in defaults.items()}
    if not fields['title'] or not fields['problem']:
        raise SalesValidationError('A title and business problem are required.')
    record = {'id': 'opp-'+uuid4().hex, 'workspace_id': actor.workspace, 'enterprise_id': bank.id,
              'enterprise': bank.name, 'enterprise_slug': slug, 'industry': getattr(bank,'industry','Banking'), 'origin_id': origin,
              'demonstration': True, 'stage': 'Discovered', 'owner': actor.user_id, 'priority': 'Normal',
              'confidence': 'Unknown', 'confidence_rationale': 'Claim-level supporting evidence has not been assessed.',
              'created_at': now(), 'created_by': actor.user_id, 'provenance': provenance,
              'qualification': {}, 'evidence_reviewed': False, 'amount': '', 'value_basis': 'Unknown',
              'currency': 'GBP', 'value_reference': '', 'timing': 'Unknown', **fields}
    return _persist(envelope, record, actor, 'created', {'origin_id': origin, 'stage': 'Discovered'})


@verified_service_read('commercial_context.view')
def get_opportunity(identifier, headers=None):
    if not re.fullmatch(r'opp-[a-f0-9]{32}', identifier):
        raise SalesValidationError('Opportunity not found.')
    record = _load()['records'].get(identifier)
    if record is None:
        raise SalesValidationError('Opportunity not found.')
    _scope(headers, record, 'commercial_context.view')
    return deepcopy(record)


@verified_service_read('commercial_context.view')
def list_opportunities(headers=None, filters=None):
    context = require_capability(headers, 'commercial_context.view')
    result = []
    for record in _load()['records'].values():
        if record.get('workspace_id') != context.workspace:
            continue
        try:
            _scope(headers, record, 'commercial_context.view')
        except PermissionError:
            continue
        result.append(deepcopy(record))
    filters = filters or {}
    for key in ('industry', 'enterprise', 'stage', 'owner', 'confidence', 'value_basis'):
        if filters.get(key):
            result = [r for r in result if r.get(key) == filters[key]]
    if filters.get('min_value'):
        if not filters.get('currency'):
            raise SalesValidationError('Select a currency when filtering by amount; no exchange-rate conversion is applied.')
        floor = _amount(filters['min_value'])
        result = [r for r in result if r['amount'] and Decimal(r['amount']) >= Decimal(floor)]
    if filters.get('currency'):
        result = [r for r in result if r['currency'] == filters['currency']]
    return sorted(result, key=lambda r: ({'High': 0, 'Normal': 1, 'Low': 2}[r['priority']],
                                          -datetime.fromisoformat(r['updated_at']).timestamp()))


def _amount(value):
    value = _text(value, 32)
    try:
        amount = Decimal(value)
        if not amount.is_finite() or amount < 0 or amount > Decimal('1000000000000') or amount.as_tuple().exponent < -2:
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        raise SalesValidationError('Value must be a non-negative monetary amount with at most two decimals.')
    return format(amount, 'f')


def totals(records):
    result = {'amounts': {}, 'unknown': 0, 'closed': 0}
    for record in records:
        if record['stage'] in {'Won', 'Lost'}:
            result['closed'] += 1
            continue
        if not record['amount'] or record['value_basis'] == 'Unknown':
            result['unknown'] += 1
            continue
        key = record['currency']+' · '+record['value_basis']
        result['amounts'][key] = format(Decimal(result['amounts'].get(key, '0')) + Decimal(record['amount']), 'f')
    return result


@verified_service_write('commercial_context.edit')
def update_opportunity(identifier, expected_version, values, headers=None):
    actor = require_active_service_write(headers, 'commercial_context.edit')
    envelope = _load()
    record = deepcopy(envelope['records'].get(identifier))
    if not record:
        raise SalesValidationError('Opportunity not found.')
    _scope(headers, record, 'commercial_context.edit')
    if type(expected_version) is not int or record['version'] != expected_version:
        raise SalesValidationError('This record changed. Reload before saving your update.')
    allowed = {'title', 'problem', 'solution', 'next_action', 'owner', 'priority', 'confidence', 'confidence_rationale',
               'timing', 'amount', 'currency', 'value_basis', 'value_reference', 'qualification', 'stage',
               'confirm', 'evidence_reviewed', 'activity', 'closure_evidence'}
    if set(values) - allowed:
        raise SalesValidationError('Record identity, workspace and source provenance cannot be edited.')
    before = deepcopy(record)
    for key in ('title', 'problem', 'solution', 'next_action', 'owner', 'priority', 'confidence', 'confidence_rationale',
                'timing', 'amount', 'currency', 'value_basis', 'value_reference'):
        if key in values:
            record[key] = _text(values[key])
    if not record['title'] or not record['problem'] or not record['owner']:
        raise SalesValidationError('Title, problem and owner are required.')
    if record['priority'] not in {'High', 'Normal', 'Low'} or record['confidence'] not in {'Unknown', 'Low', 'Moderate', 'High'}:
        raise SalesValidationError('Choose a supported priority and evidence assessment.')
    if record['confidence'] != 'Unknown' and not _supported(record['confidence_rationale']):
        raise SalesValidationError('Evidence assessment needs a rationale; it is not sales qualification.')
    if record['currency'] not in {'GBP', 'EUR', 'USD'} or record['value_basis'] not in {'Unknown', 'Estimate', 'Customer-confirmed amount'}:
        raise SalesValidationError('Choose a supported currency and value basis.')
    if record['value_basis'] == 'Unknown':
        if record['amount']:
            raise SalesValidationError('Choose a value basis and reference, or leave the unknown amount blank.')
    else:
        record['amount'] = _amount(record['amount'])
        if not _supported(record['value_reference']):
            raise SalesValidationError('An estimate needs assumptions; a customer-confirmed amount needs its supporting reference.')
    if 'qualification' in values:
        q = values['qualification']
        if not isinstance(q, dict) or set(q) - set(CRITERIA):
            raise SalesValidationError('Unknown qualification criterion.')
        record['qualification'] = {}
        for key, value in q.items():
            if not isinstance(value, dict) or set(value) != {'note', 'source'}:
                raise SalesValidationError('Each qualification criterion needs a note and supporting reference.')
            record['qualification'][key] = {k: _text(v) for k,v in value.items()}
        # Any substantive qualification edit requires a fresh human review.
        record['evidence_reviewed'] = values.get('evidence_reviewed') == 'yes'
    elif 'evidence_reviewed' in values:
        record['evidence_reviewed'] = values['evidence_reviewed'] == 'yes'
    stage = values.get('stage', record['stage'])
    if stage not in STAGES:
        raise SalesValidationError('Choose a supported pipeline stage.')
    reviewed = record['evidence_reviewed']
    if stage in ADVANCED and (qualification(record)['missing'] or not reviewed):
        raise SalesValidationError('Qualified and active stages need all ten supported qualification inputs and user evidence review.')
    if stage != record['stage'] and stage in ADVANCED and values.get('confirm') != 'yes':
        raise SalesValidationError('Explicit user confirmation is required for qualification or pursuit progression.')
    if stage != record['stage'] and stage in {'Won', 'Lost'}:
        closure = _text(values.get('closure_evidence', ''))
        if not _supported(closure) or values.get('confirm') != 'yes':
            raise SalesValidationError('Closing a record requires outcome evidence and explicit confirmation.')
        record['closure_evidence'] = closure
    if record['stage'] in {'Won', 'Lost'} and stage != record['stage']:
        raise SalesValidationError('Closed records cannot be reopened in this increment; create a separately traced hypothesis.')
    record['stage'] = stage
    activity = _text(values.get('activity', ''))
    changes = {key: {'before': before.get(key), 'after': value} for key, value in record.items()
               if key not in {'history', 'updated_at', 'version'} and value != before.get(key)}
    if activity:
        changes['activity'] = activity
    if not changes:
        raise SalesValidationError('No changes to save. Add an activity or update a field.')
    return _persist(envelope, record, actor, 'updated', changes)
