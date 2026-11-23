"""Investigate previous discovery results using the bounded public source lane."""
import argparse
from datetime import date
import json
from pathlib import Path

from cios.applications.flora.research_intelligence.investigation import CANDIDATE_TERMS, investigate, matches_candidate
from cios.applications.flora.research_intelligence.source_lifecycle import parse_revisions
from tools.research.initial_factory import fetch_disclosure


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('discovery', type=Path)
    parser.add_argument('--source-state', type=Path, help='Optional owner-maintained Source lifecycle snapshot')
    args = parser.parse_args()
    active = None
    withdrawn = set()
    if args.source_state:
        states = parse_revisions(json.loads(args.source_state.read_text()))
        active = {key for key, state in states.items() if state == 'current'}
        withdrawn = {url for url, _ in states} - {url for url, _ in active}
    groups = json.loads(args.discovery.read_text())
    results = []
    seen = set()
    for group in groups:
        enterprise = group['enterprise_id']
        term = CANDIDATE_TERMS.get(enterprise)
        if not term or enterprise in seen:
            continue
        seen.add(enterprise)
        candidates = (row for row in group['candidates'] if matches_candidate(row, term))
        candidate = next(candidates, None)
        if candidate:
            results.append(investigate(candidate, fetch_disclosure, as_of=date.today(),
                                       current_revisions=active, withdrawn=withdrawn))
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
