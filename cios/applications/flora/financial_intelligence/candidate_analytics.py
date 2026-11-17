"""F1 typed working data in the existing Financial run owner.

No Evidence/Observation/Model writes or source grants. This adapter is opt-in:
only a permitted projection through the existing source owner supplies candidates.
Pure contracts below also support other industry adapters without issuer rules.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, UTC
from decimal import Decimal, localcontext
from html import escape
import json
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .schema import NumericFactValue
from .normalisation import normalise_scale, SCALE_FACTORS
from .. import intelligence_presentation as presentation
from ..security import verified_service_read, verified_service_write
from ..enterprise_intelligence.models import stable_hash

WORKFLOW = 'financial_candidate_analytics_v1'
SOURCE_FILE = 'F1-BOE-LPMZ598-Candidate.json'
SOURCE_PIN = 'e3e590854f31a4559e2bb75ded79fd2aad94b59de0adba336cd5d75d22805533'


class Contract(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)


class FinancialPeriod(Contract):
    kind: Literal['instant', 'duration']
    label: str = Field(min_length=1)
    as_at: date | None = None
    start: date | None = None
    end: date | None = None
    fiscal_year_end: str | None = None

    @model_validator(mode='after')
    def boundaries(self):
        if self.kind == 'instant':
            if self.as_at is None or self.start is not None or self.end is not None or self.fiscal_year_end is not None:
                raise ValueError('Stock requires only an explicit as-at date')
        elif (self.as_at is not None or self.start is None or self.end is None
              or self.start > self.end or not self.fiscal_year_end):
            raise ValueError('Flow requires explicit start/end and issuer fiscal year end')
        if self.fiscal_year_end:
            date.fromisoformat('2000-' + self.fiscal_year_end)
        return self


class SourceReference(Contract):
    owner: str = Field(min_length=1)
    record_id: str = Field(min_length=1)
    revision: str = Field(pattern=r'^[a-f0-9]{64}$')
    source_id: str = Field(min_length=1)
    source_revision: str = Field(pattern=r'^[a-f0-9]{64}$')
    url: str = Field(min_length=1)
    title: str = Field(min_length=1)
    publisher: str = Field(min_length=1)
    locator: str = Field(min_length=1)
    published: date | None = None
    retrieved_at: str = Field(min_length=1)
    use_reference: str = Field(min_length=1)

    @model_validator(mode='after')
    def chronology(self):
        retrieved = datetime.fromisoformat(self.retrieved_at.replace('Z', '+00:00'))
        url = urlsplit(self.url)
        if url.scheme != 'https' or not url.hostname or url.username or url.password:
            raise ValueError('Invalid source locator URL')
        if (retrieved.tzinfo is None or retrieved > datetime.now(UTC)
                or (self.published and self.published > retrieved.date())):
            raise ValueError('Invalid source chronology')
        return self


class Measurement(Contract):
    schema_version: Literal[1] = 1
    measurement_id: str = Field(min_length=1)
    subject_id: str = Field(min_length=1)
    subject_name: str = Field(min_length=1)
    perimeter: str = Field(min_length=1)
    metric: str = Field(min_length=1)
    definition: str = Field(min_length=1)
    accounting_basis: str = Field(min_length=1)
    state: Literal['actual', 'target', 'guidance', 'forecast']
    period: FinancialPeriod
    value: NumericFactValue
    original_display: str = Field(min_length=1)
    precision_dp: int = Field(ge=0, le=12)
    rounding: Literal['reported_rounded', 'exact', 'unspecified']
    semantic_type: Literal['reported', 'estimated', 'assumed']
    source: SourceReference
    assumption_owner: str = ''
    assumption_version: str = ''
    caveats: tuple[str, ...] = ()

    @model_validator(mode='after')
    def meaning(self):
        v = self.value
        if (not v.amount.is_finite() or normalise_scale(v.scale) != v.scale
                or v.unit != 'currency' or not v.currency or len(v.currency) != 3
                or not v.currency.isalpha() or v.currency != v.currency.upper()):
            raise ValueError('Explicit finite currency value and canonical reported scale required')
        if v.amount.as_tuple().exponent < -self.precision_dp:
            raise ValueError('Value exceeds declared reported precision')
        if self.semantic_type in {'estimated', 'assumed'} and not (self.assumption_owner and self.assumption_version and self.caveats):
            raise ValueError('Assumption-dependent measurement needs owner/version and limitations')
        if self.state == 'actual' and (self.period.as_at or self.period.end) > date.today():
            raise ValueError('Actual cannot have a future reporting boundary')
        if (self.period.as_at or self.period.end) > datetime.fromisoformat(self.source.retrieved_at).date() and self.state == 'actual':
            raise ValueError('Actual reporting boundary follows source retrieval')
        return self

    @property
    def revision(self):
        return stable_hash(self.model_dump(mode='json'))

    @property
    def base_amount(self):
        return self.value.amount * SCALE_FACTORS[self.value.scale]


class InputReference(Contract):
    measurement_id: str
    revision: str = Field(pattern=r'^[a-f0-9]{64}$')


class Derivation(Contract):
    derivation_id: str = Field(min_length=1)
    formula: Literal['difference', 'percent_change']
    version: Literal['1'] = '1'
    comparison: Literal['same_period', 'stock_dates', 'duration_dates']
    inputs: tuple[InputReference, InputReference]
    # No arbitrary expression evaluation, annualisation, FX or peer ranking.


def calculate(spec: Derivation, measurements: list[Measurement]) -> dict:
    """Reproduce from exact input revisions; pure domain validation, not authority."""
    measurements = [Measurement.model_validate(m.model_dump(mode='json')) for m in measurements]
    by_id = {m.measurement_id: m for m in measurements}
    if len(by_id) != len(measurements):
        raise ValueError('Duplicate or conflicting measurement identity')
    selected = []
    for ref in spec.inputs:
        m = by_id.get(ref.measurement_id)
        if m is None or m.revision != ref.revision:
            raise ValueError('Input revision unavailable')
        selected.append(m)
    opening, closing = selected
    if opening.measurement_id == closing.measurement_id:
        raise ValueError('Distinct measurements required')
    for field in ('subject_id', 'subject_name', 'perimeter', 'metric', 'definition', 'accounting_basis', 'state'):
        if getattr(opening, field) != getattr(closing, field):
            raise ValueError('Incompatible financial ' + field)
    for field in ('unit', 'currency', 'scale'):
        if getattr(opening.value, field) != getattr(closing.value, field):
            raise ValueError('Incompatible financial ' + field)
    if spec.comparison == 'stock_dates':
        if (opening.period.kind != 'instant' or closing.period.kind != 'instant'
                or opening.period.as_at >= closing.period.as_at):
            raise ValueError('Ordered explicit stock dates required')
    elif spec.comparison == 'duration_dates':
        if opening.period.kind != 'duration' or closing.period.kind != 'duration':
            raise ValueError('Complete annual durations required')
        if opening.period.fiscal_year_end != closing.period.fiscal_year_end:
            raise ValueError('Different fiscal calendars')
        for m in selected:
            month, day = map(int, m.period.fiscal_year_end.split('-'))
            if (m.period.end != date(m.period.end.year, month, day)
                    or m.period.start != date(m.period.end.year-1, month, day)+timedelta(days=1)):
                raise ValueError('Complete calendar-aligned fiscal year required; no annualisation')
        if (opening.period.end >= closing.period.start
                or closing.period.end.year != opening.period.end.year+1):
            raise ValueError('Ordered adjacent complete fiscal years required')
        if ((opening.source.owner,opening.source.source_id,opening.source.source_revision)
                != (closing.source.owner,closing.source.source_id,closing.source.source_revision)):
            raise ValueError('Annual comparators require the same presented source version')
    elif opening.period.model_dump(exclude={'label'}) != closing.period.model_dump(exclude={'label'}):
        raise ValueError('Incompatible reporting periods')
    elif (opening.semantic_type == closing.semantic_type == 'reported'
          and opening.value.amount != closing.value.amount):
        raise ValueError('Conflicting reported measurements for the same period')
    with localcontext() as ctx:
        ctx.prec = 34
        # Reuse the existing Statement arithmetic after Financial compatibility
        # validation. A stock-date bridge deliberately describes both dates;
        # neither original stock is relabelled as a duration measurement.
        period = (str(opening.period.as_at) + ' to ' + str(closing.period.as_at) if spec.comparison == 'stock_dates'
                  else str(opening.period.start)+'/'+str(opening.period.end)+' to '+str(closing.period.start)+'/'+str(closing.period.end)
                  if spec.comparison == 'duration_dates' else opening.period.label)
        def statement(m):
            source = presentation.Source(m.source.title, m.source.url, m.source.publisher,
                str(m.source.published or ''), locator=m.source.locator)
            return presentation.Statement(m.metric, m.semantic_type, m.perimeter, period, (source,),
                'reviewed_excerpt', 'candidate_intelligence', measurement_state=m.state,
                basis=m.accounting_basis, value=m.value.amount, unit=m.value.currency + ' ' + m.value.scale,
                caveats=m.caveats, method='Source estimate' if m.semantic_type == 'estimated' else '',
                assumption_owner=m.assumption_owner, assumption_version=m.assumption_version)
        amount = presentation.difference(statement(closing), statement(opening), text='Difference of compatible measurements').value
        if spec.formula == 'percent_change':
            if opening.value.amount <= 0:
                raise ValueError('Positive opening denominator required')
            amount = amount / opening.value.amount * Decimal(100)
    weaker = any(m.semantic_type != 'reported' for m in selected)
    return {'derivation_id': spec.derivation_id, 'value': str(amount),
            **({'comparison':'duration_dates'} if spec.comparison=='duration_dates' else {}),
            'formula': spec.formula,
            'unit': '%' if spec.formula == 'percent_change' else opening.value.currency + ' ' + opening.value.scale,
            'semantic_type': 'estimated' if weaker else 'calculated',
            'canonical_status': 'derived_view_not_canonical',
            'measurement_state': opening.state,
            'periods': [m.period.model_dump(mode='json') for m in selected],
            'method': '(closing - opening) / opening × 100' if spec.formula == 'percent_change' else 'closing - opening',
            'formula_version': spec.version, 'inputs': [r.model_dump() for r in spec.inputs],
            'dependency_types': [m.semantic_type for m in selected],
            'assumptions': [{'owner': m.assumption_owner, 'version': m.assumption_version} for m in selected if m.semantic_type != 'reported'],
            'caveats': list(dict.fromkeys(c for m in selected for c in m.caveats))}


@dataclass(frozen=True)
class InputBundle:
    resource_id: str
    title: str
    measurements: tuple[Measurement, ...]
    source: dict
    reconciliations: tuple[dict, ...] = ()
    insights: tuple[dict, ...] = ()


class Reconciliation(Contract):
    """Finite source-disclosed signed bridge, not an expression language.

    F2 exercises this with explicitly synthetic data only. A real adapter would
    need its own eligible source/use and pinned recipe, never a request flag.
    """
    derivation_id: str = Field(min_length=1)
    formula: Literal['signed_bridge'] = 'signed_bridge'
    version: Literal['1'] = '1'
    mode: Literal['basis_reconciliation', 'reported_statement'] = 'basis_reconciliation'
    adjustment_roles: tuple[Literal['operating_costs', 'credit_impairment', 'associate_contribution', 'restructuring_provisions'], ...] = ()
    opening: InputReference
    adjustments: tuple[InputReference, ...] = Field(min_length=1, max_length=10)
    endpoint: InputReference
    opening_basis: str = Field(min_length=1)
    adjustment_basis: str = Field(min_length=1)
    endpoint_basis: str = Field(min_length=1)
    precision_rule: Literal['exact_reported_precision'] = 'exact_reported_precision'


def reconcile(spec: Reconciliation, measurements: list[Measurement]) -> dict:
    """Validate one explicit bridge against its separately reported endpoint.

    Existing difference guards are unchanged. No residual is invented, no
    absolute/sign convention inferred, no rounding tolerance auto-plugged.
    This pure Financial-owner operation supplies neither source-use authority
    nor permission to persist/promote any result.
    """
    by_id = {m.measurement_id: Measurement.model_validate(m.model_dump(mode='json')) for m in measurements}
    if len(by_id) != len(measurements):
        raise ValueError('Duplicate measurement identity')
    refs = (spec.opening, *spec.adjustments, spec.endpoint)
    if len({ref.measurement_id for ref in refs}) != len(refs):
        raise ValueError('Each bridge component must be applied exactly once')
    rows = []
    for ref in refs:
        m = by_id.get(ref.measurement_id)
        if m is None or m.revision != ref.revision:
            raise ValueError('Bridge input revision unavailable')
        rows.append(m)
    opening, endpoint = rows[0], rows[-1]
    if opening.period.kind != 'duration':
        raise ValueError('Explicit duration required')
    if spec.mode=='basis_reconciliation':
        if spec.opening_basis==spec.endpoint_basis or spec.adjustment_roles:
            raise ValueError('Different endpoint bases required for basis reconciliation')
    else:
        if not spec.opening_basis==spec.adjustment_basis==spec.endpoint_basis:
            raise ValueError('Reported statement requires the same declared accounting basis')
        roles={'operating_costs','credit_impairment','associate_contribution','restructuring_provisions'}
        if (len(spec.adjustment_roles)!=len(spec.adjustments)
                or len(set(spec.adjustment_roles))!=len(spec.adjustment_roles)
                or not set(spec.adjustment_roles).issubset(roles)
                or opening.metric not in {'revenue','total_income','net_operating_income'}
                or endpoint.metric not in {'profit_before_tax','underlying_profit_before_tax','operating_profit_before_tax'}
                or endpoint.semantic_type!='reported'
                or any(m.metric!=role for m,role in zip(rows[1:-1],spec.adjustment_roles))):
            raise ValueError('Explicit unique signed statement roles and separately reported pretax endpoint required')
    for m in rows:
        if (any(getattr(m, field) != getattr(opening, field) for field in ('subject_id','subject_name','perimeter','state'))
                or m.period.model_dump(exclude={'label'}) != opening.period.model_dump(exclude={'label'})
                or any(getattr(m.value, field) != getattr(opening.value, field) for field in ('unit','currency','scale'))
                or (m.source.owner,m.source.source_id,m.source.source_revision) !=
                   (opening.source.owner,opening.source.source_id,opening.source.source_revision)):
            raise ValueError('Incompatible bridge subject, period, unit, state or document version')
    if (opening.accounting_basis != spec.opening_basis or endpoint.accounting_basis != spec.endpoint_basis
            or any(m.accounting_basis != spec.adjustment_basis for m in rows[1:-1])):
        raise ValueError('Bridge basis transition is not the declared source reconciliation')
    with localcontext() as ctx:
        ctx.prec = 34
        amount = sum((m.value.amount for m in rows[:-1]), Decimal(0))
    if amount != endpoint.value.amount:
        raise ValueError('Bridge does not reconcile at reported precision; no residual allowed')
    return {'derivation_id':spec.derivation_id,'value':str(amount),
            'formula':spec.formula,
            'unit':opening.value.currency+' '+opening.value.scale,
            'semantic_type':'estimated' if any(m.semantic_type != 'reported' for m in rows) else 'calculated',
            'canonical_status':'derived_view_not_canonical','measurement_state':opening.state,
            'basis':spec.endpoint_basis,'method':'Opening amount + explicitly signed adjustments; exact check to separately reported endpoint',
            'formula_version':spec.version,'precision_rule':spec.precision_rule,
            'inputs':[ref.model_dump() for ref in refs],
            'periods':[m.period.model_dump(mode='json') for m in rows],
            'dependency_types':[m.semantic_type for m in rows],
            'assumptions':[{'owner':m.assumption_owner,'version':m.assumption_version} for m in rows if m.semantic_type != 'reported'],
            'caveats':list(dict.fromkeys(c for m in rows for c in m.caveats))}


def permitted_selection_keys() -> tuple[str, ...]:
    """Existing source-owner choices; no new registry or run discovery."""
    from ..research_intelligence.source_import import working_facts, bound_facts, working_restricted
    try:
        data, sources = working_facts()
        keys = tuple(row['key'] for row in data['financial_selections'] if row['source_id'] in sources)
    except (OSError, ValueError, TypeError, KeyError, PermissionError):
        keys = ()
    return ('boe-household-deposit-stocks', *keys)


def _current_inputs(selection: str) -> InputBundle:
    if selection == 'boe-household-deposit-stocks':
        return _boe_inputs(selection)
    from ..research_intelligence.source_import import working_facts, bound_facts, working_restricted
    from ..research_intelligence import model
    data, sources = working_facts()
    matches = [r for r in data['financial_selections'] if r['key'] == selection]
    row = matches[0] if len(matches) == 1 else None
    if not row or row['source_id'] not in sources:
        raise PermissionError('Financial source-use exception')
    if working_restricted(row):
        raise PermissionError('Restricted research row')
    source = sources[row['source_id']]
    ms = tuple(Measurement.model_validate(m) for m in row['measurements'])
    model.primary_text(source)
    subject = source['reported_subject']
    if (not 1 <= len(ms) <= 48 or row['resource_ref'] != 'BK-IND-002'
            or len({m.measurement_id for m in ms}) != len(ms)
            or any(m.source.source_id != source['id'] or m.source.source_revision != stable_hash(source)
                   or m.source.record_id != m.measurement_id
                   or m.source.revision != stable_hash(bound_facts(source, m.measurement_id, 'financial_measurement'))
                   or m.source.url != source['url'] or m.source.publisher != source['publisher']
                   or str(m.source.published) != source['publication_date']
                   or m.source.retrieved_at != source['retrieved_at']
                   or any(m.model_dump(mode='json')[field] != value for field, value in bound_facts(source, m.measurement_id, 'financial_measurement').items())
                   or (m.subject_id, m.subject_name, m.perimeter) != (subject['id'], subject['name'], subject['perimeter'])
                   or (str(m.period.start), str(m.period.end)) != (subject['start'], subject['end'])
                   or m.value.currency != subject['currency'] or m.value.scale != subject['scale']
                   or m.accounting_basis not in subject['bases'] for m in ms)):
        raise ValueError('Financial source/measurement identity mismatch')
    recipes = tuple(Reconciliation.model_validate(r).model_dump(mode='json') for r in row['reconciliations'])
    for recipe in recipes:
        reconcile(Reconciliation.model_validate(recipe), list(ms))
    return InputBundle(row['resource_ref'], row['title'], ms, source, recipes, tuple(i for i in row['insights'] if not working_restricted(i)))


def _boe_inputs(selection: str) -> InputBundle:
    """Narrow adapter over existing Source snapshot contracts and publisher policy.

    Never caller-supplied rights, copied source files, URL acquisition or a new
    source registry. All other sources/adapters remain closed in F1.
    """
    from ..research_intelligence import model
    from ..research_intelligence.registry import snapshot_boundary
    if selection != 'boe-household-deposit-stocks':
        raise PermissionError('No source-use decision for this financial analysis')
    path = snapshot_boundary('banking', model.REPO) / SOURCE_FILE
    if path.is_symlink():
        raise PermissionError('Source unavailable')
    package = json.loads(path.read_text())
    if (stable_hash(package) != SOURCE_PIN
            or package.get('authority') != 'candidate_intelligence'
            or package.get('canonical_mutation') is not False
            or presentation.restricted_metadata(package)
            or not date(2026, 11, 16) <= date.today() <= date.fromisoformat(package['review_until'])):
        raise PermissionError('Source unavailable')
    source = package['source']
    if (presentation.restricted_metadata(source)
            or source.get('rights', {}).get('status') != 'permitted_numerical_data'
            or source['rights'].get('purpose') != 'Attributed financial analytical working data and reproducible numerical derivation'):
        raise PermissionError('Source use unavailable')
    model.primary_text(source)  # Original owner checks publisher, excerpt, digest and retrieval extent.
    definition = source['excerpts'][0]['quote']
    measurements = tuple(Measurement(measurement_id=c['id'], subject_id=package['subject_identity'],
        subject_name=package['subject_name'], perimeter='UK monetary financial institutions; sterling retail deposits from households; excluding notes and coin; NSA',
        metric='sterling_household_retail_deposits', definition=definition,
        accounting_basis='BoE Database LPMZ598; amounts outstanding; not seasonally adjusted', state='actual',
        period=FinancialPeriod(kind='instant', label=c['as_at'], as_at=c['as_at']),
        value=NumericFactValue(amount=c['amount'], currency='GBP', scale='millions', unit='currency'),
        original_display='£' + format(Decimal(c['amount']), ',') + 'm', precision_dp=0,
        rounding='reported_rounded', semantic_type='reported',
        source=SourceReference(owner='banking_research', record_id=c['id'], revision=stable_hash(c),
            source_id=source['id'], source_revision=stable_hash(source), locator=c['locator'],
            url=source['url'], title=source['title'], publisher=source['publisher'],
            published=source['publication_date'], retrieved_at=source['retrieved_at'],
            use_reference='Bank of England Database OGL numerical-data clause; F1 document-specific review'),
        caveats=('Historical UK MFI aggregate, not Lloyds, another named bank or the latest release. Not seasonally adjusted.',
                 'A difference of stocks is not the official adjusted flow or growth series; coverage and sector changes can affect it.',
                 'Reported in GBP millions. Calculations retain source rounding; no annualisation, causal inference or buying need.')) for c in package['claims'])
    return InputBundle(package['resource_ref'], 'UK household retail-deposit stocks', measurements, source)


def _derivations(measurements):
    refs = tuple(InputReference(measurement_id=m.measurement_id, revision=m.revision) for m in measurements)
    comparison = ('stock_dates' if all(m.period.kind == 'instant' for m in measurements)
                  else 'duration_dates' if all(m.period.kind=='duration' for m in measurements)
                  and len({(m.period.start,m.period.end) for m in measurements})>1 else 'same_period')
    return [Derivation(derivation_id=name, formula=formula, comparison=comparison, inputs=refs)
            for name, formula in (('published-stock-difference', 'difference'), ('published-stock-percent-change', 'percent_change'))]


def _run_record(selection: str, bundle: InputBundle, workspace: str) -> dict:
    """One v1 identity builder shared by creation and read-only lookup.

    The original F1 payload and run ID stay byte-compatible. No source/run
    creation, authority or persistence is supplied by this pure helper.
    """
    measurements = list(bundle.measurements)
    # Access resource is distinct from reported subject; no canonical identity
    # is invented for this statistical aggregate or equated to a named bank.
    enterprise = bundle.resource_id
    payload = {'schema_version': 1, 'selection': selection,
               'measurements': [m.model_dump(mode='json') for m in measurements],
               'derivations': [] if bundle.reconciliations else [d.model_dump(mode='json') for d in _derivations(measurements)]}
    if bundle.reconciliations:
        payload['reconciliations'] = list(bundle.reconciliations)
        payload['insights'] = list(bundle.insights)
    run_id = 'fi-f1-' + stable_hash({'workspace': workspace, 'enterprise': enterprise, 'payload': payload})[:32]
    run = {'run_id': run_id, 'workflow': WORKFLOW, 'workspace_id': workspace,
           'enterprise_id': enterprise, 'document': {'enterprise_id': enterprise, 'workspace_id': workspace},
           'status': 'candidate_analytics', 'terminal': True, 'current_stage': 'complete',
           'claims': [], 'analytical_candidate': payload,
           'canonical_update': {'enterprise_model_updated': False, 'observations_created': 0}}
    return run


def public_nationwide_projection() -> dict:
    """Finite public Source facts, never private Financial runs or metadata.

    AUTH-2 changes product audience, not publisher permission. Reuse the existing
    isolated factual-use method, source lifecycle, exact bindings and arithmetic.
    No run path, lookup, workspace, storage, identity or provider is consulted.
    """
    from ..research_intelligence.source_import import routine_factual_use
    try:
        bundle = _current_inputs('nationwide-fy2026')
        if routine_factual_use(bundle.source) != 'minimal_factual_analysis':
            return {}
        if (bundle.source['id'] != 'RUD1-NATIONWIDE-FY26' or len(bundle.measurements) != 8
                or any(m.subject_name != 'Nationwide Building Society Group' for m in bundle.measurements)):
            return {}
        measurements = list(bundle.measurements)
        results = [reconcile(Reconciliation.model_validate(r), measurements) for r in bundle.reconciliations]
        # Projection contains only the same Source-owned factual slice. No
        # private run identity, annotation, availability, tenant or overrides.
        return {'title': bundle.title, 'measurements': [m.model_dump(mode='json') for m in measurements],
                'results': results, 'insights': list(bundle.insights),
                'sources': [{'title': bundle.source['title'], 'url': bundle.source['url'],
                             'published': bundle.source['publication_date']}]}
    except (OSError, ValueError, KeyError, TypeError, PermissionError):
        return {}


@verified_service_read('package.inspect')
def find_existing_run(selection: str, resource_id: str, *, headers=None) -> str | None:
    """Resolve only the current known ID in one authorised scope; never scan.

    A missing/old-version/withdrawn/denied run creates no entry. This is a read
    service: package.upload is not required and no missing run is generated.
    """
    from .. import document_review as review
    from ..access import require_resource_scope, active_flora_workspace
    workspace = active_flora_workspace(headers)
    require_resource_scope(headers, 'package.inspect', resource_id, workspace)
    try:
        bundle = _current_inputs(selection)
        if bundle.resource_id != resource_id:
            return None
        run_id = _run_record(selection, bundle, workspace)['run_id']
        if not review._run_path(run_id).is_file():
            return None
        return run_id if read_analysis(run_id, headers=headers) else None
    except (OSError, ValueError, TypeError, KeyError, PermissionError):
        return None


@verified_service_write('package.upload')
def create_run(selection: str, *, headers=None) -> str:
    """Opt-in trusted service; actual existing Financial repository, no promotion."""
    from .. import document_review as review
    from ..access import require_resource_scope, active_flora_workspace
    from ..storage import atomic_write_json
    bundle = _current_inputs(selection)
    enterprise = bundle.resource_id
    workspace = active_flora_workspace(headers)
    require_resource_scope(headers, 'package.upload', enterprise, workspace)
    run = _run_record(selection, bundle, workspace)
    run_id = run['run_id']
    path = review._run_path(run_id)
    if path.exists():
        if review.load_run(run_id) != run:
            raise ValueError('Existing run differs; immutable candidate revision required')
    else:
        atomic_write_json(path, run)
    if _current_inputs(selection) != bundle:
        raise PermissionError('Source changed during candidate persistence')
    require_resource_scope(headers, 'package.upload', enterprise, workspace)
    return run_id


def current_projection(run: dict) -> dict:
    """Internal projection after Financial IAM; revalidate original owners at use.

    No result cache/export exists. Returned values are recomputed, never trusted
    from a persisted result. On any source/version/use change, no title, link,
    input, amount or derivation is returned; lawful run history stays internal.
    """
    try:
        payload = run['analytical_candidate']
        if payload['schema_version'] != 1 or run['claims']:
            raise ValueError('Unsupported candidate payload')
        bundle = _current_inputs(payload['selection'])
        current = list(bundle.measurements)
        stored = [Measurement.model_validate(m) for m in payload['measurements']]
        if current != stored or bundle.resource_id != run['enterprise_id']:
            raise ValueError('Source or measurement revision unavailable')
        specs = [Derivation.model_validate(d) for d in payload['derivations']]
        bridges = [Reconciliation.model_validate(r) for r in payload.get('reconciliations', [])]
        if (payload != _run_record(payload['selection'], bundle, run['workspace_id'])['analytical_candidate']
                or specs != ([] if bundle.reconciliations else _derivations(stored))):
            raise ValueError('Unrecognised analytical recipe')
        source = bundle.source
        return {'title': bundle.title,
                'measurements': [m.model_dump(mode='json') for m in stored],
                'results': [calculate(d, stored) for d in specs] + [reconcile(r, stored) for r in bridges],
                **({'insights': list(bundle.insights)} if bundle.insights else {}),
                'sources': [{'title': source['title'], 'url': source['url'],
                             'published': source.get('publication_date') or '',
                             'retrieved_at': source['retrieved_at'],
                             'extent': source['retrieval_extent'],
                             'period': source['reporting_period'],
                             'locator': '; '.join(dict.fromkeys(m.source.locator for m in stored)),
                             'attribution': source['rights']['attribution'],
                             'licence_url': source['rights']['licence_url']}]}
    except (OSError, ValueError, KeyError, TypeError, PermissionError):
        return {}


@verified_service_read('package.inspect')
def read_analysis(run_id: str, *, headers=None) -> dict:
    from .. import document_review as review
    from ..access import require_financial_run_authority
    run = review.load_run(run_id)
    require_financial_run_authority(headers, 'package.inspect', run)
    if run.get('workflow') != WORKFLOW:
        raise ValueError('Not a typed analytical run')
    return current_projection(run)


def _render_projection(projection: dict) -> str:
    if not projection:
        return '<section class="card"><h1>Financial analysis unavailable</h1></section>'
    if any(r['formula'] == 'signed_bridge' for r in projection['results']):
        from .analyst import compose, STYLE
        return STYLE + compose(projection)
    stocks = all(m['period']['kind'] == 'instant' for m in projection['measurements'])
    rows = ''.join('<tr><td>' + presentation.LABELS[m['semantic_type']] + '</td><th scope="row">' + escape(m['original_display']) + '</th><td>' +
                   escape(m['period']['as_at'] or (m['period']['start'] + ' to ' + m['period']['end'])) + '</td></tr>' for m in projection['measurements'])
    cards = ''
    for result in projection['results']:
        number = Decimal(result['value'])
        display = format(number, '.4f') + '%' if result['unit'] == '%' else format(number, ',') + ' ' + result['unit']
        label = ('Change in published stocks' if result['unit'] == '%' else 'Difference in published stocks') if stocks else ('Percentage difference' if result['unit'] == '%' else 'Difference between measurements')
        state = '' if result['measurement_state'] == 'actual' else ' · ' + result['measurement_state'].title()
        cards += '<p><small>' + presentation.LABELS[result['semantic_type']] + state + '</small> · ' + label + ' <strong>' + display + '</strong></p>'
    sources = ''.join('<li><a href="' + escape(s['url'], quote=True) + '">' + escape(s['title']) + '</a> · ' + escape(s['locator']) + '<p>Historical snapshot retrieved ' + escape(s['retrieved_at'][:10]) + '. Two reviewed database rows; original publication day and release vintage are not established. Original document bytes are not archived.</p><p>' + escape(s['attribution']) + ' <a href="' + escape(s['licence_url'], quote=True) + '">Licence</a></p></li>' for s in projection['sources'])
    return ('<style>.f1-result table{width:100%;table-layout:fixed}.f1-result th,.f1-result td{overflow-wrap:anywhere}'
            '@media(max-width:40rem){body:has(.f1-result) .product-header{display:block}'
            'body:has(.f1-result) .product-header nav{display:flex;flex-wrap:wrap;width:100%;min-width:0;margin-top:.5rem}'
            'body:has(.f1-result) .product-header summary{white-space:normal;overflow-wrap:anywhere}'
            '.f1-result table,.f1-result tbody{display:block}.f1-result thead{position:absolute;width:1px;height:1px;clip-path:inset(50%);overflow:hidden}'
            '.f1-result tr{display:grid;grid-template-columns:minmax(0,1fr);gap:.3rem;padding:1rem 0;border-bottom:1px solid #ded8ce}'
            '.f1-result tr>*{padding:0;border:0;overflow-wrap:normal;white-space:nowrap}.f1-result td:first-child{font-size:.85rem}}</style>'
            '<section class="hero"><h1>' + escape(projection['title']) + '</h1>'
            '<p>' + escape(projection['measurements'][0]['perimeter']) + '</p></section>'
            '<section class="card f1-result"><table><caption>Financial measurements</caption><thead><tr><th>Type</th><th>Amount</th><th>' + ('As at' if stocks else 'Period') + '</th></tr></thead><tbody>' + rows + '</tbody></table>' + cards +
            ('<p>Comparison of published stocks; composition is not adjusted.</p>' if stocks else '<p>Same reporting period; retains stated assumptions.</p>') +
            '<details><summary>Sources and calculation</summary><p>Analytical working view; no Enterprise record has been updated. Reported values and calculated results are separate from governed record acceptance.</p><ul>' + sources + '</ul><p>(closing − opening) ÷ opening × 100. No annualisation or consolidation adjustment.</p><p>' +
            escape(' '.join(projection['results'][0]['caveats'])) + '</p></details></section>')


@verified_service_read('package.inspect')
def render_run(run_id: str, *, headers=None) -> str:
    return _render_projection(read_analysis(run_id, headers=headers))


@verified_service_write('package.upload')
def refresh_research(*, headers=None):
    """Routine authorised working-data refresh, not an evidence approval.

    No source/metric parameters, external calls or canonical hand-off. Existing
    per-run workspace/resource authority and immutable persistence do the work.
    Exceptions are isolated; a failed source never admits a different source.
    """
    from ..access import active_flora_workspace, require_resource_scope
    workspace = active_flora_workspace(headers)
    require_resource_scope(headers, 'package.upload', 'BK-IND-002', workspace)
    from .. import document_review as review
    # Pure preflight isolates ordinary source/row/storage exceptions BEFORE any
    # nested verified writer. An unexpected write-time race still fails the
    # enclosing journal atomically; never swallow a poisoned transaction.
    selections = []
    for key in permitted_selection_keys():
        try:
            bundle = _current_inputs(key)
            require_resource_scope(headers, 'package.upload', bundle.resource_id, workspace)
            expected = _run_record(key, bundle, workspace)
            path = review._run_path(expected['run_id'])
            if path.exists() and review.load_run(expected['run_id']) != expected:
                continue
            selections.append(key)
        except (PermissionError, ValueError, OSError, KeyError, TypeError):
            continue
    return tuple(create_run(key, headers=headers) for key in selections)
