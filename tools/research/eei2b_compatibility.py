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

EEI3_BASE = 'e6d49f3391f5cd1527ace9010db8ab56f459b87b'
EEI3_CUTS = {'cios/applications/flora/research_intelligence/source_import.py': ('a7d1744b6b9b8d02470100d29cae8954ac67ec20affe8e1bf536c7413c3b5fe8', ('routine_factual_use',)), 'cios/applications/flora/visual_panels.py': ('61d11d985ba0f00e5a8adbd439556e77b6803a30daf4f3aefb2fad69c998f732', ('render',))}


FLAGSHIP_BASE = '6af7ef0afeb8e8ad4059fbb27460add7f80d4ec1'
FLAGSHIP_CUTS = {'tools/research/history_integrity.py': ('6bbbcbfc3f22f3a0c4f627d7f1b031a2736572ab84e51103f4252c19c80e5391', ('verify_history',)), 'cios/applications/flora/lloyds_recovery.py': ('5f2443489d9fe79639f101102951082e8b8ef9f5621889ab89242dd8f8cfa84b', ('landscape',)), 'cios/applications/flora/visual_streams.py': ('35948fa8947c3a0882d3934265ef5a25e5e4373fcd61b5af145cb15eaaa10f42', ('resolve',)), 'cios/applications/flora/visual_panels.py': ('c606965067e6439445f479e588c6f83ba73d5b882eb0105ba61fccd0e2b58d64', ('render',))}


def predecessor(root, path, current):
    current = checked_cut(root, path, current, FLAGSHIP_BASE, FLAGSHIP_CUTS)
    current = checked_cut(root, path, current, EEI3_BASE, EEI3_CUTS)
    return checked_cut(root, path, current, BASE, CUTS)


def checked_cut(root, path, current, base, cuts):
    cut = cuts.get(path)
    if cut is None or sha256(current).hexdigest() != cut[0]:
        return current
    old = subprocess.check_output(['git', 'show', base + ':' + path], cwd=root)

    def protected(raw):
        tree = ast.parse(raw)
        tree.body = [node for node in tree.body
                     if not isinstance(node, ast.FunctionDef) or node.name not in cut[1]]
        return ast.dump(tree, include_attributes=False)

    assert protected(old) == protected(current), 'Unexpected change outside statement integration boundary'
    return old
