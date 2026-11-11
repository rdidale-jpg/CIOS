"""Versioned, read-only market context over FLORA's existing evidence spine.

A view selection is never membership, legal applicability or Pipeline authority.
No network client, private-store lookup, canonical promotion or persistence.
"""
from copy import deepcopy
from datetime import date
import hashlib
import json
from typing import Literal
from urllib.parse import parse_qsl
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .model import REPO, load_assessment, primary_text
from .cycle import digest
from .commercial_intelligence import commercial_projection
from ..enterprise_intelligence.semantic import SourceSegment, CandidateClaim
from ..enterprise_intelligence.models import EvidencePackageItem
from ..blueprint_import.semantic_twin import SemanticObject, SemanticTwin

PATH=REPO/'enterprise-knowledge/macro/research-model/Macro-Context-v1.json'
OFFERINGS={'none':'No offering selected','cyber':'Cyber & resilience services',
           'ai-delivery':'AI transformation, integration & managed services','reporting':'Reporting data & assurance services'}
KINDS={'observed_trend':'Observed trend','threat_or_scenario':'Threat / scenario','policy_priority':'Procurement policy',
       'proposed_legislation':'Proposed legislation','regulatory_rule':'Final regulatory rule',
       'enacted_law':'Enacted EU amendment · national implementation differs'}
CATEGORIES=('cyber','sustainability','technology','economy','society','policy')


class Specification(BaseModel):
    model_config=ConfigDict(extra='forbid', frozen=True)
    schema_version: Literal[1]=1


class GeographicArea(Specification):
    id: str
    kind: Literal['world','geographic_region','country']
    label: str
    members: list[str]=Field(default_factory=list)
    code_system: str | None=None
    membership_kind: str | None=None


class Jurisdiction(Specification):
    id: str
    label: str
    scope: str


class LegalEntityScope(Specification):
    id: str
    enterprise_id: str
    legal_entity_id: str | None=None
    registry_id: str | None=None
    legal_name: str | None=None
    parent_id: str | None=None
    status: Literal['unknown','interpreted','verified','conflicting']='unknown'
    evidence_ids: list[str]=Field(default_factory=list)

    @model_validator(mode='after')
    def verified_identity_needs_evidence(self):
        if self.status=='verified' and not all((self.legal_entity_id,self.registry_id,self.legal_name,self.evidence_ids)):
            raise ValueError('Verified legal identity requires exact registry identity and evidence')
        return self


class MarketContext(Specification):
    id: str
    country_id: Literal['GB','FR']
    industry_id: Literal['banking','aviation']
    industry_model_id: str
    as_of: date
    coverage: str


class ContextEdge(Specification):
    id: str
    subject: str
    predicate: Literal['INTERPRETED_PESTLE_IMPACT','INTERPRETED_CAPABILITY_PRESSURE',
                       'ENTERPRISE_APPLICABILITY','MOTIVATES_INVESTIGATION']
    object: str
    status: Literal['interpreted','unknown','verified','conflicting']
    country_id: Literal['GB','FR']
    jurisdiction_ids: list[str]
    entity_scope_id: str | None
    effective_from: date | None
    observed_period: str
    assessed_at: date
    source_ids: list[str]
    claim_ids: list[str]
    limitations: str
    supersedes: str | None=None

    @model_validator(mode='after')
    def scope_is_not_authority(self):
        if not self.source_ids or not self.claim_ids or not self.limitations:
            raise ValueError('Context relationship requires provenance and explicit limits')
        if self.predicate=='ENTERPRISE_APPLICABILITY' and self.status=='verified':
            raise ValueError('Pilot has no verified legal-entity applicability evidence')
        return self


class Selection(BaseModel):
    model_config=ConfigDict(extra='forbid', frozen=True)
    market: Literal['global','GB','FR']='global'
    category: Literal['cyber','sustainability','technology','economy','society','policy']='cyber'
    force: Literal['cyber','cyber-bill','social-value','uk-srs','eu-csrd','']='cyber'
    industry: Literal['banking','aviation']='banking'
    offering: Literal['none','cyber','ai-delivery','reporting']='none'
    view: Literal['atlas','industry','enterprise']='atlas'
    factor: str=''
    capability: str=''
    mode: Literal['explore','new','expert']='explore'


