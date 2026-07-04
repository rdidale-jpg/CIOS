"""Factual Enterprise Model projection helpers for Digital Twin foundation."""
from __future__ import annotations
import hashlib, re
from dataclasses import asdict
from html import escape
from typing import Any
from cios.applications.flora.memory.models import Observation
from cios.applications.flora.live.documents import DocumentParseResult

DOMAINS = {
 "identity":["legal_name","sector","principal_geography","listed_status","reporting_currency","financial_year_end"],
 "structure":["group","reporting_segment","business_unit","brand"],
 "financial_performance":["revenue","adjusted EBITDA","capital expenditure","free cash flow","net debt"],
 "strategy":["purpose","ambition","strategic_pillar","commitment"],
 "leadership":["Group Chief Executive","Chair","Chief Financial Officer"],
}

METRIC_RE = re.compile(r"(?P<segment>Group|Consumer|Business|Openreach|International)?\s*(?P<metric>revenue|adjusted EBITDA|EBITDA|operating profit|capital expenditure|capex|free cash flow|net debt|cost savings)(?:\s|\|)*(?:of|was|:)?(?:\s|\|)*£(?P<value>[0-9,.]+)\s*(?P<unit>m|bn|million|billion)?", re.I)
UNIT_RE = re.compile(r"\b(Consumer|Business|International|Openreach|Digital|Networks)\b.*\b(business unit|customer-facing business unit|reporting segment|internal capability|operating unit)\b", re.I)
BRAND_RE = re.compile(r"\b(BT|EE|Plusnet)\b.*\bbrand\b", re.I)
LEADER_RE = re.compile(r"(?P<person>[A-Z][A-Za-z .'-]+)\s+(?:held|is|was|serves as|appointed as)\s+(?:the role of\s+)?(?P<role>Group Chief Executive|Chief Executive|Chief Financial Officer|Chair|Chairman|CEO|CFO)", re.I)
PILLAR_RE = re.compile(r"(?:strategic pillar|pillar)\s+(?P<name>Build|Connect|Accelerate|Transform|Grow|Simplify)\b", re.I)

def _eid(doc_id: str, page:int, text:str) -> str:
 return "EV-" + hashlib.sha256(f"{doc_id}|{page}|{text}".encode()).hexdigest()[:16].upper()

def _obs(statement: str, typ: str, attr: str, evidence_id: str, doc: DocumentParseResult, confidence:int=86, state:str="current") -> Observation:
 return Observation(doc.canonical_enterprise_id, typ, statement.rstrip("." )+".", doc.publication_date or doc.retrieval_date[:10], doc.retrieval_date, attr, confidence, (evidence_id,), evidence_publication_date=doc.publication_date, freshness=state)

