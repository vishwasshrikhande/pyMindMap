"""Format dispatch by file extension."""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from pymindmap.errors import MindMapIOError
from pymindmap.model import MindMap

from . import freemind, json_format, markdown_export


def _detect_format(path: Union[str, Path]) -> str:
    suffix = Path(path).suffix.lower()
    if suffix == ".mm":
        return "mm"
    if suffix == ".md":
        return "md"
    if suffix == ".json":
        return "json"
    raise MindMapIOError(f"Cannot detect mind map format from extension: {path}")


def load_any(path: Union[str, Path], fmt: Optional[str] = None) -> MindMap:
    fmt = fmt or _detect_format(path)
    if fmt == "json":
        return json_format.load(path)
    if fmt == "mm":
        return freemind.import_mm(path)
    raise MindMapIOError(f"Unsupported format for loading: {fmt}")


def save_any(doc: MindMap, path: Union[str, Path], fmt: Optional[str] = None) -> None:
    fmt = fmt or _detect_format(path)
    if fmt == "json":
        json_format.save(doc, path)
    elif fmt == "mm":
        freemind.export_mm(doc, path)
    elif fmt == "md":
        markdown_export.export_markdown(doc, path)
    else:
        raise MindMapIOError(f"Unsupported format for saving: {fmt}")
