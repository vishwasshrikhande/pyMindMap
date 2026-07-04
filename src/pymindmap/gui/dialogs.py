"""Small dialog helpers: color chooser and a notes editor."""

from __future__ import annotations

import tkinter as tk
from tkinter import colorchooser, simpledialog


def ask_color(parent: tk.Widget, initial_color: str) -> str:
    _, hex_color = colorchooser.askcolor(color=initial_color, parent=parent)
    return hex_color if hex_color else initial_color


class NotesDialog(simpledialog.Dialog):
    def __init__(self, parent: tk.Widget, title: str, initial_text: str) -> None:
        self.initial_text = initial_text
        self.result_text = None
        super().__init__(parent, title=title)

    def body(self, master: tk.Widget) -> tk.Widget:
        self.text = tk.Text(master, width=50, height=12)
        self.text.insert("1.0", self.initial_text)
        self.text.pack()
        return self.text

    def apply(self) -> None:
        self.result_text = self.text.get("1.0", tk.END).rstrip("\n")


def ask_notes(parent: tk.Widget, title: str, initial_text: str) -> str:
    dialog = NotesDialog(parent, title, initial_text)
    return dialog.result_text if dialog.result_text is not None else initial_text
