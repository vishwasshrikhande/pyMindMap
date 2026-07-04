"""Command-pattern undo/redo for mind map edits. No GUI dependencies."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Protocol

from pymindmap.model import MindMap, Node, NodeStyle


class Command(Protocol):
    def apply(self, doc: MindMap) -> None: ...
    def undo(self, doc: MindMap) -> None: ...


@dataclass
class AddChildCommand:
    parent_id: str
    new_node: Node = field(default_factory=Node)

    def apply(self, doc: MindMap) -> None:
        parent = doc.find_by_id(self.parent_id)
        parent.add_child(self.new_node)

    def undo(self, doc: MindMap) -> None:
        self.new_node.remove()


@dataclass
class RemoveCommand:
    node_id: str
    _saved_parent_id: Optional[str] = field(init=False, default=None)
    _saved_index: Optional[int] = field(init=False, default=None)
    _saved_node: Optional[Node] = field(init=False, default=None)

    def apply(self, doc: MindMap) -> None:
        node = doc.find_by_id(self.node_id)
        self._saved_parent_id = node.parent.id
        self._saved_index = node.sibling_index()
        self._saved_node = node
        node.remove()

    def undo(self, doc: MindMap) -> None:
        parent = doc.find_by_id(self._saved_parent_id)
        parent.add_child(self._saved_node, index=self._saved_index)


@dataclass
class ReparentCommand:
    node_id: str
    new_parent_id: str
    new_index: Optional[int] = None
    _old_parent_id: Optional[str] = field(init=False, default=None)
    _old_index: Optional[int] = field(init=False, default=None)

    def apply(self, doc: MindMap) -> None:
        node = doc.find_by_id(self.node_id)
        self._old_parent_id = node.parent.id
        self._old_index = node.sibling_index()
        new_parent = doc.find_by_id(self.new_parent_id)
        node.reparent(new_parent, index=self.new_index)

    def undo(self, doc: MindMap) -> None:
        node = doc.find_by_id(self.node_id)
        old_parent = doc.find_by_id(self._old_parent_id)
        node.reparent(old_parent, index=self._old_index)


@dataclass
class RenameCommand:
    node_id: str
    new_title: str
    _old_title: Optional[str] = field(init=False, default=None)

    def apply(self, doc: MindMap) -> None:
        node = doc.find_by_id(self.node_id)
        self._old_title = node.title
        node.title = self.new_title

    def undo(self, doc: MindMap) -> None:
        node = doc.find_by_id(self.node_id)
        node.title = self._old_title


@dataclass
class RestyleCommand:
    node_id: str
    fill_color: Optional[str] = None
    text_color: Optional[str] = None
    _old_style: Optional[NodeStyle] = field(init=False, default=None)

    def apply(self, doc: MindMap) -> None:
        node = doc.find_by_id(self.node_id)
        self._old_style = NodeStyle(**node.style.to_dict())
        if self.fill_color is not None:
            node.style.fill_color = self.fill_color
        if self.text_color is not None:
            node.style.text_color = self.text_color

    def undo(self, doc: MindMap) -> None:
        node = doc.find_by_id(self.node_id)
        node.style = self._old_style


@dataclass
class MoveCommand:
    node_id: str
    new_x: float
    new_y: float
    _old_x: Optional[float] = field(init=False, default=None)
    _old_y: Optional[float] = field(init=False, default=None)

    def apply(self, doc: MindMap) -> None:
        node = doc.find_by_id(self.node_id)
        self._old_x, self._old_y = node.x, node.y
        node.x, node.y = self.new_x, self.new_y

    def undo(self, doc: MindMap) -> None:
        node = doc.find_by_id(self.node_id)
        node.x, node.y = self._old_x, self._old_y


class CommandHistory:
    def __init__(self, max_size: int = 200) -> None:
        self._undo: list = []
        self._redo: list = []
        self._max = max_size

    def do(self, cmd: Command, doc: MindMap) -> None:
        cmd.apply(doc)
        self._undo.append(cmd)
        self._redo.clear()
        if len(self._undo) > self._max:
            self._undo.pop(0)

    def undo(self, doc: MindMap) -> bool:
        if not self._undo:
            return False
        cmd = self._undo.pop()
        cmd.undo(doc)
        self._redo.append(cmd)
        return True

    def redo(self, doc: MindMap) -> bool:
        if not self._redo:
            return False
        cmd = self._redo.pop()
        cmd.apply(doc)
        self._undo.append(cmd)
        return True

    def can_undo(self) -> bool:
        return bool(self._undo)

    def can_redo(self) -> bool:
        return bool(self._redo)
