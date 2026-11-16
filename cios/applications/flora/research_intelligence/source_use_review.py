"""Proposed series-use review contracts under the existing research Source owner.

Offline review only: no runtime imports, registry, persistence, permissions or
accepted decisions. Matching proposed conditions NEVER authorises a source.
"""
from __future__ import annotations

from datetime import date
from typing import Literal
from urllib.parse import unquote, urlsplit

from pydantic import BaseModel, ConfigDict, Field, model_validator

Use = Literal['access', 'processing', 'numerical_reuse', 'measurement_retention',
              'source_linking', 'seller_display', 'export', 'expression_redistribution']
Audience = Literal['owner_review', 'private_seller', 'public', 'external_recipient']
Category = Literal['issuer_results', 'issuer_announcement', 'regulatory_filing',
                   'fca_owned_data', 'boe_database', 'official_statistics', 'third_party']


class ReviewContract(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)


def original_url(value):
    parsed=urlsplit(value)
    decoded=unquote(parsed.path)
    if (parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password
            or parsed.port not in (None,443) or parsed.query or parsed.fragment
            or '\\' in decoded or '//' in decoded or unquote(decoded)!=decoded
            or any(x in {'.','..'} for x in decoded.split('/'))
            or any(ord(c)<32 or ord(c)==127 for c in decoded)
            or any(c.isspace() or ord(c)==127 for c in value)):
        raise ValueError('Exact original HTTPS source/terms locator required')
    return parsed


class SeriesUseProposal(ReviewContract):
    """One proposed decision can describe many compatible measurements.

    No 'approved' state, authority identifier or caller-granted permission exists.
    Existing source policy must be separately resolved by its actual owners.
    """
    proposal_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    status: Literal['proposed', 'superseded', 'withdrawn', 'rejected'] = 'proposed'
    category: Category
    publisher: str = Field(min_length=1)
    document_series: str = Field(min_length=1)
    reporting_subjects: tuple[str,...] = Field(min_length=1)
    original_prefixes: tuple[str,...] = Field(min_length=1)
    seed_documents: tuple[str,...] = Field(min_length=1)
    terms_url: str
    terms_review_record_revision: str = Field(pattern=r'^[a-f0-9]{64}$')
    terms_applicability: Literal['verified_for_series', 'unresolved']
    # This hashes OUR retained review record, never unavailable publisher bytes.
    reviewed_on: date
    review_due: date
    basis_for_review: str = Field(min_length=1)
    basis_evidence_urls: tuple[str,...] = Field(min_length=1)
    unresolved_legal_questions: tuple[str,...] = Field(min_length=1)
    proposed_uses: tuple[Use,...] = Field(min_length=1)
    proposed_audiences: tuple[Audience,...] = Field(min_length=1)
    purpose: str = Field(min_length=1)
    proposed_retention: str = Field(min_length=1)
    attribution: str = Field(min_length=1)
    proposed_link_conditions: str = Field(min_length=1)
    exclusions: tuple[str,...] = Field(min_length=1)
    maximum_measurements_per_document: int = Field(ge=1, le=100)
    maximum_documents_per_window: int = Field(ge=1, le=20)
    window_days: int = Field(ge=1, le=366)
    required_decisions: tuple[Literal['source_legal', 'source_owner', 'chief_architect', 'resource_owner'],...] = Field(min_length=1)

    @model_validator(mode='after')
    def boundaries(self):
        if self.reviewed_on>date.today() or self.review_due<self.reviewed_on:
            raise ValueError('Invalid review chronology')
        for seq in (self.reporting_subjects,self.original_prefixes,self.seed_documents,
                    self.proposed_uses,self.proposed_audiences,self.required_decisions):
            if len(seq)!=len(set(seq)):
                raise ValueError('Duplicate review scope')
        for prefix in self.original_prefixes:
            parsed=original_url(prefix)
            if parsed.path in {'','/'} or not parsed.path.endswith('/') or '*'in prefix:
                raise ValueError('A proposal cannot be an entire-host wildcard')
        for url in (*self.seed_documents,self.terms_url,*self.basis_evidence_urls):original_url(url)
        if any(not any(u.startswith(prefix) for prefix in self.original_prefixes) for u in self.seed_documents):
            raise ValueError('Seed outside proposed series')
        return self


