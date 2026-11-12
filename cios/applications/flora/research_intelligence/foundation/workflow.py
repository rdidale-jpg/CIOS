"""Bounded establish driver with an injected, permissioned acquisition bridge.

A collector receives only the finite public request, not previous evidence,
private context, commands or permission-editing capabilities. It returns an
Acquisition receipt or raises AcquisitionUnavailable. No built-in network bypass.
"""
from copy import deepcopy
from .contracts import Programme
from ..cycle import digest
from ..mission_adapter import mission_owner


class AwaitingAcquisition(Exception):
    """Pause for the external approved bridge without treating the pause as failure."""


class AcquisitionUnavailable(Exception):
    """Expected collector/network unavailability; bounded retry, never fake evidence."""


def establish(operations, job_id, collector):
    with operations.db() as db:
        job, programme=operations._job(db,job_id)
    if programme.mode!='establish':raise NotImplementedError('Mode contract exists; this runner implements establish only')
    for source in programme.sources:
        for role in ('researcher','verifier'):
            while True:
                status=operations.status(job_id)
                if status['cancelled'] or status['state']=='exhausted':return {'status':status,'release':None}
                request=operations.request(job_id,role,source.source_id)
                if request is None:break
                try:
                    # Each verifier invocation gets a new request and no researcher passage.
                    receipt=collector(deepcopy(request))
                except AwaitingAcquisition:
                    return {'status':operations.status(job_id),'pending_request':request,'release':None}
                except AcquisitionUnavailable as exc:
                    operations.fail_request(job_id,request['request_id'],str(exc))
                    continue
                # Invalid/unsafe evidence is a hard gate, not a swallowed retry.
                operations.ingest(job_id,receipt)
                break
    if operations.status(job_id)['state']=='exhausted':return {'status':operations.status(job_id),'release':None}
    assurance=operations.assure(job_id)
    return {'status':operations.status(job_id),'assurance':assurance,'release':operations.release(job_id)}


def mission_manifest(programme):
    """Compose the existing Researcher owner's manifest, validated by that owner."""
    p=programme if isinstance(programme,Programme) else Programme(**programme)
    owner=mission_owner();templates,_,profiles=owner.registries();template=templates['targeted-evidence-closure']
    mid=p.id+'-'+p.as_of.isoformat()
    manifest={
      'schema_id':'CIOS-Research-Mission-Manifest','schema_version':'1.1.0',
      'mission_id':mid,'mission_name':p.objective,'mission_type':template['id'],
      'mission_template_id':template['id'],'mission_template_version':template['version'],
      'parent_twin_id':p.industry_id,'baseline_release':'unestablished-research-programme-v1',
      'created_date':p.as_of.isoformat(),'generated_date':p.as_of.isoformat()+'T00:00:00Z',
      'owner':'Automated bounded research controller; product direction remains owner-managed',
      'governance_state':'DRAFT',
      'scope':{'industry':p.industry_id,'geography':[p.country,*p.jurisdictions],
        'included_domains':p.baseline_requirements,'excluded_domains':['Commercialisation','Canonical promotion','Pipeline qualification','Unattended monitoring'],
        'material_subject_criteria':'Documented catalogue discovery, UK relevance and scale/importance gaps; no automatic key-company ranking',
        'research_period':'Historical context through dated cut-off','evidence_cut_off':p.as_of.isoformat(),
        'current_checkpoint':digest(p.model_dump(mode='json')),'complete_scope_rule':'Literal publisher entries only; unanswered baseline dimensions remain Unknown'},
      'profile_pins':{pid:profiles[pid] for pid in template['profiles']},
      'relationship_profile_versions':{'industry-membership':profiles['industry-membership']},
      'evidence_uncertainty_profile_versions':{'evidence':'EI-012','unknown':'IT-001','contradiction':'IT-001'},
      'release_manifest_version':'2.0.0',
      'research_priorities':{'priority_outcomes':['Comparable evidence-backed industry and provider baseline'],
        'current_governed_gaps':p.baseline_requirements,'named_closure_targets':p.baseline_requirements,
        'monitoring_targets':['Not scheduled in v1'],'current_object_counts':{'candidate_claims':0},
        'current_unknowns':p.baseline_requirements,'current_contradictions':['Not yet researched; no absence assertion']},
      'evidence_policy':{'preferred_source_types':['Government catalogues','Official registers','Enterprise publications','Regulators','Government statistics'],
        'primary_source_expectation':'Located permitted excerpts, separate retrieval receipts; original bytes not claimed',
        'evidence_exhaustion_policy':'Bounded failed acquisition creates a gap, not routine owner factual review',
        'closure_classifications':['CLOSED','PARTIAL','EVIDENCE_EXHAUSTED','OPEN'],
        'freshness_rules':'Publication/effectivity/retrieval distinct; unknown publication date disclosed','review_period':'90 days'},
      'estimation_policy':{'permitted_estimate_types':[],'retain_underlying_unknown':True},
      'outputs':{'required_object_classes':['governed-records'],
        'required_registers':sorted(owner.MANDATORY_OUTPUTS-{'governed-records'}|set(template['required_outputs'])),
        'required_reports':['change-log','executive-checkpoint'],'required_package_name':mid+'-candidate',
        'release_manifest_requirement':True,'checksums':True,'change_log':True,'executive_checkpoint':True},
      'outcome_states':sorted(owner.OUTCOMES),'pack_version':(owner.BASE/'VERSION').read_text().strip()}
    owner.validate_manifest(manifest)
    return manifest
