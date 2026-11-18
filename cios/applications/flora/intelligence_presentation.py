"""ISP-1 deterministic, read-only presentation policy. No intelligence ownership.

Types below describe a transient view, never canonical enums or acceptance.
Callers must supply already authorised owner projections; this module never
queries a repository, authenticates a user, qualifies a pressure or writes data.
"""
from dataclasses import dataclass, replace
from contextvars import ContextVar
from contextlib import contextmanager
from decimal import Decimal, InvalidOperation
from datetime import date
import hashlib
from html import escape
import re
from urllib.parse import urlsplit

TYPES = frozenset({'reported', 'calculated', 'estimated', 'assumed', 'insight', 'hypothesis'})
LABELS = {'reported':'Reported', 'calculated':'Calculated', 'estimated':'Estimated',
          'assumed':'Working assumption', 'insight':'FLORA Insight', 'hypothesis':'Hypothesis'}
# Fail closed for backlog/action copy; this is not a text classifier. Semantic
# kind is supplied by the owning adapter, never guessed from these words.
NON_CORE = re.compile(r'\?|\b(?:unknown|missing|research gap|research coverage|completeness|next action|next question|needs? validation|needs? verification|must (?:check|confirm)|should (?:investigate|engage)|recommend(?:ed|ation)?|investigate next|still to establish)\b', re.I)

@dataclass(frozen=True)
class Source:
    title: str
    url: str
    publisher: str = ''
    published: str = ''
    period: str = ''
    quote: str = ''
    locator: str = ''

@dataclass(frozen=True)
class Statement:
    text: str
    semantic_type: str
    scope: str
    period: str
    sources: tuple[Source, ...]
    verification: str
    canonical_status: str
    measurement_state: str = 'not_applicable'
    basis: str = ''
    value: Decimal | None = None
    unit: str = ''
    method: str = ''
    reasoning: str = ''
    caveats: tuple[str, ...] = ()
    counter_evidence: tuple[str, ...] = ()
    falsifier: str = ''
    assumption_owner: str = ''
    assumption_version: str = ''
    dependencies: tuple[str, ...] = ()
    dependency_types: tuple[str, ...] = ()
    input_authorities: tuple[str, ...] = ()
    owner_only: bool = False
    freshness: str = 'current'
    core_contradiction: bool = False
    material_caveats: tuple[str, ...] = ()


def eligible(item: Statement) -> bool:
    """Omission, not Unknown placeholders. Does not grant source/record access."""
    if (item.semantic_type not in TYPES or item.owner_only or item.core_contradiction
            or item.freshness in {'stale','superseded','withdrawn'}
            or not item.text.strip() or NON_CORE.search(item.text)
            or not item.scope or not item.period or not item.sources):
        return False
    if item.value is not None and not item.value.is_finite():
        return False
    for s in item.sources:
        p=urlsplit(s.url)
        if s.published:
            try:
                if date.fromisoformat(s.published[:10])>date.today():return False
            except ValueError:return False
        if not s.title or p.scheme!='https' or not p.hostname or p.username or p.password:
            return False
    if item.semantic_type=='reported' and (item.verification not in {'reviewed_excerpt','verified_original','reported_source'} or item.dependencies):
        return False
    if item.semantic_type=='calculated' and (not item.method or not item.dependencies or not item.dependency_types):
        return False
    if item.semantic_type=='estimated' and (not item.method or not item.caveats):
        return False
    if item.semantic_type=='assumed' and (not item.assumption_owner or not item.assumption_version or not item.caveats):
        return False
    if item.semantic_type in {'insight','hypothesis'} and (not item.reasoning or not item.dependencies or not item.counter_evidence):
        return False
    if item.semantic_type=='hypothesis' and not item.falsifier:
        return False
    return True


def difference(left: Statement, right: Statement, *, text: str) -> Statement:
    """One bounded display calculation, not an expression/reasoning engine."""
    if (not eligible(left) or not eligible(right) or left.value is None or right.value is None
            or left.semantic_type not in {'reported','calculated','estimated','assumed'}
            or right.semantic_type not in {'reported','calculated','estimated','assumed'}
            or (left.scope,left.period,left.unit,left.basis,left.measurement_state)
               !=(right.scope,right.period,right.unit,right.basis,right.measurement_state)):
        raise ValueError('Incompatible or unsupported calculation inputs')
    sources=tuple(dict.fromkeys((*left.sources,*right.sources)))
    kinds=tuple(dict.fromkeys((left.semantic_type,*left.dependency_types,right.semantic_type,*right.dependency_types)))
    return Statement(text,'calculated',left.scope,left.period,sources,'derived_from_inputs',
        'derived_view_not_canonical',left.measurement_state,left.basis,left.value-right.value,left.unit,
        method=f'{left.value} − {right.value} {left.unit}',
        caveats=tuple(dict.fromkeys((*left.caveats,*right.caveats))),
        counter_evidence=tuple(dict.fromkeys((*left.counter_evidence,*right.counter_evidence))),
        dependencies=(left.text,right.text),dependency_types=kinds,
        input_authorities=(left.canonical_status,right.canonical_status))



