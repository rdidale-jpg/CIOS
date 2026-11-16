"""Explicitly fictional contract examples. Never admitted runtime research."""
from decimal import Decimal

from cios.applications.flora.financial_intelligence import candidate_analytics as f
from cios.applications.flora.enterprise_intelligence.models import stable_hash


def measurement(case, key, amount, *, basis='statutory', kind='reported', metric=None):
    source = f.SourceReference(owner='synthetic-nonproduction-fixture',record_id=case+'-'+key,
        revision=stable_hash([case,key]),source_id='synthetic-'+case,source_revision=stable_hash(case),
        url='https://example.invalid/synthetic-'+case,title='Synthetic contract fixture only',
        publisher='Fictional test source',locator=key,published='2026-11-15',
        retrieved_at='2026-11-16T00:00:00+00:00',use_reference='Test only; no source permission or issuer authority')
    return f.Measurement(measurement_id=case+'-'+key,subject_id='synthetic-'+case,
        subject_name='Synthetic '+case,perimeter='Fictional '+case+' entity; no real issuer',
        metric=metric or key,definition='Synthetic explicitly defined '+(metric or key),accounting_basis=basis,
        state='actual',period=f.FinancialPeriod(kind='duration',label='Synthetic H1 2026',
            start='2026-01-01',end='2026-06-30',fiscal_year_end='12-31'),
        value=f.NumericFactValue(amount=Decimal(amount),currency='GBP',scale='millions',unit='currency'),
        original_display='Synthetic GBP '+amount+'m',precision_dp=2,rounding='exact',semantic_type=kind,
        source=source,assumption_owner='synthetic-scenario-owner' if kind!='reported' else '',
        assumption_version='fixture-v1' if kind!='reported' else '',
        caveats=('Synthetic non-production figures; no company, customer demand or real source eligibility is claimed.',))


def reference(m): return f.InputReference(measurement_id=m.measurement_id,revision=m.revision)


def example(case):
    if case=='mutual-bridge':
        ms=[measurement(case,'underlying_profit','300',basis='underlying'),
            measurement(case,'signed_cost_adjustment','-80',basis='disclosed_bridge'),
            measurement(case,'signed_member_adjustment','-20',basis='disclosed_bridge'),
            measurement(case,'statutory_profit','200',basis='statutory')]
        recipe=f.Reconciliation(derivation_id='synthetic-mutual-bridge',opening=reference(ms[0]),
            adjustments=tuple(map(reference,ms[1:-1])),endpoint=reference(ms[-1]),
            opening_basis='underlying',adjustment_basis='disclosed_bridge',endpoint_basis='statutory')
        results=[f.reconcile(recipe,ms)]
    elif case in {'bank-income','technology','aviation'}:
        ms=[measurement(case,'income','500'),measurement(case,'signed_costs','-260'),
            measurement(case,'signed_impairments','-30'),measurement(case,'pretax_profit','210')]
        results=[]
    elif case=='technology-scenario':
        ms=[measurement(case,'case_a','100',kind='assumed',metric='operating_costs'),
            measurement(case,'case_b','95',kind='assumed',metric='operating_costs')]
        recipe=f.Derivation(derivation_id='synthetic-assumption-difference',formula='difference',comparison='same_period',
            inputs=tuple(map(reference,ms)))
        results=[f.calculate(recipe,ms)]
    else:
        raise ValueError('Unknown synthetic example')
    return {'title':'Synthetic '+case.replace('-',' ')+' — contract example only',
        'measurements':[m.model_dump(mode='json') for m in ms],'results':results,
        'sources':[{'title':'Synthetic non-production fixture','url':ms[0].source.url,'published':'2026-11-15',
            'retrieved_at':'2026-11-16T00:00:00+00:00','extent':'Fictional monetary test values, not research',
            'locator':'test fixture','attribution':'Synthetic only; no issuer authority.',
            'licence_url':'https://example.invalid/fixture-not-a-licence'}]}
