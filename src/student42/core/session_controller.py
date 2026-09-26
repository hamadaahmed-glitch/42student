"""
Timed Study Session and Daily Mission Controller.
Persists active sessions to SQLite across separate CLI process executions.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import desc, select

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
    """Controls session timers and records learning sprints via persistent database state."""

    def __init__(self, project_slug: str) -> None:
        self.project_slug = project_slug
        self.profile = ProfileManager()

    def get_open_session(self) -> Optional[StudySession]:
        """Finds any ongoing session where end_time is NULL."""
        db = get_db_manager()
        with db.session() as session:
            student = self.profile.get_profile()
            stmt = (
                select(StudySession)
                .where(StudySession.student_id == student.id, StudySession.end_time == None)
                .order_by(desc(StudySession.start_time))
                .limit(1)
            )
            return session.execute(stmt).scalar_one_or_none()

    def start_session(self) -> int:
        """Starts a timed study session."""
        existing = self.get_open_session()
        if existing:
            return existing.id

        db = get_db_manager()
        with db.session() as session:
            student = self.profile.get_profile()
            proj_repo = ProjectRepository(session)
            project = proj_repo.get_by_slug(self.project_slug)

            study_session = StudySession(
                student_id=student.id,
                project_id=project.id if project else None,
                start_time=datetime.now(timezone.utc),
            )
            session.add(study_session)
            session.flush()
            return study_session.id

    def end_session(self, functions_completed: int = 0, hints_used: int = 0) -> StudySession:
        """Concludes active study session and credits session XP."""
        db = get_db_manager()
        with db.session() as session:
            student = self.profile.get_profile()
            stmt = (
                select(StudySession)
                .where(StudySession.student_id == student.id, StudySession.end_time == None)
                .order_by(desc(StudySession.start_time))
                .limit(1)
            )
            study_session = session.execute(stmt).scalar_one_or_none()

            if not study_session:
                raise RuntimeError("No active study session to conclude. Start one with '42student session start'.")

            study_session.end_time = datetime.now(timezone.utc)
            study_session.functions_completed = functions_completed
            study_session.hints_used = hints_used

            calculated_xp = max(50, 100 + (functions_completed * 50) - (hints_used * 10))
            study_session.xp_earned = calculated_xp

            student_repo = StudentRepository(session)
            student_repo.add_xp(study_session.student_id, calculated_xp)
            return study_session

    def get_daily_missions(self, student_id: int = 1) -> List[DailyMission]:
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