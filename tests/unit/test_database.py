"""
Unit tests for Database Models, Repositories, and XP tracking.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from student42.database.repository import (
    AttemptRepository,
    ExerciseRepository,
    MistakeRepository,
    ProjectRepository,
    SkillRepository,
    StudentRepository,
)


def test_student_xp_and_level_advancement(db_session: Session):
    repo = StudentRepository(db_session)
    student = repo.get_or_create_student("cadet_coder", campus="Benguerir")

    assert student.xp == 0
    assert student.level == 0.0

    updated = repo.add_xp(student.id, 1500)
    assert updated.xp == 1500
    assert updated.level == 1.5


def test_project_and_exercise_lifecycle(db_session: Session):
    proj_repo = ProjectRepository(db_session)
    ex_repo = ExerciseRepository(db_session)

    project = proj_repo.create_or_update_project(
        slug="libft_test",
        name="Libft Test",
        tier="Rank 00",
        access_mode="strict",
    )
    assert project.slug == "libft_test"

    exercise = ex_repo.register_exercise(
        project_id=project.id,
        module_id="part_1",
        name="ft_strlen",
        source_file="ft_strlen.c",
        signature="size_t ft_strlen(const char *s);",
    )
    assert exercise.name == "ft_strlen"
    assert exercise.status == "pending"


def test_mistake_deduplication_and_occurrences(db_session: Session):
    proj_repo = ProjectRepository(db_session)
    ex_repo = ExerciseRepository(db_session)
    mistake_repo = MistakeRepository(db_session)

    project = proj_repo.create_or_update_project("gnl", "GNL", "Rank 01")
    exercise = ex_repo.register_exercise(project.id, "mandatory", "get_next_line", "get_next_line.c")

    m1 = mistake_repo.log_mistake(
        exercise_id=exercise.id,
        category="memory_leak",
        raw_error="definitely lost: 32 bytes in 1 blocks",
    )
    assert m1.occurrences == 1

    m2 = mistake_repo.log_mistake(
        exercise_id=exercise.id,
        category="memory_leak",
        raw_error="definitely lost: 64 bytes in 2 blocks",
    )
    assert m2.id == m1.id
    assert m2.occurrences == 2


def test_skill_record_outcome_null_safety(db_session: Session):
    """Verifies that record_outcome handles uninitialized counters without TypeError."""
    student_repo = StudentRepository(db_session)
    student = student_repo.get_or_create_student("null_safe_tester")

    skill_repo = SkillRepository(db_session)

    # First record on clean skill (failure)
    s1 = skill_repo.record_outcome(student.id, "pointers", success=False)
    assert s1.failure_count == 1
    assert s1.success_count == 0
    assert s1.mastery_level == 0.0

    # Second record (success)
    s2 = skill_repo.record_outcome(student.id, "pointers", success=True)
    assert s2.failure_count == 1
    assert s2.success_count == 1
    assert s2.mastery_level == 50.0