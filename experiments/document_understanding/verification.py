from __future__ import annotations
import re
from pydantic import BaseModel, ConfigDict
from .schema import FoundationFact, ClaimType
class VerificationResult(BaseModel):
    model_config=ConfigDict(extra='forbid')
    fact_id:str; status:str; errors:list[str]

def verify_fact(fact:FoundationFact, pages:dict[int,str])->VerificationResult:
    errors=[]
    for p in range(fact.source_page_start, fact.source_page_end+1):
        if p not in pages: errors.append(f'cited page does not exist: {p}')
    text=' '.join(pages.get(p,'') for p in range(fact.source_page_start, fact.source_page_end+1))
    if fact.source_excerpt and fact.source_excerpt not in text: errors.append('source excerpt not found on cited page')
    if fact.value_number is not None:
        n=(str(int(fact.value_number)) if float(fact.value_number).is_integer() else str(fact.value_number)).replace('.0','')
        if n not in text.replace(',',''): errors.append('numeric value not found on cited page')
    if fact.currency and fact.currency not in text and {'GBP':'£','USD':'$','EUR':'€'}.get(fact.currency) not in text: errors.append('currency not supported by page')
    if fact.scale and fact.scale.lower() not in text.lower(): errors.append('scale not supported by page')
    if fact.period_label and fact.period_label not in text: errors.append('period not supported by page')
    if fact.business_unit and fact.business_unit not in text: errors.append('business unit not supported by page')
    if fact.claim_type in {ClaimType.financial_metric_reported,ClaimType.financial_guidance_stated,ClaimType.financial_target_stated}:
        if sum(v is not None for v in (fact.value_text,fact.value_number)) != 1: errors.append('fact is not atomic')
    return VerificationResult(fact_id=fact.fact_id,status='supported' if not errors else 'unsupported',errors=errors)
