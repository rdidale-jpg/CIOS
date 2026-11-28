"""Reproduce the bounded coverage census and retained public financial bridges."""
from collections import Counter
from pathlib import Path
import re
import sys

AUDIT = Path(__file__).resolve().parent
ROOT = AUDIT.parents[4]
sys.path.insert(0, str(ROOT))

from cios.applications.flora import lloyds_financials as finance


def coverage():
    matrix = (AUDIT / 'coverage.md').read_text()
    rows = re.findall(r'^\| ([LIF]\d\d) \| [^|]+ `([01]{4})` \| ([0-5]) \|', matrix, re.M)
    standard = ROOT / 'docs/architecture/enterprise-twin-production/enterprise-intelligence-standard-v2.md'
    standard_ids = re.findall(r'^\| ([LIF]\d\d) ', standard.read_text(), re.M)
    required_ids = [f'{area}{index:02}' for area, size in (('L', 10), ('I', 12), ('F', 10))
                    for index in range(1, size + 1)]
    assert [row[0] for row in rows] == standard_ids == required_ids
    for identifier, gates, level in rows:
        researched, verified, connected, usable = map(int, gates)
        assert researched >= verified >= connected, identifier
        expected = 5 if connected and usable else 4 if connected else 3 if verified else 2 if researched else 0
        assert int(level) == expected, identifier
    counts = [sum(gates[index] == '1' for _, gates, _ in rows) for index in range(4)]
    for label, count in zip(('Research', 'Verified', 'Connected', 'Usable'), counts):
        print(f'{label}: {count}/{len(rows)} ({count / len(rows):.1%})')
    print('Levels:', dict(sorted(Counter(level for _, _, level in rows).items())))


def reconciliations():
    retained = finance.current()
    group = finance.GROUP

    def amount(metric, end, scope=group, start=None, basis=None):
        rows = finance.select(retained, (metric,), end, scope=scope, start=start)
        values = finance.values(rows, monetary_bridge=True, basis=(basis,) if basis else None)
        assert values, (metric, end, scope, start, basis)
        return values[0]

    first_half = '2026-06-30'
    components = [amount('segment_pbt', first_half, scope)
                  for scope in finance.DIVISIONS.values()]
    assert components == [2256, 1425, 245, 289]
    segment_total = amount('segment_pbt', first_half)
    assert sum(components[:3]) == 3926
    assert sum(components) == segment_total == 4215
    restructuring = amount('remove_restructuring', first_half)
    volatility = amount('remove_volatility', first_half)
    assert (restructuring, volatility) == (34, -112)
    h1 = amount('pbt', first_half, basis='Statutory')
    q3 = amount('pbt', '2026-09-30', start='2026-07-01', basis='Statutory')
    nine_months = amount('pbt', '2026-09-30', basis='Statutory')
    assert segment_total - restructuring - volatility == h1 == 4293
    assert q3 == 2332 and h1 + q3 == nine_months == 6625

    expected_divisional = {
        'Retail': ((5279, -2922, 1974), (5710, -2872, 2256)),
        'Commercial Banking': ((2688, -1394, 1194), (2897, -1409, 1425)),
        'Insurance Pensions and Investments': ((611, -466, 144), (747, -494, 245)),
    }
    for scope, rows in expected_divisional.items():
        for year, expected in zip((2025, 2026), rows):
            values = tuple(amount(metric, f'{year}-06-30', scope, basis='Underlying segment reporting')
                           for metric in ('net', 'cost', 'segment_pbt'))
            assert values == expected, (scope, year)
    print('Divisional sample: 18/18 comparable retained income, costs and profit cells.')

    keys = ('u_net', 'u_cost', 'u_remediation', 'u_impairment', 'restructuring', 'volatility')
    changes = [amount(key, '2026-09-30') - amount(key, '2025-09-30') for key in keys]
    assert changes == [1262, -70, 851, -312, -35, 251]
    assert sum(changes[:4]) == 1731 and sum(changes[4:]) == 216
    assert sum(changes) == nine_months - amount('pbt', '2025-09-30', basis='Statutory') == 1947
    print('H1: 3926 + 289 - 34 + 112 = 4293. Q3: 4293 + 2332 = 6625.')
    print('Nine-month movement: 1262 - 70 + 851 - 312 - 35 + 251 = 1947.')


if __name__ == '__main__':
    coverage()
    reconciliations()
