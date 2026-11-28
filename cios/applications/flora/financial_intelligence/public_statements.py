"""Read-only three-statement projection for Source-owned numerical facts."""
from collections import Counter
from datetime import date, datetime, timedelta
from typing import Literal

from pydantic import Field, model_validator

from .candidate_analytics import Measurement, calculate, stable_hash
from .. import intelligence_presentation as isp
from ..research_intelligence import source_import as source

StatementKind = Literal['income', 'balance', 'cash_flow', 'segment']


class Line(Measurement):
    statement: StatementKind
    fiscal_year: int = Field(ge=1900, le=9999)
    accounting_standard: str = ''
    reported_label: str = Field(min_length=1)
    sign_convention: str = Field(min_length=1)
    revision_state: Literal['original', 'restated', 'superseded'] = 'original'
    supersedes: str = ''

    @model_validator(mode='after')
    def statement_meaning(self):
        expected = 'instant' if self.statement == 'balance' else 'duration'
        if self.period.kind != expected:
            raise ValueError('Statement and period kind are incompatible')
        if (self.revision_state == 'restated') != bool(self.supersedes):
            raise ValueError('Restatements require an exact superseded revision')
        return self

    @model_validator(mode='after')
    def meaning(self):
        # Preserve F1 for currency; ratio support here is reported display only.
        if self.value.unit != 'percentage':
            return super().meaning()
        value = self.value
        boundary = self.period.as_at or self.period.end
        if (value.scale != 'units' or value.currency is not None or not value.amount.is_finite()
                or value.amount.as_tuple().exponent < -self.precision_dp
                or self.semantic_type != 'reported' or self.state not in {'actual','pro_forma'} or boundary > date.today()
                or boundary > datetime.fromisoformat(self.source.retrieved_at).date()):
            raise ValueError('Percentage requires a dated, reported actual and exact precision')
        return self


def _identity(line):
    return (line.subject_id, line.subject_name, line.perimeter, line.statement, line.metric,
            line.definition, line.accounting_standard, line.accounting_basis, line.sign_convention,
            line.state, line.value.unit, line.value.currency, line.value.scale)


def _period_key(line):
    return (line.period.kind, line.period.as_at, line.period.start, line.period.end,
            line.period.fiscal_year_end, line.fiscal_year)


def _check_history(lines):
    revisions = {line.source.revision: line for line in lines}
    if len(revisions) != len(lines) or len({line.measurement_id for line in lines}) != len(lines):
        raise ValueError('Duplicate financial revision')
    active = Counter((_identity(line), _period_key(line)) for line in lines if line.revision_state != 'superseded')
    if any(count != 1 for count in active.values()):
        raise ValueError('Conflicting active statement lines')
    references = Counter(line.supersedes for line in lines if line.supersedes)
    for line in lines:
        if line.revision_state == 'superseded' and references[line.source.revision] != 1:
            raise ValueError('Superseded line needs one explicit successor')
        if line.supersedes:
            old = revisions.get(line.supersedes)
            if (old is None or old.revision_state != 'superseded'
                    or (_identity(line), _period_key(line)) != (_identity(old), _period_key(old))):
                raise ValueError('Restatement scope or predecessor mismatch')
    return tuple(line for line in lines if line.revision_state != 'superseded')


def project(record, *, subject, url_validator=source.official_url, check_history=True):
    """Accept only trusted Source records selected by the caller, never URLs or runs.

    Source remains the owner of eligibility and applicable exceptions. This function exposes no HTTP request or record lookup.
    """
    try:
        rights = record['rights']
        if (record.get('authority') != 'analytical_working_research'
                or record.get('canonical_mutation') is not False
                or rights.get('basis') != 'ordinary_public_factual_analysis'):
            return ()
        if source.routine_factual_use(record, url_validator=url_validator) != 'minimal_factual_analysis':
            return ()
        bindings = source.minimal_factual_integrity(record, statement_periods=True)
        lines = []
        for binding in bindings:
            fields = dict(binding['facts'])
            if ((fields['subject_id'], fields['subject_name']) != subject
                    or fields.pop('semantic_type') != 'reported' or fields['state'] not in {'actual','pro_forma'}):
                return ()
            period = dict(fields.pop('period'))
            period['label'] = (period['as_at'] if period['kind'] == 'instant'
                               else period['start'] + ' to ' + period['end'])
            line = Line.model_validate({
                **fields, 'measurement_id': binding['key'], 'period': period, 'semantic_type': 'reported',
                'source': {'owner': 'source_import', 'record_id': binding['key'],
                           'revision': stable_hash(binding), 'source_id': record['id'],
                           'source_revision': stable_hash(record), 'url': rights['attribution_url'],
                           'title': record['title'], 'publisher': record['publisher'],
                           'locator': binding['locator'], 'published': record['publication_date'],
                           'retrieved_at': record['retrieved_at'], 'use_reference': rights['basis']},
            })
            lines.append(line)
        if check_history:
            _check_history(lines)
        return tuple(lines)
    except (OSError, ValueError, KeyError, TypeError, PermissionError, ArithmeticError, AttributeError):
        return ()


