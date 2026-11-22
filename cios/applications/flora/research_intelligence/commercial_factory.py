"""Compile scoped, reviewed public disclosures into the existing Blueprint path.

Recorded disclosures are a fixture lane. A checksum protects reviewed claim
bindings, not publisher authenticity or rights for production reuse.
"""
from collections import Counter
from datetime import date
import re
from urllib.parse import urlsplit

from .initial_factory import fingerprint, record
from ..blueprint_import.atomicity import validate_atomic_statement
from ..memory.service import CLAIM_VOCABULARY

CATEGORIES = {'corporate_announcement', 'financial_publication', 'regulatory',
              'supplier_announcement', 'procurement_notice'}
PERSPECTIVES = ('landscape', 'inside', 'forces')


def usable_url(value):
    url = urlsplit(value)
    return (url.scheme == 'https' and url.hostname and not url.username
            and not url.password and url.port in (None, 443) and not url.fragment)


def active(source):
    return not (source.get('hold') or source.get('withdrawn')
                or source.get('status') in {'withdrawn', 'superseded', 'restricted'})


def prepare_commercial(result, commission, sources):
    """Extend a commissioned wave without giving replay data production authority."""
    enterprise = commission['enterprise_id']
    if result['enterprise_id'] != enterprise:
        raise ValueError('Commercial subject differs from register commission')
    cutoff = date.fromisoformat(commission['as_of'])
    held = Counter(result['held'])
    candidates = {}
    conflicts = set()
    unavailable = {(s.get('url'), s.get('sha256')) for s in sources if not active(s)}
    for source in sources:
        binding = {k: v for k, v in source.items() if k not in {'sha256', 'withdrawn', 'status'}}
        try:
            if ((source['url'], source['sha256']) in unavailable
                    or not usable_url(source['url']) or source['category'] not in CATEGORIES
                    or source['enterprise_id'] != enterprise or not source['publisher']
                    or not source['scope'] or fingerprint(binding) != source['sha256']
                    or date.fromisoformat(source['published']) > cutoff):
                raise ValueError('Unusable disclosure')
        except (ValueError, KeyError, TypeError):
            held['commercial disclosure held or provenance invalid'] += max(1, len(source.get('claims', ())))
            continue

        for claim in source['claims']:
            try:
                key = claim['key']
                period = claim['period']
                if (claim['scope'] != source['scope'] or claim['family'] not in result['coverage']
                        or claim['perspective'] not in PERSPECTIVES or not claim['locator']
                        or not claim['caveat'] or not re.fullmatch(r'[a-z][a-z0-9_]*', key)
                        or not validate_atomic_statement(claim['statement']).atomic
                        or date.fromisoformat(period) > date.fromisoformat(source['published'])):
                    raise ValueError('Invalid claim binding')
                prefix = CLAIM_VOCABULARY[claim['type']]['attribute_prefix']
                metric = claim.get('metric')
                if metric is not None and (claim['type'] != 'financial_metric_reported'
                        or metric['group'] != 'revenue_mix'
                        or metric['axis'] not in {'licensing', 'royalties'}
                        or metric['unit'] != 'USD million' or type(metric['amount']) is not int
                        or metric['amount'] <= 0
                        or f"USD {metric['amount']} million" not in claim['statement']):
                    raise ValueError('Invalid typed metric')

            except (ValueError, KeyError, TypeError):
                held['commercial claim outside verified scope'] += 1
                continue
            identity = (prefix + key, claim['scope'], period)
            previous = candidates.get(identity)
            if previous and claim['statement'] != previous[0]['statement']:
                conflicts.add(identity)
            elif previous:
                held['repeated commercial assertion'] += 1
                if source['sha256'] < previous[1]['sha256']:
                    candidates[identity] = claim, source
            else:
                candidates[identity] = claim, source

    rows = list(result['records'])
    coverage = dict(result['coverage'])
    accepted = set()
    for (attribute, scope, period), (claim, source) in sorted(candidates.items()):
        if (attribute, scope, period) in conflicts:
            continue
        statement = claim['statement']
        basis = enterprise, attribute, scope, period, statement
        evidence = 'EV-' + fingerprint((*basis, source['sha256']))[:24]
        observation = 'OBS-' + fingerprint(basis)[:24]
        rows.extend([
            record(evidence, 'evidence', {
                'enterprise_id': enterprise, 'source_url': source['url'],
                'source_locator': claim['locator'], 'source_content_sha256': source['sha256'],
                'publisher': source['publisher'], 'source_category': source['category'],
                'reporting_scope': scope, 'publication_date': source['published'],
                'period': period, 'statement': statement, 'affected_attribute': attribute,
                'perspective': claim['perspective'], 'caveat': claim['caveat'],
                'family': claim['family'], 'metric': claim.get('metric'), 'status': 'current', 'recorded_replay': not bool(source.get('live_content_sha256')),
                'live_content_sha256': source.get('live_content_sha256'),
                'use_scope': 'isolated_commercial_replay',
            }),
            record(observation, 'observation', {
                'enterprise_id': enterprise, 'observation_id': observation,
                'atomic_statement': statement, 'type': claim['type'],
                'affected_entity_relationship': attribute, 'event_date': period,
                'evidence_date': source['published'], 'scope': scope,
                'supporting_evidence_ids': [evidence], 'freshness': 'current',
                'contradiction_state': 'none',
            }),
        ])
        coverage[claim['family']] = 'Partial'
        accepted.add(claim['family'])
    models = dict(result['models'])
    for model, family in (
        ('Operating and Capability Model', 'Operating model'),
        ('Technology and Supplier Ecosystem Model', 'Suppliers and outsourcing'),
        ('Enterprise Economics Model', 'Revenue pools, margins and cost drivers'),
        ('Enterprise Transformation Timeline', 'Programmes and milestones'),
        ('PESTLE', 'Technology and regulation'),
    ):
        if family in accepted:
            models[model] = 'Partial'
    models['limitation'] = ('Partial models expose attributable inputs and bounded comparisons. '
                            'Commercial intent, causal outcomes and delivery remain unverified.')
    return dict(result, records=rows, coverage=coverage, models=models, held=dict(held),
                conflicts=[*result['conflicts'], *[dict(attribute=a, scope=s, observed=d)
                                                  for a, s, d in sorted(conflicts)]])
