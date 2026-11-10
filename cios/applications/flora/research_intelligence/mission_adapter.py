"""Compose, then validate with the existing Researcher mission owner."""
from functools import lru_cache
import importlib.util

from .model import REPO
from .cycle import research_plan


@lru_cache(maxsize=1)
def mission_owner():
    spec = importlib.util.spec_from_file_location('flora_research_mission_owner', REPO / 'tools/knowledge-packs/research_missions.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def manifest(data, as_of, limit=3):
    plan = research_plan(data, as_of, limit)
    owner = mission_owner()
    templates, _, profiles = owner.registries()
    template = templates['targeted-evidence-closure']
    mid = data['enterprise_twin_id'] + '-research-' + as_of
    selected = [t for t in plan['tasks'] if t['id'] in plan['selected_task_ids']]
    result = {
        'schema_id': 'CIOS-Research-Mission-Manifest', 'schema_version': '1.1.0',
        'mission_id': mid, 'mission_name': data['enterprise_name'] + ' evidence-led deepening',
        'mission_type': template['id'], 'mission_template_id': template['id'],
        'mission_template_version': template['version'], 'parent_twin_id': data['enterprise_twin_id'],
        'baseline_release': data['assessment_id'], 'created_date': as_of,
        'generated_date': as_of + 'T00:00:00Z', 'owner': 'Research owner unassigned',
        'governance_state': 'DRAFT',
        'scope': {'industry': data['industry_name'], 'geography': [data.get('geography', 'Source-specific geography; enterprise and industry boundaries require review')],
            'included_domains': [t['title'] for t in selected],
            'excluded_domains': ['Automatic canonical updates', 'Sales qualification'],
            'material_subject_criteria': 'Deepen the existing reference enterprise; preserve industry scope boundaries',
            'research_period': 'Historical baseline through cut-off', 'evidence_cut_off': as_of,
            'current_checkpoint': plan['coverage']['baseline_digest'],
            'complete_scope_rule': 'Selected evidence demands need governed review; no automatic completion.'},
        'profile_pins': {pid: profiles[pid] for pid in template['profiles']},
        'relationship_profile_versions': {'industry-membership': profiles['industry-membership']},
        'evidence_uncertainty_profile_versions': {'evidence': 'EI-012', 'unknown': 'IT-001', 'contradiction': 'IT-001'},
        'release_manifest_version': '2.0.0',
        'research_priorities': {'priority_outcomes': ['Improve evidence quality and connected understanding'],
            'current_governed_gaps': ['Candidate overlay task (not accepted canonical gap): ' + t['id'] + ': ' + t['question'].strip() for t in selected],
            'named_closure_targets': [t['id'] + ': ' + t['question'].strip() for t in selected],
            'monitoring_targets': ['Dated source changes and contrary evidence'],
            'current_object_counts': {'candidate_claims': len(data['claims'])},
            'current_unknowns': [g['id'] + ': ' + g['question'].strip() for g in data['gaps']],
            'current_contradictions': ['No complete structured contradiction register in overlay; inspect source history']},
        'evidence_policy': {'preferred_source_types': sorted({f for t in selected for f in t['source_families']}),
            'primary_source_expectation': 'Located primary passages; reviewer-attested supplied files; original bytes retained',
            'evidence_exhaustion_policy': 'Network restrictions are an escalation, not evidence exhaustion. Continue other permitted routes.',
            'closure_classifications': ['CLOSED', 'PARTIAL', 'EVIDENCE_EXHAUSTED', 'OPEN'],
            'freshness_rules': 'Keep publication, effective, reporting and retrieval dates distinct', 'review_period': '90 days'},
        'estimation_policy': {'permitted_estimate_types': [], 'retain_underlying_unknown': True},
        'outputs': {'required_object_classes': ['governed-records'],
            'required_registers': sorted(owner.MANDATORY_OUTPUTS - {'governed-records'} | set(template['required_outputs'])),
            'required_reports': ['change-log', 'executive-checkpoint'],
            'required_package_name': mid + '-candidate', 'release_manifest_requirement': True,
            'checksums': True, 'change_log': True, 'executive_checkpoint': True},
        'outcome_states': sorted(owner.OUTCOMES), 'pack_version': (owner.BASE / 'VERSION').read_text().strip(),
    }
    owner.validate_manifest(result)
    return result
