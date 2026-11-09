"""Read-only evidence spine, assessment lenses and commercial research priorities.

Reuse existing SourceSegment, CandidateClaim and EvidencePackageItem contracts.
The overlay references existing Twin IDs and preserves their source documents.
Repository citation integrity is not verification of the cited primary content.
"""
from copy import deepcopy
from datetime import date, datetime
import hashlib
import json
from pathlib import Path
import re

from ..enterprise_intelligence.semantic import SourceSegment, CandidateClaim
from ..enterprise_intelligence.models import EvidencePackageItem, stable_hash
from ..memory.models import stable_observation_fingerprint
from .source_import import official_url, provenance

REPO = Path(__file__).resolve().parents[4]
DATA = REPO / 'enterprise-knowledge/banking/research-model/Assessment-Overlay.json'
ROOT = '/flora/banking/research'
LENSES = ('pestle','porter','value-chain')


def _sha(value):
    return hashlib.sha256(value.encode()).hexdigest()


def _index(values):
    result = {v['id']: v for v in values}
    if len(result) != len(values):
        raise ValueError('Duplicate research identity')
    return result


def load_assessment():
    data = json.loads(DATA.read_text())
    validate(data)
    return data


def _asset(data, asset_id):
    path = (REPO / data['assets'][asset_id]).resolve()
    boundary=(REPO/data.get('knowledge_root','enterprise-knowledge/banking')).resolve()
    if not boundary.is_relative_to(REPO/'enterprise-knowledge') or not path.is_relative_to(boundary) or not path.is_file():
        raise ValueError('Unknown public research asset')
    text = path.read_text()
    if not re.search(r'^asset_id:\s*[\"\']?'+re.escape(asset_id)+r'[\"\']?\s*$',text,re.M):
        raise ValueError('Research source does not match existing manifest identity')
    return path,text


def claim_segment(data, claim):
    if claim.get('verification') == 'source_supported' and not claim.get('repository_quote'):
        if not primary_claim_supported(data, claim):
            raise ValueError('Primary research segment requires reviewed quotation support')
        ref = claim['source_ids'][0]
        source = _index(data['sources'])[ref]
        quote = claim['primary_quotes'][ref]
        line = primary_text(source).find(quote)
        line = primary_text(source)[:line].count('\n') + 1 if line >= 0 else 1
        return SourceSegment(f"{ref}::quote-{_sha(quote)[:16]}", claim['asset_id'],
                             claim['quote_locator'], quote, _sha(quote),
                             source['text_path'] + f'#L{line}',
                             'candidate_intelligence', 'reviewed_primary_excerpt')
    path,text = _asset(data, claim['asset_id'])
    quote = claim['repository_quote']
    offset = text.find(quote)
    if offset < 0:
        raise ValueError('Research quotation no longer matches its preserved asset')
    line = text[:offset].count('\n')+1
    headings = re.findall(r'^#{1,4}\s+(.+)$',text[:offset],re.M)
    return SourceSegment(
        f"{claim['asset_id']}::quote-{_sha(quote)[:16]}",claim['asset_id'],headings[-1] if headings else 'Document',
        quote,_sha(quote),str(path.relative_to(REPO))+f'#L{line}',
        'candidate_intelligence','repository_citation_only')


def primary_text(source):
    """Read a reviewed public-source snapshot; a status flag alone proves nothing."""
    official_url(source['url'])
    snapshot=(REPO/source.get('text_path','')).resolve()
    boundary=REPO/'enterprise-knowledge/banking/research-model/source-snapshots'
    if not snapshot.is_relative_to(boundary) or not snapshot.is_file():
        raise ValueError('Primary snapshot unavailable')
    content=snapshot.read_text()
    if source.get('text_sha256')!=_sha(content):
        raise ValueError('Primary snapshot/content digest mismatch')
    kind = source.get('content_kind', 'verified_download')
    if kind == 'reviewed_web_excerpt':
        provenance(source)
        if (source.get('primary_content_sha256') is not None
                or source.get('retrieval_method') != 'approved_web_research_tool'
                or not source.get('retrieval_reference') or not source.get('excerpts')):
            raise ValueError('Web extracts cannot claim a hash of unavailable original bytes')
        for entry in source['excerpts']:
            if not entry.get('locator') or not entry.get('quote') or entry['quote'] not in content:
                raise ValueError('Web excerpt must retain its reviewed location and quotation')
    elif kind == 'verified_download':
        if not re.fullmatch(r'[a-f0-9]{64}',str(source.get('primary_content_sha256') or '')):
            raise ValueError('Missing original-file checksum')
        raw=(REPO/source.get('raw_path','')).resolve()
        if not raw.is_relative_to(boundary) or not raw.is_file() or hashlib.sha256(raw.read_bytes()).hexdigest()!=source['primary_content_sha256']:
            raise ValueError('Original source bytes mismatch')
    else:
        raise ValueError('Unsupported primary snapshot extent')
    retrieved=datetime.fromisoformat(source.get('retrieved_at','').replace('Z','+00:00'))
    official_url(source.get('retrieval_url',''))
    if retrieved.tzinfo is None:
        raise ValueError('Dated official-URL retrieval provenance required')
    return content


