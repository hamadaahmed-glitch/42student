"""
Progressive Hint Ladder Manager (Tiers 0 to 6).
Ensures the AI acts as a mentor rather than an autocomplete engine.
"""

from __future__ import annotations

from enum import IntEnum
from typing import Dict


class HintLevel(IntEnum):
    LEVEL_0_OUTCOME = 0    # Only report test/crash category
    LEVEL_1_CONCEPT = 1    # Theoretical CS concept explanation
    LEVEL_2_LOCALIZER = 2  # Point to problematic block or boundary condition
    LEVEL_3_ALGORITHM = 3  # Plain English description of the required steps
    LEVEL_4_PSEUDOCODE = 4 # Language-agnostic structured pseudocode
    LEVEL_5_SCAFFOLD = 5   # C function frame with blanks/comments
    LEVEL_6_REFERENCE = 6  # Full solution (strictly gated)


class HintLadder:
    """Manages hint escalation rules and generates system prompts for the active tier."""

    TIER_INSTRUCTIONS: Dict[HintLevel, str] = {
        HintLevel.LEVEL_0_OUTCOME: (
            "HINT LEVEL 0: State solely the category of error (e.g., Memory Leak, SIGSEGV, Logic Failure). "
            "Do NOT explain why or how to solve it."
        ),
        HintLevel.LEVEL_1_CONCEPT: (
            "HINT LEVEL 1: Explain the abstract low-level concept (e.g., how the stack vs heap works, "
            "what undefined behavior in memcpy means). Do NOT reference specific variables in the student's file."
        ),
        HintLevel.LEVEL_2_LOCALIZER: (
            "HINT LEVEL 2: Direct the student's eyes to the specific loop, null-check, or variable boundary. "
            "Tell them WHERE the state goes invalid, but not how to fix it."
        ),
        HintLevel.LEVEL_3_ALGORITHM: (
            "HINT LEVEL 3: Describe the logical sequence of operations required in plain English sentences. "
            "No code or syntax allowed."
        ),
        HintLevel.LEVEL_4_PSEUDOCODE: (
            "HINT LEVEL 4: Provide structured, language-agnostic pseudocode steps. Do not write C."
        ),
        HintLevel.LEVEL_5_SCAFFOLD: (
            "HINT LEVEL 5: Provide a C code scaffold with comments marking where the student must insert "
            "their own logic. Keep the critical lines empty."
        ),
        HintLevel.LEVEL_6_REFERENCE: (
            "HINT LEVEL 6: Full pedagogical breakdown. Explain the canonical implementation."
        ),
    }

    @classmethod
    def get_tier_instruction(cls, level: int) -> str:
        safe_level = max(0, min(6, level))
        return cls.TIER_INSTRUCTIONS[HintLevel(safe_level)]

    @classmethod
    def next_level(cls, current_level: int) -> int:
        return min(6, current_level + 1)