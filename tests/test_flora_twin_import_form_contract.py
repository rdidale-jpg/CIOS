from html.parser import HTMLParser

from cios.applications.flora.blueprint_import.views import import_blueprint_entry_page


class _ImportFormParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.forms = []
        self.stack = []
        self.inputs = []
        self.labels = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "form":
            self.forms.append(attributes)
            self.stack.append(len(self.forms) - 1)
        elif tag == "input":
            self.inputs.append((attributes, self.stack[-1] if self.stack else None))
        elif tag == "label":
            self.labels.append(attributes)

    def handle_endtag(self, tag):
        if tag == "form" and self.stack:
            self.stack.pop()


def test_import_form_has_one_native_enabled_labelled_file_control(monkeypatch):
    monkeypatch.setenv("FLORA_ENVIRONMENT", "pilot")
    html, status = import_blueprint_entry_page({})
    parser = _ImportFormParser()
    parser.feed(html)
    files = [(attrs, owner) for attrs, owner in parser.inputs if attrs.get("type") == "file"]

    assert status == 200 and len(files) == 1
    attrs, owner = files[0]
    assert owner is not None
    assert parser.forms[owner]["method"] == "post"
    assert parser.forms[owner]["action"] == "/blueprint-import/upload"
    assert parser.forms[owner]["enctype"] == "multipart/form-data"
    assert attrs == {
        "type": "file", "id": "twin-package", "name": "blueprint_zip",
        "accept": ".zip,application/zip", "required": None,
    }
    assert sum(label.get("for") == attrs["id"] for label in parser.labels) == 1
    assert "disabled" not in attrs and "hidden" not in attrs
    assert "pointer-events:auto" in html and "opacity:1" in html
    assert html.count("id='twin-package'") == 1
    assert "<span class='pill'>PILOT</span>" in html
    assert "Import workflow" in html
