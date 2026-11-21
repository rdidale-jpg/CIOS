"""Bounded historical cuts for the public statement reader and presentation."""
import ast
from hashlib import sha256
import subprocess

BASE = 'df6173c186e6469783c732247f4c13aaa961aec4'
CUTS = {
    'cios/applications/flora/research_intelligence/source_import.py': ('74a2faa257f86b4896ccc0afc6edead6444c2d225765dc4b1cd617e0600bec44', 'minimal_factual_integrity'),
    'cios/applications/flora/visual_panels.py': ('6235d24dd286a24e4cc21bc1ca76b8ee916c2a97b43986e9673b703e33dc13e7', 'render'),
}


def predecessor(root, path, current):
    cut = CUTS.get(path)
    if cut is None or sha256(current).hexdigest() != cut[0]:
        return current
    old = subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=root)

    def protected(raw):
        tree = ast.parse(raw)
        tree.body = [node for node in tree.body
                     if not isinstance(node, ast.FunctionDef) or node.name != cut[1]]
        return ast.dump(tree, include_attributes=False)

    assert protected(old) == protected(current), 'Unexpected change outside EEI-2A boundary'
    return old
