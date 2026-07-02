"""Deterministic Flora runtime alignment with FP-004/005/006."""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cios.applications.flora.live.store import read_jsonl, write_jsonl

EVIDENCE_ACQUISITION_PLANS_PATH = Path('.flora_pilot/live_evidence/evidence_acquisition_plans.jsonl')
USER_FEEDBACK_PATH = Path('.flora_pilot/live_evidence/user_feedback.jsonl')
COVERAGE_CATEGORIES = ('Strategy','Finance','Technology','Procurement','Leadership','Operations','Regulation','Delivery','Suppliers','Customers / citizens','Risk / security')
DEMAND_TYPES = ('sponsor evidence','budget evidence','procurement evidence','supplier evidence','technology architecture evidence','delivery pressure evidence','regulatory evidence','operating model evidence','skills / workforce evidence','customer/citizen impact evidence')

CATEGORY_TERMS = {
 'Strategy': ('strategy','commitment','modernisation','transformation','reform','priority'),
 'Finance': ('£','$','€','budget','investment','capex','revenue','savings','funding','financial'),
 'Technology': ('ai','cloud','data','platform','cyber','technology','automation','legacy'),
 'Procurement': ('procurement','contract','tender','award','framework','supplier'),
 'Leadership': ('chief','director','minister','secretary','ceo','cfo','cio','cto','executive','chair'),
 'Operations': ('operations','operational','performance','workforce','service','resilience'),
 'Regulation': ('regulator','regulatory','ofcom','ofwat','ofgem','fca','nao','audit','finding','enforcement'),
 'Delivery': ('delivery','milestone','rollout','implementation','programme','delay'),
 'Suppliers': ('supplier','partner','vendor','microsoft','aws','oracle','salesforce','servicenow'),
 'Customers / citizens': ('customer','citizen','user','patient','complaint','satisfaction','experience'),
 'Risk / security': ('risk','security','cyber','incident','outage','fraud','resilience','continuity'),
}
NEXT_SOURCE = {
 'Strategy':'official strategy document or annual report', 'Finance':'annual report, results or budget document', 'Technology':'technology strategy, platform announcement or senior job advert', 'Procurement':'procurement notice or contract award', 'Leadership':'named executive speech or leadership update', 'Operations':'operational performance report', 'Regulation':'regulator, NAO or audit report', 'Delivery':'programme update or delivery milestone', 'Suppliers':'contract award or supplier case study with named client', 'Customers / citizens':'service performance or customer outcome report', 'Risk / security':'security, resilience or incident report'
}
PRIMARY_TYPES = ('annual_report','investor_results','procurement','contract','regulator','govuk_policy','official_strategy','nao')
TIER1_TERMS = ('annual','financial results','investor presentation','capital markets','regulatory','regulator','nao','audit','procurement','contract award','strategy','speech')
TIER2_TERMS = ('press','news','partnership','case','sector','industry','job')
DIAGNOSTIC_TERMS = ('cookie','footer','modern slavery','accessibility','publication scheme','contact','complaints')

def source_tier(source_type: str='', source_name: str='', url: str='') -> str:
    text = f'{source_type} {source_name} {url}'.casefold()
    if any(t in text for t in DIAGNOSTIC_TERMS): return 'diagnostics-only'
    if any(t in text for t in TIER1_TERMS): return 'Tier 1'
    if any(t in text for t in TIER2_TERMS): return 'Tier 2'
    if any(t in text for t in ('home','landing','careers','service','marketing','tag','category','supplier_newsroom')): return 'Tier 3'
    return 'Tier 2'

def evidence_quality_band(item: dict[str, Any]) -> int:
    if item.get('boilerplate_detected') or item.get('relevance_level') == 'REJECT': return 20
    base = int(item.get('overall_evidence_quality') or item.get('confidence') or 50)
    etype = item.get('evidence_type')
    tier = item.get('source_tier') or source_tier(str(item.get('source_type','')), str(item.get('source_name','')), str(item.get('source_url','')))
    if etype == 'Primary Evidence': base += 10
    if etype == 'Context Only' or tier == 'Tier 3': base = min(base, 59)
    if tier == 'diagnostics-only': base = min(base, 39)
    if not item.get('specificity_markers'): base = min(base, 59)
    for fb in read_jsonl(USER_FEEDBACK_PATH):
        if fb.get('target_id') in {item.get('evidence_id'), item.get('evidence_fingerprint')}:
            base += 6 if fb.get('feedback_type') == 'useful evidence' else -8 if fb.get('feedback_type') in {'weak evidence','wrong classification'} else 0
    return max(0, min(100, base))

