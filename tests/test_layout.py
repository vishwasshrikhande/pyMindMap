from pymindmap.layout import compute_layout
from pymindmap.model import Node


def test_single_node_layout():
    root = Node(title="Root")
    positions = compute_layout(root)
    assert positions == {root.id: (0.0, 0.0)}


def test_children_increase_depth_x():
    root = Node(title="Root")
    child = root.add_child(Node(title="Child"))
    positions = compute_layout(root, h_gap=60.0)
    root_x, _ = positions[root.id]
    child_x, _ = positions[child.id]
    assert child_x > root_x
    assert child_x - root_x == 60.0


def test_siblings_are_stacked_with_increasing_y():
    root = Node(title="Root")
    a = root.add_child(Node(title="A"))
    b = root.add_child(Node(title="B"))
    c = root.add_child(Node(title="C"))
    positions = compute_layout(root)
    ys = [positions[n.id][1] for n in (a, b, c)]
    assert ys == sorted(ys)
    assert len(set(ys)) == 3


def test_left_direction_produces_negative_x_for_children():
    root = Node(title="Root")
    child = root.add_child(Node(title="Child"))
    positions = compute_layout(root, direction="left", h_gap=60.0)
    assert positions[child.id][0] == -60.0


def test_manual_position_override_is_respected():
    root = Node(title="Root")
    child = root.add_child(Node(title="Child", x=500.0, y=999.0))
    positions = compute_layout(root)
    assert positions[child.id] == (500.0, 999.0)


def test_manual_override_subtree_laid_out_relative_to_anchor():
    root = Node(title="Root")
    child = root.add_child(Node(title="Child", x=500.0, y=999.0))
    grandchild = child.add_child(Node(title="GC"))
    positions = compute_layout(root, h_gap=60.0)
    gx, gy = positions[grandchild.id]
    assert gx == 560.0
    assert gy == 999.0


def test_collapsed_node_excludes_descendants():
    root = Node(title="Root")
    child = root.add_child(Node(title="Child", collapsed=True))
    grandchild = child.add_child(Node(title="GC"))

    positions = compute_layout(root)

    assert root.id in positions
    assert child.id in positions
    assert grandchild.id not in positions
