from __future__ import annotations

import hashlib, time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

from cios.applications.flora.storage import atomic_write_json, data_path, ensure_writable_dir
from cios.applications.flora.financial_intelligence.config import financial_intelligence_settings
from cios.applications.flora.financial_intelligence.rapid_candidates import extract_rapid_financial_candidates
from cios.applications.flora.financial_intelligence.rapid_sources import AcquiredRapidSource

# Deferred architecture debt: the BT-specific structured filing ingestion branch is
# intentionally unchanged in this Slice 2A-to-2B cleanup. This runtime lane only
# accepts Slice 2A source receipts and Slice 2B deterministic extraction results.

@dataclass(frozen=True)
class OfficialSource:
    source_id: str; authority: str; title: str; url: str; document_date: str; reporting_period: str; source_type: str = 'annual_report'

@dataclass(frozen=True)
class CandidateFact:
    fact_id: str; concept: str; label: str; value: str; period: str; scope: str; unit: str; scale: str; basis: str; state: str; source_id: str; location: str; evidence: str; extraction_method: str = 'deterministic_slice_2b_source_extraction'; confidence: float = 0.95; verification_status: str = 'candidate_awaiting_structured_verification'; contradiction: str | None = None

@dataclass(frozen=True)
class VerificationException:
    exception_type: str; fact_id: str | None; message: str; source_id: str | None = None

@dataclass(frozen=True)
class RapidEnterpriseProfile:
    enterprise_id: str; legal_name: str; fiscal_year: str; sources: tuple[OfficialSource, ...]; facts: tuple[CandidateFact, ...]; management_commitments: tuple[dict[str, Any], ...]; pressures: tuple[dict[str, Any], ...]; hypotheses: tuple[dict[str, Any], ...]; outlook: tuple[dict[str, Any], ...]; unknowns: tuple[str, ...]; contradictions: tuple[str, ...] = ()


def _empty_profile(enterprise_id: str, reporting_period: str) -> RapidEnterpriseProfile:
    return RapidEnterpriseProfile(
        enterprise_id, enterprise_id.replace('-', ' ').title(), reporting_period, (), (), (), (), (), (),
        ('Accepted Slice 2A source receipt and deterministic Slice 2B extraction are required before rapid candidate facts can be produced.',),
    )


def _candidate_to_fact(candidate: Any) -> CandidateFact:
    location = f"page {candidate.source_page}; {candidate.source_locator}"
    return CandidateFact(
        fact_id=candidate.candidate_id,
        concept=candidate.proposed_canonical_metric_id,
        label=candidate.raw_metric_label,
        value=candidate.original_displayed_value or candidate.raw_value_text,
        period=candidate.raw_period_text,
        scope=candidate.scope_text,
        unit=candidate.currency,
        scale=candidate.reported_scale,
        basis=candidate.accounting_basis_text,
        state=candidate.measurement_state_text,
        source_id=candidate.source_id,
        location=location,
        evidence=candidate.supporting_excerpt,
        confidence=candidate.extraction_confidence / 100,
        verification_status=candidate.verification_status,
    )


def _result(run_id: str, started: float, profile: RapidEnterpriseProfile, facts: list[dict[str, Any]], sources: list[dict[str, Any]], exceptions: list[dict[str, Any]], status: str, deterministic_ms: int = 0) -> dict[str, Any]:
    settings = financial_intelligence_settings()
    user_result = render_financial_pressure_outlook(profile, facts)
    result={'run_id':run_id,'workflow':'rapid_financial_intelligence','enterprise_id':profile.enterprise_id,'legal_name':profile.legal_name,'reporting_period':profile.fiscal_year,'created_at':datetime.now(UTC).isoformat(timespec='seconds'),'status':status,'sources':sources,'reported_financial_reality':facts,'management_commitments':list(profile.management_commitments),'enterprise_pressure':list(profile.pressures),'transformation_hypotheses':list(profile.hypotheses),'flagship_transformation_outlook':list(profile.outlook),'unknowns':list(profile.unknowns),'contradictions':list(profile.contradictions),'verification_status':'rapid_candidate_only' if facts else 'source_precondition_failed','candidate_fact_count':len(facts),'accepted_canonical_fact_count':0,'facts_awaiting_verification':len(facts),'evidence_citation_coverage': '100% of candidate facts include source_id and source location' if facts else '0%; no accepted source-backed candidates were produced','metrics':{'elapsed_seconds':0,'retrieval_seconds':0,'deterministic_extraction_seconds':deterministic_ms/1000,'verification_seconds':0,'ai_call_count':0,'model_used':settings.model,'token_use':{},'estimated_provider_cost_usd':0,'candidate_fact_count':len(facts),'accepted_fact_count':0,'exception_count':len(exceptions)},'verification_exceptions':exceptions,'canonical_update':{'enterprise_model_updated':False,'observations_created':0,'reason':'candidate facts await governed acceptance' if facts else 'no accepted Slice 2A source receipt was provided'},'user_result': user_result}
    result['metrics']['elapsed_seconds']=time.perf_counter()-started
    return result


