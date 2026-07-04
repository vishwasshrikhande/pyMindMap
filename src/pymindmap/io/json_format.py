"""Native .mindmap.json format: load/save/dumps/loads."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Union

from pymindmap.errors import MindMapIOError
from pymindmap.model import MindMap

FORMAT_MAGIC = "pymindmap"


def dumps(doc: MindMap) -> str:
    return json.dumps(doc.to_dict(), indent=2)


def loads(text: str) -> MindMap:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise MindMapIOError(f"Invalid JSON: {exc}") from exc

    if not isinstance(data, dict) or data.get("format") != FORMAT_MAGIC:
        raise MindMapIOError(
            "Not a pymindmap JSON file (missing or incorrect 'format' field)."
        )
    if "root" not in data:
        raise MindMapIOError("Malformed pymindmap file: missing 'root' node.")

    return MindMap.from_dict(data)


def save(doc: MindMap, path: Union[str, Path]) -> None:
    Path(path).write_text(dumps(doc), encoding="utf-8")


def load(path: Union[str, Path]) -> MindMap:
    p = Path(path)
    try:
        text = p.read_text(encoding="utf-8")
    except OSError as exc:
        raise MindMapIOError(f"Could not read {p}: {exc}") from exc
    return loads(text)
