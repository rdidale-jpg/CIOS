#!/usr/bin/env python3
"""Prepare an offline Initial Decision Twin brief from reviewed Researcher records."""
import argparse
from collections import defaultdict
from datetime import date
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from cios.applications.flora.blueprint_import.researcher_profile_adapter import adapt_researcher_payload
from cios.applications.flora.leadership_agenda import agenda

PRODUCER = ROOT / 'knowledge-packs/researcher/package-contracts/flora-blueprint-import/build_flora_import.py'
CLASSES = {'evidence_register': 'evidence', 'relationship_register': 'relationship',
           'unknown_register': 'unknown', 'contradiction_register': 'contradiction'}
REVIEWABLE = {'eligible for consideration', 'corrected eligible for consideration'}
DATE = re.compile(r'\d{4}(?:-\d{2}(?:-\d{2})?)?')


def producer():
    spec = importlib.util.spec_from_file_location('researcher_blueprint_producer', PRODUCER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_review(folder):
    """Validate the existing manifest without creating a ZIP or staging records."""
    owner = producer()
    if (folder / owner.MANIFEST).is_symlink():
        raise ValueError('Expected a local Blueprint manifest')
    manifest = json.loads((folder / owner.MANIFEST).read_text())
    root = folder.resolve()
    for section in ('files', 'record_sets'):
        for entry in manifest.get(section, []):
            path = root / owner.safe_path(entry['path'])
            if not path.resolve().is_relative_to(root):
                raise ValueError('Blueprint path leaves the reviewed directory')
    declared = set(owner.validate_content(folder, manifest, schema))
    required = {'sources.json', 'entity.ndjson', 'review-lineage.json'}
    if not required <= declared:
        raise ValueError('This review uses the existing Source, endpoint and review-lineage files')
    sources, lineage = (json.loads((folder / name).read_text())
                        for name in ('sources.json', 'review-lineage.json'))
    endpoints = [json.loads(line) for line in (folder / 'entity.ndjson').read_text().splitlines()]
    records = defaultdict(list)
    for entry in manifest['record_sets']:
        kind = CLASSES.get(entry['record_class'])
        if kind is None:
            raise ValueError('Unsupported Initial Decision Twin review record set')
        rows = [json.loads(line) for line in (folder / entry['path']).read_text().splitlines() if line.strip()]
        if len(rows) != entry['count']:
            raise ValueError('Blueprint record count differs from manifest')
        records[kind].extend(adapt_researcher_payload(kind, row)[1] for row in rows)
    rows = endpoints + [row for group in records.values() for row in group]
    ids = [row['id'] for row in rows]
    if (len(ids) != len(set(ids)) or any(not re.fullmatch(r'[\w.:-]+', key, re.ASCII) for key in ids)
            or any(row.get('enterprise_id') != manifest['enterprise_id']
                   or row.get('canonical_accepted') is not False for row in rows)):
        raise ValueError('Ambiguous identity, scope or acceptance status')
    evidence_ids = {row['id']: row for row in records['evidence']}
    for predecessor, successors in lineage.get('superseded_evidence_candidates', {}).items():
        if (predecessor in evidence_ids or not successors or any(
                evidence_ids.get(key, {}).get('predecessor_candidate_id')
                != predecessor for key in successors)):
            raise ValueError('Invalid predecessor lineage')
    return manifest, dict(records), sources, {row['id'] for row in endpoints}, lineage


def dates_in_order(period, cutoff):
    bounds = period.split(' to ')
    if len(bounds) > 2 or any(not DATE.fullmatch(bound) for bound in bounds):
        return False
    try:
        dates = [date.fromisoformat(bound + {4: '-01-01', 7: '-01', 10: ''}[len(bound)]) for bound in bounds]
    except ValueError:
        return False
    return dates == sorted(dates) and dates[-1] <= cutoff


def prepare(folder, cutoff):
    manifest, records, sources, endpoints, lineage = read_review(folder)
    batches = defaultdict(list)
    reviewable = set()
    seen = {}
    for row in records['evidence']:
        key = row['id']
        refs = tuple(sorted(set(row.get('evidence_refs', []))))
        status = row.get('review_disposition')
        if status not in REVIEWABLE:
            batches['Held or needs further evidence'].append(key)
            continue
        if any(sources.get(ref, {}).get('status') in {'withdrawn', 'restricted', 'superseded'}
               or sources.get(ref, {}).get('withdrawn') is True for ref in refs):
            batches['Held or needs further evidence'].append(key)
            continue
        if (not refs or any(not sources.get(ref, {}).get('version') or not sources[ref].get('withdrawal')
                            or not sources[ref].get('original_locator') for ref in refs)
                or not row.get('statement') or not row.get('subject') or not row.get('source_location')
                or not dates_in_order(row.get('period', ''), cutoff)
                or not dates_in_order(row.get('collection_date', ''), cutoff)):
            batches['Incomplete lineage or scope'].append(key)
            continue
        # Only exact repeat assertions with identical Source and temporal axes.
        identity = (row['subject'], row['statement'], row['period'], row['verification_status'],
                    row['source_location'], row.get('limitations'), refs)
        if identity in seen:
            batches['Exact repeat within package'].append(f"{key} → {seen[identity]}")
            continue
        seen[identity] = key
        reviewable.add(key)
        if row['verification_status'].startswith('external-'):
            batches['External context owner review'].append(key)
        else:
            batches['Candidate preparation'].append(key)
    edges = []
    deferred_edges = []
    for row in records.get('relationship', []):
        refs = set(row.get('evidence_refs', []))
        if (row.get('relationship_source') in endpoints and row.get('relationship_target') in endpoints
                and refs and refs <= reviewable and row.get('relationship_type')
                and row.get('review_disposition') == 'evidence and identity review'
                and dates_in_order(row.get('period', ''), cutoff)):
            edges.append(row['id'])
        else:
            deferred_edges.append(row['id'])
    return manifest, batches, edges, deferred_edges, records, lineage


def render(folder, cutoff, decision=None):
    manifest, batches, edges, deferred_edges, records, lineage = prepare(folder, cutoff)
    lines = [
        '# Initial Decision Twin · local research brief', '',
        f"Reviewed package {manifest['package_id']} v{manifest['package_version']} · research subject "
        f"{manifest['enterprise_id']} · cut-off {cutoff}.",
        'Candidate preparation only. Source eligibility and record acceptance remain with their existing owners.', '',
    ]
    if decision == 'lloyds-service':
        if manifest['enterprise_id'] != 'BK-ENT-001':
            raise ValueError('Lloyds service preview requires the Lloyds research subject')
        issue = next((item for item in agenda('lloyds') if item.key == 'service-recovery'
                      and all(source.published and dates_in_order(source.published, cutoff)
                              for source in item.conclusion.sources)), None)
        lines.extend(['## Executive decision · what can be said about service performance?', '',
                      issue.conclusion.text if issue else 'The existing Source-bound service view is unavailable.'])
        if issue:
            lines.extend(['', 'Existing Flora evidence, separate from these package candidates.',
                          *(f'- {caveat}' for caveat in issue.conclusion.counter_evidence),
                          *[f'- {s.publisher} · {s.locator} · {s.url}' for s in issue.conclusion.sources]])
        lines.append('')
    lines.extend(['## Candidate handoff', ''])
    for label, ids in batches.items():
        lines.append(f"- {label} ({len(ids)}): {', '.join(ids)}.")
    lines.extend([
        f"- Relationship references for mapping ({len(edges)}): {', '.join(edges) or 'none'}.",
        f"- Relationship references deferred ({len(deferred_edges)}): {', '.join(deferred_edges) or 'none'}.",
        f"- Ledger retained in the input: {len(records.get('unknown', []))} Unknowns, "
        f"{len(records.get('contradiction', []))} reconciliation records, "
        f"{len(lineage.get('superseded_evidence_candidates', {}))} predecessor entries and "
        f"withheld relationships: {len(lineage.get('withheld_relationships', []))}.",
        '', 'Canonical phase needs the existing verified workspace and target binding, Source review, '
        'scoped duplicate comparison and ADR-012 approval. This brief records no canonical mapping or plan.',
    ])
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path, help='Existing reviewed Blueprint source directory')
    parser.add_argument('--as-of', type=date.fromisoformat, required=True)
    parser.add_argument('--decision', choices=('lloyds-service',))
    args = parser.parse_args()
    try:
        print(render(args.package, args.as_of, args.decision), end='')
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