def primary_claim_supported(data, claim):
    sources=_index(data['sources'])
    quotes=claim.get('primary_quotes',{})
    if claim.get('verification')!='source_supported' or not quotes:
        return False
    normalise=lambda text:re.sub(r'\s+',' ',text).strip()
    for ref in claim['source_ids']:
        source=sources[ref]
        if source.get('verification')!='primary_retrieved' or not quotes.get(ref):
            return False
        if normalise(quotes[ref]) not in normalise(primary_text(source)):
            raise ValueError('Primary quotation does not match retrieved content')
    return True


def validate(data):
    if data.get('schema_version') != 1 or data.get('authority') != 'candidate_intelligence':
        raise ValueError('Unsupported research overlay')
    sources = _index(data['sources']); claims = _index(data['claims'])
    if len(set(data['assets']) | set(sources) | set(claims)) != len(data['assets'])+len(sources)+len(claims):
        raise ValueError('Asset, source and claim identities collide')
    all_ids = set(data['assets']) | set(sources) | set(claims)
    for key in ('frameworks','capabilities','suppliers','programmes','candidates','watchlist','gaps'):
        indexed = _index(data[key])
        if set(indexed) & all_ids:
            raise ValueError('Research identities collide')
        all_ids.update(indexed)
    for source in sources.values():
        if not source['url'].startswith('https://') or source.get('verification') not in {'citation_only','primary_retrieved'}:
            raise ValueError('Unsupported source provenance')
        if source.get('publication_date') is not None:
            published=date.fromisoformat(source['publication_date'])
            if published>date.fromisoformat(data['assessed_at']):
                raise ValueError('Future publication cannot support an as-of research assessment')
        if source['verification']=='primary_retrieved':
            primary_text(source)
        elif source.get('retrieved_at') or source.get('primary_content_sha256'):
            raise ValueError('Unretrieved citations cannot claim primary retrieval')
    for claim in claims.values():
        if (claim['asset_id'] not in data['assets'] or not claim['source_ids']
                or set(claim['source_ids'])-set(sources)
                or not (claim.get('repository_quote') or claim.get('primary_quotes'))):
            raise ValueError('Claim source lineage is incomplete')
        segment = claim_segment(data,claim)
        # Resolve cited URLs from the existing source asset, not arbitrary caller strings.
        _,text = _asset(data,claim['asset_id'])
        for ref in claim['source_ids']:
            if claim.get('repository_quote') and sources[ref]['verification']=='citation_only' and sources[ref]['url'] not in text:
                raise ValueError('Cited primary URL is not present in the preserved research asset')
        if segment.content_hash != _sha(segment.content):
            raise ValueError('Research segment checksum mismatch')
        if claim.get('verification') not in {'repository_reported','source_supported'}:
            raise ValueError('Unsupported research claim verification')
        if claim.get('verification')=='source_supported' and not primary_claim_supported(data,claim):
            raise ValueError('Source-supported claim needs matching primary-content quotation')
    for category in ('frameworks','programmes','candidates','watchlist'):
        for item in data[category]:
            for field, permitted in [('claim_ids',set(claims)),('gap_ids',{v['id'] for v in data['gaps']}),
                                     ('capability_ids',{v['id'] for v in data['capabilities']}),
                                     ('driver_ids',{v['id'] for v in data['frameworks']}),
                                     ('programme_ids',{v['id'] for v in data['programmes']})]:
                if set(item.get(field,()))-permitted:
                    raise ValueError('Unresolved research relationship')
    for relation in data['relationships']:
        if relation['subject'] not in all_ids or relation['object'] not in all_ids or set(relation['claim_ids'])-set(claims):
            raise ValueError('Unresolved graph edge')
        if relation.get('verified'):
            if (relation['assertion_kind']!='source_supported_relationship' or not relation['claim_ids']
                    or not all(primary_claim_supported(data,claims[c]) for c in relation['claim_ids'])
                    or not any(claims[c].get('relationship')=={'subject':relation['subject'],'predicate':relation['predicate'],'object':relation['object']} for c in relation['claim_ids'])):
                raise ValueError('Verified edge needs explicit primary-supported subject/predicate/object; industry context is insufficient')
        if relation['predicate'] in {'reported_uses','reported_licences'} and not relation['claim_ids']:
            raise ValueError('Reported supplier relationship requires enterprise-specific support')
    ids = [r['id'] for r in data['relationships']]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate graph edge')
    for candidate in data['candidates']:
        if candidate['enterprise_id'] != data['enterprise_twin_id'] or not candidate['claim_ids']:
            raise ValueError('Candidate needs enterprise-specific lineage')
        if candidate.get('estimated_value') is not None or candidate.get('procurement_date') is not None:
            raise ValueError('Public research does not establish a deal value or procurement date')
    return True