def extract_factual_evidence(doc: DocumentParseResult) -> tuple[list[dict[str,Any]], list[dict[str,Any]]]:
 evidence=[]; rejected=[]
 for page in doc.pages:
  text = re.sub(r"\s+", " ", page.text)
  candidates=[]
  if "BT Group plc" in text:
   candidates.append(("identity.legal_name", "enterprise_identity_confirmed", "BT Group plc is the legal name.", "identity"))
  if re.search(r"telecommunications|communications", text, re.I):
   candidates.append(("identity.sector", "enterprise_identity_confirmed", "BT Group plc operates in the telecommunications sector.", "identity"))
  for m in METRIC_RE.finditer(text):
   seg=(m.group('segment') or 'Group').title(); metric=m.group('metric').lower().replace('capex','capital expenditure')
   value=m.group('value'); unit=m.group('unit') or 'm'; period='FY26' if re.search(r"FY26|2026", text) else 'reported period'
   status='target' if re.search(r"target|by FY|aim", text[m.start()-80:m.end()+80], re.I) else 'actual'
   stmt=f"BT Group plc reported {period} {seg} {metric} of £{value}{unit}"
   attr=f"financial_performance.metrics.{seg}.{metric}.{period}.{status}"
   candidates.append((attr,"reported_financial_metric",stmt,"table" if '|' in page.text else 'narrative'))
  for m in UNIT_RE.finditer(text):
   name=m.group(1); kind=m.group(2).lower().replace('customer-facing ', '').replace(' ', '_')
   candidates.append((f"structure.units.{name}","business_unit_disclosed",f"{name} is reported as a {kind.replace('_',' ')}","narrative"))
  for m in BRAND_RE.finditer(text):
   candidates.append((f"structure.brands.{m.group(1)}","brand_disclosed",f"{m.group(1)} is reported as a BT brand","narrative"))
  for m in PILLAR_RE.finditer(text):
   candidates.append((f"strategy.pillars.{m.group('name')}","strategic_commitment_stated",f"BT Group plc states {m.group('name')} as a strategic pillar","narrative"))
  for m in LEADER_RE.finditer(text):
   role=m.group('role').replace('CEO','Group Chief Executive').replace('CFO','Chief Financial Officer')
   person=re.sub(r"\b(is|was|held|serves as|appointed as)\b.*", "", m.group('person')).strip()
   candidates.append((f"leadership.roles.{role}","executive_role_confirmed",f"{person} held the role of {role}","narrative"))
  seen=set()
  for attr,typ,stmt,origin in candidates:
   if (attr,stmt) in seen: continue
   seen.add((attr,stmt)); evid=_eid(doc.document_id,page.page_number,stmt)
   evidence.append({"evidence_id":evid,"document_id":doc.document_id,"source_id":doc.source_id,"source_name":doc.source_title,"publisher":doc.publisher,"source_url":doc.source_url,"source_type":doc.source_type,"source_tier":doc.source_tier,"document_checksum":doc.checksum,"media_type":doc.media_type,"page_number":page.page_number,"page_range":str(page.page_number),"extracted_text":stmt,"snippet":stmt,"origin":origin,"evidence_class":"factual_extraction","confidence":86,"status":"accepted","rejection_reason":"","extraction_method":page.extraction_method,"canonical_enterprise_id":doc.canonical_enterprise_id,"enterprise_id":doc.canonical_enterprise_id,"organisation":doc.canonical_enterprise_id,"collection_date":doc.retrieval_date,"extraction_timestamp":doc.retrieval_date,"publication_date":doc.publication_date,"cleaned_observation":stmt,"extracted_observation":stmt,"commercial_condition":typ,"affected_attribute":attr,"evidence_type":"Primary Evidence","overall_evidence_quality":86,"source_provenance":"live"})
  if 'table' in text.lower() and not candidates:
   rejected.append({"document_id":doc.document_id,"page_number":page.page_number,"status":"rejected","rejection_reason":"Table extraction uncertain","extracted_text":text[:240]})
 return evidence,rejected

def coverage_for_model(model)->dict[str,Any]:
 out={}
 for domain, expected in DOMAINS.items():
  attrs=[k for k in model.attributes if k.startswith(domain) or (domain=='structure' and k.startswith('organisational_structure'))]
  materials=[a + ' ' + str(model.attributes[a].current_value or '') for a in attrs]
  populated=sum(1 for exp in expected if any(exp.casefold() in a.casefold() for a in materials))
  out[domain]={"expected_attributes":expected,"populated_attributes":attrs,"unsupported_attributes":[e for e in expected if not any(e.casefold() in a.casefold() for a in materials)],"stale_attributes":[],"contradicted_attributes":[a for a in attrs if model.attributes[a].contradiction_state=='contradicted'],"source_count":len({eid for a in attrs for eid in model.attributes[a].evidence_ids}),"coverage_percent":round(100*populated/len(expected)) if expected else 100}
 return out

def maturity_for_model(model)->str:
 cov=coverage_for_model(model)
 if all(cov[d]['populated_attributes'] for d in ['identity','structure','financial_performance','strategy','leadership']): return 'Foundation'
 return 'Not established'
