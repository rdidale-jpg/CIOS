"""Enterprise Canvas pages for Flora."""
from __future__ import annotations
from cios.applications.flora.workspace.views import _page

def canvas_page() -> str:
    return _page("Enterprise Canvas", "<section class='hero'><h1>Enterprise Canvas</h1><p>Blueprint-informed enterprise context, lineage and promotion status.</p></section><section class='card'><p><a href='/flora/blueprint-import'>Import Blueprint</a> · <a href='/flora/blueprint-import/history'>Import History</a></p></section>")

def lineage_page() -> str:
    return _page("Enterprise Canvas Lineage", "<section class='hero'><h1>Canvas Lineage</h1><p>Trace Blueprint Import mappings and governed promotion decisions.</p></section>")

def feedback_page() -> str:
    return _page("Enterprise Canvas Feedback", "<section class='hero'><h1>Canvas Feedback</h1><p>Capture reviewer feedback for blueprint-to-canvas mappings.</p></section>")