_editorial = ContextVar('flora_editorial_presentation', default=False)
_editorial_sources = ContextVar('flora_editorial_sources', default=None)


@contextmanager
def editorial_view(reading=True):
    token = _editorial.set(reading)
    source_token = _editorial_sources.set([])
    try:
        yield
    finally:
        _editorial_sources.reset(source_token)
        _editorial.reset(token)


def note_editorial_sources(sources):
    state = _editorial_sources.get()
    if state is not None:
        for source in sources:
            if source not in state:state.append(source)


def editorial_sources():
    return tuple(_editorial_sources.get() or ())


def is_editorial():
    return _editorial.get()


def editorial(item: Statement, *, compact=False):
    """Ordinary reading: same eligibility, no inspection/provenance markup.

    Full records/rendering stay in the existing Research owner. Material scope,
    periods and uncertainty are composed explicitly by each existing view.
    """
    if _editorial.get()=='facts' and item.semantic_type in {'insight','hypothesis','assumed'}:return ''
    if not eligible(item): return ''
    note_editorial_sources(item.sources)
    label = LABELS[item.semantic_type]
    state = {'target':'Management target','guidance':'Management guidance',
             'expectation':'Management expectation','commitment':'Stated priority',
             'proposal':'Proposed policy','conditional':'Conditional'}.get(item.measurement_state,'')
    annotation = ('<span class="sr-only">Reported: </span>' if item.semantic_type=='reported'
                  else '<span class="intelligence-label">'+label+'</span> ')
    if state: annotation += '<span class="intelligence-state">'+escape(state)+'</span> '
    return ('<article class="intelligence-statement" data-semantic-type="'+item.semantic_type+'"><p>'
            +annotation+escape(item.text)+'</p>'
            +('' if compact else '<p class="timing">'+escape(item.period)+'</p>')
            +''.join('<p class="material">'+escape(c)+'</p>' for c in item.material_caveats)
            +('<p class="material">Based on estimates or working assumptions.</p>' if {'estimated','assumed'}.intersection(item.dependency_types) else '')+'</article>')

def render(item: Statement, *, compact=False) -> str:
    if is_editorial(): return editorial(item, compact=compact)
    if not eligible(item):return ''
    e=escape;kind=item.semantic_type;label=LABELS[kind]
    # Ordinary reported facts retain an accessible type without repeated badges.
    annotation=('<span class="sr-only">Reported: </span>' if kind=='reported' else '<span class="intelligence-label">'+label+'</span> ')
    state={'target':'Management target','guidance':'Management guidance','expectation':'Management expectation','commitment':'Stated priority','proposal':'Proposed policy'}.get(item.measurement_state,'')
    if state:annotation+='<span class="intelligence-state">'+state+'</span> '
    body='<article class="intelligence-statement" data-semantic-type="'+kind+'"><p>'+annotation+e(item.text)+'</p>'
    if not compact:body+='<p class="timing">'+e(item.period)+'</p>'
    body+='<details class="intelligence-source"><summary>Sources &amp; reasoning</summary><p>'+e(item.scope)+' · '+e(item.period)+'</p>'
    if item.basis:body+='<p>'+e(item.basis)+'</p>'
    quality={'reviewed_excerpt':'Published source · reviewed excerpt','verified_original':'Published source · original inspected','reported_source':'Attributed published statement','derived_from_inputs':'Derived from the stated inputs','repository_interpretation':'Interpretation of the cited research'}.get(item.verification,'Attributed interpretation')
    body+='<p>'+quality+'</p>'
    if item.method:body+='<p>Method: '+e(item.method)+'</p>'
    if item.dependency_types and any(t in {'assumed','estimated'}for t in item.dependency_types):
        body+='<p class="material-caveat">Depends on '+e(', '.join(LABELS[t].lower()for t in item.dependency_types if t in {'assumed','estimated'}))+'. The result retains these input limitations.</p>'
    if item.assumption_owner:body+='<p>Assumption owner: '+e(item.assumption_owner)+' · version '+e(item.assumption_version)+'</p>'
    if item.reasoning:body+='<p>'+e(item.reasoning)+'</p>'
    for text in (*item.caveats,*item.counter_evidence):body+='<p>'+e(text)+'</p>'
    if item.falsifier:body+='<p>Falsifier: '+e(item.falsifier)+'</p>'
    for text in item.dependencies:body+='<p>Input: '+e(text)+'</p>'
    for source in item.sources:
        body+='<p><a href="'+e(source.url,quote=True)+'" rel="noreferrer">'+e(source.title)+'</a>'
        if source.published:body+=' · '+e(source.published)
        body+='</p>'
        if source.quote:body+='<blockquote>'+e(source.quote)+'</blockquote>'
        if source.locator:body+='<p>'+e(source.locator)+'</p>'
    # No owner IDs, gap lists, coverage counts, repair tasks or canonical-review
    # records are serialised, even into attributes, hidden markup or JSON.
    return body+'</details></article>'

