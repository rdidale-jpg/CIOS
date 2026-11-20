"""Reproduce repository inventory only; no importer, permission or model writes."""
from collections import Counter, defaultdict
import csv
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
BASE = '03719d7573f087c65d9622719273aa4b89caf7d3'


def read(path):
    return json.loads((ROOT / path).read_text())


def collect(output=HERE):
    from cios.applications.flora.live.source_registry import SOURCES
    from cios.applications.flora.seed_data import sample_watchlist
    from cios.applications.flora.banking_portfolio import BANKS
    from cios.applications.flora import banking_cohort, visual_streams
    from cios.applications.flora.research_intelligence import technology, technology_commercial
    from cios.applications.flora.research_intelligence import model
    from cios.applications.flora.financial_intelligence import candidate_analytics

    rows = []
    def row(family, identifier, name, industry, source, presentation, financial='', route='', canonical='No current canonical acceptance verified by this audit'):
        rows.append(dict(family=family, owner_qualified_id=str(identifier), name=name, industry=industry,
                         evidence_path=source, canonical_maturity=canonical, runtime_presentation=presentation,
                         financial_evidence=financial, route=route))

    # Exact source labels are grouped only within this one existing owner. This
    # is not entity resolution: roles, subsidiaries and cross-owner IDs remain.
    grouped = defaultdict(list)
    for source in SOURCES:
        grouped[source.organisation].append(source)
    for name, sources in sorted(grouped.items()):
        industries = sorted({s.sector for s in sources})
        row('source_organisation_label', name, name, '; '.join(industries),
            'cios/applications/flora/live/source_registry.py',
            'Source/watchlist/legacy intelligence support; no named three-panel Twin established by configuration',
            'Source declaration is not extracted/current financial evidence',
            canonical='Source configuration only; enabled status is not acceptance')

    for slug, bank in BANKS.items():
        row('curated_bank', bank.id, bank.name, 'Banking', 'cios/applications/flora/banking_portfolio.py',
            'Lloyds three-panel root' if slug == 'lloyds' else 'Retained public legacy bank profile; separate cohort subject where supported',
            'Lloyds released bounded context' if slug == 'lloyds' else 'Legacy financial views are not the admitted F1/F2 company projection',
            '/enterprises/' + slug, 'Curated reference/scenario; ID is not a canonical receipt')
    for path in sorted((ROOT / 'enterprise-knowledge/banking/enterprises').glob('*/*-Twin.md')):
        row('historical_bank_document', path.parent.name, path.stem, 'Banking', str(path.relative_to(ROOT)),
            'Retained narrative; source-to-current-screen coverage varies', 'Period/issuer/source reconciliation required',
            canonical='Register says Validated; no production Evidence/Model receipt inferred')
    for slug, values in banking_cohort.SUBJECTS.items():
        row('current_cohort_subject', slug, values[0], 'Banking / institutions',
            'cios/applications/flora/banking_cohort.py', 'Shared Banking illustration, Facts/Insight, finite Landscape/Inside/Forces content',
            'Nationwide public Group financial projection' if slug == 'nationwide' else
            'BoE admitted system-level household deposit data' if slug == 'boe' else 'Service/outcome context; company financial candidate not active here',
            '/industries/banking?selected=' + slug)

    foundation, _ = technology.load()
    commercial = technology_commercial.load()
    for provider in foundation['providers']:
        key = provider['key']
        presentation = ('Data-driven commercial NVIDIA profile' if key == 'nvidia' else
                        'Specific Equinix enterprise/Inside journey with fixed financial presentation' if key == 'equinix' else
                        'Provider narrative/shared profile shell; no bespoke enterprise illustration demonstrated')
        row('technology_provider', key, provider['label'], 'Technology: ' + '; '.join(provider['memberships']),
            'docs/flora-runtime/technology-visual-foundation/Foundation.json', presentation,
            'Supplementary participant metric fields where populated' if key in commercial['participants'] else 'Unpopulated fields remain blank',
            '/industries/technology/experience/enterprise?enterprise=' + key,
            'Foundation explicitly records zero canonical acceptance / import eligibility; identity ' + provider['identity_status'])

    dossier_path = 'docs/flora-runtime/research-enrich-all-w3-689/Enterprise-Dossiers.json'
    dossiers = read(dossier_path)
    for d in dossiers:
        row('wave3_dossier', d['id'], d['name'], d['archetype'], dossier_path,
            'Research-only enrichment; do not confuse existing similarly named view with presentation of these new claims',
            'Candidate measurements/reconciliations where supplied; not new public admission',
            canonical='canonical_acceptance=False; new_public_eligible=False')
    crosswalk_path = 'docs/flora-runtime/research-enrich-all-w3-689/Banking-Portfolio-Crosswalk.json'
    for d in read(crosswalk_path)['occurrence_rows']:
        row('banking_actor_occurrence', d['original_actor_id'], d['original_name'], d['original_kind'], crosswalk_path,
            str(d['public_route_state']), 'No actor-count-to-financial-readiness inference',
            canonical='Owner-qualified occurrence; no raw-ID canonical join (BK-ENT-003 collision retained)')

    tel_path = 'docs/industry-twins/TEL-001-runtime-candidate-inventory.json'
    tel = read(tel_path)
    for c in tel['candidates']:
        if c['canonical_class'] in {'enterprise_twin', 'market_participant_twin'}:
            row('tel_recorded_candidate', c['original_source_id'], c['original_source_id'], 'Telecommunications', tel_path,
                'Generic authenticated import/Twin projection code exists; recorded inventory is historical, live receipt unverified',
                'Dossier/candidate evidence requires existing owner review', canonical=str(c['governance_state']))
    archive = 'enterprise-knowledge/TMS-001_High_Fidelity_Industry_Twin_Upgrade.zip'
    with zipfile.ZipFile(ROOT / archive) as z:
        member = next(n for n in z.namelist() if n.endswith('/02_priority_enterprise_twins.json'))
        for c in json.loads(z.read(member))['items']:
            row('tms_priority_subject', c['id'], c['name'], c['domain'], archive + '::' + member,
                'Packaged composite/institution candidate; no dedicated public three-panel view',
                'Economics must follow issuer/role; no public financial admission inferred',
                canonical='Research-ready with conditions; manifest explicitly not promotion-ready')
    row('mod_package', 'MOD-CDT-Blueprint', 'Ministry of Defence', 'Public administration / defence',
        'MOD-CDT-v1.3-Flora-Blueprint 2.zip', 'Authenticated generic enterprise/import implementation; actual production import unverified',
        'Public expenditure/commitments, not company revenue or open procurement budget', canonical='Archive present; acceptance not inferred')

    for domain in ('banking', 'aviation'):
        data = model.load_assessment(domain)
        for supplier in data['suppliers']:
            row('research_supplier_or_role_node', supplier['id'], supplier['title'], domain,
                'enterprise-knowledge/' + domain + '/research-model/Assessment-Overlay.json',
                'Supplier/role context node; not a standalone accepted Enterprise Twin',
                'No supplier contract amount or company financial result inferred',
                canonical='Research graph node; a role aggregate is not a legal enterprise')
        visual_path = 'enterprise-knowledge/' + domain + '/research-model/Visual-Profile.json'
        for actor in read(visual_path)['actors']:
            row('visual_context_or_role', actor['id'], actor['label'], domain + ': ' + actor['category'], visual_path,
                'Legacy visual context/role; only explicit enterprise_slug establishes a destination, not a complete Twin',
                'A comparator or illustrated role is not a company financial adapter',
                canonical='Visual actor/aggregate/gap label, not canonical entity acceptance')
    trace_path = 'enterprise-knowledge/macro/research-model/Entity-Traces-v2.json'
    for trace in read(trace_path)['traces']:
        entity = trace['entity']
        row('macro_entity_applicability_trace', trace['id'], entity.get('legal_name') or entity['id'], trace['country_id'], trace_path,
            'Existing scoped macro inspector/context, not an independent national Enterprise Twin',
            'No entity/company financial inference', canonical='Preserve declared applicability/identity state: ' + entity['status'])

    rows.sort(key=lambda x: (x['family'], x['owner_qualified_id'], x['evidence_path']))
    with (output / 'Enterprise-Inventory.csv').open('w') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    sectors = read('docs/flora-runtime/research-enrich-all-w2-685/Twenty-Sector-Foundations.json')
    sector_rows = [{k: d[k] for k in ('sic', 'label', 'panorama_id', 'public_admission', 'completion')} for d in sectors]
    counts = {
        'source_declarations': len(SOURCES), 'exact_source_organisation_labels': len(grouped),
        'enabled_source_declarations': sum(s.enabled for s in SOURCES),
        'disabled_source_declarations': sum(not s.enabled for s in SOURCES),
        'seed_watchlist': len(sample_watchlist()), 'technology_providers': len(foundation['providers']),
        'technology_relationship_programme_records': len(foundation['relationships']),
        'technology_atomic_references': len(foundation['atomic_references']),
        'technology_participant_metric_rows': len(commercial['participants']),
        'technology_data_driven_deep_profiles': len(commercial['profiles']),
        'wave3_dossiers': len(dossiers), 'banking_actor_occurrences': len(read(crosswalk_path)['occurrence_rows']),
        'tel_recorded_semantic_candidates': tel['semantic_candidate_count'],
        'tel_recorded_enterprise_candidates': sum(c['canonical_class'] == 'enterprise_twin' for c in tel['candidates']),
        'tel_recorded_participant_candidates': sum(c['canonical_class'] == 'market_participant_twin' for c in tel['candidates']),
        'inventory_rows_not_unique_enterprises': len(rows), 'by_inventory_family': dict(Counter(r['family'] for r in rows)),
    }
    # Evidence hashes are audit reproducibility, not a Source or rights registry.
    paths = {r['evidence_path'].split('::')[0] for r in rows}
    paths.update(['docs/product/flora-experience/FLORA-Experience-Contract-v1.0.md',
                  'cios/applications/flora/public_routes.py', 'cios/applications/flora/visual_streams.py',
                  'cios/applications/flora/visual_panels.py', 'cios/applications/flora/experience_composition.py',
                  'cios/applications/flora/financial_intelligence/candidate_analytics.py',
                  'cios/applications/flora/research_intelligence/technology_experience.py',
                  'cios/applications/flora/research_intelligence/technology_commercial.py',
                  'cios/applications/flora/blueprint_import/semantic_twin.py',
                  'enterprise-knowledge/banking/canonical/banking-research-canonical-objects.json',
                  'docs/flora-runtime/research-enrich-all-w2-685/Twenty-Sector-Foundations.json'])
    hashes = {path: sha256((ROOT / path).read_bytes()).hexdigest() for path in sorted(paths)}
    evidence = {
        'audited_main': BASE, 'date': '2026-11-20', 'counts': counts, 'uk_sector_foundations': sector_rows,
        'financial_selection_keys': list(candidate_analytics.permitted_selection_keys()),
        'three_panel_scope_routes': {k: {'route': x['route'], 'streams': list(x['streams'])} for k, x in visual_streams.PRESENTATIONS.items()},
        'interpretation': 'Counts are owner-qualified artifacts/declarations, not unique legal entities, accepted Twins, lawful-use decisions or completeness scores.',
        'live_Render_or_canonical_stores_inspected': False, 'source_permission_changes': 0,
        'source_paths_sha256': hashes,
    }
    (output / 'Repository-Evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    return evidence


if __name__ == '__main__':
    result = collect()
    print(json.dumps(result['counts'], indent=2))
