"""Finite, repository-owned presentation identities; never workspace authority.

New sectors register data, not a second research or permission engine.
"""
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

REPO = Path(__file__).resolve().parents[4]
DOMAINS = MappingProxyType({'banking': ('UK Banking', 'lloyds', '/flora/banking/research'),
                          'aviation': ('Commercial Aviation', 'easyjet', '/flora/aviation/research')})


def assessment_path(domain):
    if domain not in DOMAINS:
        raise ValueError('Unknown research industry')
    return REPO / 'enterprise-knowledge' / domain / 'research-model/Assessment-Overlay.json'


def snapshot_boundary(domain, repo=None):
    if domain=='macro':
        return (repo or REPO)/'enterprise-knowledge/macro/research-model/source-snapshots'
    relative=assessment_path(domain).relative_to(REPO)
    return ((repo or REPO)/relative).parent / 'source-snapshots'


def enterprise_domain(slug):
    for domain, (_, enterprise, _) in DOMAINS.items():
        if slug == enterprise:
            return domain
    raise ValueError('Unknown research enterprise')


@dataclass(frozen=True)
class EnterpriseReference:
    """Public navigation identity, not an accepted Enterprise Model or ACL."""
    id: str
    slug: str
    name: str
    industry: str
    origin_url: str


def enterprise_reference(slug):
    from ..banking_portfolio import BANKS
    if slug in BANKS:
        return BANKS[slug]
    if slug == 'easyjet':
        return EnterpriseReference('AV-ENT-001', 'easyjet', 'easyJet', 'Aviation',
                                   '/flora/aviation/research/easyjet')
    return None


def landscape_url(slug):
    if slug == 'easyjet':
        return '/flora/aviation/research/opportunities'
    from ..banking_portfolio import BANKS
    if slug not in BANKS:
        raise ValueError('Unknown enterprise')
    return '/flora/banking/explorer/' + slug + '/opportunities'
