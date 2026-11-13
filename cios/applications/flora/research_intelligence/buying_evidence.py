"""Bounded public candidate research over existing Evidence/Observation contracts.

No collector, accepted-evidence store, ranking engine or canonical mutation.
Matching decisions remain in offers.assess_fit; operational saves in offers.py.
"""
from copy import deepcopy
from dataclasses import asdict
from datetime import date, datetime
from hashlib import sha256
import json
from pathlib import Path
from urllib.parse import urlsplit

from ..enterprise_intelligence.semantic import SourceSegment, CandidateClaim
from ..enterprise_intelligence.models import EvidencePackageItem, EvidencePackageV1
from ..blueprint_import.observation_runtime import CandidateObservation
from ..memory.models import stable_observation_fingerprint, stable_observation_id
from ..live.source_registry import SourceRecord
from .source_import import provenance

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT/'enterprise-knowledge/technology/research-model/Buying-Trigger-Pilot.json'
DATA_SHA256 = '2aa6062fba5ec016e77dbcca81989a318793c3b1746df08031da32e36a7e8927'
POLICY = 'offers-trigger-intelligence-v1'
PUBLISHERS = frozenset({'www.lloydsbankinggroup.com','www.easyjet.com','investors.computacenter.com',
    'www.tsb.co.uk','investors.natwestgroup.com','newsroom.bt.com','www.sec.gov','nvidianews.nvidia.com','home.barclays'})
DIMENSIONS = {'business_service','enterprise_ai','security','estate','social_value'}
OFFER_DIMENSIONS = dict(zip((
    'tech-strategic-digital-transformation','tech-strategic-ai-first-transformation',
    'tech-strategic-cybersecurity-resilience','tech-strategic-complex-legacy-modernisation',
    'tech-strategic-social-value-esg'),
    ('business_service','enterprise_ai','security','estate','social_value')))


def fingerprint(value):
    return sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def load():
    if DATA.is_symlink() or not DATA.resolve().is_relative_to(ROOT/'enterprise-knowledge/technology/research-model'):
        raise ValueError('Buying research boundary unavailable')
    raw=DATA.read_bytes()
    if sha256(raw).hexdigest()!=DATA_SHA256:
        raise ValueError('Buying research changed; reconcile reviewed evidence before matching')
    data=json.loads(raw)
    if data['authority']!='candidate_intelligence' or data['canonical_mutation'] is not False or data['schema_version']!=1:
        raise ValueError('Buying research authority mismatch')
    for key in ('cohort','sources','facts'):
        id_key='slug' if key=='cohort' else 'id'
        if len({r[id_key] for r in data[key]})!=len(data[key]):raise ValueError('Duplicate buying research reference')
    slugs={r['slug'] for r in data['cohort']};source_ids={r['id'] for r in data['sources']};fact_ids={r['id'] for r in data['facts']}
    approved_urls={s['url'] for s in data['sources']}
    def approved(url):
        parsed=urlsplit(url)
        if url not in approved_urls or parsed.hostname not in PUBLISHERS or parsed.scheme!='https' or parsed.username or parsed.password or parsed.port not in (None,443) or parsed.fragment:
            raise ValueError('Unregistered candidate source URL')
    for source in data['sources']:
        provenance(source,approved)
        if (source['source_type'] not in {'annual_report','investor_results','official_newsroom'} or source['accepted'] is not False or source['collector_enabled'] is not False
                or source['usage_scope']!='public_short_quote_and_link' or not source['rights']
                or source['primary_content_sha256'] is not None or not source['locator']
                or sha256(source['excerpt'].encode()).hexdigest()!=source['excerpt_sha256']
                or len(source['excerpt'].replace(' / ',' ').split())>25):
            raise ValueError('Source rights, extent or review mismatch')
    if data['policy']['id']!=POLICY or type(data['policy']['catalyst_review_days']) is not int or not 1<=data['policy']['catalyst_review_days']<=365:
        raise ValueError('Reviewed pilot timing policy required')
    for fact in data['facts']:
        if fact['enterprise_slug'] not in slugs or not set(fact['dimensions'])<=DIMENSIONS or fact['status'] not in {'retained','withdrawn'}:
            raise ValueError('Unsupported candidate fact')
        if fact['kind'] not in {'structural','catalyst','programme','completed','counter','context','closed'}:
            raise ValueError('Unsupported trigger fact kind')
        if 'source_id' in fact and fact['source_id'] not in source_ids:raise ValueError('Unknown source reference')
        if fact['kind']=='closed' and not fact['programme_id']:raise ValueError('Closure must identify the affected programme')
        for other in fact['supersedes']:
            if other not in fact_ids or next(f for f in data['facts'] if f['id']==other)['enterprise_slug']!=fact['enterprise_slug']:
                raise ValueError('Supersession cannot cross enterprise scope')
    return data


