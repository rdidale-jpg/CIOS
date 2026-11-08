"""Deterministic support checks over the existing bounded evidence package.

This is a conservative admission control, not a semantic reasoning engine:
consequential commercial assertions require direct cited source support.
"""
from __future__ import annotations
import re
from typing import Any

CLAIM_CLASSES={'canonical_fact_summary','evidence_backed_interpretation','projection','human_supplied_knowledge','unknown','contradiction','recommendation'}
VALID_STATUSES = {'valid', 'valid_with_weakening'}
_CITATIONS = {'supporting_observation_ids','supporting_evidence_ids','evidence_basis','lineage','supporting_evidence','evidence'}
_CONTEXT = {'unknown','contradiction','human_supplied_knowledge','projection','hypothesis','retired','expired','superseded','rejected','unresolved','contested'}
_NON_ASSERTIONS = {'what_not_to_claim','evidence_to_seek','question_to_ask','outcome_increasing_conviction','unknowns','contradictions','linked_unknown_ids','linked_contradiction_ids'}
_COMMERCIAL_FIELDS = {'contract_value','procurement_value','budget','buying_intent','funding_status'}
_COMMERCIAL = re.compile(r'\b(procurement|tender|contract|programme|program|budget|funding|opportunity|buying intent|intends? to buy|plans? to (?:buy|purchase)|will (?:buy|purchase)|funded)\b', re.I)
_ASSERTED = re.compile(r'\b(funded|confirmed|approved|awarded|signed|committed|worth|intends?|plans?|will|buying intent|has|exists)\b|[£$€]\s*\d', re.I)


def _normalise(text):
    return ' '.join(re.findall(r'[\w£$€%]+', str(text).casefold()))


def _commercial_assertions(item):
    """Keep caveats/questions distinct from asserted procurement and buying facts."""
    hypothetical = item.get('interpretation_status') in {'hypothesis','projection'} or item.get('truth_status') in {'hypothesis','projection'}
    for field, value in item.items():
        if field in _CITATIONS | _NON_ASSERTIONS:
            continue
        if isinstance(value, dict):
            yield from _commercial_assertions({'interpretation_status': item.get('interpretation_status', '')} | value)
            continue
        if isinstance(value, list):
            for child in value:
                yield from _commercial_assertions(child if isinstance(child, dict) else {field: child})
            continue
        if not isinstance(value, (str, int, float, bool)):
            continue
        # Value-only commercial fields still assert what the value represents.
        if str(value).casefold().strip() in {'unknown','unconfirmed','not confirmed','not yet evidenced'}:
            continue
        text = field.replace('_', ' ') + ' ' + str(value) if field in _COMMERCIAL_FIELDS else str(value)
        for sentence in re.split(r'(?<=[.!?;])\s+|[;,]\s*|\s+but\s+', text):
            if not _COMMERCIAL.search(sentence) or not (_ASSERTED.search(sentence) or field in _COMMERCIAL_FIELDS):
                continue
            if re.match(r'\s*(?:do not claim|validate whether|investigate whether|ask whether)\b', sentence, re.I):
                continue
            if re.search(r'\b(?:has|have|is|are)\s+no\s+(?:funded|confirmed|approved)?\s*(?:procurement|programme|program|contract|budget)\b', sentence, re.I):
                continue
            modal=re.search(r'\b(may|might|could|possible|potential|if)\b', sentence, re.I)
            if hypothetical and modal and modal.start() < _COMMERCIAL.search(sentence).start():
                continue
            yield sentence