def freshness(data, as_of=None):
    as_of=as_of or date.today()
    effective=date.fromisoformat(data['upstream_research_effective_date'])
    age=(as_of-effective).days
    verified=sum(s['verification']=='primary_retrieved' for s in data['sources'])
    eligible=age>=0 and date.fromisoformat(data['assessed_at'])<=as_of
    return {'as_of':as_of.isoformat(),'upstream_age_days':age,
            'eligible':eligible,
            'status':('Future-dated research assessment — excluded' if not eligible else 'Partial primary retrieval; inspect claim-level dates' if verified else 'Primary verification pending; upstream assessment stale' if age>90 else 'Primary verification pending'),
            'primary_verified':verified,'primary_total':len(data['sources']),
            'reviewed_excerpts':sum(s.get('content_kind')=='reviewed_web_excerpt' for s in data['sources']),
            'limitation':'Twin effective date is not a primary publication date. No current/fresh source claim is inferred from a URL, collection date or local file hash.'}


def candidate_claim(data, item):
    segment=claim_segment(data,item)
    fingerprint=stable_observation_fingerprint(data['enterprise_twin_id'],item['kind'],item['statement'],item['domain'],item['reporting_period'])
    supported=primary_claim_supported(data,item)
    return CandidateClaim('RC-'+fingerprint.rsplit('-',1)[-1][:16].upper(),item['kind'],item['statement'],
        item['asset_id'],segment.segment_id,'enterprise' if item['asset_id']=='BK-ENT-001' else 'industry',
        data['enterprise_twin_id'] if item['asset_id']=='BK-ENT-001' else data['industry_twin_id'],
        item['domain'],item.get('metric_value') or item['statement'],item['reporting_period'],
        'UK Banking',data['enterprise_twin_id'] if item['asset_id']=='BK-ENT-001' else '',
        'Source-supported; commercial verification outstanding' if supported else 'Provisional; primary content unverified','candidate_intelligence','source_supported_candidate' if supported else 'needs_primary_verification',item['source_ids'],[])


def evidence_item(data, item):
    segment=claim_segment(data,item)
    return EvidencePackageItem(item['id'],'research_claim_candidate',item['statement'],
        'source_supported_public_claim' if primary_claim_supported(data,item) else 'repository_reported_not_primary_verified','Source-supported public claim' if primary_claim_supported(data,item) else 'Provisional',freshness(data)['status'],
        tuple([segment.segment_id,*item['source_ids']]),(),segment.source_location,
        data['enterprise_twin_id'] if item['asset_id']=='BK-ENT-001' else '')