# Exact source statements remain owned by the existing research overlay. Only
# the first declarative disclosure is projected; material limitations are kept
# separately, not deleted from the original record or excerpt.
KINDS={'reported_fact':'reported','reported_relationship':'reported','reported_programme':'reported',
       'management_priority':'reported','management_commitment':'reported','management_expectation':'reported',
       'regulatory_requirement':'reported','proposed_transaction':'reported','interpretation':'insight'}
CAVEATS={
 'LBG-Q326-PROFIT':('Consolidated Group statutory profit is a nine-month flow, not an investment allocation.',),
 'LBG-Q326-DEPOSITS':('Deposits are a balance-sheet stock, not income or a supplier budget.',),
 'LBG-A2030-CIR':('A 2030 management target, not achieved efficiency or a spending commitment.',),
 'LBG-A2030-PLATFORMS':('A stated priority does not establish external supplier scope or an open procurement.',),
 'LBG-A2030-DATA':('A strategy priority is distinct from delivered benefits.',),
 'LBG-AR25-MIGRATION':('A dated management priority does not establish delivery outcomes.',),
 'LBG-ENVOY-GOOGLE':('An announced collaboration does not disclose contract value, exclusivity, renewal or workshare.',),
 'LBG-ENVOY-CONTROLS':('Company-described controls are not independently measured effectiveness or customer outcomes.',),
 'LBG-BRAND26-TIMING':('A dated management plan, not a measurement of completed delivery.',),
 'UK-RATE-NOV26':('Rate direction alone establishes neither a particular bank margin effect nor customer demand.',),
 'UK-PRA-REPORT27':('Sector policy scope does not establish a particular legal entity’s duties or preparedness.',),
 'UK-FCA-REPORT27':('A regulatory deadline does not establish a particular bank’s unmet need.',),
 'UK-VALUE':('Industry business-model interpretation, not a measurement of customer trust, loss or demand.',),
}


