"""
Quiz Generator Agent.
Generates technical multiple-choice questions targeted at identified student weaknesses.
"""

from __future__ import annotations

from student42.ai.agents.base import BaseAgent
from student42.ai.schemas import QuizQuestion
from student42.analytics.skill_matrix import SkillMatrix


class QuizzerAgent(BaseAgent):
    """Generates low-level C multiple-choice challenges."""

    SYSTEM_INSTRUCTION = (
        "You are the 42 Peer Examiner. Generate low-level C multiple-choice questions "
        "that test deep comprehension of pointers, memory segments, bitwise operations, "
        "and standard library edge cases. Always supply exactly 4 distinct options."
    )

    def generate_quiz(self, target_concept: str | None = None) -> QuizQuestion:
        """Generates a multiple choice question targeted at student weaknesses."""
        if not target_concept:
            matrix = SkillMatrix(self.student_id)
            weaknesses = matrix.get_critical_weaknesses()
            concept = weaknesses[0] if weaknesses else "pointers"
        else:
            concept = target_concept

        prompt = (
            f"Generate a technical multiple-choice question targeting the concept: '{concept}'.\n"
            "Focus on low-level intricacies (e.g., pointer dereferencing, buffer boundaries, "
            "allocation size calculations, operator precedence). Ensure 4 options and a clear explanation."
        )

        return self.client.generate_structured(
            prompt=prompt,
            response_model=QuizQuestion,
            system_instruction=self.SYSTEM_INSTRUCTION,
            use_fast_model=True,
        )