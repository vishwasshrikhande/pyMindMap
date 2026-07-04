from pathlib import Path

import pytest

from pymindmap.errors import MindMapIOError
from pymindmap.io import json_format
from pymindmap.model import MindMap, Node

FIXTURE = Path(__file__).parent / "fixtures" / "sample.mindmap.json"


def test_loads_fixture_file():
    doc = json_format.load(FIXTURE)
    assert doc.title == "Sample Map"
    assert doc.root.id == "root-1"
    assert doc.root.children[0].title == "Idea 1"
    assert doc.root.children[0].notes == "some notes"
    assert doc.root.children[0].x == 220.0
    assert doc.root.children[0].style.fill_color == "#FFDD88"


def test_dumps_loads_round_trip():
    doc = MindMap(title="My Map")
    doc.root.add_child(Node(title="Idea", notes="notes here"))

    text = json_format.dumps(doc)
    restored = json_format.loads(text)

    assert restored.to_dict() == doc.to_dict()


def test_save_load_round_trip(tmp_path):
    doc = MindMap(title="Saved Map")
    doc.root.add_child(Node(title="Child"))
    path = tmp_path / "out.mindmap.json"

    json_format.save(doc, path)
    restored = json_format.load(path)

    assert restored.to_dict() == doc.to_dict()


def test_loads_rejects_missing_format_field():
    with pytest.raises(MindMapIOError):
        json_format.loads('{"root": {"id": "x", "title": "t", "children": []}}')


def test_loads_rejects_invalid_json():
    with pytest.raises(MindMapIOError):
        json_format.loads("not json at all {")


def test_load_missing_file_raises(tmp_path):
    with pytest.raises(MindMapIOError):
        json_format.load(tmp_path / "does_not_exist.mindmap.json")
