"""Reviewed research projections, not a canonical intelligence store."""
import hashlib,json
from ...model import REPO
PINS = {'enterprise-knowledge/technology/research-sprint2/Assurance-v1.json': 'c0ec031d505b7a6bf28289257fb16dff5e0a7afef8841d070ecab3c30f8ffe5b', 'enterprise-knowledge/technology/research-sprint2/Research-v1.json': 'e8a48d161fe52b4382b53f792e464c7bb79014083e9ee236f64aafd71e644081'}


def assets():
    result={}
    for name,expected in PINS.items():
        path=REPO/name
        if path.is_symlink() or any(p.is_symlink() for p in path.parents):raise ValueError('Symlink research source denied')
        content=path.read_bytes()
        if hashlib.sha256(content).hexdigest()!=expected:raise ValueError('Unreviewed research projection')
        result[path.name]=json.loads(content)
    return result
