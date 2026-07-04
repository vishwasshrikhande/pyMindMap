# pyMindMap

A simple Python mind-mapping tool: a Tkinter desktop GUI for visual editing,
plus a CLI for scripting. Saves to a native JSON format and imports/exports
FreeMind (`.mm`) files for interoperability with FreeMind/Freeplane.

No third-party runtime dependencies — everything is Python standard library
(`tkinter`, `json`, `xml.etree`, `argparse`, `dataclasses`, `uuid`).

## Install

```bash
pip install -e ".[dev]"
```

## GUI

```bash
pymindmap gui [path]
# or
python -m pymindmap [path]
```

- **Tab** — add child to selected node
- **Enter** — add sibling
- **Delete / Backspace** — delete selected node
- **F2** or double-click — rename in place
- **Arrow keys** — navigate (Up/Down = siblings, Left = parent, Right = first child)
- **Ctrl+Z / Ctrl+Y** — undo / redo
- **Ctrl+N / Ctrl+O / Ctrl+S / Ctrl+Shift+S** — new / open / save / save as
- Drag a node onto another node to reparent it; drag to empty space to reposition it manually.

File menu also has Import/Export FreeMind (`.mm`) and Export Markdown outline.

## CLI

```bash
pymindmap new demo.mindmap.json --title "My Map"
pymindmap add demo.mindmap.json --title "Idea One" --color "#FFDD88"
pymindmap show demo.mindmap.json
pymindmap validate demo.mindmap.json
pymindmap convert demo.mindmap.json --to mm -o demo.mm
pymindmap convert demo.mindmap.json --to md -o demo.md
```

An example file is checked in at `examples/demo.mindmap.json` — try
`pymindmap show examples/demo.mindmap.json` or open it in the GUI.

## Architecture

- `pymindmap/model.py` — `Node`/`MindMap` tree data model. No GUI dependency.
- `pymindmap/layout.py` — pure tree-layout algorithm (depth -> x, sibling order -> y).
- `pymindmap/commands.py` — command-pattern undo/redo (`AddChildCommand`, `ReparentCommand`, etc.).
- `pymindmap/io/` — native JSON, FreeMind `.mm`, and Markdown outline import/export.
- `pymindmap/cli.py` — argparse CLI; only the `gui` subcommand touches `tkinter`.
- `pymindmap/gui/` — the Tkinter app (`App`, `MindMapView` canvas, rename overlay, dialogs).

The model, layout, commands, and I/O layers have no `tkinter` dependency, so
they're fully unit-tested. The GUI is a thin layer that translates
mouse/keyboard events into commands issued against that tested core.

## Tests

```bash
pytest
```

The GUI was additionally smoke-tested end-to-end (node creation, rename,
undo/redo, drag-to-reparent, keyboard navigation, save/load) under Xvfb
during development, but that isn't part of the automated `pytest` suite
since it requires a Tk-enabled Python build and a display (real or virtual).
