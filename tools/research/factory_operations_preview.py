"""Preview research timing and Source withdrawals from explicit offline snapshots."""
import argparse
import json
from pathlib import Path

from cios.applications.flora.research_intelligence.operations_preview import research_intent
from cios.applications.flora.research_intelligence.source_lifecycle import parse_revisions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('state', type=Path, help='Owner-provided Source lifecycle snapshot')
    parser.add_argument('request', type=Path, help='Offline research review intent')
    args = parser.parse_args()
    state = parse_revisions(json.loads(args.state.read_text()))
    request = json.loads(args.request.read_text())
    result = research_intent(enterprise=request['enterprise'], workspace=request['workspace'],
                             run_after=request['run_after'], revisions=state,
                             withdrawals=[(item['url'], item['sha256'])
                                          for item in request.get('withdrawals', [])])
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
