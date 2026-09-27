"""
SQLAlchemy 2.0 Relational Data Models for 42 Student OS.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    campus: Mapped[str] = mapped_column(String(64), default="Benguerir", nullable=False)
    level: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_active_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    skills: Mapped[List["SkillMastery"]] = relationship("SkillMastery", back_populates="student", cascade="all, delete-orphan")
    sessions: Mapped[List["StudySession"]] = relationship("StudySession", back_populates="student", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    tier: Mapped[str] = mapped_column(String(32), default="Rank 00", nullable=False)
    local_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="not_started", nullable=False)
    access_mode: Mapped[str] = mapped_column(String(32), default="strict", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    exercises: Mapped[List["Exercise"]] = relationship("Exercise", back_populates="project", cascade="all, delete-orphan")
    references: Mapped[List["ReferenceItem"]] = relationship("ReferenceItem", back_populates="project", cascade="all, delete-orphan")
    sessions: Mapped[List["StudySession"]] = relationship("StudySession", back_populates="project")


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    module_id: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    source_file: Mapped[str] = mapped_column(String(256), nullable=False)
    signature: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    is_bonus: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="exercises")
    attempts: Mapped[List["Attempt"]] = relationship("Attempt", back_populates="exercise", cascade="all, delete-orphan")
    mistakes: Mapped[List["Mistake"]] = relationship("Mistake", back_populates="exercise", cascade="all, delete-orphan")


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exercise_id: Mapped[int] = mapped_column(Integer, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    compile_status: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    norm_status: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    valgrind_status: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tests_passed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tests_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    compiler_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    norm_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    exercise: Mapped["Exercise"] = relationship("Exercise", back_populates="attempts")
    details: Mapped[List["TestDetail"]] = relationship("TestDetail", back_populates="attempt", cascade="all, delete-orphan")


class TestDetail(Base):
    __tablename__ = "test_details"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    attempt_id: Mapped[int] = mapped_column(Integer, ForeignKey("attempts.id", ondelete="CASCADE"), nullable=False)
    test_name: Mapped[str] = mapped_column(String(128), nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    input_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expected_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    actual_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_signal: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    attempt: Mapped["Attempt"] = relationship("Attempt", back_populates="details")


class Mistake(Base):
    __tablename__ = "mistakes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exercise_id: Mapped[int] = mapped_column(Integer, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)
    category: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    raw_error: Mapped[str] = mapped_column(Text, nullable=False)
    root_cause: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    occurrences: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    exercise: Mapped["Exercise"] = relationship("Exercise", back_populates="mistakes")


class SkillMastery(Base):
    __tablename__ = "skills_mastery"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    concept: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    mastery_level: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    success_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    failure_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)

    student: Mapped["Student"] = relationship("Student", back_populates="skills")


class StudySession(Base):
    __tablename__ = "study_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    functions_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hints_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    student: Mapped["Student"] = relationship("Student", back_populates="sessions")
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="sessions")


class ReferenceItem(Base):
    __tablename__ = "references"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    ref_type: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    url_or_path: Mapped[str] = mapped_column(String(512), nullable=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    tags: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="references")