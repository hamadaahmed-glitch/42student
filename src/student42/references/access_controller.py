"""
Policy access controller for student references.
Regulates visibility of solutions based on mode: Strict, Study, or Free.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Dict, Optional


class AccessMode(str, Enum):
    STRICT = "strict"  # Completely locked until exercise passes
    STUDY = "study"    # Can view architecture/signatures, full logic masked
    FREE = "free"      # Full access unlocked


class AccessController:
    """Enforces pedagogical gatekeeping on reference solutions."""

    @staticmethod
    def can_view_reference(
        mode: AccessMode,
        is_exercise_completed: bool,
        is_explicitly_unlocked: bool,
    ) -> bool:
        """Determines if a reference solution file can be opened."""
        if mode == AccessMode.FREE:
            return True
        if is_explicitly_unlocked or is_exercise_completed:
            return True
        if mode == AccessMode.STUDY:
            return True
        return False

    @classmethod
    def filter_source_content(
        cls,
        mode: AccessMode,
        source_code: str,
        is_completed: bool,
    ) -> str:
        """Masks internal function implementations when in Study mode."""
        if mode == AccessMode.FREE or is_completed:
            return source_code

        if mode == AccessMode.STRICT:
            return "/* [LOCKED] Strict Mode Active. Pass all unit tests to unlock this reference. */"

        # Study Mode: Mask function bodies, retain comments, signatures, and includes
        masked_lines = []
        brace_depth = 0

        for line in source_code.splitlines():
            stripped = line.strip()

            if brace_depth == 0:
                masked_lines.append(line)
                if "{" in stripped and not stripped.startswith("//"):
                    brace_depth += stripped.count("{") - stripped.count("}")
                    if brace_depth > 0:
                        masked_lines.append("\t/* [STUDY MODE: Implementation hidden. Deduce algorithm.] */")
            else:
                brace_depth += stripped.count("{") - stripped.count("}")
                if brace_depth <= 0:
                    masked_lines.append("}")
                    brace_depth = 0

        return "\n".join(masked_lines)