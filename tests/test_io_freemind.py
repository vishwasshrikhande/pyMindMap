from pathlib import Path

import pytest

from pymindmap.errors import MindMapIOError
from pymindmap.io import freemind
from pymindmap.model import MindMap, Node, NodeStyle

FIXTURE = Path(__file__).parent / "fixtures" / "sample.mm"


def test_import_fixture_file():
    doc = freemind.import_mm(FIXTURE)

    assert doc.root.title == "Central Topic"
    idea1, idea2 = doc.root.children
    assert idea1.title == "Idea 1"
    assert idea1.style.fill_color == "#ffdd88"
    assert idea1.notes == "some notes"
    assert idea2.title == "Idea 2"
    assert idea2.style.text_color == "#ff0000"
    assert idea2.collapsed is True
    assert idea2.children[0].title == "Hidden Grandchild"


def test_import_preserves_original_ids():
    doc = freemind.import_mm(FIXTURE)
    assert doc.root.id == "ID_1"
    assert doc.root.children[0].id == "ID_2"


def test_import_rejects_non_map_root(tmp_path):
    bad = tmp_path / "bad.mm"
    bad.write_text("<notmap></notmap>")
    with pytest.raises(MindMapIOError):
        freemind.import_mm(bad)


def test_import_rejects_invalid_xml(tmp_path):
    bad = tmp_path / "bad.mm"
    bad.write_text("<map><node TEXT='unterminated'")
    with pytest.raises(MindMapIOError):
        freemind.import_mm(bad)


def test_export_import_round_trip(tmp_path):
    doc = MindMap(title="Root")
    doc.root.title = "Root"
    doc.root.style = NodeStyle(fill_color="#ABCDEF", text_color="#123456")
    child = doc.root.add_child(Node(title="Child", notes="child notes", collapsed=True))

    path = tmp_path / "out.mm"
    freemind.export_mm(doc, path)
    restored = freemind.import_mm(path)

    assert restored.root.title == "Root"
    assert restored.root.id == doc.root.id
    assert restored.root.style.fill_color == "#ABCDEF"
    assert restored.root.style.text_color == "#123456"
    restored_child = restored.root.children[0]
    assert restored_child.title == "Child"
    assert restored_child.id == child.id
    assert restored_child.notes == "child notes"
    assert restored_child.collapsed is True


def test_export_omits_default_colors(tmp_path):
    doc = MindMap()
    path = tmp_path / "out.mm"
    freemind.export_mm(doc, path)
    text = path.read_text()
    assert "BACKGROUND_COLOR" not in text
    assert "COLOR" not in text
