from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


class EditorUnavailable(RuntimeError):
    """Raised when we can't launch an external editor."""


def _default_editor() -> str:
    """Pick a per-platform default when $EDITOR / $VISUAL are unset.

    Windows users rarely have nano on PATH, so defaulting to it made reply /
    quote-reply / edit silently no-op (subprocess raised FileNotFoundError,
    edit_markdown returned None, and the action's `if not content: return`
    swallowed it).
    """
    if sys.platform.startswith("win"):
        for candidate in ("notepad.exe", "notepad"):
            if shutil.which(candidate):
                return candidate
        return "notepad"
    for candidate in ("nano", "vim", "vi"):
        if shutil.which(candidate):
            return candidate
    return "nano"


def edit_markdown(initial: str = "", read_only: bool = False) -> str | None:
    """Open $EDITOR on a .md temp file.

    Returns the file contents after editor closes when read_only is False.
    Returns None when read_only is True (caller doesn't care about edits).
    Raises ``EditorUnavailable`` when no editor can be launched — callers
    should catch this and surface a notification instead of silently
    treating it as "user cancelled."
    """
    editor = (
        os.environ.get("VISUAL")
        or os.environ.get("EDITOR")
        or _default_editor()
    )
    fd, name = tempfile.mkstemp(suffix=".md", prefix="jtech-")
    path = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            if initial:
                f.write(initial)
        try:
            subprocess.run([editor, str(path)], check=False)
        except FileNotFoundError as e:
            raise EditorUnavailable(
                f"Could not launch editor {editor!r}. Set $EDITOR or $VISUAL "
                f"to an editor on your PATH (e.g. notepad, nano, vim, code)."
            ) from e
        if read_only:
            return None
        return path.read_text(encoding="utf-8")
    finally:
        try:
            path.unlink()
        except OSError:
            pass
