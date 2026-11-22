"""Bounded initial research over reviewed statutory-register acquisitions.

This producer only emits Blueprint candidates. The Blueprint services own
receipt, identity mapping, plan approval and canonical execution.
"""
from collections import Counter
from datetime import date
from html.parser import HTMLParser
import hashlib
import io
import json
import re
import zipfile

from .source_import import import_proposal, official_url
from ..blueprint_import.manifest import parse_manifest
from ..blueprint_import.atomicity import validate_atomic_statement

REGISTER = 'https://find-and-update.company-information.service.gov.uk/company/'
IDENTIFIER = re.compile(r'[A-Z0-9]{8}')
FIELDS = {
    'company-type-value': ('identity.legal_form', 'registered legal form', 'Identity and ownership'),
    'company-status': ('identity.register_status', 'register status', 'Identity and ownership'),
    'sic0': ('identity.register_classification', 'declared SIC classification', 'Subsidiaries, divisions and perimeter'),
}


class RegisterFields(HTMLParser):
    """Read only named register fields. Ignore unrelated register content."""

    def __init__(self, allowed):
        super().__init__()
        self.allowed = allowed
        self.fields = {}
        self.tags = []
        self.heading = []
        self.in_heading = False

    def handle_starttag(self, tag, attrs):
        if tag in {'br', 'hr', 'img', 'input', 'link', 'meta', 'source', 'wbr'}:
            return
        if tag == 'h1':
            self.in_heading = True
        key = dict(attrs).get('id')
        if key not in self.allowed:
            key = self.tags[-1][1] if self.tags else None
        elif key in self.fields:
            raise ValueError('Ambiguous register field')
        else:
            self.fields[key] = []
        self.tags.append((tag, key))

    def handle_endtag(self, tag):
        if tag == 'h1':
            self.in_heading = False
        for i in range(len(self.tags) - 1, -1, -1):
            if self.tags[i][0] == tag:
                del self.tags[i:]
                break

    def handle_data(self, value):
        if self.in_heading:
            self.heading.append(value)
        if self.tags and self.tags[-1][1] is not None:
            self.fields[self.tags[-1][1]].append(value)

    def text(self, key):
        return ' '.join(' '.join(self.fields.get(key, ())).split())


def reviewed_register(entry, url, cutoff):
    """Require the exact supplied public register document and current bytes."""
    meta = entry['metadata']
    if (official_url(meta['url']) != url
            or meta['retrieval_url'] != url or meta['publisher'] != 'Companies House'
            or unavailable(meta)):
        raise ValueError('Source scope or lifecycle does not permit this candidate')
    observed = date.fromisoformat(meta['retrieved_at'][:10])
    if observed > cutoff:
        raise ValueError('Source follows commissioned cut-off')
    return observed, import_proposal(entry['path'], meta)


def unavailable(meta):
    return (meta.get('restrictions') or meta.get('withdrawn') is True
            or meta.get('status') in {'withdrawn', 'restricted', 'superseded'})


def verify_control(entry, number, child, cutoff):
    """Verify the specific register listing, not a wider ownership inference."""
    meta = entry['metadata']
    url = REGISTER + child + '/persons-with-significant-control'
    observed, acquisition = reviewed_register(entry, url, cutoff)
    names = {'company-number', 'psc-name-1', 'psc-registration-number-1',
             'psc-status-tag-1', 'psc-notified-on-1'}
    parser = RegisterFields(names)
    parser.feed(acquisition['raw'].decode('utf-8'))
    parser.close()
    if (parser.text('company-number').split()[-1:] != [child]
            or parser.text('psc-registration-number-1').upper() != number
            or parser.text('psc-status-tag-1').casefold() != 'active'):
        raise ValueError('No matching active corporate PSC in the reviewed register entry')
    return observed.isoformat(), {
        'subject_registration': child, 'object_registration': number,
        'predicate': 'listed corporate person with significant control',
        'disclosed_notification': parser.text('psc-notified-on-1'),
        'source_url': url, 'source_locator': 'active PSC entry #1',
        'source_content_sha256': acquisition['primary_content_sha256'],
        'review': 'Canonical endpoints and predicate mapping required',
        'recorded_replay': meta.get('recorded_replay') is True,
        'captured_original_sha256': meta.get('captured_original_sha256'),
    }


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def fingerprint(value):
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def record(identifier, kind, payload):
    return {'external_id': identifier, 'record_class': kind,
            'truth_class': 'observed' if kind == 'observation' else 'evidence_record', 'payload': payload}


