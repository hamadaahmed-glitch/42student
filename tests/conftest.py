"""
Pytest configuration and fixtures for testing 42 Student OS.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Generator
import pytest
from sqlalchemy.orm import Session

from student42.core.config import get_paths, get_settings
from student42.database.connection import DatabaseManager
from student42.database.repository import (
    AttemptRepository,
    ExerciseRepository,
    ProjectRepository,
    StudentRepository,
)


@pytest.fixture
def temp_db_manager() -> Generator[DatabaseManager, None, None]:
    """Provides a fresh isolated SQLite database inside a temporary directory."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_file = Path(tmp_dir) / "test_student42.db"
        manager = DatabaseManager(db_path_override=str(db_file))
        manager.init_db()
        yield manager


@pytest.fixture
def db_session(temp_db_manager: DatabaseManager) -> Generator[Session, None, None]:
    """Provides a transaction-managed database session."""
    with temp_db_manager.session() as session:
        yield session


@pytest.fixture
def populated_student(db_session: Session):
    """Seed fixture with a primary student record."""
    repo = StudentRepository(db_session)
    student = repo.get_or_create_student("peer_tester", campus="Benguerir")
    return student