def selection(query=''):
    pairs=parse_qsl(query,keep_blank_values=True,strict_parsing=True,encoding='utf-8',errors='strict',max_num_fields=12)
    if len({k for k,v in pairs})!=len(pairs):raise ValueError('Duplicate macro selection')
    chosen=Selection(**dict(pairs));data=load_context()
    force=next((f for f in data['forces'] if f['id']==chosen.force),None)
    if not force or chosen.category not in force['category_ids']:
        # A category selection without an explicit force picks its first real theme;
        # unresearched categories have no force and cannot fabricate one.
        explicit=dict(pairs)
        if 'force' in explicit and explicit['force']:
            raise ValueError('Force/category mismatch')
        matches=[f for f in data['forces'] if chosen.category in f['category_ids']]
        local=[f for f in matches if chosen.market=='global' or chosen.market in f['country_ids']]
        force=next(iter(local or matches),None)
        chosen=chosen.model_copy(update={'force':force['id'] if force else ''})
    industry=load_assessment(chosen.industry)
    factors={r['title'] for r in industry['frameworks'] if r['lens']=='pestle'}
    if chosen.factor and chosen.factor not in factors:raise ValueError('Unknown PESTLE factor')
    if chosen.capability and chosen.capability not in {c['id'] for c in industry['capabilities']}:raise ValueError('Unknown capability')
    return chosen


def load_context():
    data=json.loads(PATH.read_text());validate_context(data);return data


def validate_context(data):
    if data['schema_version']!=1 or data['authority']!='candidate_intelligence':raise ValueError('Unknown macro context version/authority')
    cutoff=date.fromisoformat(data['as_of'])
    if cutoff>date.today():raise ValueError('Future research cut-off')
    def index(rows):
        values={r['id']:r for r in rows}
        if len(values)!=len(rows):raise ValueError('Duplicate macro identity')
        return values
    areas=index(data['areas']);jurisdictions=index(data['jurisdictions']);sources=index(data['sources']);forces=index(data['forces'])
    for area in areas.values():
        GeographicArea(**area)
        if set(area['members'])-set(areas):raise ValueError('Unknown navigation area')
    for row in jurisdictions.values():Jurisdiction(**row)
    for row in data['legal_entity_scopes']:
        scope=LegalEntityScope(**row)
        if scope.status!='unknown':raise ValueError('Pilot has no verified entity registry/footprint data')
    if {c['id'] for c in data['categories']}!=set(CATEGORIES):raise ValueError('Systemic category drift')
    for source in sources.values():
        if source['research_domain']!='macro' or source['retrieved_at'][:10]>data['as_of']:raise ValueError('Source context/date drift')
        primary_text(source)
    seen=set()
    for row in data['observations']:
        c=CandidateClaim(**row['candidate']);segment=SourceSegment(**row['segment'])
        if c.claim_id in seen or row['accepted_observation'] is not False:raise ValueError('Duplicate/accepted macro observation')
        seen.add(c.claim_id)
        source=sources.get(row['source_id'],{})
        if segment.asset_id!=row['source_id'] or c.subject!=row['source_id'] or segment.source_location!=source.get('text_path') or c.time_scope!=source.get('reporting_period'):
            raise ValueError('Passage source/scope identity drift')
        if row['source_id'] not in sources or c.source_asset_id!=row['source_id']:raise ValueError('Observation source drift')
        if c.authority!='candidate_intelligence' or segment.authority!='candidate_intelligence':raise ValueError('Macro authority escalation')
        if segment.segment_id!=row['source_id']+'::quote-'+segment.content_hash[:16]:raise ValueError('Source segment identity must remain content addressed')
        if c.statement!=segment.content or c.source_segment_id!=segment.segment_id or segment.content_hash!=hashlib.sha256(segment.content.encode()).hexdigest():raise ValueError('Passage/claim digest drift')
        if segment.content not in primary_text(sources[row['source_id']]):raise ValueError('Missing exact source passage')
    assessments={domain:load_assessment(domain) for domain in ('banking','aviation')}
    for force in forces.values():
        if force['kind'] not in KINDS or set(force['source_ids'])-set(sources):raise ValueError('Unknown force kind/source')
        if not force['source_ids'] or set(force['jurisdiction_ids'])-set(jurisdictions):raise ValueError('Missing force provenance/jurisdiction')
        if set(force['country_source_ids'])!=set(force['country_ids']) or any(not refs or set(refs)-set(force['source_ids']) for refs in force['country_source_ids'].values()):raise ValueError('Country source scope is missing or inconsistent')
        if set(force['country_ids'])-{'GB','FR'} or set(force['category_ids'])-set(CATEGORIES):raise ValueError('Unsupported market/category')
        if any(force['kind'] not in sources[sid]['supported_force_kinds'] for sid in force['source_ids']):raise ValueError('Force legal status exceeds reviewed source classification')
        if force['kind']=='proposed_legislation' and force['effective_from'] is not None:raise ValueError('Proposal cannot imply an effective law')
        for domain in ('banking','aviation'):
            assessment=assessments[domain]
            caps=set(force['capabilities'][domain])
            if caps-{c['id'] for c in assessment['capabilities']}:raise ValueError('Unknown canonical capability')
            candidates={r['id']:r for r in assessment['candidates']}
            for cid in force['candidate_ids'][domain]:
                if cid not in candidates or not caps.intersection(candidates[cid]['capability_ids']):raise ValueError('Unsupported hypothesis association')
    return data


