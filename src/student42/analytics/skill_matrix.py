"""
Dynamic Skill Mastery Matrix.
Tracks student proficiency levels across systems concepts and flags learning gaps.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from student42.database.connection import get_db_manager
from student42.database.models import SkillMastery
from student42.database.repository import SkillRepository


@dataclass
class SkillReport:
    concept: str
    mastery_percentage: float
    total_tests: int
    is_weakness: bool


class SkillMatrix:
    """Evaluates student mastery and isolates recurring weaknesses."""

    CONCEPT_MAP: Dict[str, List[str]] = {
        "pointers": ["ft_strlen", "ft_strchr", "ft_strrchr", "ft_strnstr"],
        "memory_allocation": ["ft_calloc", "ft_strdup", "ft_substr", "ft_strjoin", "ft_split"],
        "memory_manipulation": ["ft_memset", "ft_bzero", "ft_memcpy", "ft_memmove", "ft_memchr", "ft_memcmp"],
        "ascii_and_types": ["ft_isalpha", "ft_isdigit", "ft_isalnum", "ft_isascii", "ft_isprint", "ft_toupper", "ft_tolower"],
        "linked_lists": ["ft_lstnew", "ft_lstadd_front", "ft_lstsize", "ft_lstlast", "ft_lstadd_back", "ft_lstdelone", "ft_lstclear"],
    }

    def __init__(self, student_id: int) -> None:
        self.student_id = student_id

    def get_profile_report(self) -> List[SkillReport]:
        """Calculates current mastery across all registered concepts."""
        db = get_db_manager()
        reports: List[SkillReport] = []

        with db.session() as session:
            repo = SkillRepository(session)
            skills = repo.get_student_skills(self.student_id)
            skill_dict = {s.concept: s for s in skills}

            for concept in self.CONCEPT_MAP.keys():
                record = skill_dict.get(concept)
                if not record:
                    reports.append(
                        SkillReport(
                            concept=concept,
                            mastery_percentage=0.0,
                            total_tests=0,
                            is_weakness=False,
                        )
                    )
                else:
                    total = record.success_count + record.failure_count
                    is_weak = record.mastery_level < 65.0 and total >= 3
                    reports.append(
                        SkillReport(
                            concept=concept,
                            mastery_percentage=record.mastery_level,
                            total_tests=total,
                            is_weakness=is_weak,
                        )
                    )

        return reports

    def get_critical_weaknesses(self) -> List[str]:
        """Returns concepts where student has high failure rates."""
        reports = self.get_profile_report()
        return [r.concept for r in reports if r.is_weakness]