"""
Student Profile & Gamification Controller.
Calculates XP gains, level milestones, streak tracking, and achievement updates.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Tuple

from student42.database.connection import get_db_manager
from student42.database.models import Student
from student42.database.repository import StudentRepository


class ProfileManager:
    """Manages XP calculation, levels, and streak lifecycle."""

    XP_ACTIONS: Dict[str, int] = {
        "test_passed": 50,
        "function_cleared": 100,
        "clean_norminette": 25,
        "valgrind_leak_free": 30,
        "quiz_correct": 40,
        "daily_mission_complete": 150,
    }

    def __init__(self, username: str = "cadet", campus: str = "Benguerir") -> None:
        self.username = username
        self.campus = campus
        self._ensure_student()

    def _ensure_student(self) -> Student:
        db = get_db_manager()
        with db.session() as session:
            repo = StudentRepository(session)
            return repo.get_or_create_student(self.username, self.campus)

    def get_profile(self) -> Student:
        db = get_db_manager()
        with db.session() as session:
            repo = StudentRepository(session)
            student = repo.get_primary_student()
            if not student:
                student = repo.get_or_create_student(self.username, self.campus)
            return student

    def award_xp(self, action_key: str) -> Tuple[int, int]:
        """Awards XP and calculates if a level boundary was crossed."""
        gain = self.XP_ACTIONS.get(action_key, 10)
        db = get_db_manager()
        with db.session() as session:
            repo = StudentRepository(session)
            student = repo.get_primary_student()
            if not student:
                student = repo.get_or_create_student(self.username, self.campus)

            old_level = int(student.level)
            updated = repo.add_xp(student.id, gain)
            new_level = int(updated.level)

            self._update_streak(student)
            return gain, (new_level - old_level)

    def _update_streak(self, student: Student) -> None:
        """Maintains streak counter based on UTC timestamp."""
        now = datetime.now(timezone.utc)
        if not student.last_active_date:
            student.current_streak = 1
            student.last_active_date = now
            return

        diff = now - student.last_active_date
        hours = diff.total_seconds() / 3600.0

        if hours < 24.0:
            # Same day or within 24h, streak maintained
            pass
        elif 24.0 <= hours < 48.0:
            student.current_streak += 1
        else:
            # Missed grace period, reset streak
            student.current_streak = 1

        student.last_active_date = now