def semantic_projection(data):
    """Adapter into the existing SemanticTwin; all observations remain unaccepted."""
    validate_context(data);records=[]
    for row in data['observations']:
        c=CandidateClaim(**row['candidate']);s=SourceSegment(**row['segment'])
        evidence=EvidencePackageItem(c.claim_id,'Observation',c.statement,'Reviewed candidate excerpt; not accepted',c.confidence,c.time_scope,(s.segment_id,c.source_asset_id),source_location=s.source_location)
        records.append(SemanticObject(c.claim_id,'Observation',c.statement,c.subject,(s.segment_id,),
            c.time_scope,c.confidence,'candidate_intelligence',s.source_location,s.section_heading,False,
            'Reviewed macro excerpt; not accepted canonical intelligence',original_id=c.claim_id,
            references=(c.source_asset_id,),validation_status='candidate',
            attributes={'candidate_claim':c.to_dict(),'segment':s.to_dict(),'evidence_item':evidence.to_dict()}))
    return SemanticTwin(tuple(records),())


def exact_entity_identity(scope, requested_legal_entity_id):
    """Identity match only; never a legal applicability or ownership decision."""
    scope=LegalEntityScope(**scope)
    return bool(scope.status=='verified' and requested_legal_entity_id
                and scope.legal_entity_id==requested_legal_entity_id)