DISCLOSURE_PINS = {'LBG-DEPOSITS': 'f9a7dac5b0a86729a905069f2b5dae59091528b18dd77bcb3941eb8ee1e7a955', 'LBG-CUSTOMERS': '5483896c45a44970333df20a990fede6a8701d7ef9e07efc1181f2b135b787f0', 'LBG-HEDGE': '37b2f0425b52139345229e51fd93f5cdc0961fd3f93170c408bdb1a65d639bcd', 'LBG-TECH-COST': '92e83a373d8a45620a01975e2c0293f6cc840b8417189fbac23f3e516628838e', 'LBG-MIGRATION': '359769c8fce44750ef24b9caf4730be9fa4769b41ea8fec9f8cb31162b7a777f', 'LBG-AI-USE': '88b384d424fd1233bb7f579e714a30c063d7221918e4552b8e2d9e21623fd418', 'LBG-AI-VALUE': 'eb0a7857fb5b16dfb86ad3da2defc6a7f23478d3ec28caf1e9fd38bd5c2a34c8', 'LBG-AI-TARGET': '076326a4b1a4fa5419976e249a3762e2ba075c7893360a8704ce767bf06f1d24', 'LBG-VERTEX': '3b58f80458408f96163840b5711f80ecaf4d1c79f5ae29b21476b97fc0871828', 'LBG-MODELS': '8295972220aee189a60deba82a7b8a58c1045d680372aeb86647da51eadde6a9', 'LBG-COPILOT': 'f436b0366dddae267c8bbae65fecab94c266fd2e3bc985dd05809e1df0f55433', 'LBG-BRAND': 'a8c3db07428b05dc9a7c3e42e10f3fa96bdbf6c72795c039fe3ebfdcd42bab31', 'LBG-ACCESS': '36acbe82e454dba0472ac1d9ebcbc3eb447b833a1ad92b1e24855f40af25bd43', 'LBG-SUPPLIER-RISK': '8d55264fa74d0edc962fbb0e8d00b2a156bce447b7472bb8277b11b446c0c8c5', 'LBG-PRIMACY-GAP': 'edd45ff28a3790e0c2271d6e06911a0abbbd9b649a28e5b3fca45a1c3a035d9a', 'LBG-BPO-GAP': '3a984cd28cac93e3aebb99369050e717e27005bd7632dab75d2070ca9af5ef4d', 'LBG-FRAUD-GAP': '5ad3c62ec92ec880780fdbafd8ba3f90bf42e4bb639b63f78a957b8ab3bcba54', 'LBG-CURVE': 'ddb0ed836d295c8c3fd050fc5d3d58198c4a893de544831cab137bb2f4b3882c', 'UK-CTP': 'aa2c27adac174bb4bbe0e01a35b77ad8abdf563181a95b08b3a8491e3e5096e2', 'UK-CAPITAL': 'e607086ba25d655d0125471787deb06b9438aec7139e195744e03ba2d48a4c26', 'UK-VALUE': '83e031f057bfbf078ae150a1a709bed43e2a31d35c76b20e909d7303d8dfcfe9', 'LBG-Q326-PROFIT': 'd82972b2248ffa8e6fa7913df48d7ad9c4827a1a5d436a8c9dfd978f0513c4c9', 'LBG-Q326-DEPOSITS': 'f3746247b80755c67bcbe2ca791bd1d01555750c2103098501c70d101922cea2', 'LBG-Q326-CURVE': '36c70a38095379f801a9324f87aaa078e0e0250bde23e7452a04404a6cd96ca8', 'LBG-Q326-INVESTMENT': '72b5c0656891ea4ea7beb7fbbe7f53b2589d0c5affda9e440d7433205407bc55', 'LBG-AR25-DEPOSITS': '12999eda8fb9ce3b72c0a2f340b8f1cfd135b6435464b5793aabe7b6257650b8', 'LBG-AR25-COPILOT': 'bc50df400746f038858f1a196c4f4e04f21529fb815b06842871617632d59350', 'LBG-AR25-MIGRATION': '9e240bb1cb7409ab6b95008ede4058ac26a067a83d0200a54d46f358ef2695ed', 'LBG-A2030-PLATFORMS': 'ea2d9c0eb360b8de4403ffdca30b8a20f54064f9079402ab297e6dc704059c10', 'LBG-A2030-DATA': '3327445d6c4d3e99e6291a0aae6591deda6c65382fd0195fa4fae70d2f233c1b', 'LBG-A2030-SAVINGS': '9f0593a5c719cf44a6977dee26abaf5911ac57be609d787609ac4a5540aabb99', 'LBG-A2030-CIR': '9b7f624d9c15e6d727dd7eec814a9a617794252e01875a692d40c69f947b9788', 'LBG-A2030-WALLET': '846e020988b605f7f95a129fd5cdd26476939ba430b9d4c5672f482e07dab5d4', 'LBG-A2030-INVESTMENT': '318a1192f332d4842090401b164a116a7effefaeae41605d18abc5f5dd97ba56', 'LBG-ENVOY-GOOGLE': 'd879922f09591cfee3e8671b8a8cd28ae8e5d9214d715684ef6c70ac507257af', 'LBG-ENVOY-CONTROLS': '563e97eb48b3587bc0de0677af0953b37f555927dfba38dbcbeff5d76e3b0d8a', 'LBG-BRAND26-TIMING': '774ba34311c5be0062fa9d7880067b4535d7c93cd655e79d6d15e78c3fe1a279', 'LBG-BRAND26-NO-ROLES': 'c5943e89906cf5eac66484948ff888a34c8ae126fca79833e2ba519e13c28856', 'LBG-AI26-REPORTED': '47368f0080b99690b767449143327f22c9c4d8373414362cbb59cceb4e02e597', 'LBG-AI26-EXPECTED': '7a461947ac92d677b4bbb9b51311cfef96085afd41aa6a6267a792dbf700c8f9', 'UK-RATE-NOV26': 'bbf238daba15cb43ee9effaefde475d6edaf78be3fb8bcc555bcb25457066cbb', 'UK-PRA-REPORT27': 'a225ee6ddebf47f56a221be46a52caa23f18e01d60831a8ac3b85f510f664437', 'UK-FCA-REPORT27': '2bd2c6052534799b5b1aef38d7dd150b104f1158bcc523179a2ec3be81252011', 'LBG-FSQS-ACCESS': '6f88b1689128d49898cecf171a026e00fe2c46aa44ce40928db910f4e98579b2', 'LBG-SOURCING-ACCESS': 'd0e32d6b4fca98d0234212d9d3ccd2fc5b8f9d08a22cbca0e06a94af616507eb'}