def run_rapid_financial_intelligence(enterprise_id: str='bt-group-plc', run_id: str|None=None, *, acquired_source: AcquiredRapidSource | None = None, reporting_period: str = 'FY26') -> dict[str, Any]:
    started=time.perf_counter(); run_id=run_id or 'rfi-'+hashlib.sha256(f'{enterprise_id}:{datetime.now(UTC).isoformat()}'.encode()).hexdigest()[:12]
    ensure_writable_dir(data_path('ai_financial_reports','rapid_runs'))
    if acquired_source is None:
        profile=_empty_profile(enterprise_id, reporting_period)
        exceptions=[asdict(VerificationException('source_precondition_failed', None, 'Rapid candidate generation requires an accepted Slice 2A RapidSourceReceipt and deterministic Slice 2B extraction.', None))]
        result=_result(run_id, started, profile, [], [], exceptions, 'unavailable_source_precondition_failed')
    else:
        extraction=extract_rapid_financial_candidates(acquired_source)
        r=acquired_source.receipt
        facts=[asdict(_candidate_to_fact(c)) for c in extraction.candidates]
        source=OfficialSource(r.source_id, r.authority, r.document_title, r.final_url or r.requested_url, r.publication_date, r.reporting_period, r.source_kind)
        profile=RapidEnterpriseProfile(r.enterprise_id, r.legal_name, r.reporting_period, (source,), tuple(_candidate_to_fact(c) for c in extraction.candidates), (), (), (), (), ('Structured filing verification not completed in rapid lane.',), ())
        exceptions=[e.to_dict() for e in extraction.exceptions]
        status='completed_with_verification_pending' if facts else ('unavailable_source_precondition_failed' if extraction.extraction_status == 'failed_precondition' else 'unavailable_extraction_failed')
        result=_result(run_id, started, profile, facts, [r.to_dict()], exceptions, status, extraction.elapsed_ms)
    atomic_write_json(data_path('ai_financial_reports','rapid_runs',run_id+'.json'), result)
    return result


def render_financial_pressure_outlook(profile: RapidEnterpriseProfile, facts: list[dict[str, Any]]) -> str:
    lines=[f"# {profile.legal_name} {profile.fiscal_year} Financial Pressure and Transformation Outlook", "", "## Executive summary"]
    if not facts:
        lines += ["Rapid official-source intelligence is unavailable because no accepted Slice 2A source receipt was provided to the Slice 2B extractor.", "", "## Financial reality", "- No candidate facts produced."]
    else:
        lines += ["Rapid official-source intelligence is available before structured verification. Candidate facts have not updated the Enterprise Model.", "", "## Financial reality"]
        for f in facts:
            lines.append(f"- Fact: {f['label']} = {f['value']} {f['unit']} {f['scale']} for {f['period']} ({f['scope']}, {f['basis']}). Source: {f['source_id']}, {f['location']}. Status: {f['verification_status']}; confidence {f['confidence']}.")
    lines += ["", "## Management commitments"]
    for c in profile.management_commitments: lines.append(f"- {c['type']}: {c['statement']} Source: {c['source_id']}, {c['location']}. Status: {c['status']}.")
    if not profile.management_commitments: lines.append("- Unavailable pending accepted source-backed extraction.")
    lines += ["", "## Unknowns and Contradictions"] + [f"- Unknown: {u}" for u in profile.unknowns] + [f"- Contradiction: {c}" for c in profile.contradictions]
    return "\n".join(lines)