def _identity(row):
    from .registry import enterprise_reference
    from . import technology
    from ..live.source_registry import configured_enterprise_aliases
    owner=row['identity_owner'];slug=row['slug'];permission=row['permission_id']
    if owner in {'existing_banking_reference','existing_aviation_reference'}:
        known=enterprise_reference(slug)
        if not known or known.id!=permission:raise ValueError('Existing enterprise reference mismatch')
    elif owner=='existing_collection_profile':
        if permission not in configured_enterprise_aliases().values():raise ValueError('Unknown existing collection identity')
    elif owner=='existing_technology_foundation':
        foundation,_=technology.load()
        if not any(p['key']==slug and p['identity_status']=='unbound' for p in foundation['providers']) or permission!='presentation:'+slug:
            raise ValueError('Unknown public presentation identity')
    else:raise ValueError('No existing enterprise identity owner')


def _projection(fact, account, sources):
    """Adapt retained source/claim IDs into existing candidate contract classes."""
    from . import model, technology_commercial
    if fact.get('existing_claim'):
        ref=fact['existing_claim'];data=model.load_assessment(ref['domain'])
        claim=next(c for c in data['claims'] if c['id']==ref['id'])
        segment=model.claim_segment(data,claim);candidate=model.candidate_claim(data,claim);item=model.evidence_item(data,claim)
        source=deepcopy(next(s for s in data['sources'] if s['id']==claim['source_ids'][0]))
        source.update(last_verified=source.get('retrieved_at'),locator=claim['quote_locator'],scope=account['scope'],usage_scope='existing_candidate_reference_only')
        statement=claim['statement'];source_id=source['id']
    elif fact.get('existing_technology_source'):
        source=deepcopy(technology_commercial.load()['sources'][fact['existing_technology_source']])
        projection=technology_commercial.source_projection(source['id'])
        segment=SourceSegment(**projection['source_segment']);candidate=CandidateClaim(**projection['candidate_claim']);item=EvidencePackageItem(**projection['evidence_package_item'])
        source.update(last_verified=source['reviewed_at'],scope=account['scope'],usage_scope='existing_candidate_reference_only')
        statement=fact['statement'];source_id=source['id']
    else:
        source=deepcopy(sources[fact['source_id']]);source_id=source['id'];statement=fact['statement']
        # The existing registry type is an inspection projection, disabled for collection.
        SourceRecord(source_id=source_id,organisation=account['name'],source_name=source['title'],
            source_type=source['source_type'],url=source['url'],sector=account['industry'],evidence_tier='tier_1_company',
            expected_signal_types=fact['dimensions'],enabled=False,collection_purpose='Offline candidate review only')
        segment=SourceSegment(source_id+':'+source['excerpt_sha256'][:16],source_id,source['locator'],source['excerpt'],source['excerpt_sha256'],source['url'],'candidate_intelligence','reviewed_web_excerpt_not_accepted')
        candidate=CandidateClaim(fact['id'],'reported_'+fact['kind'],statement,source_id,segment.segment_id,source['scope'],account['permission_id'],fact['kind'],statement,source['reporting_period'],source['scope'],account['permission_id'],'Source-supported candidate; commercial validation outstanding','candidate_intelligence','source_supported_candidate',[source_id],[])
        item=EvidencePackageItem(fact['id'],'research_claim_candidate',statement,'source_supported_public_claim',
            'Public candidate; not accepted Evidence',source['reporting_period'],(segment.segment_id,source_id),(),source['url'],account['permission_id'])
    published=source.get('publication_date');verified=source.get('last_verified')
    fp=stable_observation_fingerprint(account['permission_id'],fact['kind'],statement,','.join(fact['dimensions']),fact.get('effective_date') or published or source.get('reporting_period'))
    obs=CandidateObservation(stable_observation_id(fp),'existing_candidate_source_projection','buying-trigger-pilot-v1',fact['id'],('statement','source_refs','effective_date'),statement,(item.stable_id,segment.segment_id),'Source-supported candidate; no buyer-intent confidence',account['permission_id'],fact['kind'],verified or '')
    return {**deepcopy(fact),'statement':statement,'publication_date':published,'last_verified':verified,
        'source_id':source_id,'source_url':source['url'],'source_title':source['title'],'source_scope':source.get('scope',account['scope']),
        'source_rights':source.get('rights','Original public-candidate rights limits retained; canonical import not authorised'),
        'quote':segment.content,'locator':source.get('locator',segment.section_heading),
        'source_segment':asdict(segment),'candidate_claim':asdict(candidate),'candidate_observation':asdict(obs),'evidence_package_item':item.to_dict(),
        'accepted':False,'canonical_evidence_id':None,'reference_digest':fingerprint([source,fact,asdict(segment)])}