class SeriesUseRequest(ReviewContract):
    """Metadata for OFFLINE applicability review, not an authority request."""
    category: Category
    publisher: str
    document_url: str
    reporting_subject: str
    terms_review_record_revision: str = Field(pattern=r'^[a-f0-9]{64}$')
    purpose: str
    uses: tuple[Use,...] = Field(min_length=1)
    audience: Audience
    retained_form: Literal['minimal_measurements_and_provenance', 'full_text_or_graphics']
    measurements_in_document: int = Field(ge=1)
    documents_in_window: int = Field(ge=1)
    cumulative_extraction_review: str = Field(min_length=1)
    as_of: date
    lifecycle: Literal['current', 'withdrawn', 'revoked', 'stale', 'contradicted', 'superseded', 'private'] = 'current'


def assess_proposed_use(proposal: SeriesUseProposal, request: SeriesUseRequest) -> dict:
    """Return applicability/exceptions only. Neither outcome grants any use.

    Quantitative caps are proposed operating limits, not legal thresholds for
    'insubstantial' extraction. Actual authority remains with existing owners.
    """
    p=SeriesUseProposal.model_validate(proposal.model_dump(mode='json'))
    r=SeriesUseRequest.model_validate(request.model_dump(mode='json'))
    exceptions=[]
    try:original_url(r.document_url)
    except ValueError:exceptions.append('invalid_original_locator')
    if p.terms_applicability!='verified_for_series':exceptions.append('terms_applicability_unresolved')
    if p.status!='proposed':exceptions.append('proposal_not_current')
    if r.lifecycle!='current':exceptions.append('source_lifecycle_exception')
    if not p.reviewed_on<=r.as_of<=min(p.review_due,date.today()):exceptions.append('review_date_exception')
    if r.category!=p.category:exceptions.append('different_source_category')
    if r.publisher!=p.publisher:exceptions.append('different_publisher')
    if not any(r.document_url.startswith(prefix) for prefix in p.original_prefixes):exceptions.append('outside_proposed_series')
    if r.reporting_subject not in p.reporting_subjects:exceptions.append('different_reporting_subject')
    if r.terms_review_record_revision!=p.terms_review_record_revision:exceptions.append('terms_review_changed')
    if r.purpose!=p.purpose:exceptions.append('different_purpose')
    if not set(r.uses).issubset(p.proposed_uses):exceptions.append('use_not_in_proposal')
    if r.audience not in p.proposed_audiences:exceptions.append('audience_not_in_proposal')
    if r.retained_form!='minimal_measurements_and_provenance':exceptions.append('expression_or_full_text_requires_separate_decision')
    if r.measurements_in_document>p.maximum_measurements_per_document:exceptions.append('document_extraction_limit')
    if r.documents_in_window>p.maximum_documents_per_window:exceptions.append('cumulative_extraction_limit')
    return {'proposal_id':p.proposal_id,'proposal_version':p.version,
            'disposition':'exception_review_required' if exceptions else 'owner_decision_required',
            'proposed_conditions_match':not exceptions,'exceptions':exceptions,
            'required_decisions':list(p.required_decisions),
            'authority':'proposed_review_only_not_source_permission',
            'technical_admission':'not_granted','canonical_acceptance':'not_granted'}


def inspect_current_origin(url: str) -> dict:
    """Actual existing positive-origin policy only; never a legal-use verdict."""
    from .source_import import official_url
    try:official_url(url)
    except (ValueError,TypeError):return {'origin_admission':'blocked','rights_decision':'not_established_by_origin_check'}
    return {'origin_admission':'current_origin_check_passed','rights_decision':'not_established_by_origin_check'}
