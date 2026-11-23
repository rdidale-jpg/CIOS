"""Live public register transcription check using the existing acquisition lane."""
from datetime import date
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from cios.applications.flora.research_intelligence.assurance import (
    Assertion, BoundEvidence, EvidenceRef, FactScope, assure,
)
from cios.applications.flora.research_intelligence.initial_factory import verify_register
from tools.research.initial_factory import acquire_online

REFERENCE = (
    ('00445790', 'TESCO PLC', 'Retail'),
    ('04031152', 'NATIONAL GRID PLC', 'Utilities'),
)


def live_register_check(reference=REFERENCE):
    """Original public registry fields; eligibility stays local to the proof."""
    now = date.today()
    outcomes = []
    with TemporaryDirectory() as directory:
        for number, name, industry in reference:
            commission = {'registration_number': number, 'as_of': now.isoformat()}
            captures, failed = acquire_online(commission, Path(directory))
            if failed or len(captures) != 1:
                raise ValueError(f'Public register document unavailable for {number}')
            observed, url, digest, fields = verify_register(captures[0], number, name, now)
            actual = {
                'company_number': fields.text('company-number').split()[-1],
                'legal_name': ' '.join(' '.join(fields.heading).split()),
                'status': fields.text('company-status'),
            }
            expected = {'company_number': number, 'legal_name': name, 'status': 'Active'}
            matches = sum(actual[key] == value for key, value in expected.items())
            assertion = Assertion(FactScope(number, number, 'register', 'registry_status',
                                            'Companies House registered status', observed),
                                  actual['status'], 'status',
                                  f'Companies House lists {name} as {actual["status"]}.')
            ref = EvidenceRef(url, digest, 'company-status')
            bound = BoundEvidence(ref, assertion, 'Companies House', 'Companies House register',
                                  'official', date.fromisoformat(observed))
            outcomes.append({
                'industry': industry, 'expected': expected, 'observed': actual,
                'matches': matches, 'reported_fields': len(actual), 'reference_fields': len(expected),
                'judgement': assure(assertion, [bound], current_revisions={(url, digest)}, as_of=now),
            })
    return outcomes


if __name__ == '__main__':
    print(json.dumps(live_register_check(), indent=2))