def accounts(base):
    data=load();sources={s['id']:s for s in data['sources']};result={}
    for row in data['cohort']:
        _identity(row);slug=row['slug']
        current=deepcopy(base.get(slug,{'id':row['permission_id'],'slug':slug,'name':row['name'],
            'industry':{'banking':'Banking','aviation':'Aviation','technology':'Technology'}[row['industry']],
            'knowledge_date':data['as_of'],'authority':'candidate_intelligence', 'lineage':[],'observation_lineage':[],
            'limitations':['Bounded public-source candidate research; no canonical acceptance or seller access.'],
            'counter_indicators':[], 'url':'/enterprises/'+slug if row['industry']=='banking' else '/industries/technology/experience/enterprise?enterprise='+slug}))
        facts=[_projection(f,row,sources) for f in data['facts'] if f['enterprise_slug']==slug]
        from ..buying_entry_plays import REVISION as entry_play_revision
        current['trigger_research']={'entry_play_revision':entry_play_revision,'version':data['version'],'registry_digest':DATA_SHA256,'identity':deepcopy(row),'facts':facts,'policy':deepcopy(data['policy'])}
        package=EvidencePackageV1('BTI-'+fingerprint([slug,DATA_SHA256])[:20],row['permission_id'],{'scope':row['scope'],'identity_state':row['canonical_identity_gap']},'candidate_only',data['as_of'],'bounded public first-party candidate passages',
            selected_observations=tuple(EvidencePackageItem(**f['evidence_package_item']) for f in facts),lineage_manifest=tuple(f['source_id'] for f in facts),freshness='Claim dates retained; current residual need unverified',retrieval_notes=('No runtime collection, accepted Evidence promotion or canonical writes.',))
        current['trigger_research']['evidence_package']=package.to_dict()
        result[slug]=current
    return result


def available_facts(research, cutoff):
    """Temporal/source admissibility only. This does not decide commercial fit."""
    asof=date.fromisoformat(cutoff);known=[]
    for f in research['facts']:
        verified=f.get('last_verified');pub=f.get('publication_date')
        if (not verified or date.fromisoformat(verified[:10])>asof or (pub and date.fromisoformat(pub)>asof)):
            continue
        known.append(deepcopy(f))
    superseded={old for f in known if f['status']=='retained' for old in f['supersedes']}
    out=[]
    for f in known:
        if f['status']!='retained' or f['id'] in superseded:continue
        f['source_age_days']=(asof-date.fromisoformat(f['publication_date'])).days if f['publication_date'] else None
        f['review_age_days']=(asof-date.fromisoformat(f['last_verified'][:10])).days
        f['dated_current']=f['source_age_days'] is not None and f['source_age_days']<=research['policy']['catalyst_review_days'] and f['review_age_days']<=research['policy']['catalyst_review_days']
        f['freshness']='Current dated source; buyer timing unknown' if f['dated_current'] else 'Undated or historical context; do not infer current urgency'
        out.append(f)
    return out
