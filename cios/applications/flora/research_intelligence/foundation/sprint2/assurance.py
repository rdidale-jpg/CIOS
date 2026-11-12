"""Conservative semantic preflight. No confidence vote or lexical overlap releases prose.

The built-in proof is intentionally narrow: a controlled investment-plan grammar
compiled independently from each retrieved passage. Other propositions require a
separately configured semantic verifier and remain unresolved in this environment.
"""
from datetime import date,datetime,timezone
from decimal import Decimal
import hashlib,re
from typing import Literal
from pydantic import Field,model_validator
from ..contracts import Contract,OPERATIONS
from ..operations import INJECTION,SENSITIVE
from ...cycle import digest
from ....enterprise_intelligence.semantic import SourceSegment,CandidateClaim

POLICY='uk-tech-semantic-preflight-v1'
RULE_VERSION='controlled-investment-plan-v1'

class Meaning(Contract):
    subject: str
    predicate: Literal['investment','owns_product','supports_capability','alliance','implementation','industry_fit','deployment','causes','business_model']
    object: str
    geography: str
    modality: Literal['planned','reported','achieved','potential']
    reporting_period: str
    amount: Decimal | None=None
    currency: str | None=None
    truth_class: Literal['publisher_reported_fact','interpretation','scenario']='publisher_reported_fact'
    assumptions: list[str]=Field(default_factory=list)
    @model_validator(mode='after')
    def bounded_numbers(self):
        if self.amount is not None and (not self.amount.is_finite() or self.amount<0 or not self.currency):raise ValueError('Scoped finite amount/currency required')
        if self.truth_class=='scenario' and not self.assumptions:raise ValueError('Scenario assumptions required')
        return self

class Passage(Contract):
    id: str
    source_id: str
    url: str
    origin_id: str
    role: Literal['researcher','verifier']
    collector_id: str
    request_id: str
    tool_reference: str
    retrieved_at: datetime
    publication_date: date
    effective_date: date | None=None
    reporting_period: str
    locator: str
    text: str
    sha256: str
    rights: dict[str,Literal['allowed','unknown','blocked']]
    rights_basis: str
    visibility: Literal['public_non_personal']='public_non_personal'
    execution_kind: Literal['fixture','live_web_bridge']='fixture'
    supersedes: list[str]=Field(default_factory=list)
    @model_validator(mode='after')
    def integrity(self):
        if self.retrieved_at.tzinfo is None or self.retrieved_at>datetime.now(timezone.utc):raise ValueError('Actual aware retrieval time required')
        if self.publication_date>self.retrieved_at.date():raise ValueError('Future publication')
        if hashlib.sha256(self.text.encode()).hexdigest()!=self.sha256:raise ValueError('Passage hash mismatch')
        if not self.locator or not self.rights_basis or not self.origin_id:raise ValueError('Located provenance and rights required')
        if set(self.rights)!=set(OPERATIONS):raise ValueError('Complete operation-specific permissions required')
        if not self.url.startswith('https://'):raise ValueError('HTTPS provenance required')
        return self

class Proposal(Contract):
    id: str
    meaning: Meaning
    statement: str
    source_ids: list[str]=Field(min_length=1)
    source_segments: list[str]=Field(min_length=1)
    period_use: Literal['historical','current']='current'


def statement(m):
    """Only this total renderer is proof-eligible; arbitrary prose is not silently accepted."""
    amount=str(m.amount.normalize()) if m.amount is not None else 'unspecified'
    return f'{m.subject} | {m.predicate} | {m.object} | {m.geography} | {m.modality} | {m.reporting_period} | {amount} {m.currency or ""} | {m.truth_class}'


def extract(p):
    """Bounded compositional meaning, not a general language model or entity resolver.

    All text must match. No ignored trailing clauses, hidden conclusion or arbitrary
    entity annotation may supply subject/geography/modality/numeric scope.
    """
    text=' '.join(p.text.split())
    # Explicit government-announcement grammar: planned amount, never estimated GDP/jobs.
    actual=re.fullmatch(r'The Chancellor Rachel Reeves has today \[11 September\] confirmed an £(?P<amount>\d+) billion investment from (?P<subject>Amazon Web Services) which is estimated to support thousands of jobs across the UK\. The Chancellor secured the planned five-year investment last week at a meeting with Amazon Web Services\. AWS estimates that these investments in the UK will contribute £14 billion to the UK’s total Gross Domestic Product \(GDP\) from 2024 to 2028\.',text)
    if actual:
        return Meaning(subject=actual['subject'],predicate='investment',object='investment',geography='GB',modality='planned',reporting_period='five-year plan (endpoints unspecified)',amount=Decimal(actual['amount'])*1000000000,currency='GBP')
    match=re.fullmatch(r'(?P<subject>[A-Za-z][A-Za-z0-9 ()&.-]{1,80}) plans to invest £(?P<amount>\d+(?:\.\d+)?) billion in (?P<object>[a-z -]+) in the (?P<country>UK|France) during (?P<start>20\d\d)[–-](?P<end>20\d\d)\.',text)
    if not match:return None
    v=match.groupdict()
    if int(v['end'])<int(v['start']):return None
    return Meaning(subject=v['subject'],predicate='investment',object=v['object'],geography={'UK':'GB','France':'FR'}[v['country']],modality='planned',reporting_period=v['start']+'-'+v['end'],amount=Decimal(v['amount'])*1000000000,currency='GBP')