def nationwide_lines(projection):
    """Adapt the already eligible AUTH-2 output without changing its selections."""
    metrics = {'total_income', 'operating_costs', 'credit_impairment',
               'underlying_profit_before_tax', 'profit_before_tax'}
    return tuple(Line.model_validate({
        **row, 'statement': 'income', 'reported_label': row['definition'].split(';', 1)[0],
        'fiscal_year': int(row['period']['end'][:4]), 'sign_convention': 'Source-reported sign',
    }) for row in projection['measurements'] if row['metric'] in metrics)


def compare(lines, spec):
    """Reuse F1 arithmetic only for compatible current monetary lines."""
    current = _check_history(lines)
    selected = [line for line in current if line.measurement_id in {ref.measurement_id for ref in spec.inputs}]
    if len(selected) != 2 or _identity(selected[0]) != _identity(selected[1]):
        raise ValueError('Comparison requires two compatible current statement lines')
    legacy = [Measurement.model_validate(line.model_dump(include=set(Measurement.model_fields))) for line in selected]
    # F1 validates its own revisions; the public result identifies statement revisions.
    refs = {line.measurement_id: line for line in selected}
    by_id = {line.measurement_id: line for line in legacy}
    if any(ref.revision != refs[ref.measurement_id].revision for ref in spec.inputs):
        raise ValueError('Statement comparison revision mismatch')
    typed_spec = spec.model_copy(update={'inputs': tuple(
        ref.model_copy(update={'revision': by_id[ref.measurement_id].revision}) for ref in spec.inputs)})
    result = calculate(typed_spec, legacy)
    return {**result, 'inputs': [ref.model_dump() for ref in spec.inputs]}


def statements(lines):
    """Convert eligible read-model lines to the existing presentation semantics."""
    for line in _check_history(lines):
        period = line.period.label
        basis = ' · '.join(filter(None, (line.accounting_standard, line.accounting_basis)))
        reference = line.source
        fact = isp.Statement(
            line.reported_label, 'reported', line.subject_name + ' · ' + line.perimeter, period,
            (isp.Source(reference.title, reference.url, reference.publisher, str(reference.published or ''),
                        locator=reference.locator),), 'reported_source', 'analytical_working_research',
            line.state, basis=basis, value=line.value.amount,
            unit='%' if line.value.unit == 'percentage' else line.value.currency + ' ' + line.value.scale,
            caveats=(line.sign_convention,))
        if isp.eligible(fact):
            yield line, fact


def annual_details(selection):
    """Read through the finite Source owner for every current public render."""
    try:
        record, subject = source.public_statement_record(selection)
        return project(record, subject=subject)
    except (OSError, KeyError, TypeError, ValueError, PermissionError):
        return ()


def statement_history(subject, *, catalogue=None):
    """Return all eligible revisions, including repeated published comparatives."""
    from ..research_intelligence.statement_sources import records

    try:
        return tuple(line for record, validate in records(subject, catalogue=catalogue)
                     for line in project(record, subject=subject, url_validator=validate,
                                         check_history=False))
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return ()


def statement_series(subject, *, catalogue=None):
    """Select current views while preserving earlier publications in history."""
    history = statement_history(subject, catalogue=catalogue)
    referenced = {line.supersedes for line in history if line.supersedes}
    # If a source is withdrawn, suppress an orphaned successor or predecessor.
    revisions = {line.source.revision for line in history}
    groups = {}
    for line in history:
        if line.revision_state == 'superseded' and line.source.revision not in referenced:
            continue
        if line.supersedes and line.supersedes not in revisions:
            continue
        groups.setdefault((_identity(line), _period_key(line)), []).append(line)
    selected = []
    for group in groups.values():
        if any(line.revision_state != 'original' for line in group):
            try:
                _check_history(group)
            except ValueError:
                continue
            selected.extend(group)
        elif len({(line.value.amount, line.precision_dp, line.rounding) for line in group}) == 1:
            selected.append(max(group, key=lambda line: (line.source.published, line.source.source_id)))
        # Divergent original reports require an explicit correction chain.
    try:
        _check_history(selected)
    except ValueError:
        return ()
    return tuple(selected)


