import pytest

from pymindmap import io
from pymindmap.errors import MindMapIOError
from pymindmap.model import MindMap, Node


def test_save_any_load_any_json_round_trip(tmp_path):
    doc = MindMap(title="Dispatch Test")
    doc.root.add_child(Node(title="Child"))
    path = tmp_path / "out.json"

    io.save_any(doc, path)
    restored = io.load_any(path)

    assert restored.to_dict() == doc.to_dict()


def test_save_any_load_any_mm_round_trip(tmp_path):
    doc = MindMap(title="Dispatch Test")
    path = tmp_path / "out.mm"

    io.save_any(doc, path)
    restored = io.load_any(path)

    assert restored.root.id == doc.root.id


def test_save_any_markdown_writes_outline(tmp_path):
    doc = MindMap()
    doc.root.title = "Root"
    path = tmp_path / "out.md"

    io.save_any(doc, path)

    assert path.read_text() == "- Root\n"


def test_unrecognized_extension_raises():
    with pytest.raises(MindMapIOError):
        io._detect_format("thing.txt")
