import pytest

from pymindmap.errors import ModelError
from pymindmap.model import MindMap, Node, NodeStyle


def test_add_child_sets_parent_and_appends():
    root = Node(title="Root")
    child = root.add_child(Node(title="Child"))
    assert child.parent is root
    assert root.children == [child]


def test_add_child_with_index_inserts_at_position():
    root = Node(title="Root")
    a = root.add_child(Node(title="A"))
    b = root.add_child(Node(title="B"))
    c = root.add_child(Node(title="C"), index=1)
    assert root.children == [a, c, b]


def test_remove_detaches_from_parent():
    root = Node(title="Root")
    child = root.add_child(Node(title="Child"))
    child.remove()
    assert root.children == []
    assert child.parent is None


def test_remove_root_raises():
    root = Node(title="Root")
    with pytest.raises(ModelError):
        root.remove()


def test_reparent_moves_node_and_subtree():
    root = Node(title="Root")
    a = root.add_child(Node(title="A"))
    b = root.add_child(Node(title="B"))
    grandchild = a.add_child(Node(title="GC"))

    a.reparent(b)

    assert a.parent is b
    assert b.children == [a]
    assert root.children == [b]
    assert grandchild.parent is a


def test_reparent_under_self_raises():
    root = Node(title="Root")
    a = root.add_child(Node(title="A"))
    with pytest.raises(ModelError):
        a.reparent(a)


def test_reparent_under_own_descendant_raises():
    root = Node(title="Root")
    a = root.add_child(Node(title="A"))
    grandchild = a.add_child(Node(title="GC"))
    with pytest.raises(ModelError):
        a.reparent(grandchild)


def test_reparent_root_raises():
    root = Node(title="Root")
    child = root.add_child(Node(title="Child"))
    with pytest.raises(ModelError):
        root.reparent(child)


def test_walk_is_depth_first_preorder():
    root = Node(title="Root")
    a = root.add_child(Node(title="A"))
    a.add_child(Node(title="A1"))
    root.add_child(Node(title="B"))

    titles = [n.title for n in root.walk()]
    assert titles == ["Root", "A", "A1", "B"]


def test_find_by_id_locates_descendant():
    root = Node(title="Root")
    child = root.add_child(Node(title="Child"))
    assert root.find_by_id(child.id) is child
    assert root.find_by_id("does-not-exist") is None


def test_depth_and_sibling_index():
    root = Node(title="Root")
    a = root.add_child(Node(title="A"))
    b = root.add_child(Node(title="B"))
    grandchild = a.add_child(Node(title="GC"))

    assert root.depth() == 0
    assert a.depth() == 1
    assert grandchild.depth() == 2
    assert b.sibling_index() == 1


def test_node_to_dict_from_dict_round_trip():
    root = Node(title="Root", notes="root notes", style=NodeStyle(fill_color="#ABCDEF"))
    root.add_child(Node(title="Child", x=10.0, y=20.0))

    restored = Node.from_dict(root.to_dict())

    assert restored.title == root.title
    assert restored.notes == root.notes
    assert restored.style == root.style
    assert restored.children[0].title == "Child"
    assert restored.children[0].x == 10.0
    assert restored.children[0].parent is restored


def test_mindmap_to_dict_from_dict_round_trip():
    doc = MindMap(title="My Map")
    doc.root.add_child(Node(title="Idea"))

    d = doc.to_dict()
    assert d["format"] == "pymindmap"
    assert d["version"] == 1

    restored = MindMap.from_dict(d)
    assert restored.title == "My Map"
    assert [n.title for n in restored.walk()] == ["Central Topic", "Idea"]
