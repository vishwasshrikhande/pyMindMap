"""Tkinter Canvas widget that draws, hit-tests, and drags mind map nodes.

All mutations are issued as Commands via self.app.do(...) — this view never
edits app.doc directly. Model-space coordinates (from layout.compute_layout)
are shifted by a fixed origin so the root renders near the canvas center;
the shift is undone when translating a drag back into model coordinates.
"""

from __future__ import annotations

import tkinter as tk
from typing import Optional

from pymindmap.commands import MoveCommand, ReparentCommand
from pymindmap.layout import compute_layout
from pymindmap.model import Node

NODE_HEIGHT = 32
CHAR_WIDTH = 7
MIN_NODE_WIDTH = 80
DRAG_THRESHOLD = 4


class MindMapView(tk.Canvas):
    def __init__(self, master: tk.Widget, app: "App") -> None:
        super().__init__(master, background="#F5F5F5")
        self.app = app
        self.origin_x = 140
        self.origin_y = 300

        self._node_bboxes: dict = {}
        self._selected: Optional[str] = None
        self._drag_node_id: Optional[str] = None
        self._drag_start_xy: Optional[tuple] = None
        self._drag_moved = False
        self._drop_target: Optional[str] = None
        self._editor = None

        self.bind("<ButtonPress-1>", self.start_drag)
        self.bind("<B1-Motion>", self.on_drag_motion)
        self.bind("<ButtonRelease-1>", self.end_drag)
        self.bind("<Double-Button-1>", self._on_double_click)

    # -- coordinate helpers -------------------------------------------------

    def _to_canvas(self, x: float, y: float) -> tuple:
        return (self.origin_x + x, self.origin_y + y)

    def _to_model(self, cx: float, cy: float) -> tuple:
        return (cx - self.origin_x, cy - self.origin_y)

    def _bbox_for(self, node: Node, cx: float, cy: float) -> tuple:
        width = max(MIN_NODE_WIDTH, len(node.title) * CHAR_WIDTH + 24)
        return (cx - width / 2, cy - NODE_HEIGHT / 2, cx + width / 2, cy + NODE_HEIGHT / 2)

    # -- drawing --------------------------------------------------------

    def redraw(self) -> None:
        self.delete("all")
        self._node_bboxes = {}

        doc = self.app.doc
        positions = compute_layout(doc.root)

        # connectors first, so node shapes draw on top of the lines.
        for node in doc.root.walk():
            if node.id not in positions or node.parent is None or node.parent.id not in positions:
                continue
            px, py = self._to_canvas(*positions[node.parent.id])
            cx, cy = self._to_canvas(*positions[node.id])
            self.create_line(px, py, cx, cy, fill="#999999", tags=("connector",))

        for node in doc.root.walk():
            if node.id not in positions:
                continue
            cx, cy = self._to_canvas(*positions[node.id])
            bbox = self._bbox_for(node, cx, cy)
            self._node_bboxes[node.id] = bbox

            outline = "#3366CC" if node.id == self._selected else "#666666"
            width = 3 if node.id == self._selected else 1
            self.create_rectangle(
                *bbox, fill=node.style.fill_color, outline=outline, width=width,
                tags=(f"node:{node.id}",),
            )
            if node.children and node.collapsed:
                self.create_text(bbox[2] - 6, (bbox[1] + bbox[3]) / 2, text="+", anchor="e")
            self.create_text(
                (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2,
                text=node.title, fill=node.style.text_color, tags=(f"node:{node.id}",),
            )

    # -- hit testing ------------------------------------------------------

    def node_at(self, cx: float, cy: float, *, exclude_subtree_of: Optional[str] = None) -> Optional[str]:
        exclude_ids = set()
        if exclude_subtree_of is not None:
            node = self.app.doc.find_by_id(exclude_subtree_of)
            if node is not None:
                exclude_ids = {n.id for n in node.walk()}

        for node_id, (x0, y0, x1, y1) in self._node_bboxes.items():
            if node_id in exclude_ids:
                continue
            if x0 <= cx <= x1 and y0 <= cy <= y1:
                return node_id
        return None

    # -- selection --------------------------------------------------------

    def select(self, node_id: Optional[str]) -> None:
        self._selected = node_id
        self.redraw()

    def selected_id(self) -> Optional[str]:
        return self._selected

    # -- drag handling ------------------------------------------------------

    def start_drag(self, event: tk.Event) -> None:
        node_id = self.node_at(event.x, event.y)
        self.select(node_id)
        self._drag_node_id = node_id
        self._drag_start_xy = (event.x, event.y)
        self._drag_moved = False

    def on_drag_motion(self, event: tk.Event) -> None:
        if self._drag_node_id is None or self._drag_start_xy is None:
            return
        sx, sy = self._drag_start_xy
        if abs(event.x - sx) > DRAG_THRESHOLD or abs(event.y - sy) > DRAG_THRESHOLD:
            self._drag_moved = True
            self._drop_target = self.node_at(event.x, event.y, exclude_subtree_of=self._drag_node_id)

    def end_drag(self, event: tk.Event) -> None:
        node_id = self._drag_node_id
        self._drag_node_id = None
        if node_id is None or not self._drag_moved:
            self._drag_start_xy = None
            self._drop_target = None
            return

        drop_target = self.node_at(event.x, event.y, exclude_subtree_of=node_id)
        node = self.app.doc.find_by_id(node_id)
        if drop_target is not None and drop_target != node.parent.id:
            self.app.do(ReparentCommand(node_id=node_id, new_parent_id=drop_target))
        else:
            mx, my = self._to_model(event.x, event.y)
            self.app.do(MoveCommand(node_id=node_id, new_x=mx, new_y=my))

        self._drag_start_xy = None
        self._drop_target = None

    # -- rename -----------------------------------------------------------

    def _on_double_click(self, event: tk.Event) -> None:
        node_id = self.node_at(event.x, event.y)
        if node_id is not None:
            self.select(node_id)
            self.begin_rename(node_id)

    def begin_rename(self, node_id: str) -> None:
        from pymindmap.gui.editor_overlay import EditorOverlay

        bbox = self._node_bboxes.get(node_id)
        if bbox is None:
            return
        if self._editor is not None:
            self._editor.cancel()
        self._editor = EditorOverlay(self, node_id, bbox)
