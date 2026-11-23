"""Offline intent for existing Source and Blueprint owners. No executor."""
from datetime import datetime
import re

from .initial_factory import fingerprint


def research_intent(*, enterprise, workspace, run_after, revisions, withdrawals=()):
    """Preview one bounded review wave and an inverse lifecycle diff.

    Revisions are already owner-provided state, keyed by (original URL, digest).
    This interface can only propose withdrawals. It does not write owner state,
    schedule work, or grant Source use or publication.
    """
    when = datetime.fromisoformat(run_after)
    if when.utcoffset() is None or not enterprise or not workspace:
        raise ValueError('Explicit enterprise, workspace and time zone required')
    changes = []
    for url, digest in sorted(set(withdrawals)):
        key = url, digest
        if (not url.startswith('https://') or not re.fullmatch(r'[a-f0-9]{64}', digest)
                or key not in revisions or revisions[key] not in {'current', 'withdrawn'}):
            raise ValueError('Withdrawal needs an existing exact Source revision')
        if revisions[key] == 'current':
            changes.append({'url': url, 'sha256': digest, 'from': 'current', 'to': 'withdrawn'})
    intent = {
        'enterprise': enterprise, 'workspace': workspace, 'run_after': when.isoformat(),
        'lifecycle_changes': changes, 'execution_enabled': False,
        'publication': 'existing Source-use decision and scoped Blueprint approval required',
        'rollback_preview': [{**row, 'from': row['to'], 'to': row['from']} for row in reversed(changes)],
    }
    return {'intent_id': fingerprint(intent), **intent}
