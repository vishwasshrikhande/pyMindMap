from pymindmap.io import markdown_export
from pymindmap.model import MindMap, Node


def test_to_markdown_nests_by_depth():
    doc = MindMap()
    doc.root.title = "Root"
    a = doc.root.add_child(Node(title="A"))
    a.add_child(Node(title="A1"))
    doc.root.add_child(Node(title="B"))

    text = markdown_export.to_markdown(doc)

    assert text == "- Root\n  - A\n    - A1\n  - B\n"


def test_export_markdown_writes_file(tmp_path):
    doc = MindMap()
    doc.root.title = "Root"
    path = tmp_path / "out.md"

    markdown_export.export_markdown(doc, path)

    assert path.read_text() == "- Root\n"