def origin_count(passages):
    remaining=set(range(len(passages)));count=0
    while remaining:
        count+=1;front={remaining.pop()}
        while front:
            neighbours={j for i in front for j in remaining if passages[j].origin_id==passages[i].origin_id or passages[j].sha256==passages[i].sha256}
            remaining-=neighbours;front=neighbours
    return count


def assess(proposal,passages,*,as_of,run_id,verifier_id,max_age_days=365,max_attempts=2):
    q=Proposal.model_validate(proposal.model_dump(mode='json') if isinstance(proposal,Proposal) else proposal)
    ps=[Passage.model_validate(p.model_dump(mode='json') if isinstance(p,Passage) else p) for p in passages]
    day=date.fromisoformat(as_of)
    if day>date.today() or not run_id or not verifier_id or not 1<=max_attempts<=3:raise ValueError('Bounded actual assurance scope required')
    outcome='unresolved';reasons=[];checks=[];proofs=[]
    def result():
        return {'schema_version':1,'policy':POLICY,'rule_version':RULE_VERSION,'run_id':run_id,'verifier_id':verifier_id,'claim_id':q.id,
          'claim_digest':digest(q.model_dump(mode='json')),'outcome':outcome,'reasons':reasons,'checks':checks,
          'passage_refs':[{'id':p.id,'hash':p.sha256,'source_id':p.source_id,'locator':p.locator,'retrieval':p.tool_reference,'origin_id':p.origin_id} for p in ps],
          'source_family_count':origin_count(ps),'assurance':'deterministic controlled-meaning proof; general natural-language semantic verifier unavailable',
          'attempt_cap':max_attempts,'attempts_used':1,'canonical_promotion':False,'pipeline_qualification':False,'decision_reasoning':'Concise rule decisions only; no private model reasoning retained'}
    if any(INJECTION.search(p.text) or SENSITIVE.search(p.text) for p in ps):
        outcome='reject';reasons.append('Unsafe/sensitive source material quarantined');return result()
    if any(any(p.rights.get(op)!='allowed' for op in ('acquisition','deterministic_extraction','retention','quotation','indexing','redistribution')) for p in ps):
        reasons.append('Required operation rights unresolved/restricted');return result()
    if q.statement!=statement(q.meaning):
        reasons.append('Arbitrary prose cannot be proved by the controlled semantic renderer');return result()
    if {p.source_id for p in ps}-set(q.source_ids) or {p.id for p in ps}-set(q.source_segments):
        outcome='reject';reasons.append('Evidence not scoped to complete proposal');return result()
    for source in q.source_ids:
        selected=[p for p in ps if p.source_id==source]
        pairs={r:[p for p in selected if p.role==r] for r in ('researcher','verifier')}
        if any(len(v)!=1 for v in pairs.values()):reasons.append('One independent researcher/verifier acquisition pair required per source');return result()
        a,b=pairs['researcher'][0],pairs['verifier'][0]
        if a.request_id==b.request_id or a.collector_id==b.collector_id or a.tool_reference==b.tool_reference or b.collector_id!=verifier_id or b.retrieved_at<a.retrieved_at:
            outcome='reject';reasons.append('Independent retrieval/run identity failed');return result()
        if (a.url,a.origin_id,a.locator,a.publication_date,a.effective_date,a.reporting_period,a.text,a.execution_kind)!=(b.url,b.origin_id,b.locator,b.publication_date,b.effective_date,b.reporting_period,b.text,b.execution_kind):
            outcome='reject';reasons.append('Conflicting source content/date/scope metadata');return result()
        if a.publication_date>day or a.effective_date and a.effective_date>day:
            outcome='reject';reasons.append('Evidence is not effective at cut-off');return result()
        if q.period_use=='current' and (day-a.publication_date).days>max_age_days:
            reasons.append('Stale support; refresh or explicitly assess historical statement');return result()
        if a.id in {s for p in ps for s in p.supersedes}:
            outcome='reject';reasons.append('Superseded passage cannot authorise a current conclusion');return result()
        frame=extract(b)
        if frame is None:
            reasons.append('Full passage outside bounded grammar; independent natural-language assurance required');return result()
        if frame.reporting_period!=b.reporting_period:
            outcome='reject';reasons.append('Reporting context contradicts passage meaning');return result()
        proofs.append(frame)
    if not proofs:reasons.append('No supporting semantic proof');return result()
    if any(p!=proofs[0] for p in proofs):outcome='reject';reasons.append('Conflicting official propositions');return result()
    if q.meaning.truth_class!='publisher_reported_fact':
        reasons.append('Interpretation/scenario needs independent semantic assurance and explicit assumptions');return result()
    if q.meaning!=proofs[0]:outcome='reject';reasons.append('Complete proposition mismatch: entity/geography/modality/period/amount/predicate/truth class');return result()
    outcome='accept_bounded';checks.extend(['complete proposition','independent passage re-extraction','temporal scope','rights','source origin','no unproved free prose'])
    reasons.append('Only a reported plan is supported; no achieved outcome, causal benefit, adoption or budget qualification inferred')
    return result()


def canonical_candidates(q,p):
    """Reuse existing canonical candidate/segment classes without promotion eligibility."""
    return (SourceSegment(p.id,p.source_id,p.locator,p.text,p.sha256,p.url,'candidate_intelligence','semantic_assurance_pending'),
      CandidateClaim(q.id,q.meaning.truth_class,q.statement,p.source_id,p.id,q.meaning.geography,q.meaning.subject,q.meaning.predicate,q.meaning.object,q.meaning.reporting_period,q.meaning.subject,q.meaning.subject,'Unverified until bounded assurance','candidate_intelligence','withheld',[],[]))
