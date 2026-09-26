"""
Repository Layer for 42 Student OS.
Provides atomic query methods for all system entities.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from student42.database.models import (
    Attempt,
    Exercise,
    Mistake,
    Project,
    ReferenceItem,
    SkillMastery,
    Student,
    StudySession,
    TestDetail,
)


class StudentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_or_create_student(self, username: str, campus: str = "Benguerir") -> Student:
        stmt = select(Student).where(Student.username == username)
        student = self.session.execute(stmt).scalar_one_or_none()
        if not student:
            student = Student(username=username, campus=campus)
            self.session.add(student)
            self.session.flush()
        return student

    def get_primary_student(self) -> Optional[Student]:
        stmt = select(Student).order_by(Student.id.asc()).limit(1)
        return self.session.execute(stmt).scalar_one_or_none()

    def add_xp(self, student_id: int, amount: int) -> Student:
        student = self.session.get(Student, student_id)
        if not student:
            raise ValueError(f"Student with id {student_id} not found.")
        student.xp += amount
        student.level = round(student.xp / 1000.0, 2)
        student.last_active_date = datetime.now(timezone.utc)
        self.session.flush()
        return student


class ProjectRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_slug(self, slug: str) -> Optional[Project]:
        stmt = select(Project).where(Project.slug == slug)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_active_project(self) -> Optional[Project]:
        stmt = select(Project).where(Project.is_active == True).limit(1)
        return self.session.execute(stmt).scalar_one_or_none()

    def set_active_project(self, slug: str) -> Project:
        # Deactivate all
        stmt_all = select(Project)
        for proj in self.session.execute(stmt_all).scalars():
            proj.is_active = False

        target = self.get_by_slug(slug)
        if not target:
            raise ValueError(f"Project '{slug}' is not registered.")
        target.is_active = True
        self.session.flush()
        return target

    def create_or_update_project(
        self,
        slug: str,
        name: str,
        tier: str,
        local_path: Optional[str] = None,
        access_mode: str = "strict",
    ) -> Project:
        project = self.get_by_slug(slug)
        if not project:
            project = Project(
                slug=slug,
                name=name,
                tier=tier,
                local_path=local_path,
                access_mode=access_mode,
            )
            self.session.add(project)
        else:
            project.name = name
            project.tier = tier
            if local_path:
                project.local_path = local_path
            project.access_mode = access_mode
        self.session.flush()
        return project

    def list_all(self) -> List[Project]:
        stmt = select(Project).order_by(Project.id.asc())
        return list(self.session.execute(stmt).scalars().all())


class ExerciseRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_exercise(self, project_id: int, name: str) -> Optional[Exercise]:
        stmt = select(Exercise).where(
            Exercise.project_id == project_id,
            Exercise.name == name,
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def register_exercise(
        self,
        project_id: int,
        module_id: str,
        name: str,
        source_file: str,
        signature: Optional[str] = None,
        is_bonus: bool = False,
    ) -> Exercise:
        exercise = self.get_exercise(project_id, name)
        if not exercise:
            exercise = Exercise(
                project_id=project_id,
                module_id=module_id,
                name=name,
                source_file=source_file,
                signature=signature,
                is_bonus=is_bonus,
            )
            self.session.add(exercise)
        else:
            exercise.module_id = module_id
            exercise.source_file = source_file
            exercise.signature = signature
            exercise.is_bonus = is_bonus
        self.session.flush()
        return exercise

    def update_status(self, exercise_id: int, status: str) -> None:
        exercise = self.session.get(Exercise, exercise_id)
        if exercise:
            exercise.status = status
            self.session.flush()


class AttemptRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def record_attempt(
        self,
        exercise_id: int,
        compile_status: bool,
        norm_status: bool,
        valgrind_status: bool,
        tests_passed: int,
        tests_failed: int,
        compiler_output: Optional[str] = None,
        norm_output: Optional[str] = None,
    ) -> Attempt:
        attempt = Attempt(
            exercise_id=exercise_id,
            compile_status=compile_status,
            norm_status=norm_status,
            valgrind_status=valgrind_status,
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            compiler_output=compiler_output,
            norm_output=norm_output,
        )
        self.session.add(attempt)
        self.session.flush()
        return attempt

    def add_test_detail(
        self,
        attempt_id: int,
        test_name: str,
        passed: bool,
        input_data: Optional[str] = None,
        expected_output: Optional[str] = None,
        actual_output: Optional[str] = None,
        error_signal: Optional[str] = None,
    ) -> TestDetail:
        detail = TestDetail(
            attempt_id=attempt_id,
            test_name=test_name,
            passed=passed,
            input_data=input_data,
            expected_output=expected_output,
            actual_output=actual_output,
            error_signal=error_signal,
        )
        self.session.add(detail)
        self.session.flush()
        return detail

    def get_latest_attempts(self, exercise_id: int, limit: int = 5) -> List[Attempt]:
        stmt = (
            select(Attempt)
            .where(Attempt.exercise_id == exercise_id)
            .order_by(desc(Attempt.timestamp))
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars().all())


class MistakeRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def log_mistake(
        self,
        exercise_id: int,
        category: str,
        raw_error: str,
        root_cause: Optional[str] = None,
    ) -> Mistake:
        # Check if identical unresolved error exists for exercise
        stmt = select(Mistake).where(
            Mistake.exercise_id == exercise_id,
            Mistake.category == category,
            Mistake.resolved == False,
        )
        existing = self.session.execute(stmt).scalar_one_or_none()
        if existing:
            existing.occurrences += 1
            existing.raw_error = raw_error
            if root_cause:
                existing.root_cause = root_cause
            self.session.flush()
            return existing

        new_mistake = Mistake(
            exercise_id=exercise_id,
            category=category,
            raw_error=raw_error,
            root_cause=root_cause,
        )
        self.session.add(new_mistake)
        self.session.flush()
        return new_mistake

    def get_unresolved_mistakes(self, project_id: Optional[int] = None) -> List[Mistake]:
        stmt = select(Mistake).join(Exercise).where(Mistake.resolved == False)
        if project_id:
            stmt = stmt.where(Exercise.project_id == project_id)
        stmt = stmt.order_by(desc(Mistake.occurrences))
        return list(self.session.execute(stmt).scalars().all())


class SkillRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def record_outcome(self, student_id: int, concept: str, success: bool) -> SkillMastery:
        stmt = select(SkillMastery).where(
            SkillMastery.student_id == student_id,
            SkillMastery.concept == concept,
        )
        skill = self.session.execute(stmt).scalar_one_or_none()
        if not skill:
            skill = SkillMastery(student_id=student_id, concept=concept)
            self.session.add(skill)

        if success:
            skill.success_count += 1
        else:
            skill.failure_count += 1

        total = skill.success_count + skill.failure_count
        if total > 0:
            skill.mastery_level = round((skill.success_count / total) * 100.0, 1)

        self.session.flush()
        return skill

    def get_student_skills(self, student_id: int) -> List[SkillMastery]:
        stmt = (
            select(SkillMastery)
            .where(SkillMastery.student_id == student_id)
            .order_by(desc(SkillMastery.mastery_level))
        )
        return list(self.session.execute(stmt).scalars().all())


class ReferenceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_references(self, project_id: int) -> List[ReferenceItem]:
        stmt = select(ReferenceItem).where(ReferenceItem.project_id == project_id)
        return list(self.session.execute(stmt).scalars().all())

    def add_reference(
        self,
        project_id: int,
        ref_type: str,
        name: str,
        url_or_path: str,
        is_locked: bool = True,
        tags: Optional[str] = None,
    ) -> ReferenceItem:
        item = ReferenceItem(
            project_id=project_id,
            ref_type=ref_type,
            name=name,
            url_or_path=url_or_path,
            is_locked=is_locked,
            tags=tags,
        )
        self.session.add(item)
        self.session.flush()
        return item

    def unlock_reference(self, reference_id: int) -> None:
        item = self.session.get(ReferenceItem, reference_id)
        if item:
            item.is_locked = False
            self.session.flush()