def context_spec(chosen, data=None):
    data=deepcopy(data) if data is not None else load_context();validate_context(data)
    if not isinstance(chosen,Selection):raise ValueError('Validated presentation selection required')
    industry=load_assessment(chosen.industry)
    force=next((f for f in data['forces'] if f['id']==chosen.force),None)
    if not force and (chosen.force or any(chosen.category in f['category_ids'] for f in data['forces'])):raise ValueError('Unresolved force selection')
    if force and chosen.category not in force['category_ids']:raise ValueError('Force/category mismatch')
    countries=['GB','FR'] if chosen.market=='global' else [chosen.market]
    markets=[MarketContext(id=f"MC-{c}-{chosen.industry}-{data['as_of']}",country_id=c,industry_id=chosen.industry,
        industry_model_id=industry['assessment_id'],as_of=data['as_of'],coverage='UK-anchored structural reference; local market evidence incomplete' if c=='FR' else 'Bounded reference research, not comprehensive coverage').model_dump(mode='json') for c in countries]
    edges=[];candidates=[];claims={o['source_id']:o['candidate']['claim_id'] for o in data['observations']}
    scope=next(e for e in data['legal_entity_scopes'] if e['enterprise_id']==industry['enterprise_twin_id'])
    if force:
        def scoped(country):
            refs=force['country_source_ids'][country]
            return dict(country_id=country,jurisdiction_ids=force['jurisdiction_ids'],entity_scope_id=scope['id'],effective_from=force['effective_from'],observed_period='; '.join(s['reporting_period'] for s in data['sources'] if s['id'] in refs),assessed_at=data['as_of'],source_ids=refs,claim_ids=[claims[sid] for sid in refs],limitations='Analytical context only. Region membership, corporate group and seller fit establish no legal duty, enterprise exposure or buying demand.')
        for country in countries:
            if country not in force['country_ids']:continue
            base=scoped(country)
            for factor in industry['frameworks']:
                if factor['lens']=='pestle' and factor['title'] in force['pestle']:
                    edges.append(ContextEdge(id=f"GM-{force['id']}-{country}-{factor['id']}",subject=force['id'],predicate='INTERPRETED_PESTLE_IMPACT',object=factor['id'],status='interpreted',**base).model_dump(mode='json'))
            for cap in force['capabilities'][chosen.industry]:
                edges.append(ContextEdge(id=f"GM-{force['id']}-{country}-{cap}",subject=force['id'],predicate='INTERPRETED_CAPABILITY_PRESSURE',object=cap,status='interpreted',**base).model_dump(mode='json'))
            edges.append(ContextEdge(id=f"GM-{force['id']}-{country}-{industry['enterprise_twin_id']}",subject=force['id'],predicate='ENTERPRISE_APPLICABILITY',object=industry['enterprise_twin_id'],status='unknown',**base).model_dump(mode='json'))
        # Existing group hypotheses are UK reference research, never silently
        # transplanted into France. Empty is an honest commercial result.
        if 'GB' in countries and 'GB' in force['country_ids']:
            projection=commercial_projection(industry)
            candidates=[deepcopy(c) for c in projection['candidates'] if c['id'] in force['candidate_ids'][chosen.industry]]
            for row in candidates:
                base=scoped('GB')
                base['claim_ids']=base['claim_ids']+row['claim_ids']
                base['source_ids']=base['source_ids']+sorted({sid for claim in industry['claims'] if claim['id'] in row['claim_ids'] for sid in claim['source_ids']})
                edges.append(ContextEdge(id=f"GM-{force['id']}-{row['id']}",subject=force['id'],predicate='MOTIVATES_INVESTIGATION',object=row['id'],status='interpreted',**base).model_dump(mode='json'))
    return {'schema_version':1,'authority':'candidate_intelligence','as_of':data['as_of'],'selection':chosen.model_dump(),
        'markets':markets,'force':force,'industry_model_id':industry['assessment_id'],'industry_id':chosen.industry,
        'enterprise':{'id':industry['enterprise_twin_id'],'name':industry['enterprise_name'],'slug':('lloyds' if chosen.industry=='banking' else 'easyjet'),'legal_entity_scope':deepcopy(scope),'applicability':'unknown'},
        'edges':edges,'candidates':candidates,'seller_relevance':{'declared_offering':chosen.offering,'match':'potential thematic fit only' if force and chosen.offering!='none' and chosen.offering in force['seller_tags'] else 'not established','territory_permission':'unverified','customer_demand':'unverified','pipeline_eligibility':'not assessed'},
        'snapshot_digest':digest(data),'automatic_capture':False,'automatic_qualification':False,'limitations':data['limitations']}


class GlobalContextContracts(Specification):
    """Portable metadata definitions; evidence classes keep their existing owner."""
    areas: list[GeographicArea]
    jurisdictions: list[Jurisdiction]
    legal_entity_scopes: list[LegalEntityScope]
    market_contexts: list[MarketContext]
    relationships: list[ContextEdge]


def context_schema():
    result=GlobalContextContracts.model_json_schema()
    result['$id']='urn:cios:flora:global-context:1'
    result['description']='Reusable presentation context contracts only; not canonical evidence, legal applicability or workspace authority. Existing SourceSegment/CandidateClaim/EvidencePackageItem remain evidence owners.'
    return result
