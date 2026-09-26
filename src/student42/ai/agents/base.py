"""
Base Agent Interface for all specialized Gemini personas.
"""

from __future__ import annotations

from typing import Optional

from student42.ai.client import GeminiClient
from student42.ai.context_builder import ContextBuilder


class BaseAgent:
    """Base class providing LLM client access and context resolution."""

    def __init__(self, project_slug: str, student_id: int = 1) -> None:
        self.project_slug = project_slug
        self.student_id = student_id
        self.client = GeminiClient()
        self.context_builder = ContextBuilder(project_slug, student_id)