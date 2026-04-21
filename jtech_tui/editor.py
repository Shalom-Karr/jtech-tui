from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path


def edit_markdown(initial: str = "", read_only: bool = False) -> str | None:
    """Open $EDITOR on a .md temp file.

    Returns the file contents after editor closes when read_only is False.
    Returns None when read_only is True (caller doesn't care about edits).
    """
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR") or "nano"
    fd, name = tempfile.mkstemp(suffix=".md", prefix="jtech-")
    path = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            if initial:
                f.write(initial)
        try:
            subprocess.run([editor, str(path)], check=False)
        except FileNotFoundError:
            return None
        if read_only:
            return None
        return path.read_text(encoding="utf-8")
    finally:
        try:
            path.unlink()
        except OSError:
            pass
