"""Export a MindMap as a nested Markdown bullet-list outline."""

from __future__ import annotations

from pathlib import Path
from typing import Union

from pymindmap.model import MindMap, Node


def to_markdown(doc: MindMap) -> str:
    lines = []

    def emit(node: Node, depth: int) -> None:
        lines.append(f"{'  ' * depth}- {node.title}")
        for child in node.children:
            emit(child, depth + 1)

    emit(doc.root, 0)
    return "\n".join(lines) + "\n"


def export_markdown(doc: MindMap, path: Union[str, Path]) -> None:
    Path(path).write_text(to_markdown(doc), encoding="utf-8")
