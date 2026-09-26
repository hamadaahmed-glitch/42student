"""
Timed Study Session and Daily Mission Controller.
Tracks active working hours, functions cleared, and daily objectives.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

from student42.analytics.skill_matrix import SkillMatrix
from student42.core.profile_manager import ProfileManager
from student42.database.connection import get_db_manager
from student42.database.models import StudySession
from student42.database.repository import ProjectRepository, StudentRepository


@dataclass
class DailyMission:
    title: str
    description: str
    target_xp: int
    completed: bool


class SessionController:
    """Controls session timers, records learning sprints, and generates daily missions."""

    def __init__(self, project_slug: str) -> None:
        self.project_slug = project_slug
        self.profile = ProfileManager()
        self.active_session_id: Optional[int] = None
        self.start_time: Optional[datetime] = None

    def start_session(self) -> int:
        """Starts a timed study session."""
        db = get_db_manager()
        with db.session() as session:
            student_repo = StudentRepository(session)
            student = student_repo.get_primary_student() or self.profile.get_profile()

            proj_repo = ProjectRepository(session)
            project = proj_repo.get_by_slug(self.project_slug)

            study_session = StudySession(
                student_id=student.id,
                project_id=project.id if project else None,
                start_time=datetime.now(timezone.utc),
            )
            session.add(study_session)
            session.flush()

            self.active_session_id = study_session.id
            self.start_time = study_session.start_time
            return study_session.id

    def end_session(self, functions_completed: int = 0, hints_used: int = 0) -> StudySession:
        """Concludes active study session and credits session XP."""
        if not self.active_session_id:
            raise RuntimeError("No active study session to conclude.")

        db = get_db_manager()
        with db.session() as session:
            study_session = session.get(StudySession, self.active_session_id)
            if not study_session:
                raise RuntimeError(f"Session {self.active_session_id} not found.")

            study_session.end_time = datetime.now(timezone.utc)
            study_session.functions_completed = functions_completed
            study_session.hints_used = hints_used

            # Session XP: 100 XP base + 50 per function - 10 per hint
            calculated_xp = max(50, 100 + (functions_completed * 50) - (hints_used * 10))
            study_session.xp_earned = calculated_xp

            student_repo = StudentRepository(session)
            student_repo.add_xp(study_session.student_id, calculated_xp)

            self.active_session_id = None
            self.start_time = None
            return study_session

    def get_daily_missions(self, student_id: int = 1) -> List[DailyMission]:
        """Dynamically generates daily learning missions tailored to student weaknesses."""
        matrix = SkillMatrix(student_id)
        weaknesses = matrix.get_critical_weaknesses()
        primary_weakness = weaknesses[0] if weaknesses else "pointers"

        return [
            DailyMission(
                title=f"Mastery Sprint: {primary_weakness.replace('_', ' ').title()}",
                description=f"Resolve failing unit tests and review edge cases for {primary_weakness}.",
                target_xp=150,
                completed=False,
            ),
            DailyMission(
                title="Norminette Perfection",
                description="Pass 3 consecutive functions with zero Norminette warnings.",
                target_xp=100,
                completed=False,
            ),
            DailyMission(
                title="Zero Leak Protocol",
                description="Execute full Valgrind check on 2 functions with 0 bytes definitely lost.",
                target_xp=100,
                completed=False,
            ),
        ]