"""
Debugger Agent.
Diagnoses compiler errors, segmentation faults, and Valgrind memory leaks.
"""

from __future__ import annotations

from typing import Optional

from student42.ai.agents.base import BaseAgent
from student42.ai.schemas import AIDiagnosis


class DebuggerAgent(BaseAgent):
    """Analyzes runtime failures and compiler diagnostics through the Hint Ladder."""

    SYSTEM_INSTRUCTION = (
        "You are the 42 Systems Debugger. Your job is to analyze compiler warnings, "
        "runtime segmentation faults, and Valgrind memory leak logs. "
        "Diagnose the root flaw and escalate strictly according to the active hint tier. "
        "Never give the corrected C code directly."
    )

    def diagnose_failure(
        self,
        exercise_name: str,
        hint_level: int = 1,
        compiler_log: Optional[str] = None,
        norm_log: Optional[str] = None,
        valgrind_log: Optional[str] = None,
    ) -> AIDiagnosis:
        """Evaluates an execution or build failure and returns structured guidance."""
        context = self.context_builder.assemble_context(
            exercise_name=exercise_name,
            hint_level=hint_level,
            compiler_output=compiler_log,
            norm_output=norm_log,
            valgrind_output=valgrind_log,
        )

        prompt = (
            f"Diagnose the failure for exercise '{exercise_name}'.\n\n"
            f"{context}\n\n"
            "Identify the problem type, explain the low-level cause, and provide a hint "
            f"strictly matching hint tier {hint_level}."
        )

        return self.client.generate_structured(
            prompt=prompt,
            response_model=AIDiagnosis,
            system_instruction=self.SYSTEM_INSTRUCTION,
            use_fast_model=False,
        )