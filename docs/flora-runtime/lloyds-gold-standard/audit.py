"""Reproducible repository utilisation census; not a runtime registry or admission."""
import ast
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from cios.applications.flora import lloyds_gold as gold,visual_streams as v

ROOT=Path(__file__).resolve().parents[3]
BASE='eaca26f2b31c3c9227bb797d60f7d3492a8313d1'

def report():
    data=v.current_data(v.Context('lloyds','landscape'));facts=gold.facts_for(data)
    # Call-site dependency inventory of #730, not a guess from a PR completion.
    old=subprocess.check_output(['git','show',BASE+':cios/applications/flora/living_enterprise_preview.py'],cwd=ROOT,text=True)
    tree=ast.parse(old)
    displayed={node.value for node in ast.walk(tree) if isinstance(node,ast.Constant) and isinstance(node.value,str) and node.value in facts}
    displayed.update(gold.recovery.MEASURES)
    displayed.update(k for _,keys,_ in gold.SWOT for k in keys)
    rows=[]
    for claim in sorted(data['claims'],key=lambda c:c['id']):
        if claim.get('asset_id')!='BK-ENT-001':continue
        ident=claim['id'];eligible=ident in facts
        category=('C' if ident in displayed else 'B') if eligible else 'D'
        destinations=[focus for focus,keys in gold.FOCUS_FACTS.items() if ident in keys]
        rows.append({'id':ident,'classification':category,'eligible_now':eligible,'baseline_730_reachable':eligible and ident in displayed,
          'gold_main_destinations':destinations if eligible else [],'domain':claim['domain'],'period':claim['reporting_period'],
          'entity':claim.get('entity_scope'),'source_ids':claim['source_ids'],'claim_kind':claim['kind'],
          'disposition':'Existing eligible public statement; deepen without new admission' if eligible else 'Retain research history; no new public authority inferred'})
    documents=[]
    patterns=['docs/flora-runtime/lei-1/*','docs/flora-runtime/research-enrich-all-w3-689/dossiers/lloyds.md',
      'enterprise-knowledge/banking/enterprises/lloyds/*','docs/architecture/enterprise-twin-production/*.md',
      'docs/flora-runtime/public-facts-policy/*.md','docs/flora-runtime/ric-1*/*',
      'enterprise-knowledge/banking/research-model/*.json']
    for path in sorted({p for pattern in patterns for p in ROOT.glob(pattern) if p.is_file()}):
        documents.append({'path':str(path.relative_to(ROOT)),'sha256':sha256(path.read_bytes()).hexdigest(),
          'authority':'Existing package; document presence does not prove canonical or public acceptance'})
    collections={k:len(data[k]) for k in ('sources','claims','capabilities','programmes','suppliers','relationships','gaps','frameworks','candidates')}
    model=[]
    for collection in ('capabilities','programmes','suppliers','relationships','gaps'):
        for row in data[collection]:
            model.append({'collection':collection,'id':row['id'],'classification':'E' if collection=='gaps' else 'C' if collection in {'capabilities','programmes'} else 'D',
             'claim_ids':row.get('claim_ids',[]),'verified':row.get('verified',False),
             'scope':row.get('scope','Candidate model record; no canonical acceptance inferred')})
    image_paths=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'cios/applications/flora/visual_stream_assets'],cwd=ROOT,text=True).splitlines()
    images=[]
    for name in image_paths:
        if Path(name).suffix not in {'.webp','.png','.jpg','.jpeg','.avif'}:continue
        before=subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT)
        after=(ROOT/name).read_bytes()
        if before!=after:raise ValueError('Original image changed: '+name)
        images.append({'path':name,'sha256':sha256(after).hexdigest()})
    eligible=[row for row in rows if row['eligible_now']]
    surfaced=[row for row in eligible if row['gold_main_destinations']]
    assert len(surfaced)==len(eligible)==19
    return {'baseline':BASE,'method':'Unique original claim IDs; older unverified duplicates remain held, not silently merged. B/C are all supported underutilised Lloyds items. No full-estate completeness claim.',
      'collections':collections,'lloyds_claim_counts':dict(Counter(r['classification'] for r in rows)),
      'eligible_lloyds_denominator':len(eligible),'eligible_lloyds_surfaced':len(surfaced),
      'baseline_reachable_eligible':sum(r['baseline_730_reachable'] for r in rows),
      'external_context_ids':sorted(set(facts)-set(gold.LLOYDS_IDS)),
      'source_records':[{'id':r['id'],'title':r['title'],'publisher':r.get('publisher'),'publication_date':r.get('publication_date'),
        'reporting_period':r.get('reporting_period'),'verification':r.get('verification'),'rights':r.get('rights'),
        'eligible_lloyds_claim_ids':[c['id'] for c in eligible if r['id'] in c['source_ids']],
        'existing_record_location':'enterprise-knowledge/banking/research-model (original identity retained)'} for r in data['sources']],
      'claims':rows,'underutilised_supported_items':eligible,'model_records':model,'documents':documents,'original_images':images,
      'canonical_record_status':'UNKNOWN: no authorised live canonical-store inspection in this task; no import or promotion claimed',
      'source_authority_delta':'None; existing request-time Source owners only'}

if __name__=='__main__':
    value=report();target=Path(__file__).with_name('Inventory.json')
    if '--check' in sys.argv:
        assert json.loads(target.read_text())==value,'Inventory differs from current owner projections'
        print('Inventory, 19/19 eligible public Lloyds claim identities, and original image hashes verified')
    else:
        target.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
        print(json.dumps({k:value[k] for k in ('collections','lloyds_claim_counts','eligible_lloyds_denominator','eligible_lloyds_surfaced','baseline_reachable_eligible')}))
