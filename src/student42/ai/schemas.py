"""
Pydantic Schemas for Structured JSON Output from Gemini.
Enforces type safety and machine readability on AI responses.
"""

from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class AIDiagnosis(BaseModel):
    """Structured diagnostic evaluation of student code and errors."""
    problem_type: Literal["memory", "syntax", "logic", "norm", "algorithm", "boundary"] = Field(
        description="The primary classification of the student's issue"
    )
    severity: Literal["info", "warning", "error", "critical"] = Field(
        description="Severity level of the detected problem"
    )
    target_file: Optional[str] = Field(
        default=None,
        description="The source or header file containing the problem"
    )
    line_reference: Optional[int] = Field(
        default=None,
        description="Approximate line number in the source file"
    )
    concept_explained: str = Field(
        description="Explanation of the theoretical C concept involved"
    )
    observation: str = Field(
        description="Specific observation of what went wrong in execution or code"
    )
    suggested_action: str = Field(
        description="Concrete next step for the student to investigate"
    )
    hint_level: int = Field(
        ge=0, le=6,
        description="Current progressive hint ladder tier (0-6)"
    )
    hint_content: str = Field(
        description="The pedagogically graduated hint text"
    )
    code_snippet_allowed: bool = Field(
        default=False,
        description="Strictly false unless hint level 5 (scaffold) is active"
    )


class QuizQuestion(BaseModel):
    """Weakness-targeted quiz problem generated for the student."""
    concept: str = Field(description="The underlying concept being tested")
    question: str = Field(description="The technical question text")
    code_context: Optional[str] = Field(default=None, description="Optional C snippet")
    options: List[str] = Field(min_length=4, max_length=4, description="Four multiple choice answers")
    correct_option_index: int = Field(ge=0, le=3, description="Index of the correct answer (0-3)")
    explanation: str = Field(description="Detailed explanation of why the correct option is right")


class ProjectAudit(BaseModel):
    """Holistic project-level architectural evaluation."""
    architecture_score: int = Field(ge=0, le=100, description="Overall quality score 0-100")
    norm_risks: List[str] = Field(description="Potential or actual Norminette violations")
    memory_risks: List[str] = Field(description="Dangerous pointer or memory allocation patterns")
    makefile_issues: List[str] = Field(description="Defects in dependencies or targets")
    repeated_patterns: List[str] = Field(description="Redundant loops or code duplication")
    learning_observation: str = Field(description="Pedagogical summary of student habits")