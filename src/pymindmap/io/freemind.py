"""FreeMind/Freeplane .mm (XML) import/export.

Lossy on import: FreeMind's POSITION, CREATED/MODIFIED timestamps, LINK,
icons, edge styling, and clouds are not preserved. Only TEXT, ID,
BACKGROUND_COLOR, COLOR, FOLDED, and a plain-text extraction of a
richcontent NOTE are mapped onto our model.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Union

from pymindmap.errors import MindMapIOError
from pymindmap.model import MindMap, Node, NodeStyle, new_id

_DEFAULT_FILL = "#FFFFFF"
_DEFAULT_TEXT = "#000000"


def _extract_notes(node_el: ET.Element) -> str:
    for rc in node_el.findall("richcontent"):
        if rc.get("TYPE") == "NOTE":
            text = "".join(rc.itertext())
            return text.strip()
    return ""


def _import_node(node_el: ET.Element, seen_ids: set) -> Node:
    raw_id = node_el.get("ID")
    node_id = raw_id if raw_id and raw_id not in seen_ids else new_id()
    seen_ids.add(node_id)

    node = Node(
        id=node_id,
        title=node_el.get("TEXT", ""),
        notes=_extract_notes(node_el),
        style=NodeStyle(
            fill_color=node_el.get("BACKGROUND_COLOR", _DEFAULT_FILL),
            text_color=node_el.get("COLOR", _DEFAULT_TEXT),
        ),
        collapsed=node_el.get("FOLDED", "false").lower() == "true",
    )
    for child_el in node_el.findall("node"):
        node.add_child(_import_node(child_el, seen_ids))
    return node


def import_mm(path: Union[str, Path]) -> MindMap:
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        raise MindMapIOError(f"Invalid FreeMind XML in {path}: {exc}") from exc
    except OSError as exc:
        raise MindMapIOError(f"Could not read {path}: {exc}") from exc

    map_el = tree.getroot()
    if map_el.tag != "map":
        raise MindMapIOError(f"Not a FreeMind file (expected <map> root, got <{map_el.tag}>).")

    root_node_el = map_el.find("node")
    if root_node_el is None:
        raise MindMapIOError("FreeMind file has no root <node>.")

    root = _import_node(root_node_el, seen_ids=set())
    title = root.title or "Untitled Mind Map"
    return MindMap(root=root, title=title)


def _export_node(node: Node) -> ET.Element:
    attrs = {"TEXT": node.title, "ID": node.id, "FOLDED": "true" if node.collapsed else "false"}
    if node.style.fill_color != _DEFAULT_FILL:
        attrs["BACKGROUND_COLOR"] = node.style.fill_color
    if node.style.text_color != _DEFAULT_TEXT:
        attrs["COLOR"] = node.style.text_color

    node_el = ET.Element("node", attrs)

    if node.notes:
        richcontent = ET.SubElement(node_el, "richcontent", {"TYPE": "NOTE"})
        html = ET.SubElement(richcontent, "html")
        body = ET.SubElement(html, "body")
        p = ET.SubElement(body, "p")
        p.text = node.notes

    for child in node.children:
        node_el.append(_export_node(child))

    return node_el


def export_mm(doc: MindMap, path: Union[str, Path]) -> None:
    map_el = ET.Element("map", {"version": "1.0.1"})
    map_el.append(_export_node(doc.root))
    tree = ET.ElementTree(map_el)
    ET.indent(tree)
    tree.write(path, encoding="UTF-8", xml_declaration=True)
