"""Read-only Technology presentation and candidate handoff over recovered Page research.

No collector, job store, promotion, model client or Pipeline writer. Existing
SourceSegment/CandidateClaim/EvidencePackageItem remain the candidate contracts.
"""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from .source_import import official_url
from .registry import enterprise_reference
from ..enterprise_intelligence.semantic import SourceSegment, CandidateClaim
from ..enterprise_intelligence.models import EvidencePackageItem

ROOT = Path(__file__).resolve().parents[4]
ASSETS = ROOT / 'docs/flora-runtime/technology-visual-foundation'
FOUNDATION_SHA256 = '1f332a13026e83d677d3897fcec9bd29c259546b070b9cea23b6b8dcd83c05b5'
PAGE_URL = 'https://chatgpt.com/space/page_61a0dab9a9708191a323c9b0e048e523'
BASE = '/industries/technology'
SEGMENTS = ('applications','cloud','ai','cyber','services','channels','infrastructure','frontier')


def _read(name, checksum):
    path = ASSETS / name
    if path.is_symlink() or not path.resolve().is_relative_to(ROOT) or not path.is_file():
        raise ValueError('Research asset unavailable')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != checksum:
        raise ValueError('Reviewed research asset changed; reconcile before publication')
    return json.loads(raw)


def load():
    data = _read('Foundation.json', FOUNDATION_SHA256)
    page = _read('Research-Page.json', data['research_page_sha256'])
    if (data['authority'] != 'candidate_intelligence' or len(data['providers']) != 80
            or len({r['key'] for r in data['providers']}) != 80
            or data['canonical_accepted_count'] != 0 or data['eligible_import_count'] != 0):
        raise ValueError('Research boundary mismatch')
    return data, {r['id']: r for r in page['blocks']}


def existing_navigation(row):
    """Reuse explicit reviewed public navigation; never create a canonical entity.

    The registry owns the returned reference. A group-level HSBC statement is not
    joined to HSBC UK by substring. Navigation is not an accepted Evidence binding.
    """
    slug = row.get('existing_enterprise_slug')
    return enterprise_reference(slug) if slug else None


def candidate_mapping(row, block):
    """Adapt the actual Page row, not fabricated original publisher bytes.

    The typed objects are an inspection projection. Withheld objects never enter
    the importer, canonical stores, review ledger or Evidence acceptance state.
    """
    content = row['source_text']
    if content != block['markdown']:
        matches = [line for line in block['markdown'].splitlines()
            if line.startswith('|') and ' | '.join(s.strip() for s in line.strip('|').split('|')) == content]
        if len(matches) != 1:
            raise ValueError('Candidate does not match one retained Page row')
        content = matches[0]  # Hash actual retained Page bytes, not a publisher document.
    digest = hashlib.sha256(content.encode()).hexdigest()
    identifier = 'page-research:' + row['key']  # Local candidate identity only.
    location = PAGE_URL + '#block-' + block['id']
    segment = SourceSegment(identifier+':segment', 'recovered-technology-page',
        'Customer / provider research row', content, digest, location,
        'candidate_intelligence', 'page_research_not_original_source')
    statement = row['customer'] + ' — ' + row['participants'] + ' — ' + row['offering']
    claim = CandidateClaim(identifier, 'relationship research draft', statement,
        segment.asset_id, segment.segment_id, row['geography'], row['customer'],
        'Page reports; see typed programme roles', row['participants'],
        row['temporal_status'], 'exact cited programme only', '',
        'Unvalidated Page research', 'candidate_intelligence', 'withheld', [], [])
    item = EvidencePackageItem(identifier, 'research_claim_candidate', statement,
        'page_research_not_accepted_evidence', 'Unvalidated', row['temporal_status'],
        (segment.segment_id,), (), location, '')
    reasons = ['source_operation_rights_unestablished', 'canonical_identity_unbound',
               'exact_source_retrieval_timestamp_missing', 'publisher_source_not_reacquired',
               'registered_technology_domain_mapping_unaccepted']
    for source in row['source_links']:
        try:
            official_url(source['url'])
        except ValueError:
            reasons.append('publisher_not_in_existing_allowlist')
    if not row['source_links']:
        reasons.append('exact_source_url_missing')
    return {'research_key': row['key'], 'status': 'withheld',
        'source_segment': asdict(segment), 'candidate_claim': asdict(claim),
        'evidence_package_item': item.to_dict(), 'reasons': sorted(set(reasons)),
        'publisher_source_links': row['source_links'],
        'publisher_original_sha256': None, 'retrieval_date': row['retrieval_date'],
        'retrieved_at': None, 'canonical_evidence_id': None,
        'canonical_enterprise_id': None, 'eligible_for_import': False}


def handoff():
    data, blocks = load()
    return {'version':1,'authority':'candidate_intelligence','as_of':data['as_of'],
        'source_page':PAGE_URL,'page_sequence':data['page_sequence'],
        'source_page_sha256':data['research_page_sha256'],
        'scope':'Deterministic Page candidate mapping; not an accepted import package',
        'existing_owners':{
            'source':'cios.applications.flora.research_intelligence.source_import',
            'candidate':'cios.applications.flora.enterprise_intelligence.semantic',
            'review_promotion':'cios.applications.flora.blueprint_import.views',
            'observations':'cios.applications.flora.memory.models',
            'enterprise_navigation':'cios.applications.flora.research_intelligence.registry'},
        'accepted':0,'eligible':0,'canonical_mutation':False,'pipeline_mutation':False,
        'relationships':[candidate_mapping(r,blocks[r['source_block']]) for r in data['relationships']],
        'atomic_passage_references':data['atomic_references'],
        'provider_identity_register':[{'key':r['key'],'label':r['label'],
            'identity_status':r['identity_status'],'canonical_enterprise_id':None,
            'note':r['identity_note'],'coverage':r['profile_status'],'gaps':r['gaps']}
            for r in data['providers']]}