def verify_register(entry, number, legal_name, cutoff):
    """Use the existing reviewed-acquisition boundary and extract named fields."""
    url = REGISTER + number
    observed, acquisition = reviewed_register(entry, url, cutoff)
    parser = RegisterFields({'company-number', *FIELDS})
    parser.feed(acquisition['raw'].decode('utf-8'))
    parser.close()
    if parser.text('company-number').split()[-1:] != [number]:
        raise ValueError('Register company number differs from commission')
    if ' '.join(' '.join(parser.heading).split()).casefold() != legal_name.casefold():
        raise ValueError('Register legal name differs from commission')
    return observed.isoformat(), url, acquisition['primary_content_sha256'], parser


def prepare(commission, acquisitions, families):
    """Return independently verified candidates and bounded coverage.

    A commission binds a legal subject to a research subject, not to a live
    workspace or a canonical alias. The caller supplies authorised acquisitions.
    """
    number = commission['registration_number']
    enterprise = commission['enterprise_id']
    legal_name = commission['legal_name']
    cutoff = date.fromisoformat(commission['as_of'])
    if not IDENTIFIER.fullmatch(number) or not legal_name.strip():
        raise ValueError('An exact legal scope is required')
    findings = {}
    conflicts = set()
    held = Counter()
    edges = {}
    disputed_edges = set()
    acquisitions = tuple(acquisitions)
    unavailable_versions = {
        (entry.get('metadata', {}).get('url'), entry.get('metadata', {}).get('expected_sha256'))
        for entry in acquisitions if unavailable(entry.get('metadata', {}))
    }
    for entry in acquisitions:
        try:
            meta = entry['metadata']
            if (meta.get('url'), meta.get('expected_sha256')) in unavailable_versions:
                raise ValueError('Source version held')

            child = entry.get('controlled_registration')
            if child is not None:
                if not IDENTIFIER.fullmatch(child) or child not in commission.get('controlled_registrations', []):
                    raise ValueError('Control subject outside commission')
                observed, edge = verify_control(entry, number, child, cutoff)
                key = (child, observed)
                previous = edges.get(key)
                if previous and previous['disclosed_notification'] != edge['disclosed_notification']:
                    disputed_edges.add(key)
                elif not previous or edge['source_content_sha256'] < previous['source_content_sha256']:
                    edges[key] = dict(edge, observed_on=observed)
                continue
            observed, url, version, parser = verify_register(entry, number, legal_name, cutoff)
        except (OSError, ValueError, KeyError, TypeError):
            held['unavailable, restricted or mismatched acquisition'] += 1
            continue
        for locator, (attribute, label, family) in FIELDS.items():
            value = parser.text(locator)
            if not value:
                held['missing register field'] += 1
                continue
            key = (attribute, observed)
            previous = findings.get(key)
            if previous and previous['value'] != value:
                conflicts.add(key)
            elif previous:
                held['repeated register assertion'] += 1
                if version < previous['version']:
                    findings[key] = dict(value=value, version=version, url=url, locator=locator,
                                         label=label, family=family,
                                         recorded_replay=entry['metadata'].get('recorded_replay') is True,
                                         captured_original_sha256=entry['metadata'].get('captured_original_sha256'))
            else:
                findings[key] = dict(value=value, version=version, url=url, locator=locator,
                                     label=label, family=family,
                                         recorded_replay=entry['metadata'].get('recorded_replay') is True,
                                         captured_original_sha256=entry['metadata'].get('captured_original_sha256'))

    for key in disputed_edges:
        edges.pop(key)
    for edge in edges.values():
        observed = edge['observed_on']
        attribute = 'identity.listed_psc_for_' + edge['subject_registration'].lower()
        findings[attribute, observed] = {
            'value': edge['subject_registration'],
            'version': edge['source_content_sha256'], 'url': edge['source_url'],
            'locator': edge['source_locator'], 'label': 'active corporate PSC listing for company number',
            'family': 'Subsidiaries, divisions and perimeter',
            'recorded_replay': edge['recorded_replay'],
            'captured_original_sha256': edge['captured_original_sha256'],
        }

    rows = []
    coverage = Counter()
    for (attribute, observed), fact in sorted(findings.items()):
        if (attribute, observed) in conflicts:
            continue
        statement = f"{legal_name} is recorded by Companies House with {fact['label']} of {fact['value']}."
        if not validate_atomic_statement(statement).atomic:
            held['non-atomic register assertion'] += 1
            continue
        coverage[fact['family']] += 1
        basis = (enterprise, number, attribute, observed, fact['value'])
        evid = 'EV-' + fingerprint((*basis, fact['version']))[:24]
        obs = 'OBS-' + fingerprint(basis)[:24]
        rows.extend([
            record(evid, 'evidence', {'enterprise_id': enterprise, 'source_url': fact['url'],
                'source_locator': fact['locator'], 'source_content_sha256': fact['version'],
                'value': fact['value'], 'affected_attribute': attribute,
                'recorded_replay': fact['recorded_replay'],
                'captured_original_sha256': fact['captured_original_sha256'],
                'collection_date': observed, 'subject': legal_name, 'registration_number': number,
                'statement': statement, 'status': 'current'}),
            record(obs, 'observation', {'enterprise_id': enterprise, 'observation_id': obs,
                'atomic_statement': statement, 'type': 'enterprise_identity_confirmed',
                'affected_entity_relationship': attribute, 'event_date': observed,
                'supporting_evidence_ids': [evid], 'freshness': 'current',
                'contradiction_state': 'none'}),
        ])
    return {'enterprise_id': enterprise, 'as_of': cutoff.isoformat(), 'records': rows,
            'held': dict(held), 'relationship_candidates': [edges[k] for k in sorted(edges)], 'conflicts': [dict(attribute=a, observed=d) for a, d in sorted(conflicts)] +
            [dict(attribute='corporate PSC notification for ' + child, observed=d)
             for child, d in sorted(disputed_edges)],
            'coverage': {family: 'Partial' if coverage[family] else 'Unknown' for family in families},
            'models': {'Business Model Canvas': 'Partial' if rows else 'Blocked',
                       'limitation': 'Statutory identity and classification only. No operating model, '
                                     'causal outcome, financial inference or supplier need follows.'}}


def blueprint_archive(result):
    """Encode inspected candidate records for the existing Blueprint lifecycle."""
    rows = result['records']
    if not rows:
        raise ValueError('No eligible candidate rows')
    path = 'records.ndjson'
    raw = ''.join(canonical_json(row) + '\n' for row in rows).encode()
    manifest = {'schema_version': '1.0', 'package_id': 'initial-' + fingerprint(result)[:20],
                'package_version': '1.0', 'enterprise_id': result['enterprise_id'], 'profile_version': '1.0',
                'files': [],
                'record_sets': [{'record_class': 'evidence_register', 'path': path,
                                 'count': len(rows), 'required': True}]}
    parse_manifest(manifest)
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w') as archive:
        archive.writestr(zipfile.ZipInfo('blueprint_manifest.json'), canonical_json(manifest))
        archive.writestr(zipfile.ZipInfo(path), raw)
    return output.getvalue()