class ClaimValidator:
    def validate(self, brief: dict[str,Any], package) -> dict[str,Any]:
        ids={i.stable_id:i for i in package.all_items() if i.stable_id}
        rejected=[]; weakened=[]

        def reject(path, reason):
            rejected.append({'path':path,'reason':reason})

        def check_refs(refs, path, expected=None):
            if not isinstance(refs, (list, tuple)):
                reject(path, 'citations must be a list of package IDs')
                return []
            good=[]
            for ref in refs:
                if not isinstance(ref, str) or ref not in ids:
                    reject(path, f'invalid cited ID {ref}')
                elif ids[ref].enterprise_id != package.enterprise_id:
                    reject(path, f'cross-enterprise cited ID {ref}')
                elif expected and ids[ref].object_class != expected:
                    reject(path, f'citation {ref} is not {expected}')
                else:
                    good.append(ref)
            return good

        def cited_refs(item, path):
            refs=[]
            for field,value in item.items():
                if field in _CITATIONS:
                    expected='observation' if field=='supporting_observation_ids' else ('evidence' if field=='supporting_evidence_ids' else None)
                    refs.extend(check_refs(value, path+'.'+field, expected))
                elif isinstance(value, dict):
                    refs.extend(cited_refs(value, path+'.'+field))
                elif isinstance(value, list):
                    for index,child in enumerate(value):
                        if isinstance(child,dict):
                            refs.extend(cited_refs(child,f'{path}.{field}[{index}]'))
            return refs

        def evidence_roots(ref, seen=None):
            seen=set() if seen is None else seen
            if ref in seen or ref not in ids:
                return set()
            seen.add(ref)
            item=ids[ref]
            if item.enterprise_id != package.enterprise_id or item.truth_status.casefold() in _CONTEXT:
                return set()
            if any(w in item.freshness.casefold() for w in ('expired','retired','superseded')):
                return set()
            if item.object_class=='evidence':
                return {ref} if item.statement.strip() else set()
            return set().union(*(evidence_roots(r, seen.copy()) for r in item.lineage)) if item.lineage else set()

        if brief.get('enterprise_id') != package.enterprise_id:
            reject('enterprise_id', 'brief enterprise does not match evidence package')

        sections=('material_pressures','material_changes','change_portfolio','stakeholder_assessments',
                  'commercial_relevance_assessments','recommended_next_moves','opportunities',
                  'opportunity_assessments','procurements','procurement_assessments')
        for section in sections:
            rows=brief.get(section) or []
            if not isinstance(rows, list):
                reject(section, 'claim section must be a list')
                continue
            for idx,item in enumerate(rows):
                path=f'{section}[{idx}]'
                if not isinstance(item, dict):
                    reject(path, 'claim must be a structured object')
                    continue
                refs=cited_refs(item,path)
                roots=set().union(*(evidence_roots(r) for r in refs)) if refs else set()
                if section=='material_pressures':
                    if not any(r in ids and ids[r].object_class=='observation' and evidence_roots(r) for r in item.get('supporting_observation_ids', []) if isinstance(r,str)):
                        reject(path, 'material pressure lacks a valid supporting Observation')
                contextual=(section=='recommended_next_moves' and refs
                            and re.match(r'^(validate|inspect|investigate|clarify|ask|resolve|review|learn)\b', str(item.get('action','')), re.I)
                            and all(ids[r].truth_status.casefold() in _CONTEXT for r in refs))
                if not roots and not contextual:
                    reject(path, 'material claim lacks resolvable governed Evidence support')
                for field, klass in (('linked_unknown_ids','unknown'),('linked_contradiction_ids','contradiction')):
                    for ref in check_refs(item.get(field, []), path+'.'+field):
                        if ids[ref].truth_status.casefold()!=klass:
                            reject(path+'.'+field, f'citation does not resolve to {klass}')
                for assertion in _commercial_assertions(item):
                    if not any(_normalise(assertion) in _normalise(ids[r].statement) for r in roots):
                        reject(path, 'commercial assertion lacks direct cited Evidence support: '+assertion)
                if item.get('confidence') in {'high','very_high'} and len(roots)<2:
                    item['confidence']='medium'
                    weakened.append({'path':path,'reason':'confidence weakened because Evidence support is limited'})
        # Summary claims cannot bypass the same commercial support boundary.
        summary=brief.get('executive_summary') or {}
        if isinstance(summary, dict):
            for assertion in _commercial_assertions(summary):
                refs=check_refs(summary.get('evidence_basis', []), 'executive_summary.evidence_basis')
                roots=set().union(*(evidence_roots(r) for r in refs)) if refs else set()
                if not any(_normalise(assertion) in _normalise(ids[r].statement) for r in roots):
                    reject('executive_summary', 'commercial assertion lacks direct cited Evidence support: '+assertion)
        for key, klass in [('unknowns','unknown'),('contradictions','contradiction')]:
            for item in brief.get(key) or []:
                if isinstance(item, dict):
                    item['claim_classification']=klass
        brief['validation_status']={'status':'valid_with_weakening' if weakened and not rejected else ('invalid' if rejected else 'valid'),
            'rejected_claims':rejected,'weakened_claims':weakened,'claim_classes':sorted(CLAIM_CLASSES)}
        return brief
