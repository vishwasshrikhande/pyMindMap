class ModelError(Exception):
    """Raised for invalid mutations of the mind map data model (e.g. cycles)."""


class MindMapIOError(Exception):
    """Raised when a mind map file cannot be parsed or is malformed."""
