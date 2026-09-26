"""
Manages official subjects, external GitHub reference clones, and notes.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

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

    @staticmethod
    def sanitize_git_url(raw_url: str) -> str:
        """Converts web browser URLs like https://github.com/user/repo/tree/master to cloneable git URL."""
        clean = raw_url.strip()
        # Match github.com/user/repo and discard /tree/..., /blob/...
        match = re.match(r"(https?://github\.com/[^/]+/[^/]+?)(?:/(?:tree|blob)/.*)?$", clean)
        if match:
            base = match.group(1)
            return base if base.endswith(".git") else f"{base}.git"
        return clean

    def register_github_repo(self, repo_url: str, name: str, tags: Optional[str] = None) -> ReferenceItem:
        """Clones a GitHub repository into managed storage and records it."""
        safe_name = "".join(c for c in name if c.isalnum() or c in ("-", "_"))
        target_path = self.github_dir / safe_name
        clean_url = self.sanitize_git_url(repo_url)

        if not target_path.exists():
            try:
                git.Repo.clone_from(clean_url, target_path)
            except git.GitCommandError as e:
                raise RuntimeError(f"Git clone failed for '{clean_url}': {e.stderr.strip() if e.stderr else str(e)}")

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