def annual_growth(lines, metrics):
    """Calculate adjacent, originally paired fiscal years through F1."""
    from .candidate_analytics import Derivation, InputReference

    current = _check_history(lines)
    for metric in metrics:
        group = sorted((line for line in current if line.metric == metric and line.statement == 'income'
                        and line.value.unit == 'currency'), key=lambda line: line.period.end)
        if len(group) < 2:
            continue
        pair = group[-2:]
        spec = Derivation(derivation_id=metric + '-annual-growth', formula='percent_change',
                          comparison='duration_dates', inputs=tuple(
                              InputReference(measurement_id=line.measurement_id, revision=line.revision)
                              for line in pair))
        try:
            yield pair[1].reported_label, compare(lines, spec)
        except ValueError:
            continue


def balance_changes(lines, keys):
    """Project scoped, revision-bound changes between eligible stock dates."""
    from .candidate_analytics import Derivation, InputReference

    current = _check_history(lines)
    result = []
    for key in keys:
        pair = sorted((line for line in current if line.metric == key
                       and line.statement == 'balance' and line.value.unit == 'currency'),
                      key=lambda line: line.period.as_at)
        if len(pair) < 2:
            continue
        pair = pair[-2:]
        spec = Derivation(derivation_id=key + '-balance-change', formula='difference', comparison='stock_dates',
                          inputs=tuple(InputReference(measurement_id=line.measurement_id, revision=line.revision)
                                       for line in pair))
        try:
            result.append((pair[1].reported_label, compare(lines, spec)))
        except ValueError:
            continue
    return tuple(result)


def economic_projection(selection):
    """Read-only reusable economics over current Source-owned statement lines.

    Existing Financial arithmetic supplies revision-bound comparisons/bridges.
    No run enumeration, persistence, publication permission or canonical write.
    """
    from .candidate_analytics import Derivation, InputReference, Reconciliation, reconcile
    try:
        record, subject = source.public_statement_record(selection)
        lines = project(record, subject=subject)
        if not lines:
            return {}
        by_id = {line.measurement_id:line for line in lines}
        comparisons = {}
        for row in record.get('comparisons', ()):
            try:
                pair = [by_id[row[k]] for k in ('opening','closing')]
                spec = Derivation(derivation_id=row['id'],formula=row['formula'],comparison=row['comparison'],
                    inputs=tuple(InputReference(measurement_id=x.measurement_id,revision=x.revision) for x in pair))
                comparisons[row['id']] = compare(lines,spec)
            except (ValueError,KeyError,TypeError,ArithmeticError):
                continue
        bridges = {}
        monetary = [Measurement.model_validate(x.model_dump(include=set(Measurement.model_fields)))
                    for x in lines if x.value.unit=='currency']
        amounts = {x.measurement_id:x for x in monetary}
        for row in record.get('bridges', ()):
            try:
                def ref(key):
                    x=amounts[key]
                    return InputReference(measurement_id=x.measurement_id,revision=x.revision)
                spec = Reconciliation(derivation_id=row['id'],mode=row['mode'],
                    opening=ref(row['opening']),endpoint=ref(row['endpoint']),
                    adjustments=tuple(ref(k) for k in row['adjustments']),
                    adjustment_roles=tuple(row.get('adjustment_roles',())),
                    opening_basis=row['opening_basis'],adjustment_basis=row['adjustment_basis'],endpoint_basis=row['endpoint_basis'])
                bridges[row['id']]=reconcile(spec,monetary)
            except (ValueError,KeyError,TypeError,ArithmeticError):
                continue
        return {'lines':lines,'comparisons':comparisons,'bridges':bridges,
                'source_revision':stable_hash(record),'source_id':record['id'],
                'authority':'analytical_working_research','canonical_mutation':False}
    except (OSError,ValueError,KeyError,TypeError,PermissionError,ArithmeticError):
        return {}


def comparable_durations(current, prior):
    """Match the scope, measurement, basis, units and calendar coverage of actual flows."""
    if not current or not prior or len(current) != len(prior):
        return False
    return all(
        _identity(now) == _identity(then)
        and now.state == then.state == 'actual'
        and now.period.kind == then.period.kind == 'duration'
        and (now.period.start.month, now.period.start.day, now.period.end.month, now.period.end.day)
        == (then.period.start.month, then.period.start.day, then.period.end.month, then.period.end.day)
        and now.precision_dp == then.precision_dp
        for now, then in zip(current, prior)
    )


def reconciled_subperiods(first, second, total):
    """Verify a signed additive duration over adjoining actual periods."""
    return (
        first.value.unit == 'currency'
        and first.statement in {'income', 'cash_flow'}
        and _identity(first) == _identity(second) == _identity(total)
        and first.state == second.state == total.state == 'actual'
        and first.period.kind == second.period.kind == total.period.kind == 'duration'
        and first.precision_dp == second.precision_dp == total.precision_dp
        and first.period.start == total.period.start
        and second.period.end == total.period.end
        and first.period.end + timedelta(days=1) == second.period.start
        and first.value.amount + second.value.amount == total.value.amount
    )
