"""Core mind map data model. Must never import tkinter or anything GUI-related."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Iterator, Optional

from pymindmap.errors import ModelError


def new_id() -> str:
    return str(uuid.uuid4())


@dataclass
class NodeStyle:
    fill_color: str = "#FFFFFF"
    text_color: str = "#000000"
    font_family: Optional[str] = None
    font_size: Optional[int] = None
    bold: bool = False
    italic: bool = False

    def to_dict(self) -> dict:
        return {
            "fill_color": self.fill_color,
            "text_color": self.text_color,
            "font_family": self.font_family,
            "font_size": self.font_size,
            "bold": self.bold,
            "italic": self.italic,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "NodeStyle":
        return cls(
            fill_color=d.get("fill_color", "#FFFFFF"),
            text_color=d.get("text_color", "#000000"),
            font_family=d.get("font_family"),
            font_size=d.get("font_size"),
            bold=d.get("bold", False),
            italic=d.get("italic", False),
        )


@dataclass
class Node:
    id: str = field(default_factory=new_id)
    title: str = "New Node"
    notes: str = ""
    style: NodeStyle = field(default_factory=NodeStyle)
    x: Optional[float] = None
    y: Optional[float] = None
    collapsed: bool = False
    children: list = field(default_factory=list)
    parent: Optional["Node"] = field(default=None, repr=False, compare=False)

    def add_child(self, node: Optional["Node"] = None, *, index: Optional[int] = None) -> "Node":
        if node is None:
            node = Node()
        node.parent = self
        if index is None:
            self.children.append(node)
        else:
            self.children.insert(index, node)
        return node

    def remove(self) -> None:
        if self.parent is None:
            raise ModelError("Cannot remove the root node of a mind map.")
        self.parent.children.remove(self)
        self.parent = None

    def reparent(self, new_parent: "Node", *, index: Optional[int] = None) -> None:
        if new_parent is self or self.find_by_id(new_parent.id) is not None:
            raise ModelError("Cannot reparent a node under itself or one of its own descendants.")
        old_parent = self.parent
        if old_parent is None:
            raise ModelError("Cannot reparent the root node of a mind map.")
        old_parent.children.remove(self)
        self.parent = new_parent
        if index is None:
            new_parent.children.append(self)
        else:
            new_parent.children.insert(index, self)

    def walk(self) -> Iterator["Node"]:
        yield self
        for child in self.children:
            yield from child.walk()

    def find_by_id(self, node_id: str) -> Optional["Node"]:
        for node in self.walk():
            if node.id == node_id:
                return node
        return None

    def depth(self) -> int:
        d = 0
        node = self
        while node.parent is not None:
            d += 1
            node = node.parent
        return d

    def sibling_index(self) -> int:
        if self.parent is None:
            return 0
        return self.parent.children.index(self)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "notes": self.notes,
            "collapsed": self.collapsed,
            "x": self.x,
            "y": self.y,
            "style": self.style.to_dict(),
            "children": [child.to_dict() for child in self.children],
        }

    @classmethod
    def from_dict(cls, d: dict, parent: Optional["Node"] = None) -> "Node":
        node = cls(
            id=d.get("id") or new_id(),
            title=d.get("title", "New Node"),
            notes=d.get("notes", ""),
            style=NodeStyle.from_dict(d.get("style", {})),
            x=d.get("x"),
            y=d.get("y"),
            collapsed=d.get("collapsed", False),
            parent=parent,
        )
        node.children = [Node.from_dict(child_d, parent=node) for child_d in d.get("children", [])]
        return node


@dataclass
class MindMap:
    root: Node = field(default_factory=lambda: Node(title="Central Topic"))
    version: int = 1
    title: str = "Untitled Mind Map"

    def find_by_id(self, node_id: str) -> Optional[Node]:
        return self.root.find_by_id(node_id)

    def walk(self) -> Iterator[Node]:
        yield from self.root.walk()

    def to_dict(self) -> dict:
        return {
            "format": "pymindmap",
            "version": self.version,
            "title": self.title,
            "root": self.root.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "MindMap":
        return cls(
            root=Node.from_dict(d["root"]),
            version=d.get("version", 1),
            title=d.get("title", "Untitled Mind Map"),
        )
