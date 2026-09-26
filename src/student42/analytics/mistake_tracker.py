"""
Categorizes execution failures, memory errors, and compiler diagnostic logs.
Logs errors into the database and tracks recurrence patterns.
"""

from __future__ import annotations

import re
from typing import Optional

from student42.database.connection import get_db_manager
from student42.database.models import Mistake
from student42.database.repository import MistakeRepository


class MistakeClassifier:
    """Classifies raw errors into pedagogical categories."""

    @staticmethod
    def classify(error_text: str) -> str:
        lowered = error_text.lower()

        if "segmentation fault" in lowered or "sigsegv" in lowered:
            return "memory_segmentation_fault"
        if "definitely lost" in lowered or "leaks" in lowered:
            return "memory_leak"
        if "uninitialised value" in lowered:
            return "memory_uninitialized"
        if "error: too_many_lines" in lowered:
            return "norm_function_length"
        if "error:" in lowered and ("line:" in lowered and "col:" in lowered):
            return "norminette_violation"
        if "error: implicit declaration" in lowered:
            return "syntax_missing_header"
        if "error:" in lowered:
            return "compiler_syntax"
        if "assert" in lowered or "expected" in lowered:
            return "logic_assertion"

        return "logic_general"

    @classmethod
    def record_failure(
        cls,
        exercise_id: int,
        raw_error: str,
        root_cause_explanation: Optional[str] = None,
    ) -> Mistake:
        """Stores or increments occurrence count of a mistake."""
        category = cls.classify(raw_error)
        db = get_db_manager()

        with db.session() as session:
            repo = MistakeRepository(session)
            mistake = repo.log_mistake(
                exercise_id=exercise_id,
                category=category,
                raw_error=raw_error[:2000],  # Bound text length
                root_cause=root_cause_explanation,
            )
            return mistake