"""
Git repository integration for 42 Student OS.
Tracks code changes, diffs, commits, and student work patterns.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import git


class GitEngine:
    """Wraps GitPython for workspace repo tracking and diff retrieval."""

    def __init__(self, workspace_path: Path) -> None:
        self.workspace_path = workspace_path
        self._repo: Optional[git.Repo] = None
        self._load_repo()

    def _load_repo(self) -> None:
        try:
            self._repo = git.Repo(self.workspace_path, search_parent_directories=True)
        except (git.InvalidGitRepositoryError, git.NoSuchPathError):
            self._repo = None

    def is_git_repo(self) -> bool:
        return self._repo is not None

    def get_current_branch(self) -> str:
        if not self._repo:
            return "no-git"
        try:
            return self._repo.active_branch.name
        except TypeError:
            return "detached-HEAD"

    def is_clean(self) -> bool:
        if not self._repo:
            return True
        return not self._repo.is_dirty(untracked_files=True)

    def get_uncommitted_files(self) -> List[str]:
        if not self._repo:
            return []
        changed = [item.a_path for item in self._repo.index.diff(None)]
        untracked = self._repo.untracked_files
        staged = [item.a_path for item in self._repo.index.diff("HEAD")] if self._repo.head.is_valid() else []
        return sorted(list(set(changed + untracked + staged)))

    def get_file_diff(self, file_path: str) -> str:
        """Returns the unstaged + staged diff for a given relative file path."""
        if not self._repo:
            return ""
        try:
            diff_text = self._repo.git.diff("HEAD", "--", file_path)
            if not diff_text:
                diff_text = self._repo.git.diff("--", file_path)
            return diff_text
        except git.GitCommandError:
            return ""

    def get_recent_commits(self, limit: int = 5) -> List[Dict[str, Any]]:
        if not self._repo or not self._repo.head.is_valid():
            return []
        commits = []
        try:
            for commit in self._repo.iter_commits(max_count=limit):
                commits.append({
                    "hexsha": commit.hexsha[:7],
                    "message": commit.message.strip(),
                    "author": commit.author.name,
                    "timestamp": commit.authored_datetime.isoformat(),
                })
        except Exception:
            return []
        return commits