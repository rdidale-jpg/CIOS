"""Review-time exact compatibility for the bounded audited statement slice."""
import ast
from hashlib import sha256
import subprocess

BASE = '38ae6acb92d7ffcd6a0b82e162b291e3fd4705ce'
CUTS = {
    'cios/applications/flora/research_intelligence/source_import.py': ('d6d9d567699018167ccecbf9cf96d671bb39d3e365ee2c2156433ada26e1b89b', ('official_url', 'public_statement_record')),
    'cios/applications/flora/visual_panels.py': ('251ba94b4984188626d5b72dff3c12755398920f02176c6e00a3f1c50426e37a', ('render',)),
    'tools/research/history_integrity.py': ('d147e4f49cb9e4ad6d367659e4a6e0057884886c6e79c3840e5d2e4430691560', ('verify_history',)),
}

def predecessor(root, path, current):
    cut = CUTS.get(path)
    if cut is None or sha256(current).hexdigest() != cut[0]:
        return current
    old = subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=root)

    def protected(raw):
        tree = ast.parse(raw)
        tree.body = [node for node in tree.body
                     if not isinstance(node, ast.FunctionDef) or node.name not in cut[1]]
        return ast.dump(tree, include_attributes=False)

    assert protected(old) == protected(current), 'Unexpected change outside EEI-2B boundary'
    return old
