from pymindmap.commands import (
    AddChildCommand,
    CommandHistory,
    MoveCommand,
    RemoveCommand,
    RenameCommand,
    ReparentCommand,
    RestyleCommand,
)
from pymindmap.model import MindMap, Node


def make_doc():
    doc = MindMap(title="Test")
    a = doc.root.add_child(Node(title="A"))
    doc.root.add_child(Node(title="B"))
    return doc, a


def test_add_child_apply_and_undo():
    doc, _ = make_doc()
    before = doc.to_dict()

    cmd = AddChildCommand(parent_id=doc.root.id, new_node=Node(title="New"))
    cmd.apply(doc)
    assert any(n.title == "New" for n in doc.walk())

    cmd.undo(doc)
    assert doc.to_dict() == before


def test_remove_apply_and_undo_restores_position():
    doc, a = make_doc()
    before = doc.to_dict()

    cmd = RemoveCommand(node_id=a.id)
    cmd.apply(doc)
    assert doc.find_by_id(a.id) is None

    cmd.undo(doc)
    assert doc.to_dict() == before


def test_reparent_apply_and_undo():
    doc = MindMap(title="Test")
    a = doc.root.add_child(Node(title="A"))
    b = doc.root.add_child(Node(title="B"))
    grandchild = a.add_child(Node(title="GC"))
    before = doc.to_dict()

    cmd = ReparentCommand(node_id=grandchild.id, new_parent_id=b.id)
    cmd.apply(doc)
    assert grandchild.parent is b

    cmd.undo(doc)
    assert doc.to_dict() == before


def test_rename_apply_and_undo():
    doc, a = make_doc()
    cmd = RenameCommand(node_id=a.id, new_title="Renamed")
    cmd.apply(doc)
    assert a.title == "Renamed"
    cmd.undo(doc)
    assert a.title == "A"


def test_restyle_apply_and_undo():
    doc, a = make_doc()
    original_fill = a.style.fill_color
    cmd = RestyleCommand(node_id=a.id, fill_color="#FF0000")
    cmd.apply(doc)
    assert a.style.fill_color == "#FF0000"
    cmd.undo(doc)
    assert a.style.fill_color == original_fill


def test_move_apply_and_undo():
    doc, a = make_doc()
    cmd = MoveCommand(node_id=a.id, new_x=100.0, new_y=200.0)
    cmd.apply(doc)
    assert (a.x, a.y) == (100.0, 200.0)
    cmd.undo(doc)
    assert (a.x, a.y) == (None, None)


def test_command_history_do_undo_redo():
    doc, a = make_doc()
    history = CommandHistory()

    history.do(RenameCommand(node_id=a.id, new_title="X"), doc)
    assert a.title == "X"
    assert history.can_undo()
    assert not history.can_redo()

    history.undo(doc)
    assert a.title == "A"
    assert history.can_redo()

    history.redo(doc)
    assert a.title == "X"


def test_new_command_after_undo_clears_redo_stack():
    doc, a = make_doc()
    history = CommandHistory()

    history.do(RenameCommand(node_id=a.id, new_title="X"), doc)
    history.undo(doc)
    assert history.can_redo()

    history.do(RenameCommand(node_id=a.id, new_title="Y"), doc)
    assert not history.can_redo()
    assert a.title == "Y"


def test_undo_redo_on_empty_history_returns_false():
    doc, _ = make_doc()
    history = CommandHistory()
    assert history.undo(doc) is False
    assert history.redo(doc) is False
