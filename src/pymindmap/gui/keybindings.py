"""Centralized Tk event-sequence -> App method-name table.

App._build_keybindings binds each sequence to getattr(app, method_name).
Keeping the table here (rather than scattered .bind() calls) makes the
full keymap reviewable in one place.
"""

KEYBINDINGS = {
    "<Tab>": "add_child_to_selected",
    "<Return>": "add_sibling_to_selected",
    "<Delete>": "delete_selected",
    "<BackSpace>": "delete_selected",
    "<F2>": "rename_selected",
    "<Control-z>": "undo",
    "<Control-y>": "redo",
    "<Control-Shift-Z>": "redo",
    "<Up>": "select_prev_sibling",
    "<Down>": "select_next_sibling",
    "<Left>": "select_parent",
    "<Right>": "select_first_child",
    "<Control-n>": "new_file",
    "<Control-o>": "open_file_dialog",
    "<Control-s>": "save_file",
    "<Control-Shift-S>": "save_file_as",
}