def can_support_strategic_signal(item: dict[str, Any]) -> bool:
    tier = item.get('source_tier') or source_tier(str(item.get('source_type','')), str(item.get('source_name','')), str(item.get('source_url','')))
    quality = int(item.get('evidence_quality_band') or evidence_quality_band(item))
    if quality < 60 or item.get('evidence_type') == 'Context Only' or tier == 'diagnostics-only' or not item.get('specificity_markers'):
        return False
    if tier == 'Tier 3' and not (quality >= 75 and item.get('corroborated')):
        return False
    return True

def coverage_map_for(organisation: str, evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = [e for e in evidence if e.get('organisation') == organisation]
    out=[]
    for cat in COVERAGE_CATEGORIES:
        terms=CATEGORY_TERMS[cat]
        matches=[e for e in rows if any(t in ' '.join(str(e.get(k,'')) for k in ('snippet','cleaned_observation','commercial_condition','likely_capability','source_type')).casefold() for t in terms)]
        primary=[e for e in matches if e.get('evidence_type')=='Primary Evidence' or any(t in str(e.get('source_type','')).casefold() for t in PRIMARY_TYPES)]
        sources={e.get('source_id') or e.get('source_url') for e in matches}
        noisy=sum(1 for e in matches if e.get('evidence_type')=='Context Only' or int(e.get('evidence_quality_band') or 0)<40)
        if matches and noisy >= max(1, len(matches)//2): status='noisy'
        elif len(matches)>=3 and primary and len(sources)>=2: status='sufficient'
        elif matches: status='partial'
        else: status='insufficient'
        latest=max((str(e.get('extraction_timestamp') or '') for e in matches), default='')
        out.append({'category':cat,'status':status,'evidence_count':len(matches),'primary_evidence_count':len(primary),'source_diversity':len(sources),'freshness':latest[:10] or 'unknown','missing_evidence': [] if status=='sufficient' else [f'{cat} primary evidence'], 'recommended_next_source_family':NEXT_SOURCE[cat]})
    return out

def coverage_score(cmap: list[dict[str, Any]]) -> int:
    weights={'sufficient':100,'partial':60,'noisy':30,'insufficient':10}
    return round(sum(weights[r['status']] for r in cmap)/max(1,len(cmap)))

def collection_priority(priority_level: str, score: int) -> str:
    high = str(priority_level).lower() in {'high','strategic','1','priority'}
    strong = score >= 60
    if high and not strong: return 'collect urgently'
    if high and strong: return 'monitor and corroborate'
    if not high and not strong: return 'defer'
    return 'monitor'

def evidence_demand(theses: list[str], cmap: list[dict[str, Any]]) -> list[dict[str, Any]]:
    missing_cats={r['category'] for r in cmap if r['status']!='sufficient'}
    demands=[]
    for thesis in theses or ['Unproven transformation thesis']:
        req=[d for d in DEMAND_TYPES if any(w in d for w in ('sponsor','budget','procurement','supplier','technology','delivery','regulatory'))]
        if {'Operations','Customers / citizens'} & missing_cats: req += ['operating model evidence','customer/citizen impact evidence']
        demands.append({'thesis': thesis, 'required_evidence_still_needed': list(dict.fromkeys(req))})
    return demands

def lifecycle_action(diag: dict[str, Any]) -> dict[str, Any]:
    accepted=int(diag.get('accepted_evidence_count') or diag.get('evidence_count') or 0); rejected=int(diag.get('rejected_evidence_count') or 0); primary=int(diag.get('primary_evidence_count') or 0)
    total=max(1,accepted+rejected); rejection_rate=rejected/total; noisy=int(diag.get('context_only_count') or 0)/total; duplicate_rate=float(diag.get('duplicate_rate') or 0)
    tier=source_tier(str(diag.get('source_type','')), str(diag.get('source_name','')), str(diag.get('url','')))
    quality=max(0,min(100, (90 if tier=='Tier 1' else 70 if tier=='Tier 2' else 45 if tier=='Tier 3' else 20) + primary*5 - round(rejection_rate*35)))
    yield_score=max(0,min(100, accepted*18 + primary*12 - round(rejection_rate*45) - round(noisy*25)))
    if tier=='diagnostics-only' or (accepted==0 and rejected>0 and noisy>.6): action='diagnostics only'
    elif accepted==0 and rejected==0: action='monitor'
    elif rejection_rate>.65 and ('landing' in str(diag.get('source_classification','')) or diag.get('preferred_child_paths')): action='split into child sources'
    elif yield_score>=70 and primary: action='keep'
    elif yield_score>=45: action='monitor'
    elif rejection_rate>.5: action='replace'
    else: action='downgrade'
    return {'source_quality_score':quality,'source_yield_score':yield_score,'accepted_evidence_count':accepted,'primary_evidence_count':primary,'rejection_rate':round(rejection_rate,2),'duplicate_rate':round(duplicate_rate,2),'signal_conversion_potential':round(min(1, accepted/max(1,total)),2),'noisy_snippet_rate':round(noisy,2),'source_tier':tier,'lifecycle_action':action}

def build_acquisition_plans(sources, evidence: list[dict[str, Any]], diagnostics: list[dict[str, Any]], priorities: dict[str,str]|None=None) -> list[dict[str, Any]]:
    priorities=priorities or {}; by_org=defaultdict(list)
    for s in sources: by_org[s.organisation].append(s)
    plans=[]
    for org, ss in sorted(by_org.items()):
        sector=ss[0].sector; etype='government department' if sector.lower() in {'government','public sector'} or any('govuk' in s.source_type for s in ss) else 'competitor' if sector=='Competitors' else sector.lower() or 'enterprise'
        org_e=[dict(e, source_tier=e.get('source_tier') or source_tier(str(e.get('source_type','')),str(e.get('source_name','')),str(e.get('source_url',''))), evidence_quality_band=evidence_quality_band(e)) for e in evidence if e.get('organisation')==org]
        cmap=coverage_map_for(org, org_e); score=coverage_score(cmap); theses=sorted({e.get('commercial_condition') for e in org_e if e.get('commercial_condition')})[:5]
        low=[d.get('source_name') for d in diagnostics if d.get('organisation')==org and lifecycle_action(d)['lifecycle_action'] in {'replace','diagnostics only','split into child sources'}]
        missing=[m for r in cmap for m in r['missing_evidence']]
        plan={'organisation':org,'sector':sector,'enterprise_type':etype,'priority_level':priorities.get(org,'medium'),'active_transformation_theses':theses,'required_evidence_categories':list(COVERAGE_CATEGORIES),'current_coverage_by_category':cmap,'missing_evidence':missing,'priority_source_families':sorted({r['recommended_next_source_family'] for r in cmap if r['status']!='sufficient'})[:6],'low_yield_sources_to_replace':low,'next_collection_objectives':[f"Find {m}" for m in missing[:5]],'collection_confidence':score,'collection_priority':collection_priority(priorities.get(org,'medium'),score),'evidence_demand':evidence_demand(theses,cmap)}
        plans.append(plan)
    EVIDENCE_ACQUISITION_PLANS_PATH.unlink(missing_ok=True)
    write_jsonl(plans, EVIDENCE_ACQUISITION_PLANS_PATH)
    return plans

def persist_feedback(target_type: str, target_id: str, feedback_type: str, organisation: str='', comment: str='') -> dict[str, Any]:
    row={'timestamp':datetime.now(UTC).isoformat(),'target_type':target_type,'target_id':target_id,'feedback_type':feedback_type,'organisation':organisation,'comment':comment}
    write_jsonl([row], USER_FEEDBACK_PATH); return row
