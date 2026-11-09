"""Import a verified downloaded PDF/HTML/text into new scratch review storage.

No network requests, live-overlay edits, canonical writes or commercial changes.
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cios.applications.flora.research_intelligence.source_import import import_proposal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--file', required=True, type=Path)
    parser.add_argument('--metadata', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    from cios.applications.flora.storage import data_root
    destination = args.output.resolve()
    if (destination.exists() or destination.is_relative_to(data_root().resolve())
            or destination.is_relative_to(Path('/var/data'))
            or destination.is_relative_to(Path(__file__).resolve().parents[1])):
        parser.error('Use a new scratch directory outside the repository and application data')
    try:
        result = import_proposal(args.file, json.loads(args.metadata.read_text()))
    except (ValueError, KeyError, OSError) as exc:
        parser.error(str(exc))
    destination.mkdir(mode=0o700, parents=True)
    (destination/('original'+args.file.suffix.lower())).write_bytes(result.pop('raw'))
    (destination/'source.txt').write_text(result.pop('text'))
    (destination/'review-proposal.json').write_text(json.dumps(result, indent=2)+'\n')
    print('Review proposal created. No research, canonical or pipeline records changed.')


if __name__ == '__main__': main()
