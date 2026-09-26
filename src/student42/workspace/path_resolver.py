"""
Resolves directory paths and file locations within student workspaces.
Handles discovery of Makefiles, C source files, and header definitions.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from student42.core.config import get_settings


class PathResolver:
    """Finds and verifies physical workspace artifacts on disk."""

    def __init__(self, project_slug: str, custom_path: Optional[str] = None) -> None:
        self.project_slug = project_slug
        settings = get_settings()

        if custom_path:
            self.root = Path(custom_path).expanduser().resolve()
        else:
            self.root = (settings.default_workspace_dir / project_slug).resolve()

    def exists(self) -> bool:
        """Checks if the project root folder exists."""
        return self.root.exists() and self.root.is_dir()

    def get_makefile(self) -> Optional[Path]:
        """Locates standard Makefile at project root."""
        makefile = self.root / "Makefile"
        if makefile.exists() and makefile.is_file():
            return makefile
        return None

    def find_source_file(self, filename: str) -> Optional[Path]:
        """Recursively scans the workspace to find a specific source file."""
        if not self.exists():
            return None
        matches = list(self.root.rglob(filename))
        return matches[0] if matches else None

    def list_all_sources(self) -> List[Path]:
        """Returns all .c files in the project workspace, excluding hidden dirs."""
        if not self.exists():
            return []
        return [
            p for p in self.root.rglob("*.c")
            if not any(part.startswith(".") for part in p.parts)
        ]

    def list_all_headers(self) -> List[Path]:
        """Returns all .h files in the project workspace."""
        if not self.exists():
            return []
        return [
            p for p in self.root.rglob("*.h")
            if not any(part.startswith(".") for part in p.parts)
        ]

    def resolve_relative_path(self, relative_path: str) -> Path:
        """Safely anchors an input relative path to the workspace root."""
        resolved = (self.root / relative_path).resolve()
        if not str(resolved).startswith(str(self.root)):
            raise ValueError(f"Access violation: {relative_path} escapes workspace root.")
        return resolved