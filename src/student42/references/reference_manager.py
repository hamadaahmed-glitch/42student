"""
Manages official subjects, external GitHub reference clones, and notes.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import List, Optional

import git

from student42.core.config import get_paths
from student42.database.connection import get_db_manager
from student42.database.models import ReferenceItem
from student42.database.repository import ReferenceRepository


class ReferenceManager:
    """Manages cloning, indexing, and retrieving student references."""

    def __init__(self, project_id: int) -> None:
        self.project_id = project_id
        self.paths = get_paths()
        self.github_dir = self.paths.references_dir / "github"

    def register_github_repo(self, repo_url: str, name: str, tags: Optional[str] = None) -> ReferenceItem:
        """Clones a GitHub repository into managed storage and records it."""
        safe_name = "".join(c for c in name if c.isalnum() or c in ("-", "_"))
        target_path = self.github_dir / safe_name

        if not target_path.exists():
            git.Repo.clone_from(repo_url, target_path)

        db = get_db_manager()
        with db.session() as session:
            repo = ReferenceRepository(session)
            item = repo.add_reference(
                project_id=self.project_id,
                ref_type="github_repo",
                name=name,
                url_or_path=str(target_path),
                is_locked=True,
                tags=tags,
            )
            return item

    def get_reference_content(self, reference_id: int) -> str:
        """Reads content of a local reference safely."""
        db = get_db_manager()
        with db.session() as session:
            item = session.get(ReferenceItem, reference_id)
            if not item:
                raise ValueError(f"Reference item {reference_id} does not exist.")

            ref_path = Path(item.url_or_path)
            if not ref_path.exists():
                return f"[Error: Reference path '{ref_path}' no longer exists on disk.]"

            if ref_path.is_file():
                return ref_path.read_text(encoding="utf-8", errors="replace")

            # If directory, list file tree
            files = [str(p.relative_to(ref_path)) for p in ref_path.rglob("*") if p.is_file()]
            return f"Directory Reference [{item.name}]:\n" + "\n".join(files[:50])