def restricted_metadata(item) -> bool:
    """Deny an explicit restriction; never grant source or canonical authority."""
    rights=item.get('rights',{})
    return bool(item.get('owner_only')is True or item.get('withdrawn')or item.get('retracted')
        or item.get('core_contradiction')or item.get('freshness')in {'stale','superseded','withdrawn'}
        or not isinstance(rights,dict)or rights.get('status')in {'revoked','denied','unknown'})


def claim_view(data, claim) -> Statement | None:
    """Existing validated public research adapter, not a new fact extractor."""
    # Presentation cannot turn a public owner's later restriction/revocation
    # into reusable core intelligence. Metadata collections are not booleans.
    if data.get('owner_only')is True or restricted_metadata(claim):return None
    kind=KINDS.get(claim.get('kind'))
    if not kind or claim.get('verification')!='source_supported' and kind!='insight':return None
    if any(c.get('supersedes')==claim['id']or c.get('updates')==claim['id']for c in data['claims']):return None
    source_by_id={s['id']:s for s in data['sources']}
    sources=[]
    for sid in claim['source_ids']:
        s=source_by_id[sid]
        if restricted_metadata(s):return None
        if 'search-index'in s.get('retrieval_extent',''):return None
        sources.append(Source(s['title'],s['url'],s.get('publisher',''),s.get('publication_date')or'',s.get('reporting_period',''),claim.get('primary_quotes',{}).get(sid,''),claim.get('quote_locator','')))
    # Curated adapter permits only a disclosure before a distinct research-task
    # sentence. It never strips adverse source evidence from the original quote.
    text=claim['statement']
    if hashlib.sha256(text.encode()).hexdigest()==DISCLOSURE_PINS.get(claim['id']):
        text=re.split(r'(?<=[.!])\s+',text,maxsplit=1)[0]
        if ';'in text:text=text.split(';',1)[0]+'.'
    state=('target'if 'target'in (claim.get('metric_unit')or'')else'expectation')if claim['kind']=='management_expectation'else'commitment'if claim['kind']in {'management_priority','management_commitment'}else'not_applicable'
    value=None
    if claim.get('metric_value')is not None:
        try:value=Decimal(str(claim['metric_value']))
        except InvalidOperation:return None
    scope=claim.get('entity_scope','').replace('legal-entity applicability must be confirmed','no specific legal entity is asserted')
    item=Statement(text,kind,scope,claim['reporting_period'],tuple(sources),
        'reviewed_excerpt'if claim['verification']=='source_supported'else'repository_interpretation',data['authority'],state,
        basis=claim.get('metric_unit')or'',value=value,unit=claim.get('metric_unit')or'',
        caveats=CAVEATS.get(claim['id'],()))
    if kind=='insight':item=replace(item,reasoning='Interpretation of the cited industry value system.',dependencies=(claim.get('repository_quote',''),),counter_evidence=CAVEATS.get(claim['id'],()))
    return item if eligible(item)else None


def editorial_force(item, key):
    if item is None or not is_editorial():return item
    if key=='economic':return replace(item,material_caveats=('Preliminary estimate; subject to revision.',))
    if key=='environmental':return replace(item,text=item.text.removeprefix('Reviewed '),period='Accounting periods from January 2027',material_caveats=('First reporting is in 2028. Listing-category scope and transitional relief apply.',))
    if key=='legal':return replace(item,period='Proposed legislation at 11 November 2026',material_caveats=('Parliamentary approval was not established at that date.',))
    if key=='LBG-ENVOY-CONTROLS':return replace(item,period='Company-announced platform',material_caveats=('Company-described controls; independent effectiveness is not established here.',))
    return item
