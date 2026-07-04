"""Pure tree-layout algorithm. No GUI dependencies; operates on model.Node."""

from __future__ import annotations

from pymindmap.model import Node


def compute_layout(
    root: Node,
    *,
    direction: str = "right",
    h_gap: float = 60.0,
    v_gap: float = 30.0,
) -> dict:
    """Compute (x, y) for every visible node in the tree rooted at `root`.

    Nodes that already have a manual (x, y) override keep it; their subtree is
    laid out relative to that anchor. Children of a collapsed node are excluded
    from the returned positions (and not laid out at all).

    Returns: dict mapping node.id -> (x, y).
    """
    positions: dict = {}
    sign = 1.0 if direction == "right" else -1.0

    def visible_children(node: Node) -> list:
        if node.collapsed:
            return []
        return node.children

    def subtree_height(node: Node) -> float:
        children = visible_children(node)
        if not children:
            return v_gap
        return sum(subtree_height(c) for c in children) + v_gap * max(0, len(children) - 1)

    def layout(node: Node, x: float, top: float) -> None:
        height = subtree_height(node)
        if node.x is not None and node.y is not None:
            x, y = node.x, node.y
        else:
            y = top + height / 2.0

        positions[node.id] = (x, y)

        child_x = x + sign * h_gap
        cursor = y - height / 2.0
        for child in visible_children(node):
            layout(child, child_x, cursor)
            cursor += subtree_height(child)

    layout(root, 0.0, -subtree_height(root) / 2.0)
    return positions
