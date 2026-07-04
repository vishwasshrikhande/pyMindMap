"""Tkinter application shell: owns the document, undo history, menu, and canvas view."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional

from pymindmap.commands import AddChildCommand, Command, CommandHistory, RemoveCommand, RestyleCommand
from pymindmap.errors import MindMapIOError
from pymindmap.io import load_any, save_any
from pymindmap.model import MindMap, Node

from .canvas_view import MindMapView
from .dialogs import ask_color, ask_notes
from .keybindings import KEYBINDINGS


class App:
    def __init__(self, root: tk.Tk, initial_path: Optional[str] = None) -> None:
        self.root = root
        self.doc = MindMap()
        self.current_path: Optional[Path] = None
        self.history = CommandHistory()

        self.view = MindMapView(root, app=self)
        self.view.pack(fill="both", expand=True)

        self._build_menu()
        self._build_keybindings()

        self.root.title("pyMindMap")
        self.root.geometry("900x600")

        if initial_path:
            self.open_file(initial_path)
        else:
            self.view.select(self.doc.root.id)

    # -- menu / keybindings -------------------------------------------------

    def _build_menu(self) -> None:
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", accelerator="Ctrl+N", command=self.new_file)
        file_menu.add_command(label="Open...", accelerator="Ctrl+O", command=self.open_file_dialog)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Save As...", accelerator="Ctrl+Shift+S", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Import FreeMind (.mm)...", command=self.import_freemind)
        file_menu.add_command(label="Export FreeMind (.mm)...", command=self.export_freemind)
        file_menu.add_command(label="Export Markdown...", command=self.export_markdown)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=self.undo)
        edit_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Add Child", accelerator="Tab", command=self.add_child_to_selected)
        edit_menu.add_command(label="Add Sibling", accelerator="Enter", command=self.add_sibling_to_selected)
        edit_menu.add_command(label="Delete Node", accelerator="Delete", command=self.delete_selected)
        edit_menu.add_command(label="Rename Node", accelerator="F2", command=self.rename_selected)
        edit_menu.add_separator()
        edit_menu.add_command(label="Change Color...", command=self.change_color_of_selected)
        edit_menu.add_command(label="Edit Notes...", command=self.edit_notes_of_selected)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Redraw", command=self.view.redraw)
        menubar.add_cascade(label="View", menu=view_menu)

        self.root.config(menu=menubar)

    def _build_keybindings(self) -> None:
        for sequence, method_name in KEYBINDINGS.items():
            handler = getattr(self, method_name)
            self.root.bind_all(sequence, lambda event, handler=handler: handler(event))

    # -- undo/redo ------------------------------------------------------

    def do(self, command: Command) -> None:
        self.history.do(command, self.doc)
        self.view.redraw()

    def undo(self, event: Optional[tk.Event] = None) -> None:
        if self.history.undo(self.doc):
            self.view.redraw()

    def redo(self, event: Optional[tk.Event] = None) -> None:
        if self.history.redo(self.doc):
            self.view.redraw()

    # -- file operations ------------------------------------------------------

    def new_file(self, event: Optional[tk.Event] = None) -> None:
        self.doc = MindMap()
        self.current_path = None
        self.history = CommandHistory()
        self.view.select(self.doc.root.id)

    def open_file(self, path: str) -> None:
        try:
            self.doc = load_any(path)
        except MindMapIOError as exc:
            messagebox.showerror("Open failed", str(exc))
            return
        self.current_path = Path(path)
        self.history = CommandHistory()
        self.view.select(self.doc.root.id)

    def open_file_dialog(self, event: Optional[tk.Event] = None) -> None:
        path = filedialog.askopenfilename(filetypes=[("Mind maps", "*.json *.mm"), ("All files", "*.*")])
        if path:
            self.open_file(path)

    def save_file(self, event: Optional[tk.Event] = None) -> None:
        if self.current_path is None:
            self.save_file_as()
            return
        save_any(self.doc, self.current_path)

    def save_file_as(self, event: Optional[tk.Event] = None) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Mind maps", "*.json")])
        if not path:
            return
        self.current_path = Path(path)
        save_any(self.doc, self.current_path)

    def import_freemind(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("FreeMind", "*.mm")])
        if path:
            self.open_file(path)

    def export_freemind(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".mm", filetypes=[("FreeMind", "*.mm")])
        if path:
            save_any(self.doc, path, fmt="mm")

    def export_markdown(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown", "*.md")])
        if path:
            save_any(self.doc, path, fmt="md")

    # -- selection-driven edit commands ------------------------------------------------------

    def _selected_node(self) -> Optional[Node]:
        node_id = self.view.selected_id()
        if node_id is None:
            return None
        return self.doc.find_by_id(node_id)

    def add_child_to_selected(self, event: Optional[tk.Event] = None) -> None:
        parent = self._selected_node() or self.doc.root
        new_node = Node(title="New Node")
        self.do(AddChildCommand(parent_id=parent.id, new_node=new_node))
        self.view.select(new_node.id)
        self.view.begin_rename(new_node.id)

    def add_sibling_to_selected(self, event: Optional[tk.Event] = None) -> None:
        selected = self._selected_node()
        if selected is None or selected.parent is None:
            self.add_child_to_selected(event)
            return
        new_node = Node(title="New Node")
        self.do(AddChildCommand(parent_id=selected.parent.id, new_node=new_node))
        self.view.select(new_node.id)
        self.view.begin_rename(new_node.id)

    def delete_selected(self, event: Optional[tk.Event] = None) -> None:
        selected = self._selected_node()
        if selected is None or selected.parent is None:
            return
        parent_id = selected.parent.id
        self.do(RemoveCommand(node_id=selected.id))
        self.view.select(parent_id)

    def rename_selected(self, event: Optional[tk.Event] = None) -> None:
        selected = self._selected_node()
        if selected is not None:
            self.view.begin_rename(selected.id)

    def change_color_of_selected(self) -> None:
        selected = self._selected_node()
        if selected is None:
            return
        color = ask_color(self.root, selected.style.fill_color)
        self.do(RestyleCommand(node_id=selected.id, fill_color=color))

    def edit_notes_of_selected(self) -> None:
        selected = self._selected_node()
        if selected is None:
            return
        notes = ask_notes(self.root, f"Notes for {selected.title}", selected.notes)
        selected.notes = notes
        self.view.redraw()

    # -- keyboard navigation -----------------------------------------------

    def select_prev_sibling(self, event: Optional[tk.Event] = None) -> None:
        selected = self._selected_node()
        if selected is None or selected.parent is None:
            return
        siblings = selected.parent.children
        idx = siblings.index(selected)
        if idx > 0:
            self.view.select(siblings[idx - 1].id)

    def select_next_sibling(self, event: Optional[tk.Event] = None) -> None:
        selected = self._selected_node()
        if selected is None or selected.parent is None:
            return
        siblings = selected.parent.children
        idx = siblings.index(selected)
        if idx < len(siblings) - 1:
            self.view.select(siblings[idx + 1].id)

    def select_parent(self, event: Optional[tk.Event] = None) -> None:
        selected = self._selected_node()
        if selected is not None and selected.parent is not None:
            self.view.select(selected.parent.id)

    def select_first_child(self, event: Optional[tk.Event] = None) -> None:
        selected = self._selected_node()
        if selected is not None and selected.children:
            self.view.select(selected.children[0].id)
