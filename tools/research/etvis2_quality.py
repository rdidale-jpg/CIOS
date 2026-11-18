"""Read-only source/asset/lineage integrity; no baseline refresh or admission."""
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))


def validate():
    from cios.applications.flora import enterprise_preview as v
    from tools.research.etvis2_compatibility import validate as owners
    folder=ROOT/'docs/flora-runtime/et-vis2-659'
    inputs=json.loads((folder/'Retained-Inputs.json').read_text())
    for path,digest in inputs.items():
        assert sha256((ROOT/path).read_bytes()).hexdigest()==digest, 'Retained input changed: '+path
    lineage=json.loads((folder/'Content-Lineage.json').read_text())
    assert len(lineage['disclosures'])==7 and len(lineage['capability_bindings'])==3
    data=v._data();assert data is not None
    for row in lineage['disclosures']:
        fact=v.fact(data,row['claim_id']);assert fact is not None
        assert fact.text==row['display_text'] and fact.period==row['display_period']
        assert fact.canonical_status=='candidate_intelligence'
        assert row['claim_digest']==v.CLAIM_PINS[row['claim_id']]
        for source in row['source_records']:
            assert source['source_digest']==v.SOURCE_PINS[source['id']]
            assert source['primary_content_sha256'] is None
    assert set(v.CAPABILITIES)=={row['selection']for row in lineage['capability_bindings']}
    for binding in lineage['capability_bindings']:
        assert binding['model_fields']==json.loads(json.dumps(v.CONTENT[binding['selection']]))
        assert v._capability_available(v.Context(capability=binding['selection']))
    return {'retained_inputs':len(inputs),'unchanged_visual_stream_files':sum('visual_stream_assets/'in p for p in inputs),
            'public_disclosures':7,'existing_source_records':len(v.SOURCE_PINS),'conceptual_capabilities':3,
            'canonical_or_production_writes':0,'source_permissions_added':0,'owners':owners()}


if __name__=='__main__': print(json.dumps(validate(),indent=2))
