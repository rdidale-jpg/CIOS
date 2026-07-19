#!/usr/bin/env python3
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
POT=ROOT/'enterprise-knowledge/banking/provider-offer-twin'
CAN=ROOT/'enterprise-knowledge/banking/canonical/banking-research-canonical-objects.json'
STRONG={'Pursue','Shape','Partner'}
errors=[]
def load(p):
    with open(p) as f: return json.load(f)
canon=load(CAN); canon_ids={o['object_id']:o for o in canon['canonical_objects']}
unknowns={o['object_id'] for o in canon['canonical_objects'] if o.get('object_type')=='Unknown'}
contradictions={o['object_id'] for o in canon['canonical_objects'] if o.get('object_type')=='Contradiction'}
review=load(POT/'provider-offer-twin-review-items.json')
review_ids={r['review_item_id'] for r in review['review_items']}
def check_lineage(obj, field='source_lineage'):
    lin=obj.get(field) or obj.get('evidence_lineage') or []
    if not lin: errors.append(f"{obj.get('object_type')} missing lineage")
    partial=False
    for e in lin:
        cid=e.get('canonical_object_id')
        if cid and cid not in canon_ids: errors.append(f"broken canonical lineage {cid}")
        if not all(e.get(k) for k in ['canonical_object_id','source_zip_path','source_zip_sha256','archive_member_path','archive_member_sha256']): partial=True
    if partial and 'owner_review' not in obj.get('review_status',''):
        errors.append(f"partial lineage not owner-reviewed: {obj}")

def req(obj, idfield):
    for k in ['object_type','confidence','review_status']:
        if k not in obj: errors.append(f"{idfield} missing {k}")
    if not obj.get(idfield): errors.append(f"missing stable id {idfield}")
    check_lineage(obj)

data=load(POT/'banking-provider-offer-twin.json')
for sec,idf in [('providers','provider_id'),('provider_capabilities','capability_id'),('provider_offers','offer_id'),('offer_variants','offer_variant_id'),('provider_proofs','proof_id'),('provider_constraints','constraint_id'),('partner_dependencies','partner_dependency_id')]:
    for o in data.get(sec,[]): req(o,idf)
for c in data['provider_capabilities']:
    if c['object_type']=='ProviderOffer': errors.append('capability collapsed into offer')
for o in data['provider_offers']:
    if o['object_type']=='ProviderCapability': errors.append('offer collapsed into capability')
fit=load(POT/'provider-fit-assessment-seed.json')
for f in fit['provider_fits']:
    req(f,'provider_fit_id')
    for bad in ['buying_authority','procurement_route','relationship_access','accessibility_strength']:
        if bad in f: errors.append('ProviderFit contains accessibility field '+bad)
    if f.get('fit_basis')!='capability_only' and not f.get('linked_offer_ids'):
        errors.append('ProviderFit claims non-capability-only fit without offer')
acc=load(POT/'commercial-accessibility-seed.json')
for a in acc['commercial_accessibility']:
    req(a,'commercial_accessibility_id')
    for bad in ['linked_capability_ids','linked_offer_ids','fit_strength','fit_basis']:
        if bad in a: errors.append('CommercialAccessibility contains fit field '+bad)
conv=load(POT/'commercial-conviction-seed.json')
fit_ids={f['provider_fit_id'] for f in fit['provider_fits']}; acc_ids={a['commercial_accessibility_id'] for a in acc['commercial_accessibility']}
for c in conv['commercial_convictions']:
    req(c,'commercial_conviction_id')
    for k in ['enterprise_need_ref','provider_fit_ref','commercial_accessibility_ref']:
        if not c.get(k): errors.append('CommercialConviction missing '+k)
    if c.get('provider_fit_ref') not in fit_ids: errors.append('broken provider_fit_ref')
    if c.get('commercial_accessibility_ref') not in acc_ids: errors.append('broken commercial_accessibility_ref')
    refs=set(c.get('lineage_path',[]))
    if c.get('recommended_action') in STRONG and not refs: errors.append('strong action without lineage')
    for u in c.get('unknowns',[]):
        if u not in unknowns and u not in review_ids: errors.append('unknown not queryable '+u)
    for con in c.get('contradictions',[]):
        if con not in contradictions and con not in review_ids: errors.append('contradiction not queryable '+con)
for r in conv.get('recommendations',[]):
    if not r.get('commercial_conviction_ref'): errors.append('Recommendation without CommercialConviction')
# conceptual fixtures from seed state
if data['provider_capabilities'] and data['provider_offers']:
    pass
if not data['provider_offers'] and fit['provider_fits'][0].get('fit_basis')!='capability_only': errors.append('capability-only fixture failed')
if acc['commercial_accessibility'][0]['accessibility_strength']=='weak' and conv['commercial_convictions'][0]['recommended_action'] in STRONG: errors.append('accessibility separation fixture failed')
if errors:
    print('Provider Offer Twin validation failed:'); print('\n'.join('- '+e for e in errors)); sys.exit(1)
print('Provider Offer Twin validation passed')
