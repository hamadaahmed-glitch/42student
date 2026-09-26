"""
Context Assembly Engine.
Constructs rich, compact prompts containing constitutions, student state, code diffs, and test outputs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from student42.ai.ladder import HintLadder
from student42.analytics.skill_matrix import SkillMatrix
from student42.core.config import get_paths
from student42.database.connection import get_db_manager
from student42.database.repository import MistakeRepository, StudentRepository
from student42.workspace.file_scanner import FileScanner
from student42.workspace.git_engine import GitEngine
from student42.workspace.path_resolver import PathResolver


class ContextBuilder:
    """Assembles all dynamic project state into LLM context."""

    def __init__(self, project_slug: str, student_id: int = 1) -> None:
        self.project_slug = project_slug
        self.student_id = student_id
        self.paths = get_paths()
        self.resolver = PathResolver(project_slug)
        self.git = GitEngine(self.resolver.root)

    def load_constitution(self) -> str:
        """Loads base constitution plus project-specific constitution if present."""
        base_file = self.paths.constitutions_dir / "base_constitution.md"
        base_text = base_file.read_text(encoding="utf-8") if base_file.exists() else ""

        proj_file = self.paths.constitutions_dir / f"{self.project_slug}_constitution.md"
        proj_text = proj_file.read_text(encoding="utf-8") if proj_file.exists() else ""

        return f"{base_text}\n\n=== PROJECT-SPECIFIC CONSTITUTION ===\n{proj_text}"

    def assemble_context(
        self,
        exercise_name: Optional[str] = None,
        hint_level: int = 1,
        compiler_output: Optional[str] = None,
        norm_output: Optional[str] = None,
        valgrind_output: Optional[str] = None,
    ) -> str:
        """Constructs complete prompt context with current student and workspace state."""
        sections: List[str] = []

        # 1. Constitution & Pedagogical Directives
        sections.append("### SYSTEM PEDAGOGICAL DIRECTIVES")
        sections.append(self.load_constitution())
        sections.append(f"### ACTIVE HINT LEVEL [{hint_level}]\n{HintLadder.get_tier_instruction(hint_level)}")

        # 2. Student Profile & Weakness Snapshot
        db = get_db_manager()
        with db.session() as session:
            student_repo = StudentRepository(session)
            student = student_repo.get_primary_student()
            username = student.username if student else "peer"
            xp = student.xp if student else 0

            matrix = SkillMatrix(self.student_id)
            weaknesses = matrix.get_critical_weaknesses()

            mistake_repo = MistakeRepository(session)
            unresolved = mistake_repo.get_unresolved_mistakes()

        sections.append(
            f"### STUDENT SNAPSHOT\n"
            f"Student: {username} | XP: {xp}\n"
            f"Known Critical Weaknesses: {', '.join(weaknesses) if weaknesses else 'None registered'}\n"
            f"Unresolved Common Mistakes: {len(unresolved)}"
        )

        # 3. Exercise Source and Git Diff
        if exercise_name:
            source_file = self.resolver.find_source_file(f"{exercise_name}.c")
            if source_file and source_file.exists():
                code = FileScanner.read_file_safe(source_file)
                sections.append(f"### STUDENT CODE [{exercise_name}.c]\n```c\n{code}\n```")

                diff = self.git.get_file_diff(str(source_file.relative_to(self.resolver.root)))
                if diff:
                    sections.append(f"### RECENT GIT DIFF\n```diff\n{diff}\n```")

        # 4. Deterministic Diagnostics
        if compiler_output:
            sections.append(f"### COMPILER / BUILD LOG\n```\n{compiler_output}\n```")
        if norm_output:
            sections.append(f"### NORMINETTE VIOLATIONS\n```\n{norm_output}\n```")
        if valgrind_output:
            sections.append(f"### VALGRIND MEMORY REPORT\n```\n{valgrind_output}\n```")

        return "\n\n".join(sections)