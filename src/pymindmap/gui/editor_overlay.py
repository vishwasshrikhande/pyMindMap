"""In-place rename editor: a tk.Entry positioned over a node's bbox on the canvas."""

from __future__ import annotations

import tkinter as tk

from pymindmap.commands import RenameCommand


class EditorOverlay:
    def __init__(self, view, node_id: str, bbox: tuple) -> None:
        self.view = view
        self.node_id = node_id
        self._committed = False

        node = view.app.doc.find_by_id(node_id)
        x0, y0, x1, y1 = bbox

        self.entry = tk.Entry(view)
        self.entry.insert(0, node.title)
        self.entry.select_range(0, tk.END)
        self.entry.focus_set()

        self.window_id = view.create_window(
            (x0 + x1) / 2, (y0 + y1) / 2, window=self.entry, width=x1 - x0, height=y1 - y0
        )

        self.entry.bind("<Return>", lambda e: self.commit())
        self.entry.bind("<Escape>", lambda e: self.cancel())
        self.entry.bind("<FocusOut>", lambda e: self.commit())

    def commit(self) -> None:
        if self._committed:
            return
        self._committed = True
        new_title = self.entry.get()
        self._destroy()
        node = self.view.app.doc.find_by_id(self.node_id)
        if node is not None and new_title != node.title:
            self.view.app.do(RenameCommand(node_id=self.node_id, new_title=new_title))
        else:
            self.view.redraw()

    def cancel(self) -> None:
        if self._committed:
            return
        self._committed = True
        self._destroy()
        self.view.redraw()

    def _destroy(self) -> None:
        self.view.delete(self.window_id)
        self.entry.destroy()
        if self.view._editor is self:
            self.view._editor = None
