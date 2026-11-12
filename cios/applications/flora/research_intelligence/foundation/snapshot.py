"""Exact reviewed public release assets, never a live operations/private-store reader."""
import hashlib
import json
from ..model import REPO
from ..cycle import digest

PINS = {'enterprise-knowledge/technology/research-foundation-v1/Acquisition-Receipts-v1.json': 'c67a816d1822e07114e94a64e87f29ebdebc5a6ef63e12ec04e7716a5c26d437', 'enterprise-knowledge/technology/research-foundation-v1/Mission-v1.json': '6022ed52a54d37ae1d6e8e3c10e790cd81ff98a2bec46c49011bbdc62663f2be', 'enterprise-knowledge/technology/research-foundation-v1/Population-v1.json': '1423f9ce7b683fc9d15dc545b87b166efae81ff590d10acbc5a5f64758bba545', 'enterprise-knowledge/technology/research-foundation-v1/Programme.json': '76c9c1fb3d078c65440a503f060658fec90572c6942436074f3bfb144009bf9c', 'enterprise-knowledge/technology/research-foundation-v1/Release-v1.json': '087af7f4e634b3c2ac9bb97ce1e123cd5fff9d2f8566befd5cda75ddb3edf176'}


def assets():
    result={}
    for name,expected in PINS.items():
        path=REPO/name
        if path.is_symlink() or any(p.is_symlink() for p in path.parents):raise ValueError('Research asset symlink denied')
        content=path.read_bytes()
        if hashlib.sha256(content).hexdigest()!=expected:raise ValueError('Unreviewed public research asset')
        result[path.name]=json.loads(content)
    release=result['Release-v1.json']
    if digest(release['content'])!=release['digest'] or not release['content']['live_research']:
        raise ValueError('Public release integrity or live-evidence gate failed')
    return result
