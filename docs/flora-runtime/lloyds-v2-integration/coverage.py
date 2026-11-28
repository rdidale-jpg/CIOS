"""Reproduce the two explicitly separate Lloyds coverage censuses."""
import csv
from collections import defaultdict
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
BASELINE = (HERE.parents[1] / 'product/flora-experience/lloyds-intelligence-audit/v2/coverage.md')
GATES = ('researched', 'verified', 'connected', 'usable')
LEGACY_IMPROVEMENTS = {'L06', 'L08', 'I12', 'F07'}


def counts(rows):
    pairs = (tuple(sum(flags[index] == '1' for flags in group) for index in range(4))
             for group in zip(*rows))
    first, second = pairs
    return ' '.join(f'{name} {a}/{len(rows)} → {b}/{len(rows)}'
                    for name, a, b in zip(GATES, first, second))


def main():
    original = dict(re.findall(r'^\| ([LIF]\d\d) \| [^|]+ `([01]{4})` \|', BASELINE.read_text(), re.M))
    assert len(original) == 32
    samples = [(flags, '1111' if name in LEGACY_IMPROVEMENTS else flags) for name, flags in original.items()]
    print('Original 32-item sample:', counts(samples))

    groups = defaultdict(list)
    ids = set()
    with (HERE / 'requirements.tsv').open() as table:
        for row in csv.DictReader(table, delimiter='\t'):
            identifier = row['id']
            domain = identifier.split('.')[0]
            assert domain in original and identifier not in ids and all(row.values()), identifier
            ids.add(identifier)
            before, after = (row[key] for key in ('before', 'after'))
            for values in (before, after):
                assert re.fullmatch('[01]{4}', values) and values[0] >= values[1] >= values[2], row
            groups[domain].append((before, after))
    assert all(len(groups[domain]) == 3 for domain in original)
    print('Expanded 96-requirement census:', counts([pair for group in groups.values() for pair in group]))
    for perspective in 'LIF':
        print(perspective, counts([pair for domain, rows in groups.items() if domain.startswith(perspective)
                                   for pair in rows]))
        for domain, rows in groups.items():
            if domain.startswith(perspective):
                print(' ', domain, counts(rows))


if __name__ == '__main__':
    main()
