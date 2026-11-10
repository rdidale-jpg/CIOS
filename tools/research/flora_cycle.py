#!/usr/bin/env python3
"""Export an offline research wave; never operate on production or canonical stores."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from cios.applications.flora.research_intelligence.cycle import research_plan, run_cycle
from cios.applications.flora.research_intelligence.model import load_assessment
from cios.applications.flora.research_intelligence.registry import enterprise_domain
from cios.applications.flora.research_intelligence.mission_adapter import manifest, mission_owner


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--enterprise', choices=('lloyds', 'easyjet'), required=True)
    parser.add_argument('--as-of', required=True)
    parser.add_argument('--limit', type=int, default=3)
    parser.add_argument('--submissions', type=Path, help='JSON array: task_id, path, metadata, effect, target_claim_id, rationale')
    parser.add_argument('--resume', type=Path)
    parser.add_argument('--output', type=Path, required=True, help='New local directory; existing directories are never overwritten')
    args = parser.parse_args(argv)
    data = load_assessment(enterprise_domain(args.enterprise))
    submissions = json.loads(args.submissions.read_text()) if args.submissions else []
    previous = json.loads(args.resume.read_text()) if args.resume else None
    plan = research_plan(data, args.as_of, args.limit)
    if not isinstance(submissions, list) or len(submissions) > args.limit:
        raise ValueError('Submissions must be an array within the task budget')
    from cios.applications.flora.research_intelligence.source_import import import_proposal
    originals = [import_proposal(s['path'], s['metadata']) for s in submissions]
    checkpoint = run_cycle(data, args.as_of, submissions, args.limit, previous)
    if [p['raw_sha256'] for p in checkpoint['waves'][-1]['proposals']] != [s['primary_content_sha256'] for s in originals]:
        raise ValueError('Source changed during acquisition')
    commission = manifest(data, args.as_of, args.limit)
    # Export resume-selected tasks instead of silently commissioning the first wave again.
    selected = checkpoint['waves'][-1]['selected_task_ids']
    plan['selected_task_ids'] = selected
    commission['scope']['included_domains'] = [t['title'] for t in plan['tasks'] if t['id'] in selected]
    commission['research_priorities']['named_closure_targets'] = [t['id'] + ': ' + t['question'].strip() for t in plan['tasks'] if t['id'] in selected]
    commission['research_priorities']['current_governed_gaps'] = ['Candidate overlay task (not accepted canonical gap): ' + t['id'] + ': ' + t['question'].strip() for t in plan['tasks'] if t['id'] in selected]
    owner = mission_owner()
    owner.validate_manifest(commission)
    rendered = owner.render(commission)
    args.output.mkdir(parents=True, exist_ok=False)
    for filename, value in [('plan.json', plan), ('checkpoint.json', checkpoint), ('mission.json', commission)]:
        (args.output / filename).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    (args.output / 'commission.md').write_text(rendered)
    # Preserve supplied original bytes in the explicit LOCAL output, never in a
    # canonical snapshot store or a public route. Resume keeps prior bundles.
    if submissions:
        sources = args.output / 'sources'; sources.mkdir()
        for acquired in originals:
            (sources / acquired['primary_content_sha256']).write_bytes(acquired['raw'])
    print(f"{args.enterprise}: {len(plan['tasks'])} tasks; {len(checkpoint['waves'][-1]['proposals'])} review proposals; CONTINUE. Local output: {args.output}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