def ranked_candidates(data=None, as_of=None):
    data=data or load_assessment()
    claims=_index(data['claims'])
    state=freshness(data,as_of)
    if not state['eligible']:
        return []
    result=[]
    for entry in data['candidates']:
        row=deepcopy(entry)
        # Rank research effort, never deal probability. Relevance tiers are an
        # explicit analyst assessment. Citation counts do not calibrate truth.
        enterprise_claims=sum(claims[c]['asset_id']==data['enterprise_twin_id'] and claims[c]['kind'] not in {'unknown','interpretation'} for c in row['claim_ids'])
        supported=sum(primary_claim_supported(data,claims[c]) for c in row['claim_ids'])
        row['rank_basis']={'research_tier':row['research_tier'],'enterprise_claims':enterprise_claims,
                           'programme_signals':len(row['programme_ids']),'primary_supported_claims':supported}
        row['confidence']=('Source-supported public signal; customer demand unverified' if supported else 'Provisional — primary-source verification outstanding')
        row['readiness']='Research candidate; customer qualification outstanding'
        row['freshness']=state['status']
        row['reasoning_authority']='derived_runtime_assessment'
        result.append(row)
    result.sort(key=lambda r:(r['research_tier'],-r['rank_basis']['primary_supported_claims'],-r['rank_basis']['enterprise_claims'],r['id']))
    for rank,row in enumerate(result,1):row['rank']=rank
    return result


def candidate(identifier, data=None):
    data=data or load_assessment()
    return next((r for r in ranked_candidates(data) if r['id']==identifier),None)


def commercial_capture(slug, identifier):
    data=load_assessment();row=candidate(identifier,data)
    if row is None or row['enterprise_slug']!=slug:
        raise ValueError('Research candidate does not belong to this enterprise')
    claims=_index(data['claims']);sources=_index(data['sources'])
    refs=list(dict.fromkeys(s for c in row['claim_ids'] for s in claims[c]['source_ids']))
    return {
        'fields':{'title':row['title'],'problem':row['problem'],'solution':row['intervention'],
                  'next_action':row.get('review',{}).get('next_action') or 'Research validation first: '+ '; '.join(next(g['question'] for g in data['gaps'] if g['id']==gid) for gid in row['gap_ids'][:3])},
        'provenance':{'kind':'research_candidate','source_labels':[sources[s]['title']+(' (reviewed primary excerpt; customer demand unverified)' if sources[s]['verification']=='primary_retrieved' else ' (citation only; primary verification pending)') for s in refs],
                      'snapshot':data['assessed_at'],'signals':[claims[c]['statement'] for c in row['claim_ids']],
                      'evidence_url':ROOT+'/candidates/'+row['id']+'#evidence','origin_url':ROOT+'/candidates/'+row['id'],
                      'limitations':row['confidence']+'. Not customer-verified demand; no accepted canonical Evidence.',
                      'research_assessment_id':data['assessment_id'],'claim_ids':row['claim_ids'],
                      'source_ids':refs,'assessment_digest':stable_hash(data)},
    }


def compare_revision(previous, proposed):
    """Read-only update proposal; never overwrite an established fact/store."""
    old=_index(previous['claims']);new=_index(proposed['claims'])
    semantics=('asset_id','statement','repository_quote','reporting_period','domain','kind','metric_value','metric_unit','entity_scope')
    reused=[key for key in old.keys()&new.keys() if any(old[key].get(k)!=new[key].get(k) for k in semantics)]
    if reused:
        raise ValueError('Changed facts need new stable IDs and explicit supersession, not overwrite')
    for key in old.keys()&new.keys():
        if set(old[key]['source_ids'])-set(new[key]['source_ids']):
            raise ValueError('Existing provenance must be retained in the update proposal')
    for entry in new.values():
        prior=entry.get('supersedes')
        if prior and (prior not in old or any(entry.get(k)!=old[prior].get(k) for k in ('asset_id','domain','reporting_period'))):
            raise ValueError('Supersession must be an explicit same-scope/period correction, not removal of earlier period facts')
    return {'added':sorted(new.keys()-old.keys()),'not_in_proposed':sorted(old.keys()-new.keys()),
            'corroborated':[key for key in sorted(old.keys()&new.keys()) if old[key]!=new[key]],
            'retained_history':deepcopy(previous),'proposed':deepcopy(proposed),
            'automatic_acceptance':False,'canonical_mutation':False}
