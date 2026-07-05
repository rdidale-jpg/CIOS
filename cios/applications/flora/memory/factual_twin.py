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
   candidates.append(("identity.legal_name", "enterprise_identity_confirmed", "BT Group plc is the reporting enterprise.", "identity"))
  if re.search(r"telecommunications|communications", text, re.I):
   candidates.append(("identity.sector", "enterprise_identity_confirmed", "BT Group plc operates in the telecommunications sector.", "identity"))
  for m in METRIC_RE.finditer(text):
   seg=(m.group('segment') or 'Group').title(); metric=m.group('metric').lower().replace('capex','capital expenditure')
   value=m.group('value'); unit=m.group('unit') or 'm'; period='FY26' if re.search(r"FY26|2026", text) else 'reported period'
   status='target' if re.search(r"target|by FY|aim", text[m.start()-80:m.end()+80], re.I) else 'actual'
   stmt=f"BT Group plc reported {seg} {metric} of GBP {value}{unit} for {period}"
   attr=f"financial_performance.metrics.{seg}.{metric}.{period}.{status}"
   candidates.append((attr,"financial_metric_reported",stmt,"table" if '|' in page.text else 'narrative'))
  for m in UNIT_RE.finditer(text):
   name=m.group(1); kind=m.group(2).lower().replace('customer-facing ', '').replace(' ', '_')
   candidates.append((f"structure.units.{name}","business_unit_disclosed",f"{name} is reported as a {kind.replace('_',' ')}","narrative"))
  for m in PILLAR_RE.finditer(text):
   candidates.append((f"strategy.pillars.{m.group('name')}","strategic_pillar_stated",f"{m.group('name')} is a stated BT Group strategic pillar","narrative"))
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
  materials=[(a + ' ' + str(model.attributes[a].current_value or '')).replace('_', ' ') for a in attrs]
  populated=sum(1 for exp in expected if any(exp.casefold() in a.casefold() for a in materials))
  out[domain]={"expected_attributes":expected,"populated_attributes":attrs,"unsupported_attributes":[e for e in expected if not any(e.casefold() in a.casefold() for a in materials)],"stale_attributes":[],"contradicted_attributes":[a for a in attrs if model.attributes[a].contradiction_state=='contradicted'],"source_count":len({eid for a in attrs for eid in model.attributes[a].evidence_ids}),"coverage_percent":round(100*populated/len(expected)) if expected else 100}
 return out

def maturity_for_model(model)->str:
 cov=coverage_for_model(model)
 if all(cov[d]['populated_attributes'] for d in ['identity','structure','financial_performance','strategy','leadership']) and any('bt-foundation' in eid or str(eid).startswith('bt-') for a in model.attributes.values() for eid in a.evidence_ids):
  return 'Foundation — calibrated'
 if all(cov[d]['populated_attributes'] for d in ['identity','structure','financial_performance','strategy','leadership']): return 'Foundation'
 if any(cov[d]['populated_attributes'] for d in cov): return 'Foundation — partial'
 return 'Not established'

def automatic_extraction_comparison(golden_facts:list[dict[str,Any]], automatic_evidence:list[dict[str,Any]], accepted_attributes:set[str]|None=None)->list[dict[str,Any]]:
 rows=[]
 accepted_attributes=accepted_attributes or set()
 for fact in golden_facts:
  matches=[e for e in automatic_evidence if e.get('affected_attribute')==fact.get('affected_attribute') or str(fact.get('atomic_statement')) in str(e.get('cleaned_observation') or e.get('snippet') or '')]
  best=matches[0] if matches else {}
  rows.append({'fact_id':fact.get('fact_id'),'automatically_recovered':bool(matches),'claim_type_correct':best.get('commercial_condition')==fact.get('claim_type') if best else False,'value_correct':str(fact.get('structured_value') or '') in str(best.get('cleaned_observation') or best.get('snippet') or best.get('value') or '') if best else False,'period_correct':(not fact.get('period')) or str(fact.get('period')) in str(best.get('affected_attribute') or best.get('period') or best.get('cleaned_observation') or ''),'page_correct':str(best.get('page_number') or best.get('page_range') or '')==str(fact.get('page')) if best else False,'observation_accepted':bool(matches),'model_attribute_correct':str(fact.get('affected_attribute')) in accepted_attributes})
 return rows
