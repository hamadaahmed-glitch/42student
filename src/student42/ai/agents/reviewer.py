"""
Code Reviewer Agent.
Audits code against Norminette rules, complexity, naming, and redundancy.
"""

from __future__ import annotations

from student42.ai.agents.base import BaseAgent
from student42.ai.schemas import AIDiagnosis


class CodeReviewerAgent(BaseAgent):
    """Audits C code architecture without refactoring it on the student's behalf."""

    SYSTEM_INSTRUCTION = (
        "You are the 42 Code Reviewer. Audit the student's code against Norminette rules, "
        "variable scoping, line counts, duplicate loops, and memory safety hygiene. "
        "Do not rewrite the code. Point out code smells, unhandled NULL cases, and Norm violations."
    )

    def review_exercise(self, exercise_name: str) -> AIDiagnosis:
        """Performs static code review of an exercise source file."""
        context = self.context_builder.assemble_context(
            exercise_name=exercise_name,
            hint_level=2,
        )

        prompt = (
            f"Perform a thorough code hygiene and Norm review for '{exercise_name}.c'.\n\n"
            f"{context}\n\n"
            "Assess line counts, pointer checks, helper function declarations, and redundancy."
        )

        return self.client.generate_structured(
            prompt=prompt,
            response_model=AIDiagnosis,
            system_instruction=self.SYSTEM_INSTRUCTION,
            use_fast_model=False,
        )