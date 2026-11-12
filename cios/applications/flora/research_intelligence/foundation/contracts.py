"""Versioned operational contracts, not competing canonical intelligence classes."""
from datetime import date, datetime, timezone
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from ..cycle import digest

ROLES=('researcher','verifier','entity_checker','challenger','synthesis_reviewer','publication_reviewer','release_controller')
OPERATIONS=('acquisition','deterministic_extraction','model_processing','retention','quotation','indexing','redistribution')
GATES=frozenset(('independent-acquisition','schema-date-identity-locator','operation-rights','contradiction-source-family','sensitive-publication','release-controller'))
RELATIONS=('provider_supplies_product','product_supports_capability','declared_alliance','implementation_role',
           'industry_relevance','enterprise_deployment')

class Contract(BaseModel):
    model_config=ConfigDict(extra='forbid',frozen=True)
    schema_version: Literal[1]=1

class Rights(Contract):
    source_id: str
    url: str
    family_id: Literal['GCA-published-catalogue']
    licence_url: Literal['https://www.gca.gov.uk/terms-and-conditions']
    licence_locator: str
    attribution: str
    decisions: dict[str,Literal['allowed','blocked','unknown']]
    allowed_extent: Literal['short_crown_factual_excerpt']='short_crown_factual_excerpt'
    max_quote_words: int=Field(default=25,ge=1,le=25)
    exclusions: list[str]=Field(min_length=1)
    @model_validator(mode='after')
    def complete(self):
        if set(self.decisions)!=set(OPERATIONS) or not all((self.licence_url,self.licence_locator,self.attribution)):
            raise ValueError('Separate complete operation permissions and licence evidence required')
        if not self.url.startswith('https://') or self.url.split('/')[2]!='www.gca.gov.uk':
            raise ValueError('Foundation live source profile is finite GCA public catalogue only')
        if self.url not in {
          'https://www.gca.gov.uk/agreements/RM6098:3/lot-suppliers',
          'https://www.gca.gov.uk/agreements/RM6292/suppliers',
          'https://www.gca.gov.uk/agreements/RM3764.3/suppliers',
          'https://www.gca.gov.uk/agreements/RM6190:1/lot-suppliers',
          'https://www.gca.gov.uk/suppliers/6512/advania-uk-ccs-limited'}:
            raise ValueError('Unreviewed source URL')
        return self
    def require(self,*operations):
        if any(self.decisions.get(op)!='allowed' for op in operations):
            raise PermissionError('Operation rights unresolved or restricted')

class Caps(Contract):
    requests: int=Field(default=12,ge=2,le=30)
    bytes: int=Field(default=16000,ge=100,le=1000000)
    attempts_per_source: int=Field(default=2,ge=1,le=3)
    max_publication_age_days: int=Field(default=365,ge=1,le=3650)
    monetary_cost: float=Field(default=0,ge=0,le=0)

class Programme(Contract):
    id: str
    objective: str
    mode: Literal['establish','enrich','monitor','reconcile']='establish'
    as_of: date
    country: Literal['GB']='GB'
    jurisdictions: list[str]=Field(min_length=1)
    industry_id: Literal['UK-TECHNOLOGY']='UK-TECHNOLOGY'
    audience: Literal['shared_public']='shared_public'
    taxonomy: list[dict]
    baseline_requirements: list[str]
    dependencies: list[str]
    source_policy_version: Literal['uk-tech-crown-excerpts-v1']='uk-tech-crown-excerpts-v1'
    output_schema_version: Literal['research-publication-v1']='research-publication-v1'
    assurance_gates: list[str]
    roles: dict[str,str]
    caps: Caps=Field(default_factory=Caps)
    sources: list[Rights]
    publication_limitations: list[str]
    @model_validator(mode='after')
    def bounded(self):
        if self.as_of>date.today():raise ValueError('Future programme cut-off')
        if set(self.roles)!=set(ROLES) or len(set(self.roles.values()))!=len(ROLES):
            raise ValueError('Distinct configured role responsibilities required')
        if len({s.source_id for s in self.sources})!=len(self.sources):raise ValueError('Duplicate source identity')
        if set(self.assurance_gates)!=GATES:raise ValueError('All mandatory assurance gates required')
        if not self.sources or not self.taxonomy:raise ValueError('Bounded sources and taxonomy required')
        if not self.baseline_requirements or not self.publication_limitations:raise ValueError('Coverage and limitations required')
        return self

class Acquisition(Contract):
    request_id: str
    source_id: str
    url: str
    role: Literal['researcher','verifier']
    collector_id: str
    retrieved_at: datetime
    publication_date: date | None=None
    effective_date: date | None=None
    locator: str
    excerpt: str
    excerpt_sha256: str
    primary_content_sha256: None=None
    tool_reference: str
    execution_kind: Literal['fixture','live_web_bridge']='fixture'
    visibility: Literal['public']='public'
    extent: Literal['reviewed_web_excerpt']='reviewed_web_excerpt'
    @model_validator(mode='after')
    def honest_extent(self):
        import hashlib
        if self.retrieved_at.tzinfo is None or self.retrieved_at>datetime.now(timezone.utc):raise ValueError('Nonfuture timezone-aware retrieval required')
        if self.publication_date and self.publication_date>self.retrieved_at.date():raise ValueError('Publication after retrieval')
        if self.effective_date and self.effective_date>date.today():raise ValueError('Future effectivity is not current support')
        if not self.locator or not self.tool_reference or not self.collector_id:raise ValueError('Located actual acquisition provenance required')
        if hashlib.sha256(self.excerpt.encode()).hexdigest()!=self.excerpt_sha256:raise ValueError('Excerpt checksum mismatch')
        return self

class Relationship(Contract):
    id: str
    subject: str
    predicate: Literal['provider_supplies_product','product_supports_capability','declared_alliance','implementation_role','industry_relevance','enterprise_deployment']
    object: str
    truth_class: Literal['publisher_reported_fact','interpretation','scenario']
    claim_ids: list[str]=Field(min_length=1)
    entity_id: str | None
    jurisdiction: str
    limitations: str
    @model_validator(mode='after')
    def exact_scope(self):
        if self.predicate in ('implementation_role','enterprise_deployment') and (not self.entity_id or self.truth_class!='publisher_reported_fact'):
            raise ValueError('Named deployment/implementation requires exact entity and direct factual support')
        return self


class Narrative(Contract):
    """Operational envelope around existing CandidateClaim IDs; never canonical fact."""
    id: str
    truth_class: Literal['interpretation','scenario']
    statement: str
    claim_ids: list[str]
    assumptions: list[str]
    limitations: str=Field(min_length=1)
    @model_validator(mode='after')
    def explicit_basis(self):
        if self.truth_class=='interpretation' and not self.claim_ids:raise ValueError('Interpretation needs traceable evidence')
        if self.truth_class=='scenario' and not self.assumptions:raise ValueError('Scenario needs explicit assumptions')
        return self
