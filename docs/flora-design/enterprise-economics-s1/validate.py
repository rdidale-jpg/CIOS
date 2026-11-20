"""Design-scope, provenance, existing-contract and negative-case validation.

Pure read/calculation only: no runtime server, source import, persistence, rights
decision, canonical write or private Financial-run service is called.
"""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, UTC
from decimal import Decimal
import json
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = '03719d7573f087c65d9622719273aa4b89caf7d3'
PREFIX = 'docs/flora-design/enterprise-economics-s1/'
WORKFLOW = '.github/workflows/flora-enterprise-economics-design.yml'
sys.path.insert(0, str(ROOT))


def run():
    from cios.applications.flora.financial_intelligence import candidate_analytics as f
    from cios.applications.flora.research_intelligence import model
    checks = []

    def check(value, label):
        assert value, label
        checks.append(label)

    def git(*args):
        return subprocess.check_output(['git', *args], cwd=ROOT)

    names = set(git('diff', '--name-only', BASE).decode().splitlines())
    names.update(git('ls-files', '--others', '--exclude-standard').decode().splitlines())
    check(all(n.startswith(PREFIX) or n == WORKFLOW for n in names), 'Design-only diff; runtime/records/permissions/ADRs unchanged')
    check(git('merge-base', BASE, 'HEAD').decode().strip() == BASE, 'Branch starts from verified main')
    for n, entry in json.loads((HERE/'Artwork-Provenance.json').read_text())['assets'].items():
        original = (ROOT/entry['original']).read_bytes()
        copied = (HERE/'prototype/assets'/n).read_bytes()
        check(sha256(original).hexdigest() == entry['sha256'] == entry['copy_sha256'] == sha256(copied).hexdigest(), 'Unchanged artwork '+n)
    source_path = 'enterprise-knowledge/banking/research-model/source-snapshots/PFI-Lloyds-Q326.json'
    original = (ROOT/source_path).read_bytes()
    check(sha256(original).hexdigest() == 'd5d6c29d840502101991c166428af18e7a4b77b19b016f9bfe9707130a809775', 'Lloyds source/holds unchanged')
    check(f.public_factual_projection() == {} and f.public_factual_html() == '', 'Real Lloyds output remains inactive')
    for directory in ('cios', 'enterprise-knowledge', 'architecture', 'tests', 'tools'):
        check(not git('diff', BASE, '--', directory), 'No modification under '+directory)
    check(not git('diff', BASE, '--', 'render.yaml'), 'Render configuration unchanged')
    for doc in HERE.glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
            if target.startswith(('https://','http://','#')):
                continue
            check((doc.parent/target.split('#')[0]).exists(), 'Documentation/preview link '+doc.name+':'+target)

    data = json.loads((ROOT/'enterprise-knowledge/aviation/research-model/Assessment-Overlay.json').read_text())
    source = next(s for s in data['sources'] if s['id'] == 'SRC-AV-AR25')
    for identifier in ('AV-REVENUE', 'AV-PROFIT'):
        claim = next(c for c in data['claims'] if c['id'] == identifier)
        check(model.primary_claim_supported(data, claim), 'Existing primary lineage '+identifier)
    # The compound historical AV-PROFIT text is not adopted as a new full claim;
    # the design uses only its independently rechecked headline value.
    source_revision = f.stable_hash(source)
    def measurement(year, value):
        return f.Measurement(measurement_id='design-revenue-'+str(year),
            subject_id='research-subject:easyjet-plc-group', subject_name='easyJet plc consolidated Group',
            perimeter='Consolidated Group', metric='group_revenue', definition='Reported annual Group total revenue',
            accounting_basis='Annual report revenue; same FY2025 presented source version', state='actual',
            period=f.FinancialPeriod(kind='duration', label='FY'+str(year), start=f'{year-1}-10-01', end=f'{year}-09-30', fiscal_year_end='09-30'),
            value=f.NumericFactValue(amount=str(value), currency='GBP', scale='millions', unit='currency'),
            original_display=f'GBP {value} million', precision_dp=0, rounding='reported_rounded', semantic_type='reported',
            source=f.SourceReference(owner='aviation_research', record_id='design-revenue-'+str(year),
                revision=f.stable_hash({'year':year,'amount':str(value)}), source_id=source['id'],
                source_revision=source_revision, url=source['url'], title=source['title'], publisher=source['publisher'],
                locator='Printed p32 performance summary; comparative in FY2025 report', published=None,
                retrieved_at='2026-11-19T00:00:00+00:00', use_reference='Design-only factual illustration; no Source permission or runtime admission grant'),
            caveats=('Historical Group revenue; not capability allocation or current trading.',))
    ms = [measurement(2024,9309), measurement(2025,10106)]
    def recipe(values):
        return f.Derivation(derivation_id='design-only-annual-growth', formula='percent_change', comparison='duration_dates',
            inputs=tuple(f.InputReference(measurement_id=m.measurement_id, revision=m.revision) for m in values))
    result = f.calculate(recipe(ms), ms)
    check(Decimal(result['value']).quantize(Decimal('.01')) == Decimal('8.56'), 'Growth reproduces through existing Financial owner')
    check(result['semantic_type'] == 'calculated', 'Calculated result stays distinct from Reported')
    for field, value in [('subject_id','another-enterprise'),('perimeter','Airline only'),('accounting_basis','Different accounting basis'),('state','target')]:
        altered = [ms[0], ms[1].model_copy(update={field:value})]
        try: f.calculate(recipe(altered), altered)
        except ValueError: check(True, 'Reject mismatched '+field)
        else: raise AssertionError('Accepted incompatible '+field)
    wrong_period = ms[1].model_copy(update={'period': f.FinancialPeriod(kind='duration',label='Partial FY2025',start='2025-01-01',end='2025-09-30',fiscal_year_end='09-30')})
    try: f.calculate(recipe([ms[0],wrong_period]),[ms[0],wrong_period])
    except ValueError: check(True,'Reject partial year / annualisation')
    else: raise AssertionError('Accepted partial year')
    wrong_unit = ms[1].model_copy(update={'value':f.NumericFactValue(amount='10106',currency='USD',scale='millions',unit='currency')})
    try: f.calculate(recipe([ms[0],wrong_unit]),[ms[0],wrong_unit])
    except ValueError: check(True,'Reject wrong currency')
    else: raise AssertionError('Accepted wrong currency')
    different_version = ms[1].model_copy(update={'source':ms[1].source.model_copy(update={'source_revision':'0'*64})})
    try: f.calculate(recipe([ms[0],different_version]),[ms[0],different_version])
    except ValueError: check(True,'Reject annual comparators from different source revisions')
    else: raise AssertionError('Accepted mismatched source version')
    js = (HERE/'prototype/app.js').read_text()
    check(all(v not in js for v in ('11084','11.084','3.21','477.5','2026-lbg-q3-ims.pdf')), 'Restricted Lloyds values/PDF not embedded')
    check(not any(token in js for token in ('fetch(', 'localStorage', 'sessionStorage', 'XMLHttpRequest', 'create_run(', 'Pipeline.create')), 'No runtime, network acquisition, persistence or consequential action')
    check('9,309' in js and 'Headline' in js and 'GROWTH' in js, 'Only bounded, defined airline financial example')
    check(original == (ROOT/source_path).read_bytes(), 'No Source mutation after validation')
    output = {'head':git('rev-parse','HEAD').decode().strip(), 'base':BASE, 'passed':len(checks), 'checks':checks,
        'design_only':True, 'runtime_or_canonical_writes':0, 'source_permissions_added':0,
        'existing_financial_recipe_result':result, 'timestamp':datetime.now(UTC).isoformat()}
    print(json.dumps(output,indent=2,default=str))
    return output


if __name__ == '__main__':
    run()
