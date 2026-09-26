"""
Socratic Tutor Agent.
Explains low-level computer science concepts and libc specifications without code-dumping.
"""

from __future__ import annotations

from student42.ai.agents.base import BaseAgent
from student42.ai.schemas import AIDiagnosis


class TutorAgent(BaseAgent):
    """Mentors students on memory, pointers, and libc theory."""

    SYSTEM_INSTRUCTION = (
        "You are the 42 Socratic Tutor. Your role is strictly pedagogical. "
        "Explain low-level system mechanics (stack, heap, pointer arithmetic, memory layout). "
        "Never write functional C code solutions for the student. Formulate thoughtful "
        "guiding questions and explain theoretical mechanics."
    )

    def explain_concept(self, topic: str, exercise_name: str | None = None) -> AIDiagnosis:
        """Provides theoretical explanation for a low-level topic within exercise scope."""
        context = self.context_builder.assemble_context(
            exercise_name=exercise_name,
            hint_level=1,
        )

        prompt = (
            f"The student is asking for a theoretical explanation regarding: '{topic}'.\n\n"
            f"Context:\n{context}\n\n"
            "Explain the concept clearly using standard 42 low-level terminology. "
            "Suggest what mental model or boundary condition they should visualize."
        )

        return self.client.generate_structured(
            prompt=prompt,
            response_model=AIDiagnosis,
            system_instruction=self.SYSTEM_INSTRUCTION,
            use_fast_model=True,
        )