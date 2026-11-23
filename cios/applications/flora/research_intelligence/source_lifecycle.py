"""Read owner-maintained document revision state for reviewed commercial evidence."""

import json

from ..storage import data_path


def lifecycle_path():
    """Existing Flora data boundary. No runtime writer or publication grant."""
    return data_path('research_intelligence', 'document-lifecycle.json')


def parse_revisions(document):
    """Validate the owner lifecycle envelope."""
    if not isinstance(document, dict) or document.get('schema_version') != '1.0':
        raise ValueError('Invalid or ambiguous Source lifecycle state')
    rows = document.get('revisions')
    if not isinstance(rows, list):
        raise ValueError('Invalid or ambiguous Source lifecycle state')
    states = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('Invalid or ambiguous Source lifecycle state')
        locator, digest = row.get('url'), row.get('sha256')
        if not isinstance(locator, str) or not isinstance(digest, str) or len(digest) != 64:
            raise ValueError('Invalid or ambiguous Source lifecycle state')
        key = locator, digest
        if key in states:
            raise ValueError('Invalid or ambiguous Source lifecycle state')
        states[key] = row.get('lifecycle')
    return states



def current_revisions():
    """Read current states afresh. Missing or invalid owner data fails closed."""
    try:
        document = json.loads(lifecycle_path().read_text(encoding='utf-8'))
        states = parse_revisions(document)
    except (OSError, ValueError):
        return set()
    return {key for key, state in states.items() if state == 'current'}


def apply_source_lifecycle(rows):
    """Project withdrawal into Evidence reads without rewriting accepted facts."""
    selected = [row for row in rows if 'commercial_change' in row]
    if not selected:
        return rows
    current = current_revisions()
    result = []
    for row in rows:
        if 'commercial_change' in row:
            dependencies = row.get('document_revisions')
            if (not isinstance(dependencies, list) or not dependencies
                    or not all(isinstance(dep, dict)
                               and isinstance(dep.get('url'), str)
                               and isinstance(dep.get('sha256'), str)
                               and (dep['url'], dep['sha256']) in current
                               for dep in dependencies)):
                row = {**row, 'status': 'withdrawn', 'source_lifecycle': 'unavailable'}
        result.append(row)
    return result
