"""Explicit isolated authority and reference bindings for the native proof."""
from dataclasses import asdict
from datetime import date

from cios.applications.flora.research_intelligence.assurance import (
    Assertion, BoundEvidence, EvidenceRef, FactScope, assure, publication_preview,
)
from cios.applications.flora.research_intelligence.initial_factory import fingerprint

ARM = 'arm-holdings-plc'
NOTICE = Assertion(
    FactScope(ARM, 'microsoft', 'azure-cobalt-200', 'publisher_notice',
              'Microsoft announcement of Azure Cobalt 200 availability', '2026-11-17'),
    'announced', 'status', 'Microsoft announced general availability of Azure Cobalt 200 virtual machines.',
)
# Fixture-only scoped consent. This is not inferred from the assurance decision.
FIXTURE_SCOPES = frozenset({(ARM, 'isolated_workspace', fingerprint(asdict(NOTICE)))})


def assess_existing_proof(result, current_revisions):
    """Classify prior accepted sample statements; no live review or reuse grant."""
    payload = result['records'][0]['payload']
    enterprise = result['enterprise_id']
    observed = date.fromisoformat(payload['period'])
    assertion = NOTICE if enterprise == ARM else Assertion(
        FactScope(enterprise, enterprise, payload['affected_attribute'], 'status',
                  'Attribution in the previously reviewed isolated sample', observed.isoformat()),
        'announced', 'status', payload['statement'],
    )
    if assertion.statement != payload['statement']:
        raise ValueError('Isolated record differs from the approved assertion')
    bindings = []
    for source in payload['document_revisions']:
        direct = (enterprise == ARM and source['url'] ==
                  'https://azure.microsoft.com/en-us/blog/azure-cobalt-200-vms-now-available-proven-on-real-workloads-and-built-for-the-agentic-era/')
        bindings.append(BoundEvidence(
            EvidenceRef(source['url'], source['sha256'], 'publisher body · reviewed binding'),
            assertion, 'Microsoft' if direct else payload['publisher'],
            'Microsoft announcement' if enterprise == ARM else payload['publisher'],
            'official' if direct else 'issuer', observed,
        ))
    return assure(assertion, bindings, current_revisions=current_revisions, as_of=observed)


def fixture_handoff(decision, enterprise):
    return publication_preview(decision, workspace=enterprise, audience='isolated_workspace',
                               approved_scopes=FIXTURE_SCOPES,
                               source_use_approved=enterprise == ARM,
                               workspace_allowed=enterprise == ARM, execution_approved=enterprise == ARM)
