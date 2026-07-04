"""Command-line interface for pymindmap. Only the `gui` subcommand touches tkinter."""

from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence

from pymindmap.errors import MindMapIOError, ModelError
from pymindmap.io import load_any, save_any
from pymindmap.io.json_format import save as save_json
from pymindmap.model import MindMap, Node


def _print_tree(node: Node, depth: int = 0) -> None:
    print(f"{'  ' * depth}- {node.title} ({node.id})")
    for child in node.children:
        _print_tree(child, depth + 1)


def _cmd_new(args: argparse.Namespace) -> int:
    doc = MindMap(title=args.title)
    save_json(doc, args.path)
    print(f"Created {args.path}")
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    doc = load_any(args.path)
    if args.format == "json":
        from pymindmap.io.json_format import dumps

        print(dumps(doc))
    else:
        print(doc.title)
        _print_tree(doc.root)
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    load_any(args.path)
    print("OK")
    return 0


def _cmd_convert(args: argparse.Namespace) -> int:
    doc = load_any(args.input, fmt=args.from_format)
    save_any(doc, args.output, fmt=args.to_format)
    print(f"Wrote {args.output}")
    return 0


def _cmd_add(args: argparse.Namespace) -> int:
    doc = load_any(args.path)
    parent = doc.root if args.parent in (None, "root") else doc.find_by_id(args.parent)
    if parent is None:
        raise ModelError(f"No node with id {args.parent!r} found in {args.path}")

    node = Node(title=args.title, notes=args.notes or "")
    if args.color:
        node.style.fill_color = args.color
    parent.add_child(node)
    save_any(doc, args.path)
    print(f"Added node {node.id} under {parent.id}")
    return 0


def _cmd_gui(args: argparse.Namespace) -> int:
    import tkinter as tk

    from pymindmap.gui.app import App

    root = tk.Tk()
    App(root, initial_path=args.path)
    root.mainloop()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pymindmap", description="A simple mind mapping tool.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_new = subparsers.add_parser("new", help="Create a new mind map file.")
    p_new.add_argument("path")
    p_new.add_argument("--title", default="Untitled Mind Map")
    p_new.set_defaults(func=_cmd_new)

    p_show = subparsers.add_parser("show", help="Print a mind map file.")
    p_show.add_argument("path")
    p_show.add_argument("--format", choices=["tree", "json"], default="tree")
    p_show.set_defaults(func=_cmd_show)

    p_validate = subparsers.add_parser("validate", help="Check that a mind map file loads cleanly.")
    p_validate.add_argument("path")
    p_validate.set_defaults(func=_cmd_validate)

    p_convert = subparsers.add_parser("convert", help="Convert between mind map formats.")
    p_convert.add_argument("input")
    p_convert.add_argument("--from", dest="from_format", choices=["json", "mm"], default=None)
    p_convert.add_argument("--to", dest="to_format", choices=["json", "mm", "md"], required=True)
    p_convert.add_argument("-o", "--output", dest="output", required=True)
    p_convert.set_defaults(func=_cmd_convert)

    p_add = subparsers.add_parser("add", help="Add a node to a mind map file in place.")
    p_add.add_argument("path")
    p_add.add_argument("--parent", default="root")
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--notes", default=None)
    p_add.add_argument("--color", default=None)
    p_add.set_defaults(func=_cmd_add)

    p_gui = subparsers.add_parser("gui", help="Launch the Tkinter GUI.")
    p_gui.add_argument("path", nargs="?", default=None)
    p_gui.set_defaults(func=_cmd_gui)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (MindMapIOError, ModelError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
